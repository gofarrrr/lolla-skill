"""Atomic one-alias stance-object extension for chronological position shards."""
from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from typing import Any

from .reasoning_process_chronological_shard_reader_v2 import (
    build_shard_prompts_v2,
    compile_shard_response_recordwise_v2,
    shard_response_schema_v2,
    validate_shard_record_v2,
)
from .reasoning_process_chronological_shard_reader_v4 import (
    STANCE_EXPRESSION_KINDS,
    STANCE_OBJECT_KINDS,
)
from .reasoning_process_view_specific import ViewSpecificInterfaceError
from .reasoning_process_views import canonical_json_bytes, sha256_bytes

RESPONSE_SCHEMA_VERSION_V41 = "lolla.reasoning_process_chronological_shard_response.v4_1"
OBSERVATION_SCHEMA_VERSION_V41 = "lolla.reasoning_process_chronological_shard_observation.v4_1"

STANCE_COLUMN_FIELDS_V41 = {
    "stance_temporal_roles",
    "stance_object_kinds",
    "stance_object_interpretations",
    "stance_expression_kinds",
    "stance_source_evidence_ids",
}
STANCE_FIELDS_V41 = {*STANCE_COLUMN_FIELDS_V41, "stance_object_fidelity_note"}
ROLE_EVIDENCE_V41 = {
    "starting": "starting_state_evidence_ids",
    "current": "current_position_evidence_ids",
    "qualification": "qualification_evidence_ids",
}
ROLE_LIMITS_V41 = {
    "starting": (0, 4),
    "current": (1, 5),
    "qualification": (1, 4),
}

STANCE_OBJECT_INSTRUCTION_V41 = (
    "Identify the object of each stance before classifying the expression toward it. Return one "
    "atomic component per object and source alias; source_evidence_id is exactly one alias from the "
    "component's starting, current, or qualification parent role. If two aliases support an object, "
    "split them into two components. Return components as five index-aligned arrays: temporal roles, "
    "object kinds, object interpretations, expression kinds, and source evidence IDs. Index i across "
    "all five arrays is one component. If one alias expresses stances toward two objects, use two "
    "indices sharing that alias. Belief intensity is not a decision; decision means a chosen "
    "action, course, or outcome. A proposal action is distinct from willingness to accept its "
    "result. Reported positions do not imply user endorsement. Preserve uncertainty, conditions, "
    "provisionality, and counterpressure. Categories are descriptions, not scores or a hierarchy. "
    "Explain the decomposition in stance_object_fidelity_note."
)


def _column_schema(*, description: str, enum: list[str] | None = None) -> dict[str, Any]:
    items: dict[str, Any] = {"type": "string"}
    if enum is not None:
        items["enum"] = enum
    return {
        "type": "array",
        "minItems": 2,
        "maxItems": 13,
        "items": items,
        "description": description,
    }


def shard_response_schema_v41(view_kind: str) -> dict[str, Any]:
    schema = deepcopy(shard_response_schema_v2(view_kind))
    if view_kind != "position_and_decision_trajectory":
        return schema
    record = schema["properties"]["records"]["items"]
    properties = record["properties"]
    properties["stance_temporal_roles"] = _column_schema(
        description="Temporal role column; index-aligned with all stance columns.",
        enum=list(ROLE_EVIDENCE_V41),
    )
    properties["stance_object_kinds"] = _column_schema(
        description="Object-kind column; index-aligned with all stance columns.",
        enum=list(STANCE_OBJECT_KINDS),
    )
    properties["stance_object_interpretations"] = _column_schema(
        description="Concise source-faithful object column; index-aligned with all stance columns."
    )
    properties["stance_expression_kinds"] = _column_schema(
        description="Expression-kind column; decision means a chosen course, never belief intensity.",
        enum=list(STANCE_EXPRESSION_KINDS),
    )
    properties["stance_source_evidence_ids"] = _column_schema(
        description="One parent-role source alias per component; index-aligned with all stance columns."
    )
    properties["stance_object_fidelity_note"] = {
        "type": "string",
        "minLength": 1,
        "maxLength": 800,
        "description": "Why the atomic decomposition keeps belief, action, outcome, and acceptance distinct without force inflation.",
    }
    record["required"].extend(
        [
            "stance_temporal_roles",
            "stance_object_kinds",
            "stance_object_interpretations",
            "stance_expression_kinds",
            "stance_source_evidence_ids",
            "stance_object_fidelity_note",
        ]
    )
    schema["description"] += " Position records use shallow atomic one-alias stance columns."
    return schema


