"""PR 2 Fix #1 — persist full top-25 embedding tendency ranks.

`_embedding_tendency_signal` ranks the top-25 tendencies by cosine
similarity but discards every row below the 0.30 threshold. The
sub-threshold rows are exactly the "close calls" an operator would want
to see. This test pins the new return contract: the function exposes
the full ranked list (with a `promoted: bool` flag per row) AND the
legacy promoted-only dict that feeds Pass 2.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.system_b.pipeline import (
    _embedding_tendency_signal,
    _select_triggered_tendencies,
)


class _StubRetriever:
    """Stand-in for `OpenAIEmbeddingRetriever` with deterministic ranks."""

    def __init__(self, ranked_rows: list[dict]) -> None:
        self._ranked_rows = ranked_rows

    def embed_and_cache(self, _text: str, _api_key: str) -> list[float]:
        return [0.0]

    def rank_tendencies(self, _query_vec, top_k: int = 25) -> list[dict]:
        return self._ranked_rows[:top_k]


def _ranked_rows() -> list[dict]:
    return [
        {"tendency_id": "anchoring-tendency", "score": 0.42},
        {"tendency_id": "inconsistency-avoidance-tendency", "score": 0.34},
        {"tendency_id": "stress-influence-tendency", "score": 0.31},
        {"tendency_id": "doubt-avoidance-tendency", "score": 0.28},
        {"tendency_id": "deprival-superreaction-tendency", "score": 0.22},
        {"tendency_id": "sunk-cost-tendency", "score": 0.18},
    ]


def test_signal_returns_promoted_dict_and_full_ranks_with_flags():
    retriever = _StubRetriever(_ranked_rows())
    promoted, ranks = _embedding_tendency_signal(
        assistant_text="anything",
        retriever=retriever,
        api_key="sk-test",
    )

    # Legacy promoted-only dict: only rows ≥ 0.30 threshold
    assert promoted == {
        "anchoring-tendency": 0.42,
        "inconsistency-avoidance-tendency": 0.34,
        "stress-influence-tendency": 0.31,
    }

    # Full ranked list: every row, with promoted flag
    assert len(ranks) == 6
    assert all(set(row.keys()) == {"tendency_id", "score", "promoted"} for row in ranks)
    assert [r["tendency_id"] for r in ranks] == [
        "anchoring-tendency",
        "inconsistency-avoidance-tendency",
        "stress-influence-tendency",
        "doubt-avoidance-tendency",
        "deprival-superreaction-tendency",
        "sunk-cost-tendency",
    ]
    assert [r["promoted"] for r in ranks] == [True, True, True, False, False, False]


def test_signal_returns_empty_when_no_retriever():
    promoted, ranks = _embedding_tendency_signal(
        assistant_text="anything",
        retriever=None,
        api_key="",
    )
    assert promoted == {}
    assert ranks == []


def test_select_triggered_tendencies_only_promotes_thresholded_rows():
    """Behavior preservation: Pass 2 must not fire for sub-threshold rows."""
    from engine.system_b.triage import TriageScore

    retriever = _StubRetriever(_ranked_rows())
    promoted, _ranks = _embedding_tendency_signal(
        assistant_text="x",
        retriever=retriever,
        api_key="sk-test",
    )

    triggered = _select_triggered_tendencies(
        triage_scores=[TriageScore(tendency_id="anchoring-tendency", score=0, evidence="")],
        triage_threshold=5,
        embedding_tendency_hits=promoted,
    )

    triggered_ids = {tt.tendency_id for tt in triggered}
    assert triggered_ids == {
        "anchoring-tendency",
        "inconsistency-avoidance-tendency",
        "stress-influence-tendency",
    }
    # Sub-threshold rows must NOT promote into Pass 2
    assert "doubt-avoidance-tendency" not in triggered_ids
    assert "sunk-cost-tendency" not in triggered_ids
