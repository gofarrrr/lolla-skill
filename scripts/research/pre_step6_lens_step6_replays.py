#!/usr/bin/env python3
"""Research-only Step 6 replay records for lens-enhanced answer cores."""
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
from pre_step6_lens_answer_cores import (
    EXTRA_FORBIDDEN_PUBLIC_TERMS,
    load_lens_answer_core_payload,
    validate_lens_answer_core_payload,
)
from pre_step6_lens_comparisons import (
    load_lens_comparison_payload,
    validate_lens_comparison_payload,
)
from pre_step6_portfolio_step6_replays import (
    load_portfolio_step6_replay_payload,
    validate_portfolio_step6_replay_payload,
)
from pre_step6_raw_artifacts import MAX_ANSWER_CORE_CHARS, validate_public_answer_hygiene


LENS_STEP6_REPLAY_SCHEMA_VERSION = "pre_step6_lens_step6_replay.v1"
ALLOWED_STATUS = frozenset({"research_only"})
ALLOWED_RUNTIME_POLICY = frozenset({"runtime_dormant"})
ALLOWED_REPLAY_MODES = frozenset({"bevelin_lens_static_replay"})
ALLOWED_JUDGMENT_MODES = frozenset(
    {
        "human_static_research_judgment",
        "manual_llm_reviewer_judgment",
    }
)
ALLOWED_WINNERS = frozenset({"lens_replay", "prior_replay", "tie_retest"})
ALLOWED_REPLAY_DECISIONS = frozenset(
    {
        "pass_to_next_lens_replay",
        "pass_to_polya_comparison",
        "retest",
        "stop",
    }
)
ALLOWED_PRODUCT_PROMOTION = frozenset({"blocked"})
TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "replay_mode",
        "source_attention_map",
        "source_attention_map_render_sha256",
        "source_lens_answer_core",
        "prior_portfolio_replay",
        "lens_comparison_ref",
        "cognitive_gate",
        "replay_answer",
        "expected_inclusions",
        "expected_exclusions",
        "comparison_vs_prior_replay",
        "gates",
        "outcome",
        "notes",
    }
)
COGNITIVE_GATE_FIELDS = frozenset(
    {
        "judgment_mode",
        "cognitive_question",
        "cognitive_inputs",
        "deterministic_checks",
        "cognitive_judgment",
        "why_this_is_not_deterministic",
    }
)
COMPARISON_FIELDS = frozenset(
    {
        "winner",
        "rationale",
        "improvements",
        "regressions_or_watch_items",
    }
)
GATE_FIELDS = frozenset(
    {
        "attention_map_loaded",
        "lens_answer_core_validated",
        "prior_replay_loaded",
        "lens_comparison_validated",
        "runtime_wiring_allowed",
        "skill_update_allowed",
    }
)
OUTCOME_FIELDS = frozenset({"replay_decision", "product_promotion", "next_step"})


class LensStep6ReplayValidationError(ValueError):
    pass


def load_lens_step6_replay_payload(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise LensStep6ReplayValidationError(f"{path}: payload must be an object")
    return payload


def validate_lens_step6_replay_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
    repo_root: Path | None = None,
) -> None:
    errors = list(
        iter_lens_step6_replay_errors(payload, path=Path(path), repo_root=repo_root)
    )
    if errors:
        raise LensStep6ReplayValidationError("; ".join(errors))


def validate_lens_step6_replay_file(
    path: Path,
    *,
    repo_root: Path | None = None,
) -> None:
    validate_lens_step6_replay_payload(
        load_lens_step6_replay_payload(path),
        path=Path(path),
        repo_root=repo_root,
    )


