"""Synthetic review validation for Lolla review rehearsals.

Synthetic review outputs are candidate notes, not human labels. This validator
keeps that boundary explicit and delegates candidate label validation to the
human-review contract.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .human_review import HUMAN_REVIEW_SCHEMA_VERSION, validate_human_review


SYNTHETIC_REVIEW_SCHEMA_VERSION = "lolla.synthetic_review.v0"
SYNTHETIC_REVIEW_SCHEMA_DOC_VERSION = "lolla.synthetic_review_schema.v0"

REVIEWER_KIND_VALUES = ("synthetic",)
CONFIDENCE_VALUES = ("low", "medium", "high", "unclear")

REQUIRED_SCOPE = {
    "synthetic_only": True,
    "human_review_ground_truth": False,
    "requires_human_ratification": True,
    "may_populate_human_review_without_ratification": False,
    "automatic_approval": False,
}

TOP_LEVEL_FIELDS = (
    "schema_version",
    "reviewer_kind",
    "model_or_agent",
    "scope",
    "records",
    "source_corpus_manifest",
    "pilot_id",
    "generated_at",
    "notes",
)

REQUIRED_TOP_LEVEL_FIELDS = (
    "schema_version",
    "reviewer_kind",
    "model_or_agent",
    "scope",
    "records",
)

RECORD_FIELDS = (
    "index",
    "archive_relpath",
    "case_id",
    "run_id",
    "candidate_human_review",
    "confidence",
    "uncertainties",
    "qa_notes",
)

REQUIRED_RECORD_FIELDS = (
    "index",
    "archive_relpath",
    "candidate_human_review",
    "confidence",
    "uncertainties",
    "qa_notes",
)

REQUIRED_CANDIDATE_HUMAN_REVIEW_FIELDS = (
    "review_status",
    "primary_failure_mode",
    "severity",
    "useful_friction",
    "noisy_friction",
    "missing_friction",
    "revised_answer_improved",
    "safe_for_agent_use",
)


def synthetic_review_schema_definition() -> dict[str, Any]:
    """Return the machine-readable schema summary for synthetic review notes."""

    return {
        "schema_version": SYNTHETIC_REVIEW_SCHEMA_DOC_VERSION,
        "synthetic_review_record_schema_version": SYNTHETIC_REVIEW_SCHEMA_VERSION,
        "scope": dict(REQUIRED_SCOPE),
        "top_level_fields": list(TOP_LEVEL_FIELDS),
        "required_top_level_fields": list(REQUIRED_TOP_LEVEL_FIELDS),
        "record_fields": list(RECORD_FIELDS),
        "required_record_fields": list(REQUIRED_RECORD_FIELDS),
        "allowed_values": {
            "reviewer_kind": list(REVIEWER_KIND_VALUES),
            "confidence": list(CONFIDENCE_VALUES),
        },
        "candidate_human_review": {
            "schema_version": HUMAN_REVIEW_SCHEMA_VERSION,
            "must_validate_with": "engine.system_b.human_review.validate_human_review",
            "human_review_ground_truth": False,
            "required_non_null_fields_for_synthetic_output": list(
                REQUIRED_CANDIDATE_HUMAN_REVIEW_FIELDS
            ),
        },
    }


def validate_synthetic_review(payload: Mapping[str, Any]) -> list[str]:
    """Validate a `lolla.synthetic_review.v0` payload."""

    if not isinstance(payload, Mapping):
        return ["synthetic_review must be an object"]

    errors: list[str] = []
    allowed_fields = set(TOP_LEVEL_FIELDS)

    for field in sorted(set(payload) - allowed_fields):
        errors.append(f"unknown synthetic_review field: {field}")

    for field in REQUIRED_TOP_LEVEL_FIELDS:
        if field not in payload:
            errors.append(f"missing synthetic_review field: {field}")

    if payload.get("schema_version") != SYNTHETIC_REVIEW_SCHEMA_VERSION:
        errors.append(
            f"schema_version must be {SYNTHETIC_REVIEW_SCHEMA_VERSION!r}"
        )

    reviewer_kind = payload.get("reviewer_kind")
    if reviewer_kind not in REVIEWER_KIND_VALUES:
        expected = ", ".join(REVIEWER_KIND_VALUES)
        errors.append(
            f"reviewer_kind has invalid value {reviewer_kind!r}; expected one of: {expected}"
        )

    _validate_optional_string(payload, "model_or_agent", errors, required=True)
    _validate_optional_string(payload, "source_corpus_manifest", errors)
    _validate_optional_string(payload, "pilot_id", errors)
    _validate_optional_string(payload, "generated_at", errors)
    _validate_optional_string(payload, "notes", errors)

    _validate_scope(payload.get("scope"), errors)

    records = payload.get("records")
    if not isinstance(records, list):
        errors.append("records must be a list")
        return errors

    for index, record in enumerate(records):
        errors.extend(_validate_record(record, index))

    return errors


def _validate_scope(scope: Any, errors: list[str]) -> None:
    if not isinstance(scope, Mapping):
        errors.append("scope must be an object")
        return
    for field, expected_value in REQUIRED_SCOPE.items():
        value = scope.get(field)
        if value != expected_value:
            errors.append(f"scope.{field} must be {expected_value!r}")


def _validate_record(record: Any, record_index: int) -> list[str]:
    prefix = f"records[{record_index}]"
    errors: list[str] = []
    if not isinstance(record, Mapping):
        return [f"{prefix} must be an object"]

    allowed_fields = set(RECORD_FIELDS)
    for field in sorted(set(record) - allowed_fields):
        errors.append(f"unknown {prefix} field: {field}")

    for field in REQUIRED_RECORD_FIELDS:
        if field not in record:
            errors.append(f"missing {prefix} field: {field}")

    index = record.get("index")
    if type(index) is not int or index < 0:
        errors.append(f"{prefix}.index must be a non-negative integer")

    _validate_optional_string(
        record,
        "archive_relpath",
        errors,
        prefix=prefix,
        required=True,
    )
    _validate_optional_string(record, "case_id", errors, prefix=prefix)
    _validate_optional_string(record, "run_id", errors, prefix=prefix)

    confidence = record.get("confidence")
    if confidence not in CONFIDENCE_VALUES:
        expected = ", ".join(CONFIDENCE_VALUES)
        errors.append(
            f"{prefix}.confidence has invalid value {confidence!r}; expected one of: {expected}"
        )

    for field in ("uncertainties", "qa_notes"):
        value = record.get(field)
        if not _is_string_list(value):
            errors.append(f"{prefix}.{field} must be a list of strings")

    candidate = record.get("candidate_human_review")
    if not isinstance(candidate, Mapping):
        errors.append(f"{prefix}.candidate_human_review must be an object")
    else:
        for error in validate_human_review(candidate):
            errors.append(f"{prefix}.candidate_human_review.{error}")
        for field in REQUIRED_CANDIDATE_HUMAN_REVIEW_FIELDS:
            if candidate.get(field) is None:
                errors.append(
                    f"{prefix}.candidate_human_review.{field} is required "
                    "for synthetic review"
                )

    return errors


def _validate_optional_string(
    payload: Mapping[str, Any],
    field: str,
    errors: list[str],
    *,
    prefix: str = "",
    required: bool = False,
) -> None:
    label = f"{prefix}.{field}" if prefix else field
    value = payload.get(field)
    if required and (not isinstance(value, str) or not value.strip()):
        errors.append(f"{label} must be a non-empty string")
        return
    if value is not None and not isinstance(value, str):
        errors.append(f"{label} must be a string or null")


def _is_string_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)
