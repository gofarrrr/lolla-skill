"""Phase 7.5 extraction: audit trace dataclasses + assembly helpers.

Moved from ``pipeline.py`` to shrink the orchestration module while
preserving behavior and public import paths. Existing callers can still
import ``AuditTrace`` from ``engine.system_b.pipeline`` via re-export.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .boundary_tracing import BoundaryCallTrace
from .deep_checks import DeepCheckResult
from .frame_pressure import FramePressureCard
from .pressure_bundle_selector import SelectedChunkRecord
from .routing import TendencyRoute
from .structural_coverage import StructuralCoverageCard
from .triage import TriageScore

if TYPE_CHECKING:
    # Avoid circular import: TriggeredTendency is defined in pipeline.py and
    # remains importable from there for existing callers.
    from .pipeline import TriggeredTendency


@dataclass(frozen=True)
class PromotedBundleTrace:
    tendency_id: str
    sub_pattern: str
    primary_model_id: str
    primary_activation_context: str = ""
    activation_context_source_path: str = ""
    activation_context_source_quote: str = ""
    activation_context_extraction_type: str = ""
    activation_context_confidence: str = ""
    activation_context_blocking_quality_flags: tuple[str, ...] = ()
    activation_context_advisory_quality_flags: tuple[str, ...] = ()
    selected_chunks: tuple[SelectedChunkRecord, ...] = ()
    guardrail_tags: tuple[str, ...] = ()
    provenance_complete: bool = False
    provenance_gaps: tuple[str, ...] = ()
    blocking_quality_flags: tuple[str, ...] = ()
    advisory_quality_flags: tuple[str, ...] = ()


@dataclass(frozen=True)
class AuditTrace:
    triage_scores: tuple[TriageScore, ...] = ()
    triggered_tendencies: tuple["TriggeredTendency", ...] = ()
    deep_check_results: tuple[DeepCheckResult, ...] = ()
    routing_decisions: tuple[TendencyRoute, ...] = ()
    boundary_calls: tuple[BoundaryCallTrace, ...] = ()
    promoted_bundle_traces: tuple[PromotedBundleTrace, ...] = ()
    warnings: tuple[str, ...] = ()
    companion_fingerprint_raw: list[dict[str, object]] = field(default_factory=list)
    companion_fingerprint_validated: list[dict[str, object]] = field(default_factory=list)
    companion_fingerprint_dropped: list[dict[str, object]] = field(default_factory=list)
    companion_detected_models: list[dict[str, str]] = field(default_factory=list)
    companion_rejected_models: list[dict[str, str]] = field(default_factory=list)
    # Lane 2 attribution (research/lane2-attribution-design-2026-04-26.md):
    # `companion_candidates` mirrors the recall input to the verifier with
    # per-source rank metadata. `companion_verification_accepted_before_cap`
    # is the full accepted set before the top-5 surfacing budget is applied;
    # `companion_verification_capped_models` is the accepted-but-not-surfaced
    # subset (drop_reason="capped_at_top_5"). Capped is NOT rejected; they
    # are persisted separately so verification_precision stays meaningful.
    companion_candidates: list[dict[str, object]] = field(default_factory=list)
    companion_verification_accepted_before_cap: list[dict[str, str]] = field(default_factory=list)
    companion_verification_capped_models: list[dict[str, str]] = field(default_factory=list)
    # Verifier-side dedupe of accepted entries by model_id. Drop reason
    # "duplicate_accept_dedupe". NOT semantically rejected (verification_precision
    # depends on rejected meaning rejected). Lives separately so we can quantify
    # how often the verifier double-accepts and detect regressions.
    companion_verification_duplicate_accepts: list[dict[str, str]] = field(default_factory=list)
    # Verifier accepted entries whose evidence quote was repaired to a literal
    # assistant-source substring before acceptance. Not rejected; measured
    # separately so the quote-validation gate remains auditable.
    companion_verification_quote_repairs: list[dict[str, str]] = field(default_factory=list)
    companion_candidate_cap: int = 0
    # Embedding mode in effect for this run: "on" | "off". Recorded so
    # downstream stability/attribution reports can group by mode without
    # having to inspect environment variables after the fact.
    embedding_mode: str = ""
    # Pass 1 swiss-cheese embedding signal: full top-25 ranked tendencies
    # with `promoted: bool` flag. Promoted rows (≥ 0.30) drove Pass 2; the
    # sub-threshold rows are the close-call telemetry — useful to spot
    # "tendency X scored 0.28, almost made it" patterns. Empty list when
    # embeddings are off.
    embedding_tendency_ranks: list[dict[str, object]] = field(default_factory=list)
    # Frame Pressure lane (Lane 3) — additive metadata, absent when lane is off
    frame_extraction_element_count: int = 0
    frame_extraction_pattern_ids: tuple[str, ...] = ()
    frame_extraction_fired: bool = False
    # Structural Coverage lane (Lane 4) — additive metadata, absent when lane is off
    structural_coverage_question_type: str = ""
    structural_coverage_dimension_count: int = 0
    structural_coverage_gap_count: int = 0
    structural_coverage_gap_question_count: int = 0
    structural_coverage_fired: bool = False


def build_empty_audit_trace(
    *,
    triage_scores: tuple[TriageScore, ...] | list[TriageScore],
    boundary_calls: tuple[BoundaryCallTrace, ...] | list[BoundaryCallTrace],
    warnings: tuple[str, ...] | list[str],
    companion_fingerprint_raw: list[dict[str, object]],
    companion_fingerprint_validated: list[dict[str, object]],
    companion_fingerprint_dropped: list[dict[str, object]],
    companion_detected_models: list[dict[str, str]],
    companion_rejected_models: list[dict[str, str]],
    frame_card: FramePressureCard | None,
    structural_card: StructuralCoverageCard | None,
    companion_candidates: list[dict[str, object]] | None = None,
    companion_verification_accepted_before_cap: list[dict[str, str]] | None = None,
    companion_verification_capped_models: list[dict[str, str]] | None = None,
    companion_verification_duplicate_accepts: list[dict[str, str]] | None = None,
    companion_verification_quote_repairs: list[dict[str, str]] | None = None,
    companion_candidate_cap: int = 0,
    embedding_mode: str = "",
    embedding_tendency_ranks: list[dict[str, object]] | None = None,
) -> AuditTrace:
    return AuditTrace(
        triage_scores=tuple(triage_scores),
        triggered_tendencies=(),
        deep_check_results=(),
        routing_decisions=(),
        boundary_calls=tuple(boundary_calls),
        warnings=tuple(warnings),
        companion_fingerprint_raw=companion_fingerprint_raw,
        companion_fingerprint_validated=companion_fingerprint_validated,
        companion_fingerprint_dropped=companion_fingerprint_dropped,
        companion_detected_models=companion_detected_models,
        companion_rejected_models=companion_rejected_models,
        companion_candidates=list(companion_candidates or []),
        companion_verification_accepted_before_cap=list(companion_verification_accepted_before_cap or []),
        companion_verification_capped_models=list(companion_verification_capped_models or []),
        companion_verification_duplicate_accepts=list(companion_verification_duplicate_accepts or []),
        companion_verification_quote_repairs=list(companion_verification_quote_repairs or []),
        companion_candidate_cap=companion_candidate_cap,
        embedding_mode=embedding_mode,
        embedding_tendency_ranks=list(embedding_tendency_ranks or []),
        **_frame_audit_fields(frame_card),
        **_structural_coverage_audit_fields(structural_card),
    )


def build_pipeline_audit_trace(
    *,
    triage_scores: tuple[TriageScore, ...] | list[TriageScore],
    triggered_tendencies: tuple["TriggeredTendency", ...],
    deep_check_results: tuple[DeepCheckResult, ...] | list[DeepCheckResult],
    routing_decisions: tuple[TendencyRoute, ...],
    boundary_calls: tuple[BoundaryCallTrace, ...] | list[BoundaryCallTrace],
    warnings: tuple[str, ...] | list[str],
    companion_fingerprint_raw: list[dict[str, object]],
    companion_fingerprint_validated: list[dict[str, object]],
    companion_fingerprint_dropped: list[dict[str, object]],
    companion_detected_models: list[dict[str, str]],
    companion_rejected_models: list[dict[str, str]],
    frame_card: FramePressureCard | None,
    structural_card: StructuralCoverageCard | None,
    promoted_overoptimism_results: dict[str, object],
    promoted_authority_results: dict[str, object],
    promoted_stress_results: dict[str, object],
    companion_candidates: list[dict[str, object]] | None = None,
    companion_verification_accepted_before_cap: list[dict[str, str]] | None = None,
    companion_verification_capped_models: list[dict[str, str]] | None = None,
    companion_verification_duplicate_accepts: list[dict[str, str]] | None = None,
    companion_verification_quote_repairs: list[dict[str, str]] | None = None,
    companion_candidate_cap: int = 0,
    embedding_mode: str = "",
    embedding_tendency_ranks: list[dict[str, object]] | None = None,
) -> AuditTrace:
    return AuditTrace(
        triage_scores=tuple(triage_scores),
        triggered_tendencies=triggered_tendencies,
        deep_check_results=tuple(deep_check_results),
        routing_decisions=routing_decisions,
        boundary_calls=tuple(boundary_calls),
        promoted_bundle_traces=_build_promoted_bundle_traces(
            promoted_overoptimism_results,
            promoted_authority_results,
            promoted_stress_results,
        ),
        warnings=tuple(warnings),
        companion_fingerprint_raw=companion_fingerprint_raw,
        companion_fingerprint_validated=companion_fingerprint_validated,
        companion_fingerprint_dropped=companion_fingerprint_dropped,
        companion_detected_models=companion_detected_models,
        companion_rejected_models=companion_rejected_models,
        companion_candidates=list(companion_candidates or []),
        companion_verification_accepted_before_cap=list(companion_verification_accepted_before_cap or []),
        companion_verification_capped_models=list(companion_verification_capped_models or []),
        companion_verification_duplicate_accepts=list(companion_verification_duplicate_accepts or []),
        companion_verification_quote_repairs=list(companion_verification_quote_repairs or []),
        companion_candidate_cap=companion_candidate_cap,
        embedding_mode=embedding_mode,
        embedding_tendency_ranks=list(embedding_tendency_ranks or []),
        **_frame_audit_fields(frame_card),
        **_structural_coverage_audit_fields(structural_card),
    )


def _frame_audit_fields(card: FramePressureCard | None) -> dict[str, object]:
    """Return AuditTrace field overrides for the Frame Pressure lane."""
    if card is None:
        return {}
    return {
        "frame_extraction_element_count": len(card.frame_elements),
        "frame_extraction_pattern_ids": tuple(
            el.frame_pattern for el in card.frame_elements
        ),
        "frame_extraction_fired": len(card.frame_elements) > 0,
    }


def _structural_coverage_audit_fields(card: StructuralCoverageCard | None) -> dict[str, object]:
    """Return AuditTrace field overrides for the Structural Coverage lane."""
    if card is None:
        return {}
    gap_count = sum(1 for d in card.dimensions if not d.covered)
    return {
        "structural_coverage_question_type": card.question_type,
        "structural_coverage_dimension_count": len(card.dimensions),
        "structural_coverage_gap_count": gap_count,
        "structural_coverage_gap_question_count": len(card.gap_questions),
        "structural_coverage_fired": len(card.dimensions) > 0,
    }


def _build_promoted_bundle_traces(
    *promoted_result_groups: dict[str, object],
) -> tuple[PromotedBundleTrace, ...]:
    traces: list[PromotedBundleTrace] = []
    for promoted_results in promoted_result_groups:
        for tendency_id, promoted_result in promoted_results.items():
            pilot_result = getattr(promoted_result, "pilot_result", None)
            if pilot_result is None:
                continue
            selected_chunks = pilot_result.bundle.selected_chunks
            provenance_gaps = _provenance_gaps(selected_chunks)
            traces.append(
                PromotedBundleTrace(
                    tendency_id=tendency_id,
                    sub_pattern=pilot_result.bundle.route.subpattern_id,
                    primary_model_id=pilot_result.bundle.route.primary_model_id,
                    primary_activation_context=pilot_result.bundle.route.primary_activation_context,
                    activation_context_source_path=(
                        pilot_result.bundle.route.primary_activation_context_ref.path
                        if pilot_result.bundle.route.primary_activation_context_ref is not None
                        else ""
                    ),
                    activation_context_source_quote=(
                        pilot_result.bundle.route.primary_activation_context_ref.quote
                        if pilot_result.bundle.route.primary_activation_context_ref is not None
                        else ""
                    ),
                    activation_context_extraction_type=(
                        pilot_result.bundle.route.primary_activation_context_ref.extraction_type
                        if pilot_result.bundle.route.primary_activation_context_ref is not None
                        else ""
                    ),
                    activation_context_confidence=(
                        pilot_result.bundle.route.primary_activation_context_ref.confidence
                        if pilot_result.bundle.route.primary_activation_context_ref is not None
                        else ""
                    ),
                    activation_context_blocking_quality_flags=pilot_result.bundle.route.primary_activation_context_blocking_quality_flags,
                    activation_context_advisory_quality_flags=pilot_result.bundle.route.primary_activation_context_advisory_quality_flags,
                    selected_chunks=selected_chunks,
                    guardrail_tags=_collect_guardrail_tags(selected_chunks),
                    provenance_complete=not provenance_gaps,
                    provenance_gaps=provenance_gaps,
                    blocking_quality_flags=_collect_quality_flags(selected_chunks, "blocking_quality_flags"),
                    advisory_quality_flags=_collect_quality_flags(selected_chunks, "advisory_quality_flags"),
                )
            )
    return tuple(traces)


def _provenance_gaps(selected_chunks: tuple[SelectedChunkRecord, ...]) -> tuple[str, ...]:
    gaps: list[str] = []
    for chunk in selected_chunks:
        if not chunk.source_file:
            gaps.append(f"{chunk.chunk_id}:missing-source-file")
        if not chunk.source_quote:
            gaps.append(f"{chunk.chunk_id}:missing-source-quote")
        if not chunk.extraction_type:
            gaps.append(f"{chunk.chunk_id}:missing-extraction-type")
        if not chunk.confidence:
            gaps.append(f"{chunk.chunk_id}:missing-confidence")
    return tuple(gaps)


def _collect_guardrail_tags(selected_chunks: tuple[SelectedChunkRecord, ...]) -> tuple[str, ...]:
    tags: list[str] = []
    seen: set[str] = set()
    for chunk in selected_chunks:
        for tag in chunk.guardrail_tags:
            if not tag or tag in seen:
                continue
            seen.add(tag)
            tags.append(tag)
    return tuple(tags)


def _collect_quality_flags(
    selected_chunks: tuple[SelectedChunkRecord, ...],
    field_name: str,
) -> tuple[str, ...]:
    flags: list[str] = []
    seen: set[str] = set()
    for chunk in selected_chunks:
        lane = chunk.lane or chunk.chunk_id
        for flag in getattr(chunk, field_name, ()) or ():
            qualified = f"{lane}:{flag}"
            if qualified in seen:
                continue
            seen.add(qualified)
            flags.append(qualified)
    return tuple(flags)
