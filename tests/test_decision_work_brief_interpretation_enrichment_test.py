from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-interpretation-enrichment-test-v0/review.json"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-interpretation-enrichment-test-v0.md"
)
ENRICHED_BRIEF_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-enriched-launch-public-enterprise-beta-v0.md"
)
ORIGINAL_BRIEF_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-rendered-launch-public-enterprise-beta-v0.md"
)
PR131_READ_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-conversation-interpretation-tiny-offline-read-v0/read.json"
)
PR134_REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-conversation-interpretation-read-comparison-v0/review.json"
)
PRD_PATH = REPO_ROOT / "docs/conversation-understanding/decision-work-brief-prd-v0.md"

SCHEMA_VERSION = "lolla.decision_work_brief_interpretation_enrichment_test.v0"
ALLOWED_FIELDS_USED = {
    "decision_question",
    "likely_starting_direction",
    "revised_direction_or_action_consequence",
    "decision_thresholds",
    "evidence_gates",
    "useful_friction",
    "what_the_final_answer_does_not_prove",
}
REQUIRED_EXCLUDED = {
    "live_options",
    "abandoned_or_rejected_options",
    "noisy_friction",
    "lost_value",
}
ALLOWED_GATES = {
    "proceed_to_original_vs_enriched_review",
    "patch_enrichment_rules",
    "run_second_enriched_brief_test",
    "pause_until_human_review",
    "stop_and_simplify",
}
REQUIRED_CUSTODY_FALSE_FIELDS = {
    "human_validated",
    "product_proof",
    "archive_mutated",
    "runtime_invoked",
    "skill_invoked",
    "answer_quality_scored",
    "agent_action_authorized",
    "raw_private_content_checked_in",
    "provider_text_checked_in",
    "local_absolute_paths_checked_in",
    "broad_judge_used",
    "automatic_labels_created",
    "runtime_extraction_implemented",
    "new_interpretation_read_created",
    "original_brief_modified",
}
REQUIRED_NON_CLAIMS = {
    "enrichment_is_codex_assisted",
    "enrichment_is_provisional",
    "not_human_validated",
    "not_product_proof",
    "not_answer_quality_score",
    "not_agent_action_authorization",
    "not_correctness_proof",
    "not_runtime_integration",
    "not_new_interpretation_read",
    "not_original_brief_replacement",
    "clean_artifacts_do_not_imply_good_advice",
    "enriched_brief_is_not_better_as_fact",
    "future_human_review_required",
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


def _review() -> dict[str, Any]:
    return json.loads(REVIEW_PATH.read_text(encoding="utf-8"))


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _repo_ref_exists(ref: str) -> bool:
    if not ref.endswith((".md", ".json")):
        return True
    return (REPO_ROOT / ref).exists()


def test_enriched_brief_exists_and_original_brief_is_not_enriched() -> None:
    assert ENRICHED_BRIEF_PATH.exists()
    assert ORIGINAL_BRIEF_PATH.exists()

    enriched = _text(ENRICHED_BRIEF_PATH)
    original = _text(ORIGINAL_BRIEF_PATH)

    assert "## What the interpretation adds" in enriched
    assert "## What the interpretation adds" not in original
    assert "Enrichment status: provisional offline test" in enriched


def test_enriched_brief_preserves_non_claims_and_limits() -> None:
    enriched = _text(ENRICHED_BRIEF_PATH)

    assert "## What this does not prove" in enriched
    assert "## Evidence and limits" in enriched
    assert "Human validation: no" in enriched
    assert "Product proof: no" in enriched
    assert "Answer-quality scoring: no" in enriched
    assert "Agent action authorization: no" in enriched
    assert "Runtime invoked: no" in enriched
    assert "Skill invoked: no" in enriched
    assert "Model calls: 0" in enriched
    assert "Private/raw content included: no" in enriched
    assert "Provider text included: no" in enriched
    assert "does not prove that Lolla improved the decision" in enriched


def test_enriched_brief_uses_plain_language_without_private_markers() -> None:
    enriched = _text(ENRICHED_BRIEF_PATH)
    main_body = enriched.split("## Evidence and limits", 1)[0].lower()

    for forbidden in (
        "source_status:",
        "human_validated:",
        "product_proof:",
        "agent_action_authorized:",
        "schema_version",
        "packet",
        "artifact family",
        "custody machinery",
    ):
        assert forbidden not in main_body

    for marker in PRIVACY_MARKERS:
        assert marker not in enriched


def test_review_json_schema_and_custody_are_conservative() -> None:
    review = _review()

    assert review["schema_version"] == SCHEMA_VERSION
    assert {
        "schema_version",
        "review_metadata",
        "custody_flags",
        "source_brief",
        "source_interpretation_read",
        "enrichment_scope",
        "enriched_brief_ref",
        "fields_used",
        "fields_excluded",
        "expected_reader_value",
        "risks",
        "decision_gate",
        "next_recommendation",
        "non_claims",
    } <= set(review)

    custody = review["custody_flags"]
    for field in REQUIRED_CUSTODY_FALSE_FIELDS:
        assert custody[field] is False
    assert custody["model_calls"] == 0
    assert custody["enrichment_is_provisional"] is True


def test_sources_and_enriched_brief_refs_resolve() -> None:
    review = _review()

    assert _repo_ref_exists(review["source_brief"]["brief_ref"])
    assert _repo_ref_exists(review["source_interpretation_read"]["read_ref"])
    assert _repo_ref_exists(review["enriched_brief_ref"])
    assert PR131_READ_PATH.exists()
    assert PR134_REVIEW_PATH.exists()
    assert review["source_brief"]["original_left_untouched"] is True
    assert review["enrichment_scope"]["original_brief_modified"] is False


def test_fields_used_are_allowed_and_excluded_fields_are_recorded() -> None:
    review = _review()
    fields_used = {item["field_name"] for item in review["fields_used"]}
    fields_excluded = {item["field_name"] for item in review["fields_excluded"]}

    assert fields_used == ALLOWED_FIELDS_USED
    assert REQUIRED_EXCLUDED <= fields_excluded
    for item in review["fields_used"]:
        assert item["must_not_be_used_as_quality_label"] is True
        assert item["uncertainty"]
        assert item["source_status"]
    assert "live_options" not in fields_used
    assert "lost_value" not in fields_used
    assert "noisy_friction" not in fields_used


def test_decision_gate_and_non_claims_are_explicit() -> None:
    review = _review()
    gate = review["decision_gate"]

    assert gate["outcome"] in ALLOWED_GATES
    assert gate["outcome"] == "proceed_to_original_vs_enriched_review"
    assert gate["runtime_integration_recommended"] is False
    assert gate["product_readiness_claimed"] is False
    assert review["next_recommendation"]["recommended_next_pr"] == (
        "PR136 Original vs Enriched Brief Review v0"
    )
    assert set(review["non_claims"]) >= REQUIRED_NON_CLAIMS


def test_pr135_files_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths(
        [REVIEW_PATH, DOC_PATH, ENRICHED_BRIEF_PATH, PR134_REVIEW_PATH, PRD_PATH]
    )

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }


def test_checked_in_pr135_files_do_not_include_private_markers() -> None:
    for path in [REVIEW_PATH, DOC_PATH, ENRICHED_BRIEF_PATH, Path(__file__)]:
        text = _text(path)
        for marker in PRIVACY_MARKERS:
            assert marker not in text
