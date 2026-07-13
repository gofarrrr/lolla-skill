"""Deterministic validation for the research-only reasoning-pressure handoff.

This module checks shape, caps, lineage, references, and non-claims. It does
not decide which pressures matter, infer meaning from conversation text, call
models, score answer quality, or authorize runtime integration.
"""
from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from typing import Any


HANDOFF_SCHEMA_VERSION = "lolla.reasoning_pressure_handoff.v0"
VALIDATION_SCHEMA_VERSION = "lolla.reasoning_pressure_handoff_validation.v0"
DISPOSITION_LEDGER_SCHEMA_VERSION = "lolla.reasoning_pressure_disposition_ledger.v0"
DISPOSITION_LEDGER_VALIDATION_SCHEMA_VERSION = (
    "lolla.reasoning_pressure_disposition_ledger_validation.v0"
)
ALLOWED_STATUSES = {
    "illustrative_not_runtime_output",
    "research_candidate",
}
ALLOWED_DECISION_EFFECTS = {
    "question",
    "alternative",
    "evidence_gate",
    "condition",
    "sequence",
    "reversal_rule",
    "risk_treatment",
}
ALLOWED_DISPOSITIONS = [
    "used",
    "rejected",
    "deferred",
    "private_guardrail",
]
REQUIRED_NON_CLAIMS = {
    "not_a_quality_score",
    "not_a_command_to_reverse_the_original_answer",
    "not_graph_integration_authority",
}

_TOP_LEVEL_FIELDS = {
    "schema_version",
    "status",
    "source",
    "lineage",
    "boundary",
    "pressure_items",
    "preservation_items",
    "known_limits",
    "consideration_contract",
    "non_claims",
}
_SOURCE_FIELDS = {
    "conversation_sha256",
    "authoritative_full_conversation_reattached",
    "original_answer_reattached",
}
_LINEAGE_FIELDS = {
    "reasoning_pattern_packet_sha256",
    "graph_version",
    "graph_trace_artifact_sha256",
    "routing_projection_sha256",
}
_BOUNDARY_FIELDS = {
    "full_semantic_inventory_included",
    "full_graph_candidate_catalog_included",
    "raw_provider_content_included",
    "private_reasoning_included",
    "expected_answer_included",
    "quality_score_included",
}
_PRESSURE_FIELDS = {
    "pressure_id",
    "mechanism_id",
    "source_event_ids",
    "challenge",
    "applicability_condition",
    "decision_effect",
    "consequence_if_true",
    "set_aside_condition",
    "graph_trace_refs",
}
_PRESERVATION_FIELDS = {
    "preservation_id",
    "source_event_ids",
    "preserve",
    "reason",
}
_CONSIDERATION_FIELDS = {
    "allowed_dispositions",
    "public_surface_must_hide_machinery",
    "every_item_requires_private_disposition",
}
_DISPOSITION_LEDGER_FIELDS = {
    "schema_version",
    "status",
    "handoff_sha256",
    "items",
    "semantic_effect_review",
}
_DISPOSITION_ITEM_FIELDS = {
    "pressure_id",
    "disposition",
    "strongest_plausible_application",
    "why",
    "visible_effect",
    "private_guardrail",
    "risk_if_forced",
    "risk_if_ignored",
}
_EFFECT_REVIEW_FIELDS = {
    "status",
    "reviewer",
    "reviewed_output_sha256",
    "findings",
}
_EFFECT_REVIEW_STATUSES = {"pending", "accepted", "rejected"}
_SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._:-]*$")


class ReasoningPressureHandoffValidationError(ValueError):
    """Raised when a handoff violates the deterministic research contract."""


def build_reasoning_pressure_disposition_skeleton(
    handoff: Mapping[str, Any],
    *,
    handoff_sha256: str,
) -> dict[str, Any]:
    """Build the exact pressure-ID shells a reasoning consumer must complete."""

    if not _SHA256_RE.fullmatch(handoff_sha256):
        raise ReasoningPressureHandoffValidationError(
            "handoff_sha256 must be a prefixed lowercase SHA-256"
        )
    items = []
    for pressure in handoff.get("pressure_items", []):
        if not isinstance(pressure, Mapping) or not _nonempty_string(
            pressure.get("pressure_id")
        ):
            raise ReasoningPressureHandoffValidationError(
                "handoff pressure_items must have valid pressure_id values"
            )
        items.append(
            {
                "pressure_id": str(pressure["pressure_id"]),
                "disposition": "",
                "strongest_plausible_application": "",
                "why": "",
                "visible_effect": "",
                "private_guardrail": "",
                "risk_if_forced": "",
                "risk_if_ignored": "",
            }
        )
    return {
        "schema_version": DISPOSITION_LEDGER_SCHEMA_VERSION,
        "status": "pending",
        "handoff_sha256": handoff_sha256,
        "items": items,
        "semantic_effect_review": {
            "status": "pending",
            "reviewer": "",
            "reviewed_output_sha256": "",
            "findings": [],
        },
    }


