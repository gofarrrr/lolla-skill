from __future__ import annotations

from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True)
class DetectedModel:
    model_id: str
    model_name: str
    evidence_quote: str
    presence_mode: str
    presence_explanation: str
    detection_confidence: str


@dataclass(frozen=True)
class FingerprintMove:
    move_id: str
    reasoning_move: str
    evidence_quotes: list[str]
    evidence_rationale: str
    confidence: str


@dataclass(frozen=True)
class FingerprintPayload:
    raw: list[FingerprintMove]
    validated: list[FingerprintMove]
    dropped: list[dict[str, object]]


@dataclass(frozen=True)
class CompanionExpansion:
    source_model_id: str
    relation_type: str
    model_id: str
    model_name: str
    substrate_chunk: str
    why_relevant: str
    tension_type: str | None = None
    affinity_rationale: str = ""
    activation_condition: str = ""


@dataclass(frozen=True)
class CompanionFailureHint:
    """Wave 2 failure mode snippet for a detected model (compact, provenance-tagged)."""

    source_model_id: str
    text: str
    extraction_type: str
    confidence: str


@dataclass(frozen=True)
class CompanionHeuristicHint:
    """Wave 2 heuristic snippet for a detected model (compact, provenance-tagged)."""

    source_model_id: str
    text: str
    extraction_type: str
    confidence: str


@dataclass(frozen=True)
class CompanionPremortermHint:
    """Wave 2 premortem question for a detected model (compact, provenance-tagged)."""

    source_model_id: str
    text: str
    extraction_type: str
    confidence: str


@dataclass(frozen=True)
class CompanionIdentityChunk:
    """Wave 1 identity snapshot for a detected model."""

    model_id: str
    display_name: str
    select_when: tuple[str, ...]
    danger_when: tuple[str, ...]
    reasoning_types: tuple[str, ...]
    input_type: str
    output_type: str


@dataclass(frozen=True)
class CompanionCard:
    detected_models: list[DetectedModel]
    expansions: list[CompanionExpansion]
    failure_hints: list[CompanionFailureHint]
    heuristic_hints: list[CompanionHeuristicHint]
    premortem_hints: list[CompanionPremortermHint]
    identity_chunks: list[CompanionIdentityChunk]
    detection_model_count: int
    expansion_count: int
    failure_hint_count: int
    heuristic_hint_count: int
    premortem_hint_count: int
    identity_chunk_count: int
    detection_source: str

    def __post_init__(self) -> None:
        if self.detection_model_count > 5:
            raise ValueError("CompanionCard cannot contain more than 5 detected models")

        if self.expansion_count != len(self.expansions):
            raise ValueError("expansion_count must match len(expansions)")

        if self.failure_hint_count != len(self.failure_hints):
            raise ValueError("failure_hint_count must match len(failure_hints)")

        if self.heuristic_hint_count != len(self.heuristic_hints):
            raise ValueError("heuristic_hint_count must match len(heuristic_hints)")

        if self.premortem_hint_count != len(self.premortem_hints):
            raise ValueError("premortem_hint_count must match len(premortem_hints)")

        if self.identity_chunk_count != len(self.identity_chunks):
            raise ValueError("identity_chunk_count must match len(identity_chunks)")

        expansions_by_source = Counter(item.source_model_id for item in self.expansions)
        if any(count > 3 for count in expansions_by_source.values()):
            raise ValueError("CompanionCard cannot contain more than 3 expansions per detected model")

        hints_by_source = Counter(item.source_model_id for item in self.failure_hints)
        if any(count > 2 for count in hints_by_source.values()):
            raise ValueError("CompanionCard cannot contain more than 2 failure hints per detected model")

        heuristics_by_source = Counter(item.source_model_id for item in self.heuristic_hints)
        if any(count > 2 for count in heuristics_by_source.values()):
            raise ValueError("CompanionCard cannot contain more than 2 heuristic hints per detected model")

        premortems_by_source = Counter(item.source_model_id for item in self.premortem_hints)
        if any(count > 2 for count in premortems_by_source.values()):
            raise ValueError("CompanionCard cannot contain more than 2 premortem hints per detected model")


def build_companion_card(
    *,
    detected_models: list[DetectedModel],
    knowledge_graph: dict,
    relation_graph: dict,
) -> CompanionCard:
    from .companion_routing import (
        collect_failure_hints_for_model,
        collect_heuristics_for_model,
        collect_identity_for_model,
        collect_premortem_questions_for_model,
        expand_detected_model,
    )

    expansions: list[CompanionExpansion] = []
    failure_hints: list[CompanionFailureHint] = []
    heuristic_hints: list[CompanionHeuristicHint] = []
    premortem_hints: list[CompanionPremortermHint] = []
    identity_chunks: list[CompanionIdentityChunk] = []
    for detected_model in detected_models:
        expansions.extend(
            expand_detected_model(
                model_id=detected_model.model_id,
                knowledge_graph=knowledge_graph,
                relation_graph=relation_graph,
                max_expansions=3,
            )
        )
        failure_hints.extend(
            collect_failure_hints_for_model(
                detected_model.model_id,
                knowledge_graph,
                max_hints=2,
            )
        )
        heuristic_hints.extend(
            collect_heuristics_for_model(
                detected_model.model_id,
                knowledge_graph,
                max_hints=2,
            )
        )
        premortem_hints.extend(
            collect_premortem_questions_for_model(
                detected_model.model_id,
                knowledge_graph,
                max_hints=2,
            )
        )
        identity_chunk = collect_identity_for_model(
            detected_model.model_id,
            knowledge_graph,
        )
        if identity_chunk is not None:
            identity_chunks.append(identity_chunk)

    return CompanionCard(
        detected_models=detected_models,
        expansions=expansions,
        failure_hints=failure_hints,
        heuristic_hints=heuristic_hints,
        premortem_hints=premortem_hints,
        identity_chunks=identity_chunks,
        detection_model_count=len(detected_models),
        expansion_count=len(expansions),
        failure_hint_count=len(failure_hints),
        heuristic_hint_count=len(heuristic_hints),
        premortem_hint_count=len(premortem_hints),
        identity_chunk_count=len(identity_chunks),
        detection_source="independent_llm_pass",
    )
