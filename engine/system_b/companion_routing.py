from __future__ import annotations

import logging
import re
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor

_LOGGER = logging.getLogger("system_b.companion_routing")

from .boundary_tracing import (
    BoundaryCallTrace,
    _capture_boundary_call,
    _metadata_to_boundary_call_trace,
)
from .boundary_validation import coerce_str, require_list_of_dicts
from .companion import (
    CompanionExpansion,
    CompanionFailureHint,
    CompanionHeuristicHint,
    CompanionIdentityChunk,
    CompanionPremortermHint,
    DetectedModel,
    FingerprintMove,
    FingerprintPayload,
)
from .conversation_context import ConversationContext


_BROAD_OVERLAY_MODELS: frozenset[str] = frozenset(
    {
        "tier-2-high-value",
        "second-order-thinking",
        "systems-thinking",
        "power-laws",
        "butterfly-effect",
        "multi-criteria-decision-analysis",
    }
)


def _quotes_overlap(quote_a: str, quote_b: str) -> bool:
    """Return True if two evidence quotes share substantial content."""
    if not quote_a or not quote_b:
        return False
    if quote_a in quote_b or quote_b in quote_a:
        return True
    tokens_a = _tokenize(quote_a)
    tokens_b = _tokenize(quote_b)
    if not tokens_a or not tokens_b:
        return False
    return len(tokens_a & tokens_b) / min(len(tokens_a), len(tokens_b)) >= 0.6


def _tokenize(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) >= 3
    }


def _iter_activation_texts(model_payload: dict) -> Iterable[str]:
    display_name = model_payload.get("display_name")
    if isinstance(display_name, str):
        yield display_name

    select_when = model_payload.get("select_when", [])
    if isinstance(select_when, list):
        for item in select_when:
            if isinstance(item, str):
                yield item

    danger_when = model_payload.get("danger_when", [])
    if isinstance(danger_when, list):
        for item in danger_when:
            if isinstance(item, str):
                yield item


def _pick_activation_trigger(model_payload: dict, *, fallback: str = "") -> str:
    select_when = model_payload.get("select_when", [])
    if isinstance(select_when, list):
        for item in select_when:
            if isinstance(item, str) and item.strip():
                return item
    display_name = model_payload.get("display_name")
    if isinstance(display_name, str) and display_name.strip():
        return display_name
    return fallback


def _rank_overlap(texts: Iterable[str], model_payload: dict) -> int:
    candidate_tokens = set()
    for text in _iter_activation_texts(model_payload):
        candidate_tokens.update(_tokenize(text))
    return sum(len(_tokenize(text) & candidate_tokens) for text in texts if isinstance(text, str))


def _normalize_quotes(text: str) -> str:
    """Normalize escaped JSON quotes so substring matching works across formats.

    The vanilla_answer may contain escaped quotes (\\") from JSON serialization
    while the fingerprint LLM returns quotes with unescaped formatting.
    Normalize both sides to plain double-quotes for comparison.
    """
    return text.replace('\\"', '"').replace("\\'", "'")


def _quote_in_answer(quote: str, answer_text: str) -> bool:
    """Check if a quote appears in the answer, tolerant of quote escaping."""
    if quote in answer_text:
        return True
    normalized_quote = _normalize_quotes(quote)
    normalized_answer = _normalize_quotes(answer_text)
    return normalized_quote in normalized_answer


def _fuzzy_quote_in_answer(quote: str, answer_text: str, threshold: float = 0.80) -> bool:
    """Check if a quote has high token overlap with the answer.

    Fallback for when exact substring matching fails due to minor
    paraphrasing by the LLM. Uses 80% threshold (stricter than the 60%
    used for dedup in _quotes_overlap).
    """
    quote_tokens = _tokenize(quote)
    if not quote_tokens or len(quote_tokens) < 3:
        return False
    answer_tokens = _tokenize(answer_text)
    if not answer_tokens:
        return False
    return len(quote_tokens & answer_tokens) / len(quote_tokens) >= threshold


def validate_fingerprint_moves(
    moves: list[FingerprintMove] | object,
    vanilla_answer: str,
) -> tuple[list[FingerprintMove], list[dict[str, object]]]:
    validated: list[FingerprintMove] = []
    dropped: list[dict[str, object]] = []
    answer_text = vanilla_answer if isinstance(vanilla_answer, str) else str(vanilla_answer or "")

    if not isinstance(moves, list):
        return validated, dropped

    for move in moves:
        if not isinstance(move, FingerprintMove):
            continue
        quotes = move.evidence_quotes if isinstance(move.evidence_quotes, list) else []
        if not quotes:
            dropped.append({"move": move, "drop_reason": "missing_quotes"})
            continue
        if all(isinstance(quote, str) and quote and _quote_in_answer(quote, answer_text) for quote in quotes):
            validated.append(move)
            continue
        if any(isinstance(quote, str) and quote and not _quote_in_answer(quote, answer_text) for quote in quotes):
            # Fuzzy fallback: check if the non-matching quotes have high token overlap
            if all(
                isinstance(quote, str) and quote and (
                    _quote_in_answer(quote, answer_text) or _fuzzy_quote_in_answer(quote, answer_text)
                )
                for quote in quotes
            ):
                validated.append(move)
                continue
            dropped.append({"move": move, "drop_reason": "fabricated_quote"})
            continue
        dropped.append({"move": move, "drop_reason": "quote_not_literal_substring"})

    return validated, dropped


def parse_fingerprint_response(
    raw_payload: dict,
    vanilla_answer: str,
) -> FingerprintPayload:
    moves_list = require_list_of_dicts(raw_payload, "reasoning_moves", "companion_fingerprint")
    if not moves_list:
        return FingerprintPayload(raw=[], validated=[], dropped=[])

    raw_moves: list[FingerprintMove] = []
    for item in moves_list:
        evidence_quotes = item.get("evidence_quotes", [])
        if not isinstance(evidence_quotes, list):
            evidence_quotes = []
        evidence_quotes = [quote for quote in evidence_quotes if isinstance(quote, str)]
        raw_moves.append(
            FingerprintMove(
                move_id=coerce_str(item.get("move_id")).strip(),
                reasoning_move=coerce_str(item.get("reasoning_move")).strip(),
                evidence_quotes=evidence_quotes,
                evidence_rationale=coerce_str(item.get("evidence_rationale")).strip(),
                confidence=coerce_str(item.get("confidence")).strip().lower() or "medium",
            )
        )

    validated, dropped = validate_fingerprint_moves(raw_moves, vanilla_answer)
    return FingerprintPayload(raw=raw_moves, validated=validated, dropped=dropped)


def _joined_assistant_turns(context: ConversationContext) -> str:
    """Flat string of assistant turns for substring validation + keyword recall.

    Used by the pipeline's Lane 2 recall path so fingerprint + verification
    evidence quotes must be substrings of actual assistant text (turn-structured),
    not of a flattened `query + vanilla_answer` compilation.
    """
    return "\n\n".join(t.text for t in context.turns if t.speaker == "assistant")


def _build_fingerprint_system_prompt_from_context() -> str:
    """Phase 2d: CONTEXT/SOURCE-aware fingerprint system prompt.

    Same behavioral contract as the legacy prompt (extract 3-8 reasoning moves
    with verbatim evidence quotes) but names SOURCE = assistant turns as the
    audit target and requires evidence quotes to be literal substrings of
    SOURCE text only (not of user turns or extraction summaries).
    """
    return (
        "You are extracting reasoning moves from an AI assistant's response. "
        "You will receive the user prompt in two sections:\n"
        "- CONTEXT: the decision situation, framing, live constraints, dropped threads, and the user's turns. Background only — NOT where the reasoning moves live.\n"
        "- SOURCE: the assistant's turns verbatim. Reasoning moves live HERE. Evidence quotes MUST be literal substrings of SOURCE.\n\n"
        "Return strict JSON with a top-level 'reasoning_moves' list. "
        "Each move must include move_id, reasoning_move, evidence_quotes, evidence_rationale, and confidence. "
        "Do not name mental models. Describe abstract reasoning moves only.\n\n"
        "CRITICAL RULE FOR evidence_quotes:\n"
        "Every evidence_quotes entry must be a LITERAL SUBSTRING copied character-for-character "
        "from an assistant turn in SOURCE. It must pass a simple `quote in <joined-assistant-turns>` check. "
        "Do NOT paraphrase, summarize, compress, or combine multiple passages into one quote. "
        "Do NOT quote from CONTEXT (user turns or extraction summaries). "
        "If a reasoning move spans multiple passages, include each passage as a SEPARATE entry "
        "in the evidence_quotes array. Each entry must be a verbatim contiguous substring of assistant text. "
        "Quotes that are not literal substrings of SOURCE will be rejected by the validation layer."
    )


# ---------------------------------------------------------------------------
# Packet-driven Lane 2 entry points
# ---------------------------------------------------------------------------

from .packet_builders.lane4 import Lane4Packet  # noqa: E402  (intentional cycle-avoidance)


def _joined_assistant_turns_from_packet(packet: Lane4Packet) -> str:
    """Mirror of `_joined_assistant_turns` for packet input."""
    parts = [t.text for t in packet.turns if t.speaker == "assistant"]
    return "\n".join(parts)


