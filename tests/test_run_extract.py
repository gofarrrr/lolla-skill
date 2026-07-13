"""Tests for run_extract.py — canonical_key slug validation and
post-extraction invalid-key handling.

TDD scaffolding for PR #1 of the extraction contract roadmap.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import run_extract  # noqa: E402
from run_extract import (  # noqa: E402
    _apply_canonical_key_validation,
    _build_audit_seed,
    _map_to_critique_request,
    _validate_reasoning_passages,
    _validate_conversation_capture,
    _validate_canonical_key,
    _prepare_output_parent,
)


def _write_conversation(path: Path) -> None:
    path.write_text(
        "CONVERSATION: 2 turns, 1 user messages, 1 assistant responses\n"
        "[Turn 1] USER:\n"
        "Should I accept this offer?\n\n"
        "[Turn 1] ASSISTANT:\n"
        "Accept only if the downside is bounded.\n",
        encoding="utf-8",
    )


class _FakeClient:
    call_log = []

    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def run_json(self, *args, **kwargs) -> dict:  # noqa: ANN002, ANN003, ARG002
        return self.payload


class _RecordedFakeClient:
    def __init__(
        self,
        payload: dict | list[dict] | None = None,
        *,
        error: Exception | None = None,
        status: str = "ok",
    ) -> None:
        if isinstance(payload, list):
            self.payloads = payload or [{}]
        else:
            self.payloads = [payload or {}]
        self.error = error
        self.status = status
        self.call_log: list[dict] = []

    def run_json(self, *args, **kwargs) -> dict:  # noqa: ANN002, ANN003, ARG002
        stage = str(kwargs.get("stage", "unlabeled"))
        payload = self.payloads[min(len(self.call_log), len(self.payloads) - 1)]
        self.call_log.append(
            {
                "stage": stage,
                "provider_name": "openrouter",
                "requested_model": "google/gemini-3.1-flash-lite",
                "served_model": "google/gemini-3.1-flash-lite",
                "model": "google/gemini-3.1-flash-lite",
                "model_attribution_status": "matched",
                "status": self.status,
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150,
                "cached_tokens": 0,
                "raw_message_content": json.dumps(payload),
            }
        )
        if self.error is not None:
            raise self.error
        return payload


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


def test_capture_validation_no_header_final_user_turn_is_critical():
    transcript = """[Turn 1] USER:
Should I take the job?

[Turn 1] ASSISTANT:
Only if the role survives a downside test.

[Turn 2] USER:
What downside test?
"""

    result = _validate_conversation_capture(transcript)

    assert result["capture_health"] == "critical"
    assert result["capture_manifest"]["last_turn_role"] == "USER"
    assert any("CONVERSATION" in warning for warning in result["capture_warnings"])
    assert any("ends on a user turn" in warning for warning in result["capture_warnings"])


def test_capture_validation_no_header_complete_assistant_turn_is_warning_bearing():
    transcript = """[Turn 1] USER:
Should I take the job?

