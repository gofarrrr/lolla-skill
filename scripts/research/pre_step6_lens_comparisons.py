#!/usr/bin/env python3
"""Research-only comparison gate for lens-enhanced Step 6 answer cores."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, Sequence

from pre_step6_lens_answer_cores import (
    load_lens_answer_core_payload,
    validate_lens_answer_core_payload,
)
from pre_step6_lens_probes import load_lens_probe_payload, validate_lens_probe_payload
from pre_step6_portfolio_answer_cores import (
    load_portfolio_answer_core_payload,
    validate_portfolio_answer_core_payload,
)
from pre_step6_pressure_card_consumption import (
    load_pressure_consumption_payload,
    validate_rendered_hybrid_answer_core_payload,
)


LENS_COMPARISON_SCHEMA_VERSION = "pre_step6_lens_comparison.v1"
ALLOWED_STATUS = frozenset({"research_only"})
ALLOWED_RUNTIME_POLICY = frozenset({"runtime_dormant"})
ALLOWED_LENS_PACKS = frozenset(
    {
        "bevelin_seeking_wisdom_v0",
        "polya_problem_solving_v0",
    }
)
ALLOWED_COMPARISON_KINDS = frozenset(
    {
        "bevelin_lens_local_rubric",
        "polya_lens_local_rubric",
    }
)
ALLOWED_ARMS = frozenset({"rendered_hybrid", "portfolio_base", "lens", "tie"})
ALLOWED_DECISIONS = frozenset(
    {
        "lens_improves",
        "lens_retest",
        "lens_boundary_case",
        "lens_discard",
    }
)
ALLOWED_PROMOTION_READS = frozenset({"expand_replay", "retest", "stop", "discard"})
REQUIRED_CRITERIA = (
    "decision_usefulness",
    "source_grounding",
    "overclaim_risk",
    "answer_length_cognitive_load",
    "machinery_hygiene",
    "conflict_preservation",
    "edge_pressure_preservation",
    "breadth_depth_preservation",
    "premature_pruning_risk",
    "negative_control_discipline",
)
TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "experiment_id",
        "case_id",
        "comparison_kind",
        "lens_pack",
        "candidate_refs",
        "criteria",
        "tie_break_rule",
        "aggregate_winner_arm",
        "aggregate_decision",
        "promotion_read",
        "notes",
    }
)
CANDIDATE_REF_FIELDS = frozenset(
    {
        "rendered_hybrid_answer_core",
        "portfolio_base_answer_core",
        "lens_answer_core",
        "lens_probe",
    }
)
CRITERION_FIELDS = frozenset(
    {"criterion_id", "question", "winner_arm", "evidence_by_arm", "rationale"}
)


class LensComparisonValidationError(ValueError):
    pass


def load_lens_comparison_payload(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise LensComparisonValidationError(f"{path}: payload must be an object")
    return payload


def validate_lens_comparison_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
    repo_root: Path | None = None,
) -> None:
    errors = list(
        iter_lens_comparison_errors(payload, path=Path(path), repo_root=repo_root)
    )
    if errors:
        raise LensComparisonValidationError("; ".join(errors))


def validate_lens_comparison_file(
    path: Path,
    *,
    repo_root: Path | None = None,
) -> None:
    validate_lens_comparison_payload(
        load_lens_comparison_payload(path),
        path=Path(path),
        repo_root=repo_root,
    )


def iter_lens_comparison_errors(
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
        "experiment_id",
        "case_id",
        "comparison_kind",
        "lens_pack",
        "candidate_refs",
        "criteria",
        "tie_break_rule",
        "aggregate_winner_arm",
        "aggregate_decision",
        "promotion_read",
    )
    yield from _unknown_fields(payload, TOP_LEVEL_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return

    if _string(payload.get("schema_version")) != LENS_COMPARISON_SCHEMA_VERSION:
        yield f"{path / 'schema_version'}: must be {LENS_COMPARISON_SCHEMA_VERSION}"
    if _string(payload.get("status")) not in ALLOWED_STATUS:
        yield f"{path / 'status'}: status must be research_only"
    if _string(payload.get("runtime_policy")) not in ALLOWED_RUNTIME_POLICY:
        yield f"{path / 'runtime_policy'}: runtime_policy must be runtime_dormant"
    if not _string(payload.get("experiment_id")).strip():
        yield f"{path / 'experiment_id'}: experiment_id must be non-empty"
    case_id = _string(payload.get("case_id"))
    if not case_id.strip():
        yield f"{path / 'case_id'}: case_id must be non-empty"
    if _string(payload.get("comparison_kind")) not in ALLOWED_COMPARISON_KINDS:
        yield f"{path / 'comparison_kind'}: unknown comparison_kind"
    if _string(payload.get("lens_pack")) not in ALLOWED_LENS_PACKS:
        yield f"{path / 'lens_pack'}: unknown lens_pack"

    yield from _validate_candidate_refs(
        payload.get("candidate_refs"),
        case_id=case_id,
        lens_pack=_string(payload.get("lens_pack")),
        path=path / "candidate_refs",
        repo_root=repo_root,
    )
    yield from _validate_criteria(payload.get("criteria"), path / "criteria")

    if _string(payload.get("tie_break_rule")) != "lens_must_add_edge_without_pruning":
        yield f"{path / 'tie_break_rule'}: must be lens_must_add_edge_without_pruning"
    if _string(payload.get("aggregate_winner_arm")) not in ALLOWED_ARMS:
        yield f"{path / 'aggregate_winner_arm'}: unknown aggregate_winner_arm"

    decision = _string(payload.get("aggregate_decision"))
    expected = _expected_decision(payload)
    if decision not in ALLOWED_DECISIONS:
        yield f"{path / 'aggregate_decision'}: unknown aggregate_decision"
    elif decision != expected:
        yield f"{path / 'aggregate_decision'}: aggregate_decision must be {expected}"

    promotion_read = _string(payload.get("promotion_read"))
    if promotion_read not in ALLOWED_PROMOTION_READS:
        yield f"{path / 'promotion_read'}: unknown promotion_read"
    elif promotion_read == "expand_replay" and decision != "lens_improves":
        yield f"{path / 'promotion_read'}: expand_replay requires lens_improves"
    elif promotion_read == "discard" and decision != "lens_discard":
        yield f"{path / 'promotion_read'}: discard requires lens_discard"


def score_lens_comparison(payload: dict[str, object]) -> dict[str, object]:
    criteria = payload.get("criteria")
    counts = {
        "rendered_hybrid": 0,
        "portfolio_base": 0,
        "lens": 0,
        "tie": 0,
    }
    if isinstance(criteria, list):
        for criterion in criteria:
            if not isinstance(criterion, dict):
                continue
            winner = _string(criterion.get("winner_arm"))
            if winner in counts:
                counts[winner] += 1
    return {**counts, "aggregate_decision": _expected_decision(payload)}


def _expected_decision(payload: dict[str, object]) -> str:
    winner = _string(payload.get("aggregate_winner_arm"))
    if winner == "lens":
        return "lens_improves"
    if _criteria_lens_win_count(payload) > 0:
        return "lens_boundary_case"
    if winner == "tie":
        return "lens_retest"
    return "lens_discard"


def _criteria_lens_win_count(payload: dict[str, object]) -> int:
    criteria = payload.get("criteria")
    if not isinstance(criteria, list):
        return 0
    return sum(
        1
        for criterion in criteria
        if isinstance(criterion, dict)
        and _string(criterion.get("winner_arm")) == "lens"
    )


def _validate_candidate_refs(
    value: object,
    *,
    case_id: str,
    lens_pack: str,
    path: Path,
    repo_root: Path | None,
) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: candidate_refs must be an object"
        return
    yield from _unknown_fields(value, CANDIDATE_REF_FIELDS, path)
    yield from _missing_fields(value, tuple(CANDIDATE_REF_FIELDS), path)
    if any(field not in value for field in CANDIDATE_REF_FIELDS):
        return
    for field in CANDIDATE_REF_FIELDS:
        if not _string(value.get(field)).strip():
            yield f"{path / field}: must be non-empty"
    if repo_root is None:
        return

    rendered_ref = _string(value.get("rendered_hybrid_answer_core"))
    rendered_path = repo_root / rendered_ref
    if rendered_ref and rendered_path.exists():
        rendered_payload = load_pressure_consumption_payload(rendered_path)
        validate_rendered_hybrid_answer_core_payload(
            rendered_payload,
            path=rendered_path,
            repo_root=repo_root,
        )
    else:
        yield f"{path / 'rendered_hybrid_answer_core'}: answer core missing"

    portfolio_ref = _string(value.get("portfolio_base_answer_core"))
    portfolio_path = repo_root / portfolio_ref
    if portfolio_ref and portfolio_path.exists():
        portfolio_payload = load_portfolio_answer_core_payload(portfolio_path)
        validate_portfolio_answer_core_payload(
            portfolio_payload,
            path=portfolio_path,
            repo_root=repo_root,
        )
        if _string(portfolio_payload.get("case_id")) != case_id:
            yield f"{path / 'portfolio_base_answer_core'}: case_id mismatch"
    else:
        yield f"{path / 'portfolio_base_answer_core'}: answer core missing"

    lens_ref = _string(value.get("lens_answer_core"))
    lens_path = repo_root / lens_ref
    if lens_ref and lens_path.exists():
        lens_payload = load_lens_answer_core_payload(lens_path)
        validate_lens_answer_core_payload(
            lens_payload,
            path=lens_path,
            repo_root=repo_root,
        )
        if _string(lens_payload.get("case_id")) != case_id:
            yield f"{path / 'lens_answer_core'}: case_id mismatch"
        if _string(lens_payload.get("lens_pack")) != lens_pack:
            yield f"{path / 'lens_answer_core'}: lens_pack mismatch"
    else:
        yield f"{path / 'lens_answer_core'}: answer core missing"

    probe_ref = _string(value.get("lens_probe"))
    probe_path = repo_root / probe_ref
    if probe_ref and probe_path.exists():
        probe_payload = load_lens_probe_payload(probe_path)
        validate_lens_probe_payload(probe_payload, path=probe_path)
        if _string(probe_payload.get("case_id")) != case_id:
            yield f"{path / 'lens_probe'}: case_id mismatch"
        if _string(probe_payload.get("lens_pack")) != lens_pack:
            yield f"{path / 'lens_probe'}: lens_pack mismatch"
    else:
        yield f"{path / 'lens_probe'}: lens probe missing"


def _validate_criteria(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, list):
        yield f"{path}: criteria must be a list"
        return
    ids = [
        _string(item.get("criterion_id")) if isinstance(item, dict) else ""
        for item in value
    ]
    if tuple(ids) != REQUIRED_CRITERIA:
        yield f"{path}: criteria must match the required rubric order"
    for index, criterion in enumerate(value):
        item_path = path / f"[{index}]"
        if not isinstance(criterion, dict):
            yield f"{item_path}: criterion must be an object"
            continue
        yield from _unknown_fields(criterion, CRITERION_FIELDS, item_path)
        yield from _missing_fields(criterion, tuple(CRITERION_FIELDS), item_path)
        if any(field not in criterion for field in CRITERION_FIELDS):
            continue
        if _string(criterion.get("winner_arm")) not in ALLOWED_ARMS:
            yield f"{item_path / 'winner_arm'}: unknown winner_arm"
        for field in ("question", "rationale"):
            if not _string(criterion.get(field)).strip():
                yield f"{item_path / field}: must be non-empty"
        yield from _validate_evidence_by_arm(
            criterion.get("evidence_by_arm"),
            item_path / "evidence_by_arm",
        )


def _validate_evidence_by_arm(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: evidence_by_arm must be an object"
        return
    required = ("rendered_hybrid", "portfolio_base", "lens")
    yield from _missing_fields(value, required, path)
    for field in required:
        if not _string(value.get(field)).strip():
            yield f"{path / field}: must be non-empty"
    unknown = sorted(set(value) - set(required))
    for field in unknown:
        yield f"{path / field}: unknown field"


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


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--repo-root", type=Path)
    args = parser.parse_args(argv)
    for path in args.paths:
        validate_lens_comparison_file(path, repo_root=args.repo_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
