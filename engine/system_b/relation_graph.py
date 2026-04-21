from __future__ import annotations

from dataclasses import dataclass
import json
import math
from pathlib import Path
from typing import Any, Callable


# Phase 3 Commit B calibration constants (commit 43d39e4, 2026-04-21).
# See research/deep-graph-enrichment-handover.md §14h item 2 for the
# measurement protocol and the sample distributions these numbers come from.
#
# ε: top-1/top-2 fan-adjusted affinity delta below which we consider the
# pair a "near-tie" worth consulting the activation matcher for. Measured
# on 204 qualifying seeds; 18% have delta < 0.01, 1% are exact ties.
_ACTIVATION_MATCH_EPSILON = 0.01
#
# Noise floor: cosine similarity below which the matcher's answer is too
# weak to override affinity ordering. Measured against 6 probes × 523 ally
# edges: on-target reasoning prose lands at 0.73–0.79 top-1, deliberately
# off-topic ("bread proofing") lands at 0.19 — 0.45 sits in the ~30-point
# protective gap between real signal and noise.
_ACTIVATION_MATCH_NOISE_FLOOR = 0.45


@dataclass(frozen=True)
class RelationNeighbor:
    model_id: str
    edge_type: str
    composition_affinity: float
    source_description: str = ""
    affinity_rationale: str = ""
    activation_condition: str = ""


@dataclass(frozen=True)
class RouteNeighborhood:
    supporting_model_ids: tuple[str, ...] = ()
    risk_model_ids: tuple[str, ...] = ()


class RelationGraph:
    def __init__(self, graph: dict[str, tuple[RelationNeighbor, ...]]) -> None:
        self._graph = graph
        # Degree counts for fan correction — hub models (high degree) get their
        # ranking affinity dampened so focused models can surface.
        dc: dict[str, int] = {}
        for source, neighbors in graph.items():
            dc[source] = dc.get(source, 0) + len(neighbors)
            for n in neighbors:
                dc[n.model_id] = dc.get(n.model_id, 0) + 1
        self._degree_counts = dc

    def _fan_adjusted_affinity(self, model_id: str, raw_affinity: float) -> float:
        """Dampen affinity for hub models: affinity / (1 + ln(degree))."""
        fan = self._degree_counts.get(model_id, 1)
        if fan <= 1:
            return raw_affinity
        return raw_affinity / (1.0 + math.log(fan))

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
                    affinity_rationale=str(edge.get("affinity_rationale", "") or ""),
                    activation_condition=str(edge.get("activation_condition", "") or ""),
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
        relevance_scores: dict[str, float] | None = None,
        reasoning_context: Any = None,
        embeddings_db_path: Path | str | None = None,
        openai_api_key: str | None = None,
        _activation_matcher: Callable[..., Any] | None = None,
    ) -> RouteNeighborhood:
        seeds = tuple(model_id for model_id in seed_model_ids if model_id)
        if not seeds:
            return RouteNeighborhood()

        seed_set = set(seeds)
        # Candidate tuples carry source + edge_type so the activation matcher
        # has the edge-identity triple it needs. `_bounded_unique_model_ids`
        # only consumes (adj_aff, model_id).
        supporting_candidates: list[tuple[float, str, str, str]] = []
        risk_candidates: list[tuple[float, str, str, str]] = []

        for seed_model_id in seeds:
            for neighbor in self._graph.get(seed_model_id, ()):
                if neighbor.model_id in seed_set:
                    continue
                if neighbor.edge_type in {"ally", "compound"}:
                    if neighbor.composition_affinity < min_supporting_affinity:
                        continue
                    adjusted = self._fan_adjusted_affinity(
                        neighbor.model_id, neighbor.composition_affinity,
                    )
                    supporting_candidates.append(
                        (adjusted, neighbor.model_id, seed_model_id, neighbor.edge_type)
                    )
                elif neighbor.edge_type in {"antagonist", "tension"}:
                    adjusted = self._fan_adjusted_affinity(
                        neighbor.model_id, neighbor.composition_affinity,
                    )
                    risk_candidates.append(
                        (adjusted, neighbor.model_id, seed_model_id, neighbor.edge_type)
                    )

        # Phase 3 activation-match tiebreaker. Fires only when reasoning context
        # is supplied AND no relevance_scores are overriding the sort AND a DB
        # path is available. When it doesn't fire, behavior is byte-identical
        # to the pre-wire default path.
        if (
            reasoning_context is not None
            and relevance_scores is None
            and embeddings_db_path is not None
        ):
            supporting_candidates = _activation_retie_if_near_tie(
                supporting_candidates,
                reasoning_context=reasoning_context,
                db_path=embeddings_db_path,
                api_key=openai_api_key,
                matcher=_activation_matcher,
            )
            risk_candidates = _activation_retie_if_near_tie(
                risk_candidates,
                reasoning_context=reasoning_context,
                db_path=embeddings_db_path,
                api_key=openai_api_key,
                matcher=_activation_matcher,
            )

        return RouteNeighborhood(
            supporting_model_ids=_bounded_unique_model_ids(
                [(c[0], c[1]) for c in supporting_candidates],
                limit=max_supporting_models,
                relevance_scores=relevance_scores,
            ),
            risk_model_ids=_bounded_unique_model_ids(
                [(c[0], c[1]) for c in risk_candidates],
                limit=max_risk_models,
                relevance_scores=relevance_scores,
            ),
        )


