#!/usr/bin/env python3
"""Research-only validation/rendering for Step 6 attention maps."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, Sequence


STEP6_ATTENTION_MAP_SCHEMA_VERSION = "step6_attention_map.v1"
MAX_RENDER_CHARS = 4200
ALLOWED_STATUS = frozenset({"research_only"})
ALLOWED_RUNTIME_POLICY = frozenset({"runtime_dormant"})
ALLOWED_REVIEW_ADMISSION = frozenset(
    {"none", "optional_review", "manual_only", "stop_insufficient_grounding"}
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
TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "source_refs",
        "problem_read",
        "active_working_set",
        "edge_latticework_reserve",
        "weak_or_negative_space_receipts",
        "parked_but_preserved",
        "ask_user_if_any",
        "review_admission",
        "full_archive_refs",
        "step6_instruction",
    }
)
REQUIRED_FIELDS = tuple(TOP_LEVEL_FIELDS)
PROBLEM_READ_FIELDS = frozenset({"user_goal", "problem_type", "suggested_next_move"})
ACTIVE_FIELDS = frozenset(
    {
        "artifact_id",
        "why_available",
        "step6_use",
        "boundary",
        "risk_if_ignored",
        "expansion_ref",
    }
)
EDGE_FIELDS = frozenset(
    {
        "artifact_id",
        "protected_slot",
        "why_available",
        "cheap_test",
        "risk_if_forced",
        "risk_if_ignored",
        "expansion_ref",
    }
)
WEAK_FIELDS = frozenset({"artifact_id", "why_preserved", "reactivate_if", "expansion_ref"})
PARKED_FIELDS = frozenset({"artifact_id", "park_reason", "reactivate_if", "expansion_ref"})
ASK_FIELDS = frozenset({"question", "why_it_matters"})
FORBIDDEN_INSTRUCTION_LANGUAGE = (
    "final recommendation",
    "correct answer",
    "best option",
    "step 6 should conclude",
    "openrouter",
    "gpt-",
    "claude",
)


class Step6AttentionMapValidationError(ValueError):
    pass


def load_step6_attention_map_payload(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise Step6AttentionMapValidationError(f"{path}: payload must be an object")
    return payload


def validate_step6_attention_map_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_step6_attention_map_errors(payload, path=Path(path)))
    if errors:
        raise Step6AttentionMapValidationError("; ".join(errors))


def validate_step6_attention_map_file(path: Path) -> None:
    validate_step6_attention_map_payload(
        load_step6_attention_map_payload(path),
        path=Path(path),
    )


def render_step6_attention_map(payload: dict[str, object]) -> str:
    validate_step6_attention_map_payload(payload)
    lines: list[str] = [
        "STEP 6 ATTENTION MAP",
        "",
        "Use as advisory private context, not as a verdict.",
        "",
    ]
    problem_read = payload["problem_read"]
    assert isinstance(problem_read, dict)
    lines.extend(
        [
            "PROBLEM READ",
            f"- Goal: {_string(problem_read.get('user_goal'))}",
            f"- Type: {_string(problem_read.get('problem_type'))}",
            f"- Move: {_string(problem_read.get('suggested_next_move'))}",
            "",
        ]
    )
    _extend_active(lines, payload["active_working_set"])
    _extend_edge(lines, payload["edge_latticework_reserve"])
    _extend_weak(lines, payload["weak_or_negative_space_receipts"])
    _extend_parked(lines, payload["parked_but_preserved"])
    lines.extend(["FULL ARCHIVE REFS"])
    for ref in payload["full_archive_refs"]:
        lines.append(f"- {ref}")
    lines.extend(["", "INSTRUCTION", _string(payload["step6_instruction"])])
    rendered = "\n".join(lines).strip() + "\n"
    if len(rendered) > MAX_RENDER_CHARS:
        raise Step6AttentionMapValidationError(
            f"rendered attention map exceeds {MAX_RENDER_CHARS} chars"
        )
    return rendered


def iter_step6_attention_map_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> Iterable[str]:
    if not isinstance(payload, dict):
        yield f"{path}: payload must be an object"
        return

    yield from _unknown_fields(payload, TOP_LEVEL_FIELDS, path)
    yield from _missing_fields(payload, REQUIRED_FIELDS, path)
    if any(field not in payload for field in REQUIRED_FIELDS):
        return

    if _string(payload.get("schema_version")) != STEP6_ATTENTION_MAP_SCHEMA_VERSION:
        yield f"{path / 'schema_version'}: must be {STEP6_ATTENTION_MAP_SCHEMA_VERSION}"
    if _string(payload.get("status")) not in ALLOWED_STATUS:
        yield f"{path / 'status'}: status must be research_only"
    if _string(payload.get("runtime_policy")) not in ALLOWED_RUNTIME_POLICY:
        yield f"{path / 'runtime_policy'}: runtime_policy must be runtime_dormant"
    if not _string(payload.get("case_id")).strip():
        yield f"{path / 'case_id'}: case_id must be non-empty"
    if not _non_empty_string_list(payload.get("source_refs")):
        yield f"{path / 'source_refs'}: source_refs must be a non-empty string list"
    if _string(payload.get("review_admission")) not in ALLOWED_REVIEW_ADMISSION:
        yield f"{path / 'review_admission'}: unknown review_admission"
    if not _non_empty_string_list(payload.get("full_archive_refs")):
        yield f"{path / 'full_archive_refs'}: full_archive_refs must be a non-empty string list"

    yield from _validate_problem_read(payload.get("problem_read"), path / "problem_read")
    yield from _validate_items(
        payload.get("active_working_set"),
        fields=ACTIVE_FIELDS,
        required=tuple(ACTIVE_FIELDS),
        path=path / "active_working_set",
    )
    yield from _validate_items(
        payload.get("edge_latticework_reserve"),
        fields=EDGE_FIELDS,
        required=tuple(EDGE_FIELDS),
        path=path / "edge_latticework_reserve",
    )
    yield from _validate_items(
        payload.get("weak_or_negative_space_receipts"),
        fields=WEAK_FIELDS,
        required=tuple(WEAK_FIELDS),
        path=path / "weak_or_negative_space_receipts",
    )
    yield from _validate_items(
        payload.get("parked_but_preserved"),
        fields=PARKED_FIELDS,
        required=tuple(PARKED_FIELDS),
        path=path / "parked_but_preserved",
    )
    yield from _validate_items(
        payload.get("ask_user_if_any"),
        fields=ASK_FIELDS,
        required=tuple(ASK_FIELDS),
        path=path / "ask_user_if_any",
        allow_empty=True,
    )

    instruction = _string(payload.get("step6_instruction"))
    if not instruction.strip():
        yield f"{path / 'step6_instruction'}: must be non-empty"
    elif _contains_forbidden_instruction_language(instruction):
        yield f"{path / 'step6_instruction'}: forbidden language"


def _validate_problem_read(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: problem_read must be an object"
        return
    yield from _unknown_fields(value, PROBLEM_READ_FIELDS, path)
    yield from _missing_fields(value, tuple(PROBLEM_READ_FIELDS), path)
    if any(field not in value for field in PROBLEM_READ_FIELDS):
        return
    for field in ("user_goal", "problem_type"):
        if not _string(value.get(field)).strip():
            yield f"{path / field}: must be non-empty"
    if _string(value.get("suggested_next_move")) not in ALLOWED_NEXT_MOVES:
        yield f"{path / 'suggested_next_move'}: unknown suggested_next_move"


def _validate_items(
    value: object,
    *,
    fields: frozenset[str],
    required: Sequence[str],
    path: Path,
    allow_empty: bool = False,
) -> Iterable[str]:
    if not isinstance(value, list):
        yield f"{path}: must be a list"
        return
    if not value and not allow_empty:
        yield f"{path}: must not be empty"
        return
    for index, item in enumerate(value):
        item_path = path / f"[{index}]"
        if not isinstance(item, dict):
            yield f"{item_path}: item must be an object"
            continue
        yield from _unknown_fields(item, fields, item_path)
        yield from _missing_fields(item, required, item_path)
        if any(field not in item for field in required):
            continue
        for field in required:
            if not _string(item.get(field)).strip():
                yield f"{item_path / field}: must be non-empty"


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


def _contains_forbidden_instruction_language(text: str) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in FORBIDDEN_INSTRUCTION_LANGUAGE)


def _extend_active(lines: list[str], items: object) -> None:
    lines.append("ACTIVE WORKING SET")
    for item in items:
        assert isinstance(item, dict)
        lines.append(f"- {item['artifact_id']}: {item['step6_use']}")
        lines.append(f"  Boundary: {item['boundary']}")
        lines.append(f"  Risk if ignored: {item['risk_if_ignored']}")
    lines.append("")


def _extend_edge(lines: list[str], items: object) -> None:
    lines.append("EDGE LATTICEWORK RESERVE")
    for item in items:
        assert isinstance(item, dict)
        lines.append(f"- {item['artifact_id']} [{item['protected_slot']}]: {item['cheap_test']}")
        lines.append(f"  Risk if forced: {item['risk_if_forced']}")
        lines.append(f"  Risk if ignored: {item['risk_if_ignored']}")
    lines.append("")


def _extend_weak(lines: list[str], items: object) -> None:
    lines.append("WEAK OR NEGATIVE SPACE RECEIPTS")
    for item in items:
        assert isinstance(item, dict)
        lines.append(f"- {item['artifact_id']}: {item['why_preserved']}")
        lines.append(f"  Reactivate if: {item['reactivate_if']}")
    lines.append("")


def _extend_parked(lines: list[str], items: object) -> None:
    lines.append("PARKED BUT PRESERVED")
    for item in items:
        assert isinstance(item, dict)
        lines.append(f"- {item['artifact_id']}: {item['park_reason']}")
        lines.append(f"  Reactivate if: {item['reactivate_if']}")
    lines.append("")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args(argv)
    for path in args.paths:
        validate_step6_attention_map_file(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
