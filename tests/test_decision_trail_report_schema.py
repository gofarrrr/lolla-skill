from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    REPO_ROOT
    / "docs"
    / "conversation-understanding"
    / "decision-trail-report-v0.json"
)
PRD_PATH = (
    REPO_ROOT
    / "docs"
    / "conversation-understanding"
    / "decision-trail-report-prd-v0.md"
)

SCHEMA_VERSION = "lolla.decision_trail_report.v0"
SEMANTIC_SECTIONS = {
    "conversation_understanding_summary",
    "decision_question",
    "vanilla_likely_next_action",
    "revised_likely_next_action",
    "option_map",
    "constraints",
    "stakeholders",
    "values_or_priorities",
    "assistant_influence",
    "audit_pressure_summary",
    "structural_delta",
    "useful_noisy_friction",
    "lost_value",
    "unresolved_questions",
}
REQUIRED_STATUSES = {
    "not_supplied",
    "not_measured",
    "not_applicable",
    "available_from_structured_artifact",
    "available_from_review_artifact",
    "available_but_redacted_in_safe_mode",
    "available_in_private_artifact_not_exported",
    "requires_llm_interpretation",
    "unavailable_missing_artifact",
    "unavailable_malformed_artifact",
    "unclear",
}
REPORT_MODES = {
    "checked_in_safe_mode",
    "local_private_mode",
    "future_runtime_mode_not_implemented",
}
TRACE_STATUSES = {
    "not_used",
    "future_compatible",
    "experimental_mapping",
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


def _schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


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


def _resolve_ref(schema: dict[str, Any], ref: str) -> dict[str, Any]:
    assert ref.startswith("#/$defs/")
    return schema["$defs"][ref.removeprefix("#/$defs/")]


def test_schema_json_parses_and_uses_expected_version() -> None:
    schema = _schema()

    assert schema["$id"] == SCHEMA_VERSION
    assert schema["properties"]["schema_version"]["const"] == SCHEMA_VERSION
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"


def test_required_top_level_fields_match_pr86_contract() -> None:
    schema = _schema()
    required = set(schema["required"])

    assert required == {
        "schema_version",
        "report_metadata",
        "source_artifacts",
        "custody_flags",
        "trace_context",
        "report_mode",
        "conversation_understanding_summary",
        "decision_question",
        "vanilla_likely_next_action",
        "revised_likely_next_action",
        "option_map",
        "constraints",
        "stakeholders",
        "values_or_priorities",
        "assistant_influence",
        "audit_pressure_summary",
        "structural_delta",
        "useful_noisy_friction",
        "lost_value",
        "unresolved_questions",
        "artifact_health",
        "field_population_policy",
        "limitations",
        "non_claims",
    }


def test_status_report_mode_and_trace_vocabularies_are_explicit() -> None:
    schema = _schema()

    assert set(schema["$defs"]["status"]["enum"]) == REQUIRED_STATUSES
    assert set(schema["$defs"]["report_mode"]["enum"]) == REPORT_MODES
    assert set(schema["$defs"]["trace_status"]["enum"]) == TRACE_STATUSES


def test_every_semantic_section_uses_shared_population_contract() -> None:
    schema = _schema()
    semantic_def = schema["$defs"]["semantic_section"]
    required = set(semantic_def["required"])

    assert {
        "status",
        "source_status",
        "source_refs",
        "empty_meaning",
        "owner",
        "requires_llm_interpretation",
        "exporter_inferred_from_prose",
    }.issubset(required)
    assert {"required": ["value"]} in semantic_def["anyOf"]
    assert {"required": ["items"]} in semantic_def["anyOf"]
    assert semantic_def["properties"]["exporter_inferred_from_prose"]["const"] is False

    for section in SEMANTIC_SECTIONS:
        ref = schema["properties"][section]["$ref"]
        assert _resolve_ref(schema, ref) is semantic_def


def test_custody_flags_and_non_claims_remain_const_false() -> None:
    schema = _schema()
    custody = schema["$defs"]["custody_flags"]["properties"]
    non_claims = schema["$defs"]["non_claims"]["properties"]
    false_fields = {
        "raw_transcript_included",
        "raw_memo_included",
        "raw_revised_answer_included",
        "provider_text_included",
        "private_reasoning_included",
        "local_absolute_paths_included",
        "secrets_included",
        "raw_private_content_included",
        "archive_mutated",
        "runtime_invoked",
        "skill_invoked",
        "human_validated",
        "ground_truth",
        "judge_calibration_eligible",
        "product_proof",
        "answer_quality_scored",
        "llm_judge_used",
        "automatic_labels_created",
        "agent_action_authorized",
    }

    assert custody["model_calls"]["const"] == 0
    for field in false_fields:
        assert custody[field]["const"] is False

    for field in {
        "human_validated",
        "ground_truth",
        "judge_calibration_eligible",
        "product_proof",
        "answer_quality_scored",
        "llm_judge_used",
        "automatic_labels_created",
        "agent_action_authorized",
    }:
        assert non_claims[field]["const"] is False


def test_trace_context_is_future_compatible_without_dependency_adoption() -> None:
    schema = _schema()
    trace_context = schema["$defs"]["trace_context"]

    assert {
        "status",
        "source_refs",
        "external_trace_id",
        "otel_genai_semconv_status",
        "external_trace_dependency_added",
    }.issubset(trace_context["required"])
    assert trace_context["properties"]["external_trace_dependency_added"]["const"] is False
    assert trace_context["properties"]["status"]["$ref"] == "#/$defs/trace_status"
    assert (
        trace_context["properties"]["otel_genai_semconv_status"]["$ref"]
        == "#/$defs/trace_status"
    )


def test_source_artifacts_include_future_trace_mapping_fields() -> None:
    schema = _schema()
    source_artifact = schema["$defs"]["source_artifact"]

    assert {
        "activity_kind",
        "generated_by",
        "used_by",
        "raw_content_read",
        "content_included",
    }.issubset(source_artifact["required"])
    assert "future_decision_trail_export" in source_artifact["properties"]["activity_kind"]["enum"]


def test_schema_avoids_forbidden_authority_field_names() -> None:
    schema = _schema()
    keys = {key.lower() for key in _walk_keys(schema)}

    assert not keys.intersection(FORBIDDEN_FIELD_NAMES)
    assert not any(
        key.endswith("_score") and key != "not_a_score"
        for key in keys
    )


def test_pr86_artifacts_have_no_privacy_markers() -> None:
    text = "\n".join(
        [
            SCHEMA_PATH.read_text(encoding="utf-8"),
            PRD_PATH.read_text(encoding="utf-8"),
            Path(__file__).read_text(encoding="utf-8"),
        ]
    )

    for marker in PRIVACY_MARKERS:
        assert marker not in text


def test_product_delta_boundary_lint_accepts_pr86_artifacts() -> None:
    report = lint_product_delta_paths([PRD_PATH, SCHEMA_PATH])

    assert report["summary"]["blocking_error_count"] == 0
