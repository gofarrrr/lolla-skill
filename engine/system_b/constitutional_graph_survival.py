"""Bounded live custody for deterministic Lane-2 graph pressure.

The probabilistic verifier remains useful as interpretation telemetry, but it
has no authority over this portfolio.  Deterministic code owns canonical
identity, one-hop graph provenance, active/reserve bounds, and disposition
completeness.  A later reasoner owns apply/reject/park judgment.
"""
from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import Any

from .canonical_model_selection import build_challenge_cards
from .simulated_reliability_v1 import build_direct_ledger, build_graph_ledger


SCHEMA_VERSION = "lolla.constitutional_graph_survival.v1"
LEDGER_SCHEMA_VERSION = "lolla.constitutional_graph_survival_ledger.v1"
VALIDATION_SCHEMA_VERSION = "lolla.constitutional_graph_survival_ledger_validation.v1"
DIRECT_ACTIVE_CAP = 6
GRAPH_RELATION_SLOTS = ("antagonist", "tension", "ally")
# Frozen after an exhaustive provider-free sliding-window measurement across
# all 163 possible 60-ID windows in the current 222-model registry. Observed
# maxima were 4,690 active and 9,510 reserve estimated tokens.
ACTIVE_PACKET_MAX_ESTIMATED_TOKENS = 6000
RESERVE_PACKET_MAX_ESTIMATED_TOKENS = 12000
ALLOWED_DISPOSITIONS = frozenset({"apply", "reject", "park"})


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _text(value: Any) -> str:
    return str(value or "").strip()


def _edges(relationship_graph: Mapping[str, Any] | Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    raw = relationship_graph.get("edges", []) if isinstance(relationship_graph, Mapping) else relationship_graph
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)):
        return []
    return [item for item in raw if isinstance(item, Mapping)]


def _edge_ref(
    edge: Mapping[str, Any],
    relationship_edges: Sequence[Mapping[str, Any]],
) -> str:
    keys = ("source_model_id", "target_model_id", "edge_type")
    for index, candidate in enumerate(relationship_edges):
        if all(_text(candidate.get(key)) == _text(edge.get(key)) for key in keys):
            return f"data/relationship_graph.json#/{index}"
    return ""


def _estimated_tokens(value: Any) -> int:
    encoded = _canonical(value).encode("utf-8")
    return (len(encoded) + 3) // 4


def _pressure_item(
    row: Mapping[str, Any],
    *,
    challenge_cards: Mapping[str, Mapping[str, Any]],
    direct_source_index: Mapping[str, int],
    relationship_edges: Sequence[Mapping[str, Any]],
    index: int,
) -> dict[str, Any]:
    model_id = _text(row.get("model_id"))
    card = dict(challenge_cards[model_id])
    origin = _text(row.get("candidate_origin"))
    graph_path = row.get("admission_edge") if isinstance(row.get("admission_edge"), Mapping) else {}
    source_refs = [f"data/knowledge_graph.json#/models/{model_id}"]
    if origin == "direct_seed":
        source_refs.append(
            f"result.json#/audit_summary/companion_candidates/{direct_source_index[model_id]}"
        )
    elif graph_path:
        relation_ref = _edge_ref(graph_path, relationship_edges)
        if relation_ref:
            source_refs.append(relation_ref)
    return {
        "pressure_id": f"constitutional_graph_pressure::{origin}::{model_id}",
        "model_id": model_id,
        "display_name": _text(card.get("display_name")) or model_id,
        "candidate_origin": origin,
        "admission_rank": int(row.get("admission_rank", index + 1) or index + 1),
        "recalled_by_mechanism_ids": list(row.get("recalled_by_mechanism_ids") or []),
        "selected_relation_slot": _text(row.get("selected_relation_slot")),
        "graph_path": dict(graph_path),
        "strongest_plausible_application": _text(card.get("challenge_when")),
        "concrete_test": _text(card.get("pressure_question")),
        "force_boundary": _text(card.get("do_not_apply_when")),
        "ignore_boundary": (
            "Do not ignore this pressure without stating why its challenge condition "
            "fails here or what evidence would justify reopening it."
        ),
        "source_refs": source_refs,
        "consumer_visibility": "full_active_pressure_item",
        "consumer_locator": (
            f"result.json#/constitutional_graph_survival/active_pressure_items/{index}"
        ),
        "portfolio_status": "intentionally_noisy_pressure_hypothesis",
    }