def validate_reasoning_pressure_disposition_ledger(
    ledger: Mapping[str, Any],
    *,
    handoff: Mapping[str, Any],
    expected_handoff_sha256: str,
) -> dict[str, Any]:
    """Validate exact pressure custody without judging whether prose changed.

    The semantic-effect review is an externally supplied status. This function
    verifies its shape and output hash when present; it never infers effect
    consistency from the revised answer.
    """

    errors: list[str] = []
    if set(ledger) != _DISPOSITION_LEDGER_FIELDS:
        errors.append("disposition ledger fields are invalid")
    if ledger.get("schema_version") != DISPOSITION_LEDGER_SCHEMA_VERSION:
        errors.append("disposition ledger schema_version is invalid")
    if ledger.get("status") != "completed":
        errors.append("disposition ledger status must be completed")
    handoff_hash = ledger.get("handoff_sha256")
    if not isinstance(handoff_hash, str) or not _SHA256_RE.fullmatch(handoff_hash):
        errors.append("handoff_sha256 must be a prefixed lowercase SHA-256")
    elif handoff_hash != expected_handoff_sha256:
        errors.append("handoff_sha256 does not match custody")

    pressure_ids = [
        str(item.get("pressure_id"))
        for item in handoff.get("pressure_items", [])
        if isinstance(item, Mapping) and _nonempty_string(item.get("pressure_id"))
    ]
    items = ledger.get("items")
    if not isinstance(items, list):
        errors.append("items must be a list")
        items = []
    observed_ids: list[str] = []
    disposition_counts: dict[str, int] = {}
    for index, item in enumerate(items):
        prefix = f"items[{index}]"
        if not isinstance(item, Mapping):
            errors.append(f"{prefix} must be an object")
            continue
        if set(item) != _DISPOSITION_ITEM_FIELDS:
            errors.append(f"{prefix} fields are invalid")
            continue
        pressure_id = str(item.get("pressure_id", ""))
        observed_ids.append(pressure_id)
        disposition = str(item.get("disposition", ""))
        if disposition not in ALLOWED_DISPOSITIONS:
            errors.append(f"{prefix}.disposition is invalid")
        else:
            disposition_counts[disposition] = (
                disposition_counts.get(disposition, 0) + 1
            )
        for field in _DISPOSITION_ITEM_FIELDS - {"pressure_id", "disposition"}:
            if not isinstance(item.get(field), str):
                errors.append(f"{prefix}.{field} must be a string")
        for field in (
            "strongest_plausible_application",
            "why",
            "risk_if_forced",
            "risk_if_ignored",
        ):
            if not _nonempty_string(item.get(field)):
                errors.append(f"{prefix}.{field} is required")
        visible_effect = str(item.get("visible_effect", "")).strip()
        private_guardrail = str(item.get("private_guardrail", "")).strip()
        if disposition == "used" and not (visible_effect or private_guardrail):
            errors.append(
                f"{prefix}.used requires visible_effect or private_guardrail"
            )
        if disposition == "private_guardrail":
            if not private_guardrail:
                errors.append(
                    f"{prefix}.private_guardrail disposition requires private_guardrail"
                )
            if visible_effect:
                errors.append(
                    f"{prefix}.private_guardrail disposition must not claim visible_effect"
                )
        if disposition in {"rejected", "deferred"} and (
            visible_effect or private_guardrail
        ):
            errors.append(
                f"{prefix}.{disposition} must not claim visible or private effect"
            )
    if observed_ids != pressure_ids:
        errors.append(
            "items must copy every handoff pressure_id exactly once in packet order"
        )

    effect_review = ledger.get("semantic_effect_review")
    effect_review_status = "invalid"
    if not isinstance(effect_review, Mapping):
        errors.append("semantic_effect_review must be an object")
    else:
        if set(effect_review) != _EFFECT_REVIEW_FIELDS:
            errors.append("semantic_effect_review fields are invalid")
        effect_review_status = str(effect_review.get("status", ""))
        if effect_review_status not in _EFFECT_REVIEW_STATUSES:
            errors.append("semantic_effect_review.status is invalid")
        reviewer = effect_review.get("reviewer")
        output_hash = effect_review.get("reviewed_output_sha256")
        findings = effect_review.get("findings")
        if not isinstance(findings, list) or any(
            not _nonempty_string(finding) for finding in findings or []
        ):
            errors.append("semantic_effect_review.findings must be strings")
        if effect_review_status == "pending":
            if reviewer or output_hash or findings:
                errors.append(
                    "pending semantic_effect_review must not claim review evidence"
                )
        elif effect_review_status in {"accepted", "rejected"}:
            if not _nonempty_string(reviewer):
                errors.append("reviewed semantic_effect_review requires reviewer")
            if not isinstance(output_hash, str) or not _SHA256_RE.fullmatch(
                output_hash
            ):
                errors.append(
                    "reviewed semantic_effect_review requires reviewed_output_sha256"
                )
            if effect_review_status == "rejected" and not findings:
                errors.append("rejected semantic_effect_review requires findings")

    if errors:
        raise ReasoningPressureHandoffValidationError("; ".join(errors))
    return {
        "schema_version": DISPOSITION_LEDGER_VALIDATION_SCHEMA_VERSION,
        "status": "structurally_valid",
        "pressure_item_count": len(pressure_ids),
        "disposition_counts": dict(sorted(disposition_counts.items())),
        "exact_pressure_id_coverage": True,
        "semantic_effect_review_status": effect_review_status,
        "semantic_effect_consistency_inferred_by_code": False,
        "runtime_integration_authorized": False,
    }


