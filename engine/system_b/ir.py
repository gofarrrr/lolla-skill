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
    kind: Literal["span"] = "span"
    span_ref: SpanRef | None = None

    def __post_init__(self) -> None:
        if self.kind != "span":
            raise ValueError("SpanProvenance.kind must be 'span'")
        if self.span_ref is None:
            raise ValueError("SpanProvenance requires span_ref")

    def to_dict(self) -> dict[str, Any]:
        return {"kind": self.kind, "span_ref": self.span_ref.to_dict()}


@dataclass(frozen=True)
class ConversationIR:
    turns: tuple[Turn, ...] = ()

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
