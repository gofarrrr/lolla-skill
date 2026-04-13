"""Tests for trigger source tracking in _select_triggered_tendencies."""
from __future__ import annotations

import sys
from pathlib import Path

# Allow imports from the project root
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.system_b.triage import TriageScore
from engine.system_b.pipeline import _select_triggered_tendencies, TriggeredTendency


def test_triage_source_when_above_threshold():
    """A tendency exceeding triage threshold gets source='triage' and its score."""
    scores = [TriageScore(tendency_id="anchoring-tendency", score=8, evidence="anchored to first number")]
    result = _select_triggered_tendencies(scores, triage_threshold=5)
    assert len(result) == 1
    t = result[0]
    assert isinstance(t, TriggeredTendency)
    assert t.tendency_id == "anchoring-tendency"
    assert t.source == "triage"
    assert t.score == 8


def test_embedding_source_for_swiss_cheese_hit():
    """A tendency from embedding swiss cheese gets source='embedding' with cosine score."""
    scores = [TriageScore(tendency_id="anchoring-tendency", score=2, evidence="weak")]
    embedding_hits = {"inconsistency-avoidance-tendency": 0.87}
    result = _select_triggered_tendencies(
        scores, triage_threshold=5, embedding_tendency_hits=embedding_hits
    )
    # anchoring below threshold, only embedding hit triggers
    assert len(result) == 1
    t = result[0]
    assert t.tendency_id == "inconsistency-avoidance-tendency"
    assert t.source == "embedding"
    assert t.score == 0.87


def test_always_include_source():
    """A tendency from always_include gets source='always_include' with score 0."""
    result = _select_triggered_tendencies(
        [], triage_threshold=5, always_include=("sunk-cost-tendency",)
    )
    assert len(result) == 1
    t = result[0]
    assert t.tendency_id == "sunk-cost-tendency"
    assert t.source == "always_include"
    assert t.score == 0


def test_mixed_sources_preserve_order():
    """All three sources coexist and maintain insertion order."""
    scores = [
        TriageScore(tendency_id="anchoring-tendency", score=8, evidence="strong"),
        TriageScore(tendency_id="sunk-cost-tendency", score=2, evidence="weak"),
    ]
    result = _select_triggered_tendencies(
        scores,
        triage_threshold=5,
        always_include=("overoptimism-tendency",),
        embedding_tendency_hits={"inconsistency-avoidance-tendency": 0.91},
    )
    assert len(result) == 3
    assert result[0].source == "triage"
    assert result[1].source == "always_include"
    assert result[2].source == "embedding"
    # Verify they serialize cleanly
    serialized = [
        {"tendency_id": tt.tendency_id, "source": tt.source, "score": tt.score}
        for tt in result
    ]
    assert serialized[0]["tendency_id"] == "anchoring-tendency"
    assert serialized[0]["score"] == 8
    assert serialized[2]["score"] == 0.91


def test_triage_below_threshold_excluded():
    """Tendencies below triage threshold don't appear in results."""
    scores = [TriageScore(tendency_id="anchoring-tendency", score=3, evidence="weak")]
    result = _select_triggered_tendencies(scores, triage_threshold=5)
    assert len(result) == 0
