"""Phase 3b: LLM-backed assistant stance extraction.

Populates `StanceEvent` objects in the IR by asking a bounded LLM call
to identify spans in the assistant's turns that represent stance moves
(recommendations, qualifications, conditions, deferrals, reframings,
or initial stances), each anchored to a verbatim substring.

Design decisions (from Phase 3.0 annotation gate, 2026-04-24):

- Six-relation taxonomy: `commitment`, `revision`, `qualification`,
  `condition`, `deferral`, `initial`. Each carried 95%+ relation
  agreement between two independent reviewers on 20 real candidates.
- Composite stance spans (two relations simultaneously) get the primary
  relation stored in `stance` and `relation_ambiguity=True`.
- Every emitted stance must be an exact substring of an assistant turn
  (case-tolerant via `find_substring_tolerant`). Paraphrase/hallucination
  fails validation and is dropped.
- Separate from `scripts/run_extract.py` — this is a dedicated LLM call,
  not an addition to the monolithic extraction prompt. Keeps the
  saturation firewall intact.

Not included in Phase 3b:

- `ReasoningSegment` / `ClaimSpan` / `Caveat` / `ReversalCondition`
  (deferred per roadmap; promote only if evidence accumulates).
- User-side stance extraction (PR #23 `StanceEvent.speaker` supports
  both, but v1 assistant-only).
- Measurement on the 10-case corpus — that's an evaluation pass, not
  part of the feature code.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from .boundary_validation import coerce_str, require_list_of_dicts
from .conversation_context import ConversationContext
from .ir import SpanProvenance, SpanRef, StanceEvent
from .text_matching import find_substring_tolerant


_LOGGER = logging.getLogger("system_b.stance_extraction")


VALID_RELATIONS: tuple[str, ...] = (
    "commitment",
    "revision",
    "qualification",
    "condition",
    "deferral",
    "initial",
)


STANCE_EXTRACTION_SYSTEM_PROMPT = """You are identifying assistant stance events in a decision-support conversation.

A STANCE EVENT is a span from an assistant turn that records a meaningful position in the assistant's reasoning trajectory — not generic explanation, empathy, or background.

INCLUDE as a stance event:
- a concrete recommendation or commitment (what the user should do)
- a material qualification or boundary on earlier advice
- an if/then decision criterion
- a deferral, parking, or "not now" instruction
- a revision in how the assistant reframes the user's decision

EXCLUDE:
- generic empathy or reassurance
- background explanation with no position change
- examples that merely illustrate an already-recorded stance
- operational details that do not change the stance trajectory

RELATION TAXONOMY (pick ONE per stance, unless genuinely two apply):

- "initial" — first substantive stance on a decision axis (rare in mid-conversation).
- "revision" — material shift from an earlier stance or from the user's framing.
- "qualification" — caveat, boundary, or limiting condition on an existing stance.
- "commitment" — direct recommendation, directive, or firm conclusion.
- "condition" — if/then gate, test, or criterion for deciding.
- "deferral" — explicitly parks an action, topic, or decision for later.

SPECIFIC GUIDANCE ON "revision" (commonly under-detected):

Revision fires when the assistant is pushing back on the user's mental model of the decision — reframing WHAT the decision is really about, not just advising WHAT to do. Watch for these patterns:

- "You don't have X; you have Y" (replacing a concept: "you don't have a pipeline; you have a network that might become a pipeline")
- "It's not actually X" / "it's not really X, it's more like Y" (replacing the decision type: "it's not actually a financial decision")
- "The first move here isn't X. It's Y" (reframing the priority: "the first move isn't to push on the 19-year-old; it's to create a way for her to re-enter the relationship")
- "You're framing this as X, but actually Y" / "from an X standpoint, Y is the more interesting move" (explicit lens shift)

These spans often lack a "recommend" or "you should" verb — the stance is the frame shift itself. Emit them as "revision" even when no directive appears in the same sentence. If the user's framing is wrong in the assistant's read, that correction is a stance event.

If a span genuinely carries two relations (e.g., "call RAINN today, not the police" = commitment + deferral), set the PRIMARY relation in `relation` and mark `relation_ambiguity: true`. Primary = the dominant reading.

CRITICAL EVIDENCE RULE:
- Every `text` you return MUST be a LITERAL contiguous substring of a single assistant turn, character-for-character.
- Do NOT paraphrase, summarize, or combine across turns.
- Do NOT quote from CONTEXT or user turns — stance events are assistant-side only.
- The `turn_index` field identifies which assistant turn the quote comes from.
- Quotes that are not literal substrings will be rejected downstream.

Respond with ONLY valid JSON of this shape:
```json
{
  "stance_events": [
    {
      "text": "exact verbatim substring from an assistant turn",
      "turn_index": 3,
      "relation": "commitment",
      "relation_ambiguity": false
    }
  ]
}
```

