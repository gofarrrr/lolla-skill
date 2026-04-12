from __future__ import annotations

from dataclasses import dataclass, field
import json
import logging
import os
from pathlib import Path
import time
from typing import Callable, Protocol

_LOGGER = logging.getLogger("system_b.pipeline")

from .authority_pilot_bridge import AuthorityPilotBridge, AuthorityPilotBridgeResult
from concurrent.futures import ThreadPoolExecutor

from .boundary_provider import BoundaryCallMetadata, load_boundary_client_from_env
from .companion import CompanionCard, DetectedModel, FingerprintMove, FingerprintPayload, build_companion_card
from .frame_pressure import (
    FramePressureCard,
    assemble_frame_card,
    compute_pressure_concept_overlap,
    generate_reframings,
    route_frame_elements,
    run_frame_extraction,
)
from .structural_coverage import StructuralCoverageCard, run_structural_coverage
from .companion_routing import recall_candidates, run_fingerprint_call, run_verification_call
from .companion_selection import CompanionCheatSheet, select_companion_cheat_sheet
from .compound_catalog import COMPOUND_CATALOG
from .contrast_misreaction_deep_check_packet_adapter import (
    map_contrast_misreaction_result_to_subpattern,
)
from .deprival_superreaction_deep_check_packet_adapter import (
    map_deprival_superreaction_result_to_subpattern,
)
from .disliking_hating_deep_check_packet_adapter import (
    map_disliking_hating_result_to_subpattern,
)
from .excessive_self_regard_deep_check_packet_adapter import (
    map_excessive_self_regard_result_to_subpattern,
)
from .envy_jealousy_deep_check_packet_adapter import (
    map_envy_jealousy_result_to_subpattern,
)
from .deep_checks import DeepCheckResult, format_pass2_prompt, parse_pass2_result
from .authority_phase1_builder import AuthorityPhase1Builder
from .authority_deep_check_packet_adapter import (
    map_authority_result_to_subpattern,
)
from .inconsistency_avoidance_deep_check_packet_adapter import (
    map_inconsistency_avoidance_result_to_subpattern,
)
from .influence_from_mere_association_deep_check_packet_adapter import (
    map_influence_from_mere_association_result_to_subpattern,
)
from .kantian_fairness_deep_check_packet_adapter import (
    map_kantian_fairness_result_to_subpattern,
)
from .liking_loving_deep_check_packet_adapter import (
    map_liking_loving_result_to_subpattern,
)
from .reciprocation_deep_check_packet_adapter import (
    map_reciprocation_result_to_subpattern,
)
from .pilot_deep_check_bridge import PilotDeepCheckBridge, PilotDeepCheckBridgeResult
from .pressure_bundle_selector import PressureBundleSelector
from .pressure_bundle_selector import SelectedChunkRecord
from .prompts import format_pass1_prompt
from .relation_graph import RelationGraph
from .reward_and_punishment_deep_check_packet_adapter import (
    map_reward_and_punishment_result_to_subpattern,
)
from .routing import TendencyRoute, route_deep_check_results
from .stress_phase1_builder import StressPhase1Builder
from .stress_pilot_bridge import StressPilotBridge, StressPilotBridgeResult
from .simple_pain_denial_deep_check_packet_adapter import (
    map_simple_pain_denial_result_to_subpattern,
)
from .curiosity_deep_check_packet_adapter import (
    map_curiosity_result_to_subpattern,
)
from .twaddle_deep_check_packet_adapter import (
    map_twaddle_result_to_subpattern,
)
from .use_it_or_lose_it_deep_check_packet_adapter import (
    map_use_it_or_lose_it_result_to_subpattern,
)
from .lollapalooza_deep_check_packet_adapter import (
    map_lollapalooza_result_to_subpattern,
)
from .doubt_avoidance_deep_check_packet_adapter import (
    map_doubt_avoidance_result_to_subpattern,
)
from .stress_deep_check_packet_adapter import (
    map_stress_result_to_subpattern,
)
from .social_proof_deep_check_packet_adapter import (
    map_social_proof_result_to_subpattern,
)
from .reason_respecting_deep_check_packet_adapter import (
    map_reason_respecting_result_to_subpattern,
)
from .tendency_catalog import TendencyCatalog
from .triage import TriageScore, parse_pass1_scores


class BoundaryClient(Protocol):
    def run_json(self, system_prompt: str, user_prompt: str) -> dict:
        ...

    def run_json_with_metadata(
        self, system_prompt: str, user_prompt: str
    ) -> tuple[dict, BoundaryCallMetadata]:
        ...


@dataclass(frozen=True)
class CritiqueRequest:
    query: str
    vanilla_answer: str


@dataclass(frozen=True)
class PipelineConfig:
    triage_threshold: int = 4
    max_supporting_models: int = 2
    max_risk_models: int = 1
    always_deep_check_tendencies: tuple[str, ...] = ()
    overoptimism_phase1_active: bool = False
    authority_phase1_active: bool = False
    stress_phase1_active: bool = False
    enable_companion: bool = False
    enable_frame_pressure: bool = False
    enable_structural_coverage: bool = False
    enable_embeddings: bool = True
    enable_deep_checks: bool = True
    enable_telemetry: bool = False
    telemetry_db_path: str = ""
    telemetry_tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class BoundaryCallTrace:
    stage: str
    tendency_id: str = ""
    provider_name: str = ""
    model: str = ""
    status: str = "not_called"
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cached_tokens: int = 0
    cache_write_tokens: int = 0
    reasoning_tokens: int = 0
    reasoning_disabled: bool = False
    reasoning_details_present: bool = False


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
    triggered_tendencies: tuple[str, ...] = ()
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


@dataclass(frozen=True)
class DeltaFinding:
    tendency_id: str
    tendency_name: str
    sub_pattern: str = ""
    severity: str = ""
    specific_passage: str = ""
    primary_model_id: str = ""
    intervention_hint: str = ""
    supporting_model_ids: tuple[str, ...] = ()
    risk_model_ids: tuple[str, ...] = ()
    selected_model_ids: tuple[str, ...] = ()
    major_tensions: tuple[str, ...] = ()
    challenge_statement: str = ""
    next_move: str = ""
    is_trusted_surface: bool = False


@dataclass(frozen=True)
class CompoundGroup:
    compound_id: str
    label: str
    description: str
    member_tendency_ids: tuple[str, ...] = ()
    findings: tuple[DeltaFinding, ...] = ()
    tier: str = ""


@dataclass(frozen=True)
class DeltaCard:
    findings: tuple[DeltaFinding, ...] = ()
    top_findings: tuple[DeltaFinding, ...] = ()
    secondary_findings: tuple[DeltaFinding, ...] = ()
    presented_secondary_findings: tuple[DeltaFinding, ...] = ()
    compound_groups: tuple[CompoundGroup, ...] = ()
    top_compound_groups: tuple[CompoundGroup, ...] = ()
    secondary_compound_groups: tuple[CompoundGroup, ...] = ()
    secondary_summarization_active: bool = False
    secondary_additional_pressures_note: str = ""
    secondary_additional_pressure_count: int = 0
    secondary_additional_pressure_tendency_ids: tuple[str, ...] = ()
    detected_tendencies: tuple[str, ...] = ()
    selected_model_ids: tuple[str, ...] = ()
    challenge_statements: tuple[str, ...] = ()
    next_moves: tuple[str, ...] = ()
    major_tensions: tuple[str, ...] = ()
    top_challenge_statements: tuple[str, ...] = ()
    secondary_challenge_statements: tuple[str, ...] = ()
    top_next_moves: tuple[str, ...] = ()
    secondary_next_moves: tuple[str, ...] = ()


@dataclass(frozen=True)
class PipelineResult:
    detected_tendencies: tuple[str, ...]
    routes: tuple[TendencyRoute, ...]
    delta_card: DeltaCard
    audit: AuditTrace
    companion_card: CompanionCard | None = None
    companion_cheat_sheet: CompanionCheatSheet | None = None
    frame_pressure_card: FramePressureCard | None = None
    structural_coverage_card: StructuralCoverageCard | None = None
    prompt_versions: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class CompanionRunResult:
    companion_card: CompanionCard | None = None
    fingerprint_payload: FingerprintPayload = field(
        default_factory=lambda: FingerprintPayload(raw=[], validated=[], dropped=[])
    )
    detected_models: list[DetectedModel] = field(default_factory=list)
    rejected_models: list[dict[str, str]] = field(default_factory=list)
    candidates: list[dict[str, object]] = field(default_factory=list)


