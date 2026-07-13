#!/usr/bin/env python3
"""Validate or execute the one authorized generic Phase-3 prompt repair."""
from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.reasoning_process_contracts import (  # noqa: E402
    OBSERVATION_FAMILIES,
    schema_metrics,
)
from engine.system_b.reasoning_process_probe import (  # noqa: E402
    build_probe_prompts as baseline_prompt_builder,
    catalog_from_packet,
    file_sha256,
    validate_probe_packet,
)
from engine.system_b.reasoning_process_probe_repair import (  # noqa: E402
    REPAIR_PROMPT_VERSION,
    build_repair_prompts,
    rekey_compiled_repair,
)
from engine.system_b.reasoning_process_views import canonical_json_bytes, sha256_bytes  # noqa: E402
from scripts.evals import run_reasoning_process_phase3_probe as baseline  # noqa: E402


CONTRACT_SCHEMA = "lolla.reasoning_process_phase3_repair_contract.v1"
AUTHORIZATION_SCHEMA = "lolla.reasoning_process_phase3_repair_authorization.v1"
CALL_SCHEMA = "lolla.reasoning_process_phase3_repair_call.v1"
RESULT_SCHEMA = "lolla.reasoning_process_phase3_repair_result.v1"


class Phase3RepairError(RuntimeError):
    pass


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise Phase3RepairError(f"expected JSON object: {path}")
    return value


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def _repo_path(raw: object, *, label: str) -> Path:
    path = Path(str(raw))
    if path.is_absolute():
        raise Phase3RepairError(f"{label} must be repo-relative")
    resolved = (ROOT / path).resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise Phase3RepairError(f"{label} escapes repository") from exc
    return resolved


def _report_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _json_sha(value: object) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def _packet(job: Mapping[str, Any]) -> dict[str, Any]:
    wrapper = _load(_repo_path(job["packet_path"], label="probe packet"))
    packet = wrapper.get("packet")
    if not isinstance(packet, dict):
        raise Phase3RepairError("probe packet wrapper lacks packet object")
    return packet


