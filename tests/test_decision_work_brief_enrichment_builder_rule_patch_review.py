from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-enrichment-builder-rule-patch-review-v0/review.json"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-enrichment-builder-rule-patch-review-v0.md"
)
PR142_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-enrichment-builder-rule-patch-v0.md"
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
SCHEMA_VERSION = "lolla.decision_work_brief_enrichment_builder_rule_patch_review.v0"
ALLOWED_GATES = {
    "proceed_to_offline_system_closure_gate",
    "run_third_builder_case",
    "patch_builder_rules_again",
    "keep_hand_built_only",
    "pause_until_human_review",
    "stop_and_simplify",
}
EXPECTED_CASES = {
    "launch-public-enterprise-beta",
    "deploy-assisted-intake-routing",
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
    "review_is_provisional",
    "not_human_validated",
    "not_product_proof",
    "not_answer_quality_score",
    "not_agent_action_authorization",
    "not_correctness_proof",
    "not_runtime_integration",
    "not_new_interpretation_read",
    "not_new_lolla_run",
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
    if not ref.endswith((".md", ".json", ".py")):
        return True
    return (REPO_ROOT / ref).exists()


def _main_enrichment_section(markdown: str) -> str:
    start = markdown.index("## What the interpretation adds")
    end = markdown.index("## What still might be wrong")
    return markdown[start:end]


def test_review_json_schema_and_top_level_shape() -> None:
    review = _review()

    assert review["schema_version"] == SCHEMA_VERSION
    assert {
        "schema_version",
        "review_metadata",
        "custody_flags",
        "source_artifacts",
        "reviewed_examples",
        "readability_findings",
        "uncertainty_findings",
        "overclaim_findings",
        "field_boundary_findings",
        "comparison_to_hand_built_examples",
        "decision_gate",
        "recommended_next_pr",
        "non_claims",
    } <= set(review)


def test_custody_flags_are_conservative() -> None:
    custody = _review()["custody_flags"]

    for field in REQUIRED_CUSTODY_FALSE_FIELDS:
        assert custody[field] is False
    assert custody["model_calls"] == 0
    assert custody["builder_patch_review_is_provisional"] is True


def test_source_refs_and_reviewed_examples_resolve() -> None:
    review = _review()

    for ref in review["source_artifacts"].values():
        assert _repo_ref_exists(ref)

    examples = review["reviewed_examples"]
    assert {item["case_id"] for item in examples} == EXPECTED_CASES
    for item in examples:
        assert _repo_ref_exists(item["patched_builder_output_ref"])
        assert _repo_ref_exists(item["hand_built_enriched_brief_ref"])
        assert _repo_ref_exists(item["original_brief_ref"])
        assert _repo_ref_exists(item["interpretation_read_ref"])
        assert item["patched_output_exists"] is True
        assert item["hand_built_output_exists"] is True
        assert item["original_left_untouched"] is True
        assert item["action_consequence_visible"] is True
        assert item["uncertainty_visible"] is True
        assert item["non_claims_visible"] is True


def test_readability_uncertainty_and_field_boundaries_are_present() -> None:
    review = _review()

    readability = review["readability_findings"]
    assert readability["does_patched_output_read_less_robotic"] is True
    assert readability["repeated_stock_phrase_reduced"] is True
    assert readability["action_consequence_easier_to_understand"] is True
    assert readability["preferred_offline_enrichment_path_for_existing_two_cases"] is True

    uncertainty = review["uncertainty_findings"]
    assert uncertainty["starting_direction_uncertainty_visible"] is True
    assert uncertainty["checked_in_safe_compression_visible"] is True
    assert uncertainty["source_limits_visible"] is True
    assert uncertainty["interpretation_marked_provisional"] is True

    boundaries = review["field_boundary_findings"]
    assert boundaries["allowed_user_facing_fields_only"] is True
    assert boundaries["evidence_only_fields_excluded_from_main_body"] is True
    assert boundaries["forbidden_quality_or_authority_fields_excluded"] is True
    assert boundaries["rules_contract_unchanged"] is True


def test_overclaim_findings_and_decision_gate_are_conservative() -> None:
    review = _review()
    overclaim = review["overclaim_findings"]
    gate = review["decision_gate"]

    assert overclaim["product_proof_claimed"] is False
    assert overclaim["human_validation_claimed"] is False
    assert overclaim["answer_quality_scored"] is False
    assert overclaim["agent_action_authorized"] is False
    assert overclaim["lolla_improvement_claimed_as_fact"] is False
    assert gate["outcome"] in ALLOWED_GATES
    assert gate["outcome"] == "proceed_to_offline_system_closure_gate"
    assert gate["runtime_integration_recommended"] is False
    assert gate["product_readiness_claimed"] is False
    assert review["recommended_next_pr"]["recommended_next_pr"] == (
        "PR144 Decision Work Brief Offline System Closure Gate v0"
    )


def test_patched_outputs_preserve_non_claims_and_are_less_repetitive() -> None:
    for path in [GENERATED_LAUNCH_PATH, GENERATED_DEPLOY_PATH]:
        text = path.read_text(encoding="utf-8")
        section = _main_enrichment_section(text)

        assert text.count("## What the interpretation adds") == 1
        assert "## What this does not prove" in text
        assert "## Evidence and limits" in text
        assert "Human validation: no" in text
        assert "Product proof: no" in text
        assert "Answer-quality scoring: no" in text
        assert "Agent action authorization: no" in text
        assert "This enrichment remains provisional" in section
        assert "does not prove Lolla improved the decision" in section
        assert section.count("The interpretation read") == 0
        assert section.count("provisional") <= 1
        assert "quality score" not in section
        assert "approval" not in section
        assert "agent action authorization" not in section


def test_non_claims_are_complete() -> None:
    review = _review()

    assert set(review["non_claims"]) >= REQUIRED_NON_CLAIMS


def test_pr143_files_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths(
        [REVIEW_PATH, DOC_PATH, PR142_DOC_PATH, RULES_PATH]
    )

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }


def test_checked_in_pr143_files_do_not_include_private_markers() -> None:
    for path in [
        REVIEW_PATH,
        DOC_PATH,
        PR142_DOC_PATH,
        RULES_PATH,
        GENERATED_LAUNCH_PATH,
        GENERATED_DEPLOY_PATH,
        Path(__file__),
    ]:
        text = path.read_text(encoding="utf-8")
        for marker in PRIVACY_MARKERS:
            assert marker not in text
