"""Tests for the Lane 2 (Companion) packet-driven entry points.

Covers:
- `run_fingerprint_call_from_packet` — fingerprints assistant turns verbatim,
  evidence_quotes validated against joined assistant text.
- `run_verification_call_from_packet` — verification of candidate models
  against assistant turns; evidence_quote substring check uses joined assistant text.
- Prompt shape: CONTEXT (extractor summaries + user turns) / SOURCE (assistant turns).

Boundary calls mocked; no real LLM work.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.system_b.companion import FingerprintMove
from engine.system_b.companion_routing import (
    FingerprintPayload,
    _build_fingerprint_system_prompt_from_context,
    _build_fingerprint_user_prompt_from_packet,
    _build_verification_user_prompt_from_packet,
    run_fingerprint_call_from_packet,
    run_verification_call_from_packet,
    validate_fingerprint_moves,
)
from engine.system_b.conversation_context import (
    ConversationContext,
    DroppedThread,
    ExtractionPayload,
    LiveConstraint,
    Turn,
)
from engine.system_b.ir_constructor import construct_conversation_ir
from engine.system_b.packet_builders.lane4 import Lane4Packet, build_lane4_packet


def _ctx(
    user_texts=("Should I take the Series B offer at 15% equity?",),
    assistant_texts=("You should take it. 15% is standard for Series B; reputable VCs know best.",),
    *,
    decision_situation: str = "Founder-CEO considers Series B equity offer.",
    original_framing: str = "Is 15% Series B equity too low?",
    live_constraints: tuple[LiveConstraint, ...] = (),
    dropped_threads: tuple[DroppedThread, ...] = (),
) -> ConversationContext:
    turns: list[Turn] = []
    idx = 1
    for u, a in zip(user_texts, assistant_texts + ("",) * max(0, len(user_texts) - len(assistant_texts))):
        turns.append(Turn(turn_index=idx, speaker="user", text=u))
        idx += 1
        if a:
            turns.append(Turn(turn_index=idx, speaker="assistant", text=a))
            idx += 1
    for a in assistant_texts[len(user_texts):]:
        turns.append(Turn(turn_index=idx, speaker="assistant", text=a))
        idx += 1

    return ConversationContext(
        turns=tuple(turns),
        extraction=ExtractionPayload(
            decision_situation=decision_situation,
            live_constraints=live_constraints,
            synthesized_position="take the offer",
            reasoning_passages=(),
            original_framing=original_framing,
            dropped_threads=dropped_threads,
        ),
    )


def _packet_from_ctx(ctx: ConversationContext) -> Lane4Packet:
    return build_lane4_packet(construct_conversation_ir(ctx))


class _RecordingClient:
    def __init__(self, return_payload: dict | None = None):
        self.calls: list[tuple[str, str]] = []
        self._payload = return_payload or {"reasoning_moves": []}

    def run_json(self, system_prompt: str, user_prompt: str) -> dict:
        self.calls.append((system_prompt, user_prompt))
        return self._payload


# ---------------------------------------------------------------------------
# Fingerprint prompt shape
# ---------------------------------------------------------------------------

def test_fingerprint_system_prompt_from_context_mentions_source():
    """System prompt should name SOURCE as the audit target (assistant turns)."""
    system = _build_fingerprint_system_prompt_from_context()
    assert "SOURCE" in system
    # Evidence must be substring of SOURCE (assistant turns), not flattened vanilla
    assert "substring" in system.lower()
    assert "assistant" in system.lower()


def test_fingerprint_user_prompt_from_packet_has_context_source_split():
    ctx = _ctx(
        user_texts=("question about Series B",),
        assistant_texts=("Take it because reputable VCs know best.",),
    )
    packet = _packet_from_ctx(ctx)
    user = _build_fingerprint_user_prompt_from_packet(packet)
    assert "CONTEXT" in user
    assert "SOURCE" in user
    # Assistant turn verbatim in SOURCE
    assert "reputable VCs know best" in user
    # User turn in CONTEXT
    assert "question about Series B" in user


def test_fingerprint_user_prompt_includes_extraction_context_fields():
    ctx = _ctx(
        live_constraints=(
            LiveConstraint(
                constraint="equity minimum 18%",
                introduced_turn=1,
                status="active",
                weight="structural",
                canonical_key=None,
            ),
        ),
        decision_situation="Founder equity decision",
        original_framing="Is 15% too low?",
    )
    packet = _packet_from_ctx(ctx)
    user = _build_fingerprint_user_prompt_from_packet(packet)
    assert "equity minimum 18%" in user
    assert "Founder equity decision" in user


# ---------------------------------------------------------------------------
# Fingerprint run from packet
# ---------------------------------------------------------------------------

def test_run_fingerprint_from_packet_calls_client_with_assistant_source():
    client = _RecordingClient({
        "reasoning_moves": [
            {
                "move_id": "m1",
                "reasoning_move": "Deferring to authority",
                "evidence_quotes": ["reputable VCs know best"],
                "evidence_rationale": "uses authority as justification",
                "confidence": "high",
            }
        ]
    })
    ctx = _ctx(
        user_texts=("question",),
        assistant_texts=("Take it because reputable VCs know best.",),
    )
    packet = _packet_from_ctx(ctx)
    payload = run_fingerprint_call_from_packet(packet=packet, client=client)
    assert isinstance(payload, FingerprintPayload)
    assert len(client.calls) == 1
    _, user = client.calls[0]
    assert "reputable VCs know best" in user
    # Validation: evidence_quote should be substring of assistant text → validated
    assert len(payload.validated) == 1
    assert payload.validated[0].evidence_quotes == ["reputable VCs know best"]


def test_run_fingerprint_from_packet_rejects_quote_not_in_assistant_turns():
    """Evidence quotes that aren't substrings of ASSISTANT turns should be dropped."""
    client = _RecordingClient({
        "reasoning_moves": [
            {
                "move_id": "m1",
                "reasoning_move": "Fabricated move",
                "evidence_quotes": ["this text is not in the assistant turns at all"],
                "evidence_rationale": "should be dropped",
                "confidence": "high",
            }
        ]
    })
    ctx = _ctx(
        user_texts=("q",),
        assistant_texts=("Take it.",),
    )
    packet = _packet_from_ctx(ctx)
    payload = run_fingerprint_call_from_packet(packet=packet, client=client)
    assert len(payload.validated) == 0
    assert len(payload.dropped) == 1


