#!/usr/bin/env python3
"""Run one frozen fresh-case stance-object position probe via Gemini/OpenRouter."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any
from urllib import error, request

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.reasoning_process_chronological_shard_reader_v4 import (  # noqa: E402
    build_shard_prompts_v4,
    shard_response_schema_v4,
)
from engine.system_b.reasoning_process_views import canonical_json_bytes, sha256_bytes  # noqa: E402
from scripts.evals.run_conversation_state_microtask_probe import _load_env  # noqa: E402
from scripts.evals.run_reasoning_process_phase4_transfer import (  # noqa: E402
    MODEL,
    _error_headers,
    _json_sha,
    _load,
    _sha,
    _write,
)
from scripts.evals.run_fixed_safe_holdout_pool import _extract_json_object, _model_attribution  # noqa: E402
from scripts.evals.run_fixed_safe_holdout_pool_v2 import _provider_diagnostic  # noqa: E402
from scripts.evals.run_reasoning_process_view_specific_probe import _estimated_cost  # noqa: E402
from engine.system_b.reasoning_process_chronological_shard_reader_v4 import (  # noqa: E402
    compile_shard_response_recordwise_v4,
)

CONTRACT_SCHEMA = "lolla.reasoning_process_stance_object_v4_probe_contract.v1"
AUTH_SCHEMA = "lolla.reasoning_process_stance_object_v4_probe_authorization.v1"


def run_job_v4(*, contract: Mapping[str, Any], job: Mapping[str, Any], snapshot: Mapping[str, Any]) -> dict[str, Any]:
    started = time.monotonic()
    wrapper = _load(ROOT / str(job["packet_path"]))
    prompts = build_shard_prompts_v4(wrapper)
    schema = shard_response_schema_v4(str(job["view_kind"]))
    config = contract["call_configuration"]
    base = {
        "schema_version": "lolla.reasoning_process_stance_object_v4_probe_call.v1",
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
                "name": "lolla_reasoning_process_stance_object_v4",
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
        compiled = compile_shard_response_recordwise_v4(
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


def validate_contract(contract: dict, contract_path: Path) -> dict:
    if contract.get("schema_version") != CONTRACT_SCHEMA:
        raise RuntimeError("unexpected stance-object v4 probe contract")
    if contract.get("status") != "frozen_before_one_fresh_provider_call":
        raise RuntimeError("stance-object v4 probe contract is not frozen")
    for item in contract["frozen_inputs"]:
        if _sha(ROOT / item["path"]) != item["sha256"]:
            raise RuntimeError(f"frozen input drifted: {item['path']}")
    if _sha(ROOT / contract["model_snapshot"]["path"]) != contract["model_snapshot"]["sha256"]:
        raise RuntimeError("model snapshot drifted")
    job = contract["job"]
    packet_path = ROOT / job["packet_path"]
    if _sha(packet_path) != job["packet_sha256"]:
        raise RuntimeError("stance-object probe packet drifted")
    wrapper = _load(packet_path)
    prompts = build_shard_prompts_v4(wrapper)
    schema = shard_response_schema_v4(job["view_kind"])
    observed = {
        "system_prompt_sha256": prompts["system_prompt_sha256"],
        "user_prompt_sha256": prompts["user_prompt_sha256"],
        "response_schema_sha256": sha256_bytes(canonical_json_bytes(schema)),
    }
    if any(job[key] != value for key, value in observed.items()):
        raise RuntimeError("stance-object probe prompt or schema drifted")
    if (
        job["case_id"] != "amb1-case04-research-tool-release"
        or job["mechanism"] != "chronological_shard_stance_object_v4"
        or job["view_kind"] != "position_and_decision_trajectory"
    ):
        raise RuntimeError("fresh-case or mechanism selection drifted")
    config = contract["call_configuration"]
    if (
        config["provider"] != "openrouter"
        or config["model"] != MODEL
        or config["allow_provider_fallbacks"] is not False
        or config["automatic_retries"] != 0
        or config["response_healing"] is not False
    ):
        raise RuntimeError("stance-object probe route or failure policy drifted")
    if contract["budget"] != {
        "maximum_provider_calls": 1,
        "maximum_estimated_cost_usd": 0.01,
        "automatic_retries": 0,
        "semantic_retries": 0,
        "fallback_models": 0,
        "evaluator_calls": 0,
        "embedding_calls": 0,
        "graph_calls": 0,
        "pipeline_calls": 0,
        "runtime_calls": 0,
    }:
        raise RuntimeError("stance-object probe budget drifted")
    return {
        "status": "stance_object_v4_probe_contract_valid",
        "contract_path": str(contract_path.relative_to(ROOT)),
        "provider_calls_made": 0,
    }


def validate_authorization(value: dict, *, contract: dict, contract_path: Path) -> None:
    expected = {
        "schema_version": AUTH_SCHEMA,
        "status": "authorized_once_after_provider_free_adversarial_and_cold_reader_gates",
        "contract_path": str(contract_path.relative_to(ROOT)),
        "contract_sha256": _sha(contract_path),
        "run_id": contract["run_id"],
        "maximum_provider_calls": 1,
        "automatic_retries": 0,
        "semantic_retries": 0,
        "fallback_models": 0,
        "evaluator_calls": 0,
        "embedding_calls": 0,
        "graph_calls": 0,
        "pipeline_calls": 0,
        "runtime_calls": 0,
    }
    if value != expected:
        raise RuntimeError("stance-object v4 probe authorization drifted")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    contract_path = args.contract.resolve()
    contract = _load(contract_path)
    validation = validate_contract(contract, contract_path)
    if args.dry_run:
        print(json.dumps(validation, indent=2, sort_keys=True))
        return 0
    if args.authorization is None or args.env_file is None or args.output is None:
        raise RuntimeError("execution arguments are missing")
    validate_authorization(
        _load(args.authorization.resolve()), contract=contract, contract_path=contract_path
    )
    output = args.output.resolve()
    if output.exists():
        raise RuntimeError("stance-object probe output already exists")
    _load_env(args.env_file.resolve())
    snapshot = _load(ROOT / contract["model_snapshot"]["path"])
    call = run_job_v4(contract=contract, job=contract["job"], snapshot=snapshot)
    result = {
        "schema_version": "lolla.reasoning_process_stance_object_v4_probe_result.v1",
        "status": "one_fresh_position_probe_call_preserved",
        "run_id": contract["run_id"],
        "call": call,
        "provider_request_count": call.get("provider_calls", 0),
        "semantic_review_status": "pending_source_first_review",
        "boundary": contract["boundary"],
    }
    _write(output, result)
    print(
        json.dumps(
            {
                "operational_status": call["operational_status"],
                "typed_status": call["typed_status"],
                "admitted_record_count": call.get("admitted_record_count", 0),
                "quarantined_record_count": call.get("quarantined_record_count", 0),
                "estimated_cost_usd": call.get("estimated_cost_usd"),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
