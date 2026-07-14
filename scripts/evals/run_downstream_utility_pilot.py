#!/usr/bin/env python3
"""Run the frozen two-arm downstream-utility pilot with exactly two calls."""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import random
import sys
from pathlib import Path
from typing import Any, Mapping
from urllib import error, request


CONTRACT_SCHEMA = "lolla.downstream_utility_pilot_contract.v0"
BLIND_SCHEMA = "lolla.downstream_utility_blind_outputs.v0"
KEY_SCHEMA = "lolla.downstream_utility_arm_key.v0"
SUMMARY_SCHEMA = "lolla.downstream_utility_pilot_run_summary.v0"
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class PilotError(RuntimeError):
    pass


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise PilotError(f"expected JSON object: {path}")
    return value


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_text(value: str) -> str:
    return _sha256_bytes(value.encode("utf-8"))


def _load_env_file(path: Path) -> None:
    if not path.is_file():
        raise PilotError(f"env file missing: {path}")
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value


def validate_contract(contract: Mapping[str, Any]) -> None:
    if contract.get("schema_version") != CONTRACT_SCHEMA:
        raise PilotError("unexpected pilot contract schema")
    if contract.get("status") != "frozen_before_calls":
        raise PilotError("pilot contract is not frozen_before_calls")
    config = contract.get("call_configuration", {})
    if config.get("total_generation_calls") != 2:
        raise PilotError("pilot must use exactly two generation calls")
    if config.get("samples_per_arm") != 1:
        raise PilotError("pilot must use exactly one sample per arm")
    if config.get("evaluator_calls") != 0:
        raise PilotError("pilot forbids evaluator calls")
    if config.get("reasoning_effort") != "none":
        raise PilotError("pilot reasoning configuration drifted")
    pressure_packet = contract.get("treatment_pressure_packet", [])
    if not isinstance(pressure_packet, list) or len(pressure_packet) < 1:
        raise PilotError("treatment pressure packet is empty")
    pressure_ids: list[str] = []
    for index, item in enumerate(pressure_packet):
        if not isinstance(item, Mapping):
            raise PilotError(f"treatment_pressure_packet[{index}] must be an object")
        pressure_id = str(item.get("pressure_id", "")).strip()
        if not pressure_id:
            raise PilotError(
                f"treatment_pressure_packet[{index}].pressure_id is required"
            )
        pressure_ids.append(pressure_id)
        source_turns = item.get("source_turns")
        if not isinstance(source_turns, list) or not source_turns:
            raise PilotError(
                f"treatment_pressure_packet[{index}].source_turns is required"
            )
    if len(pressure_ids) != len(set(pressure_ids)):
        raise PilotError("treatment pressure IDs must be unique")
    runner = contract.get("runner", {})
    if runner:
        if not isinstance(runner, Mapping):
            raise PilotError("runner must be an object")
        runner_path = REPO_ROOT / str(runner.get("path", ""))
        if not runner_path.is_file():
            raise PilotError("runner path is missing")
        if _sha256_bytes(runner_path.read_bytes()) != runner.get("sha256"):
            raise PilotError("runner hash mismatch")
    packet_source = contract.get("treatment_pressure_packet_source", {})
    if packet_source:
        if not isinstance(packet_source, Mapping):
            raise PilotError("treatment_pressure_packet_source must be an object")
        packet_path = REPO_ROOT / str(packet_source.get("path", ""))
        if not packet_path.is_file():
            raise PilotError("treatment pressure packet source is missing")
        if _sha256_bytes(packet_path.read_bytes()) != packet_source.get("sha256"):
            raise PilotError("treatment pressure packet hash mismatch")
        packet_payload = _load_json(packet_path)
        if packet_payload.get("items") != contract.get("treatment_pressure_packet"):
            raise PilotError("embedded treatment pressure packet differs from source")
    source_artifacts = contract.get("source_artifacts", [])
    if source_artifacts:
        if not isinstance(source_artifacts, list):
            raise PilotError("source_artifacts must be an array")
        for index, artifact in enumerate(source_artifacts):
            if not isinstance(artifact, Mapping):
                raise PilotError(f"source_artifacts[{index}] must be an object")
            artifact_path = REPO_ROOT / str(artifact.get("path", ""))
            if not artifact_path.is_file():
                raise PilotError(f"source artifact missing: {artifact_path}")
            if _sha256_bytes(artifact_path.read_bytes()) != artifact.get("sha256"):
                raise PilotError(f"source artifact hash mismatch: {artifact_path}")
    output = contract.get("output_contract", {})
    field_types = output.get("field_types", {}) if isinstance(output, Mapping) else {}
    if field_types:
        if not isinstance(field_types, Mapping):
            raise PilotError("output field_types must be an object")
        required_keys = set(output.get("required_keys", []))
        if set(field_types) != required_keys:
            raise PilotError("output field_types must cover exactly the required_keys")
        supported_types = {"string", "array_of_strings", "array_of_objects"}
        unsupported = sorted(set(field_types.values()) - supported_types)
        if unsupported:
            raise PilotError(f"unsupported output field types: {unsupported}")
    object_contracts = (
        output.get("object_array_contracts", {})
        if isinstance(output, Mapping)
        else {}
    )
    if object_contracts:
        if not isinstance(object_contracts, Mapping):
            raise PilotError("output object_array_contracts must be an object")
        for field, item_contract in object_contracts.items():
            if not isinstance(item_contract, Mapping):
                raise PilotError(f"object_array_contracts.{field} must be an object")
            id_custody = item_contract.get("id_custody")
            if not id_custody:
                continue
            if not isinstance(id_custody, Mapping):
                raise PilotError(f"{field}.id_custody must be an object")
            expected_custody = {
                "source": "treatment_pressure_packet",
                "source_id_field": "pressure_id",
                "item_id_field": "pressure_id",
                "coverage": "exactly_once_in_treatment_empty_in_control",
            }
            if dict(id_custody) != expected_custody:
                raise PilotError(f"{field}.id_custody is unsupported")
            required_item_keys = set(item_contract.get("required_keys", []))
            if "pressure_id" not in required_item_keys:
                raise PilotError(f"{field}.pressure_id must be a required item key")
            maximum = int(item_contract.get("maximum_items", 0) or 0)
            if maximum != len(pressure_ids):
                raise PilotError(
                    f"{field}.maximum_items must match treatment pressure count"
                )
            allowed_values = item_contract.get("allowed_values", {})
            allowed_ids = (
                allowed_values.get("pressure_id", [])
                if isinstance(allowed_values, Mapping)
                else []
            )
            if list(allowed_ids) != pressure_ids:
                raise PilotError(
                    f"{field}.pressure_id allowed values must exactly match "
                    "treatment pressure IDs in packet order"
                )

    protocol = contract["protocol"]
    protocol_path = REPO_ROOT / protocol["path"]
    if _sha256_bytes(protocol_path.read_bytes()) != protocol["sha256"]:
        raise PilotError("protocol hash mismatch")
    case = contract["case"]
    source_path = REPO_ROOT / case["source_path"]
    if _sha256_bytes(source_path.read_bytes()) != case["source_sha256"]:
        raise PilotError("source conversation hash mismatch")


