#!/usr/bin/env python3
"""Run one frozen transcript-only reconsideration control with no retries."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any
from urllib import error, request


OUTPUT_SCHEMA = "lolla.strong_reconsideration_control_result.v0"


class ControlError(RuntimeError):
    pass


def _load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ControlError(f"expected JSON object: {path}")
    return value


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_text(value: str) -> str:
    return _sha256_bytes(value.encode("utf-8"))


def _load_env_file(path: Path) -> None:
    if not path.is_file():
        raise ControlError(f"env file missing: {path}")
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value


def validate_contract(
    contract: Mapping[str, Any], *, repo_root: Path
) -> None:
    if contract.get("status") != "frozen_before_calls":
        raise ControlError("contract is not frozen_before_calls")
    control = contract.get("strong_control", {})
    config = control.get("call_configuration", {}) if isinstance(control, Mapping) else {}
    if config.get("generation_calls") != 1:
        raise ControlError("strong control must use exactly one generation call")
    if config.get("evaluator_calls") != 0:
        raise ControlError("strong control forbids evaluator calls")
    if config.get("automatic_retries") != 0:
        raise ControlError("strong control forbids automatic retries")
    if config.get("reasoning_effort") != "none":
        raise ControlError("strong control reasoning configuration drifted")
    case = contract.get("case", {})
    source_path = repo_root / str(case.get("source_path", ""))
    if not source_path.is_file():
        raise ControlError("source conversation missing")
    if _sha256_bytes(source_path.read_bytes()) != case.get("source_sha256"):
        raise ControlError("source conversation hash mismatch")


def build_prompt(contract: Mapping[str, Any], *, repo_root: Path) -> str:
    validate_contract(contract, repo_root=repo_root)
    case = contract["case"]
    control = contract["strong_control"]
    output = control["output_contract"]
    conversation = (repo_root / str(case["source_path"])).read_text(encoding="utf-8")
    required = ", ".join(str(item) for item in output["required_keys"])
    shift_required = ", ".join(
        str(item) for item in output["material_shift_required_keys"]
    )
    return "\n\n---\n\n".join(
        [
            "COMPLETE CONVERSATION\n\n" + conversation.strip(),
            "RECONSIDERATION TASK\n\n"
            + str(control["neutral_reconsideration_instruction"]).strip(),
            (
                "OUTPUT JSON\n\nReturn one JSON object with exactly these "
                f"top-level keys: {required}. material_shifts must contain at "
                f"most {int(output['maximum_material_shifts'])} objects and each "
                f"must have exactly these keys: {shift_required}."
            ),
        ]
    )


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


def validate_response(
    response: Mapping[str, Any], contract: Mapping[str, Any]
) -> list[str]:
    output = contract["strong_control"]["output_contract"]
    required = set(output["required_keys"])
    errors: list[str] = []
    missing = sorted(required - set(response))
    unknown = sorted(set(response) - required)
    if missing:
        errors.append(f"missing top-level keys: {missing}")
    if unknown:
        errors.append(f"unknown top-level keys: {unknown}")
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


def run_control(
    contract: Mapping[str, Any], *, repo_root: Path
) -> dict[str, Any]:
    user_prompt = build_prompt(contract, repo_root=repo_root)
    control = contract["strong_control"]
    config = control["call_configuration"]
    api_key = os.getenv("LOLLA_OPENROUTER_API_KEY") or os.getenv(
        "OPENROUTER_API_KEY"
    )
    if not api_key:
        raise ControlError("OPENROUTER_API_KEY is required")
    body = {
        "model": config["model"],
        "messages": [
            {"role": "system", "content": control["system_prompt"]},
            {"role": "user", "content": user_prompt},
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
            "schema_version": OUTPUT_SCHEMA,
            "status": f"http_error_{exc.code}",
            "response": {},
            "validation_errors": [f"provider HTTP error {exc.code}"],
            "call_count": 1,
            "automatic_retry_count": 0,
        }
    except (error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {
            "schema_version": OUTPUT_SCHEMA,
            "status": "provider_error",
            "response": {},
            "validation_errors": [type(exc).__name__],
            "call_count": 1,
            "automatic_retry_count": 0,
        }
    choices = payload.get("choices", [])
    message = choices[0].get("message", {}) if choices else {}
    raw = str(message.get("content", ""))
    parsed = _extract_json_object(raw)
    errors = validate_response(parsed, contract)
    usage = payload.get("usage", {})
    details = usage.get("completion_tokens_details", {})
    if not isinstance(details, Mapping):
        details = {}
    return {
        "schema_version": OUTPUT_SCHEMA,
        "status": "ok" if not errors else "invalid_contract",
        "case_id": contract["case"]["case_id"],
        "source_sha256": contract["case"]["source_sha256"],
        "response": parsed,
        "validation_errors": errors,
        "metadata": {
            "provider": "openrouter",
            "requested_model": config["model"],
            "served_model": payload.get("model", ""),
            "finish_reason": choices[0].get("finish_reason", "") if choices else "",
            "prompt_tokens": int(usage.get("prompt_tokens", 0) or 0),
            "completion_tokens": int(usage.get("completion_tokens", 0) or 0),
            "total_tokens": int(usage.get("total_tokens", 0) or 0),
            "reasoning_tokens": int(details.get("reasoning_tokens", 0) or 0),
            "system_prompt_sha256": _sha256_text(str(control["system_prompt"])),
            "user_prompt_sha256": _sha256_text(user_prompt),
            "raw_response_sha256": _sha256_text(raw),
        },
        "call_count": 1,
        "automatic_retry_count": 0,
        "evaluator_call_count": 0,
        "portfolio_context_received": False,
        "runtime_change_authorized": False,
    }


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    contract = _load_object(args.contract)
    if args.env_file:
        _load_env_file(args.env_file)
    prompt = build_prompt(contract, repo_root=args.repo_root)
    if args.dry_run:
        print(
            json.dumps(
                {
                    "status": "dry_run_valid",
                    "call_count": 1,
                    "user_prompt_sha256": _sha256_text(prompt),
                },
                indent=2,
            )
        )
        return 0
    result = run_control(contract, repo_root=args.repo_root)
    _write_json(args.output, result)
    print(json.dumps({key: result.get(key) for key in ("status", "call_count", "validation_errors")}, indent=2))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
