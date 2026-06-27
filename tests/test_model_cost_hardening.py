from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.system_b.boundary_provider import (
    BoundaryCallRecord,
    DEFAULT_OPENROUTER_MODEL,
    OpenAICompatibleBoundaryClient,
    _build_call_metadata,
    _record_from_metadata,
)
from engine.system_b.usage_summary import build_usage_summary


def test_openrouter_default_uses_priced_low_cost_model(monkeypatch):
    monkeypatch.delenv("LOLLA_OPENROUTER_MODEL", raising=False)
    client = OpenAICompatibleBoundaryClient.openrouter_from_env()

    assert client.model == DEFAULT_OPENROUTER_MODEL
    assert client.model == "google/gemini-3.1-flash-lite"
    assert client._reasoning_config() == {"effort": "none"}


def test_boundary_metadata_records_requested_and_served_model_mismatch():
    metadata = _build_call_metadata(
        provider_name="openrouter",
        model="x-ai/grok-4.1-fast",
        payload={
            "model": "x-ai/grok-4.3",
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 20,
                "total_tokens": 120,
            },
            "choices": [{"finish_reason": "stop", "message": {"content": "{}"}}],
        },
        reasoning_config={"effort": "none"},
        status="ok",
    )

    assert metadata.requested_model == "x-ai/grok-4.1-fast"
    assert metadata.served_model == "x-ai/grok-4.3"
    assert metadata.model == "x-ai/grok-4.3"
    assert metadata.model_attribution_status == "mismatch"

    record = _record_from_metadata(metadata, stage="extraction", tendency_id="")
    assert record.requested_model == "x-ai/grok-4.1-fast"
    assert record.served_model == "x-ai/grok-4.3"
    assert record.model == "x-ai/grok-4.3"
    assert record.model_attribution_status == "mismatch"


def test_boundary_metadata_treats_provider_version_suffix_as_alias():
    metadata = _build_call_metadata(
        provider_name="openrouter",
        model="deepseek/deepseek-v4-flash",
        payload={
            "model": "deepseek/deepseek-v4-flash-20260423",
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 20,
                "total_tokens": 120,
            },
            "choices": [{"finish_reason": "stop", "message": {"content": "{}"}}],
        },
        reasoning_config={"effort": "none"},
        status="ok",
    )

    assert metadata.model == "deepseek/deepseek-v4-flash-20260423"
    assert metadata.model_attribution_status == "served_version_alias"


def test_boundary_metadata_ignores_gemini_signature_only_reasoning_details():
    metadata = _build_call_metadata(
        provider_name="openrouter",
        model="google/gemini-3.1-flash-lite",
        payload={
            "model": "google/gemini-3.1-flash-lite-20260507",
            "usage": {
                "prompt_tokens": 24,
                "completion_tokens": 18,
                "total_tokens": 42,
                "completion_tokens_details": {"reasoning_tokens": 0},
            },
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {
                        "content": "{}",
                        "reasoning": None,
                        "reasoning_details": [
                            {
                                "type": "reasoning.encrypted",
                                "format": "google-gemini-v1",
                                "index": 0,
                                "signature": "signed-provider-metadata",
                            }
                        ],
                    },
                }
            ],
        },
        reasoning_config={"effort": "none"},
        status="ok",
    )

    assert metadata.reasoning_disabled is True
    assert metadata.reasoning_tokens == 0
    assert metadata.reasoning_details_present is False


def test_boundary_metadata_flags_content_bearing_reasoning_details():
    metadata = _build_call_metadata(
        provider_name="openrouter",
        model="google/gemini-3.1-flash-lite",
        payload={
            "model": "google/gemini-3.1-flash-lite-20260507",
            "usage": {
                "prompt_tokens": 24,
                "completion_tokens": 18,
                "total_tokens": 42,
                "completion_tokens_details": {"reasoning_tokens": 0},
            },
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {
                        "content": "{}",
                        "reasoning_details": [
                            {
                                "type": "reasoning.summary",
                                "format": "google-gemini-v1",
                                "index": 0,
                                "summary": "private reasoning summary",
                            }
                        ],
                    },
                }
            ],
        },
        reasoning_config={"effort": "none"},
        status="ok",
    )

    assert metadata.reasoning_details_present is True


def test_usage_summary_prices_served_model_and_flags_attribution_mismatch():
    summary = build_usage_summary(
        run_id="run123",
        pipeline_boundary_calls=[
            BoundaryCallRecord(
                stage="extraction",
                provider_name="openrouter",
                requested_model="x-ai/grok-4.1-fast",
                served_model="x-ai/grok-4.3",
                model="x-ai/grok-4.3",
                model_attribution_status="mismatch",
                status="ok",
                prompt_tokens=1_000_000,
                completion_tokens=1_000_000,
                total_tokens=2_000_000,
            )
        ],
    )

    openrouter = summary["vendors"]["openrouter"]
    assert summary["cost_estimate_state"] == "complete"
    assert openrouter["estimated_cost_usd"] == 3.75
    assert openrouter["models_seen"] == ["x-ai/grok-4.3"]
    assert openrouter["requested_models_seen"] == ["x-ai/grok-4.1-fast"]
    assert openrouter["model_attribution"]["mismatch_count"] == 1
    assert openrouter["model_attribution"]["mismatches"][0]["served_model"] == "x-ai/grok-4.3"


def test_usage_summary_prices_version_alias_without_mismatch():
    summary = build_usage_summary(
        run_id="run123",
        pipeline_boundary_calls=[
            BoundaryCallRecord(
                stage="extraction",
                provider_name="openrouter",
                requested_model="deepseek/deepseek-v4-flash",
                served_model="deepseek/deepseek-v4-flash-20260423",
                model="deepseek/deepseek-v4-flash-20260423",
                model_attribution_status="served_version_alias",
                status="ok",
                prompt_tokens=1_000_000,
                completion_tokens=1_000_000,
                total_tokens=2_000_000,
            )
        ],
    )

    openrouter = summary["vendors"]["openrouter"]
    assert summary["cost_estimate_state"] == "complete"
    assert openrouter["estimated_cost_usd"] == 0.3
    assert openrouter["model_attribution"]["mismatch_count"] == 0
    assert openrouter["model_attribution"]["status_counts"]["served_version_alias"] == 1


def test_usage_summary_marks_unknown_cost_as_lower_bound():
    summary = build_usage_summary(
        run_id="run123",
        pipeline_boundary_calls=[
            BoundaryCallRecord(
                stage="extraction",
                provider_name="openrouter",
                requested_model="unknown/model",
                served_model="unknown/model",
                model="unknown/model",
                model_attribution_status="matched",
                status="ok",
                prompt_tokens=1000,
                completion_tokens=1000,
                total_tokens=2000,
            )
        ],
    )

    assert summary["estimated_total_cost_usd"] == 0.0
    assert summary["cost_estimate_state"] == "unknown"
    assert summary["cost_estimate_coverage"]["calls_with_unknown_price"] == 1
    assert summary["cost_estimate_coverage"]["unknown_price_models"] == ["unknown/model"]
