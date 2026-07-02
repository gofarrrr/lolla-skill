from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-conversation-interpretation-read-comparison-v0/review.json"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-conversation-interpretation-read-comparison-v0.md"
)
PR131_READ_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-conversation-interpretation-tiny-offline-read-v0/read.json"
)
PR132_READ_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-conversation-interpretation-second-tiny-offline-read-v0/read.json"
)
PR133_SCHEMA_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-conversation-interpretation-read-v0.json"
)
PR133_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-conversation-interpretation-read-schema-v0.md"
)
PRD_PATH = (
    REPO_ROOT / "docs/conversation-understanding/decision-work-brief-prd-v0.md"
)

SCHEMA_VERSION = "lolla.decision_work_conversation_interpretation_read_comparison.v0"
EXPECTED_CASES = {
    "launch-public-enterprise-beta",
    "deploy-assisted-intake-routing",
}
EXPECTED_FIELDS = {
    "decision_question",
    "likely_starting_direction",
    "revised_direction_or_action_consequence",
    "live_options",
    "abandoned_or_rejected_options",
    "decision_thresholds",
    "evidence_gates",
    "useful_friction",
    "noisy_friction",
    "lost_value",
    "what_the_final_answer_does_not_prove",
}
ALLOWED_STABLE_PATTERN = {
    "stable_useful",
    "stable_partial",
    "stable_insufficient_context",
    "divergent",
    "unclear",
}
ALLOWED_SOURCE_DEPTH_PATTERN = {
    "safe_summary_sufficient_for_tiny_read",
    "safe_summary_partial_private_context_needed",
    "local_private_or_human_review_needed",
    "not_enough_evidence",
    "unclear",
}
ALLOWED_DECISION_GATES = {
    "proceed_to_brief_enrichment_test",
    "run_third_tiny_offline_read",
    "patch_interpretation_packet_builder",
    "patch_interpretation_read_schema",
    "pause_until_human_review",
    "stop_and_simplify",
}
ALLOWED_READ_SCHEMA_VERSIONS = {
    "lolla.decision_work_conversation_interpretation_read.v0",
    "lolla.decision_work_conversation_interpretation_tiny_offline_read.v0",
    "lolla.decision_work_conversation_interpretation_second_tiny_offline_read.v0",
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
    "brief_enrichment_implemented",
}
REQUIRED_NON_CLAIMS = {
    "comparison_is_codex_assisted",
    "comparison_is_provisional",
    "not_human_validated",
    "not_product_proof",
    "not_answer_quality_score",
    "not_agent_action_authorization",
    "not_correctness_proof",
    "not_runtime_integration",
    "not_runtime_extraction",
    "not_lolla_runtime_change",
    "two_reads_are_not_general_evidence",
    "clean_artifacts_do_not_imply_good_advice",
    "stable_field_shape_is_not_product_readiness",
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
FORBIDDEN_RUNTIME_FILES = (
    REPO_ROOT / "engine/system_b/decision_work_conversation_interpretation_compare.py",
    REPO_ROOT / "scripts/evals/compare_decision_work_conversation_interpretation_reads.py",
    REPO_ROOT / "scripts/evals/enrich_decision_work_brief_from_interpretation.py",
)


def _review() -> dict[str, Any]:
    return json.loads(REVIEW_PATH.read_text(encoding="utf-8"))


def _repo_ref_exists(ref: str) -> bool:
    if not ref.endswith((".md", ".json")):
        return True
    return (REPO_ROOT / ref).exists()


def test_review_has_expected_schema_and_top_level_fields() -> None:
    review = _review()

    assert review["schema_version"] == SCHEMA_VERSION
    assert {
        "schema_version",
        "review_metadata",
        "custody_flags",
        "compared_reads",
        "field_stability_comparison",
        "shared_useful_signals",
        "shared_uncertainties",
        "brief_enrichment_assessment",
        "risks",
        "decision_gate",
        "next_recommendation",
        "non_claims",
    } <= set(review)
    assert review["review_metadata"]["read_count"] == 2


def test_custody_flags_are_conservative_and_provisional() -> None:
    custody = _review()["custody_flags"]

    for field in REQUIRED_CUSTODY_FALSE_FIELDS:
        assert custody[field] is False
    assert custody["model_calls"] == 0
    assert custody["comparison_is_provisional"] is True


def test_both_expected_reads_are_compared_and_refs_resolve() -> None:
    reads = _review()["compared_reads"]

    assert {read["case_id"] for read in reads} == EXPECTED_CASES
    for read in reads:
        assert _repo_ref_exists(read["read_ref"])
        assert _repo_ref_exists(read["rendered_brief_ref"])
        assert read["read_schema_version"] in ALLOWED_READ_SCHEMA_VERSIONS
        assert read["interpreted_field_count"] == 11
        assert read["unresolved_field_count"] >= 1
        custody = read["custody_summary"]
        assert custody["human_validated"] is False
        assert custody["product_proof"] is False
        assert custody["model_calls"] == 0
        assert custody["runtime_invoked"] is False
        assert custody["skill_invoked"] is False
        assert custody["archive_mutated"] is False
        assert custody["raw_private_content_checked_in"] is False
        assert custody["provider_text_checked_in"] is False


def test_field_stability_comparison_covers_all_overlapping_fields() -> None:
    comparisons = _review()["field_stability_comparison"]

    assert {field["field_name"] for field in comparisons} == EXPECTED_FIELDS
    for field in comparisons:
        assert field["stable_pattern"] in ALLOWED_STABLE_PATTERN
        assert field["source_depth_pattern"] in ALLOWED_SOURCE_DEPTH_PATTERN
        assert isinstance(field["could_feed_brief"], bool)
        assert isinstance(field["should_feed_brief_now"], bool)
        assert isinstance(field["requires_human_review_before_user_facing"], bool)
        assert field["risk_if_used_in_brief"]


def test_stable_action_consequence_and_non_proof_fields_can_feed_brief() -> None:
    fields = {
        field["field_name"]: field
        for field in _review()["field_stability_comparison"]
    }

    for name in {
        "decision_question",
        "revised_direction_or_action_consequence",
        "decision_thresholds",
        "evidence_gates",
        "what_the_final_answer_does_not_prove",
    }:
        assert fields[name]["stable_pattern"] == "stable_useful"
        assert fields[name]["could_feed_brief"] is True
        assert fields[name]["should_feed_brief_now"] is True

    assert fields["lost_value"]["stable_pattern"] == "stable_insufficient_context"
    assert fields["lost_value"]["should_feed_brief_now"] is False


def test_shared_signals_and_uncertainties_answer_required_questions() -> None:
    review = _review()
    signals = review["shared_useful_signals"]
    uncertainties = review["shared_uncertainties"]

    assert signals["fields_that_worked_in_both_reads"]
    assert "action consequence" in signals["action_consequence_pattern"].lower()
    assert "already" in signals["sharpened_vs_already_present_read"].lower()

    assert "lost_value" in uncertainties["fields_uncertain_in_both_reads"]
    assert "private" in uncertainties["why_lost_value_remains_hard"].lower()
    assert "checked-in-safe" in uncertainties["why_starting_direction_remains_partial"]
    assert "rejected" in uncertainties["why_abandoned_options_remain_source_limited"]
    assert "outside" in uncertainties[
        "why_values_stakeholders_assistant_influence_remain_outside_scope"
    ]


def test_brief_enrichment_assessment_is_present_and_conservative() -> None:
    assessment = _review()["brief_enrichment_assessment"]

    assert assessment["would_interpretation_reads_help_decision_work_brief"] is True
    assert "revised_direction_or_action_consequence" in assessment[
        "fields_that_could_safely_enrich_the_brief_now"
    ]
    assert "lost_value" in assessment["fields_that_should_stay_evidence_or_inspection_only"]
    assert "assistant_influence_on_user_framing" in assessment[
        "fields_too_speculative_for_the_brief"
    ]
    assert "one existing brief" in assessment["smallest_safe_enrichment_test"]


def test_risks_and_decision_gate_are_explicit() -> None:
    review = _review()
    risks = review["risks"]

    assert risks["source_depth_risk"]
    assert risks["overclaim_risk"]
    assert risks["product_language_risk"]
    assert risks["quality_label_risk"]
    assert risks["runtime_integration_risk"]

    gate = review["decision_gate"]
    assert gate["outcome"] in ALLOWED_DECISION_GATES
    assert gate["outcome"] == "proceed_to_brief_enrichment_test"
    assert gate["runtime_integration_recommended"] is False
    assert gate["product_readiness_claimed"] is False
    assert review["next_recommendation"]["recommended_next_pr"] == (
        "PR135 Decision Work Brief Interpretation Enrichment Test v0"
    )


def test_non_claims_are_required_and_no_pr134_runtime_or_comparison_code_added() -> None:
    review = _review()

    assert set(review["non_claims"]) >= REQUIRED_NON_CLAIMS
    assert review["custody_flags"]["brief_enrichment_implemented"] is False
    for path in FORBIDDEN_RUNTIME_FILES:
        assert not path.exists(), path


def test_docs_and_review_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths(
        [REVIEW_PATH, DOC_PATH, PR133_DOC_PATH, PR133_SCHEMA_PATH, PRD_PATH]
    )

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }


def test_checked_in_pr134_files_do_not_include_private_markers() -> None:
    paths = [
        REVIEW_PATH,
        DOC_PATH,
        Path(__file__),
    ]

    for path in paths:
        text = path.read_text(encoding="utf-8")
        for marker in PRIVACY_MARKERS:
            assert marker not in text


def test_source_json_refs_resolve() -> None:
    assert PR131_READ_PATH.exists()
    assert PR132_READ_PATH.exists()
    assert PR133_SCHEMA_PATH.exists()

    for read in _review()["compared_reads"]:
        assert _repo_ref_exists(read["read_ref"])
        assert _repo_ref_exists(read["rendered_brief_ref"])
