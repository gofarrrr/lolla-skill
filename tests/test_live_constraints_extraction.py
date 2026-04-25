"""Tests for Phase 5 LLM-backed live_constraints specialist extraction.

Boundary client is always mocked — no live LLM calls. These tests verify
prompt shape, parse/validation for span and derivation modes, single-turn
derivation downgrade, constructor integration via the injectable
`live_constraints_extractor` hook, and resilience on extractor exceptions.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.system_b.conversation_context import (
    ConversationContext,
    ExtractionPayload,
    Turn as ContextTurn,
)
from engine.system_b.ir import (
    DerivationProvenance,
    SpanProvenance,
    TurnRefProvenance,
    UserIssueEvent,
)
from engine.system_b.ir_constructor import construct_conversation_ir
from engine.system_b.live_constraints_extraction import (
    LIVE_CONSTRAINTS_SYSTEM_PROMPT,
    VALID_KINDS,
    _format_user_prompt,
    extract_live_constraints,
)


class _FakeBoundary:
    """Returns a canned payload and records prompts it was called with."""

    def __init__(self, payload: dict):
        self._payload = payload
        self.calls: list[tuple[str, str]] = []

    def run_json(self, system_prompt: str, user_prompt: str) -> dict:
        self.calls.append((system_prompt, user_prompt))
        return self._payload


def _ctx(
    *,
    turns: list[tuple[int, str, str]] | None = None,
    extraction: ExtractionPayload | None = None,
) -> ConversationContext:
    if turns is None:
        turns = [
            (1, "user", "I have 8 months runway saved. Plan is 6 weeks."),
            (1, "assistant", "Tell me about your pipeline."),
        ]
    if extraction is None:
        extraction = ExtractionPayload(
            decision_situation="Launch timing decision.",
            live_constraints=(),
            synthesized_position="mixed",
            reasoning_passages=(),
            original_framing="Launch in 6 weeks?",
            dropped_threads=(),
        )
    return ConversationContext(
        turns=tuple(ContextTurn(turn_index=i, speaker=s, text=t) for (i, s, t) in turns),
        extraction=extraction,
    )


# ---------------------------------------------------------------------------
# Prompt shape
# ---------------------------------------------------------------------------


def test_valid_kinds_is_the_three_kind_taxonomy() -> None:
    assert VALID_KINDS == ("constraint", "concern", "open_loop")


def test_system_prompt_names_the_three_kinds_exactly() -> None:
    for kind in VALID_KINDS:
        assert kind in LIVE_CONSTRAINTS_SYSTEM_PROMPT


def test_system_prompt_requires_verbatim_substring_evidence() -> None:
    lowered = LIVE_CONSTRAINTS_SYSTEM_PROMPT.lower()
    assert "substring" in lowered
    assert "user turn" in lowered


def test_system_prompt_supports_derivation_mode() -> None:
    assert "derivation" in LIVE_CONSTRAINTS_SYSTEM_PROMPT.lower()
    assert "turn_refs" in LIVE_CONSTRAINTS_SYSTEM_PROMPT


def test_system_prompt_names_kind_ambiguity() -> None:
    assert "kind_ambiguity" in LIVE_CONSTRAINTS_SYSTEM_PROMPT


def test_user_prompt_has_context_and_source_sections() -> None:
    prompt = _format_user_prompt(_ctx())
    assert "CONTEXT" in prompt
    assert "SOURCE" in prompt


def test_user_prompt_places_user_turns_in_source() -> None:
    prompt = _format_user_prompt(_ctx(turns=[(1, "user", "User says XYZ.")]))
    source_pos = prompt.find("SOURCE (")
    assert source_pos >= 0
    source_section = prompt[source_pos:]
    assert "User says XYZ." in source_section
    assert "USER:" in source_section


def test_user_prompt_excludes_user_turns_from_context_section() -> None:
    """User turns belong in SOURCE only — keep them out of CONTEXT."""
    prompt = _format_user_prompt(_ctx(turns=[(1, "user", "UNIQ_USER_XYZ")]))
    source_pos = prompt.find("SOURCE (")
    context_section = prompt[:source_pos]
    assert "UNIQ_USER_XYZ" not in context_section


def test_user_prompt_places_assistant_turns_in_context_not_source() -> None:
    prompt = _format_user_prompt(
        _ctx(turns=[
            (1, "user", "User speaks."),
            (1, "assistant", "Assistant speaks UNIQ_ASSIST."),
        ])
    )
    source_pos = prompt.find("SOURCE (")
    context_section = prompt[:source_pos]
    source_section = prompt[source_pos:]
    assert "UNIQ_ASSIST" in context_section
    assert "UNIQ_ASSIST" not in source_section


# ---------------------------------------------------------------------------
# Span-mode parse + validation
# ---------------------------------------------------------------------------


def test_extract_parses_valid_span_output() -> None:
    ctx = _ctx(turns=[(1, "user", "I have 8 months runway saved.")])
    boundary = _FakeBoundary({
        "live_constraints": [
            {
                "mode": "span",
                "text": "I have 8 months runway saved.",
                "turn_index": 1,
                "kind": "constraint",
                "kind_ambiguity": False,
            }
        ]
    })
    events, stats = extract_live_constraints(context=ctx, boundary=boundary)
    assert len(events) == 1
    event = events[0]
    assert event.kind == "constraint"
    assert event.text == "I have 8 months runway saved."
    assert isinstance(event.provenance, SpanProvenance)
    assert event.kind_ambiguity is False
    assert event.status == "active"
    assert stats.validated_count == 1
    assert stats.span_mode_count == 1
    assert stats.derivation_mode_count == 0


def test_extract_computes_exact_span_positions() -> None:
    user_text = "Before it. I have 8 months runway saved. After it."
    ctx = _ctx(turns=[(1, "user", user_text)])
    boundary = _FakeBoundary({
        "live_constraints": [
            {
                "mode": "span",
                "text": "I have 8 months runway saved.",
                "turn_index": 1,
                "kind": "constraint",
                "kind_ambiguity": False,
            }
        ]
    })
    events, _ = extract_live_constraints(context=ctx, boundary=boundary)
    ref = events[0].provenance.span_ref
    assert user_text[ref.start_char:ref.end_char] == "I have 8 months runway saved."
    assert ref.speaker == "user"


def test_extract_drops_span_with_invalid_kind() -> None:
    ctx = _ctx(turns=[(1, "user", "A fact lives here.")])
    boundary = _FakeBoundary({
        "live_constraints": [
            {
                "mode": "span",
                "text": "A fact lives here.",
                "turn_index": 1,
                "kind": "bogus_kind",
                "kind_ambiguity": False,
            }
        ]
    })
    events, stats = extract_live_constraints(context=ctx, boundary=boundary)
    assert events == []
    assert stats.dropped_invalid_kind == 1


def test_extract_drops_span_whose_text_is_not_a_substring() -> None:
    ctx = _ctx(turns=[(1, "user", "Something entirely different.")])
    boundary = _FakeBoundary({
        "live_constraints": [
            {
                "mode": "span",
                "text": "This text is not in the user turn",
                "turn_index": 1,
                "kind": "constraint",
                "kind_ambiguity": False,
            }
        ]
    })
    events, stats = extract_live_constraints(context=ctx, boundary=boundary)
    assert events == []
    assert stats.dropped_not_substring == 1


def test_extract_drops_span_pointing_at_nonexistent_turn() -> None:
    ctx = _ctx(turns=[(1, "user", "Only turn 1 user.")])
    boundary = _FakeBoundary({
        "live_constraints": [
            {
                "mode": "span",
                "text": "Only turn 1 user.",
                "turn_index": 99,
                "kind": "constraint",
                "kind_ambiguity": False,
            }
        ]
    })
    events, stats = extract_live_constraints(context=ctx, boundary=boundary)
    assert events == []
    assert stats.dropped_invalid_turn == 1


def test_extract_span_mode_does_not_quote_from_assistant_turns() -> None:
    """Even if an assistant turn text matches the extract literally, a
    turn_index whose speaker is assistant and has no user counterpart
    should fail the user_turn_map lookup."""
    ctx = _ctx(turns=[
        (1, "user", "User content only."),
        (2, "assistant", "This is assistant content."),
    ])
    boundary = _FakeBoundary({
        "live_constraints": [
            {
                "mode": "span",
                "text": "This is assistant content.",
                "turn_index": 2,  # only assistant, no user turn 2
                "kind": "constraint",
                "kind_ambiguity": False,
            }
        ]
    })
    events, stats = extract_live_constraints(context=ctx, boundary=boundary)
    assert events == []
    assert stats.dropped_invalid_turn == 1


def test_extract_tolerates_case_folding_and_preserves_transcript_casing() -> None:
    user_text = "You should know, I have 8 months runway saved."
    ctx = _ctx(turns=[(1, "user", user_text)])
    boundary = _FakeBoundary({
        "live_constraints": [
            {
                "mode": "span",
                "text": "i have 8 months runway saved.",  # lowercase i
                "turn_index": 1,
                "kind": "constraint",
                "kind_ambiguity": False,
            }
        ]
    })
    events, stats = extract_live_constraints(context=ctx, boundary=boundary)
    assert len(events) == 1
    assert events[0].text == "I have 8 months runway saved."
    assert stats.validated_count == 1


def test_extract_carries_kind_ambiguity_true() -> None:
    ctx = _ctx(turns=[(1, "user", "I've been going through her phone for months. I'm not proud of it.")])
    boundary = _FakeBoundary({
        "live_constraints": [
            {
                "mode": "span",
                "text": "I've been going through her phone for months.",
                "turn_index": 1,
                "kind": "constraint",
                "kind_ambiguity": True,  # constraint + concern
            }
        ]
    })
    events, _ = extract_live_constraints(context=ctx, boundary=boundary)
    assert len(events) == 1
    assert events[0].kind_ambiguity is True
    assert events[0].kind == "constraint"  # primary preserved


def test_extract_returns_empty_on_no_live_constraints() -> None:
    ctx = _ctx()
    boundary = _FakeBoundary({"live_constraints": []})
    events, stats = extract_live_constraints(context=ctx, boundary=boundary)
    assert events == []
    assert stats.raw_count == 0
    assert stats.validated_count == 0


# ---------------------------------------------------------------------------
# Derivation-mode parse + validation
# ---------------------------------------------------------------------------


def test_extract_parses_valid_derivation_output() -> None:
    ctx = _ctx(turns=[
        (1, "user", "Plan is to go independent starting in 6 weeks."),
        (2, "user", "Our Q3 planning cycle ends mid-July."),
    ])
    boundary = _FakeBoundary({
        "live_constraints": [
            {
                "mode": "derivation",
                "text": "Launch timeline: 6 weeks aligned with Q3 planning end",
                "turn_refs": [
                    {"turn_index": 1, "span_excerpt": "Plan is to go independent starting in 6 weeks."},
                    {"turn_index": 2, "span_excerpt": "Our Q3 planning cycle ends mid-July."},
                ],
                "kind": "constraint",
                "kind_ambiguity": False,
            }
        ]
    })
    events, stats = extract_live_constraints(context=ctx, boundary=boundary)
    assert len(events) == 1
    event = events[0]
    assert isinstance(event.provenance, DerivationProvenance)
    assert len(event.provenance.turn_refs) == 2
    assert event.provenance.turn_refs[0].turn_index == 1
    assert event.provenance.turn_refs[1].turn_index == 2
    assert event.kind == "constraint"
    assert event.text.startswith("Launch timeline")
    assert stats.derivation_mode_count == 1


def test_extract_derivation_drops_ref_with_bad_excerpt() -> None:
    """Refs where span_excerpt doesn't substring-validate are silently
    removed. If that leaves only 1 valid ref, the event auto-downgrades
    to span mode."""
    ctx = _ctx(turns=[
        (1, "user", "Plan is to go independent starting in 6 weeks."),
        (2, "user", "Completely unrelated turn text."),
    ])
    boundary = _FakeBoundary({
        "live_constraints": [
            {
                "mode": "derivation",
                "text": "Launch timeline label",
                "turn_refs": [
                    {"turn_index": 1, "span_excerpt": "Plan is to go independent starting in 6 weeks."},
                    {"turn_index": 2, "span_excerpt": "This excerpt is not in turn 2"},
                ],
                "kind": "constraint",
                "kind_ambiguity": False,
            }
        ]
    })
    events, stats = extract_live_constraints(context=ctx, boundary=boundary)
    # Downgraded to span mode with 1 valid ref
    assert len(events) == 1
    assert isinstance(events[0].provenance, SpanProvenance)
    assert stats.span_mode_count == 1
    assert stats.derivation_mode_count == 0


def test_extract_derivation_with_zero_valid_excerpts_is_dropped() -> None:
    ctx = _ctx(turns=[(1, "user", "One user turn only.")])
    boundary = _FakeBoundary({
        "live_constraints": [
            {
                "mode": "derivation",
                "text": "All excerpts bogus",
                "turn_refs": [
                    {"turn_index": 1, "span_excerpt": "Not in turn 1"},
                    {"turn_index": 2, "span_excerpt": "Not in a turn at all"},
                ],
                "kind": "constraint",
                "kind_ambiguity": False,
            }
        ]
    })
    events, stats = extract_live_constraints(context=ctx, boundary=boundary)
    assert events == []
    assert stats.dropped_derivation_no_valid_excerpt == 1


def test_extract_derivation_single_valid_turn_downgrades_to_span() -> None:
    """If only one valid excerpt survives, emit as SpanProvenance — this
    prevents the LLM using derivation to dodge substring validation."""
    ctx = _ctx(turns=[
        (1, "user", "Plan is 6 weeks."),
    ])
    boundary = _FakeBoundary({
        "live_constraints": [
            {
                "mode": "derivation",
                "text": "Timeline combined label",
                "turn_refs": [
                    {"turn_index": 1, "span_excerpt": "Plan is 6 weeks."},
                ],
                "kind": "constraint",
                "kind_ambiguity": False,
            }
        ]
    })
    events, stats = extract_live_constraints(context=ctx, boundary=boundary)
    assert len(events) == 1
    assert isinstance(events[0].provenance, SpanProvenance)
    assert events[0].text == "Plan is 6 weeks."  # uses matched substring, not the derivation label
    assert stats.span_mode_count == 1
    assert stats.derivation_mode_count == 0


def test_extract_derivation_carries_kind_ambiguity() -> None:
    ctx = _ctx(turns=[
        (1, "user", "Her dad says I'm overreacting."),
        (2, "user", "Also she shut down completely."),
    ])
    boundary = _FakeBoundary({
        "live_constraints": [
            {
                "mode": "derivation",
                "text": "Composite situational constraint",
                "turn_refs": [
                    {"turn_index": 1, "span_excerpt": "Her dad says I'm overreacting."},
                    {"turn_index": 2, "span_excerpt": "she shut down completely."},
                ],
                "kind": "constraint",
                "kind_ambiguity": True,
            }
        ]
    })
    events, _ = extract_live_constraints(context=ctx, boundary=boundary)
    assert len(events) == 1
    assert events[0].kind_ambiguity is True


# ---------------------------------------------------------------------------
# Observability: stats + issue_id determinism + log
# ---------------------------------------------------------------------------


def test_validation_stats_has_per_drop_counters() -> None:
    ctx = _ctx(turns=[(1, "user", "Real text here.")])
    boundary = _FakeBoundary({
        "live_constraints": [
            {"mode": "span", "text": "Real text here.", "turn_index": 1, "kind": "constraint"},
            {"mode": "span", "text": "Bogus", "turn_index": 99, "kind": "constraint"},
            {"mode": "span", "text": "Other bogus", "turn_index": 1, "kind": "not-a-kind"},
            {"mode": "span", "text": "Not substring", "turn_index": 1, "kind": "constraint"},
            {"mode": "unknown_mode", "text": "x", "turn_index": 1, "kind": "constraint"},
        ]
    })
    events, stats = extract_live_constraints(context=ctx, boundary=boundary)
    assert len(events) == 1
    assert stats.raw_count == 5
    assert stats.validated_count == 1
    assert stats.span_mode_count == 1
    assert stats.dropped_invalid_turn == 1
    assert stats.dropped_invalid_kind == 1
    assert stats.dropped_not_substring == 1
    assert stats.dropped_invalid_mode == 1


def test_span_issue_id_is_deterministic_on_same_input() -> None:
    ctx = _ctx(turns=[(1, "user", "I have 8 months runway saved.")])
    payload = {
        "live_constraints": [
            {
                "mode": "span",
                "text": "I have 8 months runway saved.",
                "turn_index": 1,
                "kind": "constraint",
                "kind_ambiguity": False,
            }
        ]
    }
    first_events, _ = extract_live_constraints(context=ctx, boundary=_FakeBoundary(payload))
    second_events, _ = extract_live_constraints(context=ctx, boundary=_FakeBoundary(payload))
    assert first_events[0].issue_id == second_events[0].issue_id
    assert first_events[0].issue_id.startswith("live_constraint_t1_constraint_")


def test_completion_log_fires_at_info_level(caplog) -> None:
    ctx = _ctx(turns=[(1, "user", "Fact.")])
    boundary = _FakeBoundary({
        "live_constraints": [
            {"mode": "span", "text": "Fact.", "turn_index": 1, "kind": "constraint"}
        ]
    })
    with caplog.at_level(logging.INFO, logger="system_b.live_constraints_extraction"):
        extract_live_constraints(context=ctx, boundary=boundary)
    messages = [r.getMessage() for r in caplog.records]
    assert any("live_constraints_extraction.completed" in m for m in messages)


# ---------------------------------------------------------------------------
# Constructor integration
# ---------------------------------------------------------------------------


def test_constructor_default_uses_monolith_live_constraints_mapping() -> None:
    """Phase-1 behavior preserved: without a live_constraints_extractor,
    the constructor maps context.extraction.live_constraints via
    TurnRefProvenance. Existing tests already prove this shape."""
    from engine.system_b.conversation_context import ExtractionPayload, LiveConstraint

    ctx = ConversationContext(
        turns=(
            ContextTurn(turn_index=1, speaker="user", text="I have X."),
            ContextTurn(turn_index=1, speaker="assistant", text="OK."),
        ),
        extraction=ExtractionPayload(
            decision_situation="S",
            live_constraints=(
                LiveConstraint(constraint="monolith says X", introduced_turn=1, status="active", weight="situational"),
            ),
            synthesized_position="",
            reasoning_passages=(),
            original_framing="F",
            dropped_threads=(),
        ),
    )
    ir = construct_conversation_ir(ctx)
    live_events = [e for e in ir.user_issue_events if e.kind == "constraint"]
    assert len(live_events) == 1
    assert live_events[0].text == "monolith says X"
    assert isinstance(live_events[0].provenance, TurnRefProvenance)


def test_constructor_uses_injected_live_constraints_extractor() -> None:
    """Phase 5 behavior: extractor output replaces monolith's
    live_constraints mapping. dropped_threads still come from monolith."""
    from engine.system_b.conversation_context import ExtractionPayload, LiveConstraint

    ctx = ConversationContext(
        turns=(
            ContextTurn(turn_index=1, speaker="user", text="I have 8 months runway."),
            ContextTurn(turn_index=1, speaker="assistant", text="Context."),
        ),
        extraction=ExtractionPayload(
            decision_situation="S",
            live_constraints=(
                LiveConstraint(constraint="monolith-emitted paraphrase", introduced_turn=1, status="active", weight="situational"),
            ),
            synthesized_position="",
            reasoning_passages=(),
            original_framing="F",
            dropped_threads=(),
        ),
    )

    boundary = _FakeBoundary({
        "live_constraints": [
            {
                "mode": "span",
                "text": "I have 8 months runway.",
                "turn_index": 1,
                "kind": "constraint",
                "kind_ambiguity": False,
            }
        ]
    })

    def specialist(context: ConversationContext) -> list[UserIssueEvent]:
        events, _ = extract_live_constraints(context=context, boundary=boundary)
        return events

    ir = construct_conversation_ir(ctx, live_constraints_extractor=specialist)
    live_events = [e for e in ir.user_issue_events if e.kind == "constraint"]
    assert len(live_events) == 1
    # specialist's span-backed event, NOT the monolith's paraphrase
    assert live_events[0].text == "I have 8 months runway."
    assert isinstance(live_events[0].provenance, SpanProvenance)


def test_constructor_survives_live_constraints_extractor_raising() -> None:
    """If the extractor raises, the constructor logs WARNING and
    continues — rest of IR still builds; user_issue_events just stays
    empty for the specialist path."""
    from engine.system_b.conversation_context import ExtractionPayload

    ctx = ConversationContext(
        turns=(
            ContextTurn(turn_index=1, speaker="user", text="Turn 1 user."),
            ContextTurn(turn_index=1, speaker="assistant", text="Turn 1 asst."),
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
        raise RuntimeError("specialist boundary failed")

    ir = construct_conversation_ir(ctx, live_constraints_extractor=broken)
    assert [e for e in ir.user_issue_events if e.kind == "constraint"] == []
    assert len(ir.turns) == 2  # IR still built turns + frame anchor
