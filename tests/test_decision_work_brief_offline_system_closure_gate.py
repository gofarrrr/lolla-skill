from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-offline-system-closure-gate-v0/review.json"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-offline-system-closure-gate-v0.md"
)
PR143_REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-enrichment-builder-rule-patch-review-v0/review.json"
)
PR143_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-enrichment-builder-rule-patch-review-v0.md"
)
SCHEMA_VERSION = "lolla.decision_work_brief_offline_system_closure_gate.v0"
ALLOWED_GATES = {
    "package_pr114_pr144",
    "run_third_builder_case",
    "run_more_local_private_adequacy_checks",
    "pause_until_human_review",
    "simplify_brief_surface",
    "do_not_continue_current_shape",
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
    "new_lolla_run_created",
    "new_interpretation_read_created",
    "new_case_created",
}
REQUIRED_NON_CLAIMS = {
    "closure_gate_is_codex_assisted",
    "closure_gate_is_provisional",
    "not_human_validated",
    "not_product_proof",
    "not_answer_quality_score",
    "not_agent_action_authorization",
    "not_correctness_proof",
    "not_runtime_integration",
    "not_new_lolla_run",
    "not_new_interpretation_read",
    "package_gate_does_not_mean_product_ready",
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


def _collect_repo_refs(value: Any) -> set[str]:
    refs: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if key.endswith("_ref") or key == "source_refs":
                refs.update(_collect_strings(child))
            refs.update(_collect_repo_refs(child))
    elif isinstance(value, list):
        for child in value:
            refs.update(_collect_repo_refs(child))
    return {
        ref
        for ref in refs
        if ref.startswith(("docs/", "reviews/", "engine/", "tests/", "scripts/"))
    }


def _collect_strings(value: Any) -> set[str]:
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        strings: set[str] = set()
        for item in value:
            strings.update(_collect_strings(item))
        return strings
    if isinstance(value, dict):
        strings = set()
        for item in value.values():
            strings.update(_collect_strings(item))
        return strings
    return set()


def test_review_json_schema_and_top_level_shape() -> None:
    review = _review()

    assert review["schema_version"] == SCHEMA_VERSION
    assert {
        "schema_version",
        "review_metadata",
        "custody_flags",
        "source_phase_refs",
        "capability_summary",
        "deterministic_components",
        "provisional_interpretation_components",
        "artifacts_produced",
        "remaining_limits",
        "closure_questions",
        "packaging_assessment",
        "decision_gate",
        "next_recommendation",
        "non_claims",
    } <= set(review)


def test_custody_flags_are_conservative() -> None:
    custody = _review()["custody_flags"]

    for field in REQUIRED_CUSTODY_FALSE_FIELDS:
        assert custody[field] is False
    assert custody["model_calls"] == 0
    assert custody["closure_gate_is_provisional"] is True


def test_source_refs_resolve() -> None:
    refs = _collect_repo_refs(_review())

    assert refs
    for ref in refs:
        assert _repo_ref_exists(ref), ref

    assert PR143_REVIEW_PATH.exists()
    assert PR143_DOC_PATH.exists()


def test_capability_summary_separates_offline_from_runtime() -> None:
    capability = _review()["capability_summary"]

    assert capability["can_render_plain_language_markdown"] is True
    assert capability["can_prepare_offline_packets_without_interpretation"] is True
    assert capability["can_carry_provisional_interpretation_reads"] is True
    assert capability["can_preserve_uncertainty_and_non_claims"] is True
    assert capability["can_package_offline_surface"] is True
    assert capability["cannot_claim_product_readiness"] is True
    assert capability["cannot_attach_to_runtime_from_this_gate"] is True


def test_components_record_deterministic_and_provisional_parts() -> None:
    review = _review()
    deterministic = {item["component"] for item in review["deterministic_components"]}
    provisional = {item["component"] for item in review["provisional_interpretation_components"]}

    assert {
        "decision_work_brief_schema",
        "decision_work_brief_packets",
        "decision_work_brief_renderer",
        "conversation_interpretation_packets",
        "brief_enrichment_builder",
    } <= deterministic
    assert {
        "brief_pilots_and_pattern_reviews",
        "conversation_interpretation_reads",
        "enrichment_reviews",
    } <= provisional
    for item in review["deterministic_components"]:
        assert item["what_it_does"]
        assert item["what_it_does_not_do"]
    for item in review["provisional_interpretation_components"]:
        assert item["status"] == "codex_assisted_provisional"
        assert item["non_claim"]


def test_artifacts_and_limits_are_recorded() -> None:
    review = _review()
    artifacts = review["artifacts_produced"]
    limits = review["remaining_limits"]

    assert len(artifacts["plain_rendered_briefs"]) == 3
    assert len(artifacts["builder_enriched_briefs"]) == 2
    assert "docs/conversation-understanding/decision-work-brief-enrichment-rules-contract-v0.json" in artifacts["schemas_and_contracts"]
    assert "engine/system_b/decision_work_brief_enrichment.py" in artifacts["code_modules"]
    assert limits["strongest_source_depth_risk"]
    assert limits["strongest_overclaim_risk"]
    assert limits["human_review_gap"]


def test_closure_questions_and_gate_select_packaging() -> None:
    review = _review()
    questions = review["closure_questions"]
    gate = review["decision_gate"]

    assert questions["can_create_readable_brief_from_completed_lolla_run"] == (
        "yes_for_three_checked_in_safe_pilots"
    )
    assert questions["can_add_interpretation_without_pretending_proof"] == (
        "yes_for_two_enriched_cases_with_rules"
    )
    assert questions["does_enriched_brief_help_explain_action_change"] == (
        "yes_provisionally"
    )
    assert questions["are_uncertainties_still_visible"] == "yes"
    assert questions["is_runtime_integration_recommended"] == "no"
    assert gate["outcome"] in ALLOWED_GATES
    assert gate["outcome"] == "package_pr114_pr144"
    assert gate["runtime_integration_recommended"] is False
    assert gate["product_readiness_claimed"] is False
    assert review["next_recommendation"]["recommended_next_pr"] == (
        "PR145 Decision Work Brief Offline Evidence Package Gate v0"
    )


def test_packaging_assessment_is_lower_claim() -> None:
    assessment = _review()["packaging_assessment"]

    assert assessment["packageable"] is True
    assert "Decision Work Brief" in assessment["package_scope"]
    assert "implement runtime integration" in assessment["what_packaging_must_not_do"]
    assert "claim product proof" in assessment["what_packaging_must_not_do"]
    assert "create new interpretation reads" in assessment["what_packaging_must_not_do"]


def test_non_claims_are_complete() -> None:
    review = _review()

    assert set(review["non_claims"]) >= REQUIRED_NON_CLAIMS


def test_pr144_files_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths([REVIEW_PATH, DOC_PATH, PR143_REVIEW_PATH, PR143_DOC_PATH])

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }


def test_checked_in_pr144_files_do_not_include_private_markers() -> None:
    for path in [REVIEW_PATH, DOC_PATH, PR143_REVIEW_PATH, PR143_DOC_PATH, Path(__file__)]:
        text = path.read_text(encoding="utf-8")
        for marker in PRIVACY_MARKERS:
            assert marker not in text
