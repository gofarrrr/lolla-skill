from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-human-review-intake-plan-v0/review.json"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-human-review-intake-plan-v0.md"
)
PR149_REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-three-builder-case-pattern-review-v0/review.json"
)
BUILDER_OUTPUT_REFS = {
    "docs/conversation-understanding/decision-work-brief-builder-enriched-launch-public-enterprise-beta-v0.md",
    "docs/conversation-understanding/decision-work-brief-builder-enriched-deploy-assisted-intake-routing-v0.md",
    "docs/conversation-understanding/decision-work-brief-builder-enriched-ceo-remove-founding-cofounder-v0.md",
}
SCHEMA_VERSION = "lolla.decision_work_brief_human_review_intake_plan.v0"
EXPECTED_CASES = {
    "launch-public-enterprise-beta",
    "deploy-assisted-intake-routing",
    "ceo-remove-founding-cofounder",
}
REQUIRED_FALSE_FIELDS = {
    "human_validated",
    "human_review_completed",
    "product_proof",
    "runtime_invoked",
    "skill_invoked",
    "archive_mutated",
    "answer_quality_scored",
    "agent_action_authorized",
}
REQUIRED_CUSTODY_FALSE_FIELDS = REQUIRED_FALSE_FIELDS | {
    "raw_private_content_checked_in",
    "provider_text_checked_in",
    "local_absolute_paths_checked_in",
    "new_lolla_run_created",
    "new_interpretation_read_created",
    "new_builder_output_created",
    "runtime_attachment_implemented",
}
ALLOWED_OUTCOMES = {
    "useful_but_needs_source_depth",
    "useful_but_too_overtrust_inducing",
    "readable_but_not_actionable",
    "too_internal_for_user_surface",
    "ready_for_more_human_review",
    "not_ready_for_runtime",
    "needs_simplification",
    "inconclusive",
}
ALLOWED_DECISION_GATES = {
    "package_pr146_pr150",
    "run_human_review_pilot",
    "revise_brief_surface_before_human_review",
    "run_more_local_private_adequacy_checks",
    "stop_and_simplify",
    "runtime_attachment_plan_only",
}
REQUIRED_REVIEWER_CATEGORIES = {
    "usefulness",
    "action_consequence",
    "uncertainty",
    "source_depth",
    "overtrust",
    "private_context",
    "runtime_blockers",
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
    "Product proof: yes",
    "Human validation: yes",
    "Answer-quality scoring: yes",
    "Agent action authorization: yes",
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
            if key.endswith("_ref") or key.endswith("_refs") or key == "ref":
                refs.update(_collect_strings(child))
            refs.update(_collect_repo_refs(child))
    elif isinstance(value, list):
        for child in value:
            refs.update(_collect_repo_refs(child))
    return {ref for ref in refs if ref.startswith(("docs/", "reviews/", "tests/"))}


def test_schema_and_conservative_metadata() -> None:
    review = _review()

    assert review["schema_version"] == SCHEMA_VERSION
    assert review["review_mode"] == "human_review_intake_plan_only"
    assert review["model_calls"] == 0
    for field in REQUIRED_FALSE_FIELDS:
        assert review[field] is False

    custody = review["custody_flags"]
    assert custody["model_calls"] == 0
    for field in REQUIRED_CUSTODY_FALSE_FIELDS:
        assert custody[field] is False


def test_review_scope_includes_all_three_builder_outputs() -> None:
    review = _review()

    assert set(review["review_scope"]["case_ids"]) == EXPECTED_CASES
    assert set(review["review_scope"]["builder_output_refs"]) == BUILDER_OUTPUT_REFS
    source_builder_refs = {
        artifact["ref"]
        for artifact in review["source_artifacts"]
        if artifact["artifact_type"] == "builder_generated_enriched_brief"
    }
    assert source_builder_refs == BUILDER_OUTPUT_REFS
    for ref in _collect_repo_refs(review):
        assert (REPO_ROOT / ref).exists(), ref


def test_reviewer_questions_cover_required_categories() -> None:
    questions = _review()["reviewer_questions"]

    assert {item["category"] for item in questions} >= REQUIRED_REVIEWER_CATEGORIES
    joined = json.dumps(questions)
    for phrase in [
        "busy decision-maker",
        "action consequence",
        "uncertainty",
        "source-depth",
        "false confidence",
        "private",
        "runtime attachment",
    ]:
        assert phrase in joined


def test_case_review_forms_cover_case_specific_risks() -> None:
    forms = _review()["case_review_forms"]

    assert {item["case_id"] for item in forms} == EXPECTED_CASES
    joined = json.dumps(forms)
    assert "public launch versus private proof" in joined
    assert "patient-risk and compliance caveats" in joined
    assert "authority-transfer consequences" in joined
    assert "legal, equity, board, employment" in joined
    for form in forms:
        assert form["builder_output_ref"] in BUILDER_OUTPUT_REFS
        assert form["case_specific_stop_condition"]
        assert form["required_questions"]


def test_overtrust_source_depth_private_context_and_stop_conditions() -> None:
    review = _review()

    assert review["overtrust_checks"]
    assert review["source_depth_checks"]
    assert review["private_context_checks"]
    stop_conditions = review["stop_conditions"]
    assert stop_conditions["runtime_attachment_blockers"]
    assert stop_conditions["customer_facing_blockers"]
    assert stop_conditions["simplification_triggers"]
    joined = json.dumps(stop_conditions)
    assert "brief reads like action authorization" in joined
    assert "source limits are too buried" in joined
    assert "human review has not been completed" in joined


def test_allowed_outcomes_and_decision_gate_use_approved_vocabulary() -> None:
    review = _review()

    assert set(review["allowed_outcomes"]) == ALLOWED_OUTCOMES
    assert set(review["allowed_decision_gates"]) == ALLOWED_DECISION_GATES
    assert review["decision_gate"] in ALLOWED_DECISION_GATES
    assert review["decision_gate"] == "run_human_review_pilot"
    assert review["recommended_next_pr"] == (
        "PR151 Decision Work Brief Human Review Pilot v0"
    )


def test_doc_explains_intake_without_claiming_completed_human_review() -> None:
    markdown = DOC_PATH.read_text(encoding="utf-8")

    assert "This is not the human review itself" in markdown
    assert "run_human_review_pilot" in markdown
    assert "PR151 Decision Work Brief Human Review Pilot v0" in markdown
    assert "Runtime attachment is still premature" in markdown


def test_no_private_markers_or_authority_claims() -> None:
    text = (
        REVIEW_PATH.read_text(encoding="utf-8")
        + "\n"
        + DOC_PATH.read_text(encoding="utf-8")
        + "\n"
        + PR149_REVIEW_PATH.read_text(encoding="utf-8")
    )

    for marker in PRIVACY_MARKERS:
        assert marker not in text
    for claim in FORBIDDEN_TRUE_CLAIMS:
        assert claim not in text


def test_product_delta_boundary_lint_passes_for_pr150_artifacts() -> None:
    report = lint_product_delta_paths([DOC_PATH, REVIEW_PATH, PR149_REVIEW_PATH])

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
