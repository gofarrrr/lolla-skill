"""Tests for source-complete BI context building."""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.run_pipeline import _build_bi_context, _build_fact_registry


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


def test_fact_registry_does_not_repeat_global_dropped_threads_per_passage():
    """Dropped-thread coverage belongs to the main audit, not every BI call."""
    result = _build_fact_registry(EXTRACTION)
    assert "DROPPED" not in result
    assert "Wife's concern about equity precedent" not in result
    assert "acknowledged_then_dropped" not in result


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


def test_bi_context_preserves_all_available_user_facts_even_when_extraction_misses_them():
    user_turns = (
        "Marcus joined in year two and leads a 35-person engineering team.\n\n"
        "Tom left and the lost clients cost about $800K in revenue.\n\n"
        "The company deployment pipeline, component library, and estimation "
        "framework are central to delivery."
    )

    context, custody = _build_bi_context(
        extraction=EXTRACTION,
        user_context_text=user_turns,
        user_turn_count=3,
    )

    assert user_turns in context
    assert "joined in year two" in context
    assert "35-person engineering team" in context
    assert "$800K" in context
    assert "deployment pipeline" in context
    assert "Wife's concern about equity precedent" not in context
    assert custody["schema_version"] == "lolla.bullshit_index_context_custody.v1"
    assert (
        custody["source"]
        == "complete_available_user_turns_plus_provisional_extraction"
    )
    assert custody["complete_available_user_turns"] is True
    assert custody["user_turn_count"] == 3
    assert custody["user_context_char_count"] == len(user_turns)
    assert custody["user_context_sha256"] == hashlib.sha256(
        user_turns.encode("utf-8")
    ).hexdigest()
    assert custody["passage_context_char_count"] == len(context)
    assert custody["passage_context_sha256"] == hashlib.sha256(
        context.encode("utf-8")
    ).hexdigest()
    assert custody["dropped_threads_in_passage_context"] is False
