from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_lens_step6_replays import validate_lens_step6_replay_payload  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "research/pre-step6-lens-step6-replays"


def test_bevelin_lens_step6_replay_fixtures_validate_and_keep_gate_cognitive() -> None:
    paths = sorted(FIXTURE_DIR.glob("*.bevelin-lens-step6-replay.v1.json"))

    assert [path.name for path in paths] == [
        "founder-grant-marcus-equity.high-clutter.bevelin-lens-step6-replay.v1.json",
        "third-year-phd-student.v2.bevelin-lens-step6-replay.v1.json",
    ]
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        validate_lens_step6_replay_payload(payload, path=path, repo_root=REPO_ROOT)

        gate = payload["cognitive_gate"]
        assert gate["judgment_mode"] == "human_static_research_judgment"
        assert "code validates" in gate["why_this_is_not_deterministic"]
        assert "quality" in gate["why_this_is_not_deterministic"]
        assert payload["comparison_vs_prior_replay"]["winner"] == "lens_replay"
        assert payload["outcome"]["product_promotion"] == "blocked"
        assert payload["gates"]["runtime_wiring_allowed"] is False
        assert payload["gates"]["skill_update_allowed"] is False
