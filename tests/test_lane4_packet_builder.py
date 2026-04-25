"""Tests for Phase 4 Lane 4 packet builder.

Verifies that `build_lane4_packet` projects ConversationIR into the
minimum slice Lane 4 needs, with provenance kinds preserved, kind
distinctions intact, and speaker derived from provenance.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

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
    Turn,
    TurnRef,
    TurnRefProvenance,
    UserIssueEvent,
)
from engine.system_b.ir_builders import (
    add_frame_anchor,
    add_turn,
    add_user_issue_event,
)
from engine.system_b.ir_constructor import construct_conversation_ir
from engine.system_b.packet_builders.lane4 import (
    ConstraintView,
    FrameView,
    IssueView,
    Lane4Packet,
    build_lane4_packet,
)


ROOT = Path(__file__).resolve().parents[1]
USER_HAS_PLAN_EXTRACTION = (
    ROOT
    / "research/test-cases/phase2a-lane3-equivalence-2026-04-23/_scratch/user_has_plan_extraction.json"
)
USER_HAS_PLAN_CONVERSATION = (
    ROOT / "research/test-cases/case_user_has_plan_conversation.txt"
)


# ---------------------------------------------------------------------------
# Empty IR
# ---------------------------------------------------------------------------


def test_empty_ir_produces_empty_packet() -> None:
    ir = ConversationIR()
    packet = build_lane4_packet(ir)
    assert packet.turns == ()
    assert packet.original_framing is None
    assert packet.decision_situation is None
    assert packet.constraints == ()
    assert packet.issues == ()


def test_packet_preserves_turns_in_order() -> None:
    ir = ConversationIR()
    ir = add_turn(ir, Turn(turn_index=1, speaker="user", text="user1"))
    ir = add_turn(ir, Turn(turn_index=1, speaker="assistant", text="asst1"))
    ir = add_turn(ir, Turn(turn_index=2, speaker="user", text="user2"))
    packet = build_lane4_packet(ir)
    assert len(packet.turns) == 3
    assert packet.turns[0].text == "user1"
    assert packet.turns[1].text == "asst1"
    assert packet.turns[2].text == "user2"


# ---------------------------------------------------------------------------
# Frame projection
# ---------------------------------------------------------------------------


def test_frame_views_distinguish_provenance_kinds() -> None:
    ir = ConversationIR()
    ir = add_turn(ir, Turn(turn_index=1, speaker="user", text="user1"))

    # original_framing as derivation (Phase 5.7 heuristic)
    ir = add_frame_anchor(
        ir,
        FrameAnchor(
            anchor_id="frame_001",
            text="framing text",
            provenance=DerivationProvenance(
                turn_refs=(TurnRef(turn_index=1, speaker="user"),),
                source_object_ids=(),
                note="multi-turn synthesis",
            ),
            frame_pattern="original_framing",
        ),
    )
    # decision_situation as derivation (Phase 5.8 heuristic)
    ir = add_frame_anchor(
        ir,
        FrameAnchor(
            anchor_id="frame_002",
            text="decision text",
            provenance=DerivationProvenance(
                turn_refs=(TurnRef(turn_index=1, speaker="user"),),
                source_object_ids=(),
                note="multi-turn synthesis",
            ),
            frame_pattern="decision_situation",
        ),
    )

    packet = build_lane4_packet(ir)
    assert packet.original_framing == FrameView(
        text="framing text", provenance_kind="derivation"
    )
    assert packet.decision_situation == FrameView(
        text="decision text", provenance_kind="derivation"
    )


def test_frame_view_carries_span_provenance_kind_when_substring_validated() -> None:
    """If a future specialist emits FrameAnchor with SpanProvenance, the
    packet must surface that as provenance_kind='span'."""
    ir = ConversationIR()
    ir = add_turn(ir, Turn(turn_index=1, speaker="user", text="The framing text spans here."))
    ir = add_frame_anchor(
        ir,
        FrameAnchor(
            anchor_id="frame_001",
            text="The framing text spans here.",
            provenance=SpanProvenance(
                span_ref=SpanRef(
                    turn_index=1, speaker="user", start_char=0, end_char=28,
                )
            ),
            frame_pattern="original_framing",
        ),
    )
    packet = build_lane4_packet(ir)
    assert packet.original_framing is not None
    assert packet.original_framing.provenance_kind == "span"


def test_missing_frame_anchor_produces_none() -> None:
    ir = ConversationIR()
    ir = add_turn(ir, Turn(turn_index=1, speaker="user", text="just a turn"))
    packet = build_lane4_packet(ir)
    assert packet.original_framing is None
    assert packet.decision_situation is None


# ---------------------------------------------------------------------------
# Constraint projection
# ---------------------------------------------------------------------------


def test_constraint_view_separates_constraints_from_other_kinds() -> None:
    ir = ConversationIR()
    ir = add_turn(ir, Turn(turn_index=1, speaker="user", text="u"))
    ir = add_user_issue_event(
        ir,
        UserIssueEvent(
            issue_id="c1",
            text="hard deadline",
            kind="constraint",
            status="active",
            provenance=TurnRefProvenance(
                turn_refs=(TurnRef(turn_index=1, speaker="user"),)
            ),
            introduced_at_turn=1,
            kind_ambiguity=False,
        ),
    )
    ir = add_user_issue_event(
        ir,
        UserIssueEvent(
            issue_id="o1",
            text="dropped question",
            kind="open_loop",
            status="acknowledged_then_dropped",
            provenance=TurnRefProvenance(
                turn_refs=(TurnRef(turn_index=1, speaker="user"),)
            ),
            superseded_by="later focus",
        ),
    )
    packet = build_lane4_packet(ir)
    assert len(packet.constraints) == 1
    assert packet.constraints[0].text == "hard deadline"
    assert len(packet.issues) == 1
    assert packet.issues[0].text == "dropped question"
    assert packet.issues[0].kind == "open_loop"


def test_constraint_view_carries_status_and_provenance_kind() -> None:
    ir = ConversationIR()
    ir = add_turn(ir, Turn(turn_index=1, speaker="user", text="I have 8 months."))
    ir = add_user_issue_event(
        ir,
        UserIssueEvent(
            issue_id="c1",
            text="I have 8 months.",
            kind="constraint",
            status="active",
            provenance=SpanProvenance(
                span_ref=SpanRef(
                    turn_index=1, speaker="user", start_char=0, end_char=16,
                )
            ),
            introduced_at_turn=1,
            kind_ambiguity=False,
        ),
    )
    packet = build_lane4_packet(ir)
    assert len(packet.constraints) == 1
    cv = packet.constraints[0]
    assert cv.status == "active"
    assert cv.provenance_kind == "span"
    assert cv.introduced_at_turn == 1


def test_constraint_view_preserves_kind_ambiguity_flag() -> None:
    ir = ConversationIR()
    ir = add_turn(ir, Turn(turn_index=1, speaker="user", text="u"))
    ir = add_user_issue_event(
        ir,
        UserIssueEvent(
            issue_id="c1",
            text="ambiguous",
            kind="constraint",
            status="active",
            provenance=TurnRefProvenance(
                turn_refs=(TurnRef(turn_index=1, speaker="user"),)
            ),
            kind_ambiguity=True,
        ),
    )
    packet = build_lane4_packet(ir)
    assert packet.constraints[0].kind_ambiguity is True


# ---------------------------------------------------------------------------
# Issue projection (open_loop + concern)
# ---------------------------------------------------------------------------


def test_issue_view_distinguishes_open_loop_and_concern() -> None:
    ir = ConversationIR()
    ir = add_turn(ir, Turn(turn_index=1, speaker="user", text="u"))
    ir = add_user_issue_event(
        ir,
        UserIssueEvent(
            issue_id="o1",
            text="open thread",
            kind="open_loop",
            status="acknowledged_then_dropped",
            provenance=TurnRefProvenance(
                turn_refs=(TurnRef(turn_index=1, speaker="user"),)
            ),
        ),
    )
    ir = add_user_issue_event(
        ir,
        UserIssueEvent(
            issue_id="c1",
            text="active worry",
            kind="concern",
            status="active",
            provenance=TurnRefProvenance(
                turn_refs=(TurnRef(turn_index=1, speaker="user"),)
            ),
        ),
    )
    packet = build_lane4_packet(ir)
    assert len(packet.issues) == 2
    kinds = {i.kind for i in packet.issues}
    assert kinds == {"open_loop", "concern"}


def test_issue_view_derives_raised_by_from_span_provenance() -> None:
    ir = ConversationIR()
    ir = add_turn(ir, Turn(turn_index=1, speaker="user", text="u"))
    ir = add_turn(ir, Turn(turn_index=1, speaker="assistant", text="assistant span here"))
    ir = add_user_issue_event(
        ir,
        UserIssueEvent(
            issue_id="o1",
            text="assistant span here",
            kind="open_loop",
            status="acknowledged_then_dropped",
            provenance=SpanProvenance(
                span_ref=SpanRef(
                    turn_index=1, speaker="assistant", start_char=0, end_char=19,
                )
            ),
        ),
    )
    packet = build_lane4_packet(ir)
    assert packet.issues[0].raised_by == "assistant"


def test_issue_view_derives_raised_by_from_turn_ref_provenance() -> None:
    ir = ConversationIR()
    ir = add_turn(ir, Turn(turn_index=1, speaker="user", text="u"))
    ir = add_user_issue_event(
        ir,
        UserIssueEvent(
            issue_id="o1",
            text="user thread",
            kind="open_loop",
            status="acknowledged_then_dropped",
            provenance=TurnRefProvenance(
                turn_refs=(TurnRef(turn_index=1, speaker="user"),)
            ),
        ),
    )
    packet = build_lane4_packet(ir)
    assert packet.issues[0].raised_by == "user"


def test_issue_view_carries_superseded_by_passthrough() -> None:
    ir = ConversationIR()
    ir = add_turn(ir, Turn(turn_index=1, speaker="user", text="u"))
    ir = add_user_issue_event(
        ir,
        UserIssueEvent(
            issue_id="o1",
            text="thread",
            kind="open_loop",
            status="acknowledged_then_dropped",
            provenance=TurnRefProvenance(
                turn_refs=(TurnRef(turn_index=1, speaker="user"),)
            ),
            superseded_by="focus on fundamentals",
        ),
    )
    packet = build_lane4_packet(ir)
    assert packet.issues[0].superseded_by == "focus on fundamentals"


# ---------------------------------------------------------------------------
# Real fixture round-trip
# ---------------------------------------------------------------------------


def test_packet_built_from_real_user_has_plan_fixture() -> None:
    """End-to-end: load a real conversation, construct IR, project to
    Lane4Packet, verify the projection matches expected counts and kinds."""
    context = load_conversation_context(
        USER_HAS_PLAN_EXTRACTION,
        USER_HAS_PLAN_CONVERSATION,
    )
    ir = construct_conversation_ir(context)
    packet = build_lane4_packet(ir)

    # 16 turns (8 user + 8 assistant)
    assert len(packet.turns) == 16

    # Both frame anchors present after Phase 5.7/5.8 heuristics
    assert packet.original_framing is not None
    assert packet.original_framing.provenance_kind == "derivation"
    assert packet.decision_situation is not None
    assert packet.decision_situation.provenance_kind == "derivation"

    # 4 live_constraints in monolith output for this case
    assert len(packet.constraints) == 4
    # Phase 5.7 hasn't substring-validated these yet — still turn_ref
    assert all(c.provenance_kind == "turn_ref" for c in packet.constraints)

    # 1 dropped_thread → 1 issue (open_loop)
    assert len(packet.issues) == 1
    assert packet.issues[0].kind == "open_loop"
    assert packet.issues[0].raised_by == "user"
    assert packet.issues[0].superseded_by is not None
