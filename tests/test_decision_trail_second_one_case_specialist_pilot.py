from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-trail-second-one-case-specialist-pilot-v0.md"
)
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-trail-second-one-case-specialist-pilot-v0/review.json"
)
EXPECTED_SCHEMA_VERSION = (
    "lolla.decision_trail_second_one_case_specialist_pilot.v0"
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
        "codex_assisted_pr100_second_one_case_specialist_pilot"
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


def test_source_packet_summary_records_local_private_deletion_and_scope() -> None:
    summary = _review()["source_packet_summary"]

    assert summary["pilot_case_count"] == 1
    assert summary["pilot_case_ref"] == (
        "accept-founding-engineer-role/20260627T073034Z_a7c221"
    )
    assert summary["prior_pilot_case_ref"] == (
        "ceo-remove-founding-cofounder/20260627T093131Z_59d153"
    )
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
        "specialists_cited_scope_status": True,
    }
    assert summary["truncation_summary"]["artifact_records_truncated"] == 4
    assert summary["local_private_retention_policy_observed"][
        "include_text_output_retention_status"
    ] == "deleted_after_review"


def test_pilot_case_is_second_case_and_has_all_roles() -> None:
    case = _pilot_case()

    assert case["case_ref"] == (
        "accept-founding-engineer-role/20260627T073034Z_a7c221"
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


def test_each_specialist_output_has_pr99_contract_surface() -> None:
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


def test_pr99_patch_fields_force_partial_usefulness_not_broad_positive() -> None:
    outputs = _pilot_case()["specialist_outputs"]

    conversation = outputs["conversation_shape_reader"]["fields"]
    likely_action = outputs["likely_action_reader"]["fields"]
    friction = outputs["friction_lost_value_reader"]["fields"]
    fan_in = outputs["conservative_fan_in_reader"]["fields"]

    assert conversation["assistant_influence_source_status"] == (
        "visible_in_local_private_packet"
    )
    assert likely_action["vanilla_overlap_read"] == "material_overlap_candidate"
    assert friction["lost_value_severity_read"] == "moderate_candidate"
    assert friction["severity_source_status"] == (
        "source_limited_no_human_or_spouse_calibration"
    )
    assert "vanilla_overlap_read is material_overlap_candidate" in fan_in[
        "downgrade_triggers"
    ]
    assert fan_in["not_ready_reason"]
    assert fan_in["net_read_candidate"] == "local_private_specialist_read_partly_useful"


def test_comparison_recommends_decision_gate_not_broad_batch() -> None:
    review = _review()

    comparison = review["comparison_to_pr97"]
    assert "PR100 exercised all PR99 fields directly." in comparison[
        "useful_progress"
    ]
    assert comparison["directional_read"].endswith(
        "before any broader specialist-output batch."
    )
    next_slice = review["next_recommended_slice"]
    assert next_slice["recommended_slice"] == (
        "PR101 Decision Trail Specialist Pilot Comparison Gate v0"
    )
    assert "why_not_broad_batch" in next_slice
    must_not = set(next_slice["must_not_do"])
    assert "run_lolla" in must_not
    assert "invoke_lolla_skill" in must_not
    assert "mutate_archives" in must_not
    assert "score_answer_quality" in must_not
    assert "create_automatic_labels" in must_not
    assert "authorize_agent_action" in must_not


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


def test_pr78_lint_accepts_pr100_review_artifacts() -> None:
    report = lint_product_delta_paths([DOC_PATH, REVIEW_PATH])

    assert report["summary"]["blocking_error_count"] == 0
    assert report["summary"]["warning_count"] == 0
    assert report["summary"]["info_count"] == 0
