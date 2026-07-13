"""Provider-free contracts for the first R4 complementary semantic readers.

The probabilistic boundaries interpret unresolved matters, reopen conditions,
and exact-ID relationships.  This module owns only packet construction,
structured-output shape, source/record custody, identity, and fan-in projection.
It does not infer whether model-authored prose is semantically correct.
"""
from __future__ import annotations

import copy
import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import Any

from .conversation_state_fan_in import (
    FAN_IN_SCHEMA,
    build_reader_result,
    build_semantic_record,
    build_source_registry,
    planned_reader,
)


UNCERTAINTY_PACKET_SCHEMA = "lolla.r4_complementary_uncertainty_packet.v1"
UNCERTAINTY_RESPONSE_SCHEMA = "lolla.r4_complementary_uncertainty_response.v1"
RELATIONSHIP_PACKET_SCHEMA = "lolla.r4_exact_id_relationship_packet.v1"
RELATIONSHIP_RESPONSE_SCHEMA = "lolla.r4_exact_id_relationship_response.v1"
COMPILED_UNCERTAINTY_SCHEMA = "lolla.r4_complementary_uncertainty_compiled.v1"
COMPILED_RELATIONSHIP_SCHEMA = "lolla.r4_exact_id_relationship_compiled.v1"

UNCERTAINTY_SURFACES = ("unresolved_matter", "reopen_condition")
OUTCOMES = (
    "records_present",
    "no_supported_record_observed",
    "ambiguous_review",
)
SUPPORT_STATUSES = ("supported", "ambiguous")
MAX_RECORDS_PER_UNCERTAINTY_SURFACE = 2
MAX_RELATIONSHIP_RECORDS = 2
MAX_EVIDENCE_IDS = 8
MAX_RELATED_RECORD_IDS = 6


