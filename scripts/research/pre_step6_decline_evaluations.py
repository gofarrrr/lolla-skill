#!/usr/bin/env python3
"""Research-only replay-style evaluation for no-rendered-handoff declines.

This validates whether a generated or manual no-rendered-handoff candidate can
count as a healthy decline. It does not require a rendered candidate, run source
audits, route /lolla, launch workers, build bundles, or promote runtime.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, Sequence

from pre_step6_no_rendered_handoffs import (
    load_no_rendered_handoff_payload,
    validate_no_rendered_handoff_payload,
)
from pre_step6_raw_artifacts import (
    load_answer_comparison_payload,
    validate_answer_comparison_payload,
)


DECLINE_EVALUATION_SCHEMA_VERSION = "pre_step6_decline_evaluation.v1"

ALLOWED_STATUS = frozenset({"research_only"})
ALLOWED_RUNTIME_POLICY = frozenset({"runtime_dormant"})
ALLOWED_EVALUATION_MODES = frozenset({"off_by_default_static_decline_replay"})
ALLOWED_DECLINE_EVALUATION_DECISIONS = frozenset(
    {"healthy_decline", "retest_decline", "missed_decline"}
)
ALLOWED_PRODUCT_PROMOTION = frozenset({"blocked"})
ALLOWED_GENERATOR_NEXT_STEPS = frozenset({"blocked", "schema_only_next"})
ALLOWED_CHECK_SEVERITIES = frozenset({"pass", "watch", "fail"})
ALLOWED_NATURALNESS_DEBT_AVOIDED_LEVELS = frozenset({"none", "low", "medium", "high"})

REQUIRED_MISS_CHECKS = (
    "no_critical_pressure_lost",
    "control_sufficiency_survives",
    "receipt_stayed_small",
    "reactivation_condition_clear",
)
TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "evaluation_mode",
        "decline_candidate_ref",
        "comparison_ref",
        "gates",
        "outcome",
        "naturalness_debt_avoided",
        "miss_checks",
        "notes",
    }
)
GATE_FIELDS = frozenset(
    {
        "decline_candidate_loaded",
        "simpler_comparison_recorded",
        "rendered_candidate_required",
        "source_overclaim_audit_required",
        "runtime_wiring_allowed",
        "product_promotion_allowed",
        "generator_implementation_allowed",
    }
)
OUTCOME_FIELDS = frozenset(
    {
        "comparison_decision",
        "decline_evaluation_decision",
        "product_promotion",
        "generator_next_step",
    }
)
NATURALNESS_DEBT_AVOIDED_FIELDS = frozenset({"level", "evidence"})
MISS_CHECK_FIELDS = frozenset({"check_id", "severity", "evidence"})


class DeclineEvaluationValidationError(ValueError):
    pass


def load_decline_evaluation_payload(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise DeclineEvaluationValidationError(f"{path}: payload must be an object")
    return payload


def validate_decline_evaluation_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
    repo_root: Path | None = None,
) -> None:
    errors = list(
        iter_decline_evaluation_errors(payload, path=Path(path), repo_root=repo_root)
    )
    if errors:
        raise DeclineEvaluationValidationError("; ".join(errors))


def validate_decline_evaluation_file(
    path: Path,
    *,
    repo_root: Path | None = None,
) -> None:
    validate_decline_evaluation_payload(
        load_decline_evaluation_payload(path),
        path=Path(path),
        repo_root=repo_root,
    )


def summarize_decline_evaluation(payload: dict[str, object]) -> dict[str, object]:
    outcome = payload.get("outcome") if isinstance(payload.get("outcome"), dict) else {}
    debt = (
        payload.get("naturalness_debt_avoided")
        if isinstance(payload.get("naturalness_debt_avoided"), dict)
        else {}
    )
    return {
        "case_id": _string(payload.get("case_id")),
        "comparison_decision": _string(outcome.get("comparison_decision")),
        "decline_evaluation_decision": _string(
            outcome.get("decline_evaluation_decision")
        ),
        "generator_next_step": _string(outcome.get("generator_next_step")),
        "naturalness_debt_avoided": _string(debt.get("level")),
    }


def iter_decline_evaluation_errors(
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
        "evaluation_mode",
        "decline_candidate_ref",
        "comparison_ref",
        "gates",
        "outcome",
        "naturalness_debt_avoided",
        "miss_checks",
    )
    yield from _unknown_fields(payload, TOP_LEVEL_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return

    if _string(payload.get("schema_version")) != DECLINE_EVALUATION_SCHEMA_VERSION:
        yield f"{path}: schema_version must be {DECLINE_EVALUATION_SCHEMA_VERSION}"
    if _string(payload.get("status")) not in ALLOWED_STATUS:
        yield f"{path / 'status'}: status must be research_only"
    if _string(payload.get("runtime_policy")) not in ALLOWED_RUNTIME_POLICY:
        yield f"{path / 'runtime_policy'}: runtime_policy must be runtime_dormant"
    case_id = _string(payload.get("case_id"))
    if not case_id.strip():
        yield f"{path / 'case_id'}: case_id must be non-empty"
    if _string(payload.get("evaluation_mode")) not in ALLOWED_EVALUATION_MODES:
        yield f"{path / 'evaluation_mode'}: unknown evaluation_mode"

    decline_payload: dict[str, object] | None = None
    comparison_payload: dict[str, object] | None = None
    decline_ref = _string(payload.get("decline_candidate_ref"))
    comparison_ref = _string(payload.get("comparison_ref"))

    if not decline_ref.strip():
        yield f"{path / 'decline_candidate_ref'}: must be non-empty"
    elif repo_root is not None:
        decline_path = repo_root / decline_ref
        if not decline_path.exists():
            yield f"{path / 'decline_candidate_ref'}: decline candidate missing"
        else:
            decline_payload = load_no_rendered_handoff_payload(decline_path)
            validate_no_rendered_handoff_payload(
                decline_payload,
                path=decline_path,
                repo_root=repo_root,
            )
            if _string(decline_payload.get("case_id")) != case_id:
                yield f"{path / 'decline_candidate_ref'}: case_id mismatch"

    if not comparison_ref.strip():
        yield f"{path / 'comparison_ref'}: must be non-empty"
    elif repo_root is not None:
        comparison_path = repo_root / comparison_ref
        if not comparison_path.exists():
            yield f"{path / 'comparison_ref'}: comparison missing"
        else:
            comparison_payload = load_answer_comparison_payload(comparison_path)
            validate_answer_comparison_payload(
                comparison_payload,
                path=comparison_path,
                repo_root=repo_root,
            )
            if _string(comparison_payload.get("case_id")) != case_id:
                yield f"{path / 'comparison_ref'}: case_id mismatch"

    if decline_payload is not None and comparison_ref:
        source_refs = decline_payload.get("source_refs")
        if isinstance(source_refs, dict):
            decline_comparison_ref = _string(source_refs.get("control_comparison"))
            if decline_comparison_ref and decline_comparison_ref != comparison_ref:
                yield (
                    f"{path / 'comparison_ref'}: must match decline candidate "
                    "control_comparison"
                )

    comparison_decision = ""
    if comparison_payload is not None:
        comparison_decision = _string(comparison_payload.get("aggregate_decision"))

    yield from _validate_gates(payload.get("gates"), path=path / "gates")
    yield from _validate_outcome(
        payload.get("outcome"),
        path=path / "outcome",
        comparison_decision=comparison_decision,
    )
    yield from _validate_naturalness_debt_avoided(
        payload.get("naturalness_debt_avoided"),
        path=path / "naturalness_debt_avoided",
    )
    yield from _validate_miss_checks(
        payload.get("miss_checks"),
        path=path / "miss_checks",
        outcome=payload.get("outcome"),
    )

    notes = payload.get("notes")
    if notes is not None and (not isinstance(notes, str) or not notes.strip()):
        yield f"{path / 'notes'}: notes must be non-empty when present"


def _validate_gates(value: object, *, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: gates must be an object"
        return
    yield from _unknown_fields(value, GATE_FIELDS, path)
    yield from _missing_fields(value, tuple(GATE_FIELDS), path)
    if any(field not in value for field in GATE_FIELDS):
        return

    required_true = ("decline_candidate_loaded", "simpler_comparison_recorded")
    for field in required_true:
        if value.get(field) is not True:
            yield f"{path / field}: must be true"
    required_false = (
        "rendered_candidate_required",
        "source_overclaim_audit_required",
        "runtime_wiring_allowed",
        "product_promotion_allowed",
        "generator_implementation_allowed",
    )
    for field in required_false:
        if value.get(field) is not False:
            yield f"{path / field}: must be false"


def _validate_outcome(
    value: object,
    *,
    path: Path,
    comparison_decision: str,
) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: outcome must be an object"
        return
    yield from _unknown_fields(value, OUTCOME_FIELDS, path)
    yield from _missing_fields(value, tuple(OUTCOME_FIELDS), path)
    if any(field not in value for field in OUTCOME_FIELDS):
        return

    outcome_comparison = _string(value.get("comparison_decision"))
    if comparison_decision and outcome_comparison != comparison_decision:
        yield f"{path / 'comparison_decision'}: must match simpler comparison"
    decision = _string(value.get("decline_evaluation_decision"))
    if decision not in ALLOWED_DECLINE_EVALUATION_DECISIONS:
        yield f"{path / 'decline_evaluation_decision'}: unknown decision"
    if _string(value.get("product_promotion")) not in ALLOWED_PRODUCT_PROMOTION:
        yield f"{path / 'product_promotion'}: product_promotion must be blocked"
    next_step = _string(value.get("generator_next_step"))
    if next_step not in ALLOWED_GENERATOR_NEXT_STEPS:
        yield f"{path / 'generator_next_step'}: unknown generator_next_step"

    if decision == "healthy_decline":
        if outcome_comparison == "rendered_hybrid_wins":
            yield (
                f"{path / 'decline_evaluation_decision'}: healthy decline "
                "cannot rest on rendered_hybrid_wins"
            )
        if next_step != "blocked":
            yield (
                f"{path / 'generator_next_step'}: healthy decline still keeps "
                "generator implementation blocked"
            )


def _validate_naturalness_debt_avoided(
    value: object,
    *,
    path: Path,
) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: naturalness_debt_avoided must be an object"
        return
    yield from _unknown_fields(value, NATURALNESS_DEBT_AVOIDED_FIELDS, path)
    yield from _missing_fields(value, tuple(NATURALNESS_DEBT_AVOIDED_FIELDS), path)
    if any(field not in value for field in NATURALNESS_DEBT_AVOIDED_FIELDS):
        return
    if _string(value.get("level")) not in ALLOWED_NATURALNESS_DEBT_AVOIDED_LEVELS:
        yield f"{path / 'level'}: unknown level"
    if not _string(value.get("evidence")).strip():
        yield f"{path / 'evidence'}: evidence must be non-empty"


def _validate_miss_checks(
    value: object,
    *,
    path: Path,
    outcome: object,
) -> Iterable[str]:
    if not isinstance(value, list):
        yield f"{path}: miss_checks must be a list"
        return
    ids = [
        _string(item.get("check_id")) if isinstance(item, dict) else ""
        for item in value
    ]
    if tuple(ids) != REQUIRED_MISS_CHECKS:
        yield f"{path}: miss_checks must match the required order"
    has_fail = False
    for index, item in enumerate(value):
        item_path = path / f"miss_checks[{index}]"
        if not isinstance(item, dict):
            yield f"{item_path}: miss check must be an object"
            continue
        yield from _unknown_fields(item, MISS_CHECK_FIELDS, item_path)
        yield from _missing_fields(item, tuple(MISS_CHECK_FIELDS), item_path)
        if any(field not in item for field in MISS_CHECK_FIELDS):
            continue
        if _string(item.get("check_id")) not in REQUIRED_MISS_CHECKS:
            yield f"{item_path / 'check_id'}: unknown check_id"
        severity = _string(item.get("severity"))
        if severity not in ALLOWED_CHECK_SEVERITIES:
            yield f"{item_path / 'severity'}: unknown severity"
        if severity == "fail":
            has_fail = True
        if not _string(item.get("evidence")).strip():
            yield f"{item_path / 'evidence'}: evidence must be non-empty"

    if (
        has_fail
        and isinstance(outcome, dict)
        and _string(outcome.get("decline_evaluation_decision")) == "healthy_decline"
    ):
        yield f"{path}: healthy decline is invalid when a miss check failed"


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
        description="Validate research-only pre-Step-6 decline evaluation records."
    )
    parser.add_argument("path", type=Path)
    parser.add_argument("--repo-root", type=Path)
    args = parser.parse_args(argv)

    validate_decline_evaluation_file(args.path, repo_root=args.repo_root)
    summary = summarize_decline_evaluation(load_decline_evaluation_payload(args.path))
    print(
        f"valid decline evaluation: {args.path} "
        f"case={summary['case_id']} "
        f"comparison={summary['comparison_decision']} "
        f"decision={summary['decline_evaluation_decision']} "
        f"debt_avoided={summary['naturalness_debt_avoided']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