# ---------------------------------------------------------------------------
# Verification prompt + run from packet
# ---------------------------------------------------------------------------

def test_verification_user_prompt_from_packet_puts_assistant_in_source():
    ctx = _ctx(
        user_texts=("q",),
        assistant_texts=("Because experts generally agree this is right.",),
    )
    packet = _packet_from_ctx(ctx)
    fingerprint = FingerprintPayload(raw=[], validated=[], dropped=[])
    candidates = [
        {"model_id": "authority-bias", "model_name": "Authority Bias", "activation_trigger": "appeals to expertise"},
    ]
    user = _build_verification_user_prompt_from_packet(packet, fingerprint, candidates)
    assert "CONTEXT" in user
    assert "SOURCE" in user
    assert "Because experts generally agree" in user
    assert "authority-bias" in user


def test_run_verification_from_packet_accepts_quote_substring_of_assistant():
    client = _RecordingClient({
        "accepted": [
            {
                "model_id": "authority-bias",
                "presence_mode": "executed",
                "evidence_quote": "reputable VCs know best",
                "presence_explanation": "appeals to authority",
            }
        ],
        "rejected": [],
    })
    ctx = _ctx(
        user_texts=("q",),
        assistant_texts=("Take it because reputable VCs know best.",),
    )
    packet = _packet_from_ctx(ctx)
    fingerprint = FingerprintPayload(raw=[], validated=[], dropped=[])
    candidates = [
        {"model_id": "authority-bias", "model_name": "Authority Bias", "activation_trigger": "x"},
    ]
    detected, rejected, accepted_before_cap, capped, duplicate_accepts, quote_repairs = run_verification_call_from_packet(
        packet=packet,
        fingerprint_payload=fingerprint,
        candidates=candidates,
        client=client,
    )
    assert len(detected) == 1
    assert detected[0].model_id == "authority-bias"
    assert detected[0].evidence_quote == "reputable VCs know best"
    assert rejected == []
    # Single accepted model: pre-cap == post-cap; capped is empty.
    assert len(accepted_before_cap) == 1
    assert capped == []
    assert quote_repairs == []


def test_run_verification_from_packet_rejects_quote_not_in_assistant_turns():
    client = _RecordingClient({
        "accepted": [
            {
                "model_id": "authority-bias",
                "presence_mode": "executed",
                "evidence_quote": "NOT IN ASSISTANT TEXT AT ALL",
                "presence_explanation": "should be rejected",
            }
        ],
        "rejected": [],
    })
    ctx = _ctx(
        user_texts=("q",),
        assistant_texts=("Take it because reputable VCs know best.",),
    )
    packet = _packet_from_ctx(ctx)
    fingerprint = FingerprintPayload(raw=[], validated=[], dropped=[])
    candidates = [
        {"model_id": "authority-bias", "model_name": "Authority Bias", "activation_trigger": "x"},
    ]
    detected, rejected, accepted_before_cap, capped, duplicate_accepts, quote_repairs = run_verification_call_from_packet(
        packet=packet,
        fingerprint_payload=fingerprint,
        candidates=candidates,
        client=client,
    )
    assert len(detected) == 0
    assert len(rejected) == 1
    assert rejected[0]["rejection_reason"] == "execution_quote_not_literal_substring"
    assert accepted_before_cap == []
    assert capped == []
    assert quote_repairs == []


