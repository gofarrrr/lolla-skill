"""Tests for Phase 3b LLM-backed assistant stance extraction.

The boundary client is always mocked here — no live LLM calls. These tests
verify prompt shape, parse + validation logic, substring-matching, relation-
vocabulary enforcement, and constructor integration via the injectable
`stance_extractor` hook.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.system_b.conversation_context import (
    ConversationContext,
    ExtractionPayload,
    Turn as ContextTurn,
)
from engine.system_b.ir import SpanProvenance, StanceEvent
from engine.system_b.ir_constructor import construct_conversation_ir
from engine.system_b.stance_extraction import (
    STANCE_EXTRACTION_SYSTEM_PROMPT,
    VALID_RELATIONS,
    _format_user_prompt,
    extract_stance_events,
)


class _FakeBoundary:
    """Returns a canned payload and records the prompts it was called with."""

    def __init__(self, payload: dict):
        self._payload = payload
        self.calls: list[tuple[str, str]] = []

    def run_json(self, system_prompt: str, user_prompt: str) -> dict:
        self.calls.append((system_prompt, user_prompt))
        return self._payload


def _ctx(
    user_text: str = "Should I take the offer?",
    assistant_text: str = "My honest read: take it because reputable VCs know best. Push back on the 7-day deadline.",
) -> ConversationContext:
    return ConversationContext(
        turns=(
            ContextTurn(turn_index=1, speaker="user", text=user_text),
            ContextTurn(turn_index=2, speaker="assistant", text=assistant_text),
        ),
        extraction=ExtractionPayload(
            decision_situation="User evaluates an offer.",
            live_constraints=(),
            synthesized_position="mixed",
            reasoning_passages=(),
            original_framing="Take the offer or push back?",
            dropped_threads=(),
        ),
    )


# ---------------------------------------------------------------------------
# Prompt shape
# ---------------------------------------------------------------------------


def test_system_prompt_names_the_six_relations_exactly() -> None:
    for relation in VALID_RELATIONS:
        assert relation in STANCE_EXTRACTION_SYSTEM_PROMPT


def test_system_prompt_requires_literal_substring_evidence() -> None:
    lowered = STANCE_EXTRACTION_SYSTEM_PROMPT.lower()
    assert "substring" in lowered
    assert "assistant" in lowered


def test_system_prompt_names_composite_relation_marker() -> None:
    assert "relation_ambiguity" in STANCE_EXTRACTION_SYSTEM_PROMPT


def test_user_prompt_has_context_and_source_sections() -> None:
    prompt = _format_user_prompt(_ctx())
    assert "CONTEXT" in prompt
    assert "SOURCE" in prompt


def test_user_prompt_includes_assistant_turns_in_source() -> None:
    prompt = _format_user_prompt(_ctx(assistant_text="Assistant says X."))
    assert "Assistant says X." in prompt
    assert "ASSISTANT:" in prompt


def test_user_prompt_excludes_assistant_quotes_from_context_section() -> None:
    """User turns appear in CONTEXT; assistant turns appear only in SOURCE."""
    prompt = _format_user_prompt(
        _ctx(user_text="What should I do?", assistant_text="Take the offer."),
    )
    source_pos = prompt.find("SOURCE (")
    context_section = prompt[:source_pos]
    # Assistant text must NOT appear in the CONTEXT section
    assert "Take the offer." not in context_section


# ---------------------------------------------------------------------------
# Happy-path extraction
# ---------------------------------------------------------------------------


def test_extract_stance_events_parses_valid_output() -> None:
    ctx = _ctx(
        assistant_text="My honest read: take it. Push back on the 7-day deadline.",
    )
    boundary = _FakeBoundary({
        "stance_events": [
            {
                "text": "My honest read: take it.",
                "turn_index": 2,
                "relation": "commitment",
                "relation_ambiguity": False,
            },
            {
                "text": "Push back on the 7-day deadline.",
                "turn_index": 2,
                "relation": "revision",
                "relation_ambiguity": False,
            },
        ],
    })
    stances, stats = extract_stance_events(context=ctx, boundary=boundary)
    assert len(stances) == 2
    assert stats.validated_count == 2
    assert stats.raw_count == 2
    assert stats.dropped_not_substring == 0
    assert stances[0].stance == "commitment"
    assert stances[1].stance == "revision"
    assert all(s.speaker == "assistant" for s in stances)
    assert all(isinstance(s.provenance, SpanProvenance) for s in stances)


def test_extract_stance_events_computes_exact_span_positions() -> None:
    """SpanRef start/end must bracket the matched text within the assistant turn."""
    assistant = "Before the quote. Take the offer today. After the quote."
    ctx = _ctx(assistant_text=assistant)
    boundary = _FakeBoundary({
        "stance_events": [
            {
                "text": "Take the offer today.",
                "turn_index": 2,
                "relation": "commitment",
                "relation_ambiguity": False,
            },
        ],
    })
    stances, _ = extract_stance_events(context=ctx, boundary=boundary)
    assert len(stances) == 1
    ref = stances[0].provenance.span_ref
    assert assistant[ref.start_char:ref.end_char] == "Take the offer today."


def test_extract_stance_events_carries_relation_ambiguity_flag() -> None:
    ctx = _ctx(
        assistant_text="you don't call the police today. You call RAINN this afternoon.",
    )
    boundary = _FakeBoundary({
        "stance_events": [
            {
                "text": "you don't call the police today. You call RAINN this afternoon.",
                "turn_index": 2,
                "relation": "commitment",
                "relation_ambiguity": True,  # composite: commitment + deferral
            },
        ],
    })
    stances, _ = extract_stance_events(context=ctx, boundary=boundary)
    assert len(stances) == 1
    assert stances[0].relation_ambiguity is True
    assert stances[0].stance == "commitment"  # primary relation preserved


# ---------------------------------------------------------------------------
# Validation / drop behavior
# ---------------------------------------------------------------------------


def test_extract_drops_stance_whose_text_is_not_in_assistant_turn() -> None:
    """Paraphrase / hallucination / wrong-turn citation → dropped, counted."""
    ctx = _ctx(assistant_text="The real answer is: take it.")
    boundary = _FakeBoundary({
        "stance_events": [
            {
                "text": "This text is nowhere in the transcript",
                "turn_index": 2,
                "relation": "commitment",
                "relation_ambiguity": False,
            },
        ],
    })
    stances, stats = extract_stance_events(context=ctx, boundary=boundary)
    assert stances == []
    assert stats.dropped_not_substring == 1
    assert stats.validated_count == 0


def test_extract_drops_stance_with_invalid_relation() -> None:
    ctx = _ctx()
    boundary = _FakeBoundary({
        "stance_events": [
            {
                "text": "My honest read: take it.",
                "turn_index": 2,
                "relation": "not-a-real-relation",
                "relation_ambiguity": False,
            },
        ],
    })
    stances, stats = extract_stance_events(context=ctx, boundary=boundary)
    assert stances == []
    assert stats.dropped_invalid_relation == 1


def test_extract_drops_stance_with_invalid_turn_index() -> None:
    """turn_index pointing at a user turn or a non-existent index gets dropped."""
    ctx = _ctx()
    boundary = _FakeBoundary({
        "stance_events": [
            {
                "text": "Should I take the offer?",  # verbatim from user turn
                "turn_index": 1,  # user turn, not assistant
                "relation": "commitment",
                "relation_ambiguity": False,
            },
            {
                "text": "My honest read: take it.",
                "turn_index": 99,  # nonexistent
                "relation": "commitment",
                "relation_ambiguity": False,
            },
        ],
    })
    stances, stats = extract_stance_events(context=ctx, boundary=boundary)
    assert stances == []
    assert stats.dropped_invalid_turn == 2


def test_extract_tolerates_case_folding_on_first_character() -> None:
    """LLM lowercased 'You' → 'you'. find_substring_tolerant accepts this
    and the returned text uses the transcript's original casing."""
    assistant = "You should take the offer today."
    ctx = _ctx(assistant_text=assistant)
    boundary = _FakeBoundary({
        "stance_events": [
            {
                "text": "you should take the offer today.",  # lowercase y
                "turn_index": 2,
                "relation": "commitment",
                "relation_ambiguity": False,
            },
        ],
    })
    stances, stats = extract_stance_events(context=ctx, boundary=boundary)
    assert len(stances) == 1
    # Transcript's original uppercase-Y preserved in the StanceEvent text
    assert stances[0].text == "You should take the offer today."
    assert stats.validated_count == 1


