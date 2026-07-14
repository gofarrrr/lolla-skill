import json
from pathlib import Path

import pytest

from engine.system_b.residual_challenge_representation_v1 import (
    build_residual_coverage_packet_v1,
    build_residual_discovery_packet_v1,
    compile_residual_coverage_response_v1,
    compile_residual_discovery_response_v1,
    evidence_records_from_annotated_text_v1,
    join_residual_challenge_portfolio_v1,
)
from engine.system_b.simulated_reliability_v1 import SimulatedReliabilityError


EVIDENCE = [
    {
        "evidence_id": "e023",
        "speaker": "user",
        "turn_number": 3,
        "text": "The panels require embedded anchors and two storage buildings.",
    },
    {
        "evidence_id": "e078",
        "speaker": "user",
        "turn_number": 9,
        "text": "The shuttle has not priced staffing.",
    },
    {
        "evidence_id": "e099",
        "speaker": "user",
        "turn_number": 11,
        "text": "We spent less time on people, storage, traffic control, and night deployment.",
    },
    {
        "evidence_id": "e103",
        "speaker": "assistant",
        "turn_number": 11,
        "text": "Treat readiness as a city responsibility with staffing, exercises, and review.",
    },
]

ROOT = Path(__file__).resolve().parents[1]


def _case_evidence(case_id):
    path = (
        ROOT
        / "research/simulated-reliability-corpus-v1-2026-07-12/provider-free-role-input-preflight/transfer"
        / case_id
        / "position-wrapper.json"
    )
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    annotated = wrapper["packet"]["focal_region"]["annotated_sentence_text"]
    return evidence_records_from_annotated_text_v1(annotated)


def _discovery_packet():
    return build_residual_discovery_packet_v1(
        case_id="v1-case01-flood-infrastructure",
        evidence_records=EVIDENCE,
        source_refs=[{"path": "fixture", "sha256": "abc"}],
    )


def _candidate(candidate_id="rc1"):
    return {
        "candidate_id": candidate_id,
        "candidate_kind": "time_horizon",
        "challenge_question": "Who owns and funds recurring operating capacity after capital funding ends?",
        "structural_pressure": "A capital commitment may depend on recurring operating capacity with a different funding horizon.",
        "applicability_condition": "The path requires continuing staffing, storage, transport, or incident review after installation.",
        "risk_if_ignored": "Installed protection may exist without the recurring capacity needed to deliver its promised service.",
        "force_boundary": "Do not assume a future funding gap exists; ask for ownership, duration, and a renewal decision.",
        "source_evidence_ids": ["e023", "e078", "e099"],
        "claim_status": "question_not_external_fact",
    }


def _compile_discovery(*candidates):
    return compile_residual_discovery_response_v1(
        response={"candidates": list(candidates)},
        packet=_discovery_packet(),
        producer_id="test-model",
    )


def test_discovery_excludes_assistant_frame_and_preserves_source_grounded_question():
    packet = _discovery_packet()
    assert {row["evidence_id"] for row in packet["user_evidence"]} == {
        "e023",
        "e078",
        "e099",
    }
    result = compile_residual_discovery_response_v1(
        response={"candidates": [_candidate()]},
        packet=packet,
        producer_id="test-model",
    )
    assert result["candidates"][0]["candidate_kind"] == "time_horizon"
    assert result["boundary"]["coverage_not_yet_judged"] is True


def test_discovery_rejects_unknown_or_assistant_only_evidence():
    packet = _discovery_packet()
    candidate = _candidate()
    candidate["source_evidence_ids"] = ["e103"]
    with pytest.raises(SimulatedReliabilityError):
        compile_residual_discovery_response_v1(
            response={"candidates": [candidate]},
            packet=packet,
            producer_id="test-model",
        )


def test_discovery_rejects_candidate_identity_gaps_and_packet_tampering():
    packet = _discovery_packet()
    candidate = _candidate("rc2")
    with pytest.raises(SimulatedReliabilityError):
        compile_residual_discovery_response_v1(
            response={"candidates": [candidate]},
            packet=packet,
            producer_id="test-model",
        )
    packet["case_id"] = "tampered"
    with pytest.raises(SimulatedReliabilityError):
        compile_residual_discovery_response_v1(
            response={"candidates": []},
            packet=packet,
            producer_id="test-model",
        )


