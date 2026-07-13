#!/usr/bin/env python3
"""Validate or execute the frozen view-specific Gemini/OpenRouter probe."""
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
from engine.system_b.reasoning_process_contracts import schema_metrics  # noqa: E402
from engine.system_b.reasoning_process_view_specific import (  # noqa: E402
    VIEW_QUESTIONS,
    build_view_specific_prompts,
    compile_protected_fixture,
    validate_annotated_reader_packet,
    validate_view_specific_response,
    view_specific_response_schema,
)
from engine.system_b.reasoning_process_views import (  # noqa: E402
    canonical_json_bytes,
    sha256_bytes,
)
from scripts.evals.run_conversation_state_microtask_probe import _load_env  # noqa: E402
from scripts.evals.run_fixed_safe_holdout_pool import (  # noqa: E402
    _extract_json_object,
    _model_attribution,
)
from scripts.evals.run_fixed_safe_holdout_pool_v2 import _provider_diagnostic  # noqa: E402


CONTRACT_SCHEMA = "lolla.reasoning_process_view_specific_probe_contract.v1"
AUTHORIZATION_SCHEMA = "lolla.reasoning_process_view_specific_probe_authorization.v1"
CALL_SCHEMA = "lolla.reasoning_process_view_specific_probe_call.v1"
RESULT_SCHEMA = "lolla.reasoning_process_view_specific_probe_result.v1"


class ViewSpecificProbeRunnerError(RuntimeError):
    pass


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ViewSpecificProbeRunnerError(f"expected JSON object: {path}")
    return value


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json_sha(value: object) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def _repo_path(raw: object, *, label: str) -> Path:
    path = Path(str(raw))
    if path.is_absolute():
        raise ViewSpecificProbeRunnerError(f"{label} must be repo-relative")
    resolved = (ROOT / path).resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise ViewSpecificProbeRunnerError(f"{label} escapes the repository") from exc
    return resolved


def _report_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _wrapper(job: Mapping[str, Any]) -> dict[str, Any]:
    return _load(_repo_path(job["packet_path"], label="reader packet"))


