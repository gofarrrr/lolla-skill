"""Reducer-style builders for the Conversation IR.

These helpers keep IR construction explicit and replayable: each update takes
an existing immutable IR and returns a new one.
"""

from __future__ import annotations

from dataclasses import replace

from .ir import (
    ConversationIR,
    FrameAnchor,
    SpanRef,
    StanceEvent,
    Turn,
    UserIssueEvent,
)


def add_turn(ir: ConversationIR, turn: Turn) -> ConversationIR:
    return replace(ir, turns=(*ir.turns, turn))


def add_span(ir: ConversationIR, span_ref: SpanRef) -> ConversationIR:
    ir.resolve_span(span_ref)
    return replace(ir, spans=(*ir.spans, span_ref))


def add_frame_anchor(ir: ConversationIR, anchor: FrameAnchor) -> ConversationIR:
    return replace(ir, frame_anchors=(*ir.frame_anchors, anchor))


def add_user_issue_event(
    ir: ConversationIR,
    issue: UserIssueEvent,
) -> ConversationIR:
    return replace(ir, user_issue_events=(*ir.user_issue_events, issue))


def supersede_issue(
    ir: ConversationIR,
    *,
    issue_id: str,
    superseded_by: str,
    resolved_at_turn: int | None = None,
) -> ConversationIR:
    found = False
    issues: list[UserIssueEvent] = []
    for issue in ir.user_issue_events:
        if issue.issue_id != issue_id:
            issues.append(issue)
            continue
        found = True
        issues.append(
            replace(
                issue,
                status="superseded",
                superseded_by=superseded_by,
                resolved_at_turn=resolved_at_turn,
            )
        )
    if not found:
        raise ValueError(f"Unknown UserIssueEvent issue_id: {issue_id}")
    return replace(ir, user_issue_events=tuple(issues))


def add_stance_event(ir: ConversationIR, stance: StanceEvent) -> ConversationIR:
    return replace(ir, stance_events=(*ir.stance_events, stance))
