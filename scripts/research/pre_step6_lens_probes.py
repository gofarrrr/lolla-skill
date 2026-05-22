#!/usr/bin/env python3
"""Research-only validation for pre-Step-6 lens probes.

Lens probes are private cognition aids. They map a lens pack such as Bevelin
onto candidate reasoning material, but they do not solve the user's problem,
choose final advice, or change runtime behavior.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, Sequence


LENS_PROBE_SCHEMA_VERSION = "pre_step6_lens_probe.v1"
ALLOWED_STATUS = frozenset({"research_only"})
ALLOWED_RUNTIME_POLICY = frozenset({"runtime_dormant"})
ALLOWED_LENS_PACKS = frozenset(
    {
        "bevelin_seeking_wisdom_v0",
        "polya_problem_solving_v0",
    }
)
ALLOWED_ATTENTION = frozenset({"active", "scan", "parked"})
TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "lens_pack",
        "source_refs",
        "problem_state_ref",
        "attention_map_ref",
        "lens_candidates",
        "off_narrative_preservation",
        "do_not_force",
        "notes",
    }
)
LENS_CANDIDATE_FIELDS = frozenset(
    {
        "lens_id",
        "lens_name",
        "why_it_might_matter",
        "source_hooks",
        "supported_by_artifact_ids",
        "cheap_test_for_step6",
        "risk_if_forced",
        "risk_if_ignored",
        "suggested_attention",
        "false_friend_warning",
    }
)
OFF_NARRATIVE_FIELDS = frozenset(
    {
        "lens_id",
        "why_preserve_even_if_not_obvious",
        "preserve_as",
        "reactivate_if",
        "risk_if_forced",
    }
)
FORBIDDEN_LANGUAGE = (
    "best option",
    "correct answer",
    "final recommendation",
    "step 6 should conclude",
    "use this because it is correct",
    "drop this because it is not relevant",
    "bevelin says the answer",
    "munger says the answer",
)


class LensProbeValidationError(ValueError):
    pass


def load_lens_probe_payload(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise LensProbeValidationError(f"{path}: payload must be an object")
    return payload


def validate_lens_probe_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_lens_probe_errors(payload, path=Path(path)))
    if errors:
        raise LensProbeValidationError("; ".join(errors))


def validate_lens_probe_file(path: Path) -> None:
    validate_lens_probe_payload(load_lens_probe_payload(path), path=Path(path))


def iter_lens_probe_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> Iterable[str]:
    if not isinstance(payload, dict):
        yield f"{path}: payload must be an object"
        return
    required = (
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "lens_pack",
        "source_refs",
        "problem_state_ref",
        "attention_map_ref",
        "lens_candidates",
        "off_narrative_preservation",
        "do_not_force",
    )
    yield from _unknown_fields(payload, TOP_LEVEL_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return

    if _string(payload.get("schema_version")) != LENS_PROBE_SCHEMA_VERSION:
        yield f"{path / 'schema_version'}: must be {LENS_PROBE_SCHEMA_VERSION}"
    if _string(payload.get("status")) not in ALLOWED_STATUS:
        yield f"{path / 'status'}: status must be research_only"
    if _string(payload.get("runtime_policy")) not in ALLOWED_RUNTIME_POLICY:
        yield f"{path / 'runtime_policy'}: runtime_policy must be runtime_dormant"
    if not _string(payload.get("case_id")).strip():
        yield f"{path / 'case_id'}: case_id must be non-empty"
    if _string(payload.get("lens_pack")) not in ALLOWED_LENS_PACKS:
        yield f"{path / 'lens_pack'}: unknown lens_pack"
    for field in ("source_refs", "do_not_force"):
        if not _non_empty_string_list(payload.get(field)):
            yield f"{path / field}: must be a non-empty string list"
    for field in ("problem_state_ref", "attention_map_ref"):
        if not _string(payload.get(field)).strip():
            yield f"{path / field}: must be non-empty"

    yield from _validate_lens_candidates(
        payload.get("lens_candidates"),
        path / "lens_candidates",
    )
    yield from _validate_off_narrative(
        payload.get("off_narrative_preservation"),
        path / "off_narrative_preservation",
    )
    yield from _forbidden_text_errors(payload, path)


def _validate_lens_candidates(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, list):
        yield f"{path}: lens_candidates must be a list"
        return
    if not value:
        yield f"{path}: lens_candidates must not be empty"
        return
    for index, candidate in enumerate(value):
        item_path = path / f"[{index}]"
        if not isinstance(candidate, dict):
            yield f"{item_path}: candidate must be an object"
            continue
        required = tuple(LENS_CANDIDATE_FIELDS)
        yield from _unknown_fields(candidate, LENS_CANDIDATE_FIELDS, item_path)
        yield from _missing_fields(candidate, required, item_path)
        if any(field not in candidate for field in required):
            continue
        for field in (
            "lens_id",
            "lens_name",
            "why_it_might_matter",
            "cheap_test_for_step6",
            "risk_if_forced",
            "risk_if_ignored",
            "false_friend_warning",
        ):
            if not _string(candidate.get(field)).strip():
                yield f"{item_path / field}: must be non-empty"
        for field in ("source_hooks", "supported_by_artifact_ids"):
            if not _non_empty_string_list(candidate.get(field)):
                yield f"{item_path / field}: must be a non-empty string list"
        if _string(candidate.get("suggested_attention")) not in ALLOWED_ATTENTION:
            yield f"{item_path / 'suggested_attention'}: unknown suggested_attention"


def _validate_off_narrative(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: off_narrative_preservation must be an object"
        return
    required = tuple(OFF_NARRATIVE_FIELDS)
    yield from _unknown_fields(value, OFF_NARRATIVE_FIELDS, path)
    yield from _missing_fields(value, required, path)
    if any(field not in value for field in required):
        return
    for field in required:
        if not _string(value.get(field)).strip():
            yield f"{path / field}: must be non-empty"
    if _string(value.get("preserve_as")) not in {"scan", "parked"}:
        yield f"{path / 'preserve_as'}: must be scan or parked"


def _forbidden_text_errors(payload: dict[str, object], path: Path) -> Iterable[str]:
    for field, text in _walk_text(payload):
        lowered = text.lower()
        if any(term in lowered for term in FORBIDDEN_LANGUAGE):
            yield f"{path / field}: forbidden language"


def _walk_text(value: object, prefix: str = "") -> Iterable[tuple[str, str]]:
    if isinstance(value, str):
        yield prefix or "<root>", value
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _walk_text(item, f"{prefix}[{index}]")
    elif isinstance(value, dict):
        for key, item in value.items():
            next_prefix = f"{prefix}.{key}" if prefix else str(key)
            yield from _walk_text(item, next_prefix)


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


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args(argv)
    for path in args.paths:
        validate_lens_probe_file(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