def iter_lens_step6_replay_errors(
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
        "replay_mode",
        "source_attention_map",
        "source_attention_map_render_sha256",
        "source_lens_answer_core",
        "prior_portfolio_replay",
        "lens_comparison_ref",
        "cognitive_gate",
        "replay_answer",
        "expected_inclusions",
        "expected_exclusions",
        "comparison_vs_prior_replay",
        "gates",
        "outcome",
    )
    yield from _unknown_fields(payload, TOP_LEVEL_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return

    if _string(payload.get("schema_version")) != LENS_STEP6_REPLAY_SCHEMA_VERSION:
        yield f"{path / 'schema_version'}: must be {LENS_STEP6_REPLAY_SCHEMA_VERSION}"
    if _string(payload.get("status")) not in ALLOWED_STATUS:
        yield f"{path / 'status'}: status must be research_only"
    if _string(payload.get("runtime_policy")) not in ALLOWED_RUNTIME_POLICY:
        yield f"{path / 'runtime_policy'}: runtime_policy must be runtime_dormant"
    if _string(payload.get("replay_mode")) not in ALLOWED_REPLAY_MODES:
        yield f"{path / 'replay_mode'}: unknown replay_mode"
    case_id = _string(payload.get("case_id"))
    if not case_id.strip():
        yield f"{path / 'case_id'}: case_id must be non-empty"

    yield from _validate_cognitive_gate(payload.get("cognitive_gate"), path / "cognitive_gate")
    answer = _string(payload.get("replay_answer"))
    yield from _validate_public_answer(answer, path / "replay_answer")
    yield from _validate_expected_lists(payload, answer, path)
    yield from _validate_comparison(
        payload.get("comparison_vs_prior_replay"),
        path / "comparison_vs_prior_replay",
    )
    yield from _validate_gates(payload.get("gates"), path / "gates")
    yield from _validate_outcome(payload.get("outcome"), path / "outcome")

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
        rendered = render_step6_attention_map(map_payload)
        expected_hash = hashlib.sha256(rendered.encode("utf-8")).hexdigest()
        if _string(payload.get("source_attention_map_render_sha256")) != expected_hash:
            yield f"{path / 'source_attention_map_render_sha256'}: hash mismatch"

    lens_ref = _string(payload.get("source_lens_answer_core"))
    lens_path = repo_root / lens_ref
    if not lens_ref or not lens_path.exists():
        yield f"{path / 'source_lens_answer_core'}: lens answer core missing"
    else:
        lens_payload = load_lens_answer_core_payload(lens_path)
        validate_lens_answer_core_payload(
            lens_payload,
            path=lens_path,
            repo_root=repo_root,
        )
        if _string(lens_payload.get("case_id")) != case_id:
            yield f"{path / 'source_lens_answer_core'}: case_id mismatch"

    prior_ref = _string(payload.get("prior_portfolio_replay"))
    prior_path = repo_root / prior_ref
    if not prior_ref or not prior_path.exists():
        yield f"{path / 'prior_portfolio_replay'}: prior replay missing"
    else:
        prior_payload = load_portfolio_step6_replay_payload(prior_path)
        validate_portfolio_step6_replay_payload(
            prior_payload,
            path=prior_path,
            repo_root=repo_root,
        )
        if _string(prior_payload.get("case_id")) != case_id:
            yield f"{path / 'prior_portfolio_replay'}: case_id mismatch"

    comparison_ref = _string(payload.get("lens_comparison_ref"))
    comparison_path = repo_root / comparison_ref
    if not comparison_ref or not comparison_path.exists():
        yield f"{path / 'lens_comparison_ref'}: lens comparison missing"
    else:
        comparison_payload = load_lens_comparison_payload(comparison_path)
        validate_lens_comparison_payload(
            comparison_payload,
            path=comparison_path,
            repo_root=repo_root,
        )
        if _string(comparison_payload.get("case_id")) != case_id:
            yield f"{path / 'lens_comparison_ref'}: case_id mismatch"


def _validate_cognitive_gate(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: cognitive_gate must be an object"
        return
    required = tuple(COGNITIVE_GATE_FIELDS)
    yield from _unknown_fields(value, COGNITIVE_GATE_FIELDS, path)
    yield from _missing_fields(value, required, path)
    if any(field not in value for field in required):
        return
    if _string(value.get("judgment_mode")) not in ALLOWED_JUDGMENT_MODES:
        yield f"{path / 'judgment_mode'}: unknown judgment_mode"
    for field in ("cognitive_question", "why_this_is_not_deterministic"):
        if not _string(value.get(field)).strip():
            yield f"{path / field}: must be non-empty"
    for field in ("cognitive_inputs", "deterministic_checks", "cognitive_judgment"):
        if not _non_empty_string_list(value.get(field)):
            yield f"{path / field}: must be a non-empty string list"
    explanation = _string(value.get("why_this_is_not_deterministic")).lower()
    if "code validates" not in explanation or "quality" not in explanation:
        yield f"{path / 'why_this_is_not_deterministic'}: must separate validation from quality judgment"


def _validate_public_answer(answer: str, path: Path) -> Iterable[str]:
    if not answer.strip():
        yield f"{path}: replay_answer must be non-empty"
        return
    if len(answer) > MAX_ANSWER_CORE_CHARS:
        yield f"{path}: replay_answer exceeds {MAX_ANSWER_CORE_CHARS} chars"
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


def _validate_comparison(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: comparison_vs_prior_replay must be an object"
        return
    yield from _unknown_fields(value, COMPARISON_FIELDS, path)
    yield from _missing_fields(value, tuple(COMPARISON_FIELDS), path)
    if any(field not in value for field in COMPARISON_FIELDS):
        return
    if _string(value.get("winner")) not in ALLOWED_WINNERS:
        yield f"{path / 'winner'}: unknown winner"
    if not _string(value.get("rationale")).strip():
        yield f"{path / 'rationale'}: rationale must be non-empty"
    for field in ("improvements", "regressions_or_watch_items"):
        if not _non_empty_string_list(value.get(field)):
            yield f"{path / field}: must be a non-empty string list"


def _validate_gates(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: gates must be an object"
        return
    yield from _unknown_fields(value, GATE_FIELDS, path)
    yield from _missing_fields(value, tuple(GATE_FIELDS), path)
    if any(field not in value for field in GATE_FIELDS):
        return
    for field in GATE_FIELDS:
        if not isinstance(value.get(field), bool):
            yield f"{path / field}: must be boolean"
    if value.get("runtime_wiring_allowed") is not False:
        yield f"{path / 'runtime_wiring_allowed'}: must be false"
    if value.get("skill_update_allowed") is not False:
        yield f"{path / 'skill_update_allowed'}: must be false"


def _validate_outcome(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: outcome must be an object"
        return
    yield from _unknown_fields(value, OUTCOME_FIELDS, path)
    yield from _missing_fields(value, tuple(OUTCOME_FIELDS), path)
    if any(field not in value for field in OUTCOME_FIELDS):
        return
    if _string(value.get("replay_decision")) not in ALLOWED_REPLAY_DECISIONS:
        yield f"{path / 'replay_decision'}: unknown replay_decision"
    if _string(value.get("product_promotion")) not in ALLOWED_PRODUCT_PROMOTION:
        yield f"{path / 'product_promotion'}: product_promotion must be blocked"
    if not _string(value.get("next_step")).strip():
        yield f"{path / 'next_step'}: next_step must be non-empty"


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
        validate_lens_step6_replay_file(path, repo_root=args.repo_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
