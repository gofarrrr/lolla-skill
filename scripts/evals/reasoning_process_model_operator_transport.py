"""Generic no-retry transport for versioned reasoning-process model/operator evals."""
from __future__ import annotations

import hashlib
import json
import os
import time
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any
from urllib import error, request

from scripts.evals.run_fixed_safe_holdout_pool import _extract_json_object, _model_attribution
from scripts.evals.run_fixed_safe_holdout_pool_v2 import _provider_diagnostic
from scripts.evals.run_reasoning_process_phase4_transfer import _error_headers


def _canonical_sha(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()


def run_model_operator_job(
    *,
    contract: Mapping[str, Any],
    job: Mapping[str, Any],
    wrapper: Mapping[str, Any],
    build_prompts: Callable[[Mapping[str, Any]], dict[str, str]],
    build_schema: Callable[[str], dict[str, Any]],
    compile_response: Callable[..., dict[str, Any]],
    response_schema_name: str,
) -> dict[str, Any]:
    """Run one exact model/provider pair and return full local custody metadata."""
    config = contract["call_configuration"]
    prompts = build_prompts(wrapper)
    schema = build_schema("position_and_decision_trajectory")
    started = time.monotonic()
    base = {
        "job_id": job["job_id"],
        "model": job["model"],
        "provider_slug": job["provider_slug"],
        "provider_display_name": job["provider_display_name"],
        "system_prompt_sha256": prompts["system_prompt_sha256"],
        "user_prompt_sha256": prompts["user_prompt_sha256"],
        "response_schema_sha256": _canonical_sha(schema),
        "temperature": config["temperature"],
        "seed": config["seed"],
        "automatic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
    }
    api_key = os.getenv("LOLLA_OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return {**base, "operational_status": "missing_api_key", "provider_calls": 0}
    body = {
        "model": job["model"],
        "messages": [
            {"role": "system", "content": prompts["system_prompt"]},
            {"role": "user", "content": prompts["user_prompt"]},
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": response_schema_name,
                "strict": True,
                "schema": schema,
            },
        },
        "provider": {
            "only": [job["provider_slug"]],
            "require_parameters": True,
            "allow_fallbacks": False,
        },
        "temperature": config["temperature"],
        "seed": config["seed"],
        "max_tokens": config["max_output_tokens"],
        "reasoning": {"enabled": config["reasoning_enabled"]},
    }
    req = request.Request(
        config["endpoint"],
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=config["provider_timeout_seconds"]) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        raw_error = exc.read().decode("utf-8", errors="replace")
        try:
            error_payload = json.loads(raw_error)
        except json.JSONDecodeError:
            error_payload = {"message": raw_error[:2000]}
        return {
            **base,
            "operational_status": f"http_error_{exc.code}",
            "http_status": exc.code,
            "provider_diagnostic": _provider_diagnostic(error_payload, []),
            "response_headers": _error_headers(exc),
            "provider_payload_sha256": _canonical_sha(error_payload),
            "provider_calls": 1,
            "duration_seconds": round(time.monotonic() - started, 3),
        }
    choices = payload.get("choices") if isinstance(payload.get("choices"), list) else []
    choice = choices[0] if choices and isinstance(choices[0], Mapping) else {}
    message = choice.get("message") if isinstance(choice.get("message"), Mapping) else {}
    raw_content = str(message.get("content", ""))
    served_model = str(payload.get("model", ""))
    served_provider = str(payload.get("provider", ""))
    usage = payload.get("usage") if isinstance(payload.get("usage"), Mapping) else {}
    candidate = None
    compiled = None
    validation_error = ""
    try:
        candidate = _extract_json_object(raw_content)
        if not isinstance(candidate, dict):
            raise RuntimeError("provider response is not an object")
        compiled = compile_response(
            response=candidate,
            wrapper=wrapper,
            producer_kind="model_operator_eval",
            producer_id=str(job["model"]),
            record_identity=str(job["job_id"]),
            call_metadata={
                "call_id": str(job["job_id"]),
                "model": served_model,
                "prompt_sha256": "sha256:" + prompts["user_prompt_sha256"],
            },
        )
    except Exception as exc:  # noqa: BLE001
        validation_error = f"{type(exc).__name__}: {exc}"
    custody = compiled.get("records", []) if compiled else []
    admitted = sum(item.get("terminal_state") == "admitted" for item in custody)
    quarantined = sum(item.get("terminal_state") == "quarantined" for item in custody)
    prompt_tokens = usage.get("prompt_tokens")
    completion_tokens = usage.get("completion_tokens")
    estimated_cost = None
    pricing = job["pricing_per_token"]
    if isinstance(prompt_tokens, int) and isinstance(completion_tokens, int):
        estimated_cost = round(
            prompt_tokens * float(pricing["prompt"])
            + completion_tokens * float(pricing["completion"]),
            12,
        )
    wire_accepted = bool(choices) and candidate is not None
    return {
        **base,
        "operational_status": "ok" if wire_accepted else "operational_failure",
        "wire_schema_accepted": wire_accepted,
        "json_schema_candidate_present": candidate is not None,
        "candidate_payload": candidate,
        "candidate_payload_sha256": _canonical_sha(candidate) if candidate else "",
        "compiled": compiled,
        "validation_error": validation_error,
        "deterministic_terminal_disposition": (
            compiled.get("shard_terminal_disposition") if compiled else "not_compiled"
        ),
        "admitted_record_count": admitted,
        "quarantined_record_count": quarantined,
        "served_model": served_model,
        "model_attribution_status": _model_attribution(str(job["model"]), served_model),
        "served_provider": served_provider,
        "provider_attribution_status": (
            "matched"
            if served_provider.lower() == str(job["provider_display_name"]).lower()
            else "mismatched_or_missing"
        ),
        "finish_reason": str(choice.get("finish_reason", "")),
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": usage.get("total_tokens"),
        "estimated_cost_usd": estimated_cost,
        "provider_reported_cost_usd": usage.get("cost"),
        "provider_payload_sha256": _canonical_sha(payload),
        "provider_diagnostic": _provider_diagnostic(payload, choices),
        "raw_provider_content_included": False,
        "provider_calls": 1,
        "evaluator_calls": 0,
        "embedding_calls": 0,
        "graph_calls": 0,
        "pipeline_calls": 0,
        "runtime_calls": 0,
        "duration_seconds": round(time.monotonic() - started, 3),
    }