def build_constitutional_graph_survival(
    *,
    candidates: Sequence[Mapping[str, Any]],
    knowledge_graph: Mapping[str, Any],
    relationship_graph: Mapping[str, Any] | Sequence[Mapping[str, Any]],
    direct_active_cap: int = DIRECT_ACTIVE_CAP,
    relation_slots: Sequence[str] = GRAPH_RELATION_SLOTS,
) -> dict[str, Any]:
    """Build a bounded active portfolio plus complete compact reserve."""

    models = knowledge_graph.get("models")
    if not isinstance(models, Mapping) or not models:
        raise ValueError("canonical model registry is unavailable")
    canonical_ids = set(models)
    if direct_active_cap < 1:
        raise ValueError("direct_active_cap must be positive")

    malformed: list[dict[str, Any]] = []
    duplicates: list[dict[str, Any]] = []
    canonical_candidates: list[dict[str, Any]] = []
    first_index: dict[str, int] = {}
    for index, raw in enumerate(candidates):
        model_id = _text(raw.get("model_id")) if isinstance(raw, Mapping) else ""
        if not model_id or model_id not in canonical_ids:
            malformed.append(
                {
                    "input_index": index,
                    "raw_model_id": model_id,
                    "custody_status": "malformed_or_noncanonical_before_admission",
                    "semantic_rejection_performed": False,
                }
            )
            continue
        if model_id in first_index:
            duplicates.append(
                {
                    "model_id": model_id,
                    "input_index": index,
                    "first_input_index": first_index[model_id],
                    "custody_status": "duplicate_of_direct_candidate",
                    "semantic_rejection_performed": False,
                }
            )
            continue
        first_index[model_id] = index
        canonical_candidates.append(dict(raw))

    mechanism_ids = [
        f"lane2_recall_rank:{index:03d}" for index in range(len(canonical_candidates))
    ]
    mechanism_models = {
        mechanism_id: [_text(candidate.get("model_id"))]
        for mechanism_id, candidate in zip(mechanism_ids, canonical_candidates)
    }
    direct = build_direct_ledger(
        unresolved_mechanism_ids=mechanism_ids,
        mechanism_seed_models=mechanism_models,
        canonical_model_ids=canonical_ids,
        active_cap=direct_active_cap,
    )
    graph = build_graph_ledger(
        direct_ledger=direct,
        relation_graph=relationship_graph,
        canonical_model_ids=canonical_ids,
        slot_order=tuple(relation_slots),
    )
    relationship_edges = _edges(relationship_graph)
    direct_source_index = {
        _text(candidate.get("model_id")): first_index[_text(candidate.get("model_id"))]
        for candidate in canonical_candidates
    }
    active_rows = [*direct["active_candidates"], *graph["active_candidates"]]
    challenge_cards = build_challenge_cards(models) if active_rows else {}
    active_items = [
        _pressure_item(
            row,
            challenge_cards=challenge_cards,
            direct_source_index=direct_source_index,
            relationship_edges=relationship_edges,
            index=index,
        )
        for index, row in enumerate(active_rows)
    ]

    direct_reserve = []
    for row in direct["reserve_candidates"]:
        model_id = row["model_id"]
        direct_reserve.append(
            {
                **dict(row),
                "source_refs": [
                    f"result.json#/audit_summary/companion_candidates/{direct_source_index[model_id]}",
                    f"data/knowledge_graph.json#/models/{model_id}",
                ],
            }
        )
    graph_reserve = []
    for row in graph["reserve_candidates"]:
        provenance = list(row.get("graph_provenance") or [])
        refs = [
            ref
            for ref in (_edge_ref(edge, relationship_edges) for edge in provenance)
            if ref
        ]
        graph_reserve.append(
            {
                "model_id": row["model_id"],
                "candidate_origin": row["candidate_origin"],
                "recalled_by_mechanism_ids": list(row["recalled_by_mechanism_ids"]),
                "custody_status": row["custody_status"],
                "semantic_rejection_performed": False,
                "reactivation_condition": row["reactivation_condition"],
                "graph_provenance_refs": refs,
                "graph_edge_types": sorted({_text(edge.get("edge_type")) for edge in provenance}),
                "source_refs": [
                    f"data/knowledge_graph.json#/models/{row['model_id']}",
                    *refs,
                ],
            }
        )

    disposition_items = [
        {
            "pressure_id": item["pressure_id"],
            "model_id": item["model_id"],
            "candidate_origin": item["candidate_origin"],
            "consumer_locator": item["consumer_locator"],
            "disposition": "",
            "strongest_plausible_application": "",
            "attempted_application_condition": "",
            "why": "",
            "failed_condition": "",
            "reopen_condition": "",
            "visible_effect": "",
            "private_guardrail": "",
            "risk_if_forced": "",
            "risk_if_ignored": "",
        }
        for item in active_items
    ]
    ledger_skeleton = {
        "schema_version": LEDGER_SCHEMA_VERSION,
        "status": "pending",
        "portfolio_sha256": "",
        "items": disposition_items,
        "notes": [
            "Private custody only. Every active candidate requires apply, reject, or park."
        ],
    }
    reserve = {
        "direct_capacity_reserve": direct_reserve,
        "graph_edge_reserve": graph_reserve,
        "duplicate_candidates": duplicates,
        "malformed_candidates": malformed,
    }
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": "active" if active_items else "stand_down",
        "active_pressure_items": active_items,
        "reserve_custody": reserve,
        "path_counts": {
            "direct_active": len(direct["active_candidates"]),
            "direct_cap_reserve": len(direct_reserve),
            "graph_active": len(graph["active_candidates"]),
            "graph_cap_or_duplicate_reserve": len(graph_reserve),
            "duplicate_input": len(duplicates),
            "malformed_input": len(malformed),
        },
        "selection_contract": {
            "direct_active_cap": direct_active_cap,
            "direct_operation": "bounded_recall_order_no_verifier_gate",
            "graph_relation_slots": list(relation_slots),
            "graph_operation": "one_exact_id_per_declared_relation_slot",
            "probabilistic_applicability_gate": False,
            "verifier_fields_used_for_survival": [],
            "candidate_deletion": False,
        },
        "consumer_delivery": {
            "active_material_location": "result.json#/constitutional_graph_survival/active_pressure_items",
            "reserve_material_location": "result.json#/constitutional_graph_survival/reserve_custody",
            "every_active_item_fully_visible_or_exactly_resolvable": True,
            "reserve_requires_current_disposition": False,
            "active_requires_apply_reject_or_park": True,
            "public_use_required": False,
        },
        "fan_in_measurement": {},
        "disposition_ledger_skeleton": ledger_skeleton,
        "non_claims": [
            "graph_recall_is_not_relevance_proof",
            "active_admission_is_not_best_model_selection",
            "reserve_status_is_not_semantic_rejection",
            "receipt_is_not_a_quality_score",
        ],
    }
    active_tokens = _estimated_tokens(
        {
            "active_pressure_items": active_items,
            "disposition_ledger_skeleton": payload["disposition_ledger_skeleton"],
        }
    )
    reserve_tokens = _estimated_tokens(reserve)
    payload["fan_in_measurement"] = {
        "active_item_count": len(active_items),
        "reserve_candidate_count": len(direct_reserve) + len(graph_reserve),
        "active_estimated_tokens": active_tokens,
        "reserve_estimated_tokens": reserve_tokens,
        "active_max_estimated_tokens": ACTIVE_PACKET_MAX_ESTIMATED_TOKENS,
        "reserve_max_estimated_tokens": RESERVE_PACKET_MAX_ESTIMATED_TOKENS,
        "active_within_frozen_bound": active_tokens <= ACTIVE_PACKET_MAX_ESTIMATED_TOKENS,
        "reserve_within_frozen_bound": reserve_tokens <= RESERVE_PACKET_MAX_ESTIMATED_TOKENS,
        "estimation_method": "compact_json_utf8_bytes_divided_by_4_ceiling",
    }
    # The hash covers the final portfolio with the self-reference slot blank.
    # The same value is then copied into the top level and ledger skeleton.
    hash_material = json.loads(json.dumps(payload))
    hash_material["disposition_ledger_skeleton"]["portfolio_sha256"] = ""
    payload_hash = _sha(hash_material)
    payload["portfolio_sha256"] = payload_hash
    payload["disposition_ledger_skeleton"]["portfolio_sha256"] = payload_hash
    validate_constitutional_graph_survival(payload)
    return payload


