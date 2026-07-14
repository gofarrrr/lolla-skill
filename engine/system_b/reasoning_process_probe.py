"""Phase-3 bounded reasoning-process probe contracts and compilation.

The probabilistic reader interprets one narrow process question and returns
exact speaker/turn/quote evidence.  Deterministic code validates shape and
source custody, attaches stable span IDs, expands explicit compact selection
into complete dispositions, and builds append-only observations and a bounded
view.  It never decides conversational relevance or semantic adequacy.
"""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from .conversation_state_candidates import SourceCatalog, build_source_catalog
from .reasoning_process_contracts import (
    BOUNDED_VIEW_SCHEMA_VERSION,
    OBSERVATION_FAMILIES,
    VIEW_STATUS,
    phase0_contract,
    validate_bounded_view,
)
from .reasoning_process_views import (
    canonical_json_bytes,
    resolve_target_evidence,
    sha256_bytes,
)


PROBE_RESPONSE_SCHEMA_VERSION = "lolla.reasoning_process_probe_response.v1"
MODEL_ADDENDUM_SCHEMA_VERSION = "lolla.reasoning_process_phase3_model_addendum.v1"
COMBINED_MANIFEST_SCHEMA_VERSION = "lolla.reasoning_process_phase3_combined_manifest.v1"
COMPILED_VIEW_SCHEMA_VERSION = "lolla.reasoning_process_phase3_compiled_view.v1"

RESPONSE_STATUSES = ("supported", "mixed", "unclear", "not_found")
ITEM_STATUSES = ("supported", "mixed", "unclear")

_TOP_FIELDS = {
    "status",
    "items",
    "evidence",
    "park_unselected_auxiliary_observations",
    "global_limitations",
}
_ITEM_FIELDS = {
    "interpretation",
    "status",
    "evidence_ids",
    "auxiliary_observation_ids",
    "limitations",
}
_EVIDENCE_FIELDS = {"evidence_id", "speaker", "turn_index", "quote"}


class ReasoningProcessProbeError(ValueError):
    """Raised when Phase-3 probe custody or compilation is invalid."""


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def schema_depth(value: Any) -> int:
    if isinstance(value, Mapping):
        return 1 + max((schema_depth(item) for item in value.values()), default=0)
    if isinstance(value, list):
        return 1 + max((schema_depth(item) for item in value), default=0)
    return 0


def probe_response_schema(
    *, allowed_auxiliary_observation_ids: Sequence[str], max_turn_index: int
) -> dict[str, Any]:
    """Return the strict, shallow model-facing schema for one case."""

    allowed_ids = list(allowed_auxiliary_observation_ids)
    if not allowed_ids or len(allowed_ids) != len(set(allowed_ids)):
        raise ReasoningProcessProbeError(
            "probe schema requires unique auxiliary observation IDs"
        )
    if max_turn_index < 1:
        raise ReasoningProcessProbeError("probe schema requires a positive turn ceiling")
    return {
        "type": "object",
        "description": "One bounded, source-linked reasoning-process read.",
        "properties": {
            "status": {
                "type": "string",
                "enum": list(RESPONSE_STATUSES),
                "description": "Overall evidence state for this narrow process question.",
            },
            "items": {
                "type": "array",
                "minItems": 0,
                "maxItems": 4,
                "description": "Only material process observations needed to answer the question.",
                "items": {
                    "type": "object",
                    "properties": {
                        "interpretation": {
                            "type": "string",
                            "minLength": 1,
                            "maxLength": 600,
                            "description": "Neutral interpretation of what happened in the reasoning process, not advice or answer evaluation.",
                        },
                        "status": {
                            "type": "string",
                            "enum": list(ITEM_STATUSES),
                            "description": "Whether the cited evidence supports one reading, materially mixed readings, or remains unclear.",
                        },
                        "evidence_ids": {
                            "type": "array",
                            "minItems": 1,
                            "maxItems": 6,
                            "uniqueItems": True,
                            "description": "IDs from the top-level exact evidence table that support this interpretation.",
                            "items": {"type": "string", "minLength": 1, "maxLength": 40},
                        },
                        "auxiliary_observation_ids": {
                            "type": "array",
                            "minItems": 0,
                            "maxItems": 8,
                            "uniqueItems": True,
                            "description": "Optional Phase-1 observations that genuinely support this item; empty is valid because the conversation is authoritative.",
                            "items": {
                                "type": "string",
                                "minLength": 1,
                                "maxLength": 120,
                            },
                        },
                        "limitations": {
                            "type": "string",
                            "maxLength": 500,
                            "description": "Missing evidence, alternative reading, or boundary; empty only when none is material.",
                        },
                    },
                    "required": [
                        "interpretation",
                        "status",
                        "evidence_ids",
                        "auxiliary_observation_ids",
                        "limitations",
                    ],
                    "additionalProperties": False,
                },
            },
            "evidence": {
                "type": "array",
                "minItems": 0,
                "maxItems": 12,
                "description": "Deduplicated exact contiguous conversation quotations used by the items.",
                "items": {
                    "type": "object",
                    "properties": {
                        "evidence_id": {
                            "type": "string",
                            "minLength": 1,
                            "maxLength": 40,
                        },
                        "speaker": {
                            "type": "string",
                            "enum": ["user", "assistant"],
                        },
                        "turn_index": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": max_turn_index,
                        },
                        "quote": {
                            "type": "string",
                            "minLength": 1,
                            "maxLength": 800,
                        },
                    },
                    "required": ["evidence_id", "speaker", "turn_index", "quote"],
                    "additionalProperties": False,
                },
            },
            "park_unselected_auxiliary_observations": {
                "type": "boolean",
                "const": True,
                "description": "Explicitly authorizes the local compiler to park the complement of selected auxiliary observations for this view only.",
            },
            "global_limitations": {
                "type": "string",
                "maxLength": 700,
                "description": "Overall limits of this narrow read; it must not evaluate final-answer quality.",
            },
        },
        "required": [
            "status",
            "items",
            "evidence",
            "park_unselected_auxiliary_observations",
            "global_limitations",
        ],
        "additionalProperties": False,
    }


