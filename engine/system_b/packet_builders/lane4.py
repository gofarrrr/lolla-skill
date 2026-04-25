"""Phase 4: Lane 4 (Structural Coverage) packet builder.

Projects ConversationIR into the minimum slice Lane 4 needs:
- All turns (the lane's prompt-builders need full conversation context)
- Original framing text + provenance flag (substring-grounded vs paraphrase)
- Decision situation text + provenance flag
- Live constraints (`UserIssueEvent` with kind="constraint") with status
- Open loops + concerns (`UserIssueEvent` with kind in {"open_loop", "concern"})
  with superseded_by + raised_by speaker

The packet is provenance-aware: each text-bearing field carries a
`provenance_kind` literal so downstream consumers can distinguish
substring-validated content from paraphrase. Today's Phase 4 PoC scope
emits the packet but does NOT yet rewire Lane 4's prompt-builders to
consume it — that's Phase 4b. This PoC proves the projection is
correct and stable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from ..ir import (
    ConversationIR,
    DerivationProvenance,
    SpanProvenance,
    Turn,
    TurnRefProvenance,
    UserIssueEvent,
)


ProvenanceKind = Literal["span", "turn_ref", "derivation"]


@dataclass(frozen=True)
class FrameView:
    """A FrameAnchor projected for lane consumption."""
    text: str
    provenance_kind: ProvenanceKind


@dataclass(frozen=True)
class ConstraintView:
    """A live constraint projected from UserIssueEvent(kind="constraint")."""
    text: str
    status: str
    provenance_kind: ProvenanceKind
    introduced_at_turn: int | None
    kind_ambiguity: bool


@dataclass(frozen=True)
class IssueView:
    """An open_loop or concern projected from UserIssueEvent."""
    text: str
    kind: Literal["open_loop", "concern"]
    status: str
    superseded_by: str | None
    raised_by: Literal["user", "assistant"]
    introduced_at_turn: int | None
    provenance_kind: ProvenanceKind
    kind_ambiguity: bool


@dataclass(frozen=True)
class Lane4Packet:
    """Minimum-viable IR projection for Lane 4 (Structural Coverage).

    Contains only the fields Lane 4 actually reads. Built deterministically
    from `ConversationIR` — no LLM calls, no I/O.
    """
    turns: tuple[Turn, ...]
    original_framing: FrameView | None
    decision_situation: FrameView | None
    constraints: tuple[ConstraintView, ...]
    issues: tuple[IssueView, ...]


def _provenance_kind(provenance) -> ProvenanceKind:
    if isinstance(provenance, SpanProvenance):
        return "span"
    if isinstance(provenance, TurnRefProvenance):
        return "turn_ref"
    if isinstance(provenance, DerivationProvenance):
        return "derivation"
    raise ValueError(f"Unknown provenance type: {type(provenance).__name__}")


def _raised_by_for_issue(issue: UserIssueEvent) -> Literal["user", "assistant"]:
    """Determine speaker from the issue's provenance.

    SpanProvenance carries the speaker on its span_ref directly. TurnRef
    and Derivation carry one or more turn_refs each with a speaker; we
    take the first one's speaker as the canonical raiser. Defaults to
    "user" if no speaker info is available (matches Phase 1 fallback in
    ir_constructor's _normalize_speaker).
    """
    prov = issue.provenance
    if isinstance(prov, SpanProvenance):
        speaker = prov.span_ref.speaker
        return "user" if speaker == "user" else "assistant"
    if isinstance(prov, TurnRefProvenance) and prov.turn_refs:
        speaker = prov.turn_refs[0].speaker
        return "user" if speaker == "user" else "assistant"
    if isinstance(prov, DerivationProvenance) and prov.turn_refs:
        speaker = prov.turn_refs[0].speaker
        return "user" if speaker == "user" else "assistant"
    return "user"


def _frame_view(ir: ConversationIR, frame_pattern: str) -> FrameView | None:
    """Project the FrameAnchor matching `frame_pattern` (or None if absent)."""
    for anchor in ir.frame_anchors:
        if anchor.frame_pattern == frame_pattern:
            return FrameView(
                text=anchor.text,
                provenance_kind=_provenance_kind(anchor.provenance),
            )
    return None


def build_lane4_packet(ir: ConversationIR) -> Lane4Packet:
    """Build a Lane4Packet from a ConversationIR.

    Deterministic projection. Order-preserving: constraints and issues
    appear in the same order they were added to the IR. Speaker is
    derived from each issue's provenance.

    The packet is the minimum slice Lane 4 reads. Lane 1, 2, 3 will get
    their own packet builders (similar shape, possibly different fields).
    """
    constraints: list[ConstraintView] = []
    issues: list[IssueView] = []

    for event in ir.user_issue_events:
        if event.kind == "constraint":
            constraints.append(
                ConstraintView(
                    text=event.text,
                    status=event.status,
                    provenance_kind=_provenance_kind(event.provenance),
                    introduced_at_turn=event.introduced_at_turn,
                    kind_ambiguity=event.kind_ambiguity,
                )
            )
        else:
            # Both open_loop and concern flow into the issues list. Lane 4
            # treats them similarly (both are "things that didn't get
            # resolved"), but the kind field is preserved so consumers can
            # filter if they need to.
            issues.append(
                IssueView(
                    text=event.text,
                    kind=event.kind,  # type: ignore[arg-type]
                    status=event.status,
                    superseded_by=event.superseded_by,
                    raised_by=_raised_by_for_issue(event),
                    introduced_at_turn=event.introduced_at_turn,
                    provenance_kind=_provenance_kind(event.provenance),
                    kind_ambiguity=event.kind_ambiguity,
                )
            )

    return Lane4Packet(
        turns=ir.turns,
        original_framing=_frame_view(ir, "original_framing"),
        decision_situation=_frame_view(ir, "decision_situation"),
        constraints=tuple(constraints),
        issues=tuple(issues),
    )
