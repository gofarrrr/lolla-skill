from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-brief-runtime-safe-brief-supply-plan-v0.md"
)
REVIEW_JSON_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-brief-runtime-safe-brief-supply-plan-v0/review.json"
)
FOLLOWUP_REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-brief-runtime-attached-v1-followup-plan-v0/review.json"
)
EXPECTED_SCHEMA = "lolla.decision_work_brief_runtime_safe_brief_supply_plan.v0"
ALLOWED_INPUT_STATUSES = {
    "available_from_completed_run_artifacts",
    "available_from_existing_offline_builder",
    "available_from_existing_checked_in_safe_example_only",
    "available_from_manual_operator_ref",
    "available_from_local_private_mode_only",
    "requires_future_llm_interpretation",
    "requires_future_triage_read",
    "not_available_yet",
}
REQUIRED_FALSE_FIELDS = {
    "human_validated",
    "human_review_completed",
    "product_proof",
    "runtime_invoked",
    "skill_invoked",
    "archive_mutated",
    "runtime_behavior_changed",
    "prompt_changed",
    "skill_files_changed",
    "answer_quality_scored",
    "agent_action_authorized",
    "automatic_action_authorized",
    "customer_readiness_claimed",
    "default_on_runtime_behavior_claimed",
    "lolla_improvement_proof_claimed",
}
REQUIRED_UNSAFE_INPUTS = {
    "raw_conversation_text",
    "private_ledgers",
    "provider_text",
    "local_absolute_paths",
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
    return json.loads(REVIEW_JSON_PATH.read_text(encoding="utf-8"))


def test_review_schema_and_conservative_flags() -> None:
    review = _review()

    assert review["schema_version"] == EXPECTED_SCHEMA
    assert review["model_calls"] == 0
    for field in REQUIRED_FALSE_FIELDS:
        assert review[field] is False


def test_required_inputs_are_classified_and_have_safe_defaults() -> None:
    review = _review()
    required_inputs = review["required_inputs"]

    assert len(required_inputs) >= 10
    for item in required_inputs:
        assert item["input_name"]
        assert item["current_status"] in ALLOWED_INPUT_STATUSES
        assert item["safe_default_policy"]
        assert isinstance(item["can_be_auto_supplied_now"], bool)
        assert isinstance(item["requires_llm_interpretation"], bool)
        assert isinstance(item["requires_local_private_context"], bool)
        assert isinstance(item["can_feed_user_receipt"], bool)
        assert isinstance(item["can_feed_agent_handoff"], bool)


def test_classification_covers_current_runtime_bundle_inputs() -> None:
    classification = _review()["input_classification"]

    for key in (
        "completed_run_directory",
        "rendered_brief_markdown",
        "enriched_brief_markdown",
        "automatic_triage_read_json",
        "attachment_status",
        "source_refs",
        "eligibility_blocker_state",
    ):
        assert key in classification
        assert classification[key] in ALLOWED_INPUT_STATUSES
    assert classification["automatic_triage_read_json"] == "requires_future_triage_read"
    assert classification["decision_work_brief_json"] == "not_available_yet"


def test_unsafe_auto_supply_inputs_are_explicit() -> None:
    unsafe = {item["input_name"] for item in _review()["unsafe_auto_supply_inputs"]}

    assert REQUIRED_UNSAFE_INPUTS <= unsafe
    assert "runtime_model_generated_interpretation" in unsafe


def test_selected_next_step_rejects_direct_runtime_interpretation() -> None:
    review = _review()

    assert review["selected_next_step"]
    assert review["selected_next_step"] != "direct_runtime_interpretation"
    assert review["selected_next_step"] == "build_safe_brief_supply_resolver_contract"
    assert review["recommended_next_pr"]
    assert "PR170" in review["recommended_next_pr"]
    direct_options = [
        option
        for option in review["options_considered"]
        if option["option"] == "direct_runtime_interpretation"
    ]
    assert direct_options
    assert direct_options[0]["selected"] is False


def test_review_keeps_runtime_hook_input_supply_limited() -> None:
    summary = _review()["current_input_supply_summary"]

    assert summary["safe_default_without_supplied_refs"] == "deferred"
    assert "safe_rendered_brief_not_supplied" in summary["deferred_reasons"]
    assert "runtime_specific_triage_read_not_supplied" in summary["deferred_reasons"]
    assert "correctly deferred" in _review()["strongest_unresolved_risk"]


def test_review_does_not_claim_customer_readiness_or_runtime_authority() -> None:
    rendered = REVIEW_JSON_PATH.read_text(encoding="utf-8")

    forbidden_fragments = (
        '"customer_readiness_claimed": true',
        '"default_on_runtime_behavior_claimed": true',
        '"human_validated": true',
        '"product_proof": true',
        '"answer_quality_scored": true',
        '"agent_action_authorized": true',
        '"automatic_action_authorized": true',
        "customer_ready",
        "default-on runtime behavior is implemented",
        "Lolla improved decisions as fact",
    )
    for fragment in forbidden_fragments:
        assert fragment not in rendered


def test_docs_and_review_have_no_private_markers() -> None:
    rendered = (
        DOC_PATH.read_text(encoding="utf-8")
        + "\n"
        + REVIEW_JSON_PATH.read_text(encoding="utf-8")
    )

    for marker in PRIVACY_MARKERS:
        assert marker not in rendered


def test_pr169_follows_pr168_gate() -> None:
    followup = json.loads(FOLLOWUP_REVIEW_PATH.read_text(encoding="utf-8"))

    assert followup["selected_next_step"] == "safe_brief_supply_planning"
    assert followup["recommended_next_pr"].startswith("PR169")


def test_pr169_docs_and_json_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths([DOC_PATH, REVIEW_JSON_PATH])

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
