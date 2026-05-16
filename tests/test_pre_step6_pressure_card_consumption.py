from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_pressure_card_consumption import (  # noqa: E402
    PressureCardConsumptionValidationError,
    score_pressure_vs_raw_comparison,
    validate_pressure_answer_core_payload,
    validate_pressure_vs_raw_comparison_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
ANSWER_CORE_DIR = REPO_ROOT / "research" / "pre-step6-pressure-card-answer-cores"
COMPARISON_DIR = REPO_ROOT / "research" / "pre-step6-pressure-vs-raw-comparisons"


def _answer_core_paths() -> list[Path]:
    return sorted(ANSWER_CORE_DIR.glob("*.pressure-answer-core.v1.json"))


def _comparison_paths() -> list[Path]:
    return sorted(COMPARISON_DIR.glob("*.pressure-vs-raw-comparison.v1.json"))


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_all_pressure_answer_cores_validate() -> None:
    paths = _answer_core_paths()

    assert [path.name for path in paths] == [
        "founder-grant-marcus-equity.native.pressure-answer-core.v1.json",
        "mid-level-consultant-report-2.native.pressure-answer-core.v1.json",
        "third-year-phd-student.native.pressure-answer-core.v1.json",
    ]

    for path in paths:
        validate_pressure_answer_core_payload(_load(path), path=path, repo_root=REPO_ROOT)


def test_all_pressure_vs_raw_comparisons_validate() -> None:
    paths = _comparison_paths()

    assert [path.name for path in paths] == [
        "founder-grant-marcus-equity.pressure-vs-raw-comparison.v1.json",
        "mid-level-consultant-report-2.pressure-vs-raw-comparison.v1.json",
        "third-year-phd-student.pressure-vs-raw-comparison.v1.json",
    ]

    expected_decisions = {
        "founder-grant-marcus-equity": "pressure_wins",
        "mid-level-consultant-report-2": "raw_wins",
        "third-year-phd-student": "tie_stop",
    }
    for path in paths:
        payload = _load(path)
        validate_pressure_vs_raw_comparison_payload(
            payload,
            path=path,
            repo_root=REPO_ROOT,
        )
        score = score_pressure_vs_raw_comparison(payload)
        assert score["aggregate_decision"] == expected_decisions[payload["case_id"]]


def test_pressure_answer_core_rejects_missing_inclusion() -> None:
    path = ANSWER_CORE_DIR / "third-year-phd-student.native.pressure-answer-core.v1.json"
    payload = _load(path)
    payload["expected_inclusions"] = ["not in the answer core"]

    with pytest.raises(
        PressureCardConsumptionValidationError,
        match="expected inclusion",
    ):
        validate_pressure_answer_core_payload(payload, repo_root=REPO_ROOT)


def test_pressure_answer_core_rejects_private_machinery() -> None:
    path = ANSWER_CORE_DIR / "founder-grant-marcus-equity.native.pressure-answer-core.v1.json"
    payload = _load(path)
    payload["answer_core"] = "This public answer mentions an artifact."

    with pytest.raises(
        PressureCardConsumptionValidationError,
        match="private machinery",
    ):
        validate_pressure_answer_core_payload(payload, repo_root=REPO_ROOT)


def test_pressure_vs_raw_comparison_rejects_inconsistent_aggregate() -> None:
    path = COMPARISON_DIR / "founder-grant-marcus-equity.pressure-vs-raw-comparison.v1.json"
    payload = _load(path)
    payload["aggregate_decision"] = "raw_wins"

    with pytest.raises(
        PressureCardConsumptionValidationError,
        match="aggregate_decision",
    ):
        validate_pressure_vs_raw_comparison_payload(payload, repo_root=REPO_ROOT)


def test_pressure_vs_raw_comparison_rejects_unknown_winner() -> None:
    path = COMPARISON_DIR / "mid-level-consultant-report-2.pressure-vs-raw-comparison.v1.json"
    payload = _load(path)
    criteria = payload["criteria"]
    assert isinstance(criteria, list)
    first = criteria[0]
    assert isinstance(first, dict)
    first["winner"] = "control"

    with pytest.raises(
        PressureCardConsumptionValidationError,
        match="unknown winner",
    ):
        validate_pressure_vs_raw_comparison_payload(payload, repo_root=REPO_ROOT)
