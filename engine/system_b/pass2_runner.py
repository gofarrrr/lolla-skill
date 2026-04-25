"""Phase 7.3 extraction: Pass 2 deep-check runner helpers.

Moved from ``pipeline.py`` to shrink the orchestration module while
preserving behavior and public import paths. Existing callers can still
import these helpers from ``engine.system_b.pipeline`` via re-export.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING

from .boundary_tracing import (
    BoundaryCallTrace,
    _capture_boundary_call,
    _metadata_to_boundary_call_trace,
)
from .deep_checks import (
    DeepCheckResult,
    format_pass2_prompt_from_packet,
    parse_pass2_result,
)
from .ir import ConversationIR
from .packet_builders.lane4 import build_lane4_packet
from .tendency_catalog import TendencyCatalog

if TYPE_CHECKING:
    # Avoid circular import: the runtime only relies on duck-typed access to
    # BoundaryClient / TriggeredTendency members, so these
    # imports are for type checking only.
    from .pipeline import BoundaryClient, TriggeredTendency


def _run_pass2_single(
    tendency_id: str,
    boundary: "BoundaryClient",
    catalog: TendencyCatalog,
    conversation_ir: ConversationIR,
) -> tuple[DeepCheckResult, BoundaryCallTrace]:
    """Run a single Pass 2 deep check. Thread-safe — uses run_json_with_metadata.

    Phase 6 contract: Pass 2 runs from the conversation IR only.
    """
    packet = build_lane4_packet(conversation_ir)
    pass2_system, pass2_user = format_pass2_prompt_from_packet(
        packet=packet,
        tendency_key=tendency_id,
        catalog=catalog,
    )
    payload, metadata = boundary.run_json_with_metadata(pass2_system, pass2_user)
    trace = _metadata_to_boundary_call_trace(metadata, stage="pass2", tendency_id=tendency_id)
    result = parse_pass2_result(
        payload,
        requested_tendency_key=tendency_id,
        catalog=catalog,
    )
    return result, trace


def _run_pass2_parallel(
    *,
    triggered_tendencies: tuple["TriggeredTendency", ...],
    boundary: "BoundaryClient",
    catalog: TendencyCatalog,
    conversation_ir: ConversationIR,
) -> tuple[list[DeepCheckResult], list[BoundaryCallTrace]]:
    """Run Pass 2 deep checks in parallel using thread pool.

    Results are returned in the same order as triggered_tendencies.
    Falls back to sequential execution if run_json_with_metadata is unavailable.
    Phase 6 contract: Pass 2 runs from the IR-driven packet path only.
    """
    if not triggered_tendencies:
        return [], []

    # Build the packet ONCE per pipeline run, then reuse across all parallel
    # Pass 2 calls (saves redundant projection work).
    packet = build_lane4_packet(conversation_ir)

    def _format_prompt_for(tendency_key: str) -> tuple[str, str]:
        return format_pass2_prompt_from_packet(
            packet=packet,
            tendency_key=tendency_key,
            catalog=catalog,
        )

    if not hasattr(boundary, "run_json_with_metadata") or not getattr(boundary, "supports_parallel_calls", False):
        # Fallback for test mocks or custom clients without the new method
        results: list[DeepCheckResult] = []
        traces: list[BoundaryCallTrace] = []
        for tt in triggered_tendencies:
            pass2_system, pass2_user = _format_prompt_for(tt.tendency_id)
            payload = boundary.run_json(pass2_system, pass2_user)
            traces.append(_capture_boundary_call(boundary, stage="pass2", tendency_id=tt.tendency_id))
            results.append(parse_pass2_result(payload, requested_tendency_key=tt.tendency_id, catalog=catalog))
        return results, traces

    max_workers = min(len(triggered_tendencies), 8)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(
                _run_pass2_single,
                tt.tendency_id,
                boundary,
                catalog,
                conversation_ir,
            )
            for tt in triggered_tendencies
        ]
    # Collect in submission order (preserves tendency ordering)
    deep_results: list[DeepCheckResult] = []
    boundary_traces: list[BoundaryCallTrace] = []
    for future in futures:
        result, trace = future.result()
        deep_results.append(result)
        boundary_traces.append(trace)
    return deep_results, boundary_traces