class SystemBPipeline:
    def __init__(
        self,
        catalog: TendencyCatalog,
        relation_graph: RelationGraph,
        boundary: BoundaryClient,
        bundle_selector: PressureBundleSelector | None = None,
        companion_knowledge_graph: dict | None = None,
        companion_relation_graph: dict | list | None = None,
        companion_reasoning_signals: dict | None = None,
        overoptimism_bridge: PilotDeepCheckBridge | None = None,
        authority_bridge: AuthorityPilotBridge | None = None,
        stress_bridge: StressPilotBridge | None = None,
        embedding_retriever=None,
        telemetry_store=None,
        startup_warnings: tuple[str, ...] = (),
        config: PipelineConfig | None = None,
    ) -> None:
        self._catalog = catalog
        self._relation_graph = relation_graph
        self._boundary = boundary
        self._bundle_selector = bundle_selector
        self._companion_knowledge_graph = companion_knowledge_graph or {}
        self._companion_relation_graph = companion_relation_graph or {}
        self._companion_reasoning_signals = companion_reasoning_signals or {}
        self._overoptimism_bridge = overoptimism_bridge
        self._authority_bridge = authority_bridge
        self._stress_bridge = stress_bridge
        self._embedding_retriever = embedding_retriever
        self._telemetry_store = telemetry_store
        self._embedding_api_key = os.environ.get("OPENAI_API_KEY", "")
        self._startup_warnings = startup_warnings
        self._config = config or PipelineConfig()
        # Compute prompt version hashes once at init
        from .prompt_versioning import compute_prompt_versions
        self._prompt_versions = tuple(sorted(compute_prompt_versions().items()))

    @classmethod
    def load(
        cls,
        root: Path,
        boundary: BoundaryClient,
        config: PipelineConfig | None = None,
    ) -> "SystemBPipeline":
        active_config = config or PipelineConfig()
        overoptimism_bridge, overoptimism_warnings = _load_overoptimism_bridge(root, active_config)
        authority_bridge, authority_warnings = _load_authority_bridge(root, active_config)
        stress_bridge, stress_warnings = _load_stress_bridge(root, active_config)
        return cls(
            catalog=TendencyCatalog.load(root),
            relation_graph=RelationGraph.load(root),
            boundary=boundary,
            bundle_selector=_load_bundle_selector(root),
            companion_knowledge_graph=_load_companion_knowledge_graph(root),
            companion_relation_graph=_load_companion_relation_graph(root),
            companion_reasoning_signals=_load_companion_reasoning_signals(root),
            overoptimism_bridge=overoptimism_bridge,
            authority_bridge=authority_bridge,
            stress_bridge=stress_bridge,
            embedding_retriever=_load_embedding_retriever(root),
            telemetry_store=_load_telemetry_store(root, active_config),
            startup_warnings=tuple((*overoptimism_warnings, *authority_warnings, *stress_warnings)),
            config=active_config,
        )

    @classmethod
    def load_live(
        cls,
        root: Path,
        *,
        provider_name: str = "openrouter",
        config: PipelineConfig | None = None,
    ) -> "SystemBPipeline":
        return cls.load(
            root=root,
            boundary=load_boundary_client_from_env(provider_name),
            config=config,
        )

    def run(self, request: CritiqueRequest) -> PipelineResult:
        run_started = time.monotonic()
        boundary_calls: list[BoundaryCallTrace] = []
        pass1_started = time.monotonic()
        pass1_system, pass1_user = format_pass1_prompt(
            query=request.query,
            vanilla_answer=request.vanilla_answer,
            catalog=self._catalog,
        )
        triage_payload = self._boundary.run_json(pass1_system, pass1_user)
        boundary_calls.append(_capture_boundary_call(self._boundary, stage="pass1"))
        triage_scores = parse_pass1_scores(triage_payload, self._catalog)
        pass1_seconds = time.monotonic() - pass1_started
        embedding_tendency_hits = _embedding_tendency_signal(
            vanilla_answer=request.vanilla_answer,
            retriever=self._embedding_retriever if self._config.enable_embeddings else None,
            api_key=self._embedding_api_key,
        )
        triggered_tendencies = _select_triggered_tendencies(
            triage_scores,
            triage_threshold=self._config.triage_threshold,
            always_include=self._config.always_deep_check_tendencies,
            catalog=self._catalog,
            embedding_tendency_hits=embedding_tendency_hits,
        )

        lane1_relevance = self._build_lane1_relevance_scores(
            f"{request.query} {request.vanilla_answer}"
        )

        if not triggered_tendencies:
            companion_started = time.monotonic()
            companion_result = self._run_companion(request, boundary_calls)
            companion_seconds = time.monotonic() - companion_started
            frame_card = self._run_frame_pressure(
                request, boundary_calls,
                lane1_tendency_ids=set(),
                lane1_model_ids=set(),
            )
            _lane2_model_ids = _extract_companion_model_ids(companion_result)
            _lane3_model_ids = _extract_frame_model_ids(frame_card)
            structural_card = self._run_structural_coverage(
                request, boundary_calls,
                lane1_model_ids=set(),
                lane2_model_ids=_lane2_model_ids,
                lane3_model_ids=_lane3_model_ids,
            )
            audit = AuditTrace(
                triage_scores=tuple(triage_scores),
                triggered_tendencies=(),
                deep_check_results=(),
                routing_decisions=(),
                boundary_calls=tuple(boundary_calls),
                warnings=self._catalog.warnings,
                companion_fingerprint_raw=_serialize_fingerprint_moves(companion_result.fingerprint_payload.raw),
                companion_fingerprint_validated=_serialize_fingerprint_moves(companion_result.fingerprint_payload.validated),
                companion_fingerprint_dropped=_serialize_dropped_fingerprint_moves(companion_result.fingerprint_payload.dropped),
                companion_detected_models=_serialize_detected_models(companion_result.detected_models),
                companion_rejected_models=list(companion_result.rejected_models),
                **_frame_audit_fields(frame_card),
                **_structural_coverage_audit_fields(structural_card),
            )
            empty_delta = DeltaCard(findings=(), detected_tendencies=())
            cheat_sheet = select_companion_cheat_sheet(
                companion_result.companion_card, empty_delta,
                query_text=f"{request.query} {request.vanilla_answer}",
                embedding_retriever=self._embedding_retriever if self._config.enable_embeddings else None,
                embedding_api_key=self._embedding_api_key,
                prerequisite_edges=self._companion_knowledge_graph.get("prerequisite_edges"),
            ) if companion_result.companion_card else None
            result = PipelineResult(
                detected_tendencies=(),
                routes=(),
                delta_card=empty_delta,
                audit=audit,
                companion_card=companion_result.companion_card,
                companion_cheat_sheet=cheat_sheet,
                frame_pressure_card=frame_card,
                structural_coverage_card=structural_card,
                prompt_versions=self._prompt_versions,
            )
            self._record_telemetry(
                request=request,
                result=result,
                timings={
                    "total_seconds": round(time.monotonic() - run_started, 3),
                    "pass1_seconds": round(pass1_seconds, 3),
                    "pass2_seconds": 0.0,
                    "companion_seconds": round(companion_seconds, 3),
                },
                companion_candidates=companion_result.candidates,
            )
            return result

        if not self._config.enable_deep_checks:
            # Triage-only mode: skip pass2, build synthetic DeltaCard from triage scores
            triage_by_id = {s.tendency_id: s for s in triage_scores}
            synthetic_results = [
                DeepCheckResult(
                    tendency_id=tid,
                    tendency_name=self._catalog.lookup(tid).display_name,
                    tendency_number=self._catalog.lookup(tid).tendency_number,
                    detected=True,
                    confidence=round(triage_by_id[tid].score / 10.0, 2),
                    evidence=triage_by_id[tid].evidence,
                    sub_pattern="",
                    specific_passage="",
                    severity="medium" if triage_by_id[tid].score >= 7 else "low",
                    reason="triage-only synthetic result",
                )
                for tid in triggered_tendencies
                if tid in triage_by_id
            ]
            routes = tuple(
                route_deep_check_results(
                    synthetic_results,
                    self._catalog,
                    relation_graph=self._relation_graph,
                    max_supporting_models=self._config.max_supporting_models,
                    max_risk_models=self._config.max_risk_models,
                    relevance_scores=lane1_relevance,
                )
            )
            delta_card = _assemble_delta_card(routes, synthetic_results, bundle_selector=self._bundle_selector)
            pass2_seconds = 0.0
            deep_check_results = synthetic_results
            promotion_warnings: list[str] = []
            promoted_overoptimism_results = {}
            promoted_authority_results = {}
            promoted_stress_results = {}
        else:
            pass2_started = time.monotonic()
            deep_check_results, pass2_boundary_calls = _run_pass2_parallel(
                triggered_tendencies=triggered_tendencies,
                request=request,
                boundary=self._boundary,
                catalog=self._catalog,
            )
            boundary_calls.extend(pass2_boundary_calls)
            pass2_seconds = time.monotonic() - pass2_started

            routes = tuple(
                route_deep_check_results(
                    deep_check_results,
                    self._catalog,
                    relation_graph=self._relation_graph,
                    max_supporting_models=self._config.max_supporting_models,
                    max_risk_models=self._config.max_risk_models,
                    relevance_scores=lane1_relevance,
                )
            )
            promotion_warnings: list[str] = []
            promoted_overoptimism_results = _build_promoted_overoptimism_results(
                deep_check_results,
                bridge=self._overoptimism_bridge if self._config.overoptimism_phase1_active else None,
                warnings=promotion_warnings,
            )
            promoted_authority_results = _build_promoted_authority_results(
                deep_check_results,
                bridge=self._authority_bridge if self._config.authority_phase1_active else None,
                warnings=promotion_warnings,
            )
            promoted_stress_results = _build_promoted_stress_results(
                deep_check_results,
                bridge=self._stress_bridge if self._config.stress_phase1_active else None,
                warnings=promotion_warnings,
            )
            delta_card = _assemble_delta_card(
                routes,
                deep_check_results,
                bundle_selector=self._bundle_selector,
                promoted_overoptimism_results=promoted_overoptimism_results,
                promoted_authority_results=promoted_authority_results,
                promoted_stress_results=promoted_stress_results,
            )
        companion_started = time.monotonic()
        companion_result = self._run_companion(request, boundary_calls)
        companion_seconds = time.monotonic() - companion_started
        frame_card = self._run_frame_pressure(
            request, boundary_calls,
            lane1_tendency_ids={route.tendency.tendency_id for route in routes},
            lane1_model_ids=set(delta_card.selected_model_ids),
        )
        _lane2_model_ids = _extract_companion_model_ids(companion_result)
        _lane3_model_ids = _extract_frame_model_ids(frame_card)
        structural_card = self._run_structural_coverage(
            request, boundary_calls,
            lane1_model_ids=set(delta_card.selected_model_ids),
            lane2_model_ids=_lane2_model_ids,
            lane3_model_ids=_lane3_model_ids,
        )
        audit = AuditTrace(
            triage_scores=tuple(triage_scores),
            triggered_tendencies=triggered_tendencies,
            deep_check_results=tuple(deep_check_results),
            routing_decisions=routes,
            boundary_calls=tuple(boundary_calls),
            promoted_bundle_traces=_build_promoted_bundle_traces(
                promoted_overoptimism_results,
                promoted_authority_results,
                promoted_stress_results,
            ),
            warnings=tuple((*self._catalog.warnings, *self._startup_warnings, *promotion_warnings)),
            companion_fingerprint_raw=_serialize_fingerprint_moves(companion_result.fingerprint_payload.raw),
            companion_fingerprint_validated=_serialize_fingerprint_moves(companion_result.fingerprint_payload.validated),
            companion_fingerprint_dropped=_serialize_dropped_fingerprint_moves(companion_result.fingerprint_payload.dropped),
            companion_detected_models=_serialize_detected_models(companion_result.detected_models),
            companion_rejected_models=list(companion_result.rejected_models),
            **_frame_audit_fields(frame_card),
            **_structural_coverage_audit_fields(structural_card),
        )
        cheat_sheet = select_companion_cheat_sheet(
            companion_result.companion_card, delta_card,
            query_text=f"{request.query} {request.vanilla_answer}",
            embedding_retriever=self._embedding_retriever if self._config.enable_embeddings else None,
            embedding_api_key=self._embedding_api_key,
            prerequisite_edges=self._companion_knowledge_graph.get("prerequisite_edges"),
        ) if companion_result.companion_card else None
        result = PipelineResult(
            detected_tendencies=tuple(route.tendency.tendency_id for route in routes),
            routes=routes,
            delta_card=delta_card,
            audit=audit,
            companion_card=companion_result.companion_card,
            companion_cheat_sheet=cheat_sheet,
            frame_pressure_card=frame_card,
            structural_coverage_card=structural_card,
            prompt_versions=self._prompt_versions,
        )
        self._record_telemetry(
            request=request,
            result=result,
            timings={
                "total_seconds": round(time.monotonic() - run_started, 3),
                "pass1_seconds": round(pass1_seconds, 3),
                "pass2_seconds": round(pass2_seconds, 3),
                "companion_seconds": round(companion_seconds, 3),
            },
            companion_candidates=companion_result.candidates,
        )
        return result

    def _build_lane1_relevance_scores(
        self, query_text: str,
    ) -> dict[str, float] | None:
        """Build model relevance scores for Lane 1 neighbor reranking.

        Returns {model_id: cosine_similarity} or None if embeddings unavailable.
        """
        if not self._config.enable_embeddings or self._embedding_retriever is None:
            return None
        if not self._embedding_api_key:
            return None
        ranked = self._embedding_retriever.rank_models_expanded(
            query_text, self._embedding_api_key,
        )
        if not ranked:
            return None
        return {hit["model_id"]: hit["score"] for hit in ranked}

    def _run_companion(
        self,
        request: CritiqueRequest,
        boundary_calls: list[BoundaryCallTrace],
    ) -> CompanionRunResult:
        if not self._config.enable_companion:
            return CompanionRunResult()
        if not self._companion_knowledge_graph:
            return CompanionRunResult(
                companion_card=build_companion_card(
                    detected_models=[],
                    knowledge_graph={},
                    relation_graph={},
                ),
            )

        fingerprint_payload = run_fingerprint_call(
            query=request.query,
            vanilla_answer=request.vanilla_answer,
            client=self._boundary,
        )
        boundary_calls.append(_capture_boundary_call(self._boundary, stage="companion_fingerprint"))
        candidates = recall_candidates(
            vanilla_answer=request.vanilla_answer,
            fingerprint_payload=fingerprint_payload,
            knowledge_graph=self._companion_knowledge_graph,
            reasoning_signals=self._companion_reasoning_signals,
            embedding_retriever=self._embedding_retriever if self._config.enable_embeddings else None,
            embedding_api_key=self._embedding_api_key,
        )
        detected_models, rejected_models = run_verification_call(
            vanilla_answer=request.vanilla_answer,
            fingerprint_payload=fingerprint_payload,
            candidates=candidates,
            client=self._boundary,
        )
        if candidates:
            boundary_calls.append(_capture_boundary_call(self._boundary, stage="companion_verification"))
        return CompanionRunResult(
            companion_card=build_companion_card(
                detected_models=detected_models,
                knowledge_graph=self._companion_knowledge_graph,
                relation_graph=self._companion_relation_graph,
            ),
            fingerprint_payload=fingerprint_payload,
            detected_models=detected_models,
            rejected_models=rejected_models,
            candidates=candidates,
        )

    def _run_frame_pressure(
        self,
        request: CritiqueRequest,
        boundary_calls: list[BoundaryCallTrace],
        lane1_tendency_ids: set[str] | None = None,
        lane1_model_ids: set[str] | None = None,
    ) -> FramePressureCard | None:
        if not self._config.enable_frame_pressure:
            return None

        # Phase 1: Extract frame elements from the query
        extraction_result = run_frame_extraction(
            boundary=self._boundary,
            query=request.query,
            vanilla_answer=request.vanilla_answer,
        )
        boundary_calls.append(_capture_boundary_call(self._boundary, stage="frame_extraction"))

        if extraction_result is None or not extraction_result.frame_elements:
            return extraction_result

        elements = extraction_result.frame_elements
        anti_echo_ids = lane1_model_ids or set()

        # Phase 2: Route + overlap detection
        reframing_routing = self._companion_knowledge_graph.get("reframing_routing", {})
        routes = route_frame_elements(
            elements=elements,
            reframing_routing=reframing_routing,
            anti_echo_model_ids=anti_echo_ids,
        )
        overlap_flags = compute_pressure_concept_overlap(
            elements=elements,
            lane1_tendency_ids=lane1_tendency_ids or set(),
        )

        # Phase 3: Generate reframings + assemble card
        reframings = generate_reframings(
            boundary=self._boundary,
            query=request.query,
            elements=elements,
            routes=routes,
        )
        boundary_calls.append(_capture_boundary_call(self._boundary, stage="frame_reframing"))

        return assemble_frame_card(
            elements=elements,
            routes=routes,
            candidate_reframings=reframings,
            anti_echo_model_ids=anti_echo_ids,
            overlap_flags=overlap_flags,
        )

    def _run_structural_coverage(
        self,
        request: CritiqueRequest,
        boundary_calls: list[BoundaryCallTrace],
        lane1_model_ids: set[str],
        lane2_model_ids: set[str],
        lane3_model_ids: set[str],
    ) -> StructuralCoverageCard | None:
        if not self._config.enable_structural_coverage:
            return None

        routing = self._companion_knowledge_graph.get("structural_coverage_routing", {})
        if not routing:
            return None

        # Anti-echo: exclude models from all other lanes
        anti_echo = lane1_model_ids | lane2_model_ids | lane3_model_ids

        card = run_structural_coverage(
            boundary=self._boundary,
            query=request.query,
            vanilla_answer=request.vanilla_answer,
            structural_coverage_routing=routing,
            anti_echo_model_ids=anti_echo,
        )
        if card is not None:
            boundary_calls.append(
                _capture_boundary_call(self._boundary, stage="structural_coverage_classification")
            )
            boundary_calls.append(
                _capture_boundary_call(self._boundary, stage="structural_coverage_detection")
            )
        return card

    def _record_telemetry(
        self,
        *,
        request: CritiqueRequest,
        result: PipelineResult,
        timings: dict[str, float],
        companion_candidates: list[dict[str, object]],
    ) -> None:
        if self._telemetry_store is None:
            return
        try:
            from .telemetry import record_pipeline_run

            record_pipeline_run(
                store=self._telemetry_store,
                request=request,
                result=result,
                config=self._config,
                tags=self._config.telemetry_tags,
                timings=timings,
                companion_candidates=companion_candidates,
            )
        except Exception:
            _LOGGER.warning("telemetry: failed to record run", exc_info=True)


