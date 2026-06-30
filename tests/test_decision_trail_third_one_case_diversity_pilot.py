from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-trail-third-one-case-diversity-pilot-v0.md"
)
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-trail-third-one-case-diversity-pilot-v0/review.json"
)
EXPECTED_SCHEMA_VERSION = (
    "lolla.decision_trail_third_one_case_diversity_pilot.v0"
)
EXPECTED_CONTRACT_VERSION = "lolla.decision_trail_specialist_contracts.v0"
SPECIALIST_ROLES = {
    "conversation_shape_reader",
    "likely_action_reader",
    "friction_lost_value_reader",
    "conservative_fan_in_reader",
}
REQUIRED_PR99_FIELDS = {
    "assistant_influence_source_status",
    "vanilla_overlap_read",
    "lost_value_severity_read",
    "severity_source_status",
    "downgrade_triggers",
    "not_ready_reason",
    "source_scope_and_truncation_impact",
}
FORBIDDEN_MARKERS = (
    "/" + "Users/",
    "SEC" + "RET",
    "raw" + "_message_content",
    "fabricated" + "_passages",
    "FULL ASSISTANT " + "REASONING",
    "client" + "_secret",
    "api" + "_key",
    "pass" + "word",
)
FORBIDDEN_FIELD_NAMES = {
    "safe_for_agent_use",
    "quality" + "_score",
    "answer_quality" + "_score",
    "improvement" + "_score",
    "judge" + "_score",
    "winner",
    "approved",
    "certified",
    "pass_fail",
}


def _review() -> dict[str, Any]:
    return json.loads(REVIEW_PATH.read_text(encoding="utf-8"))


