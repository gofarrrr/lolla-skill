#!/usr/bin/env python3
"""Run the frozen three-arm Case 07 semantic-overlay counterfactual."""
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


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

RUN_CONTRACT_SCHEMA = "lolla.semantic_overlay_counterfactual_run_contract.v0"
BLIND_SCHEMA = "lolla.semantic_overlay_counterfactual_blind_outputs.v0"
KEY_SCHEMA = "lolla.semantic_overlay_counterfactual_arm_key.v0"
SUMMARY_SCHEMA = "lolla.semantic_overlay_counterfactual_run_summary.v0"


class CounterfactualError(RuntimeError):
    pass


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CounterfactualError(f"expected JSON object: {path}")
    return value


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_text(value: str) -> str:
    return _sha256_bytes(value.encode("utf-8"))


def _require_hash(path: Path, expected: str, label: str) -> None:
    if not path.is_file() or _sha256_bytes(path.read_bytes()) != expected:
        raise CounterfactualError(f"{label} missing or hash mismatch")


def _load_env_file(path: Path) -> None:
    if not path.is_file():
        raise CounterfactualError(f"env file missing: {path}")
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip() and key.strip() not in os.environ:
            os.environ[key.strip()] = value.strip().strip("'\"")


def validate_run_contract(contract: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    if contract.get("schema_version") != RUN_CONTRACT_SCHEMA:
        raise CounterfactualError("unexpected run contract schema")
    if contract.get("status") != "frozen_before_calls":
        raise CounterfactualError("run contract is not frozen")
    config = contract.get("call_configuration", {})
    if config.get("total_generation_calls") != 3:
        raise CounterfactualError("counterfactual must use exactly three calls")
    if config.get("samples_per_arm") != 1 or config.get("evaluator_calls") != 0:
        raise CounterfactualError("counterfactual call budget drifted")
    if config.get("automatic_retries") != 0:
        raise CounterfactualError("counterfactual forbids retries")

    design_ref = contract["design_contract"]
    design_path = REPO_ROOT / design_ref["path"]
    _require_hash(design_path, design_ref["sha256"], "design contract")
    design = _load_json(design_path)
    packet_ref = contract["packets"]
    packet_path = REPO_ROOT / packet_ref["path"]
    _require_hash(packet_path, packet_ref["sha256"], "packet")
    packets = _load_json(packet_path)
    if packets.get("status") != "packets_built_no_model_calls":
        raise CounterfactualError("packet status drifted")
    if len(design.get("arms", [])) != 3:
        raise CounterfactualError("design arm count drifted")
    return design, packets


def _render_events(events: list[Mapping[str, Any]]) -> str:
    lines = []
    for event in events:
        lines.append(
            "- [{family} | {role} | turn {turn_index} {speaker}] {quote}".format(
                family=event["family"],
                role=event["role"],
                turn_index=event["turn_index"],
                speaker=event["speaker"],
                quote=event["quote"],
            )
        )
    return "\n".join(lines)


def build_call_specs(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    design, packets = validate_run_contract(contract)
    source_path = REPO_ROOT / design["case"]["source_path"]
    conversation = source_path.read_text(encoding="utf-8").strip()
    actual_events = list(packets["actual_overlay"]["events"])
    oracle_events = list(packets["reviewed_oracle_addition"]["events"])
    labels = ["A", "B", "C"]
    random.Random(str(contract["blind_label_seed"])).shuffle(labels)
    specs: list[dict[str, Any]] = []
    for label, arm in zip(labels, design["arms"], strict=True):
        arm_id = arm["arm_id"]
        events: list[Mapping[str, Any]] = []
        if arm_id == "actual_sk3_overlay":
            events = actual_events
        elif arm_id == "actual_sk3_plus_reviewed_omission_oracle":
            events = [*actual_events, *oracle_events]
        elif arm_id != "strong_fresh_reconsideration_control":
            raise CounterfactualError(f"unknown arm: {arm_id}")

        sections = ["COMPLETE CONVERSATION\n\n" + conversation]
        if events:
            sections.append(
                "PROVISIONAL SEMANTIC NAVIGATION\n\n"
                "These are source-linked attention cues, not conclusions. The full "
                "conversation remains authoritative.\n\n"
                + _render_events(events)
            )
        sections.extend(
            [
                "RECONSIDERATION TASK\n\n"
                + str(contract["neutral_reconsideration_instruction"]),
                "OUTPUT JSON\n\n"
                "Return exactly these top-level keys: decision_state_read "
                "(string), updated_position (string), what_survived (array of "
                "strings), take_backs_or_set_aside (array of strings), "
                "material_shifts (array of at most four objects with shift, "
                "source_basis, and action_consequence strings), next_actions "
                "(array of strings), and uncertainties (array of strings).",
            ]
        )
        specs.append(
            {
                "blind_label": label,
                "arm_id": arm_id,
                "overlay_event_count": len(events),
                "system_prompt": str(contract["system_prompt"]),
                "user_prompt": "\n\n---\n\n".join(sections),
            }
        )
    return specs


def _extract_json(text: str) -> dict[str, Any]:
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


def _validate_output(value: Mapping[str, Any], contract: Mapping[str, Any]) -> list[str]:
    output = contract["output_contract"]
    required = set(output["required_keys"])
    errors: list[str] = []
    if set(value) != required:
        errors.append(
            f"top-level key mismatch missing={sorted(required-set(value))} "
            f"unknown={sorted(set(value)-required)}"
        )
    shifts = value.get("material_shifts", [])
    if not isinstance(shifts, list):
        errors.append("material_shifts must be an array")
    else:
        if len(shifts) > int(output["maximum_material_shifts"]):
            errors.append("material_shifts exceeds maximum")
        required_shift = set(output["material_shift_required_keys"])
        for index, item in enumerate(shifts):
            if not isinstance(item, dict) or set(item) != required_shift:
                errors.append(f"material_shifts[{index}] has invalid shape")
    return errors


def _call(spec: Mapping[str, Any], contract: Mapping[str, Any]) -> dict[str, Any]:
    api_key = os.getenv("LOLLA_OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise CounterfactualError("OPENROUTER_API_KEY is required")
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
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=float(config["timeout_seconds"])) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        return {"blind_label": spec["blind_label"], "status": f"http_error_{exc.code}", "response": {}, "validation_errors": [f"provider HTTP error {exc.code}"]}
    except (error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {"blind_label": spec["blind_label"], "status": "provider_error", "response": {}, "validation_errors": [type(exc).__name__]}
    choices = payload.get("choices", [])
    message = choices[0].get("message", {}) if choices else {}
    raw = str(message.get("content", ""))
    parsed = _extract_json(raw)
    errors = _validate_output(parsed, contract)
    usage = payload.get("usage", {})
    completion_details = usage.get("completion_tokens_details", {})
    if not isinstance(completion_details, dict):
        completion_details = {}
    return {
        "blind_label": spec["blind_label"],
        "status": "ok" if not errors else "invalid_contract",
        "response": parsed,
        "validation_errors": errors,
        "metadata": {
            "requested_model": config["model"],
            "served_model": payload.get("model", ""),
            "finish_reason": choices[0].get("finish_reason", "") if choices else "",
            "overlay_event_count": spec["overlay_event_count"],
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
            "reasoning_tokens": completion_details.get("reasoning_tokens", 0),
            "prompt_sha256": _sha256_text(str(spec["user_prompt"])),
            "response_sha256": _sha256_text(raw),
        },
    }


def run_counterfactual(contract: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    from engine.system_b.pricing import PRICES_LAST_VERIFIED, estimate_chat_cost_usd, lookup_chat_price

    specs = build_call_specs(contract)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        outputs = list(executor.map(lambda spec: _call(spec, contract), specs))
    outputs.sort(key=lambda item: item["blind_label"])
    blind = {
        "schema_version": BLIND_SCHEMA,
        "case_id": "case-07-messy-linked-decisions",
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
    prompt_tokens = sum(item.get("metadata", {}).get("prompt_tokens", 0) for item in outputs)
    completion_tokens = sum(item.get("metadata", {}).get("completion_tokens", 0) for item in outputs)
    price = lookup_chat_price("openrouter", contract["call_configuration"]["model"])
    cost = estimate_chat_cost_usd(price=price, prompt_tokens=prompt_tokens, completion_tokens=completion_tokens) if price else None
    summary = {
        "schema_version": SUMMARY_SCHEMA,
        "case_id": "case-07-messy-linked-decisions",
        "call_count": len(outputs),
        "successful_call_count": sum(item["status"] == "ok" for item in outputs),
        "invalid_or_failed_call_count": sum(item["status"] != "ok" for item in outputs),
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": sum(item.get("metadata", {}).get("total_tokens", 0) for item in outputs),
        "estimated_cost_usd": cost,
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
        print(json.dumps({"status": "dry_run_valid", "call_count": len(specs), "specs": [{"blind_label": spec["blind_label"], "overlay_event_count": spec["overlay_event_count"], "prompt_sha256": _sha256_text(spec["user_prompt"])} for spec in specs]}, indent=2))
        return 0
    if args.env_file:
        _load_env_file(args.env_file)
    blind, key, summary = run_counterfactual(contract)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    for name, payload in (("blind-outputs.json", blind), ("arm-key.json", key), ("run-summary.json", summary)):
        (args.out_dir / name).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0 if summary["successful_call_count"] == 3 else 1


if __name__ == "__main__":
    raise SystemExit(main())
