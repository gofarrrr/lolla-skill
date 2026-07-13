"""PR 1 — persist raw_message_content + finish_reason + temperature per boundary call.

Source memo: research/granular-visibility-audit-2026-04-28.md §"Per-call
telemetry" + Bucket B item 7. The data has always lived on
``BoundaryCallMetadata``; ``BoundaryCallRecord`` and ``BoundaryCallTrace``
just dropped it on the floor when they were built. These tests pin the
contract so every LLM decision becomes investigable from result.json
without re-running the pipeline.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.system_b.boundary_provider import (
    BoundaryCallMetadata,
    OpenAICompatibleBoundaryClient,
    _record_from_metadata,
)
from engine.system_b.boundary_tracing import (
    _capture_boundary_call,
    _metadata_to_boundary_call_trace,
)


def _populated_metadata() -> BoundaryCallMetadata:
    return BoundaryCallMetadata(
        provider_name="openrouter",
        model="x-ai/grok-4.1-fast",
        status="ok",
        finish_reason="stop",
        raw_message_content='{"hello": "world"}',
        temperature=0.2,
        prompt_tokens=10,
        completion_tokens=20,
        total_tokens=30,
    )


def test_record_from_metadata_carries_raw_finish_temperature():
    metadata = _populated_metadata()
    record = _record_from_metadata(metadata, stage="lane1.pass1", tendency_id="")

    assert record.raw_message_content == '{"hello": "world"}'
    assert record.finish_reason == "stop"
    assert record.temperature == 0.2


def test_metadata_to_boundary_call_trace_carries_raw_finish_temperature():
    metadata = _populated_metadata()
    trace = _metadata_to_boundary_call_trace(metadata, stage="lane1.pass1")

    assert trace.raw_message_content == '{"hello": "world"}'
    assert trace.finish_reason == "stop"
    assert trace.temperature == 0.2


def test_capture_boundary_call_reads_raw_finish_temperature_from_last_call():
    metadata = _populated_metadata()

    class _StubBoundary:
        def __init__(self, md: BoundaryCallMetadata) -> None:
            self.last_call_metadata = md

    trace = _capture_boundary_call(_StubBoundary(metadata), stage="lane3.frame")

    assert trace.raw_message_content == '{"hello": "world"}'
    assert trace.finish_reason == "stop"
    assert trace.temperature == 0.2


def test_record_and_trace_share_same_field_set_for_three_new_fields():
    """Drift between record and trace is the bug we are fixing — keep them in lockstep."""
    metadata = _populated_metadata()
    record = _record_from_metadata(metadata, stage="x", tendency_id="")
    trace = _metadata_to_boundary_call_trace(metadata, stage="x")

    for field_name in ("raw_message_content", "finish_reason", "temperature"):
        assert getattr(record, field_name) == getattr(trace, field_name), (
            f"record.{field_name} drifted from trace.{field_name}"
        )


def test_openrouter_can_disable_reasoning_by_env(monkeypatch):
    monkeypatch.setenv("LOLLA_OPENROUTER_DISABLE_REASONING", "1")
    client = OpenAICompatibleBoundaryClient(
        provider_name="openrouter",
        api_key="test-key",
        base_url="https://openrouter.ai/api/v1",
        model="moonshotai/kimi-k2.6",
    )

    assert client._reasoning_config() == {"enabled": False}


def test_gemini_uses_provider_off_switch_instead_of_unsupported_none_effort():
    client = OpenAICompatibleBoundaryClient(
        provider_name="openrouter",
        api_key="test-key",
        base_url="https://openrouter.ai/api/v1",
        model="google/gemini-3.1-flash-lite",
    )

    assert client._reasoning_config() == {"enabled": False}


def test_unexpected_boundary_exception_is_recorded_before_it_is_reraised(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = OpenAICompatibleBoundaryClient(
        provider_name="openrouter",
        api_key="test-key",
        base_url="https://openrouter.ai/api/v1",
        model="google/gemini-3.1-flash-lite",
    )

    def _raise(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("unexpected transport failure")

    monkeypatch.setattr(client, "_do_call", _raise)
    with pytest.raises(RuntimeError, match="unexpected transport failure"):
        client.run_json("system", "user", stage="extraction")

    assert len(client.call_log) == 1
    record = client.call_log[0]
    assert record.stage == "extraction"
    assert record.status == "unexpected_error"
    assert record.requested_model == "google/gemini-3.1-flash-lite"
    assert record.provider_name == "openrouter"
