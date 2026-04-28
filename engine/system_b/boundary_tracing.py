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
    model: str = ""
    status: str = "not_called"
    finish_reason: str = ""
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
        model=metadata.model,
        status=metadata.status,
        finish_reason=metadata.finish_reason,
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
        model=metadata.model,
        status=metadata.status,
        finish_reason=metadata.finish_reason,
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
    )