[Turn 1] ASSISTANT:
Only if the role survives a downside test.
"""

    result = _validate_conversation_capture(transcript)

    assert result["capture_health"] == "unknown"
    assert result["capture_manifest"]["last_turn_role"] == "ASSISTANT"
    assert any("CONVERSATION" in warning for warning in result["capture_warnings"])


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


def test_reasoning_passage_validation_recovers_literal_source_quote_delimiters() -> None:
    transcript = (
        '[Turn 1] ASSISTANT:\nThe "if it\'s escape not fit, stay" framing still holds.\n'
    )
    payload = {
        "reasoning_passages": [
            "The 'if it's escape not fit, stay' framing still holds."
        ]
    }

    verified, fabricated = _validate_reasoning_passages(payload, transcript)

    assert fabricated == []
    assert verified == ['The "if it\'s escape not fit, stay" framing still holds.']


def test_reasoning_passage_validation_keeps_apostrophes_semantically_significant() -> None:
    transcript = "[Turn 1] ASSISTANT:\nIt isn't safe to assume consent.\n"
    payload = {"reasoning_passages": ["It isnt safe to assume consent."]}

    verified, fabricated = _validate_reasoning_passages(payload, transcript)

    assert verified == []
    assert fabricated == ["It isnt safe to assume consent."]


def test_not_strategic_path_writes_output_file_with_capture_diagnostics(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    run_id = "run_extract_not_strategic_custody"
    conversation_path = tmp_path / "conversation.txt"
    output_path = tmp_path / f"lolla_{run_id}_extraction.json"
    sidecar_path = Path(f"/tmp/lolla_{run_id}_extraction_calls.json")
    sidecar_path.unlink(missing_ok=True)
    _write_conversation(conversation_path)
    monkeypatch.setenv("LOLLA_RUN_ID", run_id)
    monkeypatch.setattr(
        run_extract,
        "load_boundary_client_from_env",
        lambda provider: _RecordedFakeClient({  # noqa: ARG005
            "is_strategic": False,
            "decline_reason": "Not a decision conversation.",
        }),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_extract.py",
            "--conversation-file",
            str(conversation_path),
            "--output-file",
            str(output_path),
        ],
    )

    try:
        assert run_extract.main() == 0
        assert output_path.exists()
        payload = json.loads(output_path.read_text(encoding="utf-8"))
        assert payload["status"] == "not_strategic"
        assert payload["capture_health"] == "good"
        assert "capture_manifest" in payload
        assert payload["capture_adequacy"]["status"] == "good"
        assert payload["capture_adequacy"]["capture_strategy"] == "full"
        assert "capture_warnings" in payload
        custody = payload["provider_call_custody"]
        assert custody["call_attempted"] is True
        assert custody["call_record_persisted"] is True
        assert custody["recorded_call_count"] == 1
        assert custody["admissible_extraction"] is False
        assert custody["terminal_status"] == "not_strategic"
        assert len(json.loads(sidecar_path.read_text(encoding="utf-8"))) == 1
        assert capsys.readouterr().out
    finally:
        sidecar_path.unlink(missing_ok=True)


def test_missing_required_fields_path_writes_output_file_with_capture_diagnostics(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    run_id = "run_extract_missing_fields_custody"
    conversation_path = tmp_path / "conversation.txt"
    output_path = tmp_path / f"lolla_{run_id}_extraction.json"
    sidecar_path = Path(f"/tmp/lolla_{run_id}_extraction_calls.json")
    sidecar_path.unlink(missing_ok=True)
    _write_conversation(conversation_path)
    monkeypatch.setenv("LOLLA_RUN_ID", run_id)
    monkeypatch.setattr(
        run_extract,
        "load_boundary_client_from_env",
        lambda provider: _RecordedFakeClient({  # noqa: ARG005
            "is_strategic": True,
            "decision_situation": "",
            "synthesized_position": "",
        }),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_extract.py",
            "--conversation-file",
            str(conversation_path),
            "--output-file",
            str(output_path),
        ],
    )

    try:
        assert run_extract.main() == 1
        assert output_path.exists()
        payload = json.loads(output_path.read_text(encoding="utf-8"))
        assert payload["status"] == "error"
        assert "Extraction missing required fields" in payload["error"]
        assert payload["capture_health"] == "good"
        assert "capture_manifest" in payload
        assert payload["capture_adequacy"]["status"] == "good"
        assert "capture_warnings" in payload
        custody = payload["provider_call_custody"]
        assert custody["call_attempted"] is True
        assert custody["sidecar_persisted"] is True
        assert custody["call_record_persisted"] is True
        assert custody["recorded_call_count"] == 1
        assert custody["admissible_extraction"] is False
        assert custody["terminal_status"] == "missing_required_fields"
        records = json.loads(sidecar_path.read_text(encoding="utf-8"))
        assert records[0]["stage"] == "extraction"
    finally:
        sidecar_path.unlink(missing_ok=True)


def test_provider_exception_persists_failed_call_record_before_error_exit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run_id = "run_extract_provider_error_custody"
    conversation_path = tmp_path / "conversation.txt"
    output_path = tmp_path / f"lolla_{run_id}_extraction.json"
    sidecar_path = Path(f"/tmp/lolla_{run_id}_extraction_calls.json")
    sidecar_path.unlink(missing_ok=True)
    _write_conversation(conversation_path)
    monkeypatch.setenv("LOLLA_RUN_ID", run_id)
    monkeypatch.setattr(
        run_extract,
        "load_boundary_client_from_env",
        lambda provider: _RecordedFakeClient(  # noqa: ARG005
            error=RuntimeError("provider broke"),
            status="unexpected_error",
        ),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_extract.py",
            "--conversation-file",
            str(conversation_path),
            "--output-file",
            str(output_path),
        ],
    )

    try:
        assert run_extract.main() == 1
        payload = json.loads(output_path.read_text(encoding="utf-8"))
        assert payload["status"] == "error"
        assert "OpenRouter call failed" in payload["error"]
        custody = payload["provider_call_custody"]
        assert custody["call_attempted"] is True
        assert custody["call_record_persisted"] is True
        assert custody["admissible_extraction"] is False
        assert custody["terminal_status"] == "initial_provider_call_failed"
        records = json.loads(sidecar_path.read_text(encoding="utf-8"))
        assert records[0]["status"] == "unexpected_error"
    finally:
        sidecar_path.unlink(missing_ok=True)


def test_success_path_declares_admissible_extraction_and_persists_call_record(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run_id = "run_extract_success_custody"
    conversation_path = tmp_path / "conversation.txt"
    output_path = tmp_path / f"lolla_{run_id}_extraction.json"
    sidecar_path = Path(f"/tmp/lolla_{run_id}_extraction_calls.json")
    sidecar_path.unlink(missing_ok=True)
    _write_conversation(conversation_path)
    monkeypatch.setenv("LOLLA_RUN_ID", run_id)
    monkeypatch.setattr(
        run_extract,
        "load_boundary_client_from_env",
        lambda provider: _RecordedFakeClient(  # noqa: ARG005
            {
                "is_strategic": True,
                "decision_situation": "Whether to accept the offer.",
                "synthesized_position": "Accept only with bounded downside.",
                "reasoning_passages": [
                    "Accept only if the downside is bounded."
                ],
            }
        ),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_extract.py",
            "--conversation-file",
            str(conversation_path),
            "--output-file",
            str(output_path),
        ],
    )

    try:
        assert run_extract.main() == 0
        payload = json.loads(output_path.read_text(encoding="utf-8"))
        assert payload["status"] == "ok"
        custody = payload["provider_call_custody"]
        assert custody["call_attempted"] is True
        assert custody["sidecar_persisted"] is True
        assert custody["call_record_persisted"] is True
        assert custody["recorded_call_count"] == 1
        assert custody["admissible_extraction"] is True
        assert custody["terminal_status"] == "admissible_extraction"
        records = json.loads(sidecar_path.read_text(encoding="utf-8"))
        assert records[0]["stage"] == "extraction"
    finally:
        sidecar_path.unlink(missing_ok=True)


def test_success_path_persists_canonical_source_span_after_casefold_match(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run_id = "run_extract_canonical_quote_custody"
    conversation_path = tmp_path / "conversation.txt"
    output_path = tmp_path / f"lolla_{run_id}_extraction.json"
    sidecar_path = Path(f"/tmp/lolla_{run_id}_extraction_calls.json")
    sidecar_path.unlink(missing_ok=True)
    conversation_path.write_text(
        "CONVERSATION: 2 turns, 1 user messages, 1 assistant responses\n"
        "[Turn 1] USER:\nShould I accept this offer?\n\n"
        "[Turn 1] ASSISTANT:\nBut if the downside is bounded, accept.\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("LOLLA_RUN_ID", run_id)
    monkeypatch.setattr(
        run_extract,
        "load_boundary_client_from_env",
        lambda provider: _RecordedFakeClient(  # noqa: ARG005
            {
                "is_strategic": True,
                "decision_situation": "Whether to accept the offer.",
                "synthesized_position": "Accept only with bounded downside.",
                "reasoning_passages": ["If the downside is bounded, accept."],
            }
        ),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_extract.py",
            "--conversation-file",
            str(conversation_path),
            "--output-file",
            str(output_path),
        ],
    )

    try:
        assert run_extract.main() == 0
        payload = json.loads(output_path.read_text(encoding="utf-8"))
        assert payload["extraction"]["reasoning_passages"] == [
            "if the downside is bounded, accept."
        ]
        assert payload["extraction"]["_quote_validation"]["fabricated"] == 0
    finally:
        sidecar_path.unlink(missing_ok=True)


def test_quote_repair_updates_sidecar_with_both_call_records(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run_id = "run_extract_quote_repair_custody"
    conversation_path = tmp_path / "conversation.txt"
    output_path = tmp_path / f"lolla_{run_id}_extraction.json"
    sidecar_path = Path(f"/tmp/lolla_{run_id}_extraction_calls.json")
    sidecar_path.unlink(missing_ok=True)
    _write_conversation(conversation_path)
    common = {
        "is_strategic": True,
        "decision_situation": "Whether to accept the offer.",
        "synthesized_position": "Accept only with bounded downside.",
    }
    client = _RecordedFakeClient(
        [
            {
                **common,
                "reasoning_passages": ["A paraphrase that is not in the source."],
            },
            {
                **common,
                "reasoning_passages": [
                    "Accept only if the downside is bounded."
                ],
            },
        ]
    )
    monkeypatch.setenv("LOLLA_RUN_ID", run_id)
    monkeypatch.setattr(
        run_extract,
        "load_boundary_client_from_env",
        lambda provider: client,  # noqa: ARG005
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_extract.py",
            "--conversation-file",
            str(conversation_path),
            "--output-file",
            str(output_path),
        ],
    )

    try:
        assert run_extract.main() == 0
        payload = json.loads(output_path.read_text(encoding="utf-8"))
        custody = payload["provider_call_custody"]
        assert custody["recorded_call_count"] == 2
        assert custody["admissible_extraction"] is True
        quote = payload["extraction"]["_quote_validation"]
        assert quote["retry_attempted"] is True
        assert quote["retry_succeeded"] is True
        records = json.loads(sidecar_path.read_text(encoding="utf-8"))
        assert [record["stage"] for record in records] == [
            "extraction",
            "extraction_retry",
        ]
    finally:
        sidecar_path.unlink(missing_ok=True)


def test_output_parent_is_created_before_provider_call(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    conversation_path = tmp_path / "conversation.txt"
    output_path = tmp_path / "new" / "nested" / "extraction.json"
    _write_conversation(conversation_path)
    provider_observations: list[bool] = []

    def _client(provider: str) -> _FakeClient:  # noqa: ARG001
        provider_observations.append(output_path.parent.is_dir())
        return _FakeClient(
            {
                "is_strategic": False,
                "decline_reason": "Test stops after path preflight.",
            }
        )

    monkeypatch.setattr(run_extract, "load_boundary_client_from_env", _client)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_extract.py",
            "--conversation-file",
            str(conversation_path),
            "--output-file",
            str(output_path),
        ],
    )

    assert run_extract.main() == 0
    assert provider_observations == [True]
    assert output_path.exists()


def test_output_parent_preflight_failure_happens_without_provider_call(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    conversation_path = tmp_path / "conversation.txt"
    _write_conversation(conversation_path)
    blocking_file = tmp_path / "not-a-directory"
    blocking_file.write_text("block", encoding="utf-8")
    output_path = blocking_file / "extraction.json"

    def _unexpected_client(provider: str) -> _FakeClient:  # noqa: ARG001
        raise AssertionError("provider must not initialize after path preflight failure")

    monkeypatch.setattr(
        run_extract,
        "load_boundary_client_from_env",
        _unexpected_client,
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_extract.py",
            "--conversation-file",
            str(conversation_path),
            "--output-file",
            str(output_path),
        ],
    )

    assert run_extract.main() == 1
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "error"
    assert "Unable to prepare output directory" in output["error"]


def test_prepare_output_parent_accepts_stdout_mode() -> None:
    assert _prepare_output_parent(None) is None
