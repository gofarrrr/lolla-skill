from __future__ import annotations

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_skill_shadow_comparison_contract import (  # noqa: E402
    build_skill_shadow_comparison_contract,
    render_skill_shadow_comparison_contract_markdown,
    validate_skill_shadow_comparison_contract,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_skill_shadow_contract_is_research_only_and_does_not_edit_skill() -> None:
    contract = build_skill_shadow_comparison_contract(root=REPO_ROOT)

    validate_skill_shadow_comparison_contract(contract, root=REPO_ROOT)

    assert contract["schema_version"] == "pre_step6_skill_shadow_comparison_contract.v1"
    assert contract["runtime_policy"] == "runtime_dormant"
    assert contract["promotion_effect"] == "none_research_only"
    assert contract["skill_update_allowed"] is False
    assert contract["runtime_visibility_change_allowed"] is False
    assert contract["manual_interpretation_required"] is True
    assert contract["principles"]["step7_not_obsolete_by_assertion"] is True
    assert contract["principles"]["automatic_graduation_allowed"] is False
    assert contract["principles"]["model_selector_allowed"] is False
    assert "default Step 7" in contract["product_intent"]["desired_direction"]
    assert contract["product_intent"]["non_claim"] == "Step 7 is not obsolete by assertion."


def test_skill_shadow_contract_compares_legacy_to_cleaner_table_with_step7_still_required() -> None:
    contract = build_skill_shadow_comparison_contract(root=REPO_ROOT)

    arms = {arm["arm_id"]: arm for arm in contract["comparison_arms"]}

    assert set(arms) == {
        "legacy_required_pressure_check",
        "cleaner_table_shadow_required_pressure_check",
    }
    assert "required" in arms["legacy_required_pressure_check"]["step7_policy"]
    assert "required" in arms["cleaner_table_shadow_required_pressure_check"]["step7_policy"]
    assert arms["cleaner_table_shadow_required_pressure_check"]["visible_behavior"] == "unchanged_shadow_only"


def test_skill_shadow_contract_pins_measurement_protocol_before_records() -> None:
    contract = build_skill_shadow_comparison_contract(root=REPO_ROOT)

    protocol = contract["measurement_protocol"]
    cleaner = protocol["cleaner_table_operational_definition"]
    labels = protocol["operator_labeling_protocol"]

    assert protocol["record_unit"] == "case_sample_pair"
    assert protocol["sample_count_per_case"] == 3
    assert protocol["target_record_count"] == 12
    assert cleaner["step6_receives_cleaner_private_table"] is True
    assert cleaner["step7_runs_in_both_arms"] is True
    assert "new model selector" in cleaner["excluded_material"]
    assert "automatic card graduation" in cleaner["excluded_material"]
    assert labels["primary_label_source"] == "human_operator_review"
    assert labels["llm_reviewers_authoritative"] is False


def test_skill_shadow_contract_case_set_covers_cleaning_and_guardrail_shapes() -> None:
    contract = build_skill_shadow_comparison_contract(root=REPO_ROOT)

    roles = {case["case_role"] for case in contract["case_set"]}
    case_ids = {case["case_id"] for case in contract["case_set"]}

    assert roles == {
        "consultant_graduation_candidate",
        "phd_distributed_atom",
        "founder_v60_destabilization",
        "negative_control",
    }
    assert "mid-level-consultant-report-2" in case_ids
    assert "third-year-phd-student.v2.v60-off" in case_ids
    assert "founder-grant-marcus-equity.high-clutter.v60-on" in case_ids
    assert "mother-address-year" in case_ids


def test_skill_shadow_contract_metrics_keep_step7_residual_work_visible() -> None:
    contract = build_skill_shadow_comparison_contract(root=REPO_ROOT)

    metrics = {metric["metric_id"]: metric for metric in contract["metrics"]}

    assert "step7_meaningful_divergence_rate" in metrics
    assert "question_1_shift_missed_rate" in metrics
    assert "question_2_material_noise_rate" in metrics
    assert "question_3_named_mechanism_missed_rate" in metrics
    assert metrics["anthropic_subagent_cost_delta"]["human_review_required"] is False
    assert metrics["operator_review_label"]["human_review_required"] is True


def test_skill_shadow_contract_outcomes_do_not_directly_authorize_skill_md_edits() -> None:
    contract = build_skill_shadow_comparison_contract(root=REPO_ROOT)

    outcomes = {outcome["label"]: outcome for outcome in contract["outcomes"]}

    assert set(outcomes) == {
        "supports_optional_pressure_check_trial",
        "preserve_required_pressure_check",
        "ambiguous_continue_research",
    }
    assert all(outcome["allows_skill_md_edit"] is False for outcome in outcomes.values())


def test_skill_shadow_contract_pins_decision_thresholds() -> None:
    contract = build_skill_shadow_comparison_contract(root=REPO_ROOT)

    thresholds = contract["decision_thresholds"]
    supports = thresholds["supports_optional_pressure_check_trial"]
    preserve = thresholds["preserve_required_pressure_check"]

    assert supports["minimum_records"] == 12
    assert supports["min_support_labels"] == 9
    assert supports["max_preserve_labels"] == 1
    assert supports["max_safety_blocked_records"] == 0
    assert preserve["any_safety_blocked_records"] is True
    assert preserve["min_preserve_labels"] == 4


def test_skill_shadow_contract_markdown_is_human_readable() -> None:
    contract = build_skill_shadow_comparison_contract(root=REPO_ROOT)

    markdown = render_skill_shadow_comparison_contract_markdown(contract)

    assert "Skill Shadow Comparison Contract" in markdown
    assert "Code records; humans decide." in markdown
    assert "SKILL.md unchanged" in markdown
    assert "Product Intent" in markdown
    assert "Measurement Protocol" in markdown
    assert "Decision Thresholds" in markdown
    assert "legacy_required_pressure_check" in markdown
    assert "cleaner_table_shadow_required_pressure_check" in markdown