def build_probe_prompts(packet: Mapping[str, Any]) -> dict[str, str]:
    validate_probe_packet(packet)
    system_prompt = """You are a bounded reasoning-process reader.

Answer exactly one narrow question about how a conversation's reasoning unfolded. Analyze the process, not whether the final recommendation is correct or good. Do not give advice, improve the answer, score quality, infer facts outside the conversation, or reward polished language.

The authoritative conversation is primary. The auxiliary Phase-1 observations are fallible prior interpretations: use an observation ID only when it genuinely supports an item, and do not let those observations override or narrow what the conversation shows.

Return the minimum number of material items needed. Every item must cite exact contiguous quotes using the correct speaker and turn. Preserve user challenges, assistant responses, changes, qualifications, uncertainty, and evidence strength when the assigned question requires them. Do not convert a possibility, concern, informal report, preference, or unresolved condition into a fact. A valid empty result is better than invention.

Set park_unselected_auxiliary_observations to true only to declare that every auxiliary observation not explicitly selected may be parked for this view while remaining recoverable in the canonical ledger. Follow the response schema exactly."""
    user_prompt = (
        "Perform the bounded process read described by this target-blind packet. "
        "Do not mention or assess any protected target; none is supplied.\n\n"
        + json.dumps(packet, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    )
    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "system_prompt_sha256": sha256_bytes(system_prompt.encode("utf-8")),
        "user_prompt_sha256": sha256_bytes(user_prompt.encode("utf-8")),
    }


