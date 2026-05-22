from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_portfolio_answer_cores import validate_portfolio_answer_core_payload  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "research/pre-step6-portfolio-answer-cores"


def test_portfolio_answer_core_fixtures_validate() -> None:
    paths = sorted(FIXTURE_DIR.glob("*.portfolio-answer-core.v1.json"))

    assert {path.name for path in paths} == {
        "founder-grant-marcus-equity.high-clutter.native.portfolio-answer-core.v1.json",
        "mid-level-consultant-report-2.native.portfolio-answer-core.v1.json",
        "mother-address-year.native.portfolio-answer-core.v1.json",
        "third-year-phd-student.native.portfolio-answer-core.v1.json",
        "third-year-phd-student.v2.native.portfolio-answer-core.v1.json",
    }
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        validate_portfolio_answer_core_payload(
            payload,
            path=path,
            repo_root=REPO_ROOT,
        )
