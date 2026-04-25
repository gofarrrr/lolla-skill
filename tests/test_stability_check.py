"""Tests for Mode C drift harness extensions (canonical_key Jaccard +
invalid_key_rate + cross-capture aggregation).

TDD red-green scaffolding for PR #1 of the extraction contract roadmap.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import stability_check as sc  # noqa: E402
from stability_check import compute_extraction_drift  # noqa: E402

# ---------------------------------------------------------------------------
# PR #1b — embedding cosine helpers
# ---------------------------------------------------------------------------

import numpy as np  # noqa: E402


def test_rerun_pipeline_uses_conversation_contract(monkeypatch, tmp_path):
    """Mode B reruns the conversation-first pipeline path."""
    captured: list[list[str]] = []

    def _fake_run(cmd: list[str], *, check: bool, cwd: str) -> None:  # noqa: ARG001
        captured.append(cmd)

    monkeypatch.setattr(sc.subprocess, "run", _fake_run)
    monkeypatch.setattr(sc.time, "sleep", lambda seconds: None)

    sc._rerun_pipeline(
        tmp_path / "extraction.json",
        tmp_path / "conversation.txt",
        1,
        tmp_path,
    )

    assert len(captured) == 1
    assert "--conversation-file" in captured[0]
    assert not any(part.startswith("--legacy") for part in captured[0])


def test_cosine_identical_vectors_is_one():
    """Self-similarity sanity: cosine of a vector with itself is 1.0."""
    from stability_check import _cosine_similarity
    v = np.array([1.0, 2.0, 3.0, 4.0])
    assert abs(_cosine_similarity(v, v) - 1.0) < 1e-6


def test_cosine_orthogonal_vectors_is_zero():
    """Orthogonal vectors: cosine is 0."""
    from stability_check import _cosine_similarity
    a = np.array([1.0, 0.0])
    b = np.array([0.0, 1.0])
    assert abs(_cosine_similarity(a, b)) < 1e-6


def test_cosine_opposite_vectors_is_negative_one():
    """Opposite-direction vectors: cosine is -1.0."""
    from stability_check import _cosine_similarity
    a = np.array([1.0, 1.0])
    b = np.array([-1.0, -1.0])
    assert abs(_cosine_similarity(a, b) - (-1.0)) < 1e-6


def test_best_match_mean_identical_lists_is_one():
    """Two identical lists of vectors: best-match mean is 1.0 (every item has a perfect partner)."""
    from stability_check import _best_match_mean_cosine
    vecs_a = [np.array([1.0, 0.0]), np.array([0.0, 1.0])]
    vecs_b = [np.array([1.0, 0.0]), np.array([0.0, 1.0])]
    assert abs(_best_match_mean_cosine(vecs_a, vecs_b) - 1.0) < 1e-6


def test_best_match_mean_empty_lists_returns_none():
    """Both lists empty → undefined (None). Matches empty-set Jaccard doctrine."""
    from stability_check import _best_match_mean_cosine
    assert _best_match_mean_cosine([], []) is None


def test_best_match_mean_one_empty_list_returns_zero():
    """One side empty → 0.0 (no agreement possible)."""
    from stability_check import _best_match_mean_cosine
    vecs_a = [np.array([1.0, 0.0])]
    assert _best_match_mean_cosine(vecs_a, []) == 0.0
    assert _best_match_mean_cosine([], vecs_a) == 0.0


def test_best_match_mean_different_lengths_penalizes_unmatched():
    """Short list fully matches; longer list's unmatched items count as 0 penalty
    against the longer-list size. Prevents a trivially high score when one
    side has many fewer items than the other."""
    from stability_check import _best_match_mean_cosine
    vecs_a = [np.array([1.0, 0.0])]  # 1 item
    vecs_b = [np.array([1.0, 0.0]), np.array([0.0, 1.0])]  # 2 items
    # Best match for a[0] is b[0] with cosine 1.0. b[1] is unmatched.
    # Denominator = max(len_a, len_b) = 2. Mean = (1.0 + 0.0) / 2 = 0.5.
    result = _best_match_mean_cosine(vecs_a, vecs_b)
    assert abs(result - 0.5) < 1e-6


# ---------------------------------------------------------------------------
# PR #1b — compute_extraction_drift integration for canonical_key embedding
# ---------------------------------------------------------------------------
#
# These tests use a mocked embedding function so the test suite doesn't
# require a live OpenAI API call.

def test_drift_includes_canonical_key_embedding_pair_block(monkeypatch):
    """When both runs have matching canonical_keys (semantically identical
    strings), the pair's live_constraints_canonical_key_embedding metric
    reports mean_cosine ~ 1.0."""
    # Stub the embedding fetcher so we don't need network
    embeddings = {
        "alpha-one": np.array([1.0, 0.0, 0.0]),
        "alpha-two": np.array([0.0, 1.0, 0.0]),
        "alpha-three": np.array([0.0, 0.0, 1.0]),
    }
    import stability_check as sc
    monkeypatch.setattr(sc, "_get_embedding", lambda s: embeddings[s])

    run_a = _make_extraction([
        {"constraint": "c1", "canonical_key": "alpha-one"},
        {"constraint": "c2", "canonical_key": "alpha-two"},
    ])
    run_b = _make_extraction([
        {"constraint": "c1", "canonical_key": "alpha-one"},
        {"constraint": "c2", "canonical_key": "alpha-two"},
    ])
    drift = sc.compute_extraction_drift([("a", run_a), ("b", run_b)])
    pair = drift["pairs"][0]
    assert "live_constraints_canonical_key_embedding" in pair
    assert pair["live_constraints_canonical_key_embedding"]["mean_cosine"] == 1.0


def test_drift_embedding_semantically_close_slugs(monkeypatch):
    """Slugs like marcus-comp and marcus-comp-below-market are both about
    the same subject; embeddings should rate them close. Here we stub two
    vectors that are 0.95-cosine close to simulate this."""
    v1 = np.array([1.0, 0.0, 0.0])
    v2 = np.array([0.95, 0.3122, 0.0])  # cosine with v1 ≈ 0.95
    v2 = v2 / np.linalg.norm(v2)
    embeddings = {"marcus-comp": v1, "marcus-comp-below-market": v2}
    import stability_check as sc
    monkeypatch.setattr(sc, "_get_embedding", lambda s: embeddings[s])

    run_a = _make_extraction([{"constraint": "c", "canonical_key": "marcus-comp"}])
    run_b = _make_extraction([{"constraint": "c", "canonical_key": "marcus-comp-below-market"}])
    drift = sc.compute_extraction_drift([("a", run_a), ("b", run_b)])
    pair = drift["pairs"][0]
    score = pair["live_constraints_canonical_key_embedding"]["mean_cosine"]
    assert score >= 0.90, f"Expected ≥0.90 (semantically close), got {score}"


def test_drift_embedding_both_empty_returns_none(monkeypatch):
    """Both runs have empty canonical_keys after filtering → metric is None
    (undefined), not 1.0. Parallel to the exact-text Jaccard both-empty case."""
    import stability_check as sc
    monkeypatch.setattr(sc, "_get_embedding", lambda s: np.array([1.0, 0.0]))

    run_a = _make_extraction([{"constraint": "x", "canonical_key": ""}])
    run_b = _make_extraction([{"constraint": "y", "canonical_key": ""}])
    drift = sc.compute_extraction_drift([("a", run_a), ("b", run_b)])
    pair = drift["pairs"][0]
    assert pair["live_constraints_canonical_key_embedding"]["mean_cosine"] is None


def test_drift_aggregate_has_canonical_key_embedding_block(monkeypatch):
    """Aggregate result includes live_constraints_canonical_key_embedding
    with mean_cosine/min_cosine/max_cosine, filtering None pairs."""
    embeddings = {
        "alpha-one": np.array([1.0, 0.0]),
        "alpha-two": np.array([0.0, 1.0]),
    }
    import stability_check as sc
    monkeypatch.setattr(sc, "_get_embedding", lambda s: embeddings[s])

    run_a = _make_extraction([{"constraint": "c", "canonical_key": "alpha-one"}])
    run_b = _make_extraction([{"constraint": "c", "canonical_key": "alpha-one"}])
    run_c = _make_extraction([{"constraint": "c", "canonical_key": "alpha-two"}])
    drift = sc.compute_extraction_drift([
        ("a", run_a), ("b", run_b), ("c", run_c)
    ])
    agg = drift["aggregate"]
    assert "live_constraints_canonical_key_embedding" in agg
    block = agg["live_constraints_canonical_key_embedding"]
    # Pairs: (a,b)=1.0, (a,c)=0.0, (b,c)=0.0 → mean=0.333, min=0.0, max=1.0
    assert abs(block["mean_cosine"] - (1.0 / 3)) < 0.01
    assert block["min_cosine"] == 0.0
    assert block["max_cosine"] == 1.0


def _make_extraction(constraints: list[dict]) -> dict:
    """Build a minimal extraction payload with just live_constraints populated.
    Other fields are stubbed so compute_extraction_drift doesn't KeyError."""
    return {
        "extraction": {
            "decision_situation": "",
            "original_framing": "",
            "synthesized_position": "",
            "live_constraints": constraints,
            "reasoning_passages": [],
            "dropped_threads": [],
            "_quote_validation": {"fabricated": 0},
        },
        "capture_health": "good",
    }


