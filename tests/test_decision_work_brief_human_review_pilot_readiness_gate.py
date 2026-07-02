from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-human-review-pilot-readiness-gate-v0.md"
)
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-human-review-pilot-readiness-gate-v0/review.json"
)
SCAFFOLD_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-human-review-pilot-scaffold-v0.md"
)
TEMPLATE_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-human-review-response-template-v0.json"
)
SCHEMA_VERSION = "lolla.decision_work_brief_human_review_pilot_readiness_gate.v0"
EXPECTED_CASES = {
    "launch-public-enterprise-beta",
    "deploy-assisted-intake-routing",
    "ceo-remove-founding-cofounder",
}
ALLOWED_NEXT_STEPS = {
    "collect_real_human_review_response",
    "package_pr146_pr152",
    "pause_until_human_review_capacity",
    "revise_review_form_first",
    "stop_and_simplify",
}
REQUIRED_FALSE_FIELDS = {
    "human_validated",
    "human_review_completed",
    "human_response_collected",
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
    "human_answers_filled_by_codex",
    "runtime_attachment_implemented",
    "customer_surface_enabled",
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
    "Human review completed: yes",
    "Human response collected: yes",
    "Answer-quality scoring: yes",
    "Agent action authorization: yes",
    "agent_action_authorized" + ": true",
    "product_proof" + ": true",
    "human_validated" + ": true",
    "human_review_completed" + ": true",
    "human_response_collected" + ": true",
)


def _review() -> dict[str, Any]:
    return json.loads(REVIEW_PATH.read_text(encoding="utf-8"))


def _template() -> dict[str, Any]:
    return json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))


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


def test_review_schema_and_conservative_metadata() -> None:
    review = _review()

    assert review["schema_version"] == SCHEMA_VERSION
    assert review["review_mode"] == "human_review_pilot_readiness_gate_only"
    assert review["model_calls"] == 0
    for field in REQUIRED_FALSE_FIELDS:
        assert review[field] is False

    custody = review["custody_flags"]
    assert custody["model_calls"] == 0
    for field in REQUIRED_CUSTODY_FALSE_FIELDS:
        assert custody[field] is False


def test_scaffold_template_and_target_refs_resolve() -> None:
    review = _review()

    assert (REPO_ROOT / review["pilot_scaffold_ref"]) == SCAFFOLD_PATH
    assert (REPO_ROOT / review["response_template_ref"]) == TEMPLATE_PATH
    assert SCAFFOLD_PATH.exists()
    assert TEMPLATE_PATH.exists()
    for ref in _collect_repo_refs(review):
        assert (REPO_ROOT / ref).exists(), ref


def test_exactly_three_target_cases_are_listed() -> None:
    review = _review()

    assert {case["case_id"] for case in review["target_cases"]} == EXPECTED_CASES
    for case in review["target_cases"]:
        assert (REPO_ROOT / case["enriched_brief_ref"]).exists()
        assert case["known_highest_risk_uncertainty"]


def test_readiness_checks_keep_review_uncollected() -> None:
    checks = _review()["readiness_checks"]

    assert checks["pilot_scaffold_exists"] is True
    assert checks["response_template_exists"] is True
    assert checks["response_template_is_blank"] is True
    assert checks["exactly_three_cases_in_scope"] is True
    assert checks["all_enriched_brief_refs_resolve"] is True
    assert checks["all_case_answers_are_not_reviewed"] is True
    assert checks["human_review_completed"] is False
    assert checks["human_response_collected"] is False
    assert checks["codex_did_not_fill_human_answers"] is True
    assert checks["runtime_customer_surface_blocked"] is True
    assert checks["ready_for_real_human_review"] is True


def test_response_template_still_has_blank_human_fields() -> None:
    template = _template()

    assert template["review_status"] == "not_started"
    assert template["human_review_completed"] is False
    for case in template["cases"]:
        assert case["case_id"] in EXPECTED_CASES
        assert case["useful_to_decision_maker"] == "not_reviewed"
        assert case["action_consequence_clear"] == "not_reviewed"
        assert case["uncertainty_visible"] == "not_reviewed"
        assert case["source_limits_visible"] == "not_reviewed"
        assert case["overtrust_risk"] == "not_reviewed"
        assert case["should_show_to_user"] == "not_reviewed"
        assert case["reviewer_notes"] is None
        assert case["missing_context_needed"] == []


def test_runtime_customer_surface_remains_blocked_and_human_input_required() -> None:
    review = _review()
    blockers = set(review["blockers_to_runtime_or_customer_surface"])
    required_inputs = set(review["required_human_inputs"])

    assert "no_real_human_response_collected" in blockers
    assert "human_review_not_completed" in blockers
    assert "runtime_attachment_not_implemented" in blockers
    assert "template_answers_are_blank" in blockers
    assert "reviewer_metadata" in required_inputs
    assert "case_usefulness_answers" in required_inputs
    assert "case_overtrust_answers" in required_inputs
    assert "final_recommendation" in required_inputs


def test_decision_gate_uses_allowed_next_step() -> None:
    review = _review()

    assert set(review["allowed_next_steps"]) == ALLOWED_NEXT_STEPS
    assert review["decision_gate"] in ALLOWED_NEXT_STEPS
    assert review["decision_gate"] == "collect_real_human_review_response"
    assert review["recommended_next_pr"] == (
        "PR153 Decision Work Brief Human Review Response Collection v0"
    )


def test_doc_says_review_not_run_and_codex_must_not_substitute() -> None:
    markdown = DOC_PATH.read_text(encoding="utf-8")

    assert "No real human response has been collected yet" in markdown
    assert "The pilot has not run" in markdown
    assert "Runtime or customer-facing use remains blocked" in markdown
    assert "Codex must not fill these fields for the reviewer" in markdown
    assert "collect_real_human_review_response" in markdown


def test_no_private_markers_or_authority_claims() -> None:
    text = "\n".join(
        [
            DOC_PATH.read_text(encoding="utf-8"),
            REVIEW_PATH.read_text(encoding="utf-8"),
            TEMPLATE_PATH.read_text(encoding="utf-8"),
            SCAFFOLD_PATH.read_text(encoding="utf-8"),
        ]
    )

    for marker in PRIVACY_MARKERS:
        assert marker not in text
    for claim in FORBIDDEN_TRUE_CLAIMS:
        assert claim not in text


def test_product_delta_boundary_lint_passes_for_pr152_artifacts() -> None:
    report = lint_product_delta_paths([DOC_PATH, REVIEW_PATH, TEMPLATE_PATH, SCAFFOLD_PATH])

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
