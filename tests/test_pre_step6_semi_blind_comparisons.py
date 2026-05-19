from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_semi_blind_comparisons import (  # noqa: E402
    SemiBlindComparisonValidationError,
    score_semi_blind_comparison,
    validate_semi_blind_comparison_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
COMPARISON_DIR = REPO_ROOT / "research" / "pre-step6-semi-blind-comparisons"


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _comparison_paths() -> list[Path]:
    return sorted(COMPARISON_DIR.glob("*.semi-blind-comparison.v1.json"))


def test_all_semi_blind_comparisons_validate() -> None:
    paths = _comparison_paths()

    assert [path.name for path in paths] == [
        "founder-grant-marcus-equity.high-clutter.native-rejudge.semi-blind-comparison.v1.json",
        "founder-grant-marcus-equity.high-clutter.semi-blind-comparison.v1.json",
        "mid-level-consultant-report-2.negative-control.semi-blind-comparison.v1.json",
        "mother-address-year.quiet.semi-blind-comparison.v1.json",
        "third-year-phd-student.conflict.semi-blind-comparison.v1.json",
    ]

    expected_scores = {
        "founder-grant-marcus-equity.high-clutter.native-rejudge.semi-blind-comparison.v1.json": {
            "control": 4,
            "raw": 0,
            "rendered_hybrid": 4,
            "tie": 0,
            "label_counts": {"A": 4, "B": 4, "C": 0, "tie": 0},
            "criterion_count_decision": "tie_stop",
            "aggregate_decision": "rendered_hybrid_wins",
        },
        "founder-grant-marcus-equity.high-clutter.semi-blind-comparison.v1.json": {
            "control": 2,
            "raw": 0,
            "rendered_hybrid": 4,
            "tie": 2,
            "label_counts": {"A": 0, "B": 2, "C": 4, "tie": 2},
            "criterion_count_decision": "rendered_hybrid_wins",
            "aggregate_decision": "rendered_hybrid_wins",
        },
        "mid-level-consultant-report-2.negative-control.semi-blind-comparison.v1.json": {
            "control": 7,
            "raw": 0,
            "rendered_hybrid": 1,
            "tie": 0,
            "label_counts": {"A": 1, "B": 7, "C": 0, "tie": 0},
            "criterion_count_decision": "control_wins",
            "aggregate_decision": "control_wins",
        },
        "mother-address-year.quiet.semi-blind-comparison.v1.json": {
            "control": 2,
            "raw": 0,
            "rendered_hybrid": 4,
            "tie": 2,
            "label_counts": {"A": 2, "B": 4, "C": 0, "tie": 2},
            "criterion_count_decision": "rendered_hybrid_wins",
            "aggregate_decision": "rendered_hybrid_wins",
        },
        "third-year-phd-student.conflict.semi-blind-comparison.v1.json": {
            "control": 1,
            "raw": 3,
            "rendered_hybrid": 3,
            "tie": 1,
            "label_counts": {"A": 3, "B": 3, "C": 1, "tie": 1},
            "criterion_count_decision": "tie_stop",
            "aggregate_decision": "rendered_hybrid_wins",
        },
    }

    for path in paths:
        payload = _load(path)
        validate_semi_blind_comparison_payload(
            payload,
            path=path,
            repo_root=REPO_ROOT,
        )
        score = score_semi_blind_comparison(payload)
        assert score == expected_scores[path.name]
        expected_promotion_read = (
            "stop"
            if path.name
            == "mid-level-consultant-report-2.negative-control.semi-blind-comparison.v1.json"
            else "pass_to_replay"
        )
        assert payload["promotion_read"] == expected_promotion_read


def test_semi_blind_comparison_rejects_duplicate_blind_map_arm() -> None:
    path = COMPARISON_DIR / "third-year-phd-student.conflict.semi-blind-comparison.v1.json"
    payload = _load(path)
    blind_map = payload["blind_map"]
    assert isinstance(blind_map, dict)
    blind_map["C"] = "raw"

    with pytest.raises(
        SemiBlindComparisonValidationError,
        match="blind_map arms",
    ):
        validate_semi_blind_comparison_payload(payload, repo_root=REPO_ROOT)


def test_semi_blind_comparison_rejects_wrong_criterion_order() -> None:
    path = COMPARISON_DIR / "third-year-phd-student.conflict.semi-blind-comparison.v1.json"
    payload = _load(path)
    criteria = payload["criteria"]
    assert isinstance(criteria, list)
    criteria[0], criteria[1] = criteria[1], criteria[0]

    with pytest.raises(
        SemiBlindComparisonValidationError,
        match="required semi-blind rubric order",
    ):
        validate_semi_blind_comparison_payload(payload, repo_root=REPO_ROOT)


def test_semi_blind_comparison_rejects_inconsistent_aggregate() -> None:
    path = COMPARISON_DIR / "third-year-phd-student.conflict.semi-blind-comparison.v1.json"
    payload = _load(path)
    payload["aggregate_winner_label"] = "A"

    with pytest.raises(
        SemiBlindComparisonValidationError,
        match="aggregate_decision",
    ):
        validate_semi_blind_comparison_payload(payload, repo_root=REPO_ROOT)


def test_semi_blind_comparison_rejects_replay_without_rendered_winner() -> None:
    path = COMPARISON_DIR / "third-year-phd-student.conflict.semi-blind-comparison.v1.json"
    payload = _load(path)
    payload["aggregate_winner_label"] = "A"
    payload["aggregate_decision"] = "raw_wins"

    with pytest.raises(
        SemiBlindComparisonValidationError,
        match="pass_to_replay requires rendered_hybrid_wins",
    ):
        validate_semi_blind_comparison_payload(payload, repo_root=REPO_ROOT)