def test_canonical_key_jaccard_full_match():
    """Two runs with identical non-empty canonical_keys → Jaccard = 1.0."""
    run_a = _make_extraction([
        {"constraint": "A1", "canonical_key": "alpha-one"},
        {"constraint": "A2", "canonical_key": "alpha-two"},
        {"constraint": "A3", "canonical_key": "alpha-three"},
    ])
    run_b = _make_extraction([
        {"constraint": "B1", "canonical_key": "alpha-one"},
        {"constraint": "B2", "canonical_key": "alpha-two"},
        {"constraint": "B3", "canonical_key": "alpha-three"},
    ])
    drift = compute_extraction_drift([("a", run_a), ("b", run_b)])
    pair = drift["pairs"][0]
    assert "live_constraints_canonical_key" in pair
    assert pair["live_constraints_canonical_key"]["jaccard"] == 1.0


def test_aggregate_includes_canonical_key_block():
    """Aggregate result has live_constraints_canonical_key with mean/min/max,
    filtering out None pair values before aggregation."""
    # 3 runs: A and B have matching keys (Jaccard 1.0); C has a degenerate
    # all-empty set (Jaccard None when paired with A or B via nonempty filter
    # — wait, when paired against a non-empty set the nonempty helper returns
    # 0.0, not None. None is only when BOTH are empty. Use a mix to force
    # inclusion.)
    run_a = _make_extraction([{"constraint": "x", "canonical_key": "same-key-here"}])
    run_b = _make_extraction([{"constraint": "y", "canonical_key": "same-key-here"}])
    run_c = _make_extraction([{"constraint": "z", "canonical_key": "different-key-two"}])
    drift = compute_extraction_drift([("a", run_a), ("b", run_b), ("c", run_c)])
    agg = drift["aggregate"]
    assert "live_constraints_canonical_key" in agg
    block = agg["live_constraints_canonical_key"]
    # Pairs: (a,b)=1.0, (a,c)=0.0, (b,c)=0.0 → mean=0.333, min=0.0, max=1.0
    assert block["mean_jaccard"] == round((1.0 + 0.0 + 0.0) / 3, 3)
    assert block["min_jaccard"] == 0.0
    assert block["max_jaccard"] == 1.0