def _observed_jobs(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    observed: list[dict[str, Any]] = []
    source_text = _repo_path(
        contract["case"]["source_path"], label="source"
    ).read_text(encoding="utf-8")
    jobs = {item["view_kind"]: item for item in contract["jobs"]}
    for view_kind in contract["view_order"]:
        job = jobs[view_kind]
        packet_path = _repo_path(job["packet_path"], label="reader packet")
        wrapper = _load(packet_path)
        validation = validate_annotated_reader_packet(wrapper, source_text=source_text)
        prompts = build_view_specific_prompts(wrapper)
        schema = view_specific_response_schema(view_kind)
        observed.append(
            {
                "job_id": f"view-specific-{contract['case']['case_id']}-{view_kind}",
                "view_kind": view_kind,
                "packet_path": str(packet_path.relative_to(ROOT)),
                "packet_sha256": _file_sha(packet_path),
                "input_utf8_bytes": validation["input_utf8_bytes"],
                "source_sentence_count": validation["sentence_count"],
                "auxiliary_ledger_included": validation["auxiliary_ledger_included"],
                "system_prompt_sha256": prompts["system_prompt_sha256"],
                "user_prompt_sha256": prompts["user_prompt_sha256"],
                "response_schema_sha256": _json_sha(schema),
                "response_schema_metrics": schema_metrics(schema),
            }
        )
    return observed


def validate_contract(contract: Mapping[str, Any]) -> dict[str, Any]:
    if contract.get("schema_version") != CONTRACT_SCHEMA:
        raise ViewSpecificProbeRunnerError("unexpected contract schema")
    if contract.get("status") != "frozen_before_provider_calls":
        raise ViewSpecificProbeRunnerError("probe contract is not frozen")
    if contract.get("view_order") != list(VIEW_QUESTIONS):
        raise ViewSpecificProbeRunnerError("view order drifted")
    for ref_name in ("redesign_contract", "redesign_report", "model_snapshot"):
        ref = contract.get(ref_name)
        if not isinstance(ref, Mapping):
            raise ViewSpecificProbeRunnerError(f"missing {ref_name}")
        path = _repo_path(ref.get("path"), label=ref_name)
        if _file_sha(path) != ref.get("sha256"):
            raise ViewSpecificProbeRunnerError(f"{ref_name} hash drifted")
    case = contract.get("case")
    if not isinstance(case, Mapping):
        raise ViewSpecificProbeRunnerError("case is missing")
    for path_key, hash_key in (
        ("source_path", "source_sha256"),
        ("phase1_ledger_path", "phase1_ledger_sha256"),
    ):
        if _file_sha(_repo_path(case.get(path_key), label=path_key)) != case.get(hash_key):
            raise ViewSpecificProbeRunnerError(f"case {path_key} drifted")
    expected_config = {
        "provider": "openrouter",
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "model": "google/gemini-3.1-flash-lite",
        "wire_mode": "strict_json_schema",
        "temperature": 0.0,
        "seed": 0,
        "reasoning_enabled": False,
        "max_output_tokens": 2400,
        "provider_timeout_seconds": 90,
        "require_supported_parameters": True,
        "allow_provider_fallbacks": False,
        "automatic_retries": 0,
        "response_healing": False,
        "parallel_calls": False,
        "evaluator_calls": 0,
        "embedding_calls": 0,
        "graph_calls": 0,
        "pipeline_calls": 0,
        "runtime_calls": 0,
    }
    if contract.get("call_configuration") != expected_config:
        raise ViewSpecificProbeRunnerError("call configuration drifted")
    snapshot = _load(_repo_path(contract["model_snapshot"]["path"], label="snapshot"))
    if snapshot.get("model_id") != expected_config["model"]:
        raise ViewSpecificProbeRunnerError("model snapshot drifted from Gemini route")
    if contract.get("jobs") != _observed_jobs(contract):
        raise ViewSpecificProbeRunnerError("job, packet, prompt, or schema lock drifted")
    if contract.get("budget") != {
        "maximum_provider_calls": 5,
        "maximum_calls_per_view": 1,
        "maximum_estimated_cost_usd": 0.05,
        "automatic_retries": 0,
        "fallback_models": 0,
        "evaluator_calls": 0,
        "embedding_calls": 0,
        "graph_calls": 0,
        "pipeline_calls": 0,
        "runtime_calls": 0,
    }:
        raise ViewSpecificProbeRunnerError("budget drifted")
    for job in contract["jobs"]:
        if job["input_utf8_bytes"] > 24000:
            raise ViewSpecificProbeRunnerError("input budget exceeded")
        if job["response_schema_metrics"]["bytes"] > 12000:
            raise ViewSpecificProbeRunnerError("schema byte budget exceeded")
        if job["response_schema_metrics"]["depth"] > 8:
            raise ViewSpecificProbeRunnerError("schema depth exceeded")
    for lock in contract["artifact_locks"]:
        if _file_sha(_repo_path(lock["path"], label="artifact lock")) != lock["sha256"]:
            raise ViewSpecificProbeRunnerError(f"artifact lock drifted: {lock['role']}")
    return {
        "status": "contract_valid",
        "case_id": case["case_id"],
        "job_count": 5,
        "provider": "openrouter",
        "model": "google/gemini-3.1-flash-lite",
        "provider_calls_made": 0,
    }


def validate_authorization(
    authorization: Mapping[str, Any], *, contract: Mapping[str, Any], contract_path: Path
) -> None:
    if authorization.get("schema_version") != AUTHORIZATION_SCHEMA:
        raise ViewSpecificProbeRunnerError("unexpected authorization schema")
    if authorization.get("status") != "authorized_once_under_founder_continuation_mandate":
        raise ViewSpecificProbeRunnerError("probe is not authorized")
    if authorization.get("contract_path") != str(contract_path.relative_to(ROOT)):
        raise ViewSpecificProbeRunnerError("authorization contract path drifted")
    if authorization.get("contract_sha256") != _file_sha(contract_path):
        raise ViewSpecificProbeRunnerError("authorization contract hash drifted")
    if authorization.get("run_id") != contract.get("run_id"):
        raise ViewSpecificProbeRunnerError("authorization run ID drifted")
    if authorization.get("maximum_provider_calls") != 5:
        raise ViewSpecificProbeRunnerError("authorization call ceiling drifted")
    for key in (
        "automatic_retries",
        "fallback_models",
        "evaluator_calls",
        "embedding_calls",
        "graph_calls",
        "pipeline_calls",
        "runtime_calls",
    ):
        if authorization.get(key) != 0:
            raise ViewSpecificProbeRunnerError("authorization includes forbidden calls")


def _estimated_cost(
    *, snapshot: Mapping[str, Any], prompt_tokens: int, completion_tokens: int, cached_tokens: int
) -> float:
    pricing = snapshot["pricing"]
    cached = min(max(cached_tokens, 0), max(prompt_tokens, 0))
    fresh = max(prompt_tokens, 0) - cached
    return (
        fresh * pricing["prompt_usd_per_token"]
        + cached * pricing["cached_prompt_usd_per_token"]
        + max(completion_tokens, 0) * pricing["completion_usd_per_token"]
    )


def run_job(
    *, contract: Mapping[str, Any], job: Mapping[str, Any], snapshot: Mapping[str, Any]
) -> dict[str, Any]:
    started = time.monotonic()
    wrapper = _wrapper(job)
    packet = wrapper["reader_packet"]
    prompts = build_view_specific_prompts(wrapper)
    schema = view_specific_response_schema(job["view_kind"])
    config = contract["call_configuration"]
    base = {
        "schema_version": CALL_SCHEMA,
        "run_id": contract["run_id"],
        "call_id": job["job_id"],
        "case_id": packet["case_id"],
        "view_kind": packet["view_kind"],
        "requested_model": config["model"],
        "packet_path": job["packet_path"],
        "packet_sha256": job["packet_sha256"],
        "input_utf8_bytes": job["input_utf8_bytes"],
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
        "model": config["model"],
        "messages": [
            {"role": "system", "content": prompts["system_prompt"]},
            {"role": "user", "content": prompts["user_prompt"]},
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "lolla_reasoning_process_view_specific_read",
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
            "typed_status": "not_observed",
            "provider_error_type": type(exc).__name__,
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
    attribution = _model_attribution(config["model"], served_model)
    operational_ok = (
        bool(choices)
        and finish_reason.lower() != "error"
        and usage_complete
        and attribution in {"matched", "served_version_alias"}
    )
    candidate_payload: dict[str, Any] | None = None
    validated: dict[str, Any] | None = None
    compiled: dict[str, Any] | None = None
    validation_error = ""
    try:
        parsed = _extract_json_object(raw_content)
        if not isinstance(parsed, dict):
            raise ViewSpecificProbeRunnerError("provider response is not an object")
        candidate_payload = parsed
        validated = validate_view_specific_response(parsed, wrapper=wrapper)
        source_text = _repo_path(
            contract["case"]["source_path"], label="source"
        ).read_text(encoding="utf-8")
        catalog = build_source_catalog(
            source_text=source_text, source_path=contract["case"]["source_path"]
        )
        # Reuse the append-only compiler with a synthetic target identity only;
        # no protected target content enters the call or compilation semantics.
        compiled = compile_protected_fixture(
            target={
                "target_id": f"model-{job['job_id']}",
                "view_kind": job["view_kind"],
            },
            response=parsed,
            wrapper=wrapper,
            base_ledger=_load(
                _repo_path(contract["case"]["phase1_ledger_path"], label="ledger")
            ),
            catalog=catalog,
            producer_kind="model",
            producer_id=config["model"],
            call_metadata={
                "call_id": job["job_id"],
                "model": served_model,
                "prompt_sha256": "sha256:" + prompts["user_prompt_sha256"],
            },
        )
    except Exception as exc:  # noqa: BLE001
        validation_error = f"{type(exc).__name__}: {exc}"
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
        "typed_status": (
            "admitted" if operational_ok and validated is not None and compiled is not None else "quarantined"
        ),
        "validation_error": validation_error,
        "candidate_payload": candidate_payload,
        "candidate_payload_sha256": _json_sha(candidate_payload) if candidate_payload else "",
        "compiled": compiled,
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
        "nonclaims": [
            "typed_and_alias_valid_is_not_semantic_adequacy",
            "development_case_is_not_independent_gold",
            "bounded_view_is_not_reasoning_or_final_answer_quality",
            "result_does_not_authorize_graph_or_runtime_integration",
        ],
    }


def execute(*, contract: Mapping[str, Any], output_dir: Path) -> dict[str, Any]:
    output_dir = output_dir.resolve()
    calls_dir = output_dir / "calls"
    if (output_dir / "result.json").exists() or (
        calls_dir.exists() and any(calls_dir.iterdir())
    ):
        raise ViewSpecificProbeRunnerError("output already exists; repeat is forbidden")
    snapshot = _load(_repo_path(contract["model_snapshot"]["path"], label="snapshot"))
    jobs = {item["view_kind"]: item for item in contract["jobs"]}
    calls: list[dict[str, Any]] = []
    cumulative_cost = 0.0
    stop_reason = ""
    for view_kind in contract["view_order"]:
        if cumulative_cost > contract["budget"]["maximum_estimated_cost_usd"]:
            stop_reason = "estimated cost ceiling exceeded"
            break
        call = run_job(contract=contract, job=jobs[view_kind], snapshot=snapshot)
        calls.append(call)
        _write(calls_dir / f"{view_kind}.json", call)
        if isinstance(call.get("estimated_cost_usd"), (int, float)):
            cumulative_cost += float(call["estimated_cost_usd"])
        if call.get("operational_status") == "missing_api_key":
            stop_reason = "missing OpenRouter API key"
            break
    result = {
        "schema_version": RESULT_SCHEMA,
        "status": "probe_calls_complete" if len(calls) == 5 else "probe_stopped",
        "run_id": contract["run_id"],
        "case_id": contract["case"]["case_id"],
        "call_artifacts": [
            {
                "view_kind": call["view_kind"],
                "path": _report_path(calls_dir / f"{call['view_kind']}.json"),
                "sha256": _file_sha(calls_dir / f"{call['view_kind']}.json"),
                "operational_status": call["operational_status"],
                "typed_status": call["typed_status"],
            }
            for call in calls
        ],
        "expected_call_count": 5,
        "attempted_call_count": len(calls),
        "provider_call_count": sum(int(call.get("provider_calls", 0)) for call in calls),
        "operational_success_count": sum(call.get("operational_status") == "ok" for call in calls),
        "typed_admission_count": sum(call.get("typed_status") == "admitted" for call in calls),
        "estimated_cost_usd": round(cumulative_cost, 9),
        "stop_reason": stop_reason,
        "semantic_review_status": "pending_source_first_review",
        "calls": {
            "automatic_retries": 0,
            "fallback_models": 0,
            "evaluator": 0,
            "embedding": 0,
            "graph": 0,
            "pipeline": 0,
            "runtime": 0,
        },
        "boundary": {
            "protected_targets_seen_by_model": False,
            "source_review_addenda_seen_by_model": False,
            "semantic_adequacy_inferred_by_code": False,
            "final_output_evaluated": False,
            "graph_or_runtime_authorized": False,
        },
    }
    _write(output_dir / "result.json", result)
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
    validation = validate_contract(contract)
    if args.dry_run:
        print(json.dumps(validation, indent=2, sort_keys=True))
        return 0
    if args.authorization is None or args.env_file is None or args.output is None:
        raise ViewSpecificProbeRunnerError(
            "--authorization, --env-file, and --output are required for execution"
        )
    authorization = _load(args.authorization.resolve())
    validate_authorization(
        authorization, contract=contract, contract_path=contract_path
    )
    _load_env(args.env_file.resolve())
    result = execute(contract=contract, output_dir=args.output)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
