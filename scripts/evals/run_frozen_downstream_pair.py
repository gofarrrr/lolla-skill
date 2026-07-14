#!/usr/bin/env python3
"""Run one prospectively frozen blind control-versus-Lolla pair exactly once."""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import random
import re
import sys
import time
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any
from urllib import error, request


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from engine.system_b.pricing import (  # noqa: E402
    PRICES_LAST_VERIFIED,
    estimate_chat_cost_usd,
    lookup_chat_price,
)


CONTRACT_SCHEMA = "lolla.frozen_downstream_pair_contract.v1"
BLIND_SCHEMA = "lolla.frozen_downstream_pair_blind_outputs.v1"
KEY_SCHEMA = "lolla.frozen_downstream_pair_arm_key.v1"
SUMMARY_SCHEMA = "lolla.frozen_downstream_pair_run_summary.v1"
CUSTODY_SCHEMA = "lolla.frozen_downstream_pair_call_custody.v1"
RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


class PairContractError(RuntimeError):
    pass


def _load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise PairContractError(f"expected JSON object: {path}")
    return value


def _hash_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _hash_text(value: str) -> str:
    return _hash_bytes(value.encode("utf-8"))


def _hash_file(path: Path) -> str:
    return _hash_bytes(path.read_bytes())


def _repo_path(raw_path: object, *, label: str) -> Path:
    relative = Path(str(raw_path))
    if relative.is_absolute():
        raise PairContractError(f"{label} must be repo-relative")
    resolved = (REPO_ROOT / relative).resolve()
    try:
        resolved.relative_to(REPO_ROOT.resolve())
    except ValueError as exc:
        raise PairContractError(f"{label} must remain inside the repository") from exc
    return resolved