def _build_fingerprint_user_prompt_from_packet(packet: Lane4Packet) -> str:
    """Build the fingerprint user prompt body from a Lane4Packet.

    Renders CONTEXT (extraction summaries + user turns) and SOURCE
    (assistant turns verbatim — the audit target whose substrings must
    back every evidence_quote).
    """
    parts: list[str] = [
        "CONTEXT (background — NOT the audit target; use to understand what the user made live):",
    ]
    if packet.decision_situation:
        parts.append(f"- Decision situation: {packet.decision_situation.text}")
    if packet.original_framing:
        parts.append(f"- Framing: {packet.original_framing.text}")
    if packet.constraints:
        parts.append("- Live constraints:")
        for c in packet.constraints:
            status = (c.status or "active").upper()
            tag = status  # weight not in IR
            parts.append(f"  - [{tag}] {c.text} (turn {c.introduced_at_turn})")
    if packet.issues:
        parts.append("- Dropped threads:")
        for i in packet.issues:
            line = (
                f"  - {i.text} (raised by {i.raised_by} turn {i.introduced_at_turn}, "
                f"status: {i.status or '?'})"
            )
            if i.superseded_by:
                line += f", superseded_by: {i.superseded_by}"
            parts.append(line)
    user_turns = [t for t in packet.turns if t.speaker == "user"]
    if user_turns:
        parts.append("- User turns (CONTEXT only):")
        for t in user_turns:
            parts.append(f"  [Turn {t.turn_index}] USER: {t.text}")
    parts.append("")
    parts.append(
        "SOURCE (assistant turns — extract reasoning moves from HERE; evidence quotes MUST be literal substrings of this section):"
    )
    assistant_turns = [t for t in packet.turns if t.speaker == "assistant"]
    if not assistant_turns:
        parts.append("(no assistant turns present)")
    else:
        for t in assistant_turns:
            parts.append(f"[Turn {t.turn_index}] ASSISTANT:")
            parts.append(t.text)
            parts.append("")
    parts.append(
        "Extract 3-8 reasoning moves from SOURCE. "
        "Each move must be supported by exact quotes copied from SOURCE. "
        "Remember: every evidence_quotes entry must be a literal contiguous substring of assistant text in SOURCE — not from CONTEXT, not a paraphrase."
    )
    return "\n".join(parts)


def run_fingerprint_call_from_packet(
    *,
    packet: Lane4Packet,
    client,
) -> FingerprintPayload:
    """Packet-driven Lane 2 fingerprint call."""
    assistant_text = _joined_assistant_turns_from_packet(packet)
    raw_payload = client.run_json(
        _build_fingerprint_system_prompt_from_context(),
        _build_fingerprint_user_prompt_from_packet(packet),
    )
    fingerprint = parse_fingerprint_response(raw_payload, assistant_text)
    validated = sorted(
        fingerprint.validated,
        key=lambda item: (0 if item.confidence == "high" else 1, item.move_id),
    )[:8]
    return FingerprintPayload(
        raw=fingerprint.raw,
        validated=validated,
        dropped=fingerprint.dropped,
    )


def _build_verification_user_prompt_from_packet(
    packet: Lane4Packet,
    fingerprint_payload: FingerprintPayload,
    candidates: list[dict[str, str]],
) -> str:
    """Build the verification user prompt body from a Lane4Packet.

    Renders CONTEXT (extraction summaries + user turns) and SOURCE
    (assistant turns verbatim — the audit target whose substrings must
    back every accepted-model evidence_quote).
    """
    parts: list[str] = [
        "CONTEXT (background — what the user made live; NOT quotable as evidence):",
    ]
    if packet.decision_situation:
        parts.append(f"- Decision situation: {packet.decision_situation.text}")
    if packet.original_framing:
        parts.append(f"- Framing: {packet.original_framing.text}")
    if packet.constraints:
        parts.append("- Live constraints:")
        for c in packet.constraints:
            status = (c.status or "active").upper()
            tag = status  # weight not in IR
            parts.append(f"  - [{tag}] {c.text} (turn {c.introduced_at_turn})")
    user_turns = [t for t in packet.turns if t.speaker == "user"]
    if user_turns:
        parts.append("- User turns (CONTEXT only):")
        for t in user_turns:
            parts.append(f"  [Turn {t.turn_index}] USER: {t.text}")
    parts.append("")
    parts.append(
        "SOURCE (assistant turns — evidence_quote for each accepted model MUST be a literal substring of this section):"
    )
    assistant_turns = [t for t in packet.turns if t.speaker == "assistant"]
    if not assistant_turns:
        parts.append("(no assistant turns present)")
    else:
        for t in assistant_turns:
            parts.append(f"[Turn {t.turn_index}] ASSISTANT:")
            parts.append(t.text)
            parts.append("")

    fingerprint_lines = [
        "- {move_id} | {reasoning_move} | quotes: {quotes}".format(
            move_id=move.move_id,
            reasoning_move=move.reasoning_move,
            quotes=" | ".join(move.evidence_quotes),
        )
        for move in fingerprint_payload.validated
    ]
    candidate_lines: list[str] = []
    for candidate in candidates:
        line = "- {model_id} | {model_name} | activation: {activation_trigger}".format(
            model_id=candidate["model_id"],
            model_name=candidate["model_name"],
            activation_trigger=candidate["activation_trigger"],
        )
        dw = candidate.get("danger_when", "")
        if dw:
            line += f" | watches_for: {dw}"
        candidate_lines.append(line)

    parts.append("Validated fingerprint moves:")
    parts.append("\n".join(fingerprint_lines) if fingerprint_lines else "(none)")
    parts.append("")
    parts.append("Candidate models:")
    parts.append("\n".join(candidate_lines))
    parts.append("")
    parts.append(
        "Return ONLY the JSON object described in the system prompt. "
        "Do not return arrays of model ids. "
        "Use exact evidence quotes copied from SOURCE (assistant turns) for every accepted model."
    )
    return "\n".join(parts)


_DETECTED_MODELS_CAP = 5


_NUM_VERIFIER_SHARDS = 3


def _shard_candidates_rank_stratified(
    candidates: list[dict[str, object]],
) -> dict[str, list[dict[str, object]]]:
    """Partition candidates into rank-stratified shards (PR-B v3).

    Shard assignment: ``shard_index = (final_rank - 1) % _NUM_VERIFIER_SHARDS``.
    Each shard receives a top/middle/tail slice of recall — final_rank 1 → shard
    0, rank 2 → shard 1, rank 3 → shard 2, rank 4 → shard 0, ... So every shard
    sees a mixed competitive field (high-rank + middle + tail), not a clustered
    cognitive type. This is the v3 architecture: same number of LLM calls (3)
    regardless of input volume; competition preserved within each shard via
    the rank stratification.

    v1/v2 used reasoning-type partitioning here. v3 changes the decomposition
    AXIS, not the decomposition direction. The granularity finding from v1/v2:
    cognitive-type partition was too fine (4-9 shards × per-shard accept floor
    overflowed the global product budget). Rank-stratified at 3 shards is
    coarser AND restores cross-cognitive competition inside each shard.

    Returns a dict keyed by shard_id (``"shard_0"``, ``"shard_1"``,
    ``"shard_2"``); empty shards are omitted. Insertion order is shard_0 →
    shard_1 → shard_2, giving deterministic submission order to the executor.
    Candidates without a numeric ``final_rank`` go to ``"shard_unranked"``
    (defensive — production candidates always have final_rank set by recall).
    """
    shards: dict[str, list[dict[str, object]]] = {}
    for c in candidates:
        rank = c.get("final_rank")
        if not isinstance(rank, int) or rank < 1:
            shard_id = "shard_unranked"
        else:
            shard_id = f"shard_{(rank - 1) % _NUM_VERIFIER_SHARDS}"
        shards.setdefault(shard_id, []).append(c)
    # Sort shard keys deterministically so submission order is stable across
    # runs (dict insertion order would otherwise depend on which shard got
    # its first member first, which depends on candidate ordering).
    return {sid: shards[sid] for sid in sorted(shards.keys())}


def _run_verifier_single_shard(
    *,
    shard_id: str,
    packet: Lane4Packet,
    fingerprint_payload: FingerprintPayload,
    shard_candidates: list[dict[str, object]],
    assistant_text: str,
    candidate_ids: set[str],
    client,
    use_metadata: bool,
):
    """Run one verifier LLM call for a single rank-stratified shard.

    Returns ``(accepted_items, rejected_items, weak_matches_items,
    BoundaryCallTrace)``. When ``use_metadata`` is True, uses
    ``client.run_json_with_metadata`` (thread-safe; required for parallel
    execution). When False, falls back to ``client.run_json`` +
    ``_capture_boundary_call`` (sequential test mocks).
    """
    user_prompt = _build_verification_user_prompt_from_packet(
        packet, fingerprint_payload, shard_candidates
    )
    system_prompt = _build_verification_system_prompt()
    stage = f"companion_verification_{shard_id}"
    if use_metadata:
        raw_payload, metadata = client.run_json_with_metadata(system_prompt, user_prompt)
        trace = _metadata_to_boundary_call_trace(metadata, stage=stage)
    else:
        raw_payload = client.run_json(system_prompt, user_prompt)
        trace = _capture_boundary_call(client, stage=stage)
    accepted, rejected, weak_matches = parse_verification_response(raw_payload, assistant_text, candidate_ids)
    return accepted, rejected, weak_matches, trace


