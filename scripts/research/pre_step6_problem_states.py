#!/usr/bin/env python3
"""Research-only validation for pre-Step-6 problem states.

This module validates the small Polya-shaped problem read used by the Step 6
reasoning-portfolio experiment. It is deliberately outside the live pipeline.
It does not solve the user's problem, choose final advice, or change /lolla
runtime behavior.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, Sequence


PROBLEM_STATE_SCHEMA_VERSION = "problem_state.v1"
ALLOWED_STATUS = frozenset({"research_only"})
ALLOWED_RUNTIME_POLICY = frozenset({"runtime_dormant"})
ALLOWED_PROBLEM_TYPES = frozenset(
    {
        "decision_evaluation",
        "action_planning",
        "causal_diagnosis",
        "critique",
        "explanation",
        "prediction",
        "design",
        "unclear",
    }
)
ALLOWED_NEXT_MOVES = frozenset(
    {
        "answer_now",
        "ask_user",
        "audit_first",
        "stop_capture_or_scope_issue",
        "stop_insufficient_grounding",
    }
)
PROBLEM_STATE_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "source_refs",
        "user_goal",
        "problem_type",
        "knowns",
        "unknowns",
        "constraints",
        "success_condition",
        "missing_user_owned_info",
        "suggested_next_move",
        "why",
    }
)
REQUIRED_FIELDS = tuple(PROBLEM_STATE_FIELDS)
FORBIDDEN_LANGUAGE = (
    "best option",
    "correct answer",
    "final recommendation",
    "the user should",
    "step 6 should conclude",
)


class ProblemStateValidationError(ValueError):
    pass


def load_problem_state_payload(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ProblemStateValidationError(f"{path}: payload must be an object")
    return payload


def validate_problem_state_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_problem_state_errors(payload, path=Path(path)))
    if errors:
        raise ProblemStateValidationError("; ".join(errors))


def validate_problem_state_file(path: Path) -> None:
    validate_problem_state_payload(load_problem_state_payload(path), path=Path(path))


def iter_problem_state_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> Iterable[str]:
    if not isinstance(payload, dict):
        yield f"{path}: payload must be an object"
        return

    yield from _unknown_fields(payload, PROBLEM_STATE_FIELDS, path)
    yield from _missing_fields(payload, REQUIRED_FIELDS, path)
    if any(field not in payload for field in REQUIRED_FIELDS):
        return

    if _string(payload.get("schema_version")) != PROBLEM_STATE_SCHEMA_VERSION:
        yield f"{path / 'schema_version'}: must be {PROBLEM_STATE_SCHEMA_VERSION}"
    if _string(payload.get("status")) not in ALLOWED_STATUS:
        yield f"{path / 'status'}: status must be research_only"
    if _string(payload.get("runtime_policy")) not in ALLOWED_RUNTIME_POLICY:
        yield f"{path / 'runtime_policy'}: runtime_policy must be runtime_dormant"
    if not _string(payload.get("case_id")).strip():
        yield f"{path / 'case_id'}: case_id must be non-empty"

    source_refs = payload.get("source_refs")
    if not _non_empty_string_list(source_refs):
        yield f"{path / 'source_refs'}: source_refs must be a non-empty string list"

    if not _string(payload.get("user_goal")).strip():
        yield f"{path / 'user_goal'}: user_goal must be non-empty"
    if _string(payload.get("problem_type")) not in ALLOWED_PROBLEM_TYPES:
        yield f"{path / 'problem_type'}: unknown problem_type"
    if _string(payload.get("suggested_next_move")) not in ALLOWED_NEXT_MOVES:
        yield f"{path / 'suggested_next_move'}: unknown suggested_next_move"

    for field in ("knowns", "unknowns", "constraints", "missing_user_owned_info"):
        value = payload.get(field)
        if not isinstance(value, list) or not all(
            isinstance(item, str) and item.strip() for item in value
        ):
            yield f"{path / field}: must be a list of non-empty strings"

    for field in ("success_condition", "why"):
        if not _string(payload.get(field)).strip():
            yield f"{path / field}: must be non-empty"

    for field in (
        "user_goal",
        "success_condition",
        "why",
        "knowns",
        "unknowns",
        "constraints",
        "missing_user_owned_info",
    ):
        text = _field_text(payload.get(field))
        if _contains_forbidden_language(text):
            yield f"{path / field}: forbidden language"


def _unknown_fields(
    payload: dict[str, object],
    allowed: frozenset[str],
    path: Path,
) -> Iterable[str]:
    for field in sorted(set(payload) - allowed):
        yield f"{path / field}: unknown field"


def _missing_fields(
    payload: dict[str, object],
    required: Sequence[str],
    path: Path,
) -> Iterable[str]:
    for field in required:
        if field not in payload:
            yield f"{path / field}: missing required field"


def _string(value: object) -> str:
    return value if isinstance(value, str) else ""


def _non_empty_string_list(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(
        isinstance(item, str) and item.strip() for item in value
    )


def _field_text(value: object) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return " ".join(item for item in value if isinstance(item, str))
    return ""


def _contains_forbidden_language(text: str) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in FORBIDDEN_LANGUAGE)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args(argv)
    for path in args.paths:
        validate_problem_state_file(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
