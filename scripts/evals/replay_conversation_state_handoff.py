#!/usr/bin/env python3
"""Provider-free replay of reviewed conversation-state handoff packets."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from engine.system_b.conversation_state_handoff import (
    build_fact_free_routing_boundary,
    validate_conversation_state_handoff,
)


CONTRACT_SCHEMA = "lolla.conversation_state_handoff_replay_contract.v1"
RESULT_SCHEMA = "lolla.conversation_state_handoff_replay_result.v1"


class ConversationStateReplayError(ValueError):
    pass


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ConversationStateReplayError(f"expected JSON object: {path}")
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _repo_path(value: object, *, repo_root: Path) -> Path:
    path = Path(str(value))
    if path.is_absolute():
        raise ConversationStateReplayError("contract paths must be repo-relative")
    resolved = (repo_root / path).resolve()
    resolved.relative_to(repo_root.resolve())
    return resolved


def _evidence_count(packet: Mapping[str, Any]) -> int:
    count = len(packet["decision_summary"]["source_evidence"])
    count += sum(len(item["contributions"]) for item in packet["positions"])
    for item in packet["threads"]:
        count += 2 + len(item["responses"])
    count += sum(len(item["source_evidence"]) for item in packet["constraints"])
    return count


def run_replay(contract: Mapping[str, Any], *, repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    if contract.get("schema_version") != CONTRACT_SCHEMA:
        raise ConversationStateReplayError("unexpected replay contract schema")
    if contract.get("status") != "frozen_provider_free":
        raise ConversationStateReplayError("replay contract is not frozen")
    module = contract.get("module", {})
    baseline = contract.get("baseline", {})
    for label, record in (("module", module), ("baseline", baseline)):
        if not isinstance(record, Mapping):
            raise ConversationStateReplayError(f"{label} lock missing")
        path = _repo_path(record.get("path"), repo_root=repo_root)
        if not path.is_file() or _sha(path) != record.get("sha256"):
            raise ConversationStateReplayError(f"{label} hash mismatch")

    baseline_payload = _load(_repo_path(baseline["path"], repo_root=repo_root))
    baseline_aggregate = baseline_payload.get("aggregate", {})
    cases = contract.get("cases")
    if not isinstance(cases, list):
        raise ConversationStateReplayError("cases must be an array")

    case_results: list[dict[str, Any]] = []
    ownership_counts: Counter[str] = Counter()
    disposition_counts: Counter[str] = Counter()
    claim_mode_counts: Counter[str] = Counter()
    total_positions = total_threads = total_constraints = total_evidence = 0
    total_direct_graph_seeds = 0
    for record in cases:
        if not isinstance(record, Mapping):
            raise ConversationStateReplayError("case contract row invalid")
        packet_path = _repo_path(record.get("path"), repo_root=repo_root)
        if not packet_path.is_file() or _sha(packet_path) != record.get("sha256"):
            raise ConversationStateReplayError(f"case hash mismatch: {record.get('case_id')}")
        packet = _load(packet_path)
        if packet.get("case_id") != record.get("case_id"):
            raise ConversationStateReplayError("case identity mismatch")
        source_path = _repo_path(packet["source"]["path"], repo_root=repo_root)
        source_text = source_path.read_text(encoding="utf-8")
        violations = validate_conversation_state_handoff(packet, source_text=source_text)
        if violations:
            raise ConversationStateReplayError(
                f"case validation failed: {record.get('case_id')}: {violations}"
            )
        positions = packet["positions"]
        threads = packet["threads"]
        constraints = packet["constraints"]
        if len(constraints) != int(record.get("constraint_count", -1)):
            raise ConversationStateReplayError("case constraint count mismatch")
        if [item["ownership"] for item in positions] != [record.get("position_ownership")]:
            raise ConversationStateReplayError("case position ownership mismatch")
        if [item["disposition"] for item in threads] != [record.get("thread_disposition")]:
            raise ConversationStateReplayError("case thread disposition mismatch")
        projection = build_fact_free_routing_boundary(packet)
        direct_seeds = int(projection["direct_graph_seed_count"])
        total_direct_graph_seeds += direct_seeds
        total_positions += len(positions)
        total_threads += len(threads)
        total_constraints += len(constraints)
        evidence_count = _evidence_count(packet)
        total_evidence += evidence_count
        ownership_counts.update(item["ownership"] for item in positions)
        disposition_counts.update(item["disposition"] for item in threads)
        claim_mode_counts.update(item["claim_mode"] for item in constraints)
        case_results.append(
            {
                "case_id": packet["case_id"],
                "status": "passed",
                "position_count": len(positions),
                "thread_count": len(threads),
                "constraint_count": len(constraints),
                "exact_source_evidence_count": evidence_count,
                "position_ownership": positions[0]["ownership"],
                "thread_disposition": threads[0]["disposition"],
                "direct_graph_seed_count": direct_seeds,
                "routing_projection_contains_case_context": projection["contains_case_context"],
            }
        )

    observed = {
        "case_count": len(case_results),
        "position_count": total_positions,
        "joint_position_count": ownership_counts.get("joint", 0),
        "thread_count": total_threads,
        "constraint_count": total_constraints,
        "exact_source_evidence_count": total_evidence,
        "direct_graph_seed_count": total_direct_graph_seeds,
        "position_ownership_counts": dict(sorted(ownership_counts.items())),
        "thread_disposition_counts": dict(sorted(disposition_counts.items())),
        "claim_mode_counts": dict(sorted(claim_mode_counts.items())),
    }
    required = contract.get("required_aggregate", {})
    gates = {
        key: observed.get(key) == expected
        for key, expected in required.items()
    }
    gates.update(
        {
            "all_case_packets_passed": all(item["status"] == "passed" for item in case_results),
            "all_evidence_exactly_source_grounded": total_evidence > 0,
            "case_context_excluded_from_routing_projection": all(
                item["routing_projection_contains_case_context"] is False
                for item in case_results
            ),
            "baseline_failure_counts_preserved": (
                int(baseline_aggregate.get("cases_with_user_final_plan_recast_as_assistant_recommendation", -1)) == 5
                and int(baseline_aggregate.get("correct_dropped_thread_status_items", -1)) == 0
                and int(baseline_aggregate.get("reviewed_load_bearing_constraints", -1)) == 43
            ),
        }
    )
    failed = [key for key, passed in gates.items() if not passed]
    return {
        "schema_version": RESULT_SCHEMA,
        "status": "passed" if not failed else "failed",
        "comparison_kind": "representation_capacity_against_reviewed_failures_not_new_extractor_output",
        "contract_sha256": hashlib.sha256(
            json.dumps(contract, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
        "baseline": {
            "proposal_provenance_case_precision": baseline_aggregate.get("proposal_provenance_case_precision"),
            "thread_status_precision": baseline_aggregate.get("thread_status_precision"),
            "strict_constraint_coverage": baseline_aggregate.get("strict_constraint_coverage"),
        },
        "observed": observed,
        "case_results": case_results,
        "gates": gates,
        "failed_gates": failed,
        "interpretation": {
            "representation_can_express_reviewed_state": not failed,
            "production_extractor_can_populate_state": "not_tested",
            "semantic_label_correctness": "human_reviewed_same_session_not_independent",
            "consumer_context_effect": "not_tested",
            "graph_effect": "none_direct_routing_forbidden",
        },
        "provider_calls": 0,
        "graph_calls": 0,
        "runtime_modified": False,
        "next_decision": "design_one_bounded_extraction_only_probe_after_prompt_and_schema_freeze",
        "non_claims": [
            "not_extractor_improvement",
            "not_independent_gold",
            "not_graph_value",
            "not_runtime_authority",
            "not_provider_probe_execution_authority",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", required=True)
    args = parser.parse_args()
    contract = _load(Path(args.contract))
    print(json.dumps(run_replay(contract), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
