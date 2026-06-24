from __future__ import annotations

from scripts.skill.validate_conversation_capture import validate_capture


def test_validate_conversation_capture_accepts_lolla_turn_format() -> None:
    ok, errors, manifest = validate_capture(
        "CONVERSATION: 1 turn, 1 user message, 1 assistant response\n\n"
        "[Turn 1] USER:\n"
        "Should I grant equity?\n\n"
        "[Turn 1] ASSISTANT:\n"
        "Only after testing alignment.\n"
    )

    assert ok is True
    assert errors == []
    assert manifest["actual_user_turns"] == 1
    assert manifest["actual_assistant_turns"] == 1


def test_validate_conversation_capture_rejects_unmarked_chat_export() -> None:
    ok, errors, manifest = validate_capture(
        "USER: Should I grant equity?\n\n"
        "ASSISTANT: Only after testing alignment.\n"
    )

    assert ok is False
    assert manifest["actual_user_turns"] == 0
    assert any("CONVERSATION header" in error for error in errors)
    assert any("no [Turn N] USER markers" in error for error in errors)
    assert any("no [Turn N] ASSISTANT markers" in error for error in errors)


def test_validate_conversation_capture_rejects_final_user_turn() -> None:
    ok, errors, _manifest = validate_capture(
        "CONVERSATION: 2 turns, 2 user messages, 1 assistant response\n\n"
        "[Turn 1] USER:\n"
        "Should I grant equity?\n\n"
        "[Turn 1] ASSISTANT:\n"
        "Only after testing alignment.\n\n"
        "[Turn 2] USER:\n"
        "What test?\n"
    )

    assert ok is False
    assert any("must end with an assistant answer" in error for error in errors)
