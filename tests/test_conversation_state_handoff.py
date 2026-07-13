from __future__ import annotations

import copy
import hashlib

import pytest

from engine.system_b.conversation_state_handoff import (
    ConversationStateHandoffError,
    SCHEMA_VERSION,
    assert_valid_conversation_state_handoff,
    build_fact_free_routing_boundary,
    validate_conversation_state_handoff,
)


SOURCE = """CONVERSATION: 4 turns, 2 user messages, 2 assistant responses

[Turn 1] USER:
I may run a four-week pilot, but funding is only a possibility.

[Turn 1] ASSISTANT:
A bounded pilot could preserve learning without pretending the funding exists.

[Turn 2] USER:
I will propose the pilot, although the support rule remains unresolved.

[Turn 2] ASSISTANT:
The pilot is workable, but the support rule still needs a named owner.
"""


def _evidence(speaker: str, turn: int, quote: str) -> dict:
    return {"speaker": speaker, "turn_index": turn, "quote": quote}


def _payload() -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "reviewed_shadow",
        "case_id": "case-test",
        "source": {
            "path": "fixtures/case-test.txt",
            "sha256": hashlib.sha256(SOURCE.encode()).hexdigest(),
            "message_count": 4,
        },
        "decision_summary": {
            "text": "Whether to run a bounded pilot.",
            "evidence_mode": "multi_turn_derivation",
            "source_evidence": [
                _evidence("user", 1, "I may run a four-week pilot"),
                _evidence("user", 2, "I will propose the pilot"),
            ],
        },
        "positions": [
            {
                "position_id": "position-001",
                "text": "Run a bounded pilot while keeping the support rule open.",
                "ownership": "joint",
                "state": "conditional",
                "evidence_mode": "multi_turn_derivation",
                "contributions": [
                    {
                        **_evidence("user", 2, "I will propose the pilot"),
                        "role": "originated",
                    },
                    {
                        **_evidence("assistant", 2, "The pilot is workable"),
                        "role": "qualified",
                    },
                ],
                "graph_routing_eligible": False,
            }
        ],
        "threads": [
            {
                "thread_id": "thread-001",
                "text": "Who owns support remains unresolved.",
                "disposition": "addressed_unresolved",
                "introduced": _evidence("user", 2, "the support rule remains unresolved"),
                "responses": [
                    {
                        **_evidence("assistant", 2, "the support rule still needs a named owner"),
                        "engagement": "substantive",
                    }
                ],
                "latest_ref": _evidence("assistant", 2, "the support rule still needs a named owner"),
                "superseded_by": None,
                "evidence_mode": "multi_turn_derivation",
                "graph_routing_eligible": False,
            }
        ],
        "constraints": [
            {
                "constraint_id": "constraint-001",
                "text": "Funding is possible but not committed.",
                "state": "active",
                "claim_mode": "possibility",
                "evidence_mode": "exact_span",
                "source_evidence": [
                    _evidence("user", 1, "funding is only a possibility")
                ],
                "graph_routing_eligible": False,
            }
        ],
        "routing_boundary": {
            "contains_case_context": True,
            "direct_graph_routing_allowed": False,
            "reasoning_pattern_abstraction_required": True,
            "runtime_integration": False,
        },
        "non_claims": [
            "state_items_are_probabilistic_or_human_interpretations",
            "source_grounding_is_not_semantic_correctness",
            "conversation_state_is_not_reasoning_pattern",
            "facts_cannot_seed_graph_directly",
            "not_runtime_integration_authority",
        ],
    }


def test_valid_handoff_preserves_joint_position_and_addressed_thread() -> None:
    payload = _payload()
    assert validate_conversation_state_handoff(payload, source_text=SOURCE) == []
    assert_valid_conversation_state_handoff(payload, source_text=SOURCE)


def test_unreviewed_model_probe_status_is_explicitly_valid() -> None:
    payload = _payload()
    payload["status"] = "model_probe_unreviewed"
    assert validate_conversation_state_handoff(payload, source_text=SOURCE) == []


def test_joint_position_requires_user_and_assistant_evidence() -> None:
    payload = _payload()
    payload["positions"][0]["contributions"] = payload["positions"][0]["contributions"][:1]
    violations = validate_conversation_state_handoff(payload, source_text=SOURCE)
    assert "joint_position_requires_both_speakers" in {item["code"] for item in violations}


def test_addressed_unresolved_requires_substantive_response() -> None:
    payload = _payload()
    payload["threads"][0]["responses"][0]["engagement"] = "acknowledged"
    violations = validate_conversation_state_handoff(payload, source_text=SOURCE)
    assert "addressed_thread_requires_substantive_response" in {
        item["code"] for item in violations
    }


def test_genuinely_dropped_rejects_substantive_response() -> None:
    payload = _payload()
    payload["threads"][0]["disposition"] = "genuinely_dropped"
    violations = validate_conversation_state_handoff(payload, source_text=SOURCE)
    assert "dropped_thread_cannot_have_substantive_response" in {
        item["code"] for item in violations
    }


def test_claim_mode_preserves_possibility_without_scoring_truth() -> None:
    payload = _payload()
    payload["constraints"][0]["claim_mode"] = "certain"
    violations = validate_conversation_state_handoff(payload, source_text=SOURCE)
    assert "constraint_claim_mode_invalid" in {item["code"] for item in violations}


def test_mixed_claim_mode_is_explicitly_representable() -> None:
    payload = _payload()
    payload["constraints"][0]["claim_mode"] = "mixed"
    assert validate_conversation_state_handoff(payload, source_text=SOURCE) == []


def test_quote_must_be_exact_in_named_turn() -> None:
    payload = _payload()
    payload["constraints"][0]["source_evidence"][0]["quote"] = "funding exists"
    violations = validate_conversation_state_handoff(payload, source_text=SOURCE)
    assert "source_quote_not_exact" in {item["code"] for item in violations}


def test_case_state_cannot_be_marked_graph_eligible() -> None:
    payload = _payload()
    payload["positions"][0]["graph_routing_eligible"] = True
    violations = validate_conversation_state_handoff(payload, source_text=SOURCE)
    assert "case_state_graph_routing_forbidden" in {item["code"] for item in violations}


def test_fact_free_projection_has_zero_direct_seeds() -> None:
    projection = build_fact_free_routing_boundary(_payload())
    assert projection["direct_graph_seed_count"] == 0
    assert projection["reasoning_pattern_inputs"] == []
    assert projection["contains_case_context"] is False
    assert projection["reasoning_pattern_abstraction_required"] is True


def test_assertion_raises_compact_error() -> None:
    payload = copy.deepcopy(_payload())
    payload["routing_boundary"]["direct_graph_routing_allowed"] = True
    with pytest.raises(ConversationStateHandoffError, match="routing_boundary_invalid"):
        assert_valid_conversation_state_handoff(payload, source_text=SOURCE)
