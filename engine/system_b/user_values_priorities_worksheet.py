"""Blank user-values/priorities worksheet builder.

This module creates only an empty, human-owned review worksheet. It does not
read archive folders, transcript text, memos, revised answers, model/provider
text, or private reasoning.
"""
from __future__ import annotations

import json
import re
from collections.abc import Mapping
from pathlib import Path, PureWindowsPath
from typing import Any


USER_VALUES_PRIORITIES_WORKSHEET_SCHEMA_VERSION = (
    "lolla.user_values_priorities_worksheet.v0"
)

REVIEW_SCOPE = "human_review_only"
UNFILLED = "unfilled"

SOURCE_FALSE_FLAGS = (
    "human_filled",
    "auto_extracted",
    "llm_judge_used",
    "raw_transcript_included",
    "raw_memo_included",
    "raw_revised_answer_included",
    "raw_model_message_content_included",
    "provider_reasoning_details_included",
    "private_reasoning_included",
    "local_absolute_paths_included",
)

SOURCE_ARTIFACT_KEYS = (
    "memo",
    "revised_answer",
    "agent_result",
    "evaluation",
    "review_corpus_record",
)

ANSWER_TREATMENT_KEYS = (
    "honored_values",
    "distorted_values",
    "ignored_values",
    "over_hardened_values",
    "open_questions_added",
)

REVIEWER_SUMMARY_KEYS = (
    "values_surface_sufficient_for_review",
    "would_change_actionable_delta_label",
    "safe_for_agent_use_impact",
)

FORBIDDEN_MARKERS = (
    "/" + "Users/",
    "SEC" + "RET",
    "raw_message" + "_content",
    "fabricated" + "_passages",
    "FULL ASSISTANT " + "REASONING",
    "client" + "_secret",
    "api" + "_key",
    "pass" + "word",
)

_WINDOWS_ABSOLUTE_RE = re.compile(r"^[A-Za-z]:[\\/]")


class InputError(ValueError):
    """Deterministic, sanitized input error."""


def build_blank_worksheet(
    *,
    case_id: str | None = None,
    run_id: str | None = None,
    archive_relpath: str | None = None,
) -> dict[str, Any]:
    """Build a blank worksheet with optional compact metadata."""

    payload = {
        "schema_version": USER_VALUES_PRIORITIES_WORKSHEET_SCHEMA_VERSION,
        "case_id": _metadata_value("case_id", case_id, allow_path=False),
        "run_id": _metadata_value("run_id", run_id, allow_path=False),
        "archive_relpath": _metadata_value(
            "archive_relpath", archive_relpath, allow_path=True
        ),
        "review_scope": REVIEW_SCOPE,
        "source": {
            "local_only": True,
            "blank_template": True,
            "human_filled": False,
            "auto_extracted": False,
            "model_calls": 0,
            "llm_judge_used": False,
            "raw_transcript_included": False,
            "raw_memo_included": False,
            "raw_revised_answer_included": False,
            "raw_model_message_content_included": False,
            "provider_reasoning_details_included": False,
            "private_reasoning_included": False,
            "local_absolute_paths_included": False,
        },
        "source_artifacts_reviewed": {
            key: False for key in SOURCE_ARTIFACT_KEYS
        },
        "values_items": [],
        "conflicts": [],
        "answer_treatment": {
            key: [] for key in ANSWER_TREATMENT_KEYS
        },
        "reviewer_summary": {
            key: UNFILLED for key in REVIEWER_SUMMARY_KEYS
        },
        "reviewer_notes": [],
    }
    errors = validate_blank_worksheet(payload)
    if errors:
        raise InputError("; ".join(errors))
    return payload


