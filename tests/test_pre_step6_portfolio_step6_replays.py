from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_portfolio_step6_replays import validate_portfolio_step6_replay_payload  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "research/pre-step6-portfolio-step6-replays"


def test_portfolio_step6_replay_fixture_validates_and_blocks_runtime_promotion() -> None:
    paths = sorted(FIXTURE_DIR.glob("*.portfolio-step6-replay.v1.json"))

    assert [path.name for path in paths] == [
        "founder-grant-marcus-equity.high-clutter.portfolio-step6-replay.v1.json",
        "third-year-phd-student.v2.portfolio-step6-replay.v1.json",
    ]
    expected_decisions = {
        "founder-grant-marcus-equity.high-clutter.portfolio-step6-replay.v1.json": "pass_to_next_portfolio_replay",
        "third-year-phd-student.v2.portfolio-step6-replay.v1.json": "pass_to_next_portfolio_replay",
    }
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        validate_portfolio_step6_replay_payload(payload, path=path, repo_root=REPO_ROOT)

        assert payload["outcome"]["replay_decision"] == expected_decisions[path.name]
        assert payload["outcome"]["product_promotion"] == "blocked"
        assert payload["gates"]["runtime_wiring_allowed"] is False
        assert payload["gates"]["skill_update_allowed"] is False
