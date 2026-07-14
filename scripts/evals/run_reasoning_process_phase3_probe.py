#!/usr/bin/env python3
"""Validate or execute the frozen five-view Phase-3 development probe."""
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

from engine.system_b.reasoning_process_contracts import (  # noqa: E402
    OBSERVATION_FAMILIES,
    schema_metrics,
)
from engine.system_b.reasoning_process_probe import (  # noqa: E402
    ReasoningProcessProbeError,
    build_probe_prompts,
    catalog_from_packet,
    compile_probe_view,
    file_sha256,
    probe_response_schema,
    validate_probe_packet,
    validate_probe_response,
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


CONTRACT_SCHEMA = "lolla.reasoning_process_phase3_probe_contract.v1"
AUTHORIZATION_SCHEMA = "lolla.reasoning_process_phase3_probe_authorization.v1"
CALL_SCHEMA = "lolla.reasoning_process_phase3_call.v1"
RESULT_SCHEMA = "lolla.reasoning_process_phase3_baseline_result.v1"


class Phase3RunnerError(RuntimeError):
    pass


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise Phase3RunnerError(f"expected JSON object: {path}")
    return value


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def _report_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _repo_path(raw: object, *, label: str) -> Path:
    path = Path(str(raw))
    if path.is_absolute():
        raise Phase3RunnerError(f"{label} must be repo-relative")
    resolved = (ROOT / path).resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise Phase3RunnerError(f"{label} escapes the repository") from exc
    return resolved


def _json_sha(value: object) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def _packet(job: Mapping[str, Any]) -> dict[str, Any]:
    wrapper = _load(_repo_path(job["packet_path"], label="probe packet"))
    packet = wrapper.get("packet")
    if not isinstance(packet, dict):
        raise Phase3RunnerError("probe packet wrapper lacks packet object")
    return packet


def _response_schema(packet: Mapping[str, Any]) -> dict[str, Any]:
    observations = packet["auxiliary_phase1_ledger"]["observations"]
    catalog = catalog_from_packet(packet)
    return probe_response_schema(
        allowed_auxiliary_observation_ids=[item["observation_id"] for item in observations],
        max_turn_index=max(span.turn_index for span in catalog.spans),
    )


def _selection(review: Mapping[str, Any]) -> dict[str, Any]:
    eligible = [
        case["case_id"]
        for case in review["cases"]
        if all(target["decision"] == "addendum_required" for target in case["targets"])
    ]
    ranking = sorted(
        (
            {
                "case_id": case_id,
                "sha256_case_id": hashlib.sha256(case_id.encode("utf-8")).hexdigest(),
            }
            for case_id in eligible
        ),
        key=lambda item: item["sha256_case_id"],
    )
    return {
        "eligibility_rule": "all five protected targets required prospective Phase-2 addenda",
        "ranking_rule": "ascending SHA-256 of case_id",
        "eligible_case_ids": eligible,
        "ranking": ranking,
        "selected_case_id": ranking[0]["case_id"],
    }


def validate_contract(contract: Mapping[str, Any]) -> dict[str, Any]:
    if contract.get("schema_version") != CONTRACT_SCHEMA:
        raise Phase3RunnerError("unexpected Phase-3 contract schema")
    if contract.get("status") != "frozen_before_provider_calls":
        raise Phase3RunnerError("Phase-3 contract is not frozen")
    if contract.get("view_order") != list(OBSERVATION_FAMILIES):
        raise Phase3RunnerError("view order drifted")
    review_ref = contract.get("phase2_coverage_review")
    if not isinstance(review_ref, Mapping):
        raise Phase3RunnerError("Phase-2 coverage-review reference is missing")
    review_path = _repo_path(review_ref.get("path"), label="coverage review")
    if file_sha256(review_path) != review_ref.get("sha256"):
        raise Phase3RunnerError("coverage-review hash drifted")
    observed_selection = _selection(_load(review_path))
    if contract.get("selection") != observed_selection:
        raise Phase3RunnerError("mechanical case selection drifted")
    selected_case = str(observed_selection["selected_case_id"])
    case = contract.get("case")
    if not isinstance(case, Mapping) or case.get("case_id") != selected_case:
        raise Phase3RunnerError("selected case custody drifted")
    for path_field, hash_field in (
        ("source_path", "source_sha256"),
        ("phase1_ledger_path", "phase1_ledger_sha256"),
    ):
        path = _repo_path(case.get(path_field), label=path_field)
        if file_sha256(path) != case.get(hash_field):
            raise Phase3RunnerError(f"case hash drifted: {path_field}")
    config = contract.get("call_configuration")
    expected_config = {
        "provider": "openrouter",
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "model": "google/gemini-3.1-flash-lite",
        "wire_mode": "strict_json_schema",
        "temperature": 0.0,
        "seed": 0,
        "reasoning_enabled": False,
        "reasoning_parameter_sent": True,
        "max_output_tokens": 2200,
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
    if config != expected_config:
        raise Phase3RunnerError("call configuration drifted")
    snapshot_ref = contract.get("model_snapshot")
    if not isinstance(snapshot_ref, Mapping):
        raise Phase3RunnerError("model snapshot reference is missing")
    snapshot_path = _repo_path(snapshot_ref.get("path"), label="model snapshot")
    if file_sha256(snapshot_path) != snapshot_ref.get("sha256"):
        raise Phase3RunnerError("model snapshot hash drifted")
    snapshot = _load(snapshot_path)
    if snapshot.get("model_id") != config["model"]:
        raise Phase3RunnerError("model snapshot and configuration differ")
    required_parameters = {
        "max_tokens",
        "response_format",
        "seed",
        "structured_outputs",
        "temperature",
    }
    if not required_parameters <= set(snapshot.get("supported_parameters", [])):
        raise Phase3RunnerError("model snapshot lacks a required parameter")
    if snapshot.get("pricing", {}).get("prompt_usd_per_token") != 0.00000025:
        raise Phase3RunnerError("model input pricing drifted")
    if snapshot.get("pricing", {}).get("completion_usd_per_token") != 0.0000015:
        raise Phase3RunnerError("model output pricing drifted")
    jobs = contract.get("jobs")
    if not isinstance(jobs, list) or len(jobs) != 5:
        raise Phase3RunnerError("Phase-3 contract requires five jobs")
    observed_jobs: list[dict[str, Any]] = []
    for view_kind in OBSERVATION_FAMILIES:
        job = next((item for item in jobs if item.get("view_kind") == view_kind), None)
        if not isinstance(job, Mapping):
            raise Phase3RunnerError(f"missing job: {view_kind}")
        packet_path = _repo_path(job.get("packet_path"), label="probe packet")
        packet = _packet(job)
        validation = validate_probe_packet(packet)
        if packet.get("case_id") != selected_case or packet.get("view_kind") != view_kind:
            raise Phase3RunnerError("job packet identity drifted")
        prompts = build_probe_prompts(packet)
        schema = _response_schema(packet)
        observed_jobs.append(
            {
                "job_id": f"phase3-{selected_case}-{view_kind}",
                "view_kind": view_kind,
                "packet_path": str(packet_path.relative_to(ROOT)),
                "packet_sha256": file_sha256(packet_path),
                "input_utf8_bytes": validation["input_utf8_bytes"],
                "auxiliary_observation_count": validation["auxiliary_observation_count"],
                "system_prompt_sha256": prompts["system_prompt_sha256"],
                "user_prompt_sha256": prompts["user_prompt_sha256"],
                "response_schema_sha256": _json_sha(schema),
                "response_schema_metrics": schema_metrics(schema),
            }
        )
    if jobs != observed_jobs:
        raise Phase3RunnerError("job, prompt, packet, or schema locks drifted")
    budget = contract.get("budget")
    if budget != {
        "maximum_provider_calls": 5,
        "maximum_calls_per_view": 1,
        "maximum_estimated_cost_usd": 0.05,
        "automatic_retries": 0,
        "fallback_models": 0,
        "evaluator_calls": 0,
        "graph_calls": 0,
        "pipeline_calls": 0,
        "runtime_calls": 0,
    }:
        raise Phase3RunnerError("Phase-3 budget drifted")
    if contract.get("success_requirements") != {
        "operational_success_rate": 1.0,
        "typed_admission_rate": 1.0,
        "exact_source_reference_validity_rate": 1.0,
        "protected_target_visibility_rate": 1.0,
        "invalid_admitted_item_count": 0,
        "source_strength_inflation_count": 0,
        "context_invisible_label_count": 0,
        "critical_dimension_zero_count": 0,
        "max_output_items_per_view": 4,
        "valid_empty_output_allowed": True,
        "source_review_required_for_semantic_pass": True,
    }:
        raise Phase3RunnerError("success requirements drifted")
    if contract.get("source_review_contract") != {
        "method": "source_first_before_polish",
        "reviewer_independence": "same_project_session_not_blind",
        "protected_targets_are_exhaustive_gold": False,
        "review_exact_evidence_before_interpretation": True,
        "semantic_adequacy_inferred_by_code": False,
        "model_output_may_change_the_gate": False,
        "final_answer_quality_reviewed": False,
        "scalar_score_allowed": False,
    }:
        raise Phase3RunnerError("source-review contract drifted")
    if contract.get("repair_policy") != {
        "baseline_authorizes_repair_calls": False,
        "separate_prospective_authorization_required": True,
        "maximum_generic_repair_calls": 5,
        "repair_must_address_shared_prompt_or_representation_failure": True,
        "case_specific_examples_allowed": False,
        "gate_weakening_allowed": False,
        "target_or_addendum_leakage_allowed": False,
        "model_change_allowed": False,
        "conversation_only_ablation_counts_as_repair": False,
    }:
        raise Phase3RunnerError("repair policy drifted")
    if contract.get("stop_rules") != {
        "operational_failure_stops_remaining_baseline_calls": True,
        "semantic_or_valid_empty_result_is_preserved_without_retry": True,
        "cost_ceiling_stops_remaining_calls": True,
        "no_prompt_change_inside_baseline": True,
        "no_fallback_retry_or_response_healing": True,
        "no_graph_pipeline_runtime_or_evaluator_calls": True,
        "source_review_required_before_repair_decision": True,
    }:
        raise Phase3RunnerError("stop rules drifted")
    for job in jobs:
        metrics = job["response_schema_metrics"]
        if metrics["bytes"] > 12000 or metrics["depth"] > 8:
            raise Phase3RunnerError("provider schema exceeds frozen Phase-0 ceiling")
        if job["input_utf8_bytes"] > 24000 or job["auxiliary_observation_count"] > 32:
            raise Phase3RunnerError("probe input exceeds frozen Phase-0 ceiling")
    roles: set[str] = set()
    for lock in contract.get("artifact_locks", []):
        path = _repo_path(lock.get("path"), label="artifact lock")
        if file_sha256(path) != lock.get("sha256"):
            raise Phase3RunnerError(f"artifact lock drifted: {lock.get('role')}")
        roles.add(str(lock.get("role")))
    required_roles = {
        "phase3_runner",
        "phase3_probe_contracts",
        "phase0_contract",
        "phase2_coverage_contract",
        "phase2_coverage_review",
        "phase2_result",
        "phase1_ledger",
        "product_constitution",
        "evaluation_doctrine",
    }
    if not required_roles <= roles:
        raise Phase3RunnerError("required artifact locks are missing")
    return {
        "status": "contract_valid",
        "selected_case_id": selected_case,
        "job_count": len(jobs),
        "maximum_provider_calls": budget["maximum_provider_calls"],
        "provider_calls_made": 0,
    }


def validate_authorization(
    authorization: Mapping[str, Any], *, contract: Mapping[str, Any], contract_path: Path
) -> None:
    if authorization.get("schema_version") != AUTHORIZATION_SCHEMA:
        raise Phase3RunnerError("unexpected Phase-3 authorization schema")
    if authorization.get("status") != "authorized_once_by_founder_phase3_goal":
        raise Phase3RunnerError("Phase-3 baseline is not authorized")
    if authorization.get("contract_path") != str(contract_path.relative_to(ROOT)):
        raise Phase3RunnerError("authorization contract path drifted")
    if authorization.get("contract_sha256") != file_sha256(contract_path):
        raise Phase3RunnerError("authorization contract hash drifted")
    if authorization.get("run_id") != contract.get("run_id"):
        raise Phase3RunnerError("authorization run ID drifted")
    if authorization.get("selected_case_id") != contract["case"]["case_id"]:
        raise Phase3RunnerError("authorization selected case drifted")
    if authorization.get("view_order") != list(OBSERVATION_FAMILIES):
        raise Phase3RunnerError("authorization view order drifted")
    if authorization.get("maximum_provider_calls") != 5:
        raise Phase3RunnerError("authorization call ceiling drifted")
    forbidden = (
        "automatic_retries",
        "fallback_models",
        "evaluator_calls",
        "embedding_calls",
        "graph_calls",
        "pipeline_calls",
        "runtime_calls",
    )
    if any(authorization.get(key) != 0 for key in forbidden):
        raise Phase3RunnerError("authorization includes forbidden calls")


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
    packet = _packet(job)
    prompts = build_probe_prompts(packet)
    schema = _response_schema(packet)
    config = contract["call_configuration"]
    call_id = str(job["job_id"])
    base = {
        "schema_version": CALL_SCHEMA,
        "run_id": contract["run_id"],
        "call_id": call_id,
        "case_id": packet["case_id"],
        "view_kind": packet["view_kind"],
        "requested_model": config["model"],
        "packet_path": job["packet_path"],
        "packet_sha256": job["packet_sha256"],
        "input_utf8_bytes": job["input_utf8_bytes"],
        "system_prompt_sha256": prompts["system_prompt_sha256"],
        "user_prompt_sha256": prompts["user_prompt_sha256"],
        "response_schema_sha256": _json_sha(schema),
        "temperature": config["temperature"],
        "seed": config["seed"],
        "reasoning_enabled": False,
        "reasoning_parameter_sent": True,
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
                "name": "lolla_reasoning_process_bounded_read",
                "strict": True,
                "schema": schema,
            },
        },
        "provider": {
            "require_parameters": True,
            "allow_fallbacks": False,
        },
        "temperature": config["temperature"],
        "seed": config["seed"],
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
    validation_error = ""
    validated_response: dict[str, Any] | None = None
    compiled: dict[str, Any] | None = None
    try:
        parsed = _extract_json_object(raw_content)
        if not isinstance(parsed, dict):
            raise ReasoningProcessProbeError("provider response is not an object")
        candidate_payload = parsed
        validated_response = validate_probe_response(
            parsed, packet=packet, catalog=catalog_from_packet(packet)
        )
        ledger_path = _repo_path(
            contract["case"]["phase1_ledger_path"], label="Phase-1 ledger"
        )
        compiled = compile_probe_view(
            validated_response=validated_response,
            packet=packet,
            base_ledger=_load(ledger_path),
            catalog=catalog_from_packet(packet),
            call_metadata={
                "call_id": call_id,
                "requested_model": config["model"],
                "served_model": served_model,
                "prompt_sha256": "sha256:" + prompts["user_prompt_sha256"],
                "base_ledger_sha256": "sha256:" + contract["case"]["phase1_ledger_sha256"],
            },
        )
    except Exception as exc:  # noqa: BLE001
        validation_error = f"{type(exc).__name__}: {exc}"
    cached_tokens = 0
    prompt_details = usage.get("prompt_tokens_details")
    if isinstance(prompt_details, Mapping) and isinstance(
        prompt_details.get("cached_tokens"), int
    ):
        cached_tokens = int(prompt_details["cached_tokens"])
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
            "admitted"
            if operational_ok and validated_response is not None and compiled is not None
            else "quarantined"
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
        "non_claims": [
            "typed_and_source_valid_is_not_semantic_adequacy",
            "development_case_is_not_independent_gold",
            "bounded_view_is_not_reasoning_quality",
            "bounded_view_is_not_final_answer_quality",
            "result_does_not_authorize_graph_or_runtime_integration",
        ],
    }


