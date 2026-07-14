"""Provider-free position/stance decomposition with deterministic custody.

The role-trajectory reader answers only where the position started, where it
currently stands, what still qualifies it, and how those roles relate. Three
bounded stance readers may then classify the objects and expressions inside
one role each. Code validates shape, exact IDs, source aliases, and fan-in; it
does not infer whether a semantic interpretation or category is correct.
"""
from __future__ import annotations

import hashlib
from collections.abc import Mapping
from copy import deepcopy
from typing import Any

from .reasoning_process_chronological_shard_reader_v2 import (
    build_shard_prompts_v2,
    compile_shard_response_recordwise_v2,
    shard_response_schema_v2,
)
from .reasoning_process_chronological_shard_reader_v4 import (
    STANCE_EXPRESSION_KINDS,
    STANCE_OBJECT_KINDS,
)
from .reasoning_process_view_specific import (
    ITEM_STATUSES,
    RESPONSE_STATUSES,
    ViewSpecificInterfaceError,
)
from .reasoning_process_views import canonical_json_bytes, sha256_bytes

POSITION_VIEW = "position_and_decision_trajectory"
DECOMPOSITION_SCHEMA_VERSION = "lolla.reasoning_process_position_decomposition.v1"
TRAJECTORY_RESPONSE_SCHEMA_VERSION = (
    "lolla.reasoning_process_position_role_trajectory_response.v1"
)
TRAJECTORY_OBSERVATION_SCHEMA_VERSION = (
    "lolla.reasoning_process_position_role_trajectory_observation.v1"
)
STANCE_PACKET_SCHEMA_VERSION = "lolla.reasoning_process_position_stance_packet.v1"
STANCE_RESPONSE_SCHEMA_VERSION = "lolla.reasoning_process_position_stance_response.v1"
STANCE_OBSERVATION_SCHEMA_VERSION = (
    "lolla.reasoning_process_position_stance_observation.v1"
)

ROLE_EVIDENCE_FIELDS = {
    "starting": "starting_state_evidence_ids",
    "current": "current_position_evidence_ids",
    "qualification": "qualification_evidence_ids",
}
ROLE_INTERPRETATION_FIELDS = {
    "starting": "starting_position_interpretation",
    "current": "current_position_interpretation",
    "qualification": "qualification_interpretation",
}
ROLE_COMPONENT_LIMITS = {
    "starting": 4,
    "current": 5,
    "qualification": 4,
}


def _require_position_wrapper(wrapper: Mapping[str, Any]) -> None:
    packet = wrapper.get("packet")
    if not isinstance(packet, Mapping) or packet.get("view_kind") != POSITION_VIEW:
        raise ViewSpecificInterfaceError("position decomposition requires a position shard")


def _strip_unique_items(value: object) -> None:
    if isinstance(value, dict):
        value.pop("uniqueItems", None)
        for child in value.values():
            _strip_unique_items(child)
    elif isinstance(value, list):
        for child in value:
            _strip_unique_items(child)


def role_trajectory_response_schema_v1() -> dict[str, Any]:
    """Return the shallow role-trajectory schema without provider-specific keywords."""
    schema = deepcopy(shard_response_schema_v2(POSITION_VIEW))
    _strip_unique_items(schema)
    schema["description"] = (
        "At most two position trajectories. This task excludes stance-object classification."
    )
    return schema


def build_role_trajectory_prompts_v1(wrapper: Mapping[str, Any]) -> dict[str, str]:
    """Use the already reviewed role-explicit prompt, now as a standalone task."""
    _require_position_wrapper(wrapper)
    return build_shard_prompts_v2(wrapper)