def validate_probe_packet(packet: Mapping[str, Any]) -> dict[str, Any]:
    if packet.get("schema_version") != "lolla.reasoning_process_probe_input.v1":
        raise ReasoningProcessProbeError("unexpected probe input schema")
    if packet.get("status") != "provider_free_target_blind_fixture":
        raise ReasoningProcessProbeError("probe input is not a frozen target-blind fixture")
    if packet.get("view_kind") not in OBSERVATION_FAMILIES:
        raise ReasoningProcessProbeError("probe input view kind is invalid")
    if not isinstance(packet.get("question"), str) or not packet["question"]:
        raise ReasoningProcessProbeError("probe input question is missing")
    source = packet.get("authoritative_conversation")
    if not isinstance(source, Mapping):
        raise ReasoningProcessProbeError("authoritative conversation is missing")
    source_text = source.get("exact_text")
    source_hash = str(source.get("source_sha256", ""))
    if not isinstance(source_text, str) or not source_text:
        raise ReasoningProcessProbeError("authoritative conversation text is missing")
    if source_hash != "sha256:" + sha256_bytes(source_text.encode("utf-8")):
        raise ReasoningProcessProbeError("probe input source hash mismatch")
    auxiliary = packet.get("auxiliary_phase1_ledger")
    if not isinstance(auxiliary, Mapping) or auxiliary.get("included") is not True:
        raise ReasoningProcessProbeError(
            "Phase-3 development packet requires the complete auxiliary ledger"
        )
    observations = auxiliary.get("observations")
    if not isinstance(observations, list) or not observations:
        raise ReasoningProcessProbeError("auxiliary observations are missing")
    ids = [item.get("observation_id") for item in observations if isinstance(item, Mapping)]
    if len(ids) != len(observations) or len(ids) != len(set(ids)) or not all(
        isinstance(item, str) and item for item in ids
    ):
        raise ReasoningProcessProbeError("auxiliary observation IDs are invalid")
    boundary = packet.get("boundary")
    expected_boundary = {
        "protected_target_included": False,
        "source_review_addendum_included": False,
        "semantic_prefilter_performed": False,
        "authoritative_conversation_dropped": False,
        "final_output_evaluated": False,
        "direct_graph_routing_allowed": False,
    }
    if not isinstance(boundary, Mapping) or any(
        boundary.get(key) is not value for key, value in expected_boundary.items()
    ):
        raise ReasoningProcessProbeError("probe input boundary drifted")
    encoded = canonical_json_bytes(packet)
    hard = phase0_contract()["numeric_gates"]["max_view_input_utf8_bytes"]
    if len(encoded) > hard:
        raise ReasoningProcessProbeError("probe input exceeds frozen byte ceiling")
    return {
        "case_id": packet.get("case_id"),
        "view_kind": packet["view_kind"],
        "source_sha256": source_hash,
        "auxiliary_observation_count": len(observations),
        "input_utf8_bytes": len(encoded),
        "protected_target_included": False,
    }