def test_separate_coverage_and_join_keep_uncovered_active_and_covered_preserved():
    first = _candidate("rc1")
    second = _candidate("rc2")
    second["candidate_kind"] = "stakeholder_or_distribution"
    second["challenge_question"] = "Could the protected corridor create expectations that reshape later service or land-use choices?"
    discovery = _compile_discovery(first, second)
    coverage_results = []
    for candidate, coverage, source_ids in (
        (first, "not_covered", []),
        (second, "operationalized", ["e103"]),
    ):
        packet = build_residual_coverage_packet_v1(
            case_id=discovery["case_id"],
            candidate=candidate,
            evidence_records=EVIDENCE,
        )
        coverage_results.append(
            compile_residual_coverage_response_v1(
                response={
                    "candidate_id": candidate["candidate_id"],
                    "joint_coverage": coverage,
                    "source_evidence_ids": source_ids,
                },
                packet=packet,
                producer_id="test-model",
            )
        )
    portfolio = join_residual_challenge_portfolio_v1(
        discovery_result=discovery,
        coverage_results=coverage_results,
    )
    assert portfolio["counts"] == {
        "discovered_candidates": 2,
        "active_working_set": 1,
        "edge_reserve": 0,
        "covered_receipt": 1,
    }
    assert len(portfolio["portfolio_items"]) == 2
    assert portfolio["graph_handoff"]["direct_graph_routing_allowed"] is False


def test_ambiguous_coverage_enters_edge_reserve_without_deletion():
    candidate = _candidate()
    discovery = _compile_discovery(candidate)
    packet = build_residual_coverage_packet_v1(
        case_id=discovery["case_id"],
        candidate=candidate,
        evidence_records=EVIDENCE,
    )
    coverage = compile_residual_coverage_response_v1(
        response={
            "candidate_id": "rc1",
            "joint_coverage": "ambiguous",
            "source_evidence_ids": ["e099", "e103"],
        },
        packet=packet,
        producer_id="test-model",
    )
    portfolio = join_residual_challenge_portfolio_v1(
        discovery_result=discovery,
        coverage_results=[coverage],
    )
    assert portfolio["counts"]["edge_reserve"] == 1
    assert portfolio["portfolio_items"][0]["active_pressure_eligible"] is False


def test_coverage_custody_rejects_missing_or_invented_citations():
    candidate = _candidate()
    packet = build_residual_coverage_packet_v1(
        case_id="v1-case01-flood-infrastructure",
        candidate=candidate,
        evidence_records=EVIDENCE,
    )
    with pytest.raises(SimulatedReliabilityError):
        compile_residual_coverage_response_v1(
            response={
                "candidate_id": "rc1",
                "joint_coverage": "operationalized",
                "source_evidence_ids": [],
            },
            packet=packet,
            producer_id="test-model",
        )
    with pytest.raises(SimulatedReliabilityError):
        compile_residual_coverage_response_v1(
            response={
                "candidate_id": "rc1",
                "joint_coverage": "not_covered",
                "source_evidence_ids": ["invented"],
            },
            packet=packet,
            producer_id="test-model",
        )


def test_model_authored_empty_discovery_is_valid_but_cannot_masquerade_as_graph_input():
    discovery = _compile_discovery()
    portfolio = join_residual_challenge_portfolio_v1(
        discovery_result=discovery,
        coverage_results=[],
    )
    assert portfolio["status"] == "model_authored_empty_residual_portfolio_preserved"
    assert portfolio["counts"]["discovered_candidates"] == 0
    assert portfolio["graph_handoff"]["status"] == "not_built_requires_separate_probabilistic_abstraction"


def test_join_rejects_missing_coverage_instead_of_silently_dropping_candidate():
    discovery = _compile_discovery(_candidate())
    with pytest.raises(SimulatedReliabilityError):
        join_residual_challenge_portfolio_v1(
            discovery_result=discovery,
            coverage_results=[],
        )


