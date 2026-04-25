"""Phase 5.5: LLM-backed dropped_threads specialist extraction.

Replaces paraphrased `dropped_threads` extraction with verbatim-grounded
`UserIssueEvent` emission. Every event's `text` is an exact substring of
the named speaker's turn (user OR assistant — dropped threads can be
raised by either party).

Design decisions (locked in by Phase 5.5 annotation gate, 2026-04-24):

- Single-span mode only for v1. All 9 gate items had clean single-turn
  anchors; no derivation needed. The derivation-mode code path remains
  available in `live_constraints_extraction` for future specialists.
- Dual-speaker SOURCE: both user AND assistant turns are quotable here
  (live_constraints is user-only; dropped_threads accepts both).
- Default `kind = "open_loop"`. `kind_ambiguity=True` flag for threads
  that read as live concern despite status=acknowledged_then_dropped.
- `superseded_by` is a paraphrase label passthrough — NOT substring-
  validated. It is the "what replaced this thread" summary.
- Paraphrase expansion is explicitly forbidden in the prompt. The gate
  surfaced two monolith cases where the paraphrase added content
  ($950K push, "(pricing, positioning, website, legal structure)")
  absent from the source turn.
- Validation is substring-exact (case-tolerant via
  `find_substring_tolerant`). Paraphrase/hallucination fails and is
  dropped + counted.
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from .boundary_validation import coerce_str, require_list_of_dicts
from .conversation_context import ConversationContext
from .ir import SpanProvenance, SpanRef, UserIssueEvent
from .text_matching import find_substring_tolerant


_LOGGER = logging.getLogger("system_b.dropped_threads_extraction")


VALID_KINDS: tuple[str, ...] = ("open_loop", "concern")
VALID_SPEAKERS: tuple[str, ...] = ("user", "assistant")


DROPPED_THREADS_SYSTEM_PROMPT = """You are identifying DROPPED THREADS in a decision-support conversation.

A DROPPED THREAD is a SUBSTANTIVE TOPIC raised by one party that the conversation then walked away from — the stakes, framing, or question it carried didn't get directly addressed; the conversation pivoted somewhere else.

The key test: **would a thoughtful reader looking back think "they raised X but never really dealt with X — they dealt with Y instead"?**

A thread is about CONTENT (stakes, framing, arguments, options, concerns), not conversation structure (clarifying questions, transitions, summaries).

