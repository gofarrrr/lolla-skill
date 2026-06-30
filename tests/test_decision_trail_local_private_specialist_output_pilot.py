from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-trail-local-private-specialist-output-pilot-v0.md"
)
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-trail-local-private-specialist-output-pilot-v0/review.json"
)
EXPECTED_SCHEMA_VERSION = (
    "lolla.decision_trail_local_private_specialist_output_pilot.v0"
)
EXPECTED_CONTRACT_VERSION = "lolla.decision_trail_specialist_contracts.v0"
SPECIALIST_ROLES = {
    "conversation_shape_reader",
    "likely_action_reader",
    "friction_lost_value_reader",
    "conservative_fan_in_reader",
}
ALLOWED_NET_READS = {
    "local_private_specialist_read_useful_but_unvalidated",
    "local_private_specialist_read_partly_useful",
    "local_private_packet_too_thin",
    "local_private_packet_too_bulky",
    "local_private_packet_too_risky",
    "inconclusive",
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
    "quality_score",
    "answer_quality_score",
    "improvement_score",
    "judge_score",
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
        "codex_assisted_local_private_specialist_output_pilot"
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


def test_source_packet_summary_is_sanitized_and_local_only() -> None:
    summary = _review()["source_packet_summary"]

    assert summary["pilot_case_count"] == 1
    assert summary["metadata_packet_generated"] is True
    assert summary["metadata_packet_checked_in"] is False
    assert summary["include_text_packet_generated"] is True
    assert summary["include_text_packet_checked_in"] is False
    assert summary["include_text_packet_deleted_after_review"] is True
    assert summary["private_content_in_checked_in_review"] is False
    assert summary["metadata_packet_ref"].startswith(
        "local_temp_output_not_checked_in:"
    )
    assert summary["include_text_packet_ref"].startswith(
        "local_temp_output_not_checked_in:"
    )
    assert not summary["metadata_packet_ref"].startswith("/")
    assert not summary["include_text_packet_ref"].startswith("/")


def test_pilot_case_has_all_four_specialist_outputs() -> None:
    case = _pilot_case()

    assert case["case_ref"] == "ceo-remove-founding-cofounder/20260627T093131Z_59d153"
    assert case["input_packet_mode"] == "local_private_mode"
    assert case["content_policy_observed"] == "include_text_summary_only_checked_in"
    assert set(case["specialist_outputs"]) == SPECIALIST_ROLES
    assert (
        case["source_packet_summary"]["local_packet_private_content_state"]
        == "included_in_local_temp_output_only"
    )
    assert case["source_packet_summary"]["local_packet_checked_in"] is False
    assert case["source_packet_summary"]["local_absolute_paths_in_checked_in_review"] is False
    assert case["source_packet_summary"]["artifact_records_included_in_local_packet"] == 16


def test_each_specialist_output_has_required_contract_surface() -> None:
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


def test_conservative_fan_in_preserves_disagreement_without_scoring() -> None:
    fan_in = _pilot_case()["specialist_outputs"]["conservative_fan_in_reader"]
    fields = fan_in["fields"]

    assert fields["net_read_candidate"] in ALLOWED_NET_READS
    assert fields["net_read_candidate"] == (
        "local_private_specialist_read_useful_but_unvalidated"
    )
    assert fields["disagreements_preserved"]
    assert fields["high_uncertainty_fields"]
    assert fields["fields_not_ready_for_report"]
    assert fields["human_followup_questions"]
    assert "vote" not in json.dumps(fields).lower()
    assert "score" not in json.dumps(fields).lower()


def test_no_raw_private_markers_local_paths_or_forbidden_authority_fields() -> None:
    review_text = REVIEW_PATH.read_text(encoding="utf-8")
    doc_text = DOC_PATH.read_text(encoding="utf-8")
    combined_text = review_text + "\n" + doc_text

    for marker in FORBIDDEN_MARKERS:
        assert marker not in combined_text
    assert "/tmp/" not in combined_text
    assert not FORBIDDEN_FIELD_NAMES.intersection(_walk_keys(_review()))


def test_next_recommendation_is_contract_review_not_broad_batch() -> None:
    recommendation = _review()["next_recommended_slice"]

    assert recommendation["recommended_slice"] == (
        "PR98 Decision Trail Specialist Output Pilot Review / Contract Revision v0"
    )
    assert "one-case" in recommendation["purpose"]
    assert "broad batch" in recommendation["why_not_broad_batch"]
    must_not = set(recommendation["must_not_do"])
    assert "run_lolla" in must_not
    assert "invoke_lolla_skill" in must_not
    assert "mutate_archives" in must_not
    assert "score_answer_quality" in must_not
    assert "create_automatic_labels" in must_not
    assert "authorize_agent_action" in must_not


def test_pr78_lint_accepts_pr97_review_artifacts() -> None:
    report = lint_product_delta_paths([DOC_PATH, REVIEW_PATH])

    assert report["summary"]["blocking_error_count"] == 0
    assert report["summary"]["warning_count"] == 0
    assert report["summary"]["info_count"] == 0
