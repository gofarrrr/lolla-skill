"""ConversationContext -> ConversationIR construction."""

from __future__ import annotations

import logging
from typing import Callable

from .conversation_context import ConversationContext
from .ir import (
    ConversationIR,
    DerivationProvenance,
    FrameAnchor,
    StanceEvent,
    Turn,
    TurnRef,
    TurnRefProvenance,
    UserIssueEvent,
)
from .ir_builders import (
    add_frame_anchor,
    add_stance_event,
    add_turn,
    add_user_issue_event,
)


# Phase 3b: optional injectable callable that takes a ConversationContext and
# returns a list of StanceEvent. Default is None (deterministic, no-LLM IR
# construction — matches Phase 1 behavior). Production callers can pass
# `stance_extractor=partial(extract_stance_events, boundary=boundary_client)`
# to populate stance events; tests can inject deterministic fakes.
StanceExtractor = Callable[[ConversationContext], list[StanceEvent]]

# Phase 5: optional injectable callable that takes a ConversationContext and
# returns a list of UserIssueEvent (live_constraints only). When provided, its
# output REPLACES the monolith-extracted live_constraints mapping.
# dropped_threads mapping from context.extraction.dropped_threads is unaffected.
LiveConstraintsExtractor = Callable[[ConversationContext], list[UserIssueEvent]]


_LOGGER = logging.getLogger("system_b.ir_constructor")

_OPEN_LOOP_STATUSES = {
    "acknowledged_then_dropped",
    "dropped",
    "superseded",
}

_KIND_AMBIGUITY_MARKERS = (
    "not specifics",
    "not aligned",
    "not communicating",
    "minimizes",
    "minimizing",
    "ongoing secret",
    "surveillance",
    "reporting viable but",
    "worried",
)


