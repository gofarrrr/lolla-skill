from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-original-vs-enriched-review-v0/review.json"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-original-vs-enriched-review-v0.md"
)
ORIGINAL_BRIEF_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-rendered-launch-public-enterprise-beta-v0.md"
)
ENRICHED_BRIEF_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-enriched-launch-public-enterprise-beta-v0.md"
)
PR135_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-interpretation-enrichment-test-v0.md"
)
PR135_REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-interpretation-enrichment-test-v0/review.json"
)

SCHEMA_VERSION = "lolla.decision_work_brief_original_vs_enriched_review.v0"
ALLOWED_GATES = {
    "proceed_to_second_enriched_brief_test",
    "patch_enrichment_rules",
    "keep_interpretation_evidence_only",
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
    "second_case_enriched",
}
REQUIRED_QUESTIONS = {
    "Is the enriched brief clearer about what changed for action?",
    "Does it better distinguish what Lolla sharpened from what may already have been present?",
    "Does it preserve uncertainty?",
    "Does it preserve non-claims?",
    "Does it add useful context or just more text?",
    "Does it make the brief more overconfident?",
    "Does it remain readable for a busy decision-maker?",
    "Does it keep evidence/source limits visible?",
    "Should enrichment be tested on a second case?",
}
REQUIRED_NON_CLAIMS = {
    "review_is_codex_assisted",
    "review_is_provisional",
    "not_human_validated",
    "not_product_proof",
    "not_answer_quality_score",
    "not_agent_action_authorization",
    "not_correctness_proof",
    "not_runtime_integration",
    "not_enrichment_better_as_fact",
    "one_case_is_not_general_evidence",
    "clean_artifacts_do_not_imply_good_advice",
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


def test_review_json_has_expected_schema_and_fields() -> None:
    review = _review()

    assert review["schema_version"] == SCHEMA_VERSION
    assert {
        "schema_version",
        "review_metadata",
        "custody_flags",
        "original_brief_ref",
        "enriched_brief_ref",
        "comparison_questions",
        "reader_value_assessment",
        "uncertainty_and_nonclaim_assessment",
        "overclaim_assessment",
        "decision_gate",
        "next_recommendation",
        "non_claims",
    } <= set(review)


def test_custody_flags_are_conservative() -> None:
    custody = _review()["custody_flags"]

    for field in REQUIRED_CUSTODY_FALSE_FIELDS:
        assert custody[field] is False
    assert custody["model_calls"] == 0
    assert custody["comparison_is_provisional"] is True


def test_original_and_enriched_refs_resolve() -> None:
    review = _review()

    assert _repo_ref_exists(review["original_brief_ref"])
    assert _repo_ref_exists(review["enriched_brief_ref"])
    assert ORIGINAL_BRIEF_PATH.exists()
    assert ENRICHED_BRIEF_PATH.exists()
    assert "## What the interpretation adds" not in _text(ORIGINAL_BRIEF_PATH)
    assert "## What the interpretation adds" in _text(ENRICHED_BRIEF_PATH)


def test_comparison_questions_are_present() -> None:
    questions = _review()["comparison_questions"]

    assert {item["question"] for item in questions} == REQUIRED_QUESTIONS
    for item in questions:
        assert item["answer"] in {
            "clear",
            "partly_clear",
            "unclear",
            "overclaim_risk",
            "requires_human_review",
        }
        assert item["read"]


def test_reader_value_preserves_provisional_language() -> None:
    review = _review()
    value = review["reader_value_assessment"]
    nonclaim = review["uncertainty_and_nonclaim_assessment"]
    overclaim = review["overclaim_assessment"]

    assert "appears" in value["overall_read"].lower()
    assert nonclaim["uncertainty_preserved"] is True
    assert nonclaim["non_claims_preserved"] is True
    assert nonclaim["human_review_required"] is True
    assert overclaim["overclaim_risk_level"] in {"low", "medium", "high"}
    assert "does not prove Lolla improved" in overclaim["why_not_blocking"]


def test_decision_gate_and_non_claims_are_allowed() -> None:
    review = _review()
    gate = review["decision_gate"]

    assert gate["outcome"] in ALLOWED_GATES
    assert gate["outcome"] == "proceed_to_second_enriched_brief_test"
    assert gate["runtime_integration_recommended"] is False
    assert gate["product_readiness_claimed"] is False
    assert review["next_recommendation"]["recommended_next_pr"] == (
        "PR137 Second Enriched Brief Test v0"
    )
    assert set(review["non_claims"]) >= REQUIRED_NON_CLAIMS


def test_review_does_not_claim_enrichment_is_better_as_fact() -> None:
    text = _text(REVIEW_PATH)

    forbidden = (
        "enrichment is better",
        "enrichment proved",
        "proved better",
        "is product proof",
        "is human validated",
        "answer quality was scored",
        "agent action was authorized",
    )
    lowered = text.lower()
    for phrase in forbidden:
        assert phrase not in lowered


def test_pr136_files_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths(
        [REVIEW_PATH, DOC_PATH, PR135_DOC_PATH, PR135_REVIEW_PATH]
    )

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }


def test_checked_in_pr136_files_do_not_include_private_markers() -> None:
    for path in [REVIEW_PATH, DOC_PATH, Path(__file__)]:
        text = _text(path)
        for marker in PRIVACY_MARKERS:
            assert marker not in text