If no stance events are present, return `{"stance_events": []}`. Err on the side of fewer but higher-quality events. 3-6 per conversation is typical; more is acceptable only if the conversation is long and the trajectory truly evolves."""


def _format_user_prompt(context: ConversationContext) -> str:
    """Build the CONTEXT/SOURCE-shaped user prompt. Only assistant turns go
    in SOURCE since stance events are assistant-side."""
    parts: list[str] = []
    ext = context.extraction
    parts.append("CONTEXT (background for understanding the decision — NOT quotable):")
    if ext.decision_situation:
        parts.append(f"- Decision situation: {ext.decision_situation}")
    if ext.original_framing:
        parts.append(f"- Original framing: {ext.original_framing}")
    user_turns = [t for t in context.turns if t.speaker == "user"]
    if user_turns:
        parts.append("- User turns (CONTEXT — not quotable; use for understanding what the assistant is responding to):")
        for t in user_turns:
            parts.append(f"  [Turn {t.turn_index}] USER: {t.text}")
    parts.append("")
    parts.append("SOURCE (assistant turns — the only place stance events can come from; `text` MUST be a literal substring of one of these):")
    assistant_turns = [t for t in context.turns if t.speaker == "assistant"]
    if not assistant_turns:
        parts.append("(no assistant turns present)")
    else:
        for t in assistant_turns:
            parts.append(f"[Turn {t.turn_index}] ASSISTANT:")
            parts.append(t.text)
            parts.append("")
    parts.append(
        "Identify the stance events in SOURCE. Every `text` must be a verbatim "
        "substring of an assistant turn. Respond with JSON only."
    )
    return "\n".join(parts)


@runtime_checkable
class _BoundaryClient(Protocol):
    def run_json(self, system_prompt: str, user_prompt: str) -> dict[str, object]: ...


@dataclass(frozen=True)
class _ValidationStats:
    """Observability counters for stance-extraction validation."""
    raw_count: int
    validated_count: int
    dropped_invalid_turn: int
    dropped_invalid_relation: int
    dropped_not_substring: int


def _assistant_turn_map(context: ConversationContext) -> dict[int, str]:
    return {t.turn_index: t.text for t in context.turns if t.speaker == "assistant"}


def extract_stance_events(
    *,
    context: ConversationContext,
    boundary: _BoundaryClient,
) -> tuple[list[StanceEvent], _ValidationStats]:
    """Run the stance-extraction LLM call, validate output, return typed
    StanceEvent objects plus validation stats.

    Each returned StanceEvent has:
      - exact `text` (validated substring of the named assistant turn)
      - `speaker="assistant"`
      - `stance` = the primary relation
      - `relation_ambiguity` = LLM's composite-relation flag
      - `provenance` = SpanProvenance with a computed SpanRef at the
        exact character position where the quote appears in the turn

    Invalid entries (bad turn_index, bad relation, or non-substring text)
    are silently dropped; counts surface via the stats object and the
    INFO log. The stance_id is deterministic based on (turn_index,
    relation, quote hash) so repeated runs produce stable ids on
    identical input.
    """
    raw_payload = boundary.run_json(
        STANCE_EXTRACTION_SYSTEM_PROMPT,
        _format_user_prompt(context),
    )
    raw_items = require_list_of_dicts(raw_payload, "stance_events", "stance_extraction")
    turn_map = _assistant_turn_map(context)

    validated: list[StanceEvent] = []
    dropped_invalid_turn = 0
    dropped_invalid_relation = 0
    dropped_not_substring = 0

    for idx, item in enumerate(raw_items):
        text = coerce_str(item.get("text")).strip()
        relation = coerce_str(item.get("relation")).strip().lower()
        turn_val = item.get("turn_index")
        try:
            turn_index = int(turn_val) if turn_val is not None else -1
        except (TypeError, ValueError):
            turn_index = -1
        relation_ambiguity = bool(item.get("relation_ambiguity", False))

        turn_text = turn_map.get(turn_index)
        if turn_text is None:
            dropped_invalid_turn += 1
            continue
        if relation not in VALID_RELATIONS:
            dropped_invalid_relation += 1
            continue
        if not text:
            dropped_not_substring += 1
            continue

        matched = find_substring_tolerant(text, turn_text)
        if matched is None:
            dropped_not_substring += 1
            continue

        # Compute the exact span position using the matched (transcript-cased)
        # substring. This preserves the transcript's original casing if the LLM
        # case-folded the first character.
        start_char = turn_text.find(matched)
        if start_char == -1:
            # Fallback for case-insensitive match where .find missed due to case
            start_char = turn_text.lower().find(matched.lower())
        if start_char == -1:
            dropped_not_substring += 1
            continue

        span_ref = SpanRef(
            turn_index=turn_index,
            speaker="assistant",
            start_char=start_char,
            end_char=start_char + len(matched),
        )
        stance_id = f"stance_t{turn_index}_{relation}_{idx:02d}"
        validated.append(
            StanceEvent(
                stance_id=stance_id,
                speaker="assistant",
                stance=relation,
                text=matched,
                provenance=SpanProvenance(span_ref=span_ref),
                turn_index=turn_index,
                relation_ambiguity=relation_ambiguity,
            )
        )

    stats = _ValidationStats(
        raw_count=len(raw_items),
        validated_count=len(validated),
        dropped_invalid_turn=dropped_invalid_turn,
        dropped_invalid_relation=dropped_invalid_relation,
        dropped_not_substring=dropped_not_substring,
    )
    _LOGGER.info(
        "stance_extraction.completed raw=%d validated=%d "
        "dropped_turn=%d dropped_relation=%d dropped_substring=%d",
        stats.raw_count, stats.validated_count,
        stats.dropped_invalid_turn, stats.dropped_invalid_relation,
        stats.dropped_not_substring,
    )
    return validated, stats