def _activation_retie_if_near_tie(
    candidates: list[tuple[float, str, str, str]],
    *,
    reasoning_context: Any,
    db_path: Path | str,
    api_key: str | None,
    matcher: Callable[..., Any] | None,
) -> list[tuple[float, str, str, str]]:
    """Phase 3 near-tie tiebreaker. Returns the candidates list with the top-2
    (by adjusted affinity, deduped by model_id) potentially reordered based on
    activation-match cosine similarity. All other items are preserved.

    Fires only when all four conditions hold:
      1. ≥2 distinct candidates after dedup
      2. top-1 vs top-2 adjusted affinity delta < ε
      3. matcher returns scores for both top-1 and top-2
      4. max(top-1 sim, top-2 sim) ≥ noise floor

    Any degradation (missing DB, missing backfill rows, empty matcher output,
    any exception from the matcher that isn't TypeError) is a silent no-op.
    TypeError from the matcher IS re-raised — the matcher contract says type
    violations are programmer errors, not runtime degradations.
    """
    if len(candidates) < 2:
        return candidates

    # Dedup by model_id, keeping highest-affinity occurrence. Mirrors the
    # later _bounded_unique_model_ids dedup so we compare the right two.
    deduped: dict[str, tuple[float, str, str, str]] = {}
    for c in candidates:
        existing = deduped.get(c[1])
        if existing is None or c[0] > existing[0]:
            deduped[c[1]] = c
    ordered = sorted(deduped.values(), key=lambda c: (-c[0], c[1]))
    if len(ordered) < 2:
        return candidates

    top1, top2 = ordered[0], ordered[1]
    if top1[0] - top2[0] >= _ACTIVATION_MATCH_EPSILON:
        return candidates

    if matcher is None:
        from .activation_matcher import match_activation
        matcher = match_activation

    edges = [
        (top1[2], top1[1], top1[3]),
        (top2[2], top2[1], top2[3]),
    ]
    try:
        results = matcher(
            reasoning_context, edges, db_path=db_path, api_key=api_key,
        )
    except TypeError:
        raise
    except Exception:
        return candidates

    if not results or len(results) < 2:
        return candidates

    by_target = {r.target_model_id: r.similarity for r in results}
    sim_top1 = by_target.get(top1[1], 0.0)
    sim_top2 = by_target.get(top2[1], 0.0)

    if max(sim_top1, sim_top2) < _ACTIVATION_MATCH_NOISE_FLOOR:
        return candidates

    if sim_top2 <= sim_top1:
        return candidates

    # Swap: give top2 a tiny affinity bump so the downstream
    # _bounded_unique_model_ids sort surfaces it first. The bump is invisible
    # to callers (only model_ids are returned) and cannot cascade past the
    # immediate top-2 because top-3's affinity is at least ε below top-1.
    bumped = (top1[0] + 1e-6, top2[1], top2[2], top2[3])
    # Drop every occurrence of top2's model_id and prepend the bumped row.
    # Keep all other items (including duplicates of top1's model_id from
    # other seeds) so dedup-by-model_id downstream still produces a stable
    # total order.
    remaining = [c for c in candidates if c[1] != top2[1]]
    return [bumped, *remaining]


def _bounded_unique_model_ids(
    candidates: list[tuple[float, str]],
    *,
    limit: int,
    relevance_scores: dict[str, float] | None = None,
) -> tuple[str, ...]:
    if limit <= 0:
        return ()

    if relevance_scores:
        ordered = sorted(
            candidates,
            key=lambda c: (-relevance_scores.get(c[1], 0.0), -c[0], c[1]),
        )
    else:
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
