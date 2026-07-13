"""Smaller residual discovery contract after the verbose v1 probe truncated."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import Any

from .residual_challenge_representation_v1 import (
    CANDIDATE_IDS,
    CANDIDATE_KINDS,
    COVERAGE_RESPONSE_SCHEMA,
    DISCOVERY_PACKET_SCHEMA,
    PORTFOLIO_TIER_BY_COVERAGE,
)
from .simulated_reliability_v1 import SimulatedReliabilityError


SEED_RESPONSE_SCHEMA = "lolla.residual_challenge_seed_response.v1"
SEED_PORTFOLIO_SCHEMA = "lolla.residual_challenge_seed_portfolio.v1"


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _hash(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _verify_discovery_packet(packet: Mapping[str, Any]) -> None:
    if packet.get("schema_version") != DISCOVERY_PACKET_SCHEMA:
        raise SimulatedReliabilityError("invalid residual seed packet schema")
    supplied = packet.get("packet_sha256")
    payload = {key: value for key, value in packet.items() if key != "packet_sha256"}
    if supplied != _hash(payload):
        raise SimulatedReliabilityError("residual seed packet hash drifted")


def residual_seed_response_schema_v1() -> dict[str, Any]:
    item_properties = {
        "candidate_id": {"type": "string", "enum": list(CANDIDATE_IDS)},
        "candidate_kind": {"type": "string", "enum": sorted(CANDIDATE_KINDS)},
        "challenge_question": {"type": "string", "minLength": 8, "maxLength": 500},
        "source_evidence_ids": {
            "type": "array",
            "minItems": 1,
            "maxItems": 5,
            "items": {"type": "string", "minLength": 1, "maxLength": 160},
        },
        "claim_status": {"type": "string", "enum": ["question_not_external_fact"]},
    }
    properties = {
        "candidates": {
            "type": "array",
            "minItems": 0,
            "maxItems": 3,
            "items": {
                "type": "object",
                "properties": item_properties,
                "required": list(item_properties),
                "additionalProperties": False,
            },
        }
    }
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }


def build_residual_seed_prompts_v1(packet: Mapping[str, Any]) -> dict[str, str]:
    _verify_discovery_packet(packet)
    system = (
        "Propose at most three source-grounded residual challenge seeds from user evidence. "
        "Each seed is only one structurally different question plus its kind and exact evidence IDs. "
        "Ask about an explicit dependency, second-order effect, affected party, time horizon, or "
        "break condition. Never assert an unstated external fact. Do not explain applicability, "
        "risk, force boundaries, or prior-answer coverage; later tasks own those jobs."
    )
    user = (
        "RESIDUAL CHALLENGE SEED DISCOVERY\n"
        + _canonical(packet)
        + "\n\nReturn only identity, kind, one question, source IDs, and question_not_external_fact. "
        "Use rc1, rc2, and rc3 in order without gaps. Prefer structurally different questions. "
        "Exclude generic caution. Empty is allowed when the evidence supports no concrete seed."
    )
    return {
        "system_prompt": system,
        "user_prompt": user,
        "system_prompt_sha256": hashlib.sha256(system.encode("utf-8")).hexdigest(),
        "user_prompt_sha256": hashlib.sha256(user.encode("utf-8")).hexdigest(),
    }


def compile_residual_seed_response_v1(
    *,
    response: Mapping[str, Any],
    packet: Mapping[str, Any],
    producer_id: str,
) -> dict[str, Any]:
    _verify_discovery_packet(packet)
    if set(response) != {"candidates"} or not isinstance(response.get("candidates"), list):
        raise SimulatedReliabilityError("invalid residual seed response")
    candidates = response["candidates"]
    if len(candidates) > 3:
        raise SimulatedReliabilityError("residual seed cap exceeded")
    valid_evidence = {row["evidence_id"] for row in packet["user_evidence"]}
    expected = {
        "candidate_id",
        "candidate_kind",
        "challenge_question",
        "source_evidence_ids",
        "claim_status",
    }
    compiled = []
    for index, candidate in enumerate(candidates):
        if not isinstance(candidate, Mapping) or set(candidate) != expected:
            raise SimulatedReliabilityError("invalid residual seed fields")
        source_ids = candidate.get("source_evidence_ids")
        question = candidate.get("challenge_question")
        if (
            candidate.get("candidate_id") != CANDIDATE_IDS[index]
            or candidate.get("candidate_kind") not in CANDIDATE_KINDS
            or candidate.get("claim_status") != "question_not_external_fact"
            or not isinstance(question, str)
            or not question.strip()
            or len(question) > 500
            or not isinstance(source_ids, list)
            or not source_ids
            or len(source_ids) > 5
            or len(source_ids) != len(set(source_ids))
            or bool(set(source_ids) - valid_evidence)
        ):
            raise SimulatedReliabilityError("invalid residual seed value or evidence custody")
        compiled.append(dict(candidate))
    return {
        "schema_version": SEED_RESPONSE_SCHEMA,
        "status": "residual_seeds_preserved_for_separate_coverage_review",
        "case_id": packet["case_id"],
        "candidates": compiled,
        "producer_id": producer_id,
        "source_packet_sha256": packet["packet_sha256"],
        "boundary": {
            "seed_semantics_model_authored": True,
            "coverage_not_yet_judged": True,
            "enrichment_not_yet_authored": True,
            "empty_is_model_authored_not_deterministically_inferred": True,
            "deterministic_semantic_inference": False,
            "direct_graph_routing_allowed": False,
        },
    }


def join_residual_seed_portfolio_v1(
    *,
    seed_result: Mapping[str, Any],
    coverage_results: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    if seed_result.get("schema_version") != SEED_RESPONSE_SCHEMA:
        raise SimulatedReliabilityError("invalid residual seed join input")
    candidates = seed_result.get("candidates")
    if not isinstance(candidates, list):
        raise SimulatedReliabilityError("invalid residual seed candidates")
    by_candidate: dict[str, Mapping[str, Any]] = {}
    for result in coverage_results:
        if result.get("schema_version") != COVERAGE_RESPONSE_SCHEMA:
            raise SimulatedReliabilityError("invalid residual seed coverage input")
        candidate_id = result.get("assessment", {}).get("candidate_id")
        if candidate_id in by_candidate:
            raise SimulatedReliabilityError("duplicate residual seed coverage")
        by_candidate[candidate_id] = result
    candidate_ids = [row["candidate_id"] for row in candidates]
    if set(by_candidate) != set(candidate_ids):
        raise SimulatedReliabilityError("residual seed coverage is incomplete")
    items = []
    for candidate in candidates:
        assessment = by_candidate[candidate["candidate_id"]]["assessment"]
        coverage = assessment["joint_coverage"]
        items.append(
            {
                **dict(candidate),
                "joint_coverage": coverage,
                "coverage_source_evidence_ids": list(assessment["source_evidence_ids"]),
                "portfolio_tier": PORTFOLIO_TIER_BY_COVERAGE[coverage],
                "active_pressure_eligible": coverage in {"acknowledged_only", "not_covered"},
                "enrichment_status": (
                    "required_before_consumer_or_graph"
                    if coverage != "operationalized"
                    else "optional_for_covered_receipt"
                ),
            }
        )
    counts = {
        tier: sum(row["portfolio_tier"] == tier for row in items)
        for tier in ("active_working_set", "edge_reserve", "covered_receipt")
    }
    return {
        "schema_version": SEED_PORTFOLIO_SCHEMA,
        "status": (
            "residual_seed_portfolio_joined_enrichment_pending"
            if items
            else "model_authored_empty_residual_seed_portfolio_preserved"
        ),
        "case_id": seed_result["case_id"],
        "portfolio_items": items,
        "counts": {"discovered_candidates": len(items), **counts},
        "graph_handoff": {
            "status": "blocked_pending_probabilistic_enrichment_and_fact_free_abstraction",
            "contains_case_context": False,
            "candidate_ids": candidate_ids,
            "direct_graph_routing_allowed": False,
        },
        "boundary": {
            "all_seeds_preserved": True,
            "covered_seeds_not_deleted": True,
            "ambiguous_seeds_preserved_in_edge_reserve": True,
            "portfolio_tier_derived_from_model_authored_coverage": True,
            "enrichment_deferred_until_after_coverage": True,
            "deterministic_semantic_inference": False,
            "keyword_or_chronology_gate_added": False,
            "runtime_effect": "none",
        },
    }