def test_actual_case01_contract_can_preserve_the_missed_long_horizon_pressure():
    evidence = _case_evidence("v1-case01-flood-infrastructure")
    packet = build_residual_discovery_packet_v1(
        case_id="v1-case01-flood-infrastructure",
        evidence_records=evidence,
        source_refs=[{"path": "case01", "sha256": "fixture"}],
    )
    candidate = {
        "candidate_id": "rc1",
        "candidate_kind": "time_horizon",
        "challenge_question": "Who owns and funds recurring deployment, storage, shuttle, training, and incident-review capacity after capital funding ends?",
        "structural_pressure": "A capital commitment may depend on recurring operating capacity governed by a different funding horizon.",
        "applicability_condition": "The promised service requires continuing staffing, storage, transport, training, and review after installation.",
        "risk_if_ignored": "The installed asset may persist while the recurring capacity needed to deliver the service weakens.",
        "force_boundary": "Do not assert that funding will disappear; require an owner, duration, renewal process, and reopening condition.",
        "source_evidence_ids": ["e024", "e078", "e099", "e104", "e105"],
        "claim_status": "question_not_external_fact",
    }
    discovery = compile_residual_discovery_response_v1(
        response={"candidates": [candidate]},
        packet=packet,
        producer_id="provider-free-fixture",
    )
    coverage_packet = build_residual_coverage_packet_v1(
        case_id=discovery["case_id"],
        candidate=candidate,
        evidence_records=evidence,
    )
    coverage = compile_residual_coverage_response_v1(
        response={
            "candidate_id": "rc1",
            "joint_coverage": "not_covered",
            "source_evidence_ids": [],
        },
        packet=coverage_packet,
        producer_id="provider-free-fixture",
    )
    portfolio = join_residual_challenge_portfolio_v1(
        discovery_result=discovery,
        coverage_results=[coverage],
    )
    assert portfolio["counts"]["active_working_set"] == 1
    assert portfolio["portfolio_items"][0]["claim_status"] == "question_not_external_fact"


def test_actual_case07_contract_preserves_already_operationalized_candidate_as_receipt():
    evidence = _case_evidence("v1-case07-cooperative-scheduling")
    packet = build_residual_discovery_packet_v1(
        case_id="v1-case07-cooperative-scheduling",
        evidence_records=evidence,
        source_refs=[{"path": "case07", "sha256": "fixture"}],
    )
    candidate = {
        "candidate_id": "rc1",
        "candidate_kind": "omitted_dependency",
        "challenge_question": "Could recurring extra shifts be evidence of a permanent staffing need rather than optional demand?",
        "structural_pressure": "Repeated optional capacity may conceal a recurring structural resource requirement.",
        "applicability_condition": "The same roles repeatedly need extra hours across the bounded trial.",
        "risk_if_ignored": "A permanent staffing need could remain classified as voluntary flexibility.",
        "force_boundary": "Do not infer a new position from one spike; use the prewritten recurring-gap evidence threshold.",
        "source_evidence_ids": ["e079", "e080", "e081", "e095"],
        "claim_status": "question_not_external_fact",
    }
    discovery = compile_residual_discovery_response_v1(
        response={"candidates": [candidate]},
        packet=packet,
        producer_id="provider-free-fixture",
    )
    coverage_packet = build_residual_coverage_packet_v1(
        case_id=discovery["case_id"],
        candidate=candidate,
        evidence_records=evidence,
    )
    coverage = compile_residual_coverage_response_v1(
        response={
            "candidate_id": "rc1",
            "joint_coverage": "operationalized",
            "source_evidence_ids": ["e083", "e095", "e101"],
        },
        packet=coverage_packet,
        producer_id="provider-free-fixture",
    )
    portfolio = join_residual_challenge_portfolio_v1(
        discovery_result=discovery,
        coverage_results=[coverage],
    )
    assert portfolio["counts"]["covered_receipt"] == 1
    assert portfolio["counts"]["active_working_set"] == 0
    assert portfolio["portfolio_items"][0]["portfolio_tier"] == "covered_receipt"
