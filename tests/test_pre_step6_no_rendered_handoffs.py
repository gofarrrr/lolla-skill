from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_no_rendered_handoffs import (  # noqa: E402
    NoRenderedHandoffValidationError,
    summarize_no_rendered_handoff,
    validate_no_rendered_handoff_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
NO_RENDERED_DIR = REPO_ROOT / "research" / "pre-step6-no-rendered-handoffs"


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _no_rendered_paths() -> list[Path]:
    return sorted(NO_RENDERED_DIR.glob("*.no-rendered-handoff.v1.json"))


def test_all_no_rendered_handoffs_validate() -> None:
    paths = _no_rendered_paths()

    assert [path.name for path in paths] == [
        "mid-level-consultant-report-2.negative-control.native-rejudge.no-rendered-handoff.v1.json",
    ]

    payload = _load(paths[0])
    validate_no_rendered_handoff_payload(payload, path=paths[0], repo_root=REPO_ROOT)

    assert summarize_no_rendered_handoff(payload) == {
        "case_id": "mid-level-consultant-report-2",
        "decline_decision": "valid_research_decline",
        "naturalness_debt_risk": "medium",
        "expected_result": "healthy_decline",
        "simpler_arm_expected": "control_wins",
    }


def test_no_rendered_handoff_rejects_product_promotion() -> None:
    path = _no_rendered_paths()[0]
    payload = _load(path)
    gates = payload["gates"]
    assert isinstance(gates, dict)
    gates["product_promotion_allowed"] = True

    with pytest.raises(
        NoRenderedHandoffValidationError,
        match="product_promotion_allowed",
    ):
        validate_no_rendered_handoff_payload(payload, repo_root=REPO_ROOT)


def test_no_rendered_handoff_rejects_generator_implementation() -> None:
    path = _no_rendered_paths()[0]
    payload = _load(path)
    gates = payload["gates"]
    assert isinstance(gates, dict)
    gates["generator_implementation_allowed"] = True

    with pytest.raises(
        NoRenderedHandoffValidationError,
        match="generator_implementation_allowed",
    ):
        validate_no_rendered_handoff_payload(payload, repo_root=REPO_ROOT)


def test_no_rendered_handoff_rejects_hidden_answer_plan_language() -> None:
    path = _no_rendered_paths()[0]
    payload = _load(path)
    receipt = payload["decline_receipt"]
    assert isinstance(receipt, dict)
    receipt["decline_reason"] = "The correct answer is the control answer."

    with pytest.raises(
        NoRenderedHandoffValidationError,
        match="hidden answer-plan phrase",
    ):
        validate_no_rendered_handoff_payload(payload, repo_root=REPO_ROOT)


def test_no_rendered_handoff_rejects_missing_decline_evidence() -> None:
    path = _no_rendered_paths()[0]
    payload = _load(path)
    source_refs = payload["source_refs"]
    assert isinstance(source_refs, dict)
    source_refs.pop("semi_blind_comparison")
    source_refs.pop("replay_record")

    with pytest.raises(
        NoRenderedHandoffValidationError,
        match="valid decline requires",
    ):
        validate_no_rendered_handoff_payload(payload, repo_root=REPO_ROOT)


def test_no_rendered_handoff_rejects_cross_ref_case_drift() -> None:
    path = _no_rendered_paths()[0]
    payload = _load(path)
    source_refs = payload["source_refs"]
    assert isinstance(source_refs, dict)
    source_refs["raw_answer_core"] = (
        "research/pre-step6-raw-artifact-answer-cores/"
        "mother-address-year.raw-answer-core.v1.json"
    )

    with pytest.raises(
        NoRenderedHandoffValidationError,
        match="case_id mismatch",
    ):
        validate_no_rendered_handoff_payload(payload, repo_root=REPO_ROOT)
