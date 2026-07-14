#!/usr/bin/env python3
"""Run a provider-free fact-free deterministic graph-impact shadow."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.reasoning_pattern_shadow import (  # noqa: E402
    conversation_turn_numbers, normalized_projection_signature,
    route_projection, seal_pattern_response,
)
from engine.system_b.relation_graph import RelationGraph, RelationNeighbor  # noqa: E402


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _load_explicit_graph(path: Path) -> RelationGraph:
    edges = _load(path)
    if not isinstance(edges, list) or not edges:
        raise RuntimeError("explicit relationship graph is absent or empty")
    adjacency: dict[str, list[RelationNeighbor]] = {}
    for edge in edges:
        source = str(edge.get("source_model_id", "")).strip()
        target = str(edge.get("target_model_id", "")).strip()
        if not source or not target:
            continue
        adjacency.setdefault(source, []).append(RelationNeighbor(
            model_id=target,
            edge_type=str(edge.get("edge_type", "")).strip().lower(),
            composition_affinity=float(edge.get("composition_affinity", 0.0) or 0.0),
            source_description=str(edge.get("source_description", "") or ""),
            affinity_rationale=str(edge.get("affinity_rationale", "") or ""),
            activation_condition=str(edge.get("activation_condition", "") or ""),
        ))
    if not adjacency:
        raise RuntimeError("explicit relationship graph produced no adjacency")
    return RelationGraph({source: tuple(neighbors) for source, neighbors in adjacency.items()})


def _expand(graph: RelationGraph, seeds: list[str], *, support_cap: int, risk_cap: int) -> dict:
    rows, selected_support, selected_risk = [], set(), set()
    for seed in seeds:
        neighborhood = graph.neighborhood((seed,), max_supporting_models=support_cap, max_risk_models=risk_cap)
        selected_support.update(neighborhood.supporting_model_ids)
        selected_risk.update(neighborhood.risk_model_ids)
        rows.append({
            "seed_model_id": seed,
            "supporting_model_ids": list(neighborhood.supporting_model_ids),
            "risk_model_ids": list(neighborhood.risk_model_ids),
            "supporting_candidate_trace": [asdict(item) for item in neighborhood.supporting_candidate_trace],
            "risk_candidate_trace": [asdict(item) for item in neighborhood.risk_candidate_trace],
            "tiebreaker_supporting": asdict(neighborhood.tiebreaker_supporting) if neighborhood.tiebreaker_supporting else {},
            "tiebreaker_risk": asdict(neighborhood.tiebreaker_risk) if neighborhood.tiebreaker_risk else {},
        })
    return {"per_seed": rows, "selected_supporting_model_ids": sorted(selected_support), "selected_risk_model_ids": sorted(selected_risk), "embedding_tiebreaker_attempted": False}


def run(contract_path: Path) -> dict:
    contract = _load(contract_path)
    if contract.get("status") != "provider_free_deterministic_shadow_authorized":
        raise RuntimeError("graph-impact contract is not authorized")
    interpretations_path = ROOT / contract["interpretations_path"]
    interpretations = _load(interpretations_path)
    routing_path = ROOT / contract["routing_contract_path"]
    routing = _load(routing_path)
    affordances_path = ROOT / contract["affordances_path"]
    affordances = _load(affordances_path)
    known = {str(item["model_id"]) for item in affordances["model_records"]}
    graph_path = ROOT / contract["relationship_graph_path"]
    graph = _load_explicit_graph(graph_path)
    scope = contract["deterministic_graph_scope"]
    arms = {}
    for case in interpretations["cases"]:
        conversation_path = ROOT / case["conversation_path"]
        valid_turns = conversation_turn_numbers(conversation_path.read_text(encoding="utf-8"))
        for arm in case["arms"]:
            source_path = ROOT / arm["source_ref"]
            packet = seal_pattern_response(
                {"patterns": arm["patterns"]}, packet_id=arm["arm_id"],
                source_ref=arm["source_ref"], source_sha256=_sha(source_path),
                valid_turn_numbers=valid_turns,
            )
            seed_route = route_projection(packet, routing_contract=routing, known_model_ids=known)
            seed_ids = [item["model_id"] for item in seed_route["seed_candidates"]]
            arms[arm["arm_id"]] = {
                "case_id": case["case_id"], "packet": packet,
                "projection_signature": normalized_projection_signature(packet),
                "seed_route": seed_route,
                "deterministic_neighborhood": _expand(graph, seed_ids, support_cap=scope["maximum_supporting_per_seed"], risk_cap=scope["maximum_risk_per_seed"]),
                "review_note": arm["review_note"],
            }
    comparisons = []
    for prefix in ("registry", "housing"):
        source, provider, ablation = arms[f"{prefix}_source_first"], arms[f"{prefix}_provider"], arms[f"{prefix}_missing_reversal_ablation"]
        def seed_ids(value: dict) -> list[str]:
            return [item["model_id"] for item in value["seed_route"]["seed_candidates"]]
        def neighborhood_signature(value: dict) -> dict:
            n = value["deterministic_neighborhood"]
            return {"supporting": n["selected_supporting_model_ids"], "risk": n["selected_risk_model_ids"]}
        comparisons.append({
            "case_id": source["case_id"],
            "source_provider": {
                "projection_equal": source["projection_signature"] == provider["projection_signature"],
                "seed_candidates_equal": seed_ids(source) == seed_ids(provider),
                "deterministic_neighborhood_equal": neighborhood_signature(source) == neighborhood_signature(provider),
            },
            "sensitivity_control": {
                "projection_differs_after_missing_reversal_ablation": source["projection_signature"] != ablation["projection_signature"],
                "seed_candidates_differ_after_missing_reversal_ablation": seed_ids(source) != seed_ids(ablation),
                "removed_seed_candidates": sorted(set(seed_ids(source)) - set(seed_ids(ablation))),
                "remaining_neighborhood_overlap_is_allowed": True,
            },
        })
    gates = [
        item["source_provider"]["projection_equal"]
        and item["source_provider"]["seed_candidates_equal"]
        and item["source_provider"]["deterministic_neighborhood_equal"]
        and item["sensitivity_control"]["projection_differs_after_missing_reversal_ablation"]
        and item["sensitivity_control"]["seed_candidates_differ_after_missing_reversal_ablation"]
        for item in comparisons
    ]
    return {
        "schema_version": "lolla.reasoning_process_graph_impact_shadow_result.v1",
        "status": "provider_free_deterministic_graph_impact_shadow_pass" if all(gates) else "provider_free_deterministic_graph_impact_shadow_fail",
        "contract_path": str(contract_path.relative_to(ROOT)), "contract_sha256": _sha(contract_path),
        "interpretations_path": contract["interpretations_path"], "interpretations_sha256": _sha(interpretations_path),
        "routing_contract_sha256": _sha(routing_path), "relationship_graph_path": contract["relationship_graph_path"], "relationship_graph_sha256": _sha(graph_path),
        "arms": arms, "comparisons": comparisons,
        "embedding_comparison": {"status": "not_authorized_missing_typed_reasoning_pattern_adapter", "embedding_calls": 0, "raw_role_prose_embedded": False},
        "boundary": {"provider_calls": 0, "evaluator_calls": 0, "embedding_calls": 0, "deterministic_graph_reads": True, "runtime_mutations": 0, "reconsideration_calls": 0, "receipts_written": 0, "scalar_quality_score_computed": False, "semantic_winner_inferred_by_code": False, "production_integration_authorized": False},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.contract.resolve())
    _write(args.output.resolve(), result)
    print(json.dumps({"status": result["status"], "comparisons": result["comparisons"], "embedding_comparison": result["embedding_comparison"]}, indent=2))
    return 0 if result["status"].endswith("_pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