def validate_contract(contract: Mapping[str, Any]) -> dict[str, Any]:
    if contract.get("schema_version") != CONTRACT_SCHEMA:
        raise Phase3RepairError("unexpected repair contract schema")
    if contract.get("status") != "generic_repair_frozen_before_calls":
        raise Phase3RepairError("repair contract is not frozen")
    baseline_ref = contract.get("baseline_contract")
    review_ref = contract.get("baseline_source_review")
    result_ref = contract.get("baseline_result")
    for reference, label in (
        (baseline_ref, "baseline contract"),
        (review_ref, "baseline source review"),
        (result_ref, "baseline result"),
    ):
        if not isinstance(reference, Mapping):
            raise Phase3RepairError(f"{label} reference is missing")
        path = _repo_path(reference.get("path"), label=label)
        if file_sha256(path) != reference.get("sha256"):
            raise Phase3RepairError(f"{label} hash drifted")
    baseline_contract = _load(_repo_path(baseline_ref["path"], label="baseline contract"))
    baseline.validate_contract(baseline_contract)
    baseline_review = _load(
        _repo_path(review_ref["path"], label="baseline source review")
    )
    if not baseline_review.get("repair_decision", {}).get("generic_repair_justified"):
        raise Phase3RepairError("baseline source review did not justify repair")
    if contract.get("prompt_version") != REPAIR_PROMPT_VERSION:
        raise Phase3RepairError("repair prompt version drifted")
    for field in ("case", "view_order", "call_configuration", "model_snapshot"):
        if contract.get(field) != baseline_contract.get(field):
            raise Phase3RepairError(f"repair changed frozen field: {field}")
    if contract["view_order"] != list(OBSERVATION_FAMILIES):
        raise Phase3RepairError("repair view order drifted")
    jobs = contract.get("jobs")
    if not isinstance(jobs, list) or len(jobs) != 5:
        raise Phase3RepairError("repair requires five jobs")
    baseline_jobs = {item["view_kind"]: item for item in baseline_contract["jobs"]}
    observed_jobs: list[dict[str, Any]] = []
    for view_kind in OBSERVATION_FAMILIES:
        inherited = baseline_jobs[view_kind]
        packet_path = _repo_path(inherited["packet_path"], label="probe packet")
        packet = _packet(inherited)
        validation = validate_probe_packet(packet)
        prompts = build_repair_prompts(packet)
        schema = baseline._response_schema(packet)
        observed_jobs.append(
            {
                "job_id": f"phase3-repair-{contract['case']['case_id']}-{view_kind}",
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
        raise Phase3RepairError("repair job, prompt, packet, or schema locks drifted")
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
        raise Phase3RepairError("repair budget drifted")
    if contract.get("allowed_change") != {
        "shared_system_prompt_full_conversation_scan_instruction": True,
        "generic_per_view_coverage_instruction": True,
        "case_specific_examples": False,
        "protected_target_or_addendum_input": False,
        "model_changed": False,
        "schema_changed": False,
        "budget_increased": False,
        "gates_weakened": False,
        "conversation_only_ablation": False,
    }:
        raise Phase3RepairError("repair change boundary drifted")
    roles: set[str] = set()
    for lock in contract.get("artifact_locks", []):
        path = _repo_path(lock.get("path"), label="artifact lock")
        if file_sha256(path) != lock.get("sha256"):
            raise Phase3RepairError(f"artifact lock drifted: {lock.get('role')}")
        roles.add(str(lock.get("role")))
    required = {
        "repair_runner",
        "repair_prompt_and_rekey",
        "baseline_runner",
        "baseline_probe_contracts",
        "baseline_source_review",
    }
    if not required <= roles:
        raise Phase3RepairError("required repair locks are missing")
    return {
        "status": "repair_contract_valid",
        "selected_case_id": contract["case"]["case_id"],
        "job_count": 5,
        "maximum_provider_calls": 5,
        "provider_calls_made": 0,
    }


def validate_authorization(
    authorization: Mapping[str, Any], *, contract: Mapping[str, Any], contract_path: Path
) -> None:
    if authorization.get("schema_version") != AUTHORIZATION_SCHEMA:
        raise Phase3RepairError("unexpected repair authorization schema")
    if authorization.get("status") != "one_generic_repair_authorized_once":
        raise Phase3RepairError("generic repair is not authorized")
    if authorization.get("contract_path") != str(contract_path.relative_to(ROOT)):
        raise Phase3RepairError("repair authorization path drifted")
    if authorization.get("contract_sha256") != file_sha256(contract_path):
        raise Phase3RepairError("repair authorization hash drifted")
    if authorization.get("run_id") != contract.get("run_id"):
        raise Phase3RepairError("repair authorization run ID drifted")
    if authorization.get("maximum_provider_calls") != 5:
        raise Phase3RepairError("repair authorization call ceiling drifted")
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
        raise Phase3RepairError("repair authorization includes forbidden calls")


def run_job(
    *, contract: Mapping[str, Any], job: Mapping[str, Any], snapshot: Mapping[str, Any]
) -> dict[str, Any]:
    original = baseline.build_probe_prompts
    if original is not baseline_prompt_builder:
        raise Phase3RepairError("baseline prompt builder was already replaced")
    try:
        baseline.build_probe_prompts = build_repair_prompts
        result = baseline.run_job(contract=contract, job=job, snapshot=snapshot)
    finally:
        baseline.build_probe_prompts = original
    result["schema_version"] = CALL_SCHEMA
    result["stage"] = "one_generic_prompt_repair"
    result["prompt_version"] = REPAIR_PROMPT_VERSION
    if result.get("compiled") is not None:
        packet = _packet(job)
        ledger = _load(_repo_path(contract["case"]["phase1_ledger_path"], label="ledger"))
        result["compiled"] = rekey_compiled_repair(
            result["compiled"],
            catalog=catalog_from_packet(packet),
            known_base_observation_ids=[
                item["observation_id"] for item in ledger["observations"]
            ],
        )
    return result


def execute(*, contract: Mapping[str, Any], output_dir: Path) -> dict[str, Any]:
    output_dir = output_dir.resolve()
    calls_dir = output_dir / "calls"
    if (output_dir / "result.json").exists() or (calls_dir.exists() and any(calls_dir.iterdir())):
        raise Phase3RepairError("repair output already exists; repeat execution is forbidden")
    snapshot = _load(_repo_path(contract["model_snapshot"]["path"], label="model snapshot"))
    calls: list[dict[str, Any]] = []
    cumulative_cost = 0.0
    stop_reason = ""
    jobs = {job["view_kind"]: job for job in contract["jobs"]}
    for view_kind in contract["view_order"]:
        call = run_job(contract=contract, job=jobs[view_kind], snapshot=snapshot)
        calls.append(call)
        call_path = calls_dir / f"{view_kind}.json"
        _write(call_path, call)
        if isinstance(call.get("estimated_cost_usd"), (int, float)):
            cumulative_cost += float(call["estimated_cost_usd"])
        if call.get("operational_status") != "ok":
            stop_reason = f"operational failure in {view_kind}"
            break
        if cumulative_cost > contract["budget"]["maximum_estimated_cost_usd"]:
            stop_reason = "estimated cost ceiling exceeded"
            break
    provider_calls = sum(int(call.get("provider_calls", 0)) for call in calls)
    result = {
        "schema_version": RESULT_SCHEMA,
        "status": (
            "repair_operational_and_custody_complete"
            if len(calls) == 5
            and provider_calls == 5
            and all(call.get("operational_status") == "ok" for call in calls)
            else "repair_stopped_operationally"
        ),
        "run_id": contract["run_id"],
        "case_id": contract["case"]["case_id"],
        "prompt_version": REPAIR_PROMPT_VERSION,
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
        "typed_admission_count": sum(
            call.get("typed_status") == "admitted" for call in calls
        ),
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
            "second_generic_repair_authorized": False,
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
        raise Phase3RepairError(
            "--authorization, --env-file, and --output are required for execution"
        )
    authorization = _load(args.authorization.resolve())
    validate_authorization(
        authorization, contract=contract, contract_path=contract_path
    )
    baseline._load_env(args.env_file.resolve())
    result = execute(contract=contract, output_dir=args.output)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
