"""Tests for run_extract.py — canonical_key slug validation and
post-extraction invalid-key handling.

TDD scaffolding for PR #1 of the extraction contract roadmap.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import run_extract  # noqa: E402
import scripts.run_pipeline as run_pipeline  # noqa: E402
from engine.system_b.agent_result import build_agent_result  # noqa: E402
from engine.system_b.extraction_adequacy_report import (  # noqa: E402
    build_extraction_adequacy_report,
)
from engine.system_b.reasoning_trace import build_reasoning_trace  # noqa: E402
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


def _write_long_conversation(path: Path) -> str:
    parts = [
        "CONVERSATION: 140 turns, 70 user messages, 70 assistant responses\n"
    ]
    for index in range(1, 71):
        parts.append(
            f"[Turn {index}] USER:\nQuestion {index} " + ("u" * 600) + "\n\n"
        )
        parts.append(
            f"[Turn {index}] ASSISTANT:\nAnswer {index} " + ("a" * 600) + "\n\n"
        )
    text = "".join(parts)
    path.write_text(text, encoding="utf-8")
    return text


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
        record_fields: dict | None = None,
    ) -> None:
        if isinstance(payload, list):
            self.payloads = payload or [{}]
        else:
            self.payloads = [payload or {}]
        self.error = error
        self.status = status
        self.record_fields = dict(record_fields or {})
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
                **self.record_fields,
            }
        )
        if self.error is not None:
            raise self.error
        return payload


def _install_provider_free_pipeline_fakes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    import system_b.boundary_provider as boundary_provider
    import system_b.bullshit_index as bullshit_index
    import system_b.pipeline as pipeline_mod

    class _FakeSubstrate:
        def all_chunks(self) -> tuple[object, ...]:
            return (object(),)

    class _FakeBundleSelector:
        _substrate = _FakeSubstrate()

    class _FakePipeline:
        _embedding_retriever = None
        _bundle_selector = _FakeBundleSelector()

        def run(self, pipeline_input: object) -> object:  # noqa: ARG002
            return SimpleNamespace(
                delta_card=SimpleNamespace(findings=[]),
                frame_pressure_card=None,
                audit=SimpleNamespace(
                    warnings=[],
                    companion_fingerprint_validated=[object()],
                ),
                prompt_versions={},
            )

    class _FakeBullshitProfile:
        def to_payload(self) -> dict:
            return {"status": "skipped-test-double"}

    def _load_live(cls, *, root, provider_name, config):  # noqa: ANN001, ARG001
        return _FakePipeline()

    monkeypatch.setattr(run_pipeline, "_resolve_data_root", lambda: tmp_path)
    monkeypatch.setattr(run_pipeline, "_serialize_result", lambda result, **kwargs: {})
    monkeypatch.setattr(pipeline_mod.SystemBPipeline, "load_live", classmethod(_load_live))
    monkeypatch.setattr(
        boundary_provider,
        "load_boundary_client_from_env",
        lambda provider_name: object(),
    )
    monkeypatch.setattr(
        bullshit_index,
        "evaluate_text",
        lambda text, client, *, context_summary: _FakeBullshitProfile(),
    )


def test_long_extraction_declares_exact_bounded_source_coverage(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run_id = "run_extract_long_source_coverage"
    conversation_path = tmp_path / f"lolla_{run_id}_conversation.txt"
    output_path = tmp_path / f"lolla_{run_id}_extraction.json"
    sidecar_path = Path(f"/tmp/lolla_{run_id}_extraction_calls.json")
    sidecar_path.unlink(missing_ok=True)
    authoritative = _write_long_conversation(conversation_path)
    assert len(authoritative) > run_extract.MAX_CONVERSATION_CHARS

    monkeypatch.setenv("LOLLA_RUN_ID", run_id)
    monkeypatch.setattr(
        run_extract,
        "load_boundary_client_from_env",
        lambda provider: _RecordedFakeClient(  # noqa: ARG005
            {
                "is_strategic": True,
                "decision_situation": "Whether to continue the long-running project.",
                "synthesized_position": "Continue only with an explicit review gate.",
                "reasoning_passages": ["Answer 70"],
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
        manifest = payload["capture_manifest"]
        adequacy = payload["capture_adequacy"]
        processing_view = payload["conversation_processing_view"]

        assert conversation_path.read_text(encoding="utf-8") == authoritative
        assert manifest["truncation_applied"] is True
        assert manifest["total_turns"] == 140
        assert manifest["kept_turns"] == 18
        assert manifest["omitted_turns"] == 122
        assert adequacy["status"] == "warn"
        assert adequacy["capture_strategy"] == "first_n_plus_last_n"
        assert adequacy["declared_turn_count"] == 140
        assert adequacy["captured_turn_count"] == 18
        assert adequacy["omitted_turn_count"] == 122
        assert adequacy["captured_windows"] == [
            {"label": "opening", "start_turn": 1, "end_turn": 3, "turn_count": 3},
            {"label": "recent", "start_turn": 126, "end_turn": 140, "turn_count": 15},
        ]
        assert adequacy["omitted_windows"] == [
            {"start_turn": 4, "end_turn": 125, "turn_count": 122}
        ]
        assert processing_view["status"] == "partial"
        assert processing_view["omitted_turn_count"] == 122
        assert processing_view["authoritative_conversation_preserved"] is True

        pipeline_output = tmp_path / f"lolla_{run_id}_result.json"
        _install_provider_free_pipeline_fakes(monkeypatch, tmp_path)
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "run_pipeline.py",
                "--extraction-file",
                str(output_path),
                "--conversation-file",
                str(conversation_path),
                "--output-file",
                str(pipeline_output),
                "--skip-revision",
                "--embeddings",
                "off",
                "--v60-enrichment",
                "off",
            ],
        )
        assert run_pipeline.main() == 0
        result = json.loads(pipeline_output.read_text(encoding="utf-8"))
        health = result["run_health"]
        assert health["overall"] == "degraded"
        assert health["capture_adequacy"] == adequacy
        assert health["authoritative_conversation_preserved"] is True
        assert health["extraction_processing_view_status"] == "partial"
        assert health["processing_view_omitted_turns"] == 122
        assert "extraction_processing_view_partial" in health["issues"]
        assert "capture_truncated" not in health["issues"]
        capture_issue = next(
            item
            for item in health["issue_details"]
            if item["code"] == "extraction_processing_view_partial"
        )
        assert capture_issue["axis"] == "extraction"
        assert capture_issue["omitted_turns"] == 122

        run_dir = tmp_path / "archive" / run_id
        run_dir.mkdir(parents=True)
        shutil.copy2(conversation_path, run_dir / "conversation.txt")
        shutil.copy2(output_path, run_dir / "extraction.json")
        shutil.copy2(pipeline_output, run_dir / "result.json")
        for source_name, archive_name in (
            (f"lolla_{run_id}_conversation_processing_view.txt", "conversation_processing_view.txt"),
            (f"lolla_{run_id}_conversation_processing_view.json", "conversation_processing_view.json"),
        ):
            shutil.copy2(tmp_path / source_name, run_dir / archive_name)

        agent_result = build_agent_result(
            run_dir,
            run_id=run_id,
            case_id="long-source-coverage",
            created_at="2026-07-15T00:00:00Z",
        )
        adequacy_report = build_extraction_adequacy_report(
            run_dir,
            run_id=run_id,
            case_id="long-source-coverage",
            created_at="2026-07-15T00:00:00Z",
        )
        trace = build_reasoning_trace(
            run_dir,
            run_id=run_id,
            case_id="long-source-coverage",
            fingerprint="long-source-coverage",
            how_matched="new",
            files_copied=[path.name for path in run_dir.iterdir()],
            files_missing=[],
            manifest={"run_count": 1},
            created_at="2026-07-15T00:00:00Z",
        )

        assert agent_result["capture_adequacy"]["status"] == "warn"
        assert agent_result["capture_adequacy"]["omitted_turn_count"] == 122
        assert agent_result["source_coverage"]["authoritative_conversation_preserved"] is True
        assert agent_result["source_coverage"]["extraction_processing_view_status"] == "partial"
        assert agent_result["source_coverage"]["authoritative_turn_count"] == 140
        assert agent_result["source_coverage"]["extraction_processing_turn_count"] == 18
        assert agent_result["source_coverage"]["extraction_omitted_turn_count"] == 122
        assert adequacy_report["capture_summary"]["truncation_applied"] is True
        assert adequacy_report["capture_summary"]["omitted_turn_count"] == 122
        assert adequacy_report["capture_summary"]["authoritative_conversation_preserved"] is True
        assert adequacy_report["capture_summary"]["extraction_processing_view_status"] == "partial"
        assert trace["capture"]["capture_adequacy"]["omitted_turn_count"] == 122
        assert trace["capture"]["source_coverage"] == agent_result["source_coverage"]
    finally:
        sidecar_path.unlink(missing_ok=True)


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


def test_provider_finish_error_preempts_semantic_missing_fields(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run_id = "run_extract_finish_error_custody"
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
                "decision_situation": "",
                "synthesized_position": "",
            },
            status="provider_finish_error",
            record_fields={
                "finish_reason": "error",
                "provider_error_source": "choice",
                "provider_error_type": "provider_unavailable",
                "provider_error_code": "503",
                "provider_error_provider_code": "UNAVAILABLE",
                "provider_error_message_sha256": "a" * 64,
            },
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
        assert payload["error"] == (
            "Extraction provider call did not complete: provider_finish_error"
        )
        assert "raw_extraction" not in payload
        assert payload["provider_failure"] == {
            "status": "provider_finish_error",
            "finish_reason": "error",
            "provider_error_source": "choice",
            "provider_error_type": "provider_unavailable",
            "provider_error_code": "503",
            "provider_error_provider_code": "UNAVAILABLE",
            "provider_error_message_sha256": "a" * 64,
            "retry_after_seconds": None,
            "response_id": "",
            "raw_message_content_present": True,
            "raw_message_content_chars": len(
                json.dumps(
                    {
                        "is_strategic": True,
                        "decision_situation": "",
                        "synthesized_position": "",
                    }
                )
            ),
        }
        custody = payload["provider_call_custody"]
        assert custody["terminal_status"] == "provider_finish_error"
        assert custody["admissible_extraction"] is False
    finally:
        sidecar_path.unlink(missing_ok=True)


def test_extraction_call_sidecar_preserves_prior_process_attempts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run_id = "run_extract_preserve_prior_attempt"
    output_path = tmp_path / f"lolla_{run_id}_extraction.json"
    sidecar_path = Path(f"/tmp/lolla_{run_id}_extraction_calls.json")
    prior = {
        "stage": "extraction",
        "status": "url_error",
        "provider_attempted": True,
        "budget_reservation_id": "reservation-one",
    }
    sidecar_path.write_text(json.dumps([prior]), encoding="utf-8")
    client = _RecordedFakeClient(
        {"is_strategic": True},
        status="provider_finish_error",
        record_fields={"budget_reservation_id": "reservation-two"},
    )
    client.run_json("system", "user", stage="extraction")

    try:
        custody = run_extract._persist_extraction_call_sidecar(
            client,
            run_id=run_id,
            output_file=str(output_path),
            terminal_status="provider_finish_error",
            admissible_extraction=False,
        )
        records = json.loads(sidecar_path.read_text(encoding="utf-8"))
        assert [record["budget_reservation_id"] for record in records] == [
            "reservation-one",
            "reservation-two",
        ]
        assert custody["recorded_call_count"] == 2
        assert custody["call_attempted"] is True
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
        assert payload["error"] == (
            "Extraction provider call raised an unexpected RuntimeError."
        )
        assert payload["provider_failure"]["status"] == "unexpected_error"
        custody = payload["provider_call_custody"]
        assert custody["call_attempted"] is True
        assert custody["call_record_persisted"] is True
        assert custody["admissible_extraction"] is False
        assert custody["terminal_status"] == "unexpected_error"
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
