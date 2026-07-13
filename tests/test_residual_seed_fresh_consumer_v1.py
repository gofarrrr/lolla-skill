import copy
import json
from pathlib import Path

import pytest

from engine.system_b.canonical_model_selection import build_assessment_cards
from engine.system_b.residual_seed_fresh_consumer_v1 import (
    build_residual_seed_fresh_consumer_bundle_v1,
    compile_residual_seed_fresh_consumer_response_v1,
)
from engine.system_b.residual_seed_graph_recall_v1 import (
    build_residual_seed_graph_recall_v1,
)
from engine.system_b.simulated_reliability_v1 import SimulatedReliabilityError


ROOT = Path(__file__).resolve().parents[1]


def _load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _bundle():
    seed = _load("research/residual-challenge-seed-case01-probe-2026-07-13/t1/result.json")
    knowledge = _load("data/knowledge_graph.json")
    recall = build_residual_seed_graph_recall_v1(
        seed_portfolio=seed["joined_seed_portfolio"],
        routing_contract=_load("docs/conversation-understanding/residual-challenge-seed-graph-routing-v1.json"),
        knowledge_graph=knowledge,
        relationship_graph=_load("data/relationship_graph.json"),
    )
    source = ROOT / "research/simulated-reliability-corpus-v1-2026-07-12/naturalized-transfer-sources/v1-case01-flood-infrastructure.txt"
    return build_residual_seed_fresh_consumer_bundle_v1(
        case_id=seed["case_id"],
        conversation=source.read_text(encoding="utf-8"),
        seed_portfolio=seed["joined_seed_portfolio"],
        recall=recall,
        challenge_cards=build_assessment_cards(knowledge["models"]),
        source_refs=[],
    )


def test_handoff_preserves_all_active_and_reserve_candidates_without_coverage_gate():
    bundle = _bundle()
    packet = bundle["packet"]
    assert len(packet["pressure_portfolio"]) == 9
    assert packet["portfolio_structure"] == {
        "direct_active_count": 6,
        "graph_active_count": 3,
        "active_candidate_count": 9,
        "direct_reserve_count": 3,
        "graph_reserve_count": 23,
        "active_selection_operation": "deterministic_cap_and_declared_relation_slots",
        "active_selection_is_semantic_ranking": False,
    }
    assert len(packet["residual_seed_context"]) == 3
    assert all(row["joint_coverage"] == "operationalized" for row in packet["residual_seed_context"])
    assert packet["instructions"]["coverage_metadata_may_suppress_pressure"] is False
    assert packet["boundary"]["all_reserve_candidates_inspectable"] is True
    assert bundle["call_policy"]["provider_calls_made"] == 0
    assert bundle["call_policy"]["next_call_authorized"] is False
    assert bundle["call_policy"]["premium_testing_model_prohibited"] == "google/gemini-3.5-flash"
    assert len(bundle["prompts"]["user_prompt"].encode("utf-8")) < 40000
    assert '"exact_provenance_location":"persisted_packet.reserve_custody"' in bundle["prompts"]["user_prompt"]
    assert '"graph_provenance"' not in bundle["prompts"]["user_prompt"]


def test_handoff_is_deterministic_and_uses_full_conversation():
    first = _bundle()
    second = _bundle()
    assert first == second
    assert first["packet"]["source_turn_numbers"] == list(range(1, 13))
    assert first["bundle_sha256"] == second["bundle_sha256"]


def test_handoff_rejects_recall_that_uses_coverage_as_gate():
    seed = _load("research/residual-challenge-seed-case01-probe-2026-07-13/t1/result.json")
    knowledge = _load("data/knowledge_graph.json")
    recall = build_residual_seed_graph_recall_v1(
        seed_portfolio=seed["joined_seed_portfolio"],
        routing_contract=_load("docs/conversation-understanding/residual-challenge-seed-graph-routing-v1.json"),
        knowledge_graph=knowledge,
        relationship_graph=_load("data/relationship_graph.json"),
    )
    recall = copy.deepcopy(recall)
    recall["boundary"]["joint_coverage_used_for_admission"] = True
    with pytest.raises(SimulatedReliabilityError, match="hash is invalid|hybrid boundary"):
        build_residual_seed_fresh_consumer_bundle_v1(
            case_id=seed["case_id"],
            conversation="[Turn 1] USER:\nA\n[Turn 1] ASSISTANT:\nB\n",
            seed_portfolio=seed["joined_seed_portfolio"],
            recall=recall,
            challenge_cards=build_assessment_cards(knowledge["models"]),
            source_refs=[],
        )


def test_compiler_requires_disposition_for_every_active_candidate():
    bundle = _bundle()
    packet = bundle["packet"]
    rows = []
    for item in packet["pressure_portfolio"]:
        rows.append(
            {
                "model_id": item["model_id"],
                "disposition": "park",
                "source_turn_numbers": [1],
                "effect": "uncertainty_change",
                "strongest_plausible_application": "The lens may expose a source-grounded dependency.",
                "disposition_reason": "The conversation does not yet establish whether it changes the decision.",
                "risk_if_forced": "It could turn a question into an unsupported conclusion.",
                "reopen_condition": "Reopen if operating evidence shows the dependency changes service continuity.",
            }
        )
    response = {
        "candidate_dispositions": rows,
        "reconsidered_answer": "Keep the current conclusion conditional while gathering the named evidence.",
        "change_summary": "No conclusion changed; the unresolved dependencies remain explicit.",
    }
    compiled = compile_residual_seed_fresh_consumer_response_v1(
        response=response, packet=packet
    )
    assert compiled["all_active_candidates_accounted_for"] is True
    assert compiled["coverage_metadata_used_as_gate"] is False
    with pytest.raises(SimulatedReliabilityError, match="coverage"):
        compile_residual_seed_fresh_consumer_response_v1(
            response={**response, "candidate_dispositions": rows[:-1]}, packet=packet
        )
