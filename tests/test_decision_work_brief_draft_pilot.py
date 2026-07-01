from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = (
    REPO_ROOT
    / "reviews"
    / "codex-assisted"
    / "decision-work-brief-draft-pilot-v0"
    / "review.json"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-draft-pilot-v0.md"
)
BRIEF_SCHEMA_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-schema-v0.md"
)
BRIEF_SCHEMA_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-v0.json"
)
PACKET_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-packet-builder-v0.md"
)
PRD_PATH = (
    REPO_ROOT / "docs/conversation-understanding/decision-work-brief-prd-v0.md"
)

PILOT_SCHEMA_VERSION = "lolla.decision_work_brief_draft_pilot.v0"
BRIEF_SCHEMA_VERSION = "lolla.decision_work_brief.v0"
PACKET_SCHEMA_VERSION = "lolla.decision_work_brief_packets.v0"
REQUIRED_TOP_LEVEL_FIELDS = {
    "schema_version",
    "pilot_metadata",
    "input_scope",
    "source_packets",
    "custody_flags",
    "draft_briefs",
    "aggregate_observations",
    "non_claims",
    "next_recommendation",
}
REQUIRED_BRIEF_TOP_LEVEL_FIELDS = {
    "schema_version",
    "brief_metadata",
    "mode",
    "source_refs",
    "custody_flags",
    "sections",
    "non_claims",
}
BRIEF_SECTIONS = {
    "decision",
    "starting_direction",
    "what_lolla_pressed_on",
    "what_changed",
    "what_this_means_for_action",
    "what_still_might_be_wrong",
    "what_was_not_proven",
    "evidence_receipt",
}
SECTION_REQUIRED_FIELDS = {
    "status",
    "source_status",
    "source_refs",
    "interpreted_by",
    "human_validated",
    "uncertainty",
    "value",
    "empty_meaning",
}
REQUIRED_CUSTODY_FALSE_FIELDS = {
    "human_validated",
    "product_proof",
    "answer_quality_scored",
    "agent_action_authorized",
    "runtime_invoked",
    "skill_invoked",
    "archive_mutated",
    "broad_judge_used",
    "automatic_labels_created",
    "raw_private_content_included",
    "provider_text_included",
}
REQUIRED_BRIEF_CUSTODY_FALSE_FIELDS = {
    "human_validated",
    "product_proof",
    "answer_quality_scored",
    "agent_action_authorized",
    "runtime_invoked",
    "skill_invoked",
    "archive_mutated",
    "raw_private_content_included",
    "provider_text_included",
    "raw_transcript_included",
    "raw_revised_answer_included",
    "raw_memo_included",
    "private_reasoning_included",
    "local_absolute_paths_included",
    "secrets_included",
    "llm_judge_used",
    "automatic_labels_created",
}
REQUIRED_PILOT_NON_CLAIMS = {
    "draft_is_provisional",
    "not_human_validated",
    "not_product_proof",
    "not_answer_quality_score",
    "not_agent_action_authorization",
    "not_correctness_proof",
    "clean_artifacts_do_not_imply_good_advice",
    "codex_assisted_interpretation_is_uncalibrated",
    "future_human_review_required",
}
REQUIRED_BRIEF_NON_CLAIMS = {
    "not_correctness_proof",
    "not_answer_quality_score",
    "not_agent_action_authorization",
    "not_human_validated_unless_marked",
    "clean_artifacts_do_not_imply_good_advice",
    "process_evidence_is_not_decision_certification",
    "llm_interpretation_is_provisional_unless_human_reviewed",
}
FORBIDDEN_FIELD_NAMES = {
    "safe_for_" + "agent_use",
    "approved",
    "certified",
    "pass_fail",
    "winner",
    "quality_score",
    "improvement_score",
    "judge_score",
    "answer_quality_score",
    "product_score",
    "correctness_score",
    "rating",
}
PRIVACY_MARKERS = (
    "/" + "Users" + "/",
    "SEC" + "RET",
    "raw_message" + "_content",
    "fabricated" + "_passages",
    "FULL ASSISTANT" + " REASONING",
    "client" + "_secret",
    "api" + "_key",
    "pass" + "word",
)
LOCAL_ABSOLUTE_PATH_MARKERS = (
    "/" + "Users" + "/",
    "/tmp/",
)
PRODUCTION_DRAFT_GENERATOR_FILES = (
    REPO_ROOT / "engine/system_b/decision_work_brief_draft_pilot.py",
    REPO_ROOT / "scripts/evals/draft_decision_work_brief.py",
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


def _embedded_briefs(review: dict[str, Any]) -> list[dict[str, Any]]:
    briefs: list[dict[str, Any]] = []
    for draft in review["draft_briefs"]:
        if "brief" in draft:
            briefs.append(draft["brief"])
        else:
            assert draft.get("brief_ref")
    return briefs


def test_review_json_has_pr116_schema_and_required_top_level_fields() -> None:
    review = _review()

    assert review["schema_version"] == PILOT_SCHEMA_VERSION
    assert REQUIRED_TOP_LEVEL_FIELDS <= set(review)
    assert review["pilot_metadata"]["review_mode"] == (
        "codex_assisted_provisional_checked_in_safe"
    )
    assert review["pilot_metadata"]["case_count"] == 1


def test_source_packet_scope_uses_pr115_metadata_only_packet_without_private_text() -> None:
    review = _review()
    packets = review["source_packets"]

    assert len(packets) == 1
    packet = packets[0]
    assert packet["packet_schema_version"] == PACKET_SCHEMA_VERSION
    assert packet["packet_mode"] == "metadata_only"
    assert packet["generated_locally_for_pr116"] is True
    assert packet["checked_in"] is False
    assert packet["local_private_text_used"] is False
    assert packet["raw_private_content_included"] is False
    assert packet["provider_text_included"] is False
    assert set(packet["target_sections"]) == BRIEF_SECTIONS
    assert "product_delta_report" in packet["not_supplied_refs"]


def test_pilot_custody_flags_are_conservative() -> None:
    custody = _review()["custody_flags"]

    for field in REQUIRED_CUSTODY_FALSE_FIELDS:
        assert custody[field] is False
    assert custody["model_calls"] == 0
    assert custody["checked_in_safe"] is True
    assert custody["local_absolute_paths_included"] is False
    assert custody["local_private_packet_checked_in"] is False
    assert custody["codex_assisted"] is True


def test_draft_wrappers_include_conservative_custody() -> None:
    for draft in _review()["draft_briefs"]:
        custody = draft["custody_flags"]
        for field in REQUIRED_CUSTODY_FALSE_FIELDS:
            assert custody[field] is False
        assert custody["model_calls"] == 0
        assert custody["checked_in_safe"] is True
        assert custody["local_absolute_paths_included"] is False


def test_all_draft_briefs_embed_or_reference_pr114_brief_contract() -> None:
    review = _review()
    briefs = _embedded_briefs(review)

    assert briefs
    for brief in briefs:
        assert brief["schema_version"] == BRIEF_SCHEMA_VERSION
        assert REQUIRED_BRIEF_TOP_LEVEL_FIELDS <= set(brief)
        assert brief["mode"] == "checked_in_safe_mode"


def test_embedded_briefs_have_required_sections_and_shared_section_shape() -> None:
    for brief in _embedded_briefs(_review()):
        assert set(brief["sections"]) == BRIEF_SECTIONS
        for section_id, section in brief["sections"].items():
            assert SECTION_REQUIRED_FIELDS <= set(section)
            assert section["human_validated"] is False
            assert isinstance(section["source_refs"], list)
            assert section["empty_meaning"]
            if section["status"] == "populated_from_llm_interpretation":
                assert section["interpreted_by"] == "llm_interpretation"
            for source_ref in section["source_refs"]:
                assert source_ref["content_included"] is False
                assert source_ref["raw_private_content_included"] is False
                assert source_ref["provider_text_included"] is False


def test_embedded_brief_custody_flags_are_conservative() -> None:
    for brief in _embedded_briefs(_review()):
        custody = brief["custody_flags"]
        for field in REQUIRED_BRIEF_CUSTODY_FALSE_FIELDS:
            assert custody[field] is False
        assert custody["model_calls"] == 0
        assert custody["human_validation_status"] == "not_human_validated"
        assert custody["human_review_refs"] == []


def test_non_claims_are_explicit_at_pilot_and_brief_levels() -> None:
    review = _review()

    assert REQUIRED_PILOT_NON_CLAIMS <= set(review["non_claims"])
    for brief in _embedded_briefs(review):
        assert REQUIRED_BRIEF_NON_CLAIMS <= set(brief["non_claims"]["items"])


def test_pilot_records_uncertainty_followup_and_action_consequence() -> None:
    review = _review()

    assert any(draft["human_followup_questions"] for draft in review["draft_briefs"])
    assert any(draft["action_consequence_read"] for draft in review["draft_briefs"])
    assert any(
        draft["missingness_or_uncertainty_read"] for draft in review["draft_briefs"]
    )
    assert any(
        draft["lost_value_or_overcorrection_note"] for draft in review["draft_briefs"]
    )

    sections = _embedded_briefs(review)[0]["sections"]
    assert sections["starting_direction"]["uncertainty"] == "high"
    assert sections["what_still_might_be_wrong"]["uncertainty"] == "high"
    assert sections["what_still_might_be_wrong"]["value"]["missingness_and_uncertainty"]
    assert sections["what_this_means_for_action"]["value"]["action_consequence"]


def test_checked_in_artifacts_have_no_local_absolute_paths_or_privacy_markers() -> None:
    text = "\n".join(
        [
            REVIEW_PATH.read_text(encoding="utf-8"),
            DOC_PATH.read_text(encoding="utf-8"),
            Path(__file__).read_text(encoding="utf-8"),
        ]
    )
    artifact_text = "\n".join(
        [
            REVIEW_PATH.read_text(encoding="utf-8"),
            DOC_PATH.read_text(encoding="utf-8"),
        ]
    )

    for marker in PRIVACY_MARKERS:
        assert marker not in text
    for marker in LOCAL_ABSOLUTE_PATH_MARKERS:
        assert marker not in artifact_text


def test_forbidden_authority_and_score_fields_do_not_appear() -> None:
    review = _review()

    assert not (FORBIDDEN_FIELD_NAMES & set(_walk_keys(review)))


def test_pr116_artifacts_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths([DOC_PATH, REVIEW_PATH])

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }


def test_prd_and_related_docs_reference_pr116_without_runtime_claims() -> None:
    combined = "\n".join(
        [
            PRD_PATH.read_text(encoding="utf-8"),
            PACKET_DOC_PATH.read_text(encoding="utf-8"),
            BRIEF_SCHEMA_DOC_PATH.read_text(encoding="utf-8"),
            BRIEF_SCHEMA_PATH.read_text(encoding="utf-8"),
            DOC_PATH.read_text(encoding="utf-8"),
        ]
    )

    assert "PR116" in combined
    assert "lolla.decision_work_brief_draft_pilot.v0" in combined
    lowered = combined.lower()
    assert "no generator" in lowered
    assert "no runtime integration" in lowered


def test_draft_pilot_does_not_add_production_brief_generator() -> None:
    for path in PRODUCTION_DRAFT_GENERATOR_FILES:
        assert not path.exists()
