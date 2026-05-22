from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_problem_states import (  # noqa: E402
    ProblemStateValidationError,
    validate_problem_state_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "research" / "pre-step6-problem-states"


def _load_fixture(name: str) -> dict[str, object]:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def test_valid_problem_state_fixture_validates() -> None:
    payload = _load_fixture("mother-address-year.problem-state.v1.json")

    validate_problem_state_payload(payload)


def test_problem_state_rejects_missing_source_refs() -> None:
    payload = _load_fixture("mother-address-year.problem-state.v1.json")
    payload["source_refs"] = []

    with pytest.raises(ProblemStateValidationError, match="source_refs"):
        validate_problem_state_payload(payload)


def test_problem_state_rejects_final_advice_language() -> None:
    payload = _load_fixture("mother-address-year.problem-state.v1.json")
    payload["why"] = "The best option is to accept the address-year plan."

    with pytest.raises(ProblemStateValidationError, match="forbidden language"):
        validate_problem_state_payload(payload)


def test_static_problem_state_fixtures_validate() -> None:
    paths = sorted(FIXTURE_DIR.glob("*.problem-state.v1.json"))

    assert {path.name for path in paths} == {
        "founder-grant-marcus-equity.high-clutter.problem-state.v1.json",
        "mid-level-consultant-report-2.problem-state.v1.json",
        "mother-address-year.problem-state.v1.json",
        "third-year-phd-student.problem-state.v1.json",
    }
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        validate_problem_state_payload(payload, path=path)
