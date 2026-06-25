"""Human review label contract for Lolla archive-corpus records.

This module defines the first versioned label set for human review. It is
deliberately a review scaffold: it does not score advice quality, call models,
or decide whether a run is safe automatically.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any


HUMAN_REVIEW_SCHEMA_VERSION = "lolla.human_review.v0"
HUMAN_REVIEW_SCHEMA_DEFINITION_VERSION = "lolla.human_review_schema.v0"

HUMAN_REVIEW_FIELDS = (
    "schema_version",
    "reviewer_id",
    "review_status",
    "primary_failure_mode",
    "severity",
    "useful_friction",
    "noisy_friction",
    "missing_friction",
    "revised_answer_improved",
    "safe_for_agent_use",
    "reviewer_notes",
)

REVIEW_STATUS_VALUES = (
    "pass",
    "fail",
    "needs_followup",
    "exclude_from_eval",
)

FAILURE_MODE_VALUES = (
    "none",
    "capture_loss",
    "artifact_custody_failure",
    "private_public_leak",
    "audit_pressure_ignored",
    "smooth_no_op",
    "unearned_noise",
    "overcorrection",
    "constraint_drift",
    "unsupported_new_claim",
    "memo_divergence",
    "false_clean_health",
    "judge_palatable_blandness",
)

SEVERITY_VALUES = (
    "none",
    "low",
    "medium",
    "high",
    "critical",
)

FRICTION_VALUES = (
    "present",
    "partial",
    "absent",
    "unclear",
    "not_applicable",
)

REVISED_ANSWER_IMPROVED_VALUES = (
    "yes",
    "partly",
    "no",
    "unclear",
)

SAFE_FOR_AGENT_USE_VALUES = (
    "yes",
    "with_human_review",
    "no",
    "unclear",
)

ENUM_FIELDS = {
    "review_status": REVIEW_STATUS_VALUES,
    "primary_failure_mode": FAILURE_MODE_VALUES,
    "severity": SEVERITY_VALUES,
    "useful_friction": FRICTION_VALUES,
    "noisy_friction": FRICTION_VALUES,
    "missing_friction": FRICTION_VALUES,
    "revised_answer_improved": REVISED_ANSWER_IMPROVED_VALUES,
    "safe_for_agent_use": SAFE_FOR_AGENT_USE_VALUES,
}

STRING_OR_NULL_FIELDS = (
    "reviewer_id",
    "reviewer_notes",
)


def blank_human_review_template() -> dict[str, Any]:
    """Return the blank review fields carried by every corpus record."""

    return {
        "schema_version": HUMAN_REVIEW_SCHEMA_VERSION,
        "reviewer_id": None,
        "review_status": None,
        "primary_failure_mode": None,
        "severity": None,
        "useful_friction": None,
        "noisy_friction": None,
        "missing_friction": None,
        "revised_answer_improved": None,
        "safe_for_agent_use": None,
        "reviewer_notes": None,
    }


def human_review_schema_definition() -> dict[str, Any]:
    """Return a deterministic machine-readable summary of the label contract."""

    return {
        "schema_version": HUMAN_REVIEW_SCHEMA_DEFINITION_VERSION,
        "review_record_schema_version": HUMAN_REVIEW_SCHEMA_VERSION,
        "scope": {
            "human_review_only": True,
            "advice_quality_scored_automatically": False,
            "llm_judge_used": False,
            "model_calls": 0,
            "automatic_approval": False,
        },
        "fields": list(HUMAN_REVIEW_FIELDS),
        "allowed_values": {
            field: list(values)
            for field, values in sorted(ENUM_FIELDS.items(), key=lambda item: item[0])
        },
        "string_or_null_fields": list(STRING_OR_NULL_FIELDS),
    }


def validate_human_review(review: Mapping[str, Any]) -> list[str]:
    """Validate a `lolla.human_review.v0` object.

    The blank template is valid. Cross-field checks are intentionally light:
    they catch obvious contradictions without turning human review into an
    automated answer-quality verdict.
    """

    if not isinstance(review, Mapping):
        return ["human_review must be an object"]

    errors: list[str] = []
    allowed_fields = set(HUMAN_REVIEW_FIELDS)

    for field in sorted(set(review) - allowed_fields):
        errors.append(f"unknown human_review field: {field}")

    schema_version = review.get("schema_version")
    if schema_version != HUMAN_REVIEW_SCHEMA_VERSION:
        errors.append(
            f"schema_version must be {HUMAN_REVIEW_SCHEMA_VERSION!r}"
        )

    for field in STRING_OR_NULL_FIELDS:
        value = review.get(field)
        if value is not None and not isinstance(value, str):
            errors.append(f"{field} must be a string or null")

    for field, allowed_values in ENUM_FIELDS.items():
        value = review.get(field)
        if value is None:
            continue
        if not isinstance(value, str):
            errors.append(f"{field} must be a string or null")
            continue
        if value not in allowed_values:
            expected = ", ".join(allowed_values)
            errors.append(
                f"{field} has invalid value {value!r}; expected one of: {expected}"
            )

    review_status = review.get("review_status")
    primary_failure_mode = review.get("primary_failure_mode")
    severity = review.get("severity")

    if review_status == "pass" and primary_failure_mode not in (None, "none"):
        errors.append(
            "review_status 'pass' requires primary_failure_mode to be null or 'none'"
        )
    if review_status == "pass" and severity not in (None, "none"):
        errors.append("review_status 'pass' requires severity to be null or 'none'")
    if review_status == "fail" and primary_failure_mode in (None, "none"):
        errors.append("review_status 'fail' requires a primary_failure_mode")
    if review_status == "fail" and severity in (None, "none"):
        errors.append("review_status 'fail' requires non-none severity")

    return errors
