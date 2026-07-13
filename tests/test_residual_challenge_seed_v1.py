import pytest

from engine.system_b.residual_challenge_representation_v1 import (
    build_residual_coverage_packet_v1,
    build_residual_discovery_packet_v1,
    compile_residual_coverage_response_v1,
)
from engine.system_b.residual_challenge_seed_v1 import (
    compile_residual_seed_response_v1,
    join_residual_seed_portfolio_v1,
)
from engine.system_b.simulated_reliability_v1 import SimulatedReliabilityError


EVIDENCE = [
    {"evidence_id": "e1", "speaker": "user", "turn_number": 1, "text": "Capital funding covers installation."},
    {"evidence_id": "e2", "speaker": "user", "turn_number": 2, "text": "The service also requires recurring staffing."},
    {"evidence_id": "e3", "speaker": "assistant", "turn_number": 2, "text": "Assign an operating owner and renewal review."},
]


def _packet():
    return build_residual_discovery_packet_v1(
        case_id="case",
        evidence_records=EVIDENCE,
        source_refs=[{"path": "fixture", "sha256": "abc"}],
    )


def _seed():
    return {
        "candidate_id": "rc1",
        "candidate_kind": "time_horizon",
        "challenge_question": "Who funds recurring operating capacity after capital funding ends?",
        "source_evidence_ids": ["e1", "e2"],
        "claim_status": "question_not_external_fact",
    }


def test_seed_contract_keeps_discovery_small_and_defers_enrichment():
    result = compile_residual_seed_response_v1(
        response={"candidates": [_seed()]},
        packet=_packet(),
        producer_id="test-model",
    )
    assert set(result["candidates"][0]) == {
        "candidate_id",
        "candidate_kind",
        "challenge_question",
        "source_evidence_ids",
        "claim_status",
    }
    assert result["boundary"]["enrichment_not_yet_authored"] is True


def test_seed_rejects_verbose_extra_fields_and_unknown_evidence():
    seed = _seed()
    seed["risk_if_ignored"] = "Extra work belongs later."
    with pytest.raises(SimulatedReliabilityError):
        compile_residual_seed_response_v1(
            response={"candidates": [seed]},
            packet=_packet(),
            producer_id="test-model",
        )
    seed = _seed()
    seed["source_evidence_ids"] = ["unknown"]
    with pytest.raises(SimulatedReliabilityError):
        compile_residual_seed_response_v1(
            response={"candidates": [seed]},
            packet=_packet(),
            producer_id="test-model",
        )


def test_seed_coverage_join_marks_active_enrichment_pending():
    packet = _packet()
    seed = _seed()
    result = compile_residual_seed_response_v1(
        response={"candidates": [seed]},
        packet=packet,
        producer_id="test-model",
    )
    coverage_packet = build_residual_coverage_packet_v1(
        case_id="case",
        candidate=seed,
        evidence_records=EVIDENCE,
    )
    coverage = compile_residual_coverage_response_v1(
        response={"candidate_id": "rc1", "joint_coverage": "not_covered", "source_evidence_ids": []},
        packet=coverage_packet,
        producer_id="test-model",
    )
    portfolio = join_residual_seed_portfolio_v1(
        seed_result=result,
        coverage_results=[coverage],
    )
    assert portfolio["counts"]["active_working_set"] == 1
    assert portfolio["portfolio_items"][0]["enrichment_status"] == "required_before_consumer_or_graph"
    assert portfolio["graph_handoff"]["direct_graph_routing_allowed"] is False


def test_seed_empty_and_missing_coverage_fail_closed():
    empty = compile_residual_seed_response_v1(
        response={"candidates": []},
        packet=_packet(),
        producer_id="test-model",
    )
    portfolio = join_residual_seed_portfolio_v1(seed_result=empty, coverage_results=[])
    assert portfolio["status"] == "model_authored_empty_residual_seed_portfolio_preserved"
    nonempty = compile_residual_seed_response_v1(
        response={"candidates": [_seed()]},
        packet=_packet(),
        producer_id="test-model",
    )
    with pytest.raises(SimulatedReliabilityError):
        join_residual_seed_portfolio_v1(seed_result=nonempty, coverage_results=[])
