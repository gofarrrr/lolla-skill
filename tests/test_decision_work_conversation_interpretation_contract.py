from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-conversation-interpretation-contract-v0.json"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-conversation-interpretation-contract-v0.md"
)
PR127_REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-conversation-interpretation-gap-map-v0/review.json"
)
PR127_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-conversation-interpretation-gap-map-v0.md"
)

SCHEMA_VERSION = "lolla.decision_work_conversation_interpretation_contract.v0"
REQUIRED_FIELD_GROUPS = {
    "decision_shape",
    "options_and_paths",
    "conversation_process",
    "provided_context_and_evidence",
    "stakeholders_and_values",
    "constraints_and_unknowns",
    "audit_pressure_and_change",
    "losses_and_overcorrection",
    "evidence_and_custody",
    "handoff_for_brief",
    "handoff_for_agent_inspection",
}
REQUIRED_FIELD_KEYS = {
    "field_name",
    "purpose",
    "owner",
    "interpretation_required",
    "deterministic_allowed",
    "human_review_required_when",
    "source_refs_required",
    "empty_meaning",
    "privacy_handling",
    "checked_in_safe_policy",
    "local_private_policy",
    "should_feed_brief",
    "should_feed_agent_inspection",
    "must_not_be_used_as_quality_label",
}
ALLOWED_OWNERS = {
    "llm_interpretation",
    "deterministic_custody",
    "human_review",
    "mixed_llm_and_deterministic_custody",
}
ALLOWED_INTERPRETATION_REQUIRED = {"yes", "no", "conditional"}
ALLOWED_PRIVACY_HANDLING = {
    "safe_checked_in_summary_allowed",
    "local_private_only",
    "redacted_in_checked_in_safe_mode",
    "do_not_export",
    "metadata_only",
}
REQUIRED_SOURCE_STATUS = {
    "available_from_checked_in_safe_artifact",
    "available_from_local_private_artifact",
    "available_but_redacted",
    "missing_artifact",
    "malformed_artifact",
    "not_captured",
    "requires_llm_interpretation",
    "requires_human_review",
    "unclear",
}
REQUIRED_INTERPRETATION_STATUS = {
    "not_interpreted",
    "interpreted_by_llm_provisional",
    "interpreted_by_human",
    "contradicted",
    "uncertain",
    "insufficient_context",
    "not_applicable",
}
REQUIRED_NON_CLAIMS = {
    "not_runtime_extraction",
    "not_product_proof",
    "not_human_validated",
    "not_answer_quality_score",
    "not_agent_action_authorization",
    "not_correctness_proof",
    "not_a_broad_judge",
    "not_safe_for_agent_action",
    "clean_artifacts_do_not_imply_good_advice",
    "interpretation_contract_does_not_generate_briefs",
}
REQUIRED_CUSTODY_FALSE_FIELDS = {
    "runtime_invoked",
    "skill_invoked",
    "archive_mutated",
    "human_validated",
    "product_proof",
    "answer_quality_scored",
    "agent_action_authorized",
    "raw_private_content_included",
    "provider_text_included",
    "local_absolute_paths_included",
}
FORBIDDEN_FIELD_NAMES = {
    "safe_for_" + "agent_use",
    "approved",
    "approval",
    "approval_status",
    "certified",
    "passed",
    "pass",
    "pass_fail",
    "score",
    "quality_score",
    "answer_quality_score",
    "improvement_score",
    "decision_quality_score",
    "confidence_score",
    "judge_score",
    "rating",
    "winner",
    "llm_judge_winner",
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
RUNTIME_INTEGRATION_FILES = (
    REPO_ROOT / "engine/system_b/decision_work_brief_runtime.py",
    REPO_ROOT / "scripts/evals/integrate_decision_work_brief_runtime.py",
)


def _contract() -> dict[str, Any]:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def _all_fields(contract: dict[str, Any]) -> list[dict[str, Any]]:
    fields: list[dict[str, Any]] = []
    for group_fields in contract["field_groups"].values():
        fields.extend(group_fields)
    return fields


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


def test_contract_json_has_expected_schema_and_top_level_fields() -> None:
    contract = _contract()

    assert contract["schema_version"] == SCHEMA_VERSION
    assert {
        "schema_version",
        "contract_metadata",
        "custody_policy",
        "field_groups",
        "source_status_vocabulary",
        "interpretation_status_vocabulary",
        "privacy_mode_vocabulary",
        "deterministic_non_claims",
        "future_use_notes",
    } <= set(contract)


def test_required_field_groups_exist() -> None:
    assert set(_contract()["field_groups"]) == REQUIRED_FIELD_GROUPS


def test_every_field_defines_required_contract_keys_and_allowed_values() -> None:
    fields = _all_fields(_contract())

    assert fields
    for field in fields:
        assert REQUIRED_FIELD_KEYS <= set(field)
        assert field["owner"] in ALLOWED_OWNERS
        assert field["interpretation_required"] in ALLOWED_INTERPRETATION_REQUIRED
        assert field["privacy_handling"] in ALLOWED_PRIVACY_HANDLING
        assert isinstance(field["deterministic_allowed"], bool)
        assert isinstance(field["source_refs_required"], bool)
        assert isinstance(field["should_feed_brief"], bool)
        assert isinstance(field["should_feed_agent_inspection"], bool)
        assert field["must_not_be_used_as_quality_label"] is True


def test_source_and_interpretation_vocabularies_include_required_statuses() -> None:
    contract = _contract()

    assert REQUIRED_SOURCE_STATUS <= set(contract["source_status_vocabulary"])
    assert REQUIRED_INTERPRETATION_STATUS <= set(
        contract["interpretation_status_vocabulary"]
    )
    assert set(contract["privacy_mode_vocabulary"]) == ALLOWED_PRIVACY_HANDLING


def test_custody_policy_and_non_claims_are_conservative() -> None:
    contract = _contract()
    custody = contract["custody_policy"]

    for field in REQUIRED_CUSTODY_FALSE_FIELDS:
        assert custody[field] is False
    assert custody["model_calls"] == 0
    assert REQUIRED_NON_CLAIMS <= set(contract["deterministic_non_claims"])
    assert contract["future_use_notes"]["runtime_integration_implemented"] is False
    assert contract["future_use_notes"]["extractor_implemented"] is False
    assert contract["future_use_notes"]["prompt_change_implemented"] is False


def test_pr128_follows_pr127_gate() -> None:
    pr127 = json.loads(PR127_REVIEW_PATH.read_text(encoding="utf-8"))

    assert pr127["recommended_next_step"]["outcome"] == (
        "define_interpretation_target_contract"
    )
    assert _contract()["contract_metadata"]["triggering_gap_map_ref"] == (
        "reviews/codex-assisted/decision-work-brief-conversation-interpretation-gap-map-v0/review.json"
    )


def test_checked_in_files_have_no_local_paths_or_privacy_markers() -> None:
    text = "\n".join(
        [
            CONTRACT_PATH.read_text(encoding="utf-8"),
            DOC_PATH.read_text(encoding="utf-8"),
            Path(__file__).read_text(encoding="utf-8"),
        ]
    )

    assert "/" + "tmp" + "/" not in text
    for marker in PRIVACY_MARKERS:
        assert marker not in text


def test_forbidden_authority_or_score_fields_do_not_appear() -> None:
    keys = {key.lower() for key in _walk_keys(_contract())}

    assert not keys.intersection(FORBIDDEN_FIELD_NAMES)
    assert not any(key.endswith("_score") and key != "not_a_score" for key in keys)


def test_no_runtime_integration_or_skill_surface_changes() -> None:
    for path in RUNTIME_INTEGRATION_FILES:
        assert not path.exists()

    result = subprocess.run(
        ["git", "status", "--short", "--", "SKILL.md", "scripts/skill"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == ""


def test_pr128_artifacts_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths([DOC_PATH, CONTRACT_PATH, PR127_DOC_PATH, PR127_REVIEW_PATH])

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