def build_shard_prompts_v41(wrapper: Mapping[str, Any]) -> dict[str, str]:
    base = build_shard_prompts_v2(wrapper)
    if wrapper["packet"]["view_kind"] != "position_and_decision_trajectory":
        return base
    user_prompt = base["user_prompt"].replace(
        "\nQuestion: ", "\nAtomic stance-object contract: " + STANCE_OBJECT_INSTRUCTION_V41 + "\nQuestion: "
    )
    return {
        "system_prompt": base["system_prompt"],
        "user_prompt": user_prompt,
        "system_prompt_sha256": base["system_prompt_sha256"],
        "user_prompt_sha256": sha256_bytes(user_prompt.encode("utf-8")),
    }


def _validate_components_v41(
    *, record: Mapping[str, Any], errors: list[str]
) -> list[dict[str, Any]]:
    columns = {field: record.get(field) for field in STANCE_COLUMN_FIELDS_V41}
    if any(not isinstance(value, list) for value in columns.values()):
        errors.append("stance columns must be arrays")
        return []
    lengths = {len(value) for value in columns.values() if isinstance(value, list)}
    if len(lengths) != 1 or not lengths or not 2 <= next(iter(lengths)) <= 13:
        errors.append("stance columns must have equal bounded lengths")
        return []
    validated: list[dict[str, Any]] = []
    digests: list[bytes] = []
    values = zip(
        columns["stance_temporal_roles"],
        columns["stance_object_kinds"],
        columns["stance_object_interpretations"],
        columns["stance_expression_kinds"],
        columns["stance_source_evidence_ids"],
        strict=True,
    )
    for index, (temporal_role, object_kind, interpretation, expression_kind, evidence) in enumerate(values, start=1):
        prefix = f"stance_component[{index}]"
        if temporal_role not in ROLE_EVIDENCE_V41:
            errors.append(f"{prefix} temporal role is invalid")
        if object_kind not in STANCE_OBJECT_KINDS:
            errors.append(f"{prefix} object kind is invalid")
        if expression_kind not in STANCE_EXPRESSION_KINDS:
            errors.append(f"{prefix} expression kind is invalid")
        if (
            not isinstance(interpretation, str)
            or not interpretation.strip()
            or len(interpretation) > 300
        ):
            errors.append(f"{prefix} interpretation is invalid")
        parent_evidence = record.get(ROLE_EVIDENCE_V41.get(temporal_role, ""))
        allowed = set(parent_evidence) if isinstance(parent_evidence, list) else set()
        if not isinstance(evidence, str) or evidence not in allowed:
            errors.append(f"{prefix} evidence is not one parent-role alias")
        normalized = {
            "temporal_role": temporal_role,
            "stance_object_kind": object_kind,
            "stance_object_interpretation": interpretation,
            "stance_expression_kind": expression_kind,
            "source_evidence_id": evidence,
        }
        digest = canonical_json_bytes(normalized)
        if digest in digests:
            errors.append(f"{prefix} exactly duplicates an earlier component")
        digests.append(digest)
        validated.append(normalized)
    return validated


def validate_shard_record_v41(
    record: Mapping[str, Any], *, wrapper: Mapping[str, Any]
) -> dict[str, Any]:
    view_kind = str(wrapper["packet"]["view_kind"])
    if view_kind != "position_and_decision_trajectory":
        validated = validate_shard_record_v2(record, wrapper=wrapper)
        return {**validated, "stance_object_contract_version": "not_applicable_v2_unchanged"}
    if not STANCE_FIELDS_V41.issubset(record):
        raise ViewSpecificInterfaceError("position atomic stance-object fields are missing")
    projected = {key: value for key, value in record.items() if key not in STANCE_FIELDS_V41}
    validated = validate_shard_record_v2(projected, wrapper=wrapper)
    errors: list[str] = []
    components = _validate_components_v41(record=record, errors=errors)
    role_counts = {
        role: sum(component.get("temporal_role") == role for component in components)
        for role in ROLE_EVIDENCE_V41
    }
    for role, (minimum, maximum) in ROLE_LIMITS_V41.items():
        if not minimum <= role_counts[role] <= maximum:
            errors.append(f"{role} stance component count is invalid")
    starting_present = bool(record.get("starting_state_evidence_ids")) and bool(
        str(record.get("starting_position_interpretation", "")).strip()
    )
    if starting_present != bool(role_counts["starting"]):
        errors.append("starting components must be empty or present with the starting role")
    note = record.get("stance_object_fidelity_note")
    if not isinstance(note, str) or not note.strip() or len(note) > 800:
        errors.append("stance object fidelity note is invalid")
    if errors:
        raise ViewSpecificInterfaceError("; ".join(errors))
    return {
        **validated,
        "stance_objects": {
            "stance_components": components,
            "stance_object_fidelity_note": note,
        },
        "stance_object_contract_version": "atomic_one_alias_stance_v1",
    }


