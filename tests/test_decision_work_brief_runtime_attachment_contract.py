from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-runtime-attachment-contract-v0.md"
)
JSON_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-runtime-attachment-contract-v0.json"
)
PR159_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-runtime-attachment-prd-v0.md"
)
SCHEMA_VERSION = "lolla.decision_work_brief_runtime_attachment_contract.v0"
REQUIRED_MODES = {
    "disabled",
    "manual_post_archive",
    "flagged_post_archive",
    "future_default_not_implemented",
}
REQUIRED_STATES = {
    "not_requested",
    "not_eligible",
    "blocked",
    "deferred",
    "generated",
    "generated_agent_only",
    "failed_closed",
}
REQUIRED_HARD_BLOCKERS = {
    "incomplete_run_artifacts",
    "archive_not_finalized",
    "missing_revised_answer",
    "missing_required_structured_artifacts",
    "malformed_json",
    "failed_hygiene",
    "failed_boundary_lint",
    "unsafe_output_path",
    "source_refs_unresolved",
    "privacy_marker_or_raw_private_export_risk",
    "schema_validation_failure",
    "attempted_model_or_provider_invocation",
    "attempted_runtime_invocation_during_generation",
    "attempted_action_authorization_or_scoring",
}
REQUIRED_SOFT_BLOCKERS = {
    "source_depth_too_thin",
    "high_overtrust_risk",
    "private_context_required",
    "domain_review_recommended",
    "legal_or_compliance_review_recommended",
    "medical_or_financial_review_recommended",
    "governance_or_employment_review_recommended",
    "safety_review_recommended",
    "relationship_or_political_sensitivity",
    "unresolved_lost_value_risk",
    "agent_inspection_only",
}
REQUIRED_FALSE_FLAGS = {
    "human_validated",
    "human_review_completed",
    "product_proof",
    "runtime_invoked",
    "skill_invoked",
    "archive_mutated",
    "answer_quality_scored",
    "agent_action_authorized",
    "automatic_action_authorized",
    "raw_private_content_included",
    "provider_text_included",
    "local_absolute_paths_included",
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


def test_contract_schema_and_pr159_ref() -> None:
    contract = _contract()

    assert contract["schema_version"] == SCHEMA_VERSION
    assert contract["contract_metadata"]["status"] == "contract_only"
    assert contract["contract_metadata"]["decision_gate"] == (
        "proceed_to_runtime_sidecar_contract"
    )
    assert contract["contract_metadata"]["source_prd_ref"] == str(
        PR159_PATH.relative_to(REPO_ROOT)
    )
    assert PR159_PATH.exists()
    assert "runtime_hook" in contract["contract_metadata"]["not_implemented_here"]


def test_modes_states_and_default_off_policy() -> None:
    contract = _contract()
    modes = {item["mode"] for item in contract["attachment_modes"]}

    assert modes == REQUIRED_MODES
    assert {item["mode"] for item in contract["attachment_modes"] if item["default"]} == {
        "disabled"
    }
    assert set(contract["attachment_states"]) == REQUIRED_STATES
    assert contract["default_off_requirement"]["required"] is True
    assert contract["default_off_requirement"]["flagged_mode_must_default_off"] is True
    assert contract["post_archive_only_requirement"]["required"] is True
    assert (
        contract["post_archive_only_requirement"][
            "must_not_run_during_revised_answer_generation"
        ]
        is True
    )


def test_user_receipt_and_handoff_shapes_are_conservative() -> None:
    contract = _contract()
    receipt = contract["user_receipt_shape"]

    assert receipt["must_be_short"] is True
    assert receipt["must_include_non_claim"] is True
    assert receipt["must_not_render_full_brief_by_default"] is True
    assert receipt["must_not_include_quality_rating"] is True
    assert receipt["must_not_authorize_action"] is True
    assert "main_caveat" in receipt["required_fields"]
    assert "blocked_or_deferred_reason" in receipt["required_fields"]

    handoff = contract["agent_handoff_refs"]
    assert handoff["agent_action_authorized_value"] is False
    assert "privacy_redaction_status" in handoff["required_fields"]
    assert "blocked_or_deferred_state" in handoff["required_fields"]


def test_blocker_vocabularies_cover_required_cases() -> None:
    contract = _contract()

    assert REQUIRED_HARD_BLOCKERS <= set(contract["hard_blocker_vocabulary"])
    assert REQUIRED_SOFT_BLOCKERS <= set(contract["soft_triage_blocker_vocabulary"])


def test_custody_and_privacy_flags_are_conservative() -> None:
    contract = _contract()
    custody = contract["custody_flags"]
    privacy = contract["privacy_export_policy"]

    assert custody["model_calls"] == 0
    for field in REQUIRED_FALSE_FLAGS:
        assert custody[field] is False
    assert custody["runtime_attachment_contract_only"] is True
    assert privacy["default_mode"] == "checked_in_safe_refs_only"
    assert privacy["raw_conversation_text_exported_by_default"] is False
    assert privacy["raw_revised_answer_text_exported_by_default"] is False
    assert privacy["raw_memo_text_exported_by_default"] is False
    assert privacy["provider_text_exported_by_default"] is False
    assert privacy["private_ledgers_exported_by_default"] is False
    assert privacy["private_material_may_be_referenced_as_availability_status_only"] is True


def test_non_claims_and_no_private_markers() -> None:
    text = DOC_PATH.read_text(encoding="utf-8") + "\n" + JSON_PATH.read_text(
        encoding="utf-8"
    )
    contract = _contract()

    assert "triage_is_routing_not_scoring" in contract["non_claims"]
    assert "not_agent_action_authorization" in contract["non_claims"]
    assert "not_product_proof" in contract["non_claims"]
    for marker in PRIVACY_MARKERS:
        assert marker not in text
    for forbidden in (
        '"human_validated": true',
        '"product_proof": true',
        '"answer_quality_scored": true',
        '"agent_action_authorized": true',
        "safe_for_agent_use",
    ):
        assert forbidden not in text


def test_contract_docs_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths([DOC_PATH, JSON_PATH, PR159_PATH])

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
