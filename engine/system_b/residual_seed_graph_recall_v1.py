"""Deterministic graph recall from every residual seed, independent of coverage."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import Any

from .residual_challenge_representation_v1 import CANDIDATE_KINDS
from .residual_challenge_seed_v1 import SEED_PORTFOLIO_SCHEMA
from .simulated_reliability_v1 import (
    SimulatedReliabilityError,
    build_direct_ledger,
    build_graph_ledger,
)


ROUTING_SCHEMA = "lolla.residual_challenge_seed_graph_routing.v1"
RESULT_SCHEMA = "lolla.residual_seed_graph_recall.v1"


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _hash(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def build_residual_seed_graph_recall_v1(
    *,
    seed_portfolio: Mapping[str, Any],
    routing_contract: Mapping[str, Any],
    knowledge_graph: Mapping[str, Any],
    relationship_graph: Mapping[str, Any] | Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    if seed_portfolio.get("schema_version") != SEED_PORTFOLIO_SCHEMA:
        raise SimulatedReliabilityError("invalid residual seed portfolio")
    if routing_contract.get("schema_version") != ROUTING_SCHEMA:
        raise SimulatedReliabilityError("invalid residual seed routing contract")
    kind_models = routing_contract.get("seed_kind_models")
    if not isinstance(kind_models, Mapping) or set(kind_models) != CANDIDATE_KINDS:
        raise SimulatedReliabilityError("residual seed routing kind coverage is incomplete")
    models = knowledge_graph.get("models")
    if not isinstance(models, Mapping) or not models:
        raise SimulatedReliabilityError("canonical model registry is invalid")
    canonical_ids = set(models)
    normalized_kind_models: dict[str, list[str]] = {}
    for kind in sorted(CANDIDATE_KINDS):
        values = kind_models[kind]
        if not isinstance(values, list):
            raise SimulatedReliabilityError("residual seed model mapping is invalid")
        model_ids = sorted({str(value).strip() for value in values})
        if not model_ids or any(not value for value in model_ids) or set(model_ids) - canonical_ids:
            raise SimulatedReliabilityError("residual seed mapping contains noncanonical models")
        normalized_kind_models[kind] = model_ids
    policy = routing_contract.get("selection_policy", {})
    if (
        policy.get("coverage_used_for_admission") is not False
        or policy.get("candidate_deletion") is not False
        or policy.get("semantic_applicability_decision") is not False
    ):
        raise SimulatedReliabilityError("residual seed routing policy permits semantic filtering")
    active_cap = policy.get("direct_active_cap")
    relation_slots = policy.get("graph_relation_slots")
    if not isinstance(active_cap, int) or active_cap < 1:
        raise SimulatedReliabilityError("residual direct cap is invalid")
    if not isinstance(relation_slots, list) or not relation_slots:
        raise SimulatedReliabilityError("residual graph slot policy is invalid")

    items = seed_portfolio.get("portfolio_items")
    if not isinstance(items, list):
        raise SimulatedReliabilityError("residual seed items are invalid")
    route_ids = []
    route_mapping: dict[str, list[str]] = {}
    custody = []
    seen_candidates: set[str] = set()
    for item in items:
        candidate_id = item.get("candidate_id")
        kind = item.get("candidate_kind")
        coverage = item.get("joint_coverage")
        tier = item.get("portfolio_tier")
        if (
            not isinstance(candidate_id, str)
            or not candidate_id
            or candidate_id in seen_candidates
            or kind not in CANDIDATE_KINDS
            or not isinstance(coverage, str)
            or not isinstance(tier, str)
        ):
            raise SimulatedReliabilityError("invalid residual seed graph identity")
        seen_candidates.add(candidate_id)
        route_id = "residual_seed:" + candidate_id
        route_ids.append(route_id)
        route_mapping[route_id] = normalized_kind_models[kind]
        custody.append(
            {
                "seed_route_id": route_id,
                "candidate_id": candidate_id,
                "candidate_kind": kind,
                "joint_coverage": coverage,
                "portfolio_tier": tier,
                "coverage_used_for_graph_admission": False,
            }
        )
    direct = build_direct_ledger(
        unresolved_mechanism_ids=route_ids,
        mechanism_seed_models=route_mapping,
        canonical_model_ids=canonical_ids,
        active_cap=active_cap,
    )
    graph = build_graph_ledger(
        direct_ledger=direct,
        relation_graph=relationship_graph,
        canonical_model_ids=canonical_ids,
        slot_order=relation_slots,
    )
    active_by_route = {route_id: [] for route_id in route_ids}
    reserve_by_route = {route_id: [] for route_id in route_ids}
    for row in direct["active_candidates"]:
        for route_id in row["recalled_by_mechanism_ids"]:
            active_by_route[route_id].append(row["model_id"])
    for row in direct["reserve_candidates"]:
        for route_id in row["recalled_by_mechanism_ids"]:
            reserve_by_route[route_id].append(row["model_id"])
    for row in custody:
        route_id = row["seed_route_id"]
        row["direct_active_model_ids"] = sorted(active_by_route[route_id])
        row["direct_reserve_model_ids"] = sorted(reserve_by_route[route_id])
        if not row["direct_active_model_ids"] and not row["direct_reserve_model_ids"]:
            raise SimulatedReliabilityError("residual seed disappeared from deterministic recall")
    result = {
        "schema_version": RESULT_SCHEMA,
        "status": "all_residual_seeds_recalled_without_coverage_gate",
        "case_id": seed_portfolio["case_id"],
        "seed_custody": custody,
        "direct_ledger": direct,
        "graph_ledger": graph,
        "counts": {
            "seed_routes": len(route_ids),
            "covered_seed_routes": sum(row["joint_coverage"] == "operationalized" for row in custody),
            "direct_active_candidates": len(direct["active_candidates"]),
            "direct_reserve_candidates": len(direct["reserve_candidates"]),
            "graph_active_candidates": len(graph["active_candidates"]),
            "graph_reserve_candidates": len(graph["reserve_candidates"]),
        },
        "boundary": {
            "every_seed_graph_recall_eligible": True,
            "joint_coverage_preserved_as_metadata": True,
            "joint_coverage_used_for_admission": False,
            "portfolio_tier_used_for_admission": False,
            "deterministic_semantic_inference": False,
            "probabilistic_applicability_filter": False,
            "candidate_deletion": False,
            "legacy_direct_ledger_unresolved_field_is_route_identity_not_semantic_claim": True,
            "graph_recall_is_not_relevance_proof": True,
            "fresh_consumer_disposition_required": True,
            "runtime_effect": "none",
        },
    }
    result["result_sha256"] = _hash(result)
    return result