def test_run_verification_accepts_normalized_literal_quote():
    client = _RecordingClient({
        "accepted": [
            {
                "model_id": "base-rates",
                "presence_mode": "executed",
                "evidence_quote": 'He wrote "protect the downside" in the memo.',
                "presence_explanation": "uses the quoted downside evidence",
            }
        ],
        "rejected": [],
    })
    ctx = _ctx(
        user_texts=("q",),
        assistant_texts=('He wrote \\"protect the downside\\" in the memo.',),
    )
    packet = _packet_from_ctx(ctx)
    candidates = [
        {"model_id": "base-rates", "model_name": "Base Rates", "activation_trigger": "x"},
    ]
    detected, rejected, accepted_before_cap, capped, duplicate_accepts, quote_repairs = run_verification_call_from_packet(
        packet=packet,
        fingerprint_payload=FingerprintPayload(raw=[], validated=[], dropped=[]),
        candidates=candidates,
        client=client,
    )
    assert len(detected) == 1
    assert detected[0].evidence_quote == 'He wrote \\"protect the downside\\" in the memo.'
    assert rejected == []
    assert len(accepted_before_cap) == 1
    assert capped == []
    assert duplicate_accepts == []
    assert quote_repairs == []


def test_run_verification_accepts_whitespace_normalized_literal_quote():
    client = _RecordingClient({
        "accepted": [
            {
                "model_id": "problem-framing-and-reframing",
                "presence_mode": "executed",
                "evidence_quote": "Before diving into tactics, can I ask a few things to make sure we're solving the right problem. First: what's your current pipeline?",
                "presence_explanation": "reframes the request before tactics",
            }
        ],
        "rejected": [],
    })
    source_span = (
        "Before diving into tactics, can I ask a few things to make sure we're solving the right problem.\n\n"
        "First: what's your current pipeline?"
    )
    ctx = _ctx(user_texts=("q",), assistant_texts=(source_span,))
    packet = _packet_from_ctx(ctx)
    candidates = [
        {
            "model_id": "problem-framing-and-reframing",
            "model_name": "Problem Framing And Reframing",
            "activation_trigger": "x",
        },
    ]
    detected, rejected, accepted_before_cap, capped, duplicate_accepts, quote_repairs = run_verification_call_from_packet(
        packet=packet,
        fingerprint_payload=FingerprintPayload(raw=[], validated=[], dropped=[]),
        candidates=candidates,
        client=client,
    )
    assert len(detected) == 1
    assert detected[0].evidence_quote == source_span
    assert rejected == []
    assert len(accepted_before_cap) == 1
    assert capped == []
    assert duplicate_accepts == []
    assert quote_repairs == []


def test_run_verification_repairs_ellipsis_quote_to_literal_fragment():
    client = _RecordingClient({
        "accepted": [
            {
                "model_id": "margin-of-safety",
                "presence_mode": "executed",
                "evidence_quote": "8 months at zero revenue is tight for a first-time independent consultant... Launching without signed LOI is possible but harder.",
                "presence_explanation": "uses runway buffer",
            }
        ],
        "rejected": [],
    })
    source_sentence = "On runway: 8 months at zero revenue is tight for a first-time independent consultant."
    ctx = _ctx(
        user_texts=("q",),
        assistant_texts=(source_sentence + " Launching without that is possible but harder.",),
    )
    packet = _packet_from_ctx(ctx)
    candidates = [
        {"model_id": "margin-of-safety", "model_name": "Margin Of Safety", "activation_trigger": "x"},
    ]
    detected, rejected, accepted_before_cap, capped, duplicate_accepts, quote_repairs = run_verification_call_from_packet(
        packet=packet,
        fingerprint_payload=FingerprintPayload(raw=[], validated=[], dropped=[]),
        candidates=candidates,
        client=client,
    )
    assert len(detected) == 1
    assert detected[0].evidence_quote == "8 months at zero revenue is tight for a first-time independent consultant"
    assert rejected == []
    assert len(accepted_before_cap) == 1
    assert capped == []
    assert duplicate_accepts == []
    assert len(quote_repairs) == 1
    assert quote_repairs[0]["model_id"] == "margin-of-safety"
    assert quote_repairs[0]["original_evidence_quote"].startswith("8 months at zero revenue")
    assert quote_repairs[0]["repaired_evidence_quote"] == detected[0].evidence_quote
    assert quote_repairs[0]["repair_method"] == "ellipsis_literal_fragment"
    assert quote_repairs[0]["repair_score"] == "1.000"


