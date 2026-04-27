"""Tests for Lane 2 verifier prompt invariants and Track 2 (Checklists KG bullet 4 tightening).

Track 1 (Path B verifier prompt restructure) was rolled back after E6 caught
catastrophic regression (PR #55). Prompt-content tests for the rolled-back blocks
were removed with the revert. The independent tests below remain in force:

- Existing governing-rules regression guard (broad-models decline list, tie-breaker,
  passage exclusivity, JSON schema fields).
- Parser compatibility: parse_verification_response preserves arbitrary
  rejection_reason strings (regression guard for future Track 1 v2 vocabulary
  additions).
- User-prompt protection: watches_for clause reaches the verifier when a candidate
  has danger_when (covers existing user-prompt formatting behavior at
  engine/system_b/companion_routing.py:660).
- Track 2 KG: checklists.select_when has 4 bullets, bullet 4 requires recurrence.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.system_b.boundary_provider import BoundaryCallMetadata, _build_call_metadata
from engine.system_b.companion_routing import (
    FingerprintPayload,
    _build_verification_system_prompt,
    _build_verification_user_prompt_from_packet,
    is_malformed_verifier_response,
    parse_verification_response,
)
from engine.system_b.conversation_context import (
    ConversationContext,
    ExtractionPayload,
    Turn,
)
from engine.system_b.ir_constructor import construct_conversation_ir
from engine.system_b.packet_builders.lane4 import build_lane4_packet


def _minimal_packet():
    ctx = ConversationContext(
        turns=(
            Turn(turn_index=1, speaker="user", text="What should I do?"),
            Turn(turn_index=2, speaker="assistant", text="Consider the options carefully."),
        ),
        extraction=ExtractionPayload(
            decision_situation="situation",
            live_constraints=(),
            synthesized_position="position",
            reasoning_passages=(),
            original_framing="framing",
            dropped_threads=(),
        ),
    )
    return build_lane4_packet(construct_conversation_ir(ctx))


# ---------------------------------------------------------------------------
# Verifier prompt invariants (governing rules that must remain present)
# ---------------------------------------------------------------------------

def test_verification_prompt_preserves_existing_governing_rules():
    """Track 1 is incremental — existing rules must still be present (not replacement)."""
    p = _build_verification_system_prompt()
    # Existing broad-models decline list
    assert "Broad models that must be actively declined" in p
    assert "second-order-thinking" in p
    assert "tier-2-high-value" in p
    # Existing tie-breaker and passage exclusivity rules
    assert "TIE-BREAKER RULE" in p
    assert "PASSAGE EXCLUSIVITY RULE" in p
    # Existing JSON schema structure unchanged
    assert "presence_mode" in p
    assert "evidence_quote" in p
    assert '"executed | violated"' in p


# ---------------------------------------------------------------------------
# Track 1: parser compatibility (direct parse_verification_response)
# ---------------------------------------------------------------------------

def test_parser_preserves_new_rejection_reason_mechanism_topical_only():
    raw = {
        "accepted": [],
        "rejected": [
            {"model_id": "reasoning-mode-router", "rejection_reason": "mechanism_topical_only"},
        ],
    }
    accepted, rejected, quote_repairs = parse_verification_response(
        raw,
        vanilla_answer="some assistant answer",
        candidate_ids={"reasoning-mode-router"},
    )
    assert accepted == []
    assert len(rejected) == 1
    assert rejected[0]["model_id"] == "reasoning-mode-router"
    assert rejected[0]["rejection_reason"] == "mechanism_topical_only"


def test_parser_preserves_new_rejection_reason_recurring_execution_required():
    raw = {
        "accepted": [],
        "rejected": [
            {"model_id": "checklists", "rejection_reason": "recurring_execution_required"},
        ],
    }
    accepted, rejected, _ = parse_verification_response(
        raw,
        vanilla_answer="numbered list of three options",
        candidate_ids={"checklists"},
    )
    assert rejected[0]["rejection_reason"] == "recurring_execution_required"


def test_parser_preserves_existing_rejection_reason_strings_unchanged():
    """Compatibility regression guard — existing reason strings must still pass through."""
    raw = {
        "accepted": [],
        "rejected": [
            {"model_id": "second-order-thinking", "rejection_reason": "too generic"},
            {"model_id": "tier-2-high-value", "rejection_reason": "passage already claimed by more specific model"},
        ],
    }
    _, rejected, _ = parse_verification_response(
        raw,
        vanilla_answer="x",
        candidate_ids={"second-order-thinking", "tier-2-high-value"},
    )
    reasons = {r["model_id"]: r["rejection_reason"] for r in rejected}
    assert reasons["second-order-thinking"] == "too generic"
    assert reasons["tier-2-high-value"] == "passage already claimed by more specific model"


# ---------------------------------------------------------------------------
# Track 1: user-prompt watches_for behavior (protects Block D)
# ---------------------------------------------------------------------------

def test_user_prompt_emits_watches_for_when_candidate_has_danger_when():
    """Block D's danger_when respect rule depends on watches_for reaching the verifier."""
    packet = _minimal_packet()
    fingerprint = FingerprintPayload(raw=[], validated=[], dropped=[])
    candidates = [
        {
            "model_id": "checklists",
            "model_name": "Checklists",
            "activation_trigger": "repeatable execution with omission risk",
            "danger_when": "The situation is novel or emergent enough that a generic checklist would force reality into a familiar but mismatched frame.",
        },
    ]
    user = _build_verification_user_prompt_from_packet(packet, fingerprint, candidates)
    assert "checklists" in user
    assert "watches_for:" in user
    assert "novel or emergent" in user