def _frame_audit_fields(card: FramePressureCard | None) -> dict:
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


def _extract_companion_model_ids(companion_result: CompanionRunResult) -> set[str]:
    """Extract model IDs from Lane 2 companion result for anti-echo."""
    if companion_result.companion_card is None:
        return set()
    return {
        m.model_id
        for m in companion_result.detected_models
        if hasattr(m, "model_id")
    }


def _extract_frame_model_ids(frame_card: FramePressureCard | None) -> set[str]:
    """Extract grounding model IDs from Lane 3 frame pressure card for anti-echo."""
    if frame_card is None:
        return set()
    return {r.grounding_model for r in frame_card.reframings if r.grounding_model}


def _structural_coverage_audit_fields(card: StructuralCoverageCard | None) -> dict:
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


def _capture_boundary_call(
    boundary: BoundaryClient,
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
        prompt_tokens=metadata.prompt_tokens,
        completion_tokens=metadata.completion_tokens,
        total_tokens=metadata.total_tokens,
        cached_tokens=metadata.cached_tokens,
        cache_write_tokens=metadata.cache_write_tokens,
        reasoning_tokens=metadata.reasoning_tokens,
        reasoning_disabled=metadata.reasoning_disabled,
        reasoning_details_present=metadata.reasoning_details_present,
    )


