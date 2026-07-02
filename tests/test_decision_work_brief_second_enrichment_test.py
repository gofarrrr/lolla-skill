from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-second-enrichment-test-v0/review.json"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-second-enrichment-test-v0.md"
)
ENRICHED_BRIEF_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-enriched-deploy-assisted-intake-routing-v0.md"
)
ORIGINAL_BRIEF_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-rendered-deploy-assisted-intake-routing-v0.md"
)
PR132_READ_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-conversation-interpretation-second-tiny-offline-read-v0/read.json"
)
PR136_REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-original-vs-enriched-review-v0/review.json"
)

SCHEMA_VERSION = "lolla.decision_work_brief_second_enrichment_test.v0"
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
    "proceed_to_enriched_brief_pattern_review",
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
    "new_interpretation_read_created",
    "cofounder_case_enriched",
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
    "not_cofounder_case_enrichment",
    "clean_artifacts_do_not_imply_good_advice",
    "two_enriched_examples_are_not_general_evidence",
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


def test_enriched_deploy_brief_exists_and_preserves_plain_language_shape() -> None:
    assert ENRICHED_BRIEF_PATH.exists()
    assert ORIGINAL_BRIEF_PATH.exists()

    enriched = _text(ENRICHED_BRIEF_PATH)
    original = _text(ORIGINAL_BRIEF_PATH)

    assert "## What the interpretation adds" in enriched
    assert "## What the interpretation adds" not in original
    assert "## What this does not prove" in enriched
    assert "## Evidence and limits" in enriched
    assert "Enrichment status: provisional offline test" in enriched


def test_enriched_deploy_brief_preserves_custody_and_non_claims() -> None:
    enriched = _text(ENRICHED_BRIEF_PATH)

    for required in (
        "Human validation: no",
        "Product proof: no",
        "Answer-quality scoring: no",
        "Agent action authorization: no",
        "Runtime invoked: no",
        "Skill invoked: no",
        "Model calls: 0",
        "Private/raw content included: no",
        "Provider text included: no",
        "does not prove that Lolla improved the decision",
    ):
        assert required in enriched


def test_review_json_schema_and_custody_are_conservative() -> None:
    review = _review()

    assert review["schema_version"] == SCHEMA_VERSION
    custody = review["custody_flags"]
    for field in REQUIRED_CUSTODY_FALSE_FIELDS:
        assert custody[field] is False
    assert custody["model_calls"] == 0
    assert custody["enrichment_is_provisional"] is True


def test_sources_and_enriched_ref_resolve() -> None:
    review = _review()

    assert _repo_ref_exists(review["source_brief"]["brief_ref"])
    assert _repo_ref_exists(review["source_interpretation_read"]["read_ref"])
    assert _repo_ref_exists(review["enriched_brief_ref"])
    assert PR132_READ_PATH.exists()
    assert PR136_REVIEW_PATH.exists()
    assert review["source_brief"]["case_id"] == "deploy-assisted-intake-routing"
    assert review["source_brief"]["original_left_untouched"] is True


def test_fields_used_match_allowed_enrichment_set() -> None:
    review = _review()
    fields_used = {item["field_name"] for item in review["fields_used"]}
    fields_excluded = {item["field_name"] for item in review["fields_excluded"]}

    assert fields_used == ALLOWED_FIELDS_USED
    assert REQUIRED_EXCLUDED <= fields_excluded
    for item in review["fields_used"]:
        assert item["must_not_be_used_as_quality_label"] is True
        assert item["uncertainty"]
        assert item["source_status"]


def test_decision_gate_and_non_claims_are_allowed() -> None:
    review = _review()
    gate = review["decision_gate"]

    assert gate["outcome"] in ALLOWED_GATES
    assert gate["outcome"] == "proceed_to_enriched_brief_pattern_review"
    assert gate["runtime_integration_recommended"] is False
    assert gate["product_readiness_claimed"] is False
    assert review["next_recommendation"]["recommended_next_pr"] == (
        "PR138 Enriched Brief Pattern Review v0"
    )
    assert set(review["non_claims"]) >= REQUIRED_NON_CLAIMS


def test_pr137_files_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths(
        [REVIEW_PATH, DOC_PATH, ENRICHED_BRIEF_PATH, PR136_REVIEW_PATH]
    )

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }


def test_checked_in_pr137_files_do_not_include_private_markers() -> None:
    for path in [REVIEW_PATH, DOC_PATH, ENRICHED_BRIEF_PATH, Path(__file__)]:
        text = _text(path)
        for marker in PRIVACY_MARKERS:
            assert marker not in text