def validate_reasoning_pressure_handoff(
    payload: Mapping[str, Any],
    *,
    known_source_event_ids: Iterable[str],
    known_graph_trace_refs: Iterable[str],
    expected_conversation_sha256: str | None = None,
    expected_reasoning_pattern_packet_sha256: str | None = None,
    expected_graph_version: str | None = None,
    expected_graph_trace_artifact_sha256: str | None = None,
    expected_routing_projection_sha256: str | None = None,
) -> dict[str, Any]:
    """Return a sanitized structural validation report or raise on failure.

    The known-reference sets must come from separately custodied source and
    graph artifacts. Passing them is deliberately mandatory: format-valid
    references are not treated as traceable merely because they look valid.
    """

    errors = list(
        iter_reasoning_pressure_handoff_errors(
            payload,
            known_source_event_ids=set(known_source_event_ids),
            known_graph_trace_refs=set(known_graph_trace_refs),
            expected_conversation_sha256=expected_conversation_sha256,
            expected_reasoning_pattern_packet_sha256=(
                expected_reasoning_pattern_packet_sha256
            ),
            expected_graph_version=expected_graph_version,
            expected_graph_trace_artifact_sha256=(
                expected_graph_trace_artifact_sha256
            ),
            expected_routing_projection_sha256=(
                expected_routing_projection_sha256
            ),
        )
    )
    if errors:
        raise ReasoningPressureHandoffValidationError("; ".join(errors))

    return {
        "schema_version": VALIDATION_SCHEMA_VERSION,
        "status": "valid_for_shadow_evaluation_only",
        "validated_scope": [
            "schema_shape",
            "item_caps",
            "lineage_hashes",
            "source_event_references",
            "graph_trace_references",
            "boundary_flags",
            "required_non_claims",
        ],
        "pressure_item_count": len(payload["pressure_items"]),
        "preservation_item_count": len(payload["preservation_items"]),
        "model_calls": 0,
        "semantic_relevance_validated": False,
        "answer_quality_validated": False,
        "runtime_integration_authorized": False,
    }