def _run_pass2_single(
    tendency_id: str,
    request: CritiqueRequest,
    boundary: BoundaryClient,
    catalog: TendencyCatalog,
) -> tuple[DeepCheckResult, BoundaryCallTrace]:
    """Run a single Pass 2 deep check. Thread-safe — uses run_json_with_metadata."""
    pass2_system, pass2_user = format_pass2_prompt(
        query=request.query,
        vanilla_answer=request.vanilla_answer,
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
    triggered_tendencies: tuple[str, ...],
    request: CritiqueRequest,
    boundary: BoundaryClient,
    catalog: TendencyCatalog,
) -> tuple[list[DeepCheckResult], list[BoundaryCallTrace]]:
    """Run Pass 2 deep checks in parallel using thread pool.

    Results are returned in the same order as triggered_tendencies.
    Falls back to sequential execution if run_json_with_metadata is unavailable.
    """
    if not triggered_tendencies:
        return [], []

    if not hasattr(boundary, "run_json_with_metadata") or not getattr(boundary, "supports_parallel_calls", False):
        # Fallback for test mocks or custom clients without the new method
        results: list[DeepCheckResult] = []
        traces: list[BoundaryCallTrace] = []
        for tendency_id in triggered_tendencies:
            pass2_system, pass2_user = format_pass2_prompt(
                query=request.query,
                vanilla_answer=request.vanilla_answer,
                tendency_key=tendency_id,
                catalog=catalog,
            )
            payload = boundary.run_json(pass2_system, pass2_user)
            traces.append(_capture_boundary_call(boundary, stage="pass2", tendency_id=tendency_id))
            results.append(parse_pass2_result(payload, requested_tendency_key=tendency_id, catalog=catalog))
        return results, traces

    max_workers = min(len(triggered_tendencies), 8)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(_run_pass2_single, tid, request, boundary, catalog)
            for tid in triggered_tendencies
        ]
    # Collect in submission order (preserves tendency ordering)
    deep_results: list[DeepCheckResult] = []
    boundary_traces: list[BoundaryCallTrace] = []
    for future in futures:
        result, trace = future.result()
        deep_results.append(result)
        boundary_traces.append(trace)
    return deep_results, boundary_traces


def _load_companion_knowledge_graph(root: Path) -> dict:
    # Loads the Wave 1+2+3 compiled knowledge graph from build/.
    # This is NOT the authoritative knowledge source — edit curation/, then recompile.
    # See CLAUDE.md and build/GENERATED.md for the knowledge layer doctrine.
    path = Path(root) / "build" / "knowledge_graph.json"
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _load_companion_relation_graph(root: Path) -> dict | list:
    # Loads the Wave 3 compiled relationship graph from build/.
    # This is NOT the authoritative relation source — edit curation/relation_semantics/, then recompile.
    # See CLAUDE.md and build/GENERATED.md for the knowledge layer doctrine.
    path = Path(root) / "build" / "relationship_graph.json"
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, (dict, list)) else {}


def _load_companion_reasoning_signals(root: Path) -> dict:
    # Recall fallback — derived from compiled fields, not directly from Wave curation.
    # Used only when keyword recall against the knowledge graph yields insufficient candidates.
    path = Path(root) / "build" / "curated" / "reasoning_signals.json"
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _load_embedding_retriever(root: Path):
    """Load embedding retriever if embeddings.db exists. Returns None on failure."""
    db_path = Path(root) / "build" / "embeddings.db"
    if not db_path.exists():
        return None
    try:
        from .embedding_retriever import EmbeddingRetriever
        retriever = EmbeddingRetriever(db_path)
        if retriever.available():
            _LOGGER.debug("embedding_retriever: loaded from %s", db_path)
            return retriever
        _LOGGER.warning("embedding_retriever: DB exists but has no data")
        retriever.close()
    except Exception:
        _LOGGER.warning("embedding_retriever: failed to load", exc_info=True)
    return None


def _load_telemetry_store(root: Path, config: PipelineConfig):
    if not config.enable_telemetry:
        return None
    try:
        from .telemetry import TelemetryStore, default_telemetry_db_path

        db_path = Path(config.telemetry_db_path).expanduser() if str(config.telemetry_db_path).strip() else default_telemetry_db_path(root)
        return TelemetryStore(db_path)
    except Exception:
        _LOGGER.warning("telemetry: failed to initialize store", exc_info=True)
        return None


def _serialize_fingerprint_move(move: FingerprintMove) -> dict[str, object]:
    return {
        "move_id": move.move_id,
        "reasoning_move": move.reasoning_move,
        "evidence_quotes": list(move.evidence_quotes),
        "evidence_rationale": move.evidence_rationale,
        "confidence": move.confidence,
    }


def _serialize_fingerprint_moves(moves: list[FingerprintMove]) -> list[dict[str, object]]:
    return [_serialize_fingerprint_move(move) for move in moves]


def _serialize_dropped_fingerprint_moves(dropped: list[dict[str, object]]) -> list[dict[str, object]]:
    serialized: list[dict[str, object]] = []
    for item in dropped:
        move = item.get("move")
        if not isinstance(move, FingerprintMove):
            continue
        serialized.append(
            {
                "move": _serialize_fingerprint_move(move),
                "drop_reason": str(item.get("drop_reason", "")).strip(),
            }
        )
    return serialized


def _serialize_detected_models(models: list[DetectedModel]) -> list[dict[str, str]]:
    return [
        {
            "model_id": model.model_id,
            "model_name": model.model_name,
            "evidence_quote": model.evidence_quote,
            "presence_mode": model.presence_mode,
            "presence_explanation": model.presence_explanation,
            "detection_confidence": model.detection_confidence,
        }
        for model in models
    ]