def test_extract_returns_empty_on_no_stance_events() -> None:
    ctx = _ctx()
    boundary = _FakeBoundary({"stance_events": []})
    stances, stats = extract_stance_events(context=ctx, boundary=boundary)
    assert stances == []
    assert stats.raw_count == 0
    assert stats.validated_count == 0


# ---------------------------------------------------------------------------
# Constructor integration
# ---------------------------------------------------------------------------


def test_constructor_emits_zero_stance_events_when_no_extractor_injected() -> None:
    """Phase 1 behavior preserved: without a stance_extractor, StanceEvent
    count stays 0 (current extraction can't source them)."""
    ctx = _ctx()
    ir = construct_conversation_ir(ctx)
    assert len(ir.stance_events) == 0


def test_constructor_uses_injected_stance_extractor_when_provided() -> None:
    """Phase 3b behavior: when caller passes a stance_extractor callable,
    its output populates StanceEvents on the IR."""
    ctx = _ctx(
        assistant_text="Take the offer. Push back on the deadline.",
    )
    boundary = _FakeBoundary({
        "stance_events": [
            {
                "text": "Take the offer.",
                "turn_index": 2,
                "relation": "commitment",
                "relation_ambiguity": False,
            },
        ],
    })

    def stance_extractor(context: ConversationContext) -> list[StanceEvent]:
        stances, _ = extract_stance_events(context=context, boundary=boundary)
        return stances

    ir = construct_conversation_ir(ctx, stance_extractor=stance_extractor)
    assert len(ir.stance_events) == 1
    assert ir.stance_events[0].stance == "commitment"
    assert ir.stance_events[0].speaker == "assistant"


def test_constructor_continues_when_stance_extractor_raises() -> None:
    """Extractor exceptions must not break IR construction — the rest of
    the IR (turns, user_issue_events, frame_anchors) still populates
    correctly and stance_events just stays empty."""
    ctx = _ctx()

    def broken_extractor(context: ConversationContext) -> list[StanceEvent]:
        raise RuntimeError("boundary client failed")

    ir = construct_conversation_ir(ctx, stance_extractor=broken_extractor)
    assert len(ir.stance_events) == 0
    # Turns still populated — IR construction completed despite the extractor failure
    assert len(ir.turns) > 0