class R4ComplementaryReaderError(ValueError):
    """Raised when a provider-free reader contract or custody check fails."""


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def value_sha256(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise R4ComplementaryReaderError(f"{label} must be an object")
    return value


def _exact(value: Mapping[str, Any], fields: set[str], label: str) -> None:
    if set(value) != fields:
        raise R4ComplementaryReaderError(f"{label} fields do not match contract")


def _text(value: Any, label: str, *, maximum: int, allow_empty: bool = False) -> str:
    if (
        not isinstance(value, str)
        or len(value) > maximum
        or (not allow_empty and not value.strip())
    ):
        raise R4ComplementaryReaderError(f"{label} is invalid")
    return value


def _sha(value: Any, label: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise R4ComplementaryReaderError(f"{label} is not a lowercase SHA-256")
    return value


def _string_array(
    value: Any,
    label: str,
    *,
    minimum: int,
    maximum: int,
    allowed: set[str] | None = None,
) -> list[str]:
    if (
        not isinstance(value, list)
        or not minimum <= len(value) <= maximum
        or any(not isinstance(item, str) or not item for item in value)
        or len(value) != len(set(value))
    ):
        raise R4ComplementaryReaderError(f"{label} is invalid")
    if allowed is not None and not set(value).issubset(allowed):
        raise R4ComplementaryReaderError(f"{label} contains an unknown identity")
    return list(value)


def source_alias_catalog_v1(wrapper: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Resolve wrapper aliases to exact text without deciding relevance."""
    packet = _mapping(wrapper.get("packet"), "wrapper.packet")
    focal = _mapping(packet.get("focal_region"), "wrapper.packet.focal_region")
    annotated = _text(
        focal.get("annotated_sentence_text"),
        "annotated_sentence_text",
        maximum=500_000,
    )
    text_by_alias: dict[str, str] = {}
    for line in annotated.splitlines():
        if "\t" not in line:
            continue
        alias, text = line.split("\t", 1)
        if alias.startswith("e"):
            if alias in text_by_alias:
                raise R4ComplementaryReaderError("source alias text is duplicated")
            text_by_alias[alias] = text

    rows = wrapper.get("focal_alias_map")
    if not isinstance(rows, list) or not rows:
        raise R4ComplementaryReaderError("wrapper focal alias map is invalid")
    result = []
    for index, raw in enumerate(rows, 1):
        row = _mapping(raw, f"focal_alias_map[{index}]")
        _exact(
            row,
            {"alias", "span_id", "speaker", "turn_index", "text_sha256"},
            f"focal_alias_map[{index}]",
        )
        alias = _text(row["alias"], f"focal_alias_map[{index}].alias", maximum=80)
        text = text_by_alias.get(alias)
        if text is None:
            raise R4ComplementaryReaderError("alias text is unavailable")
        if sha256_bytes(text.encode("utf-8")) != row["text_sha256"]:
            raise R4ComplementaryReaderError("alias text hash drifted")
        result.append({**dict(row), "text": text})
    if set(text_by_alias) != {row["alias"] for row in result}:
        raise R4ComplementaryReaderError("annotated source and alias map differ")
    return sorted(result, key=lambda item: item["alias"])


def build_source_registry_v1(
    *, wrapper: Mapping[str, Any], source_bytes: bytes
) -> dict[str, Any]:
    packet = _mapping(wrapper.get("packet"), "wrapper.packet")
    source = _mapping(packet.get("source"), "wrapper.packet.source")
    aliases = source_alias_catalog_v1(wrapper)
    expected = str(source.get("source_sha256", "")).removeprefix("sha256:")
    if _sha(expected, "source.source_sha256") != sha256_bytes(source_bytes):
        raise R4ComplementaryReaderError("authoritative source bytes drifted")
    return build_source_registry(
        case_id=_text(packet.get("case_id"), "case_id", maximum=180),
        source_path=_text(source.get("source_path"), "source_path", maximum=800),
        source_bytes=source_bytes,
        message_count=int(source.get("conversation_message_count", 0)),
        aliases=[
            {key: row[key] for key in ("alias", "span_id", "speaker", "turn_index", "text_sha256")}
            for row in aliases
        ],
    )


def _prior_record_projection(role_portfolio: Mapping[str, Any]) -> list[dict[str, Any]]:
    role_observations = _mapping(
        role_portfolio.get("role_observations"), "role_portfolio.role_observations"
    )
    projected = []
    for role, surface in (
        ("starting", "starting_position"),
        ("current", "current_position"),
        ("qualification", "qualification"),
    ):
        records = role_observations.get(role)
        if not isinstance(records, list):
            raise R4ComplementaryReaderError(f"role portfolio {role} records are invalid")
        for index, raw in enumerate(records, 1):
            record = _mapping(raw, f"role_portfolio.{role}[{index}]")
            record_id = record.get("role_record_id") or record.get("observation_id")
            evidence_ids = record.get("source_evidence_ids")
            projected.append(
                {
                    "record_id": _text(record_id, "prior record ID", maximum=180),
                    "surface": surface,
                    "interpretation": _text(
                        record.get("role_interpretation"),
                        "prior role interpretation",
                        maximum=2000,
                    ),
                    "source_aliases": _string_array(
                        evidence_ids,
                        "prior record evidence IDs",
                        minimum=1,
                        maximum=24,
                    ),
                    "limitations": _text(
                        record.get("limitations", ""),
                        "prior record limitations",
                        maximum=1000,
                        allow_empty=True,
                    ),
                }
            )
    return sorted(projected, key=lambda item: item["record_id"])


def build_uncertainty_packet_v1(
    *,
    wrapper: Mapping[str, Any],
    source_bytes: bytes,
    role_portfolio: Mapping[str, Any],
    role_artifact_path: str,
    role_artifact_bytes: bytes,
) -> dict[str, Any]:
    """Build a full-source, quiet-capable paired uncertainty packet."""
    source_registry = build_source_registry_v1(wrapper=wrapper, source_bytes=source_bytes)
    aliases = source_alias_catalog_v1(wrapper)
    qualification_review = _mapping(
        role_portfolio.get("qualification_review"),
        "role_portfolio.qualification_review",
    )
    review_fields = {"outcome", "evidence_ids", "interpretation", "limitations"}
    review = {
        key: copy.deepcopy(qualification_review.get(key)) for key in review_fields
    }
    if set(review) != review_fields:
        raise R4ComplementaryReaderError("qualification review projection failed")
    alias_ids = {row["alias"] for row in aliases}
    _string_array(
        review["evidence_ids"],
        "qualification review evidence IDs",
        minimum=1,
        maximum=8,
        allowed=alias_ids,
    )
    packet = {
        "schema_version": UNCERTAINTY_PACKET_SCHEMA,
        "status": "provider_free_uncertainty_input_frozen",
        "case_id": source_registry["case_id"],
        "source": {
            "path": source_registry["source_path"],
            "sha256": source_registry["source_sha256"],
            "message_count": source_registry["message_count"],
            "aliases": [
                {
                    "alias": row["alias"],
                    "speaker": row["speaker"],
                    "turn_index": row["turn_index"],
                    "text": row["text"],
                    "text_sha256": row["text_sha256"],
                }
                for row in aliases
            ],
        },
        "prior_interpretation_context": {
            "artifact_path": _text(
                role_artifact_path, "role_artifact_path", maximum=800
            ),
            "artifact_sha256": sha256_bytes(role_artifact_bytes),
            "records": _prior_record_projection(role_portfolio),
            "qualification_review": review,
            "authority": "fallible_prior_interpretation_not_source_truth",
        },
        "task_contract": {
            "surfaces": list(UNCERTAINTY_SURFACES),
            "maximum_records_per_surface": MAX_RECORDS_PER_UNCERTAINTY_SURFACE,
            "valid_zero_output": True,
            "valid_ambiguous_output": True,
            "source_supported_inference_allowed": True,
            "external_fact_invention_allowed": False,
        },
        "boundary": {
            "authoritative_source_precedes_prior_interpretation_in_prompt": True,
            "semantic_meaning_decided_by_model": True,
            "prior_interpretations_may_be_incomplete": True,
            "deterministic_semantic_absence_inference": False,
            "keyword_or_chronology_gate": False,
            "quality_or_pressure_decision": False,
        },
    }
    return {**packet, "packet_sha256": value_sha256(packet)}


def _model_record_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "description": "One source-linked semantic candidate.",
        "properties": {
            "support": {
                "type": "string",
                "enum": list(SUPPORT_STATUSES),
                "description": "Whether the source supports the read or leaves it ambiguous.",
            },
            "interpretation": {
                "type": "string",
                "description": "Concise meaning of this candidate without advice.",
            },
            "evidence_ids": {
                "type": "array",
                "description": "Exact source aliases supporting this candidate.",
                "minItems": 1,
                "maxItems": MAX_EVIDENCE_IDS,
                "items": {"type": "string"},
            },
            "limitations": {
                "type": "string",
                "description": "Uncertainty or scope limit; use an empty string if none.",
            },
        },
        "required": ["support", "interpretation", "evidence_ids", "limitations"],
        "additionalProperties": False,
    }


def uncertainty_response_schema_v1() -> dict[str, Any]:
    review = {
        "type": "object",
        "description": "One explicit semantic-surface review.",
        "properties": {
            "surface": {
                "type": "string",
                "enum": list(UNCERTAINTY_SURFACES),
                "description": "The semantic surface reviewed.",
            },
            "outcome": {
                "type": "string",
                "enum": list(OUTCOMES),
                "description": "Present, quiet, or ambiguous result of this review.",
            },
            "records": {
                "type": "array",
                "description": "Zero to two candidates for this surface.",
                "minItems": 0,
                "maxItems": MAX_RECORDS_PER_UNCERTAINTY_SURFACE,
                "items": _model_record_schema(),
            },
        },
        "required": ["surface", "outcome", "records"],
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "description": "Paired unresolved-matter and reopen-condition review.",
        "properties": {
            "reviews": {
                "type": "array",
                "description": "Exactly one review for each declared surface.",
                "minItems": 2,
                "maxItems": 2,
                "items": review,
            },
            "global_limitations": {
                "type": "string",
                "description": "Limits applying to the whole read; empty if none.",
            },
        },
        "required": ["reviews", "global_limitations"],
        "additionalProperties": False,
    }


def build_uncertainty_prompts_v1(packet: Mapping[str, Any]) -> dict[str, str]:
    if packet.get("schema_version") != UNCERTAINTY_PACKET_SCHEMA:
        raise R4ComplementaryReaderError("invalid uncertainty packet")
    source = packet["source"]
    prior = packet["prior_interpretation_context"]
    system = (
        "You are a narrow complementary conversation-state reader. Interpret messy meaning; "
        "do not recommend action or score reasoning. The complete source is authoritative. "
        "Prior interpretation records are fallible context and may be incomplete. Review two "
        "distinct surfaces: an unresolved matter is a source-supported question, assumption, "
        "dependency, or tension still open at the endpoint; a reopen condition is specific "
        "evidence, an event, or dependency failure that would legitimately require reconsidering "
        "the current position. A safeguard, monitoring step, or generic future uncertainty is "
        "not automatically either one. Source-supported inference is allowed; outside facts are "
        "not. It is valid to return no record or an ambiguous record. Cite exact aliases."
    )
    user = (
        "AUTHORITATIVE SOURCE (read first)\n"
        + canonical_json_bytes(source).decode("utf-8")
        + "\n\nFALLIBLE PRIOR INTERPRETATION CONTEXT\n"
        + canonical_json_bytes(prior).decode("utf-8")
        + "\n\nTASK\nReturn exactly one review for unresolved_matter and one for "
        "reopen_condition, in either order. Return at most two records per review. Use "
        "records_present only when at least one supported record exists; use "
        "ambiguous_review only when evidence supports no stronger than ambiguous records; use "
        "no_supported_record_observed with an empty records array. Preserve speaker ownership "
        "and modal force. Do not decide mental-model relevance, pressure, advice quality, or "
        "whether a human should trust the final answer. Return schema-valid JSON only."
    )
    return {
        "system_prompt": system,
        "user_prompt": user,
        "system_prompt_sha256": sha256_bytes(system.encode("utf-8")),
        "user_prompt_sha256": sha256_bytes(user.encode("utf-8")),
    }


def planned_readers_v1(
    *, case_id: str, existing_producer_id: str, complementary_producer_id: str
) -> list[dict[str, str]]:
    specs = (
        ("01-starting", "starting_position", "simulated_reliability_v1", existing_producer_id),
        ("02-current", "current_position", "simulated_reliability_v1", existing_producer_id),
        ("03-qualification", "qualification", "simulated_reliability_v1", existing_producer_id),
        ("04-unresolved", "unresolved_matter", "r4_complementary_reader_v1", complementary_producer_id),
        ("05-reopen", "reopen_condition", "r4_complementary_reader_v1", complementary_producer_id),
        ("06-relationship", "cross_thread_relationship", "r4_exact_id_relationship_reader_v1", complementary_producer_id),
    )
    return [
        planned_reader(
            reader_id=f"r4-{case_id}-{suffix}",
            surface=surface,
            producer_kind=kind,
            producer_id=producer,
        )
        for suffix, surface, kind, producer in specs
    ]


def existing_reader_results_v1(
    *,
    role_portfolio: Mapping[str, Any],
    source_registry: Mapping[str, Any],
    planned_readers: Sequence[Mapping[str, Any]],
    role_artifact_path: str,
    role_artifact_bytes: bytes,
) -> list[dict[str, Any]]:
    readers = {reader["surface"]: reader for reader in planned_readers}
    role_observations = _mapping(
        role_portfolio.get("role_observations"), "role_portfolio.role_observations"
    )
    results = []
    for role, surface in (
        ("starting", "starting_position"),
        ("current", "current_position"),
        ("qualification", "qualification"),
    ):
        raw_records = role_observations.get(role)
        if not isinstance(raw_records, list):
            raise R4ComplementaryReaderError(f"existing {role} records are invalid")
        records = []
        for raw in raw_records:
            record = _mapping(raw, f"existing {role} record")
            record_id = record.get("role_record_id") or record.get("observation_id")
            records.append(
                build_semantic_record(
                    source_registry=source_registry,
                    record_id=_text(record_id, "existing record ID", maximum=180),
                    surface=surface,
                    semantic_payload=record,
                    source_aliases=_string_array(
                        record.get("source_evidence_ids"),
                        "existing record evidence IDs",
                        minimum=1,
                        maximum=24,
                    ),
                )
            )
        results.append(
            build_reader_result(
                reader=readers[surface],
                state="complete" if records else "completed_zero",
                records=records,
                artifact_path=role_artifact_path,
                artifact_bytes=role_artifact_bytes,
            )
        )
    return results


def missing_complementary_reader_results_v1(
    *, planned_readers: Sequence[Mapping[str, Any]]
) -> list[dict[str, Any]]:
    readers = {reader["surface"]: reader for reader in planned_readers}
    return [
        build_reader_result(
            reader=readers[surface],
            state="missing",
            records=[],
            issue_code="reader_not_run",
            issue_stage="provider_authorization",
            safe_detail="The frozen reader has not been authorized for a provider call.",
        )
        for surface in UNCERTAINTY_SURFACES
    ] + [
        build_reader_result(
            reader=readers["cross_thread_relationship"],
            state="missing",
            records=[],
            issue_code="upstream_dependency_unavailable",
            issue_stage="uncertainty_reader_dependency",
            safe_detail="The relationship packet requires admitted uncertainty-reader results.",
        )
    ]


def _validate_model_record(
    raw: Any, *, label: str, allowed_aliases: set[str]
) -> dict[str, Any]:
    record = _mapping(raw, label)
    _exact(
        record,
        {"support", "interpretation", "evidence_ids", "limitations"},
        label,
    )
    if record.get("support") not in SUPPORT_STATUSES:
        raise R4ComplementaryReaderError(f"{label}.support is invalid")
    _text(record.get("interpretation"), f"{label}.interpretation", maximum=800)
    _text(
        record.get("limitations"),
        f"{label}.limitations",
        maximum=600,
        allow_empty=True,
    )
    _string_array(
        record.get("evidence_ids"),
        f"{label}.evidence_ids",
        minimum=1,
        maximum=MAX_EVIDENCE_IDS,
        allowed=allowed_aliases,
    )
    return copy.deepcopy(dict(record))


def _validate_outcome_records(
    *, outcome: Any, records: Sequence[Mapping[str, Any]], label: str
) -> None:
    if outcome not in OUTCOMES:
        raise R4ComplementaryReaderError(f"{label}.outcome is invalid")
    support = [record["support"] for record in records]
    if outcome == "no_supported_record_observed" and records:
        raise R4ComplementaryReaderError(f"{label} quiet outcome must be empty")
    if outcome == "records_present" and (not records or "supported" not in support):
        raise R4ComplementaryReaderError(
            f"{label} present outcome needs a supported record"
        )
    if outcome == "ambiguous_review" and (
        not records or set(support) != {"ambiguous"}
    ):
        raise R4ComplementaryReaderError(
            f"{label} ambiguous outcome needs only ambiguous records"
        )


def compile_uncertainty_response_v1(
    *,
    response: Mapping[str, Any],
    packet: Mapping[str, Any],
    source_registry: Mapping[str, Any],
    planned_readers: Sequence[Mapping[str, Any]],
    artifact_path: str,
    artifact_bytes: bytes,
) -> dict[str, Any]:
    """Compile provider-authored paired semantics without judging their meaning."""
    if packet.get("schema_version") != UNCERTAINTY_PACKET_SCHEMA:
        raise R4ComplementaryReaderError("invalid uncertainty packet")
    value = _mapping(response, "uncertainty response")
    _exact(value, {"reviews", "global_limitations"}, "uncertainty response")
    _text(
        value.get("global_limitations"),
        "global_limitations",
        maximum=800,
        allow_empty=True,
    )
    reviews = value.get("reviews")
    if not isinstance(reviews, list) or len(reviews) != 2:
        raise R4ComplementaryReaderError("uncertainty reviews must contain two items")
    allowed_aliases = {item["alias"] for item in source_registry["aliases"]}
    by_surface: dict[str, dict[str, Any]] = {}
    for review_index, raw_review in enumerate(reviews, 1):
        review = _mapping(raw_review, f"review[{review_index}]")
        _exact(review, {"surface", "outcome", "records"}, f"review[{review_index}]")
        surface = review.get("surface")
        if surface not in UNCERTAINTY_SURFACES or surface in by_surface:
            raise R4ComplementaryReaderError("uncertainty surface is invalid or duplicated")
        raw_records = review.get("records")
        if (
            not isinstance(raw_records, list)
            or len(raw_records) > MAX_RECORDS_PER_UNCERTAINTY_SURFACE
        ):
            raise R4ComplementaryReaderError("uncertainty record count is invalid")
        records = [
            _validate_model_record(
                raw,
                label=f"review[{review_index}].record[{record_index}]",
                allowed_aliases=allowed_aliases,
            )
            for record_index, raw in enumerate(raw_records, 1)
        ]
        _validate_outcome_records(
            outcome=review.get("outcome"),
            records=records,
            label=f"review[{review_index}]",
        )
        by_surface[surface] = {
            "outcome": review["outcome"],
            "records": records,
        }
    if set(by_surface) != set(UNCERTAINTY_SURFACES):
        raise R4ComplementaryReaderError("both uncertainty surfaces are required")

    readers = {reader["surface"]: reader for reader in planned_readers}
    reader_results = []
    compiled_record_ids = []
    for surface in UNCERTAINTY_SURFACES:
        review = by_surface[surface]
        semantic_records = []
        for index, record in enumerate(review["records"], 1):
            payload = {
                "review_outcome": review["outcome"],
                "record": record,
                "global_limitations": value["global_limitations"],
            }
            record_id = (
                f"r4u-{packet['case_id']}-{surface}-{index:02d}-"
                f"{value_sha256(payload)[:12]}"
            )
            semantic_records.append(
                build_semantic_record(
                    source_registry=source_registry,
                    record_id=record_id,
                    surface=surface,
                    semantic_payload=payload,
                    source_aliases=record["evidence_ids"],
                )
            )
            compiled_record_ids.append(record_id)
        reader_results.append(
            build_reader_result(
                reader=readers[surface],
                state="complete" if semantic_records else "completed_zero",
                records=semantic_records,
                artifact_path=artifact_path,
                artifact_bytes=artifact_bytes,
            )
        )
    return {
        "schema_version": COMPILED_UNCERTAINTY_SCHEMA,
        "status": "paired_uncertainty_custody_complete",
        "case_id": packet["case_id"],
        "reader_results": reader_results,
        "record_ids": sorted(compiled_record_ids),
        "boundary": {
            "model_records_changed": False,
            "semantic_correctness_inferred_by_code": False,
            "outcome_record_shape_consistency_validated": True,
            "source_alias_custody_validated": True,
            "deterministic_semantic_merge": False,
            "keyword_or_chronology_gate": False,
        },
    }


def build_relationship_packet_v1(
    *, fan_in: Mapping[str, Any], source_text_by_alias: Mapping[str, str]
) -> dict[str, Any]:
    """Build a bounded exact-ID relationship packet from admitted records."""
    if fan_in.get("schema_version") != FAN_IN_SCHEMA:
        raise R4ComplementaryReaderError("invalid fan-in for relationship packet")
    source_registry = _mapping(fan_in.get("source_registry"), "fan_in.source_registry")
    alias_index = {row["alias"]: row for row in source_registry["aliases"]}
    if set(source_text_by_alias) != set(alias_index):
        raise R4ComplementaryReaderError("relationship source text catalog drifted")
    record_catalog = []
    for result in fan_in.get("reader_results", []):
        if result.get("surface") == "cross_thread_relationship":
            continue
        for record in result.get("records", []):
            evidence = []
            for locator in record["source_locators"]:
                alias = locator["alias"]
                text = source_text_by_alias[alias]
                if sha256_bytes(text.encode("utf-8")) != locator["text_sha256"]:
                    raise R4ComplementaryReaderError(
                        "relationship source text hash drifted"
                    )
                evidence.append({"alias": alias, "text": text})
            record_catalog.append(
                {
                    "record_id": record["record_id"],
                    "surface": record["surface"],
                    "semantic_payload": copy.deepcopy(record["semantic_payload"]),
                    "semantic_payload_sha256": record["semantic_payload_sha256"],
                    "source_evidence": evidence,
                }
            )
    packet = {
        "schema_version": RELATIONSHIP_PACKET_SCHEMA,
        "status": "provider_free_exact_id_relationship_input_frozen",
        "case_id": fan_in["case_id"],
        "source": {
            "path": source_registry["source_path"],
            "sha256": source_registry["source_sha256"],
        },
        "record_catalog": sorted(record_catalog, key=lambda item: item["record_id"]),
        "task_contract": {
            "maximum_relationships": MAX_RELATIONSHIP_RECORDS,
            "minimum_exact_endpoints_per_relationship": 2,
            "maximum_exact_endpoints_per_relationship": MAX_RELATED_RECORD_IDS,
            "valid_zero_output": True,
            "valid_ambiguous_output": True,
        },
        "boundary": {
            "record_catalog_is_provider_authored_input": True,
            "exact_record_ids_required": True,
            "cooccurrence_is_not_automatically_a_relationship": True,
            "semantic_relationship_decided_by_model": True,
            "deterministic_relationship_meaning_inference": False,
            "quality_or_pressure_decision": False,
        },
    }
    return {**packet, "packet_sha256": value_sha256(packet)}


def relationship_response_schema_v1() -> dict[str, Any]:
    record = {
        "type": "object",
        "description": "One source-grounded relationship among exact record IDs.",
        "properties": {
            "support": {
                "type": "string",
                "enum": list(SUPPORT_STATUSES),
                "description": "Whether the source supports or leaves the relation ambiguous.",
            },
            "related_record_ids": {
                "type": "array",
                "description": "Exact IDs of records participating in this relationship.",
                "minItems": 2,
                "maxItems": MAX_RELATED_RECORD_IDS,
                "items": {"type": "string"},
            },
            "relationship": {
                "type": "string",
                "description": "Meaning added by the relationship, not a restatement.",
            },
            "evidence_ids": {
                "type": "array",
                "description": "Exact aliases supporting this relationship.",
                "minItems": 1,
                "maxItems": MAX_EVIDENCE_IDS,
                "items": {"type": "string"},
            },
            "limitations": {
                "type": "string",
                "description": "Uncertainty or scope limit; empty if none.",
            },
        },
        "required": [
            "support",
            "related_record_ids",
            "relationship",
            "evidence_ids",
            "limitations",
        ],
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "description": "Exact-ID relationship review over admitted semantic records.",
        "properties": {
            "outcome": {
                "type": "string",
                "enum": list(OUTCOMES),
                "description": "Present, quiet, or ambiguous relationship result.",
            },
            "records": {
                "type": "array",
                "description": "Zero to two relationship records.",
                "minItems": 0,
                "maxItems": MAX_RELATIONSHIP_RECORDS,
                "items": record,
            },
            "global_limitations": {
                "type": "string",
                "description": "Limits applying to the whole read; empty if none.",
            },
        },
        "required": ["outcome", "records", "global_limitations"],
        "additionalProperties": False,
    }


def build_relationship_prompts_v1(packet: Mapping[str, Any]) -> dict[str, str]:
    if packet.get("schema_version") != RELATIONSHIP_PACKET_SCHEMA:
        raise R4ComplementaryReaderError("invalid relationship packet")
    system = (
        "You are a narrow relationship reader. The input contains exact IDs and unchanged "
        "provider-authored semantic records with their source evidence. Do not create, merge, "
        "rewrite, rank, or repair those records. Identify at most two source-grounded "
        "relationships only when the combination adds meaning beyond co-occurrence or shared "
        "evidence. Existing records may be wrong; state limitations rather than silently fixing "
        "them. It is valid to return no relationship or an ambiguous relationship. Use only exact "
        "record IDs and exact evidence aliases. Do not recommend action, select mental models, "
        "activate pressure, score quality, or infer meaning from ordering or ID text."
    )
    user = (
        "EXACT-ID RECORD PACKET\n"
        + canonical_json_bytes(packet).decode("utf-8")
        + "\n\nTASK\nReturn records_present only when at least one supported relationship "
        "exists; return ambiguous_review only when no relationship is stronger than ambiguous; "
        "return no_supported_record_observed with an empty records array. Every relationship "
        "must name two to six different IDs from record_catalog and cite source aliases visible "
        "in the packet. Return schema-valid JSON only."
    )
    return {
        "system_prompt": system,
        "user_prompt": user,
        "system_prompt_sha256": sha256_bytes(system.encode("utf-8")),
        "user_prompt_sha256": sha256_bytes(user.encode("utf-8")),
    }


def compile_relationship_response_v1(
    *,
    response: Mapping[str, Any],
    packet: Mapping[str, Any],
    source_registry: Mapping[str, Any],
    planned_readers: Sequence[Mapping[str, Any]],
    artifact_path: str,
    artifact_bytes: bytes,
) -> dict[str, Any]:
    if packet.get("schema_version") != RELATIONSHIP_PACKET_SCHEMA:
        raise R4ComplementaryReaderError("invalid relationship packet")
    value = _mapping(response, "relationship response")
    _exact(value, {"outcome", "records", "global_limitations"}, "relationship response")
    _text(
        value.get("global_limitations"),
        "relationship global_limitations",
        maximum=800,
        allow_empty=True,
    )
    raw_records = value.get("records")
    if not isinstance(raw_records, list) or len(raw_records) > MAX_RELATIONSHIP_RECORDS:
        raise R4ComplementaryReaderError("relationship record count is invalid")
    allowed_ids = {row["record_id"] for row in packet["record_catalog"]}
    allowed_aliases = {row["alias"] for row in source_registry["aliases"]}
    records = []
    for index, raw in enumerate(raw_records, 1):
        record = _mapping(raw, f"relationship record[{index}]")
        _exact(
            record,
            {
                "support",
                "related_record_ids",
                "relationship",
                "evidence_ids",
                "limitations",
            },
            f"relationship record[{index}]",
        )
        if record.get("support") not in SUPPORT_STATUSES:
            raise R4ComplementaryReaderError("relationship support is invalid")
        _string_array(
            record.get("related_record_ids"),
            "relationship exact record IDs",
            minimum=2,
            maximum=MAX_RELATED_RECORD_IDS,
            allowed=allowed_ids,
        )
        _string_array(
            record.get("evidence_ids"),
            "relationship evidence IDs",
            minimum=1,
            maximum=MAX_EVIDENCE_IDS,
            allowed=allowed_aliases,
        )
        _text(record.get("relationship"), "relationship meaning", maximum=900)
        _text(
            record.get("limitations"),
            "relationship limitations",
            maximum=600,
            allow_empty=True,
        )
        records.append(copy.deepcopy(dict(record)))
    _validate_outcome_records(
        outcome=value.get("outcome"), records=records, label="relationship response"
    )
    semantic_records = []
    for index, record in enumerate(records, 1):
        payload = {
            "review_outcome": value["outcome"],
            "record": record,
            "global_limitations": value["global_limitations"],
        }
        semantic_records.append(
            build_semantic_record(
                source_registry=source_registry,
                record_id=(
                    f"r4x-{packet['case_id']}-{index:02d}-"
                    f"{value_sha256(payload)[:12]}"
                ),
                surface="cross_thread_relationship",
                semantic_payload=payload,
                source_aliases=record["evidence_ids"],
                related_record_ids=record["related_record_ids"],
            )
        )
    reader = next(
        (
            item
            for item in planned_readers
            if item["surface"] == "cross_thread_relationship"
        ),
        None,
    )
    if reader is None:
        raise R4ComplementaryReaderError("relationship reader is not planned")
    result = build_reader_result(
        reader=reader,
        state="complete" if semantic_records else "completed_zero",
        records=semantic_records,
        artifact_path=artifact_path,
        artifact_bytes=artifact_bytes,
    )
    return {
        "schema_version": COMPILED_RELATIONSHIP_SCHEMA,
        "status": "exact_id_relationship_custody_complete",
        "case_id": packet["case_id"],
        "reader_result": result,
        "record_ids": sorted(record["record_id"] for record in semantic_records),
        "boundary": {
            "model_records_changed": False,
            "exact_endpoint_membership_validated": True,
            "relationship_meaning_inferred_by_code": False,
            "semantic_repair_or_merge": False,
            "array_order_or_id_text_used_for_meaning": False,
            "quality_or_pressure_decision": False,
        },
    }