def _build_user_prompt(
    contract: Mapping[str, Any],
    *,
    arm_id: str,
) -> str:
    case = contract["case"]
    conversation = (REPO_ROOT / case["source_path"]).read_text(encoding="utf-8")
    sections = [
        "COMPLETE CONVERSATION\n\n" + conversation.strip(),
        "RECONSIDERATION TASK\n\n"
        + str(contract["neutral_reconsideration_instruction"]).strip(),
    ]
    if arm_id == "lolla_pressure_treatment":
        pressures = []
        for item in contract["treatment_pressure_packet"]:
            turns = ", ".join(map(str, item["source_turns"]))
            pressures.append(
                f"- Source turns {turns}: {str(item['challenge']).strip()}"
            )
        sections.insert(
            1,
            "SOURCE-GROUNDED CHALLENGE PRESSURE\n\n"
            "Treat these as questions to consider, not conclusions or commands. "
            "Use, reject, or qualify them based on the full conversation.\n\n"
            + "\n".join(pressures),
        )
    elif arm_id != "strong_reconsideration_control":
        raise PilotError(f"unknown arm: {arm_id}")

    output = contract["output_contract"]
    field_types = output.get("field_types", {})
    if isinstance(field_types, Mapping) and field_types:
        typed_fields = ", ".join(
            f"{key} ({field_types[key]})" for key in output["required_keys"]
        )
        output_instruction = (
            "Return an object with exactly these top-level keys and value "
            f"types: {typed_fields}. material_shifts may contain at most "
            f"{int(output['maximum_material_shifts'])} objects; each must "
            "contain exactly shift, source_basis, and action_consequence "
            "strings."
        )
        object_contracts = output.get("object_array_contracts", {})
        if isinstance(object_contracts, Mapping):
            for field, item_contract in object_contracts.items():
                if not isinstance(item_contract, Mapping):
                    continue
                item_keys = ", ".join(
                    str(item) for item in item_contract.get("required_keys", [])
                )
                maximum = int(item_contract.get("maximum_items", 0) or 0)
                output_instruction += (
                    f" {field} may contain at most {maximum} objects; each must "
                    f"contain exactly these string keys: {item_keys}."
                )
                allowed_values = item_contract.get("allowed_values", {})
                id_custody = item_contract.get("id_custody")
                if isinstance(allowed_values, Mapping):
                    for key, values in allowed_values.items():
                        if (
                            id_custody
                            and arm_id == "strong_reconsideration_control"
                            and key == id_custody.get("item_id_field")
                        ):
                            continue
                        output_instruction += (
                            f" {field}.{key} must be one of: "
                            + ", ".join(str(value) for value in values)
                            + "."
                        )
                if id_custody:
                    if arm_id == "lolla_pressure_treatment":
                        output_instruction += (
                            f" {field} must contain exactly one item for each "
                            "supplied pressure_id and must copy each pressure_id "
                            "exactly without renaming or aggregation."
                        )
                    else:
                        output_instruction += (
                            f" {field} must be an empty array because this arm "
                            "received no challenge pressure."
                        )
        field_guidance = output.get("field_guidance", {})
        if isinstance(field_guidance, Mapping):
            for field, guidance in field_guidance.items():
                output_instruction += f" {field}: {str(guidance).strip()}"
    else:
        output_instruction = (
            "Return an object with exactly these top-level keys: "
            "updated_position (string), what_survived (array of strings), "
            "take_backs_or_set_aside (array of strings), material_shifts "
            "(array of at most four objects with shift, source_basis, and "
            "action_consequence strings), and uncertainties (array of strings)."
        )
    sections.append("OUTPUT JSON\n\n" + output_instruction)
    return "\n\n---\n\n".join(sections)


