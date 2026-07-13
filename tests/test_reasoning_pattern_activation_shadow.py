from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.system_b.activation_matcher import match_activation
from engine.system_b.reasoning_pattern_activation_shadow import (
    ReasoningPatternActivationShadowError,
    fingerprint_fact_boundary,
    fingerprint_from_reasoning_pattern_packet,
)

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "research/reasoning-process-graph-impact-shadow-2026-07-12/result.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_adapter_emits_controlled_fact_free_fingerprint() -> None:
    packet = _load(RESULT)["arms"]["housing_source_first"]["packet"]
    fingerprint = fingerprint_from_reasoning_pattern_packet(packet)
    assert [move.move_id for move in fingerprint.validated] == ["rp_001", "rp_002", "rp_003"]
    assert all(move.evidence_quotes == [] for move in fingerprint.validated)
    assert "missing reversal condition" in [move.reasoning_move for move in fingerprint.validated]
    boundary = fingerprint_fact_boundary(fingerprint)
    assert boundary["all_evidence_quotes_empty"] is True
    assert boundary["controlled_reasoning_moves_only"] is True
    assert all(value is False for key, value in boundary.items() if key.endswith("_included"))
    serialized = json.dumps([move.__dict__ for move in fingerprint.validated]).lower()
    for forbidden in ("housing", "registry", "tenant", "patient", "pilot", "e034", "e036"):
        assert forbidden not in serialized


def test_activation_matcher_accepts_adapter_type_and_sees_only_controlled_text(tmp_path: Path) -> None:
    packet = _load(RESULT)["arms"]["registry_source_first"]["packet"]
    fingerprint = fingerprint_from_reasoning_pattern_packet(packet)
    seen = []
    def embedder(text: str, api_key: str):
        seen.append(text)
        return [1.0, 0.0]
    output = match_activation(fingerprint, [], db_path=tmp_path / "missing.db", api_key="test", embedder=embedder)
    assert output == ()
    assert len(seen) == 1
    text = seen[0]
    assert "acknowledged constraint not gated" in text
    assert "missing reversal condition" in text
    assert "patient" not in text.lower()


def test_adapter_rejects_unlinted_projection() -> None:
    packet = _load(RESULT)["arms"]["housing_source_first"]["packet"]
    packet["routing_projection"]["contains_case_context"] = True
    with pytest.raises(ReasoningPatternActivationShadowError):
        fingerprint_from_reasoning_pattern_packet(packet)
