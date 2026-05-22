from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_portfolio_blind_comparisons import (  # noqa: E402
    score_portfolio_blind_comparison,
    validate_portfolio_blind_comparison_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "research/pre-step6-portfolio-blind-comparisons"


def test_portfolio_blind_comparison_fixtures_validate_and_score() -> None:
    paths = sorted(FIXTURE_DIR.glob("*.portfolio-blind-comparison.v1.json"))

    assert {path.name for path in paths} == {
        "founder-grant-marcus-equity.high-clutter.portfolio-blind-comparison.v1.json",
        "mid-level-consultant-report-2.portfolio-blind-comparison.v1.json",
        "mother-address-year.portfolio-blind-comparison.v1.json",
        "third-year-phd-student.portfolio-blind-comparison.v1.json",
        "third-year-phd-student.v2.portfolio-blind-comparison.v1.json",
    }
    expected_decisions = {
        "founder-grant-marcus-equity.high-clutter.portfolio-blind-comparison.v1.json": "portfolio_wins",
        "mid-level-consultant-report-2.portfolio-blind-comparison.v1.json": "rendered_hybrid_wins",
        "mother-address-year.portfolio-blind-comparison.v1.json": "tie_keep_research_only",
        "third-year-phd-student.portfolio-blind-comparison.v1.json": "tie_keep_research_only",
        "third-year-phd-student.v2.portfolio-blind-comparison.v1.json": "portfolio_wins",
    }
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        validate_portfolio_blind_comparison_payload(
            payload,
            path=path,
            repo_root=REPO_ROOT,
        )
        score = score_portfolio_blind_comparison(payload)
        assert score["aggregate_decision"] == payload["aggregate_decision"]
        assert payload["aggregate_decision"] == expected_decisions[path.name]

        if path.name == "mid-level-consultant-report-2.portfolio-blind-comparison.v1.json":
            assert payload["promotion_read"] != "pass_to_step6_replay"
