from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-enriched-pattern-review-v0/review.json"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-enriched-pattern-review-v0.md"
)
ENRICHED_LAUNCH_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-enriched-launch-public-enterprise-beta-v0.md"
)
ENRICHED_DEPLOY_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-enriched-deploy-assisted-intake-routing-v0.md"
)
PR135_REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-interpretation-enrichment-test-v0/review.json"
)
PR137_REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-second-enrichment-test-v0/review.json"
)

SCHEMA_VERSION = "lolla.decision_work_brief_enriched_pattern_review.v0"
EXPECTED_CASES = {
    "launch-public-enterprise-beta",
    "deploy-assisted-intake-routing",
}
ALLOWED_GATES = {
    "proceed_to_enrichment_rules_contract",
    "patch_enrichment_rules",
    "keep_interpretation_evidence_only",
    "pause_until_human_review",
    "stop_and_simplify",
}
REQUIRED_STABLE_FIELDS = {
    "decision_question",
    "likely_starting_direction",
    "revised_direction_or_action_consequence",
    "decision_thresholds",
    "evidence_gates",
    "useful_friction",
    "what_the_final_answer_does_not_prove",
}
REQUIRED_EVIDENCE_ONLY_FIELDS = {
    "live_options",
    "abandoned_or_rejected_options",
    "noisy_friction",
    "lost_value",
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
    "rules_contract_implemented",
    "additional_cases_enriched",
}
REQUIRED_NON_CLAIMS = {
    "pattern_review_is_codex_assisted",
    "pattern_review_is_provisional",
    "not_human_validated",
    "not_product_proof",
    "not_answer_quality_score",
    "not_agent_action_authorization",
    "not_correctness_proof",
    "not_runtime_integration",
    "not_pr139_implementation",
    "two_enriched_examples_are_not_general_evidence",
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
        "enriched_briefs_compared",
        "pattern_observations",
        "stable_enrichment_fields",
        "evidence_only_fields",
        "rule_risks",
        "decision_gate",
        "next_recommendation",
        "non_claims",
    } <= set(review)
    assert review["review_metadata"]["enriched_brief_count"] == 2


def test_custody_flags_are_conservative() -> None:
    custody = _review()["custody_flags"]

    for field in REQUIRED_CUSTODY_FALSE_FIELDS:
        assert custody[field] is False
    assert custody["model_calls"] == 0
    assert custody["pattern_review_is_provisional"] is True


def test_both_enriched_briefs_are_compared_and_refs_resolve() -> None:
    compared = _review()["enriched_briefs_compared"]

    assert {item["case_id"] for item in compared} == EXPECTED_CASES
    for item in compared:
        assert _repo_ref_exists(item["enriched_brief_ref"])
        assert _repo_ref_exists(item["source_interpretation_read_ref"])
        assert _repo_ref_exists(item["source_enrichment_review_ref"])
        assert item["uncertainty_preserved"] is True
        assert item["non_claims_preserved"] is True

    assert ENRICHED_LAUNCH_PATH.exists()
    assert ENRICHED_DEPLOY_PATH.exists()
    assert PR135_REVIEW_PATH.exists()
    assert PR137_REVIEW_PATH.exists()


def test_pattern_observations_answer_required_questions() -> None:
    observations = _review()["pattern_observations"]

    assert observations["did_enrichment_help_in_both_cases"] == "yes_provisionally"
    assert observations["did_it_make_action_consequence_clearer"] == (
        "yes_provisionally"
    )
    assert observations["did_it_distinguish_sharpened_from_already_present"] == (
        "yes_provisionally"
    )
    assert observations["did_it_preserve_uncertainty"] == "yes"
    assert observations["did_it_create_overclaim_risk"] == "yes_manageable"
    assert observations["did_it_add_machinery_to_main_body"] == "no"


def test_stable_and_evidence_only_fields_are_present() -> None:
    review = _review()
    stable = {item["field_name"] for item in review["stable_enrichment_fields"]}
    evidence_only = {item["field_name"] for item in review["evidence_only_fields"]}

    assert stable == REQUIRED_STABLE_FIELDS
    assert REQUIRED_EVIDENCE_ONLY_FIELDS <= evidence_only
    for item in review["stable_enrichment_fields"]:
        assert item["future_rule"]
    for item in review["evidence_only_fields"]:
        assert item["reason"]


def test_risks_and_decision_gate_are_allowed() -> None:
    review = _review()
    risks = review["rule_risks"]
    gate = review["decision_gate"]

    assert risks["source_depth_risk"]
    assert risks["overclaim_risk"]
    assert risks["quality_label_risk"]
    assert risks["runtime_integration_risk"]
    assert gate["outcome"] in ALLOWED_GATES
    assert gate["outcome"] == "proceed_to_enrichment_rules_contract"
    assert gate["runtime_integration_recommended"] is False
    assert gate["product_readiness_claimed"] is False
    assert review["next_recommendation"]["recommended_next_pr"] == (
        "PR139 Decision Work Brief Enrichment Rules Contract v0"
    )


def test_non_claims_and_pr138_itself_does_not_implement_rules_contract() -> None:
    review = _review()

    assert set(review["non_claims"]) >= REQUIRED_NON_CLAIMS
    assert review["custody_flags"]["rules_contract_implemented"] is False
    assert "not_pr139_implementation" in review["non_claims"]


def test_enriched_examples_have_interpretation_section_and_limits() -> None:
    for path in [ENRICHED_LAUNCH_PATH, ENRICHED_DEPLOY_PATH]:
        markdown = _text(path)
        assert "## What the interpretation adds" in markdown
        assert "## What this does not prove" in markdown
        assert "## Evidence and limits" in markdown
        assert "Human validation: no" in markdown
        assert "Product proof: no" in markdown
        assert "Agent action authorization: no" in markdown
        assert "does not prove that Lolla improved the decision" in markdown


def test_pr138_files_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths(
        [
            REVIEW_PATH,
            DOC_PATH,
            ENRICHED_LAUNCH_PATH,
            ENRICHED_DEPLOY_PATH,
            PR135_REVIEW_PATH,
            PR137_REVIEW_PATH,
        ]
    )

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }


def test_checked_in_pr138_files_do_not_include_private_markers() -> None:
    for path in [REVIEW_PATH, DOC_PATH, ENRICHED_LAUNCH_PATH, ENRICHED_DEPLOY_PATH, Path(__file__)]:
        text = _text(path)
        for marker in PRIVACY_MARKERS:
            assert marker not in text
