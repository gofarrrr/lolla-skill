#!/usr/bin/env python3
"""Research-only semi-blind comparison gate for pre-Step-6 answer cores.

This module validates a small comparison record for control vs raw-only vs
rendered-hybrid answer cores. It is deliberately outside the live pipeline: it
does not build handoffs, launch workers, route /lolla, or decide product
promotion.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, Sequence

from pre_step6_pressure_card_consumption import (
    load_pressure_consumption_payload,
    validate_rendered_hybrid_answer_core_payload,
)
from pre_step6_raw_artifacts import (
    load_answer_comparison_payload,
    load_answer_core_payload,
    validate_answer_comparison_payload,
    validate_answer_core_payload,
)


SEMI_BLIND_COMPARISON_SCHEMA_VERSION = "pre_step6_semi_blind_comparison.v1"
ALLOWED_STATUS = frozenset({"research_only"})
ALLOWED_RUNTIME_POLICY = frozenset({"runtime_dormant"})
ALLOWED_COMPARISON_KINDS = frozenset(
    {"semi_blind_local_rubric", "semi_blind_native_judge"}
)
ALLOWED_LABELS = frozenset({"A", "B", "C"})
ALLOWED_ARMS = frozenset({"control", "raw", "rendered_hybrid"})
ALLOWED_WINNER_LABELS = frozenset({"A", "B", "C", "tie"})
ALLOWED_AGGREGATE_DECISIONS = frozenset(
    {"control_wins", "raw_wins", "rendered_hybrid_wins", "tie_stop"}
)
ALLOWED_PROMOTION_READS = frozenset({"pass_to_replay", "retest", "stop"})
REQUIRED_CRITERIA = (
    "decision_usefulness",
    "source_grounding",
    "overclaim_risk",
    "answer_length_cognitive_load",
    "machinery_hygiene",
    "conflict_preservation",
    "duplicate_demotion",
    "unforcedness",
)
TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "comparison_kind",
        "blind_seed",
        "candidate_refs",
        "blind_map",
        "criteria",
        "tie_break_rule",
        "aggregate_winner_label",
        "aggregate_decision",
        "promotion_read",
        "notes",
    }
)
CANDIDATE_REF_FIELDS = frozenset(
    {
        "control_answer_comparison",
        "raw_answer_core",
        "rendered_hybrid_answer_core",
    }
)
CRITERION_FIELDS = frozenset(
    {"criterion_id", "question", "winner_label", "evidence_by_label", "rationale"}
)


class SemiBlindComparisonValidationError(ValueError):
    pass


def load_semi_blind_comparison_payload(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SemiBlindComparisonValidationError(f"{path}: payload must be an object")
    return payload


def validate_semi_blind_comparison_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
    repo_root: Path | None = None,
) -> None:
    errors = list(
        iter_semi_blind_comparison_errors(
            payload,
            path=Path(path),
            repo_root=repo_root,
        )
    )
    if errors:
        raise SemiBlindComparisonValidationError("; ".join(errors))


def validate_semi_blind_comparison_file(
    path: Path,
    *,
    repo_root: Path | None = None,
) -> None:
    validate_semi_blind_comparison_payload(
        load_semi_blind_comparison_payload(path),
        path=Path(path),
        repo_root=repo_root,
    )


def iter_semi_blind_comparison_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
    repo_root: Path | None = None,
) -> Iterable[str]:
    required = (
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "comparison_kind",
        "blind_seed",
        "candidate_refs",
        "blind_map",
        "criteria",
        "tie_break_rule",
        "aggregate_winner_label",
        "aggregate_decision",
        "promotion_read",
    )
    yield from _unknown_fields(payload, TOP_LEVEL_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return

    if _string(payload.get("schema_version")) != SEMI_BLIND_COMPARISON_SCHEMA_VERSION:
        yield f"{path}: schema_version must be {SEMI_BLIND_COMPARISON_SCHEMA_VERSION}"
    if _string(payload.get("status")) not in ALLOWED_STATUS:
        yield f"{path / 'status'}: status must be research_only"
    if _string(payload.get("runtime_policy")) not in ALLOWED_RUNTIME_POLICY:
        yield f"{path / 'runtime_policy'}: runtime_policy must be runtime_dormant"
    if not _string(payload.get("case_id")).strip():
        yield f"{path / 'case_id'}: case_id must be non-empty"
    if _string(payload.get("comparison_kind")) not in ALLOWED_COMPARISON_KINDS:
        yield f"{path / 'comparison_kind'}: unknown comparison_kind"
    if not isinstance(payload.get("blind_seed"), int):
        yield f"{path / 'blind_seed'}: blind_seed must be an integer"

    case_id = _string(payload.get("case_id"))
    yield from _validate_candidate_refs(
        payload.get("candidate_refs"),
        path=path / "candidate_refs",
        case_id=case_id,
        repo_root=repo_root,
    )
    yield from _validate_blind_map(payload.get("blind_map"), path=path / "blind_map")
    yield from _validate_criteria(payload.get("criteria"), path=path / "criteria")

    if _string(payload.get("tie_break_rule")) != "rendered_must_beat_or_simplify":
        yield f"{path / 'tie_break_rule'}: must be rendered_must_beat_or_simplify"

    aggregate_label = _string(payload.get("aggregate_winner_label"))
    if aggregate_label not in ALLOWED_WINNER_LABELS:
        yield f"{path / 'aggregate_winner_label'}: unknown aggregate_winner_label"

    decision = _string(payload.get("aggregate_decision"))
    if decision not in ALLOWED_AGGREGATE_DECISIONS:
        yield f"{path / 'aggregate_decision'}: unknown aggregate_decision '{decision}'"
    else:
        expected = score_semi_blind_comparison(payload)["aggregate_decision"]
        if decision != expected:
            yield (
                f"{path / 'aggregate_decision'}: aggregate_decision must be "
                f"{expected} from criterion winners"
            )

    promotion_read = _string(payload.get("promotion_read"))
    if promotion_read not in ALLOWED_PROMOTION_READS:
        yield f"{path / 'promotion_read'}: unknown promotion_read '{promotion_read}'"
    elif promotion_read == "pass_to_replay" and decision != "rendered_hybrid_wins":
        yield (
            f"{path / 'promotion_read'}: pass_to_replay requires "
            "rendered_hybrid_wins"
        )


def score_semi_blind_comparison(payload: dict[str, object]) -> dict[str, object]:
    label_to_arm = payload.get("blind_map")
    criteria = payload.get("criteria")
    arm_counts = {"control": 0, "raw": 0, "rendered_hybrid": 0}
    label_counts = {"A": 0, "B": 0, "C": 0, "tie": 0}

    if isinstance(criteria, list) and isinstance(label_to_arm, dict):
        for criterion in criteria:
            if not isinstance(criterion, dict):
                continue
            winner = _string(criterion.get("winner_label"))
            if winner == "tie":
                label_counts["tie"] += 1
                continue
            if winner not in ALLOWED_LABELS:
                continue
            label_counts[winner] += 1
            arm = _string(label_to_arm.get(winner))
            if arm in arm_counts:
                arm_counts[arm] += 1

    max_count = max(arm_counts.values())
    leaders = [arm for arm, count in arm_counts.items() if count == max_count]
    if max_count == 0 or len(leaders) != 1:
        criterion_count_decision = "tie_stop"
    else:
        criterion_count_decision = f"{leaders[0]}_wins"

    aggregate_label = _string(payload.get("aggregate_winner_label"))
    if aggregate_label == "tie" or not isinstance(label_to_arm, dict):
        aggregate = "tie_stop"
    else:
        aggregate_arm = _string(label_to_arm.get(aggregate_label))
        aggregate = (
            f"{aggregate_arm}_wins" if aggregate_arm in arm_counts else "tie_stop"
        )

    return {
        **arm_counts,
        "tie": label_counts["tie"],
        "label_counts": label_counts,
        "criterion_count_decision": criterion_count_decision,
        "aggregate_decision": aggregate,
    }


def _validate_candidate_refs(
    value: object,
    *,
    path: Path,
    case_id: str,
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

    control_ref = _string(value.get("control_answer_comparison"))
    if control_ref:
        control_path = repo_root / control_ref
        if not control_path.exists():
            yield f"{path / 'control_answer_comparison'}: control comparison missing"
        else:
            control_payload = load_answer_comparison_payload(control_path)
            validate_answer_comparison_payload(
                control_payload,
                path=control_path,
                repo_root=repo_root,
            )
            if _string(control_payload.get("case_id")) != case_id:
                yield f"{path / 'control_answer_comparison'}: case_id mismatch"

    raw_ref = _string(value.get("raw_answer_core"))
    if raw_ref:
        raw_path = repo_root / raw_ref
        if not raw_path.exists():
            yield f"{path / 'raw_answer_core'}: raw answer core missing"
        else:
            raw_payload = load_answer_core_payload(raw_path)
            validate_answer_core_payload(raw_payload, path=raw_path, repo_root=repo_root)
            if _string(raw_payload.get("case_id")) != case_id:
                yield f"{path / 'raw_answer_core'}: case_id mismatch"

    rendered_ref = _string(value.get("rendered_hybrid_answer_core"))
    if rendered_ref:
        rendered_path = repo_root / rendered_ref
        if not rendered_path.exists():
            yield f"{path / 'rendered_hybrid_answer_core'}: rendered core missing"
        else:
            rendered_payload = load_pressure_consumption_payload(rendered_path)
            validate_rendered_hybrid_answer_core_payload(
                rendered_payload,
                path=rendered_path,
                repo_root=repo_root,
            )
            if _string(rendered_payload.get("case_id")) != case_id:
                yield f"{path / 'rendered_hybrid_answer_core'}: case_id mismatch"


def _validate_blind_map(value: object, *, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: blind_map must be an object"
        return
    if set(value) != ALLOWED_LABELS:
        yield f"{path}: blind_map labels must be exactly A, B, C"
    arms = [_string(value.get(label)) for label in sorted(ALLOWED_LABELS)]
    unknown = [arm for arm in arms if arm not in ALLOWED_ARMS]
    if unknown:
        yield f"{path}: blind_map contains unknown arm(s): {', '.join(unknown)}"
    if set(arms) != ALLOWED_ARMS:
        yield f"{path}: blind_map arms must be exactly control, raw, rendered_hybrid"


def _validate_criteria(value: object, *, path: Path) -> Iterable[str]:
    if not isinstance(value, list):
        yield f"{path}: criteria must be a list"
        return
    ids = [
        _string(item.get("criterion_id")) if isinstance(item, dict) else ""
        for item in value
    ]
    if tuple(ids) != REQUIRED_CRITERIA:
        yield f"{path}: criteria must match the required semi-blind rubric order"
    for index, criterion in enumerate(value):
        item_path = path / f"criteria[{index}]"
        if not isinstance(criterion, dict):
            yield f"{item_path}: criterion must be an object"
            continue
        yield from _validate_criterion(criterion, path=item_path)


def _validate_criterion(
    criterion: dict[str, object],
    *,
    path: Path,
) -> Iterable[str]:
    required = ("criterion_id", "question", "winner_label", "evidence_by_label", "rationale")
    yield from _unknown_fields(criterion, CRITERION_FIELDS, path)
    yield from _missing_fields(criterion, required, path)
    if any(field not in criterion for field in required):
        return
    if _string(criterion.get("criterion_id")) not in REQUIRED_CRITERIA:
        yield f"{path / 'criterion_id'}: unknown criterion_id"
    if not _string(criterion.get("question")).strip():
        yield f"{path / 'question'}: question must be non-empty"
    if _string(criterion.get("winner_label")) not in ALLOWED_WINNER_LABELS:
        yield f"{path / 'winner_label'}: unknown winner_label"
    evidence = criterion.get("evidence_by_label")
    if not isinstance(evidence, dict):
        yield f"{path / 'evidence_by_label'}: evidence_by_label must be an object"
    elif set(evidence) != ALLOWED_LABELS:
        yield f"{path / 'evidence_by_label'}: evidence labels must be exactly A, B, C"
    else:
        for label in sorted(ALLOWED_LABELS):
            if not _string(evidence.get(label)).strip():
                yield f"{path / 'evidence_by_label' / label}: evidence must be non-empty"
    if not _string(criterion.get("rationale")).strip():
        yield f"{path / 'rationale'}: rationale must be non-empty"


def _missing_fields(
    payload: dict[str, object],
    required: Sequence[str],
    path: Path,
) -> Iterable[str]:
    for field in required:
        if field not in payload:
            yield f"{path}: missing required field '{field}'"


def _unknown_fields(
    payload: dict[str, object],
    allowed: frozenset[str],
    path: Path,
) -> Iterable[str]:
    for field in sorted(set(payload) - allowed):
        yield f"{path}: unknown field '{field}'"


def _string(value: object) -> str:
    return value if isinstance(value, str) else ""


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate research-only pre-Step-6 semi-blind comparisons."
    )
    parser.add_argument("path", type=Path)
    parser.add_argument("--repo-root", type=Path)
    args = parser.parse_args(argv)

    validate_semi_blind_comparison_file(args.path, repo_root=args.repo_root)
    score = score_semi_blind_comparison(load_semi_blind_comparison_payload(args.path))
    print(
        f"valid semi-blind comparison: {args.path} "
        f"control={score['control']} raw={score['raw']} "
        f"rendered_hybrid={score['rendered_hybrid']} tie={score['tie']} "
        f"decision={score['aggregate_decision']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