def _embedding_tendency_signal(
    vanilla_answer: str,
    retriever,
    api_key: str,
    threshold: float = 0.30,
) -> dict[str, float]:
    """Return {tendency_id: score} for tendencies above embedding threshold.

    Swiss cheese: these are additive candidates for Pass 2, not replacements
    for the LLM triage. The threshold is intentionally conservative —
    only strong semantic matches get promoted.
    """
    if retriever is None or not api_key:
        return {}
    try:
        query_vec = retriever.embed_and_cache(vanilla_answer, api_key)
        if query_vec is None:
            _LOGGER.warning("embedding_tendency_signal: embed_and_cache returned None")
            return {}
        ranked = retriever.rank_tendencies(query_vec, top_k=25)
        return {r["tendency_id"]: r["score"] for r in ranked if r["score"] >= threshold}
    except Exception:
        _LOGGER.warning("embedding_tendency_signal: failed", exc_info=True)
        return {}


def _select_triggered_tendencies(
    triage_scores: list[TriageScore],
    triage_threshold: int,
    *,
    always_include: tuple[str, ...] = (),
    catalog: TendencyCatalog | None = None,
    embedding_tendency_hits: dict[str, float] | None = None,
) -> tuple[str, ...]:
    triggered: list[str] = []
    seen: set[str] = set()
    for score in triage_scores:
        if score.score < triage_threshold:
            continue
        if score.tendency_id in seen:
            continue
        seen.add(score.tendency_id)
        triggered.append(score.tendency_id)

    for raw_key in always_include:
        key = str(raw_key or "").strip()
        if not key:
            continue
        canonical_key = key
        if catalog is not None:
            canonical_key = catalog.lookup(key).tendency_id
        if canonical_key in seen:
            continue
        seen.add(canonical_key)
        triggered.append(canonical_key)

    # Swiss cheese: embedding hits that LLM triage missed
    if embedding_tendency_hits:
        for tendency_id in embedding_tendency_hits:
            if tendency_id in seen:
                continue
            seen.add(tendency_id)
            triggered.append(tendency_id)

    return tuple(triggered)


def _assemble_delta_card(
    routes: tuple[TendencyRoute, ...],
    deep_check_results: list[DeepCheckResult],
    *,
    bundle_selector: PressureBundleSelector | None = None,
    promoted_overoptimism_results: dict[str, PilotDeepCheckBridgeResult] | None = None,
    promoted_authority_results: dict[str, AuthorityPilotBridgeResult] | None = None,
    promoted_stress_results: dict[str, StressPilotBridgeResult] | None = None,
) -> DeltaCard:
    deep_results_by_id = {
        result.tendency_id: result
        for result in deep_check_results
        if result.detected
    }
    findings: list[DeltaFinding] = []
    card_selected_models: list[str] = []
    card_challenge_statements: list[str] = []
    card_next_moves: list[str] = []
    card_major_tensions: list[str] = []

    for route in routes:
        deep_result = deep_results_by_id.get(route.tendency.tendency_id)
        promoted_result = _active_promoted_result_for_tendency(
            route.tendency.tendency_id,
            promoted_overoptimism_results or {},
            promoted_authority_results or {},
            promoted_stress_results or {},
        )
        if promoted_result is not None and deep_result is not None:
            finding = _build_promoted_pilot_finding(
                promoted_result=promoted_result,
                deep_result=deep_result,
            )
            findings.append(finding)
            card_selected_models.extend(finding.selected_model_ids)
            if finding.challenge_statement:
                card_challenge_statements.append(finding.challenge_statement)
            if finding.next_move:
                card_next_moves.append(finding.next_move)
            card_major_tensions.extend(finding.major_tensions)
            continue
        if bundle_selector is not None:
            finding = _build_trusted_bundle_finding(
                bundle_selector=bundle_selector,
                route=route,
                deep_result=deep_result,
            )
            if finding is not None:
                findings.append(finding)
                card_selected_models.extend(finding.selected_model_ids)
                if finding.challenge_statement:
                    card_challenge_statements.append(finding.challenge_statement)
                if finding.next_move:
                    card_next_moves.append(finding.next_move)
                card_major_tensions.extend(finding.major_tensions)
                continue
        selected_model_ids = _dedupe_model_ids(
            (
                route.primary_model_id,
                *route.supporting_model_ids,
            )
        )
        major_tensions = _dedupe_model_ids(route.risk_model_ids)
        challenge_statement = _build_challenge_statement(route, deep_result)
        next_move = route.primary_activation_context or route.tendency.description
        findings.append(
            DeltaFinding(
                tendency_id=route.tendency.tendency_id,
                tendency_name=route.tendency.display_name,
                sub_pattern=deep_result.sub_pattern if deep_result else route.sub_pattern,
                severity=deep_result.severity if deep_result else "",
                specific_passage=deep_result.specific_passage if deep_result else "",
                primary_model_id=route.primary_model_id,
                intervention_hint=next_move,
                supporting_model_ids=route.supporting_model_ids,
                risk_model_ids=route.risk_model_ids,
                selected_model_ids=selected_model_ids,
                major_tensions=major_tensions,
                challenge_statement=challenge_statement,
                next_move=next_move,
            )
        )
        card_selected_models.extend(selected_model_ids)
        if challenge_statement:
            card_challenge_statements.append(challenge_statement)
        if next_move:
            card_next_moves.append(next_move)
        card_major_tensions.extend(major_tensions)
    ordered_findings = _order_findings_for_tiering(findings)
    top_findings, secondary_findings = _split_tiered_findings(ordered_findings)
    top_compound_groups = _build_compound_groups(top_findings, tier="top")
    secondary_compound_groups = _build_compound_groups(
        secondary_findings,
        tier="secondary",
        all_findings=tuple(ordered_findings),
    )
    (
        presented_secondary_findings,
        secondary_summarization_active,
        secondary_additional_pressures_note,
        secondary_additional_pressure_tendency_ids,
    ) = _build_presented_secondary_layer(
        top_findings=top_findings,
        secondary_findings=secondary_findings,
        secondary_compound_groups=secondary_compound_groups,
    )
    return DeltaCard(
        findings=tuple(ordered_findings),
        top_findings=top_findings,
        secondary_findings=secondary_findings,
        presented_secondary_findings=presented_secondary_findings,
        compound_groups=tuple((*top_compound_groups, *secondary_compound_groups)),
        top_compound_groups=top_compound_groups,
        secondary_compound_groups=secondary_compound_groups,
        secondary_summarization_active=secondary_summarization_active,
        secondary_additional_pressures_note=secondary_additional_pressures_note,
        secondary_additional_pressure_count=len(secondary_additional_pressure_tendency_ids),
        secondary_additional_pressure_tendency_ids=secondary_additional_pressure_tendency_ids,
        detected_tendencies=tuple(route.tendency.tendency_id for route in routes),
        selected_model_ids=_dedupe_model_ids(card_selected_models),
        challenge_statements=tuple(card_challenge_statements),
        next_moves=tuple(card_next_moves),
        major_tensions=_dedupe_model_ids(card_major_tensions),
        top_challenge_statements=tuple(
            finding.challenge_statement for finding in top_findings if finding.challenge_statement
        ),
        secondary_challenge_statements=tuple(
            finding.challenge_statement
            for finding in secondary_findings
            if finding.challenge_statement
        ),
        top_next_moves=tuple(finding.next_move for finding in top_findings if finding.next_move),
        secondary_next_moves=tuple(
            finding.next_move for finding in secondary_findings if finding.next_move
        ),
    )


def _order_findings_for_tiering(findings: list[DeltaFinding]) -> list[DeltaFinding]:
    return [
        finding
        for _, finding in sorted(
            enumerate(findings),
            key=lambda item: (
                _finding_specificity_rank(item[1]),
                _severity_rank(item[1].severity),
                item[0],
            ),
        )
    ]


def _split_tiered_findings(
    findings: list[DeltaFinding],
) -> tuple[tuple[DeltaFinding, ...], tuple[DeltaFinding, ...]]:
    top = tuple(finding for finding in findings if _finding_specificity_rank(finding) == 0)
    secondary = tuple(finding for finding in findings if _finding_specificity_rank(finding) != 0)
    if top:
        return top, secondary
    if not findings:
        return (), ()
    return (findings[0],), tuple(findings[1:])


