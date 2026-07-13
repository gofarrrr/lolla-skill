"""Provider-free Google-schema projection for the frozen R3 pressure proof.

The failed R3 request remains immutable.  This module creates a prospective
provider-facing projection that uses only the JSON Schema keywords documented
for Gemini structured output as of 2026-07-13.  Deterministic code restores
redundant portfolio identity fields and enforces lengths and cross-field
business rules after generation; it never decides whether pressure is useful.
"""

from __future__ import annotations

import copy
import json
from collections.abc import Mapping
from typing import Any

from .r3_fresh_consumer import (
    ALLOWED_DISPOSITIONS,
    EFFECTS,
    MAX_PROVIDER_COST_USD,
    R3FreshConsumerError,
    build_prompts,
    compile_pressure_response,
    maximum_estimated_call_cost_usd,
    text_sha256,
    validate_pressure_bundle,
    validate_pressure_packet,
    value_sha256,
)


PROJECTION_SCHEMA = "lolla.r3_google_schema_projection.v1"
PROJECTION_BUNDLE_SCHEMA = "lolla.r3_google_schema_projection_bundle.v1"
PROJECTION_COMPILED_SCHEMA = "lolla.r3_google_schema_projection_compiled.v1"
LINT_SCHEMA = "lolla.google_documented_schema_subset_lint.v1"

REQUIRED_ROW_TEXT_MAX = 520
BOUNDARY_TEXT_MAX = 420
EFFECT_TEXT_MAX = 420
RECONSIDERED_ANSWER_MAX = 6000
CHANGE_SUMMARY_MAX = 1200

ROW_FIELDS = (
    "pressure_id",
    "disposition",
    "source_turn_numbers",
    "effect",
    "strongest_plausible_application",
    "attempted_application_condition",
    "why",
    "disposition_boundary",
    "visible_effect",
    "private_guardrail",
)
TOP_FIELDS = (
    "candidate_dispositions",
    "reconsidered_answer",
    "change_summary",
    "original_answer_preservation",
)

_COMMON_SCHEMA_KEYS = frozenset({"type", "title", "description"})
_TYPE_SCHEMA_KEYS = {
    "object": frozenset({"properties", "required", "additionalProperties"}),
    "string": frozenset({"enum", "format"}),
    "number": frozenset({"enum", "minimum", "maximum"}),
    "integer": frozenset({"enum", "minimum", "maximum"}),
    "boolean": frozenset(),
    "array": frozenset({"items", "prefixItems", "minItems", "maxItems"}),
    "null": frozenset(),
}


class R3GoogleProjectionError(RuntimeError):
    """Raised when the prospective Google projection loses custody."""


def _without(value: Mapping[str, Any], *fields: str) -> dict[str, Any]:
    return {key: item for key, item in value.items() if key not in fields}


def _text(value: Any) -> str:
    return str(value or "").strip()


def _property_count(schema: Any) -> int:
    if isinstance(schema, Mapping):
        own = len(schema.get("properties", {})) if isinstance(schema.get("properties"), Mapping) else 0
        return own + sum(_property_count(item) for item in schema.values())
    if isinstance(schema, list):
        return sum(_property_count(item) for item in schema)
    return 0


def _schema_depth(schema: Any, depth: int = 0) -> int:
    if not isinstance(schema, Mapping):
        return depth
    children: list[int] = []
    properties = schema.get("properties")
    if isinstance(properties, Mapping):
        children.extend(_schema_depth(item, depth + 1) for item in properties.values())
    items = schema.get("items")
    if isinstance(items, Mapping):
        children.append(_schema_depth(items, depth + 1))
    prefix = schema.get("prefixItems")
    if isinstance(prefix, list):
        children.extend(_schema_depth(item, depth + 1) for item in prefix)
    additional = schema.get("additionalProperties")
    if isinstance(additional, Mapping):
        children.append(_schema_depth(additional, depth + 1))
    return max([depth, *children])


def _keyword_counts(schema: Any) -> dict[str, int]:
    counts: dict[str, int] = {}

    def visit(value: Any, *, inside_properties: bool = False) -> None:
        if isinstance(value, Mapping):
            for key, item in value.items():
                if not inside_properties:
                    counts[str(key)] = counts.get(str(key), 0) + 1
                visit(item, inside_properties=key == "properties")
        elif isinstance(value, list):
            for item in value:
                visit(item)

    visit(schema)
    return dict(sorted(counts.items()))