def test_aggregate_skips_none_pairs():
    """Aggregate filters out None pairs (both-empty degenerate) before mean."""
    run_a = _make_extraction([{"constraint": "x", "canonical_key": "alpha-beta"}])
    run_b = _make_extraction([{"constraint": "y", "canonical_key": "alpha-beta"}])
    # run_c forces a None pair when paired with a degenerate empty-only run.
    # Construct run_d as all-empty so (c, d) pair... actually simpler: use
    # two runs both all-empty, one valid. Pairs: (valid, empty)=0.0,
    # (valid, empty)=0.0, (empty, empty)=None. Mean over non-None = 0.0.
    run_e1 = _make_extraction([{"constraint": "a", "canonical_key": "valid-key"}])
    run_e2 = _make_extraction([{"constraint": "b", "canonical_key": ""}])
    run_e3 = _make_extraction([{"constraint": "c", "canonical_key": ""}])
    drift = compute_extraction_drift([("1", run_e1), ("2", run_e2), ("3", run_e3)])
    agg = drift["aggregate"]
    block = agg["live_constraints_canonical_key"]
    # Pairs: (1,2)=0.0 (one side empty), (1,3)=0.0 (one side empty), (2,3)=None
    # Mean over non-None pairs = 0.0
    assert block["mean_jaccard"] == 0.0


