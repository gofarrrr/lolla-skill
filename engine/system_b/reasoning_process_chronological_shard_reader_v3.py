"""Modal-force fidelity extension for role-explicit chronological shards."""
from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from typing import Any

from .reasoning_process_chronological_shard_reader_v2 import (
    OBSERVATION_SCHEMA_VERSION_V2,
    RESPONSE_SCHEMA_VERSION_V2,
    build_shard_prompts_v2,
    compile_shard_response_recordwise_v2,
    shard_response_schema_v2,
    validate_shard_record_v2,
)
from .reasoning_process_view_specific import ViewSpecificInterfaceError
from .reasoning_process_views import canonical_json_bytes, sha256_bytes

RESPONSE_SCHEMA_VERSION_V3 = "lolla.reasoning_process_chronological_shard_response.v3"
OBSERVATION_SCHEMA_VERSION_V3 = "lolla.reasoning_process_chronological_shard_observation.v3"

POSITION_FORCE_LABELS = (
    "undecided_or_ambivalent",
    "considering",
    "preference_or_desire",
    "leaning",
    "provisional_plan",
    "decision",
    "commitment",
    "unclear",
    "not_applicable",
)
QUALIFICATION_MODALITY_LABELS = (
    "possibility",
    "concern_or_risk",
    "unresolved_question",
    "condition",
    "constraint",
    "counterpressure",
    "unclear",
)
FORCE_FIELDS = {
    "starting_position_force",
    "current_position_force",
    "qualification_modalities",
    "strength_fidelity_note",
}

FORCE_INSTRUCTION = (
    "Preserve modal and commitment force exactly. Classify the starting and current positions "
    "with the supplied categorical force labels and classify the qualification with one or more "
    "modalities. Explain why the paraphrases do not promote uncertainty, consideration, desire, "
    "preference, leaning, or a provisional plan into insistence, decision, commitment, requirement, "
    "certainty, or totality. The labels are semantic descriptions, not scores or a hierarchy."
)


def shard_response_schema_v3(view_kind: str) -> dict[str, Any]:
    schema = deepcopy(shard_response_schema_v2(view_kind))
    if view_kind != "position_and_decision_trajectory":
        return schema
    record = schema["properties"]["records"]["items"]
    properties = record["properties"]
    properties["starting_position_force"] = {
        "type": "string",
        "enum": list(POSITION_FORCE_LABELS),
        "description": "Categorical source stance for the starting position; not a score or ordinal.",
    }
    properties["current_position_force"] = {
        "type": "string",
        "enum": list(POSITION_FORCE_LABELS[:-1]),
        "description": "Categorical source stance for the current position; not a score or ordinal.",
    }
    properties["qualification_modalities"] = {
        "type": "array",
        "minItems": 1,
        "maxItems": 3,
        "uniqueItems": True,
        "items": {"type": "string", "enum": list(QUALIFICATION_MODALITY_LABELS)},
        "description": "Source modalities carried by the qualification; not confidence or quality labels.",
    }
    properties["strength_fidelity_note"] = {
        "type": "string",
        "minLength": 1,
        "maxLength": 600,
        "description": "Why the role paraphrases preserve the source's modal and commitment force without promotion.",
    }
    record["required"].extend(
        [
            "starting_position_force",
            "current_position_force",
            "qualification_modalities",
            "strength_fidelity_note",
        ]
    )
    schema["description"] += " Position records preserve source modal and commitment force explicitly."
    return schema


def build_shard_prompts_v3(wrapper: Mapping[str, Any]) -> dict[str, str]:
    base = build_shard_prompts_v2(wrapper)
    if wrapper["packet"]["view_kind"] != "position_and_decision_trajectory":
        return base
    user_prompt = base["user_prompt"].replace(
        "\nQuestion: ", "\nModal and commitment-strength contract: " + FORCE_INSTRUCTION + "\nQuestion: "
    )
    return {
        "system_prompt": base["system_prompt"],
        "user_prompt": user_prompt,
        "system_prompt_sha256": base["system_prompt_sha256"],
        "user_prompt_sha256": sha256_bytes(user_prompt.encode("utf-8")),
    }