def test_run_verification_repairs_paraphrased_quote_to_literal_source_span():
    client = _RecordingClient({
        "accepted": [
            {
                "model_id": "base-rates",
                "presence_mode": "executed",
                "evidence_quote": "The base rate is 20-30%, not 50%.",
                "presence_explanation": "uses base-rate correction",
            }
        ],
        "rejected": [],
    })
    source_sentence = (
        "The actual base rate is 20-30%, not 50%, once you remove the visible winners."
    )
    ctx = _ctx(user_texts=("q",), assistant_texts=(source_sentence,))
    packet = _packet_from_ctx(ctx)
    candidates = [
        {"model_id": "base-rates", "model_name": "Base Rates", "activation_trigger": "x"},
    ]
    detected, rejected, accepted_before_cap, capped, duplicate_accepts, quote_repairs = run_verification_call_from_packet(
        packet=packet,
        fingerprint_payload=FingerprintPayload(raw=[], validated=[], dropped=[]),
        candidates=candidates,
        client=client,
    )
    assert len(detected) == 1
    assert detected[0].evidence_quote == source_sentence
    assert rejected == []
    assert len(accepted_before_cap) == 1
    assert capped == []
    assert duplicate_accepts == []
    assert len(quote_repairs) == 1
    assert quote_repairs[0]["model_id"] == "base-rates"
    assert quote_repairs[0]["original_evidence_quote"] == "The base rate is 20-30%, not 50%."
    assert quote_repairs[0]["repaired_evidence_quote"] == source_sentence
    assert quote_repairs[0]["repair_method"] == "token_overlap_literal_span"
    assert float(quote_repairs[0]["repair_score"]) >= 0.80


def test_run_verification_does_not_repair_meaning_flipped_quote():
    client = _RecordingClient({
        "accepted": [
            {
                "model_id": "confidence-calibration",
                "presence_mode": "executed",
                "evidence_quote": "The team does not have a strong record of delivery.",
                "presence_explanation": "claims weak evidence",
            }
        ],
        "rejected": [],
    })
    ctx = _ctx(
        user_texts=("q",),
        assistant_texts=("The team has a strong record of delivery.",),
    )
    packet = _packet_from_ctx(ctx)
    candidates = [
        {
            "model_id": "confidence-calibration",
            "model_name": "Confidence Calibration",
            "activation_trigger": "x",
        },
    ]
    detected, rejected, accepted_before_cap, capped, duplicate_accepts, quote_repairs = run_verification_call_from_packet(
        packet=packet,
        fingerprint_payload=FingerprintPayload(raw=[], validated=[], dropped=[]),
        candidates=candidates,
        client=client,
    )
    assert detected == []
    assert accepted_before_cap == []
    assert capped == []
    assert duplicate_accepts == []
    assert quote_repairs == []
    assert len(rejected) == 1
    assert rejected[0]["model_id"] == "confidence-calibration"
    assert rejected[0]["rejection_reason"] == "execution_quote_not_literal_substring"


def test_run_verification_does_not_repair_contracted_negation_flip():
    client = _RecordingClient({
        "accepted": [
            {
                "model_id": "confidence-calibration",
                "presence_mode": "executed",
                "evidence_quote": "The team doesn't have a strong delivery record.",
                "presence_explanation": "claims weak evidence",
            }
        ],
        "rejected": [],
    })
    ctx = _ctx(
        user_texts=("q",),
        assistant_texts=("The team has a strong delivery record.",),
    )
    packet = _packet_from_ctx(ctx)
    candidates = [
        {
            "model_id": "confidence-calibration",
            "model_name": "Confidence Calibration",
            "activation_trigger": "x",
        },
    ]
    detected, rejected, accepted_before_cap, capped, duplicate_accepts, quote_repairs = run_verification_call_from_packet(
        packet=packet,
        fingerprint_payload=FingerprintPayload(raw=[], validated=[], dropped=[]),
        candidates=candidates,
        client=client,
    )
    assert detected == []
    assert accepted_before_cap == []
    assert capped == []
    assert duplicate_accepts == []
    assert quote_repairs == []
    assert len(rejected) == 1
    assert rejected[0]["model_id"] == "confidence-calibration"
    assert rejected[0]["rejection_reason"] == "execution_quote_not_literal_substring"


def test_run_verification_from_packet_empty_candidates_short_circuits():
    client = _RecordingClient()
    ctx = _ctx()
    packet = _packet_from_ctx(ctx)
    detected, rejected, accepted_before_cap, capped, duplicate_accepts, quote_repairs = run_verification_call_from_packet(
        packet=packet,
        fingerprint_payload=FingerprintPayload(raw=[], validated=[], dropped=[]),
        candidates=[],
        client=client,
    )
    assert detected == []
    assert rejected == []
    assert accepted_before_cap == []
    assert capped == []
    assert quote_repairs == []
    assert client.calls == [], "no LLM call when there are no candidates"
