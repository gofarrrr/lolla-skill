from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .relation_graph import RelationGraph
from .subpattern_catalog import SourceRef, SubpatternCatalog, SubpatternRef
from .tendency_catalog import TendencyCatalog


@dataclass(frozen=True)
class PressureRoute:
    tendency_id: str
    tendency_name: str
    subpattern_id: str
    subpattern_name: str
    primary_model_id: str = ""
    primary_activation_context: str = ""
    primary_activation_context_ref: SourceRef | None = None
    primary_activation_context_blocking_quality_flags: tuple[str, ...] = ()
    primary_activation_context_advisory_quality_flags: tuple[str, ...] = ()
    candidate_model_ids: tuple[str, ...] = ()
    supporting_model_ids: tuple[str, ...] = ()
    risk_model_ids: tuple[str, ...] = ()


class PressureRouter:
    def __init__(
        self,
        catalog: TendencyCatalog,
        subpatterns: SubpatternCatalog,
        relation_graph: RelationGraph,
    ) -> None:
        self._catalog = catalog
        self._subpatterns = subpatterns
        self._relation_graph = relation_graph

    @classmethod
    def load(cls, root: Path) -> "PressureRouter":
        root = Path(root)
        return cls(
            catalog=TendencyCatalog.load(root),
            subpatterns=SubpatternCatalog.load(root),
            relation_graph=RelationGraph.load(root),
        )

    def route(
        self,
        tendency_key: str,
        *,
        subpattern_id: str = "general",
        max_supporting_models: int = 2,
        max_risk_models: int = 1,
        reasoning_context: Any = None,
        embeddings_db_path: Path | str | None = None,
        openai_api_key: str | None = None,
    ) -> PressureRoute:
        tendency = self._catalog.lookup(tendency_key)
        subpattern = self._resolve_subpattern(
            tendency_id=tendency.tendency_id,
            requested_subpattern_id=subpattern_id,
        )
        candidate_model_ids = _dedupe_model_ids(
            (*subpattern.primary_model_ids, *subpattern.supporting_model_ids)
        )
        primary_model_id = subpattern.primary_model_ids[0] if subpattern.primary_model_ids else ""
        neighborhood = self._relation_graph.neighborhood(
            (primary_model_id,) if primary_model_id else (),
            max_supporting_models=max_supporting_models,
            max_risk_models=max_risk_models,
            reasoning_context=reasoning_context,
            embeddings_db_path=embeddings_db_path,
            openai_api_key=openai_api_key,
        )
        primary_binding = _binding_for_model(subpattern, primary_model_id)
        return PressureRoute(
            tendency_id=tendency.tendency_id,
            tendency_name=tendency.display_name,
            subpattern_id=subpattern.subpattern_id,
            subpattern_name=subpattern.display_name,
            primary_model_id=primary_model_id,
            primary_activation_context=primary_binding.activation_context if primary_binding is not None else "",
            primary_activation_context_ref=(
                primary_binding.source_refs[0] if primary_binding is not None and primary_binding.source_refs else None
            ),
            primary_activation_context_blocking_quality_flags=(
                primary_binding.blocking_quality_flags if primary_binding is not None else ()
            ),
            primary_activation_context_advisory_quality_flags=(
                primary_binding.advisory_quality_flags if primary_binding is not None else ()
            ),
            candidate_model_ids=candidate_model_ids,
            supporting_model_ids=neighborhood.supporting_model_ids,
            risk_model_ids=neighborhood.risk_model_ids,
        )

    def _resolve_subpattern(
        self,
        *,
        tendency_id: str,
        requested_subpattern_id: str,
    ) -> SubpatternRef:
        tendency_subpatterns = self._subpatterns.for_tendency(tendency_id)
        requested = _normalize_subpattern_id(requested_subpattern_id)
        general: SubpatternRef | None = None
        for subpattern in tendency_subpatterns.subpatterns:
            normalized = _normalize_subpattern_id(subpattern.subpattern_id)
            if normalized == "general":
                general = subpattern
            if requested and normalized == requested:
                return subpattern
        if general is not None:
            return general
        if tendency_subpatterns.subpatterns:
            return tendency_subpatterns.subpatterns[0]
        raise KeyError(f"No subpatterns defined for {tendency_id}")


def _normalize_subpattern_id(value: str) -> str:
    return str(value or "").strip().replace("_", "-").lower()


def _dedupe_model_ids(model_ids: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    results: list[str] = []
    seen: set[str] = set()
    for model_id in model_ids:
        if not model_id or model_id in seen:
            continue
        seen.add(model_id)
        results.append(model_id)
    return tuple(results)


def _binding_for_model(subpattern: SubpatternRef, model_id: str):
    target = str(model_id or "").strip()
    if not target:
        return None
    for binding in subpattern.bindings:
        if binding.model_id == target:
            return binding
    return None
