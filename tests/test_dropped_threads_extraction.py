"""Tests for Phase 5.5 LLM-backed dropped_threads specialist extraction.

Boundary is always mocked. Covers prompt shape, substring + speaker
validation, kind handling, deterministic ids, observability stats,
and constructor integration via the injectable hook.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.system_b.conversation_context import (
    ConversationContext,
    DroppedThread,
    ExtractionPayload,
    Turn as ContextTurn,
)
from engine.system_b.dropped_threads_extraction import (
    DROPPED_THREADS_SYSTEM_PROMPT,
    VALID_KINDS,
    VALID_SPEAKERS,
    _format_user_prompt,
    extract_dropped_threads,
)
from engine.system_b.ir import (
    SpanProvenance,
    TurnRefProvenance,
    UserIssueEvent,
)
from engine.system_b.ir_constructor import construct_conversation_ir


class _FakeBoundary:
    def __init__(self, payload: dict):
        self._payload = payload
        self.calls: list[tuple[str, str]] = []

    def run_json(self, system_prompt: str, user_prompt: str) -> dict:
        self.calls.append((system_prompt, user_prompt))
        return self._payload


def _ctx(
    *,
    turns: list[tuple[int, str, str]] | None = None,
    dropped_threads: tuple[DroppedThread, ...] = (),
) -> ConversationContext:
    if turns is None:
        turns = [
            (1, "user", "I asked about launch plan."),
            (1, "assistant", "Let me push back on fundamentals first."),
        ]
    return ConversationContext(
        turns=tuple(ContextTurn(turn_index=i, speaker=s, text=t) for (i, s, t) in turns),
        extraction=ExtractionPayload(
            decision_situation="Test situation.",
            live_constraints=(),
            synthesized_position="",
            reasoning_passages=(),
            original_framing="Test framing.",
            dropped_threads=dropped_threads,
        ),
    )


# ---------------------------------------------------------------------------
# Prompt shape
# ---------------------------------------------------------------------------


def test_valid_kinds_is_open_loop_and_concern() -> None:
    assert VALID_KINDS == ("open_loop", "concern")


def test_valid_speakers_is_user_and_assistant() -> None:
    assert VALID_SPEAKERS == ("user", "assistant")


def test_system_prompt_names_both_speakers() -> None:
    lowered = DROPPED_THREADS_SYSTEM_PROMPT.lower()
    assert "user" in lowered
    assert "assistant" in lowered


def test_system_prompt_names_both_kinds() -> None:
    for kind in VALID_KINDS:
        assert kind in DROPPED_THREADS_SYSTEM_PROMPT


def test_system_prompt_forbids_paraphrase_expansion() -> None:
    """Gate finding: monolith invented "$950K" and enumerations not in source.
    Prompt must explicitly forbid this."""
    lowered = DROPPED_THREADS_SYSTEM_PROMPT.lower()
    assert "expand" in lowered or "expansion" in lowered or "invent" in lowered


def test_system_prompt_requires_substring_evidence() -> None:
    assert "substring" in DROPPED_THREADS_SYSTEM_PROMPT.lower()


def test_user_prompt_source_section_includes_both_speakers() -> None:
    ctx = _ctx(turns=[
        (1, "user", "USER_UNIQ_XYZ"),
        (1, "assistant", "ASSIST_UNIQ_ABC"),
    ])
    prompt = _format_user_prompt(ctx)
    source_pos = prompt.find("SOURCE (")
    source_section = prompt[source_pos:]
    assert "USER_UNIQ_XYZ" in source_section
    assert "ASSIST_UNIQ_ABC" in source_section
    assert "USER" in source_section
    assert "ASSISTANT" in source_section


def test_user_prompt_has_context_section() -> None:
    prompt = _format_user_prompt(_ctx())
    assert "CONTEXT" in prompt


# ---------------------------------------------------------------------------
# Span-mode parse + validation
# ---------------------------------------------------------------------------


def test_extract_parses_valid_user_raised_thread() -> None:
    ctx = _ctx(turns=[
        (1, "user", "Can you help me think through the launch plan?"),
        (1, "assistant", "Let me push back first."),
    ])
    boundary = _FakeBoundary({
        "dropped_threads": [
            {
                "text": "Can you help me think through the launch plan?",
                "turn_index": 1,
                "speaker": "user",
                "kind": "open_loop",
                "kind_ambiguity": False,
                "superseded_by": "focus on fundamentals",
            }
        ]
    })
    events, stats = extract_dropped_threads(context=ctx, boundary=boundary)
    assert len(events) == 1
    event = events[0]
    assert event.kind == "open_loop"
    assert event.text == "Can you help me think through the launch plan?"
    assert isinstance(event.provenance, SpanProvenance)
    assert event.provenance.span_ref.speaker == "user"
    assert event.status == "acknowledged_then_dropped"
    assert event.superseded_by == "focus on fundamentals"
    assert stats.validated_count == 1
    assert stats.user_raised_count == 1
    assert stats.assistant_raised_count == 0


def test_extract_parses_valid_assistant_raised_thread() -> None:
    ctx = _ctx(turns=[
        (1, "user", "What about option 2?"),
        (1, "assistant", "The latter isn't viable, based on what you've described."),
    ])
    boundary = _FakeBoundary({
        "dropped_threads": [
            {
                "text": "The latter isn't viable, based on what you've described.",
                "turn_index": 1,
                "speaker": "assistant",
                "kind": "open_loop",
                "kind_ambiguity": False,
                "superseded_by": "collaborative version",
            }
        ]
    })
    events, stats = extract_dropped_threads(context=ctx, boundary=boundary)
    assert len(events) == 1
    assert events[0].provenance.span_ref.speaker == "assistant"
    assert stats.assistant_raised_count == 1
    assert stats.user_raised_count == 0


def test_extract_computes_exact_span_positions() -> None:
    user_text = "Before thread. She's going to be homeless. After thread."
    ctx = _ctx(turns=[(1, "user", user_text), (1, "assistant", "Assistant.")])
    boundary = _FakeBoundary({
        "dropped_threads": [
            {
                "text": "She's going to be homeless.",
                "turn_index": 1,
                "speaker": "user",
                "kind": "open_loop",
                "kind_ambiguity": True,
                "superseded_by": "partial help framing",
            }
        ]
    })
    events, _ = extract_dropped_threads(context=ctx, boundary=boundary)
    ref = events[0].provenance.span_ref
    assert user_text[ref.start_char:ref.end_char] == "She's going to be homeless."


def test_extract_drops_thread_with_invalid_kind() -> None:
    ctx = _ctx(turns=[(1, "user", "Real text.")])
    boundary = _FakeBoundary({
        "dropped_threads": [
            {
                "text": "Real text.",
                "turn_index": 1,
                "speaker": "user",
                "kind": "constraint",  # not a valid dropped_threads kind
                "kind_ambiguity": False,
            }
        ]
    })
    events, stats = extract_dropped_threads(context=ctx, boundary=boundary)
    assert events == []
    assert stats.dropped_invalid_kind == 1


def test_extract_drops_thread_with_invalid_speaker() -> None:
    ctx = _ctx(turns=[(1, "user", "Real text.")])
    boundary = _FakeBoundary({
        "dropped_threads": [
            {
                "text": "Real text.",
                "turn_index": 1,
                "speaker": "bogus_speaker",
                "kind": "open_loop",
                "kind_ambiguity": False,
            }
        ]
    })
    events, stats = extract_dropped_threads(context=ctx, boundary=boundary)
    assert events == []
    assert stats.dropped_invalid_speaker == 1


def test_extract_drops_non_substring_text() -> None:
    ctx = _ctx(turns=[(1, "user", "Actual user content.")])
    boundary = _FakeBoundary({
        "dropped_threads": [
            {
                "text": "This text is not in the turn",
                "turn_index": 1,
                "speaker": "user",
                "kind": "open_loop",
                "kind_ambiguity": False,
            }
        ]
    })
    events, stats = extract_dropped_threads(context=ctx, boundary=boundary)
    assert events == []
    assert stats.dropped_not_substring == 1


def test_extract_drops_thread_pointing_at_nonexistent_turn() -> None:
    ctx = _ctx(turns=[(1, "user", "Only turn 1.")])
    boundary = _FakeBoundary({
        "dropped_threads": [
            {
                "text": "Only turn 1.",
                "turn_index": 99,
                "speaker": "user",
                "kind": "open_loop",
                "kind_ambiguity": False,
            }
        ]
    })
    events, stats = extract_dropped_threads(context=ctx, boundary=boundary)
    assert events == []
    assert stats.dropped_invalid_turn == 1


def test_extract_distinguishes_speaker_mismatch_from_missing_turn() -> None:
    """Turn 1 exists for user but not assistant. If LLM claims
    speaker=assistant, turn_index=1, that's a SPEAKER MISMATCH
    (tracked separately from "turn does not exist at all")."""
    ctx = _ctx(turns=[
        (1, "user", "User content."),
        # deliberately NO assistant turn 1
    ])
    boundary = _FakeBoundary({
        "dropped_threads": [
            {
                "text": "User content.",
                "turn_index": 1,
                "speaker": "assistant",  # wrong speaker for turn 1
                "kind": "open_loop",
                "kind_ambiguity": False,
            }
        ]
    })
    events, stats = extract_dropped_threads(context=ctx, boundary=boundary)
    assert events == []
    assert stats.dropped_speaker_mismatch == 1
    assert stats.dropped_invalid_turn == 0


def test_extract_tolerates_case_folding() -> None:
    user_text = "Can you help me think through the launch plan?"
    ctx = _ctx(turns=[(1, "user", user_text), (1, "assistant", "Asst.")])
    boundary = _FakeBoundary({
        "dropped_threads": [
            {
                "text": "can you help me think through the launch plan?",  # lowercase c
                "turn_index": 1,
                "speaker": "user",
                "kind": "open_loop",
                "kind_ambiguity": False,
            }
        ]
    })
    events, _ = extract_dropped_threads(context=ctx, boundary=boundary)
    assert len(events) == 1
    assert events[0].text == user_text  # transcript casing preserved


def test_extract_carries_kind_ambiguity() -> None:
    ctx = _ctx(turns=[(1, "user", "She's going to be homeless."), (1, "assistant", "Asst.")])
    boundary = _FakeBoundary({
        "dropped_threads": [
            {
                "text": "She's going to be homeless.",
                "turn_index": 1,
                "speaker": "user",
                "kind": "open_loop",
                "kind_ambiguity": True,
            }
        ]
    })
    events, _ = extract_dropped_threads(context=ctx, boundary=boundary)
    assert events[0].kind_ambiguity is True


def test_extract_returns_empty_on_no_threads() -> None:
    ctx = _ctx()
    boundary = _FakeBoundary({"dropped_threads": []})
    events, stats = extract_dropped_threads(context=ctx, boundary=boundary)
    assert events == []
    assert stats.raw_count == 0


def test_extract_defaults_kind_to_open_loop_if_missing() -> None:
    """LLM sometimes omits the kind field — default is open_loop."""
    ctx = _ctx(turns=[(1, "user", "Real text here.")])
    boundary = _FakeBoundary({
        "dropped_threads": [
            {
                "text": "Real text here.",
                "turn_index": 1,
                "speaker": "user",
                # no kind field
            }
        ]
    })
    events, _ = extract_dropped_threads(context=ctx, boundary=boundary)
    assert len(events) == 1
    assert events[0].kind == "open_loop"


# ---------------------------------------------------------------------------
# Observability
# ---------------------------------------------------------------------------


def test_stats_tracks_per_drop_counters() -> None:
    ctx = _ctx(turns=[(1, "user", "Real text.")])
    boundary = _FakeBoundary({
        "dropped_threads": [
            {"text": "Real text.", "turn_index": 1, "speaker": "user", "kind": "open_loop"},
            {"text": "Real text.", "turn_index": 99, "speaker": "user", "kind": "open_loop"},
            {"text": "Bogus", "turn_index": 1, "speaker": "bogus", "kind": "open_loop"},
            {"text": "Real text.", "turn_index": 1, "speaker": "user", "kind": "not-a-kind"},
            {"text": "Not a substring", "turn_index": 1, "speaker": "user", "kind": "open_loop"},
        ]
    })
    events, stats = extract_dropped_threads(context=ctx, boundary=boundary)
    assert len(events) == 1
    assert stats.raw_count == 5
    assert stats.dropped_invalid_turn == 1
    assert stats.dropped_invalid_speaker == 1
    assert stats.dropped_invalid_kind == 1
    assert stats.dropped_not_substring == 1


def test_issue_id_is_deterministic() -> None:
    ctx = _ctx(turns=[(1, "user", "Some thread text here.")])
    payload = {
        "dropped_threads": [
            {
                "text": "Some thread text here.",
                "turn_index": 1,
                "speaker": "user",
                "kind": "open_loop",
            }
        ]
    }
    e1, _ = extract_dropped_threads(context=ctx, boundary=_FakeBoundary(payload))
    e2, _ = extract_dropped_threads(context=ctx, boundary=_FakeBoundary(payload))
    assert e1[0].issue_id == e2[0].issue_id
    assert e1[0].issue_id.startswith("dropped_thread_t1_user_")


def test_completion_log_fires(caplog) -> None:
    ctx = _ctx(turns=[(1, "user", "Text.")])
    boundary = _FakeBoundary({
        "dropped_threads": [
            {"text": "Text.", "turn_index": 1, "speaker": "user", "kind": "open_loop"}
        ]
    })
    with caplog.at_level(logging.INFO, logger="system_b.dropped_threads_extraction"):
        extract_dropped_threads(context=ctx, boundary=boundary)
    assert any("dropped_threads_extraction.completed" in r.getMessage() for r in caplog.records)


# ---------------------------------------------------------------------------
# Constructor integration
# ---------------------------------------------------------------------------


def test_constructor_default_uses_monolith_dropped_threads_mapping() -> None:
    ctx = ConversationContext(
        turns=(
            ContextTurn(turn_index=1, speaker="user", text="User."),
            ContextTurn(turn_index=1, speaker="assistant", text="Assistant."),
        ),
        extraction=ExtractionPayload(
            decision_situation="S",
            live_constraints=(),
            synthesized_position="",
            reasoning_passages=(),
            original_framing="F",
            dropped_threads=(
                DroppedThread(
                    thread="monolith-paraphrase thread",
                    raised_by="user",
                    raised_turn=1,
                    status="acknowledged_then_dropped",
                    superseded_by="later focus",
                ),
            ),
        ),
    )
    ir = construct_conversation_ir(ctx)
    dropped = [e for e in ir.user_issue_events if e.kind == "open_loop"]
    assert len(dropped) == 1
    assert dropped[0].text == "monolith-paraphrase thread"
    assert isinstance(dropped[0].provenance, TurnRefProvenance)


def test_constructor_uses_injected_dropped_threads_extractor() -> None:
    ctx = ConversationContext(
        turns=(
            ContextTurn(turn_index=1, speaker="user", text="Can you help me think through the launch plan?"),
            ContextTurn(turn_index=1, speaker="assistant", text="Push back on fundamentals."),
        ),
        extraction=ExtractionPayload(
            decision_situation="S",
            live_constraints=(),
            synthesized_position="",
            reasoning_passages=(),
            original_framing="F",
            dropped_threads=(
                DroppedThread(
                    thread="paraphrase the specialist should replace",
                    raised_by="user",
                    raised_turn=1,
                    status="acknowledged_then_dropped",
                    superseded_by="focus on fundamentals",
                ),
            ),
        ),
    )

    boundary = _FakeBoundary({
        "dropped_threads": [
            {
                "text": "Can you help me think through the launch plan?",
                "turn_index": 1,
                "speaker": "user",
                "kind": "open_loop",
                "kind_ambiguity": False,
                "superseded_by": "fundamentals first",
            }
        ]
    })

    def specialist(context: ConversationContext) -> list[UserIssueEvent]:
        events, _ = extract_dropped_threads(context=context, boundary=boundary)
        return events

    ir = construct_conversation_ir(ctx, dropped_threads_extractor=specialist)
    dropped = [e for e in ir.user_issue_events if e.kind == "open_loop"]
    assert len(dropped) == 1
    # specialist's span-backed event, NOT the monolith's paraphrase
    assert dropped[0].text == "Can you help me think through the launch plan?"
    assert isinstance(dropped[0].provenance, SpanProvenance)


def test_constructor_survives_dropped_threads_extractor_raising() -> None:
    ctx = ConversationContext(
        turns=(
            ContextTurn(turn_index=1, speaker="user", text="User."),
            ContextTurn(turn_index=1, speaker="assistant", text="Assistant."),
        ),
        extraction=ExtractionPayload(
            decision_situation="S",
            live_constraints=(),
            synthesized_position="",
            reasoning_passages=(),
            original_framing="F",
            dropped_threads=(),
        ),
    )

    def broken(context: ConversationContext) -> list[UserIssueEvent]:
        raise RuntimeError("boundary failed")

    ir = construct_conversation_ir(ctx, dropped_threads_extractor=broken)
    assert [e for e in ir.user_issue_events if e.kind == "open_loop"] == []
    assert len(ir.turns) == 2
