"""Wire-only Gemini compatibility projection for stance-object v4.1."""
from __future__ import annotations

from copy import deepcopy
from collections.abc import Mapping
from typing import Any

from .reasoning_process_chronological_shard_reader_v41 import (
    build_shard_prompts_v41,
    compile_shard_response_recordwise_v41,
    shard_response_schema_v41,
    validate_shard_record_v41,
)

RESPONSE_SCHEMA_VERSION_V42 = "lolla.reasoning_process_chronological_shard_response.v4_2"
OBSERVATION_SCHEMA_VERSION_V42 = "lolla.reasoning_process_chronological_shard_observation.v4_2"


def _remove_unique_items(value: object) -> int:
    removed = 0
    if isinstance(value, dict):
        if "uniqueItems" in value:
            value.pop("uniqueItems")
            removed += 1
        for child in value.values():
            removed += _remove_unique_items(child)
    elif isinstance(value, list):
        for child in value:
            removed += _remove_unique_items(child)
    return removed


def shard_response_schema_v42(view_kind: str) -> dict[str, Any]:
    schema = deepcopy(shard_response_schema_v41(view_kind))
    if view_kind == "position_and_decision_trajectory":
        removed = _remove_unique_items(schema)
        if removed != 3:
            raise RuntimeError(f"expected three inherited uniqueItems keywords, removed {removed}")
    return schema


def build_shard_prompts_v42(wrapper: Mapping[str, Any]) -> dict[str, str]:
    return build_shard_prompts_v41(wrapper)


def validate_shard_record_v42(
    record: Mapping[str, Any], *, wrapper: Mapping[str, Any]
) -> dict[str, Any]:
    return validate_shard_record_v41(record, wrapper=wrapper)


def compile_shard_response_recordwise_v42(
    *,
    response: Mapping[str, Any],
    wrapper: Mapping[str, Any],
    producer_kind: str,
    producer_id: str,
    record_identity: str,
    call_metadata: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    compiled = compile_shard_response_recordwise_v41(
        response=response,
        wrapper=wrapper,
        producer_kind=producer_kind,
        producer_id=producer_id,
        record_identity=record_identity,
        call_metadata=call_metadata,
    )
    if wrapper["packet"]["view_kind"] != "position_and_decision_trajectory":
        return compiled
    compiled["schema_version"] = RESPONSE_SCHEMA_VERSION_V42
    compiled["status"] = "chronological_shard_v42_record_custody_complete"
    id_map: dict[str, str] = {}
    for observation in compiled["observations"]:
        old_id = observation["observation_id"]
        new_id = old_id.replace("rpshardv41-", "rpshardv42-", 1)
        id_map[old_id] = new_id
        observation["observation_id"] = new_id
        observation["schema_version"] = OBSERVATION_SCHEMA_VERSION_V42
    for custody in compiled["records"]:
        old_id = custody.get("observation_id")
        if old_id in id_map:
            custody["observation_id"] = id_map[old_id]
    compiled["boundary"].update(
        {
            "provider_wire_unique_items_removed": True,
            "semantic_contract_changed_from_v41": False,
            "prompt_changed_from_v41": False,
            "record_validator_changed_from_v41": False,
            "deterministic_duplicate_validation_retained": True,
        }
    )
    return compiled
