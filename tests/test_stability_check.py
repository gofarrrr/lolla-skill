"""Tests for Mode C drift harness extensions (canonical_key Jaccard +
invalid_key_rate + cross-capture aggregation).

TDD red-green scaffolding for PR #1 of the extraction contract roadmap.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from stability_check import compute_extraction_drift  # noqa: E402


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