def run_verification_call_from_packet(
    *,
    packet: Lane4Packet,
    fingerprint_payload: FingerprintPayload,
    candidates: list[dict[str, str]],
    client,
) -> tuple[
    list[DetectedModel],
    list[dict[str, str]],
    list[DetectedModel],
    list[dict[str, str]],
    list[dict[str, str]],
    list[dict[str, str]],
    dict[str, dict[str, object]],
    list["BoundaryCallTrace"],
]:
    """Packet-driven Lane 2 verification call — rank-stratified shards (PR-B v3).

    Partitions ``candidates`` into ``_NUM_VERIFIER_SHARDS`` (3) shards via
    rank stratification: ``shard_index = (final_rank - 1) % 3``. Each shard
    receives a top/middle/tail slice of recall, so every shard sees a mixed
    competitive field (cross-cognitive-shape comparison preserved within
    the call). Each per-shard call sees the FULL assistant source text and
    FULL validated fingerprint — only the candidates are shard-local.

    Architecture progression (committed on this branch):
      v1: reasoning-type partition (4-9 shards × variable size). Removed
          monolithic-call overload but lost cross-bucket competition →
          accepted count exploded to ~14.6 per run.
      v2: + strict shared rubric. Routed compatible-but-not-load-bearing
          candidates to weak_matches but couldn't break the per-bucket
          accept floor (~10.8 per run).
      v3 (this code): rank-stratified shards. Same number of LLM calls (3)
          regardless of input volume; competition restored INSIDE each
          shard via rank stratification. Test of the granularity
          hypothesis: was the v1/v2 issue too-fine partitioning, or
          something deeper?

    Pre-registered fan-in (deterministic, independent of which shard
    finishes first):

    1. Concatenate accepted lists from every shard in stable shard-id order
       (shard_0 → shard_1 → shard_2; empties skipped).
    2. Dedupe by ``model_id`` — first valid occurrence wins, surplus go to
       ``duplicate_accepts`` (NOT ``rejected_models``).
    3. Sort the deduped accepted list by ``(candidate.final_rank, model_id)``.
    4. Apply the existing top-5 surfacing budget. Overflow → ``capped_models``.

    Returns a 7-tuple: ``(detected_models, rejected_models,
    accepted_before_cap, capped_models, duplicate_accepts, weak_matches,
    boundary_traces)``. ``boundary_traces`` is one per non-empty shard.

    Falls back to sequential execution when the boundary client doesn't
    expose ``run_json_with_metadata`` (test mocks).
    """
    if not candidates:
        return [], [], [], [], [], [], {}, []

    assistant_text = _joined_assistant_turns_from_packet(packet)
    candidate_names = {
        candidate["model_id"]: candidate["model_name"]
        for candidate in candidates
        if candidate.get("model_id") and candidate.get("model_name")
    }
    candidate_final_rank = {
        candidate["model_id"]: int(candidate.get("final_rank") or 0)
        for candidate in candidates
        if candidate.get("model_id")
    }

    shards = _shard_candidates_rank_stratified(candidates)

    # Determine execution mode. Parallel requires `run_json_with_metadata` and
    # the explicit `supports_parallel_calls` opt-in. Test mocks typically have
    # neither, so they route through the sequential path automatically.
    use_metadata = (
        hasattr(client, "run_json_with_metadata")
        and getattr(client, "supports_parallel_calls", False)
    )

    per_shard_results: list[tuple[str, list[dict], list[dict], list[dict], BoundaryCallTrace]] = []

    if use_metadata and len(shards) > 1:
        max_workers = min(len(shards), _NUM_VERIFIER_SHARDS)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for shard_id, shard_cands in shards.items():
                shard_ids = {c["model_id"] for c in shard_cands if c.get("model_id")}
                fut = executor.submit(
                    _run_verifier_single_shard,
                    shard_id=shard_id,
                    packet=packet,
                    fingerprint_payload=fingerprint_payload,
                    shard_candidates=shard_cands,
                    assistant_text=assistant_text,
                    candidate_ids=shard_ids,
                    client=client,
                    use_metadata=True,
                )
                futures.append((shard_id, fut))
        for shard_id, fut in futures:
            accepted, rejected, shard_weak, trace = fut.result()
            per_shard_results.append((shard_id, accepted, rejected, shard_weak, trace))
    else:
        # Sequential path: single-shard cases, test mocks, or boundary clients
        # that don't support parallel calls.
        for shard_id, shard_cands in shards.items():
            shard_ids = {c["model_id"] for c in shard_cands if c.get("model_id")}
            accepted, rejected, shard_weak, trace = _run_verifier_single_shard(
                shard_id=shard_id,
                packet=packet,
                fingerprint_payload=fingerprint_payload,
                shard_candidates=shard_cands,
                assistant_text=assistant_text,
                candidate_ids=shard_ids,
                client=client,
                use_metadata=use_metadata,
            )
            per_shard_results.append((shard_id, accepted, rejected, shard_weak, trace))

    # Fan-in step 1: concatenate in deterministic shard-id order.
    raw_accepted: list[dict] = []
    rejected: list[dict] = []
    weak_matches: list[dict] = []
    boundary_traces: list[BoundaryCallTrace] = []
    # Per-shard breakdown — diagnostic; persisted via the verifier->pipeline
    # boundary so stability_check.py can compute per-shard accept/weak counts.
    accepted_by_shard: dict[str, list[str]] = {}
    weak_by_shard: dict[str, list[str]] = {}
    for shard_id, accepted, shard_rejected, shard_weak, trace in per_shard_results:
        raw_accepted.extend(accepted)
        rejected.extend(shard_rejected)
        weak_matches.extend(shard_weak)
        boundary_traces.append(trace)
        accepted_by_shard[shard_id] = [a.get("model_id", "") for a in accepted if a.get("model_id")]
        weak_by_shard[shard_id] = [w.get("model_id", "") for w in shard_weak if w.get("model_id")]

    # Build the shard_breakdown diagnostic surface. Per-shard accept/weak
    # counts answer the question "is one shard the over-acceptance source,
    # or are all three contributing?" — important for v3 gate evaluation.
    shard_breakdown: dict[str, dict[str, object]] = {}
    rejected_per_shard: dict[str, int] = {}
    for shard_id, _, shard_rejected, _, _ in per_shard_results:
        rejected_per_shard[shard_id] = len(shard_rejected)
    for shard_id in sorted(set(accepted_by_shard) | set(weak_by_shard) | set(rejected_per_shard)):
        shard_breakdown[shard_id] = {
            "accepted": accepted_by_shard.get(shard_id, []),
            "weak_matches": weak_by_shard.get(shard_id, []),
            "rejected_count": rejected_per_shard.get(shard_id, 0),
            "candidate_count": len(shards.get(shard_id, [])),
        }

    # Fan-in step 2: dedupe by model_id (first valid occurrence wins).
    seen_model_ids: set[str] = set()
    deduped_accepted: list[dict] = []
    duplicate_accepts: list[dict[str, str]] = []
    for item in raw_accepted:
        mid = item.get("model_id", "")
        if not mid:
            continue
        if mid in seen_model_ids:
            duplicate_accepts.append(
                {
                    "model_id": mid,
                    "model_name": candidate_names.get(mid, mid),
                    "drop_reason": "duplicate_accept_dedupe",
                }
            )
            continue
        seen_model_ids.add(mid)
        deduped_accepted.append(item)

    # Fan-in step 3: deterministic sort by (final_rank, model_id). High recall
    # rank (small final_rank) surfaces first; ties broken alphabetically. This
    # makes the post-cap surfacing budget independent of which bucket finished
    # first AND independent of the LLM's per-bucket response order.
    deduped_accepted.sort(
        key=lambda item: (
            candidate_final_rank.get(item.get("model_id", ""), 10_000),
            item.get("model_id", ""),
        )
    )

    accepted_before_cap = [
        DetectedModel(
            model_id=item["model_id"],
            model_name=candidate_names.get(item["model_id"], item["model_id"]),
            evidence_quote=item.get("evidence_quote", ""),
            presence_mode=item.get("presence_mode", "executed"),
            presence_explanation=item.get("presence_explanation", ""),
            detection_confidence="structural",
        )
        for item in deduped_accepted
    ]
    # Fan-in step 4: apply the existing top-5 surfacing budget.
    detected_models = accepted_before_cap[:_DETECTED_MODELS_CAP]
    capped_models = [
        {
            "model_id": m.model_id,
            "model_name": m.model_name,
            "drop_reason": "capped_at_top_5",
        }
        for m in accepted_before_cap[_DETECTED_MODELS_CAP:]
    ]
    return (
        detected_models,
        rejected,
        accepted_before_cap,
        capped_models,
        duplicate_accepts,
        weak_matches,
        shard_breakdown,
        boundary_traces,
    )


