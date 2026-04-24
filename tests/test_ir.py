"""Tests for the Phase 1 provenance-bearing Conversation IR."""

from __future__ import annotations

import pytest

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
    add_stance_event,
    add_turn,
    add_user_issue_event,
    supersede_issue,
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
