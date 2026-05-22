from __future__ import annotations

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_false_positive_visibility_probe import (  # noqa: E402
    build_false_positive_probe_contract,
    build_false_positive_probe_result,
    build_step6_replay_prompts,
    build_static_step6_replay,
    build_static_visibility_judgment,
    load_false_positive_probe_contract,
    validate_false_positive_probe_contract,
    validate_false_positive_probe_result,
    validate_step6_replay,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_contract_pins_split_outcome_failure_order_and_null_evidence_rule() -> None:
    contract = build_false_positive_probe_contract()

    validate_false_positive_probe_contract(contract)

    assert contract["schema_version"] == "pre_step6_false_positive_visibility_probe.v1"
    assert contract["probe_id"] == "false_positive_visibility_probe_v0"
    assert contract["status"] == "planned_non_promotional"
    assert contract["confirmation_rule"] == {
        "confirmed_false_positive_visible": (
            "Two reviewer judgments label the same additive-ledger case "
            "false_positive_visible under the same rubric, fresh blind shuffles, "
            "and different model families."
        ),
        "split_reviewer_outcome": "ambiguous_visibility",
        "single_reviewer_false_positive": "not_confirmed",
        "human_spot_check_only": "not_confirmed",
    }
    assert contract["failure_response_order"] == [
        "tighten_answer_delta_visible_effect_check",
        "add_entity_level_payload_gate",
        "split_additive_private_pressure_from_additive_public_payload",
    ]
    assert contract["case_construction_rule"] == {
        "max_attempts_per_shape": 3,
        "unconstructed_shape_result": "not_observed",
        "null_evidence_warning": (
            "Failure to construct a natural marker-preserved/entity-lost exemplar "
            "is not evidence that the omission gate is strong enough."
        ),
    }
    assert [case["shape_id"] for case in contract["probe_cases"]] == [
        "bevelin_structurally_applicable_but_irrelevant",
        "polya_true_but_useless_abstraction",
        "marker_preserved_entity_lost",
    ]
    for case in contract["probe_cases"]:
        assert case["selection_timing"] == "pre_run"
        assert case["pre_run_failure_hypothesis"].startswith("If Step 6 marks")
        assert case["expected_step6_signal"] == "additive_pressure_present"


def test_step6_prompt_and_static_replay_use_structured_answer_delta() -> None:
    contract = build_false_positive_probe_contract()
    prompts = build_step6_replay_prompts(
        contract=contract,
        case_id="fp-polya-true-but-useless",
    )
    step6_replay = build_static_step6_replay(
        contract=contract,
        case_id="fp-polya-true-but-useless",
        ledger_signal="additive_pressure_present",
    )

    validate_step6_replay(step6_replay)

    assert "added_entities" in prompts["user_prompt"]
    assert "removed_entities" in prompts["user_prompt"]
    assert "reordered_sequences" in prompts["user_prompt"]
    assert "structural_delta" in prompts["user_prompt"]
    assert "reframed_emphasis" in prompts["user_prompt"]

    deck_item = step6_replay["step6_output"]["private_visibility_ledger"][1]
    assert deck_item["answer_delta"] == {
        "added_entities": ["deck-pressure candidate"],
        "removed_entities": [],
        "reordered_sequences": [],
        "structural_delta": [],
        "reframed_emphasis": ["deck-pressure framing"],
    }


def test_confirmed_false_positive_requires_two_reviewer_families_and_triggers_review() -> None:
    contract = build_false_positive_probe_contract()
    case_id = "fp-marker-preserved-entity-lost"
    step6_replay = build_static_step6_replay(
        contract=contract,
        case_id=case_id,
        ledger_signal="additive_pressure_present",
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

    result = build_false_positive_probe_result(
        contract=contract,
        step6_replays=[step6_replay],
        judgments=[reviewer_a, reviewer_b],
    )

    validate_false_positive_probe_result(result)

    assert result["case_results"] == [
        {
            "case_id": case_id,
            "step6_ledger_signal": "additive_pressure_present",
            "answer_delta_specificity": "concrete_delta_present",
            "reviewer_count": 2,
            "reviewer_model_families": ["google", "openai"],
            "visibility_labels": ["false_positive_visible", "false_positive_visible"],
            "reviewer_winner_arms": ["anchor_visible", "anchor_visible"],
            "reviewer_non_inferiority_reads": ["worse", "worse"],
            "reviewer_label_consistency": "aligned",
            "confirmed_label": "false_positive_visible",
            "stop_condition_triggered": True,
        }
    ]
    assert result["probe_result"] == "design_review_required"


def test_split_reviewers_are_ambiguous_visibility_without_stop_trigger() -> None:
    contract = build_false_positive_probe_contract()
    case_id = "fp-polya-true-but-useless"
    step6_replay = build_static_step6_replay(
        contract=contract,
        case_id=case_id,
        ledger_signal="additive_pressure_present",
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
        visibility_label="true_visible",
        winner_arm="deck_visible",
    )

    result = build_false_positive_probe_result(
        contract=contract,
        step6_replays=[step6_replay],
        judgments=[reviewer_a, reviewer_b],
    )

    validate_false_positive_probe_result(result)

    assert result["case_results"][0]["confirmed_label"] == "ambiguous_visibility"
    assert result["case_results"][0]["stop_condition_triggered"] is False
    assert result["probe_result"] == "continue_probe_with_ambiguity"


def test_true_visible_label_with_anchor_winner_tension_is_ambiguous() -> None:
    contract = build_false_positive_probe_contract()
    case_id = "fp-polya-true-but-useless"
    step6_replay = build_static_step6_replay(
        contract=contract,
        case_id=case_id,
        ledger_signal="additive_pressure_present",
    )
    reviewer_a = build_static_visibility_judgment(
        contract=contract,
        step6_replay=step6_replay,
        model="openai/gpt-5.1-chat",
        visibility_label="true_visible",
        winner_arm="anchor_visible",
    )
    reviewer_b = build_static_visibility_judgment(
        contract=contract,
        step6_replay=step6_replay,
        model="google/gemini-3.1-flash-lite",
        visibility_label="true_visible",
        winner_arm="anchor_visible",
    )

    result = build_false_positive_probe_result(
        contract=contract,
        step6_replays=[step6_replay],
        judgments=[reviewer_a, reviewer_b],
    )

    validate_false_positive_probe_result(result)

    assert result["case_results"][0]["reviewer_winner_arms"] == [
        "anchor_visible",
        "anchor_visible",
    ]
    assert result["case_results"][0]["reviewer_label_consistency"] == "tension_detected"
    assert result["case_results"][0]["confirmed_label"] == "ambiguous_visibility"
    assert result["probe_result"] == "continue_probe_with_ambiguity"


def test_step6_standdown_is_clean_pass_without_reviewer_judgments() -> None:
    contract = build_false_positive_probe_contract()
    step6_replay = build_static_step6_replay(
        contract=contract,
        case_id="fp-bevelin-irrelevant-incentives",
        ledger_signal="all_private_or_confirming",
    )

    result = build_false_positive_probe_result(
        contract=contract,
        step6_replays=[step6_replay],
        judgments=[],
    )

    validate_false_positive_probe_result(result)

    assert result["case_results"][0]["confirmed_label"] == "step6_stood_down"
    assert result["case_results"][0]["stop_condition_triggered"] is False
    assert result["probe_result"] == "continue_probe"


def test_marker_entity_loss_shape_standdown_is_not_observed_not_gate_pass() -> None:
    contract = build_false_positive_probe_contract()
    step6_replay = build_static_step6_replay(
        contract=contract,
        case_id="fp-marker-preserved-entity-lost",
        ledger_signal="all_private_or_confirming",
    )

    result = build_false_positive_probe_result(
        contract=contract,
        step6_replays=[step6_replay],
        judgments=[],
    )

    validate_false_positive_probe_result(result)

    assert result["case_results"][0]["confirmed_label"] == "not_observed"
    assert result["case_results"][0]["stop_condition_triggered"] is False
    assert result["probe_result"] == "continue_probe_with_not_observed"


def test_contract_fixture_validates() -> None:
    path = (
        REPO_ROOT
        / "research"
        / "pre-step6-false-positive-visibility-probe"
        / "false-positive-visibility-probe.v1.json"
    )
    payload = load_false_positive_probe_contract(path)

    validate_false_positive_probe_contract(payload)

    assert len(payload["probe_cases"]) == 3