# ---------------------------------------------------------------------------
# Path B: global anchor calibrator
# ---------------------------------------------------------------------------
#
# After the rank-stratified shards return their strong accepts, an additional
# LLM call selects the TOP-5 most structurally load-bearing for downstream
# Step 6 consumption. This restores the cross-shard competition that the
# monolithic verifier did silently and that the partition removed.
#
# Crucial framing (research/lane2-prb-v3-2026-04-26/interpretation.md):
# the calibrator does NOT make per-shard verifier judgments more stable.
# It produces a stable downstream PRODUCT (calibrated anchors) despite
# per-shard verifier noise. Gates are anchor-Jaccard, not Cand-cond.
#
# The calibrator sees ONLY strong accepts (typically 4-9 items). Weak
# matches are NOT included — they are not candidates for surfacing,
# they are diagnostic. Including them would re-create the overload v3
# fixed.

_CALIBRATOR_TARGET_COUNT = 5


def _build_calibrator_system_prompt() -> str:
    return (
        "You are calibrating a final anchor selection for downstream consumption.\n"
        "\n"
        "An upstream rank-stratified verifier has already accepted N candidate mental models as STRONG "
        "activations in the assistant's reasoning. Each comes with a literal evidence quote. Your job is "
        "NOT to re-judge whether they are strong. Your job is to select the TOP 5 most STRUCTURALLY "
        "LOAD-BEARING anchors.\n"
        "\n"
        "LOAD-BEARING means: removing this model from the analysis would meaningfully weaken the downstream "
        "reasoning audit's ability to challenge or sharpen the assistant's reasoning. A model that is "
        "strongly executed but redundant with another, more load-bearing accept, should be dropped — "
        "NOT because it is weak, but because surfacing it crowds out a more load-bearing model.\n"
        "\n"
        "RULES:\n"
        "  - Maximum 5 calibrated_anchors.\n"
        "  - Every input model_id must appear in EITHER calibrated_anchors OR calibration_dropped.\n"
        "  - Dropped models are NOT 'weak' and NOT 'rejected'. Their drop_reason is\n"
        "    'strong_locally_but_less_load_bearing_globally' — they were correctly accepted as strong,\n"
        "    just out-competed by more load-bearing peers in this run's anchor budget.\n"
        "  - Prefer specific-mechanism models over broad-overlay models when both exist.\n"
        "  - Prefer models whose evidence quote names a load-bearing structural error or mechanism\n"
        "    (e.g. 'authority-bias on this rank-attestation') over models whose evidence is broad\n"
        "    framing language (e.g. 'second-order-thinking on a passing mention').\n"
        "  - You may rank fewer than 5 if input has fewer than 5 strong accepts (do not pad).\n"
        "\n"
        "Return ONLY valid JSON in this exact shape:\n"
        "{\n"
        '  "calibrated_anchors": [\n'
        "    {\n"
        '      "model_id": "candidate-model-id",\n'
        '      "rank": 1,\n'
        '      "calibration_reason": "one sentence: why this is more load-bearing than a peer"\n'
        "    }\n"
        "  ],\n"
        '  "calibration_dropped": [\n'
        "    {\n"
        '      "model_id": "candidate-model-id",\n'
        '      "drop_reason": "strong_locally_but_less_load_bearing_globally",\n'
        '      "drop_explanation": "one sentence: which other accept it lost to and why"\n'
        "    }\n"
        "  ]\n"
        "}\n"
        "\n"
        "Every input model_id MUST appear exactly once across the two lists. Do not invent new model_ids. "
        "If you mark fewer than 5 as anchors, the rest go to calibration_dropped."
    )


def _build_calibrator_user_prompt(
    *,
    packet: Lane4Packet,
    fingerprint_payload: FingerprintPayload,
    accepted_before_cap: list["DetectedModel"],
    accepted_to_shard: dict[str, str],
) -> str:
    assistant_text = _joined_assistant_turns_from_packet(packet)
    fingerprint_lines: list[str] = []
    for move in fingerprint_payload.validated[:8]:
        fingerprint_lines.append(f"- {move.reasoning_move}")
    fingerprint_block = "\n".join(fingerprint_lines) if fingerprint_lines else "(no validated moves)"
    accepted_lines: list[str] = []
    for i, m in enumerate(accepted_before_cap, start=1):
        shard_hint = accepted_to_shard.get(m.model_id, "?")
        accepted_lines.append(
            f"{i}. model_id: {m.model_id}\n"
            f"   model_name: {m.model_name}\n"
            f"   source_verifier_shard: {shard_hint}\n"
            f"   presence_mode: {m.presence_mode}\n"
            f"   evidence_quote: {m.evidence_quote!r}\n"
            f"   presence_explanation: {m.presence_explanation}"
        )
    accepted_block = "\n".join(accepted_lines)
    return (
        f"ASSISTANT'S REASONING (the audit target):\n"
        f"{assistant_text}\n\n"
        f"FINGERPRINT (validated reasoning moves):\n"
        f"{fingerprint_block}\n\n"
        f"STRONG ACCEPTS FROM VERIFIER (calibrate these):\n"
        f"{accepted_block}\n"
    )


