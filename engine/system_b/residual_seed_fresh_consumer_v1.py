"""Provider-free fresh-consumer handoff for residual-seed graph pressure.

The handoff keeps probabilistic coverage as receipt metadata.  It never uses
that metadata to suppress deterministic direct or graph recall.  A later fresh
reasoner must inspect every active candidate and may apply, reject, or park it.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import Any

from .residual_challenge_seed_v1 import SEED_PORTFOLIO_SCHEMA
from .residual_seed_graph_recall_v1 import RESULT_SCHEMA as RECALL_SCHEMA
from .simulated_reliability_v1 import (
    SimulatedReliabilityError,
    build_pressure_packet,
    compile_pressure_response,
    pressure_response_schema,
)


PACKET_SCHEMA = "lolla.residual_seed_fresh_consumer_input.v1"
RESULT_SCHEMA = "lolla.residual_seed_fresh_consumer_bundle.v1"


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _hash(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _without_hash(value: Mapping[str, Any], field: str) -> dict[str, Any]:
    return {key: item for key, item in value.items() if key != field}


def _seed_context(seed_portfolio: Mapping[str, Any], recall: Mapping[str, Any]) -> list[dict[str, Any]]:
    items = seed_portfolio.get("portfolio_items")
    custody = recall.get("seed_custody")
    if not isinstance(items, list) or not isinstance(custody, list):
        raise SimulatedReliabilityError("residual seed custody is invalid")
    by_id = {item.get("candidate_id"): item for item in items}
    if len(by_id) != len(items) or set(by_id) != {item.get("candidate_id") for item in custody}:
        raise SimulatedReliabilityError("residual seed and recall identities differ")
    context = []
    for row in custody:
        candidate_id = row["candidate_id"]
        source = by_id[candidate_id]
        if source.get("candidate_kind") != row.get("candidate_kind"):
            raise SimulatedReliabilityError("residual seed kind drifted")
        context.append(
            {
                "seed_route_id": row["seed_route_id"],
                "candidate_id": candidate_id,
                "candidate_kind": row["candidate_kind"],
                "challenge_question": source["challenge_question"],
                "claim_status": source["claim_status"],
                "source_evidence_ids": list(source["source_evidence_ids"]),
                "joint_coverage": row["joint_coverage"],
                "coverage_source_evidence_ids": list(source["coverage_source_evidence_ids"]),
                "coverage_role": "receipt_only_not_admission_or_suppression_authority",
                "direct_active_model_ids": list(row["direct_active_model_ids"]),
                "direct_reserve_model_ids": list(row["direct_reserve_model_ids"]),
            }
        )
    return sorted(context, key=lambda item: item["candidate_id"])


def _reserve_custody(recall: Mapping[str, Any]) -> dict[str, list[dict[str, Any]]]:
    direct = []
    for row in recall["direct_ledger"]["reserve_candidates"]:
        direct.append(
            {
                "model_id": row["model_id"],
                "candidate_origin": "direct_seed",
                "recalled_by_seed_route_ids": list(row["recalled_by_mechanism_ids"]),
                "custody_status": row["custody_status"],
                "semantic_rejection_performed": row["semantic_rejection_performed"],
                "reactivation_condition": row["reactivation_condition"],
            }
        )
    graph = []
    for row in recall["graph_ledger"]["reserve_candidates"]:
        graph.append(
            {
                "model_id": row["model_id"],
                "candidate_origin": "graph_expansion",
                "recalled_by_seed_route_ids": list(row["recalled_by_mechanism_ids"]),
                "graph_provenance": list(row["graph_provenance"]),
                "custody_status": row["custody_status"],
                "semantic_rejection_performed": row["semantic_rejection_performed"],
                "reactivation_condition": row["reactivation_condition"],
            }
        )
    return {
        "direct_reserve": sorted(direct, key=lambda item: item["model_id"]),
        "graph_reserve": sorted(graph, key=lambda item: item["model_id"]),
    }


def build_residual_seed_fresh_consumer_bundle_v1(
    *,
    case_id: str,
    conversation: str,
    seed_portfolio: Mapping[str, Any],
    recall: Mapping[str, Any],
    challenge_cards: Mapping[str, Mapping[str, Any]],
    source_refs: Sequence[Mapping[str, str]],
) -> dict[str, Any]:
    """Build one bounded fresh-consumer request without making a provider call."""

    if seed_portfolio.get("schema_version") != SEED_PORTFOLIO_SCHEMA:
        raise SimulatedReliabilityError("invalid residual seed portfolio")
    if recall.get("schema_version") != RECALL_SCHEMA:
        raise SimulatedReliabilityError("invalid residual graph recall")
    if case_id != seed_portfolio.get("case_id") or case_id != recall.get("case_id"):
        raise SimulatedReliabilityError("residual fresh-consumer case identity drifted")
    if recall.get("result_sha256") != _hash(_without_hash(recall, "result_sha256")):
        raise SimulatedReliabilityError("residual graph recall hash is invalid")
    boundary = recall.get("boundary", {})
    if (
        boundary.get("joint_coverage_used_for_admission") is not False
        or boundary.get("probabilistic_applicability_filter") is not False
        or boundary.get("candidate_deletion") is not False
    ):
        raise SimulatedReliabilityError("residual graph recall violates the hybrid boundary")

    direct_active = list(recall["direct_ledger"]["active_candidates"])
    graph_active = list(recall["graph_ledger"]["active_candidates"])
    candidates = [*direct_active, *graph_active]
    if not direct_active or not graph_active:
        raise SimulatedReliabilityError("corrected residual consumer requires direct and graph pressure")

    packet = build_pressure_packet(
        case_id=case_id,
        arm_id="graph_expanded_pressure",
        conversation=conversation,
        candidates=candidates,
        challenge_cards=challenge_cards,
        portfolio_ledger_refs=[
            {"ledger_type": "residual_seed_graph_recall", "sha256": recall["result_sha256"]},
            {"ledger_type": "direct", "sha256": recall["direct_ledger"]["ledger_sha256"]},
            {"ledger_type": "graph", "sha256": recall["graph_ledger"]["ledger_sha256"]},
        ],
        source_refs=source_refs,
    )
    packet["schema_version"] = PACKET_SCHEMA
    packet["residual_seed_context"] = _seed_context(seed_portfolio, recall)
    packet["reserve_custody"] = _reserve_custody(recall)
    packet["portfolio_structure"] = {
        "direct_active_count": len(direct_active),
        "graph_active_count": len(graph_active),
        "active_candidate_count": len(candidates),
        "direct_reserve_count": len(packet["reserve_custody"]["direct_reserve"]),
        "graph_reserve_count": len(packet["reserve_custody"]["graph_reserve"]),
        "active_selection_operation": "deterministic_cap_and_declared_relation_slots",
        "active_selection_is_semantic_ranking": False,
    }
    packet["instructions"].update(
        {
            "residual_challenge_is_question_not_case_fact": True,
            "coverage_metadata_may_suppress_pressure": False,
            "reserve_candidates_require_current_disposition": False,
            "reserve_status_is_semantic_rejection": False,
            "strongest_plausible_application_must_precede_fit_judgment": True,
        }
    )
    packet["boundary"].update(
        {
            "probabilistic_coverage_gate": False,
            "every_residual_seed_reaches_deterministic_recall": True,
            "all_active_direct_and_graph_candidates_preserved": True,
            "all_reserve_candidates_inspectable": True,
            "receipt_metadata_has_no_routing_authority": True,
        }
    )
    packet["packet_sha256"] = _hash(_without_hash(packet, "packet_sha256"))
    candidate_ids = [item["model_id"] for item in packet["pressure_portfolio"]]
    prompts = build_residual_seed_fresh_consumer_prompts_v1(packet)
    schema = pressure_response_schema(candidate_ids)
    bundle = {
        "schema_version": RESULT_SCHEMA,
        "status": "provider_free_corrected_fresh_consumer_handoff_pass",
        "case_id": case_id,
        "packet": packet,
        "prompts": prompts,
        "response_schema": schema,
        "call_policy": {
            "provider_calls_made": 0,
            "next_call_authorized": False,
            "maximum_future_calls_if_separately_authorized": 1,
            "maximum_future_provider_reported_cost_usd": 0.01,
            "preferred_testing_model": "google/gemini-3.1-flash-lite",
            "premium_testing_model_prohibited": "google/gemini-3.5-flash",
            "automatic_retries": 0,
            "fallback_models": 0,
            "response_healing": False,
        },
        "boundary": {
            "fresh_context_required": True,
            "full_authoritative_conversation_included": True,
            "active_pressure_requires_apply_reject_or_park": True,
            "mental_models_are_not_case_evidence": True,
            "strong_original_reasoning_may_survive_unchanged": True,
            "public_stand_down_allowed": True,
            "runtime_effect": "none",
            "production_authorization": False,
        },
    }
    bundle["bundle_sha256"] = _hash(bundle)
    return bundle


def build_residual_seed_fresh_consumer_prompts_v1(packet: Mapping[str, Any]) -> dict[str, str]:
    if packet.get("schema_version") != PACKET_SCHEMA:
        raise SimulatedReliabilityError("corrected residual fresh-consumer packet required")
    # The full reserve remains inspectable in the persisted packet, but it is not
    # an active semantic task.  Sending every reserve edge to the provider would
    # add cost and distraction without giving the consumer permission to use it.
    # The provider view therefore carries identities, counts, and ledger hashes;
    # exact reserve provenance stays in the packet referenced by packet_sha256.
    consumer_view = {
        key: value for key, value in packet.items() if key != "reserve_custody"
    }
    consumer_view["reserve_notice"] = {
        "direct_reserve_model_ids": [
            item["model_id"] for item in packet["reserve_custody"]["direct_reserve"]
        ],
        "graph_reserve_model_ids": [
            item["model_id"] for item in packet["reserve_custody"]["graph_reserve"]
        ],
        "exact_provenance_location": "persisted_packet.reserve_custody",
        "persisted_packet_sha256": packet["packet_sha256"],
        "current_disposition_required": False,
        "semantic_rejection_performed": False,
    }
    system = (
        "You are a fresh-context reasoner. Reconsider the full authoritative conversation "
        "using every active canonical mental-model candidate as intentionally noisy pressure. "
        "A residual challenge is a source-grounded question, not a fact. Deterministic or graph "
        "recall is not applicability proof. Coverage metadata is receipt evidence only and may "
        "not suppress a candidate. Preserve strong reasoning, reject noise freely, and do not "
        "invent facts or quantitative precision."
    )
    user = (
        "CORRECTED RESIDUAL-SEED FRESH-CONSUMER PACKET\n"
        + _canonical(consumer_view)
        + "\n\nInspect every active pressure candidate exactly once. First state its strongest "
        "plausible application; then apply, reject, or park it against exact conversation turns. "
        "Apply only when it materially reframes the reasoning or creates a concrete test, condition, "
        "alternative, uncertainty change, or reversal rule. Reject when the strongest application "
        "fails, naming the failed condition and the risk of forcing it. Park when evidence or timing "
        "is insufficient, naming the reopening condition. An applied lens must also retain a real "
        "falsifier. Do not disposition reserve candidates in this call; they are inspectable custody, "
        "not deleted or semantically rejected. Do not turn a mental model into evidence, confidence, "
        "or a risk level that the conversation did not earn. Then write a self-contained reconsidered "
        "answer containing only earned friction and a concise factual change summary. A valid result "
        "may preserve the original conclusion or publicly stand down if all pressure is noise."
    )
    return {
        "system_prompt": system,
        "user_prompt": user,
        "system_prompt_sha256": hashlib.sha256(system.encode("utf-8")).hexdigest(),
        "user_prompt_sha256": hashlib.sha256(user.encode("utf-8")).hexdigest(),
    }


def compile_residual_seed_fresh_consumer_response_v1(
    *, response: Mapping[str, Any], packet: Mapping[str, Any]
) -> dict[str, Any]:
    compiled = compile_pressure_response(response=response, packet=packet)
    compiled["schema_version"] = "lolla.residual_seed_fresh_consumer_response.v1"
    compiled["source_residual_seed_route_ids"] = sorted(
        item["seed_route_id"] for item in packet["residual_seed_context"]
    )
    compiled["coverage_metadata_used_as_gate"] = False
    compiled["reserve_candidates_semantically_rejected"] = False
    compiled["runtime_effect"] = "none"
    return compiled
