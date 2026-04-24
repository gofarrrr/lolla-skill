"""Provenance-bearing Conversation IR.

Phase 1 keeps this layer observational: it records typed objects and their
source provenance without changing lane prompts, routing, or extraction.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


Speaker = Literal["user", "assistant"]
ProvenanceKind = Literal["span", "turn_ref", "derivation"]

_VALID_SPEAKERS = ("user", "assistant")


@dataclass(frozen=True)
class Turn:
    """A semantic conversation turn, using turn-relative text offsets."""

    turn_index: int
    speaker: Speaker
    text: str

    def __post_init__(self) -> None:
        if self.speaker not in _VALID_SPEAKERS:
            raise ValueError(
                f"Turn.speaker must be one of {_VALID_SPEAKERS}; got {self.speaker!r}"
            )
        if self.turn_index < 1:
            raise ValueError(
                f"Turn.turn_index must be >= 1 (1-indexed); got {self.turn_index}"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "turn_index": self.turn_index,
            "speaker": self.speaker,
            "text": self.text,
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Turn":
        return cls(
            turn_index=int(raw["turn_index"]),
            speaker=raw["speaker"],
            text=raw["text"],
        )


@dataclass(frozen=True)
class TurnRef:
    turn_index: int
    speaker: Speaker

    def __post_init__(self) -> None:
        if self.speaker not in _VALID_SPEAKERS:
            raise ValueError(
                f"TurnRef.speaker must be one of {_VALID_SPEAKERS}; got {self.speaker!r}"
            )
        if self.turn_index < 1:
            raise ValueError(
                f"TurnRef.turn_index must be >= 1 (1-indexed); got {self.turn_index}"
            )

    def to_dict(self) -> dict[str, Any]:
        return {"turn_index": self.turn_index, "speaker": self.speaker}

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "TurnRef":
        return cls(turn_index=int(raw["turn_index"]), speaker=raw["speaker"])


@dataclass(frozen=True)
class SpanRef:
    """Exact substring reference in a single semantic turn.

    Offsets are end-exclusive and relative to `Turn.text`, not to the
    conversation file containing `[Turn N] USER:` markers.
    """

    turn_index: int
    speaker: Speaker
    start_char: int
    end_char: int

    def __post_init__(self) -> None:
        if self.speaker not in _VALID_SPEAKERS:
            raise ValueError(
                f"SpanRef.speaker must be one of {_VALID_SPEAKERS}; got {self.speaker!r}"
            )
        if self.turn_index < 1:
            raise ValueError(
                f"SpanRef.turn_index must be >= 1 (1-indexed); got {self.turn_index}"
            )
        if self.start_char < 0:
            raise ValueError("SpanRef.start_char must be >= 0")
        if self.end_char < self.start_char:
            raise ValueError("SpanRef.end_char must be >= start_char")

    def to_turn_ref(self) -> TurnRef:
        return TurnRef(turn_index=self.turn_index, speaker=self.speaker)

    def to_dict(self) -> dict[str, Any]:
        return {
            "turn_index": self.turn_index,
            "speaker": self.speaker,
            "start_char": self.start_char,
            "end_char": self.end_char,
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "SpanRef":
        return cls(
            turn_index=int(raw["turn_index"]),
            speaker=raw["speaker"],
            start_char=int(raw["start_char"]),
            end_char=int(raw["end_char"]),
        )


@dataclass(frozen=True)
class SpanProvenance:
    span_ref: SpanRef
    kind: Literal["span"] = "span"

    def __post_init__(self) -> None:
        if self.kind != "span":
            raise ValueError("SpanProvenance.kind must be 'span'")

    def to_dict(self) -> dict[str, Any]:
        return {"kind": self.kind, "span_ref": self.span_ref.to_dict()}

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "SpanProvenance":
        return cls(span_ref=SpanRef.from_dict(raw["span_ref"]))


@dataclass(frozen=True)
class TurnRefProvenance:
    turn_refs: tuple[TurnRef, ...]
    note: str = ""
    kind: Literal["turn_ref"] = "turn_ref"

    def __post_init__(self) -> None:
        if self.kind != "turn_ref":
            raise ValueError("TurnRefProvenance.kind must be 'turn_ref'")
        if not self.turn_refs:
            raise ValueError("TurnRefProvenance requires at least one turn_ref")

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "kind": self.kind,
            "turn_refs": [turn_ref.to_dict() for turn_ref in self.turn_refs],
        }
        if self.note:
            payload["note"] = self.note
        return payload

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "TurnRefProvenance":
        return cls(
            turn_refs=tuple(TurnRef.from_dict(r) for r in raw["turn_refs"]),
            note=raw.get("note", ""),
        )


@dataclass(frozen=True)
class DerivationProvenance:
    turn_refs: tuple[TurnRef, ...] = ()
    source_object_ids: tuple[str, ...] = ()
    note: str = ""
    kind: Literal["derivation"] = "derivation"

    def __post_init__(self) -> None:
        if self.kind != "derivation":
            raise ValueError("DerivationProvenance.kind must be 'derivation'")
        if not self.turn_refs and not self.source_object_ids:
            raise ValueError(
                "DerivationProvenance requires turn_refs or source_object_ids"
            )

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "kind": self.kind,
            "turn_refs": [turn_ref.to_dict() for turn_ref in self.turn_refs],
            "source_object_ids": list(self.source_object_ids),
        }
        if self.note:
            payload["note"] = self.note
        return payload

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "DerivationProvenance":
        return cls(
            turn_refs=tuple(TurnRef.from_dict(r) for r in raw.get("turn_refs", ())),
            source_object_ids=tuple(raw.get("source_object_ids", ())),
            note=raw.get("note", ""),
        )


Provenance = SpanProvenance | TurnRefProvenance | DerivationProvenance


def provenance_from_dict(raw: dict[str, Any]) -> Provenance:
    kind = raw.get("kind")
    if kind == "span":
        return SpanProvenance.from_dict(raw)
    if kind == "turn_ref":
        return TurnRefProvenance.from_dict(raw)
    if kind == "derivation":
        return DerivationProvenance.from_dict(raw)
    raise ValueError(f"Unknown provenance kind: {kind!r}")


@dataclass(frozen=True)
class FrameAnchor:
    anchor_id: str
    text: str
    provenance: Provenance
    frame_pattern: str = ""
    element_type: str = ""
    fragility_signal: str = ""
    inquiry_stage: str = ""
    likely_default: str = ""

    def __post_init__(self) -> None:
        if self.provenance is None:
            raise ValueError("FrameAnchor.provenance is required")

    def to_dict(self) -> dict[str, Any]:
        return {
            "anchor_id": self.anchor_id,
            "text": self.text,
            "provenance": self.provenance.to_dict(),
            "frame_pattern": self.frame_pattern,
            "element_type": self.element_type,
            "fragility_signal": self.fragility_signal,
            "inquiry_stage": self.inquiry_stage,
            "likely_default": self.likely_default,
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "FrameAnchor":
        return cls(
            anchor_id=raw["anchor_id"],
            text=raw["text"],
            provenance=provenance_from_dict(raw["provenance"]),
            frame_pattern=raw.get("frame_pattern", ""),
            element_type=raw.get("element_type", ""),
            fragility_signal=raw.get("fragility_signal", ""),
            inquiry_stage=raw.get("inquiry_stage", ""),
            likely_default=raw.get("likely_default", ""),
        )


UserIssueKind = Literal["constraint", "concern", "open_loop"]


@dataclass(frozen=True)
class UserIssueEvent:
    issue_id: str
    text: str
    kind: UserIssueKind
    status: str
    provenance: Provenance
    introduced_at_turn: int | None = None
    resolved_at_turn: int | None = None
    superseded_by: str | None = None
    kind_ambiguity: bool = False

    def __post_init__(self) -> None:
        valid_kinds = ("constraint", "concern", "open_loop")
        if self.kind not in valid_kinds:
            raise ValueError(
                f"UserIssueEvent.kind must be one of {valid_kinds}; got {self.kind!r}"
            )
        if self.provenance is None:
            raise ValueError("UserIssueEvent.provenance is required")

    def to_dict(self) -> dict[str, Any]:
        return {
            "issue_id": self.issue_id,
            "text": self.text,
            "kind": self.kind,
            "status": self.status,
            "provenance": self.provenance.to_dict(),
            "introduced_at_turn": self.introduced_at_turn,
            "resolved_at_turn": self.resolved_at_turn,
            "superseded_by": self.superseded_by,
            "kind_ambiguity": self.kind_ambiguity,
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "UserIssueEvent":
        return cls(
            issue_id=raw["issue_id"],
            text=raw["text"],
            kind=raw["kind"],
            status=raw["status"],
            provenance=provenance_from_dict(raw["provenance"]),
            introduced_at_turn=raw.get("introduced_at_turn"),
            resolved_at_turn=raw.get("resolved_at_turn"),
            superseded_by=raw.get("superseded_by"),
            kind_ambiguity=bool(raw.get("kind_ambiguity", False)),
        )


@dataclass(frozen=True)
class StanceEvent:
    stance_id: str
    speaker: Speaker
    stance: str
    text: str
    provenance: Provenance
    turn_index: int | None = None

    def __post_init__(self) -> None:
        if self.speaker not in _VALID_SPEAKERS:
            raise ValueError(
                f"StanceEvent.speaker must be one of {_VALID_SPEAKERS}; got {self.speaker!r}"
            )
        if self.provenance is None:
            raise ValueError("StanceEvent.provenance is required")

    def to_dict(self) -> dict[str, Any]:
        return {
            "stance_id": self.stance_id,
            "speaker": self.speaker,
            "stance": self.stance,
            "text": self.text,
            "provenance": self.provenance.to_dict(),
            "turn_index": self.turn_index,
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "StanceEvent":
        return cls(
            stance_id=raw["stance_id"],
            speaker=raw["speaker"],
            stance=raw["stance"],
            text=raw["text"],
            provenance=provenance_from_dict(raw["provenance"]),
            turn_index=raw.get("turn_index"),
        )


@dataclass(frozen=True)
class ConversationIR:
    turns: tuple[Turn, ...] = ()
    spans: tuple[SpanRef, ...] = ()
    frame_anchors: tuple[FrameAnchor, ...] = ()
    user_issue_events: tuple[UserIssueEvent, ...] = ()
    stance_events: tuple[StanceEvent, ...] = ()

    def turn_map(self) -> dict[tuple[int, Speaker], Turn]:
        return {(turn.turn_index, turn.speaker): turn for turn in self.turns}

    def resolve_span(self, span_ref: SpanRef) -> str:
        turn = self.turn_map().get((span_ref.turn_index, span_ref.speaker))
        if turn is None:
            raise ValueError(
                "SpanRef points to missing turn "
                f"{span_ref.turn_index}/{span_ref.speaker}"
            )
        if span_ref.end_char > len(turn.text):
            raise ValueError(
                "SpanRef outside turn text: "
                f"end_char={span_ref.end_char}, turn_len={len(turn.text)}"
            )
        return turn.text[span_ref.start_char:span_ref.end_char]

    def provenance_tier_counts(self) -> dict[ProvenanceKind, int]:
        counts: dict[ProvenanceKind, int] = {
            "span": 0,
            "turn_ref": 0,
            "derivation": 0,
        }
        for obj in (
            *self.frame_anchors,
            *self.user_issue_events,
            *self.stance_events,
        ):
            counts[obj.provenance.kind] += 1
        return counts

    def to_dict(self) -> dict[str, Any]:
        return {
            "turns": [turn.to_dict() for turn in self.turns],
            "spans": [span.to_dict() for span in self.spans],
            "frame_anchors": [anchor.to_dict() for anchor in self.frame_anchors],
            "user_issue_events": [
                issue.to_dict() for issue in self.user_issue_events
            ],
            "stance_events": [stance.to_dict() for stance in self.stance_events],
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "ConversationIR":
        return cls(
            turns=tuple(Turn.from_dict(t) for t in raw.get("turns", ())),
            spans=tuple(SpanRef.from_dict(s) for s in raw.get("spans", ())),
            frame_anchors=tuple(
                FrameAnchor.from_dict(a) for a in raw.get("frame_anchors", ())
            ),
            user_issue_events=tuple(
                UserIssueEvent.from_dict(i)
                for i in raw.get("user_issue_events", ())
            ),
            stance_events=tuple(
                StanceEvent.from_dict(s) for s in raw.get("stance_events", ())
            ),
        )