def parse_calibrator_response(
    raw_payload: dict,
    input_model_ids: set[str],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Parse calibrator output. Returns ``(calibrated_anchors, calibration_dropped)``.

    Defensive: ensures every input model_id appears exactly once across the
    two lists. Models the calibrator omits go to calibration_dropped with
    drop_reason="missing_from_calibrator_output". Models the calibrator
    invents (not in input_model_ids) are silently filtered.
    """
    anchors_entries = (
        require_list_of_dicts(raw_payload, "calibrated_anchors", "companion_calibration")
        if isinstance(raw_payload.get("calibrated_anchors"), list)
        else []
    )
    dropped_entries = (
        require_list_of_dicts(raw_payload, "calibration_dropped", "companion_calibration")
        if isinstance(raw_payload.get("calibration_dropped"), list)
        else []
    )

    calibrated_anchors: list[dict[str, str]] = []
    seen_in_anchors: set[str] = set()
    for item in anchors_entries:
        mid = coerce_str(item.get("model_id")).strip()
        if not mid or mid not in input_model_ids or mid in seen_in_anchors:
            continue
        if len(calibrated_anchors) >= _CALIBRATOR_TARGET_COUNT:
            # Calibrator went over budget; route excess to dropped.
            continue
        seen_in_anchors.add(mid)
        rank = item.get("rank")
        try:
            rank_int = int(rank) if rank is not None else len(calibrated_anchors) + 1
        except (TypeError, ValueError):
            rank_int = len(calibrated_anchors) + 1
        calibrated_anchors.append(
            {
                "model_id": mid,
                "rank": str(rank_int),
                "calibration_reason": coerce_str(item.get("calibration_reason")).strip(),
            }
        )

    calibration_dropped: list[dict[str, str]] = []
    seen_in_dropped: set[str] = set()
    for item in dropped_entries:
        mid = coerce_str(item.get("model_id")).strip()
        if not mid or mid not in input_model_ids or mid in seen_in_anchors or mid in seen_in_dropped:
            continue
        seen_in_dropped.add(mid)
        calibration_dropped.append(
            {
                "model_id": mid,
                "drop_reason": coerce_str(item.get("drop_reason")).strip()
                or "strong_locally_but_less_load_bearing_globally",
                "drop_explanation": coerce_str(item.get("drop_explanation")).strip(),
            }
        )

    # Defensive: any input model_id not seen in either list goes to dropped
    # with a defensive reason. Keeps the contract "every input appears once".
    for mid in input_model_ids:
        if mid in seen_in_anchors or mid in seen_in_dropped:
            continue
        calibration_dropped.append(
            {
                "model_id": mid,
                "drop_reason": "missing_from_calibrator_output",
                "drop_explanation": "calibrator did not list this model in either calibrated_anchors or calibration_dropped",
            }
        )

    # Also: if the calibrator went over budget, route the excess (anchors
    # beyond target count) to dropped. This already happened above in the
    # loop, but if the calibrator returned more than _CALIBRATOR_TARGET_COUNT
    # we want the excess as dropped (already in seen_in_anchors test above).
    # No-op here.

    return calibrated_anchors, calibration_dropped


def run_calibrator_call_from_packet(
    *,
    packet: Lane4Packet,
    fingerprint_payload: FingerprintPayload,
    accepted_before_cap: list[DetectedModel],
    shard_breakdown: dict[str, dict[str, object]],
    client,
) -> tuple[
    list[DetectedModel],   # calibrated_anchors (≤ _CALIBRATOR_TARGET_COUNT)
    list[dict[str, str]],  # calibration_dropped — strong-but-not-selected (NOT weak)
    BoundaryCallTrace | None,  # boundary trace; None if calibration was skipped
]:
    """Path B global anchor calibrator.

    Skipped (no LLM call) when ``len(accepted_before_cap) <= _CALIBRATOR_TARGET_COUNT``
    — the entire input is already within budget; no calibration needed. The
    return mirrors the input as calibrated_anchors with rank-by-position and
    empty calibration_dropped.

    When called, returns a (calibrated_anchors, calibration_dropped, trace)
    tuple. Calibration_dropped models are NOT weak_matches and NOT
    rejected_models — they are correctly-accepted strong models that lost to
    more load-bearing peers in the run's surfacing budget.
    """
    n_input = len(accepted_before_cap)
    if n_input == 0:
        return [], [], None
    if n_input <= _CALIBRATOR_TARGET_COUNT:
        # Skip the call. The input is already within budget; pass through
        # as calibrated_anchors in input order. No rank-by-load-bearingness
        # because there's no selection pressure.
        return list(accepted_before_cap), [], None

    # Map model_id -> source shard for diagnostics.
    accepted_to_shard: dict[str, str] = {}
    for shard_id, info in (shard_breakdown or {}).items():
        for mid in info.get("accepted", []) or []:
            if isinstance(mid, str):
                accepted_to_shard[mid] = shard_id

    user_prompt = _build_calibrator_user_prompt(
        packet=packet,
        fingerprint_payload=fingerprint_payload,
        accepted_before_cap=accepted_before_cap,
        accepted_to_shard=accepted_to_shard,
    )
    system_prompt = _build_calibrator_system_prompt()
    stage = "companion_calibrator"

    use_metadata = (
        hasattr(client, "run_json_with_metadata")
        and getattr(client, "supports_parallel_calls", False)
    )
    if use_metadata:
        raw_payload, metadata = client.run_json_with_metadata(system_prompt, user_prompt)
        trace = _metadata_to_boundary_call_trace(metadata, stage=stage)
    else:
        raw_payload = client.run_json(system_prompt, user_prompt)
        trace = _capture_boundary_call(client, stage=stage)

    input_model_ids = {m.model_id for m in accepted_before_cap}
    parsed_anchors, parsed_dropped = parse_calibrator_response(raw_payload, input_model_ids)

    # Convert parsed_anchors back into DetectedModel objects, preserving the
    # original DetectedModel fields from accepted_before_cap (the calibrator
    # only ranks; it doesn't change presence_mode, evidence, or explanation).
    by_mid = {m.model_id: m for m in accepted_before_cap}
    # Sort by rank field (1-indexed).
    parsed_anchors.sort(key=lambda a: int(a.get("rank") or 99))
    calibrated_anchors: list[DetectedModel] = []
    for entry in parsed_anchors:
        mid = entry["model_id"]
        if mid in by_mid:
            calibrated_anchors.append(by_mid[mid])
        if len(calibrated_anchors) >= _CALIBRATOR_TARGET_COUNT:
            break

    return calibrated_anchors, parsed_dropped, trace


def parse_verification_response(
    raw_payload: dict,
    vanilla_answer: str,
    candidate_ids: set[str] | list[str] | tuple[str, ...],
) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    """Parse verifier output into the strict shared-rubric three-category form.

    Returns ``(accepted, rejected, weak_matches)``. The strict acceptance bar
    (PR-B v2) is enforced HERE — if the LLM didn't supply
    ``activation_strength="strong"`` or ``why_not_merely_compatible``, the
    item is demoted to ``weak_matches`` regardless of what the LLM put it in.
    This protects against per-bucket verifiers becoming under-discriminating
    after partition removed cross-bucket competition.
    """
    allowed_ids = {str(item).strip() for item in candidate_ids if str(item).strip()}
    accepted_entries = require_list_of_dicts(raw_payload, "accepted", "companion_verification")
    rejected_entries = require_list_of_dicts(raw_payload, "rejected", "companion_verification")
    # weak_matches is optional in the schema (PR-B v2 introduces it). Older
    # responses without this field continue to work — they just produce no
    # weak_matches entries from this branch.
    weak_matches_entries = (
        require_list_of_dicts(raw_payload, "weak_matches", "companion_verification")
        if isinstance(raw_payload.get("weak_matches"), list)
        else []
    )
    accepted: list[dict[str, str]] = []
    rejected: list[dict[str, str]] = []
    weak_matches: list[dict[str, str]] = []
    answer_text = vanilla_answer if isinstance(vanilla_answer, str) else str(vanilla_answer or "")

    def _record_weak(model_id: str, reason: str) -> None:
        weak_matches.append({"model_id": model_id, "weak_match_reason": reason})

    for item in accepted_entries:
        model_id = coerce_str(item.get("model_id")).strip()
        presence_mode = coerce_str(item.get("presence_mode")).strip().lower()
        evidence_quote = coerce_str(item.get("evidence_quote")).strip()
        presence_explanation = coerce_str(item.get("presence_explanation")).strip()
        activation_strength = coerce_str(item.get("activation_strength")).strip().lower()
        why_not_merely_compatible = coerce_str(item.get("why_not_merely_compatible")).strip()
        if not model_id or model_id not in allowed_ids:
            continue
        if presence_mode not in {"executed", "violated"}:
            rejected.append({"model_id": model_id, "rejection_reason": "invalid_presence_mode"})
            continue
        if not (evidence_quote and evidence_quote in answer_text):
            rejected.append(
                {"model_id": model_id, "rejection_reason": "execution_quote_not_literal_substring"}
            )
            continue
        # Strict shared-rubric bar (PR-B v2). The verifier must explicitly
        # declare strength and explain the distinction-from-compatibility.
        # If either is missing/non-strong, demote — do not reward
        # under-specified acceptance.
        if activation_strength != "strong":
            _record_weak(model_id, "missing_or_non_strong_activation_strength")
            continue
        if not why_not_merely_compatible:
            _record_weak(model_id, "missing_why_not_merely_compatible")
            continue
        accepted.append(
            {
                "model_id": model_id,
                "presence_mode": presence_mode,
                "evidence_quote": evidence_quote,
                "presence_explanation": presence_explanation,
                "activation_strength": "strong",
                "why_not_merely_compatible": why_not_merely_compatible,
            }
        )

    for item in rejected_entries:
        model_id = coerce_str(item.get("model_id")).strip()
        rejection_reason = coerce_str(item.get("rejection_reason")).strip()
        if not model_id or model_id not in allowed_ids:
            continue
        rejected.append(
            {"model_id": model_id, "rejection_reason": rejection_reason or "rejected_without_reason"}
        )

    for item in weak_matches_entries:
        model_id = coerce_str(item.get("model_id")).strip()
        reason = coerce_str(item.get("weak_match_reason")).strip()
        if not model_id or model_id not in allowed_ids:
            continue
        # Allow LLM to put plausible-but-not-load-bearing items here directly,
        # without forcing a demotion through the accepted->weak path.
        weak_matches.append(
            {"model_id": model_id, "weak_match_reason": reason or "unspecified_weak_match"}
        )

    # Post-processing: passage exclusivity. If a broad overlay model shares a
    # substantially overlapping evidence_quote with a specific mechanism model
    # already in the accepted list, demote it — to weak_matches now (was
    # rejected pre-PR-B v2). The mechanism is plausibly present, just not
    # load-bearing once a more specific model has claimed the same passage.
    specific_quotes = [
        item["evidence_quote"]
        for item in accepted
        if item["model_id"] not in _BROAD_OVERLAY_MODELS
    ]
    final_accepted: list[dict[str, str]] = []
    for item in accepted:
        if item["model_id"] in _BROAD_OVERLAY_MODELS:
            if any(_quotes_overlap(item["evidence_quote"], sq) for sq in specific_quotes):
                _record_weak(item["model_id"], "broad_overlay_without_distinct_passage")
                continue
        final_accepted.append(item)

    return final_accepted, rejected, weak_matches


def _build_verification_system_prompt() -> str:
    return (
        "You are verifying whether candidate mental models are structurally present in a vanilla answer.\n"
        "\n"
        "THIS RUN IS PART OF A RANK-STRATIFIED PARTITIONED VERIFIER. You see one of 3 shards — a mixed slice of "
        "candidates spanning recall ranks (top, middle, tail) and cognitive types. Other shards are running in "
        "parallel. To preserve a global product budget under partition, you must apply a SHARED STRICT RUBRIC. "
        "Be deliberately conservative: when in doubt, downgrade to weak_matches; do NOT accept.\n"
        "\n"
        "SHARD BUDGET CALIBRATION (soft):\n"
        "Most shards should have 0-2 strong accepts. The total surface across the full run is capped at 5 detected "
        "models, so each shard's acceptance budget is roughly 1-2. If you mark 3+ candidates strong, EACH must have "
        "independent quoted evidence showing the assistant actually used that model's distinct mechanism — not "
        "similarity, adjacency, or compatibility. Otherwise route the third+ candidate to weak_matches with reason "
        "'compatible_but_not_executed' or 'more_specific_model_likely'. This is a calibration nudge, not a hard cap; "
        "if you genuinely see 3+ independently load-bearing models in this shard, mark them all strong with "
        "individual evidence.\n"
        "\n"
        "OUTPUT THREE CATEGORIES, NOT TWO:\n"
        "  1. accepted (strong only) — the model's specific mechanism is RUNNING in the answer with a literal evidence quote.\n"
        "  2. weak_matches — the model is plausibly compatible or topically adjacent, but the mechanism is not actually executed/violated.\n"
        "  3. rejected — the model is structurally off (wrong domain, wrong frame, no plausible connection).\n"
        "\n"
        "ACCEPTANCE BAR (strong only):\n"
        "An item enters `accepted` ONLY when ALL of these hold:\n"
        "  (a) `presence_mode` is exactly 'executed' or 'violated'.\n"
        "  (b) `evidence_quote` is a literal verbatim substring of the assistant's answer (not paraphrased).\n"
        "  (c) `activation_strength` is exactly 'strong' — meaning the answer's reasoning performs the model's mechanism, "
        "      not merely uses adjacent language or makes a judgment compatible with the model.\n"
        "  (d) `why_not_merely_compatible` names the SPECIFIC structural feature that distinguishes execution from compatibility: "
        "      what the answer is doing that a 'merely compatible' answer would NOT do.\n"
        "  (e) The acceptance survives the COMPETITION TEST: would a more specific model elsewhere explain the same passage better? "
        "      If yes, demote to weak_matches with reason 'more_specific_model_likely'.\n"
        "If ANY of (a)-(e) is uncertain, route to weak_matches. Do NOT borderline-accept.\n"
        "\n"
        "WEAK_MATCHES BAR:\n"
        "Use weak_matches when the model is in the right neighborhood but the mechanism is not executed:\n"
        "  - 'topic-adjacent' — answer mentions related ideas without using the model's mechanism.\n"
        "  - 'compatible_but_not_executed' — answer's reasoning is consistent with the model but doesn't perform it.\n"
        "  - 'broad_overlay_without_distinct_passage' — broad/overlay model whose passage is better explained by a more specific model.\n"
        "  - 'more_specific_model_likely' — there is plausibly a more specific model in another bucket that better fits this passage.\n"
        "  - 'name_or_vocabulary_only' — model's name or vocabulary appears but the mechanism is not executed.\n"
        "Weak matches stay audit-visible but do NOT enter the surfaced cheat sheet.\n"
        "\n"
        "BROAD-MODEL DEFAULT:\n"
        "These models default to weak_matches unless there is unmistakable evidence the answer's reasoning RUNS the mechanism: "
        "second-order-thinking, multi-criteria-decision-analysis, systems-thinking, power-laws, tier-2-high-value, butterfly-effect. "
        "For these, the bar for accepted is higher: the answer must perform the model's distinctive operation (not merely consider tradeoffs, "
        "not merely think about consequences, not merely classify value).\n"
        "\n"
        "PASSAGE EXCLUSIVITY:\n"
        "Even within a single bucket, a passage already cited by a specific-mechanism model in your accepted list MUST NOT also be claimed by "
        "a broad/overlay model. The broad model must find a distinct passage or be routed to weak_matches with reason 'broad_overlay_without_distinct_passage'.\n"
        "\n"
        "REJECT (not weak_matches):\n"
        "Reject only when the model is structurally off — wrong domain, wrong frame, no plausible connection at all. "
        "Anything plausible-but-not-load-bearing belongs in weak_matches, not rejected.\n"
        "\n"
        "Return ONLY valid JSON matching this exact structure and nothing else:\n"
        "{\n"
        '  "accepted": [\n'
        "    {\n"
        '      "model_id": "candidate-model-id",\n'
        '      "presence_mode": "executed | violated",\n'
        '      "evidence_quote": "exact literal substring from vanilla_answer",\n'
        '      "presence_explanation": "one sentence: how the mechanism is executed, or how the discipline is violated",\n'
        '      "activation_strength": "strong",\n'
        '      "why_not_merely_compatible": "one sentence naming the structural feature that distinguishes execution from compatibility"\n'
        "    }\n"
        "  ],\n"
        '  "weak_matches": [\n'
        "    {\n"
        '      "model_id": "candidate-model-id",\n'
        '      "weak_match_reason": "topic-adjacent | compatible_but_not_executed | broad_overlay_without_distinct_passage | more_specific_model_likely | name_or_vocabulary_only"\n'
        "    }\n"
        "  ],\n"
        '  "rejected": [\n'
        "    {\n"
        '      "model_id": "candidate-model-id",\n'
        '      "rejection_reason": "wrong-domain | wrong-frame | no-plausible-connection"\n'
        "    }\n"
        "  ]\n"
        "}\n"
        "\n"
        "Every accepted item must include all six fields above (model_id, presence_mode, evidence_quote, presence_explanation, "
        "activation_strength, why_not_merely_compatible). If activation_strength is anything other than 'strong', or if "
        "why_not_merely_compatible is missing or generic ('it's relevant', 'it applies'), the item will be auto-demoted to weak_matches.\n"
        "\n"
        "If nothing is accepted, return an empty `accepted` list. The same applies for `weak_matches` and `rejected`. "
        "Never return arrays of bare model ids. Never return strings.\n"
        "\n"
        "EXAMPLE — accepted (executed, strong):\n"
        '  model_id: "authority-bias"\n'
        '  presence_mode: "executed"\n'
        '  evidence_quote: "the account executive says the customer\'s CTO personally vouched for their internal security posture"\n'
        '  presence_explanation: "The answer treats a senior executive\'s personal attestation as sufficient assurance, instantiating authority-bias by substituting rank for independent evidence."\n'
        '  activation_strength: "strong"\n'
        '  why_not_merely_compatible: "The answer does not just acknowledge the CTO\'s opinion exists — it uses the CTO\'s rank as the load-bearing reason to skip independent verification, which is the precise mechanism authority-bias names."\n'
        "\n"
        "EXAMPLE — weak_match (broad overlay):\n"
        '  model_id: "second-order-thinking"\n'
        '  weak_match_reason: "broad_overlay_without_distinct_passage"\n'
        "  (commentary: the answer considers downstream implications, but the passage where it does so is already cited by a more specific model; second-order-thinking has no distinct passage of its own here.)\n"
        "\n"
        "EXAMPLE — weak_match (more specific model likely):\n"
        '  model_id: "tier-2-high-value"\n'
        '  weak_match_reason: "more_specific_model_likely"\n'
        "  (commentary: the answer makes a judgment about worth, but the structural error is better explained by a specific bias model in another reasoning-type bucket.)\n"
        "\n"
        "EXAMPLE — rejected (truly off):\n"
        '  model_id: "monte-carlo-methods"\n'
        '  rejection_reason: "wrong-domain"\n'
        "  (commentary: the answer concerns interpersonal trust, not stochastic simulation. No plausible connection.)"
    )


def get_prompt_templates() -> dict[str, str]:
    """Return the active companion lane prompt templates keyed by boundary name."""
    return {
        "companion_fingerprint": _build_fingerprint_system_prompt_from_context(),
        "companion_verification": _build_verification_system_prompt(),
    }


def retrieve_candidate_models(
    vanilla_answer: str,
    knowledge_graph: dict,
    max_candidates: int = 30,
) -> list[dict[str, str]]:
    # v0 uses deterministic keyword overlap against model activation fields until reviewed embedding retrieval is introduced.
    models = knowledge_graph.get("models", {})
    answer_tokens = _tokenize(vanilla_answer)
    ranked_candidates: list[tuple[int, str, str, str]] = []

    for model_id, model_payload in models.items():
        if not isinstance(model_payload, dict):
            continue

        activation_texts = list(_iter_activation_texts(model_payload))
        combined_tokens = set()
        for text in activation_texts:
            combined_tokens.update(_tokenize(text))

        overlap_score = len(answer_tokens & combined_tokens)
        ranked_candidates.append(
            (
                overlap_score,
                model_id,
                model_payload.get("display_name", model_id),
                _pick_activation_trigger(model_payload, fallback=model_id),
            )
        )

    ranked_candidates.sort(key=lambda item: (-item[0], item[2], item[1]))

    return [
        {
            "model_id": model_id,
            "model_name": model_name,
            "activation_trigger": activation_trigger,
        }
        for _, model_id, model_name, activation_trigger in ranked_candidates[:max_candidates]
    ]


def _primary_reasoning_type(model_payload: dict | None) -> str:
    """Extract `reasoning_types[0]` for a model, with `"unknown"` fallback.

    The verifier-partition substrate. Always single primary type for
    deterministic bucketing — list-aware bucketing is a deferred follow-up
    (see research/lane2-followup-tracking-2026-04-26.md open questions).
    """
    if not isinstance(model_payload, dict):
        return "unknown"
    types = model_payload.get("reasoning_types")
    if isinstance(types, list) and types:
        first = types[0]
        if isinstance(first, str) and first.strip():
            return first.strip()
    return "unknown"


def recall_candidates(
    *,
    assistant_text: str,
    fingerprint_payload: FingerprintPayload,
    knowledge_graph: dict,
    reasoning_signals: dict,
    max_candidates: int = 60,
    embedding_retriever=None,
    embedding_api_key: str = "",
) -> list[dict[str, object]]:
    """Build the Lane 2 candidate list fed into the verifier.

    Each returned candidate carries Lane 2 attribution metadata:
    - ``recall_source``: ``"keyword"`` | ``"embedding"`` | ``"both"``.
    - ``keyword_rank``: 1-indexed position in keyword recall, or ``None``.
    - ``embedding_rank``: 1-indexed position in embedding recall, or ``None``.
    - ``final_rank``: 1-indexed position in the returned list.
    - ``reasoning_type``: primary ``reasoning_types[0]`` from
      ``knowledge_graph.models[mid]``, fallback ``"unknown"`` when absent.
      Used by the partitioned verifier (PR-B) to bucket candidates.

    The "keyword" path covers both primary keyword overlap and the
    reasoning-signals fallback (both are deterministic). The "embedding"
    path is the optional ``embedding_retriever.rank_models_expanded`` route.

    Backwards-compatible: the verifier only reads ``model_id`` and
    ``model_name`` from each entry; new fields are additive.
    """
    models = knowledge_graph.get("models", {})
    if not isinstance(models, dict):
        return []

    fingerprint_texts = [move.reasoning_move for move in fingerprint_payload.validated]
    primary_texts = [assistant_text, *fingerprint_texts]
    ranked_primary: list[tuple[int, str, str, str]] = []

    for model_id, model_payload in models.items():
        if not isinstance(model_payload, dict):
            continue
        score = _rank_overlap(primary_texts, model_payload)
        if score <= 0:
            continue
        ranked_primary.append(
            (
                score,
                model_id,
                str(model_payload.get("display_name", model_id)),
                _pick_activation_trigger(model_payload, fallback=model_id),
            )
        )

    ranked_primary.sort(key=lambda item: (-item[0], item[2], item[1]))
    results: list[dict[str, object]] = []
    seen: set[str] = set()
    # Keyword rank counter — 1-indexed across the primary keyword pass and the
    # reasoning-signals fallback (both are deterministic keyword paths).
    keyword_rank_counter = 0

    for _, model_id, model_name, activation_trigger in ranked_primary:
        if model_id in seen:
            continue
        seen.add(model_id)
        keyword_rank_counter += 1
        mp = models.get(model_id, {})
        dw = mp.get("danger_when", []) if isinstance(mp, dict) else []
        results.append(
            {
                "model_id": model_id,
                "model_name": model_name,
                "activation_trigger": activation_trigger,
                "danger_when": dw[0] if isinstance(dw, list) and dw and isinstance(dw[0], str) else "",
                "recall_source": "keyword",
                "keyword_rank": keyword_rank_counter,
                "embedding_rank": None,
                "reasoning_type": _primary_reasoning_type(mp),
            }
        )
        if len(results) >= max_candidates:
            break

    if isinstance(reasoning_signals, dict) and len(results) < max_candidates:
        for model_id, signals in reasoning_signals.items():
            if model_id in seen or not isinstance(signals, list):
                continue
            signal_payload = {
                "display_name": models.get(model_id, {}).get("display_name", model_id) if isinstance(models.get(model_id, {}), dict) else model_id,
                "select_when": [item for item in signals if isinstance(item, str)],
            }
            score = _rank_overlap(primary_texts, signal_payload)
            if score <= 0:
                continue
            seen.add(model_id)
            keyword_rank_counter += 1
            sig_model = models.get(model_id, {})
            sig_dw = sig_model.get("danger_when", []) if isinstance(sig_model, dict) else []
            results.append(
                {
                    "model_id": model_id,
                    "model_name": str(signal_payload["display_name"]),
                    "activation_trigger": _pick_activation_trigger(signal_payload, fallback=model_id),
                    "recall_source": "keyword",
                    "keyword_rank": keyword_rank_counter,
                    "embedding_rank": None,
                    "reasoning_type": _primary_reasoning_type(sig_model),
                    "danger_when": sig_dw[0] if isinstance(sig_dw, list) and sig_dw and isinstance(sig_dw[0], str) else "",
                }
            )
            if len(results) >= max_candidates:
                break

    # --- Embedding recall path (swiss cheese: additive, never gating) ---
    # Guard `len(results) < max_candidates` preserves the pre-refactor behavior:
    # when keyword recall has already filled the cap, the embedding path does
    # not run. This avoids (a) untraced `rank_models_expanded` cost on cap-
    # saturated runs and (b) `recall_source="both"` metadata leakage that would
    # falsely imply embedding contributed when it was structurally prevented
    # from doing so. Whether embedding *should* be allowed to displace low-rank
    # keyword candidates when the cap is full is an open question deferred to
    # the post-attribution fix PR (see research/lane2-attribution-design-2026-04-26.md).
    if embedding_retriever is not None and embedding_api_key and len(results) < max_candidates:
        try:
            query_text = " ".join(primary_texts)
            ranked = embedding_retriever.rank_models_expanded(
                query_text, embedding_api_key, top_k=max_candidates,
            )
            if ranked:
                for emb_idx, hit in enumerate(ranked, start=1):
                    mid = hit["model_id"]
                    if mid in seen:
                        # Existing keyword candidate also surfaced by embedding:
                        # promote recall_source to "both" and record the
                        # embedding_rank for diagnosis.
                        for r in results:
                            if r["model_id"] == mid:
                                r["recall_source"] = "both"
                                if r.get("embedding_rank") is None:
                                    r["embedding_rank"] = emb_idx
                                break
                        continue
                    model_payload = models.get(mid)
                    if not isinstance(model_payload, dict):
                        continue
                    seen.add(mid)
                    emb_dw = model_payload.get("danger_when", [])
                    results.append(
                        {
                            "model_id": mid,
                            "model_name": str(model_payload.get("display_name", mid)),
                            "activation_trigger": _pick_activation_trigger(model_payload, fallback=mid),
                            "recall_source": "embedding",
                            "keyword_rank": None,
                            "embedding_rank": emb_idx,
                            "reasoning_type": _primary_reasoning_type(model_payload),
                            "danger_when": emb_dw[0] if isinstance(emb_dw, list) and emb_dw and isinstance(emb_dw[0], str) else "",
                        }
                    )
                    if len(results) >= max_candidates:
                        break
        except Exception:
            _LOGGER.warning("embedding_recall: failed in companion recall", exc_info=True)

    capped = results[:max_candidates]
    for idx, candidate in enumerate(capped, start=1):
        candidate["final_rank"] = idx
    return capped


def parse_detection_response(
    raw_payload: dict,
    candidates: list[dict[str, str]],
) -> list[DetectedModel]:
    detections = raw_payload.get("detections", [])
    if not isinstance(detections, list):
        return []

    candidate_names = {
        item["model_id"]: item["model_name"]
        for item in candidates
        if item.get("model_id") and item.get("model_name")
    }

    parsed: list[DetectedModel] = []
    for item in detections:
        if not isinstance(item, dict):
            continue
        model_id = str(item.get("model_id", "")).strip()
        if not model_id or model_id not in candidate_names:
            continue
        evidence = str(item.get("reasoning_evidence", "")).strip()
        raw_confidence = str(item.get("detection_confidence", "")).strip().lower()
        confidence = raw_confidence if raw_confidence in {"structural", "partial"} else "partial"
        if not evidence:
            confidence = "partial"
        parsed.append(
            DetectedModel(
                model_id=model_id,
                model_name=candidate_names[model_id],
                evidence_quote=evidence,
                presence_mode="executed",
                presence_explanation=evidence,
                detection_confidence=confidence,
            )
        )
    return parsed


def _build_detection_system_prompt() -> str:
    return (
        "You are identifying which candidate mental models are structurally present in a vanilla answer. "
        "Read how the answer reasons, not what topic it mentions. "
        "Return JSON with a top-level 'detections' list. "
        "Each detection must include 'model_id', 'reasoning_evidence', and optional "
        "'detection_confidence' ('structural' or 'partial'). "
        "Only include a model when the reasoning pattern is structurally present in the answer."
    )


def _build_detection_user_prompt(
    vanilla_answer: str,
    candidates: list[dict[str, str]],
) -> str:
    candidate_lines = []
    for candidate in candidates:
        candidate_lines.append(
            "- {model_id} | {model_name} | activation: {activation_trigger}".format(
                model_id=candidate["model_id"],
                model_name=candidate["model_name"],
                activation_trigger=candidate["activation_trigger"],
            )
        )
    return "\n".join(
        [
            "Vanilla answer:",
            vanilla_answer.strip(),
            "",
            "Candidate models:",
            "\n".join(candidate_lines),
            "",
            "Return only the models whose reasoning pattern is structurally present in the answer.",
        ]
    )


def run_companion_detection(
    vanilla_answer: str,
    candidates: list[dict[str, str]],
    client,
) -> list[DetectedModel]:
    if not candidates:
        return []

    system_prompt = _build_detection_system_prompt()
    user_prompt = _build_detection_user_prompt(vanilla_answer, candidates)
    raw_payload = client.run_json(system_prompt, user_prompt)
    detections = parse_detection_response(raw_payload, candidates)

    def sort_key(item: DetectedModel) -> tuple[int, str]:
        return (0 if item.detection_confidence == "structural" else 1, item.model_name.lower())

    return sorted(detections, key=sort_key)[:5]


def _is_substantive_chunk(text: str) -> bool:
    stripped = str(text or "").strip()
    if not stripped:
        return False
    if stripped.startswith("#"):
        return False
    words = stripped.split()
    if len(words) < 6:
        return False
    return True


def _one_sentence_for_hint(description: str) -> str:
    """Compress failure mode description to a single sentence for compact card output."""
    stripped = " ".join(str(description).split())
    if not stripped:
        return ""
    match = re.match(r"^(.+?[.!?])(?:\s+|$)", stripped)
    if match:
        return match.group(1).strip()
    if len(stripped) <= 240:
        return stripped
    return stripped[:237].rstrip() + "…"


def _failure_mode_sort_key(failure_mode: dict) -> tuple[int, int, str]:
    conf = str(failure_mode.get("confidence", "")).strip().lower()
    conf_rank = {"high": 0, "medium": 1, "low": 2}.get(conf, 3)
    ext = str(failure_mode.get("extraction_type", "")).strip().lower()
    ext_rank = 0 if ext == "explicit" else 1
    mode_id = str(failure_mode.get("mode", "")).strip()
    return (conf_rank, ext_rank, mode_id)


def collect_failure_hints_for_model(
    model_id: str,
    knowledge_graph: dict,
    *,
    max_hints: int = 2,
) -> list[CompanionFailureHint]:
    if max_hints <= 0:
        return []

    models = knowledge_graph.get("models", {})
    payload = models.get(model_id, {})
    if not isinstance(payload, dict):
        return []

    raw_modes = payload.get("failure_modes", [])
    if not isinstance(raw_modes, list):
        return []

    candidates: list[dict] = []
    for item in raw_modes:
        if not isinstance(item, dict):
            continue
        description = str(item.get("description", "")).strip()
        if not _is_substantive_chunk(description):
            continue
        candidates.append(item)

    candidates.sort(key=_failure_mode_sort_key)

    hints: list[CompanionFailureHint] = []
    for failure_mode in candidates[:max_hints]:
        description = str(failure_mode.get("description", "")).strip()
        text = _one_sentence_for_hint(description)
        if not text:
            continue
        extraction_type = str(failure_mode.get("extraction_type", "")).strip() or "unknown"
        confidence = str(failure_mode.get("confidence", "")).strip() or "unknown"
        hints.append(
            CompanionFailureHint(
                source_model_id=model_id,
                text=text,
                extraction_type=extraction_type,
                confidence=confidence,
            )
        )
        if len(hints) >= max_hints:
            break

    return hints


def _intervention_sort_key(item: dict) -> tuple[int, int, str]:
    """Sort intervention items (heuristics, premortems) by confidence then extraction type."""
    conf = str(item.get("confidence", "")).strip().lower()
    conf_rank = {"high": 0, "medium": 1, "low": 2}.get(conf, 3)
    ext = str(item.get("extraction_type", "")).strip().lower()
    ext_rank = 0 if ext == "explicit" else 1
    label = str(item.get("description", "")).strip()[:40]
    return (conf_rank, ext_rank, label)


def collect_heuristics_for_model(
    model_id: str,
    knowledge_graph: dict,
    *,
    max_hints: int = 2,
) -> list[CompanionHeuristicHint]:
    if max_hints <= 0:
        return []

    models = knowledge_graph.get("models", {})
    payload = models.get(model_id, {})
    if not isinstance(payload, dict):
        return []

    raw_items = payload.get("heuristics", [])
    if not isinstance(raw_items, list):
        return []

    candidates: list[dict] = []
    for item in raw_items:
        if not isinstance(item, dict):
            continue
        description = str(item.get("description", "")).strip()
        if not _is_substantive_chunk(description):
            continue
        candidates.append(item)

    candidates.sort(key=_intervention_sort_key)

    hints: list[CompanionHeuristicHint] = []
    for item in candidates[:max_hints]:
        description = str(item.get("description", "")).strip()
        text = _one_sentence_for_hint(description)
        if not text:
            continue
        extraction_type = str(item.get("extraction_type", "")).strip() or "unknown"
        confidence = str(item.get("confidence", "")).strip() or "unknown"
        hints.append(
            CompanionHeuristicHint(
                source_model_id=model_id,
                text=text,
                extraction_type=extraction_type,
                confidence=confidence,
            )
        )
        if len(hints) >= max_hints:
            break

    return hints


def collect_premortem_questions_for_model(
    model_id: str,
    knowledge_graph: dict,
    *,
    max_hints: int = 2,
) -> list[CompanionPremortermHint]:
    if max_hints <= 0:
        return []

    models = knowledge_graph.get("models", {})
    payload = models.get(model_id, {})
    if not isinstance(payload, dict):
        return []

    raw_items = payload.get("premortem_questions", [])
    if not isinstance(raw_items, list):
        return []

    candidates: list[dict] = []
    for item in raw_items:
        if not isinstance(item, dict):
            continue
        description = str(item.get("description", "")).strip()
        if not _is_substantive_chunk(description):
            continue
        candidates.append(item)

    candidates.sort(key=_intervention_sort_key)

    hints: list[CompanionPremortermHint] = []
    for item in candidates[:max_hints]:
        description = str(item.get("description", "")).strip()
        text = _one_sentence_for_hint(description)
        if not text:
            continue
        extraction_type = str(item.get("extraction_type", "")).strip() or "unknown"
        confidence = str(item.get("confidence", "")).strip() or "unknown"
        hints.append(
            CompanionPremortermHint(
                source_model_id=model_id,
                text=text,
                extraction_type=extraction_type,
                confidence=confidence,
            )
        )
        if len(hints) >= max_hints:
            break

    return hints


def collect_identity_for_model(
    model_id: str,
    knowledge_graph: dict,
) -> CompanionIdentityChunk | None:
    models = knowledge_graph.get("models", {})
    if model_id not in models:
        return None
    payload = models[model_id]
    if not isinstance(payload, dict):
        return None

    display_name = str(payload.get("display_name", model_id)).strip()
    select_when = payload.get("select_when", [])
    if not isinstance(select_when, list):
        select_when = []
    danger_when = payload.get("danger_when", [])
    if not isinstance(danger_when, list):
        danger_when = []
    reasoning_types = payload.get("reasoning_types", [])
    if not isinstance(reasoning_types, list):
        reasoning_types = []
    input_type = str(payload.get("input_type", "")).strip()
    output_type = str(payload.get("output_type", "")).strip()

    return CompanionIdentityChunk(
        model_id=model_id,
        display_name=display_name,
        select_when=tuple(str(s).strip() for s in select_when if isinstance(s, str) and str(s).strip()),
        danger_when=tuple(str(s).strip() for s in danger_when if isinstance(s, str) and str(s).strip()),
        reasoning_types=tuple(str(s).strip() for s in reasoning_types if isinstance(s, str) and str(s).strip()),
        input_type=input_type,
        output_type=output_type,
    )


def _iter_relation_edges(relation_graph: dict) -> Iterable[dict]:
    if isinstance(relation_graph, list):
        for edge in relation_graph:
            if isinstance(edge, dict):
                yield edge
        return

    if isinstance(relation_graph, dict):
        edges = relation_graph.get("edges", [])
        if isinstance(edges, list):
            for edge in edges:
                if isinstance(edge, dict):
                    yield edge


def expand_detected_model(
    model_id: str,
    knowledge_graph: dict,
    relation_graph: dict,
    max_expansions: int = 3,
) -> list[CompanionExpansion]:
    if max_expansions <= 0:
        return []

    models = knowledge_graph.get("models", {})
    source_model = models.get(model_id, {})
    if not isinstance(source_model, dict):
        return []

    expansions: list[CompanionExpansion] = []

    edge_priority = {"antagonist": 1, "tension": 1, "ally": 2, "compound": 3}
    sorted_edges = sorted(
        (
            edge
            for edge in _iter_relation_edges(relation_graph)
            if str(edge.get("source_model_id", "")).strip() == model_id
            and str(edge.get("edge_type", "")).strip().lower() in edge_priority
        ),
        key=lambda edge: (
            edge_priority[str(edge.get("edge_type", "")).strip().lower()],
            str(edge.get("target_model_id", "")).strip(),
        ),
    )

    for edge in sorted_edges:
        edge_type = str(edge.get("edge_type", "")).strip().lower()
        target_model_id = str(edge.get("target_model_id", "")).strip()
        target_model = models.get(target_model_id, {})
        if not target_model_id or not isinstance(target_model, dict):
            continue

        description = str(edge.get("source_description", "")).strip()
        if not _is_substantive_chunk(description):
            continue

        relation_type = {
            "antagonist": "antagonist",
            "tension": "tension",
            "ally": "ally",
            "compound": "adjacent_protocol",
        }[edge_type]

        why_relevant = description

        expansions.append(
            CompanionExpansion(
                source_model_id=model_id,
                relation_type=relation_type,
                model_id=target_model_id,
                model_name=str(target_model.get("display_name", target_model_id)),
                substrate_chunk=description,
                why_relevant=why_relevant,
                tension_type=str(edge.get("tension_type", "conflicts")) if edge_type == "tension" else None,
                affinity_rationale=str(edge.get("affinity_rationale", "") or ""),
                activation_condition=str(edge.get("activation_condition", "") or ""),
            )
        )
        if len(expansions) >= max_expansions:
            break

    return expansions[:max_expansions]
