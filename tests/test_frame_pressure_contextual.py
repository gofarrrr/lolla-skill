"""Tests for the Phase 2a conversation-first Lane 3 entry points.

Covers:
- `run_frame_extraction_from_context` — builds the user prompt from a
  ConversationContext, validates evidence against user turns (not the
  collapsed query), returns the same FramePressureCard shape as the legacy
  entry point.
- `generate_reframings_from_context` — reuses the existing reframe system
  prompt but grounds reframings in the actual first user turn.

Boundary calls are mocked; no real LLM work.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.system_b.conversation_context import (
    ConversationContext,
    DroppedThread,
    ExtractionPayload,
    LiveConstraint,
    Turn,
)
from engine.system_b.frame_pressure import (
    ExtractedFrameElement,
    FrameRoute,
    _FRAME_EXTRACTION_SYSTEM_FROM_CONTEXT,
    _format_frame_extraction_from_context_user_prompt,
    _format_reframe_generation_from_context_prompt,
    _joined_user_turns_text,
    generate_reframings_from_context,
    run_frame_extraction_from_context,
)


def _minimal_payload() -> ExtractionPayload:
    return ExtractionPayload(
        decision_situation="Whether to take the offer",
        live_constraints=(
            LiveConstraint(
                constraint="timeline is 10 days",
                introduced_turn=1,
                status="active",
                weight="situational",
            ),
        ),
        synthesized_position="",
        reasoning_passages=(),
        original_framing="Is this obvious or crazy?",
        dropped_threads=(
            DroppedThread(
                thread="partner's reaction",
                raised_by="user",
                raised_turn=2,
                status="acknowledged_then_dropped",
                superseded_by=None,
            ),
        ),
    )


def _ctx(turns: tuple[tuple[int, str, str], ...]) -> ConversationContext:
    return ConversationContext(
        turns=tuple(Turn(turn_index=i, speaker=s, text=t) for (i, s, t) in turns),
        extraction=_minimal_payload(),
    )


def _boundary_returning(payload: dict) -> MagicMock:
    boundary = MagicMock()
    boundary.run_json = MagicMock(return_value=payload)
    return boundary


# ---------- run_frame_extraction_from_context ----------


def test_run_frame_extraction_from_context_basic() -> None:
    ctx = _ctx((
        (1, "user", "I need to decide whether to take this job. It's 3x my salary but feels crazy."),
        (1, "assistant", "Let's unpack that."),
    ))
    boundary = _boundary_returning({
        "frame_elements": [
            {
                "element_text": "assumes the decision is binary (take or decline)",
                "element_type": "assumption",
                "evidence_quote": "whether to take this job",
                "frame_pattern": "binary_collapse",
                "fragility_signal": "alternative arrangements not considered",
                "inquiry_stage": "why",
                "likely_default": "inertia",
            }
        ]
    })
    card = run_frame_extraction_from_context(boundary, ctx)
    assert len(card.frame_elements) == 1
    assert card.frame_elements[0].frame_pattern == "binary_collapse"
    assert card.dropped_frame_elements == ()


def test_run_frame_extraction_from_context_rejects_evidence_not_in_user_turns() -> None:
    ctx = _ctx((
        (1, "user", "What's the right move here?"),
        (1, "assistant", "Consider the opportunity cost carefully."),
    ))
    boundary = _boundary_returning({
        "frame_elements": [
            {
                "element_text": "assumes opportunity cost frames the decision",
                "element_type": "assumption",
                # Evidence is only in the assistant turn — must be rejected
                "evidence_quote": "opportunity cost",
                "frame_pattern": "scope_lock",
                "fragility_signal": "",
                "inquiry_stage": "why",
                "likely_default": "none",
            }
        ]
    })
    card = run_frame_extraction_from_context(boundary, ctx)
    assert card.frame_elements == ()
    assert len(card.dropped_frame_elements) == 1
    assert card.dropped_frame_elements[0]["drop_reason"] == "evidence_not_in_user_turns"


def test_run_frame_extraction_from_context_accepts_evidence_from_any_user_turn() -> None:
    """Evidence can come from a later user turn, not just the first."""
    ctx = _ctx((
        (1, "user", "I'm thinking about a career move."),
        (1, "assistant", "Tell me more."),
        (2, "user", "The thing is, I'm assuming I have to decide this week. Maybe I don't."),
    ))
    boundary = _boundary_returning({
        "frame_elements": [
            {
                "element_text": "time pressure assumption",
                "element_type": "mutable_constraint",
                "evidence_quote": "I have to decide this week",  # turn 2 text
                "frame_pattern": "temporal_fixation",
                "fragility_signal": "deadline may be self-imposed",
                "inquiry_stage": "what_if",
                "likely_default": "inertia",
            }
        ]
    })
    card = run_frame_extraction_from_context(boundary, ctx)
    assert len(card.frame_elements) == 1
    assert card.frame_elements[0].frame_pattern == "temporal_fixation"


def test_run_frame_extraction_from_context_handles_empty_turns() -> None:
    """A context with zero turns still returns a valid (empty) card.

    All evidence fails the literal-substring check against empty user text,
    so every element is dropped.
    """
    ctx = ConversationContext(
        turns=(),
        extraction=_minimal_payload(),
    )
    boundary = _boundary_returning({
        "frame_elements": [
            {
                "element_text": "some element",
                "element_type": "assumption",
                "evidence_quote": "anything",
                "frame_pattern": "scope_lock",
                "fragility_signal": "",
                "inquiry_stage": "why",
                "likely_default": "none",
            }
        ]
    })
    card = run_frame_extraction_from_context(boundary, ctx)
    assert card.frame_elements == ()
    assert card.dropped_frame_elements[0]["drop_reason"] == "evidence_not_in_user_turns"


def test_run_frame_extraction_from_context_drops_missing_evidence_and_pattern() -> None:
    ctx = _ctx(((1, "user", "hello world"), (1, "assistant", "hi")))
    boundary = _boundary_returning({
        "frame_elements": [
            {"element_text": "a", "evidence_quote": "", "frame_pattern": "x"},
            {"element_text": "b", "evidence_quote": "hello", "frame_pattern": ""},
        ]
    })
    card = run_frame_extraction_from_context(boundary, ctx)
    assert card.frame_elements == ()
    reasons = [d["drop_reason"] for d in card.dropped_frame_elements]
    assert "missing_evidence" in reasons
    assert "missing_pattern" in reasons


def test_run_frame_extraction_from_context_calls_boundary_with_context_system_prompt() -> None:
    ctx = _ctx(((1, "user", "q"), (1, "assistant", "a")))
    boundary = _boundary_returning({"frame_elements": []})
    run_frame_extraction_from_context(boundary, ctx)
    args, _ = boundary.run_json.call_args
    system_prompt, user_prompt = args
    assert system_prompt is _FRAME_EXTRACTION_SYSTEM_FROM_CONTEXT
    # User prompt must have two labelled sections: CONTEXT (not quotable) +
    # SOURCE (evidence must come from here)
    assert "CONTEXT (background for understanding" in user_prompt
    assert "SOURCE (evidence_quote MUST be a literal substring" in user_prompt
    # User turns appear in the SOURCE section
    assert "[Turn 1] USER:" in user_prompt
    # Assistant turns appear in CONTEXT with a non-quotable marker
    assert "[Turn 1 ASSISTANT]" in user_prompt


# ---------- prompt formatting helpers ----------


def test_format_user_prompt_includes_extracted_structure_in_context_section() -> None:
    ctx = _ctx((
        (1, "user", "first question"),
        (1, "assistant", "first reply"),
        (2, "user", "follow-up"),
    ))
    prompt = _format_frame_extraction_from_context_user_prompt(ctx)
    # Extracted structure lives in the CONTEXT section (not quotable)
    ctx_section_end = prompt.index("SOURCE")
    context_section = prompt[:ctx_section_end]
    assert "CONTEXT (background for understanding" in context_section
    assert "Decision situation: Whether to take the offer" in context_section
    assert "Framing extracted upstream: Is this obvious or crazy?" in context_section
    assert "Constraints:" in context_section
    assert "[ACTIVE] timeline is 10 days (turn 1)" in context_section
    assert "Dropped threads:" in context_section
    assert "partner's reaction" in context_section


def test_format_user_prompt_places_user_turns_in_source_and_assistant_turns_in_context() -> None:
    ctx = _ctx((
        (1, "user", "first question"),
        (1, "assistant", "first reply"),
        (2, "user", "follow-up"),
    ))
    prompt = _format_frame_extraction_from_context_user_prompt(ctx)
    # SOURCE section contains user-turn bodies; assistant-turn bodies appear
    # in the CONTEXT half only (marked non-quotable).
    context_section, source_section = prompt.split("SOURCE", 1)
    assert "first question" in source_section
    assert "follow-up" in source_section
    # Assistant reply is NOT in SOURCE (would bypass the quotability rule)
    assert "first reply" not in source_section
    # It IS in CONTEXT, marked non-quotable
    assert "first reply" in context_section
    assert "[Turn 1 ASSISTANT]" in context_section


def test_format_user_prompt_omits_empty_context_sections() -> None:
    """If live_constraints + dropped_threads are empty, don't render dangling labels."""
    empty_ext = ExtractionPayload(
        decision_situation="D",
        live_constraints=(),
        synthesized_position="",
        reasoning_passages=(),
        original_framing="",
        dropped_threads=(),
    )
    ctx = ConversationContext(
        turns=(Turn(turn_index=1, speaker="user", text="q"),),
        extraction=empty_ext,
    )
    prompt = _format_frame_extraction_from_context_user_prompt(ctx)
    assert "- Constraints:" not in prompt
    assert "- Dropped threads:" not in prompt
    assert "Framing extracted upstream:" not in prompt


