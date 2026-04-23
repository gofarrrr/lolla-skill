"""Loader: on-disk artifacts → ConversationContext.

Reads the extraction JSON + conversation .txt produced by
`scripts/run_extract.py` and the Step 1 capture, and constructs the Phase 1
conversation-first input shape.

Kept intentionally tolerant:
- Missing/empty extraction (e.g. capture_critical) → empty ExtractionPayload;
  downstream checks `capture_health` to decide whether to short-circuit.
- `_quote_validation` (JSON-side underscore marker) → `quote_validation`
  (Python-side dataclass field). Single place that knows the boundary.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from engine.system_b.conversation_context import (
    ConversationContext,
    DroppedThread,
    ExtractionPayload,
    LiveConstraint,
    Turn,
)


_TURN_MARKER = re.compile(r"^\[Turn (\d+)\] (USER|ASSISTANT):\s*$")


def load_conversation_context(
    extraction_path: str | Path,
    conversation_path: str | Path,
) -> ConversationContext:
    raw = json.loads(Path(extraction_path).read_text())
    conversation_text = Path(conversation_path).read_text()

    return ConversationContext(
        turns=_parse_turns(conversation_text),
        extraction=_build_extraction_payload(raw.get("extraction") or {}),
        capture_manifest=raw.get("capture_manifest") or {},
        capture_health=raw.get("capture_health") or "unknown",
        capture_warnings=tuple(raw.get("capture_warnings") or ()),
    )


def _parse_turns(text: str) -> tuple[Turn, ...]:
    turns: list[Turn] = []
    current_index: int | None = None
    current_speaker: str | None = None
    current_buffer: list[str] = []

    for line in text.splitlines():
        marker = _TURN_MARKER.match(line)
        if marker:
            if current_index is not None and current_speaker is not None:
                turns.append(
                    Turn(
                        turn_index=current_index,
                        speaker=current_speaker,
                        text="\n".join(current_buffer).strip(),
                    )
                )
            current_index = int(marker.group(1))
            current_speaker = marker.group(2).lower()
            current_buffer = []
        elif current_index is not None:
            current_buffer.append(line)

    if current_index is not None and current_speaker is not None:
        turns.append(
            Turn(
                turn_index=current_index,
                speaker=current_speaker,
                text="\n".join(current_buffer).strip(),
            )
        )

    return tuple(turns)


def _build_extraction_payload(raw: dict[str, Any]) -> ExtractionPayload:
    if not raw:
        return ExtractionPayload(
            decision_situation="",
            live_constraints=(),
            synthesized_position="",
            reasoning_passages=(),
            original_framing="",
            dropped_threads=(),
        )

    live_constraints = tuple(
        LiveConstraint(
            constraint=c.get("constraint", ""),
            introduced_turn=int(c.get("introduced_turn", 0)),
            status=c.get("status", ""),
            weight=c.get("weight", ""),
            canonical_key=c.get("canonical_key"),
        )
        for c in (raw.get("live_constraints") or ())
    )

    dropped_threads = tuple(
        DroppedThread(
            thread=t.get("thread", ""),
            raised_by=t.get("raised_by", ""),
            raised_turn=int(t.get("raised_turn", 0)),
            status=t.get("status", ""),
            superseded_by=t.get("superseded_by"),
        )
        for t in (raw.get("dropped_threads") or ())
    )

    return ExtractionPayload(
        decision_situation=raw.get("decision_situation", ""),
        live_constraints=live_constraints,
        synthesized_position=raw.get("synthesized_position", ""),
        reasoning_passages=tuple(raw.get("reasoning_passages") or ()),
        original_framing=raw.get("original_framing", ""),
        dropped_threads=dropped_threads,
        quote_validation=raw.get("_quote_validation") or {},
    )
