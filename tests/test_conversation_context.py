"""Tests for the Phase 1 ConversationContext dataclass shape."""

from __future__ import annotations

import dataclasses

import pytest

from engine.system_b.conversation_context import (
    ConversationContext,
    DroppedThread,
    ExtractionPayload,
    LiveConstraint,
    Turn,
)


# ---------- Turn ----------


def test_turn_user_minimal() -> None:
    turn = Turn(turn_index=1, speaker="user", text="hello")
    assert turn.speaker == "user"
    assert turn.text == "hello"
    assert turn.turn_index == 1


def test_turn_assistant_minimal() -> None:
    turn = Turn(turn_index=2, speaker="assistant", text="reply")
    assert turn.speaker == "assistant"


def test_turn_invalid_speaker_raises() -> None:
    with pytest.raises(ValueError, match="speaker must be one of"):
        Turn(turn_index=1, speaker="system", text="x")


def test_turn_zero_index_raises() -> None:
    with pytest.raises(ValueError, match="turn_index must be >= 1"):
        Turn(turn_index=0, speaker="user", text="x")


def test_turn_is_frozen() -> None:
    turn = Turn(turn_index=1, speaker="user", text="hi")
    with pytest.raises(dataclasses.FrozenInstanceError):
        turn.text = "hacked"  # type: ignore[misc]


# ---------- LiveConstraint ----------


def test_live_constraint_minimal_without_canonical_key() -> None:
    c = LiveConstraint(
        constraint="price capped at 100k",
        introduced_turn=3,
        status="active",
        weight="structural",
    )
    assert c.canonical_key is None


def test_live_constraint_with_canonical_key_passthrough() -> None:
    c = LiveConstraint(
        constraint="price capped at 100k",
        introduced_turn=3,
        status="active",
        weight="structural",
        canonical_key="price-cap",
    )
    assert c.canonical_key == "price-cap"


# ---------- DroppedThread ----------


def test_dropped_thread_without_superseded_by() -> None:
    t = DroppedThread(
        thread="user raised timeline concern",
        raised_by="user",
        raised_turn=4,
        status="acknowledged_then_dropped",
    )
    assert t.superseded_by is None


def test_dropped_thread_with_superseded_by() -> None:
    t = DroppedThread(
        thread="profit-sharing alternative",
        raised_by="user",
        raised_turn=3,
        status="acknowledged_then_dropped",
        superseded_by="full equity partnership",
    )
    assert t.superseded_by == "full equity partnership"


# ---------- ExtractionPayload ----------


def test_extraction_payload_empty_collections() -> None:
    payload = ExtractionPayload(
        decision_situation="",
        live_constraints=(),
        synthesized_position="",
        reasoning_passages=(),
        original_framing="",
        dropped_threads=(),
    )
    assert payload.quote_validation == {}
    assert payload.live_constraints == ()


def test_extraction_payload_fully_populated() -> None:
    payload = ExtractionPayload(
        decision_situation="Whether to accept offer",
        live_constraints=(
            LiveConstraint(
                constraint="salary 3x", introduced_turn=1, status="active", weight="structural"
            ),
        ),
        synthesized_position="Take the offer with conditions",
        reasoning_passages=("quote one", "quote two"),
        original_framing="Should I take this?",
        dropped_threads=(
            DroppedThread(
                thread="mentorship continuity",
                raised_by="user",
                raised_turn=2,
                status="acknowledged_then_dropped",
            ),
        ),
        quote_validation={"retry_attempted": True, "fabricated": 0},
    )
    assert len(payload.live_constraints) == 1
    assert payload.quote_validation["fabricated"] == 0


# ---------- ConversationContext ----------


def _minimal_payload() -> ExtractionPayload:
    return ExtractionPayload(
        decision_situation="",
        live_constraints=(),
        synthesized_position="",
        reasoning_passages=(),
        original_framing="",
        dropped_threads=(),
    )


def test_conversation_context_minimal() -> None:
    ctx = ConversationContext(
        turns=(Turn(turn_index=1, speaker="user", text="hi"),),
        extraction=_minimal_payload(),
    )
    assert len(ctx.turns) == 1
    assert ctx.capture_health == "unknown"
    assert ctx.capture_warnings == ()
    assert ctx.capture_manifest == {}


def test_conversation_context_multi_turn_full_metadata() -> None:
    ctx = ConversationContext(
        turns=(
            Turn(turn_index=1, speaker="user", text="question"),
            Turn(turn_index=1, speaker="assistant", text="answer"),
            Turn(turn_index=2, speaker="user", text="follow-up"),
        ),
        extraction=_minimal_payload(),
        capture_manifest={"declared_turns": 2, "actual_user_turns": 2},
        capture_health="good",
        capture_warnings=("minor skew",),
    )
    assert len(ctx.turns) == 3
    assert ctx.capture_health == "good"
    assert ctx.capture_warnings == ("minor skew",)


def test_conversation_context_is_frozen() -> None:
    ctx = ConversationContext(
        turns=(Turn(turn_index=1, speaker="user", text="hi"),),
        extraction=_minimal_payload(),
    )
    with pytest.raises(dataclasses.FrozenInstanceError):
        ctx.capture_health = "critical"  # type: ignore[misc]


def test_conversation_context_asdict_roundtrip_preserves_shape() -> None:
    ctx = ConversationContext(
        turns=(
            Turn(turn_index=1, speaker="user", text="hello"),
            Turn(turn_index=1, speaker="assistant", text="world"),
        ),
        extraction=ExtractionPayload(
            decision_situation="test",
            live_constraints=(
                LiveConstraint(
                    constraint="budget cap",
                    introduced_turn=1,
                    status="active",
                    weight="structural",
                    canonical_key="budget",
                ),
            ),
            synthesized_position="proceed",
            reasoning_passages=("quote",),
            original_framing="go or no go",
            dropped_threads=(),
            quote_validation={"retry_attempted": False},
        ),
        capture_manifest={"declared_turns": 1},
        capture_health="good",
        capture_warnings=(),
    )

    as_dict = dataclasses.asdict(ctx)
    assert as_dict["capture_health"] == "good"
    assert as_dict["turns"][0]["speaker"] == "user"
    assert as_dict["extraction"]["live_constraints"][0]["canonical_key"] == "budget"
    assert as_dict["extraction"]["quote_validation"]["retry_attempted"] is False