def validate_constitutional_graph_survival(payload: Mapping[str, Any]) -> None:
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("constitutional graph survival schema is invalid")
    observed_hash = _text(payload.get("portfolio_sha256"))
    hash_material = json.loads(json.dumps(payload))
    hash_material.pop("portfolio_sha256", None)
    skeleton_for_hash = hash_material.get("disposition_ledger_skeleton")
    if isinstance(skeleton_for_hash, dict):
        skeleton_for_hash["portfolio_sha256"] = ""
    if not observed_hash or observed_hash != _sha(hash_material):
        raise ValueError("constitutional graph survival portfolio hash is invalid")
    active = payload.get("active_pressure_items")
    if not isinstance(active, list):
        raise ValueError("active pressure items must be a list")
    ids = [_text(item.get("pressure_id")) for item in active if isinstance(item, Mapping)]
    if len(ids) != len(active) or any(not value for value in ids) or len(ids) != len(set(ids)):
        raise ValueError("active pressure identity custody is invalid")
    canonical_ids = [_text(item.get("model_id")) for item in active]
    if any(not value for value in canonical_ids) or len(canonical_ids) != len(set(canonical_ids)):
        raise ValueError("active canonical model identities are invalid")
    for index, item in enumerate(active):
        expected = f"result.json#/constitutional_graph_survival/active_pressure_items/{index}"
        if item.get("consumer_locator") != expected:
            raise ValueError("active consumer locator is invalid")
        for field in (
            "strongest_plausible_application",
            "concrete_test",
            "force_boundary",
            "ignore_boundary",
        ):
            if not _text(item.get(field)):
                raise ValueError(f"active pressure item lacks {field}")
        if not item.get("source_refs"):
            raise ValueError("active pressure item lacks exact source references")
    reserve = payload.get("reserve_custody")
    if not isinstance(reserve, Mapping):
        raise ValueError("reserve custody is invalid")
    direct_ids = set(canonical_ids)
    direct_ids.update(
        _text(item.get("model_id"))
        for item in reserve.get("direct_capacity_reserve", [])
        if isinstance(item, Mapping)
    )
    if any(not value for value in direct_ids):
        raise ValueError("direct reserve identity is invalid")
    fan_in = payload.get("fan_in_measurement")
    if not isinstance(fan_in, Mapping) or not fan_in.get("active_within_frozen_bound") or not fan_in.get("reserve_within_frozen_bound"):
        raise ValueError("constitutional graph survival exceeds frozen fan-in bounds")
    skeleton = payload.get("disposition_ledger_skeleton")
    if not isinstance(skeleton, Mapping):
        raise ValueError("disposition ledger skeleton is missing")
    if skeleton.get("portfolio_sha256") != observed_hash:
        raise ValueError("disposition skeleton portfolio hash is invalid")
    if [item.get("pressure_id") for item in skeleton.get("items", [])] != ids:
        raise ValueError("disposition skeleton does not mirror active pressure")