def test_user_prompt_omits_watches_for_when_candidate_has_no_danger_when():
    """Negative companion: absence of danger_when must not emit a stray watches_for line."""
    packet = _minimal_packet()
    fingerprint = FingerprintPayload(raw=[], validated=[], dropped=[])
    candidates = [
        {
            "model_id": "authority-bias",
            "model_name": "Authority Bias",
            "activation_trigger": "appeals to expertise",
        },
    ]
    user = _build_verification_user_prompt_from_packet(packet, fingerprint, candidates)
    assert "authority-bias" in user
    assert "watches_for:" not in user


# ---------------------------------------------------------------------------
# Track 2: Checklists KG bullet 4 tightening
# ---------------------------------------------------------------------------

def _load_kg():
    path = Path(__file__).resolve().parents[1] / "data" / "knowledge_graph.json"
    return json.loads(path.read_text())


def test_kg_loads_and_has_checklists():
    kg = _load_kg()
    assert "models" in kg
    assert "checklists" in kg["models"]


def test_checklists_select_when_has_four_bullets():
    kg = _load_kg()
    bullets = kg["models"]["checklists"]["select_when"]
    assert isinstance(bullets, list)
    assert len(bullets) == 4
    assert all(isinstance(b, str) and b for b in bullets)


def test_checklists_select_when_bullet_4_requires_recurrence():
    """Form B: bullet 4 in-place tightening must require recurring execution across instances."""
    kg = _load_kg()
    bullet_4 = kg["models"]["checklists"]["select_when"][3]
    assert "recurring multi-step process" in bullet_4
    assert "across instances" in bullet_4


def test_checklists_select_when_bullet_4_no_longer_reads_as_any_multistep_task():
    """Negative guard: the pre-fix wording invited 'any multi-step task' — must be gone."""
    kg = _load_kg()
    bullet_4 = kg["models"]["checklists"]["select_when"][3]
    # The pre-fix wording was: "Working memory limits are turning a complex multi-step task into ..."
    # The fix replaces "complex multi-step task" with "recurring multi-step process".
    assert "complex multi-step task" not in bullet_4


# ---------------------------------------------------------------------------
# Output-contract integrity (Track 1 v2 design memo §4)
# ---------------------------------------------------------------------------

def test_malformed_detector_flags_empty_dict():
    """The verifier returning {} (a valid empty JSON object that satisfies JSON
    mode without committing to either accepted or rejected) is the canonical
    malformed case observed in E6 v1 (PR #55)."""
    assert is_malformed_verifier_response({}) is True


def test_malformed_detector_flags_dict_missing_both_fields():
    assert is_malformed_verifier_response({"foo": "bar"}) is True


def test_malformed_detector_flags_non_list_accepted():
    assert is_malformed_verifier_response({"accepted": "not a list", "rejected": "also not a list"}) is True


