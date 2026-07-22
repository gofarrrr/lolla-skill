"""Candidate-only complete custody for the frozen constitutional portfolio.

This projection records the exact bounded scope and every exact one-hop path
inside that scope. It is not imported by the live pipeline, reasoner, receipt,
or Decision Trail and cannot change active selection.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
import hashlib
import json
from typing import Any

from .constitutional_pressure_survival import (
    build_constitutional_graph_survival_from_snapshot,
)
from .constitutional_pressure_planner import ConstitutionalPressurePlanner
from .published_knowledge_substrate import PublishedKnowledgeSnapshot, PublishedRelation


SCHEMA_VERSION = "lolla.prospective_constitutional_portfolio_custody.v1"


class ProspectivePortfolioCustodyError(ValueError):
    pass


def build_prospective_portfolio_custody(
    *,
    candidates: Sequence[Mapping[str, Any]],
    substrate: PublishedKnowledgeSnapshot,
    max_serialized_paths: int | None = None,
) -> dict[str, Any]:
    """Describe the current policy completely without connecting it live."""

    if max_serialized_paths is not None and max_serialized_paths < 0:
        raise ProspectivePortfolioCustodyError("max_serialized_paths must be nonnegative")

    planner = ConstitutionalPressurePlanner()
    plan = planner.plan(candidates=candidates, substrate=substrate)
    live_portfolio = build_constitutional_graph_survival_from_snapshot(
        candidates=candidates,
        substrate=substrate,
        planner=planner,
    )
    direct_active_rows = list(plan.direct_ledger.get("active_candidates", []))
    direct_reserve_rows = list(plan.direct_ledger.get("reserve_candidates", []))
    graph_active_rows = list(plan.graph_ledger.get("active_candidates", []))
    graph_reserve_rows = list(plan.graph_ledger.get("reserve_candidates", []))
    expanded_seed_ids = [str(row["model_id"]) for row in direct_active_rows]
    direct_active_set = set(expanded_seed_ids)
    graph_active_by_target = {str(row["model_id"]): row for row in graph_active_rows}
    graph_reserve_by_target = {str(row["model_id"]): row for row in graph_reserve_rows}

    relation_by_identity = {
        (
            relation.source_model_id,
            relation.target_model_id,
            relation.edge_type,
        ): relation
        for relation in substrate.relations
    }
    eligible_relations: list[PublishedRelation] = []
    for raw in plan.graph_ledger.get("all_eligible_edges", []):
        identity = (
            str(raw.get("source_model_id", "")),
            str(raw.get("target_model_id", "")),
            str(raw.get("edge_type", "")),
        )
        relation = relation_by_identity.get(identity)
        if relation is None:
            raise ProspectivePortfolioCustodyError(
                f"planner edge has no published relation identity: {identity}"
            )
        eligible_relations.append(relation)

    by_target: dict[str, list[PublishedRelation]] = {}
    for relation in eligible_relations:
        by_target.setdefault(relation.target_model_id, []).append(relation)

    remaining_path_budget = (
        len(eligible_relations)
        if max_serialized_paths is None
        else max_serialized_paths
    )
    enumerated_targets: list[dict[str, Any]] = []
    total_serialized_paths = 0
    graph_active_additional_paths = 0
    for target_model_id in sorted(by_target):
        exact_relations = by_target[target_model_id]
        if target_model_id in direct_active_set:
            disposition = "reserve_duplicate_of_direct_active"
            active_row = None
            reserve_row = graph_reserve_by_target.get(target_model_id)
        elif target_model_id in graph_active_by_target:
            disposition = "active_graph_slot"
            active_row = graph_active_by_target[target_model_id]
            reserve_row = None
        else:
            disposition = "reserve_graph_capacity"
            active_row = None
            reserve_row = graph_reserve_by_target.get(target_model_id)
        if active_row is None and reserve_row is None:
            raise ProspectivePortfolioCustodyError(
                f"enumerated graph target has no active or reserve disposition: {target_model_id}"
            )

        admission_relation: PublishedRelation | None = None
        selected_relation_slot = ""
        if active_row is not None:
            admission = active_row.get("admission_edge")
            if not isinstance(admission, Mapping):
                raise ProspectivePortfolioCustodyError(
                    f"active target has no admission edge: {target_model_id}"
                )
            admission_identity = (
                str(admission.get("source_model_id", "")),
                str(admission.get("target_model_id", "")),
                str(admission.get("edge_type", "")),
            )
            admission_relation = relation_by_identity.get(admission_identity)
            if admission_relation is None:
                raise ProspectivePortfolioCustodyError(
                    f"active admission edge is not published: {admission_identity}"
                )
            selected_relation_slot = str(active_row.get("selected_relation_slot", ""))
            graph_active_additional_paths += len(exact_relations) - 1

        serialized_count = min(len(exact_relations), remaining_path_budget)
        serialized_relations = exact_relations[:serialized_count]
        remaining_path_budget -= serialized_count
        omitted_count = len(exact_relations) - serialized_count
        total_serialized_paths += serialized_count
        enumerated_targets.append(
            {
                "target_model_id": target_model_id,
                "disposition": disposition,
                "selected_relation_slot": selected_relation_slot,
                "admission_path": (
                    _path_payload(admission_relation)
                    if admission_relation is not None
                    else None
                ),
                "provenance_paths": [
                    _path_payload(relation) for relation in serialized_relations
                ],
                "path_coverage": {
                    "status": "complete" if omitted_count == 0 else "partial",
                    "exact_path_count": len(exact_relations),
                    "serialized_path_count": serialized_count,
                    "omitted_path_count": omitted_count,
                    "partial_reason": (
                        "max_serialized_paths_safety_bound"
                        if omitted_count
                        else ""
                    ),
                },
                "semantic_rejection_performed": False,
            }
        )

    total_path_count = len(eligible_relations)
    omitted_path_count = total_path_count - total_serialized_paths
    graph_coverage = "complete" if omitted_path_count == 0 else "partial"
    live_active_identity_order = [
        {
            "pressure_id": str(row["pressure_id"]),
            "model_id": str(row["model_id"]),
            "candidate_origin": str(row["candidate_origin"]),
        }
        for row in live_portfolio["active_pressure_items"]
    ]
    planned_active_identity_order = [
        {
            "pressure_id": f"constitutional_graph_pressure::direct_seed::{row['model_id']}",
            "model_id": str(row["model_id"]),
            "candidate_origin": "direct_seed",
        }
        for row in direct_active_rows
    ] + [
        {
            "pressure_id": f"constitutional_graph_pressure::graph_expansion::{row['model_id']}",
            "model_id": str(row["model_id"]),
            "candidate_origin": "graph_expansion",
        }
        for row in graph_active_rows
    ]
    active_equivalent = live_active_identity_order == planned_active_identity_order
    if not active_equivalent:
        raise ProspectivePortfolioCustodyError(
            "prospective custody changed live active identities or order"
        )

    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": "complete" if graph_coverage == "complete" else "partial",
        "candidate_only": True,
        "live_reasoner_connected": False,
        "live_receipt_connected": False,
        "decision_trail_connected": False,
        "provider_calls": 0,
        "policy_identity": {
            "policy_id": plan.policy.policy_id,
            "version": plan.policy.version,
            "sha256": plan.policy_sha256,
        },
        "substrate_identity": {
            "release_id": plan.substrate_release_id,
            "release_identity": _json_value(substrate.release_identity),
        },
        "scope": {
            "expansion_seed_rule": "direct_active_only",
            "direction": "outgoing_authored_relations",
            "hop_depth": 1,
            "allowed_relation_types": list(plan.policy.graph_relation_slots),
            "expanded_direct_active_seed_ids": expanded_seed_ids,
            "unexpanded_direct_reserve_count": len(direct_reserve_rows),
            "safety_path_bound": max_serialized_paths,
        },
        "unexpanded_direct_reserve": [
            {
                "model_id": str(row["model_id"]),
                "disposition": "direct_capacity_reserve_unexpanded",
                "neighborhood_status": "not_enumerated_by_current_policy",
                "neighborhood": None,
                "semantic_rejection_performed": False,
                "reactivation_condition": str(row["reactivation_condition"]),
            }
            for row in direct_reserve_rows
        ],
        "enumerated_graph_targets": enumerated_targets,
        "path_accounting": {
            "enumerated_target_count": len(enumerated_targets),
            "exact_path_count": total_path_count,
            "serialized_path_count": total_serialized_paths,
            "omitted_path_count": omitted_path_count,
            "graph_active_target_count": len(graph_active_rows),
            "graph_active_additional_nonadmission_path_count": (
                graph_active_additional_paths
            ),
            "partial_reason": (
                "max_serialized_paths_safety_bound"
                if omitted_path_count
                else ""
            ),
        },
        "coverage": {
            "substrate": "complete",
            "direct_allocation": "complete",
            "expansion_seed_scope": "complete",
            "unexpanded_direct_reserve": "complete",
            "graph_target_enumeration": "complete",
            "target_dispositions": "complete",
            "exact_path_serialization": graph_coverage,
            "live_active_equivalence": "complete",
        },
        "live_equivalence": {
            "status": "complete",
            "active_identities_and_order_equal": active_equivalent,
            "live_portfolio_sha256": live_portfolio["portfolio_sha256"],
            "active_identity_order": live_active_identity_order,
        },
        "input_custody": {
            "duplicate_candidates": [dict(row) for row in plan.duplicate_candidates],
            "malformed_candidates": [dict(row) for row in plan.malformed_candidates],
        },
        "non_claims": [
            "multiple_paths_are_not_relevance_proof",
            "convergence_is_not_causation",
            "reserve_is_not_semantic_rejection",
            "candidate_custody_does_not_change_live_pressure",
        ],
    }
    payload["candidate_sha256"] = _sha(payload)
    validate_prospective_portfolio_custody(payload)
    return payload


def validate_prospective_portfolio_custody(payload: Mapping[str, Any]) -> None:
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ProspectivePortfolioCustodyError("prospective custody schema is invalid")
    supplied_hash = str(payload.get("candidate_sha256", ""))
    material = {key: value for key, value in payload.items() if key != "candidate_sha256"}
    if not supplied_hash or supplied_hash != _sha(material):
        raise ProspectivePortfolioCustodyError("prospective custody hash is invalid")
    if payload.get("candidate_only") is not True:
        raise ProspectivePortfolioCustodyError("prospective custody must remain candidate-only")
    if any(
        payload.get(field) is not False
        for field in (
            "live_reasoner_connected",
            "live_receipt_connected",
            "decision_trail_connected",
        )
    ):
        raise ProspectivePortfolioCustodyError("prospective custody is connected live")
    scope = payload.get("scope")
    if not isinstance(scope, Mapping):
        raise ProspectivePortfolioCustodyError("prospective custody scope is missing")
    if (
        scope.get("expansion_seed_rule") != "direct_active_only"
        or scope.get("direction") != "outgoing_authored_relations"
        or scope.get("hop_depth") != 1
    ):
        raise ProspectivePortfolioCustodyError("prospective custody scope drifted")
    targets = payload.get("enumerated_graph_targets")
    if not isinstance(targets, list):
        raise ProspectivePortfolioCustodyError("enumerated graph targets are missing")
    valid_dispositions = {
        "active_graph_slot",
        "reserve_graph_capacity",
        "reserve_duplicate_of_direct_active",
    }
    if any(row.get("disposition") not in valid_dispositions for row in targets):
        raise ProspectivePortfolioCustodyError("graph target disposition is invalid")
    accounting = payload.get("path_accounting")
    if not isinstance(accounting, Mapping):
        raise ProspectivePortfolioCustodyError("path accounting is missing")
    serialized = sum(
        len(row.get("provenance_paths", []))
        for row in targets
        if isinstance(row, Mapping)
    )
    if serialized != accounting.get("serialized_path_count"):
        raise ProspectivePortfolioCustodyError("serialized path accounting drifted")
    if accounting.get("exact_path_count") != (
        accounting.get("serialized_path_count", 0)
        + accounting.get("omitted_path_count", 0)
    ):
        raise ProspectivePortfolioCustodyError("exact path accounting drifted")
    if payload.get("status") == "complete" and accounting.get("omitted_path_count") != 0:
        raise ProspectivePortfolioCustodyError("complete custody has omitted paths")
    if payload.get("status") == "partial" and not accounting.get("partial_reason"):
        raise ProspectivePortfolioCustodyError("partial custody lacks a reason")
    if payload.get("live_equivalence", {}).get("active_identities_and_order_equal") is not True:
        raise ProspectivePortfolioCustodyError("live active identity equivalence failed")


def _path_payload(relation: PublishedRelation) -> dict[str, Any]:
    custody = relation.custody
    return {
        "relation_id": relation.relation_id,
        "source_model_id": relation.source_model_id,
        "target_model_id": relation.target_model_id,
        "edge_type": relation.edge_type,
        "direction": "outgoing_authored_relation",
        "hop_count": 1,
        "source_order": relation.source_order,
        "compiled_pointer": relation.compiled_pointer,
        "authoring_pointer": (
            {
                "path": custody.authoring_path,
                "family": custody.authoring_family,
                "item_index": custody.authoring_item_index,
            }
            if custody is not None
            else None
        ),
        "source_custody": (
            {
                "path": custody.source_path,
                "sha256": custody.source_sha256,
                "bytes": custody.source_bytes,
                "source_anchor_state": custody.source_anchor_state,
                "exact_span": dict(custody.exact_span) if custody.exact_span else None,
            }
            if custody is not None
            else None
        ),
    }


def _sha(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _json_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    return value