def build_call_specs(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    validate_contract(contract)
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
    response: Mapping[str, Any],
    contract: Mapping[str, Any],
    *,
    arm_id: str | None = None,
) -> list[str]:
    output = contract["output_contract"]
    required = set(output["required_keys"])
    errors: list[str] = []
    missing = sorted(required - set(response))
    unknown = sorted(set(response) - required)
    if missing:
        errors.append(f"missing top-level keys: {missing}")
    if unknown:
        errors.append(f"unknown top-level keys: {unknown}")
    field_types = output.get("field_types", {})
    if isinstance(field_types, Mapping):
        for key, expected_type in field_types.items():
            if key not in response:
                continue
            value = response[key]
            if expected_type == "string" and not isinstance(value, str):
                errors.append(f"{key} must be a string")
            elif expected_type == "array_of_strings" and (
                not isinstance(value, list)
                or any(not isinstance(item, str) for item in value)
            ):
                errors.append(f"{key} must be an array of strings")
            elif expected_type == "array_of_objects" and (
                not isinstance(value, list)
                or any(not isinstance(item, dict) for item in value)
            ):
                errors.append(f"{key} must be an array of objects")
            elif expected_type not in {
                "string",
                "array_of_strings",
                "array_of_objects",
            }:
                errors.append(f"{key} has unsupported field type: {expected_type}")
    object_contracts = output.get("object_array_contracts", {})
    if isinstance(object_contracts, Mapping):
        for field, item_contract in object_contracts.items():
            if not isinstance(item_contract, Mapping) or field not in response:
                continue
            items = response[field]
            if not isinstance(items, list):
                continue
            maximum = int(item_contract.get("maximum_items", 0) or 0)
            if len(items) > maximum:
                errors.append(f"{field} exceeds maximum")
            required_item_keys = set(item_contract.get("required_keys", []))
            allowed_values = item_contract.get("allowed_values", {})
            for index, item in enumerate(items):
                if not isinstance(item, dict):
                    continue
                if set(item) != required_item_keys:
                    errors.append(f"{field}[{index}] has invalid shape")
                    continue
                for key, value in item.items():
                    if not isinstance(value, str):
                        errors.append(f"{field}[{index}].{key} must be a string")
                if isinstance(allowed_values, Mapping):
                    for key, values in allowed_values.items():
                        if item.get(key) not in values:
                            errors.append(
                                f"{field}[{index}].{key} has invalid value"
                            )
            id_custody = item_contract.get("id_custody")
            if isinstance(id_custody, Mapping) and arm_id:
                item_id_field = str(id_custody.get("item_id_field", ""))
                observed_ids = [
                    str(item.get(item_id_field, ""))
                    for item in items
                    if isinstance(item, Mapping)
                ]
                if arm_id == "lolla_pressure_treatment":
                    expected_ids = [
                        str(item["pressure_id"])
                        for item in contract["treatment_pressure_packet"]
                    ]
                    if observed_ids != expected_ids:
                        errors.append(
                            f"{field} must cover treatment pressure IDs exactly "
                            "once in packet order"
                        )
                elif arm_id == "strong_reconsideration_control" and items:
                    errors.append(f"{field} must be empty in control arm")
    shifts = response.get("material_shifts", [])
    if not isinstance(shifts, list):
        errors.append("material_shifts must be an array")
    else:
        if len(shifts) > int(output["maximum_material_shifts"]):
            errors.append("material_shifts exceeds maximum")
        shift_required = set(output["material_shift_required_keys"])
        for index, shift in enumerate(shifts):
            if not isinstance(shift, dict) or set(shift) != shift_required:
                errors.append(f"material_shifts[{index}] has invalid shape")
    return errors


