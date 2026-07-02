from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-brief-runtime-safe-supply-resolver-contract-v0.md"
)
JSON_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-brief-runtime-safe-supply-resolver-contract-v0.json"
)
SUPPLY_PLAN_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-brief-runtime-safe-brief-supply-plan-v0.md"
)
EXPECTED_SCHEMA = (
    "lolla.decision_work_brief_runtime_safe_supply_resolver_contract.v0"
)
REQUIRED_MODES = {
    "disabled",
    "manual_ref_supply_only",
    "checked_in_safe_case_registry",
    "archive_local_safe_resolver",
    "offline_interpretation_queue",
    "local_private_operator_mode",
    "future_direct_runtime_interpretation_not_allowed",
}
REQUIRED_STATUSES = {
    "not_requested",
    "no_safe_inputs",
    "resolved",
    "partially_resolved",
    "deferred_missing_brief",
    "deferred_missing_enriched_brief",
    "deferred_missing_interpretation_read",
    "deferred_missing_triage_read",
    "blocked_privacy_risk",
    "blocked_unsafe_path",
    "blocked_untrusted_source",
    "blocked_schema_invalid",
    "blocked_direct_runtime_interpretation",
    "queued_for_offline_interpretation",
    "local_private_operator_required",
}
REQUIRED_INPUT_TYPES = {
    "completed_run_dir_ref",
    "decision_work_brief_json_ref",
    "rendered_brief_markdown_ref",
    "enriched_brief_markdown_ref",
    "interpretation_read_json_ref",
    "automatic_triage_packet_json_ref",
    "automatic_triage_read_json_ref",
    "source_refs",
    "eligibility_result_ref",
    "attachment_status_ref",
    "user_receipt_ref",
    "agent_handoff_ref",
}
REQUIRED_BLOCKED_INPUTS = {
    "raw_conversation_text",
    "raw_revised_answer_text",
    "raw_memo_text",
    "provider_text",
    "private_ledgers",
    "local_absolute_paths",
    "secrets",
    "hidden_chain_of_thought_style_material",
    "runtime_model_generated_interpretation",
    "action_authorization",
    "score_or_approval_labels",
}
REQUIRED_FALSE_FLAGS = {
    "human_validated",
    "human_review_completed",
    "product_proof",
    "runtime_invoked",
    "runtime_behavior_changed",
    "skill_invoked",
    "archive_mutated",
    "prompt_changed",
    "skill_files_changed",
    "answer_quality_scored",
    "agent_action_authorized",
    "automatic_action_authorized",
    "raw_private_content_included",
    "provider_text_included",
    "local_absolute_paths_included",
}
REQUIRED_NON_CLAIMS = {
    "not_customer_readiness",
    "not_product_proof",
    "not_human_validation",
    "not_advice_correctness",
    "not_answer_quality_scoring",
    "not_agent_action_authorization",
    "not_automatic_action_authorization",
    "not_lolla_improvement_proof",
    "not_default_on_runtime_behavior",
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


def _contract() -> dict[str, Any]:
    return json.loads(JSON_PATH.read_text(encoding="utf-8"))


def test_contract_json_parses_and_schema_version_is_expected() -> None:
    contract = _contract()

    assert contract["schema_version"] == EXPECTED_SCHEMA
    assert contract["contract_metadata"]["status"] == "contract_only"
    assert contract["contract_metadata"]["resolver_implemented_here"] is False
    assert contract["contract_metadata"]["runtime_behavior_changed"] is False


def test_required_resolver_modes_are_present_and_direct_runtime_is_blocked() -> None:
    modes = {item["mode"]: item for item in _contract()["resolver_modes"]}

    assert REQUIRED_MODES <= set(modes)
    assert modes["disabled"]["default"] is True
    direct_runtime = modes["future_direct_runtime_interpretation_not_allowed"]
    assert direct_runtime["allowed"] is False
    assert direct_runtime["blocked_status"] == "blocked_direct_runtime_interpretation"
    assert direct_runtime["can_feed_runtime_bundle"] is False


def test_required_resolver_statuses_are_present() -> None:
    statuses = {item["status"] for item in _contract()["resolver_statuses"]}

    assert REQUIRED_STATUSES <= statuses


def test_required_input_types_have_supply_policies() -> None:
    inputs = {item["input_name"]: item for item in _contract()["input_types"]}

    assert REQUIRED_INPUT_TYPES <= set(inputs)
    for input_name in REQUIRED_INPUT_TYPES:
        item = inputs[input_name]
        assert isinstance(item["required_for_user_receipt"], bool)
        assert isinstance(item["required_for_full_brief"], bool)
        assert isinstance(item["required_for_agent_handoff"], bool)
        assert isinstance(item["required_for_triage"], bool)
        assert item["allowed_source_modes"]
        assert item["safe_default_policy"]
        assert item["local_private_policy"]
        assert item["checked_in_safe_policy"]
        assert isinstance(item["can_be_absent"], bool)
        assert item["absence_status"] in REQUIRED_STATUSES
        assert item["privacy_risk"]
        assert isinstance(item["requires_llm_interpretation"], bool)
        assert isinstance(item["can_feed_runtime_bundle"], bool)


def test_unsafe_blocked_inputs_are_explicit() -> None:
    blocked = {item["input_name"]: item for item in _contract()["blocked_inputs"]}

    assert REQUIRED_BLOCKED_INPUTS <= set(blocked)
    for input_name in REQUIRED_BLOCKED_INPUTS:
        assert blocked[input_name]["must_never_auto_supply"] is True


def test_output_shape_is_bundle_feedability_contract_not_interpretation() -> None:
    output_shape = _contract()["output_shape"]

    for field in (
        "resolved_inputs",
        "deferred_inputs",
        "blocked_inputs",
        "unsafe_inputs_excluded",
        "feeds_runtime_bundle",
        "reason_if_not_feedable",
    ):
        assert field in output_shape["required_fields"]
    assert "no_runtime_model_generated_interpretation" in (
        output_shape["feeds_runtime_bundle_true_requires"]
    )
    assert "blocked_direct_runtime_interpretation" in (
        output_shape["reason_if_not_feedable_required_when"]
    )


def test_custody_flags_are_conservative() -> None:
    custody = _contract()["custody_flags"]

    assert custody["model_calls"] == 0
    for field in REQUIRED_FALSE_FLAGS:
        assert custody[field] is False
    assert custody["resolver_contract_only"] is True


def test_non_claims_prohibit_product_and_runtime_authority_claims() -> None:
    contract = _contract()
    non_claims = set(contract["non_claims"])
    rendered = JSON_PATH.read_text(encoding="utf-8") + "\n" + DOC_PATH.read_text(
        encoding="utf-8"
    )

    assert REQUIRED_NON_CLAIMS <= non_claims
    for forbidden in (
        '"human_validated": true',
        '"product_proof": true',
        '"answer_quality_scored": true',
        '"agent_action_authorized": true',
        '"automatic_action_authorized": true',
        "customer_ready",
        "advice is correct",
        "Lolla improved decisions as fact",
        "safe_for_agent_use",
    ):
        assert forbidden not in rendered


def test_next_recommended_pr_does_not_recommend_default_on_runtime_behavior() -> None:
    next_pr = _contract()["next_recommended_pr"]

    assert "PR171" in next_pr["pr"]
    assert next_pr["must_not_recommend_default_on_runtime_behavior"] is True
    assert next_pr["runtime_behavior_change_allowed"] is False
    assert "do_not_change_runtime_hook_behavior" in next_pr["implementation_boundary"]


def test_docs_and_json_have_no_private_markers() -> None:
    rendered = JSON_PATH.read_text(encoding="utf-8") + "\n" + DOC_PATH.read_text(
        encoding="utf-8"
    )

    for marker in PRIVACY_MARKERS:
        assert marker not in rendered


def test_contract_docs_and_json_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths([DOC_PATH, JSON_PATH, SUPPLY_PLAN_PATH])

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