def test_invalid_key_rate_per_run():
    """Per-run: count constraints with missing or empty canonical_key,
    divide by total. E.g., 5 constraints, 1 empty → rate = 0.2."""
    run = _make_extraction([
        {"constraint": "c1", "canonical_key": "valid-one"},
        {"constraint": "c2", "canonical_key": "valid-two"},
        {"constraint": "c3", "canonical_key": "valid-three"},
        {"constraint": "c4", "canonical_key": "valid-four"},
        {"constraint": "c5", "canonical_key": ""},
    ])
    other = _make_extraction([{"constraint": "x", "canonical_key": "valid-x"}])
    drift = compute_extraction_drift([("a", run), ("b", other)])
    rates = drift["aggregate"]["invalid_key_rate_per_run"]
    assert rates[0] == 0.2
    assert rates[1] == 0.0


def test_invalid_key_rate_per_run_counts_missing_field():
    """A constraint missing the canonical_key key entirely counts as invalid."""
    run = _make_extraction([
        {"constraint": "c1", "canonical_key": "valid"},
        {"constraint": "c2"},  # no canonical_key key at all
    ])
    other = _make_extraction([{"constraint": "x", "canonical_key": "ok-here"}])
    drift = compute_extraction_drift([("a", run), ("b", other)])
    rates = drift["aggregate"]["invalid_key_rate_per_run"]
    assert rates[0] == 0.5


def test_invalid_key_rate_overall():
    """Overall: sum(invalid) / sum(total) across all runs."""
    run_a = _make_extraction([  # 4 total, 1 invalid
        {"constraint": "a1", "canonical_key": "valid-a-one"},
        {"constraint": "a2", "canonical_key": "valid-a-two"},
        {"constraint": "a3", "canonical_key": "valid-a-three"},
        {"constraint": "a4", "canonical_key": ""},
    ])
    run_b = _make_extraction([  # 2 total, 1 invalid
        {"constraint": "b1", "canonical_key": "valid-b-one"},
        {"constraint": "b2", "canonical_key": ""},
    ])
    drift = compute_extraction_drift([("a", run_a), ("b", run_b)])
    # invalid: 1 + 1 = 2; total: 4 + 2 = 6; rate = 2/6 ≈ 0.333
    assert drift["aggregate"]["invalid_key_rate_overall"] == round(2 / 6, 3)


def test_canonical_key_jaccard_both_empty_returns_none():
    """Both runs have all-empty canonical_keys (full-degenerate) → Jaccard is
    None, not 1.0. The invalid_key_rate metric captures this case; Jaccard
    shouldn't conflate "no data" with "perfect agreement"."""
    run_a = _make_extraction([
        {"constraint": "A1", "canonical_key": ""},
        {"constraint": "A2", "canonical_key": ""},
    ])
    run_b = _make_extraction([
        {"constraint": "B1", "canonical_key": ""},
        {"constraint": "B2", "canonical_key": ""},
    ])
    drift = compute_extraction_drift([("a", run_a), ("b", run_b)])
    pair = drift["pairs"][0]
    assert pair["live_constraints_canonical_key"]["jaccard"] is None


def test_canonical_key_jaccard_excludes_empty_from_both_sides():
    """Empty canonical_keys are filtered before set intersection — two empty
    strings on either side do NOT count as a trivial match.

    Run A: 3 valid keys {alpha-one, alpha-two, alpha-three}
    Run B: 1 valid key {alpha-one} + 2 empty → filtered set is just {alpha-one}
    Jaccard = |{alpha-one}| / |{alpha-one, alpha-two, alpha-three}| = 1/3 ≈ 0.333
    """
    run_a = _make_extraction([
        {"constraint": "A1", "canonical_key": "alpha-one"},
        {"constraint": "A2", "canonical_key": "alpha-two"},
        {"constraint": "A3", "canonical_key": "alpha-three"},
    ])
    run_b = _make_extraction([
        {"constraint": "B1", "canonical_key": "alpha-one"},
        {"constraint": "B2", "canonical_key": ""},
        {"constraint": "B3", "canonical_key": ""},
    ])
    drift = compute_extraction_drift([("a", run_a), ("b", run_b)])
    pair = drift["pairs"][0]
    assert pair["live_constraints_canonical_key"]["jaccard"] == round(1 / 3, 3)
