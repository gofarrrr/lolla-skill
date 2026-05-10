"""Tests for run_extract.py — canonical_key slug validation and
post-extraction invalid-key handling.

TDD scaffolding for PR #1 of the extraction contract roadmap.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from run_extract import (  # noqa: E402
    _apply_canonical_key_validation,
    _build_audit_seed,
    _map_to_critique_request,
    _validate_reasoning_passages,
    _validate_conversation_capture,
    _validate_canonical_key,
)


def test_valid_four_token_slug():
    assert _validate_canonical_key("marcus-comp-below-market") is True


def test_valid_two_token_boundary():
    """2-token minimum: 'marcus-comp' is valid (first token ≥2 chars)."""
    assert _validate_canonical_key("marcus-comp") is True


def test_valid_three_token():
    assert _validate_canonical_key("equity-retention-risk") is True


def test_rejects_uppercase():
    assert _validate_canonical_key("UPPERCASE") is False


def test_rejects_mixed_case():
    assert _validate_canonical_key("Marcus-Comp") is False


def test_rejects_single_token_no_hyphen():
    assert _validate_canonical_key("onetoken") is False


def test_rejects_five_token_slug():
    """4-token ceiling: 'a-b-c-d-e' has 5 tokens (4 hyphens) → reject."""
    assert _validate_canonical_key("marcus-comp-below-market-rate") is False


def test_rejects_empty_string():
    assert _validate_canonical_key("") is False


def test_rejects_underscore():
    assert _validate_canonical_key("has_underscore") is False


def test_rejects_space():
    assert _validate_canonical_key("has space") is False


def test_rejects_leading_hyphen():
    assert _validate_canonical_key("-leading-hyphen") is False


def test_rejects_trailing_hyphen():
    assert _validate_canonical_key("trailing-hyphen-") is False


def test_rejects_double_hyphen():
    assert _validate_canonical_key("double--hyphen") is False


def test_rejects_single_char_first_token():
    """First token must be ≥2 chars: 'a-b' has 1-char first token → reject.

    This is the deliberate letter-first-≥2 regex choice. Single-letter tokens
    like 'x-factor' also fail; iterate the regex if a real case needs them.
    """
    assert _validate_canonical_key("a-b") is False


def test_rejects_leading_digit():
    """Letter-first: '401k-vesting-risk' fails. Noted in the validator's
    docstring comment as deliberate."""
    assert _validate_canonical_key("401k-vesting-risk") is False


def test_rejects_non_string_input():
    assert _validate_canonical_key(None) is False  # type: ignore[arg-type]
    assert _validate_canonical_key(42) is False  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Post-extraction validation — walks payload, sets invalid keys to "",
# appends a capture_warning listing offenders.
# ---------------------------------------------------------------------------

def test_post_validation_mixed_payload():
    """Valid key preserved; invalid key blanked; missing key left missing;
    a capture_warning is appended summarizing the offenders."""
    payload = {
        "live_constraints": [
            {"constraint": "c1", "canonical_key": "valid-one-here"},
            {"constraint": "c2", "canonical_key": "BAD-KEY"},
            {"constraint": "c3"},  # canonical_key field absent
        ]
    }
    warnings: list[str] = []
    offenders = _apply_canonical_key_validation(payload, warnings)

    assert payload["live_constraints"][0]["canonical_key"] == "valid-one-here"
    assert payload["live_constraints"][1]["canonical_key"] == ""
    assert "canonical_key" not in payload["live_constraints"][2]
    assert offenders == ["BAD-KEY"]
    assert len(warnings) == 1
    assert "canonical_key validation" in warnings[0]


def test_post_validation_all_valid_no_warning():
    """If every canonical_key is valid, no capture_warning is added."""
    payload = {
        "live_constraints": [
            {"constraint": "c1", "canonical_key": "alpha-beta"},
            {"constraint": "c2", "canonical_key": "gamma-delta-epsilon"},
        ]
    }
    warnings: list[str] = []
    offenders = _apply_canonical_key_validation(payload, warnings)
    assert offenders == []
    assert warnings == []
    assert payload["live_constraints"][0]["canonical_key"] == "alpha-beta"


def test_post_validation_no_live_constraints_key():
    """If payload has no live_constraints field, function is a no-op."""
    payload = {"some_other_field": "x"}
    warnings: list[str] = []
    offenders = _apply_canonical_key_validation(payload, warnings)
    assert offenders == []
    assert warnings == []


def test_post_validation_empty_string_counts_as_invalid():
    """An explicit empty canonical_key (LLM wrote "") counts as invalid and
    goes into the offenders list even though the field stays empty."""
    payload = {
        "live_constraints": [
            {"constraint": "c1", "canonical_key": ""},
        ]
    }
    warnings: list[str] = []
    offenders = _apply_canonical_key_validation(payload, warnings)
    assert offenders == [""]
    assert len(warnings) == 1
    assert payload["live_constraints"][0]["canonical_key"] == ""


def test_audit_seed_prefers_actual_assistant_text_without_changing_legacy_mapping():
    payload = {
        "decision_situation": "Should we accept the offer?",
        "synthesized_position": "Legacy synthesis.",
        "reasoning_passages": [],
    }

    audit_seed = _build_audit_seed(payload, assistant_text="Actual assistant reply.")
    critique_request = _map_to_critique_request(
        payload,
        assistant_text="Actual assistant reply.",
    )

    assert audit_seed["case_focus"] == "Should we accept the offer?"
    assert audit_seed["audit_target_assistant_text"] == "Actual assistant reply."
    assert critique_request["vanilla_answer"] == "Legacy synthesis."


def test_capture_validation_marks_final_user_turn_critical():
    transcript = """CONVERSATION: 3 turns, 2 user messages, 1 assistant responses
[Turn 1] USER:
Should I take the job?

[Turn 1] ASSISTANT:
Only if the role survives a downside test.

[Turn 2] USER:
What downside test?
"""

    result = _validate_conversation_capture(transcript)

    assert result["capture_health"] == "critical"
    assert result["capture_manifest"]["last_turn_role"] == "USER"
    assert any("ends on a user turn" in warning for warning in result["capture_warnings"])


def test_capture_validation_accepts_complete_last_assistant_turn():
    transcript = """CONVERSATION: 2 turns, 1 user messages, 1 assistant responses
[Turn 1] USER:
Should I take the job?

[Turn 1] ASSISTANT:
Only if the role survives a downside test.
"""

    result = _validate_conversation_capture(transcript)

    assert result["capture_health"] == "good"
    assert result["capture_manifest"]["last_turn_role"] == "ASSISTANT"
    assert result["capture_warnings"] == []


def test_reasoning_passage_validation_accepts_quote_wrapped_literal_span():
    transcript = (
        "[Turn 1] ASSISTANT:\n"
        "Conversational signal is real but not decision-grade.\n"
    )
    payload = {
        "reasoning_passages": [
            '"Conversational signal is real but not decision-grade."',
            '"this will impact the team"',
        ],
    }

    verified, fabricated = _validate_reasoning_passages(payload, transcript)

    assert verified == ["Conversational signal is real but not decision-grade."]
    assert fabricated == ['"this will impact the team"']
