from __future__ import annotations

from engine.system_b.capture_adequacy import (
    CAPTURE_ADEQUACY_SCHEMA_VERSION,
    build_capture_adequacy,
)


def test_capture_adequacy_full_capture_is_good() -> None:
    text = (
        "CONVERSATION: 4 turns, 2 user messages, 2 assistant responses\n\n"
        "[Turn 1] USER:\nQuestion.\n\n"
        "[Turn 1] ASSISTANT:\nAnswer.\n\n"
        "[Turn 2] USER:\nFollow-up.\n\n"
        "[Turn 2] ASSISTANT:\nAnswer two.\n"
    )

    payload = build_capture_adequacy(
        conversation_text=text,
        run_id="run123",
        capture_manifest={
            "declared_turns": 4,
            "declared_user": 2,
            "declared_assistant": 2,
            "actual_user_turns": 2,
            "actual_assistant_turns": 2,
        },
        capture_health="good",
    )

    assert payload["schema_version"] == CAPTURE_ADEQUACY_SCHEMA_VERSION
    assert payload["status"] == "good"
    assert payload["capture_strategy"] == "full"
    assert payload["declared_turn_count"] == 4
    assert payload["captured_turn_count"] == 4
    assert payload["omitted_turn_count"] == 0
    assert payload["captured_windows"] == [
        {"label": "full", "start_turn": 1, "end_turn": 4, "turn_count": 4}
    ]
    assert payload["omitted_windows"] == []
    assert payload["risk_flags"] == []


def test_capture_adequacy_first_plus_last_records_middle_omission() -> None:
    text = "\n".join(
        [
            "CONVERSATION: 30 turns, 15 user messages, 15 assistant responses",
            "[Turn 1] USER:",
            "Opening.",
            "[... 12 turns omitted for brevity ...]",
            "[Turn 16] ASSISTANT:",
            "Recent.",
        ]
    )

    payload = build_capture_adequacy(
        conversation_text=text,
        capture_manifest={
            "truncation_applied": True,
            "total_turns": 30,
            "kept_turns": 18,
            "keep_first_turns": 3,
            "keep_last_turns": 15,
            "omitted_turns": 12,
            "actual_user_turns": 15,
            "actual_assistant_turns": 15,
        },
        capture_health="good",
    )

    assert payload["status"] == "warn"
    assert payload["capture_strategy"] == "first_n_plus_last_n"
    assert payload["declared_turn_count"] == 30
    assert payload["captured_turn_count"] == 18
    assert payload["omitted_turn_count"] == 12
    assert payload["captured_windows"] == [
        {"label": "opening", "start_turn": 1, "end_turn": 3, "turn_count": 3},
        {"label": "recent", "start_turn": 16, "end_turn": 30, "turn_count": 15},
    ]
    assert payload["omitted_windows"] == [
        {"start_turn": 4, "end_turn": 15, "turn_count": 12}
    ]
    assert "middle_turns_omitted" in payload["risk_flags"]


def test_capture_adequacy_zero_user_turns_is_critical() -> None:
    payload = build_capture_adequacy(
        conversation_text="[Turn 1] ASSISTANT:\nOnly an answer.\n",
        capture_manifest={
            "declared_turns": 1,
            "declared_user": 1,
            "declared_assistant": 1,
            "actual_user_turns": 0,
            "actual_assistant_turns": 1,
        },
        capture_health="degraded",
    )

    assert payload["status"] == "critical"
    assert "zero_user_turns_captured" in payload["risk_flags"]