def schema_metrics(schema: Mapping[str, Any]) -> dict[str, Any]:
    """Return descriptive, non-quality metrics for one provider schema."""

    keyword_counts = _keyword_counts(schema)
    return {
        "canonical_bytes": len(
            json.dumps(
                schema,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ),
        "total_object_properties": _property_count(schema),
        "schema_structural_depth": _schema_depth(schema),
        "keyword_counts": keyword_counts,
        "string_length_constraint_count": keyword_counts.get("minLength", 0)
        + keyword_counts.get("maxLength", 0),
        "pattern_constraint_count": keyword_counts.get("pattern", 0),
        "unique_items_constraint_count": keyword_counts.get("uniqueItems", 0),
    }


def lint_google_documented_schema_subset(
    schema: Mapping[str, Any],
) -> dict[str, Any]:
    """Lint against the currently documented Gemini structured-output subset.

    This is a local compatibility preflight, not proof that a provider will
    accept the schema.  It deliberately rejects undocumented keywords even if
    an older or smaller request happened to work with them.
    """

    errors: list[dict[str, str]] = []

    def error(path: str, code: str, detail: str) -> None:
        errors.append({"path": path or "/", "code": code, "detail": detail})

    def walk(node: Any, path: str) -> None:
        if not isinstance(node, Mapping):
            error(path, "schema_node_not_object", "Every schema node must be an object.")
            return
        schema_type = node.get("type")
        if schema_type not in _TYPE_SCHEMA_KEYS:
            error(path, "unsupported_or_missing_type", f"Unsupported type: {schema_type!r}")
            allowed = _COMMON_SCHEMA_KEYS
        else:
            allowed = _COMMON_SCHEMA_KEYS | _TYPE_SCHEMA_KEYS[str(schema_type)]
        for key in node:
            if key not in allowed:
                error(
                    f"{path}/{key}",
                    "undocumented_keyword",
                    f"{key} is not in the documented subset for {schema_type}.",
                )
        properties = node.get("properties")
        if schema_type == "object":
            if not isinstance(properties, Mapping):
                error(f"{path}/properties", "properties_missing", "Object properties are required.")
                properties = {}
            for name, child in properties.items():
                walk(child, f"{path}/properties/{name}")
            required = node.get("required")
            if not isinstance(required, list) or any(
                not isinstance(item, str) for item in required
            ):
                error(f"{path}/required", "required_invalid", "required must be a string array.")
            elif set(required) - set(properties):
                error(
                    f"{path}/required",
                    "required_unknown_property",
                    "required names must exist in properties.",
                )
            additional = node.get("additionalProperties")
            if not isinstance(additional, (bool, Mapping)):
                error(
                    f"{path}/additionalProperties",
                    "additional_properties_invalid",
                    "additionalProperties must be boolean or a schema.",
                )
            elif isinstance(additional, Mapping):
                walk(additional, f"{path}/additionalProperties")
        if schema_type == "array":
            items = node.get("items")
            prefix = node.get("prefixItems")
            if items is None and prefix is None:
                error(f"{path}/items", "array_items_missing", "Array item schema is required.")
            if items is not None:
                walk(items, f"{path}/items")
            if prefix is not None:
                if not isinstance(prefix, list):
                    error(
                        f"{path}/prefixItems",
                        "prefix_items_invalid",
                        "prefixItems must be an array of schemas.",
                    )
                else:
                    for index, child in enumerate(prefix):
                        walk(child, f"{path}/prefixItems/{index}")

    walk(schema, "")
    return {
        "schema_version": LINT_SCHEMA,
        "status": "pass_documented_subset" if not errors else "fail_documented_subset",
        "source_snapshot": {
            "as_of_date": "2026-07-13",
            "google_structured_output_docs": (
                "https://ai.google.dev/gemini-api/docs/structured-output"
            ),
            "documented_string_keywords": ["enum", "format"],
            "documented_object_keywords": [
                "properties",
                "required",
                "additionalProperties",
            ],
            "documented_array_keywords": [
                "items",
                "prefixItems",
                "minItems",
                "maxItems",
            ],
            "documented_number_keywords": ["enum", "minimum", "maximum"],
        },
        "errors": errors,
        "metrics": schema_metrics(schema),
        "provider_acceptance_proven": False,
    }


def projected_response_json_schema(packet: Mapping[str, Any]) -> dict[str, Any]:
    validate_pressure_packet(packet)
    active = packet["constitutional_graph_survival"]["active_pressure_items"]
    maximum_turn = max(packet["source_turn_numbers"])
    row_properties: dict[str, Any] = {
        "pressure_id": {
            "type": "string",
            "description": "Exact pressure_id from the matching packet row, in packet order.",
        },
        "disposition": {
            "type": "string",
            "enum": ["apply", "reject", "park"],
            "description": "Current disposition of this intentionally noisy pressure hypothesis.",
        },
        "source_turn_numbers": {
            "type": "array",
            "minItems": 1,
            "maxItems": 6,
            "items": {"type": "integer", "minimum": 1, "maximum": maximum_turn},
            "description": "Exact supplied conversation turns supporting this disposition.",
        },
        "effect": {
            "type": "string",
            "enum": sorted(EFFECTS),
            "description": "The bounded effect earned by the disposition.",
        },
        "strongest_plausible_application": {
            "type": "string",
            "description": "Strongest good-faith source-grounded use before dispositioning.",
        },
        "attempted_application_condition": {
            "type": "string",
            "description": "Condition that would have to hold for the application to be sound.",
        },
        "why": {
            "type": "string",
            "description": "Source-grounded reason for apply, reject, or park.",
        },
        "disposition_boundary": {
            "type": "string",
            "description": (
                "Failed condition for reject; exact reopen or falsifier condition for apply or park."
            ),
        },
        "visible_effect": {
            "type": "string",
            "description": "Public answer effect for apply, otherwise an empty string.",
        },
        "private_guardrail": {
            "type": "string",
            "description": "Private reasoning guardrail for apply, otherwise an empty string.",
        },
    }
    row = {
        "type": "object",
        "properties": row_properties,
        "required": list(ROW_FIELDS),
        "additionalProperties": False,
    }
    top_properties: dict[str, Any] = {
        "candidate_dispositions": {
            "type": "array",
            "minItems": len(active),
            "maxItems": len(active),
            "items": row,
            "description": "One disposition for every active pressure, exactly in packet order.",
        },
        "reconsidered_answer": {
            "type": "string",
            "description": "Self-contained answer containing only earned friction.",
        },
        "change_summary": {
            "type": "string",
            "description": "Concise factual account of what changed or remained unchanged.",
        },
        "original_answer_preservation": {
            "type": "string",
            "enum": ["preserved", "partially_changed", "replaced"],
            "description": "Honest classification of original useful advice preservation.",
        },
    }
    schema = {
        "type": "object",
        "properties": top_properties,
        "required": list(TOP_FIELDS),
        "additionalProperties": False,
    }
    lint = lint_google_documented_schema_subset(schema)
    if lint["status"] != "pass_documented_subset":
        raise R3GoogleProjectionError("projected schema escaped documented subset")
    return schema


def build_projected_prompts(packet: Mapping[str, Any]) -> dict[str, str]:
    base = build_prompts(packet)
    system = base["system_prompt"]
    user = (
        base["user_prompt"]
        + "\n\nPROVIDER WIRE PROJECTION: Return the compact schema fields exactly. "
        "For each row, disposition_boundary is the failed condition when rejecting and "
        "the exact reopen or falsifier condition when applying or parking. Do not echo "
        "model_id, risk_if_forced, or risk_if_ignored; deterministic code restores those "
        "unchanged from the matching pressure item after validating pressure_id and packet "
        "order. Text lengths and disposition-specific field combinations are validated "
        "locally after generation."
    )
    return {
        "system_prompt": system,
        "user_prompt": user,
        "system_prompt_sha256": text_sha256(system),
        "user_prompt_sha256": text_sha256(user),
    }


def build_projected_request_body(base_bundle: Mapping[str, Any]) -> dict[str, Any]:
    validate_pressure_bundle(base_bundle)
    packet = base_bundle["packet"]
    prompts = build_projected_prompts(packet)
    schema = projected_response_json_schema(packet)
    body = copy.deepcopy(base_bundle["request_body"])
    body["messages"] = [
        {"role": "system", "content": prompts["system_prompt"]},
        {"role": "user", "content": prompts["user_prompt"]},
    ]
    body["response_format"] = {
        "type": "json_schema",
        "json_schema": {
            "name": "lolla_r3_google_schema_projection",
            "strict": True,
            "schema": schema,
        },
    }
    return body


def _bounded_text(
    value: Any,
    *,
    field: str,
    maximum: int,
    allow_empty: bool,
) -> str:
    if not isinstance(value, str):
        raise R3GoogleProjectionError(f"{field} must be text")
    if not allow_empty and not value.strip():
        raise R3GoogleProjectionError(f"{field} is required")
    if len(value) > maximum:
        raise R3GoogleProjectionError(f"{field} exceeds local length boundary")
    return value


def compile_projected_pressure_response(
    *, response: Mapping[str, Any], packet: Mapping[str, Any]
) -> dict[str, Any]:
    """Restore the canonical R3 response after strict local validation."""

    validate_pressure_packet(packet)
    if set(response) != set(TOP_FIELDS):
        raise R3GoogleProjectionError("projected response envelope is invalid")
    active = packet["constitutional_graph_survival"]["active_pressure_items"]
    observed = response.get("candidate_dispositions")
    if not isinstance(observed, list) or len(observed) != len(active):
        raise R3GoogleProjectionError("projected response lacks exact active coverage")
    valid_turns = set(packet["source_turn_numbers"])
    canonical_rows: list[dict[str, Any]] = []
    restoration_rows: list[dict[str, Any]] = []
    for index, (row, expected) in enumerate(zip(observed, active)):
        prefix = f"candidate_dispositions[{index}]"
        if not isinstance(row, Mapping) or set(row) != set(ROW_FIELDS):
            raise R3GoogleProjectionError(f"{prefix} shape is invalid")
        if row.get("pressure_id") != expected["pressure_id"]:
            raise R3GoogleProjectionError(f"{prefix} pressure identity or order drifted")
        disposition = row.get("disposition")
        effect = row.get("effect")
        if disposition not in ALLOWED_DISPOSITIONS or effect not in EFFECTS:
            raise R3GoogleProjectionError(f"{prefix} disposition or effect is invalid")
        turns = row.get("source_turn_numbers")
        if (
            not isinstance(turns, list)
            or not turns
            or len(turns) > 6
            or any(not isinstance(turn, int) or isinstance(turn, bool) for turn in turns)
            or len(turns) != len(set(turns))
            or set(turns) - valid_turns
        ):
            raise R3GoogleProjectionError(f"{prefix} source-turn custody is invalid")
        strongest = _bounded_text(
            row.get("strongest_plausible_application"),
            field=f"{prefix}.strongest_plausible_application",
            maximum=REQUIRED_ROW_TEXT_MAX,
            allow_empty=False,
        )
        attempted = _bounded_text(
            row.get("attempted_application_condition"),
            field=f"{prefix}.attempted_application_condition",
            maximum=REQUIRED_ROW_TEXT_MAX,
            allow_empty=False,
        )
        why = _bounded_text(
            row.get("why"),
            field=f"{prefix}.why",
            maximum=REQUIRED_ROW_TEXT_MAX,
            allow_empty=False,
        )
        boundary = _bounded_text(
            row.get("disposition_boundary"),
            field=f"{prefix}.disposition_boundary",
            maximum=BOUNDARY_TEXT_MAX,
            allow_empty=False,
        )
        visible = _bounded_text(
            row.get("visible_effect"),
            field=f"{prefix}.visible_effect",
            maximum=EFFECT_TEXT_MAX,
            allow_empty=True,
        )
        private = _bounded_text(
            row.get("private_guardrail"),
            field=f"{prefix}.private_guardrail",
            maximum=EFFECT_TEXT_MAX,
            allow_empty=True,
        )
        if disposition == "apply":
            if effect == "no_material_effect" or not (visible or private):
                raise R3GoogleProjectionError(
                    f"{prefix} apply requires material effect custody"
                )
            failed_condition = ""
            reopen_condition = boundary
        elif disposition == "reject":
            if effect != "no_material_effect" or visible or private:
                raise R3GoogleProjectionError(
                    f"{prefix} reject cannot claim a material effect"
                )
            failed_condition = boundary
            reopen_condition = ""
        else:
            if effect != "no_material_effect" or visible or private:
                raise R3GoogleProjectionError(
                    f"{prefix} park cannot claim a material effect"
                )
            failed_condition = ""
            reopen_condition = boundary
        canonical_rows.append(
            {
                "pressure_id": expected["pressure_id"],
                "model_id": expected["model_id"],
                "disposition": disposition,
                "source_turn_numbers": list(turns),
                "effect": effect,
                "strongest_plausible_application": strongest,
                "attempted_application_condition": attempted,
                "why": why,
                "failed_condition": failed_condition,
                "reopen_condition": reopen_condition,
                "visible_effect": visible,
                "private_guardrail": private,
                "risk_if_forced": expected["force_boundary"],
                "risk_if_ignored": expected["ignore_boundary"],
            }
        )
        restoration_rows.append(
            {
                "pressure_id": expected["pressure_id"],
                "model_id_source": "packet.active_pressure_items.model_id",
                "risk_if_forced_source": "packet.active_pressure_items.force_boundary",
                "risk_if_ignored_source": "packet.active_pressure_items.ignore_boundary",
                "boundary_mapping": (
                    "failed_condition" if disposition == "reject" else "reopen_condition"
                ),
            }
        )
    canonical_response = {
        "candidate_dispositions": canonical_rows,
        "reconsidered_answer": _bounded_text(
            response.get("reconsidered_answer"),
            field="reconsidered_answer",
            maximum=RECONSIDERED_ANSWER_MAX,
            allow_empty=False,
        ),
        "change_summary": _bounded_text(
            response.get("change_summary"),
            field="change_summary",
            maximum=CHANGE_SUMMARY_MAX,
            allow_empty=False,
        ),
        "original_answer_preservation": response.get("original_answer_preservation"),
    }
    compiled = compile_pressure_response(response=canonical_response, packet=packet)
    compiled["provider_projection"] = {
        "schema_version": PROJECTION_COMPILED_SCHEMA,
        "projection_schema_version": PROJECTION_SCHEMA,
        "provider_supplied_row_fields": list(ROW_FIELDS),
        "deterministically_restored_fields": [
            "model_id",
            "risk_if_forced",
            "risk_if_ignored",
            "failed_condition_or_reopen_condition_name",
        ],
        "restoration_rows": restoration_rows,
        "semantic_applicability_inferred_by_code": False,
        "keyword_or_chronology_gate_added": False,
    }
    return compiled


def build_projection_bundle(
    *,
    base_bundle: Mapping[str, Any],
    operational_reference: Mapping[str, Any],
) -> dict[str, Any]:
    validate_pressure_bundle(base_bundle)
    if not isinstance(operational_reference, Mapping) or not operational_reference:
        raise R3GoogleProjectionError("operational schema reference is required")
    packet = base_bundle["packet"]
    schema = projected_response_json_schema(packet)
    lint = lint_google_documented_schema_subset(schema)
    prompts = build_projected_prompts(packet)
    body = build_projected_request_body(base_bundle)
    maximum_cost = maximum_estimated_call_cost_usd(body)
    if maximum_cost > MAX_PROVIDER_COST_USD:
        raise R3GoogleProjectionError("projected request exceeds the one-cent envelope")
    bundle: dict[str, Any] = {
        "schema_version": PROJECTION_BUNDLE_SCHEMA,
        "status": "provider_free_repair_ready_not_authorized",
        "case_id": base_bundle["case_id"],
        "base_r3_bundle_sha256": base_bundle["bundle_sha256"],
        "packet": copy.deepcopy(packet),
        "prompts": prompts,
        "response_schema": schema,
        "documented_subset_lint": lint,
        "request_body": body,
        "request_contract": {
            **copy.deepcopy(base_bundle["request_contract"]),
            "maximum_estimated_call_cost_usd": maximum_cost,
            "wire_projection": PROJECTION_SCHEMA,
            "provider_calls_authorized": 0,
        },
        "schema_comparison": {
            "failed_r3_schema": schema_metrics(base_bundle["response_schema"]),
            "projected_schema": schema_metrics(schema),
            "operational_smaller_reference": dict(operational_reference),
            "interpretation": (
                "The projection removes undocumented constraints and redundant generated "
                "fields. The historical success is operational evidence only, not proof "
                "that any particular keyword caused the R3 failure."
            ),
        },
        "compiler_contract": {
            "canonical_compiler_reused": True,
            "text_lengths_enforced_locally": True,
            "cross_field_disposition_rules_enforced_locally": True,
            "portfolio_identity_restored_locally": True,
            "portfolio_force_and_ignore_boundaries_restored_locally": True,
            "semantic_applicability_inferred_by_code": False,
            "candidate_deletion_allowed": False,
        },
        "hashes": {
            "packet_sha256": packet["packet_sha256"],
            "system_prompt_sha256": prompts["system_prompt_sha256"],
            "user_prompt_sha256": prompts["user_prompt_sha256"],
            "response_schema_sha256": value_sha256(schema),
            "request_body_sha256": value_sha256(body),
        },
        "provider_calls_made": 0,
        "next_call_authorized": False,
    }
    bundle["bundle_sha256"] = value_sha256(bundle)
    validate_projection_bundle(bundle, base_bundle=base_bundle)
    return bundle


def validate_projection_bundle(
    bundle: Mapping[str, Any], *, base_bundle: Mapping[str, Any]
) -> None:
    validate_pressure_bundle(base_bundle)
    if bundle.get("schema_version") != PROJECTION_BUNDLE_SCHEMA:
        raise R3GoogleProjectionError("projection bundle schema is invalid")
    if bundle.get("status") != "provider_free_repair_ready_not_authorized":
        raise R3GoogleProjectionError("projection bundle status is invalid")
    observed = bundle.get("bundle_sha256")
    if observed != value_sha256(_without(bundle, "bundle_sha256")):
        raise R3GoogleProjectionError("projection bundle hash is invalid")
    if bundle.get("base_r3_bundle_sha256") != base_bundle["bundle_sha256"]:
        raise R3GoogleProjectionError("base R3 bundle identity drifted")
    if bundle.get("packet") != base_bundle["packet"]:
        raise R3GoogleProjectionError("projection packet drifted from frozen R3")
    schema = projected_response_json_schema(base_bundle["packet"])
    prompts = build_projected_prompts(base_bundle["packet"])
    body = build_projected_request_body(base_bundle)
    lint = lint_google_documented_schema_subset(schema)
    if (
        bundle.get("response_schema") != schema
        or bundle.get("prompts") != prompts
        or bundle.get("request_body") != body
        or bundle.get("documented_subset_lint") != lint
    ):
        raise R3GoogleProjectionError("projection schema, prompt, body, or lint drifted")
    expected_hashes = {
        "packet_sha256": base_bundle["packet"]["packet_sha256"],
        "system_prompt_sha256": prompts["system_prompt_sha256"],
        "user_prompt_sha256": prompts["user_prompt_sha256"],
        "response_schema_sha256": value_sha256(schema),
        "request_body_sha256": value_sha256(body),
    }
    if bundle.get("hashes") != expected_hashes:
        raise R3GoogleProjectionError("projection hash custody is invalid")
    contract = bundle.get("request_contract")
    if not isinstance(contract, Mapping):
        raise R3GoogleProjectionError("projection request contract is missing")
    expected_contract = {
        **copy.deepcopy(base_bundle["request_contract"]),
        "maximum_estimated_call_cost_usd": maximum_estimated_call_cost_usd(body),
        "wire_projection": PROJECTION_SCHEMA,
        "provider_calls_authorized": 0,
    }
    if contract != expected_contract:
        raise R3GoogleProjectionError("projection request contract drifted")
    comparison = bundle.get("schema_comparison")
    if not isinstance(comparison, Mapping) or set(comparison) != {
        "failed_r3_schema",
        "projected_schema",
        "operational_smaller_reference",
        "interpretation",
    }:
        raise R3GoogleProjectionError("projection schema comparison is invalid")
    if (
        comparison.get("failed_r3_schema") != schema_metrics(base_bundle["response_schema"])
        or comparison.get("projected_schema") != schema_metrics(schema)
        or not isinstance(comparison.get("operational_smaller_reference"), Mapping)
        or not _text(comparison.get("interpretation"))
    ):
        raise R3GoogleProjectionError("projection schema comparison drifted")
    expected_compiler_contract = {
        "canonical_compiler_reused": True,
        "text_lengths_enforced_locally": True,
        "cross_field_disposition_rules_enforced_locally": True,
        "portfolio_identity_restored_locally": True,
        "portfolio_force_and_ignore_boundaries_restored_locally": True,
        "semantic_applicability_inferred_by_code": False,
        "candidate_deletion_allowed": False,
    }
    if bundle.get("compiler_contract") != expected_compiler_contract:
        raise R3GoogleProjectionError("projection compiler contract drifted")
    if maximum_estimated_call_cost_usd(body) > MAX_PROVIDER_COST_USD:
        raise R3GoogleProjectionError("projection request exceeds one-cent envelope")
    if bundle.get("provider_calls_made") != 0 or bundle.get("next_call_authorized") is not False:
        raise R3GoogleProjectionError("projection bundle accidentally authorizes provider work")


def assert_failed_r3_contract_unchanged(base_bundle: Mapping[str, Any]) -> None:
    """Make the historical non-mutation boundary explicit for tests/builders."""

    try:
        validate_pressure_bundle(base_bundle)
    except R3FreshConsumerError as exc:
        raise R3GoogleProjectionError("failed R3 contract was mutated") from exc
