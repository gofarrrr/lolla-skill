"""Tests for the Phase 1 provenance-bearing Conversation IR."""

from __future__ import annotations

import pytest

from engine.system_b.ir import ConversationIR, SpanProvenance, SpanRef, Turn


def test_span_ref_resolves_exact_turn_relative_text() -> None:
    """Span provenance resolves against semantic turn text, not raw file bytes."""

    turn = Turn(
        turn_index=2,
        speaker="user",
        text="I decided to quit, but I still need spouse alignment.",
    )
    ir = ConversationIR(turns=(turn,))
    start = turn.text.index("spouse")
    span = SpanRef(
        turn_index=2,
        speaker="user",
        start_char=start,
        end_char=start + len("spouse alignment"),
    )

    assert ir.resolve_span(span) == "spouse alignment"


def test_span_ref_rejects_offsets_outside_the_turn_text() -> None:
    turn = Turn(turn_index=1, speaker="user", text="short")
    ir = ConversationIR(turns=(turn,))

    with pytest.raises(ValueError, match="outside turn text"):
        ir.resolve_span(
            SpanRef(
                turn_index=1,
                speaker="user",
                start_char=0,
                end_char=99,
            )
        )


def test_span_provenance_serializes_with_exact_span_ref() -> None:
    provenance = SpanProvenance(
        span_ref=SpanRef(
            turn_index=1,
            speaker="user",
            start_char=3,
            end_char=12,
        )
    )

    assert provenance.to_dict() == {
        "kind": "span",
        "span_ref": {
            "turn_index": 1,
            "speaker": "user",
            "start_char": 3,
            "end_char": 12,
        },
    }