def construct_conversation_ir(
    context: ConversationContext,
    *,
    stance_extractor: StanceExtractor | None = None,
    live_constraints_extractor: LiveConstraintsExtractor | None = None,
) -> ConversationIR:
    """Build the Phase 1 IR without changing lane behavior.

    Current extraction fields are summaries or paraphrases, so constructor
    provenance is conservative by default: use `turn_ref`, not exact spans.

    Phase 3b: optional `stance_extractor` populates `StanceEvent` objects
    when provided. Default is None — constructor stays deterministic and
    LLM-free. When provided, each returned stance is appended via the
    reducer; the extractor is expected to have already validated each span
    as an exact substring of an assistant turn.

    Phase 5: optional `live_constraints_extractor` REPLACES the monolith's
    paraphrased `live_constraints` → `UserIssueEvent` mapping with
    substring-validated span/derivation events. Default None preserves
    Phase-1 behavior. When provided and it raises, a WARNING is logged
    and live_constraint events stay empty from the specialist path;
    dropped_threads are still mapped from the monolith regardless.
    """

    ir = ConversationIR()
    for turn in context.turns:
        ir = add_turn(
            ir,
            Turn(
                turn_index=turn.turn_index,
                speaker=turn.speaker,
                text=turn.text,
            ),
        )

    if live_constraints_extractor is not None:
        try:
            specialist_events = live_constraints_extractor(context)
        except Exception as exc:  # noqa: BLE001
            _LOGGER.warning("live_constraints_extractor_failed: %s", exc)
            specialist_events = []
        for event in specialist_events:
            ir = add_user_issue_event(ir, event)
    else:
        for index, constraint in enumerate(context.extraction.live_constraints, 1):
            source_ref = _source_turn_ref(context, constraint.introduced_turn, "user")
            ir = add_user_issue_event(
                ir,
                UserIssueEvent(
                    issue_id=f"live_constraint_{index:03d}",
                    text=constraint.constraint,
                    kind="constraint",
                    status=constraint.status or "active",
                    provenance=TurnRefProvenance(
                        turn_refs=(source_ref,),
                        note="live_constraints",
                    ),
                    introduced_at_turn=source_ref.turn_index,
                    kind_ambiguity=_kind_ambiguity(constraint.constraint),
                ),
            )

    for index, thread in enumerate(context.extraction.dropped_threads, 1):
        source_ref = _source_turn_ref(
            context,
            thread.raised_turn,
            _normalize_speaker(thread.raised_by),
        )
        kind = _dropped_thread_kind(thread.status, thread.superseded_by)
        ir = add_user_issue_event(
            ir,
            UserIssueEvent(
                issue_id=f"dropped_thread_{index:03d}",
                text=thread.thread,
                kind=kind,
                status=thread.status or "active",
                provenance=TurnRefProvenance(
                    turn_refs=(source_ref,),
                    note="dropped_threads",
                ),
                introduced_at_turn=source_ref.turn_index,
                superseded_by=thread.superseded_by,
            ),
        )

    user_turn_refs = tuple(
        TurnRef(turn_index=turn.turn_index, speaker=turn.speaker)
        for turn in context.turns
        if turn.speaker == "user"
    )

    if context.extraction.original_framing:
        # Phase 5.7 heuristic: original_framing is multi-turn synthesis; ref
        # all user turns rather than just the first.
        if user_turn_refs:
            framing_provenance: TurnRefProvenance | DerivationProvenance = (
                DerivationProvenance(
                    turn_refs=user_turn_refs,
                    source_object_ids=(),
                    note=(
                        "original_framing is multi-turn extractor synthesis; "
                        "situation parts are substring-grounded across user turns, "
                        "exclusions are inferred"
                    ),
                )
            )
        else:
            framing_provenance = TurnRefProvenance(
                turn_refs=(_first_user_turn_ref(context),),
                note="original_framing fallback (no user turns found)",
            )
        ir = add_frame_anchor(
            ir,
            FrameAnchor(
                anchor_id="frame_001",
                text=context.extraction.original_framing,
                provenance=framing_provenance,
                frame_pattern="original_framing",
            ),
        )

    if context.extraction.decision_situation:
        # Phase 5.8 heuristic: decision_situation has the same multi-turn
        # synthesis shape as original_framing — wrapper template inferred,
        # decision/agent/context parts substring-grounded across user turns.
        # See research/phase5.8-decision-situation-design-memo-2026-04-25.md.
        if user_turn_refs:
            decision_provenance: TurnRefProvenance | DerivationProvenance = (
                DerivationProvenance(
                    turn_refs=user_turn_refs,
                    source_object_ids=(),
                    note=(
                        "decision_situation is multi-turn extractor synthesis; "
                        "decision/agent/context parts are substring-grounded "
                        "across user turns, the 'Whether X should Y' wrapper "
                        "template is inferred"
                    ),
                )
            )
        else:
            decision_provenance = TurnRefProvenance(
                turn_refs=(_first_user_turn_ref(context),),
                note="decision_situation fallback (no user turns found)",
            )
        ir = add_frame_anchor(
            ir,
            FrameAnchor(
                anchor_id="frame_002",
                text=context.extraction.decision_situation,
                provenance=decision_provenance,
                frame_pattern="decision_situation",
            ),
        )

    # Phase 3b: inject stance events if an extractor is provided. The extractor
    # is responsible for validation (substring check, relation vocabulary);
    # the constructor trusts what it gets back.
    if stance_extractor is not None:
        try:
            stances = stance_extractor(context)
        except Exception as exc:  # noqa: BLE001
            _LOGGER.warning("stance_extractor_failed: %s", exc)
            stances = []
        for stance in stances:
            ir = add_stance_event(ir, stance)

    _LOGGER.info(
        "conversation_ir_constructed turns=%s user_issue_events=%s "
        "frame_anchors=%s stance_events=%s provenance_tiers=%s",
        len(ir.turns),
        len(ir.user_issue_events),
        len(ir.frame_anchors),
        len(ir.stance_events),
        ir.provenance_tier_counts(),
    )
    return ir


def _dropped_thread_kind(status: str, superseded_by: str | None) -> str:
    normalized_status = (status or "").strip().lower()
    if superseded_by or normalized_status in _OPEN_LOOP_STATUSES:
        return "open_loop"
    return "concern"


def _kind_ambiguity(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in _KIND_AMBIGUITY_MARKERS)


def _normalize_speaker(speaker: str) -> str:
    if speaker in {"user", "assistant"}:
        return speaker
    return "user"


def _source_turn_ref(
    context: ConversationContext,
    turn_index: int,
    preferred_speaker: str,
) -> TurnRef:
    speaker = _normalize_speaker(preferred_speaker)
    for turn in context.turns:
        if turn.turn_index == turn_index and turn.speaker == speaker:
            return TurnRef(turn_index=turn.turn_index, speaker=turn.speaker)
    for turn in context.turns:
        if turn.turn_index == turn_index:
            return TurnRef(turn_index=turn.turn_index, speaker=turn.speaker)
    return _first_user_turn_ref(context)


def _first_user_turn_ref(context: ConversationContext) -> TurnRef:
    for turn in context.turns:
        if turn.speaker == "user":
            return TurnRef(turn_index=turn.turn_index, speaker=turn.speaker)
    if context.turns:
        turn = context.turns[0]
        return TurnRef(turn_index=turn.turn_index, speaker=turn.speaker)
    raise ValueError("ConversationIR construction requires at least one source turn")
