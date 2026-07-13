"""Role-first position extraction with exact deterministic joins.

Each model task owns one semantic role: starting position, current position,
or qualification. A fourth task may describe relationships among admitted role
records. Deterministic code validates only shape, source custody, exact IDs,
budgets, and join completeness; it never decides what a role or stance means.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .reasoning_process_chronological_shard_reader_v4 import (
    STANCE_EXPRESSION_KINDS,
    STANCE_OBJECT_KINDS,
)
from .reasoning_process_position_decomposition_v1 import (
    ROLE_COMPONENT_LIMITS,
)
from .reasoning_process_view_specific import (
    ITEM_STATUSES,
    RESPONSE_STATUSES,
    ViewSpecificInterfaceError,
)
from .reasoning_process_views import canonical_json_bytes, sha256_bytes

POSITION_VIEW = "position_and_decision_trajectory"
ROLE_PACKET_SCHEMA = "lolla.reasoning_process_position_role_packet.v2"
ROLE_RESPONSE_SCHEMA = "lolla.reasoning_process_position_role_response.v2"
ROLE_OBSERVATION_SCHEMA = "lolla.reasoning_process_position_role_observation.v2"
RELATION_PACKET_SCHEMA = "lolla.reasoning_process_position_relation_packet.v2"
RELATION_RESPONSE_SCHEMA = "lolla.reasoning_process_position_relation_response.v2"
RELATION_OBSERVATION_SCHEMA = "lolla.reasoning_process_position_relation_observation.v2"
JOIN_SCHEMA = "lolla.reasoning_process_position_role_first_join.v2"
ROLE_ORDER = ("starting", "current", "qualification")

ROLE_QUESTIONS = {
    "starting": (
        "What starting position, attraction, hesitation, or undecided stance is visible before "
        "the current position? Do not infer a start that the source does not show."
    ),
    "current": (
        "What current working position, decision, leaning, plan, or commitment is visible? "
        "Keep proposals, intentions, decisions, and willingness distinct."
    ),
    "qualification": (
        "What qualification, counterpressure, unresolved condition, or reopen reason remains "
        "capable of changing or limiting the current position?"
    ),
}


def _require_position_wrapper(wrapper: Mapping[str, Any]) -> Mapping[str, Any]:
    packet = wrapper.get("packet")
    if not isinstance(packet, Mapping) or packet.get("view_kind") != POSITION_VIEW:
        raise ViewSpecificInterfaceError("role-first extraction requires a position shard")
    return packet


def build_position_role_packet_v2(
    *, wrapper: Mapping[str, Any], role: str
) -> dict[str, Any]:
    packet = _require_position_wrapper(wrapper)
    if role not in ROLE_ORDER:
        raise ViewSpecificInterfaceError("unsupported position role")
    prior_allowed = (
        role == "starting"
        and packet["prior_context"]["role_limited_citation_policy"] == "starting_state_only"
    )
    return {
        "schema_version": ROLE_PACKET_SCHEMA,
        "case_id": packet["case_id"],
        "shard_id": packet["shard_id"],
        "role": role,
        "focal_region": packet["focal_region"],
        "prior_context": packet["prior_context"] if prior_allowed else {
            "included": False,
            "annotated_sentence_text": "",
            "evidence_aliases": [],
            "citation_allowed": False,
            "role_limited_citation_policy": "none",
        },
        "question": ROLE_QUESTIONS[role],
        "maximum_records": 2,
        "maximum_components_per_record": ROLE_COMPONENT_LIMITS[role],
        "valid_empty_output_allowed": True,
        "boundary": {
            "one_semantic_role_only": True,
            "other_role_labels_requested": False,
            "trajectory_relation_requested": False,
            "semantic_prefilter_performed": False,
            "direct_graph_routing_allowed": False,
        },
    }


def position_role_response_schema_v2(role: str) -> dict[str, Any]:
    if role not in ROLE_ORDER:
        raise ViewSpecificInterfaceError("unsupported position role")

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

    properties = {
        "role": {"type": "string", "enum": [role]},
        "status": {"type": "string", "enum": list(ITEM_STATUSES)},
        "evidence_ids": {
            "type": "array",
            "minItems": 1,
            "maxItems": 6,
            "items": {"type": "string", "pattern": "^e[0-9]{3}$"},
        },
        "role_interpretation": {"type": "string", "minLength": 1, "maxLength": 500},
        "object_kinds": column(enum=STANCE_OBJECT_KINDS),
        "object_interpretations": column(),
        "expression_kinds": column(enum=STANCE_EXPRESSION_KINDS),
        "source_evidence_ids": column(pattern="^e[0-9]{3}$"),
        "fidelity_note": {"type": "string", "minLength": 1, "maxLength": 800},
        "limitations": {"type": "string", "maxLength": 500},
    }
    return {
        "type": "object",
        "description": f"At most two source-linked {role} role records.",
        "properties": {
            "status": {"type": "string", "enum": list(RESPONSE_STATUSES)},
            "records": {
                "type": "array",
                "minItems": 0,
                "maxItems": 2,
                "items": {
                    "type": "object",
                    "properties": properties,
                    "required": list(properties),
                    "additionalProperties": False,
                },
            },
            "global_limitations": {"type": "string", "maxLength": 700},
        },
        "required": ["status", "records", "global_limitations"],
        "additionalProperties": False,
    }


def build_position_role_prompts_v2(packet: Mapping[str, Any]) -> dict[str, str]:
    if packet.get("schema_version") != ROLE_PACKET_SCHEMA or packet.get("role") not in ROLE_ORDER:
        raise ViewSpecificInterfaceError("invalid position role packet")
    role = str(packet["role"])
    system_prompt = (
        "You extract one assigned semantic role from a chronological conversation shard. Use only "
        "visible evidence aliases. Preserve ambiguity, conditions, reported positions, and speaker "
        "ownership. A belief is not a decision; a proposal is not acceptance of its outcome. Return "
        "JSON matching the supplied schema."
    )
    user_prompt = (
        "Single-role packet:\n"
        + canonical_json_bytes(packet).decode("utf-8")
        + "\n\nContract: Return only "
        + role
        + " records. Each stance component uses exactly one alias already cited by its role record. "
        "Split distinct objects even when one alias supports both. A valid empty response is better "
        "than inventing the role.\nQuestion: "
        + str(packet["question"])
    )
    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "system_prompt_sha256": sha256_bytes(system_prompt.encode("utf-8")),
        "user_prompt_sha256": sha256_bytes(user_prompt.encode("utf-8")),
    }


def _packet_aliases(packet: Mapping[str, Any]) -> tuple[set[str], dict[str, str]]:
    aliases: set[str] = set()
    text: dict[str, str] = {}
    for region in ("focal_region", "prior_context"):
        value = packet[region]
        aliases.update(value.get("evidence_aliases", []))
        for line in str(value.get("annotated_sentence_text", "")).splitlines():
            alias, separator, source = line.partition("\t")
            if separator and alias in aliases:
                text[alias] = source
    return aliases, text


def _validate_role_record_v2(
    *, record: Mapping[str, Any], packet: Mapping[str, Any]
) -> dict[str, Any]:
    fields = {
        "role",
        "status",
        "evidence_ids",
        "role_interpretation",
        "object_kinds",
        "object_interpretations",
        "expression_kinds",
        "source_evidence_ids",
        "fidelity_note",
        "limitations",
    }
    errors: list[str] = []
    role = str(packet["role"])
    if set(record) != fields:
        errors.append("role record fields do not match contract")
    if record.get("role") != role:
        errors.append("record role does not match packet")
    if record.get("status") not in ITEM_STATUSES:
        errors.append("role record status is invalid")
    allowed_aliases, source_text = _packet_aliases(packet)
    evidence = record.get("evidence_ids")
    if (
        not isinstance(evidence, list)
        or not evidence
        or len(evidence) > 6
        or any(not isinstance(item, str) for item in evidence)
        or len(evidence) != len(set(evidence))
        or not set(evidence).issubset(allowed_aliases)
    ):
        errors.append("role evidence is not a unique visible alias subset")
        evidence = []
    interpretation = record.get("role_interpretation")
    if not isinstance(interpretation, str) or not interpretation.strip() or len(interpretation) > 500:
        errors.append("role interpretation is invalid")
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
        lengths: set[int] = set()
        errors.append("role stance columns must be arrays")
    else:
        lengths = {len(value) for value in columns.values()}
    if len(lengths) != 1 or not lengths or not 1 <= next(iter(lengths)) <= ROLE_COMPONENT_LIMITS[role]:
        errors.append("role stance columns must have equal bounded lengths")
    components = []
    seen: set[bytes] = set()
    if len(lengths) == 1:
        values = zip(
            columns["object_kinds"],
            columns["object_interpretations"],
            columns["expression_kinds"],
            columns["source_evidence_ids"],
            strict=True,
        )
        for index, (object_kind, object_text, expression_kind, alias) in enumerate(values, 1):
            prefix = f"role_component[{index}]"
            if object_kind not in STANCE_OBJECT_KINDS:
                errors.append(f"{prefix} object kind is invalid")
            if expression_kind not in STANCE_EXPRESSION_KINDS:
                errors.append(f"{prefix} expression kind is invalid")
            if not isinstance(object_text, str) or not object_text.strip() or len(object_text) > 300:
                errors.append(f"{prefix} interpretation is invalid")
            if not isinstance(alias, str) or alias not in set(evidence):
                errors.append(f"{prefix} source is not one parent-record alias")
            component = {
                "role": role,
                "stance_object_kind": object_kind,
                "stance_object_interpretation": object_text,
                "stance_expression_kind": expression_kind,
                "source_evidence_id": alias,
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
        "role": role,
        "semantic_status": record["status"],
        "role_interpretation": interpretation,
        "source_evidence_ids": list(evidence),
        "source_evidence": [
            {"alias": alias, "text": source_text[alias]} for alias in evidence
        ],
        "stance_components": components,
        "fidelity_note": note,
        "limitations": limitations,
    }


def compile_position_role_response_v2(
    *,
    response: Mapping[str, Any],
    packet: Mapping[str, Any],
    producer_kind: str,
    producer_id: str,
    call_metadata: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    if packet.get("schema_version") != ROLE_PACKET_SCHEMA:
        raise ViewSpecificInterfaceError("invalid position role packet")
    if set(response) != {"status", "records", "global_limitations"}:
        raise ViewSpecificInterfaceError("role response envelope fields do not match")
    status = response.get("status")
    records = response.get("records")
    if status not in RESPONSE_STATUSES:
        raise ViewSpecificInterfaceError("role response status is invalid")
    if not isinstance(records, list) or len(records) > 2:
        raise ViewSpecificInterfaceError("role response records are invalid")
    if status == "not_found" and records:
        raise ViewSpecificInterfaceError("not_found role response must be empty")
    if status != "not_found" and not records:
        raise ViewSpecificInterfaceError("non-empty role status requires records")
    if not isinstance(response.get("global_limitations"), str) or len(response["global_limitations"]) > 700:
        raise ViewSpecificInterfaceError("role global limitations are invalid")
    observations = []
    custody = []
    for index, record in enumerate(records, 1):
        digest = sha256_bytes(canonical_json_bytes(record))
        try:
            if not isinstance(record, Mapping):
                raise ViewSpecificInterfaceError("role record must be an object")
            validated = _validate_role_record_v2(record=record, packet=packet)
            record_id = f"rprolev2-{packet['role']}-{index:02d}-{digest[:14]}"
            observations.append(
                {
                    "schema_version": ROLE_OBSERVATION_SCHEMA,
                    "observation_id": record_id,
                    "role_record_id": record_id,
                    "source_record_index": index,
                    "case_id": packet["case_id"],
                    "shard_id": packet["shard_id"],
                    **validated,
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
                    "role_record_id": record_id,
                    "terminal_state": "admitted",
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
    admitted = len(observations)
    quarantined = sum(item["terminal_state"] == "quarantined" for item in custody)
    return {
        "schema_version": ROLE_RESPONSE_SCHEMA,
        "status": "position_role_response_custody_complete",
        "role": packet["role"],
        "response_status": status,
        "global_limitations": response["global_limitations"],
        "records": custody,
        "observations": observations,
        "role_terminal_disposition": (
            "reviewed_empty" if not custody and status == "not_found"
            else "partially_compiled" if admitted and quarantined
            else "compiled" if admitted
            else "quarantined"
        ),
        "boundary": {
            "semantic_role_or_category_correctness_inferred_by_code": False,
            "object_expression_compatibility_gate_added": False,
            "prose_keyword_gate_added": False,
            "one_alias_per_component_enforced": True,
            "semantic_merge_performed": False,
            "direct_graph_routing_allowed": False,
        },
    }


def build_position_relation_packet_v2(
    *, role_compiled_by_role: Mapping[str, Mapping[str, Any]]
) -> dict[str, Any]:
    if set(role_compiled_by_role) != set(ROLE_ORDER):
        raise ViewSpecificInterfaceError("relation packet requires all three role dispositions")
    role_records = {}
    case_ids = set()
    shard_ids = set()
    for role in ROLE_ORDER:
        compiled = role_compiled_by_role[role]
        if compiled.get("schema_version") != ROLE_RESPONSE_SCHEMA or compiled.get("role") != role:
            raise ViewSpecificInterfaceError("relation input role compilation is invalid")
        role_records[role] = [
            {
                "role_record_id": item["role_record_id"],
                "role": role,
                "semantic_status": item["semantic_status"],
                "role_interpretation": item["role_interpretation"],
                "source_evidence": item["source_evidence"],
                "limitations": item["limitations"],
            }
            for item in compiled["observations"]
        ]
        case_ids.update(item["case_id"] for item in compiled["observations"])
        shard_ids.update(item["shard_id"] for item in compiled["observations"])
    if len(case_ids) > 1 or len(shard_ids) > 1:
        raise ViewSpecificInterfaceError("relation inputs cross case or shard boundaries")
    current_present = bool(role_records["current"])
    return {
        "schema_version": RELATION_PACKET_SCHEMA,
        "case_id": next(iter(case_ids), ""),
        "shard_id": next(iter(shard_ids), ""),
        "role_records": role_records,
        "call_required": current_present,
        "maximum_input_role_records": 6,
        "maximum_relationship_records": 2,
        "boundary": {
            "role_records_changed": False,
            "categorical_trajectory_label_requested": False,
            "semantic_prefilter_performed": False,
            "deterministic_role_matching_performed": False,
            "direct_graph_routing_allowed": False,
        },
    }


def position_relation_response_schema_v2() -> dict[str, Any]:
    properties = {
        "status": {"type": "string", "enum": list(ITEM_STATUSES)},
        "starting_role_record_id": {"type": "string", "maxLength": 180},
        "current_role_record_id": {"type": "string", "minLength": 1, "maxLength": 180},
        "qualification_role_record_id": {"type": "string", "maxLength": 180},
        "relationship_interpretation": {"type": "string", "minLength": 1, "maxLength": 600},
        "limitations": {"type": "string", "maxLength": 500},
    }
    return {
        "type": "object",
        "description": "At most two exact-ID relationships among independently extracted position roles.",
        "properties": {
            "status": {"type": "string", "enum": list(RESPONSE_STATUSES)},
            "records": {
                "type": "array",
                "minItems": 0,
                "maxItems": 2,
                "items": {
                    "type": "object",
                    "properties": properties,
                    "required": list(properties),
                    "additionalProperties": False,
                },
            },
            "global_limitations": {"type": "string", "maxLength": 700},
        },
        "required": ["status", "records", "global_limitations"],
        "additionalProperties": False,
    }


def build_position_relation_prompts_v2(packet: Mapping[str, Any]) -> dict[str, str]:
    if packet.get("schema_version") != RELATION_PACKET_SCHEMA or not packet.get("call_required"):
        raise ViewSpecificInterfaceError("invalid or empty relation packet")
    system_prompt = (
        "You relate independently extracted starting, current, and qualification records. Use exact "
        "role_record_id values. Do not rewrite, strengthen, or silently reconcile the role records. "
        "Return JSON matching the supplied schema."
    )
    user_prompt = (
        "Role records:\n"
        + canonical_json_bytes(packet).decode("utf-8")
        + "\n\nContract: Link only records that form one source-supported position trajectory. "
        "A starting or qualification ID may be empty when that role is genuinely absent. Do not "
        "return a categorical trajectory label. Preserve disagreement and limitations.\nQuestion: "
        "How do the admitted role records relate over the conversation?"
    )
    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "system_prompt_sha256": sha256_bytes(system_prompt.encode("utf-8")),
        "user_prompt_sha256": sha256_bytes(user_prompt.encode("utf-8")),
    }


def compile_position_relation_response_v2(
    *, response: Mapping[str, Any], packet: Mapping[str, Any], producer_kind: str, producer_id: str
) -> dict[str, Any]:
    if packet.get("schema_version") != RELATION_PACKET_SCHEMA or not packet.get("call_required"):
        raise ViewSpecificInterfaceError("invalid relation packet")
    if set(response) != {"status", "records", "global_limitations"}:
        raise ViewSpecificInterfaceError("relation response envelope fields do not match")
    status = response.get("status")
    records = response.get("records")
    if status not in RESPONSE_STATUSES:
        raise ViewSpecificInterfaceError("relation response status is invalid")
    if not isinstance(records, list) or len(records) > 2:
        raise ViewSpecificInterfaceError("relation response records are invalid")
    if status == "not_found" and records:
        raise ViewSpecificInterfaceError("not_found relation response must be empty")
    if status != "not_found" and not records:
        raise ViewSpecificInterfaceError("non-empty relation status requires records")
    if not isinstance(response.get("global_limitations"), str) or len(response["global_limitations"]) > 700:
        raise ViewSpecificInterfaceError("relation global limitations are invalid")
    allowed = {
        role: {item["role_record_id"] for item in packet["role_records"][role]}
        for role in ROLE_ORDER
    }
    fields = {
        "status",
        "starting_role_record_id",
        "current_role_record_id",
        "qualification_role_record_id",
        "relationship_interpretation",
        "limitations",
    }
    observations = []
    custody = []
    seen: set[tuple[str, str, str]] = set()
    for index, record in enumerate(records, 1):
        digest = sha256_bytes(canonical_json_bytes(record))
        try:
            if not isinstance(record, Mapping) or set(record) != fields:
                raise ViewSpecificInterfaceError("relation record fields do not match contract")
            if record.get("status") not in ITEM_STATUSES:
                raise ViewSpecificInterfaceError("relation record status is invalid")
            starting = record.get("starting_role_record_id")
            current = record.get("current_role_record_id")
            qualification = record.get("qualification_role_record_id")
            if starting and starting not in allowed["starting"]:
                raise ViewSpecificInterfaceError("starting role ID is not in relation packet")
            if current not in allowed["current"]:
                raise ViewSpecificInterfaceError("current role ID is not in relation packet")
            if qualification and qualification not in allowed["qualification"]:
                raise ViewSpecificInterfaceError("qualification role ID is not in relation packet")
            identity = (str(starting), str(current), str(qualification))
            if identity in seen:
                raise ViewSpecificInterfaceError("exact relationship ID tuple is duplicated")
            seen.add(identity)
            interpretation = record.get("relationship_interpretation")
            limitations = record.get("limitations")
            if not isinstance(interpretation, str) or not interpretation.strip() or len(interpretation) > 600:
                raise ViewSpecificInterfaceError("relationship interpretation is invalid")
            if not isinstance(limitations, str) or len(limitations) > 500:
                raise ViewSpecificInterfaceError("relationship limitations are invalid")
            relation_id = f"rprelationv2-{index:02d}-{digest[:14]}"
            observations.append(
                {
                    "schema_version": RELATION_OBSERVATION_SCHEMA,
                    "observation_id": relation_id,
                    "relation_record_id": relation_id,
                    "semantic_status": record["status"],
                    "starting_role_record_id": starting,
                    "current_role_record_id": current,
                    "qualification_role_record_id": qualification,
                    "relationship_interpretation": interpretation,
                    "limitations": limitations,
                    "raw_record_sha256": "sha256:" + digest,
                    "provenance": {"producer_kind": producer_kind, "producer_id": producer_id},
                    "terminal_state": "admitted",
                    "graph_routing_eligible": False,
                }
            )
            custody.append(
                {
                    "record_index": index,
                    "relation_record_id": relation_id,
                    "terminal_state": "admitted",
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
    admitted = len(observations)
    quarantined = sum(item["terminal_state"] == "quarantined" for item in custody)
    return {
        "schema_version": RELATION_RESPONSE_SCHEMA,
        "status": "position_relation_response_custody_complete",
        "records": custody,
        "observations": observations,
        "relation_terminal_disposition": (
            "reviewed_empty" if not custody and status == "not_found"
            else "partially_compiled" if admitted and quarantined
            else "compiled" if admitted
            else "quarantined"
        ),
        "boundary": {
            "semantic_relationship_correctness_inferred_by_code": False,
            "categorical_trajectory_gate_added": False,
            "semantic_role_matching_performed": False,
            "prose_keyword_gate_added": False,
            "direct_graph_routing_allowed": False,
        },
    }


def join_position_role_first_v2(
    *,
    role_compiled_by_role: Mapping[str, Mapping[str, Any]],
    relation_compiled: Mapping[str, Any] | None,
) -> dict[str, Any]:
    if set(role_compiled_by_role) != set(ROLE_ORDER):
        raise ViewSpecificInterfaceError("role-first join requires all role dispositions")
    role_index = {}
    quarantined_role_records = 0
    for role in ROLE_ORDER:
        compiled = role_compiled_by_role[role]
        if compiled.get("schema_version") != ROLE_RESPONSE_SCHEMA or compiled.get("role") != role:
            raise ViewSpecificInterfaceError("role-first join input is invalid")
        role_index[role] = {item["role_record_id"]: item for item in compiled["observations"]}
        quarantined_role_records += sum(
            item["terminal_state"] == "quarantined" for item in compiled["records"]
        )
    joined = []
    referenced = {role: set() for role in ROLE_ORDER}
    quarantined_relations = 0
    if relation_compiled is not None:
        if relation_compiled.get("schema_version") != RELATION_RESPONSE_SCHEMA:
            raise ViewSpecificInterfaceError("relation join input is invalid")
        quarantined_relations = sum(
            item["terminal_state"] == "quarantined" for item in relation_compiled["records"]
        )
        for relation in relation_compiled["observations"]:
            roles = {}
            for role in ROLE_ORDER:
                record_id = relation[f"{role}_role_record_id"]
                observation = role_index[role].get(record_id) if record_id else None
                if record_id:
                    referenced[role].add(record_id)
                roles[role] = observation
            joined.append({"relation_observation": relation, "role_observations": roles})
    unreferenced = {
        role: sorted(set(role_index[role]) - referenced[role]) for role in ROLE_ORDER
    }
    missing_relation = bool(role_index["current"]) and relation_compiled is None
    complete = (
        not quarantined_role_records
        and not quarantined_relations
        and not missing_relation
        and bool(joined)
        and not any(unreferenced.values())
    )
    return {
        "schema_version": JOIN_SCHEMA,
        "status": "position_role_first_join_complete" if complete else "position_role_first_join_incomplete",
        "records": joined,
        "unreferenced_role_record_ids": unreferenced,
        "custody": {
            "quarantined_role_record_count": quarantined_role_records,
            "quarantined_relation_record_count": quarantined_relations,
            "relation_missing_despite_current_role": missing_relation,
        },
        "fan_in": {
            "maximum_provider_calls": 4,
            "maximum_role_records": 6,
            "maximum_relationship_records": 2,
            "actual_role_records": sum(len(value) for value in role_index.values()),
            "actual_relationship_records": len(joined),
        },
        "boundary": {
            "join_keys": ["fixed_role", "role_record_id"],
            "semantic_join_inferred_by_code": False,
            "missing_or_quarantined_records_filled": False,
            "categorical_trajectory_gate_added": False,
            "object_expression_compatibility_gate_added": False,
            "prose_keyword_gate_added": False,
            "global_synthesis_performed": False,
            "direct_graph_routing_allowed": False,
        },
    }
