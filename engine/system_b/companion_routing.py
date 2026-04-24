from __future__ import annotations

import logging
import re
from collections.abc import Iterable

_LOGGER = logging.getLogger("system_b.companion_routing")

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


def _build_fingerprint_system_prompt() -> str:
    return (
        "You are extracting reasoning moves from a vanilla answer. "
        "Return strict JSON with a top-level 'reasoning_moves' list. "
        "Each move must include move_id, reasoning_move, evidence_quotes, evidence_rationale, and confidence. "
        "Do not name mental models. Describe abstract reasoning moves only.\n\n"
        "CRITICAL RULE FOR evidence_quotes:\n"
        "Every evidence_quotes entry must be a LITERAL SUBSTRING copied character-for-character "
        "from the vanilla answer text. It must pass a simple `quote in vanilla_answer` check. "
        "Do NOT paraphrase, summarize, compress, or combine multiple passages into one quote. "
        "If a reasoning move spans multiple passages, include each passage as a SEPARATE entry "
        "in the evidence_quotes array. Each entry must be a verbatim contiguous substring. "
        "Quotes that are not literal substrings will be rejected by the validation layer."
    )


def _build_fingerprint_user_prompt(query: str, vanilla_answer: str) -> str:
    return "\n".join(
        [
            "Query:",
            query.strip(),
            "",
            "Vanilla answer:",
            vanilla_answer.strip(),
            "",
            "Extract 3-8 reasoning moves from the answer. "
            "Each move must be supported by exact quotes copied from the answer. "
            "Remember: every evidence_quotes entry must be a literal contiguous substring "
            "from the vanilla answer above — not a paraphrase or summary.",
        ]
    )