def iter_reasoning_pressure_handoff_errors(
    payload: Mapping[str, Any],
    *,
    known_source_event_ids: set[str],
    known_graph_trace_refs: set[str],
    expected_conversation_sha256: str | None = None,
    expected_reasoning_pattern_packet_sha256: str | None = None,
    expected_graph_version: str | None = None,
    expected_graph_trace_artifact_sha256: str | None = None,
    expected_routing_projection_sha256: str | None = None,
) -> Iterable[str]:
    """Yield deterministic contract errors without interpreting prose."""

    if not isinstance(payload, Mapping):
        yield "payload must be an object"
        return

    yield from _field_errors(payload, _TOP_LEVEL_FIELDS, "payload")
    if not _TOP_LEVEL_FIELDS <= set(payload):
        return

    if payload.get("schema_version") != HANDOFF_SCHEMA_VERSION:
        yield f"schema_version must be {HANDOFF_SCHEMA_VERSION}"
    if payload.get("status") not in ALLOWED_STATUSES:
        yield "status is not allowed"

    source = payload.get("source")
    if not isinstance(source, Mapping):
        yield "source must be an object"
    else:
        yield from _field_errors(source, _SOURCE_FIELDS, "source")
        conversation_hash = source.get("conversation_sha256")
        yield from _hash_errors(conversation_hash, "source.conversation_sha256")
        if (
            expected_conversation_sha256 is not None
            and conversation_hash != expected_conversation_sha256
        ):
            yield "source.conversation_sha256 does not match the custodied conversation"
        for field in (
            "authoritative_full_conversation_reattached",
            "original_answer_reattached",
        ):
            if source.get(field) is not True:
                yield f"source.{field} must be true"

    lineage = payload.get("lineage")
    if not isinstance(lineage, Mapping):
        yield "lineage must be an object"
    else:
        yield from _field_errors(lineage, _LINEAGE_FIELDS, "lineage")
        pattern_hash = lineage.get("reasoning_pattern_packet_sha256")
        graph_trace_hash = lineage.get("graph_trace_artifact_sha256")
        routing_hash = lineage.get("routing_projection_sha256")
        yield from _hash_errors(
            pattern_hash, "lineage.reasoning_pattern_packet_sha256"
        )
        yield from _hash_errors(
            graph_trace_hash, "lineage.graph_trace_artifact_sha256"
        )
        yield from _hash_errors(routing_hash, "lineage.routing_projection_sha256")
        graph_version = lineage.get("graph_version")
        if not _nonempty_string(graph_version):
            yield "lineage.graph_version must be a non-empty string"
        if (
            expected_reasoning_pattern_packet_sha256 is not None
            and pattern_hash != expected_reasoning_pattern_packet_sha256
        ):
            yield "lineage.reasoning_pattern_packet_sha256 does not match custody"
        if expected_graph_version is not None and graph_version != expected_graph_version:
            yield "lineage.graph_version does not match custody"
        if (
            expected_graph_trace_artifact_sha256 is not None
            and graph_trace_hash != expected_graph_trace_artifact_sha256
        ):
            yield "lineage.graph_trace_artifact_sha256 does not match custody"
        if (
            expected_routing_projection_sha256 is not None
            and routing_hash != expected_routing_projection_sha256
        ):
            yield "lineage.routing_projection_sha256 does not match custody"

    boundary = payload.get("boundary")
    if not isinstance(boundary, Mapping):
        yield "boundary must be an object"
    else:
        yield from _field_errors(boundary, _BOUNDARY_FIELDS, "boundary")
        for field in sorted(_BOUNDARY_FIELDS):
            if boundary.get(field) is not False:
                yield f"boundary.{field} must be false"

    pressure_items = payload.get("pressure_items")
    pressure_ids: set[str] = set()
    if not isinstance(pressure_items, list):
        yield "pressure_items must be a list"
    else:
        if len(pressure_items) > 4:
            yield "pressure_items must not exceed 4"
        for index, item in enumerate(pressure_items):
            if not isinstance(item, Mapping):
                yield f"pressure_items[{index}] must be an object"
                continue
            yield from _field_errors(item, _PRESSURE_FIELDS, f"pressure_items[{index}]")
            pressure_id = item.get("pressure_id")
            yield from _id_errors(pressure_id, f"pressure_items[{index}].pressure_id")
            if isinstance(pressure_id, str):
                if pressure_id in pressure_ids:
                    yield f"pressure_items[{index}].pressure_id is duplicated"
                pressure_ids.add(pressure_id)
            yield from _id_errors(
                item.get("mechanism_id"), f"pressure_items[{index}].mechanism_id"
            )
            for field in (
                "challenge",
                "applicability_condition",
                "consequence_if_true",
                "set_aside_condition",
            ):
                if not _nonempty_string(item.get(field)):
                    yield f"pressure_items[{index}].{field} must be a non-empty string"
            if item.get("decision_effect") not in ALLOWED_DECISION_EFFECTS:
                yield f"pressure_items[{index}].decision_effect is not allowed"
            yield from _reference_errors(
                item.get("source_event_ids"),
                known=known_source_event_ids,
                path=f"pressure_items[{index}].source_event_ids",
            )
            yield from _reference_errors(
                item.get("graph_trace_refs"),
                known=known_graph_trace_refs,
                path=f"pressure_items[{index}].graph_trace_refs",
            )

    preservation_items = payload.get("preservation_items")
    preservation_ids: set[str] = set()
    if not isinstance(preservation_items, list):
        yield "preservation_items must be a list"
    else:
        if len(preservation_items) > 4:
            yield "preservation_items must not exceed 4"
        for index, item in enumerate(preservation_items):
            if not isinstance(item, Mapping):
                yield f"preservation_items[{index}] must be an object"
                continue
            yield from _field_errors(
                item, _PRESERVATION_FIELDS, f"preservation_items[{index}]"
            )
            preservation_id = item.get("preservation_id")
            yield from _id_errors(
                preservation_id, f"preservation_items[{index}].preservation_id"
            )
            if isinstance(preservation_id, str):
                if preservation_id in preservation_ids:
                    yield f"preservation_items[{index}].preservation_id is duplicated"
                preservation_ids.add(preservation_id)
            for field in ("preserve", "reason"):
                if not _nonempty_string(item.get(field)):
                    yield f"preservation_items[{index}].{field} must be a non-empty string"
            yield from _reference_errors(
                item.get("source_event_ids"),
                known=known_source_event_ids,
                path=f"preservation_items[{index}].source_event_ids",
            )

    yield from _string_list_errors(payload.get("known_limits"), "known_limits")

    contract = payload.get("consideration_contract")
    if not isinstance(contract, Mapping):
        yield "consideration_contract must be an object"
    else:
        yield from _field_errors(contract, _CONSIDERATION_FIELDS, "consideration_contract")
        if contract.get("allowed_dispositions") != ALLOWED_DISPOSITIONS:
            yield "consideration_contract.allowed_dispositions must match the contract"
        for field in (
            "public_surface_must_hide_machinery",
            "every_item_requires_private_disposition",
        ):
            if contract.get(field) is not True:
                yield f"consideration_contract.{field} must be true"

    non_claims = payload.get("non_claims")
    yield from _string_list_errors(non_claims, "non_claims", required_nonempty=True)
    if isinstance(non_claims, list):
        missing = REQUIRED_NON_CLAIMS - set(non_claims)
        for value in sorted(missing):
            yield f"non_claims is missing {value}"