def _build_compound_groups(
    findings: tuple[DeltaFinding, ...],
    *,
    tier: str,
    all_findings: tuple[DeltaFinding, ...] | None = None,
) -> tuple[CompoundGroup, ...]:
    findings_by_tendency = {finding.tendency_id: finding for finding in findings}
    all_findings_by_tendency = {
        finding.tendency_id: finding for finding in (all_findings if all_findings is not None else findings)
    }
    used_tendencies: set[str] = set()
    compounds: list[CompoundGroup] = []
    ordered_definitions = sorted(
        enumerate(COMPOUND_CATALOG),
        key=lambda item: (-len(item[1].member_tendency_ids), item[0]),
    )
    for _, definition in ordered_definitions:
        if any(member_id in used_tendencies for member_id in definition.member_tendency_ids):
            continue
        tendency_source = all_findings_by_tendency if definition.cross_tier else findings_by_tendency
        if any(member_id not in tendency_source for member_id in definition.member_tendency_ids):
            continue
        compound_findings = tuple(
            tendency_source[member_id] for member_id in definition.member_tendency_ids
        )
        compounds.append(
            CompoundGroup(
                compound_id=definition.compound_id,
                label=definition.label,
                description=definition.description,
                member_tendency_ids=definition.member_tendency_ids,
                findings=compound_findings,
                tier=tier,
            )
        )
        used_tendencies.update(definition.member_tendency_ids)
    return tuple(compounds)


def _build_presented_secondary_layer(
    *,
    top_findings: tuple[DeltaFinding, ...],
    secondary_findings: tuple[DeltaFinding, ...],
    secondary_compound_groups: tuple[CompoundGroup, ...],
) -> tuple[tuple[DeltaFinding, ...], bool, str, tuple[str, ...]]:
    grouped_tendency_ids = {
        tendency_id
        for group in secondary_compound_groups
        for tendency_id in group.member_tendency_ids
    }
    ungrouped_secondary_findings = tuple(
        finding
        for finding in secondary_findings
        if finding.tendency_id not in grouped_tendency_ids
    )
    top_named_surface_count = sum(
        1
        for finding in top_findings
        if _finding_specificity_rank(finding) == 0
    )
    should_summarize = (
        top_named_surface_count >= 2
        and bool(secondary_compound_groups)
        and bool(ungrouped_secondary_findings)
    )
    if not should_summarize:
        return (
            ungrouped_secondary_findings,
            False,
            "",
            (),
        )
    tendency_ids = tuple(finding.tendency_id for finding in ungrouped_secondary_findings)
    labels = ", ".join(
        _display_tendency_label(finding.tendency_name)
        for finding in ungrouped_secondary_findings
    )
    note = f"Additional pressures present: {labels}."
    return (
        (),
        True,
        note,
        tendency_ids,
    )


def _display_tendency_label(tendency_name: str) -> str:
    cleaned = str(tendency_name or "").strip()
    if cleaned.endswith(" Tendency"):
        cleaned = cleaned[: -len(" Tendency")]
    return cleaned


def _finding_specificity_rank(finding: DeltaFinding) -> int:
    normalized = str(finding.sub_pattern or "").strip().replace("_", "-").lower()
    if finding.is_trusted_surface and normalized and normalized != "general":
        return 0
    return 1


def _severity_rank(severity: str) -> int:
    normalized = str(severity or "").strip().lower()
    if normalized == "high":
        return 0
    if normalized == "medium":
        return 1
    if normalized == "low":
        return 2
    return 3


def _build_promoted_overoptimism_results(
    deep_check_results: list[DeepCheckResult],
    *,
    bridge: PilotDeepCheckBridge | None,
    warnings: list[str],
) -> dict[str, PilotDeepCheckBridgeResult]:
    return _build_promoted_results_for_tendency(
        deep_check_results,
        bridge=bridge,
        tendency_id="overoptimism-tendency",
        warnings=warnings,
        active_warning="overoptimism-phase1-live-promotion-active",
        skipped_warning_prefix="overoptimism-phase1-live-promotion-skipped:",
        strip_pilot_result=lambda bridge_result: PilotDeepCheckBridgeResult(
            adaptation=bridge_result.adaptation,
            pilot_result=None,
        ),
    )


_AUTHORITY_PROMOTED_SUBPATTERNS = frozenset(
    {
        "prestige-cue-substitution",
        "authority-overrides-protocol",
    }
)


def _build_promoted_authority_results(
    deep_check_results: list[DeepCheckResult],
    *,
    bridge: AuthorityPilotBridge | None,
    warnings: list[str],
) -> dict[str, AuthorityPilotBridgeResult]:
    return _build_promoted_results_for_tendency(
        deep_check_results,
        bridge=bridge,
        tendency_id="authority-misinfluence-tendency",
        warnings=warnings,
        active_warning="authority-phase1-live-promotion-active",
        skipped_warning_prefix="authority-phase1-live-promotion-skipped:",
        promoted_subpatterns=_AUTHORITY_PROMOTED_SUBPATTERNS,
        strip_pilot_result=lambda bridge_result: AuthorityPilotBridgeResult(
            adaptation=bridge_result.adaptation,
            pilot_result=None,
        ),
    )


_STRESS_PROMOTED_SUBPATTERNS = frozenset({"deadline-driven-shortcutting"})


def _build_promoted_results_for_tendency(
    deep_check_results: list[DeepCheckResult],
    *,
    bridge: object | None,
    tendency_id: str,
    warnings: list[str],
    active_warning: str,
    skipped_warning_prefix: str,
    strip_pilot_result: Callable[[object], object],
    promoted_subpatterns: frozenset[str] | None = None,
    observation_only_warning_prefix: str | None = None,
) -> dict[str, object]:
    if bridge is None:
        return {}
    results: dict[str, object] = {}
    for deep_result in deep_check_results:
        if not deep_result.detected:
            continue
        if deep_result.tendency_id != tendency_id:
            continue
        bridge_result = bridge.run(deep_result)
        results[deep_result.tendency_id] = bridge_result
        mapped_subpattern = bridge_result.adaptation.mapped_subpattern_id
        if bridge_result.pilot_result is not None and (
            promoted_subpatterns is None or mapped_subpattern in promoted_subpatterns
        ):
            warnings.append(active_warning)
            continue
        if bridge_result.pilot_result is not None and observation_only_warning_prefix is not None:
            warnings.append(
                f"{observation_only_warning_prefix}{mapped_subpattern or bridge_result.adaptation.adaptation_mode}"
            )
        else:
            warnings.append(f"{skipped_warning_prefix}{bridge_result.adaptation.adaptation_mode}")
        results[deep_result.tendency_id] = strip_pilot_result(bridge_result)
    return results


def _build_promoted_stress_results(
    deep_check_results: list[DeepCheckResult],
    *,
    bridge: StressPilotBridge | None,
    warnings: list[str],
) -> dict[str, StressPilotBridgeResult]:
    return _build_promoted_results_for_tendency(
        deep_check_results,
        bridge=bridge,
        tendency_id="stress-influence-tendency",
        warnings=warnings,
        active_warning="stress-phase1-live-promotion-active",
        skipped_warning_prefix="stress-phase1-live-promotion-skipped:",
        promoted_subpatterns=_STRESS_PROMOTED_SUBPATTERNS,
        observation_only_warning_prefix="stress-phase1-live-observation-only:",
        strip_pilot_result=lambda bridge_result: StressPilotBridgeResult(
            adaptation=bridge_result.adaptation,
            pilot_result=None,
        ),
    )


def _active_promoted_result_for_tendency(
    tendency_id: str,
    *promoted_result_groups: dict[str, object],
) -> object | None:
    for promoted_results in promoted_result_groups:
        promoted_result = promoted_results.get(tendency_id)
        if promoted_result is None:
            continue
        if getattr(promoted_result, "pilot_result", None) is not None:
            return promoted_result
    return None


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


def _build_promoted_pilot_finding(
    *,
    promoted_result: object,
    deep_result: DeepCheckResult,
) -> DeltaFinding:
    pilot_result = getattr(promoted_result, "pilot_result")
    assert pilot_result is not None
    bundle = pilot_result.bundle
    selected_chunks = pilot_result.trace.selected_chunks
    chunks_by_type = {chunk.chunk_type: chunk for chunk in selected_chunks}
    challenge_chunk = chunks_by_type.get("challenge") or chunks_by_type.get("premortem_question")
    protocol_chunk = chunks_by_type.get("protocol") or chunks_by_type.get("heuristic")
    tension_chunk = (
        chunks_by_type.get("tension")
        or chunks_by_type.get("guardrail")
        or chunks_by_type.get("danger_when")
        or chunks_by_type.get("failure_mode")
    )
    selected_model_ids = _dedupe_model_ids(tuple(chunk.model_id for chunk in selected_chunks))
    next_move = protocol_chunk.text if protocol_chunk is not None else (challenge_chunk.text if challenge_chunk is not None else "")
    major_tensions = (tension_chunk.text,) if tension_chunk is not None else ()
    return DeltaFinding(
        tendency_id=deep_result.tendency_id,
        tendency_name=deep_result.tendency_name,
        sub_pattern=bundle.route.subpattern_id,
        severity=deep_result.severity,
        specific_passage=deep_result.specific_passage,
        primary_model_id=bundle.route.primary_model_id,
        intervention_hint=next_move,
        supporting_model_ids=bundle.route.supporting_model_ids,
        risk_model_ids=bundle.route.risk_model_ids,
        selected_model_ids=selected_model_ids,
        major_tensions=major_tensions,
        challenge_statement=challenge_chunk.text if challenge_chunk is not None else "",
        next_move=next_move,
        is_trusted_surface=True,
    )


