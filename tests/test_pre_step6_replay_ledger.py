from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_replay_ledger import (  # noqa: E402
    ReplayLedgerValidationError,
    summarize_replay_record,
    validate_replay_record_payload,
    validate_source_overclaim_audit_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = REPO_ROOT / "research" / "pre-step6-source-overclaim-audits"
REPLAY_DIR = REPO_ROOT / "research" / "pre-step6-replay-records"


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _audit_paths() -> list[Path]:
    return sorted(AUDIT_DIR.glob("*.source-overclaim-audit.v1.json"))


def _replay_paths() -> list[Path]:
    return sorted(REPLAY_DIR.glob("*.off-default-replay.v1.json"))


def test_all_source_overclaim_audits_validate() -> None:
    paths = _audit_paths()

    assert [path.name for path in paths] == [
        "founder-grant-marcus-equity.high-clutter.rendered-hybrid.source-overclaim-audit.v1.json",
        "mother-address-year.quiet.rendered-hybrid.source-overclaim-audit.v1.json",
        "third-year-phd-student.conflict.rendered-hybrid.source-overclaim-audit.v1.json",
    ]

    expected_debt = {
        "founder-grant-marcus-equity": "medium",
        "mother-deciding-address-year": "low",
        "third-year-phd-student": "medium",
    }

    for path in paths:
        payload = _load(path)
        validate_source_overclaim_audit_payload(
            payload,
            path=path,
            repo_root=REPO_ROOT,
        )

        assert payload["audit_result"] == "pass"
        assert payload["decision"] == "counts_as_replay_win"
        assert payload["naturalness_debt_level"] == expected_debt[payload["case_id"]]


def test_all_replay_records_validate() -> None:
    paths = _replay_paths()

    assert [path.name for path in paths] == [
        "founder-grant-marcus-equity.high-clutter.off-default-replay.v1.json",
        "mother-address-year.quiet.off-default-replay.v1.json",
        "third-year-phd-student.conflict.off-default-replay.v1.json",
    ]

    expected_summaries = {
        "founder-grant-marcus-equity": {
            "comparison_decision": "rendered_hybrid_wins",
            "replay_decision": "pass_to_next_replay",
            "product_promotion": "blocked",
            "naturalness_debt_level": "medium",
            "present_or_watch_failure_modes": 2,
        },
        "mother-deciding-address-year": {
            "comparison_decision": "rendered_hybrid_wins",
            "replay_decision": "pass_to_next_replay",
            "product_promotion": "blocked",
            "naturalness_debt_level": "low",
            "present_or_watch_failure_modes": 0,
        },
        "third-year-phd-student": {
            "comparison_decision": "rendered_hybrid_wins",
            "replay_decision": "pass_to_next_replay",
            "product_promotion": "blocked",
            "naturalness_debt_level": "medium",
            "present_or_watch_failure_modes": 1,
        },
    }

    for path in paths:
        payload = _load(path)
        validate_replay_record_payload(payload, path=path, repo_root=REPO_ROOT)

        summary = summarize_replay_record(payload)
        assert summary == expected_summaries[payload["case_id"]]


def test_source_overclaim_audit_rejects_pass_with_failed_check() -> None:
    path = (
        AUDIT_DIR
        / "third-year-phd-student.conflict.rendered-hybrid.source-overclaim-audit.v1.json"
    )
    payload = _load(path)
    checks = payload["checks"]
    assert isinstance(checks, list)
    first = checks[0]
    assert isinstance(first, dict)
    first["severity"] = "fail"

    with pytest.raises(
        ReplayLedgerValidationError,
        match="pass is invalid",
    ):
        validate_source_overclaim_audit_payload(payload, repo_root=REPO_ROOT)


def test_source_overclaim_audit_can_record_failed_audit() -> None:
    path = (
        AUDIT_DIR
        / "third-year-phd-student.conflict.rendered-hybrid.source-overclaim-audit.v1.json"
    )
    payload = _load(path)
    checks = payload["checks"]
    assert isinstance(checks, list)
    first = checks[0]
    assert isinstance(first, dict)
    first["severity"] = "fail"
    payload["audit_result"] = "fail"
    payload["decision"] = "does_not_count"

    validate_source_overclaim_audit_payload(payload, repo_root=REPO_ROOT)


def test_source_overclaim_audit_rejects_high_debt_replay_win() -> None:
    path = (
        AUDIT_DIR
        / "third-year-phd-student.conflict.rendered-hybrid.source-overclaim-audit.v1.json"
    )
    payload = _load(path)
    payload["naturalness_debt_level"] = "high"

    with pytest.raises(
        ReplayLedgerValidationError,
        match="high debt cannot count",
    ):
        validate_source_overclaim_audit_payload(payload, repo_root=REPO_ROOT)


def test_replay_record_can_record_failed_audit_as_stop() -> None:
    path = REPLAY_DIR / "third-year-phd-student.conflict.off-default-replay.v1.json"
    payload = _load(path)
    gates = payload["gates"]
    outcome = payload["outcome"]
    naturalness = payload["naturalness_debt"]
    assert isinstance(gates, dict)
    assert isinstance(outcome, dict)
    assert isinstance(naturalness, dict)
    gates["source_overclaim_audit_passed"] = False
    outcome["replay_decision"] = "stop"
    naturalness["level"] = "high"

    validate_replay_record_payload(payload)


def test_replay_record_rejects_pass_without_source_audit_gate() -> None:
    path = REPLAY_DIR / "third-year-phd-student.conflict.off-default-replay.v1.json"
    payload = _load(path)
    gates = payload["gates"]
    assert isinstance(gates, dict)
    gates["source_overclaim_audit_passed"] = False

    with pytest.raises(
        ReplayLedgerValidationError,
        match="source_overclaim_audit_passed",
    ):
        validate_replay_record_payload(payload, repo_root=REPO_ROOT)


def test_replay_record_rejects_cross_ref_answer_drift() -> None:
    path = REPLAY_DIR / "third-year-phd-student.conflict.off-default-replay.v1.json"
    payload = _load(path)
    artifact_refs = payload["artifact_refs"]
    assert isinstance(artifact_refs, dict)
    artifact_refs["rendered_hybrid_answer_core"] = (
        "research/pre-step6-rendered-hybrid-answer-cores/"
        "third-year-phd-student.native.rendered-hybrid-answer-core.v1.json"
    )

    with pytest.raises(
        ReplayLedgerValidationError,
        match="audited_answer_core_ref",
    ):
        validate_replay_record_payload(payload, repo_root=REPO_ROOT)


def test_replay_record_rejects_product_promotion() -> None:
    path = REPLAY_DIR / "third-year-phd-student.conflict.off-default-replay.v1.json"
    payload = _load(path)
    gates = payload["gates"]
    outcome = payload["outcome"]
    assert isinstance(gates, dict)
    assert isinstance(outcome, dict)
    gates["product_promotion_allowed"] = True
    outcome["product_promotion"] = "allowed"

    with pytest.raises(
        ReplayLedgerValidationError,
        match="product_promotion",
    ):
        validate_replay_record_payload(payload, repo_root=REPO_ROOT)
