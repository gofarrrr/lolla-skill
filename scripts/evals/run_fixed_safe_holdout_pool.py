#!/usr/bin/env python3
"""Generate one prospectively frozen synthetic holdout pool exactly once."""

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


CONTRACT_SCHEMA = "lolla.fixed_safe_holdout_pool_generation_contract.v1"
PAYLOAD_SCHEMA = "lolla.synthetic_holdout_pool_payload.v1"
POOL_SCHEMA = "lolla.fixed_safe_holdout_pool.v1"
CUSTODY_SCHEMA = "lolla.fixed_safe_holdout_pool_call_custody.v1"
SUMMARY_SCHEMA = "lolla.fixed_safe_holdout_pool_run_summary.v1"
RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


class HoldoutPoolError(RuntimeError):
    pass


def _load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise HoldoutPoolError(f"expected JSON object: {path}")
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
        raise HoldoutPoolError(f"{label} must be repo-relative")
    resolved = (REPO_ROOT / path).resolve()
    try:
        resolved.relative_to(REPO_ROOT.resolve())
    except ValueError as exc:
        raise HoldoutPoolError(f"{label} must remain inside repository") from exc
    return resolved


def _write_json_atomic(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def _write_text_atomic(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(value, encoding="utf-8")
    temporary.replace(path)


def _load_env_file(path: Path) -> None:
    if not path.is_file():
        raise HoldoutPoolError(f"env file missing: {path}")
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


def _selection_order(seed: str, case_ids: Sequence[str]) -> list[str]:
    return sorted(case_ids, key=lambda item: _hash_text(f"{seed}:{item}"))


def build_prompts(contract: Mapping[str, Any]) -> dict[str, str]:
    specs = [
        {
            "case_id": row["case_id"],
            "title": row["title"],
            "stratum": row["stratum"],
            "scenario_brief": row["scenario_brief"],
            "required_message_count": row["required_message_count"],
        }
        for row in contract["case_specs"]
    ]
    user = (
        str(contract["authoring_instruction"]).strip()
        + "\n\nCASE SPECIFICATIONS\n"
        + json.dumps(specs, indent=2, ensure_ascii=False)
        + "\n\nOUTPUT CONTRACT\n"
        + "Return one JSON object with exactly two keys: schema_version and cases. "
        + f"schema_version must be {PAYLOAD_SCHEMA}. Preserve the case order above. "
        + "Every case must contain exactly case_id, title, stratum, and messages. "
        + "Every message must contain exactly message_id, role, and content."
    )
    return {
        "system_prompt": str(contract["system_prompt"]).strip(),
        "user_prompt": user,
    }


def _prompt_hashes(contract: Mapping[str, Any]) -> dict[str, str]:
    prompts = build_prompts(contract)
    return {
        "system_prompt_sha256": _hash_text(prompts["system_prompt"]),
        "user_prompt_sha256": _hash_text(prompts["user_prompt"]),
    }


def validate_contract(contract: Mapping[str, Any]) -> None:
    if contract.get("schema_version") != CONTRACT_SCHEMA:
        raise HoldoutPoolError("unexpected pool contract schema")
    if contract.get("status") != "frozen_before_call":
        raise HoldoutPoolError("contract must be frozen_before_call")
    if not RUN_ID_PATTERN.fullmatch(str(contract.get("run_id", ""))):
        raise HoldoutPoolError("invalid run_id")
    specs = contract.get("case_specs")
    if not isinstance(specs, list) or len(specs) != 5:
        raise HoldoutPoolError("exactly five case specifications are required")
    case_ids: list[str] = []
    strata: list[str] = []
    for row in specs:
        if not isinstance(row, Mapping) or set(row) != {
            "case_id",
            "title",
            "stratum",
            "scenario_brief",
            "required_message_count",
        }:
            raise HoldoutPoolError("case specification shape invalid")
        case_id = str(row["case_id"])
        stratum = str(row["stratum"])
        if not RUN_ID_PATTERN.fullmatch(case_id):
            raise HoldoutPoolError("case_id invalid")
        if not all(str(row[key]).strip() for key in ("title", "stratum", "scenario_brief")):
            raise HoldoutPoolError("case specification text missing")
        if int(row["required_message_count"]) != 12:
            raise HoldoutPoolError("each case must require exactly 12 messages")
        case_ids.append(case_id)
        strata.append(stratum)
    if len(case_ids) != len(set(case_ids)) or len(strata) != len(set(strata)):
        raise HoldoutPoolError("case IDs and strata must be unique")

    selection = contract.get("selection_contract", {})
    seed = str(selection.get("public_seed", ""))
    expected_order = _selection_order(seed, case_ids)
    if selection.get("algorithm") != "sha256_seed_colon_case_id_ascending":
        raise HoldoutPoolError("selection algorithm drifted")
    if not seed or selection.get("ranked_case_ids") != expected_order:
        raise HoldoutPoolError("selection order drifted")
    if selection.get("generator_receives_selection_order") is not False:
        raise HoldoutPoolError("generator must not receive selection order")
    prompts = build_prompts(contract)
    for case_id in expected_order:
        if case_id not in prompts["user_prompt"]:
            raise HoldoutPoolError("case specification missing from prompt")
    if seed in prompts["user_prompt"] or json.dumps(expected_order) in prompts["user_prompt"]:
        raise HoldoutPoolError("selection information leaked to generator prompt")

    config = contract.get("call_configuration", {})
    expected_config = {
        "provider": "openrouter",
        "generation_calls": 1,
        "evaluator_calls": 0,
        "automatic_retries": 0,
        "reasoning_effort": "none",
    }
    for key, value in expected_config.items():
        if config.get(key) != value:
            raise HoldoutPoolError(f"call configuration drifted: {key}")
    if not 0 <= float(config.get("temperature", -1)) <= 1:
        raise HoldoutPoolError("temperature invalid")
    if not 1 <= int(config.get("max_output_tokens", 0)) <= 12000:
        raise HoldoutPoolError("max_output_tokens invalid")
    if not 1 <= float(config.get("provider_timeout_seconds", 0)) <= 120:
        raise HoldoutPoolError("provider timeout invalid")
    if not 1 <= float(config.get("wall_clock_timeout_seconds", 0)) <= 180:
        raise HoldoutPoolError("wall timeout invalid")
    if lookup_chat_price("openrouter", str(config.get("model", ""))) is None:
        raise HoldoutPoolError("model missing from pricing table")
    budget = contract.get("call_budget", {})
    if budget.get("pricing_table_version") != PRICES_LAST_VERIFIED:
        raise HoldoutPoolError("pricing table version drifted")
    if not 0 < float(budget.get("estimated_cost_ceiling_usd", 0)) <= 0.10:
        raise HoldoutPoolError("cost ceiling invalid")

    locks = contract.get("hash_locks", [])
    roles: set[str] = set()
    for row in locks:
        if not isinstance(row, Mapping) or set(row) != {"role", "path", "sha256"}:
            raise HoldoutPoolError("hash lock shape invalid")
        role = str(row["role"])
        if role in roles:
            raise HoldoutPoolError("hash lock roles must be unique")
        roles.add(role)
        path = _repo_path(row["path"], label=f"hash lock {role}")
        if not path.is_file() or _hash_file(path) != row["sha256"]:
            raise HoldoutPoolError(f"hash lock mismatch: {role}")
    if not {"pool_runner", "pricing", "evaluation_doctrine", "holdout_protocol"} <= roles:
        raise HoldoutPoolError("required hash lock roles missing")
    if contract.get("prompt_hashes") != _prompt_hashes(contract):
        raise HoldoutPoolError("prompt hashes drifted")

    artifacts = contract.get("artifacts", {})
    output_dir = _repo_path(artifacts.get("output_dir", ""), label="output dir")
    for key in ("pool_path", "call_custody_path", "run_summary_path"):
        path = _repo_path(artifacts.get(key, ""), label=key)
        if path.parent != output_dir:
            raise HoldoutPoolError(f"{key} must be directly inside output dir")
    case_dir = _repo_path(artifacts.get("case_dir", ""), label="case dir")
    if case_dir.parent != output_dir:
        raise HoldoutPoolError("case_dir must be directly inside output dir")
    if contract.get("post_call_review", {}).get("selection_review_scope") != (
        "safety_and_contract_only_not_likely_lolla_or_graph_value"
    ):
        raise HoldoutPoolError("post-call review scope drifted")


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


def _validate_payload(payload: Mapping[str, Any], contract: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if set(payload) != {"schema_version", "cases"}:
        errors.append("payload top-level shape invalid")
    if payload.get("schema_version") != PAYLOAD_SCHEMA:
        errors.append("payload schema invalid")
    cases = payload.get("cases")
    if not isinstance(cases, list) or len(cases) != len(contract["case_specs"]):
        return errors + ["payload case count invalid"]
    for index, (case, spec) in enumerate(zip(cases, contract["case_specs"], strict=True)):
        label = f"case[{index}]"
        if not isinstance(case, Mapping) or set(case) != {
            "case_id",
            "title",
            "stratum",
            "messages",
        }:
            errors.append(f"{label} shape invalid")
            continue
        for key in ("case_id", "title", "stratum"):
            if case.get(key) != spec[key]:
                errors.append(f"{label} {key} drifted")
        messages = case.get("messages")
        required = int(spec["required_message_count"])
        if not isinstance(messages, list) or len(messages) != required:
            errors.append(f"{label} message count invalid")
            continue
        total_chars = 0
        for message_index, message in enumerate(messages, start=1):
            message_label = f"{label}.messages[{message_index - 1}]"
            if not isinstance(message, Mapping) or set(message) != {
                "message_id",
                "role",
                "content",
            }:
                errors.append(f"{message_label} shape invalid")
                continue
            expected_id = f"{spec['case_id']}-m{message_index:02d}"
            expected_role = "user" if message_index % 2 else "assistant"
            content = message.get("content")
            if message.get("message_id") != expected_id:
                errors.append(f"{message_label} ID invalid")
            if message.get("role") != expected_role:
                errors.append(f"{message_label} role invalid")
            if not isinstance(content, str) or not content.strip() or len(content) > 2400:
                errors.append(f"{message_label} content invalid")
            elif content != content.strip():
                errors.append(f"{message_label} content must be trimmed")
            else:
                total_chars += len(content)
        if total_chars < 2400 or total_chars > 14000:
            errors.append(f"{label} conversation length outside contract")
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
            provider_payload = json.loads(response.read().decode("utf-8"))
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
    choices = provider_payload.get("choices", [])
    message = choices[0].get("message", {}) if choices else {}
    raw = str(message.get("content", ""))
    parsed = _extract_json_object(raw)
    validation_errors = _validate_payload(parsed, contract)
    usage = provider_payload.get("usage", {})
    prompt_tokens = usage.get("prompt_tokens") if isinstance(usage, Mapping) else None
    completion_tokens = (
        usage.get("completion_tokens") if isinstance(usage, Mapping) else None
    )
    total_tokens = usage.get("total_tokens") if isinstance(usage, Mapping) else None
    usage_complete = all(
        isinstance(value, int) and value > 0
        for value in (prompt_tokens, completion_tokens, total_tokens)
    )
    served_model = str(provider_payload.get("model", ""))
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


def _render_conversation(case: Mapping[str, Any]) -> str:
    lines = [
        f"# {case['title']}",
        "",
        f"Case ID: {case['case_id']}",
        f"Stratum: {case['stratum']}",
        "Synthetic evaluation fixture; not a real person's conversation.",
        "",
    ]
    turn = 0
    for message in case["messages"]:
        if message["role"] == "user":
            turn += 1
        lines.extend(
            [
                f"[Turn {turn}] {str(message['role']).upper()}:",
                str(message["content"]),
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def _build_pool(contract: Mapping[str, Any], call: Mapping[str, Any]) -> dict[str, Any]:
    cases = []
    for case in call.get("response", {}).get("cases", []):
        conversation = _render_conversation(case)
        cases.append(
            {
                **dict(case),
                "message_count": len(case["messages"]),
                "conversation_sha256": _hash_text(conversation),
                "conversation_path": (
                    f"{contract['artifacts']['case_dir']}/{case['case_id']}.txt"
                ),
            }
        )
    return {
        "schema_version": POOL_SCHEMA,
        "pool_id": contract["pool_id"],
        "status": "frozen_unreviewed" if call.get("status") == "ok" else "generation_failed",
        "provenance": {
            "kind": "synthetic_single_call",
            "real_person_data": False,
            "requested_model": call.get("requested_model", ""),
            "served_model": call.get("served_model", ""),
            "generation_contract_sha256": contract.get("contract_sha256_at_execution", ""),
        },
        "selection_contract": contract["selection_contract"],
        "selected_case_id": None,
        "selection_review_status": "pending_safety_and_contract_review",
        "cases": cases,
        "non_claims": contract["non_claims"],
    }


def run_pool_generation(
    contract: Mapping[str, Any],
    *,
    call_fn: Callable[[Mapping[str, Any]], dict[str, Any]] = _call_openrouter,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    validate_contract(contract)
    started = time.monotonic()
    call = call_fn(contract)
    wall_time = time.monotonic() - started
    pool = _build_pool(contract, call)
    custody = {
        "schema_version": CUSTODY_SCHEMA,
        "run_id": contract["run_id"],
        "recorded_call_count": 1,
        "call": call,
        "raw_provider_content_included": False,
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
        "typed_pool_valid": not call.get("validation_errors"),
        "five_cases_preserved": len(pool["cases"]) == 5,
        "usage_evidence_complete": usage_complete,
        "served_model_attribution_complete": call.get("model_attribution_status")
        in {"matched", "served_version_alias"},
        "wall_clock_ceiling_met": wall_time
        <= float(contract["call_configuration"]["wall_clock_timeout_seconds"]),
        "cost_estimate_complete": estimated_cost is not None,
        "cost_ceiling_met": estimated_cost is not None
        and estimated_cost <= float(contract["call_budget"]["estimated_cost_ceiling_usd"]),
        "automatic_retries_zero": True,
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
        "automatic_retries": 0,
        "evaluator_calls": 0,
        "semantic_or_graph_selection_performed": False,
        "runtime_change_authorized": False,
    }
    return pool, custody, summary


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
                    "ranked_case_ids": contract["selection_contract"]["ranked_case_ids"],
                    "provider_calls": 0,
                },
                indent=2,
            )
        )
        return 0
    if args.env_file is None:
        raise HoldoutPoolError("--env-file is required for execution")
    contract = dict(contract)
    contract["contract_sha256_at_execution"] = _hash_file(args.contract)
    _load_env_file(args.env_file)
    output_dir = _repo_path(contract["artifacts"]["output_dir"], label="output dir")
    if output_dir.exists():
        raise HoldoutPoolError("pool output directory already exists")
    output_dir.mkdir(parents=True)
    pool, custody, summary = run_pool_generation(contract)
    summary["gates"]["output_directory_absent_before_run"] = True
    summary["failed_gates"] = [
        name for name, passed in summary["gates"].items() if not passed
    ]
    summary["status"] = "passed" if not summary["failed_gates"] else "failed"
    case_dir = _repo_path(contract["artifacts"]["case_dir"], label="case dir")
    for case in pool["cases"]:
        _write_text_atomic(
            _repo_path(case["conversation_path"], label="conversation path"),
            _render_conversation(case),
        )
    _write_json_atomic(
        _repo_path(contract["artifacts"]["pool_path"], label="pool path"), pool
    )
    _write_json_atomic(
        _repo_path(
            contract["artifacts"]["call_custody_path"], label="call custody path"
        ),
        custody,
    )
    _write_json_atomic(
        _repo_path(contract["artifacts"]["run_summary_path"], label="run summary path"),
        summary,
    )
    print(json.dumps(summary, indent=2))
    return 0 if summary["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
