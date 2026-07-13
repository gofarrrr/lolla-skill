from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from engine.system_b.reasoning_pattern_shadow import (
    ReasoningPatternShadowError,
    conversation_turn_numbers,
    lint_routing_projection,
    normalized_projection_signature,
    route_projection,
    seal_pattern_response,
)
from scripts.evals.run_reasoning_pattern_invariance_shadow import (
    evaluate_comparisons,
)


ROOT = Path(__file__).resolve().parents[1]


def _response(*mechanisms: str) -> dict:
    return {
        "patterns": [
            {
                "mechanism_id": mechanism,
                "subject_scope": "assistant",
                "state": "present",
                "source_turns": [1, 2],
            }
            for mechanism in mechanisms
        ]
    }


def _packet(response: dict, *, source: str = "fixture:a") -> dict:
    return seal_pattern_response(
        response,
        packet_id=source.replace(":", "_"),
        source_ref=source,
        source_sha256="a" * 64,
        valid_turn_numbers={1, 2, 3},
    )


def test_sealer_strips_facts_and_assigns_stable_ids() -> None:
    packet = _packet(
        _response(
            "acknowledged_constraint_not_gated",
            "ambiguous_signal_treated_as_commitment",
        )
    )
    projection = packet["routing_projection"]
    assert packet["lint"] == {"status": "passed", "violations": []}
    assert packet["fact_boundary"] == {
        "raw_text_included": False,
        "quotes_included": False,
        "entities_included": False,
        "case_quantities_included": False,
        "dates_included": False,
        "desired_outcome_included": False,
        "topic_labels_included": False,
    }
    assert [node["pattern_id"] for node in projection["pattern_nodes"]] == [
        "rp_001",
        "rp_002",
    ]
    serialized = json.dumps(projection).lower()
    for forbidden in ("dental", "$4k", "customer", "runway", "pivot"):
        assert forbidden not in serialized


def test_linter_rejects_free_text_case_field() -> None:
    projection = copy.deepcopy(_packet(_response("ambiguous_signal_treated_as_commitment"))["routing_projection"])
    projection["pattern_nodes"][0]["case_summary"] = "three dental customers"
    violations = lint_routing_projection(projection)
    assert {item["code"] for item in violations} == {"routing_node_shape_invalid"}


def test_same_patterns_have_same_signature_across_provenance() -> None:
    response = _response(
        "ambiguous_signal_treated_as_commitment",
        "acknowledged_constraint_not_gated",
    )
    first = _packet(response, source="fixture:facts_a")
    second = _packet(response, source="fixture:facts_b")
    assert first["provenance"] != second["provenance"]
    assert normalized_projection_signature(first) == normalized_projection_signature(second)


def test_mechanism_change_changes_signature_and_seed_candidates() -> None:
    routing = json.loads(
        (ROOT / "docs/conversation-understanding/reasoning-pattern-shadow-routing-v0.json").read_text()
    )
    known = {
        item["model_id"]
        for item in json.loads(
            (ROOT / "data/compiled/model_affordances/affordances_v60.json").read_text()
        )["model_records"]
    }
    base = _packet(
        _response(
            "ambiguous_signal_treated_as_commitment",
            "acknowledged_constraint_not_gated",
        )
    )
    changed = _packet(_response("other_review_required"), source="fixture:changed")
    base_route = route_projection(base, routing_contract=routing, known_model_ids=known)
    changed_route = route_projection(changed, routing_contract=routing, known_model_ids=known)
    assert normalized_projection_signature(base) != normalized_projection_signature(changed)
    assert base_route["seed_candidates"] != changed_route["seed_candidates"]
    assert changed_route["seed_candidates"] == []


def test_sealer_rejects_unknown_turn_and_uncontrolled_mechanism() -> None:
    bad_turn = _response("ambiguous_signal_treated_as_commitment")
    bad_turn["patterns"][0]["source_turns"] = [99]
    with pytest.raises(ReasoningPatternShadowError, match="unknown turn"):
        _packet(bad_turn)
    bad_mechanism = _response("dental_customer_signal")
    with pytest.raises(ReasoningPatternShadowError, match="not controlled"):
        _packet(bad_mechanism)


def test_fixture_turn_parser_finds_all_three_turns() -> None:
    for name in ("facts_a.txt", "facts_b.txt", "mechanism_changed.txt"):
        text = (ROOT / "tests/fixtures/reasoning_pattern_invariance" / name).read_text()
        assert conversation_turn_numbers(text) == {1, 2, 3}


def _shadow_result(packet: dict, routing: dict) -> dict:
    return {"status": "ok", "packet": packet, "routing": routing}


def test_comparison_evaluator_distinguishes_invariance_and_sensitivity() -> None:
    routing_contract = json.loads(
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
    same_response = _response(
        "ambiguous_signal_treated_as_commitment",
        "acknowledged_constraint_not_gated",
    )
    facts_a = _packet(same_response, source="fixture:facts_a")
    facts_b = _packet(same_response, source="fixture:facts_b")
    changed = _packet(_response("other_review_required"), source="fixture:changed")
    results = {
        "facts_a": _shadow_result(
            facts_a,
            route_projection(
                facts_a, routing_contract=routing_contract, known_model_ids=known
            ),
        ),
        "facts_b": _shadow_result(
            facts_b,
            route_projection(
                facts_b, routing_contract=routing_contract, known_model_ids=known
            ),
        ),
        "mechanism_changed": _shadow_result(
            changed,
            route_projection(
                changed, routing_contract=routing_contract, known_model_ids=known
            ),
        ),
    }
    contract = {
        "comparisons": [
            {
                "comparison_id": "fact_invariance",
                "comparison_type": "same_reasoning_different_facts",
                "fixture_ids": ["facts_a", "facts_b"],
                "expect_projection_equal": True,
                "expect_candidates_equal": True,
                "required_left_mechanisms": [
                    "ambiguous_signal_treated_as_commitment",
                    "acknowledged_constraint_not_gated",
                ],
                "required_absent_right_mechanisms": [],
            },
            {
                "comparison_id": "mechanism_sensitivity",
                "comparison_type": "same_facts_different_reasoning",
                "fixture_ids": ["facts_a", "mechanism_changed"],
                "expect_projection_equal": False,
                "expect_candidates_equal": False,
                "required_left_mechanisms": [
                    "ambiguous_signal_treated_as_commitment",
                    "acknowledged_constraint_not_gated",
                ],
                "required_absent_right_mechanisms": [
                    "ambiguous_signal_treated_as_commitment",
                    "acknowledged_constraint_not_gated",
                ],
            },
        ]
    }
    reviews = evaluate_comparisons(results, contract)
    assert [review["status"] for review in reviews] == ["passed", "passed"]
