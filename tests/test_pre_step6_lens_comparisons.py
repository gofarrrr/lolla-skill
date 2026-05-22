from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_lens_comparisons import (  # noqa: E402
    score_lens_comparison,
    validate_lens_comparison_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "research/pre-step6-lens-comparisons"


def test_bevelin_lens_comparison_fixtures_validate_and_score_fixed_suite() -> None:
    paths = sorted(FIXTURE_DIR.glob("*.bevelin-comparison.v1.json"))

    assert {path.name for path in paths} == {
        "founder-grant-marcus-equity.high-clutter.bevelin-comparison.v1.json",
        "mid-level-consultant-report-2.bevelin-comparison.v1.json",
        "mother-address-year.bevelin-comparison.v1.json",
        "third-year-phd-student.v2.bevelin-comparison.v1.json",
    }
    expected_decisions = {
        "founder-grant-marcus-equity.high-clutter.bevelin-comparison.v1.json": "lens_improves",
        "mid-level-consultant-report-2.bevelin-comparison.v1.json": "lens_boundary_case",
        "mother-address-year.bevelin-comparison.v1.json": "lens_boundary_case",
        "third-year-phd-student.v2.bevelin-comparison.v1.json": "lens_improves",
    }
    expected_promotions = {
        "founder-grant-marcus-equity.high-clutter.bevelin-comparison.v1.json": "expand_replay",
        "mid-level-consultant-report-2.bevelin-comparison.v1.json": "stop",
        "mother-address-year.bevelin-comparison.v1.json": "retest",
        "third-year-phd-student.v2.bevelin-comparison.v1.json": "expand_replay",
    }
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        validate_lens_comparison_payload(
            payload,
            path=path,
            repo_root=REPO_ROOT,
        )
        score = score_lens_comparison(payload)
        assert score["aggregate_decision"] == payload["aggregate_decision"]
        assert payload["aggregate_decision"] == expected_decisions[path.name]
        assert payload["promotion_read"] == expected_promotions[path.name]
