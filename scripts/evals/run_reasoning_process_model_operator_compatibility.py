#!/usr/bin/env python3
"""Run a frozen, provider-pinned v4.2 schema compatibility comparison."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from collections.abc import Mapping
from pathlib import Path
from urllib import error, request

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.reasoning_process_chronological_shard_reader_v42 import (  # noqa: E402
    build_shard_prompts_v42,
    compile_shard_response_recordwise_v42,
    shard_response_schema_v42,
)
from engine.system_b.reasoning_process_views import canonical_json_bytes, sha256_bytes  # noqa: E402
from scripts.evals.run_conversation_state_microtask_probe import _load_env  # noqa: E402
from scripts.evals.run_fixed_safe_holdout_pool import _extract_json_object, _model_attribution  # noqa: E402
from scripts.evals.run_fixed_safe_holdout_pool_v2 import _provider_diagnostic  # noqa: E402
from scripts.evals.run_reasoning_process_phase4_transfer import _error_headers, _load, _sha, _write  # noqa: E402

CONTRACT_SCHEMA = "lolla.reasoning_process_model_operator_compatibility_contract.v1"
AUTH_SCHEMA = "lolla.reasoning_process_model_operator_compatibility_authorization.v1"


def _json_sha(value: object) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def validate_contract(contract: dict, contract_path: Path) -> dict:
    if contract.get("schema_version") != CONTRACT_SCHEMA:
        raise RuntimeError("unexpected model/operator compatibility contract")
    if contract.get("status") != "frozen_before_two_synthetic_compatibility_calls":
        raise RuntimeError("model/operator compatibility contract is not frozen")
    for item in contract["frozen_inputs"]:
        if _sha(ROOT / item["path"]) != item["sha256"]:
            raise RuntimeError(f"frozen input drifted: {item['path']}")
    packet_path = ROOT / contract["packet"]["path"]
    if _sha(packet_path) != contract["packet"]["sha256"]:
        raise RuntimeError("synthetic compatibility packet drifted")
    wrapper = _load(packet_path)
    prompts = build_shard_prompts_v42(wrapper)
    schema = shard_response_schema_v42("position_and_decision_trajectory")
    observed = {
        "system_prompt_sha256": prompts["system_prompt_sha256"],
        "user_prompt_sha256": prompts["user_prompt_sha256"],
        "response_schema_sha256": sha256_bytes(canonical_json_bytes(schema)),
    }
    if any(contract["request_contract"][key] != value for key, value in observed.items()):
        raise RuntimeError("compatibility prompt or schema drifted")
    jobs = contract.get("jobs")
    if not isinstance(jobs, list) or len(jobs) != 2:
        raise RuntimeError("exactly two compatibility jobs are required")
    expected = {
        ("deepseek/deepseek-v4-flash", "deepinfra"),
        ("z-ai/glm-5.2", "deepinfra"),
    }
    if {(job["model"], job["provider_slug"]) for job in jobs} != expected:
        raise RuntimeError("compatibility shortlist drifted")
    config = contract["call_configuration"]
    if config != {
        "provider": "openrouter",
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "wire_mode": "strict_json_schema",
        "temperature": 0.0,
        "seed": 0,
        "reasoning_enabled": False,
        "max_output_tokens": 1600,
        "provider_timeout_seconds": 90,
        "require_supported_parameters": True,
        "allow_provider_fallbacks": False,
        "automatic_retries": 0,
        "response_healing": False,
        "parallel_calls": False,
    }:
        raise RuntimeError("compatibility call configuration drifted")
    if contract["budget"]["maximum_provider_calls"] != 2:
        raise RuntimeError("compatibility call budget drifted")
    return {
        "status": "model_operator_compatibility_contract_valid",
        "contract_path": str(contract_path.relative_to(ROOT)),
        "provider_calls_made": 0,
    }


def validate_authorization(value: dict, *, contract: dict, contract_path: Path) -> None:
    expected = {
        "schema_version": AUTH_SCHEMA,
        "status": "authorized_once_for_two_synthetic_provider_pinned_calls",
        "contract_path": str(contract_path.relative_to(ROOT)),
        "contract_sha256": _sha(contract_path),
        "run_id": contract["run_id"],
        "maximum_provider_calls": 2,
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
        raise RuntimeError("model/operator compatibility authorization drifted")


def _run_job(*, contract: Mapping[str, object], job: Mapping[str, object], wrapper: dict) -> dict:
    config = contract["call_configuration"]
    assert isinstance(config, Mapping)
    prompts = build_shard_prompts_v42(wrapper)
    schema = shard_response_schema_v42("position_and_decision_trajectory")
    started = time.monotonic()
    base = {
        "job_id": job["job_id"],
        "model": job["model"],
        "provider_slug": job["provider_slug"],
        "provider_display_name": job["provider_display_name"],
        "system_prompt_sha256": prompts["system_prompt_sha256"],
        "user_prompt_sha256": prompts["user_prompt_sha256"],
        "response_schema_sha256": _json_sha(schema),
        "temperature": 0.0,
        "seed": 0,
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
                "name": "lolla_reasoning_process_stance_object_v42_compatibility",
                "strict": True,
                "schema": schema,
            },
        },
        "provider": {
            "only": [job["provider_slug"]],
            "require_parameters": True,
            "allow_fallbacks": False,
        },
        "temperature": 0.0,
        "seed": 0,
        "max_tokens": config["max_output_tokens"],
        "reasoning": {"enabled": False},
    }
    req = request.Request(
        str(config["endpoint"]),
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=int(config["provider_timeout_seconds"])) as response:
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
            "provider_payload_sha256": _json_sha(error_payload),
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
        compiled = compile_shard_response_recordwise_v42(
            response=candidate,
            wrapper=wrapper,
            producer_kind="synthetic_compatibility_probe",
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
    pricing = job["pricing_per_token"]
    estimated_cost = None
    if isinstance(prompt_tokens, int) and isinstance(completion_tokens, int):
        estimated_cost = round(
            prompt_tokens * float(pricing["prompt"])
            + completion_tokens * float(pricing["completion"]),
            12,
        )
    model_match = _model_attribution(str(job["model"]), served_model)
    provider_match = served_provider.lower() == str(job["provider_display_name"]).lower()
    wire_accepted = bool(choices) and candidate is not None
    strict_generation_pass = compiled is not None and not validation_error
    return {
        **base,
        "operational_status": "ok" if wire_accepted else "operational_failure",
        "wire_schema_accepted": wire_accepted,
        "strict_schema_generation_pass": strict_generation_pass,
        "candidate_payload": candidate,
        "candidate_payload_sha256": _json_sha(candidate) if candidate else "",
        "compiled": compiled,
        "validation_error": validation_error,
        "admitted_record_count": admitted,
        "quarantined_record_count": quarantined,
        "served_model": served_model,
        "model_attribution_status": model_match,
        "served_provider": served_provider,
        "provider_attribution_status": "matched" if provider_match else "mismatched_or_missing",
        "finish_reason": str(choice.get("finish_reason", "")),
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": usage.get("total_tokens"),
        "estimated_cost_usd": estimated_cost,
        "provider_reported_cost_usd": usage.get("cost"),
        "provider_payload_sha256": _json_sha(payload),
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
        raise RuntimeError("model/operator compatibility output already exists")
    _load_env(args.env_file.resolve())
    wrapper = _load(ROOT / contract["packet"]["path"])
    results = [_run_job(contract=contract, job=job, wrapper=wrapper) for job in contract["jobs"]]
    result = {
        "schema_version": "lolla.reasoning_process_model_operator_compatibility_result.v1",
        "status": "two_synthetic_provider_pinned_calls_preserved",
        "run_id": contract["run_id"],
        "calls": results,
        "provider_request_count": sum(item.get("provider_calls", 0) for item in results),
        "wire_accepted_count": sum(item.get("wire_schema_accepted") is True for item in results),
        "strict_generation_pass_count": sum(
            item.get("strict_schema_generation_pass") is True for item in results
        ),
        "semantic_review_status": "not_applicable_synthetic_compatibility_only",
        "boundary": contract["boundary"],
    }
    _write(output, result)
    print(
        json.dumps(
            {
                "provider_request_count": result["provider_request_count"],
                "wire_accepted_count": result["wire_accepted_count"],
                "strict_generation_pass_count": result["strict_generation_pass_count"],
                "calls": [
                    {
                        "job_id": item["job_id"],
                        "operational_status": item["operational_status"],
                        "wire_schema_accepted": item.get("wire_schema_accepted", False),
                        "strict_schema_generation_pass": item.get(
                            "strict_schema_generation_pass", False
                        ),
                        "estimated_cost_usd": item.get("estimated_cost_usd"),
                    }
                    for item in results
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
