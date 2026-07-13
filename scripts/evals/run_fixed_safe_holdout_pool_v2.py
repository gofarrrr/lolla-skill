#!/usr/bin/env python3
"""Prospective v2 pool runner with supported reasoning and error custody."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import time
from typing import Any, Callable, Mapping, Sequence
from urllib import error, request

from scripts.evals import run_fixed_safe_holdout_pool as v1


CONTRACT_SCHEMA = "lolla.fixed_safe_holdout_pool_generation_contract.v2"


def _shadow_v1_contract(contract: Mapping[str, Any]) -> dict[str, Any]:
    shadow = dict(contract)
    shadow["schema_version"] = v1.CONTRACT_SCHEMA
    config = dict(contract["call_configuration"])
    config["reasoning_effort"] = "none"
    shadow["call_configuration"] = config
    return shadow


def validate_contract(contract: Mapping[str, Any]) -> None:
    if contract.get("schema_version") != CONTRACT_SCHEMA:
        raise v1.HoldoutPoolError("unexpected v2 pool contract schema")
    config = contract.get("call_configuration", {})
    if config.get("model") != "google/gemini-3.1-flash-lite":
        raise v1.HoldoutPoolError("v2 repair is scoped to the frozen Gemini model")
    if config.get("reasoning_effort") != "minimal":
        raise v1.HoldoutPoolError("v2 Gemini reasoning effort must be minimal")
    repair = contract.get("operational_repair", {})
    if repair.get("semantic_prompt_changed") is not False:
        raise v1.HoldoutPoolError("v2 repair must not change semantic prompts")
    if repair.get("selection_contract_changed") is not False:
        raise v1.HoldoutPoolError("v2 repair must not change selection")
    if repair.get("automatic_retry_of_v1") is not False:
        raise v1.HoldoutPoolError("v2 must be a new prospective run, not a retry")
    v1.validate_contract(_shadow_v1_contract(contract))
    if contract.get("prompt_hashes") != v1._prompt_hashes(contract):
        raise v1.HoldoutPoolError("v2 prompt hashes drifted")


def _json_hash(value: object) -> str:
    return v1._hash_text(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    )


def _provider_diagnostic(payload: Mapping[str, Any], choices: list[Any]) -> dict[str, Any]:
    candidates = [payload.get("error")]
    if choices and isinstance(choices[0], Mapping):
        candidates.append(choices[0].get("error"))
        message = choices[0].get("message")
        if isinstance(message, Mapping):
            candidates.append(message.get("refusal"))
    for value in candidates:
        if isinstance(value, Mapping):
            diagnostic = {}
            for key in ("code", "message", "type", "provider_name"):
                item = value.get(key)
                if isinstance(item, (str, int, float, bool)):
                    diagnostic[key] = item
            metadata = value.get("metadata")
            if isinstance(metadata, Mapping):
                diagnostic["metadata"] = {
                    str(key): item
                    for key, item in metadata.items()
                    if isinstance(item, (str, int, float, bool))
                }
            if diagnostic:
                return diagnostic
        elif isinstance(value, str) and value.strip():
            return {"message": value.strip()}
    return {}


def _call_openrouter(contract: Mapping[str, Any]) -> dict[str, Any]:
    started = time.monotonic()
    config = contract["call_configuration"]
    prompts = v1.build_prompts(contract)
    requested_model = str(config["model"])
    base = {
        "call_attempted": True,
        "requested_model": requested_model,
        "system_prompt_sha256": v1._hash_text(prompts["system_prompt"]),
        "user_prompt_sha256": v1._hash_text(prompts["user_prompt"]),
        "reasoning_effort_requested": config["reasoning_effort"],
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
            "provider_diagnostic": {},
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
        body_text = exc.read().decode("utf-8", errors="replace")
        try:
            error_payload = json.loads(body_text)
        except json.JSONDecodeError:
            error_payload = {"message": body_text[:1000]}
        return {
            **base,
            "status": f"http_error_{exc.code}",
            "response": {},
            "validation_errors": [f"provider HTTP error {exc.code}"],
            "served_model": "",
            "model_attribution_status": "not_observed",
            "usage_evidence_state": "unknown",
            "provider_diagnostic": _provider_diagnostic(error_payload, []),
            "provider_payload_sha256": _json_hash(error_payload),
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
            "provider_diagnostic": {"type": type(exc).__name__},
            "duration_seconds": round(time.monotonic() - started, 3),
        }
    choices_raw = provider_payload.get("choices", [])
    choices = choices_raw if isinstance(choices_raw, list) else []
    choice = choices[0] if choices and isinstance(choices[0], Mapping) else {}
    message = choice.get("message", {}) if isinstance(choice, Mapping) else {}
    raw = str(message.get("content", "")) if isinstance(message, Mapping) else ""
    parsed = v1._extract_json_object(raw)
    validation_errors = v1._validate_payload(parsed, contract)
    finish_reason = str(choice.get("finish_reason", ""))
    diagnostic = _provider_diagnostic(provider_payload, choices)
    if finish_reason == "error":
        validation_errors.insert(0, "provider returned finish_reason=error")
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
        "model_attribution_status": v1._model_attribution(requested_model, served_model),
        "finish_reason": finish_reason,
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
        "response_sha256": v1._hash_text(raw),
        "provider_payload_sha256": _json_hash(provider_payload),
        "provider_diagnostic": diagnostic,
        "raw_provider_content_included": False,
        "duration_seconds": round(time.monotonic() - started, 3),
    }


def run_pool_generation(
    contract: Mapping[str, Any],
    *,
    call_fn: Callable[[Mapping[str, Any]], dict[str, Any]] = _call_openrouter,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    validate_contract(contract)
    shadow = _shadow_v1_contract(contract)
    return v1.run_pool_generation(shadow, call_fn=lambda _: call_fn(contract))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    contract = v1._load_object(args.contract)
    validate_contract(contract)
    if args.dry_run:
        print(
            json.dumps(
                {
                    "status": "dry_run_valid",
                    "run_id": contract["run_id"],
                    "call_count": 1,
                    "prompt_hashes": contract["prompt_hashes"],
                    "reasoning_effort": contract["call_configuration"][
                        "reasoning_effort"
                    ],
                    "ranked_case_ids": contract["selection_contract"][
                        "ranked_case_ids"
                    ],
                    "provider_calls": 0,
                },
                indent=2,
            )
        )
        return 0
    if args.env_file is None:
        raise v1.HoldoutPoolError("--env-file is required for execution")
    contract = dict(contract)
    contract["contract_sha256_at_execution"] = v1._hash_file(args.contract)
    v1._load_env_file(args.env_file)
    output_dir = v1._repo_path(
        contract["artifacts"]["output_dir"], label="output dir"
    )
    if output_dir.exists():
        raise v1.HoldoutPoolError("pool output directory already exists")
    output_dir.mkdir(parents=True)
    pool, custody, summary = run_pool_generation(contract)
    summary["gates"]["output_directory_absent_before_run"] = True
    summary["failed_gates"] = [
        name for name, passed in summary["gates"].items() if not passed
    ]
    summary["status"] = "passed" if not summary["failed_gates"] else "failed"
    case_dir = v1._repo_path(contract["artifacts"]["case_dir"], label="case dir")
    for case in pool["cases"]:
        v1._write_text_atomic(
            v1._repo_path(case["conversation_path"], label="conversation path"),
            v1._render_conversation(case),
        )
    v1._write_json_atomic(
        v1._repo_path(contract["artifacts"]["pool_path"], label="pool path"), pool
    )
    v1._write_json_atomic(
        v1._repo_path(
            contract["artifacts"]["call_custody_path"], label="call custody path"
        ),
        custody,
    )
    v1._write_json_atomic(
        v1._repo_path(contract["artifacts"]["run_summary_path"], label="run summary path"),
        summary,
    )
    print(json.dumps(summary, indent=2))
    return 0 if summary["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
