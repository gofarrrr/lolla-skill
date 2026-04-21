from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, TYPE_CHECKING

from .relation_graph import RelationGraph
from .subpattern_catalog import SourceRef
from .tendency_catalog import ModelBinding, TendencyCatalog, TendencyRef

if TYPE_CHECKING:
    from .deep_checks import DeepCheckResult


@dataclass(frozen=True)
class TendencyRoute:
    tendency: TendencyRef
    primary_model_id: str = ""
    primary_activation_context: str = ""
    primary_activation_context_ref: SourceRef | None = None
    primary_activation_context_blocking_quality_flags: tuple[str, ...] = ()
    primary_activation_context_advisory_quality_flags: tuple[str, ...] = ()
    antidote_model_ids: tuple[str, ...] = ()
    core_model_ids: tuple[str, ...] = ()
    related_dynamics: tuple[str, ...] = ()
    supporting_model_ids: tuple[str, ...] = ()
    risk_model_ids: tuple[str, ...] = ()
    sub_pattern: str = ""


def route_tendency(
    tendency_key: str,
    catalog: TendencyCatalog,
    sub_pattern: str = "",
    relation_graph: RelationGraph | None = None,
    max_supporting_models: int = 2,
    max_risk_models: int = 1,
    relevance_scores: dict[str, float] | None = None,
    reasoning_context: Any = None,
    embeddings_db_path: Path | str | None = None,
    openai_api_key: str | None = None,
) -> TendencyRoute:
    tendency = catalog.lookup(tendency_key)
    primary_binding = _match_primary_binding(tendency.antidote_bindings, sub_pattern)
    neighborhood = relation_graph.neighborhood(
        (primary_binding.model_id,) if primary_binding else (),
        max_supporting_models=max_supporting_models,
        max_risk_models=max_risk_models,
        relevance_scores=relevance_scores,
        reasoning_context=reasoning_context,
        embeddings_db_path=embeddings_db_path,
        openai_api_key=openai_api_key,
    ) if relation_graph is not None else None
    return TendencyRoute(
        tendency=tendency,
        primary_model_id=primary_binding.model_id if primary_binding else "",
        primary_activation_context=primary_binding.activation_context if primary_binding else "",
        primary_activation_context_ref=(
            primary_binding.activation_context_ref if primary_binding is not None else None
        ),
        primary_activation_context_blocking_quality_flags=(
            primary_binding.blocking_quality_flags if primary_binding is not None else ()
        ),
        primary_activation_context_advisory_quality_flags=(
            primary_binding.advisory_quality_flags if primary_binding is not None else ()
        ),
        antidote_model_ids=tendency.antidote_model_ids,
        core_model_ids=tendency.core_model_ids,
        related_dynamics=tendency.related_dynamics,
        supporting_model_ids=neighborhood.supporting_model_ids if neighborhood else (),
        risk_model_ids=neighborhood.risk_model_ids if neighborhood else (),
        sub_pattern=sub_pattern,
    )


def route_detected_tendencies(
    tendency_keys: list[str],
    catalog: TendencyCatalog,
    relation_graph: RelationGraph | None = None,
    max_supporting_models: int = 2,
    max_risk_models: int = 1,
    relevance_scores: dict[str, float] | None = None,
    reasoning_context: Any = None,
    embeddings_db_path: Path | str | None = None,
    openai_api_key: str | None = None,
) -> list[TendencyRoute]:
    routes: list[TendencyRoute] = []
    seen: set[str] = set()

    for tendency_key in tendency_keys:
        route = route_tendency(
            tendency_key,
            catalog,
            relation_graph=relation_graph,
            max_supporting_models=max_supporting_models,
            max_risk_models=max_risk_models,
            relevance_scores=relevance_scores,
            reasoning_context=reasoning_context,
            embeddings_db_path=embeddings_db_path,
            openai_api_key=openai_api_key,
        )
        tendency_id = route.tendency.tendency_id
        if tendency_id in seen:
            continue
        seen.add(tendency_id)
        routes.append(route)

    return routes


def route_deep_check_results(
    deep_results: list["DeepCheckResult"],
    catalog: TendencyCatalog,
    relation_graph: RelationGraph | None = None,
    max_supporting_models: int = 2,
    max_risk_models: int = 1,
    relevance_scores: dict[str, float] | None = None,
    reasoning_context: Any = None,
    embeddings_db_path: Path | str | None = None,
    openai_api_key: str | None = None,
) -> list[TendencyRoute]:
    routes: list[TendencyRoute] = []
    seen: set[str] = set()

    for result in deep_results:
        if not result.detected:
            continue
        route = route_tendency(
            result.tendency_id,
            catalog,
            sub_pattern=result.sub_pattern,
            relation_graph=relation_graph,
            max_supporting_models=max_supporting_models,
            max_risk_models=max_risk_models,
            relevance_scores=relevance_scores,
            reasoning_context=reasoning_context,
            embeddings_db_path=embeddings_db_path,
            openai_api_key=openai_api_key,
        )
        tendency_id = route.tendency.tendency_id
        if tendency_id in seen:
            continue
        seen.add(tendency_id)
        routes.append(route)

    return routes


def _match_primary_binding(
    antidote_bindings: tuple[ModelBinding, ...],
    sub_pattern: str,
) -> ModelBinding | None:
    if not antidote_bindings:
        return None

    normalized_sub_pattern = _normalize_sub_pattern(sub_pattern)
    if normalized_sub_pattern:
        for binding in antidote_bindings:
            normalized_model_id = binding.model_id.lower()
            if (
                normalized_sub_pattern == normalized_model_id
                or normalized_sub_pattern.startswith(normalized_model_id)
                or normalized_model_id.startswith(normalized_sub_pattern)
            ):
                return binding

    return antidote_bindings[0]


def _normalize_sub_pattern(value: str) -> str:
    return str(value or "").strip().replace("_", "-").lower()
