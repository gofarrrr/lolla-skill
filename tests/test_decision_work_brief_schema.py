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
    / "decision-work-brief-v0.json"
)
SCHEMA_DOC_PATH = (
    REPO_ROOT
    / "docs"
    / "conversation-understanding"
    / "decision-work-brief-schema-v0.md"
)
PRD_PATH = (
    REPO_ROOT
    / "docs"
    / "conversation-understanding"
    / "decision-work-brief-prd-v0.md"
)

SCHEMA_VERSION = "lolla.decision_work_brief.v0"
REQUIRED_TOP_LEVEL_KEYS = {
    "schema_version",
    "brief_metadata",
    "mode",
    "source_refs",
    "custody_flags",
    "sections",
    "non_claims",
}
SEMANTIC_SECTIONS = {
    "decision",
    "starting_direction",
    "what_lolla_pressed_on",
    "what_changed",
    "what_this_means_for_action",
    "what_still_might_be_wrong",
    "what_was_not_proven",
    "evidence_receipt",
}
SECTION_REQUIRED_FIELDS = {
    "status",
    "source_status",
    "source_refs",
    "interpreted_by",
    "human_validated",
    "uncertainty",
    "value",
    "empty_meaning",
}
SECTION_STATUSES = {
    "populated_from_llm_interpretation",
    "populated_from_human_review",
    "available_from_structured_artifact",
    "not_supplied",
    "requires_llm_interpretation",
    "requires_human_review",
    "available_in_private_artifact_not_exported",
    "available_but_redacted_in_safe_mode",
    "unclear",
}
SOURCE_STATUSES = {
    "checked_in_safe_structured_artifact",
    "local_private_artifact",
    "review_artifact",
    "external_report_reference",
    "not_supplied",
    "redacted",
    "missing",
    "malformed",
    "unclear",
}
MODES = {
    "checked_in_safe_mode",
    "local_private_mode",
    "future_runtime_mode_not_implemented",
}
REQUIRED_NON_CLAIMS = {
    "not_correctness_proof",
    "not_answer_quality_score",
    "not_agent_action_authorization",
    "not_human_validated_unless_marked",
    "clean_artifacts_do_not_imply_good_advice",
    "process_evidence_is_not_decision_certification",
    "llm_interpretation_is_provisional_unless_human_reviewed",
}
FORBIDDEN_FIELD_NAMES = {
    "safe_for_" + "agent_use",
    "approved",
    "certified",
    "pass_fail",
    "winner",
    "quality_score",
    "improvement_score",
    "judge_score",
    "answer_quality_score",
    "product_score",
    "correctness_score",
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
FUTURE_IMPLEMENTATION_FILES = (
    REPO_ROOT / "engine" / "system_b" / "decision_work_brief_draft_pilot.py",
    REPO_ROOT / "scripts" / "evals" / "draft_decision_work_brief.py",
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


def _minimal_unvalidated_fixture() -> dict[str, Any]:
    section = {
        "status": "requires_llm_interpretation",
        "source_status": "not_supplied",
        "source_refs": [],
        "interpreted_by": "not_interpreted",
        "human_validated": False,
        "uncertainty": "not_assessed",
        "value": None,
        "empty_meaning": "No interpretation has been supplied yet.",
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "brief_metadata": {
            "brief_id": "decision_work_brief:schema-only",
            "created_at": "2026-07-01T00:00:00Z",
            "case_id": None,
            "run_id": None,
            "archive_relpath": None,
            "generated_by": "manual_schema_fixture",
            "schema_version": SCHEMA_VERSION,
            "notes": ["Schema-only fixture; no generated brief exists in PR114."],
        },
        "mode": "checked_in_safe_mode",
        "source_refs": [],
        "custody_flags": {
            "human_validated": False,
            "human_validation_status": "not_human_validated",
            "human_review_refs": [],
            "product_proof": False,
            "answer_quality_scored": False,
            "agent_action_authorized": False,
            "runtime_invoked": False,
            "skill_invoked": False,
            "archive_mutated": False,
            "model_calls": 0,
            "raw_private_content_included": False,
            "provider_text_included": False,
            "raw_transcript_included": False,
            "raw_revised_answer_included": False,
            "raw_memo_included": False,
            "private_reasoning_included": False,
            "local_absolute_paths_included": False,
            "secrets_included": False,
            "llm_judge_used": False,
            "automatic_labels_created": False,
        },
        "sections": {name: dict(section) for name in SEMANTIC_SECTIONS},
        "non_claims": {
            "items": sorted(REQUIRED_NON_CLAIMS),
            "empty_meaning": "A missing non-claim means the brief is incomplete.",
        },
    }


def test_schema_json_parses_and_uses_expected_version() -> None:
    schema = _schema()

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["$id"] == SCHEMA_VERSION
    assert schema["properties"]["schema_version"]["const"] == SCHEMA_VERSION


def test_required_top_level_fields_match_pr114_contract() -> None:
    schema = _schema()

    assert set(schema["required"]) == REQUIRED_TOP_LEVEL_KEYS
    assert set(schema["properties"]) == REQUIRED_TOP_LEVEL_KEYS


def test_status_source_status_and_mode_vocabularies_are_explicit() -> None:
    schema = _schema()

    assert set(schema["$defs"]["section_status"]["enum"]) == SECTION_STATUSES
    assert set(schema["$defs"]["source_status"]["enum"]) == SOURCE_STATUSES
    assert set(schema["$defs"]["mode"]["enum"]) == MODES


def test_required_semantic_sections_use_shared_section_contract() -> None:
    schema = _schema()
    sections = schema["$defs"]["sections"]
    semantic_def = schema["$defs"]["semantic_section"]

    assert set(sections["required"]) == SEMANTIC_SECTIONS
    assert set(sections["properties"]) == SEMANTIC_SECTIONS
    assert SECTION_REQUIRED_FIELDS.issubset(set(semantic_def["required"]))

    for section in SEMANTIC_SECTIONS:
        ref = sections["properties"][section]["$ref"]
        assert _resolve_ref(schema, ref) is semantic_def


def test_semantic_sections_make_llm_and_human_interpretation_explicit() -> None:
    schema = _schema()
    semantic_def = schema["$defs"]["semantic_section"]
    rules = semantic_def["allOf"]

    assert semantic_def["properties"]["human_validated"]["default"] is False
    assert any(
        rule.get("if", {})
        .get("properties", {})
        .get("status", {})
        .get("const")
        == "populated_from_llm_interpretation"
        and rule.get("then", {})
        .get("properties", {})
        .get("human_validated", {})
        .get("const")
        is False
        for rule in rules
    )
    assert any(
        rule.get("if", {})
        .get("properties", {})
        .get("human_validated", {})
        .get("const")
        is True
        and rule.get("then", {})
        .get("properties", {})
        .get("status", {})
        .get("const")
        == "populated_from_human_review"
        for rule in rules
    )


def test_lower_claim_custody_fields_are_required_and_conservative() -> None:
    schema = _schema()
    custody = schema["$defs"]["custody_flags"]
    properties = custody["properties"]

    assert {
        "human_validated",
        "product_proof",
        "answer_quality_scored",
        "agent_action_authorized",
        "runtime_invoked",
        "skill_invoked",
        "archive_mutated",
        "model_calls",
        "raw_private_content_included",
        "provider_text_included",
    }.issubset(set(custody["required"]))

    assert properties["human_validated"]["default"] is False
    assert properties["product_proof"]["const"] is False
    assert properties["answer_quality_scored"]["const"] is False
    assert properties["agent_action_authorized"]["const"] is False
    assert properties["runtime_invoked"]["const"] is False
    assert properties["skill_invoked"]["const"] is False
    assert properties["archive_mutated"]["const"] is False
    assert properties["model_calls"]["type"] == "integer"
    assert properties["model_calls"]["minimum"] == 0
    assert properties["model_calls"]["default"] == 0
    assert properties["raw_private_content_included"]["const"] is False
    assert properties["provider_text_included"]["const"] is False
    assert properties["raw_transcript_included"]["const"] is False
    assert properties["raw_revised_answer_included"]["const"] is False
    assert properties["raw_memo_included"]["const"] is False
    assert properties["private_reasoning_included"]["const"] is False
    assert properties["local_absolute_paths_included"]["const"] is False
    assert properties["secrets_included"]["const"] is False
    assert properties["llm_judge_used"]["const"] is False
    assert properties["automatic_labels_created"]["const"] is False


def test_human_validation_requires_explicit_review_refs() -> None:
    schema = _schema()
    rules = schema["$defs"]["custody_flags"]["allOf"]

    assert any(
        rule.get("if", {})
        .get("properties", {})
        .get("human_validated", {})
        .get("const")
        is True
        and rule.get("then", {})
        .get("properties", {})
        .get("human_validation_status", {})
        .get("const")
        == "human_validated_with_review_artifact"
        and rule.get("then", {})
        .get("properties", {})
        .get("human_review_refs", {})
        .get("minItems")
        == 1
        for rule in rules
    )


def test_checked_in_safe_fixture_defaults_to_no_human_validation_or_private_text() -> None:
    fixture = _minimal_unvalidated_fixture()

    assert fixture["mode"] == "checked_in_safe_mode"
    assert fixture["custody_flags"]["human_validated"] is False
    assert fixture["custody_flags"]["human_validation_status"] == "not_human_validated"
    assert fixture["custody_flags"]["human_review_refs"] == []
    assert fixture["custody_flags"]["product_proof"] is False
    assert fixture["custody_flags"]["answer_quality_scored"] is False
    assert fixture["custody_flags"]["agent_action_authorized"] is False
    assert fixture["custody_flags"]["runtime_invoked"] is False
    assert fixture["custody_flags"]["skill_invoked"] is False
    assert fixture["custody_flags"]["archive_mutated"] is False
    assert fixture["custody_flags"]["model_calls"] == 0
    assert fixture["custody_flags"]["raw_private_content_included"] is False
    assert fixture["custody_flags"]["provider_text_included"] is False
    assert all(
        section["human_validated"] is False
        for section in fixture["sections"].values()
    )


def test_source_refs_forbid_raw_private_and_provider_text_inclusion() -> None:
    schema = _schema()
    source_ref = schema["$defs"]["source_ref"]

    assert {
        "artifact",
        "field",
        "source_status",
        "content_included",
        "raw_private_content_included",
        "provider_text_included",
    }.issubset(set(source_ref["required"]))
    assert source_ref["properties"]["raw_private_content_included"]["const"] is False
    assert source_ref["properties"]["provider_text_included"]["const"] is False


def test_required_non_claims_are_schema_required_items() -> None:
    schema = _schema()
    non_claim_keys = set(schema["$defs"]["non_claim_key"]["enum"])
    item_rules = schema["$defs"]["non_claims"]["properties"]["items"]["allOf"]
    required_by_contains = {
        rule["contains"]["const"]
        for rule in item_rules
        if isinstance(rule, dict) and "contains" in rule
    }

    assert REQUIRED_NON_CLAIMS <= non_claim_keys
    assert REQUIRED_NON_CLAIMS <= required_by_contains


def test_schema_avoids_forbidden_authority_or_score_field_names() -> None:
    schema = _schema()
    keys = {key.lower() for key in _walk_keys(schema)}

    assert not keys.intersection(FORBIDDEN_FIELD_NAMES)
    assert not any(
        key.endswith("_score") and key != "not_a_score"
        for key in keys
    )


def test_schema_slice_does_not_add_production_brief_generator() -> None:
    for path in FUTURE_IMPLEMENTATION_FILES:
        assert not path.exists()


def test_pr114_artifacts_have_no_privacy_markers() -> None:
    text = "\n".join(
        [
            SCHEMA_PATH.read_text(encoding="utf-8"),
            SCHEMA_DOC_PATH.read_text(encoding="utf-8"),
            PRD_PATH.read_text(encoding="utf-8"),
            Path(__file__).read_text(encoding="utf-8"),
        ]
    )

    for marker in PRIVACY_MARKERS:
        assert marker not in text


def test_product_delta_boundary_lint_accepts_pr114_artifacts_without_blockers() -> None:
    report = lint_product_delta_paths([PRD_PATH, SCHEMA_DOC_PATH, SCHEMA_PATH])

    assert report["summary"]["blocking_error_count"] == 0
