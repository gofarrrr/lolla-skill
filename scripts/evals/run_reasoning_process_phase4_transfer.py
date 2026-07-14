#!/usr/bin/env python3
"""Execute the frozen Phase-4 transfer through Gemini on OpenRouter."""
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

from engine.system_b.conversation_state_candidates import build_source_catalog  # noqa: E402
from engine.system_b.reasoning_process_exploration_local import (  # noqa: E402
    build_local_prompts,
    local_response_schema,
)
from engine.system_b.reasoning_process_exploration_local_custody import (  # noqa: E402
    compile_local_response_recordwise,
)
from engine.system_b.reasoning_process_chronological_shard_reader import (  # noqa: E402
    build_shard_prompts,
    compile_shard_response_recordwise,
    shard_response_schema,
)
from engine.system_b.reasoning_process_chronological_shard_reader_v2 import (  # noqa: E402
    build_shard_prompts_v2,
    compile_shard_response_recordwise_v2,
    shard_response_schema_v2,
)
from engine.system_b.reasoning_process_chronological_shard_reader_v3 import (  # noqa: E402
    build_shard_prompts_v3,
    compile_shard_response_recordwise_v3,
    shard_response_schema_v3,
)
from engine.system_b.reasoning_process_view_specific_v3 import (  # noqa: E402
    build_prompts_v3,
    compile_response_v3_recordwise,
    response_schema_v3,
)
from engine.system_b.reasoning_process_views import canonical_json_bytes, sha256_bytes  # noqa: E402
from scripts.evals.build_reasoning_process_phase4_transfer import (  # noqa: E402
    MODEL,
    SCHEMA,
    validate_contract,
)
from scripts.evals.run_conversation_state_microtask_probe import _load_env  # noqa: E402
from scripts.evals.run_fixed_safe_holdout_pool import _extract_json_object, _model_attribution  # noqa: E402
from scripts.evals.run_fixed_safe_holdout_pool_v2 import _provider_diagnostic  # noqa: E402
from scripts.evals.run_reasoning_process_view_specific_probe import _estimated_cost  # noqa: E402

AUTH_SCHEMA = "lolla.reasoning_process_phase4_transfer_authorization.v1"
CALL_SCHEMA = "lolla.reasoning_process_phase4_transfer_call.v1"
RESULT_SCHEMA = "lolla.reasoning_process_phase4_transfer_result.v1"


class Phase4TransferError(RuntimeError):
    pass


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise Phase4TransferError(f"expected object: {path}")
    return value


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json_sha(value: object) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def _repo_path(raw: str) -> Path:
    path = (ROOT / raw).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise Phase4TransferError("contract path escapes repository") from exc
    return path


def validate_authorization(authorization: Mapping[str, Any], contract_path: Path, contract: Mapping[str, Any]) -> None:
    expected = {
        "schema_version": AUTH_SCHEMA,
        "status": "authorized_once_under_founder_continuation_mandate",
        "contract_path": str(contract_path.relative_to(ROOT)),
        "contract_sha256": _sha(contract_path),
        "run_id": contract["run_id"],
        "maximum_provider_calls": 22,
        "maximum_estimated_cost_usd": 0.1,
        "automatic_retries": 0,
        "fallback_models": 0,
        "semantic_retries": 0,
        "evaluator_calls": 0,
        "embedding_calls": 0,
        "graph_calls": 0,
        "pipeline_calls": 0,
        "runtime_calls": 0,
    }
    if dict(authorization) != expected:
        raise Phase4TransferError("Phase-4 authorization drifted")


def _job_material(job: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, str], dict[str, Any]]:
    wrapper = _load(_repo_path(str(job["packet_path"])))
    if job["mechanism"] == "full_conversation_reader_v3":
        return wrapper, build_prompts_v3(wrapper), response_schema_v3(str(job["view_kind"]))
    if job["mechanism"] == "local_exploration_v2":
        return wrapper, build_local_prompts(wrapper), local_response_schema()
    if job["mechanism"] == "chronological_shard_v1":
        return wrapper, build_shard_prompts(wrapper), shard_response_schema(str(job["view_kind"]))
    if job["mechanism"] == "chronological_shard_role_explicit_v2":
        return wrapper, build_shard_prompts_v2(wrapper), shard_response_schema_v2(str(job["view_kind"]))
    if job["mechanism"] == "chronological_shard_modal_strength_v3":
        return wrapper, build_shard_prompts_v3(wrapper), shard_response_schema_v3(str(job["view_kind"]))
    raise Phase4TransferError("unknown Phase-4 mechanism")


