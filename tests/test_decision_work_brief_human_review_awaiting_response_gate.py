from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-human-review-awaiting-response-gate-v0.md"
)
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-human-review-awaiting-response-gate-v0/review.json"
)
READINESS_GATE_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-human-review-pilot-readiness-gate-v0.md"
)
SCAFFOLD_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-human-review-pilot-scaffold-v0.md"
)
TEMPLATE_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-human-review-response-template-v0.json"
)
SCHEMA_VERSION = "lolla.decision_work_brief_human_review_awaiting_response_gate.v0"
ALLOWED_NEXT_STEPS = {
    "collect_real_human_review_response",
    "package_pr146_pr153",
    "pause_until_human_review_capacity",
    "revise_review_scaffold_if_reviewers_are_confused",
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
CASE_ANSWER_FIELDS = {
    "useful_to_decision_maker",
    "action_consequence_clear",
    "uncertainty_visible",
    "source_limits_visible",
    "overtrust_risk",
    "too_operationally_decisive",
    "should_show_to_user",
    "should_feed_agent_inspection",
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
    assert review["review_mode"] == "awaiting_real_human_response_gate"
    assert review["model_calls"] == 0
    for field in REQUIRED_FALSE_FIELDS:
        assert review[field] is False

    custody = review["custody_flags"]
    assert custody["model_calls"] == 0
    for field in REQUIRED_CUSTODY_FALSE_FIELDS:
        assert custody[field] is False


def test_required_refs_resolve() -> None:
    review = _review()

    assert (REPO_ROOT / review["readiness_gate_ref"]) == READINESS_GATE_PATH
    assert (REPO_ROOT / review["pilot_scaffold_ref"]) == SCAFFOLD_PATH
    assert (REPO_ROOT / review["response_template_ref"]) == TEMPLATE_PATH
    for ref in _collect_repo_refs(review):
        assert (REPO_ROOT / ref).exists(), ref


def test_current_status_says_no_human_response_exists() -> None:
    status = _review()["current_status"]

    assert status["pilot_scaffold_exists"] is True
    assert status["readiness_gate_exists"] is True
    assert status["response_template_exists"] is True
    assert status["response_template_review_status"] == "not_started"
    assert status["response_template_human_review_completed"] is False
    assert status["response_template_case_answers_blank"] is True
    assert status["human_response_collected"] is False
    assert status["human_review_completed"] is False
    assert status["human_validation_claimed"] is False
    assert status["codex_substituted_for_human_reviewer"] is False
    assert status["runtime_or_customer_surface_blocked"] is True


def test_blocked_reason_and_unblocked_by_require_real_human_response() -> None:
    review = _review()
    blocked_reason = set(review["blocked_reason"])
    unblocked_by = set(review["unblocked_by"])
    required_input = review["next_required_input"]

    assert "no_real_human_response_exists" in blocked_reason
    assert "response_template_is_blank" in blocked_reason
    assert "case_answers_remain_not_reviewed" in blocked_reason
    assert "codex_cannot_substitute_for_human_reviewer" in blocked_reason
    assert "real_human_reviewer_fills_pr151_response_template" in unblocked_by
    assert required_input["input_type"] == "real_human_review_response"
    assert required_input["template_ref"] == (
        "docs/conversation-understanding/decision-work-brief-human-review-response-template-v0.json"
    )
    assert required_input["must_not_be_filled_by_codex"] is True
    assert "final_recommendation" in set(required_input["must_include"])


def test_runtime_and_customer_surface_remain_blocked() -> None:
    blocked = set(_review()["blocked_runtime_or_customer_surface"])

    assert "runtime_attachment" in blocked
    assert "customer_facing_presentation" in blocked
    assert "human_validation_claim" in blocked
    assert "product_proof_claim" in blocked
    assert "answer_quality_scoring" in blocked
    assert "agent_action_authorization" in blocked


def test_response_template_answers_remain_blank_not_codex_filled() -> None:
    template = _template()

    assert template["review_status"] == "not_started"
    assert template["human_review_completed"] is False
    assert template["reviewer_metadata"]["reviewer_id"] is None
    for case in template["cases"]:
        for field in CASE_ANSWER_FIELDS:
            assert case[field] == "not_reviewed"
        assert case["missing_context_needed"] == []
        assert case["what_helped"] == []
        assert case["what_confused"] == []
        assert case["what_should_change_before_user_surface"] == []
        assert case["reviewer_notes"] is None
    assert template["final_recommendation"]["recommended_outcome"] == "not_reviewed"
    assert template["final_recommendation"]["reviewer_summary"] is None


def test_decision_gate_uses_allowed_pause_value() -> None:
    review = _review()

    assert set(review["allowed_next_steps"]) == ALLOWED_NEXT_STEPS
    assert review["decision_gate"] in ALLOWED_NEXT_STEPS
    assert review["decision_gate"] == "pause_until_human_review_capacity"
    assert review["recommended_next_pr"] == (
        "PR154 Decision Work Brief Human Review Response Collection v0"
    )


def test_doc_says_this_is_not_human_review_or_completed_pilot() -> None:
    markdown = DOC_PATH.read_text(encoding="utf-8")

    assert "No real human response has been collected" in markdown
    assert "PR153 is not a completed human-review pilot" in markdown
    assert "Codex must not fill the response template" in markdown
    assert "Runtime and customer-facing use remain blocked" in markdown
    assert "pause_until_human_review_capacity" in markdown


def test_no_private_markers_or_authority_claims() -> None:
    text = "\n".join(
        [
            DOC_PATH.read_text(encoding="utf-8"),
            REVIEW_PATH.read_text(encoding="utf-8"),
            TEMPLATE_PATH.read_text(encoding="utf-8"),
            READINESS_GATE_PATH.read_text(encoding="utf-8"),
            SCAFFOLD_PATH.read_text(encoding="utf-8"),
        ]
    )

    for marker in PRIVACY_MARKERS:
        assert marker not in text
    for claim in FORBIDDEN_TRUE_CLAIMS:
        assert claim not in text


def test_product_delta_boundary_lint_passes_for_pr153_artifacts() -> None:
    report = lint_product_delta_paths(
        [DOC_PATH, REVIEW_PATH, TEMPLATE_PATH, READINESS_GATE_PATH, SCAFFOLD_PATH]
    )

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
