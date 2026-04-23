"""Tests for the Phase 1 conversation-context loader."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.system_b.conversation_loader import load_conversation_context


_CONVO_HEADER = "CONVERSATION: 2 turns, 2 user messages, 2 assistant responses\n\n"


def _write_fixture(
    tmp_path: Path,
    *,
    extraction: dict,
    conversation: str,
) -> tuple[Path, Path]:
    extraction_path = tmp_path / "extraction.json"
    conversation_path = tmp_path / "conversation.txt"
    extraction_path.write_text(json.dumps(extraction))
    conversation_path.write_text(conversation)
    return extraction_path, conversation_path


def _conversation_text_two_turns() -> str:
    return (
        _CONVO_HEADER
        + "[Turn 1] USER:\n"
        + "I have a decision to make.\n"
        + "Multiple lines of context.\n\n"
        + "[Turn 1] ASSISTANT:\n"
        + "Let me reflect on that.\n\n"
        + "[Turn 2] USER:\n"
        + "follow-up question\n\n"
        + "[Turn 2] ASSISTANT:\n"
        + "follow-up answer\n"
    )


def _ok_extraction(**overrides) -> dict:
    base = {
        "status": "ok",
        "extraction": {
            "is_strategic": True,
            "decision_situation": "A hard call",
            "live_constraints": [
                {
                    "constraint": "budget capped at 100k",
                    "introduced_turn": 1,
                    "status": "active",
                    "weight": "structural",
                    "canonical_key": "budget-cap",
                },
                {
                    "constraint": "timeline is 30 days",
                    "introduced_turn": 2,
                    "status": "active",
                    "weight": "situational",
                },
            ],
            "synthesized_position": "Take the offer with conditions.",
            "reasoning_passages": ["quote one", "quote two"],
            "original_framing": "Should I take this?",
            "dropped_threads": [
                {
                    "thread": "profit-sharing alternative",
                    "raised_by": "user",
                    "raised_turn": 1,
                    "status": "acknowledged_then_dropped",
                    "superseded_by": "full equity partnership",
                },
                {
                    "thread": "timeline concern",
                    "raised_by": "user",
                    "raised_turn": 2,
                    "status": "acknowledged_then_dropped",
                    "superseded_by": None,
                },
            ],
            "_quote_validation": {
                "retry_attempted": True,
                "retry_succeeded": True,
                "fabricated": 0,
            },
        },
        "capture_manifest": {
            "declared_turns": 2,
            "actual_user_turns": 2,
            "actual_assistant_turns": 2,
            "char_length": 150,
        },
        "capture_health": "good",
        "capture_warnings": ["minor note"],
    }
    base.update(overrides)
    return base


def test_load_basic_extraction_and_turns(tmp_path: Path) -> None:
    extraction_path, conversation_path = _write_fixture(
        tmp_path,
        extraction=_ok_extraction(),
        conversation=_conversation_text_two_turns(),
    )

    ctx = load_conversation_context(extraction_path, conversation_path)

    assert len(ctx.turns) == 4
    assert ctx.turns[0].speaker == "user"
    assert ctx.turns[0].turn_index == 1
    assert "I have a decision to make" in ctx.turns[0].text
    assert "Multiple lines of context" in ctx.turns[0].text  # multi-line body preserved
    assert ctx.turns[1].speaker == "assistant"
    assert ctx.turns[3].turn_index == 2


def test_load_extraction_fields_populate_correctly(tmp_path: Path) -> None:
    extraction_path, conversation_path = _write_fixture(
        tmp_path,
        extraction=_ok_extraction(),
        conversation=_conversation_text_two_turns(),
    )

    ctx = load_conversation_context(extraction_path, conversation_path)

    assert ctx.extraction.decision_situation == "A hard call"
    assert ctx.extraction.synthesized_position == "Take the offer with conditions."
    assert ctx.extraction.original_framing == "Should I take this?"
    assert ctx.extraction.reasoning_passages == ("quote one", "quote two")


def test_load_live_constraints_with_and_without_canonical_key(tmp_path: Path) -> None:
    extraction_path, conversation_path = _write_fixture(
        tmp_path,
        extraction=_ok_extraction(),
        conversation=_conversation_text_two_turns(),
    )

    ctx = load_conversation_context(extraction_path, conversation_path)

    assert len(ctx.extraction.live_constraints) == 2
    assert ctx.extraction.live_constraints[0].canonical_key == "budget-cap"
    assert ctx.extraction.live_constraints[1].canonical_key is None
    assert ctx.extraction.live_constraints[0].weight == "structural"


def test_load_dropped_threads_with_and_without_superseded_by(tmp_path: Path) -> None:
    extraction_path, conversation_path = _write_fixture(
        tmp_path,
        extraction=_ok_extraction(),
        conversation=_conversation_text_two_turns(),
    )

    ctx = load_conversation_context(extraction_path, conversation_path)

    assert len(ctx.extraction.dropped_threads) == 2
    assert ctx.extraction.dropped_threads[0].superseded_by == "full equity partnership"
    assert ctx.extraction.dropped_threads[1].superseded_by is None


def test_load_quote_validation_passes_through_intact(tmp_path: Path) -> None:
    extraction_path, conversation_path = _write_fixture(
        tmp_path,
        extraction=_ok_extraction(),
        conversation=_conversation_text_two_turns(),
    )

    ctx = load_conversation_context(extraction_path, conversation_path)

    qv = ctx.extraction.quote_validation
    assert qv["retry_attempted"] is True
    assert qv["retry_succeeded"] is True
    assert qv["fabricated"] == 0


def test_load_capture_metadata_preserved(tmp_path: Path) -> None:
    extraction_path, conversation_path = _write_fixture(
        tmp_path,
        extraction=_ok_extraction(),
        conversation=_conversation_text_two_turns(),
    )

    ctx = load_conversation_context(extraction_path, conversation_path)

    assert ctx.capture_health == "good"
    assert ctx.capture_warnings == ("minor note",)
    assert ctx.capture_manifest["declared_turns"] == 2
    assert ctx.capture_manifest["char_length"] == 150


def test_load_capture_critical_returns_valid_empty_context(tmp_path: Path) -> None:
    capture_critical = {
        "status": "capture_critical",
        "decline_reason": "headers declared 9 assistant turns, body has 0",
        "capture_manifest": {
            "declared_turns": 9,
            "actual_user_turns": 0,
            "actual_assistant_turns": 0,
            "char_length": 200,
        },
        "capture_health": "critical",
        "capture_warnings": ["capture_health critical"],
    }
    extraction_path, conversation_path = _write_fixture(
        tmp_path,
        extraction=capture_critical,
        conversation=_conversation_text_two_turns(),
    )

    ctx = load_conversation_context(extraction_path, conversation_path)

    assert ctx.capture_health == "critical"
    assert ctx.extraction.decision_situation == ""
    assert ctx.extraction.live_constraints == ()
    assert ctx.extraction.reasoning_passages == ()
    assert ctx.extraction.quote_validation == {}
    # turns still parse from the conversation text — they're independent of extraction
    assert len(ctx.turns) == 4


def test_load_real_10_case_corpus_oncologist(tmp_path: Path) -> None:
    """Sanity check against a real corpus conversation to catch drift in the
    parser if the capture format changes."""
    conversation_path = Path("research/test-cases/case_oncologist_conversation.txt")
    if not conversation_path.exists():
        pytest.skip("oncologist corpus not present")

    # Synthetic extraction pairing the real conversation — we're testing the
    # loader parser, not the extraction content.
    extraction = {
        "status": "ok",
        "extraction": {
            "is_strategic": True,
            "decision_situation": "career move decision",
            "live_constraints": [],
            "synthesized_position": "",
            "reasoning_passages": [],
            "original_framing": "",
            "dropped_threads": [],
            "_quote_validation": {},
        },
        "capture_manifest": {},
        "capture_health": "good",
        "capture_warnings": [],
    }
    extraction_path = tmp_path / "extraction.json"
    extraction_path.write_text(json.dumps(extraction))

    ctx = load_conversation_context(extraction_path, conversation_path)

    # The oncologist conversation header declares 9 turns. Speakers
    # alternate user/assistant. That's 18 turn entries total.
    user_turns = [t for t in ctx.turns if t.speaker == "user"]
    assistant_turns = [t for t in ctx.turns if t.speaker == "assistant"]
    assert len(user_turns) == 9
    assert len(assistant_turns) == 9
    assert ctx.turns[0].turn_index == 1
    assert ctx.turns[0].speaker == "user"
    # First turn opens with the Merck role mention
    assert "Merck" in ctx.turns[0].text


def test_load_empty_conversation_file_yields_zero_turns(tmp_path: Path) -> None:
    extraction_path, conversation_path = _write_fixture(
        tmp_path,
        extraction=_ok_extraction(),
        conversation="CONVERSATION: 0 turns\n\n",
    )

    ctx = load_conversation_context(extraction_path, conversation_path)

    assert ctx.turns == ()
    assert ctx.extraction.decision_situation == "A hard call"  # extraction still loads