def _error_headers(exc: error.HTTPError) -> dict[str, str]:
    allowed = ("retry-after", "x-ratelimit-limit", "x-ratelimit-remaining", "x-ratelimit-reset")
    return {name: str(exc.headers.get(name)) for name in allowed if exc.headers.get(name) is not None}


def run_job(*, contract: Mapping[str, Any], job: Mapping[str, Any], snapshot: Mapping[str, Any]) -> dict[str, Any]:
    started = time.monotonic()
    wrapper, prompts, schema = _job_material(job)
    config = contract["call_configuration"]
    base = {
        "schema_version": CALL_SCHEMA,
        "run_id": contract["run_id"],
        "call_id": job["job_id"],
        "case_id": job["case_id"],
        "mechanism": job["mechanism"],
        "view_kind": job["view_kind"],
        "focal_turn_index": job.get("focal_turn_index"),
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
        return {**base, "operational_status": "missing_api_key", "typed_status": "not_observed", "provider_calls": 0, "duration_seconds": round(time.monotonic() - started, 3)}
    body = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": prompts["system_prompt"]},
            {"role": "user", "content": prompts["user_prompt"]},
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {"name": "lolla_reasoning_process_phase4_read", "strict": True, "schema": schema},
        },
        "provider": {"require_parameters": True, "allow_fallbacks": False},
        "temperature": 0.0,
        "seed": 0,
        "max_tokens": (
            config["full_reader_max_output_tokens"]
            if job["mechanism"] == "full_conversation_reader_v3"
            else config["local_reader_max_output_tokens"]
        ),
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
    usage_complete = all(isinstance(value, int) and value > 0 for value in (prompt_tokens, completion_tokens, total_tokens))
    served_model = str(provider_payload.get("model", ""))
    attribution = _model_attribution(MODEL, served_model)
    operational_ok = bool(choices) and finish_reason.lower() != "error" and usage_complete and attribution in {"matched", "served_version_alias"}
    candidate_payload: dict[str, Any] | None = None
    compiled: dict[str, Any] | None = None
    validation_error = ""
    try:
        parsed = _extract_json_object(raw_content)
        if not isinstance(parsed, dict):
            raise Phase4TransferError("provider response is not an object")
        candidate_payload = parsed
        if job["mechanism"] == "full_conversation_reader_v3":
            case = next(item for item in contract["cases"] if item["case_id"] == job["case_id"])
            source_text = _repo_path(case["source_path"]).read_text(encoding="utf-8")
            catalog = build_source_catalog(source_text=source_text, source_path=case["source_path"])
            compiled = compile_response_v3_recordwise(
                response=parsed,
                wrapper=wrapper,
                base_ledger=_load(_repo_path(case["phase1_ledger_path"])),
                catalog=catalog,
                record_identity=f"phase4-{job['job_id']}",
                producer_kind="model",
                producer_id=MODEL,
                call_metadata={"call_id": job["job_id"], "model": served_model, "prompt_sha256": "sha256:" + prompts["user_prompt_sha256"]},
            )
        elif job["mechanism"] == "local_exploration_v2":
            compiled = compile_local_response_recordwise(
                response=parsed,
                wrapper=wrapper,
                producer_kind="model",
                producer_id=MODEL,
                record_identity=f"phase4-{job['job_id']}",
                call_metadata={"call_id": job["job_id"], "model": served_model, "prompt_sha256": "sha256:" + prompts["user_prompt_sha256"]},
            )
        elif job["mechanism"] == "chronological_shard_v1":
            compiled = compile_shard_response_recordwise(
                response=parsed,
                wrapper=wrapper,
                producer_kind="model",
                producer_id=MODEL,
                record_identity=f"probe-{job['job_id']}",
                call_metadata={"call_id": job["job_id"], "model": served_model, "prompt_sha256": "sha256:" + prompts["user_prompt_sha256"]},
            )
        elif job["mechanism"] == "chronological_shard_role_explicit_v2":
            compiled = compile_shard_response_recordwise_v2(
                response=parsed,
                wrapper=wrapper,
                producer_kind="model",
                producer_id=MODEL,
                record_identity=f"probe-{job['job_id']}",
                call_metadata={"call_id": job["job_id"], "model": served_model, "prompt_sha256": "sha256:" + prompts["user_prompt_sha256"]},
            )
        else:
            compiled = compile_shard_response_recordwise_v3(
                response=parsed,
                wrapper=wrapper,
                producer_kind="model",
                producer_id=MODEL,
                record_identity=f"probe-{job['job_id']}",
                call_metadata={"call_id": job["job_id"], "model": served_model, "prompt_sha256": "sha256:" + prompts["user_prompt_sha256"]},
            )
    except Exception as exc:  # noqa: BLE001
        validation_error = f"{type(exc).__name__}: {exc}"
    custody = compiled.get("records", []) if compiled else []
    admitted = sum(item.get("terminal_state") == "admitted" for item in custody)
    quarantined = sum(item.get("terminal_state") == "quarantined" for item in custody)
    if operational_ok and compiled is not None:
        typed_status = "admitted_with_quarantine" if admitted and quarantined else "quarantined" if quarantined and not admitted else "admitted"
    else:
        typed_status = "quarantined"
    cached_tokens = 0
    details = usage.get("prompt_tokens_details")
    if isinstance(details, Mapping) and isinstance(details.get("cached_tokens"), int):
        cached_tokens = int(details["cached_tokens"])
    estimated_cost = (
        _estimated_cost(snapshot=snapshot, prompt_tokens=int(prompt_tokens), completion_tokens=int(completion_tokens), cached_tokens=cached_tokens)
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


def execute(*, contract: Mapping[str, Any], output: Path) -> dict[str, Any]:
    output = output.resolve()
    if output.exists() and any(output.iterdir()):
        raise Phase4TransferError("output already exists; transfer repeat is forbidden")
    snapshot = _load(ROOT / "docs/evals/reasoning-process-phase3-model-snapshot-v1.json")
    calls: list[dict[str, Any]] = []
    cost = 0.0
    stop_reason = ""
    for job in contract["jobs"]:
        if cost > contract["budget_amendment"]["maximum_estimated_cost_usd"]:
            stop_reason = "estimated cost ceiling exceeded"
            break
        call = run_job(contract=contract, job=job, snapshot=snapshot)
        calls.append(call)
        call_path = output / "calls" / job["case_id"] / f"{job['job_id']}.json"
        _write(call_path, call)
        if isinstance(call.get("estimated_cost_usd"), (int, float)):
            cost += float(call["estimated_cost_usd"])
        if call["operational_status"] == "missing_api_key":
            stop_reason = "missing OpenRouter API key"
            break
    result = {
        "schema_version": RESULT_SCHEMA,
        "status": "first_attempt_transfer_preserved" if len(calls) == 22 else "first_attempt_transfer_stopped",
        "run_id": contract["run_id"],
        "expected_call_count": 22,
        "attempted_job_count": len(calls),
        "provider_request_count": sum(call.get("provider_calls", 0) for call in calls),
        "first_attempt_operational_success_count": sum(call["operational_status"] == "ok" for call in calls),
        "typed_admission_count": sum(call["typed_status"] in {"admitted", "admitted_with_quarantine"} for call in calls),
        "admitted_record_count": sum(call.get("admitted_record_count", 0) for call in calls),
        "quarantined_record_count": sum(call.get("quarantined_record_count", 0) for call in calls),
        "estimated_cost_usd": round(cost, 9),
        "stop_reason": stop_reason,
        "operational_failures": [
            {"call_id": call["call_id"], "case_id": call["case_id"], "status": call["operational_status"], "response_headers": call.get("response_headers", {})}
            for call in calls
            if call["operational_status"] != "ok"
        ],
        "semantic_review_status": "pending_source_first_review",
        "calls": {"automatic_retries": 0, "fallback_models": 0, "semantic_retries": 0, "evaluator": 0, "embedding": 0, "graph": 0, "pipeline": 0, "runtime": 0},
        "boundary": {"protected_targets_seen_by_model": False, "semantic_adequacy_inferred_by_runner": False, "stability_repeat_authorized": False, "graph_or_runtime_authorized": False},
    }
    _write(output / "result.json", result)
    return result


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
    if contract.get("schema_version") != SCHEMA:
        raise Phase4TransferError("unexpected Phase-4 contract schema")
    validation = validate_contract(contract, ROOT)
    if args.dry_run:
        print(json.dumps(validation, indent=2, sort_keys=True))
        return 0
    if args.authorization is None or args.env_file is None or args.output is None:
        raise Phase4TransferError("execution arguments are missing")
    validate_authorization(_load(args.authorization.resolve()), contract_path, contract)
    _load_env(args.env_file.resolve())
    result = execute(contract=contract, output=args.output)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