def _field_errors(
    value: Mapping[str, Any], expected: set[str], path: str
) -> Iterable[str]:
    actual = set(value)
    for field in sorted(expected - actual):
        yield f"{path}.{field} is required"
    for field in sorted(actual - expected):
        yield f"{path}.{field} is not allowed"


def _hash_errors(value: object, path: str) -> Iterable[str]:
    if not isinstance(value, str) or not _SHA256_RE.fullmatch(value):
        yield f"{path} must be a prefixed lowercase SHA-256"


def _id_errors(value: object, path: str) -> Iterable[str]:
    if not isinstance(value, str) or not _ID_RE.fullmatch(value):
        yield f"{path} must be a valid identifier"


def _reference_errors(
    value: object, *, known: set[str], path: str
) -> Iterable[str]:
    if not isinstance(value, list) or not value:
        yield f"{path} must be a non-empty list"
        return
    seen: set[str] = set()
    for index, ref in enumerate(value):
        yield from _id_errors(ref, f"{path}[{index}]")
        if not isinstance(ref, str):
            continue
        if ref in seen:
            yield f"{path}[{index}] is duplicated"
        seen.add(ref)
        if ref not in known:
            yield f"{path}[{index}] is not present in the custodied reference set"


def _string_list_errors(
    value: object, path: str, *, required_nonempty: bool = False
) -> Iterable[str]:
    if not isinstance(value, list):
        yield f"{path} must be a list"
        return
    if required_nonempty and not value:
        yield f"{path} must not be empty"
    for index, item in enumerate(value):
        if not _nonempty_string(item):
            yield f"{path}[{index}] must be a non-empty string"


def _nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())