def validate_shard_record_v3(
    record: Mapping[str, Any], *, wrapper: Mapping[str, Any]
) -> dict[str, Any]:
    view_kind = str(wrapper["packet"]["view_kind"])
    if view_kind != "position_and_decision_trajectory":
        validated = validate_shard_record_v2(record, wrapper=wrapper)
        return {**validated, "force_contract_version": "not_applicable_v2_unchanged"}
    if not FORCE_FIELDS.issubset(record):
        raise ViewSpecificInterfaceError("position force fields are missing")
    projected = {key: value for key, value in record.items() if key not in FORCE_FIELDS}
    validated = validate_shard_record_v2(projected, wrapper=wrapper)
    starting_force = record.get("starting_position_force")
    current_force = record.get("current_position_force")
    modalities = record.get("qualification_modalities")
    note = record.get("strength_fidelity_note")
    errors: list[str] = []
    if starting_force not in POSITION_FORCE_LABELS:
        errors.append("starting position force is invalid")
    if current_force not in POSITION_FORCE_LABELS[:-1]:
        errors.append("current position force is invalid")
    if (
        not isinstance(modalities, list)
        or not modalities
        or len(modalities) > 3
        or len(modalities) != len(set(modalities))
        or not set(modalities).issubset(QUALIFICATION_MODALITY_LABELS)
    ):
        errors.append("qualification modalities are invalid")
    if not isinstance(note, str) or not note.strip() or len(note) > 600:
        errors.append("strength fidelity note is invalid")
    starting_present = bool(record.get("starting_state_evidence_ids")) and bool(
        str(record.get("starting_position_interpretation", "")).strip()
    )
    if starting_present and starting_force == "not_applicable":
        errors.append("starting force cannot be not_applicable when starting state is present")
    if not starting_present and starting_force != "not_applicable":
        errors.append("starting force must be not_applicable when starting state is absent")
    if errors:
        raise ViewSpecificInterfaceError("; ".join(errors))
    return {
        **validated,
        "source_force": {
            "starting_position_force": starting_force,
            "current_position_force": current_force,
            "qualification_modalities": list(modalities),
            "strength_fidelity_note": note,
        },
        "force_contract_version": "categorical_modal_force_v1",
    }


def compile_shard_response_recordwise_v3(
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
    status = response.get("status")
    records = response.get("records")
    if set(response) != {"status", "records", "global_limitations"}:
        raise ViewSpecificInterfaceError("v3 response envelope fields do not match")
    if status not in {"supported", "mixed", "unclear", "not_found"}:
        raise ViewSpecificInterfaceError("v3 response status is invalid")
    if not isinstance(records, list) or len(records) > 2:
        raise ViewSpecificInterfaceError("v3 response records are invalid")
    if status == "not_found" and records:
        raise ViewSpecificInterfaceError("v3 not_found response must be empty")
    if status != "not_found" and not records:
        raise ViewSpecificInterfaceError("v3 non-empty status requires records")
    if not isinstance(response.get("global_limitations"), str):
        raise ViewSpecificInterfaceError("v3 global limitations are invalid")
    observations = []
    custody = []
    for index, record in enumerate(records, start=1):
        digest = sha256_bytes(canonical_json_bytes(record))
        try:
            validated = validate_shard_record_v3(record, wrapper=wrapper)
            observation_id = (
                f"rpshardv3-{wrapper['packet']['case_id']}-"
                f"{wrapper['packet']['view_kind']}-{index:02d}-{digest[:10]}"
            )
            observations.append(
                {
                    "schema_version": OBSERVATION_SCHEMA_VERSION_V3,
                    "observation_id": observation_id,
                    "case_id": wrapper["packet"]["case_id"],
                    "shard_id": wrapper["packet"]["shard_id"],
                    "family": wrapper["packet"]["view_kind"],
                    "interpretation": validated["display_interpretation"],
                    "role_interpretations": validated["role_interpretations"],
                    "source_force": validated["source_force"],
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
        "schema_version": RESPONSE_SCHEMA_VERSION_V3,
        "status": "chronological_shard_v3_record_custody_complete",
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
            "source_force_correctness_inferred_by_code": False,
            "force_labels_compared_or_scored_by_code": False,
            "prose_keyword_gate_added": False,
            "record_level_validation_weakened": False,
            "semantic_merge_performed": False,
            "global_synthesis_performed": False,
            "direct_graph_routing_allowed": False,
        },
    }
