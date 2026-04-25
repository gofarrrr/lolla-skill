"""Phase 7.2 extraction: Pass 1 triage runner helpers.

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
from .conversation_context import ConversationContext
from .prompts import (
    cluster_tendency_ids,
    format_pass1_cluster_prompts_from_context,
)
from .tendency_catalog import TendencyCatalog
from .triage import TriageScore, parse_pass1_scores

if TYPE_CHECKING:
    # Avoid circular import: the runtime only relies on duck-typed access to
    # BoundaryClient members, so this import is for type checking only.
    from .pipeline import BoundaryClient


def _run_pass1_cluster_single(
    cluster_id: str,
    system_prompt: str,
    user_prompt: str,
    boundary: "BoundaryClient",
    catalog: TendencyCatalog,
) -> tuple[list[TriageScore], BoundaryCallTrace]:
    """Run a single Pass 1 cluster triage call."""
    payload, metadata = boundary.run_json_with_metadata(system_prompt, user_prompt)
    trace = _metadata_to_boundary_call_trace(metadata, stage=f"pass1_cluster_{cluster_id}")
    # Parse all returned scores against the full catalog, then filter to this
    # cluster's assigned tendencies. Belt-and-suspenders: if the LLM returns a
    # score outside the family (despite the prompt's instructions), drop it
    # here so downstream code sees only this cluster's output.
    all_scores = parse_pass1_scores(payload, catalog)
    assigned = set(cluster_tendency_ids(cluster_id))
    filtered = [s for s in all_scores if s.tendency_id in assigned]
    return filtered, trace


def _run_pass1_clusters_parallel(
    *,
    conversation_context: ConversationContext,
    boundary: "BoundaryClient",
    catalog: TendencyCatalog,
) -> tuple[list[TriageScore], list[BoundaryCallTrace]]:
    """Run all Pass 1 cluster triage calls in parallel and merge their scores.

    Returns a single ``list[TriageScore]`` covering all clusters' assigned
    tendencies, plus one BoundaryCallTrace per cluster call. Unassigned
    tendencies (e.g., ``lollapalooza-tendency``, which is detected by the
    deterministic compound-group logic, not by triage) are absent from the
    returned scores — downstream code treats absence as score=0.

    Falls back to sequential execution if ``run_json_with_metadata`` is
    unavailable (e.g., test mocks).
    """
    cluster_prompts = format_pass1_cluster_prompts_from_context(
        context=conversation_context,
        catalog=catalog,
    )

    if not hasattr(boundary, "run_json_with_metadata") or not getattr(boundary, "supports_parallel_calls", False):
        # Fallback for test mocks or custom clients without the new method.
        merged_scores: list[TriageScore] = []
        traces: list[BoundaryCallTrace] = []
        for cluster_id, system_prompt, user_prompt in cluster_prompts:
            payload = boundary.run_json(system_prompt, user_prompt)
            traces.append(_capture_boundary_call(boundary, stage=f"pass1_cluster_{cluster_id}"))
            all_scores = parse_pass1_scores(payload, catalog)
            assigned = set(cluster_tendency_ids(cluster_id))
            merged_scores.extend(s for s in all_scores if s.tendency_id in assigned)
        return merged_scores, traces

    max_workers = min(len(cluster_prompts), 8)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(
                _run_pass1_cluster_single,
                cluster_id,
                system_prompt,
                user_prompt,
                boundary,
                catalog,
            )
            for cluster_id, system_prompt, user_prompt in cluster_prompts
        ]
    # Collect in submission order (preserves cluster ordering)
    merged_scores: list[TriageScore] = []
    boundary_traces: list[BoundaryCallTrace] = []
    for future in futures:
        scores, trace = future.result()
        merged_scores.extend(scores)
        boundary_traces.append(trace)
    return merged_scores, boundary_traces