def validate_constitutional_graph_survival_ledger(
    ledger: Mapping[str, Any],
    *,
    portfolio: Mapping[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    if ledger.get("schema_version") != LEDGER_SCHEMA_VERSION:
        errors.append("schema_version is invalid")
    if ledger.get("status") != "completed":
        errors.append("status must be completed")
    if ledger.get("portfolio_sha256") != portfolio.get("portfolio_sha256"):
        errors.append("portfolio_sha256 does not match")
    if set(ledger) != {"schema_version", "status", "portfolio_sha256", "items", "notes"}:
        errors.append("ledger top-level fields must exactly match the skeleton")
    expected = portfolio.get("disposition_ledger_skeleton", {}).get("items", [])
    observed = ledger.get("items")
    if not isinstance(observed, list):
        observed = []
        errors.append("items must be a list")
    if len(observed) != len(expected):
        errors.append("items must cover every active pressure exactly once")
    counts: dict[str, int] = {}
    immutable = {"pressure_id", "model_id", "candidate_origin", "consumer_locator"}
    expected_fields = set(expected[0]) if expected else set()
    for index, item in enumerate(observed):
        prefix = f"items[{index}]"
        if not isinstance(item, Mapping):
            errors.append(f"{prefix} must be an object")
            continue
        if set(item) != expected_fields:
            errors.append(f"{prefix} fields must exactly match the skeleton")
            continue
        if index >= len(expected):
            continue
        for field in immutable:
            if item.get(field) != expected[index].get(field):
                errors.append(f"{prefix}.{field} must match consumer custody")
        disposition = _text(item.get("disposition"))
        if disposition not in ALLOWED_DISPOSITIONS:
            errors.append(f"{prefix}.disposition must be apply, reject, or park")
        else:
            counts[disposition] = counts.get(disposition, 0) + 1
        for field in (
            "strongest_plausible_application",
            "attempted_application_condition",
            "why",
            "risk_if_forced",
            "risk_if_ignored",
        ):
            if not _text(item.get(field)):
                errors.append(f"{prefix}.{field} is required")
        visible = _text(item.get("visible_effect"))
        private = _text(item.get("private_guardrail"))
        failed = _text(item.get("failed_condition"))
        reopen = _text(item.get("reopen_condition"))
        if disposition == "apply" and not (visible or private):
            errors.append(f"{prefix}.apply requires visible_effect or private_guardrail")
        if disposition == "reject" and not failed:
            errors.append(f"{prefix}.reject requires failed_condition")
        if disposition == "park" and not reopen:
            errors.append(f"{prefix}.park requires reopen_condition")
        if disposition in {"reject", "park"} and (visible or private):
            errors.append(f"{prefix}.{disposition} cannot claim an effect")
    expected_ids = [item.get("pressure_id") for item in expected]
    observed_ids = [item.get("pressure_id") for item in observed if isinstance(item, Mapping)]
    if observed_ids != expected_ids:
        errors.append("ledger pressure IDs must match packet order exactly")
    return {
        "schema_version": VALIDATION_SCHEMA_VERSION,
        "status": "valid" if not errors else "invalid",
        "active_pressure_count": len(expected),
        "disposition_counts": dict(sorted(counts.items())),
        "exact_pressure_id_coverage": observed_ids == expected_ids,
        "consumer_material_resolved": not any("consumer" in error for error in errors),
        "public_use_required": False,
        "errors": errors,
    }


def finalize_constitutional_graph_survival_ledger(
    result_payload: Mapping[str, Any],
    *,
    ledger: Mapping[str, Any] | None,
) -> dict[str, Any]:
    result = dict(result_payload)
    portfolio = result.get("constitutional_graph_survival")
    health = dict(result.get("run_health") or {})
    if not isinstance(portfolio, Mapping) or portfolio.get("status") != "active":
        validation = {
            "schema_version": VALIDATION_SCHEMA_VERSION,
            "status": "not_required",
            "active_pressure_count": 0,
            "disposition_counts": {},
            "exact_pressure_id_coverage": True,
            "consumer_material_resolved": True,
            "public_use_required": False,
            "errors": [],
        }
    elif ledger is None:
        validation = {
            "schema_version": VALIDATION_SCHEMA_VERSION,
            "status": "missing",
            "active_pressure_count": len(portfolio.get("active_pressure_items", [])),
            "disposition_counts": {},
            "exact_pressure_id_coverage": False,
            "consumer_material_resolved": False,
            "public_use_required": False,
            "errors": ["active constitutional graph pressure has no disposition ledger"],
        }
    else:
        validation = validate_constitutional_graph_survival_ledger(
            ledger,
            portfolio=portfolio,
        )
        result["constitutional_graph_survival_ledger"] = dict(ledger)
    result["constitutional_graph_survival_ledger_validation"] = validation
    health["constitutional_graph_survival_ledger"] = validation["status"]
    health["constitutional_graph_survival_disposition_counts"] = validation[
        "disposition_counts"
    ]
    result["run_health"] = health
    return result
