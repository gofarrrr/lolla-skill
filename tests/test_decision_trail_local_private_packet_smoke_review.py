from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-trail-local-private-packet-smoke-review-v0.md"
)
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-trail-local-private-packet-smoke-review-v0/review.json"
)
EXPECTED_SCHEMA_VERSION = (
    "lolla.decision_trail_local_private_packet_smoke_review.v0"
)
SPECIALIST_ROLES = {
    "conversation_shape_reader",
    "likely_action_reader",
    "friction_lost_value_reader",
    "conservative_fan_in_reader",
}
FORBIDDEN_MARKERS = (
    "/Users/",
    "SECRET",
    "raw_message_content",
    "fabricated_passages",
    "FULL ASSISTANT REASONING",
    "client_secret",
    "api_key",
    "password",
)
FORBIDDEN_AUTHORITY_FIELDS = (
    "safe_for_agent_use",
    "quality_score",
    "answer_quality_score",
    "improvement_score",
    "judge_score",
    "winner",
    "approved",
    "certified",
    "pass_fail",
)


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


def test_review_shape_and_boundary_metadata() -> None:
    review = _review()

    assert review["schema_version"] == EXPECTED_SCHEMA_VERSION
    assert review["review_mode"] == "local_private_packet_smoke_review"
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
    assert boundary["specialist_reads_filled"] is False
    assert boundary["fan_in_executed"] is False
    assert boundary["automatic_labels_created"] is False


def test_real_metadata_smoke_records_two_real_runs_without_private_text() -> None:
    review = _review()
    metadata_smoke = next(
        smoke
        for smoke in review["smoke_outputs"]
        if smoke["smoke_id"] == "real_metadata_only_two_runs"
    )

    assert metadata_smoke["content_inclusion_mode"] == "metadata_only"
    assert metadata_smoke["report_count"] == 2
    assert metadata_smoke["local_output_checked_in"] is False
    assert (
        metadata_smoke["packet_policy_read"]["local_packet_private_content_state"]
        == "not_included"
    )
    assert metadata_smoke["packet_policy_read"]["specialist_reads_filled"] is False
    assert metadata_smoke["packet_policy_read"]["fan_in_executed"] is False
    assert metadata_smoke["packet_policy_read"]["local_absolute_paths_included"] is False
    assert len(metadata_smoke["source_run_refs"]) == 2
    assert all(not ref.startswith("/") for ref in metadata_smoke["source_run_refs"])

    for artifact_count in metadata_smoke["artifact_counts"]:
        assert artifact_count["artifact_records_read"] == 16
        assert artifact_count["artifact_records_with_content_included"] == 0
        assert set(artifact_count["specialist_packet_roles"]) == SPECIALIST_ROLES


def test_include_text_smokes_are_local_only_and_not_product_evidence() -> None:
    review = _review()
    real_include = next(
        smoke
        for smoke in review["smoke_outputs"]
        if smoke["smoke_id"] == "real_include_text_one_run"
    )
    synthetic_include = next(
        smoke
        for smoke in review["smoke_outputs"]
        if smoke["smoke_id"] == "synthetic_include_text_guardrail"
    )

    assert real_include["content_inclusion_mode"] == "include_text"
    assert real_include["local_output_checked_in"] is False
    assert real_include["local_output_retained_after_review"] is False
    assert (
        real_include["packet_policy_read"]["local_packet_private_content_state"]
        == "included_in_deleted_local_output"
    )
    assert real_include["packet_policy_read"]["raw_transcripts_included"] is True
    assert real_include["packet_policy_read"]["raw_revised_answers_included"] is True
    assert real_include["packet_policy_read"]["raw_memos_included"] is True
    assert real_include["packet_policy_read"]["specialist_reads_filled"] is False
    assert real_include["packet_policy_read"]["fan_in_executed"] is False
    assert real_include["artifact_counts"][0]["artifact_records_with_content_included"] == 16

    assert synthetic_include["content_inclusion_mode"] == "include_text"
    assert synthetic_include["local_output_checked_in"] is False
    assert (
        synthetic_include["packet_policy_read"]["local_packet_private_content_state"]
        == "included_in_synthetic_local_output"
    )


def test_next_recommendation_is_tiny_pilot_not_broad_batch() -> None:
    review = _review()
    recommendation = review["next_recommended_slice"]

    assert (
        recommendation["recommended_slice"]
        == "PR97 Decision Trail Local-Private Specialist Output Pilot v0"
    )
    assert "tiny set" in recommendation["purpose"]
    assert "broad specialist review" in recommendation["why_not_broad_batch"]
    must_not = set(recommendation["must_not_do"])
    assert "run_lolla" in must_not
    assert "invoke_lolla_skill" in must_not
    assert "mutate_archives" in must_not
    assert "score_answer_quality" in must_not
    assert "create_automatic_labels" in must_not
    assert "authorize_agent_action" in must_not


def test_review_has_non_claims_and_no_authority_fields_or_private_markers() -> None:
    review_text = REVIEW_PATH.read_text(encoding="utf-8")
    doc_text = DOC_PATH.read_text(encoding="utf-8")
    combined_text = review_text + "\n" + doc_text

    for marker in FORBIDDEN_MARKERS:
        assert marker not in combined_text
    for field in FORBIDDEN_AUTHORITY_FIELDS:
        assert field not in _walk_keys(_review())
    assert "not product proof" in review_text
    assert "not answer-quality scoring" in review_text
    assert "not evidence that clean packets mean good advice" in review_text


def test_pr78_lint_accepts_pr96_review_artifacts() -> None:
    report = lint_product_delta_paths([DOC_PATH, REVIEW_PATH])

    assert report["summary"]["blocking_error_count"] == 0
    assert report["summary"]["warning_count"] == 0
    assert report["summary"]["info_count"] == 0