def _write_json_atomic(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _load_env_file(path: Path) -> None:
    if not path.is_file():
        raise PairContractError(f"env file missing: {path}")
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


def _pressure_items(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    value = contract.get("treatment_pressure_packet", [])
    if not isinstance(value, list) or not value:
        raise PairContractError("treatment pressure packet must be a non-empty array")
    if any(not isinstance(item, dict) for item in value):
        raise PairContractError("treatment pressure packet items must be objects")
    return value


def _output_instruction(contract: Mapping[str, Any], *, arm_id: str) -> str:
    output = contract["output_contract"]
    typed_fields = ", ".join(
        f"{key} ({output['field_types'][key]})" for key in output["required_keys"]
    )
    disposition = output["object_array_contracts"]["pressure_dispositions"]
    item_keys = ", ".join(disposition["required_keys"])
    instruction = (
        "Return an object with exactly these top-level keys and value types: "
        f"{typed_fields}. material_shifts may contain at most "
        f"{output['maximum_material_shifts']} objects; each must contain exactly "
        "shift, source_basis, and action_consequence strings. "
        f"pressure_dispositions objects must contain exactly these string keys: {item_keys}. "
    )
    if arm_id == "lolla_pressure_treatment":
        ids = ", ".join(item["pressure_id"] for item in _pressure_items(contract))
        instruction += (
            "Return exactly one pressure_dispositions item for each supplied "
            f"pressure_id in this order: {ids}. Copy IDs exactly. disposition "
            "must be use, reject, defer, or private_guardrail. A readable pressure "
            "cannot be called not_considered."
        )
    else:
        instruction += (
            "pressure_dispositions must be an empty array because this arm received "
            "no challenge pressure."
        )
    return instruction


def _build_user_prompt(contract: Mapping[str, Any], *, arm_id: str) -> str:
    conversation = _repo_path(
        contract["case"]["source_path"], label="conversation source"
    ).read_text(encoding="utf-8")
    sections = ["COMPLETE CONVERSATION\n\n" + conversation.strip()]
    if arm_id == "lolla_pressure_treatment":
        pressure_lines = []
        for item in _pressure_items(contract):
            turns = ", ".join(str(turn) for turn in item["source_turns"])
            pressure_lines.append(
                f"- pressure_id={item['pressure_id']} | source turns {turns}: "
                + str(item["challenge"]).strip()
            )
        sections.append(
            "SOURCE-GROUNDED CHALLENGE PRESSURE\n\n"
            "These are questions to consider, not conclusions or commands. Give "
            "each its strongest plausible application, then use, reject, defer, or "
            "keep it as a private guardrail based on the full conversation.\n\n"
            + "\n".join(pressure_lines)
        )
    elif arm_id != "strong_reconsideration_control":
        raise PairContractError(f"unknown arm: {arm_id}")
    sections.extend(
        [
            "RECONSIDERATION TASK\n\n"
            + str(contract["neutral_reconsideration_instruction"]).strip(),
            "OUTPUT JSON\n\n" + _output_instruction(contract, arm_id=arm_id),
        ]
    )
    return "\n\n---\n\n".join(sections)


def build_call_specs(contract: Mapping[str, Any]) -> list[dict[str, str]]:
    labels = ["A", "B"]
    random.Random(str(contract["blind_label_seed"])).shuffle(labels)
    arms = ["strong_reconsideration_control", "lolla_pressure_treatment"]
    return [
        {
            "blind_label": label,
            "arm_id": arm,
            "system_prompt": str(contract["system_prompt"]),
            "user_prompt": _build_user_prompt(contract, arm_id=arm),
        }
        for label, arm in zip(labels, arms, strict=True)
    ]


def _prompt_hashes(contract: Mapping[str, Any]) -> dict[str, dict[str, str]]:
    return {
        spec["arm_id"]: {
            "system_prompt_sha256": _hash_text(spec["system_prompt"]),
            "user_prompt_sha256": _hash_text(spec["user_prompt"]),
        }
        for spec in build_call_specs(contract)
    }


def validate_contract(contract: Mapping[str, Any]) -> None:
    if contract.get("schema_version") != CONTRACT_SCHEMA:
        raise PairContractError("unexpected frozen pair contract schema")
    if contract.get("status") != "frozen_before_calls":
        raise PairContractError("pair contract is not frozen_before_calls")
    run_id = str(contract.get("run_id", ""))
    if not RUN_ID_PATTERN.fullmatch(run_id):
        raise PairContractError("invalid run_id")
    case = contract.get("case", {})
    source_path = _repo_path(case.get("source_path", ""), label="source conversation")
    if not source_path.is_file() or _hash_file(source_path) != case.get("source_sha256"):
        raise PairContractError("source conversation hash mismatch")

    packet_source = contract.get("treatment_pressure_packet_source", {})
    packet_path = _repo_path(packet_source.get("path", ""), label="pressure packet")
    if not packet_path.is_file() or _hash_file(packet_path) != packet_source.get("sha256"):
        raise PairContractError("pressure packet hash mismatch")
    packet = _load_object(packet_path)
    if packet.get("pressure_items") != contract.get("treatment_pressure_packet"):
        raise PairContractError("embedded pressure packet differs from frozen source")
    items = _pressure_items(contract)
    ids = [str(item.get("pressure_id", "")).strip() for item in items]
    if any(not value for value in ids) or len(ids) != len(set(ids)):
        raise PairContractError("pressure IDs must be non-empty and unique")
    for index, item in enumerate(items):
        if not isinstance(item.get("source_turns"), list) or not item["source_turns"]:
            raise PairContractError(f"pressure item {index} lacks source turns")
        if not str(item.get("challenge", "")).strip():
            raise PairContractError(f"pressure item {index} lacks challenge text")

    config = contract.get("call_configuration", {})
    expected_config = {
        "provider": "openrouter",
        "temperature": 0.2,
        "reasoning_effort": "none",
        "samples_per_arm": 1,
        "total_generation_calls": 2,
        "evaluator_calls": 0,
        "automatic_retries": 0,
    }
    for key, expected in expected_config.items():
        if config.get(key) != expected:
            raise PairContractError(f"call configuration drifted: {key}")
    provider_timeout = float(config.get("provider_timeout_seconds", 0) or 0)
    wall_timeout = float(config.get("wall_clock_timeout_seconds", 0) or 0)
    if not 1 <= provider_timeout <= 120 or not provider_timeout < wall_timeout <= 300:
        raise PairContractError("invalid provider or pair wall-clock timeout")
    if int(config.get("max_output_tokens", 0) or 0) <= 0:
        raise PairContractError("max_output_tokens must be positive")
    if lookup_chat_price("openrouter", str(config.get("model", ""))) is None:
        raise PairContractError("frozen model is missing from the pricing table")
    budget = contract.get("call_budget", {})
    if budget.get("pricing_table_version") != PRICES_LAST_VERIFIED:
        raise PairContractError("pricing table version drifted")
    if float(budget.get("estimated_cost_ceiling_usd", 0) or 0) <= 0:
        raise PairContractError("estimated cost ceiling must be positive")

    output = contract.get("output_contract", {})
    required = output.get("required_keys", [])
    field_types = output.get("field_types", {})
    if not isinstance(required, list) or set(field_types) != set(required):
        raise PairContractError("field types must exactly cover required keys")
    disposition = output.get("object_array_contracts", {}).get(
        "pressure_dispositions", {}
    )
    custody = disposition.get("id_custody", {})
    expected_custody = {
        "source": "treatment_pressure_packet",
        "source_id_field": "pressure_id",
        "item_id_field": "pressure_id",
        "coverage": "exactly_once_in_treatment_empty_in_control",
    }
    if custody != expected_custody:
        raise PairContractError("pressure disposition custody contract drifted")
    if disposition.get("maximum_items") != len(ids):
        raise PairContractError("pressure disposition maximum must match packet")
    if disposition.get("allowed_values", {}).get("pressure_id") != ids:
        raise PairContractError("allowed pressure IDs must match packet order")

    artifacts = contract.get("artifacts", {})
    output_dir = _repo_path(artifacts.get("output_dir", ""), label="output directory")
    for key in ("blind_outputs_path", "arm_key_path", "run_summary_path", "call_custody_path"):
        path = _repo_path(artifacts.get(key, ""), label=key)
        if path.parent != output_dir:
            raise PairContractError(f"{key} must be directly inside output directory")

    locks = contract.get("hash_locks", [])
    if not isinstance(locks, list) or not locks:
        raise PairContractError("hash_locks must be non-empty")
    roles: set[str] = set()
    for index, lock in enumerate(locks):
        if not isinstance(lock, Mapping) or set(lock) != {"role", "path", "sha256"}:
            raise PairContractError(f"hash_locks[{index}] shape invalid")
        role = str(lock["role"])
        if role in roles:
            raise PairContractError("hash lock roles must be unique")
        roles.add(role)
        path = _repo_path(lock["path"], label=f"hash lock {role}")
        if not path.is_file() or _hash_file(path) != lock["sha256"]:
            raise PairContractError(f"hash lock mismatch: {role}")
    required_roles = {
        "pair_runner",
        "source_conversation",
        "stage_a_contract",
        "stage_a_gate",
        "private_table_snapshot",
        "v60_snapshot",
        "preliminary_pressure_review",
        "pressure_packet",
        "two_stage_protocol",
        "downstream_experiment_protocol",
        "pricing",
    }
    if not required_roles <= roles:
        raise PairContractError(
            f"required hash roles missing: {sorted(required_roles - roles)}"
        )
    if _prompt_hashes(contract) != contract.get("prompt_hashes"):
        raise PairContractError("frozen prompt hashes mismatch")
    red_lines = contract.get("source_red_lines", {})
    if not isinstance(red_lines.get("must_preserve"), list) or not red_lines[
        "must_preserve"
    ]:
        raise PairContractError("source must-preserve red lines are required")
    if not isinstance(red_lines.get("must_not_invent"), list) or not red_lines[
        "must_not_invent"
    ]:
        raise PairContractError("source must-not-invent red lines are required")
    if not isinstance(contract.get("stop_rules"), list) or not contract["stop_rules"]:
        raise PairContractError("stop rules are required")


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


def _validate_response(
    response: Mapping[str, Any], contract: Mapping[str, Any], *, arm_id: str
) -> list[str]:
    output = contract["output_contract"]
    required = set(output["required_keys"])
    errors: list[str] = []
    if set(response) != required:
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
        elif expected == "array_of_objects" and (
            not isinstance(value, list) or any(not isinstance(item, dict) for item in value)
        ):
            errors.append(f"{key} must be an array of objects")
    shifts = response.get("material_shifts", [])
    if isinstance(shifts, list):
        if len(shifts) > int(output["maximum_material_shifts"]):
            errors.append("material_shifts exceeds maximum")
        expected_shift = set(output["material_shift_required_keys"])
        for index, item in enumerate(shifts):
            if not isinstance(item, dict) or set(item) != expected_shift or any(
                not isinstance(value, str) for value in item.values()
            ):
                errors.append(f"material_shifts[{index}] shape invalid")
    disposition_contract = output["object_array_contracts"]["pressure_dispositions"]
    dispositions = response.get("pressure_dispositions", [])
    if isinstance(dispositions, list):
        expected_keys = set(disposition_contract["required_keys"])
        for index, item in enumerate(dispositions):
            if not isinstance(item, dict) or set(item) != expected_keys or any(
                not isinstance(value, str) for value in item.values()
            ):
                errors.append(f"pressure_dispositions[{index}] shape invalid")
                continue
            if item["pressure_id"] not in disposition_contract["allowed_values"]["pressure_id"]:
                errors.append(f"pressure_dispositions[{index}].pressure_id invalid")
            if item["disposition"] not in disposition_contract["allowed_values"]["disposition"]:
                errors.append(f"pressure_dispositions[{index}].disposition invalid")
        observed_ids = [
            item.get("pressure_id", "") for item in dispositions if isinstance(item, dict)
        ]
        expected_ids = [item["pressure_id"] for item in _pressure_items(contract)]
        if arm_id == "lolla_pressure_treatment" and observed_ids != expected_ids:
            errors.append("treatment pressure IDs not covered exactly once in packet order")
        if arm_id == "strong_reconsideration_control" and dispositions:
            errors.append("control pressure_dispositions must be empty")
    return errors


def _model_attribution(requested: str, served: str) -> str:
    if not served:
        return "not_observed"
    if served == requested:
        return "matched"
    if served.startswith(f"{requested}-"):
        return "served_version_alias"
    return "mismatch"


def _call_openrouter(spec: Mapping[str, str], contract: Mapping[str, Any]) -> dict[str, Any]:
    started = time.monotonic()
    config = contract["call_configuration"]
    requested_model = str(config["model"])
    base = {
        "blind_label": spec["blind_label"],
        "call_attempted": True,
        "requested_model": requested_model,
        "prompt_sha256": _hash_text(spec["user_prompt"]),
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
            {"role": "system", "content": spec["system_prompt"]},
            {"role": "user", "content": spec["user_prompt"]},
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
        with request.urlopen(req, timeout=float(config["provider_timeout_seconds"])) as response:
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
    errors = _validate_response(parsed, contract, arm_id=spec["arm_id"])
    usage = payload.get("usage", {})
    prompt_tokens = usage.get("prompt_tokens") if isinstance(usage, Mapping) else None
    completion_tokens = usage.get("completion_tokens") if isinstance(usage, Mapping) else None
    total_tokens = usage.get("total_tokens") if isinstance(usage, Mapping) else None
    usage_complete = all(
        isinstance(value, int) and value > 0
        for value in (prompt_tokens, completion_tokens, total_tokens)
    )
    served_model = str(payload.get("model", ""))
    return {
        **base,
        "status": "ok" if not errors else "invalid_contract",
        "response": parsed,
        "validation_errors": errors,
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


def _custody_payload(contract: Mapping[str, Any], calls: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": CUSTODY_SCHEMA,
        "run_id": contract["run_id"],
        "status": "complete" if len(calls) == 2 else "in_progress",
        "recorded_call_count": len(calls),
        "calls": [dict(item) for item in sorted(calls, key=lambda value: value["blind_label"])],
        "arm_identity_included": False,
        "raw_provider_content_included": False,
    }


def run_pair(
    contract: Mapping[str, Any],
    *,
    on_call: Callable[[dict[str, Any]], None] | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    validate_contract(contract)
    specs = build_call_specs(contract)
    started = time.monotonic()
    outputs: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_to_spec = {
            executor.submit(_call_openrouter, spec, contract): spec for spec in specs
        }
        for future in concurrent.futures.as_completed(future_to_spec):
            result = future.result()
            outputs.append(result)
            if on_call is not None:
                on_call(result)
    wall_time = time.monotonic() - started
    outputs.sort(key=lambda item: item["blind_label"])
    blind = {
        "schema_version": BLIND_SCHEMA,
        "run_id": contract["run_id"],
        "case_id": contract["case"]["case_id"],
        "source_sha256": contract["case"]["source_sha256"],
        "review_status": "blind_review_required_before_arm_key",
        "outputs": outputs,
        "arm_identity_included": False,
        "non_claims": contract["non_claims"],
    }
    key = {
        "schema_version": KEY_SCHEMA,
        "run_id": contract["run_id"],
        "mapping": [
            {"blind_label": spec["blind_label"], "arm_id": spec["arm_id"]}
            for spec in sorted(specs, key=lambda item: item["blind_label"])
        ],
    }
    usage_complete = all(item.get("usage_evidence_state") == "complete" for item in outputs)
    model_attribution_complete = all(
        item.get("model_attribution_status") in {"matched", "served_version_alias"}
        for item in outputs
    )
    prompt_tokens = sum(int(item.get("prompt_tokens") or 0) for item in outputs)
    completion_tokens = sum(int(item.get("completion_tokens") or 0) for item in outputs)
    total_tokens = sum(int(item.get("total_tokens") or 0) for item in outputs)
    price = lookup_chat_price("openrouter", contract["call_configuration"]["model"])
    estimated_cost = (
        estimate_chat_cost_usd(
            price=price,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )
        if price is not None and usage_complete
        else None
    )
    gates = {
        "exactly_two_calls_recorded": len(outputs) == 2,
        "both_calls_status_ok": all(item.get("status") == "ok" for item in outputs),
        "typed_outputs_valid": all(not item.get("validation_errors") for item in outputs),
        "usage_evidence_complete": usage_complete,
        "served_model_attribution_complete": model_attribution_complete,
        "reasoning_tokens_zero": all(int(item.get("reasoning_tokens") or 0) == 0 for item in outputs),
        "pair_wall_clock_ceiling_met": wall_time
        <= float(contract["call_configuration"]["wall_clock_timeout_seconds"]),
        "cost_estimate_complete": estimated_cost is not None,
        "cost_ceiling_met": estimated_cost is not None
        and estimated_cost <= float(contract["call_budget"]["estimated_cost_ceiling_usd"]),
        "experiment_retry_zero": int(contract["call_configuration"]["automatic_retries"]) == 0,
    }
    summary = {
        "schema_version": SUMMARY_SCHEMA,
        "run_id": contract["run_id"],
        "case_id": contract["case"]["case_id"],
        "status": "passed" if all(gates.values()) else "failed",
        "contract_sha256": contract.get("contract_sha256_at_execution", ""),
        "call_count": len(outputs),
        "successful_call_count": sum(item.get("status") == "ok" for item in outputs),
        "prompt_tokens": prompt_tokens if usage_complete else None,
        "completion_tokens": completion_tokens if usage_complete else None,
        "total_tokens": total_tokens if usage_complete else None,
        "estimated_cost_usd": estimated_cost,
        "pricing_table_version": PRICES_LAST_VERIFIED,
        "wall_time_seconds": round(wall_time, 3),
        "gates": gates,
        "failed_gates": [name for name, passed in gates.items() if not passed],
        "review_status": "blind_review_required_before_arm_key",
        "evaluator_calls": 0,
        "experiment_retries": 0,
        "runtime_change_authorized": False,
        "graph_integration_authorized": False,
    }
    return blind, key, summary


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
                    "call_count": 2,
                    "prompt_hashes": contract["prompt_hashes"],
                    "provider_calls": 0,
                },
                indent=2,
            )
        )
        return 0
    if args.env_file is None:
        raise PairContractError("--env-file is required for execution")
    contract = dict(contract)
    contract["contract_sha256_at_execution"] = _hash_file(args.contract)
    _load_env_file(args.env_file)
    output_dir = _repo_path(contract["artifacts"]["output_dir"], label="output directory")
    if output_dir.exists():
        raise PairContractError("frozen pair output directory already exists")
    output_dir.mkdir(parents=True)
    custody_path = _repo_path(
        contract["artifacts"]["call_custody_path"], label="call custody path"
    )
    call_records: list[dict[str, Any]] = []

    def persist_call(result: dict[str, Any]) -> None:
        call_records.append(result)
        _write_json_atomic(custody_path, _custody_payload(contract, call_records))

    blind, key, summary = run_pair(contract, on_call=persist_call)
    summary["gates"]["output_directory_absent_before_run"] = True
    summary["failed_gates"] = [
        name for name, passed in summary["gates"].items() if not passed
    ]
    summary["status"] = "passed" if not summary["failed_gates"] else "failed"
    _write_json_atomic(
        _repo_path(contract["artifacts"]["blind_outputs_path"], label="blind outputs"),
        blind,
    )
    _write_json_atomic(
        _repo_path(contract["artifacts"]["arm_key_path"], label="arm key"), key
    )
    _write_json_atomic(
        _repo_path(contract["artifacts"]["run_summary_path"], label="run summary"),
        summary,
    )
    print(json.dumps(summary, indent=2))
    return 0 if summary["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