def test_system_prompt_explicitly_forbids_quoting_from_context() -> None:
    """Confirm the system prompt tells the LLM not to quote from CONTEXT.

    This is the anti-regression for Phase 2a's first measurement run, which
    showed drops when the LLM quoted from the extracted-structure section.
    """
    prompt = _FRAME_EXTRACTION_SYSTEM_FROM_CONTEXT
    assert "DO NOT quote from CONTEXT" in prompt
    assert "ONLY section from which evidence_quote may be drawn" in prompt
    # Includes at least one right-vs-wrong worked example
    assert "RIGHT:" in prompt
    assert "WRONG:" in prompt


def test_joined_user_turns_text_includes_user_only() -> None:
    ctx = _ctx((
        (1, "user", "hello"),
        (1, "assistant", "world"),
        (2, "user", "again"),
    ))
    joined = _joined_user_turns_text(ctx)
    assert "hello" in joined
    assert "again" in joined
    assert "world" not in joined


# ---------- generate_reframings_from_context ----------


def test_generate_reframings_from_context_basic() -> None:
    ctx = _ctx((
        (1, "user", "Should I take this role? It's 3x my salary and I have 10 days."),
        (1, "assistant", "Let's think about it."),
    ))
    element = ExtractedFrameElement(
        element_text="time pressure assumed",
        element_type="mutable_constraint",
        evidence_quote="10 days",
        frame_pattern="temporal_fixation",
        fragility_signal="deadline may be self-imposed",
        inquiry_stage="what_if",
        likely_default="inertia",
    )
    route = FrameRoute(
        element_index=0,
        frame_pattern="temporal_fixation",
        candidate_model_ids=("deadline-inversion",),
        excluded_model_ids=(),
    )
    boundary = _boundary_returning({
        "reframings": [
            {
                "reframed_question": "What would change if the deadline were one month instead of ten days?",
                "what_opens": "lets you evaluate the role without the artificial urgency of the recruiter's timeline.",
                "reframe_move_type": "constraint_relaxation",
                "grounding_model": "deadline-inversion",
                "source_element_index": 0,
            }
        ]
    })
    reframings = generate_reframings_from_context(
        boundary=boundary,
        context=ctx,
        elements=(element,),
        routes=(route,),
    )
    assert len(reframings) == 1
    assert reframings[0].reframe_move_type == "constraint_relaxation"


