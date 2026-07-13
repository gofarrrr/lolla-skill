"""Shared deterministic transport for frozen structured chronological-shard probes."""
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
from scripts.evals.run_reasoning_process_phase4_transfer import (
    MODEL,
    _error_headers,
    _json_sha,
    _load,
)
from scripts.evals.run_reasoning_process_view_specific_probe import _estimated_cost


def run_structured_shard_job(
    *,
    root: Path,
    contract: Mapping[str, Any],
    job: Mapping[str, Any],
    snapshot: Mapping[str, Any],
    build_prompts: Callable[[Mapping[str, Any]], dict[str, str]],
    build_schema: Callable[[str], dict[str, Any]],
    compile_response: Callable[..., dict[str, Any]],
    call_schema: str,
    response_schema_name: str,
) -> dict[str, Any]:
    """Execute one no-retry strict-schema call and preserve raw custody metadata."""
    started = time.monotonic()
    wrapper = _load(root / str(job["packet_path"]))
    prompts = build_prompts(wrapper)
    schema = build_schema(str(job["view_kind"]))
    config = contract["call_configuration"]
    base = {
        "schema_version": call_schema,
        "run_id": contract["run_id"],
        "call_id": job["job_id"],
        "case_id": job["case_id"],
        "mechanism": job["mechanism"],
        "view_kind": job["view_kind"],
        "requested_model": MODEL,
        "packet_path": job["packet_path"],
        "packet_sha256": job["packet_sha256"],
        "system_prompt_sha256": prompts["system_prompt_sha256"],
        "user_prompt_sha256": prompts["user_prompt_sha256"],
        "response_schema_sha256": _json_sha(schema),
        "temperature": 0.0,
        "seed": 0,
        "automatic_retries": 0,
        "fallback_models": 0,
    }
    api_key = os.getenv("LOLLA_OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return {
            **base,
            "operational_status": "missing_api_key",
            "typed_status": "not_observed",
            "provider_calls": 0,
            "duration_seconds": round(time.monotonic() - started, 3),
        }
    body = {
        "model": MODEL,
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
        "provider": {"require_parameters": True, "allow_fallbacks": False},
        "temperature": 0.0,
        "seed": 0,
        "max_tokens": config["max_output_tokens"],
        "reasoning": {"enabled": False},
    }
    req = request.Request(
        config["endpoint"],
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=config["provider_timeout_seconds"]) as response:
            provider_payload = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        raw_error = exc.read().decode("utf-8", errors="replace")
        try:
            error_payload = json.loads(raw_error)
        except json.JSONDecodeError:
            error_payload = {"message": raw_error[:2000]}
        return {
            **base,
            "operational_status": f"http_error_{exc.code}",
            "operational_error_type": "HTTPError",
            "http_status": exc.code,
            "response_headers": _error_headers(exc),
            "typed_status": "not_observed",
            "provider_diagnostic": _provider_diagnostic(error_payload, []),
            "provider_payload_sha256": _json_sha(error_payload),
            "provider_calls": 1,
            "duration_seconds": round(time.monotonic() - started, 3),
        }
    except Exception as exc:  # noqa: BLE001
        return {
            **base,
            "operational_status": "provider_error",
            "operational_error_type": type(exc).__name__,
            "typed_status": "not_observed",
            "provider_calls": 1,
            "duration_seconds": round(time.monotonic() - started, 3),
        }
    choices_raw = provider_payload.get("choices")
    choices = choices_raw if isinstance(choices_raw, list) else []
    choice = choices[0] if choices and isinstance(choices[0], Mapping) else {}
    message = choice.get("message") if isinstance(choice.get("message"), Mapping) else {}
    raw_content = str(message.get("content", ""))
    finish_reason = str(choice.get("finish_reason", ""))
    usage_raw = provider_payload.get("usage")
    usage = usage_raw if isinstance(usage_raw, Mapping) else {}
    prompt_tokens = usage.get("prompt_tokens")
    completion_tokens = usage.get("completion_tokens")
    total_tokens = usage.get("total_tokens")
    usage_complete = all(
        isinstance(value, int) and value > 0
        for value in (prompt_tokens, completion_tokens, total_tokens)
    )
    served_model = str(provider_payload.get("model", ""))
    attribution = _model_attribution(MODEL, served_model)
    operational_ok = (
        bool(choices)
        and finish_reason.lower() != "error"
        and usage_complete
        and attribution in {"matched", "served_version_alias"}
    )
    candidate_payload: dict[str, Any] | None = None
    compiled: dict[str, Any] | None = None
    validation_error = ""
    try:
        parsed = _extract_json_object(raw_content)
        if not isinstance(parsed, dict):
            raise RuntimeError("provider response is not an object")
        candidate_payload = parsed
        compiled = compile_response(
            response=parsed,
            wrapper=wrapper,
            producer_kind="model",
            producer_id=MODEL,
            record_identity=f"probe-{job['job_id']}",
            call_metadata={
                "call_id": job["job_id"],
                "model": served_model,
                "prompt_sha256": "sha256:" + prompts["user_prompt_sha256"],
            },
        )
    except Exception as exc:  # noqa: BLE001
        validation_error = f"{type(exc).__name__}: {exc}"
    custody = compiled.get("records", []) if compiled else []
    admitted = sum(item.get("terminal_state") == "admitted" for item in custody)
    quarantined = sum(item.get("terminal_state") == "quarantined" for item in custody)
    if operational_ok and compiled is not None:
        typed_status = (
            "admitted_with_quarantine"
            if admitted and quarantined
            else "quarantined"
            if quarantined and not admitted
            else "admitted"
        )
    else:
        typed_status = "quarantined"
    cached_tokens = 0
    details = usage.get("prompt_tokens_details")
    if isinstance(details, Mapping) and isinstance(details.get("cached_tokens"), int):
        cached_tokens = int(details["cached_tokens"])
    estimated_cost = (
        _estimated_cost(
            snapshot=snapshot,
            prompt_tokens=int(prompt_tokens),
            completion_tokens=int(completion_tokens),
            cached_tokens=cached_tokens,
        )
        if usage_complete
        else None
    )
    return {
        **base,
        "operational_status": "ok" if operational_ok else "operational_failure",
        "typed_status": typed_status,
        "validation_error": validation_error,
        "candidate_payload": candidate_payload,
        "candidate_payload_sha256": _json_sha(candidate_payload) if candidate_payload else "",
        "compiled": compiled,
        "admitted_record_count": admitted,
        "quarantined_record_count": quarantined,
        "served_model": served_model,
        "model_attribution_status": attribution,
        "finish_reason": finish_reason,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "cached_prompt_tokens": cached_tokens,
        "usage_evidence_state": "complete" if usage_complete else "unknown",
        "estimated_cost_usd": estimated_cost,
        "provider_reported_cost_usd": usage.get("cost"),
        "pricing_snapshot_sha256": _json_sha(snapshot),
        "response_sha256": hashlib.sha256(raw_content.encode("utf-8")).hexdigest(),
        "provider_payload_sha256": _json_sha(provider_payload),
        "provider_diagnostic": _provider_diagnostic(provider_payload, choices),
        "raw_provider_content_included": False,
        "provider_calls": 1,
        "evaluator_calls": 0,
        "embedding_calls": 0,
        "graph_calls": 0,
        "pipeline_calls": 0,
        "runtime_calls": 0,
        "duration_seconds": round(time.monotonic() - started, 3),
    }