INCLUDE as a dropped thread:
- user raises emotional stakes/fears ("she's going to be homeless", "I love DC", "I've been feeling stuck") and the assistant redirects to a practical path without staying with the emotion
- user makes an argument or presents logic (EV math, a spouse's position) and the assistant reframes the decision, not engaging the argument on its own terms
- user flags a specific concern about a downstream consequence ("might implicate her") and the assistant says it's not theirs to solve
- user asks for a specific deliverable ("help me think through the launch plan") and the assistant redirects to fundamentals instead
- assistant flags an option or hypothesis as less viable and the conversation moves on without resolving it (e.g. "pure option 2 isn't viable" — not resolved, just set aside)

EXCLUDE:
- clarifying questions the assistant asked early in the conversation to gather context (these are conversation moves, not threads)
- items in the assistant's final summary/action list (these are next steps, not dropped threads)
- items the user explicitly accepted ("ok", "will do", "got it") — these are resolved
- the assistant's closing reassurance or wrap-up
- the user's questions the assistant answered directly in the next turn
- side details mentioned in passing without real "raise" quality

**Critical pattern to recognize:** the most common dropped threads are user-side emotional or logical content that the assistant acknowledges superficially and then redirects. If you see the user expressing weight ("the stakes here...", "I've been feeling...", "my argument is that...") and then the assistant's response pivots to a different framing or action — that's a dropped thread. The user's raised content is the span.

KIND TAXONOMY (pick one; default to "open_loop"):

- "open_loop" — raised and explicitly dropped, acknowledged-then-dropped, or superseded by a later focus shift. Default for most items.
- "concern" — raised and carrying live weight even though the conversation moved past it. Use when the thread reads as unresolved worry that the speaker is still holding.

If a span genuinely carries both (e.g. "she's going to be homeless with her kids if I don't help" — dropped by assistant redirecting to partial-help strategy BUT the stakes themselves remain live for the user), set the PRIMARY kind and mark `kind_ambiguity: true`. Primary = the dominant reading.

CRITICAL EVIDENCE RULE:

- Every `text` you return MUST be a LITERAL contiguous substring of a single turn, character-for-character.
- Do NOT paraphrase, summarize, or combine across turns.
- Do NOT expand content: if the user says "launch plan" you may NOT expand it to "(pricing, positioning, website, legal structure)". If the user says "$45K" you may NOT substitute "$950K". Emit only what the source turn literally says.
- The `turn_index` and `speaker` fields together identify the source turn.
- Quotes that are not literal substrings will be rejected downstream.

The `superseded_by` field is different: it is a short paraphrase label describing what the conversation shifted to INSTEAD of resolving this thread. It is NOT substring-validated, but keep it to 10-20 words of factual description — no invented specifics.

Respond with ONLY valid JSON of this shape:

```json
{
  "dropped_threads": [
    {
      "text": "exact verbatim substring from the named turn",
      "turn_index": 3,
      "speaker": "user",
      "kind": "open_loop",
      "kind_ambiguity": false,
      "superseded_by": "short paraphrase label of what the conversation shifted to"
    }
  ]
}
```

If no dropped threads are present, return `{"dropped_threads": []}`. Dropped threads are sparser than live constraints: 0-3 per conversation is typical."""


def _format_user_prompt(context: ConversationContext) -> str:
    """Build CONTEXT/SOURCE-shaped user prompt. SOURCE contains BOTH user
    and assistant turns, each labeled by speaker, because dropped threads
    can be raised by either party."""
    parts: list[str] = []
    ext = context.extraction
    parts.append("CONTEXT (background for understanding the decision — NOT quotable):")
    if ext.decision_situation:
        parts.append(f"- Decision situation: {ext.decision_situation}")
    if ext.original_framing:
        parts.append(f"- Original framing: {ext.original_framing}")
    parts.append("")
    parts.append(
        "SOURCE (user AND assistant turns — dropped threads can be raised by either; "
        "every `text` MUST be a literal substring of the claimed turn, and `speaker` "
        "must match):"
    )
    for t in context.turns:
        label = "USER" if t.speaker == "user" else "ASSISTANT"
        parts.append(f"[Turn {t.turn_index}] {label}:")
        parts.append(t.text)
        parts.append("")
    parts.append(
        "Identify the dropped threads in SOURCE. Every text must be a "
        "verbatim substring from the claimed speaker's turn. Respond with JSON only."
    )
    return "\n".join(parts)


@runtime_checkable
class _BoundaryClient(Protocol):
    def run_json(self, system_prompt: str, user_prompt: str) -> dict[str, object]: ...


@dataclass(frozen=True)
class _ValidationStats:
    """Observability counters for dropped_threads validation."""
    raw_count: int
    validated_count: int
    user_raised_count: int
    assistant_raised_count: int
    dropped_invalid_kind: int
    dropped_invalid_speaker: int
    dropped_invalid_turn: int
    dropped_not_substring: int
    dropped_speaker_mismatch: int


def _turn_map(context: ConversationContext) -> dict[tuple[int, str], str]:
    """Map (turn_index, speaker) → turn text for all turns."""
    return {(t.turn_index, t.speaker): t.text for t in context.turns}


def _hash12(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:12]


def _issue_id(turn_index: int, speaker: str, matched: str) -> str:
    return f"dropped_thread_t{turn_index}_{speaker}_{_hash12(matched)}"


def extract_dropped_threads(
    *,
    context: ConversationContext,
    boundary: _BoundaryClient,
) -> tuple[list[UserIssueEvent], _ValidationStats]:
    """Run the dropped_threads specialist LLM call, validate output,
    return typed UserIssueEvent objects plus validation stats.

    Each returned event has:
      - exact substring `text` from the named turn
      - `speaker` in {user, assistant}
      - `kind` in {open_loop, concern}, default open_loop
      - `status = "acknowledged_then_dropped"` (default; the only value
        produced by monolith extraction across the 10-case corpus)
      - `superseded_by` = LLM's paraphrase label (not substring-validated)
      - `provenance = SpanProvenance(span_ref=...)` with exact char offsets
      - `kind_ambiguity` from the LLM

    Invalid entries (bad kind, bad speaker, bad turn, non-substring text,
    speaker-turn mismatch) are silently dropped; counts surface via the
    stats object and the INFO log.
    """
    raw_payload = boundary.run_json(
        DROPPED_THREADS_SYSTEM_PROMPT,
        _format_user_prompt(context),
    )
    raw_items = require_list_of_dicts(raw_payload, "dropped_threads", "dropped_threads_extraction")
    turn_map = _turn_map(context)

    validated: list[UserIssueEvent] = []
    user_raised_count = 0
    assistant_raised_count = 0
    dropped_invalid_kind = 0
    dropped_invalid_speaker = 0
    dropped_invalid_turn = 0
    dropped_not_substring = 0
    dropped_speaker_mismatch = 0

    for item in raw_items:
        kind = coerce_str(item.get("kind")).strip().lower() or "open_loop"
        speaker = coerce_str(item.get("speaker")).strip().lower()
        text = coerce_str(item.get("text")).strip()
        superseded_by = coerce_str(item.get("superseded_by")).strip() or None
        kind_ambiguity = bool(item.get("kind_ambiguity", False))
        turn_val = item.get("turn_index")
        try:
            turn_index = int(turn_val) if turn_val is not None else -1
        except (TypeError, ValueError):
            turn_index = -1

        if kind not in VALID_KINDS:
            dropped_invalid_kind += 1
            continue
        if speaker not in VALID_SPEAKERS:
            dropped_invalid_speaker += 1
            continue

        turn_text = turn_map.get((turn_index, speaker))
        if turn_text is None:
            # Either the turn_index doesn't exist at all, or it exists for
            # a different speaker. Distinguish for observability.
            any_turn = any(ti == turn_index for (ti, _) in turn_map)
            if any_turn:
                dropped_speaker_mismatch += 1
            else:
                dropped_invalid_turn += 1
            continue

        if not text:
            dropped_not_substring += 1
            continue

        matched = find_substring_tolerant(text, turn_text)
        if matched is None:
            dropped_not_substring += 1
            continue

        start_char = turn_text.find(matched)
        if start_char == -1:
            start_char = turn_text.lower().find(matched.lower())
        if start_char == -1:
            dropped_not_substring += 1
            continue

        span_ref = SpanRef(
            turn_index=turn_index,
            speaker=speaker,
            start_char=start_char,
            end_char=start_char + len(matched),
        )
        validated.append(
            UserIssueEvent(
                issue_id=_issue_id(turn_index, speaker, matched),
                text=matched,
                kind=kind,
                status="acknowledged_then_dropped",
                provenance=SpanProvenance(span_ref=span_ref),
                introduced_at_turn=turn_index,
                superseded_by=superseded_by,
                kind_ambiguity=kind_ambiguity,
            )
        )
        if speaker == "user":
            user_raised_count += 1
        else:
            assistant_raised_count += 1

    stats = _ValidationStats(
        raw_count=len(raw_items),
        validated_count=len(validated),
        user_raised_count=user_raised_count,
        assistant_raised_count=assistant_raised_count,
        dropped_invalid_kind=dropped_invalid_kind,
        dropped_invalid_speaker=dropped_invalid_speaker,
        dropped_invalid_turn=dropped_invalid_turn,
        dropped_not_substring=dropped_not_substring,
        dropped_speaker_mismatch=dropped_speaker_mismatch,
    )
    _LOGGER.info(
        "dropped_threads_extraction.completed raw=%d validated=%d "
        "user=%d assistant=%d dropped_kind=%d dropped_speaker=%d "
        "dropped_turn=%d dropped_substring=%d dropped_mismatch=%d",
        stats.raw_count, stats.validated_count,
        stats.user_raised_count, stats.assistant_raised_count,
        stats.dropped_invalid_kind, stats.dropped_invalid_speaker,
        stats.dropped_invalid_turn, stats.dropped_not_substring,
        stats.dropped_speaker_mismatch,
    )
    return validated, stats
