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


def _bucket_candidates_by_reasoning_type(
    candidates: list[dict[str, object]],
) -> dict[str, list[dict[str, object]]]:
    """Partition candidates by ``reasoning_type`` (primary, single bucket per
    candidate). Empty buckets are not present in the returned dict.

    Iteration order of buckets is the order each bucket first appeared in the
    candidate list — gives a stable, deterministic submission order to the
    parallel executor regardless of run-to-run set order.
    """
    buckets: dict[str, list[dict[str, object]]] = {}
    for c in candidates:
        bucket_id = str(c.get("reasoning_type") or "unknown")
        buckets.setdefault(bucket_id, []).append(c)
    return buckets


def _run_verifier_single_bucket(
    *,
    bucket_id: str,
    packet: Lane4Packet,
    fingerprint_payload: FingerprintPayload,
    bucket_candidates: list[dict[str, object]],
    assistant_text: str,
    candidate_ids: set[str],
    client,
    use_metadata: bool,
):
    """Run one verifier LLM call for a single reasoning-type bucket.

    Returns ``(accepted_items, rejected_items, BoundaryCallTrace)``. When
    ``use_metadata`` is True, uses ``client.run_json_with_metadata`` (thread-
    safe; required for parallel execution). When False, falls back to
    ``client.run_json`` + ``_capture_boundary_call`` (sequential test mocks).
    """
    user_prompt = _build_verification_user_prompt_from_packet(
        packet, fingerprint_payload, bucket_candidates
    )
    system_prompt = _build_verification_system_prompt()
    stage = f"companion_verification_{bucket_id}"
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
    list["BoundaryCallTrace"],
]:
    """Packet-driven Lane 2 verification call — reasoning-type partitioned (PR-B).

    Partitions ``candidates`` by primary ``reasoning_type`` (attached during
    recall — see ``_primary_reasoning_type``), runs one verifier LLM call per
    non-empty bucket in parallel (mirrors Pass 1 family-cluster pattern), and
    fans in deterministically. Each per-bucket call sees the FULL assistant
    source text and FULL validated fingerprint — only the candidates are
    bucket-local. No information loss; obligation narrowed.

    The pre-registered fan-in ordering (deterministic, independent of which
    bucket finishes first):

    1. Concatenate accepted lists from every bucket in stable bucket-iteration
       order (which itself is the order each bucket first appeared in
       ``candidates``).
    2. Dedupe by ``model_id`` — first valid occurrence wins, surplus go into
       ``duplicate_accepts`` (NOT into ``rejected_models``; that would corrupt
       ``telemetry.verification_precision``).
    3. Sort the deduped accepted list by ``(candidate.final_rank, model_id)``.
       This is a ranking-semantics change vs. pre-PR-B (which preserved LLM
       output order); it is a corrective architecture change explicitly
       authorized by research/lane2-followup-tracking-2026-04-26.md, and the
       acceptance gates in the same doc require it.
    4. Apply the existing top-5 surfacing budget. Overflow lands in
       ``capped_models``.

    Returns a 6-tuple: ``(detected_models, rejected_models,
    accepted_before_cap, capped_models, duplicate_accepts, boundary_traces)``.
    The added 6th element is one ``BoundaryCallTrace`` per bucket call so the
    pipeline can extend ``audit_summary.boundary_calls`` cleanly and per-
    bucket cost is measurable. Falls back to sequential execution when the
    boundary client doesn't expose ``run_json_with_metadata`` (test mocks).
    """
    if not candidates:
        return [], [], [], [], [], [], []

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

    buckets = _bucket_candidates_by_reasoning_type(candidates)

    # Determine execution mode. Parallel requires `run_json_with_metadata` and
    # the explicit `supports_parallel_calls` opt-in. Test mocks typically have
    # neither, so they route through the sequential path automatically.
    use_metadata = (
        hasattr(client, "run_json_with_metadata")
        and getattr(client, "supports_parallel_calls", False)
    )

    per_bucket_results: list[tuple[str, list[dict], list[dict], list[dict], BoundaryCallTrace]] = []

    if use_metadata and len(buckets) > 1:
        max_workers = min(len(buckets), 9)  # 9 is the substrate's reasoning_types ceiling
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for bucket_id, bucket_cands in buckets.items():
                bucket_ids = {c["model_id"] for c in bucket_cands if c.get("model_id")}
                fut = executor.submit(
                    _run_verifier_single_bucket,
                    bucket_id=bucket_id,
                    packet=packet,
                    fingerprint_payload=fingerprint_payload,
                    bucket_candidates=bucket_cands,
                    assistant_text=assistant_text,
                    candidate_ids=bucket_ids,
                    client=client,
                    use_metadata=True,
                )
                futures.append((bucket_id, fut))
        for bucket_id, fut in futures:
            accepted, rejected, bucket_weak, trace = fut.result()
            per_bucket_results.append((bucket_id, accepted, rejected, bucket_weak, trace))
    else:
        # Sequential path: single-bucket cases, test mocks, or boundary clients
        # that don't support parallel calls.
        for bucket_id, bucket_cands in buckets.items():
            bucket_ids = {c["model_id"] for c in bucket_cands if c.get("model_id")}
            accepted, rejected, bucket_weak, trace = _run_verifier_single_bucket(
                bucket_id=bucket_id,
                packet=packet,
                fingerprint_payload=fingerprint_payload,
                bucket_candidates=bucket_cands,
                assistant_text=assistant_text,
                candidate_ids=bucket_ids,
                client=client,
                use_metadata=use_metadata,
            )
            per_bucket_results.append((bucket_id, accepted, rejected, bucket_weak, trace))

    # Fan-in step 1: concatenate in deterministic bucket-iteration order.
    raw_accepted: list[dict] = []
    rejected: list[dict] = []
    weak_matches: list[dict] = []
    boundary_traces: list[BoundaryCallTrace] = []
    for _, accepted, bucket_rejected, bucket_weak, trace in per_bucket_results:
        raw_accepted.extend(accepted)
        rejected.extend(bucket_rejected)
        weak_matches.extend(bucket_weak)
        boundary_traces.append(trace)

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
        boundary_traces,
    )


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
        "THIS RUN IS PART OF A PARTITIONED VERIFIER. You see only the candidates from one reasoning-type bucket. "
        "Other buckets are running in parallel. To preserve a global product budget without per-bucket competition, "
        "you must apply a SHARED STRICT RUBRIC. Be deliberately conservative: when in doubt, downgrade to weak_matches; "
        "do NOT accept.\n"
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
