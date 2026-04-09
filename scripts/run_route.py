#!/usr/bin/env python3
"""
Deterministic routing for Lolla skill.

Given detected tendency IDs, returns the relevant knowledge slices:
corrective models, failure modes, heuristics, premortem questions,
and relationship edges.

Usage:
    python3 scripts/run_route.py --tendencies "overoptimism-tendency,authority-misinfluence-tendency"

Output: JSON with knowledge slices per tendency.
"""

import argparse
import json
import sys
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_kg():
    kg_path = DATA_DIR / "knowledge_graph.json"
    with open(kg_path) as f:
        return json.load(f)


def load_relation_graph():
    """Load relationship graph. Returns list of edge dicts."""
    rg_path = DATA_DIR / "relationship_graph.json"
    if not rg_path.exists():
        return []
    with open(rg_path) as f:
        data = json.load(f)
    # Graph is a flat list of edges
    return data if isinstance(data, list) else data.get("edges", [])


def load_curation(model_id: str) -> dict:
    """Load Wave 1 curation for a model if available."""
    curation_path = DATA_DIR / "curation" / f"{model_id}.json"
    if curation_path.exists():
        with open(curation_path) as f:
            return json.load(f)
    return {}


def load_intervention(model_id: str) -> dict:
    """Load Wave 2 intervention semantics if available."""
    intervention_path = DATA_DIR / "curation" / "intervention_semantics" / f"{model_id}.json"
    if intervention_path.exists():
        with open(intervention_path) as f:
            return json.load(f)
    return {}


def expand_neighborhood(model_ids: list[str], rg: list, *, max_allies: int = 3, max_antagonists: int = 3) -> dict:
    """1-hop relation graph expansion for a set of seed models.

    Returns dict with 'allies' and 'antagonists' lists, each sorted by
    composition_affinity descending.  Deduplicates against the seed set.
    """
    seed_set = set(model_ids)
    ally_candidates: list[tuple[float, str, str]] = []  # (affinity, model_id, description)
    antag_candidates: list[tuple[float, str, str]] = []

    for edge in rg:
        source = edge.get("source_model_id", "")
        target = edge.get("target_model_id", "")
        edge_type = edge.get("edge_type", "").lower()
        affinity = float(edge.get("composition_affinity", 0.0) or 0.0)
        desc = (edge.get("source_description") or edge.get("target_description") or "")[:200]

        if source in seed_set and target not in seed_set:
            neighbor_id = target
        elif target in seed_set and source not in seed_set:
            neighbor_id = source
        else:
            continue

        if edge_type in ("ally", "compound"):
            ally_candidates.append((affinity, neighbor_id, desc))
        elif edge_type in ("antagonist", "tension"):
            antag_candidates.append((affinity, neighbor_id, desc))

    def dedupe_top(candidates, limit):
        candidates.sort(key=lambda c: (-c[0], c[1]))
        seen = set()
        result = []
        for affinity, mid, desc in candidates:
            if mid in seen:
                continue
            seen.add(mid)
            result.append({"model_id": mid, "affinity": affinity, "description": desc})
            if len(result) >= limit:
                break
        return result

    return {
        "allies": dedupe_top(ally_candidates, max_allies),
        "antagonists": dedupe_top(antag_candidates, max_antagonists),
    }


def route_tendency(tendency_id: str, kg: dict, rg: list) -> dict:
    """Route a single tendency to its knowledge slices."""
    tendency = kg.get("tendencies", {}).get(tendency_id)
    if not tendency:
        return {"error": f"Unknown tendency: {tendency_id}"}

    antidotes = tendency.get("antidote_models", [])
    models_data = []

    for binding in antidotes:
        model_id = binding["model"]
        activation_context = binding.get("activation_context", "")

        # Load curation and intervention data
        curation = load_curation(model_id)
        intervention = load_intervention(model_id)

        # Get model info from KG
        model_info = kg.get("models", {}).get(model_id, {})

        # Find relationship edges for this model
        edges = [
            e for e in rg
            if e.get("source_model_id") == model_id or e.get("target_model_id") == model_id
        ]

        model_data = {
            "model_id": model_id,
            "activation_context": activation_context,
            "core_idea": model_info.get("core_idea", ""),
        }

        # Wave 1: activation semantics
        if curation:
            model_data["select_when"] = curation.get("select_when", "")
            model_data["danger_when"] = curation.get("avoid_when", "")

        # Wave 2: intervention semantics
        if intervention:
            failure_modes = intervention.get("failure_modes", [])
            if failure_modes:
                model_data["failure_modes"] = [
                    {
                        "description": fm.get("description", ""),
                        "mitigation": fm.get("mitigation", ""),
                    }
                    for fm in failure_modes[:3]  # Top 3 to keep context lean
                ]
            heuristics = intervention.get("heuristics", [])
            if heuristics:
                model_data["heuristics"] = [
                    h.get("description", "") for h in heuristics[:3]
                ]
            premortems = intervention.get("premortem_questions", [])
            if premortems:
                model_data["premortem_questions"] = [
                    p.get("question", "") if isinstance(p, dict) else str(p)
                    for p in premortems[:3]
                ]

        # Wave 3: key relationships (direct edges)
        if edges:
            model_data["relationships"] = [
                {
                    "type": e.get("edge_type", ""),
                    "other_model": e.get("target_model_id") if e.get("source_model_id") == model_id else e.get("source_model_id"),
                    "description": (e.get("source_description") or e.get("target_description") or "")[:200],
                }
                for e in edges[:5]
            ]

        models_data.append(model_data)

    # 1-hop neighborhood expansion across all corrective models for this tendency
    corrective_ids = [b["model"] for b in antidotes]
    neighborhood = expand_neighborhood(corrective_ids, rg)

    return {
        "tendency_id": tendency_id,
        "description": tendency.get("description", ""),
        "corrective_models": models_data,
        "neighborhood": neighborhood,
    }


def main():
    parser = argparse.ArgumentParser(description="Route tendencies to knowledge slices")
    parser.add_argument("--tendencies", required=True, help="Comma-separated tendency IDs")
    args = parser.parse_args()

    tendency_ids = [t.strip() for t in args.tendencies.split(",") if t.strip()]

    kg = load_kg()
    rg = load_relation_graph()

    results = []
    for tid in tendency_ids:
        results.append(route_tendency(tid, kg, rg))

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
