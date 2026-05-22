from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_decline_evaluations import (  # noqa: E402
    DeclineEvaluationValidationError,
    summarize_decline_evaluation,
    validate_decline_evaluation_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
DECLINE_EVAL_DIR = REPO_ROOT / "research" / "pre-step6-decline-evaluations"


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _decline_eval_paths() -> list[Path]:
    return sorted(DECLINE_EVAL_DIR.glob("*.no-rendered-decline-evaluation.v1.json"))


def test_all_decline_evaluations_validate() -> None:
    paths = _decline_eval_paths()

    assert [path.name for path in paths] == [
        "mid-level-consultant-report-2.negative-control.no-rendered-decline-evaluation.v1.json",
        "third-year-phd-student.conflict.adversarial.no-rendered-decline-evaluation.v1.json",
        "user-has-plan-consulting-launch.static-decline.no-rendered-decline-evaluation.v1.json",
    ]

    expected = {
        "mid-level-consultant-report-2.negative-control.no-rendered-decline-evaluation.v1.json": {
            "case_id": "mid-level-consultant-report-2",
            "comparison_decision": "raw_wins",
            "decline_evaluation_decision": "healthy_decline",
            "generator_next_step": "blocked",
            "naturalness_debt_avoided": "medium",
        },
        "third-year-phd-student.conflict.adversarial.no-rendered-decline-evaluation.v1.json": {
            "case_id": "third-year-phd-student",
            "comparison_decision": "raw_wins",
            "decline_evaluation_decision": "missed_decline",
            "generator_next_step": "blocked",
            "naturalness_debt_avoided": "none",
        },
        "user-has-plan-consulting-launch.static-decline.no-rendered-decline-evaluation.v1.json": {
            "case_id": "user-has-plan-consulting-launch",
            "comparison_decision": "raw_wins",
            "decline_evaluation_decision": "healthy_decline",
            "generator_next_step": "blocked",
            "naturalness_debt_avoided": "medium",
        },
    }

    for path in paths:
        payload = _load(path)
        validate_decline_evaluation_payload(payload, path=path, repo_root=REPO_ROOT)
        assert summarize_decline_evaluation(payload) == expected[path.name]


def test_decline_evaluation_rejects_rendered_candidate_requirement() -> None:
    path = _decline_eval_paths()[0]
    payload = _load(path)
    gates = payload["gates"]
    assert isinstance(gates, dict)
    gates["rendered_candidate_required"] = True

    with pytest.raises(
        DeclineEvaluationValidationError,
        match="rendered_candidate_required",
    ):
        validate_decline_evaluation_payload(payload, repo_root=REPO_ROOT)


def test_decline_evaluation_rejects_source_audit_requirement() -> None:
    path = _decline_eval_paths()[0]
    payload = _load(path)
    gates = payload["gates"]
    assert isinstance(gates, dict)
    gates["source_overclaim_audit_required"] = True

    with pytest.raises(
        DeclineEvaluationValidationError,
        match="source_overclaim_audit_required",
    ):
        validate_decline_evaluation_payload(payload, repo_root=REPO_ROOT)


def test_decline_evaluation_rejects_generator_next_step() -> None:
    path = _decline_eval_paths()[0]
    payload = _load(path)
    outcome = payload["outcome"]
    assert isinstance(outcome, dict)
    outcome["generator_next_step"] = "schema_only_next"

    with pytest.raises(
        DeclineEvaluationValidationError,
        match="generator_next_step",
    ):
        validate_decline_evaluation_payload(payload, repo_root=REPO_ROOT)


def test_decline_evaluation_rejects_comparison_drift() -> None:
    path = _decline_eval_paths()[0]
    payload = _load(path)
    outcome = payload["outcome"]
    assert isinstance(outcome, dict)
    outcome["comparison_decision"] = "control_wins"

    with pytest.raises(
        DeclineEvaluationValidationError,
        match="must match simpler comparison",
    ):
        validate_decline_evaluation_payload(payload, repo_root=REPO_ROOT)


def test_decline_evaluation_rejects_failed_miss_check_as_healthy() -> None:
    path = _decline_eval_paths()[0]
    payload = _load(path)
    miss_checks = payload["miss_checks"]
    assert isinstance(miss_checks, list)
    first = miss_checks[0]
    assert isinstance(first, dict)
    first["severity"] = "fail"

    with pytest.raises(
        DeclineEvaluationValidationError,
        match="healthy decline is invalid",
    ):
        validate_decline_evaluation_payload(payload, repo_root=REPO_ROOT)


def test_decline_evaluation_missed_decline_requires_failed_miss_check() -> None:
    path = (
        DECLINE_EVAL_DIR
        / "third-year-phd-student.conflict.adversarial.no-rendered-decline-evaluation.v1.json"
    )
    payload = _load(path)
    miss_checks = payload["miss_checks"]
    assert isinstance(miss_checks, list)
    for check in miss_checks:
        assert isinstance(check, dict)
        if check["severity"] == "fail":
            check["severity"] = "watch"

    with pytest.raises(
        DeclineEvaluationValidationError,
        match="missed decline requires",
    ):
        validate_decline_evaluation_payload(payload, repo_root=REPO_ROOT)


def test_decline_evaluation_must_match_decline_candidate_expectation() -> None:
    path = (
        DECLINE_EVAL_DIR
        / "third-year-phd-student.conflict.adversarial.no-rendered-decline-evaluation.v1.json"
    )
    payload = _load(path)
    outcome = payload["outcome"]
    assert isinstance(outcome, dict)
    outcome["decline_evaluation_decision"] = "retest_decline"

    with pytest.raises(
        DeclineEvaluationValidationError,
        match="must match decline candidate expected_result",
    ):
        validate_decline_evaluation_payload(payload, repo_root=REPO_ROOT)
