from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-trail-specialist-contracts-v0.json"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-trail-specialist-contracts-v0.md"
)

EXPECTED_SCHEMA_VERSION = "lolla.decision_trail_specialist_contracts.v0"
EXPECTED_ROLES = {
    "conversation_shape_reader",
    "likely_action_reader",
    "friction_lost_value_reader",
    "conservative_fan_in_reader",
}
REQUIRED_SHARED_FIELDS = {
    "specialist_role",
    "contract_version",
    "input_mode",
    "allowed_input_refs",
    "read_status",
    "source_refs",
    "source_status",
    "uncertainty",
    "evidence_strength",
    "fields",
    "limitations",
    "non_claims",
    "boundary",
}
FORBIDDEN_AUTHORITY_FIELDS = {
    "quality_score",
    "answer_quality_score",
    "improvement_score",
    "judge_score",
    "winner",
    "approved",
    "certified",
    "pass_fail",
    "safe" + "_for_" + "agent" + "_use",
}


def _schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _example() -> dict[str, Any]:
    return _schema()["examples"][0]


def _walk_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            keys.add(str(key))
            keys.update(_walk_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(_walk_keys(child))
    return keys


def _walk_strings(value: Any) -> list[str]:
    strings: list[str] = []
    if isinstance(value, str):
        strings.append(value)
    elif isinstance(value, dict):
        for child in value.values():
            strings.extend(_walk_strings(child))
    elif isinstance(value, list):
        for child in value:
            strings.extend(_walk_strings(child))
    return strings


def test_schema_json_parses_and_has_expected_version() -> None:
    schema = _schema()

    assert schema["$id"] == EXPECTED_SCHEMA_VERSION
    assert schema["properties"]["schema_version"]["const"] == EXPECTED_SCHEMA_VERSION
    assert schema["properties"]["contract_family"]["const"] == (
        "decision_trail_specialist_contracts"
    )
    assert schema["properties"]["contract_status"]["const"] == "docs_schema_only"


def test_exactly_four_specialist_roles_are_required() -> None:
    role_schema = _schema()["properties"]["specialist_roles"]

    assert set(role_schema["required"]) == EXPECTED_ROLES
    assert set(role_schema["properties"]) == EXPECTED_ROLES
    assert set(_example()["specialist_roles"]) == EXPECTED_ROLES


def test_specialist_roles_cover_pr89_missing_fields() -> None:
    roles = _example()["specialist_roles"]

    assert {
        "decision_question",
        "live_options",
        "option_status",
        "constraints",
        "stakeholders",
        "values_or_priorities",
        "assistant_influence",
        "assistant_influence_source_status",
        "dropped_threads",
        "unresolved_questions",
        "uncertainty",
        "source_scope_and_truncation_impact",
    } <= set(roles["conversation_shape_reader"]["covered_fields"])
    assert {
        "vanilla_likely_next_action",
        "revised_likely_next_action",
        "vanilla_overlap_read",
        "action_delta",
        "threshold_delta",
        "sequence_delta",
        "evidence_gate_delta",
        "stop_rule_delta",
        "uncertainty",
        "source_scope_and_truncation_impact",
    } <= set(roles["likely_action_reader"]["covered_fields"])
    assert {
        "useful_friction",
        "noisy_friction",
        "missing_friction",
        "lost_value",
        "lost_value_severity_read",
        "severity_source_status",
        "value_overwrite_risk",
        "momentum_or_simplicity_loss",
        "overcaution_or_diligence_theater",
        "uncertainty",
        "source_scope_and_truncation_impact",
    } <= set(roles["friction_lost_value_reader"]["covered_fields"])


def test_every_specialist_contract_requires_shared_custody_fields() -> None:
    for role in _example()["specialist_roles"].values():
        assert REQUIRED_SHARED_FIELDS <= set(role["shared_required_fields"])
        assert "source_refs" in role["must_preserve"] or role[
            "specialist_role"
        ] == "conservative_fan_in_reader"


def test_boundary_defaults_are_false_or_zero_everywhere() -> None:
    root_boundary = _example()["boundary_defaults"]

    assert root_boundary["model_calls"] == 0
    assert all(value is False for key, value in root_boundary.items() if key != "model_calls")

    for role in _example()["specialist_roles"].values():
        boundary = role["boundary"]
        assert boundary["model_calls"] == 0
        assert all(value is False for key, value in boundary.items() if key != "model_calls")


def test_input_modes_record_pr95_private_packet_mode_and_runtime_mode_boundary() -> None:
    modes = _example()["input_modes"]

    assert modes["allowed"] == [
        "checked_in_safe_mode",
        "local_private_mode",
        "future_runtime_mode_not_implemented",
    ]
    assert modes["local_private_mode_status"] == "implemented_for_packet_builder_pr95"
    assert modes["future_runtime_mode_status"] == "reserved_not_implemented"
    assert {
        "raw_transcript",
        "raw_memo",
        "raw_revised_answer",
        "provider_text",
        "private_ledgers",
        "local_absolute_paths",
        "secrets",
        "private_local_content",
    } <= set(modes["checked_in_safe_mode_excludes"])


def test_status_vocabulary_preserves_missingness_and_redaction() -> None:
    vocabulary = _example()["status_vocabulary"]

    assert {
        "not_supplied",
        "explicit_in_source",
        "inferred_from_source",
        "unclear",
        "contradicted",
        "requires_private_context",
        "available_but_redacted_in_safe_mode",
        "available_in_private_artifact_not_exported",
        "unavailable_missing_artifact",
        "unavailable_malformed_artifact",
    } <= set(vocabulary["field_status"])


def test_conservative_fan_in_forbids_score_vote_winner_and_correctness_from_agreement() -> None:
    fan_in = _example()["specialist_roles"]["conservative_fan_in_reader"]

    assert {
        "downgrade_triggers",
        "not_ready_reason",
        "source_scope_and_truncation_impact",
    } <= set(fan_in["covered_fields"])
    assert {
        "vote",
        "average",
        "score",
        "certify",
        "approve",
        "choose_winner",
        "correctness_from_agreement",
        "decision_quality_claim",
    } == set(fan_in["fan_in_forbidden_actions"])
    assert {
        "structural_delta_strong_but_lost_value_unresolved",
        "likely_action_changed_but_values_unclear",
        "useful_friction_with_momentum_loss",
        "checked_in_safe_context_too_thin_for_assistant_influence",
    } <= set(fan_in["tensions_to_preserve"])


def test_schema_avoids_forbidden_authority_fields_and_claim_language() -> None:
    schema = _schema()
    text = SCHEMA_PATH.read_text(encoding="utf-8")
    keys = _walk_keys(schema)
    strings = "\n".join(_walk_strings(schema))

    assert not (FORBIDDEN_AUTHORITY_FIELDS & keys)
    for field in FORBIDDEN_AUTHORITY_FIELDS:
        assert f'"{field}"' not in text
    assert "not_product_proof" in strings
    assert "not_human_review" in strings
    assert "not_answer_quality_scoring" in strings


def test_pr78_lint_passes_new_contract_artifacts() -> None:
    report = lint_product_delta_paths([DOC_PATH, SCHEMA_PATH])

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
