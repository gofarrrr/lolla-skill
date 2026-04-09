from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class RelationNeighbor:
    model_id: str
    edge_type: str
    composition_affinity: float
    source_description: str = ""


@dataclass(frozen=True)
class RouteNeighborhood:
    supporting_model_ids: tuple[str, ...] = ()
    risk_model_ids: tuple[str, ...] = ()


class RelationGraph:
    def __init__(self, graph: dict[str, tuple[RelationNeighbor, ...]]) -> None:
        self._graph = graph

    @classmethod
    def load(cls, root: Path) -> "RelationGraph":
        # Loads relationship_graph.json — Wave 3–derived when compiled with operational curation
        # and curation/relation_semantics/ present; otherwise legacy markdown extraction.
        # See CLAUDE.md and build/GENERATED.md for the knowledge layer doctrine.
        path = Path(root) / "build" / "relationship_graph.json"
        if not path.exists():
            return cls({})

        try:
            raw_edges = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return cls({})

        graph: dict[str, list[RelationNeighbor]] = {}
        edges = raw_edges if isinstance(raw_edges, list) else raw_edges.get("edges", [])
        if not isinstance(edges, list):
            return cls({})

        for edge in edges:
            if not isinstance(edge, dict):
                continue
            source_model_id = str(edge.get("source_model_id", "")).strip()
            target_model_id = str(edge.get("target_model_id", "")).strip()
            if not source_model_id or not target_model_id:
                continue
            graph.setdefault(source_model_id, []).append(
                RelationNeighbor(
                    model_id=target_model_id,
                    edge_type=str(edge.get("edge_type", "")).strip().lower(),
                    composition_affinity=float(edge.get("composition_affinity", 0.0) or 0.0),
                    source_description=str(edge.get("source_description", "") or ""),
                )
            )

        return cls({source: tuple(neighbors) for source, neighbors in graph.items()})

    def neighborhood(
        self,
        seed_model_ids: list[str] | tuple[str, ...],
        *,
        max_supporting_models: int = 2,
        max_risk_models: int = 1,
        min_supporting_affinity: float = 0.6,
    ) -> RouteNeighborhood:
        seeds = tuple(model_id for model_id in seed_model_ids if model_id)
        if not seeds:
            return RouteNeighborhood()

        seed_set = set(seeds)
        supporting_candidates: list[tuple[float, str]] = []
        risk_candidates: list[tuple[float, str]] = []

        for seed_model_id in seeds:
            for neighbor in self._graph.get(seed_model_id, ()):
                if neighbor.model_id in seed_set:
                    continue
                if neighbor.edge_type in {"ally", "compound"}:
                    if neighbor.composition_affinity < min_supporting_affinity:
                        continue
                    supporting_candidates.append((neighbor.composition_affinity, neighbor.model_id))
                elif neighbor.edge_type in {"antagonist", "tension"}:
                    risk_candidates.append((neighbor.composition_affinity, neighbor.model_id))

        return RouteNeighborhood(
            supporting_model_ids=_bounded_unique_model_ids(
                supporting_candidates,
                limit=max_supporting_models,
            ),
            risk_model_ids=_bounded_unique_model_ids(
                risk_candidates,
                limit=max_risk_models,
            ),
        )


def _bounded_unique_model_ids(
    candidates: list[tuple[float, str]],
    *,
    limit: int,
) -> tuple[str, ...]:
    if limit <= 0:
        return ()

    ordered = sorted(candidates, key=lambda candidate: (-candidate[0], candidate[1]))
    results: list[str] = []
    seen: set[str] = set()
    for _affinity, model_id in ordered:
        if model_id in seen:
            continue
        seen.add(model_id)
        results.append(model_id)
        if len(results) >= limit:
            break
    return tuple(results)
