"""Phase 5: LLM-backed user-side live_constraints specialist extraction.

Replaces paraphrased `live_constraints` extraction with verbatim-grounded
`UserIssueEvent` emission. Every span-mode event's `text` is an exact
substring of a single user turn; every derivation-mode event has at
least two `turn_refs` each with a verifiable `span_excerpt`.

Design decisions (locked in by Phase 5.0 annotation gate, 2026-04-24):

- 3-kind taxonomy: `constraint`, `concern`, `open_loop`. Phase 1
  annotation exercise scored 94.1%; gate re-verified 87.5% on spans.
- Two output modes: `span` (single user-turn substring → SpanProvenance)
  or `derivation` (cross-turn synthesis → DerivationProvenance). 25% of
  paraphrased live_constraints in the 5-case gate were cross-turn.
- Single-turn derivation claims auto-downgrade to span mode. Prevents
  the LLM using derivation as a validation bypass.
- `kind_ambiguity: bool` flag on composite cases (constraint+concern
  seam). Primary kind stays single (dominant reading).
- SOURCE = user turns only. Assistant turns go in CONTEXT for decision
  context but are never quotable.
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
from .ir import (
    DerivationComponent,
    DerivationProvenance,
    SpanProvenance,
    SpanRef,
    TurnRef,
    UserIssueEvent,
)
from .semantic_candidate_ledger import SemanticCandidateLedgerRecorder
from .text_matching import find_substring_tolerant


_LOGGER = logging.getLogger("system_b.live_constraints_extraction")


VALID_KINDS: tuple[str, ...] = ("constraint", "concern", "open_loop")


LIVE_CONSTRAINTS_SYSTEM_PROMPT = """You are identifying user-side LIVE CONSTRAINTS in a decision-support conversation.

A LIVE CONSTRAINT is a user-stated fact or situation that the decision must work with — a bounded limit, a deadline, a resource fact, an external dependency, a relational state, a worry the user explicitly carries, or an unresolved issue they raised and left hanging.

