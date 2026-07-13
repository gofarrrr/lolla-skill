from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from engine.system_b.joint_process_reasoning_shadow import (
    JointProcessReasoningShadowError,
    lint_joint_projection,
    normalized_joint_projection_signature,
    route_joint_projection,
    seal_joint_process_response,
)
from engine.system_b.reasoning_pattern_shadow import CONTROLLED_MECHANISMS


ROOT = Path(__file__).resolve().parents[1]


def _response(
    *,
    unresolved: set[str] | None = None,
    resolved: set[str] | None = None,
    ambiguous: set[str] | None = None,
) -> dict:
    unresolved = unresolved or set()
    resolved = resolved or set()
    ambiguous = ambiguous or set()
    rows = []
    for mechanism in sorted(CONTROLLED_MECHANISMS):
        if mechanism in unresolved:
            status, source_turns, resolution_turns = "unresolved", [1, 2], []
        elif mechanism in resolved:
            status, source_turns, resolution_turns = (
                "resolved_in_conversation",
                [1],
                [2],
            )
        elif mechanism in ambiguous:
            status, source_turns, resolution_turns = "ambiguous", [1, 2], []
        else:
            status, source_turns, resolution_turns = "not_observed", [], []
        rows.append(
            {
                "mechanism_id": mechanism,
                "joint_status": status,
                "source_turns": source_turns,
                "resolution_turns": resolution_turns,
            }
        )
    return {"mechanisms": rows}


def _packet(response: dict, source_ref: str = "fixture:a") -> dict:
    return seal_joint_process_response(
        response,
        packet_id=source_ref.replace(":", "_"),
        source_ref=source_ref,
        source_sha256="a" * 64,
        valid_turn_numbers={1, 2, 3},
    )


def _routing_inputs() -> tuple[dict, set[str]]:
    routing = json.loads(
        (
            ROOT
            / "docs/conversation-understanding/reasoning-pattern-shadow-routing-v0.json"
        ).read_text()
    )
    known = {
        item["model_id"]
        for item in json.loads(
            (ROOT / "data/compiled/model_affordances/affordances_v60.json").read_text()
        )["model_records"]
    }
    return routing, known


def test_joint_packet_reviews_every_mechanism_and_routes_only_unresolved() -> None:
    packet = _packet(
        _response(
            unresolved={"ambiguous_signal_treated_as_commitment"},
            resolved={"acknowledged_constraint_not_gated"},
            ambiguous={"missing_reversal_condition"},
        )
    )
    assert len(packet["mechanism_reviews"]) == len(CONTROLLED_MECHANISMS)
    assert packet["routing_projection"] == {
        "schema_version": "lolla.joint_process_reasoning_projection.v0",
        "active_nodes": [
            {
                "mechanism_id": "ambiguous_signal_treated_as_commitment",
                "joint_status": "unresolved",
            }
        ],
        "edge_nodes": [
            {
                "mechanism_id": "missing_reversal_condition",
                "joint_status": "ambiguous",
            }
        ],
        "manual_review_nodes": [],
        "contains_case_context": False,
    }
    serialized = json.dumps(packet["routing_projection"]).lower()
    for forbidden in ("warehouse", "museum", "$4k", "customer", "pivot"):
        assert forbidden not in serialized


def test_resolved_actor_local_pattern_keeps_audit_trace_but_has_no_seed() -> None:
    mechanism = "ambiguous_signal_treated_as_commitment"
    packet = _packet(_response(resolved={mechanism}))
    review = next(
        item for item in packet["mechanism_reviews"] if item["mechanism_id"] == mechanism
    )
    assert review["joint_status"] == "resolved_in_conversation"
    assert review["source_semantic_item_ids"] == ["turn:1"]
    assert review["resolution_semantic_item_ids"] == ["turn:2"]
    assert packet["routing_projection"]["active_nodes"] == []
    routing, known = _routing_inputs()
    result = route_joint_projection(
        packet,
        routing_contract=routing,
        known_model_ids=known,
    )
    assert result["active_seed_candidates"] == []
    assert result["edge_reserve_candidates"] == []


def test_same_joint_statuses_have_same_signature_across_provenance() -> None:
    response = _response(
        unresolved={
            "ambiguous_signal_treated_as_commitment",
            "acknowledged_constraint_not_gated",
        }
    )
    first = _packet(response, "fixture:facts_c")
    second = _packet(response, "fixture:facts_d")
    assert first["provenance"] != second["provenance"]
    assert normalized_joint_projection_signature(first) == (
        normalized_joint_projection_signature(second)
    )


def test_ambiguous_is_preserved_as_edge_not_erased_or_activated() -> None:
    mechanism = "missing_reversal_condition"
    packet = _packet(_response(ambiguous={mechanism}))
    routing, known = _routing_inputs()
    result = route_joint_projection(
        packet,
        routing_contract=routing,
        known_model_ids=known,
    )
    assert result["active_seed_candidates"] == []
    assert result["edge_reserve_candidates"]
    assert all(
        mechanism in item["pulled_by_mechanisms"]
        for item in result["edge_reserve_candidates"]
    )


def test_other_review_required_is_reserved_without_automatic_seed() -> None:
    packet = _packet(_response(unresolved={"other_review_required"}))
    projection = packet["routing_projection"]
    assert projection["active_nodes"] == []
    assert projection["manual_review_nodes"] == [
        {
            "mechanism_id": "other_review_required",
            "joint_status": "unresolved",
        }
    ]
    routing, known = _routing_inputs()
    result = route_joint_projection(
        packet,
        routing_contract=routing,
        known_model_ids=known,
    )
    assert result["active_seed_candidates"] == []
    assert result["manual_review_required"] is True


def test_joint_packet_rejects_incomplete_coverage_and_invalid_resolution() -> None:
    incomplete = _response()
    incomplete["mechanisms"].pop()
    with pytest.raises(JointProcessReasoningShadowError, match="cover controlled"):
        _packet(incomplete)

    invalid = _response(resolved={"acknowledged_constraint_not_gated"})
    row = next(
        item
        for item in invalid["mechanisms"]
        if item["mechanism_id"] == "acknowledged_constraint_not_gated"
    )
    row["resolution_turns"] = []
    with pytest.raises(JointProcessReasoningShadowError, match="requires resolution_turns"):
        _packet(invalid)


def test_joint_projection_linter_rejects_free_text_case_context() -> None:
    projection = copy.deepcopy(
        _packet(_response(unresolved={"missing_reversal_condition"}))[
            "routing_projection"
        ]
    )
    projection["active_nodes"][0]["case_summary"] = "warehouse customer promise"
    assert {item["code"] for item in lint_joint_projection(projection)} == {
        "routing_node_shape_invalid"
    }
