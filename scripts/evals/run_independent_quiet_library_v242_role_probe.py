#!/usr/bin/env python3
"""Run the frozen two-call quiet-library v2.4.2 role probe."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.reasoning_process_position_role_first_v24 import (
    build_position_starting_packet_v24,
    build_position_starting_prompts_v24,
    compile_position_starting_response_v24,
    position_starting_response_schema_v24,
)
from engine.system_b.reasoning_process_position_role_first_v242 import (
    build_packet_v242,
    build_prompts_v242,
    compile_response_v242,
    join_v242,
    response_schema_v242,
)
from engine.system_b.reasoning_process_views import canonical_json_bytes, sha256_bytes
from scripts.evals.reasoning_process_position_decomposition_transport import run_decomposed_task
from scripts.evals.run_conversation_state_microtask_probe import _load_env


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def validate(contract: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, str], dict[str, str]]:
    if contract.get("status") != "frozen_before_exactly_two_no_retry_calls":
        raise RuntimeError("contract not frozen")
    budget = contract.get("budget", {})
    if budget.get("maximum_provider_calls") != 2 or budget.get("automatic_retries") != 0:
        raise RuntimeError("budget is not exactly two calls with no retries")
    for frozen in contract.get("frozen_inputs", []):
        if sha(ROOT / frozen["path"]) != frozen["sha256"]:
            raise RuntimeError("frozen input drifted")
    job = contract["job"]
    wrapper = load(ROOT / job["packet_path"])
    starting_packet = build_position_starting_packet_v24(wrapper=wrapper, role="starting")
    paired_packet = build_packet_v242(wrapper=wrapper)
    starting_prompts = build_position_starting_prompts_v24(starting_packet)
    paired_prompts = build_prompts_v242(paired_packet)
    expected = {
        "starting": {
            "system_prompt_sha256": starting_prompts["system_prompt_sha256"],
            "user_prompt_sha256": starting_prompts["user_prompt_sha256"],
            "response_schema_sha256": sha256_bytes(canonical_json_bytes(position_starting_response_schema_v24("starting"))),
        },
        "current_qualification": {
            "system_prompt_sha256": paired_prompts["system_prompt_sha256"],
            "user_prompt_sha256": paired_prompts["user_prompt_sha256"],
            "response_schema_sha256": sha256_bytes(canonical_json_bytes(response_schema_v242())),
        },
    }
    if job["request_contracts"] != expected:
        raise RuntimeError("request contract drifted")
    return wrapper, {"starting": starting_packet, "paired": paired_packet}, starting_prompts, paired_prompts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    contract_path = args.contract.resolve()
    contract = load(contract_path)
    wrapper, packets, starting_prompts, paired_prompts = validate(contract)
    if args.dry_run:
        print(json.dumps({"status": "independent_quiet_v242_role_contract_valid", "provider_calls": 0}, indent=2))
        return 0
    authorization = load(args.authorization.resolve())
    expected_authorization = {
        "schema_version": "lolla.independent_quiet_v242_role_probe_authorization.v1",
        "status": "authorized_once_after_source_target_and_local_gates",
        "contract_path": str(contract_path.relative_to(ROOT)),
        "contract_sha256": sha(contract_path),
        "run_id": contract["run_id"],
        "maximum_provider_calls": 2,
        "automatic_retries": 0,
        "fallback_models": 0,
        "evaluator_calls": 0,
        "embedding_calls": 0,
        "graph_calls": 0,
        "runtime_calls": 0,
    }
    if authorization != expected_authorization:
        raise RuntimeError("authorization drifted")
    output = args.output_dir.resolve()
    if not output.is_dir() or (output / "result.json").exists() or list(output.glob("call-*-started.json")):
        raise RuntimeError("output absent, complete, or already started")
    _load_env(args.env_file.resolve())
    single_contract = {**contract, "job": {**contract["model_route"], "case_id": contract["case_id"]}}

    write(output / "call-01-started.json", {"task_id": "starting", "case_id": contract["case_id"], "automatic_retries": 0})
    starting_call = run_decomposed_task(
        task_id="starting",
        contract=single_contract,
        prompts=starting_prompts,
        schema=position_starting_response_schema_v24("starting"),
        response_schema_name="lolla_independent_quiet_v242_starting",
        compile_candidate=lambda candidate: compile_position_starting_response_v24(
            response=candidate,
            packet=packets["starting"],
            producer_kind="model_operator_eval",
            producer_id=contract["model_route"]["model"],
        ),
    )
    write(output / "call-01-result.json", starting_call)

    write(output / "call-02-started.json", {"task_id": "current_qualification", "case_id": contract["case_id"], "automatic_retries": 0})
    paired_call = run_decomposed_task(
        task_id="current_qualification",
        contract=single_contract,
        prompts=paired_prompts,
        schema=response_schema_v242(),
        response_schema_name="lolla_independent_quiet_v242_current_qualification",
        compile_candidate=lambda candidate: compile_response_v242(
            response=candidate,
            wrapper=wrapper,
            producer_kind="model_operator_eval",
            producer_id=contract["model_route"]["model"],
        ),
    )
    write(output / "call-02-result.json", paired_call)
    calls = [starting_call, paired_call]
    joined = None
    if all(call.get("operational_status") == "ok" and call.get("compiled") for call in calls):
        joined = join_v242(starting_compiled=starting_call["compiled"], paired_compiled=paired_call["compiled"])
    review = paired_call.get("compiled", {}).get("qualification_review", {})
    gates = {
        "both_calls_operational": all(call.get("operational_status") == "ok" and call.get("compiled") for call in calls),
        "join_complete": bool(joined) and joined["status"] == "quiet_capable_position_join_complete",
        "starting_present": bool(joined) and joined["role_observations"]["starting"] is not None,
        "current_present": bool(joined) and joined["role_observations"]["current"] is not None,
        "negative_qualification_review": review.get("outcome") == "no_unresolved_qualification_observed",
        "qualification_record_absent": bool(joined) and joined["role_observations"]["qualification"] is None,
        "review_has_source_custody": bool(review.get("source_evidence")),
    }
    result = {
        "schema_version": "lolla.independent_quiet_v242_role_probe_result.v1",
        "status": "frozen_probe_preserved",
        "case_id": contract["case_id"],
        "calls": calls,
        "joined": joined,
        "evaluation": {
            "status": "quiet_role_gates_pass_source_review_required" if all(gates.values()) else "quiet_role_gate_failure",
            "gates": gates,
            "semantic_review_status": "source_review_required",
            "scalar_score": None,
        },
        "provider_request_count": sum(call.get("provider_calls", 0) for call in calls),
        "estimated_cost_usd": round(sum(float(call.get("estimated_cost_usd") or 0) for call in calls), 12),
        "boundary": contract["boundary"],
    }
    write(output / "result.json", result)
    print(json.dumps({"provider_request_count": result["provider_request_count"], "estimated_cost_usd": result["estimated_cost_usd"], "evaluation": result["evaluation"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
