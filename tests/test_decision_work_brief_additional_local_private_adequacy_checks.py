from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-additional-local-private-adequacy-checks-v0/review.json"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-additional-local-private-adequacy-checks-v0.md"
)
PR125_REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-local-private-adequacy-check-v0/review.json"
)
PR144_REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-offline-system-closure-gate-v0/review.json"
)

SCHEMA_VERSION = "lolla.decision_work_brief_additional_local_private_adequacy_checks.v0"
EXPECTED_CASES = {
    "ceo-remove-founding-cofounder",
    "deploy-assisted-intake-routing",
}
APPROVED_ADEQUACY_VALUES = {
    "adequate_no_material_change",
    "adequate_with_private_nuance",
    "partly_adequate",
    "materially_changed_by_private_context",
    "too_thin_to_assess",
    "unsafe_to_summarize",
    "requires_human_review",
}
APPROVED_DECISION_GATES = {
    "proceed_to_third_builder_case",
    "proceed_to_human_review_intake",
    "proceed_to_runtime_attachment_plan_only",
    "run_more_local_private_adequacy_checks",
    "patch_brief_or_interpretation_contract",
    "pause_until_human_review",
    "stop_and_simplify",
}
REQUIRED_TOP_LEVEL_FIELDS = {
    "schema_version",
    "review_mode",
    "human_validated",
    "product_proof",
    "model_calls",
    "answer_quality_scored",
    "agent_action_authorized",
    "archive_mutated",
    "runtime_invoked",
    "skill_invoked",
    "local_private_context_inspected",
    "raw_private_content_checked_in",
    "provider_text_checked_in",
    "local_absolute_paths_checked_in",
    "review_metadata",
    "custody_flags",
    "cases",
    "aggregate_findings",
    "source_depth_findings",
    "overclaim_findings",
    "decision_gate",
    "recommended_next_pr",
    "non_claims",
}
REQUIRED_FALSE_FIELDS = {
    "human_validated",
    "product_proof",
    "answer_quality_scored",
    "agent_action_authorized",
    "archive_mutated",
    "runtime_invoked",
    "skill_invoked",
    "raw_private_content_checked_in",
    "provider_text_checked_in",
    "local_absolute_paths_checked_in",
}
REQUIRED_CUSTODY_FALSE_FIELDS = REQUIRED_FALSE_FIELDS | {
    "new_lolla_run_created",
    "new_case_pilot_created",
    "new_interpretation_read_created",
    "runtime_integration_implemented",
    "broad_judge_used",
    "automatic_labels_created",
}
CASE_ADEQUACY_FIELDS = {
    "decision_question_adequacy",
    "starting_direction_adequacy",
    "action_consequence_adequacy",
    "pressure_or_change_adequacy",
    "option_path_adequacy",
    "lost_value_adequacy",
    "stakeholder_or_constraint_adequacy",
    "safe_conclusion",
}
REQUIRED_NON_CLAIMS = {
    "review_is_codex_assisted",
    "not_human_validated",
    "not_product_proof",
    "not_answer_quality_score",
    "not_agent_action_authorization",
    "not_correctness_proof",
    "local_private_shadow_review_is_not_human_review",
    "adequacy_check_does_not_certify_customer_readiness",
    "clean_artifacts_do_not_imply_good_advice",
    "local_private_context_was_not_checked_in",
    "future_human_review_required",
    "runtime_integration_not_implemented",
}
FORBIDDEN_AUTHORITY_KEYS = {
    "safe_for_" + "agent_use",
    "quality" + "_score",
    "answer_quality" + "_score",
    "improvement" + "_score",
    "judge" + "_score",
    "winner",
    "certified",
    "pass" + "_fail",
}
FORBIDDEN_TRUE_CLAIMS = (
    "agent_action_authorized" + ": true",
    "product_proof" + ": true",
    "human_validated" + ": true",
)
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


def _collect_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        strings: list[str] = []
        for item in value:
            strings.extend(_collect_strings(item))
        return strings
    if isinstance(value, dict):
        strings = []
        for item in value.values():
            strings.extend(_collect_strings(item))
        return strings
    return []


def _collect_repo_refs(value: Any) -> set[str]:
    refs: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if key.endswith("_ref") or key.endswith("_refs"):
                refs.update(_collect_strings(child))
            refs.update(_collect_repo_refs(child))
    elif isinstance(value, list):
        for child in value:
            refs.update(_collect_repo_refs(child))
    return {ref for ref in refs if ref.startswith(("docs/", "reviews/", "tests/", "engine/", "scripts/"))}


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