def validate_probe_response(
    payload: Mapping[str, Any],
    *,
    packet: Mapping[str, Any],
    catalog: SourceCatalog,
) -> dict[str, Any]:
    """Validate exact shape, auxiliary IDs, and exact conversation evidence."""

    validate_probe_packet(packet)
    errors: list[str] = []
    if set(payload) != _TOP_FIELDS:
        errors.append("response fields do not match the frozen contract")
    status = payload.get("status")
    if status not in RESPONSE_STATUSES:
        errors.append("response status is invalid")
    items = payload.get("items")
    if not isinstance(items, list) or len(items) > 4:
        errors.append("response items must be an array of at most four items")
        items = []
    if status == "not_found" and items:
        errors.append("not_found response must have no items")
    if status != "not_found" and not items:
        errors.append("non-empty response status requires at least one item")
    if payload.get("park_unselected_auxiliary_observations") is not True:
        errors.append("reader must explicitly park unselected auxiliary observations")
    if not isinstance(payload.get("global_limitations"), str):
        errors.append("global limitations must be a string")
    evidence_rows = payload.get("evidence")
    if not isinstance(evidence_rows, list) or len(evidence_rows) > 12:
        errors.append("response evidence must be an array of at most twelve references")
        evidence_rows = []
    if status == "not_found" and evidence_rows:
        errors.append("not_found response must have no evidence")
    resolved_evidence: dict[str, dict[str, Any]] = {}
    evidence_id_order: list[str] = []
    seen_refs: set[tuple[str, int, str]] = set()
    for evidence_index, reference in enumerate(evidence_rows):
        ref_prefix = f"evidence[{evidence_index}]"
        if not isinstance(reference, Mapping) or set(reference) != _EVIDENCE_FIELDS:
            errors.append(f"{ref_prefix} fields do not match the frozen contract")
            continue
        evidence_id = reference.get("evidence_id")
        speaker = reference.get("speaker")
        turn_index = reference.get("turn_index")
        quote = reference.get("quote")
        if not isinstance(evidence_id, str) or not evidence_id:
            errors.append(f"{ref_prefix}.evidence_id is empty")
            continue
        evidence_id_order.append(evidence_id)
        if speaker not in {"user", "assistant"}:
            errors.append(f"{ref_prefix}.speaker is invalid")
            continue
        if not isinstance(turn_index, int) or turn_index < 1:
            errors.append(f"{ref_prefix}.turn_index is invalid")
            continue
        if not isinstance(quote, str) or not quote:
            errors.append(f"{ref_prefix}.quote is empty")
            continue
        identity = (speaker, turn_index, quote)
        if identity in seen_refs:
            errors.append(f"{ref_prefix} duplicates another evidence reference")
            continue
        seen_refs.add(identity)
        try:
            span = resolve_target_evidence(
                catalog=catalog,
                speaker=speaker,
                turn_index=turn_index,
                quote=quote,
            )
        except ValueError as exc:
            errors.append(f"{ref_prefix} is not exact source evidence: {exc}")
            continue
        resolved_evidence[evidence_id] = {
            "evidence_id": evidence_id,
            "speaker": speaker,
            "turn_index": turn_index,
            "quote": quote,
            "span_id": span.span_id,
            "resolved_span_text": span.text,
        }
    if len(evidence_id_order) != len(set(evidence_id_order)):
        errors.append("response evidence IDs must be unique")
    allowed_ids = {
        item["observation_id"]
        for item in packet["auxiliary_phase1_ledger"]["observations"]
    }
    normalized_items: list[dict[str, Any]] = []
    interpretations: list[str] = []
    for index, item in enumerate(items):
        prefix = f"items[{index}]"
        if not isinstance(item, Mapping) or set(item) != _ITEM_FIELDS:
            errors.append(f"{prefix} fields do not match the frozen contract")
            continue
        interpretation = item.get("interpretation")
        if not isinstance(interpretation, str) or not interpretation.strip():
            errors.append(f"{prefix}.interpretation is empty")
        else:
            interpretations.append(interpretation.strip())
        if item.get("status") not in ITEM_STATUSES:
            errors.append(f"{prefix}.status is invalid")
        limitations = item.get("limitations")
        if not isinstance(limitations, str):
            errors.append(f"{prefix}.limitations must be a string")
        auxiliary_ids = item.get("auxiliary_observation_ids")
        if not isinstance(auxiliary_ids, list) or len(auxiliary_ids) > 8:
            errors.append(f"{prefix}.auxiliary_observation_ids is invalid")
            auxiliary_ids = []
        if len(auxiliary_ids) != len(set(auxiliary_ids)):
            errors.append(f"{prefix}.auxiliary_observation_ids contains duplicates")
        if not set(auxiliary_ids).issubset(allowed_ids):
            errors.append(f"{prefix}.auxiliary_observation_ids contains unknown IDs")
        evidence_ids = item.get("evidence_ids")
        if not isinstance(evidence_ids, list) or not 1 <= len(evidence_ids) <= 6:
            errors.append(f"{prefix}.evidence_ids must contain one to six IDs")
            evidence_ids = []
        if len(evidence_ids) != len(set(evidence_ids)):
            errors.append(f"{prefix}.evidence_ids contains duplicates")
        if not set(evidence_ids).issubset(resolved_evidence):
            errors.append(f"{prefix}.evidence_ids contains unknown IDs")
        resolved = [resolved_evidence[item_id] for item_id in evidence_ids if item_id in resolved_evidence]
        normalized_items.append(
            {
                "interpretation": interpretation,
                "status": item.get("status"),
                "evidence_ids": evidence_ids,
                "evidence": resolved,
                "source_span_ids": list(
                    dict.fromkeys(reference["span_id"] for reference in resolved)
                ),
                "auxiliary_observation_ids": auxiliary_ids,
                "limitations": limitations,
            }
        )
    if len(interpretations) != len(set(interpretations)):
        errors.append("response contains duplicate interpretations")
    used_evidence_ids = {
        evidence_id
        for item in normalized_items
        for evidence_id in item.get("evidence_ids", [])
    }
    if used_evidence_ids != set(resolved_evidence):
        errors.append("every exact evidence row must be referenced by at least one item")
    if errors:
        raise ReasoningProcessProbeError("; ".join(errors))
    return {
        "schema_version": PROBE_RESPONSE_SCHEMA_VERSION,
        "status": status,
        "items": normalized_items,
        "evidence": [resolved_evidence[item_id] for item_id in evidence_id_order if item_id in resolved_evidence],
        "park_unselected_auxiliary_observations": True,
        "global_limitations": payload["global_limitations"],
        "source_custody_validated": True,
        "semantic_adequacy_validated": False,
    }


