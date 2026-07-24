"""Phase 7.1 extraction: per-call boundary trace dataclass + helpers.

Moved from `pipeline.py` to reduce that module's size. Public API and
behavior unchanged. Importable from `engine.system_b.pipeline` (via
re-export) for backwards compatibility with existing callers including
`engine/system_b/testing_harness.py`.

The trace records per-LLM-call telemetry (model, tokens, status,
reasoning metadata) for later aggregation by
`testing_harness.summarize_boundary_calls`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .boundary_provider import BoundaryCallMetadata

if TYPE_CHECKING:
    # Avoid circular import: BoundaryClient Protocol is defined in pipeline.py
    # because lane code also uses it. The trace helper only does duck-typed
    # `getattr(boundary, "last_call_metadata", ...)`, so we don't need the
    # Protocol at runtime.
    from .pipeline import BoundaryClient


@dataclass(frozen=True)
class BoundaryCallTrace:
    stage: str
    tendency_id: str = ""
    provider_name: str = ""
    served_provider_name: str = ""
    requested_model: str = ""
    served_model: str = ""
    model: str = ""
    model_attribution_status: str = "not_observed"
    status: str = "not_called"
    finish_reason: str = ""
    provider_error_source: str = ""
    provider_error_type: str = ""
    provider_error_code: str = ""
    provider_error_provider_code: str = ""
    provider_error_message_sha256: str = ""
    retry_after_seconds: float | None = None
    raw_message_content: str = ""
    temperature: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cached_tokens: int = 0
    cache_write_tokens: int = 0
    reasoning_tokens: int = 0
    reasoning_disabled: bool = False
    reasoning_details_present: bool = False
    provider_attempted: bool = False
    response_id: str = ""
    exact_cost_usd: float | None = None
    request_max_output_tokens: int = 0
    request_max_price_prompt: float = 0.0
    request_max_price_completion: float = 0.0
    request_provider_order: tuple[str, ...] = ()
    request_allow_fallbacks: bool = False
    request_require_parameters: bool = False
    request_data_collection: str = ""
    request_zdr: bool = False
    run_max_provider_calls: int = 0
    run_max_cost_usd: float = 0.0
    maximum_call_cost_usd: float = 0.0
    budget_reservation_id: str = ""
    pricing_table_version: str = ""
    pricing_table_stale: bool = False


def _capture_boundary_call(
    boundary: "BoundaryClient",
    *,
    stage: str,
    tendency_id: str = "",
) -> BoundaryCallTrace:
    metadata = getattr(boundary, "last_call_metadata", BoundaryCallMetadata())
    return BoundaryCallTrace(
        stage=stage,
        tendency_id=tendency_id,
        provider_name=metadata.provider_name,
        served_provider_name=metadata.served_provider_name,
        requested_model=metadata.requested_model,
        served_model=metadata.served_model,
        model=metadata.model,
        model_attribution_status=metadata.model_attribution_status,
        status=metadata.status,
        finish_reason=metadata.finish_reason,
        provider_error_source=metadata.provider_error_source,
        provider_error_type=metadata.provider_error_type,
        provider_error_code=metadata.provider_error_code,
        provider_error_provider_code=metadata.provider_error_provider_code,
        provider_error_message_sha256=metadata.provider_error_message_sha256,
        retry_after_seconds=metadata.retry_after_seconds,
        raw_message_content=metadata.raw_message_content,
        temperature=metadata.temperature,
        prompt_tokens=metadata.prompt_tokens,
        completion_tokens=metadata.completion_tokens,
        total_tokens=metadata.total_tokens,
        cached_tokens=metadata.cached_tokens,
        cache_write_tokens=metadata.cache_write_tokens,
        reasoning_tokens=metadata.reasoning_tokens,
        reasoning_disabled=metadata.reasoning_disabled,
        reasoning_details_present=metadata.reasoning_details_present,
        provider_attempted=metadata.provider_attempted,
        response_id=metadata.response_id,
        exact_cost_usd=metadata.exact_cost_usd,
        request_max_output_tokens=metadata.request_max_output_tokens,
        request_max_price_prompt=metadata.request_max_price_prompt,
        request_max_price_completion=metadata.request_max_price_completion,
        request_provider_order=metadata.request_provider_order,
        request_allow_fallbacks=metadata.request_allow_fallbacks,
        request_require_parameters=metadata.request_require_parameters,
        request_data_collection=metadata.request_data_collection,
        request_zdr=metadata.request_zdr,
        run_max_provider_calls=metadata.run_max_provider_calls,
        run_max_cost_usd=metadata.run_max_cost_usd,
        maximum_call_cost_usd=metadata.maximum_call_cost_usd,
        budget_reservation_id=metadata.budget_reservation_id,
        pricing_table_version=metadata.pricing_table_version,
        pricing_table_stale=metadata.pricing_table_stale,
    )


def _metadata_to_boundary_call_trace(
    metadata: BoundaryCallMetadata,
    *,
    stage: str,
    tendency_id: str = "",
) -> BoundaryCallTrace:
    return BoundaryCallTrace(
        stage=stage,
        tendency_id=tendency_id,
        provider_name=metadata.provider_name,
        served_provider_name=metadata.served_provider_name,
        requested_model=metadata.requested_model,
        served_model=metadata.served_model,
        model=metadata.model,
        model_attribution_status=metadata.model_attribution_status,
        status=metadata.status,
        finish_reason=metadata.finish_reason,
        provider_error_source=metadata.provider_error_source,
        provider_error_type=metadata.provider_error_type,
        provider_error_code=metadata.provider_error_code,
        provider_error_provider_code=metadata.provider_error_provider_code,
        provider_error_message_sha256=metadata.provider_error_message_sha256,
        retry_after_seconds=metadata.retry_after_seconds,
        raw_message_content=metadata.raw_message_content,
        temperature=metadata.temperature,
        prompt_tokens=metadata.prompt_tokens,
        completion_tokens=metadata.completion_tokens,
        total_tokens=metadata.total_tokens,
        cached_tokens=metadata.cached_tokens,
        cache_write_tokens=metadata.cache_write_tokens,
        reasoning_tokens=metadata.reasoning_tokens,
        reasoning_disabled=metadata.reasoning_disabled,
        reasoning_details_present=metadata.reasoning_details_present,
        provider_attempted=metadata.provider_attempted,
        response_id=metadata.response_id,
        exact_cost_usd=metadata.exact_cost_usd,
        request_max_output_tokens=metadata.request_max_output_tokens,
        request_max_price_prompt=metadata.request_max_price_prompt,
        request_max_price_completion=metadata.request_max_price_completion,
        request_provider_order=metadata.request_provider_order,
        request_allow_fallbacks=metadata.request_allow_fallbacks,
        request_require_parameters=metadata.request_require_parameters,
        request_data_collection=metadata.request_data_collection,
        request_zdr=metadata.request_zdr,
        run_max_provider_calls=metadata.run_max_provider_calls,
        run_max_cost_usd=metadata.run_max_cost_usd,
        maximum_call_cost_usd=metadata.maximum_call_cost_usd,
        budget_reservation_id=metadata.budget_reservation_id,
        pricing_table_version=metadata.pricing_table_version,
        pricing_table_stale=metadata.pricing_table_stale,
    )