def _build_trusted_bundle_finding(
    *,
    bundle_selector: PressureBundleSelector,
    route: TendencyRoute,
    deep_result: DeepCheckResult | None,
) -> DeltaFinding | None:
    normalized_subpattern_id = _normalize_trusted_bundle_subpattern_id(
        route.tendency.tendency_id,
        route.sub_pattern,
        deep_result=deep_result,
    )
    try:
        bundle = bundle_selector.select(
            route.tendency.tendency_id,
            subpattern_id=normalized_subpattern_id,
        )
    except Exception:
        return None
    selected_chunks = bundle.selected_chunks
    if not selected_chunks:
        return None
    chunks_by_type = {chunk.chunk_type: chunk for chunk in selected_chunks}
    challenge_chunk = chunks_by_type.get("challenge") or chunks_by_type.get("premortem_question")
    protocol_chunk = chunks_by_type.get("protocol") or chunks_by_type.get("heuristic")
    tension_chunk = (
        chunks_by_type.get("tension")
        or chunks_by_type.get("guardrail")
        or chunks_by_type.get("danger_when")
        or chunks_by_type.get("failure_mode")
    )
    selected_model_ids = _dedupe_model_ids(tuple(chunk.model_id for chunk in selected_chunks))
    next_move = protocol_chunk.text if protocol_chunk is not None else (challenge_chunk.text if challenge_chunk is not None else "")
    major_tensions = (tension_chunk.text,) if tension_chunk is not None else ()
    return DeltaFinding(
        tendency_id=route.tendency.tendency_id,
        tendency_name=route.tendency.display_name,
        sub_pattern=bundle.route.subpattern_id,
        severity=deep_result.severity if deep_result is not None else "",
        specific_passage=deep_result.specific_passage if deep_result is not None else "",
        primary_model_id=bundle.route.primary_model_id,
        intervention_hint=next_move,
        supporting_model_ids=bundle.route.supporting_model_ids,
        risk_model_ids=bundle.route.risk_model_ids,
        selected_model_ids=selected_model_ids,
        major_tensions=major_tensions,
        challenge_statement=challenge_chunk.text if challenge_chunk is not None else "",
        next_move=next_move,
        is_trusted_surface=True,
    )


def _normalize_trusted_bundle_subpattern_id(
    tendency_id: str,
    sub_pattern: str,
    *,
    deep_result: DeepCheckResult | None = None,
) -> str:
    normalized_tendency_id = str(tendency_id or "").strip().replace("_", "-").lower()
    normalized_sub_pattern = str(sub_pattern or "").strip().replace("_", "-").lower()
    if normalized_tendency_id == "overoptimism-tendency":
        if normalized_sub_pattern == "base-rates":
            return "missing-denominator"
        if normalized_sub_pattern == "premortem":
            return "missing-reversal-condition"
    if normalized_tendency_id == "availability-misweighing-tendency":
        if normalized_sub_pattern == "base-rates":
            return "vivid-proof-substitution"
    if normalized_tendency_id == "inconsistency-avoidance-tendency":
        if deep_result is not None:
            return map_inconsistency_avoidance_result_to_subpattern(deep_result)
        if normalized_sub_pattern == "iteration":
            return "escalation-of-prior-design"
        if normalized_sub_pattern in {"first-principles-thinking", "first_principles_thinking"}:
            return "exception-to-preserve-plan"
    if normalized_tendency_id == "deprival-superreaction-tendency":
        if deep_result is not None:
            return map_deprival_superreaction_result_to_subpattern(deep_result)
        if normalized_sub_pattern == "decision-trees":
            return "near-miss-opportunity-ratchet"
        if normalized_sub_pattern == "endowment-effect":
            return "takeaway-pain-dampening"
        if normalized_sub_pattern == "expected-value":
            return "general"
    if normalized_tendency_id == "simple-pain-avoiding-psychological-denial":
        if deep_result is not None:
            return map_simple_pain_denial_result_to_subpattern(deep_result)
        if normalized_sub_pattern in {"premortem", "falsifiability"}:
            return "downside-softened-into-benign-story"
        if normalized_sub_pattern == "internal-locus-of-control":
            return "blame-shift-over-reality-contact"
    if normalized_tendency_id == "influence-from-mere-association-tendency":
        if deep_result is not None:
            return map_influence_from_mere_association_result_to_subpattern(deep_result)
        if normalized_sub_pattern == "scientific-method-evidence-testing":
            return "halo-transfer-over-substance"
        if normalized_sub_pattern == "root-cause-analysis":
            return "familiarity-equals-performance"
        if normalized_sub_pattern == "law-of-large-numbers":
            return "price-quality-signal-substitution"
        if normalized_sub_pattern == "psychological-safety":
            return "messenger-contamination"
    if normalized_tendency_id == "excessive-self-regard-tendency":
        if deep_result is not None:
            return map_excessive_self_regard_result_to_subpattern(deep_result)
        if normalized_sub_pattern in {"circle-of-competence", "user-centered-design"}:
            return "own-offering-overrated-as-uniquely-fit"
        if normalized_sub_pattern == "confidence-calibration":
            return "value-story-certainty-without-calibration"
        if normalized_sub_pattern == "johari-window":
            return "impression-over-record-selection"
        if normalized_sub_pattern == "feynman-technique":
            return "creator-judgment-insulated-from-peer-check"
        if normalized_sub_pattern == "peer-review-your-perspectives":
            return "general"
    if normalized_tendency_id == "authority-misinfluence-tendency":
        if deep_result is not None:
            mapped_subpattern = map_authority_result_to_subpattern(deep_result)
            if mapped_subpattern in {
                "prestige-cue-substitution",
                "authority-overrides-protocol",
            }:
                return mapped_subpattern
            return "general"
        return "general"
    if normalized_tendency_id == "reward-and-punishment-superresponse-tendency":
        if deep_result is not None:
            mapped_subpattern = map_reward_and_punishment_result_to_subpattern(deep_result)
            if mapped_subpattern in {
                "compensation-design-as-behavior-engine",
                "reward-window-over-governance",
                "capture-speed-over-readiness",
            }:
                return mapped_subpattern
            return "general"
        return "general"
    if normalized_tendency_id == "kantian-fairness-tendency":
        if deep_result is not None:
            mapped_subpattern = map_kantian_fairness_result_to_subpattern(deep_result)
            if mapped_subpattern in {
                "fair-sharing-expected-despite-leverage-asymmetry",
                "reciprocal-courtesy-assumed-without-enforcement",
                "concession-reciprocity-assumed-as-self-executing",
            }:
                return mapped_subpattern
            return "general"
        return "general"
    if normalized_tendency_id == "reciprocation-tendency":
        if deep_result is not None:
            mapped_subpattern = map_reciprocation_result_to_subpattern(deep_result)
            if mapped_subpattern in {
                "vendor-favors-treated-as-decision-debt",
                "courtesy-back-assumed-after-concession",
                "past-devotion-buys-current-exemption",
            }:
                return mapped_subpattern
            return "general"
        return "general"
    if normalized_tendency_id == "disliking-hating-tendency":
        if deep_result is not None:
            mapped_subpattern = map_disliking_hating_result_to_subpattern(deep_result)
            if mapped_subpattern in {
                "hostile-motive-overread-driving-switch",
                "messenger-punished-for-bad-news",
                "disliked-presenter-vetoes-valid-option",
            }:
                return mapped_subpattern
            return "general"
        return "general"
    if normalized_tendency_id == "envy-jealousy-tendency":
        if deep_result is not None:
            mapped_subpattern = map_envy_jealousy_result_to_subpattern(deep_result)
            if mapped_subpattern in {
                "peer-outcome-becomes-compensation-anchor",
                "comparative-status-gap-treated-as-emergency",
                "rivalry-escalation-over-own-standards",
            }:
                return mapped_subpattern
            return "general"
        return "general"
    if normalized_tendency_id == "liking-loving-tendency":
        if deep_result is not None:
            mapped_subpattern = map_liking_loving_result_to_subpattern(deep_result)
            if mapped_subpattern in {
                "admired-insider-devotion-over-external-check",
                "relationship-goodwill-over-cost-reality",
                "high-touch-affection-over-competitive-check",
                "trusted-referral-glow-over-vetting",
            }:
                return mapped_subpattern
            return "general"
        return "general"
    if normalized_tendency_id == "contrast-misreaction-tendency":
        if deep_result is not None:
            mapped_subpattern = map_contrast_misreaction_result_to_subpattern(deep_result)
            if mapped_subpattern in {
                "incumbent-relative-offset",
                "slow-drift-under-registration-threshold",
                "deal-size-over-absolute-risk",
                "prestige-frame-distortion",
            }:
                return mapped_subpattern
            return "general"
        return "general"
    if normalized_tendency_id == "curiosity-tendency":
        if deep_result is not None:
            mapped_subpattern = map_curiosity_result_to_subpattern(deep_result)
            if mapped_subpattern in {
                "shallow-first-answer-accepted",
                "inquiry-suppressed-for-momentum",
                "missing-process-self-audit",
            }:
                return mapped_subpattern
            return "general"
        return "general"
    if normalized_tendency_id == "twaddle-tendency":
        if deep_result is not None:
            mapped_subpattern = map_twaddle_result_to_subpattern(deep_result)
            if mapped_subpattern in {
                "procedural-noise-crowds-substance",
                "effort-spread-not-concentrated",
                "jargon-masking-shallow-analysis",
            }:
                return mapped_subpattern
            return "general"
        return "general"
    if normalized_tendency_id == "use-it-or-lose-it-tendency":
        if deep_result is not None:
            mapped_subpattern = map_use_it_or_lose_it_result_to_subpattern(deep_result)
            if mapped_subpattern in {
                "stale-methodology-unquestioned",
                "lapsed-process-from-neglect",
                "degraded-pattern-recognition",
            }:
                return mapped_subpattern
            return "general"
        return "general"
    if normalized_tendency_id == "lollapalooza-tendency":
        if deep_result is not None:
            mapped_subpattern = map_lollapalooza_result_to_subpattern(deep_result)
            if mapped_subpattern in {
                "undiagnosed-tendency-compounding",
                "cascade-effects-treated-in-isolation",
                "missing-structural-firebreak",
            }:
                return mapped_subpattern
            return "general"
        return "general"
    if normalized_tendency_id == "doubt-avoidance-tendency":
        if deep_result is not None:
            mapped_subpattern = map_doubt_avoidance_result_to_subpattern(deep_result)
            if mapped_subpattern in {
                "forced-closure-under-pressure",
                "unknowns-demoted-to-keep-motion",
                "option-set-collapse",
                "counterargument-window-skipped",
            }:
                return mapped_subpattern
            return "general"
        return "general"
    if normalized_tendency_id == "stress-influence-tendency":
        if deep_result is not None:
            mapped_subpattern = map_stress_result_to_subpattern(deep_result)
            if mapped_subpattern in {
                "deadline-driven-shortcutting",
                "load-collapse-and-omission",
                "feedback-threat-hijack",
                "challenge-beyond-capacity",
            }:
                return mapped_subpattern
            return "general"
        return "general"
    if normalized_tendency_id == "social-proof-tendency":
        if deep_result is not None:
            mapped_subpattern = map_social_proof_result_to_subpattern(deep_result)
            if mapped_subpattern in {
                "borrowed-consensus-as-proof",
                "stress-amplified-herd-following",
                "inaction-as-consensus-signal",
                "contagious-normalization",
            }:
                return mapped_subpattern
            return "general"
        return "general"
    if normalized_tendency_id == "reason-respecting-tendency":
        if deep_result is not None:
            mapped_subpattern = map_reason_respecting_result_to_subpattern(deep_result)
            if mapped_subpattern in {
                "narrative-closes-the-why",
                "correlation-accepted-as-cause",
                "shallow-first-why-stops-inquiry",
            }:
                return mapped_subpattern
            return "general"
        return "general"
    return normalized_sub_pattern