def test_malformed_detector_flags_non_dict_input():
    assert is_malformed_verifier_response(None) is True
    assert is_malformed_verifier_response("string") is True
    assert is_malformed_verifier_response([]) is True


def test_malformed_detector_passes_well_formed_empty_lists():
    """A deliberate reject-all looks like {accepted: [], rejected: [...]} (or
    even {accepted: [], rejected: []}). That is NOT malformed; it is a
    legitimate verifier judgment that no anchors apply."""
    assert is_malformed_verifier_response({"accepted": [], "rejected": []}) is False
    assert is_malformed_verifier_response({"accepted": [], "rejected": [{"model_id": "x", "rejection_reason": "y"}]}) is False


def test_malformed_detector_passes_one_field_present():
    """The existing parser contract treats missing accepted or rejected as
    permissive (require_list_of_dicts normalises to []). The malformed
    detector must only fire when BOTH list fields are missing — the
    distinction is 'schema-incomplete' vs 'partially populated.'"""
    assert is_malformed_verifier_response({"accepted": []}) is False
    assert is_malformed_verifier_response({"rejected": []}) is False
    assert is_malformed_verifier_response({"accepted": [{"model_id": "x", "presence_mode": "executed"}]}) is False


# ---------------------------------------------------------------------------
# Boundary metadata capture (Track 1 v2 design memo §4 + memo §7 commitment)
# ---------------------------------------------------------------------------

def test_boundary_metadata_has_finish_reason_field():
    md = BoundaryCallMetadata()
    assert hasattr(md, "finish_reason")
    assert md.finish_reason == ""


def test_boundary_metadata_has_raw_message_content_field():
    md = BoundaryCallMetadata()
    assert hasattr(md, "raw_message_content")
    assert md.raw_message_content == ""


def test_boundary_metadata_has_temperature_field():
    md = BoundaryCallMetadata()
    assert hasattr(md, "temperature")
    assert md.temperature == 0.0


def test_build_call_metadata_captures_finish_reason_and_content():
    """End-to-end wiring: a payload-shaped input should produce metadata with
    finish_reason populated from choices[0].finish_reason and
    raw_message_content + temperature populated from the call-site arguments.
    Field-presence tests prove the dataclass shape; this test proves the
    capture path actually works."""
    payload = {
        "choices": [
            {"message": {"content": "{}"}, "finish_reason": "stop"},
        ],
        "usage": {"prompt_tokens": 100, "completion_tokens": 5, "total_tokens": 105},
    }
    md = _build_call_metadata(
        provider_name="test-provider",
        model="test-model",
        payload=payload,
        reasoning_config=None,
        status="ok",
        temperature=0.7,
        raw_message_content="{}",
    )
    assert md.finish_reason == "stop"
    assert md.raw_message_content == "{}"
    assert md.temperature == 0.7
    assert md.status == "ok"
    # Existing fields still wire correctly so this PR doesn't silently break them
    assert md.prompt_tokens == 100
    assert md.completion_tokens == 5
    assert md.total_tokens == 105


def test_build_call_metadata_handles_empty_finish_reason():
    """If choices[0].finish_reason is missing or null, finish_reason should
    default to empty string, not None — preserving the dataclass's str type."""
    payload = {"choices": [{"message": {"content": ""}}], "usage": {}}
    md = _build_call_metadata(
        provider_name="test-provider",
        model="test-model",
        payload=payload,
        reasoning_config=None,
        status="ok",
        temperature=0.0,
        raw_message_content="",
    )
    assert md.finish_reason == ""
    assert isinstance(md.finish_reason, str)


def test_build_call_metadata_defaults_when_temperature_and_content_omitted():
    """The new keyword-only parameters have safe defaults so existing
    construction sites in non-success paths (timeout, missing_choices, etc.)
    do not need to pass them explicitly."""
    payload = {"choices": [{"message": {"content": "x"}, "finish_reason": "stop"}], "usage": {}}
    md = _build_call_metadata(
        provider_name="p",
        model="m",
        payload=payload,
        reasoning_config=None,
        status="ok",
    )
    assert md.temperature == 0.0
    assert md.raw_message_content == ""
    # finish_reason still captured from payload — the default applies only to
    # the call-site arguments, not the payload-derived fields
    assert md.finish_reason == "stop"
