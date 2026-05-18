from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_replay_harness import (  # noqa: E402
    ReplayHarnessValidationError,
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
        "third-year-phd-student.conflict.rendered-hybrid.source-overclaim-audit.v1.json",
    ]

    payload = _load(paths[0])
    validate_source_overclaim_audit_payload(payload, path=paths[0], repo_root=REPO_ROOT)

    assert payload["audit_result"] == "pass"
    assert payload["decision"] == "counts_as_replay_win"
    assert payload["naturalness_debt_level"] == "medium"


def test_all_replay_records_validate() -> None:
    paths = _replay_paths()

    assert [path.name for path in paths] == [
        "third-year-phd-student.conflict.off-default-replay.v1.json",
    ]

    payload = _load(paths[0])
    validate_replay_record_payload(payload, path=paths[0], repo_root=REPO_ROOT)

    summary = summarize_replay_record(payload)
    assert summary == {
        "comparison_decision": "rendered_hybrid_wins",
        "replay_decision": "pass_to_next_replay",
        "product_promotion": "blocked",
        "naturalness_debt_level": "medium",
        "present_or_watch_failure_modes": 1,
    }


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
        ReplayHarnessValidationError,
        match="pass is invalid",
    ):
        validate_source_overclaim_audit_payload(payload, repo_root=REPO_ROOT)


def test_source_overclaim_audit_rejects_high_debt_replay_win() -> None:
    path = (
        AUDIT_DIR
        / "third-year-phd-student.conflict.rendered-hybrid.source-overclaim-audit.v1.json"
    )
    payload = _load(path)
    payload["naturalness_debt_level"] = "high"

    with pytest.raises(
        ReplayHarnessValidationError,
        match="high debt cannot count",
    ):
        validate_source_overclaim_audit_payload(payload, repo_root=REPO_ROOT)


def test_replay_record_rejects_pass_without_source_audit_gate() -> None:
    path = REPLAY_DIR / "third-year-phd-student.conflict.off-default-replay.v1.json"
    payload = _load(path)
    gates = payload["gates"]
    assert isinstance(gates, dict)
    gates["source_overclaim_audit_passed"] = False

    with pytest.raises(
        ReplayHarnessValidationError,
        match="source_overclaim_audit_passed",
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
        ReplayHarnessValidationError,
        match="product_promotion",
    ):
        validate_replay_record_payload(payload, repo_root=REPO_ROOT)