def _walk_keys(value: Any) -> list[str]:
    keys: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            keys.append(str(key))
            keys.extend(_walk_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.extend(_walk_keys(child))
    return keys


def _pilot_case() -> dict[str, Any]:
    cases = _review()["pilot_cases"]
    assert len(cases) == 1
    return cases[0]


def test_review_shape_and_boundary_metadata() -> None:
    review = _review()

    assert review["schema_version"] == EXPECTED_SCHEMA_VERSION
    assert review["review_mode"] == (
        "codex_assisted_pr102_third_one_case_diversity_pilot"
    )
    boundary = review["boundary"]
    assert boundary["human_validated"] is False
    assert boundary["ground_truth"] is False
    assert boundary["judge_calibration_eligible"] is False
    assert boundary["product_proof"] is False
    assert boundary["answer_quality_scored"] is False
    assert boundary["agent_action_authorized"] is False
    assert boundary["model_calls"] == 0
    assert boundary["archive_mutated"] is False
    assert boundary["runtime_invoked"] is False
    assert boundary["skill_invoked"] is False
    assert boundary["automatic_labels_created"] is False
    assert boundary["raw_private_content_included"] is False
    assert boundary["fan_in_executed_as_verdict"] is False


def test_case_selection_is_pre_registered_diverse_and_not_positive_seek() -> None:
    selection = _review()["case_selection"]

    assert selection["selected_before_local_private_content_read"] is True
    assert selection["pilot_case_ref"] == (
        "deploy-assisted-intake-routing/20260627T130339Z_4cd3cb"
    )
    assert selection["decision_family"] == "deployment_controls"
    assert selection["not_selected_to_find_positive_case"] is True
    assert any("cofounder" in item for item in selection["contrast_to_prior_pilots"])
    assert any("career" in item for item in selection["contrast_to_prior_pilots"])


def test_source_packet_summary_records_local_private_deletion_and_scope() -> None:
    summary = _review()["source_packet_summary"]

    assert summary["pilot_case_count"] == 1
    assert summary["metadata_packet_generated"] is True
    assert summary["metadata_packet_checked_in"] is False
    assert summary["metadata_packet_deleted_after_review"] is True
    assert summary["include_text_packet_generated"] is True
    assert summary["include_text_packet_checked_in"] is False
    assert summary["include_text_packet_deleted_after_review"] is True
    assert summary["private_content_in_checked_in_review"] is False
    assert summary["local_absolute_paths_in_checked_in_review"] is False
    assert summary["source_scope_summary"] == {
        "content_inclusion_mode": "include_text",
        "artifact_records_read": 16,
        "read_text_complete": 12,
        "read_text_truncated": 4,
        "main_conversation_revised_answer_and_memo_complete": True,
        "specialists_cited_scope_status": True,
    }
    assert summary["truncation_summary"]["artifact_records_truncated"] == 4
    assert summary["local_private_retention_policy_observed"][
        "include_text_output_retention_status"
    ] == "deleted_after_review"


def test_pilot_case_has_all_roles_and_pr99_fields() -> None:
    case = _pilot_case()

    assert case["case_ref"] == (
        "deploy-assisted-intake-routing/20260627T130339Z_4cd3cb"
    )
    assert case["input_packet_mode"] == "local_private_mode"
    assert case["content_policy_observed"] == "include_text_summary_only_checked_in"
    assert set(case["specialist_outputs"]) == SPECIALIST_ROLES
    assert case["source_packet_summary"]["local_packet_checked_in"] is False
    assert case["source_packet_summary"][
        "local_absolute_paths_in_checked_in_review"
    ] is False
    assert set(case["source_packet_summary"]["pr99_patch_fields_present"]) == (
        REQUIRED_PR99_FIELDS
    )


def test_each_specialist_output_has_contract_boundary_and_scope() -> None:
    outputs = _pilot_case()["specialist_outputs"]

    for role, output in outputs.items():
        assert output["specialist_role"] == role
        assert output["contract_version"] == EXPECTED_CONTRACT_VERSION
        assert output["input_mode"] == "local_private_mode"
        assert output["read_status"] == "provisional_candidate"
        assert output["source_refs"]
        assert output["source_status"]
        assert output["uncertainty"]
        assert output["evidence_strength"]
        assert isinstance(output["fields"], dict)
        assert output["limitations"]
        assert output["non_claims"]
        assert output["fields"]["source_scope_and_truncation_impact"]
        boundary = output["boundary_metadata"]
        assert boundary["human_validated"] is False
        assert boundary["ground_truth"] is False
        assert boundary["judge_calibration_eligible"] is False
        assert boundary["product_proof"] is False
        assert boundary["answer_quality_scored"] is False
        assert boundary["agent_action_authorized"] is False
        assert boundary["model_calls"] == 0
        assert boundary["archive_mutated"] is False
        assert boundary["runtime_invoked"] is False
        assert boundary["skill_invoked"] is False
        assert boundary["automatic_labels_created"] is False
        assert boundary["raw_private_content_included"] is False


def test_pr102_preserves_material_overlap_and_noise_reduction_signal() -> None:
    outputs = _pilot_case()["specialist_outputs"]

    likely_action = outputs["likely_action_reader"]["fields"]
    friction = outputs["friction_lost_value_reader"]["fields"]
    fan_in = outputs["conservative_fan_in_reader"]["fields"]

    assert likely_action["vanilla_overlap_read"] == "material_overlap_candidate"
    assert "mostly overlaps" in likely_action["action_delta"]
    assert friction["overcaution_or_diligence_theater"] == (
        "vanilla_gate_bloat_candidate_reduced_by_revision"
    )
    assert friction["lost_value_severity_read"] == "low_to_moderate_candidate"
    assert fan_in["net_read_candidate"] == "local_private_specialist_read_partly_useful"
    assert "noise-reduction" in fan_in["not_ready_reason"]
    assert "vanilla_overlap_read is material_overlap_candidate" in fan_in[
        "downgrade_triggers"
    ]


def test_next_recommendation_closes_pilot_phase_not_fourth_pilot() -> None:
    review = _review()
    recommendation = review["next_recommended_slice"]

    assert recommendation["recommended_slice"] == (
        "PR103 Decision Trail Specialist Pilot Phase Closure Gate v0"
    )
    assert "Compare PR97, PR100, and PR102" in recommendation["purpose"]
    assert "More one-case pilots" in recommendation["why_not_fourth_pilot"]
    must_not = set(recommendation["must_not_do"])
    assert "run_lolla" in must_not
    assert "invoke_lolla_skill" in must_not
    assert "mutate_archives" in must_not
    assert "score_answer_quality" in must_not
    assert "create_automatic_labels" in must_not
    assert "authorize_agent_action" in must_not
    assert "run_a_fourth_one_case_pilot_by_momentum" in must_not


def test_no_private_markers_local_paths_or_authority_fields() -> None:
    combined_text = "\n".join(
        [
            REVIEW_PATH.read_text(encoding="utf-8"),
            DOC_PATH.read_text(encoding="utf-8"),
        ]
    )

    for marker in FORBIDDEN_MARKERS:
        assert marker not in combined_text
    assert "/tmp/" not in combined_text
    assert not FORBIDDEN_FIELD_NAMES.intersection(_walk_keys(_review()))


def test_pr78_lint_accepts_pr102_review_artifacts() -> None:
    report = lint_product_delta_paths([DOC_PATH, REVIEW_PATH])

    assert report["summary"]["blocking_error_count"] == 0
    assert report["summary"]["warning_count"] == 0
    assert report["summary"]["info_count"] == 0