def test_review_schema_and_top_level_shape() -> None:
    review = _review()

    assert review["schema_version"] == SCHEMA_VERSION
    assert REQUIRED_TOP_LEVEL_FIELDS <= set(review)
    assert review["review_mode"] == "local_private_shadow_review_safe_conclusions_only"
    assert review["review_metadata"]["preferred_cases_available"] is True


def test_conservative_metadata_and_custody_flags() -> None:
    review = _review()

    for field in REQUIRED_FALSE_FIELDS:
        assert review[field] is False
    assert review["model_calls"] == 0
    assert review["local_private_context_inspected"] is True

    custody = review["custody_flags"]
    for field in REQUIRED_CUSTODY_FALSE_FIELDS:
        assert custody[field] is False
    assert custody["model_calls"] == 0
    assert custody["local_private_context_inspected"] is True
    assert custody["local_private_read_only"] is True


def test_two_preferred_cases_are_reviewed() -> None:
    cases = _review()["cases"]

    assert len(cases) >= 2
    assert {case["case_id"] for case in cases} == EXPECTED_CASES
    for case in cases:
        assert case["run_ref"]
        assert "/" in case["run_ref"]
        assert case["local_private_context_status"] == "completed_read_only_safe_conclusions"
        assert case["material_change_summary"]
        assert case["human_followup_questions"]
        assert case["safe_conclusion"] in APPROVED_ADEQUACY_VALUES


def test_case_adequacy_values_are_approved() -> None:
    for case in _review()["cases"]:
        for field in CASE_ADEQUACY_FIELDS:
            assert case[field] in APPROVED_ADEQUACY_VALUES
        assert case["overconfidence_risk"]
        assert case["source_depth_risk"]


def test_case_refs_resolve_and_do_not_reference_local_paths() -> None:
    refs = _collect_repo_refs(_review())

    assert refs
    for ref in refs:
        assert _repo_ref_exists(ref), ref

    assert PR125_REVIEW_PATH.exists()
    assert PR144_REVIEW_PATH.exists()


def test_artifact_types_are_names_only_not_contents() -> None:
    for case in _review()["cases"]:
        artifact_types = case["local_private_artifact_types_inspected"]
        assert artifact_types
        assert all(isinstance(item, str) for item in artifact_types)
        joined = "\n".join(artifact_types)
        for marker in PRIVACY_MARKERS:
            assert marker not in joined
        assert all(not item.startswith("/") for item in artifact_types)


def test_aggregate_findings_and_gate_are_conservative() -> None:
    review = _review()
    aggregate = review["aggregate_findings"]
    gate = review["decision_gate"]

    assert aggregate["preferred_cases_available"] is True
    assert set(aggregate["cases_reviewed"]) == EXPECTED_CASES
    assert aggregate["prior_case_already_checked"] == "launch-public-enterprise-beta"
    assert aggregate["strongest_useful_signal"]
    assert aggregate["strongest_source_depth_private_nuance_risk"]
    assert aggregate["strongest_overclaim_risk"]
    assert gate["outcome"] in APPROVED_DECISION_GATES
    assert gate["outcome"] == "proceed_to_third_builder_case"
    assert gate["runtime_integration_recommended"] is False
    assert gate["product_readiness_claimed"] is False


def test_non_claims_are_present() -> None:
    review = _review()

    assert REQUIRED_NON_CLAIMS <= set(review["non_claims"])
    overclaim = review["overclaim_findings"]
    assert overclaim["does_pr146_show_product_proof"] is False
    assert overclaim["does_pr146_show_human_validation"] is False
    assert overclaim["does_pr146_score_answer_quality"] is False
    assert overclaim["does_pr146_authorize_agent_action"] is False


def test_checked_in_artifacts_do_not_contain_private_markers_or_authority_claims() -> None:
    text = REVIEW_PATH.read_text(encoding="utf-8") + "\n" + DOC_PATH.read_text(encoding="utf-8")

    for marker in PRIVACY_MARKERS:
        assert marker not in text
    for key in FORBIDDEN_AUTHORITY_KEYS:
        assert key not in _walk_keys(_review())
    for term in FORBIDDEN_TRUE_CLAIMS:
        assert term not in text


def test_product_delta_boundary_lint_passes_for_pr146_artifacts() -> None:
    report = lint_product_delta_paths([DOC_PATH, REVIEW_PATH])

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }


def test_skill_files_remain_untouched() -> None:
    status = subprocess.check_output(
        ["git", "status", "--short", "--", "SKILL.md", "scripts/skill"],
        cwd=REPO_ROOT,
        text=True,
    )

    assert status.strip() == ""
