#!/usr/bin/env python3
"""Research-only validation for lens-enhanced Step 6 answer cores."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Iterable, Sequence

from pre_step6_attention_maps import (
    load_step6_attention_map_payload,
    render_step6_attention_map,
    validate_step6_attention_map_payload,
)
from pre_step6_lens_probes import (
    load_lens_probe_payload,
    validate_lens_probe_payload,
)
from pre_step6_raw_artifacts import MAX_ANSWER_CORE_CHARS, validate_public_answer_hygiene


LENS_ANSWER_CORE_SCHEMA_VERSION = "pre_step6_lens_answer_core.v1"
ALLOWED_STATUS = frozenset({"research_only"})
ALLOWED_RUNTIME_POLICY = frozenset({"runtime_dormant"})
TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "lens_pack",
        "source_attention_map",
        "source_attention_map_render_sha256",
        "source_lens_probe",
        "answer_core",
        "expected_inclusions",
        "expected_exclusions",
        "lens_effect",
        "notes",
    }
)
LENS_EFFECT_FIELDS = frozenset(
    {
        "preserved_from_base",
        "changed_by_lens",
        "kept_private_or_discarded",
    }
)
EXTRA_FORBIDDEN_PUBLIC_TERMS = (
    "attention map",
    "portfolio",
    "artifact",
    "bundle",
    "worker",
    "bevelin",
    "munger",
    "polya",
    "lens pack",
    "lens probe",
    "reasoning affordance",
)


class LensAnswerCoreValidationError(ValueError):
    pass


def load_lens_answer_core_payload(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise LensAnswerCoreValidationError(f"{path}: payload must be an object")
    return payload


def validate_lens_answer_core_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
    repo_root: Path | None = None,
) -> None:
    errors = list(
        iter_lens_answer_core_errors(
            payload,
            path=Path(path),
            repo_root=repo_root,
        )
    )
    if errors:
        raise LensAnswerCoreValidationError("; ".join(errors))


def validate_lens_answer_core_file(
    path: Path,
    *,
    repo_root: Path | None = None,
) -> None:
    validate_lens_answer_core_payload(
        load_lens_answer_core_payload(path),
        path=Path(path),
        repo_root=repo_root,
    )


def iter_lens_answer_core_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
    repo_root: Path | None = None,
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
        "source_attention_map",
        "source_attention_map_render_sha256",
        "source_lens_probe",
        "answer_core",
        "expected_inclusions",
        "expected_exclusions",
        "lens_effect",
    )
    yield from _unknown_fields(payload, TOP_LEVEL_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return

    if _string(payload.get("schema_version")) != LENS_ANSWER_CORE_SCHEMA_VERSION:
        yield f"{path / 'schema_version'}: must be {LENS_ANSWER_CORE_SCHEMA_VERSION}"
    if _string(payload.get("status")) not in ALLOWED_STATUS:
        yield f"{path / 'status'}: status must be research_only"
    if _string(payload.get("runtime_policy")) not in ALLOWED_RUNTIME_POLICY:
        yield f"{path / 'runtime_policy'}: runtime_policy must be runtime_dormant"
    case_id = _string(payload.get("case_id"))
    if not case_id.strip():
        yield f"{path / 'case_id'}: case_id must be non-empty"
    if not _string(payload.get("lens_pack")).strip():
        yield f"{path / 'lens_pack'}: lens_pack must be non-empty"

    answer = _string(payload.get("answer_core"))
    yield from _validate_public_answer(answer, path / "answer_core")
    yield from _validate_expected_lists(payload, answer, path)
    yield from _validate_lens_effect(payload.get("lens_effect"), path / "lens_effect")
    if repo_root is not None:
        yield from _validate_refs(payload, case_id=case_id, path=path, repo_root=repo_root)


def _validate_refs(
    payload: dict[str, object],
    *,
    case_id: str,
    path: Path,
    repo_root: Path,
) -> Iterable[str]:
    map_ref = _string(payload.get("source_attention_map"))
    map_path = repo_root / map_ref
    if not map_ref or not map_path.exists():
        yield f"{path / 'source_attention_map'}: source attention map missing"
    else:
        map_payload = load_step6_attention_map_payload(map_path)
        validate_step6_attention_map_payload(map_payload, path=map_path)
        if _string(map_payload.get("case_id")) != case_id:
            yield f"{path / 'source_attention_map'}: case_id mismatch"
        expected_hash = hashlib.sha256(
            render_step6_attention_map(map_payload).encode("utf-8")
        ).hexdigest()
        if _string(payload.get("source_attention_map_render_sha256")) != expected_hash:
            yield f"{path / 'source_attention_map_render_sha256'}: hash mismatch"

    probe_ref = _string(payload.get("source_lens_probe"))
    probe_path = repo_root / probe_ref
    if not probe_ref or not probe_path.exists():
        yield f"{path / 'source_lens_probe'}: source lens probe missing"
    else:
        probe_payload = load_lens_probe_payload(probe_path)
        validate_lens_probe_payload(probe_payload, path=probe_path)
        if _string(probe_payload.get("case_id")) != case_id:
            yield f"{path / 'source_lens_probe'}: case_id mismatch"
        if _string(probe_payload.get("lens_pack")) != _string(payload.get("lens_pack")):
            yield f"{path / 'source_lens_probe'}: lens_pack mismatch"


def _validate_public_answer(answer: str, path: Path) -> Iterable[str]:
    if not answer.strip():
        yield f"{path}: answer_core must be non-empty"
        return
    if len(answer) > MAX_ANSWER_CORE_CHARS:
        yield f"{path}: answer_core exceeds {MAX_ANSWER_CORE_CHARS} chars"
    try:
        validate_public_answer_hygiene(answer)
    except ValueError as exc:
        yield f"{path}: {exc}"
    lowered = answer.lower()
    for term in EXTRA_FORBIDDEN_PUBLIC_TERMS:
        if term in lowered:
            yield f"{path}: private lens machinery term leaked: {term}"


def _validate_expected_lists(
    payload: dict[str, object],
    answer: str,
    path: Path,
) -> Iterable[str]:
    inclusions = payload.get("expected_inclusions")
    exclusions = payload.get("expected_exclusions")
    if not _non_empty_string_list(inclusions):
        yield f"{path / 'expected_inclusions'}: must be a non-empty string list"
    else:
        lowered = answer.lower()
        for inclusion in inclusions:
            assert isinstance(inclusion, str)
            if inclusion.lower() not in lowered:
                yield f"{path / 'expected_inclusions'}: expected inclusion missing: {inclusion}"
    if not isinstance(exclusions, list) or not all(
        isinstance(item, str) and item.strip() for item in exclusions
    ):
        yield f"{path / 'expected_exclusions'}: must be a string list"
    else:
        lowered = answer.lower()
        for exclusion in exclusions:
            assert isinstance(exclusion, str)
            if exclusion.lower() in lowered:
                yield f"{path / 'expected_exclusions'}: forbidden exclusion present: {exclusion}"


def _validate_lens_effect(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: lens_effect must be an object"
        return
    required = tuple(LENS_EFFECT_FIELDS)
    yield from _unknown_fields(value, LENS_EFFECT_FIELDS, path)
    yield from _missing_fields(value, required, path)
    if any(field not in value for field in required):
        return
    for field in required:
        if not _non_empty_string_list(value.get(field)):
            yield f"{path / field}: must be a non-empty string list"


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
    parser.add_argument("--repo-root", type=Path)
    args = parser.parse_args(argv)
    for path in args.paths:
        validate_lens_answer_core_file(path, repo_root=args.repo_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
