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
        "third-year-phd-student.conflict.semi-blind-comparison.v1.json",
    ]

    payload = _load(paths[0])
    validate_semi_blind_comparison_payload(payload, path=paths[0], repo_root=REPO_ROOT)

    score = score_semi_blind_comparison(payload)
    assert score["control"] == 1
    assert score["raw"] == 3
    assert score["rendered_hybrid"] == 3
    assert score["tie"] == 1
    assert score["label_counts"] == {"A": 3, "B": 3, "C": 1, "tie": 1}
    assert score["criterion_count_decision"] == "tie_stop"
    assert score["aggregate_decision"] == "rendered_hybrid_wins"
    assert payload["promotion_read"] == "pass_to_replay"


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