INCLUDE as a live constraint:
- a hard deadline or time window (e.g. "I have to pick within 7 days")
- a resource limit (runway, budget, salary, capacity)
- an external fact the user must work with (audit, regulation, another party's stance)
- a relational constraint (co-parent position, spouse alignment, employee commitment)
- a behavioral or situational state that shapes what's possible (daughter shut down, ongoing pattern)
- a worry or stake the user explicitly carries (career risk, family finances)
- an issue the user raised that was dropped or not answered

EXCLUDE:
- the user's opinions or preferences about the options
- the user's decision process ("I've been thinking...", "I want to figure this out")
- generic context that doesn't bound or pressure the decision
- advice or reasoning from the assistant (source is USER turns only)

KIND TAXONOMY (pick ONE per constraint, unless genuinely two apply):

- "constraint" — a bounded external fact/rule the decision must respect. Deadlines, resource limits, stated givens. User treats it as fixed.
- "concern" — a worry, stake, or risk the user carries. Stated with unease, not as a fixed external limit.
- "open_loop" — an issue raised by the user that was not resolved. Dropped threads, acknowledged-then-dropped questions.

If a span genuinely carries two kinds (e.g. "I've been going through her phone for months. I'm not proud of it" = constraint on trust AND concern about ethics), set the PRIMARY kind in `kind` and mark `kind_ambiguity: true`. Primary = the dominant reading.

OUTPUT MODES:

For each live constraint you identify, emit ONE of two modes.

**Mode "span"** — use when the constraint is fully stated in a SINGLE user turn. Prefer this mode whenever possible.

```json
{
  "mode": "span",
  "text": "exact verbatim substring from ONE user turn",
  "turn_index": 3,
  "kind": "constraint",
  "kind_ambiguity": false
}
```

**Mode "derivation"** — use ONLY when the constraint is genuinely synthesized across MULTIPLE user turns (the core fact is stated in turn N, and a substantive qualifier or elaboration is stated in turn N+k, and neither turn alone carries the whole constraint).

```json
{
  "mode": "derivation",
  "text": "short paraphrase label describing the combined multi-turn constraint",
  "turn_refs": [
    {"turn_index": 1, "span_excerpt": "verbatim substring from turn 1 that anchors part of the constraint"},
    {"turn_index": 2, "span_excerpt": "verbatim substring from turn 2 that anchors the other part"}
  ],
  "kind": "constraint",
  "kind_ambiguity": false
}
```

CRITICAL EVIDENCE RULE:

- Span-mode `text` MUST be a literal contiguous substring of ONE user turn, character-for-character.
- Derivation-mode requires at least TWO `turn_refs`; each `span_excerpt` MUST be a literal contiguous substring of its claimed user turn.
- If a constraint can be stated in a single user turn, use span mode. Do NOT use derivation mode to work around a weak single-span match.
- Quotes come from USER turns only — assistant turns appear in CONTEXT for understanding what the user is responding to, but are NEVER quotable.
- The `turn_index` field identifies which user turn the quote comes from.
- Quotes that are not literal substrings will be rejected downstream.

Respond with ONLY valid JSON of this shape:

```json
{
  "live_constraints": [
    { ... one of the two modes above ... }
  ]
}
```

If no live constraints are present, return `{"live_constraints": []}`. Aim for completeness but err on the side of verbatim grounding — one well-anchored constraint beats three paraphrased ones. 3-7 live constraints per conversation is typical."""


def _format_user_prompt(context: ConversationContext) -> str:
    """Build CONTEXT/SOURCE-shaped user prompt. SOURCE = user turns only
    (live_constraints are user-side facts); assistant turns appear in
    CONTEXT for interpretation only."""
    parts: list[str] = []
    ext = context.extraction
    parts.append("CONTEXT (background for understanding the decision — NOT quotable):")
    if ext.decision_situation:
        parts.append(f"- Decision situation: {ext.decision_situation}")
    if ext.original_framing:
        parts.append(f"- Original framing: {ext.original_framing}")
    assistant_turns = [t for t in context.turns if t.speaker == "assistant"]
    if assistant_turns:
        parts.append("- Assistant turns (CONTEXT — not quotable; included so you understand what the user is responding to):")
        for t in assistant_turns:
            parts.append(f"  [Turn {t.turn_index}] ASSISTANT: {t.text}")
    parts.append("")
    parts.append("SOURCE (user turns — the only place live-constraint quotes can come from; every `text` and `span_excerpt` MUST be a literal substring of one of these):")
    user_turns = [t for t in context.turns if t.speaker == "user"]
    if not user_turns:
        parts.append("(no user turns present)")
    else:
        for t in user_turns:
            parts.append(f"[Turn {t.turn_index}] USER:")
            parts.append(t.text)
            parts.append("")
    parts.append(
        "Identify the live constraints in SOURCE. Every quote must be a "
        "verbatim substring of a user turn. Respond with JSON only."
    )
    return "\n".join(parts)


@runtime_checkable
class _BoundaryClient(Protocol):
    def run_json(self, system_prompt: str, user_prompt: str) -> dict[str, object]: ...


@dataclass(frozen=True)
class _ValidationStats:
    """Observability counters for live_constraints validation."""
    raw_count: int
    validated_count: int
    span_mode_count: int
    derivation_mode_count: int
    dropped_invalid_kind: int
    dropped_invalid_turn: int
    dropped_not_substring: int
    dropped_derivation_no_valid_excerpt: int
    incomplete_derivation_count: int
    dropped_invalid_mode: int
    rejected_derivations: tuple[dict[str, object], ...]


def _user_turn_map(context: ConversationContext) -> dict[int, str]:
    return {t.turn_index: t.text for t in context.turns if t.speaker == "user"}


def _hash12(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:12]


def _span_issue_id(turn_index: int, kind: str, matched_text: str) -> str:
    return f"live_constraint_t{turn_index}_{kind}_{_hash12(matched_text)}"


def _derivation_issue_id(
    kind: str,
    label: str,
    entries: tuple[tuple[int, str, int], ...],
) -> str:
    evidence_key = "|".join(
        f"{turn_index}:{start_char}:{matched}"
        for turn_index, matched, start_char in entries
    )
    key = f"{kind}|{label}|{evidence_key}"
    return f"live_constraint_derivation_{_hash12(key)}"


def _derivation_component_id(
    *, turn_index: int, matched: str, start_char: int
) -> str:
    key = f"user|{turn_index}|{start_char}|{start_char + len(matched)}|{matched}"
    return f"derivation_component_t{turn_index}_{_hash12(key)}"


def _locate_span(turn_text: str, excerpt: str) -> tuple[str, int] | None:
    """Return (matched_substring, start_char) or None if excerpt not found.

    Uses find_substring_tolerant for case-folding tolerance; preserves the
    transcript's original casing in the returned substring. Mirrors the
    pattern in stance_extraction.py.
    """
    matched = find_substring_tolerant(excerpt, turn_text)
    if matched is None:
        return None
    start_char = turn_text.find(matched)
    if start_char == -1:
        start_char = turn_text.lower().find(matched.lower())
    if start_char == -1:
        return None
    return matched, start_char


def _emit_span_event(
    *,
    turn_index: int,
    turn_text: str,
    excerpt: str,
    kind: str,
    kind_ambiguity: bool,
) -> UserIssueEvent | None:
    located = _locate_span(turn_text, excerpt)
    if located is None:
        return None
    matched, start_char = located
    span_ref = SpanRef(
        turn_index=turn_index,
        speaker="user",
        start_char=start_char,
        end_char=start_char + len(matched),
    )
    return UserIssueEvent(
        issue_id=_span_issue_id(turn_index, kind, matched),
        text=matched,
        kind=kind,
        status="active",
        provenance=SpanProvenance(span_ref=span_ref),
        introduced_at_turn=turn_index,
        kind_ambiguity=kind_ambiguity,
    )


def extract_live_constraints(
    *,
    context: ConversationContext,
    boundary: _BoundaryClient,
    candidate_recorder: SemanticCandidateLedgerRecorder | None = None,
) -> tuple[list[UserIssueEvent], _ValidationStats]:
    """Run the live_constraints specialist LLM call, validate output,
    return typed UserIssueEvent objects plus validation stats.

    Each returned event has:
      - exact substring `text` (span mode) or combined paraphrase label
        (derivation mode)
      - `kind` in {constraint, concern, open_loop}
      - `kind_ambiguity` from the LLM
      - `provenance` = SpanProvenance (single turn) OR DerivationProvenance
        (2+ turns, each validated)
      - `status = "active"` by default

    Single-turn `derivation`-claimed outputs are downgraded to span mode.
    Invalid entries (bad kind, bad turn, non-substring text) are silently
    dropped; counts surface via the stats object and the INFO log.
    """
    raw_payload = boundary.run_json(
        LIVE_CONSTRAINTS_SYSTEM_PROMPT,
        _format_user_prompt(context),
    )
    raw_items = require_list_of_dicts(raw_payload, "live_constraints", "live_constraints_extraction")
    turn_map = _user_turn_map(context)

    validated: list[UserIssueEvent] = []
    span_mode_count = 0
    derivation_mode_count = 0
    dropped_invalid_kind = 0
    dropped_invalid_turn = 0
    dropped_not_substring = 0
    dropped_derivation_no_valid_excerpt = 0
    incomplete_derivation_count = 0
    dropped_invalid_mode = 0
    rejected_derivations: list[dict[str, object]] = []

    def record(
        proposal_index: int,
        raw: dict[str, object],
        state: str,
        reason: str,
        event: UserIssueEvent | None = None,
    ) -> None:
        if candidate_recorder is not None:
            candidate_recorder.record_candidate(
                reader_role="live_constraints",
                family="live_constraint_events",
                proposal_index=proposal_index,
                raw_proposal=raw,
                mechanical_state=state,
                mechanical_reason=reason,
                event=event,
            )

    for proposal_index, item in enumerate(raw_items):
        mode = coerce_str(item.get("mode")).strip().lower()
        kind = coerce_str(item.get("kind")).strip().lower()
        kind_ambiguity = bool(item.get("kind_ambiguity", False))

        if kind not in VALID_KINDS:
            dropped_invalid_kind += 1
            record(
                proposal_index,
                item,
                "invalid_evidence",
                "candidate_kind_is_invalid",
            )
            continue

        if mode == "span":
            text = coerce_str(item.get("text")).strip()
            turn_val = item.get("turn_index")
            try:
                turn_index = int(turn_val) if turn_val is not None else -1
            except (TypeError, ValueError):
                turn_index = -1

            turn_text = turn_map.get(turn_index)
            if turn_text is None:
                dropped_invalid_turn += 1
                record(
                    proposal_index,
                    item,
                    "not_supported_by_source",
                    "candidate_user_turn_not_found",
                )
                continue
            if not text:
                dropped_not_substring += 1
                record(
                    proposal_index,
                    item,
                    "not_supported_by_source",
                    "candidate_quote_is_missing",
                )
                continue

            event = _emit_span_event(
                turn_index=turn_index,
                turn_text=turn_text,
                excerpt=text,
                kind=kind,
                kind_ambiguity=kind_ambiguity,
            )
            if event is None:
                dropped_not_substring += 1
                record(
                    proposal_index,
                    item,
                    "not_supported_by_source",
                    "candidate_quote_not_found_in_source_turn",
                )
                continue
            validated.append(event)
            span_mode_count += 1
            record(
                proposal_index,
                item,
                "validated",
                "exact_source_and_contract_validation_passed",
                event,
            )

        elif mode == "derivation":
            label = coerce_str(item.get("text")).strip()
            raw_refs = item.get("turn_refs") or []
            if not isinstance(raw_refs, list):
                raw_refs = []

            # Per-ref validation: keep refs where (a) turn_index is a user
            # turn, (b) span_excerpt substring-validates on that turn.
            valid_entries: list[tuple[int, str, int]] = []
            component_rejections: list[str] = []
            for ref_index, ref in enumerate(raw_refs, start=1):
                if not isinstance(ref, dict):
                    component_rejections.append(
                        f"component_{ref_index}:invalid_shape"
                    )
                    continue
                ref_turn_val = ref.get("turn_index")
                try:
                    ref_turn = int(ref_turn_val) if ref_turn_val is not None else -1
                except (TypeError, ValueError):
                    ref_turn = -1
                ref_text = turn_map.get(ref_turn)
                if ref_text is None:
                    component_rejections.append(
                        f"component_{ref_index}:invalid_user_turn"
                    )
                    continue
                excerpt = coerce_str(ref.get("span_excerpt")).strip()
                if not excerpt:
                    component_rejections.append(
                        f"component_{ref_index}:missing_excerpt"
                    )
                    continue
                located = _locate_span(ref_text, excerpt)
                if located is None:
                    component_rejections.append(
                        f"component_{ref_index}:excerpt_not_found"
                    )
                    continue
                matched, start_char = located
                valid_entries.append((ref_turn, matched, start_char))

            if not valid_entries:
                dropped_derivation_no_valid_excerpt += 1
                rejected_derivations.append(
                    {
                        "label": label,
                        "kind": kind,
                        "routing_eligible": False,
                        "reasons": tuple(component_rejections)
                        or ("no_component_evidence",),
                    }
                )
                record(
                    proposal_index,
                    item,
                    "not_supported_by_source",
                    ";".join(component_rejections) or "no_component_evidence",
                )
                continue

            # Single-turn derivation auto-downgrades to span mode: prevents
            # the LLM using derivation as a bypass for span validation.
            if len(raw_refs) == 1 and len(valid_entries) == 1:
                turn_index, matched, _start = valid_entries[0]
                turn_text = turn_map[turn_index]
                event = _emit_span_event(
                    turn_index=turn_index,
                    turn_text=turn_text,
                    excerpt=matched,
                    kind=kind,
                    kind_ambiguity=kind_ambiguity,
                )
                if event is None:
                    # Should not happen — we just matched — defensive only.
                    dropped_not_substring += 1
                    continue
                validated.append(event)
                span_mode_count += 1
                record(
                    proposal_index,
                    item,
                    "validated",
                    "single_valid_component_downgraded_to_exact_span",
                    event,
                )
                continue

            # Multi-turn derivation: retain every exact source component.
            # Missing or structurally insufficient component evidence keeps
            # the semantic proposal inspectable but blocks routing.
            distinct_turn_indexes = tuple(dict.fromkeys(entry[0] for entry in valid_entries))
            if len(distinct_turn_indexes) < 2:
                component_rejections.append(
                    "derivation_requires_two_distinct_user_turns"
                )
            display_text = label or "(multi-turn live constraint)"
            derivation_id = _derivation_issue_id(
                kind,
                display_text,
                tuple(valid_entries),
            )
            turn_refs = tuple(
                TurnRef(turn_index=turn_index, speaker="user")
                for turn_index in distinct_turn_indexes
            )
            components = tuple(
                DerivationComponent(
                    component_id=_derivation_component_id(
                        turn_index=turn_index,
                        matched=matched,
                        start_char=start_char,
                    ),
                    quote=matched,
                    span_ref=SpanRef(
                        turn_index=turn_index,
                        speaker="user",
                        start_char=start_char,
                        end_char=start_char + len(matched),
                    ),
                )
                for turn_index, matched, start_char in valid_entries
            )
            rejection_reasons = tuple(component_rejections)
            event = UserIssueEvent(
                issue_id=derivation_id,
                text=display_text,
                kind=kind,
                status="active",
                provenance=DerivationProvenance(
                    turn_refs=turn_refs,
                    source_object_ids=(),
                    note="live_constraints_specialist",
                    derivation_id=derivation_id,
                    components=components,
                    rejection_reasons=rejection_reasons,
                ),
                introduced_at_turn=valid_entries[0][0],
                kind_ambiguity=kind_ambiguity,
            )
            validated.append(event)
            derivation_mode_count += 1
            if rejection_reasons:
                incomplete_derivation_count += 1
                rejected_derivations.append(
                    {
                        "derivation_id": derivation_id,
                        "label": display_text,
                        "kind": kind,
                        "routing_eligible": False,
                        "reasons": rejection_reasons,
                    }
                )
            record(
                proposal_index,
                item,
                "validated",
                "validated_derivation_components_preserved",
                event,
            )

        else:
            dropped_invalid_mode += 1
            record(
                proposal_index,
                item,
                "invalid_evidence",
                "candidate_provenance_mode_is_invalid",
            )
            continue

    stats = _ValidationStats(
        raw_count=len(raw_items),
        validated_count=len(validated),
        span_mode_count=span_mode_count,
        derivation_mode_count=derivation_mode_count,
        dropped_invalid_kind=dropped_invalid_kind,
        dropped_invalid_turn=dropped_invalid_turn,
        dropped_not_substring=dropped_not_substring,
        dropped_derivation_no_valid_excerpt=dropped_derivation_no_valid_excerpt,
        incomplete_derivation_count=incomplete_derivation_count,
        dropped_invalid_mode=dropped_invalid_mode,
        rejected_derivations=tuple(rejected_derivations),
    )
    _LOGGER.info(
        "live_constraints_extraction.completed raw=%d validated=%d "
        "span_mode=%d derivation_mode=%d dropped_kind=%d dropped_turn=%d "
        "dropped_substring=%d dropped_derivation=%d incomplete_derivation=%d "
        "dropped_mode=%d",
        stats.raw_count, stats.validated_count,
        stats.span_mode_count, stats.derivation_mode_count,
        stats.dropped_invalid_kind, stats.dropped_invalid_turn,
        stats.dropped_not_substring, stats.dropped_derivation_no_valid_excerpt,
        stats.incomplete_derivation_count, stats.dropped_invalid_mode,
    )
    return validated, stats