def test_format_reframe_from_context_prompt_grounds_in_first_user_turn() -> None:
    ctx = _ctx((
        (1, "user", "I want to know if I should take this."),
        (1, "assistant", "Tell me more."),
        (2, "user", "additional context"),
    ))
    element = ExtractedFrameElement(
        element_text="x",
        element_type="assumption",
        evidence_quote="take this",
        frame_pattern="binary_collapse",
        fragility_signal="",
        inquiry_stage="why",
        likely_default="none",
    )
    route = FrameRoute(
        element_index=0,
        frame_pattern="binary_collapse",
        candidate_model_ids=("inversion",),
        excluded_model_ids=(),
    )
    prompt = _format_reframe_generation_from_context_prompt(ctx, (element,), (route,))
    # First user turn appears as the canonical framing, NOT the second
    assert "I want to know if I should take this." in prompt
    assert "USER'S FRAMING (first user turn" in prompt
    # Element data present
    assert "ELEMENT 0" in prompt
    assert "pattern: binary_collapse" in prompt


def test_format_reframe_from_context_prompt_handles_context_without_user_turns() -> None:
    """Defensive: should not crash when no user turns exist."""
    ctx = ConversationContext(
        turns=(Turn(turn_index=1, speaker="assistant", text="reply only"),),
        extraction=_minimal_payload(),
    )
    prompt = _format_reframe_generation_from_context_prompt(ctx, (), ())
    assert "USER'S FRAMING" in prompt  # header still rendered
