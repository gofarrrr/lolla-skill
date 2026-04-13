"""Tests for fuzzy quote matching fallback in fingerprint validation."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.system_b.companion import FingerprintMove
from engine.system_b.companion_routing import validate_fingerprint_moves


ANSWER = (
    "The equity split should reflect both historical contributions and future expectations. "
    "Marcus has invested significant time building the prototype over the past year, "
    "while the new partner brings critical sales expertise and industry connections."
)


def _move(quote: str, move_id: str = "m1") -> FingerprintMove:
    return FingerprintMove(
        move_id=move_id,
        reasoning_move="anchoring",
        evidence_quotes=[quote],
        evidence_rationale="test",
        confidence="high",
    )


def test_exact_substring_validated():
    """Baseline: exact substring match passes validation."""
    move = _move("Marcus has invested significant time building the prototype")
    validated, dropped = validate_fingerprint_moves([move], ANSWER)
    assert len(validated) == 1
    assert len(dropped) == 0


def test_fuzzy_paraphrase_validated():
    """Minor paraphrase with >=80% token overlap passes via fuzzy matching."""
    # Same tokens, slightly reordered — not a literal substring
    move = _move("Marcus has invested significant time over the past year building the prototype")
    validated, dropped = validate_fingerprint_moves([move], ANSWER)
    assert len(validated) == 1
    assert len(dropped) == 0


def test_genuinely_fabricated_still_dropped():
    """A quote with <80% token overlap is still dropped as fabricated."""
    move = _move("The company should pursue aggressive international expansion immediately")
    validated, dropped = validate_fingerprint_moves([move], ANSWER)
    assert len(validated) == 0
    assert len(dropped) == 1
    assert dropped[0]["drop_reason"] == "fabricated_quote"


def test_fuzzy_edge_empty_quote():
    """Empty quote returns False from fuzzy matching."""
    from engine.system_b.companion_routing import _fuzzy_quote_in_answer
    assert _fuzzy_quote_in_answer("", ANSWER) is False


def test_fuzzy_edge_empty_answer():
    """Empty answer returns False from fuzzy matching."""
    from engine.system_b.companion_routing import _fuzzy_quote_in_answer
    assert _fuzzy_quote_in_answer("some quote text here", "") is False


def test_fuzzy_edge_short_quote():
    """Single-word or two-word quote returns False (too short to fuzzy match)."""
    from engine.system_b.companion_routing import _fuzzy_quote_in_answer
    assert _fuzzy_quote_in_answer("equity", ANSWER) is False
    assert _fuzzy_quote_in_answer("equity split", ANSWER) is False