def compile_role_trajectory_response_v1(
    *,
    response: Mapping[str, Any],
    wrapper: Mapping[str, Any],
    producer_kind: str,
    producer_id: str,
    record_identity: str,
    call_metadata: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Compile role trajectories and give every admitted record an exact join ID."""
    _require_position_wrapper(wrapper)
    compiled = compile_shard_response_recordwise_v2(
        response=response,
        wrapper=wrapper,
        producer_kind=producer_kind,
        producer_id=producer_id,
        record_identity=record_identity,
        call_metadata=call_metadata,
    )
    observations: list[dict[str, Any]] = []
    id_by_index: dict[int, str] = {}
    for observation in compiled["observations"]:
        raw = observation["raw_record"]
        index = int(raw["record_index"])
        digest = str(observation["raw_record_sha256"]).removeprefix("sha256:")
        trajectory_id = (
            f"rptrajv1-{wrapper['packet']['case_id']}-{index:02d}-{digest[:12]}"
        )
        id_by_index[index] = trajectory_id
        observations.append(
            {
                **observation,
                "schema_version": TRAJECTORY_OBSERVATION_SCHEMA_VERSION,
                "observation_id": trajectory_id,
                "trajectory_record_id": trajectory_id,
            }
        )
    custody = []
    for item in compiled["records"]:
        updated = dict(item)
        index = int(item["record_index"])
        if index in id_by_index:
            updated["observation_id"] = id_by_index[index]
            updated["trajectory_record_id"] = id_by_index[index]
        custody.append(updated)
    return {
        "schema_version": TRAJECTORY_RESPONSE_SCHEMA_VERSION,
        "status": "position_role_trajectory_custody_complete",
        "response_status": response["status"],
        "global_limitations": response["global_limitations"],
        "records": custody,
        "observations": observations,
        "shard_terminal_disposition": compiled["shard_terminal_disposition"],
        "boundary": {
            "semantic_role_correctness_inferred_by_code": False,
            "stance_object_task_included": False,
            "model_records_changed": False,
            "join_identity_added_by_code": True,
            "direct_graph_routing_allowed": False,
        },
    }


def _annotated_text_by_alias(wrapper: Mapping[str, Any]) -> dict[str, str]:
    text: dict[str, str] = {}
    for region in ("focal_region", "prior_context"):
        annotated = str(wrapper["packet"].get(region, {}).get("annotated_sentence_text", ""))
        for line in annotated.splitlines():
            alias, separator, value = line.partition("\t")
            if separator and alias.startswith("e") and alias[1:].isdigit():
                text[alias] = value
    return text


def build_stance_role_packet_v1(
    *,
    trajectory_compiled: Mapping[str, Any],
    wrapper: Mapping[str, Any],
    role: str,
) -> dict[str, Any]:
    """Build one role-only packet spanning at most two trajectory records."""
    _require_position_wrapper(wrapper)
    if role not in ROLE_EVIDENCE_FIELDS:
        raise ViewSpecificInterfaceError("unsupported stance role")
    if trajectory_compiled.get("schema_version") != TRAJECTORY_RESPONSE_SCHEMA_VERSION:
        raise ViewSpecificInterfaceError("invalid role-trajectory compilation")
    alias_metadata = {
        item["alias"]: item
        for item in [*wrapper["focal_alias_map"], *wrapper["context_alias_map"]]
    }
    source_text = _annotated_text_by_alias(wrapper)
    records = []
    evidence_field = ROLE_EVIDENCE_FIELDS[role]
    interpretation_field = ROLE_INTERPRETATION_FIELDS[role]
    for observation in trajectory_compiled["observations"]:
        raw_record = observation["raw_record"]["record"]
        aliases = list(raw_record[evidence_field])
        if not aliases:
            continue
        evidence = []
        for alias in aliases:
            metadata = alias_metadata.get(alias)
            value = source_text.get(alias)
            if metadata is None or value is None:
                raise ViewSpecificInterfaceError("trajectory evidence lacks exact source custody")
            if hashlib.sha256(value.encode("utf-8")).hexdigest() != metadata["text_sha256"]:
                raise ViewSpecificInterfaceError("annotated evidence text hash mismatch")
            evidence.append(
                {
                    "alias": alias,
                    "span_id": metadata["span_id"],
                    "speaker": metadata["speaker"],
                    "turn_index": metadata["turn_index"],
                    "text": value,
                    "text_sha256": metadata["text_sha256"],
                }
            )
        records.append(
            {
                "trajectory_record_id": observation["trajectory_record_id"],
                "role_interpretation": raw_record[interpretation_field],
                "trajectory_type": raw_record["trajectory_type"],
                "trajectory_interpretation": raw_record["trajectory_interpretation"],
                "evidence": evidence,
            }
        )
    if len(records) > 2:
        raise ViewSpecificInterfaceError("stance role packet exceeds two trajectory records")
    packet = {
        "schema_version": STANCE_PACKET_SCHEMA_VERSION,
        "case_id": wrapper["packet"]["case_id"],
        "shard_id": wrapper["packet"]["shard_id"],
        "role": role,
        "records": records,
        "call_required": bool(records),
        "maximum_response_records": len(records),
        "maximum_components_per_record": ROLE_COMPONENT_LIMITS[role],
        "boundary": {
            "other_roles_included": False,
            "semantic_prefilter_performed": False,
            "role_or_category_correctness_inferred_by_code": False,
            "source_text_hash_verified": True,
            "direct_graph_routing_allowed": False,
        },
    }
    return packet


def stance_role_response_schema_v1(role: str) -> dict[str, Any]:
    if role not in ROLE_EVIDENCE_FIELDS:
        raise ViewSpecificInterfaceError("unsupported stance role")

    def column(*, enum: tuple[str, ...] | None = None, pattern: str | None = None) -> dict[str, Any]:
        items: dict[str, Any] = {"type": "string"}
        if enum is not None:
            items["enum"] = list(enum)
        if pattern is not None:
            items["pattern"] = pattern
        return {
            "type": "array",
            "minItems": 1,
            "maxItems": ROLE_COMPONENT_LIMITS[role],
            "items": items,
        }

    record_properties = {
        "trajectory_record_id": {"type": "string", "minLength": 1, "maxLength": 180},
        "role": {"type": "string", "enum": [role]},
        "status": {"type": "string", "enum": list(ITEM_STATUSES)},
        "object_kinds": column(enum=STANCE_OBJECT_KINDS),
        "object_interpretations": column(),
        "expression_kinds": column(enum=STANCE_EXPRESSION_KINDS),
        "source_evidence_ids": column(pattern="^e[0-9]{3}$"),
        "fidelity_note": {"type": "string", "minLength": 1, "maxLength": 800},
        "limitations": {"type": "string", "maxLength": 500},
    }
    return {
        "type": "object",
        "description": f"Object and expression extraction for the {role} role only.",
        "properties": {
            "status": {"type": "string", "enum": list(RESPONSE_STATUSES)},
            "records": {
                "type": "array",
                "minItems": 0,
                "maxItems": 2,
                "items": {
                    "type": "object",
                    "properties": record_properties,
                    "required": list(record_properties),
                    "additionalProperties": False,
                },
            },
            "global_limitations": {"type": "string", "maxLength": 700},
        },
        "required": ["status", "records", "global_limitations"],
        "additionalProperties": False,
    }


def build_stance_role_prompts_v1(packet: Mapping[str, Any]) -> dict[str, str]:
    if packet.get("schema_version") != STANCE_PACKET_SCHEMA_VERSION:
        raise ViewSpecificInterfaceError("invalid stance role packet")
    if not packet.get("call_required"):
        raise ViewSpecificInterfaceError("empty stance role packet does not authorize a call")
    role = str(packet["role"])
    system_prompt = (
        "You extract source-faithful stance objects from one explicitly assigned temporal role. "
        "Use only supplied evidence. Preserve uncertainty and provisionality. A belief is not a "
        "decision, a proposed action is not acceptance of its outcome, and reported positions do "
        "not imply endorsement. Return JSON matching the supplied schema."
    )
    user_prompt = (
        "Role-only packet:\n"
        + canonical_json_bytes(packet).decode("utf-8")
        + "\n\nContract: For each trajectory_record_id, return atomic index-aligned object, "
        "expression, and one-alias source columns for this role only. Do not infer or copy other "
        "roles. Categories describe the source; they do not score it.\nQuestion: What distinct "
        f"objects and stance expressions are visible in the {role} evidence?"
    )
    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "system_prompt_sha256": sha256_bytes(system_prompt.encode("utf-8")),
        "user_prompt_sha256": sha256_bytes(user_prompt.encode("utf-8")),
    }


def _validate_stance_record(
    *, record: Mapping[str, Any], packet: Mapping[str, Any]
) -> dict[str, Any]:
    expected_fields = {
        "trajectory_record_id",
        "role",
        "status",
        "object_kinds",
        "object_interpretations",
        "expression_kinds",
        "source_evidence_ids",
        "fidelity_note",
        "limitations",
    }
    errors: list[str] = []
    if set(record) != expected_fields:
        errors.append("stance record fields do not match contract")
    role = packet["role"]
    if record.get("role") != role:
        errors.append("stance record role does not match packet")
    if record.get("status") not in ITEM_STATUSES:
        errors.append("stance record status is invalid")
    expected = {item["trajectory_record_id"]: item for item in packet["records"]}
    trajectory_id = record.get("trajectory_record_id")
    target = expected.get(trajectory_id)
    if target is None:
        errors.append("trajectory_record_id is not in the role packet")
    columns = {
        name: record.get(name)
        for name in (
            "object_kinds",
            "object_interpretations",
            "expression_kinds",
            "source_evidence_ids",
        )
    }
    if any(not isinstance(value, list) for value in columns.values()):
        errors.append("stance component columns must be arrays")
        lengths: set[int] = set()
    else:
        lengths = {len(value) for value in columns.values()}
    maximum = ROLE_COMPONENT_LIMITS[role]
    if len(lengths) != 1 or not lengths or not 1 <= next(iter(lengths)) <= maximum:
        errors.append("stance component columns must have equal bounded lengths")
    components = []
    seen: set[bytes] = set()
    allowed_aliases = {
        item["alias"] for item in target["evidence"]
    } if target is not None else set()
    if len(lengths) == 1:
        values = zip(
            columns["object_kinds"],
            columns["object_interpretations"],
            columns["expression_kinds"],
            columns["source_evidence_ids"],
            strict=True,
        )
        for index, (object_kind, interpretation, expression_kind, evidence) in enumerate(values, 1):
            prefix = f"stance_component[{index}]"
            if object_kind not in STANCE_OBJECT_KINDS:
                errors.append(f"{prefix} object kind is invalid")
            if expression_kind not in STANCE_EXPRESSION_KINDS:
                errors.append(f"{prefix} expression kind is invalid")
            if not isinstance(interpretation, str) or not interpretation.strip() or len(interpretation) > 300:
                errors.append(f"{prefix} interpretation is invalid")
            if not isinstance(evidence, str) or evidence not in allowed_aliases:
                errors.append(f"{prefix} evidence is not one role-packet alias")
            component = {
                "role": role,
                "stance_object_kind": object_kind,
                "stance_object_interpretation": interpretation,
                "stance_expression_kind": expression_kind,
                "source_evidence_id": evidence,
            }
            digest = canonical_json_bytes(component)
            if digest in seen:
                errors.append(f"{prefix} exactly duplicates an earlier component")
            seen.add(digest)
            components.append(component)
    note = record.get("fidelity_note")
    if not isinstance(note, str) or not note.strip() or len(note) > 800:
        errors.append("fidelity note is invalid")
    limitations = record.get("limitations")
    if not isinstance(limitations, str) or len(limitations) > 500:
        errors.append("limitations are invalid")
    if errors:
        raise ViewSpecificInterfaceError("; ".join(errors))
    return {
        "trajectory_record_id": trajectory_id,
        "role": role,
        "semantic_status": record["status"],
        "stance_components": components,
        "fidelity_note": note,
        "limitations": limitations,
    }


def compile_stance_role_response_v1(
    *,
    response: Mapping[str, Any],
    packet: Mapping[str, Any],
    producer_kind: str,
    producer_id: str,
    call_metadata: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Compile one role response recordwise and preserve missing/quarantined IDs."""
    if packet.get("schema_version") != STANCE_PACKET_SCHEMA_VERSION or not packet.get("call_required"):
        raise ViewSpecificInterfaceError("invalid or empty stance role packet")
    if set(response) != {"status", "records", "global_limitations"}:
        raise ViewSpecificInterfaceError("stance response envelope fields do not match")
    status = response.get("status")
    records = response.get("records")
    if status not in RESPONSE_STATUSES:
        raise ViewSpecificInterfaceError("stance response status is invalid")
    if not isinstance(records, list) or len(records) > 2:
        raise ViewSpecificInterfaceError("stance response records are invalid")
    if status == "not_found" and records:
        raise ViewSpecificInterfaceError("not_found stance response must be empty")
    if status != "not_found" and not records:
        raise ViewSpecificInterfaceError("non-empty stance status requires records")
    if not isinstance(response.get("global_limitations"), str) or len(response["global_limitations"]) > 700:
        raise ViewSpecificInterfaceError("stance global limitations are invalid")
    expected_ids = {item["trajectory_record_id"] for item in packet["records"]}
    supplied_ids: set[str] = set()
    admitted_ids: set[str] = set()
    observations = []
    custody = []
    for index, record in enumerate(records, 1):
        digest = sha256_bytes(canonical_json_bytes(record))
        supplied_id = record.get("trajectory_record_id") if isinstance(record, Mapping) else None
        duplicate_id = isinstance(supplied_id, str) and supplied_id in supplied_ids
        if isinstance(supplied_id, str):
            supplied_ids.add(supplied_id)
        try:
            if not isinstance(record, Mapping):
                raise ViewSpecificInterfaceError("stance record must be an object")
            if duplicate_id:
                raise ViewSpecificInterfaceError("trajectory_record_id is duplicated in response")
            validated = _validate_stance_record(record=record, packet=packet)
            trajectory_id = validated["trajectory_record_id"]
            admitted_ids.add(trajectory_id)
            observation_id = f"rpstancev1-{packet['role']}-{digest[:14]}"
            observations.append(
                {
                    "schema_version": STANCE_OBSERVATION_SCHEMA_VERSION,
                    "observation_id": observation_id,
                    **validated,
                    "case_id": packet["case_id"],
                    "shard_id": packet["shard_id"],
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
                    "trajectory_record_id": trajectory_id,
                    "terminal_state": "admitted",
                    "observation_id": observation_id,
                    "raw_record_sha256": "sha256:" + digest,
                }
            )
        except Exception as exc:  # noqa: BLE001
            custody.append(
                {
                    "record_index": index,
                    "trajectory_record_id": supplied_id if isinstance(supplied_id, str) else "",
                    "terminal_state": "quarantined",
                    "reason": f"{type(exc).__name__}: {exc}",
                    "raw_record_sha256": "sha256:" + digest,
                }
            )
    missing_ids = sorted(expected_ids - admitted_ids - {
        item["trajectory_record_id"]
        for item in custody
        if item["terminal_state"] == "quarantined" and item["trajectory_record_id"] in expected_ids
    })
    admitted = len(observations)
    quarantined = sum(item["terminal_state"] == "quarantined" for item in custody)
    return {
        "schema_version": STANCE_RESPONSE_SCHEMA_VERSION,
        "status": "position_stance_role_custody_complete",
        "role": packet["role"],
        "response_status": status,
        "global_limitations": response["global_limitations"],
        "records": custody,
        "observations": observations,
        "missing_trajectory_record_ids": missing_ids,
        "role_terminal_disposition": (
            "compiled" if admitted == len(expected_ids) and not quarantined
            else "partially_compiled" if admitted
            else "quarantined" if quarantined
            else "reviewed_empty"
        ),
        "boundary": {
            "semantic_category_correctness_inferred_by_code": False,
            "object_expression_compatibility_gate_added": False,
            "prose_keyword_gate_added": False,
            "one_alias_per_component_enforced": True,
            "evidence_restricted_to_role_packet": True,
            "semantic_merge_performed": False,
            "direct_graph_routing_allowed": False,
        },
    }


def join_position_decomposition_v1(
    *,
    trajectory_compiled: Mapping[str, Any],
    stance_compiled_by_role: Mapping[str, Mapping[str, Any] | None],
) -> dict[str, Any]:
    """Join only by exact trajectory IDs and fixed roles; preserve every gap."""
    if trajectory_compiled.get("schema_version") != TRAJECTORY_RESPONSE_SCHEMA_VERSION:
        raise ViewSpecificInterfaceError("invalid trajectory compilation for join")
    unknown_roles = set(stance_compiled_by_role) - set(ROLE_EVIDENCE_FIELDS)
    if unknown_roles:
        raise ViewSpecificInterfaceError("join contains unsupported stance roles")
    stance_index: dict[str, dict[str, Any]] = {}
    quarantine_index: dict[str, set[str]] = {}
    for role, compiled in stance_compiled_by_role.items():
        if compiled is None:
            continue
        if compiled.get("schema_version") != STANCE_RESPONSE_SCHEMA_VERSION or compiled.get("role") != role:
            raise ViewSpecificInterfaceError("stance compilation role or schema mismatch")
        stance_index[role] = {
            item["trajectory_record_id"]: item for item in compiled["observations"]
        }
        quarantine_index[role] = {
            item["trajectory_record_id"]
            for item in compiled["records"]
            if item["terminal_state"] == "quarantined" and item["trajectory_record_id"]
        }
    joined = []
    counts = {"admitted": 0, "missing": 0, "quarantined": 0, "not_applicable": 0}
    applicable_roles: set[str] = set()
    for trajectory in trajectory_compiled["observations"]:
        trajectory_id = trajectory["trajectory_record_id"]
        raw = trajectory["raw_record"]["record"]
        roles: dict[str, Any] = {}
        for role, evidence_field in ROLE_EVIDENCE_FIELDS.items():
            if not raw[evidence_field]:
                disposition = "not_applicable"
                stance = None
            else:
                applicable_roles.add(role)
                stance = stance_index.get(role, {}).get(trajectory_id)
                if stance is not None:
                    disposition = "admitted"
                elif trajectory_id in quarantine_index.get(role, set()):
                    disposition = "quarantined"
                else:
                    disposition = "missing"
            counts[disposition] += 1
            roles[role] = {"disposition": disposition, "stance_observation": stance}
        joined.append(
            {
                "trajectory_record_id": trajectory_id,
                "trajectory_observation": trajectory,
                "stance_by_role": roles,
            }
        )
    planned_calls = 1 + len(applicable_roles) if trajectory_compiled["observations"] else 1
    return {
        "schema_version": DECOMPOSITION_SCHEMA_VERSION,
        "status": (
            "position_decomposition_complete"
            if counts["missing"] == 0 and counts["quarantined"] == 0
            else "position_decomposition_incomplete"
        ),
        "records": joined,
        "role_disposition_counts": counts,
        "fan_in": {
            "trajectory_records": len(joined),
            "applicable_roles": sorted(applicable_roles),
            "planned_call_count": planned_calls,
            "maximum_call_count": 4,
            "maximum_joined_stance_records": 6,
            "within_budget": planned_calls <= 4 and len(joined) <= 2,
        },
        "boundary": {
            "join_keys": ["trajectory_record_id", "fixed_role"],
            "semantic_join_inferred_by_code": False,
            "missing_or_quarantined_roles_filled": False,
            "object_expression_compatibility_gate_added": False,
            "prose_keyword_gate_added": False,
            "global_synthesis_performed": False,
            "direct_graph_routing_allowed": False,
        },
    }
