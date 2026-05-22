#!/usr/bin/env python3
"""Research-only validation for portfolio-based Step 6 answer cores."""
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
from pre_step6_raw_artifacts import (
    MAX_ANSWER_CORE_CHARS,
    validate_public_answer_hygiene,
)


PORTFOLIO_ANSWER_CORE_SCHEMA_VERSION = "pre_step6_portfolio_answer_core.v1"
ALLOWED_STATUS = frozenset({"research_only"})
ALLOWED_RUNTIME_POLICY = frozenset({"runtime_dormant"})
TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "source_attention_map",
        "source_attention_map_render_sha256",
        "answer_core",
        "expected_inclusions",
        "expected_exclusions",
        "comparison_to_baselines",
        "notes",
    }
)
COMPARISON_FIELDS = frozenset(
    {
        "preserved_from_previous_best",
        "improved_from_portfolio",
        "kept_private_or_discarded",
    }
)
EXTRA_FORBIDDEN_PUBLIC_TERMS = (
    "attention map",
    "portfolio",
    "edge reserve",
    "active working set",
    "protected slot",
    "reasoning affordance",
    "expansion ref",
)


class PortfolioAnswerCoreValidationError(ValueError):
    pass


def load_portfolio_answer_core_payload(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise PortfolioAnswerCoreValidationError(f"{path}: payload must be an object")
    return payload


def validate_portfolio_answer_core_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
    repo_root: Path | None = None,
) -> None:
    errors = list(
        iter_portfolio_answer_core_errors(
            payload,
            path=Path(path),
            repo_root=repo_root,
        )
    )
    if errors:
        raise PortfolioAnswerCoreValidationError("; ".join(errors))


def validate_portfolio_answer_core_file(
    path: Path,
    *,
    repo_root: Path | None = None,
) -> None:
    validate_portfolio_answer_core_payload(
        load_portfolio_answer_core_payload(path),
        path=Path(path),
        repo_root=repo_root,
    )


def iter_portfolio_answer_core_errors(
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
        "source_attention_map",
        "source_attention_map_render_sha256",
        "answer_core",
        "expected_inclusions",
        "expected_exclusions",
        "comparison_to_baselines",
    )
    yield from _unknown_fields(payload, TOP_LEVEL_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return

    if _string(payload.get("schema_version")) != PORTFOLIO_ANSWER_CORE_SCHEMA_VERSION:
        yield f"{path / 'schema_version'}: must be {PORTFOLIO_ANSWER_CORE_SCHEMA_VERSION}"
    if _string(payload.get("status")) not in ALLOWED_STATUS:
        yield f"{path / 'status'}: status must be research_only"
    if _string(payload.get("runtime_policy")) not in ALLOWED_RUNTIME_POLICY:
        yield f"{path / 'runtime_policy'}: runtime_policy must be runtime_dormant"
    case_id = _string(payload.get("case_id"))
    if not case_id.strip():
        yield f"{path / 'case_id'}: case_id must be non-empty"

    answer = _string(payload.get("answer_core"))
    if not answer.strip():
        yield f"{path / 'answer_core'}: answer_core must be non-empty"
    if len(answer) > MAX_ANSWER_CORE_CHARS:
        yield f"{path / 'answer_core'}: answer_core exceeds {MAX_ANSWER_CORE_CHARS} chars"
    yield from _public_hygiene_errors(answer, path / "answer_core")

    inclusions = payload.get("expected_inclusions")
    exclusions = payload.get("expected_exclusions")
    if not _non_empty_string_list(inclusions):
        yield f"{path / 'expected_inclusions'}: must be a non-empty string list"
    else:
        for inclusion in inclusions:
            assert isinstance(inclusion, str)
            if inclusion.lower() not in answer.lower():
                yield f"{path / 'expected_inclusions'}: expected inclusion missing: {inclusion}"
    if not isinstance(exclusions, list) or not all(
        isinstance(item, str) and item.strip() for item in exclusions
    ):
        yield f"{path / 'expected_exclusions'}: must be a string list"
    else:
        for exclusion in exclusions:
            assert isinstance(exclusion, str)
            if exclusion.lower() in answer.lower():
                yield f"{path / 'expected_exclusions'}: forbidden exclusion present: {exclusion}"

    comparison = payload.get("comparison_to_baselines")
    yield from _validate_comparison(comparison, path / "comparison_to_baselines")

    if repo_root is not None:
        yield from _validate_attention_map_ref(
            payload,
            case_id=case_id,
            path=path,
            repo_root=repo_root,
        )


def _validate_attention_map_ref(
    payload: dict[str, object],
    *,
    case_id: str,
    path: Path,
    repo_root: Path,
) -> Iterable[str]:
    ref = _string(payload.get("source_attention_map"))
    if not ref.strip():
        yield f"{path / 'source_attention_map'}: must be non-empty"
        return
    map_path = repo_root / ref
    if not map_path.exists():
        yield f"{path / 'source_attention_map'}: source attention map missing"
        return
    map_payload = load_step6_attention_map_payload(map_path)
    validate_step6_attention_map_payload(map_payload, path=map_path)
    if _string(map_payload.get("case_id")) != case_id:
        yield f"{path / 'source_attention_map'}: case_id mismatch"
    rendered = render_step6_attention_map(map_payload)
    expected_hash = hashlib.sha256(rendered.encode("utf-8")).hexdigest()
    if _string(payload.get("source_attention_map_render_sha256")) != expected_hash:
        yield f"{path / 'source_attention_map_render_sha256'}: hash mismatch"


def _validate_comparison(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: comparison_to_baselines must be an object"
        return
    yield from _unknown_fields(value, COMPARISON_FIELDS, path)
    yield from _missing_fields(value, tuple(COMPARISON_FIELDS), path)
    if any(field not in value for field in COMPARISON_FIELDS):
        return
    for field in COMPARISON_FIELDS:
        if not _non_empty_string_list(value.get(field)):
            yield f"{path / field}: must be a non-empty string list"


def _public_hygiene_errors(answer: str, path: Path) -> Iterable[str]:
    try:
        validate_public_answer_hygiene(answer)
    except ValueError as exc:
        yield f"{path}: {exc}"
    lowered = answer.lower()
    for term in EXTRA_FORBIDDEN_PUBLIC_TERMS:
        if term in lowered:
            yield f"{path}: private portfolio machinery term leaked: {term}"


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
        validate_portfolio_answer_core_file(path, repo_root=args.repo_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