def execute(
    *, contract: Mapping[str, Any], output_dir: Path
) -> dict[str, Any]:
    output_dir = output_dir.resolve()
    calls_dir = output_dir / "calls"
    if (output_dir / "result.json").exists() or (calls_dir.exists() and any(calls_dir.iterdir())):
        raise Phase3RunnerError("baseline output already exists; repeat execution is forbidden")
    snapshot = _load(_repo_path(contract["model_snapshot"]["path"], label="model snapshot"))
    calls: list[dict[str, Any]] = []
    cumulative_cost = 0.0
    stop_reason = ""
    jobs_by_kind = {job["view_kind"]: job for job in contract["jobs"]}
    for view_kind in contract["view_order"]:
        call = run_job(contract=contract, job=jobs_by_kind[view_kind], snapshot=snapshot)
        calls.append(call)
        _write(calls_dir / f"{view_kind}.json", call)
        if isinstance(call.get("estimated_cost_usd"), (int, float)):
            cumulative_cost += float(call["estimated_cost_usd"])
        if call.get("operational_status") != "ok":
            stop_reason = f"operational failure in {view_kind}"
            break
        if cumulative_cost > contract["budget"]["maximum_estimated_cost_usd"]:
            stop_reason = "estimated cost ceiling exceeded"
            break
    provider_calls = sum(int(call.get("provider_calls", 0)) for call in calls)
    admitted = sum(call.get("typed_status") == "admitted" for call in calls)
    result = {
        "schema_version": RESULT_SCHEMA,
        "status": (
            "baseline_operational_and_custody_complete"
            if len(calls) == 5
            and provider_calls == 5
            and all(call.get("operational_status") == "ok" for call in calls)
            else "baseline_stopped_operationally"
        ),
        "run_id": contract["run_id"],
        "case_id": contract["case"]["case_id"],
        "view_order": contract["view_order"],
        "call_artifacts": [
            {
                "view_kind": call["view_kind"],
                "path": _report_path(calls_dir / f"{call['view_kind']}.json"),
                "sha256": file_sha256(calls_dir / f"{call['view_kind']}.json"),
                "operational_status": call["operational_status"],
                "typed_status": call["typed_status"],
            }
            for call in calls
        ],
        "expected_call_count": 5,
        "attempted_call_count": len(calls),
        "provider_call_count": provider_calls,
        "typed_admission_count": admitted,
        "estimated_cost_usd": round(cumulative_cost, 9),
        "maximum_estimated_cost_usd": contract["budget"]["maximum_estimated_cost_usd"],
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
        raise Phase3RunnerError(
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
