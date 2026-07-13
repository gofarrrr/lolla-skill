#!/usr/bin/env python3
"""Run the frozen one-call quiet-library mechanism probe."""
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

from engine.system_b.reasoning_pattern_role_record_interpreter_v3 import (
    build_prompts_v3,
    compile_response_v3,
    response_schema_v2,
)
from engine.system_b.reasoning_process_views import canonical_json_bytes, sha256_bytes
from scripts.evals.reasoning_process_position_decomposition_transport import run_decomposed_task
from scripts.evals.run_conversation_state_microtask_probe import _load_env


REPORT = ROOT / "research/independent-quiet-library-mechanism-packet-2026-07-12/report.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def validate(contract: dict[str, Any]) -> tuple[dict[str, Any], dict[str, str]]:
    if contract.get("status") != "frozen_before_exactly_one_no_retry_call":
        raise RuntimeError("contract not frozen")
    budget = contract.get("budget", {})
    if budget.get("maximum_provider_calls") != 1 or budget.get("automatic_retries") != 0:
        raise RuntimeError("budget is not exactly one call with no retries")
    for frozen in contract.get("frozen_inputs", []):
        if sha(ROOT / frozen["path"]) != frozen["sha256"]:
            raise RuntimeError("frozen input drifted")
    report = load(REPORT)
    packet = load(ROOT / report["packet_path"])
    prompts = build_prompts_v3(packet)
    if sha(ROOT / report["packet_path"]) != report["packet_sha256"]:
        raise RuntimeError("packet drifted")
    if prompts["system_prompt_sha256"] != report["system_prompt_sha256"] or prompts["user_prompt_sha256"] != report["user_prompt_sha256"]:
        raise RuntimeError("prompt drifted")
    if sha256_bytes(canonical_json_bytes(response_schema_v2())) != report["response_schema_sha256"]:
        raise RuntimeError("response schema drifted")
    return packet, prompts


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
    packet, prompts = validate(contract)
    if args.dry_run:
        print(json.dumps({"status": "independent_quiet_mechanism_contract_valid", "provider_calls": 0}, indent=2))
        return 0
    authorization = load(args.authorization.resolve())
    expected_authorization = {
        "schema_version": "lolla.independent_quiet_mechanism_probe_authorization.v1",
        "status": "authorized_once_after_quiet_role_review_and_local_gates",
        "contract_path": str(contract_path.relative_to(ROOT)),
        "contract_sha256": sha(contract_path),
        "run_id": contract["run_id"],
        "maximum_provider_calls": 1,
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
    write(output / "call-01-started.json", {"task_id": packet["arm_id"], "automatic_retries": 0})
    call = run_decomposed_task(
        task_id=packet["arm_id"],
        contract=contract,
        prompts=prompts,
        schema=response_schema_v2(),
        response_schema_name="lolla_independent_quiet_mechanism",
        compile_candidate=lambda candidate: compile_response_v3(
            response=candidate,
            packet=packet,
            producer_kind="model_operator_eval",
            producer_id=contract["job"]["model"],
        ),
    )
    write(output / "call-01-result.json", call)
    assessments = (call.get("candidate_payload") or {}).get("assessments", [])
    statuses = {row["mechanism_id"]: row["joint_status"] for row in assessments}
    projection = (call.get("compiled") or {}).get("routing_projection", {})
    gates = {
        "operational": call.get("operational_status") == "ok" and call.get("compiled") is not None,
        "complete_nine_mechanism_review": len(statuses) == 9,
        "no_unresolved_mechanism": all(status != "unresolved" for status in statuses.values()),
        "no_ambiguous_mechanism": all(status != "ambiguous" for status in statuses.values()),
        "empty_routing_projection": projection.get("pattern_nodes") == [],
        "fact_free_projection": bool(call.get("compiled")) and call["compiled"]["fact_boundary"]["raw_text_included"] is False,
        "negative_review_preserved_as_probabilistic_evidence": bool(call.get("compiled"))
        and call["compiled"]["provenance"]["qualification_review_outcome"] == "no_unresolved_qualification_observed",
    }
    result = {
        "schema_version": "lolla.independent_quiet_mechanism_probe_result.v1",
        "status": "frozen_probe_preserved",
        "call": call,
        "evaluation": {
            "status": "quiet_mechanism_standdown_pass" if all(gates.values()) else "quiet_mechanism_gate_failure",
            "gates": gates,
            "statuses": statuses,
            "candidate_count": len(projection.get("pattern_nodes", [])),
            "scalar_score": None,
        },
        "provider_request_count": call.get("provider_calls", 0),
        "estimated_cost_usd": float(call.get("estimated_cost_usd") or 0),
        "boundary": contract["boundary"],
    }
    write(output / "result.json", result)
    print(json.dumps({"provider_request_count": result["provider_request_count"], "estimated_cost_usd": result["estimated_cost_usd"], "evaluation": result["evaluation"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
