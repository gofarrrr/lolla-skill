#!/usr/bin/env python3
"""Research-only validation for no-rendered-handoff decline receipts.

This module validates the first-class decline primitive for the pre-Step-6
research track. It does not generate rendered handoffs, route /lolla, launch
workers, build bundles, update product docs, or promote runtime behavior.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, Sequence

from pre_step6_raw_artifacts import (
    load_answer_comparison_payload,
    load_answer_core_payload,
    load_raw_artifact_payload,
    validate_answer_comparison_payload,
    validate_answer_core_payload,
    validate_raw_artifact_payload,
)
from pre_step6_replay_ledger import (
    load_replay_payload,
    validate_replay_record_payload,
    validate_source_overclaim_audit_payload,
)
from pre_step6_semi_blind_comparisons import (
    load_semi_blind_comparison_payload,
    score_semi_blind_comparison,
    validate_semi_blind_comparison_payload,
)


NO_RENDERED_HANDOFF_SCHEMA_VERSION = "pre_step6_no_rendered_handoff.v1"

ALLOWED_STATUS = frozenset({"research_only"})
ALLOWED_RUNTIME_POLICY = frozenset({"runtime_dormant"})
ALLOWED_OUTCOME_TYPES = frozenset({"no_rendered_handoff"})
ALLOWED_DECLINE_DECISIONS = frozenset(
    {"valid_research_decline", "retest_decline", "missed_decline"}
)
ALLOWED_NATURALNESS_DEBT_RISKS = frozenset({"low", "medium", "high"})
ALLOWED_EXPECTED_RESULTS = frozenset(
    {"healthy_decline", "retest_decline", "missed_decline"}
)
ALLOWED_SIMPLER_ARM_EXPECTED = frozenset(
    {"control_or_raw_wins_or_ties", "control_wins", "raw_wins", "tie"}
)

MAX_RECEIPT_FIELD_CHARS = 260
MAX_NOTES_CHARS = 700
MAX_MISS_IF_ITEMS = 5
MAX_MISS_IF_ITEM_CHARS = 180
HIDDEN_ANSWER_PLAN_PHRASES = (
    "correct answer",
    "final advice",
    "answer should",
    "should say",
    "step 6",
    "pressure card",
    "inspect_more",
    "quiet_receipts",
    "card_first",
    "worker path",
    "subagent",
    "bundle",
    "new handoff mode",
)

TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "outcome_type",
        "decline_decision",
        "source_refs",
        "decline_receipt",
        "evaluation_expectations",
        "gates",
        "notes",
    }
)
SOURCE_REF_FIELDS = frozenset(
    {
        "raw_artifact_handoff",
        "raw_answer_core",
        "control_comparison",
        "semi_blind_comparison",
        "replay_record",
        "source_overclaim_audit",
    }
)
REQUIRED_SOURCE_REF_FIELDS = (
    "raw_artifact_handoff",
    "raw_answer_core",
    "control_comparison",
)
DECLINE_RECEIPT_FIELDS = frozenset(
    {
        "decline_reason",
        "control_sufficiency",
        "missing_pressure_assessment",
        "naturalness_debt_risk",
        "expected_failure_if_forced",
        "reactivation_condition",
    }
)
EVALUATION_EXPECTATION_FIELDS = frozenset(
    {"expected_result", "simpler_arm_expected", "miss_if"}
)
GATE_FIELDS = frozenset(
    {
        "no_rendered_handoff_is_success",
        "decline_receipt_is_not_answer_plan",
        "no_pressure_surface_created",
        "runtime_wiring_allowed",
        "product_promotion_allowed",
        "generator_implementation_allowed",
    }
)


class NoRenderedHandoffValidationError(ValueError):
    pass


def load_no_rendered_handoff_payload(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise NoRenderedHandoffValidationError(f"{path}: payload must be an object")
    return payload


def validate_no_rendered_handoff_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
    repo_root: Path | None = None,
) -> None:
    errors = list(
        iter_no_rendered_handoff_errors(
            payload,
            path=Path(path),
            repo_root=repo_root,
        )
    )
    if errors:
        raise NoRenderedHandoffValidationError("; ".join(errors))


def validate_no_rendered_handoff_file(
    path: Path,
    *,
    repo_root: Path | None = None,
) -> None:
    validate_no_rendered_handoff_payload(
        load_no_rendered_handoff_payload(path),
        path=Path(path),
        repo_root=repo_root,
    )


def summarize_no_rendered_handoff(payload: dict[str, object]) -> dict[str, object]:
    receipt = (
        payload.get("decline_receipt")
        if isinstance(payload.get("decline_receipt"), dict)
        else {}
    )
    expectations = (
        payload.get("evaluation_expectations")
        if isinstance(payload.get("evaluation_expectations"), dict)
        else {}
    )
    return {
        "case_id": _string(payload.get("case_id")),
        "decline_decision": _string(payload.get("decline_decision")),
        "naturalness_debt_risk": _string(receipt.get("naturalness_debt_risk")),
        "expected_result": _string(expectations.get("expected_result")),
        "simpler_arm_expected": _string(expectations.get("simpler_arm_expected")),
    }


def iter_no_rendered_handoff_errors(
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
        "outcome_type",
        "decline_decision",
        "source_refs",
        "decline_receipt",
        "evaluation_expectations",
        "gates",
    )
    yield from _unknown_fields(payload, TOP_LEVEL_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return

    if _string(payload.get("schema_version")) != NO_RENDERED_HANDOFF_SCHEMA_VERSION:
        yield f"{path}: schema_version must be {NO_RENDERED_HANDOFF_SCHEMA_VERSION}"
    if _string(payload.get("status")) not in ALLOWED_STATUS:
        yield f"{path / 'status'}: status must be research_only"
    if _string(payload.get("runtime_policy")) not in ALLOWED_RUNTIME_POLICY:
        yield f"{path / 'runtime_policy'}: runtime_policy must be runtime_dormant"
    case_id = _string(payload.get("case_id"))
    if not case_id.strip():
        yield f"{path / 'case_id'}: case_id must be non-empty"
    if _string(payload.get("outcome_type")) not in ALLOWED_OUTCOME_TYPES:
        yield f"{path / 'outcome_type'}: outcome_type must be no_rendered_handoff"

    decline_decision = _string(payload.get("decline_decision"))
    if decline_decision not in ALLOWED_DECLINE_DECISIONS:
        yield f"{path / 'decline_decision'}: unknown decline_decision"

    source_summary = _validate_source_refs(
        payload.get("source_refs"),
        path=path / "source_refs",
        case_id=case_id,
        repo_root=repo_root,
    )
    yield from source_summary.errors

    yield from _validate_decline_receipt(
        payload.get("decline_receipt"),
        path=path / "decline_receipt",
    )
    yield from _validate_evaluation_expectations(
        payload.get("evaluation_expectations"),
        path=path / "evaluation_expectations",
        decline_decision=decline_decision,
        comparison_decision=source_summary.comparison_decision,
        replay_decision=source_summary.replay_decision,
    )
    yield from _validate_gates(payload.get("gates"), path=path / "gates")

    notes = payload.get("notes")
    if notes is not None:
        if not isinstance(notes, str) or not notes.strip():
            yield f"{path / 'notes'}: notes must be a non-empty string when present"
        elif len(notes) > MAX_NOTES_CHARS:
            yield f"{path / 'notes'}: notes must not exceed {MAX_NOTES_CHARS} chars"


class _SourceSummary:
    def __init__(
        self,
        *,
        errors: list[str],
        comparison_decision: str,
        replay_decision: str,
    ) -> None:
        self.errors = errors
        self.comparison_decision = comparison_decision
        self.replay_decision = replay_decision


def _validate_source_refs(
    value: object,
    *,
    path: Path,
    case_id: str,
    repo_root: Path | None,
) -> _SourceSummary:
    errors: list[str] = []
    comparison_decision = ""
    replay_decision = ""
    if not isinstance(value, dict):
        errors.append(f"{path}: source_refs must be an object")
        return _SourceSummary(
            errors=errors,
            comparison_decision=comparison_decision,
            replay_decision=replay_decision,
        )

    errors.extend(_unknown_fields(value, SOURCE_REF_FIELDS, path))
    errors.extend(_missing_fields(value, REQUIRED_SOURCE_REF_FIELDS, path))
    for field in SOURCE_REF_FIELDS:
        if field in value and not _string(value.get(field)).strip():
            errors.append(f"{path / field}: must be non-empty when present")
    if any(field not in value for field in REQUIRED_SOURCE_REF_FIELDS):
        return _SourceSummary(
            errors=errors,
            comparison_decision=comparison_decision,
            replay_decision=replay_decision,
        )

    has_comparison_or_replay = bool(
        _string(value.get("semi_blind_comparison")).strip()
        or _string(value.get("replay_record")).strip()
    )
    if not has_comparison_or_replay:
        errors.append(
            f"{path}: valid decline requires semi_blind_comparison or replay_record evidence"
        )

    if repo_root is None:
        return _SourceSummary(
            errors=errors,
            comparison_decision=comparison_decision,
            replay_decision=replay_decision,
        )

    raw_ref = _string(value.get("raw_artifact_handoff"))
    if raw_ref:
        raw_path = repo_root / raw_ref
        if not raw_path.exists():
            errors.append(f"{path / 'raw_artifact_handoff'}: raw handoff missing")
        else:
            raw_payload = load_raw_artifact_payload(raw_path)
            validate_raw_artifact_payload(raw_payload, path=raw_path)
            if _string(raw_payload.get("case_id")) != case_id:
                errors.append(f"{path / 'raw_artifact_handoff'}: case_id mismatch")

    raw_answer_ref = _string(value.get("raw_answer_core"))
    if raw_answer_ref:
        raw_answer_path = repo_root / raw_answer_ref
        if not raw_answer_path.exists():
            errors.append(f"{path / 'raw_answer_core'}: raw answer core missing")
        else:
            raw_answer_payload = load_answer_core_payload(raw_answer_path)
            validate_answer_core_payload(
                raw_answer_payload,
                path=raw_answer_path,
                repo_root=repo_root,
            )
            if _string(raw_answer_payload.get("case_id")) != case_id:
                errors.append(f"{path / 'raw_answer_core'}: case_id mismatch")

    control_ref = _string(value.get("control_comparison"))
    if control_ref:
        control_path = repo_root / control_ref
        if not control_path.exists():
            errors.append(f"{path / 'control_comparison'}: control comparison missing")
        else:
            control_payload = load_answer_comparison_payload(control_path)
            validate_answer_comparison_payload(
                control_payload,
                path=control_path,
                repo_root=repo_root,
            )
            if _string(control_payload.get("case_id")) != case_id:
                errors.append(f"{path / 'control_comparison'}: case_id mismatch")

    comparison_ref = _string(value.get("semi_blind_comparison"))
    if comparison_ref:
        comparison_path = repo_root / comparison_ref
        if not comparison_path.exists():
            errors.append(f"{path / 'semi_blind_comparison'}: comparison missing")
        else:
            comparison_payload = load_semi_blind_comparison_payload(comparison_path)
            validate_semi_blind_comparison_payload(
                comparison_payload,
                path=comparison_path,
                repo_root=repo_root,
            )
            if _string(comparison_payload.get("case_id")) != case_id:
                errors.append(f"{path / 'semi_blind_comparison'}: case_id mismatch")
            comparison_decision = _string(
                score_semi_blind_comparison(comparison_payload).get(
                    "aggregate_decision"
                )
            )

    replay_ref = _string(value.get("replay_record"))
    if replay_ref:
        replay_path = repo_root / replay_ref
        if not replay_path.exists():
            errors.append(f"{path / 'replay_record'}: replay record missing")
        else:
            replay_payload = load_replay_payload(replay_path)
            validate_replay_record_payload(
                replay_payload,
                path=replay_path,
                repo_root=repo_root,
            )
            if _string(replay_payload.get("case_id")) != case_id:
                errors.append(f"{path / 'replay_record'}: case_id mismatch")
            outcome = (
                replay_payload.get("outcome")
                if isinstance(replay_payload.get("outcome"), dict)
                else {}
            )
            replay_decision = _string(outcome.get("replay_decision"))

    audit_ref = _string(value.get("source_overclaim_audit"))
    if audit_ref:
        audit_path = repo_root / audit_ref
        if not audit_path.exists():
            errors.append(f"{path / 'source_overclaim_audit'}: source audit missing")
        else:
            audit_payload = load_replay_payload(audit_path)
            validate_source_overclaim_audit_payload(
                audit_payload,
                path=audit_path,
                repo_root=repo_root,
            )
            if _string(audit_payload.get("case_id")) != case_id:
                errors.append(f"{path / 'source_overclaim_audit'}: case_id mismatch")

    return _SourceSummary(
        errors=errors,
        comparison_decision=comparison_decision,
        replay_decision=replay_decision,
    )


def _validate_decline_receipt(value: object, *, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: decline_receipt must be an object"
        return
    yield from _unknown_fields(value, DECLINE_RECEIPT_FIELDS, path)
    yield from _missing_fields(value, tuple(DECLINE_RECEIPT_FIELDS), path)
    if any(field not in value for field in DECLINE_RECEIPT_FIELDS):
        return

    text_fields = (
        "decline_reason",
        "control_sufficiency",
        "missing_pressure_assessment",
        "expected_failure_if_forced",
        "reactivation_condition",
    )
    for field in text_fields:
        text = _string(value.get(field))
        if not text.strip():
            yield f"{path / field}: must be non-empty"
            continue
        if len(text) > MAX_RECEIPT_FIELD_CHARS:
            yield (
                f"{path / field}: must not exceed "
                f"{MAX_RECEIPT_FIELD_CHARS} chars"
            )
        yield from _validate_not_hidden_answer_plan(text, path=path / field)

    risk = _string(value.get("naturalness_debt_risk"))
    if risk not in ALLOWED_NATURALNESS_DEBT_RISKS:
        yield f"{path / 'naturalness_debt_risk'}: unknown naturalness_debt_risk"


def _validate_evaluation_expectations(
    value: object,
    *,
    path: Path,
    decline_decision: str,
    comparison_decision: str,
    replay_decision: str,
) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: evaluation_expectations must be an object"
        return
    yield from _unknown_fields(value, EVALUATION_EXPECTATION_FIELDS, path)
    yield from _missing_fields(value, tuple(EVALUATION_EXPECTATION_FIELDS), path)
    if any(field not in value for field in EVALUATION_EXPECTATION_FIELDS):
        return

    expected_result = _string(value.get("expected_result"))
    if expected_result not in ALLOWED_EXPECTED_RESULTS:
        yield f"{path / 'expected_result'}: unknown expected_result"
    simpler_arm_expected = _string(value.get("simpler_arm_expected"))
    if simpler_arm_expected not in ALLOWED_SIMPLER_ARM_EXPECTED:
        yield f"{path / 'simpler_arm_expected'}: unknown simpler_arm_expected"

    miss_if = value.get("miss_if")
    if not isinstance(miss_if, list):
        yield f"{path / 'miss_if'}: miss_if must be a list"
    elif not miss_if:
        yield f"{path / 'miss_if'}: miss_if must not be empty"
    elif len(miss_if) > MAX_MISS_IF_ITEMS:
        yield f"{path / 'miss_if'}: miss_if must not exceed {MAX_MISS_IF_ITEMS}"
    if isinstance(miss_if, list):
        for index, item in enumerate(miss_if):
            item_path = path / "miss_if" / str(index)
            if not isinstance(item, str) or not item.strip():
                yield f"{item_path}: item must be a non-empty string"
            elif len(item) > MAX_MISS_IF_ITEM_CHARS:
                yield (
                    f"{item_path}: item must not exceed "
                    f"{MAX_MISS_IF_ITEM_CHARS} chars"
                )
            else:
                yield from _validate_not_hidden_answer_plan(item, path=item_path)

    if decline_decision == "valid_research_decline":
        if comparison_decision == "rendered_hybrid_wins":
            yield (
                f"{path / 'expected_result'}: valid decline cannot rest on "
                "rendered_hybrid_wins"
            )
        if replay_decision and replay_decision != "stop":
            yield f"{path / 'expected_result'}: valid decline replay must be stop"
        if expected_result != "healthy_decline":
            yield (
                f"{path / 'expected_result'}: valid decline expects "
                "healthy_decline"
            )


def _validate_gates(value: object, *, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: gates must be an object"
        return
    yield from _unknown_fields(value, GATE_FIELDS, path)
    yield from _missing_fields(value, tuple(GATE_FIELDS), path)
    if any(field not in value for field in GATE_FIELDS):
        return

    required_true = (
        "no_rendered_handoff_is_success",
        "decline_receipt_is_not_answer_plan",
        "no_pressure_surface_created",
    )
    for field in required_true:
        if value.get(field) is not True:
            yield f"{path / field}: must be true"
    required_false = (
        "runtime_wiring_allowed",
        "product_promotion_allowed",
        "generator_implementation_allowed",
    )
    for field in required_false:
        if value.get(field) is not False:
            yield f"{path / field}: must be false"


def _validate_not_hidden_answer_plan(text: str, *, path: Path) -> Iterable[str]:
    lower = text.lower()
    for phrase in HIDDEN_ANSWER_PLAN_PHRASES:
        if phrase in lower:
            yield f"{path}: hidden answer-plan phrase '{phrase}' is not allowed"


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
        description="Validate research-only pre-Step-6 no-rendered-handoff records."
    )
    parser.add_argument("path", type=Path)
    parser.add_argument("--repo-root", type=Path)
    args = parser.parse_args(argv)

    validate_no_rendered_handoff_file(args.path, repo_root=args.repo_root)
    summary = summarize_no_rendered_handoff(load_no_rendered_handoff_payload(args.path))
    print(
        f"valid no-rendered handoff: {args.path} "
        f"case={summary['case_id']} "
        f"decision={summary['decline_decision']} "
        f"expected={summary['expected_result']} "
        f"naturalness_debt_risk={summary['naturalness_debt_risk']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
