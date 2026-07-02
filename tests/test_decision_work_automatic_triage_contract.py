from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-automatic-triage-contract-v0.md"
)
JSON_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-automatic-triage-contract-v0.json"
)
PR153_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-human-review-awaiting-response-gate-v0.md"
)
SCHEMA_VERSION = "lolla.decision_work_automatic_triage_contract.v0"
REQUIRED_TOP_LEVEL = {
    "schema_version",
    "triage_metadata",
    "input_refs",
    "custody_flags",
    "triage_scope",
    "triage_categories",
    "triage_fields",
    "routing_outputs",
    "escalation_outputs",
    "agent_inspection_outputs",
    "brief_surface_outputs",
    "human_calibration_outputs",
    "non_claims",
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
}
REQUIRED_CATEGORIES = {
    "normal_brief_candidate",
    "agent_inspection_only",
    "source_depth_insufficient",
    "private_context_required",
    "high_overtrust_risk",
    "human_calibration_recommended",
    "domain_review_recommended",
    "legal_or_compliance_review_recommended",
    "relationship_or_political_risk",
    "lost_value_risk",
    "missing_decision_context",
    "interpretation_conflict",
    "too_thin_to_summarize",
    "not_ready_for_user_surface",
    "runtime_attachment_blocked",
}
REQUIRED_FIELD_GROUPS = {
    "decision_surface_readiness",
    "evidence_depth",
    "source_status",
    "interpretation_status",
    "uncertainty_visibility",
    "overtrust_risk",
    "high_stakes_domain_risk",
    "lost_value_or_overcorrection_risk",
    "private_context_dependency",
    "agent_inspection_readiness",
    "user_surface_readiness",
    "runtime_attachment_readiness",
    "human_calibration_need",
}
STATUS_VOCABULARY = {
    "not_evaluated",
    "clear",
    "partial",
    "unclear",
    "insufficient_source",
    "private_context_required",
    "human_calibration_required",
    "domain_review_required",
    "blocked",
    "not_applicable",
}
OWNER_VOCABULARY = {
    "llm_interpretation",
    "deterministic_validation",
    "human_calibration",
    "mixed",
}
ROUTE_VALUES = {
    "allowed_with_caveats",
    "agent_only",
    "requires_human_calibration",
    "requires_domain_review",
    "blocked_source_depth",
    "blocked_overtrust_risk",
    "blocked_runtime",
    "not_ready",
    "not_evaluated",
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
FORBIDDEN_AUTHORITY_CLAIMS = (
    "product_proof" + ": true",
    "human_validated" + ": true",
    "answer_quality_scored" + ": true",
    "agent_action_authorized" + ": true",
    "automatic_action_authorized" + ": true",
    "approval_score",
    "winner",
    "certified",
)


def _contract() -> dict[str, Any]:
    return json.loads(JSON_PATH.read_text(encoding="utf-8"))


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


def test_contract_json_schema_and_top_level_shape() -> None:
    contract = _contract()

    assert contract["schema_version"] == SCHEMA_VERSION
    assert REQUIRED_TOP_LEVEL <= set(contract)
    assert contract["triage_metadata"]["contract_mode"] == "docs_schema_tests_only"
    assert "triage_packet_builder" in contract["triage_metadata"]["not_implemented_here"]
    assert "model_calls" in contract["triage_metadata"]["not_implemented_here"]


def test_input_refs_resolve() -> None:
    contract = _contract()

    assert (REPO_ROOT / contract["input_refs"]["human_review_awaiting_response_gate_ref"]) == (
        PR153_DOC_PATH
    )
    for ref in _collect_repo_refs(contract):
        assert (REPO_ROOT / ref).exists(), ref


def test_custody_flags_are_conservative() -> None:
    custody = _contract()["custody_flags"]

    assert custody["model_calls"] == 0
    for field in REQUIRED_FALSE_FLAGS:
        assert custody[field] is False
    assert custody["triage_contract_only"] is True


def test_categories_cover_required_routing_and_escalation_cases() -> None:
    categories = {item["category"] for item in _contract()["triage_categories"]}

    assert REQUIRED_CATEGORIES <= categories
    for item in _contract()["triage_categories"]:
        assert item["must_not_be_used_as_quality_label"] is True
        assert item["purpose"]


def test_every_triage_field_has_required_contract_shape() -> None:
    contract = _contract()
    field_groups = {field["field_group"] for field in contract["triage_fields"]}

    assert REQUIRED_FIELD_GROUPS <= field_groups
    for field in contract["triage_fields"]:
        assert field["owner"] in OWNER_VOCABULARY
        assert set(field["status_vocabulary"]) == STATUS_VOCABULARY
        assert field["allowed_values"]
        assert field["source_refs_required"] is True
        assert field["uncertainty_required"] is True
        assert field["privacy_handling"]
        assert isinstance(field["can_feed_user_surface"], bool)
        assert isinstance(field["can_feed_agent_inspection"], bool)
        assert isinstance(field["blocks_runtime_attachment"], bool)
        assert isinstance(field["requires_human_or_domain_review"], bool)
        assert field["must_not_be_used_as_quality_label"] is True


def test_route_values_are_constrained() -> None:
    contract = _contract()

    assert set(contract["route_value_vocabulary"]) == ROUTE_VALUES
    for route_name, route in contract["routing_outputs"].items():
        assert route_name.endswith("_route")
        assert set(route["allowed_route_values"]) == ROUTE_VALUES
        assert route["source_refs_required"] is True
        assert route["uncertainty_required"] is True
        assert route["must_not_authorize_action"] is True


def test_human_review_is_calibration_not_normal_operating_layer() -> None:
    contract = _contract()
    calibration = contract["human_calibration_outputs"]
    doc = DOC_PATH.read_text(encoding="utf-8")

    assert calibration["calibration_role"] == (
        "human_review_calibrates_automatic_triage_not_normal_per_run_operating_layer"
    )
    assert calibration["must_not_treat_absent_human_response_as_validation"] is True
    assert calibration["must_not_turn_human_review_into_required_normal_path_for_every_run"] is True
    assert "Human review is a calibration layer" in doc
    assert "not the intended normal operating mode" in doc


def test_non_claims_block_score_approval_quality_and_authority() -> None:
    contract = _contract()
    non_claims = set(contract["non_claims"])

    assert "triage_is_not_a_score" in non_claims
    assert "triage_is_not_approval" in non_claims
    assert "triage_is_not_certification" in non_claims
    assert "triage_is_not_answer_quality_grading" in non_claims
    assert "triage_is_not_product_proof" in non_claims
    assert "triage_is_not_human_validation" in non_claims
    assert "triage_does_not_authorize_agent_action" in non_claims
    assert "triage_does_not_authorize_automatic_action" in non_claims
    assert "triage_does_not_prove_lolla_improved_the_decision" in non_claims


def test_no_private_markers_or_local_absolute_paths() -> None:
    text = "\n".join(
        [
            DOC_PATH.read_text(encoding="utf-8"),
            JSON_PATH.read_text(encoding="utf-8"),
            PR153_DOC_PATH.read_text(encoding="utf-8"),
        ]
    )

    for marker in PRIVACY_MARKERS:
        assert marker not in text
    for claim in FORBIDDEN_AUTHORITY_CLAIMS:
        assert claim not in text


def test_product_delta_boundary_lint_passes_for_pr154_artifacts() -> None:
    report = lint_product_delta_paths([DOC_PATH, JSON_PATH, PR153_DOC_PATH])

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