def _call_openrouter(
    spec: Mapping[str, Any], contract: Mapping[str, Any]
) -> dict[str, Any]:
    api_key = os.getenv("LOLLA_OPENROUTER_API_KEY") or os.getenv(
        "OPENROUTER_API_KEY"
    )
    if not api_key:
        raise PilotError("OPENROUTER_API_KEY is required")
    config = contract["call_configuration"]
    body = {
        "model": config["model"],
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
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with request.urlopen(
            req, timeout=float(config["timeout_seconds"])
        ) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        return {
            "blind_label": spec["blind_label"],
            "status": f"http_error_{exc.code}",
            "response": {},
            "validation_errors": [f"provider HTTP error {exc.code}"],
        }
    except (error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {
            "blind_label": spec["blind_label"],
            "status": "provider_error",
            "response": {},
            "validation_errors": [type(exc).__name__],
        }

    choices = payload.get("choices", [])
    message = choices[0].get("message", {}) if choices else {}
    raw = str(message.get("content", ""))
    parsed = _extract_json_object(raw)
    errors = _validate_response(
        parsed,
        contract,
        arm_id=str(spec["arm_id"]),
    )
    usage = payload.get("usage", {})
    return {
        "blind_label": spec["blind_label"],
        "status": "ok" if not errors else "invalid_contract",
        "response": parsed,
        "validation_errors": errors,
        "metadata": {
            "requested_model": config["model"],
            "served_model": payload.get("model", ""),
            "finish_reason": choices[0].get("finish_reason", "") if choices else "",
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
            "reasoning_tokens": usage.get("completion_tokens_details", {}).get(
                "reasoning_tokens", 0
            )
            if isinstance(usage.get("completion_tokens_details", {}), dict)
            else 0,
            "prompt_sha256": _sha256_text(str(spec["user_prompt"])),
            "response_sha256": _sha256_text(raw),
        },
    }


def run_pilot(contract: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    specs = build_call_specs(contract)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        outputs = list(
            executor.map(lambda spec: _call_openrouter(spec, contract), specs)
        )
    outputs.sort(key=lambda item: item["blind_label"])
    blind = {
        "schema_version": BLIND_SCHEMA,
        "case_id": contract["case"]["case_id"],
        "source_sha256": contract["case"]["source_sha256"],
        "review_status": "pending_provisional_and_human_review",
        "outputs": outputs,
        "non_claims": contract["non_claims"],
    }
    key = {
        "schema_version": KEY_SCHEMA,
        "mapping": [
            {"blind_label": spec["blind_label"], "arm_id": spec["arm_id"]}
            for spec in sorted(specs, key=lambda item: item["blind_label"])
        ],
    }
    from engine.system_b.pricing import (
        PRICES_LAST_VERIFIED,
        estimate_chat_cost_usd,
        lookup_chat_price,
    )

    prompt_tokens = sum(
        item.get("metadata", {}).get("prompt_tokens", 0) for item in outputs
    )
    completion_tokens = sum(
        item.get("metadata", {}).get("completion_tokens", 0) for item in outputs
    )
    price = lookup_chat_price("openrouter", contract["call_configuration"]["model"])
    estimated_cost = (
        estimate_chat_cost_usd(
            price=price,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )
        if price is not None
        else None
    )
    summary = {
        "schema_version": SUMMARY_SCHEMA,
        "case_id": contract["case"]["case_id"],
        "call_count": len(outputs),
        "successful_call_count": sum(item["status"] == "ok" for item in outputs),
        "invalid_or_failed_call_count": sum(item["status"] != "ok" for item in outputs),
        "total_tokens": sum(item.get("metadata", {}).get("total_tokens", 0) for item in outputs),
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "estimated_cost_usd": estimated_cost,
        "pricing_table_version": PRICES_LAST_VERIFIED,
        "review_status": "pending_provisional_and_human_review",
        "runtime_change_authorized": False,
        "semantic_kernel_integration_authorized": False,
    }
    return blind, key, summary


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    contract = _load_json(args.contract)
    specs = build_call_specs(contract)
    if args.dry_run:
        print(
            json.dumps(
                {
                    "status": "dry_run_valid",
                    "call_count": len(specs),
                    "prompt_hashes": [
                        {
                            "blind_label": spec["blind_label"],
                            "sha256": _sha256_text(spec["user_prompt"]),
                        }
                        for spec in specs
                    ],
                },
                indent=2,
            )
        )
        return 0
    if args.env_file:
        _load_env_file(args.env_file)
    blind, key, summary = run_pilot(contract)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    for name, payload in (
        ("blind-outputs.json", blind),
        ("arm-key.json", key),
        ("run-summary.json", summary),
    ):
        (args.out_dir / name).write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(summary, indent=2))
    return 0 if summary["successful_call_count"] == 2 else 1


if __name__ == "__main__":
    raise SystemExit(main())