def _build_challenge_statement(
    route: TendencyRoute,
    deep_result: DeepCheckResult | None,
) -> str:
    tendency_label = route.tendency.display_name.removesuffix(" Tendency")
    if deep_result is not None and deep_result.specific_passage and deep_result.evidence:
        return (
            f"{tendency_label}: challenge '{deep_result.specific_passage}' because "
            f"{_to_sentence_fragment(deep_result.evidence)}"
        )
    if deep_result is not None and deep_result.evidence:
        return f"{tendency_label}: {_ensure_sentence(deep_result.evidence)}"
    if route.primary_activation_context:
        return f"{tendency_label}: {_ensure_sentence(route.primary_activation_context)}"
    if route.tendency.description:
        return f"{tendency_label}: {_ensure_sentence(route.tendency.description)}"
    return tendency_label


def _to_sentence_fragment(text: str) -> str:
    cleaned = str(text or "").strip()
    if not cleaned:
        return ""
    cleaned = cleaned.rstrip(".")
    return cleaned[0].lower() + cleaned[1:] if cleaned[:1].isupper() else cleaned


def _ensure_sentence(text: str) -> str:
    cleaned = str(text or "").strip()
    if not cleaned:
        return ""
    if cleaned.endswith((".", "!", "?")):
        return cleaned
    return f"{cleaned}."


def _dedupe_model_ids(model_ids: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    deduped: list[str] = []
    seen: set[str] = set()
    for model_id in model_ids:
        if not model_id or model_id in seen:
            continue
        seen.add(model_id)
        deduped.append(model_id)
    return tuple(deduped)


def _load_overoptimism_bridge(
    root: Path,
    config: PipelineConfig,
) -> tuple[PilotDeepCheckBridge | None, tuple[str, ...]]:
    if not config.overoptimism_phase1_active:
        return None, ()
    if not _env_truthy("LOLLA_OVEROPTIMISM_PHASE1_ACTIVE", default=True):
        return None, ("overoptimism-phase1-live-promotion-disabled-by-env",)
    required_paths = (
        Path(root) / "build" / "curated" / "subpattern_catalog.json",
        Path(root) / "build" / "curated" / "compiled_chunks.json",
        Path(root) / "build" / "curated" / "structural_signal_lexicon.json",
    )
    if any(not path.exists() for path in required_paths):
        return None, ("overoptimism-phase1-live-promotion-unavailable",)
    try:
        return PilotDeepCheckBridge.load(root), ()
    except Exception:
        return None, ("overoptimism-phase1-live-promotion-unavailable",)


def _load_authority_bridge(
    root: Path,
    config: PipelineConfig,
) -> tuple[AuthorityPilotBridge | None, tuple[str, ...]]:
    if not config.authority_phase1_active:
        return None, ()
    if not _env_truthy("LOLLA_AUTHORITY_PHASE1_ACTIVE", default=True):
        return None, ("authority-phase1-live-promotion-disabled-by-env",)
    try:
        workspace = Path(root) / ".tmp" / "authority_phase1_live_workspace"
        AuthorityPhase1Builder.load(root, output_root=workspace).compile()
        return AuthorityPilotBridge.load(workspace), ()
    except Exception:
        return None, ("authority-phase1-live-promotion-unavailable",)


def _load_stress_bridge(
    root: Path,
    config: PipelineConfig,
) -> tuple[StressPilotBridge | None, tuple[str, ...]]:
    if not config.stress_phase1_active:
        return None, ()
    if not _env_truthy("LOLLA_STRESS_PHASE1_ACTIVE", default=True):
        return None, ("stress-phase1-live-promotion-disabled-by-env",)
    try:
        workspace = Path(root) / ".tmp" / "stress_phase1_live_workspace"
        StressPhase1Builder.load(root, output_root=workspace).compile()
        return StressPilotBridge.load(workspace), ()
    except Exception:
        return None, ("stress-phase1-live-promotion-unavailable",)


def _load_bundle_selector(root: Path) -> PressureBundleSelector | None:
    required_paths = (
        Path(root) / "build" / "curated" / "subpattern_catalog.json",
        Path(root) / "build" / "curated" / "compiled_chunks.json",
        Path(root) / "build" / "curated" / "structural_signal_lexicon.json",
    )
    if any(not path.exists() for path in required_paths):
        return None
    try:
        return PressureBundleSelector.load(root)
    except Exception:
        return None


def _env_truthy(name: str, *, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return str(raw).strip().lower() not in {"", "0", "false", "no", "off"}


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
