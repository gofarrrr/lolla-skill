from __future__ import annotations

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_marker_entity_loss_followup import (  # noqa: E402
    build_marker_entity_followup_contract,
    build_marker_entity_followup_result,
    build_static_step6_replay,
    build_static_visibility_judgment,
    detect_marker_entity_loss,
    load_marker_entity_followup_contract,
    validate_marker_entity_followup_contract,
    validate_marker_entity_followup_result,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_contract_pins_three_attempts_and_null_evidence_rule() -> None:
    contract = build_marker_entity_followup_contract()

    validate_marker_entity_followup_contract(contract)

    assert contract["schema_version"] == "pre_step6_marker_entity_loss_followup.v1"
    assert contract["followup_id"] == "marker_entity_loss_followup_v0"
    assert contract["status"] == "planned_non_promotional"
    assert contract["target_failure_mode"] == [
        "step6_marks_additive_pressure_present",
        "deck_answer_preserves_category_markers",
        "deck_answer_drops_anchor_entities",
        "reviewers_prefer_anchor",
    ]
    assert contract["attempt_rule"] == {
        "max_attempts": 3,
        "no_trigger_result": "not_observed",
        "null_evidence_warning": (
            "If no attempt produces additive pressure plus anchor-entity loss, "
            "the omission-gate weakness remains unclosed."
        ),
    }
    assert contract["confirmation_rule"]["split_reviewer_outcome"] == "ambiguous_visibility"
    assert [case["attempt_id"] for case in contract["attempt_cases"]] == [
        "marker-entity-attempt-1-resource-generalization",
        "marker-entity-attempt-2-tripwire-compression",
        "marker-entity-attempt-3-actor-sequence-blur",
    ]
    for case in contract["attempt_cases"]:
        assert case["selection_timing"] == "pre_run"
        assert case["critical_anchor_entities"]
        assert case["category_markers"]


def test_marker_entity_loss_detector_requires_markers_present_and_entities_missing() -> None:
    contract = build_marker_entity_followup_contract()
    case = contract["attempt_cases"][0]

    detection = detect_marker_entity_loss(
        case=case,
        answer=(
            "Use professional support and keep the safety plan active. Watch for "
            "tripwires and preserve communication boundaries, but do not assume "
            "quiet behavior means the risk has disappeared."
        ),
    )

    assert detection["markers_present"] is True
    assert detection["anchor_entities_missing"] is True
    assert detection["failure_shape_observed"] is True
    assert "RAINN" in detection["missing_entities"]


def test_confirmed_marker_entity_false_positive_triggers_design_review() -> None:
    contract = build_marker_entity_followup_contract()
    case_id = "marker-entity-attempt-1-resource-generalization"
    step6_replay = build_static_step6_replay(
        contract=contract,
        case_id=case_id,
        ledger_signal="additive_pressure_present",
        answer_mode="marker_only_entity_loss",
    )
    reviewer_a = build_static_visibility_judgment(
        contract=contract,
        step6_replay=step6_replay,
        model="openai/gpt-5.1-chat",
        visibility_label="false_positive_visible",
        winner_arm="anchor_visible",
    )
    reviewer_b = build_static_visibility_judgment(
        contract=contract,
        step6_replay=step6_replay,
        model="google/gemini-3.1-flash-lite",
        visibility_label="false_positive_visible",
        winner_arm="anchor_visible",
    )

    result = build_marker_entity_followup_result(
        contract=contract,
        step6_replays=[step6_replay],
        judgments=[reviewer_a, reviewer_b],
    )

    validate_marker_entity_followup_result(result)

    assert result["followup_result"] == "design_review_required"
    assert result["attempt_results"][0]["construction_label"] == "failure_shape_observed"
    assert result["attempt_results"][0]["confirmed_label"] == "false_positive_visible"
    assert result["attempt_results"][0]["stop_condition_triggered"] is True


def test_no_additive_entity_loss_attempts_are_not_observed() -> None:
    contract = build_marker_entity_followup_contract()
    replays = [
        build_static_step6_replay(
            contract=contract,
            case_id=case["attempt_id"],
            ledger_signal="all_private_or_confirming",
            answer_mode="anchor_preserved",
        )
        for case in contract["attempt_cases"]
    ]

    result = build_marker_entity_followup_result(
        contract=contract,
        step6_replays=replays,
        judgments=[],
    )

    validate_marker_entity_followup_result(result)

    assert result["followup_result"] == "not_observed"
    assert all(
        attempt["construction_label"] == "not_observed"
        for attempt in result["attempt_results"]
    )


def test_contract_fixture_validates() -> None:
    path = (
        REPO_ROOT
        / "research"
        / "pre-step6-marker-entity-loss-followup"
        / "marker-entity-loss-followup.v1.json"
    )
    payload = load_marker_entity_followup_contract(path)

    validate_marker_entity_followup_contract(payload)

    assert len(payload["attempt_cases"]) == 3
