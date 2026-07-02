from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-enriched-builder-output-review-v0/review.json"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-enriched-builder-output-review-v0.md"
)
BUILDER_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-offline-enriched-builder-v0.md"
)
RULES_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-enrichment-rules-contract-v0.json"
)
GENERATED_LAUNCH_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-builder-enriched-launch-public-enterprise-beta-v0.md"
)
GENERATED_DEPLOY_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-builder-enriched-deploy-assisted-intake-routing-v0.md"
)
SCHEMA_VERSION = "lolla.decision_work_brief_enriched_builder_output_review.v0"
ALLOWED_GATES = {
    "proceed_to_builder_rule_patch",
    "proceed_to_third_builder_case",
    "proceed_to_offline_system_closure_gate",
    "keep_hand_built_only",
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
    "runtime_integration_implemented",
    "new_interpretation_read_created",
    "new_lolla_run_created",
    "hand_built_examples_modified",
}
REQUIRED_NON_CLAIMS = {
    "review_is_codex_assisted",
    "not_human_validated",
    "not_product_proof",
    "not_answer_quality_score",
    "not_agent_action_authorization",
    "not_correctness_proof",
    "not_runtime_integration",
    "builder_output_is_not_better_as_fact",
    "rule_compliance_is_not_product_readiness",
    "clean_outputs_do_not_imply_good_advice",
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


def _repo_ref_exists(ref: str) -> bool:
    if not ref.endswith((".md", ".json")):
        return True
    return (REPO_ROOT / ref).exists()


def test_review_json_schema_and_top_level_shape() -> None:
    review = _review()

    assert review["schema_version"] == SCHEMA_VERSION
    assert {
        "schema_version",
        "review_metadata",
        "custody_flags",
        "reviewed_outputs",
        "comparison_to_hand_built_examples",
        "rule_compliance",
        "readability_assessment",
        "risk_assessment",
        "decision_gate",
        "next_recommendation",
        "non_claims",
    } <= set(review)


def test_custody_flags_are_conservative() -> None:
    custody = _review()["custody_flags"]

    for field in REQUIRED_CUSTODY_FALSE_FIELDS:
        assert custody[field] is False
    assert custody["model_calls"] == 0


def test_reviewed_outputs_resolve_and_compare_both_cases() -> None:
    review = _review()
    outputs = review["reviewed_outputs"]

    assert {item["case_id"] for item in outputs} == {
        "launch-public-enterprise-beta",
        "deploy-assisted-intake-routing",
    }
    for item in outputs:
        assert _repo_ref_exists(item["generated_enriched_brief_ref"])
        assert _repo_ref_exists(item["hand_built_enriched_brief_ref"])
        assert _repo_ref_exists(item["original_brief_ref"])
        assert _repo_ref_exists(item["interpretation_read_ref"])
        assert item["generated_output_exists"] is True
        assert item["hand_built_output_exists"] is True
        assert item["original_left_untouched"] is True
        assert item["builder_created_separate_output"] is True


def test_rule_compliance_and_readability_assessment_are_present() -> None:
    review = _review()
    compliance = review["rule_compliance"]
    readability = review["readability_assessment"]

    assert compliance["allowed_user_facing_fields_only"] is True
    assert compliance["evidence_only_fields_excluded_from_main_body"] is True
    assert compliance["uncertainty_visible"] is True
    assert compliance["non_claims_visible"] is True
    assert compliance["no_model_calls"] is True
    assert compliance["no_runtime_invocation"] is True
    assert readability["did_builder_preserve_useful_enrichment_signal"] is True
    assert readability["is_output_too_templated"] is True
    assert readability["good_enough_for_runtime_planning"] is False


def test_decision_gate_and_non_claims_are_conservative() -> None:
    review = _review()
    gate = review["decision_gate"]

    assert gate["outcome"] in ALLOWED_GATES
    assert gate["outcome"] == "proceed_to_builder_rule_patch"
    assert gate["runtime_integration_recommended"] is False
    assert gate["product_readiness_claimed"] is False
    assert review["next_recommendation"]["recommended_next_pr"] == (
        "PR142 Decision Work Brief Enrichment Builder Rule Patch v0"
    )
    assert set(review["non_claims"]) >= REQUIRED_NON_CLAIMS


def test_review_says_runtime_integration_is_not_implemented() -> None:
    review = _review()

    assert review["custody_flags"]["runtime_integration_implemented"] is False
    assert "not_runtime_integration" in review["non_claims"]
    assert "runtime integration" in review["next_recommendation"]["not_recommended"]
    assert review["risk_assessment"]["runtime_integration_risk"]


def test_generated_outputs_preserve_non_claims() -> None:
    for path in [GENERATED_LAUNCH_PATH, GENERATED_DEPLOY_PATH]:
        text = path.read_text(encoding="utf-8")
        assert "## What the interpretation adds" in text
        assert "## What this does not prove" in text
        assert "## Evidence and limits" in text
        assert "Human validation: no" in text
        assert "Product proof: no" in text
        assert "Answer-quality scoring: no" in text
        assert "Agent action authorization: no" in text
        assert "does not prove Lolla improved the decision" in text


def test_pr141_files_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths(
        [REVIEW_PATH, DOC_PATH, BUILDER_DOC_PATH, RULES_PATH]
    )

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }


def test_checked_in_pr141_files_do_not_include_private_markers() -> None:
    for path in [
        REVIEW_PATH,
        DOC_PATH,
        BUILDER_DOC_PATH,
        RULES_PATH,
        GENERATED_LAUNCH_PATH,
        GENERATED_DEPLOY_PATH,
        Path(__file__),
    ]:
        text = path.read_text(encoding="utf-8")
        for marker in PRIVACY_MARKERS:
            assert marker not in text
