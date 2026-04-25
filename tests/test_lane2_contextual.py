"""Tests for the Phase 2d conversation-first Lane 2 (Companion) entry points.

Covers:
- `run_fingerprint_call_from_context` — fingerprints assistant turns verbatim,
  evidence_quotes validated against joined assistant text.
- `run_verification_call_from_context` — verification of candidate models
  against assistant turns; evidence_quote substring check uses joined assistant text.
- Prompt shape: CONTEXT (extractor summaries + user turns) / SOURCE (assistant turns).

Boundary calls mocked; no real LLM work.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.system_b.conversation_context import (
    ConversationContext,
    ExtractionPayload,
    LiveConstraint,
    DroppedThread,
    Turn,
)
from engine.system_b.companion_routing import (
    _build_fingerprint_system_prompt_from_context,
    _build_fingerprint_user_prompt_from_context,
    _build_verification_user_prompt_from_context,
    run_fingerprint_call_from_context,
    run_verification_call_from_context,
    validate_fingerprint_moves,
    FingerprintPayload,
)
from engine.system_b.companion import FingerprintMove


def _ctx(
    user_texts=("Should I take the Series B offer at 15% equity?",),
    assistant_texts=("You should take it. 15% is standard for Series B; reputable VCs know best.",),
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
            decision_situation="Founder-CEO considers Series B equity offer.",
            live_constraints=(),
            synthesized_position="take the offer",
            reasoning_passages=(),
            original_framing="Is 15% Series B equity too low?",
            dropped_threads=(),
        ),
    )


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


def test_fingerprint_user_prompt_from_context_has_context_source_split():
    ctx = _ctx(
        user_texts=("question about Series B",),
        assistant_texts=("Take it because reputable VCs know best.",),
    )
    user = _build_fingerprint_user_prompt_from_context(ctx)
    assert "CONTEXT" in user
    assert "SOURCE" in user
    # Assistant turn verbatim in SOURCE
    assert "reputable VCs know best" in user
    # User turn in CONTEXT
    assert "question about Series B" in user


def test_fingerprint_user_prompt_includes_extraction_context_fields():
    ctx = _ctx()
    ctx = ConversationContext(
        turns=ctx.turns,
        extraction=ExtractionPayload(
            decision_situation="Founder equity decision",
            live_constraints=(
                LiveConstraint(
                    constraint="equity minimum 18%",
                    introduced_turn=3,
                    status="active",
                    weight="structural",
                    canonical_key=None,
                ),
            ),
            synthesized_position="take the offer",
            reasoning_passages=(),
            original_framing="Is 15% too low?",
            dropped_threads=(),
        ),
    )
    user = _build_fingerprint_user_prompt_from_context(ctx)
    assert "equity minimum 18%" in user
    assert "Founder equity decision" in user


# ---------------------------------------------------------------------------
# Fingerprint run from context
# ---------------------------------------------------------------------------

def test_run_fingerprint_from_context_calls_client_with_assistant_source():
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
    payload = run_fingerprint_call_from_context(context=ctx, client=client)
    assert isinstance(payload, FingerprintPayload)
    assert len(client.calls) == 1
    _, user = client.calls[0]
    assert "reputable VCs know best" in user
    # Validation: evidence_quote should be substring of assistant text → validated
    assert len(payload.validated) == 1
    assert payload.validated[0].evidence_quotes == ["reputable VCs know best"]


def test_run_fingerprint_from_context_rejects_quote_not_in_assistant_turns():
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
    payload = run_fingerprint_call_from_context(context=ctx, client=client)
    assert len(payload.validated) == 0
    assert len(payload.dropped) == 1


# ---------------------------------------------------------------------------
# Verification prompt + run from context
# ---------------------------------------------------------------------------

def test_verification_user_prompt_from_context_puts_assistant_in_source():
    ctx = _ctx(
        user_texts=("q",),
        assistant_texts=("Because experts generally agree this is right.",),
    )
    fingerprint = FingerprintPayload(raw=[], validated=[], dropped=[])
    candidates = [
        {"model_id": "authority-bias", "model_name": "Authority Bias", "activation_trigger": "appeals to expertise"},
    ]
    user = _build_verification_user_prompt_from_context(ctx, fingerprint, candidates)
    assert "CONTEXT" in user
    assert "SOURCE" in user
    assert "Because experts generally agree" in user
    assert "authority-bias" in user


def test_run_verification_from_context_accepts_quote_substring_of_assistant():
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
    fingerprint = FingerprintPayload(raw=[], validated=[], dropped=[])
    candidates = [
        {"model_id": "authority-bias", "model_name": "Authority Bias", "activation_trigger": "x"},
    ]
    detected, rejected = run_verification_call_from_context(
        context=ctx,
        fingerprint_payload=fingerprint,
        candidates=candidates,
        client=client,
    )
    assert len(detected) == 1
    assert detected[0].model_id == "authority-bias"
    assert detected[0].evidence_quote == "reputable VCs know best"
    assert rejected == []


def test_run_verification_from_context_rejects_quote_not_in_assistant_turns():
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
    fingerprint = FingerprintPayload(raw=[], validated=[], dropped=[])
    candidates = [
        {"model_id": "authority-bias", "model_name": "Authority Bias", "activation_trigger": "x"},
    ]
    detected, rejected = run_verification_call_from_context(
        context=ctx,
        fingerprint_payload=fingerprint,
        candidates=candidates,
        client=client,
    )
    assert len(detected) == 0
    assert len(rejected) == 1
    assert rejected[0]["rejection_reason"] == "execution_quote_not_literal_substring"


def test_run_verification_from_context_empty_candidates_short_circuits():
    client = _RecordingClient()
    ctx = _ctx()
    detected, rejected = run_verification_call_from_context(
        context=ctx,
        fingerprint_payload=FingerprintPayload(raw=[], validated=[], dropped=[]),
        candidates=[],
        client=client,
    )
    assert detected == []
    assert rejected == []
    assert client.calls == [], "no LLM call when there are no candidates"


# ---------------------------------------------------------------------------
# Phase 4c: packet-driven Lane 2 byte-equivalence tests
# ---------------------------------------------------------------------------

from engine.system_b.ir_constructor import construct_conversation_ir
from engine.system_b.packet_builders.lane4 import build_lane4_packet
from engine.system_b.companion_routing import (
    _build_fingerprint_user_prompt_from_packet,
    _build_verification_user_prompt_from_packet,
    run_fingerprint_call_from_packet,
    run_verification_call_from_packet,
)


def test_packet_fingerprint_user_prompt_matches_context_user_prompt() -> None:
    ctx = _ctx()
    ir = construct_conversation_ir(ctx)
    packet = build_lane4_packet(ir)
    ctx_prompt = _build_fingerprint_user_prompt_from_context(ctx)
    pkt_prompt = _build_fingerprint_user_prompt_from_packet(packet)
    assert ctx_prompt == pkt_prompt


def test_packet_verification_user_prompt_matches_context_user_prompt() -> None:
    ctx = _ctx()
    ir = construct_conversation_ir(ctx)
    packet = build_lane4_packet(ir)
    fingerprint_payload = FingerprintPayload(raw=[], validated=[], dropped=[])
    candidates = [{
        "model_id": "first-principles-thinking",
        "model_name": "First Principles Thinking",
        "activation_trigger": "appeal-to-authority pattern",
        "danger_when": "unverified expert claims",
    }]
    ctx_prompt = _build_verification_user_prompt_from_context(ctx, fingerprint_payload, candidates)
    pkt_prompt = _build_verification_user_prompt_from_packet(packet, fingerprint_payload, candidates)
    assert ctx_prompt == pkt_prompt


def test_run_fingerprint_call_from_packet_returns_same_payload_as_from_context() -> None:
    ctx = _ctx()
    ir = construct_conversation_ir(ctx)
    packet = build_lane4_packet(ir)
    payload = {"reasoning_moves": []}
    ctx_pl = run_fingerprint_call_from_context(context=ctx, client=_RecordingClient(payload))
    pkt_pl = run_fingerprint_call_from_packet(packet=packet, client=_RecordingClient(payload))
    assert ctx_pl == pkt_pl


def test_run_verification_from_packet_short_circuits_with_no_candidates() -> None:
    ctx = _ctx()
    ir = construct_conversation_ir(ctx)
    packet = build_lane4_packet(ir)
    client = _RecordingClient()
    detected, rejected = run_verification_call_from_packet(
        packet=packet,
        fingerprint_payload=FingerprintPayload(raw=[], validated=[], dropped=[]),
        candidates=[],
        client=client,
    )
    assert detected == []
    assert rejected == []
    assert client.calls == []
