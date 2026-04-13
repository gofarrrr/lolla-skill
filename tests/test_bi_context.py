"""Tests for BI fact registry context building."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.run_pipeline import _build_fact_registry


EXTRACTION = {
    "extraction": {
        "decision_situation": "Whether to grant 15% equity to head engineer Marcus",
        "live_constraints": [
            {
                "constraint": "Marcus responsible for 40% of technical capability",
                "introduced_turn": 1,
                "status": "active",
                "weight": "structural",
            },
            {
                "constraint": "Potential exit in 3-5 years at 4-6x EBITDA",
                "introduced_turn": 4,
                "status": "active",
                "weight": "situational",
            },
        ],
        "dropped_threads": [
            {
                "thread": "Wife's concern about equity precedent",
                "raised_by": "user",
                "raised_turn": 3,
                "status": "acknowledged_then_dropped",
            },
        ],
    }
}


def test_fact_registry_contains_constraints():
    """Fact registry includes all live_constraints."""
    result = _build_fact_registry(EXTRACTION)
    assert "Marcus responsible for 40% of technical capability" in result
    assert "Potential exit in 3-5 years" in result
    assert "structural" in result
    assert "situational" in result


def test_fact_registry_contains_dropped_threads():
    """Fact registry includes dropped_threads with status."""
    result = _build_fact_registry(EXTRACTION)
    assert "DROPPED" in result
    assert "Wife's concern about equity precedent" in result
    assert "acknowledged_then_dropped" in result


def test_fact_registry_contains_decision_situation():
    """Fact registry opens with decision_situation."""
    result = _build_fact_registry(EXTRACTION)
    lines = result.split("\n")
    assert lines[0].startswith("Decision:")
    assert "15% equity" in lines[0]


def test_fact_registry_handles_missing_keys():
    """Fact registry returns empty string when extraction has no relevant keys."""
    assert _build_fact_registry({}) == ""
    assert _build_fact_registry({"extraction": {}}) == ""


def test_fact_registry_compact_size():
    """Fact registry is well under 4000 chars for typical extraction."""
    result = _build_fact_registry(EXTRACTION)
    assert len(result) < 1000  # much more compact than raw conversation
