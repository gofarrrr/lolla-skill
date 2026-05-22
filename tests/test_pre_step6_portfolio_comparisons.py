from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_portfolio_comparisons import validate_portfolio_comparison_payload  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "research/pre-step6-portfolio-comparisons"


def test_portfolio_comparison_fixtures_validate_and_name_core_judgment() -> None:
    paths = sorted(FIXTURE_DIR.glob("*.portfolio-comparison.v1.json"))

    assert {path.name for path in paths} == {
        "founder-grant-marcus-equity.high-clutter.portfolio-comparison.v1.json",
        "mid-level-consultant-report-2.portfolio-comparison.v1.json",
        "mother-address-year.portfolio-comparison.v1.json",
        "third-year-phd-student.portfolio-comparison.v1.json",
    }
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        validate_portfolio_comparison_payload(payload, path=path)
        assert payload["case_id"]
        assert payload["source_refs"]
        assert payload["aggregate_judgment"] in {
            "portfolio_wins",
            "portfolio_promising",
            "raw_or_hybrid_wins",
            "tie_keep_research_only",
            "negative_control_success",
        }