def validate_blank_worksheet(payload: Mapping[str, Any]) -> list[str]:
    """Return deterministic validation errors for a blank worksheet."""

    errors: list[str] = []
    if not isinstance(payload, Mapping):
        return ["payload must be a JSON object"]

    if payload.get("schema_version") != USER_VALUES_PRIORITIES_WORKSHEET_SCHEMA_VERSION:
        errors.append("schema_version must be lolla.user_values_priorities_worksheet.v0")
    if payload.get("review_scope") != REVIEW_SCOPE:
        errors.append("review_scope must be human_review_only")

    errors.extend(_validate_metadata_field(payload, "case_id", allow_path=False))
    errors.extend(_validate_metadata_field(payload, "run_id", allow_path=False))
    errors.extend(_validate_metadata_field(payload, "archive_relpath", allow_path=True))
    errors.extend(_validate_source(payload.get("source")))
    errors.extend(
        _validate_false_mapping(
            payload.get("source_artifacts_reviewed"),
            SOURCE_ARTIFACT_KEYS,
            "source_artifacts_reviewed",
        )
    )

    if payload.get("values_items") != []:
        errors.append("values_items must be an empty list")
    if payload.get("conflicts") != []:
        errors.append("conflicts must be an empty list")

    answer_treatment = payload.get("answer_treatment")
    if not isinstance(answer_treatment, Mapping):
        errors.append("answer_treatment must be a JSON object")
    else:
        for key in ANSWER_TREATMENT_KEYS:
            if answer_treatment.get(key) != []:
                errors.append(f"answer_treatment.{key} must be an empty list")

    reviewer_summary = payload.get("reviewer_summary")
    if not isinstance(reviewer_summary, Mapping):
        errors.append("reviewer_summary must be a JSON object")
    else:
        for key in REVIEWER_SUMMARY_KEYS:
            if reviewer_summary.get(key) != UNFILLED:
                errors.append(f"reviewer_summary.{key} must be unfilled")

    if payload.get("reviewer_notes") != []:
        errors.append("reviewer_notes must be an empty list")

    rendered = _safe_json(payload)
    if _contains_forbidden_marker(rendered):
        errors.append("payload contains disallowed private or raw-content marker")
    return errors


def render_blank_worksheet_json(payload: Mapping[str, Any]) -> str:
    """Render deterministic JSON for a blank worksheet."""

    return json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def write_blank_worksheet(path: Path | str, payload: Mapping[str, Any]) -> None:
    """Write a worksheet JSON payload to disk."""

    output = Path(path)
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(render_blank_worksheet_json(payload), encoding="utf-8")
    except OSError as exc:
        raise InputError(f"output could not be written:{type(exc).__name__}") from exc


def _validate_source(value: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, Mapping):
        return ["source must be a JSON object"]
    if value.get("local_only") is not True:
        errors.append("source.local_only must be true")
    if value.get("blank_template") is not True:
        errors.append("source.blank_template must be true")
    if value.get("model_calls") != 0:
        errors.append("source.model_calls must be 0")
    for flag in SOURCE_FALSE_FLAGS:
        if value.get(flag) is not False:
            errors.append(f"source.{flag} must be false")
    for key, item in value.items():
        if isinstance(item, str):
            errors.extend(_validate_text_value(f"source.{key}", item, allow_path=False))
    return errors


def _validate_false_mapping(value: Any, keys: tuple[str, ...], prefix: str) -> list[str]:
    if not isinstance(value, Mapping):
        return [f"{prefix} must be a JSON object"]
    errors: list[str] = []
    for key in keys:
        if value.get(key) is not False:
            errors.append(f"{prefix}.{key} must be false")
    return errors


def _validate_metadata_field(
    payload: Mapping[str, Any], field: str, *, allow_path: bool
) -> list[str]:
    value = payload.get(field)
    if value is None:
        return [f"{field} must be a string"]
    if not isinstance(value, str):
        return [f"{field} must be a string"]
    return _validate_text_value(field, value, allow_path=allow_path)


def _metadata_value(field: str, value: str | None, *, allow_path: bool) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        raise InputError(f"{field} must be a string")
    errors = _validate_text_value(field, value, allow_path=allow_path)
    if errors:
        raise InputError("; ".join(errors))
    return value


def _validate_text_value(field: str, value: str, *, allow_path: bool) -> list[str]:
    errors: list[str] = []
    if _contains_forbidden_marker(value):
        errors.append(f"{field} contains disallowed private or raw-content marker")
    if _looks_absolute(value):
        errors.append(f"{field} must not be an absolute path")
    if value.startswith("~"):
        errors.append(f"{field} must not use home-directory shorthand")
    parts = [part for part in value.replace("\\", "/").split("/") if part]
    if any(part == ".." for part in parts):
        errors.append(f"{field} must not contain parent-directory traversal")
    if not allow_path and ("/" in value or "\\" in value):
        errors.append(f"{field} must be a compact identifier")
    if allow_path and "\\" in value:
        errors.append(f"{field} must use forward-slash relative paths")
    if allow_path and "//" in value:
        errors.append(f"{field} must not contain empty path segments")
    if allow_path and value.startswith("./"):
        errors.append(f"{field} must be relative without leading dot segments")
    return errors


def _looks_absolute(value: str) -> bool:
    if not value:
        return False
    if Path(value).is_absolute():
        return True
    if PureWindowsPath(value).is_absolute():
        return True
    return bool(_WINDOWS_ABSOLUTE_RE.match(value))


def _contains_forbidden_marker(value: str) -> bool:
    return any(marker in value for marker in FORBIDDEN_MARKERS)


def _safe_json(payload: Mapping[str, Any]) -> str:
    try:
        return json.dumps(payload, ensure_ascii=False, sort_keys=True)
    except (TypeError, ValueError):
        return ""
