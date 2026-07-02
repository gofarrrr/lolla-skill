from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-third-builder-case-v0/review.json"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-third-builder-case-v0.md"
)
COFOUNDER_OUTPUT_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-builder-enriched-ceo-remove-founding-cofounder-v0.md"
)
SCHEMA_VERSION = "lolla.decision_work_brief_third_builder_case.v0"
ALLOWED_DECISION_GATES = {
    "proceed_to_three_builder_case_pattern_review",
    "create_third_interpretation_read_first",
    "patch_builder_rules_again",
    "run_more_local_private_adequacy_checks",
    "proceed_to_human_review_intake",
    "pause_until_human_review",
    "stop_and_simplify",
}
REQUIRED_FALSE_FIELDS = {
    "human_validated",
    "product_proof",
    "answer_quality_scored",
    "agent_action_authorized",
    "archive_mutated",
    "runtime_invoked",
    "skill_invoked",
}
REQUIRED_CUSTODY_FALSE_FIELDS = REQUIRED_FALSE_FIELDS | {
    "raw_private_content_checked_in",
    "provider_text_checked_in",
    "local_absolute_paths_checked_in",
    "new_lolla_run_created",
    "new_interpretation_read_created",
    "builder_invoked",
    "builder_output_created",
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
FORBIDDEN_TRUE_CLAIMS = (
    "agent_action_authorized" + ": true",
    "product_proof" + ": true",
    "human_validated" + ": true",
)


def _review() -> dict[str, Any]:
    return json.loads(REVIEW_PATH.read_text(encoding="utf-8"))


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


def test_review_schema_and_conservative_metadata() -> None:
    review = _review()

    assert review["schema_version"] == SCHEMA_VERSION
    assert review["case_id"] == "ceo-remove-founding-cofounder"
    assert review["decision_family"] == "founder_governance_or_authority_transition"
    for field in REQUIRED_FALSE_FIELDS:
        assert review[field] is False
    assert review["model_calls"] == 0

    custody = review["custody_flags"]
    for field in REQUIRED_CUSTODY_FALSE_FIELDS:
        assert custody[field] is False
    assert custody["model_calls"] == 0


def test_decision_gate_is_allowed_and_blocks_builder_without_valid_read() -> None:
    review = _review()

    assert review["decision_gate"] in ALLOWED_DECISION_GATES
    assert review["decision_gate"] == "create_third_interpretation_read_first"
    assert review["recommended_next_pr"] == (
        "PR147A Decision Work Conversation Interpretation Third Tiny Offline Read v0"
    )
    assert review["builder_output_created"] is False
    assert review["builder_output_status"] == (
        "blocked_missing_builder_compatible_interpretation_read"
    )
    assert review["builder_output_ref"] is None
    assert review["interpretation_source_ref"] is None
    assert review["blocker"]["blocked"] is True
    assert review["blocker"]["why_builder_was_not_run"]


def test_source_refs_resolve_and_pr147_builder_output_is_not_claimed() -> None:
    review = _review()
    refs = _collect_repo_refs(review)

    assert refs
    for ref in refs:
        assert (REPO_ROOT / ref).exists(), ref

    assert review["builder_output_created"] is False
    assert review["builder_output_ref"] is None
    assert review["builder_output_status"] == (
        "blocked_missing_builder_compatible_interpretation_read"
    )


def test_source_availability_records_existing_builder_reads_for_other_cases() -> None:
    availability = _review()["source_availability_review"]

    assert availability["source_brief_available"] is True
    assert availability["rules_contract_available"] is True
    assert availability["builder_requires_interpretation_read"] is True
    assert availability["builder_compatible_cofounder_interpretation_read_available"] is False
    compatible_cases = {
        item["case_id"] for item in availability["builder_compatible_existing_reads"]
    }
    assert compatible_cases == {
        "launch-public-enterprise-beta",
        "deploy-assisted-intake-routing",
    }
    for item in availability["builder_compatible_existing_reads"]:
        assert item["used_for_pr147"] is False
        assert item["reason_not_used"] == "Different case."


def test_candidate_sources_are_not_builder_compatible() -> None:
    candidates = _review()["candidate_interpretation_sources_reviewed"]

    assert candidates
    for candidate in candidates:
        assert candidate["contains_cofounder_read"] is True
        assert candidate["builder_compatible"] is False
        assert candidate["reason_not_used"]
        assert (REPO_ROOT / candidate["source_ref"]).exists()


def test_blocking_review_preserves_field_boundary_and_non_claims() -> None:
    review = _review()

    assert review["readability_read"]["status"] == (
        "not_evaluated_because_builder_output_not_created"
    )
    assert review["field_boundary_read"]["status"] == "builder_boundary_preserved"
    assert review["comparison_to_prior_builder_cases"]["ceo_remove_founding_cofounder"][
        "builder_compatible_read_available"
    ] is False
    assert review["source_depth_read"]["runtime_integration_recommended"] is False
    assert review["source_depth_read"]["human_review_still_required"] is True
    assert {
        "not_human_validated",
        "not_product_proof",
        "not_answer_quality_score",
        "not_agent_action_authorization",
        "not_runtime_integration",
        "not_builder_output",
        "future_human_review_required",
    } <= set(review["non_claims"])


def test_checked_in_pr147_artifacts_have_no_private_markers_or_true_authority_claims() -> None:
    text = REVIEW_PATH.read_text(encoding="utf-8") + "\n" + DOC_PATH.read_text(encoding="utf-8")

    for marker in PRIVACY_MARKERS:
        assert marker not in text
    for claim in FORBIDDEN_TRUE_CLAIMS:
        assert claim not in text


def test_product_delta_boundary_lint_passes_for_pr147_artifacts() -> None:
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
