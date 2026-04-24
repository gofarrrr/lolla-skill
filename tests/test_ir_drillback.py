"""Drill-back tests for packet-like source refs over ConversationIR."""

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
    drill_back,
)


def test_drillback_from_frame_source_ref_to_exact_span_text() -> None:
    turn = Turn(
        turn_index=2,
        speaker="user",
        text='Pipeline: people said "if you were independent, we would consider you."',
    )
    span = SpanRef(
        turn_index=2,
        speaker="user",
        start_char=10,
        end_char=71,
    )
    ir = ConversationIR(
        turns=(turn,),
        spans=(span,),
        frame_anchors=(
            FrameAnchor(
                anchor_id="frame_001",
                text="network conversations are not committed pipeline",
                provenance=SpanProvenance(span_ref=span),
            ),
        ),
    )

    result = drill_back(
        ir,
        {"object_type": "frame_anchor", "object_id": "frame_001"},
    )

    assert result.provenance_kind == "span"
    assert result.exact_text == 'people said "if you were independent, we would consider you."'
    assert result.span_ref == span
    assert result.source_turns == (turn,)
    assert result.logical_hops <= 3


def test_drillback_from_issue_turn_ref_returns_full_source_turn_without_exact_text() -> None:
    turn = Turn(
        turn_index=5,
        speaker="user",
        text="Spouse is on board with the independent plan. Specific math is still in my head.",
    )
    ir = ConversationIR(
        turns=(turn,),
        user_issue_events=(
            UserIssueEvent(
                issue_id="issue_001",
                text="Spouse support: on board with concept, not specifics",
                kind="constraint",
                status="active",
                provenance=TurnRefProvenance(
                    turn_refs=(TurnRef(turn_index=5, speaker="user"),)
                ),
            ),
        ),
    )

    result = drill_back(
        ir,
        {"object_type": "user_issue_event", "object_id": "issue_001"},
    )

    assert result.provenance_kind == "turn_ref"
    assert result.exact_text is None
    assert result.span_ref is None
    assert result.source_turns == (turn,)
    assert result.logical_hops <= 3


def test_drillback_from_derivation_returns_lineage_without_fake_single_span() -> None:
    turn = Turn(turn_index=1, speaker="user", text="I have eight months runway.")
    ir = ConversationIR(
        turns=(turn,),
        stance_events=(
            StanceEvent(
                stance_id="stance_001",
                speaker="assistant",
                stance="shift",
                text="recommendation shifted after issue and frame evidence",
                provenance=DerivationProvenance(
                    turn_refs=(TurnRef(turn_index=1, speaker="user"),),
                    source_object_ids=("issue_001", "frame_001"),
                ),
            ),
        ),
    )

    result = drill_back(
        ir,
        {"object_type": "stance_event", "object_id": "stance_001"},
    )

    assert result.provenance_kind == "derivation"
    assert result.exact_text is None
    assert result.span_ref is None
    assert result.source_turns == (turn,)
    assert result.source_object_ids == ("issue_001", "frame_001")
    assert result.logical_hops <= 3


def test_drillback_missing_source_ref_fails_closed() -> None:
    ir = ConversationIR()

    with pytest.raises(ValueError, match="Unknown IR object"):
        drill_back(
            ir,
            {"object_type": "frame_anchor", "object_id": "missing"},
        )
