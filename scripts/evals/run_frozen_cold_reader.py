#!/usr/bin/env python3
"""Run one prospectively frozen cold-reader reconstruction call exactly once."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import sys
import time
from typing import Any, Callable, Mapping, Sequence
from urllib import error, request


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from engine.system_b.pricing import (  # noqa: E402
    PRICES_LAST_VERIFIED,
    estimate_chat_cost_usd,
    lookup_chat_price,
)


CONTRACT_SCHEMA = "lolla.frozen_cold_reader_contract.v1"
OUTPUT_SCHEMA = "lolla.frozen_cold_reader_output.v1"
SUMMARY_SCHEMA = "lolla.frozen_cold_reader_run_summary.v1"
CUSTODY_SCHEMA = "lolla.frozen_cold_reader_call_custody.v1"
RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


class ReaderContractError(RuntimeError):
    pass


def _load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ReaderContractError(f"expected JSON object: {path}")
    return value


def _hash_bytes(value: bytes) -> str:
    return sha256(value).hexdigest()


def _hash_text(value: str) -> str:
    return _hash_bytes(value.encode("utf-8"))


def _hash_file(path: Path) -> str:
    return _hash_bytes(path.read_bytes())


def _repo_path(raw: object, *, label: str) -> Path:
    path = Path(str(raw))
    if path.is_absolute():
        raise ReaderContractError(f"{label} must be repo-relative")
    resolved = (REPO_ROOT / path).resolve()
    try:
        resolved.relative_to(REPO_ROOT.resolve())
    except ValueError as exc:
        raise ReaderContractError(f"{label} must remain inside repository") from exc
    return resolved


def _write_json_atomic(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def _load_env_file(path: Path) -> None:
    if not path.is_file():
        raise ReaderContractError(f"env file missing: {path}")
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value


def _output_instruction(contract: Mapping[str, Any]) -> str:
    output = contract["output_contract"]
    fields = ", ".join(
        f"{key} ({output['field_types'][key]})" for key in output["required_keys"]
    )
    object_rules = []
    for field, rule in output["object_contracts"].items():
        object_rules.append(
            f"{field} must contain exactly these keys: {', '.join(rule['required_keys'])}."
        )
    array_rules = []
    for field, rule in output["object_array_contracts"].items():
        array_rules.append(
            f"Each {field} item must contain exactly these string keys: "
            + ", ".join(rule["required_keys"])
            + f"; at most {rule['maximum_items']} items."
        )
    return (
        "Return one JSON object with exactly these top-level fields: "
        + fields
        + " "
        + " ".join(object_rules + array_rules)
    )


def build_prompts(contract: Mapping[str, Any]) -> dict[str, str]:
    receipt = _repo_path(
        contract["receipt"]["markdown_path"], label="receipt markdown"
    ).read_text(encoding="utf-8")
    user = (
        "SELF-CONTAINED REASONING RECEIPT\n\n"
        + receipt.strip()
        + "\n\n---\n\nRECONSTRUCTION TASK\n\n"
        + str(contract["reader_instruction"]).strip()
        + "\n\nOUTPUT JSON\n\n"
        + _output_instruction(contract)
    )
    return {"system_prompt": str(contract["system_prompt"]), "user_prompt": user}


def _prompt_hashes(contract: Mapping[str, Any]) -> dict[str, str]:
    prompts = build_prompts(contract)
    return {
        "system_prompt_sha256": _hash_text(prompts["system_prompt"]),
        "user_prompt_sha256": _hash_text(prompts["user_prompt"]),
    }


def validate_contract(contract: Mapping[str, Any]) -> None:
    if contract.get("schema_version") != CONTRACT_SCHEMA:
        raise ReaderContractError("unexpected cold-reader contract schema")
    if contract.get("status") != "frozen_before_call":
        raise ReaderContractError("contract must be frozen_before_call")
    if not RUN_ID_PATTERN.fullmatch(str(contract.get("run_id", ""))):
        raise ReaderContractError("invalid run_id")

    receipt = contract.get("receipt", {})
    for key, hash_key in (
        ("json_path", "json_sha256"),
        ("markdown_path", "markdown_sha256"),
    ):
        path = _repo_path(receipt.get(key, ""), label=f"receipt {key}")
        if not path.is_file() or _hash_file(path) != receipt.get(hash_key):
            raise ReaderContractError(f"receipt hash mismatch: {key}")

    config = contract.get("call_configuration", {})
    expected = {
        "provider": "openrouter",
        "temperature": 0.1,
        "reasoning_effort": "none",
        "generation_calls": 1,
        "evaluator_calls": 0,
        "automatic_retries": 0,
    }
    for key, value in expected.items():
        if config.get(key) != value:
            raise ReaderContractError(f"call configuration drifted: {key}")
    if not 1 <= float(config.get("provider_timeout_seconds", 0) or 0) <= 120:
        raise ReaderContractError("provider timeout invalid")
    if not 1 <= float(config.get("wall_clock_timeout_seconds", 0) or 0) <= 180:
        raise ReaderContractError("wall timeout invalid")
    if int(config.get("max_output_tokens", 0) or 0) <= 0:
        raise ReaderContractError("max_output_tokens must be positive")
    if lookup_chat_price("openrouter", str(config.get("model", ""))) is None:
        raise ReaderContractError("model missing from pricing table")
    budget = contract.get("call_budget", {})
    if budget.get("pricing_table_version") != PRICES_LAST_VERIFIED:
        raise ReaderContractError("pricing table version drifted")
    if float(budget.get("estimated_cost_ceiling_usd", 0) or 0) <= 0:
        raise ReaderContractError("cost ceiling must be positive")

    output = contract.get("output_contract", {})
    required = output.get("required_keys", [])
    field_types = output.get("field_types", {})
    if not isinstance(required, list) or set(required) != set(field_types):
        raise ReaderContractError("field_types must exactly cover required_keys")
    for field, rule in output.get("object_contracts", {}).items():
        if field_types.get(field) != "object" or not rule.get("required_keys"):
            raise ReaderContractError(f"invalid object contract: {field}")
    for field, rule in output.get("object_array_contracts", {}).items():
        if field_types.get(field) != "array_of_objects":
            raise ReaderContractError(f"invalid object-array field: {field}")
        if not rule.get("required_keys") or int(rule.get("maximum_items", 0)) <= 0:
            raise ReaderContractError(f"invalid object-array contract: {field}")

    locks = contract.get("hash_locks", [])
    roles = set()
    for row in locks:
        if not isinstance(row, Mapping) or set(row) != {"role", "path", "sha256"}:
            raise ReaderContractError("hash lock shape invalid")
        role = str(row["role"])
        if role in roles:
            raise ReaderContractError("hash lock roles must be unique")
        roles.add(role)
        path = _repo_path(row["path"], label=f"hash lock {role}")
        if not path.is_file() or _hash_file(path) != row["sha256"]:
            raise ReaderContractError(f"hash lock mismatch: {role}")
    if not {"reader_runner", "receipt_contract", "pricing"} <= roles:
        raise ReaderContractError("required hash lock roles missing")
    if _prompt_hashes(contract) != contract.get("prompt_hashes"):
        raise ReaderContractError("frozen prompt hashes mismatch")

    artifacts = contract.get("artifacts", {})
    output_dir = _repo_path(artifacts.get("output_dir", ""), label="output dir")
    for key in ("reader_output_path", "call_custody_path", "run_summary_path"):
        path = _repo_path(artifacts.get(key, ""), label=key)
        if path.parent != output_dir:
            raise ReaderContractError(f"{key} must be directly inside output dir")
    if not contract.get("review_after_call", {}).get("not_passed_to_reader", False):
        raise ReaderContractError("review rubric must be withheld from reader")


def _extract_json_object(text: str) -> dict[str, Any]:
    raw = text.strip()
    if raw.startswith("```"):
        lines = raw.splitlines()[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        raw = "\n".join(lines).strip()
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        left, right = raw.find("{"), raw.rfind("}")
        if left < 0 or right <= left:
            return {}
        try:
            value = json.loads(raw[left : right + 1])
        except json.JSONDecodeError:
            return {}
    return value if isinstance(value, dict) else {}


def _validate_response(response: Mapping[str, Any], contract: Mapping[str, Any]) -> list[str]:
    output = contract["output_contract"]
    errors = []
    if set(response) != set(output["required_keys"]):
        errors.append("top-level keys do not exactly match contract")
    for key, expected in output["field_types"].items():
        if key not in response:
            continue
        value = response[key]
        if expected == "string" and not isinstance(value, str):
            errors.append(f"{key} must be a string")
        elif expected == "array_of_strings" and (
            not isinstance(value, list) or any(not isinstance(item, str) for item in value)
        ):
            errors.append(f"{key} must be an array of strings")
        elif expected == "object" and not isinstance(value, dict):
            errors.append(f"{key} must be an object")
        elif expected == "array_of_objects" and (
            not isinstance(value, list) or any(not isinstance(item, dict) for item in value)
        ):
            errors.append(f"{key} must be an array of objects")
    for field, rule in output["object_contracts"].items():
        value = response.get(field)
        expected_keys = set(rule["required_keys"])
        if isinstance(value, dict) and (
            set(value) != expected_keys
            or any(not isinstance(item, str) for item in value.values())
        ):
            errors.append(f"{field} object shape invalid")
    for field, rule in output["object_array_contracts"].items():
        value = response.get(field)
        if not isinstance(value, list):
            continue
        if len(value) > int(rule["maximum_items"]):
            errors.append(f"{field} exceeds maximum")
        expected_keys = set(rule["required_keys"])
        for index, item in enumerate(value):
            if not isinstance(item, dict) or set(item) != expected_keys or any(
                not isinstance(part, str) for part in item.values()
            ):
                errors.append(f"{field}[{index}] shape invalid")
    return errors


def _model_attribution(requested: str, served: str) -> str:
    if not served:
        return "not_observed"
    if served == requested:
        return "matched"
    if served.startswith(f"{requested}-"):
        return "served_version_alias"
    return "mismatch"


def _call_openrouter(contract: Mapping[str, Any]) -> dict[str, Any]:
    started = time.monotonic()
    config = contract["call_configuration"]
    prompts = build_prompts(contract)
    requested_model = str(config["model"])
    base = {
        "call_attempted": True,
        "requested_model": requested_model,
        "system_prompt_sha256": _hash_text(prompts["system_prompt"]),
        "user_prompt_sha256": _hash_text(prompts["user_prompt"]),
    }
    api_key = os.getenv("LOLLA_OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return {
            **base,
            "status": "missing_api_key",
            "response": {},
            "validation_errors": ["OPENROUTER_API_KEY is missing"],
            "served_model": "",
            "model_attribution_status": "not_observed",
            "usage_evidence_state": "unknown",
            "duration_seconds": round(time.monotonic() - started, 3),
        }
    body = {
        "model": requested_model,
        "messages": [
            {"role": "system", "content": prompts["system_prompt"]},
            {"role": "user", "content": prompts["user_prompt"]},
        ],
        "response_format": {"type": "json_object"},
        "temperature": config["temperature"],
        "max_tokens": config["max_output_tokens"],
        "reasoning": {"effort": config["reasoning_effort"]},
    }
    req = request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(
            req, timeout=float(config["provider_timeout_seconds"])
        ) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        return {
            **base,
            "status": f"http_error_{exc.code}",
            "response": {},
            "validation_errors": [f"provider HTTP error {exc.code}"],
            "served_model": "",
            "model_attribution_status": "not_observed",
            "usage_evidence_state": "unknown",
            "duration_seconds": round(time.monotonic() - started, 3),
        }
    except Exception as exc:
        return {
            **base,
            "status": "provider_error",
            "response": {},
            "validation_errors": [type(exc).__name__],
            "served_model": "",
            "model_attribution_status": "not_observed",
            "usage_evidence_state": "unknown",
            "duration_seconds": round(time.monotonic() - started, 3),
        }
    choices = payload.get("choices", [])
    message = choices[0].get("message", {}) if choices else {}
    raw = str(message.get("content", ""))
    parsed = _extract_json_object(raw)
    validation_errors = _validate_response(parsed, contract)
    usage = payload.get("usage", {})
    prompt_tokens = usage.get("prompt_tokens") if isinstance(usage, Mapping) else None
    completion_tokens = (
        usage.get("completion_tokens") if isinstance(usage, Mapping) else None
    )
    total_tokens = usage.get("total_tokens") if isinstance(usage, Mapping) else None
    usage_complete = all(
        isinstance(value, int) and value > 0
        for value in (prompt_tokens, completion_tokens, total_tokens)
    )
    served_model = str(payload.get("model", ""))
    return {
        **base,
        "status": "ok" if not validation_errors else "invalid_contract",
        "response": parsed,
        "validation_errors": validation_errors,
        "served_model": served_model,
        "model_attribution_status": _model_attribution(requested_model, served_model),
        "finish_reason": choices[0].get("finish_reason", "") if choices else "",
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "reasoning_tokens": (
            usage.get("completion_tokens_details", {}).get("reasoning_tokens", 0)
            if isinstance(usage, Mapping)
            and isinstance(usage.get("completion_tokens_details", {}), Mapping)
            else 0
        ),
        "usage_evidence_state": "complete" if usage_complete else "unknown",
        "response_sha256": _hash_text(raw),
        "raw_provider_content_included": False,
        "duration_seconds": round(time.monotonic() - started, 3),
    }


def run_reader(
    contract: Mapping[str, Any],
    *,
    call_fn: Callable[[Mapping[str, Any]], dict[str, Any]] = _call_openrouter,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    validate_contract(contract)
    started = time.monotonic()
    call = call_fn(contract)
    wall_time = time.monotonic() - started
    custody = {
        "schema_version": CUSTODY_SCHEMA,
        "run_id": contract["run_id"],
        "recorded_call_count": 1,
        "call": call,
        "raw_provider_content_included": False,
    }
    output = {
        "schema_version": OUTPUT_SCHEMA,
        "run_id": contract["run_id"],
        "receipt_sha256": contract["receipt"]["markdown_sha256"],
        "status": call.get("status"),
        "reconstruction": call.get("response", {}),
        "validation_errors": call.get("validation_errors", []),
        "non_claims": contract["non_claims"],
    }
    usage_complete = call.get("usage_evidence_state") == "complete"
    price = lookup_chat_price("openrouter", contract["call_configuration"]["model"])
    estimated_cost = (
        estimate_chat_cost_usd(
            price=price,
            prompt_tokens=int(call.get("prompt_tokens") or 0),
            completion_tokens=int(call.get("completion_tokens") or 0),
        )
        if price is not None and usage_complete
        else None
    )
    gates = {
        "exactly_one_call_recorded": True,
        "call_status_ok": call.get("status") == "ok",
        "typed_output_valid": not call.get("validation_errors"),
        "usage_evidence_complete": usage_complete,
        "served_model_attribution_complete": call.get("model_attribution_status")
        in {"matched", "served_version_alias"},
        "reasoning_tokens_zero": int(call.get("reasoning_tokens") or 0) == 0,
        "wall_clock_ceiling_met": wall_time
        <= float(contract["call_configuration"]["wall_clock_timeout_seconds"]),
        "cost_estimate_complete": estimated_cost is not None,
        "cost_ceiling_met": estimated_cost is not None
        and estimated_cost <= float(contract["call_budget"]["estimated_cost_ceiling_usd"]),
        "experiment_retry_zero": True,
        "evaluator_calls_zero": True,
    }
    summary = {
        "schema_version": SUMMARY_SCHEMA,
        "run_id": contract["run_id"],
        "status": "passed" if all(gates.values()) else "failed",
        "contract_sha256": contract.get("contract_sha256_at_execution", ""),
        "call_count": 1,
        "prompt_tokens": call.get("prompt_tokens") if usage_complete else None,
        "completion_tokens": call.get("completion_tokens") if usage_complete else None,
        "total_tokens": call.get("total_tokens") if usage_complete else None,
        "estimated_cost_usd": estimated_cost,
        "pricing_table_version": PRICES_LAST_VERIFIED,
        "wall_time_seconds": round(wall_time, 3),
        "gates": gates,
        "failed_gates": [name for name, passed in gates.items() if not passed],
        "experiment_retries": 0,
        "evaluator_calls": 0,
        "review_status": "source_first_codex_review_required",
        "human_validated": False,
        "runtime_change_authorized": False,
    }
    return output, custody, summary


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    contract = _load_object(args.contract)
    validate_contract(contract)
    if args.dry_run:
        print(
            json.dumps(
                {
                    "status": "dry_run_valid",
                    "run_id": contract["run_id"],
                    "call_count": 1,
                    "prompt_hashes": contract["prompt_hashes"],
                    "provider_calls": 0,
                },
                indent=2,
            )
        )
        return 0
    if args.env_file is None:
        raise ReaderContractError("--env-file is required for execution")
    contract = dict(contract)
    contract["contract_sha256_at_execution"] = _hash_file(args.contract)
    _load_env_file(args.env_file)
    output_dir = _repo_path(contract["artifacts"]["output_dir"], label="output dir")
    if output_dir.exists():
        raise ReaderContractError("cold-reader output directory already exists")
    output_dir.mkdir(parents=True)
    output, custody, summary = run_reader(contract)
    summary["gates"]["output_directory_absent_before_run"] = True
    summary["failed_gates"] = [
        name for name, passed in summary["gates"].items() if not passed
    ]
    summary["status"] = "passed" if not summary["failed_gates"] else "failed"
    _write_json_atomic(
        _repo_path(contract["artifacts"]["call_custody_path"], label="custody"), custody
    )
    _write_json_atomic(
        _repo_path(contract["artifacts"]["reader_output_path"], label="output"), output
    )
    _write_json_atomic(
        _repo_path(contract["artifacts"]["run_summary_path"], label="summary"), summary
    )
    print(json.dumps(summary, indent=2))
    return 0 if summary["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
