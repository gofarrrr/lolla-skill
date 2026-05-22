#!/usr/bin/env python3
"""Research-only replay ledger records for the pre-Step-6 pressure surface.

This validates off-by-default replay evidence. It does not generate answers,
route /lolla, launch workers, build bundles, update product docs, or promote
runtime behavior.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, Sequence

from pre_step6_hybrid_handoffs import (
    load_handoff_payload,
    validate_hybrid_handoff_payload,
)
from pre_step6_pressure_card_consumption import (
    load_pressure_consumption_payload,
    validate_rendered_hybrid_answer_core_payload,
)
from pre_step6_raw_artifacts import (
    load_answer_comparison_payload,
    load_answer_core_payload,
    load_raw_artifact_payload,
    validate_answer_comparison_payload,
    validate_answer_core_payload,
    validate_raw_artifact_payload,
)
from pre_step6_semi_blind_comparisons import (
    load_semi_blind_comparison_payload,
    score_semi_blind_comparison,
    validate_semi_blind_comparison_payload,
)


SOURCE_OVERCLAIM_AUDIT_SCHEMA_VERSION = "pre_step6_source_overclaim_audit.v1"
REPLAY_RECORD_SCHEMA_VERSION = "pre_step6_replay_record.v1"

ALLOWED_STATUS = frozenset({"research_only"})
ALLOWED_RUNTIME_POLICY = frozenset({"runtime_dormant"})
ALLOWED_AUDITED_ARMS = frozenset({"rendered_hybrid"})
ALLOWED_AUDIT_RESULTS = frozenset({"pass", "fail"})
ALLOWED_AUDIT_DECISIONS = frozenset({"counts_as_replay_win", "does_not_count"})
ALLOWED_CHECK_SEVERITIES = frozenset({"pass", "watch", "fail"})
ALLOWED_NATURALNESS_DEBT_LEVELS = frozenset({"low", "medium", "high"})
ALLOWED_REPLAY_MODES = frozenset({"off_by_default_static_replay"})
ALLOWED_CANDIDATE_GENERATION = frozenset({"loaded_existing_rendered_handoff"})
ALLOWED_ANSWER_GENERATION = frozenset({"loaded_existing_step6_style_answer_core"})
ALLOWED_REPLAY_DECISIONS = frozenset({"pass_to_next_replay", "retest", "stop"})
ALLOWED_PRODUCT_PROMOTION = frozenset({"blocked"})
ALLOWED_FAILURE_STATUSES = frozenset({"absent", "watch", "present"})

REQUIRED_AUDIT_CHECKS = (
    "source_grounding",
    "probability_overclaim",
    "evidence_gate_integrity",
    "unsupported_option_expansion",
    "naturalness_debt",
)
AUDIT_TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "audited_arm",
        "audited_answer_core_ref",
        "source_refs",
        "checks",
        "audit_result",
        "overclaim_findings",
        "naturalness_debt_level",
        "decision",
        "notes",
    }
)
AUDIT_SOURCE_REF_FIELDS = frozenset(
    {"source_hybrid_handoff", "raw_artifact_handoff", "semi_blind_comparison"}
)
AUDIT_CHECK_FIELDS = frozenset({"check_id", "severity", "rationale"})

REPLAY_TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "replay_mode",
        "candidate_generation",
        "answer_generation",
        "artifact_refs",
        "comparison_ref",
        "source_overclaim_audit_ref",
        "gates",
        "outcome",
        "failure_modes",
        "naturalness_debt",
        "notes",
    }
)
REPLAY_ARTIFACT_REF_FIELDS = frozenset(
    {
        "comparison_fixture",
        "raw_artifact_handoff",
        "hybrid_handoff",
        "control_comparison",
        "raw_answer_core",
        "rendered_hybrid_answer_core",
    }
)
REPLAY_GATE_FIELDS = frozenset(
    {
        "archived_artifacts_loaded",
        "candidate_handoff_loaded",
        "step6_style_answer_core_loaded",
        "semi_blind_comparison_recorded",
        "source_overclaim_audit_recorded",
        "source_overclaim_audit_passed",
        "runtime_wiring_allowed",
        "product_promotion_allowed",
    }
)
REPLAY_OUTCOME_FIELDS = frozenset(
    {"comparison_decision", "replay_decision", "product_promotion"}
)
FAILURE_MODE_FIELDS = frozenset({"failure_mode", "status", "evidence"})
NATURALNESS_DEBT_FIELDS = frozenset({"level", "evidence", "mitigation"})


class ReplayLedgerValidationError(ValueError):
    pass


def load_replay_payload(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ReplayLedgerValidationError(f"{path}: payload must be an object")
    return payload


def validate_source_overclaim_audit_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
    repo_root: Path | None = None,
) -> None:
    errors = list(
        iter_source_overclaim_audit_errors(
            payload,
            path=Path(path),
            repo_root=repo_root,
        )
    )
    if errors:
        raise ReplayLedgerValidationError("; ".join(errors))


def validate_source_overclaim_audit_file(
    path: Path,
    *,
    repo_root: Path | None = None,
) -> None:
    validate_source_overclaim_audit_payload(
        load_replay_payload(path),
        path=Path(path),
        repo_root=repo_root,
    )


def validate_replay_record_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
    repo_root: Path | None = None,
) -> None:
    errors = list(
        iter_replay_record_errors(payload, path=Path(path), repo_root=repo_root)
    )
    if errors:
        raise ReplayLedgerValidationError("; ".join(errors))


def validate_replay_record_file(
    path: Path,
    *,
    repo_root: Path | None = None,
) -> None:
    validate_replay_record_payload(
        load_replay_payload(path),
        path=Path(path),
        repo_root=repo_root,
    )


def iter_source_overclaim_audit_errors(
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
        "audited_arm",
        "audited_answer_core_ref",
        "source_refs",
        "checks",
        "audit_result",
        "overclaim_findings",
        "naturalness_debt_level",
        "decision",
    )
    yield from _unknown_fields(payload, AUDIT_TOP_LEVEL_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return

    if _string(payload.get("schema_version")) != SOURCE_OVERCLAIM_AUDIT_SCHEMA_VERSION:
        yield f"{path}: schema_version must be {SOURCE_OVERCLAIM_AUDIT_SCHEMA_VERSION}"
    yield from _validate_common_policy(payload, path=path)
    case_id = _string(payload.get("case_id"))

    if _string(payload.get("audited_arm")) not in ALLOWED_AUDITED_ARMS:
        yield f"{path / 'audited_arm'}: audited_arm must be rendered_hybrid"

    answer_ref = _string(payload.get("audited_answer_core_ref"))
    if not answer_ref:
        yield f"{path / 'audited_answer_core_ref'}: must be non-empty"
    elif repo_root is not None:
        answer_path = repo_root / answer_ref
        if not answer_path.exists():
            yield f"{path / 'audited_answer_core_ref'}: answer core missing"
        else:
            answer_payload = load_pressure_consumption_payload(answer_path)
            validate_rendered_hybrid_answer_core_payload(
                answer_payload,
                path=answer_path,
                repo_root=repo_root,
            )
            if _string(answer_payload.get("case_id")) != case_id:
                yield f"{path / 'audited_answer_core_ref'}: case_id mismatch"

    yield from _validate_audit_source_refs(
        payload.get("source_refs"),
        path=path / "source_refs",
        case_id=case_id,
        repo_root=repo_root,
    )
    yield from _validate_audit_checks(payload.get("checks"), path=path / "checks")

    audit_result = _string(payload.get("audit_result"))
    if audit_result not in ALLOWED_AUDIT_RESULTS:
        yield f"{path / 'audit_result'}: unknown audit_result '{audit_result}'"

    decision = _string(payload.get("decision"))
    if decision not in ALLOWED_AUDIT_DECISIONS:
        yield f"{path / 'decision'}: unknown decision '{decision}'"

    has_fail = _checks_have_failure(payload.get("checks"))
    if audit_result == "pass" and has_fail:
        yield f"{path / 'audit_result'}: pass is invalid when a check failed"
    if decision == "counts_as_replay_win" and audit_result != "pass":
        yield f"{path / 'decision'}: replay win requires audit_result pass"

    yield from _validate_string_list(
        payload.get("overclaim_findings"),
        path=path / "overclaim_findings",
        allow_empty=True,
    )

    naturalness_level = _string(payload.get("naturalness_debt_level"))
    if naturalness_level not in ALLOWED_NATURALNESS_DEBT_LEVELS:
        yield f"{path / 'naturalness_debt_level'}: unknown naturalness_debt_level"
    elif naturalness_level == "high" and decision == "counts_as_replay_win":
        yield f"{path / 'naturalness_debt_level'}: high debt cannot count as replay win"


def iter_replay_record_errors(
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
        "replay_mode",
        "candidate_generation",
        "answer_generation",
        "artifact_refs",
        "comparison_ref",
        "source_overclaim_audit_ref",
        "gates",
        "outcome",
        "failure_modes",
        "naturalness_debt",
    )
    yield from _unknown_fields(payload, REPLAY_TOP_LEVEL_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return

    if _string(payload.get("schema_version")) != REPLAY_RECORD_SCHEMA_VERSION:
        yield f"{path}: schema_version must be {REPLAY_RECORD_SCHEMA_VERSION}"
    yield from _validate_common_policy(payload, path=path)
    case_id = _string(payload.get("case_id"))

    if _string(payload.get("replay_mode")) not in ALLOWED_REPLAY_MODES:
        yield f"{path / 'replay_mode'}: unknown replay_mode"
    if _string(payload.get("candidate_generation")) not in ALLOWED_CANDIDATE_GENERATION:
        yield f"{path / 'candidate_generation'}: unknown candidate_generation"
    if _string(payload.get("answer_generation")) not in ALLOWED_ANSWER_GENERATION:
        yield f"{path / 'answer_generation'}: unknown answer_generation"

    yield from _validate_replay_artifact_refs(
        payload.get("artifact_refs"),
        path=path / "artifact_refs",
        case_id=case_id,
        repo_root=repo_root,
    )

    comparison_payload: dict[str, object] | None = None
    comparison_ref = _string(payload.get("comparison_ref"))
    if not comparison_ref:
        yield f"{path / 'comparison_ref'}: must be non-empty"
    elif repo_root is not None:
        comparison_path = repo_root / comparison_ref
        if not comparison_path.exists():
            yield f"{path / 'comparison_ref'}: comparison missing"
        else:
            comparison_payload = load_semi_blind_comparison_payload(comparison_path)
            validate_semi_blind_comparison_payload(
                comparison_payload,
                path=comparison_path,
                repo_root=repo_root,
            )
            if _string(comparison_payload.get("case_id")) != case_id:
                yield f"{path / 'comparison_ref'}: case_id mismatch"

    audit_payload: dict[str, object] | None = None
    audit_ref = _string(payload.get("source_overclaim_audit_ref"))
    if not audit_ref:
        yield f"{path / 'source_overclaim_audit_ref'}: must be non-empty"
    elif repo_root is not None:
        audit_path = repo_root / audit_ref
        if not audit_path.exists():
            yield f"{path / 'source_overclaim_audit_ref'}: source audit missing"
        else:
            audit_payload = load_replay_payload(audit_path)
            validate_source_overclaim_audit_payload(
                audit_payload,
                path=audit_path,
                repo_root=repo_root,
            )
            if _string(audit_payload.get("case_id")) != case_id:
                yield f"{path / 'source_overclaim_audit_ref'}: case_id mismatch"

    yield from _validate_cross_ref_custody(
        payload,
        path=path,
        comparison_payload=comparison_payload,
        audit_payload=audit_payload,
    )
    yield from _validate_gates(
        payload.get("gates"),
        path=path / "gates",
        outcome=payload.get("outcome"),
        audit_payload=audit_payload,
    )
    yield from _validate_outcome(
        payload.get("outcome"),
        path=path / "outcome",
        comparison_payload=comparison_payload,
        audit_payload=audit_payload,
    )
    yield from _validate_failure_modes(
        payload.get("failure_modes"),
        path=path / "failure_modes",
    )
    yield from _validate_naturalness_debt(
        payload.get("naturalness_debt"),
        path=path / "naturalness_debt",
        outcome=payload.get("outcome"),
    )


def summarize_replay_record(payload: dict[str, object]) -> dict[str, object]:
    outcome = payload.get("outcome") if isinstance(payload.get("outcome"), dict) else {}
    naturalness = (
        payload.get("naturalness_debt")
        if isinstance(payload.get("naturalness_debt"), dict)
        else {}
    )
    failure_modes = payload.get("failure_modes")
    present_or_watch = 0
    if isinstance(failure_modes, list):
        for item in failure_modes:
            if isinstance(item, dict) and _string(item.get("status")) in {
                "present",
                "watch",
            }:
                present_or_watch += 1
    return {
        "comparison_decision": _string(outcome.get("comparison_decision")),
        "replay_decision": _string(outcome.get("replay_decision")),
        "product_promotion": _string(outcome.get("product_promotion")),
        "naturalness_debt_level": _string(naturalness.get("level")),
        "present_or_watch_failure_modes": present_or_watch,
    }


def _validate_audit_source_refs(
    value: object,
    *,
    path: Path,
    case_id: str,
    repo_root: Path | None,
) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: source_refs must be an object"
        return
    yield from _unknown_fields(value, AUDIT_SOURCE_REF_FIELDS, path)
    yield from _missing_fields(value, tuple(AUDIT_SOURCE_REF_FIELDS), path)
    if any(field not in value for field in AUDIT_SOURCE_REF_FIELDS):
        return

    for field in AUDIT_SOURCE_REF_FIELDS:
        if not _string(value.get(field)).strip():
            yield f"{path / field}: must be non-empty"
    if repo_root is None:
        return

    hybrid_ref = _string(value.get("source_hybrid_handoff"))
    if hybrid_ref:
        hybrid_path = repo_root / hybrid_ref
        if not hybrid_path.exists():
            yield f"{path / 'source_hybrid_handoff'}: hybrid handoff missing"
        else:
            hybrid_payload = load_handoff_payload(hybrid_path)
            validate_hybrid_handoff_payload(
                hybrid_payload,
                path=hybrid_path,
                repo_root=repo_root,
            )
            if _string(hybrid_payload.get("case_id")) != case_id:
                yield f"{path / 'source_hybrid_handoff'}: case_id mismatch"

    raw_ref = _string(value.get("raw_artifact_handoff"))
    if raw_ref:
        raw_path = repo_root / raw_ref
        if not raw_path.exists():
            yield f"{path / 'raw_artifact_handoff'}: raw handoff missing"
        else:
            raw_payload = load_raw_artifact_payload(raw_path)
            validate_raw_artifact_payload(raw_payload, path=raw_path)
            if _string(raw_payload.get("case_id")) != case_id:
                yield f"{path / 'raw_artifact_handoff'}: case_id mismatch"

    comparison_ref = _string(value.get("semi_blind_comparison"))
    if comparison_ref:
        comparison_path = repo_root / comparison_ref
        if not comparison_path.exists():
            yield f"{path / 'semi_blind_comparison'}: comparison missing"
        else:
            comparison_payload = load_semi_blind_comparison_payload(comparison_path)
            validate_semi_blind_comparison_payload(
                comparison_payload,
                path=comparison_path,
                repo_root=repo_root,
            )
            if _string(comparison_payload.get("case_id")) != case_id:
                yield f"{path / 'semi_blind_comparison'}: case_id mismatch"


def _validate_audit_checks(value: object, *, path: Path) -> Iterable[str]:
    if not isinstance(value, list):
        yield f"{path}: checks must be a list"
        return
    ids = [
        _string(item.get("check_id")) if isinstance(item, dict) else ""
        for item in value
    ]
    if tuple(ids) != REQUIRED_AUDIT_CHECKS:
        yield f"{path}: checks must match the required source/overclaim order"
    for index, check in enumerate(value):
        item_path = path / f"checks[{index}]"
        if not isinstance(check, dict):
            yield f"{item_path}: check must be an object"
            continue
        yield from _unknown_fields(check, AUDIT_CHECK_FIELDS, item_path)
        yield from _missing_fields(check, ("check_id", "severity", "rationale"), item_path)
        if any(field not in check for field in ("check_id", "severity", "rationale")):
            continue
        if _string(check.get("check_id")) not in REQUIRED_AUDIT_CHECKS:
            yield f"{item_path / 'check_id'}: unknown check_id"
        if _string(check.get("severity")) not in ALLOWED_CHECK_SEVERITIES:
            yield f"{item_path / 'severity'}: unknown severity"
        if not _string(check.get("rationale")).strip():
            yield f"{item_path / 'rationale'}: rationale must be non-empty"


def _validate_replay_artifact_refs(
    value: object,
    *,
    path: Path,
    case_id: str,
    repo_root: Path | None,
) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: artifact_refs must be an object"
        return
    yield from _unknown_fields(value, REPLAY_ARTIFACT_REF_FIELDS, path)
    yield from _missing_fields(value, tuple(REPLAY_ARTIFACT_REF_FIELDS), path)
    if any(field not in value for field in REPLAY_ARTIFACT_REF_FIELDS):
        return

    for field in REPLAY_ARTIFACT_REF_FIELDS:
        if not _string(value.get(field)).strip():
            yield f"{path / field}: must be non-empty"
    if repo_root is None:
        return

    comparison_fixture = _string(value.get("comparison_fixture"))
    if comparison_fixture and not (repo_root / comparison_fixture).exists():
        yield f"{path / 'comparison_fixture'}: comparison fixture missing"

    raw_handoff_ref = _string(value.get("raw_artifact_handoff"))
    if raw_handoff_ref:
        raw_path = repo_root / raw_handoff_ref
        if not raw_path.exists():
            yield f"{path / 'raw_artifact_handoff'}: raw handoff missing"
        else:
            raw_payload = load_raw_artifact_payload(raw_path)
            validate_raw_artifact_payload(raw_payload, path=raw_path)
            if _string(raw_payload.get("case_id")) != case_id:
                yield f"{path / 'raw_artifact_handoff'}: case_id mismatch"

    hybrid_ref = _string(value.get("hybrid_handoff"))
    if hybrid_ref:
        hybrid_path = repo_root / hybrid_ref
        if not hybrid_path.exists():
            yield f"{path / 'hybrid_handoff'}: hybrid handoff missing"
        else:
            hybrid_payload = load_handoff_payload(hybrid_path)
            validate_hybrid_handoff_payload(
                hybrid_payload,
                path=hybrid_path,
                repo_root=repo_root,
            )
            if _string(hybrid_payload.get("case_id")) != case_id:
                yield f"{path / 'hybrid_handoff'}: case_id mismatch"

    control_ref = _string(value.get("control_comparison"))
    if control_ref:
        control_path = repo_root / control_ref
        if not control_path.exists():
            yield f"{path / 'control_comparison'}: control comparison missing"
        else:
            control_payload = load_answer_comparison_payload(control_path)
            validate_answer_comparison_payload(
                control_payload,
                path=control_path,
                repo_root=repo_root,
            )
            if _string(control_payload.get("case_id")) != case_id:
                yield f"{path / 'control_comparison'}: case_id mismatch"

    raw_answer_ref = _string(value.get("raw_answer_core"))
    if raw_answer_ref:
        raw_answer_path = repo_root / raw_answer_ref
        if not raw_answer_path.exists():
            yield f"{path / 'raw_answer_core'}: raw answer core missing"
        else:
            raw_answer_payload = load_answer_core_payload(raw_answer_path)
            validate_answer_core_payload(
                raw_answer_payload,
                path=raw_answer_path,
                repo_root=repo_root,
            )
            if _string(raw_answer_payload.get("case_id")) != case_id:
                yield f"{path / 'raw_answer_core'}: case_id mismatch"

    rendered_ref = _string(value.get("rendered_hybrid_answer_core"))
    if rendered_ref:
        rendered_path = repo_root / rendered_ref
        if not rendered_path.exists():
            yield f"{path / 'rendered_hybrid_answer_core'}: rendered answer core missing"
        else:
            rendered_payload = load_pressure_consumption_payload(rendered_path)
            validate_rendered_hybrid_answer_core_payload(
                rendered_payload,
                path=rendered_path,
                repo_root=repo_root,
            )
            if _string(rendered_payload.get("case_id")) != case_id:
                yield f"{path / 'rendered_hybrid_answer_core'}: case_id mismatch"


def _validate_cross_ref_custody(
    payload: dict[str, object],
    *,
    path: Path,
    comparison_payload: dict[str, object] | None,
    audit_payload: dict[str, object] | None,
) -> Iterable[str]:
    artifact_refs = payload.get("artifact_refs")
    if not isinstance(artifact_refs, dict):
        return

    comparison_ref = _string(payload.get("comparison_ref"))
    if comparison_payload is not None:
        candidate_refs = comparison_payload.get("candidate_refs")
        if isinstance(candidate_refs, dict):
            expected_pairs = (
                (
                    "control_answer_comparison",
                    "control_comparison",
                    "comparison candidate control ref",
                ),
                (
                    "raw_answer_core",
                    "raw_answer_core",
                    "comparison candidate raw ref",
                ),
                (
                    "rendered_hybrid_answer_core",
                    "rendered_hybrid_answer_core",
                    "comparison candidate rendered ref",
                ),
            )
            for comparison_field, replay_field, label in expected_pairs:
                if _string(candidate_refs.get(comparison_field)) != _string(
                    artifact_refs.get(replay_field)
                ):
                    yield (
                        f"{path}: {label} must match "
                        f"artifact_refs.{replay_field}"
                    )

    if audit_payload is None:
        return
    if _string(audit_payload.get("audited_answer_core_ref")) != _string(
        artifact_refs.get("rendered_hybrid_answer_core")
    ):
        yield (
            f"{path}: audit audited_answer_core_ref must match "
            "artifact_refs.rendered_hybrid_answer_core"
        )
    source_refs = audit_payload.get("source_refs")
    if not isinstance(source_refs, dict):
        return
    expected_pairs = (
        ("source_hybrid_handoff", "hybrid_handoff", "audit source_hybrid_handoff"),
        ("raw_artifact_handoff", "raw_artifact_handoff", "audit raw_artifact_handoff"),
    )
    for audit_field, replay_field, label in expected_pairs:
        if _string(source_refs.get(audit_field)) != _string(artifact_refs.get(replay_field)):
            yield f"{path}: {label} must match artifact_refs.{replay_field}"
    if _string(source_refs.get("semi_blind_comparison")) != comparison_ref:
        yield f"{path}: audit semi_blind_comparison must match comparison_ref"


def _validate_gates(
    value: object,
    *,
    path: Path,
    outcome: object,
    audit_payload: dict[str, object] | None,
) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: gates must be an object"
        return
    yield from _unknown_fields(value, REPLAY_GATE_FIELDS, path)
    yield from _missing_fields(value, tuple(REPLAY_GATE_FIELDS), path)
    required_true = REPLAY_GATE_FIELDS - {
        "source_overclaim_audit_passed",
        "runtime_wiring_allowed",
        "product_promotion_allowed",
    }
    for field in sorted(required_true):
        if value.get(field) is not True:
            yield f"{path / field}: must be true"
    for field in ("runtime_wiring_allowed", "product_promotion_allowed"):
        if value.get(field) is not False:
            yield f"{path / field}: must be false"
    source_passed = value.get("source_overclaim_audit_passed")
    if not isinstance(source_passed, bool):
        yield f"{path / 'source_overclaim_audit_passed'}: must be boolean"
    if audit_payload is not None and isinstance(source_passed, bool):
        expected_passed = _string(audit_payload.get("audit_result")) == "pass"
        if source_passed is not expected_passed:
            yield (
                f"{path / 'source_overclaim_audit_passed'}: must match "
                "source audit result"
            )
    if (
        isinstance(outcome, dict)
        and _string(outcome.get("replay_decision")) == "pass_to_next_replay"
        and source_passed is not True
    ):
        yield (
            f"{path / 'source_overclaim_audit_passed'}: "
            "pass_to_next_replay requires source audit pass"
        )


def _validate_outcome(
    value: object,
    *,
    path: Path,
    comparison_payload: dict[str, object] | None,
    audit_payload: dict[str, object] | None,
) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: outcome must be an object"
        return
    yield from _unknown_fields(value, REPLAY_OUTCOME_FIELDS, path)
    yield from _missing_fields(
        value,
        ("comparison_decision", "replay_decision", "product_promotion"),
        path,
    )
    if any(field not in value for field in REPLAY_OUTCOME_FIELDS):
        return

    comparison_decision = _string(value.get("comparison_decision"))
    if comparison_payload is not None:
        expected_decision = score_semi_blind_comparison(comparison_payload)[
            "aggregate_decision"
        ]
        if comparison_decision != expected_decision:
            yield f"{path / 'comparison_decision'}: must match semi-blind comparison"
    if _string(value.get("replay_decision")) not in ALLOWED_REPLAY_DECISIONS:
        yield f"{path / 'replay_decision'}: unknown replay_decision"
    if _string(value.get("product_promotion")) not in ALLOWED_PRODUCT_PROMOTION:
        yield f"{path / 'product_promotion'}: product_promotion must be blocked"

    replay_decision = _string(value.get("replay_decision"))
    if replay_decision == "pass_to_next_replay":
        if comparison_decision != "rendered_hybrid_wins":
            yield f"{path / 'replay_decision'}: pass requires rendered_hybrid_wins"
        if audit_payload is None:
            return
        if _string(audit_payload.get("audit_result")) != "pass":
            yield f"{path / 'replay_decision'}: pass requires source audit pass"
        if _string(audit_payload.get("decision")) != "counts_as_replay_win":
            yield f"{path / 'replay_decision'}: pass requires audit replay-win decision"


def _validate_failure_modes(value: object, *, path: Path) -> Iterable[str]:
    if not isinstance(value, list):
        yield f"{path}: failure_modes must be a list"
        return
    if not value:
        yield f"{path}: failure_modes must not be empty"
    for index, item in enumerate(value):
        item_path = path / f"failure_modes[{index}]"
        if not isinstance(item, dict):
            yield f"{item_path}: failure mode must be an object"
            continue
        yield from _unknown_fields(item, FAILURE_MODE_FIELDS, item_path)
        yield from _missing_fields(item, ("failure_mode", "status", "evidence"), item_path)
        if any(field not in item for field in FAILURE_MODE_FIELDS):
            continue
        if not _string(item.get("failure_mode")).strip():
            yield f"{item_path / 'failure_mode'}: failure_mode must be non-empty"
        if _string(item.get("status")) not in ALLOWED_FAILURE_STATUSES:
            yield f"{item_path / 'status'}: unknown status"
        if not _string(item.get("evidence")).strip():
            yield f"{item_path / 'evidence'}: evidence must be non-empty"


def _validate_naturalness_debt(
    value: object,
    *,
    path: Path,
    outcome: object,
) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: naturalness_debt must be an object"
        return
    yield from _unknown_fields(value, NATURALNESS_DEBT_FIELDS, path)
    yield from _missing_fields(value, ("level", "evidence", "mitigation"), path)
    if any(field not in value for field in NATURALNESS_DEBT_FIELDS):
        return
    level = _string(value.get("level"))
    if level not in ALLOWED_NATURALNESS_DEBT_LEVELS:
        yield f"{path / 'level'}: unknown level"
    if not _string(value.get("evidence")).strip():
        yield f"{path / 'evidence'}: evidence must be non-empty"
    if not _string(value.get("mitigation")).strip():
        yield f"{path / 'mitigation'}: mitigation must be non-empty"
    if (
        level == "high"
        and isinstance(outcome, dict)
        and _string(outcome.get("replay_decision")) == "pass_to_next_replay"
    ):
        yield f"{path / 'level'}: high debt cannot pass to next replay"


def _checks_have_failure(value: object) -> bool:
    if not isinstance(value, list):
        return False
    return any(
        isinstance(item, dict) and _string(item.get("severity")) == "fail"
        for item in value
    )


def _validate_common_policy(
    payload: dict[str, object],
    *,
    path: Path,
) -> Iterable[str]:
    if _string(payload.get("status")) not in ALLOWED_STATUS:
        yield f"{path / 'status'}: status must be research_only"
    if _string(payload.get("runtime_policy")) not in ALLOWED_RUNTIME_POLICY:
        yield f"{path / 'runtime_policy'}: runtime_policy must be runtime_dormant"
    if not _string(payload.get("case_id")).strip():
        yield f"{path / 'case_id'}: case_id must be non-empty"


def _validate_string_list(
    value: object,
    *,
    path: Path,
    allow_empty: bool,
) -> Iterable[str]:
    if not isinstance(value, list):
        yield f"{path}: must be a list"
        return
    if not allow_empty and not value:
        yield f"{path}: must not be empty"
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            yield f"{path / str(index)}: item must be a non-empty string"


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
        description="Validate research-only pre-Step-6 replay ledger records."
    )
    parser.add_argument("path", type=Path)
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--source-overclaim-audit", action="store_true")
    parser.add_argument("--replay-record", action="store_true")
    args = parser.parse_args(argv)

    if args.source_overclaim_audit:
        validate_source_overclaim_audit_file(args.path, repo_root=args.repo_root)
        print(f"valid source/overclaim audit: {args.path}")
        return 0

    if args.replay_record:
        validate_replay_record_file(args.path, repo_root=args.repo_root)
        summary = summarize_replay_record(load_replay_payload(args.path))
        print(
            f"valid replay ledger record: {args.path} "
            f"comparison={summary['comparison_decision']} "
            f"replay={summary['replay_decision']} "
            f"naturalness_debt={summary['naturalness_debt_level']} "
            f"watch_or_present={summary['present_or_watch_failure_modes']}"
        )
        return 0

    parser.error("choose --source-overclaim-audit or --replay-record")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
