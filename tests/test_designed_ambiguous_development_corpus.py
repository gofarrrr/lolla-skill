from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research/designed-ambiguous-pool-v1-2026-07-10"
MESSAGE_RE = re.compile(
    r"^\[Turn (\d+)\] (USER|ASSISTANT):\n(.+?)(?=\n\[Turn |\Z)",
    flags=re.MULTILINE | re.DOTALL,
)


def _json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def test_manifest_freezes_five_complete_provider_free_development_cases() -> None:
    manifest = _json(PACKAGE / "development-manifest.json")
    assert manifest["status"] == "frozen_complete"
    assert manifest["source_strategy"]["external_generation_call_used_for_these_files"] is False
    assert manifest["source_strategy"]["same_project_session_designed_and_authored"] is True
    assert manifest["source_strategy"]["clean_holdout"] is False
    assert len(manifest["cases"]) == 5
    for case in manifest["cases"]:
        path = ROOT / case["path"]
        assert path.is_file()
        assert _hash(path) == case["sha256"]
        assert len(path.read_bytes()) == case["byte_count"]
        assert len(path.read_text(encoding="utf-8").split()) == case["word_count"]


def test_every_case_has_seven_exact_alternating_turn_pairs() -> None:
    manifest = _json(PACKAGE / "development-manifest.json")
    expected = [(turn, role) for turn in range(1, 8) for role in ("USER", "ASSISTANT")]
    for case in manifest["cases"]:
        text = (ROOT / case["path"]).read_text(encoding="utf-8")
        messages = MESSAGE_RE.findall(text)
        observed = [(int(turn), role) for turn, role, _ in messages]
        assert observed == expected
        assert len(messages) == case["message_count"] == 14
        assert all(body.strip() for _, _, body in messages)


def test_development_text_has_no_explicit_evaluation_target_leakage() -> None:
    manifest = _json(PACKAGE / "development-manifest.json")
    forbidden = (
        "lolla",
        "mental model",
        "reasoning audit",
        "graph pressure",
        "expected finding",
        "gold answer",
    )
    for case in manifest["cases"]:
        text = (ROOT / case["path"]).read_text(encoding="utf-8").lower()
        for phrase in forbidden:
            assert phrase not in text


def test_frozen_rank_selects_first_development_case_without_holdout_claim() -> None:
    manifest = _json(PACKAGE / "development-manifest.json")
    review = _json(PACKAGE / "development-source-review.json")
    decision = _json(PACKAGE / "decision.json")
    assert manifest["frozen_rank"][0] == "amb1-case02-nonprofit-scale"
    assert manifest["selected_first_development_case_id"] == manifest["frozen_rank"][0]
    assert manifest["selected_clean_holdout_case_id"] is None
    assert review["selection"]["selected_development_case_id"] == manifest["frozen_rank"][0]
    assert review["selection"]["selected_for_likely_lolla_or_graph_value"] is False
    assert decision["provider_free_fallback"]["clean_holdout"] is False
    assert decision["authorizations"]["execute_development_stage_a"] is False


def test_interrupted_source_call_preserves_unknowns_and_no_retry() -> None:
    custody = _json(
        PACKAGE
        / "run/lolla_designed_ambiguous_pool_v1_20260710_a1/call-custody.json"
    )
    summary = _json(
        PACKAGE / "run/lolla_designed_ambiguous_pool_v1_20260710_a1/run-summary.json"
    )
    call = custody["call"]
    assert call["call_attempted"] is True
    assert call["http_response_read_started"] is True
    assert call["http_response_read_completed"] is False
    assert call["usage_evidence_state"] == "unknown"
    assert call["total_tokens"] is None
    assert call["estimated_cost_usd"] is None
    assert custody["automatic_retries"] == 0
    assert summary["status"] == "failed"
    assert summary["gates"]["wall_clock_ceiling_met"] is False