def compile_shard_response_recordwise_v41(
    *,
    response: Mapping[str, Any],
    wrapper: Mapping[str, Any],
    producer_kind: str,
    producer_id: str,
    record_identity: str,
    call_metadata: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    if wrapper["packet"]["view_kind"] != "position_and_decision_trajectory":
        return compile_shard_response_recordwise_v2(
            response=response,
            wrapper=wrapper,
            producer_kind=producer_kind,
            producer_id=producer_id,
            record_identity=record_identity,
            call_metadata=call_metadata,
        )
    if set(response) != {"status", "records", "global_limitations"}:
        raise ViewSpecificInterfaceError("v4.1 response envelope fields do not match")
    status = response.get("status")
    records = response.get("records")
    if status not in {"supported", "mixed", "unclear", "not_found"}:
        raise ViewSpecificInterfaceError("v4.1 response status is invalid")
    if not isinstance(records, list) or len(records) > 2:
        raise ViewSpecificInterfaceError("v4.1 response records are invalid")
    if status == "not_found" and records:
        raise ViewSpecificInterfaceError("v4.1 not_found response must be empty")
    if status != "not_found" and not records:
        raise ViewSpecificInterfaceError("v4.1 non-empty status requires records")
    if not isinstance(response.get("global_limitations"), str):
        raise ViewSpecificInterfaceError("v4.1 global limitations are invalid")
    observations = []
    custody = []
    for index, record in enumerate(records, start=1):
        digest = sha256_bytes(canonical_json_bytes(record))
        try:
            validated = validate_shard_record_v41(record, wrapper=wrapper)
            observation_id = (
                f"rpshardv41-{wrapper['packet']['case_id']}-"
                f"{wrapper['packet']['view_kind']}-{index:02d}-{digest[:10]}"
            )
            observations.append(
                {
                    "schema_version": OBSERVATION_SCHEMA_VERSION_V41,
                    "observation_id": observation_id,
                    "case_id": wrapper["packet"]["case_id"],
                    "shard_id": wrapper["packet"]["shard_id"],
                    "family": wrapper["packet"]["view_kind"],
                    "interpretation": validated["display_interpretation"],
                    "role_interpretations": validated["role_interpretations"],
                    "stance_objects": validated["stance_objects"],
                    "semantic_status": validated["status"],
                    "role_source_span_ids": validated["role_source_span_ids"],
                    "source_span_ids": validated["source_span_ids"],
                    "raw_record": {
                        "record_identity": record_identity,
                        "record_index": index,
                        "record": record,
                    },
                    "raw_record_sha256": "sha256:" + digest,
                    "provenance": {
                        "producer_kind": producer_kind,
                        "producer_id": producer_id,
                        "call_id": (call_metadata or {}).get("call_id", ""),
                        "model": (call_metadata or {}).get("model", ""),
                        "prompt_sha256": (call_metadata or {}).get("prompt_sha256", ""),
                    },
                    "terminal_state": "admitted",
                    "graph_routing_eligible": False,
                }
            )
            custody.append(
                {
                    "record_index": index,
                    "terminal_state": "admitted",
                    "observation_id": observation_id,
                    "raw_record_sha256": "sha256:" + digest,
                }
            )
        except Exception as exc:  # noqa: BLE001
            custody.append(
                {
                    "record_index": index,
                    "terminal_state": "quarantined",
                    "reason": f"{type(exc).__name__}: {exc}",
                    "raw_record_sha256": "sha256:" + digest,
                }
            )
    admitted = sum(item["terminal_state"] == "admitted" for item in custody)
    quarantined = len(custody) - admitted
    return {
        "schema_version": RESPONSE_SCHEMA_VERSION_V41,
        "status": "chronological_shard_v41_record_custody_complete",
        "records": custody,
        "observations": observations,
        "shard_terminal_disposition": (
            "reviewed_empty"
            if not custody and status == "not_found"
            else "partially_compiled"
            if admitted and quarantined
            else "compiled"
            if admitted
            else "quarantined"
        ),
        "boundary": {
            "model_records_changed": False,
            "stance_object_correctness_inferred_by_code": False,
            "stance_expression_correctness_inferred_by_code": False,
            "object_expression_compatibility_gate_added": False,
            "expressions_compared_or_scored_by_code": False,
            "prose_keyword_gate_added": False,
            "one_alias_per_component_enforced": True,
            "component_evidence_restricted_to_parent_role": True,
            "record_level_validation_weakened": False,
            "semantic_merge_performed": False,
            "global_synthesis_performed": False,
            "direct_graph_routing_allowed": False,
        },
    }