def compile_probe_view(
    *,
    validated_response: Mapping[str, Any],
    packet: Mapping[str, Any],
    base_ledger: Mapping[str, Any],
    catalog: SourceCatalog,
    call_metadata: Mapping[str, Any],
) -> dict[str, Any]:
    """Compile one valid reader response into append-only custody and a view."""

    packet_validation = validate_probe_packet(packet)
    if base_ledger.get("source", {}).get("conversation_id") != packet.get("case_id"):
        raise ReasoningProcessProbeError("base ledger and packet case IDs differ")
    base_observations = base_ledger.get("observations")
    if not isinstance(base_observations, list):
        raise ReasoningProcessProbeError("base ledger observations are missing")
    packet_ids = [
        item["observation_id"]
        for item in packet["auxiliary_phase1_ledger"]["observations"]
    ]
    base_ids = [item.get("observation_id") for item in base_observations]
    if packet_ids != base_ids:
        raise ReasoningProcessProbeError("packet is not the complete ordered base ledger")
    view_kind = str(packet["view_kind"])
    case_id = str(packet["case_id"])
    model_observations: list[dict[str, Any]] = []
    view_items: list[dict[str, Any]] = []
    auxiliary_to_items: defaultdict[str, list[str]] = defaultdict(list)
    for index, item in enumerate(validated_response["items"], start=1):
        observation_id = f"phase3-{case_id}-{view_kind}-{index:03d}"
        view_item_id = f"phase3-view-item-{case_id}-{view_kind}-{index:03d}"
        raw_record = {
            "response_status": validated_response["status"],
            "interpretation": item["interpretation"],
            "status": item["status"],
            "evidence": item["evidence"],
            "auxiliary_observation_ids": item["auxiliary_observation_ids"],
            "limitations": item["limitations"],
        }
        model_observations.append(
            {
                "observation_id": observation_id,
                "family": view_kind,
                "family_projection_status": "direct_bounded_probabilistic_reader_job",
                "interpretation": item["interpretation"],
                "semantic_status": item["status"],
                "source_span_ids": item["source_span_ids"],
                "source_artifact_id": str(call_metadata["call_id"]),
                "source_record_id": view_item_id,
                "source_family": view_kind,
                "raw_record_sha256": "sha256:" + sha256_bytes(canonical_json_bytes(raw_record)),
                "raw_record": raw_record,
                "provenance": {
                    "producer_kind": "probabilistic_reader",
                    "producer_id": str(call_metadata["requested_model"]),
                    "call_id": str(call_metadata["call_id"]),
                    "model": str(call_metadata["served_model"]),
                    "prompt_sha256": str(call_metadata["prompt_sha256"]),
                },
                "state_history": [
                    {
                        "state": "proposed",
                        "reason": "bounded probabilistic reader response",
                        "actor": "probabilistic_reader",
                    },
                    {
                        "state": "admitted",
                        "reason": "typed response and exact source custody validated",
                        "actor": "deterministic_validator",
                    },
                ],
                "terminal_state": "admitted",
                "terminal_reason": "bounded reader item admitted with exact source lineage",
                "relations": [],
                "graph_routing_eligible": False,
            }
        )
        source_observation_ids = [
            observation_id,
            *item["auxiliary_observation_ids"],
        ]
        view_items.append(
            {
                "view_item_id": view_item_id,
                "interpretation": item["interpretation"],
                "status": item["status"],
                "source_observation_ids": source_observation_ids,
                "source_span_ids": item["source_span_ids"],
                "limitations": item["limitations"],
            }
        )
        for auxiliary_id in item["auxiliary_observation_ids"]:
            auxiliary_to_items[auxiliary_id].append(view_item_id)

    addendum = {
        "schema_version": MODEL_ADDENDUM_SCHEMA_VERSION,
        "status": "bounded_probabilistic_reader_exact_source_validated",
        "case_id": case_id,
        "view_kind": view_kind,
        "base_ledger_sha256": str(call_metadata["base_ledger_sha256"]),
        "call_id": str(call_metadata["call_id"]),
        "response_status": validated_response["status"],
        "global_limitations": validated_response["global_limitations"],
        "observations": model_observations,
        "boundary": {
            "phase1_ledger_modified": False,
            "semantic_relevance_inferred_by_code": False,
            "source_custody_validated_deterministically": True,
            "semantic_adequacy_validated": False,
            "direct_graph_routing_allowed": False,
            "final_output_evaluated": False,
        },
    }
    addendum_sha = sha256_bytes(canonical_json_bytes(addendum))
    combined = [*base_observations, *model_observations]
    manifest = {
        "schema_version": COMBINED_MANIFEST_SCHEMA_VERSION,
        "status": "append_only_model_overlay",
        "case_id": case_id,
        "view_kind": view_kind,
        "base_ledger_sha256": str(call_metadata["base_ledger_sha256"]),
        "model_addendum_sha256": "sha256:" + addendum_sha,
        "observation_ids": [item["observation_id"] for item in combined],
        "boundary": {
            "append_only": True,
            "phase1_ledger_modified": False,
            "authoritative_conversation_replaced": False,
            "direct_graph_routing_allowed": False,
        },
    }
    manifest_sha = sha256_bytes(canonical_json_bytes(manifest))
    dispositions: list[dict[str, Any]] = []
    for observation in base_observations:
        observation_id = observation["observation_id"]
        linked_items = list(dict.fromkeys(auxiliary_to_items.get(observation_id, [])))
        dispositions.append(
            {
                "observation_id": observation_id,
                "disposition": "included" if linked_items else "parked_not_applicable",
                "authority": "probabilistic_reader",
                "reason": (
                    "The reader explicitly selected this auxiliary observation as support."
                    if linked_items
                    else "The reader explicitly selected its complete support set and authorized parking the unselected complement for this view; the observation remains recoverable."
                ),
                "view_item_ids": linked_items,
            }
        )
    for observation, view_item in zip(model_observations, view_items):
        dispositions.append(
            {
                "observation_id": observation["observation_id"],
                "disposition": "included",
                "authority": "probabilistic_reader",
                "reason": "This newly admitted bounded-reader observation produced the view item.",
                "view_item_ids": [view_item["view_item_id"]],
            }
        )
    projection = [
        {
            "observation_id": item["observation_id"],
            "family": item["family"],
            "interpretation": item["interpretation"],
            "semantic_status": item["semantic_status"],
            "source_span_ids": item["source_span_ids"],
        }
        for item in combined
    ]
    observed_bytes = len(canonical_json_bytes({"observations": projection}))
    gates = phase0_contract()["numeric_gates"]
    view = {
        "schema_version": BOUNDED_VIEW_SCHEMA_VERSION,
        "status": VIEW_STATUS,
        "view_id": f"phase3-view-{case_id}-{view_kind}",
        "view_kind": view_kind,
        "question": str(packet["question"]),
        "source_ledger_sha256": "sha256:" + manifest_sha,
        "input": {
            "ledger_observation_ids": [item["observation_id"] for item in combined]
        },
        "items": view_items,
        "dispositions": dispositions,
        "budget": {
            "max_input_observations": gates["max_view_input_observations"],
            "max_input_utf8_bytes": gates["max_view_input_utf8_bytes"],
            "max_output_items": gates["max_view_output_items"],
            "observed_input_observations": len(combined),
            "observed_input_utf8_bytes": observed_bytes,
            "observed_output_items": len(view_items),
            "budget_exceeded": (
                len(combined) > gates["max_view_input_observations"]
                or observed_bytes > gates["max_view_input_utf8_bytes"]
                or len(view_items) > gates["max_view_output_items"]
            ),
        },
        "boundary": {
            "authoritative_source": False,
            "semantic_selection_performed_by_code": False,
            "omissions_recoverable_from_ledger": True,
            "final_output_evaluated": False,
            "quality_score_included": False,
            "direct_graph_routing_allowed": False,
        },
    }
    validation = validate_bounded_view(
        view,
        known_ledger_observation_ids=[item["observation_id"] for item in combined],
        known_span_ids=catalog.by_id(),
        expected_ledger_sha256="sha256:" + manifest_sha,
    )
    return {
        "schema_version": COMPILED_VIEW_SCHEMA_VERSION,
        "status": "provider_response_compiled",
        "packet_validation": packet_validation,
        "model_addendum": addendum,
        "model_addendum_sha256": addendum_sha,
        "combined_manifest": manifest,
        "combined_manifest_sha256": manifest_sha,
        "view": view,
        "view_validation": validation,
        "boundary": {
            "semantic_adequacy_validated": False,
            "final_output_evaluated": False,
            "direct_graph_routing_allowed": False,
        },
    }


def catalog_from_packet(packet: Mapping[str, Any]) -> SourceCatalog:
    validate_probe_packet(packet)
    source = packet["authoritative_conversation"]
    return build_source_catalog(
        source_text=source["exact_text"], source_path=source["source_path"]
    )
