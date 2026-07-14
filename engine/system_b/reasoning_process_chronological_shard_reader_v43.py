"""Prompt-only role/component alignment correction for stance-object v4.2."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .reasoning_process_chronological_shard_reader_v42 import (
    build_shard_prompts_v42,
    compile_shard_response_recordwise_v42,
    shard_response_schema_v42,
    validate_shard_record_v42,
)
from .reasoning_process_views import sha256_bytes

RESPONSE_SCHEMA_VERSION_V43 = "lolla.reasoning_process_chronological_shard_response.v4_3"
OBSERVATION_SCHEMA_VERSION_V43 = "lolla.reasoning_process_chronological_shard_observation.v4_3"
ROLE_COMPONENT_COVERAGE_INSTRUCTION_V43 = (
    "For every record, each non-empty starting, current, or qualification evidence role must have "
    "at least one stance component with the same temporal role. If starting evidence and a starting "
    "interpretation are empty, return no starting component. This is role coverage, not a request to "
    "strengthen, merge, or invent a stance."
)


def shard_response_schema_v43(view_kind: str) -> dict[str, Any]:
    return shard_response_schema_v42(view_kind)


def build_shard_prompts_v43(wrapper: Mapping[str, Any]) -> dict[str, str]:
    base = build_shard_prompts_v42(wrapper)
    if wrapper["packet"]["view_kind"] != "position_and_decision_trajectory":
        return base
    user_prompt = base["user_prompt"].replace(
        "\nQuestion: ",
        "\nRole-component coverage contract: "
        + ROLE_COMPONENT_COVERAGE_INSTRUCTION_V43
        + "\nQuestion: ",
        1,
    )
    return {
        "system_prompt": base["system_prompt"],
        "user_prompt": user_prompt,
        "system_prompt_sha256": base["system_prompt_sha256"],
        "user_prompt_sha256": sha256_bytes(user_prompt.encode("utf-8")),
    }


def validate_shard_record_v43(
    record: Mapping[str, Any], *, wrapper: Mapping[str, Any]
) -> dict[str, Any]:
    return validate_shard_record_v42(record, wrapper=wrapper)


def compile_shard_response_recordwise_v43(
    *,
    response: Mapping[str, Any],
    wrapper: Mapping[str, Any],
    producer_kind: str,
    producer_id: str,
    record_identity: str,
    call_metadata: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    compiled = compile_shard_response_recordwise_v42(
        response=response,
        wrapper=wrapper,
        producer_kind=producer_kind,
        producer_id=producer_id,
        record_identity=record_identity,
        call_metadata=call_metadata,
    )
    if wrapper["packet"]["view_kind"] != "position_and_decision_trajectory":
        return compiled
    compiled["schema_version"] = RESPONSE_SCHEMA_VERSION_V43
    compiled["status"] = "chronological_shard_v43_record_custody_complete"
    id_map: dict[str, str] = {}
    for observation in compiled["observations"]:
        old_id = observation["observation_id"]
        new_id = old_id.replace("rpshardv42-", "rpshardv43-", 1)
        id_map[old_id] = new_id
        observation["observation_id"] = new_id
        observation["schema_version"] = OBSERVATION_SCHEMA_VERSION_V43
    for custody in compiled["records"]:
        old_id = custody.get("observation_id")
        if old_id in id_map:
            custody["observation_id"] = id_map[old_id]
    compiled["boundary"].update(
        {
            "provider_schema_changed_from_v42": False,
            "record_validator_changed_from_v42": False,
            "role_component_coverage_made_explicit": True,
            "semantic_keyword_gate_added": False,
            "stance_inferred_or_strengthened_by_code": False,
        }
    )
    return compiled
