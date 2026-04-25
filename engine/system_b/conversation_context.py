"""Conversation-first lane-input contract.

Phase 1 data model. The runtime now treats ``ConversationContext`` as the
pipeline's only entry shape.

Shape rationale:
- `Turn`, `LiveConstraint`, `DroppedThread`, `ExtractionPayload`,
  `ConversationContext` are frozen dataclasses — immutable, hashable-friendly,
  safe to share between threads in the parallel Pass 1/Pass 2 execution.
- Lists become `tuple` at the boundary to preserve immutability.
- `quote_validation` and `capture_manifest` stay as `dict` passthroughs:
  observability metadata whose shape can evolve with extraction without
  forcing ripple updates here.
- `LiveConstraint.canonical_key` is optional. The PR #13 prompt rules no
  longer emit it, but historical extraction artifacts still contain it and
  Track A may reintroduce it. Stay tolerant of both.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


_VALID_SPEAKERS = ("user", "assistant")


@dataclass(frozen=True)
class Turn:
    turn_index: int
    speaker: str
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


@dataclass(frozen=True)
class LiveConstraint:
    constraint: str
    introduced_turn: int
    status: str
    weight: str
    canonical_key: str | None = None


@dataclass(frozen=True)
class DroppedThread:
    thread: str
    raised_by: str
    raised_turn: int
    status: str
    superseded_by: str | None = None


@dataclass(frozen=True)
class ExtractionPayload:
    decision_situation: str
    live_constraints: tuple[LiveConstraint, ...]
    synthesized_position: str
    reasoning_passages: tuple[str, ...]
    original_framing: str
    dropped_threads: tuple[DroppedThread, ...]
    quote_validation: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ConversationContext:
    turns: tuple[Turn, ...]
    extraction: ExtractionPayload
    capture_manifest: dict[str, Any] = field(default_factory=dict)
    capture_health: str = "unknown"
    capture_warnings: tuple[str, ...] = ()
