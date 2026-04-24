"""Tests for the Phase 1 provenance-bearing Conversation IR."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from engine.system_b.conversation_context import (
    ConversationContext,
    DroppedThread,
    ExtractionPayload,
    LiveConstraint,
    Turn as ContextTurn,
)
from engine.system_b.conversation_loader import load_conversation_context
from engine.system_b.ir import (
    ConversationIR,
    DerivationProvenance,
    FrameAnchor,
    SpanProvenance,
    SpanRef,
    StanceEvent,
    Turn,
    TurnRef,
    TurnRefProvenance,
    UserIssueEvent,
)
from engine.system_b.ir_builders import (
    add_frame_anchor,
    add_span,
    add_stance_event,
    add_turn,
    add_user_issue_event,
    supersede_issue,
)
from engine.system_b.ir_constructor import construct_conversation_ir


ROOT = Path(__file__).resolve().parents[1]
USER_HAS_PLAN_EXTRACTION = (
    ROOT
    / "research/test-cases/phase2a-lane3-equivalence-2026-04-23/_scratch/user_has_plan_extraction.json"
)
USER_HAS_PLAN_CONVERSATION = (
    ROOT / "research/test-cases/case_user_has_plan_conversation.txt"
)
WHISTLEBLOWER_EXTRACTION = (
    ROOT
    / "research/test-cases/phase2a-lane3-equivalence-2026-04-23/_scratch/whistleblower_extraction.json"
)
WHISTLEBLOWER_CONVERSATION = (
    ROOT / "research/test-cases/case_whistleblower_conversation.txt"
)


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


def test_span_ref_rejects_invalid_or_missing_turn_identity() -> None:
    ir = ConversationIR(
        turns=(Turn(turn_index=1, speaker="user", text="only a user turn"),)
    )

    with pytest.raises(ValueError, match="start_char"):
        SpanRef(turn_index=1, speaker="user", start_char=-1, end_char=3)

    with pytest.raises(ValueError, match="end_char"):
        SpanRef(turn_index=1, speaker="user", start_char=4, end_char=3)

    with pytest.raises(ValueError, match="missing turn"):
        ir.resolve_span(
            SpanRef(
                turn_index=1,
                speaker="assistant",
                start_char=0,
                end_char=3,
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


def test_turn_ref_and_derivation_provenance_keep_paraphrases_honest() -> None:
    turn_ref = TurnRefProvenance(
        turn_refs=(TurnRef(turn_index=2, speaker="user"),),
        note="paraphrased live constraint",
    )
    derivation = DerivationProvenance(
        turn_refs=(
            TurnRef(turn_index=2, speaker="user"),
            TurnRef(turn_index=4, speaker="assistant"),
        ),
        source_object_ids=("issue_001", "frame_001"),
        note="inferred across objects",
    )

    assert turn_ref.to_dict() == {
        "kind": "turn_ref",
        "turn_refs": [{"turn_index": 2, "speaker": "user"}],
        "note": "paraphrased live constraint",
    }
    assert derivation.to_dict() == {
        "kind": "derivation",
        "turn_refs": [
            {"turn_index": 2, "speaker": "user"},
            {"turn_index": 4, "speaker": "assistant"},
        ],
        "source_object_ids": ["issue_001", "frame_001"],
        "note": "inferred across objects",
    }


def test_user_issue_event_records_kind_and_ambiguity_without_adding_a_fourth_kind() -> None:
    issue = UserIssueEvent(
        issue_id="issue_001",
        text="spouse support is concept-level, not specifics",
        kind="constraint",
        status="active",
        provenance=TurnRefProvenance(
            turn_refs=(TurnRef(turn_index=2, speaker="user"),)
        ),
        introduced_at_turn=2,
        kind_ambiguity=True,
    )

    assert issue.kind == "constraint"
    assert issue.kind_ambiguity is True
    assert issue.to_dict()["kind_ambiguity"] is True

    with pytest.raises(ValueError, match="UserIssueEvent.kind"):
        UserIssueEvent(
            issue_id="issue_bad",
            text="not a v1 kind",
            kind="mixed",
            status="active",
            provenance=issue.provenance,
        )


def test_derived_objects_require_provenance() -> None:
    with pytest.raises(ValueError, match="provenance"):
        FrameAnchor(anchor_id="frame_bad", text="frame", provenance=None)

    with pytest.raises(ValueError, match="provenance"):
        UserIssueEvent(
            issue_id="issue_bad",
            text="issue",
            kind="constraint",
            status="active",
            provenance=None,
        )

    with pytest.raises(ValueError, match="provenance"):
        StanceEvent(
            stance_id="stance_bad",
            speaker="user",
            stance="commitment",
            text="I decided.",
            provenance=None,
        )


def test_conversation_ir_round_trips_typed_objects() -> None:
    span = SpanRef(turn_index=1, speaker="user", start_char=0, end_char=10)
    ir = ConversationIR(
        turns=(Turn(turn_index=1, speaker="user", text="I decided."),),
        spans=(span,),
        frame_anchors=(
            FrameAnchor(
                anchor_id="frame_001",
                text="default framing",
                provenance=SpanProvenance(span_ref=span),
                frame_pattern="single option",
            ),
        ),
        user_issue_events=(
            UserIssueEvent(
                issue_id="issue_001",
                text="spouse alignment",
                kind="constraint",
                status="active",
                provenance=TurnRefProvenance(
                    turn_refs=(TurnRef(turn_index=1, speaker="user"),)
                ),
            ),
        ),
        stance_events=(
            StanceEvent(
                stance_id="stance_001",
                speaker="user",
                stance="commitment",
                text="I decided.",
                provenance=SpanProvenance(span_ref=span),
                turn_index=1,
            ),
        ),
    )

    assert ConversationIR.from_dict(ir.to_dict()) == ir
    assert ir.provenance_tier_counts() == {
        "span": 2,
        "turn_ref": 1,
        "derivation": 0,
    }


def test_reducer_builders_return_new_ir_instances_without_mutating_input() -> None:
    base = ConversationIR()
    with_turn = add_turn(
        base,
        Turn(turn_index=1, speaker="user", text="I decided to quit."),
    )
    issue = UserIssueEvent(
        issue_id="issue_001",
        text="spouse alignment",
        kind="constraint",
        status="active",
        provenance=TurnRefProvenance(
            turn_refs=(TurnRef(turn_index=1, speaker="user"),)
        ),
    )
    with_issue = add_user_issue_event(with_turn, issue)
    superseded = supersede_issue(
        with_issue,
        issue_id="issue_001",
        superseded_by="issue_002",
        resolved_at_turn=3,
    )

    assert base.turns == ()
    assert with_turn.turns == (
        Turn(turn_index=1, speaker="user", text="I decided to quit."),
    )
    assert with_issue.user_issue_events == (issue,)
    assert superseded.user_issue_events[0].status == "superseded"
    assert superseded.user_issue_events[0].superseded_by == "issue_002"

    with_anchor = add_frame_anchor(
        with_turn,
        FrameAnchor(
            anchor_id="frame_001",
            text="quit/no quit binary",
            provenance=TurnRefProvenance(
                turn_refs=(TurnRef(turn_index=1, speaker="user"),)
            ),
        ),
    )
    with_stance = add_stance_event(
        with_turn,
        StanceEvent(
            stance_id="stance_001",
            speaker="user",
            stance="commitment",
            text="I decided to quit.",
            provenance=TurnRefProvenance(
                turn_refs=(TurnRef(turn_index=1, speaker="user"),)
            ),
        ),
    )

    assert with_anchor.frame_anchors[0].anchor_id == "frame_001"
    assert with_stance.stance_events[0].speaker == "user"


def test_add_span_validates_against_stored_turns_before_adding() -> None:
    ir = ConversationIR(
        turns=(Turn(turn_index=1, speaker="user", text="abcdefgh"),)
    )

    with_span = add_span(
        ir,
        SpanRef(turn_index=1, speaker="user", start_char=2, end_char=5),
    )

    assert with_span.spans == (
        SpanRef(turn_index=1, speaker="user", start_char=2, end_char=5),
    )
    assert ir.spans == ()

    with pytest.raises(ValueError, match="outside turn text"):
        add_span(
            ir,
            SpanRef(turn_index=1, speaker="user", start_char=2, end_char=99),
        )


def test_deferred_candidates_are_not_first_class_v1_dataclasses() -> None:
    import engine.system_b.ir as ir_module

    for name in ("ActorRef", "DecisionOption", "ReasoningSegment", "CoverageTarget"):
        assert not hasattr(ir_module, name)


def test_construct_conversation_ir_maps_real_artifact_with_honest_provenance() -> None:
    context = load_conversation_context(
        USER_HAS_PLAN_EXTRACTION,
        USER_HAS_PLAN_CONVERSATION,
    )

    ir = construct_conversation_ir(context)

    assert ir.turns[0] == Turn(
        turn_index=1,
        speaker="user",
        text=context.turns[0].text,
    )
    assert len(ir.turns) == len(context.turns)
    assert [(t.turn_index, t.speaker) for t in ir.turns].count((1, "user")) == 1
    assert [(t.turn_index, t.speaker) for t in ir.turns].count((1, "assistant")) == 1

    assert len(ir.user_issue_events) == 5
    live_constraints = [
        issue for issue in ir.user_issue_events if issue.kind == "constraint"
    ]
    open_loops = [
        issue for issue in ir.user_issue_events if issue.kind == "open_loop"
    ]
    assert len(live_constraints) == 4
    assert len(open_loops) == 1
    assert all(issue.provenance.kind == "turn_ref" for issue in live_constraints)

    spouse_issue = next(
        issue for issue in live_constraints if issue.text.startswith("Spouse support:")
    )
    assert spouse_issue.kind == "constraint"
    assert spouse_issue.kind_ambiguity is True
    assert spouse_issue.provenance.turn_refs == (
        TurnRef(turn_index=5, speaker="user"),
    )

    dropped_thread = open_loops[0]
    assert dropped_thread.status == "acknowledged_then_dropped"
    assert dropped_thread.superseded_by == (
        "focus on fundamentals like pipeline conversion, runway realism, "
        "spouse alignment, and fractional bridge"
    )

    assert ir.frame_anchors == (
        FrameAnchor(
            anchor_id="frame_001",
            text=context.extraction.original_framing,
            provenance=TurnRefProvenance(
                turn_refs=(TurnRef(turn_index=1, speaker="user"),),
                note="original_framing is extractor paraphrase",
            ),
            frame_pattern="original_framing",
        ),
    )
    assert ir.stance_events == ()
    assert ir.spans == ()


def test_construct_conversation_ir_maps_unresolved_dropped_threads_to_concerns() -> None:
    context = ConversationContext(
        turns=(
            ContextTurn(
                turn_index=1,
                speaker="user",
                text="I am worried the internal route exposes me.",
            ),
        ),
        extraction=ExtractionPayload(
            decision_situation="Report externally or internally?",
            live_constraints=(),
            synthesized_position="",
            reasoning_passages=(),
            original_framing="",
            dropped_threads=(
                DroppedThread(
                    thread="Internal route exposes identity",
                    raised_by="user",
                    raised_turn=1,
                    status="unresolved",
                ),
            ),
        ),
    )

    ir = construct_conversation_ir(context)

    assert ir.user_issue_events == (
        UserIssueEvent(
            issue_id="dropped_thread_001",
            text="Internal route exposes identity",
            kind="concern",
            status="unresolved",
            provenance=TurnRefProvenance(
                turn_refs=(TurnRef(turn_index=1, speaker="user"),),
                note="dropped_threads",
            ),
            introduced_at_turn=1,
        ),
    )


def test_construct_conversation_ir_does_not_turn_paraphrases_into_fake_spans() -> None:
    context = ConversationContext(
        turns=(
            ContextTurn(
                turn_index=1,
                speaker="user",
                text="My spouse has not seen the specific runway math yet.",
            ),
        ),
        extraction=ExtractionPayload(
            decision_situation="Launch now?",
            live_constraints=(
                LiveConstraint(
                    constraint="Spouse support: on board with concept, not specifics of financial pressure",
                    introduced_turn=1,
                    status="active",
                    weight="situational",
                ),
            ),
            synthesized_position=(
                "Launching is viable if spouse alignment and pipeline conversion happen."
            ),
            reasoning_passages=("fake passage from quote validation should be ignored",),
            original_framing="User assumes launch tactics are the main issue.",
            dropped_threads=(),
            quote_validation={
                "fabricated_passages": ["fake passage from quote validation should be ignored"]
            },
        ),
    )

    ir = construct_conversation_ir(context)

    assert ir.spans == ()
    assert all(
        obj.provenance.kind != "span"
        for obj in (*ir.user_issue_events, *ir.frame_anchors, *ir.stance_events)
    )
    assert "fake passage" not in str(ir.to_dict())


def test_construct_conversation_ir_handles_non_lane3_fixture_case() -> None:
    context = load_conversation_context(
        WHISTLEBLOWER_EXTRACTION,
        WHISTLEBLOWER_CONVERSATION,
    )

    ir = construct_conversation_ir(context)

    assert len(ir.turns) == len(context.turns)
    assert ir.user_issue_events
    assert all(issue.provenance.kind for issue in ir.user_issue_events)
    assert all(anchor.provenance.kind for anchor in ir.frame_anchors)


def test_construct_conversation_ir_completes_user_has_plan_under_50ms() -> None:
    context = load_conversation_context(
        USER_HAS_PLAN_EXTRACTION,
        USER_HAS_PLAN_CONVERSATION,
    )

    start = time.perf_counter()
    construct_conversation_ir(context)
    elapsed = time.perf_counter() - start

    assert elapsed < 0.050
