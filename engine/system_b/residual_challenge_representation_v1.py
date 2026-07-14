"""Provider-free contracts for source-grounded residual challenge representation."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from typing import Any

from .simulated_reliability_v1 import SimulatedReliabilityError


DISCOVERY_PACKET_SCHEMA = "lolla.residual_challenge_discovery_packet.v1"
DISCOVERY_RESPONSE_SCHEMA = "lolla.residual_challenge_discovery_response.v1"
COVERAGE_PACKET_SCHEMA = "lolla.residual_challenge_coverage_packet.v1"
COVERAGE_RESPONSE_SCHEMA = "lolla.residual_challenge_coverage_response.v1"
PORTFOLIO_SCHEMA = "lolla.residual_challenge_portfolio.v1"

CANDIDATE_IDS = ("rc1", "rc2", "rc3")
CANDIDATE_KINDS = {
    "external_break_condition",
    "omitted_dependency",
    "second_order_effect",
    "stakeholder_or_distribution",
    "time_horizon",
    "other_structural_question",
}
JOINT_COVERAGES = {
    "operationalized",
    "acknowledged_only",
    "not_covered",
    "ambiguous",
}
PORTFOLIO_TIER_BY_COVERAGE = {
    "operationalized": "covered_receipt",
    "ambiguous": "edge_reserve",
    "acknowledged_only": "active_working_set",
    "not_covered": "active_working_set",
}


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _hash(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _seal(payload: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(payload)
    result["packet_sha256"] = _hash(result)
    return result


def _verify_packet(packet: Mapping[str, Any], schema: str) -> None:
    if packet.get("schema_version") != schema:
        raise SimulatedReliabilityError("invalid residual challenge packet schema")
    supplied = packet.get("packet_sha256")
    payload = {key: value for key, value in packet.items() if key != "packet_sha256"}
    if supplied != _hash(payload):
        raise SimulatedReliabilityError("residual challenge packet hash drifted")


def _validate_evidence_records(
    records: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for record in records:
        if set(record) != {"evidence_id", "speaker", "turn_number", "text"}:
            raise SimulatedReliabilityError("invalid residual evidence fields")
        evidence_id = record.get("evidence_id")
        speaker = record.get("speaker")
        turn_number = record.get("turn_number")
        text = record.get("text")
        if (
            not isinstance(evidence_id, str)
            or not evidence_id
            or evidence_id in seen
            or speaker not in {"user", "assistant"}
            or not isinstance(turn_number, int)
            or turn_number < 1
            or not isinstance(text, str)
            or not text.strip()
        ):
            raise SimulatedReliabilityError("invalid residual evidence value")
        seen.add(evidence_id)
        result.append(dict(record))
    if not result or not any(row["speaker"] == "user" for row in result):
        raise SimulatedReliabilityError("residual discovery requires user evidence")
    return result


def evidence_records_from_annotated_text_v1(annotated_text: str) -> list[dict[str, Any]]:
    """Parse the explicit annotated-evidence transport without interpreting meaning."""

    if not isinstance(annotated_text, str) or not annotated_text.strip():
        raise SimulatedReliabilityError("annotated evidence text is empty")
    speaker: str | None = None
    turn_number: int | None = None
    records: list[dict[str, Any]] = []
    for line in annotated_text.splitlines():
        header = re.fullmatch(r"\[Turn ([0-9]+) (USER|ASSISTANT)\]", line)
        if header:
            turn_number = int(header.group(1))
            speaker = header.group(2).lower()
            continue
        evidence = re.fullmatch(r"(e[0-9]+)\t(.+)", line)
        if evidence:
            if speaker is None or turn_number is None:
                raise SimulatedReliabilityError("annotated evidence lacks speaker header")
            records.append(
                {
                    "evidence_id": evidence.group(1),
                    "speaker": speaker,
                    "turn_number": turn_number,
                    "text": evidence.group(2),
                }
            )
    return _validate_evidence_records(records)


def build_residual_discovery_packet_v1(
    *,
    case_id: str,
    evidence_records: Sequence[Mapping[str, Any]],
    source_refs: Sequence[Mapping[str, str]],
) -> dict[str, Any]:
    """Build discovery input from user evidence without the prior assistant frame."""

    if not isinstance(case_id, str) or not case_id.strip():
        raise SimulatedReliabilityError("residual discovery requires case identity")
    evidence = _validate_evidence_records(evidence_records)
    user_evidence = [row for row in evidence if row["speaker"] == "user"]
    return _seal(
        {
            "schema_version": DISCOVERY_PACKET_SCHEMA,
            "case_id": case_id,
            "user_evidence": user_evidence,
            "source_refs": [dict(row) for row in source_refs],
            "candidate_contract": {
                "maximum_candidates": 3,
                "candidate_goal": "A structurally different question about an explicit dependency, commitment, affected party, time horizon, or break condition that could materially qualify the current path.",
                "source_grounding": "Every candidate cites exact supplied user evidence that makes the question plausible.",
                "unknown_unknown_boundary": "Ask what would have to be checked; do not assert that an unstated external event or condition exists.",
                "generic_caution_excluded": True,
                "coverage_judgment_deferred": True,
            },
            "boundary": {
                "assistant_evidence_supplied_to_discovery": False,
                "role_summary_supplied_to_discovery": False,
                "expected_pressure_supplied": False,
                "candidate_semantics_probabilistic": True,
                "deterministic_semantic_inference": False,
                "keyword_or_chronology_gate_added": False,
                "direct_graph_routing_allowed": False,
            },
        }
    )


def residual_discovery_response_schema_v1() -> dict[str, Any]:
    item_properties = {
        "candidate_id": {"type": "string", "enum": list(CANDIDATE_IDS)},
        "candidate_kind": {"type": "string", "enum": sorted(CANDIDATE_KINDS)},
        "challenge_question": {"type": "string", "minLength": 8, "maxLength": 500},
        "structural_pressure": {"type": "string", "minLength": 8, "maxLength": 500},
        "applicability_condition": {"type": "string", "minLength": 8, "maxLength": 500},
        "risk_if_ignored": {"type": "string", "minLength": 8, "maxLength": 500},
        "force_boundary": {"type": "string", "minLength": 8, "maxLength": 500},
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


def build_residual_discovery_prompts_v1(packet: Mapping[str, Any]) -> dict[str, str]:
    _verify_packet(packet, DISCOVERY_PACKET_SCHEMA)
    system = (
        "Discover at most three source-grounded residual challenge questions from user evidence. "
        "Seek a dependency, second-order effect, affected party, time horizon, or break condition "
        "that could materially qualify the current path. Formulate questions or conditional "
        "hypotheses, never unstated external facts. Do not judge whether the prior assistant covered "
        "the question; that is a separate task. Return exact evidence IDs and schema-valid JSON."
    )
    user = (
        "RESIDUAL CHALLENGE DISCOVERY\n"
        + _canonical(packet)
        + "\n\nReturn no generic caution. A candidate may be unusual or low-base-rate, but the "
        "supplied evidence must make its question plausible. Keep candidates structurally distinct. "
        "Use rc1, rc2, and rc3 in order without gaps. Empty is allowed when no source-grounded "
        "candidate meets the contract."
    )
    return {
        "system_prompt": system,
        "user_prompt": user,
        "system_prompt_sha256": hashlib.sha256(system.encode("utf-8")).hexdigest(),
        "user_prompt_sha256": hashlib.sha256(user.encode("utf-8")).hexdigest(),
    }


def compile_residual_discovery_response_v1(
    *,
    response: Mapping[str, Any],
    packet: Mapping[str, Any],
    producer_id: str,
) -> dict[str, Any]:
    _verify_packet(packet, DISCOVERY_PACKET_SCHEMA)
    if set(response) != {"candidates"} or not isinstance(response.get("candidates"), list):
        raise SimulatedReliabilityError("invalid residual discovery response")
    candidates = response["candidates"]
    if len(candidates) > 3:
        raise SimulatedReliabilityError("residual discovery candidate cap exceeded")
    valid_evidence = {row["evidence_id"] for row in packet["user_evidence"]}
    expected_fields = {
        "candidate_id",
        "candidate_kind",
        "challenge_question",
        "structural_pressure",
        "applicability_condition",
        "risk_if_ignored",
        "force_boundary",
        "source_evidence_ids",
        "claim_status",
    }
    compiled: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, candidate in enumerate(candidates):
        if not isinstance(candidate, Mapping) or set(candidate) != expected_fields:
            raise SimulatedReliabilityError("invalid residual candidate fields")
        candidate_id = candidate.get("candidate_id")
        source_ids = candidate.get("source_evidence_ids")
        text_fields = (
            "challenge_question",
            "structural_pressure",
            "applicability_condition",
            "risk_if_ignored",
            "force_boundary",
        )
        if (
            candidate_id != CANDIDATE_IDS[index]
            or candidate_id in seen
            or candidate.get("candidate_kind") not in CANDIDATE_KINDS
            or candidate.get("claim_status") != "question_not_external_fact"
            or not isinstance(source_ids, list)
            or not source_ids
            or len(source_ids) > 5
            or len(source_ids) != len(set(source_ids))
            or bool(set(source_ids) - valid_evidence)
            or any(
                not isinstance(candidate.get(field), str)
                or not candidate[field].strip()
                or len(candidate[field]) > 500
                for field in text_fields
            )
        ):
            raise SimulatedReliabilityError("invalid residual candidate value or evidence custody")
        seen.add(candidate_id)
        compiled.append(dict(candidate))
    return {
        "schema_version": DISCOVERY_RESPONSE_SCHEMA,
        "status": "residual_candidates_preserved_for_separate_coverage_review",
        "case_id": packet["case_id"],
        "candidates": compiled,
        "producer_id": producer_id,
        "source_packet_sha256": packet["packet_sha256"],
        "boundary": {
            "candidate_semantics_model_authored": True,
            "coverage_not_yet_judged": True,
            "empty_is_model_authored_not_deterministically_inferred": True,
            "deterministic_semantic_inference": False,
            "keyword_or_chronology_gate_added": False,
            "direct_graph_routing_allowed": False,
        },
    }


def build_residual_coverage_packet_v1(
    *,
    case_id: str,
    candidate: Mapping[str, Any],
    evidence_records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    evidence = _validate_evidence_records(evidence_records)
    if candidate.get("candidate_id") not in CANDIDATE_IDS:
        raise SimulatedReliabilityError("invalid residual coverage candidate")
    valid_ids = {row["evidence_id"] for row in evidence}
    source_ids = candidate.get("source_evidence_ids", [])
    if not isinstance(source_ids, list) or bool(set(source_ids) - valid_ids):
        raise SimulatedReliabilityError("residual candidate source custody drifted")
    return _seal(
        {
            "schema_version": COVERAGE_PACKET_SCHEMA,
            "case_id": case_id,
            "candidate": dict(candidate),
            "conversation_evidence": evidence,
            "coverage_contract": {
                "operationalized": "The joint conversation supplies an actionable test, boundary, owner, funding treatment, safeguard, or reopening condition for this exact challenge.",
                "acknowledged_only": "The joint conversation notices the challenge but does not make it actionable.",
                "not_covered": "The joint conversation does not address this challenge.",
                "ambiguous": "Responsible readings disagree about whether the exact challenge was operationalized.",
            },
            "boundary": {
                "candidate_generation_separate_from_coverage": True,
                "full_joint_evidence_supplied": True,
                "remaining_real_world_risk_does_not_negate_operationalized_coverage": True,
                "coverage_semantics_probabilistic": True,
                "deterministic_semantic_inference": False,
                "direct_graph_routing_allowed": False,
            },
        }
    )


def residual_coverage_response_schema_v1(candidate_id: str) -> dict[str, Any]:
    if candidate_id not in CANDIDATE_IDS:
        raise SimulatedReliabilityError("invalid residual coverage candidate identity")
    properties = {
        "candidate_id": {"type": "string", "enum": [candidate_id]},
        "joint_coverage": {"type": "string", "enum": sorted(JOINT_COVERAGES)},
        "source_evidence_ids": {
            "type": "array",
            "minItems": 0,
            "maxItems": 5,
            "items": {"type": "string", "minLength": 1, "maxLength": 160},
        },
    }
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }


def build_residual_coverage_prompts_v1(packet: Mapping[str, Any]) -> dict[str, str]:
    _verify_packet(packet, COVERAGE_PACKET_SCHEMA)
    system = (
        "Judge whether one residual challenge is operationalized in the supplied joint conversation. "
        "Do not decide whether the external risk is true or important. Operationalized requires an "
        "actionable test, boundary, owner, funding treatment, safeguard, or reopening condition for "
        "the exact challenge. Return exact evidence IDs and schema-valid JSON."
    )
    user = (
        "RESIDUAL CHALLENGE COVERAGE REVIEW\n"
        + _canonical(packet)
        + "\n\nUse operationalized only for actionable treatment of this exact question. General "
        "carefulness or a neighboring safeguard is not enough. acknowledged_only, operationalized, "
        "and ambiguous cite exact evidence. not_covered cites none."
    )
    return {
        "system_prompt": system,
        "user_prompt": user,
        "system_prompt_sha256": hashlib.sha256(system.encode("utf-8")).hexdigest(),
        "user_prompt_sha256": hashlib.sha256(user.encode("utf-8")).hexdigest(),
    }


def compile_residual_coverage_response_v1(
    *,
    response: Mapping[str, Any],
    packet: Mapping[str, Any],
    producer_id: str,
) -> dict[str, Any]:
    _verify_packet(packet, COVERAGE_PACKET_SCHEMA)
    expected = {"candidate_id", "joint_coverage", "source_evidence_ids"}
    if set(response) != expected or response.get("candidate_id") != packet["candidate"]["candidate_id"]:
        raise SimulatedReliabilityError("invalid residual coverage response fields")
    coverage = response.get("joint_coverage")
    source_ids = response.get("source_evidence_ids")
    valid_ids = {row["evidence_id"] for row in packet["conversation_evidence"]}
    if (
        coverage not in JOINT_COVERAGES
        or not isinstance(source_ids, list)
        or len(source_ids) > 5
        or len(source_ids) != len(set(source_ids))
        or bool(set(source_ids) - valid_ids)
    ):
        raise SimulatedReliabilityError("invalid residual coverage value or evidence custody")
    if coverage == "not_covered" and source_ids:
        raise SimulatedReliabilityError("uncovered residual challenge cites coverage evidence")
    if coverage != "not_covered" and not source_ids:
        raise SimulatedReliabilityError("covered residual challenge lacks evidence")
    return {
        "schema_version": COVERAGE_RESPONSE_SCHEMA,
        "status": "residual_challenge_joint_coverage_custody_complete",
        "case_id": packet["case_id"],
        "assessment": dict(response),
        "producer_id": producer_id,
        "source_packet_sha256": packet["packet_sha256"],
        "boundary": {
            "coverage_semantics_model_authored": True,
            "portfolio_tier_not_model_authored": True,
            "deterministic_semantic_inference": False,
            "direct_graph_routing_allowed": False,
        },
    }


def join_residual_challenge_portfolio_v1(
    *,
    discovery_result: Mapping[str, Any],
    coverage_results: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    if discovery_result.get("schema_version") != DISCOVERY_RESPONSE_SCHEMA:
        raise SimulatedReliabilityError("invalid residual discovery join input")
    candidates = discovery_result.get("candidates")
    if not isinstance(candidates, list):
        raise SimulatedReliabilityError("invalid residual discovery candidates")
    by_candidate: dict[str, Mapping[str, Any]] = {}
    for result in coverage_results:
        if result.get("schema_version") != COVERAGE_RESPONSE_SCHEMA:
            raise SimulatedReliabilityError("invalid residual coverage join input")
        candidate_id = result.get("assessment", {}).get("candidate_id")
        if candidate_id in by_candidate:
            raise SimulatedReliabilityError("duplicate residual coverage result")
        by_candidate[candidate_id] = result
    candidate_ids = [row["candidate_id"] for row in candidates]
    if set(by_candidate) != set(candidate_ids):
        raise SimulatedReliabilityError("residual coverage does not match discovery candidates")
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
            }
        )
    counts = {
        tier: sum(row["portfolio_tier"] == tier for row in items)
        for tier in ("active_working_set", "edge_reserve", "covered_receipt")
    }
    return {
        "schema_version": PORTFOLIO_SCHEMA,
        "status": (
            "residual_challenge_portfolio_joined"
            if items
            else "model_authored_empty_residual_portfolio_preserved"
        ),
        "case_id": discovery_result["case_id"],
        "portfolio_items": items,
        "counts": {
            "discovered_candidates": len(items),
            **counts,
        },
        "graph_handoff": {
            "status": "not_built_requires_separate_probabilistic_abstraction",
            "contains_case_context": False,
            "candidate_ids": [row["candidate_id"] for row in items],
            "direct_graph_routing_allowed": False,
        },
        "boundary": {
            "all_discovered_candidates_preserved": True,
            "covered_candidates_not_deleted": True,
            "ambiguous_candidates_preserved_in_edge_reserve": True,
            "active_tier_derived_from_model_authored_coverage": True,
            "deterministic_semantic_inference": False,
            "keyword_or_chronology_gate_added": False,
            "graph_candidate_selection_performed": False,
            "runtime_effect": "none",
        },
    }