def _joined_assistant_turns(context: ConversationContext) -> str:
    """Flat string of assistant turns for substring validation + keyword recall.

    Used by all Lane 2 `_from_context` entry points so fingerprint + verification
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


def _build_fingerprint_user_prompt_from_context(context: ConversationContext) -> str:
    ext = context.extraction
    parts: list[str] = [
        "CONTEXT (background — NOT the audit target; use to understand what the user made live):",
    ]
    if ext.decision_situation:
        parts.append(f"- Decision situation: {ext.decision_situation}")
    if ext.original_framing:
        parts.append(f"- Framing: {ext.original_framing}")
    if ext.live_constraints:
        parts.append("- Live constraints:")
        for c in ext.live_constraints:
            status = (c.status or "active").upper()
            weight = (c.weight or "situational").upper()
            tag = status if status == "ACTIVE" else f"{status}/{weight}"
            parts.append(f"  - [{tag}] {c.constraint} (turn {c.introduced_turn})")
    if ext.dropped_threads:
        parts.append("- Dropped threads:")
        for d in ext.dropped_threads:
            line = (
                f"  - {d.thread} (raised by {d.raised_by or '?'} turn {d.raised_turn}, "
                f"status: {d.status or '?'})"
            )
            if d.superseded_by:
                line += f", superseded_by: {d.superseded_by}"
            parts.append(line)
    user_turns = [t for t in context.turns if t.speaker == "user"]
    if user_turns:
        parts.append("- User turns (CONTEXT only):")
        for t in user_turns:
            parts.append(f"  [Turn {t.turn_index}] USER: {t.text}")
    parts.append("")
    parts.append(
        "SOURCE (assistant turns — extract reasoning moves from HERE; evidence quotes MUST be literal substrings of this section):"
    )
    assistant_turns = [t for t in context.turns if t.speaker == "assistant"]
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


def run_fingerprint_call_from_context(
    *,
    context: ConversationContext,
    client,
) -> FingerprintPayload:
    """Phase 2d conversation-first fingerprint call.

    Validates evidence quotes against joined assistant turns (not legacy
    vanilla_answer). Otherwise identical behavior to `run_fingerprint_call`.
    """
    assistant_text = _joined_assistant_turns(context)
    raw_payload = client.run_json(
        _build_fingerprint_system_prompt_from_context(),
        _build_fingerprint_user_prompt_from_context(context),
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


def _build_verification_user_prompt_from_context(
    context: ConversationContext,
    fingerprint_payload: FingerprintPayload,
    candidates: list[dict[str, str]],
) -> str:
    ext = context.extraction
    parts: list[str] = [
        "CONTEXT (background — what the user made live; NOT quotable as evidence):",
    ]
    if ext.decision_situation:
        parts.append(f"- Decision situation: {ext.decision_situation}")
    if ext.original_framing:
        parts.append(f"- Framing: {ext.original_framing}")
    if ext.live_constraints:
        parts.append("- Live constraints:")
        for c in ext.live_constraints:
            status = (c.status or "active").upper()
            weight = (c.weight or "situational").upper()
            tag = status if status == "ACTIVE" else f"{status}/{weight}"
            parts.append(f"  - [{tag}] {c.constraint} (turn {c.introduced_turn})")
    user_turns = [t for t in context.turns if t.speaker == "user"]
    if user_turns:
        parts.append("- User turns (CONTEXT only):")
        for t in user_turns:
            parts.append(f"  [Turn {t.turn_index}] USER: {t.text}")
    parts.append("")
    parts.append(
        "SOURCE (assistant turns — evidence_quote for each accepted model MUST be a literal substring of this section):"
    )
    assistant_turns = [t for t in context.turns if t.speaker == "assistant"]
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


def run_verification_call_from_context(
    *,
    context: ConversationContext,
    fingerprint_payload: FingerprintPayload,
    candidates: list[dict[str, str]],
    client,
) -> tuple[list[DetectedModel], list[dict[str, str]]]:
    """Phase 2d conversation-first verification call.

    Validates evidence quotes against joined assistant turns. Otherwise
    identical behavior to `run_verification_call`.
    """
    if not candidates:
        return [], []

    assistant_text = _joined_assistant_turns(context)
    raw_payload = client.run_json(
        _build_verification_system_prompt(),
        _build_verification_user_prompt_from_context(context, fingerprint_payload, candidates),
    )
    accepted, rejected = parse_verification_response(
        raw_payload,
        assistant_text,
        {candidate["model_id"] for candidate in candidates},
    )
    candidate_names = {
        candidate["model_id"]: candidate["model_name"]
        for candidate in candidates
        if candidate.get("model_id") and candidate.get("model_name")
    }
    detected_models = [
        DetectedModel(
            model_id=item["model_id"],
            model_name=candidate_names.get(item["model_id"], item["model_id"]),
            evidence_quote=item.get("evidence_quote", ""),
            presence_mode=item.get("presence_mode", "executed"),
            presence_explanation=item.get("presence_explanation", ""),
            detection_confidence="structural",
        )
        for item in accepted
    ]
    detected_models = detected_models[:5]
    return detected_models, rejected


def run_fingerprint_call(
    *,
    query: str,
    vanilla_answer: str,
    client,
) -> FingerprintPayload:
    raw_payload = client.run_json(
        _build_fingerprint_system_prompt(),
        _build_fingerprint_user_prompt(query, vanilla_answer),
    )
    fingerprint = parse_fingerprint_response(raw_payload, vanilla_answer)
    validated = sorted(
        fingerprint.validated,
        key=lambda item: (0 if item.confidence == "high" else 1, item.move_id),
    )[:8]
    return FingerprintPayload(
        raw=fingerprint.raw,
        validated=validated,
        dropped=fingerprint.dropped,
    )


def parse_verification_response(
    raw_payload: dict,
    vanilla_answer: str,
    candidate_ids: set[str] | list[str] | tuple[str, ...],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    allowed_ids = {str(item).strip() for item in candidate_ids if str(item).strip()}
    accepted_entries = require_list_of_dicts(raw_payload, "accepted", "companion_verification")
    rejected_entries = require_list_of_dicts(raw_payload, "rejected", "companion_verification")
    accepted: list[dict[str, str]] = []
    rejected: list[dict[str, str]] = []
    answer_text = vanilla_answer if isinstance(vanilla_answer, str) else str(vanilla_answer or "")

    for item in accepted_entries:
        model_id = coerce_str(item.get("model_id")).strip()
        presence_mode = coerce_str(item.get("presence_mode")).strip().lower()
        evidence_quote = coerce_str(item.get("evidence_quote")).strip()
        presence_explanation = coerce_str(item.get("presence_explanation")).strip()
        if not model_id or model_id not in allowed_ids:
            continue
        if presence_mode not in {"executed", "violated"}:
            rejected.append(
                {
                    "model_id": model_id,
                    "rejection_reason": "invalid_presence_mode",
                }
            )
            continue
        if evidence_quote and evidence_quote in answer_text:
            accepted.append(
                {
                    "model_id": model_id,
                    "presence_mode": presence_mode,
                    "evidence_quote": evidence_quote,
                    "presence_explanation": presence_explanation,
                }
            )
            continue
        rejected.append(
            {
                "model_id": model_id,
                "rejection_reason": "execution_quote_not_literal_substring",
            }
        )

    for item in rejected_entries:
        model_id = coerce_str(item.get("model_id")).strip()
        rejection_reason = coerce_str(item.get("rejection_reason")).strip()
        if not model_id or model_id not in allowed_ids:
            continue
        rejected.append(
            {
                "model_id": model_id,
                "rejection_reason": rejection_reason or "rejected_without_reason",
            }
        )

    # Post-processing: if a broad overlay model shares a substantially overlapping
    # evidence_quote with a specific mechanism model already in the accepted list,
    # demote it to rejected. Broad models must find their own distinct passage.
    specific_quotes = [
        item["evidence_quote"]
        for item in accepted
        if item["model_id"] not in _BROAD_OVERLAY_MODELS
    ]
    final_accepted: list[dict[str, str]] = []
    for item in accepted:
        if item["model_id"] in _BROAD_OVERLAY_MODELS:
            if any(_quotes_overlap(item["evidence_quote"], sq) for sq in specific_quotes):
                rejected.append(
                    {
                        "model_id": item["model_id"],
                        "rejection_reason": "passage claimed by more specific model",
                    }
                )
                continue
        final_accepted.append(item)

    return final_accepted, rejected


def _build_verification_system_prompt() -> str:
    return (
        "You are verifying whether candidate mental models are structurally present in a vanilla answer.\n"
        "A model may be ACCEPTED in exactly two ways: executed or violated.\n"
        "ACCEPT as EXECUTED only if the answer applies the model's specific mechanism and you can quote the exact passage where the mechanism runs.\n"
        "ACCEPT as VIOLATED only if the answer explicitly deploys a substitute mechanism the model guards against, and you can quote that substitute mechanism directly from the answer.\n"
        "REJECT a model if the answer is merely compatible with it.\n"
        "REJECT a model if the evidence only shows broad good reasoning, problem decomposition, or multi-factor thinking.\n"
        "REJECT a model if the model's name or vocabulary appears without the mechanism being executed or violated.\n"
        "REJECT a violated-mode claim if the answer simply omits the discipline rather than substituting an alternative.\n"
        "Broad models that must be actively declined unless specifically executed or violated: second-order-thinking, multi-criteria-decision-analysis, systems-thinking, power-laws, tier-2-high-value, butterfly-effect.\n"
        "CRITICAL for tier-2-high-value: the model is EXECUTED only when the answer's own reasoning performs a value-tier classification AND uses that classification as the central decision mechanism. "
        "Reject if another specific model (authority-bias, reciprocity-principle, liking-loving, etc.) already explains the structural error — tier-2-high-value is background context, not the read. "
        "Reject if the answer merely describes something as valuable, strategic, or high-priority — compatibility is not execution. "
        "Reject if the 'value tier' language comes from an external party (e.g., the vendor calling the company 'tier-one') rather than from the answer's own reasoning.\n"
        "Return ONLY valid JSON matching this exact structure and nothing else:\n"
        "{\n"
        '  "accepted": [\n'
        "    {\n"
        '      "model_id": "candidate-model-id",\n'
        '      "presence_mode": "executed | violated",\n'
        '      "evidence_quote": "exact literal substring from vanilla_answer",\n'
        '      "presence_explanation": "one sentence: how the mechanism is executed, or how the discipline is violated"\n'
        "    }\n"
        "  ],\n"
        '  "rejected": [\n'
        "    {\n"
        '      "model_id": "candidate-model-id",\n'
        '      "rejection_reason": "too generic | topic-adjacent | mechanism absent | omission not violation"\n'
        "    }\n"
        "  ]\n"
        "}\n"
        "Never return arrays of bare model ids. Every accepted item must be an object with model_id, presence_mode, evidence_quote, and presence_explanation. "
        "Every rejected item must be an object with model_id and rejection_reason. "
        "If nothing is accepted or rejected, return empty lists, not strings and not model-id arrays.\n"
        "EXAMPLE — executed:\n"
        '  model_id: "authority-bias"\n'
        '  presence_mode: "executed"\n'
        '  evidence_quote: "the account executive says the customer\'s CTO personally vouched for their internal security posture"\n'
        '  presence_explanation: "The answer treats a senior executive\'s personal attestation as sufficient assurance, instantiating authority-bias by substituting rank for independent evidence."\n'
        "\n"
        "EXAMPLE — violated:\n"
        '  model_id: "scientific-method-evidence-testing"\n'
        '  presence_mode: "violated"\n'
        '  evidence_quote: "The CTO\'s personal vouching for their security posture provides reasonable assurance"\n'
        '  presence_explanation: "The answer accepts credentialed attestation as a substitute for independent technical verification, directly violating the discipline scientific-method-evidence-testing exists to enforce."\n'
        "\n"
        "TIE-BREAKER RULE: when high-value opportunity language and rank-backed assurance appear in the same passage, ask: is the decisive epistemic move (a) classifying this as top-tier value, or (b) treating a credentialed person's say-so as sufficient? "
        "If rank or credential is doing the justificatory work, authority-bias is correct and tier-2-high-value must be rejected as coincident framing — even if value language is also present in the same sentence. "
        "Only accept tier-2-high-value when the value-tier classification itself — not rank, not credential — is the mechanism that drives the decision.\n"
        "\n"
        "PASSAGE EXCLUSIVITY RULE: if a specific mechanism model (authority-bias, reciprocity-principle, liking-loving, etc.) already cites a passage, a broad overlay model (tier-2-high-value, second-order-thinking, systems-thinking, power-laws) MUST NOT cite the same or substantially overlapping passage. "
        "The broad model must find a distinct passage that exclusively instantiates its own mechanism, or it must be rejected. "
        "Piggybacking on a passage already used by a specific model is not acceptance — it is rejection with reason 'passage already claimed by more specific model'.\n"
        "\n"
        "EXAMPLE — rejected (broad model):\n"
        '  model_id: "second-order-thinking"\n'
        '  rejection_reason: "too generic — the answer considers downstream implications but does not specifically apply second-order causal chain analysis; compatible but not executed or violated"\n'
        "\n"
        "EXAMPLE — rejected (broad strategic overlay):\n"
        '  model_id: "tier-2-high-value"\n'
        '  rejection_reason: "too generic — the answer mentions value or makes a judgment about worth, but does not specifically apply the mechanism of identifying top-tier value opportunities and concentrating attention there; framing-level mention is not execution"'
    )


def get_prompt_templates() -> dict[str, str]:
    """Return companion lane prompt templates keyed by boundary name."""
    return {
        "companion_fingerprint": _build_fingerprint_system_prompt(),
        "companion_verification": _build_verification_system_prompt(),
    }


def _build_verification_user_prompt(
    vanilla_answer: str,
    fingerprint_payload: FingerprintPayload,
    candidates: list[dict[str, str]],
) -> str:
    fingerprint_lines = [
        "- {move_id} | {reasoning_move} | quotes: {quotes}".format(
            move_id=move.move_id,
            reasoning_move=move.reasoning_move,
            quotes=" | ".join(move.evidence_quotes),
        )
        for move in fingerprint_payload.validated
    ]
    candidate_lines = []
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
    return "\n".join(
        [
            "Vanilla answer:",
            vanilla_answer.strip(),
            "",
            "Validated fingerprint moves:",
            "\n".join(fingerprint_lines) if fingerprint_lines else "(none)",
            "",
            "Candidate models:",
            "\n".join(candidate_lines),
            "",
            "Return ONLY the JSON object described in the system prompt. "
            "Do not return arrays of model ids. "
            "Use exact evidence quotes copied from the vanilla answer for every accepted model.",
        ]
    )


def run_verification_call(
    *,
    vanilla_answer: str,
    fingerprint_payload: FingerprintPayload,
    candidates: list[dict[str, str]],
    client,
) -> tuple[list[DetectedModel], list[dict[str, str]]]:
    if not candidates:
        return [], []

    raw_payload = client.run_json(
        _build_verification_system_prompt(),
        _build_verification_user_prompt(vanilla_answer, fingerprint_payload, candidates),
    )
    accepted, rejected = parse_verification_response(
        raw_payload,
        vanilla_answer,
        {candidate["model_id"] for candidate in candidates},
    )
    candidate_names = {
        candidate["model_id"]: candidate["model_name"]
        for candidate in candidates
        if candidate.get("model_id") and candidate.get("model_name")
    }
    detected_models = [
        DetectedModel(
            model_id=item["model_id"],
            model_name=candidate_names.get(item["model_id"], item["model_id"]),
            evidence_quote=item.get("evidence_quote", ""),
            presence_mode=item.get("presence_mode", "executed"),
            presence_explanation=item.get("presence_explanation", ""),
            detection_confidence="structural",
        )
        for item in accepted
    ]
    detected_models = detected_models[:5]
    return detected_models, rejected


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


def recall_candidates(
    *,
    vanilla_answer: str,
    fingerprint_payload: FingerprintPayload,
    knowledge_graph: dict,
    reasoning_signals: dict,
    max_candidates: int = 60,
    embedding_retriever=None,
    embedding_api_key: str = "",
) -> list[dict[str, str]]:
    models = knowledge_graph.get("models", {})
    if not isinstance(models, dict):
        return []

    fingerprint_texts = [move.reasoning_move for move in fingerprint_payload.validated]
    primary_texts = [vanilla_answer, *fingerprint_texts]
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
    results: list[dict[str, str]] = []
    seen: set[str] = set()

    for _, model_id, model_name, activation_trigger in ranked_primary:
        if model_id in seen:
            continue
        seen.add(model_id)
        mp = models.get(model_id, {})
        dw = mp.get("danger_when", []) if isinstance(mp, dict) else []
        results.append(
            {
                "model_id": model_id,
                "model_name": model_name,
                "activation_trigger": activation_trigger,
                "danger_when": dw[0] if isinstance(dw, list) and dw and isinstance(dw[0], str) else "",
            }
        )
        if len(results) >= max_candidates:
            return results[:max_candidates]

    if isinstance(reasoning_signals, dict):
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
            sig_model = models.get(model_id, {})
            sig_dw = sig_model.get("danger_when", []) if isinstance(sig_model, dict) else []
            results.append(
                {
                    "model_id": model_id,
                    "model_name": str(signal_payload["display_name"]),
                    "activation_trigger": _pick_activation_trigger(signal_payload, fallback=model_id),
                    "recall_source": "keyword_recall",
                    "danger_when": sig_dw[0] if isinstance(sig_dw, list) and sig_dw and isinstance(sig_dw[0], str) else "",
                }
            )
            if len(results) >= max_candidates:
                break

    # --- Embedding recall path (swiss cheese: additive, never gating) ---
    if embedding_retriever is not None and embedding_api_key:
        try:
            query_text = " ".join(primary_texts)
            ranked = embedding_retriever.rank_models_expanded(
                query_text, embedding_api_key, top_k=max_candidates,
            )
            if ranked:
                for hit in ranked:
                    mid = hit["model_id"]
                    if mid in seen:
                        # Tag existing entry if not already tagged
                        for r in results:
                            if r["model_id"] == mid and "recall_source" not in r:
                                r["recall_source"] = "keyword_recall+embedding_recall"
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
                            "recall_source": "embedding_recall",
                            "danger_when": emb_dw[0] if isinstance(emb_dw, list) and emb_dw and isinstance(emb_dw[0], str) else "",
                        }
                    )
                    if len(results) >= max_candidates:
                        break
        except Exception:
            _LOGGER.warning("embedding_recall: failed in companion recall", exc_info=True)

    return results[:max_candidates]


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
