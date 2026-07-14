"""Targeted exploration-only contract after v2's remaining minority miss."""
from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from typing import Any

from .reasoning_process_view_specific import ViewSpecificInterfaceError
from .reasoning_process_view_specific_v2 import (
    response_schema_v2,
    validate_response_v2,
)
from .reasoning_process_views import canonical_json_bytes, sha256_bytes


VIEW_KIND = "exploration_and_alternatives"


def response_schema_v3() -> dict[str, Any]:
    """Remove model authority over the mechanically parked complement."""

    schema = deepcopy(response_schema_v2(VIEW_KIND))
    schema["description"] = "Chronological exploration read with deterministic complement custody."
    del schema["properties"]["park_unselected_auxiliary_observations"]
    schema["required"].remove("park_unselected_auxiliary_observations")
    return schema


def validate_response_v3(
    payload: Mapping[str, Any], *, wrapper: Mapping[str, Any]
) -> dict[str, Any]:
    if wrapper["reader_packet"]["view_kind"] != VIEW_KIND:
        raise ViewSpecificInterfaceError("v3 is exploration-only")
    if "park_unselected_auxiliary_observations" in payload:
        raise ViewSpecificInterfaceError("mechanical parking field must not be model-authored")
    expanded = dict(payload)
    expanded["park_unselected_auxiliary_observations"] = True
    validated = validate_response_v2(expanded, wrapper=wrapper)
    validated["mechanical_complement_parking_added_by_code"] = True
    return validated


def build_prompts_v3(wrapper: Mapping[str, Any]) -> dict[str, str]:
    packet = wrapper["reader_packet"]
    if packet["view_kind"] != VIEW_KIND:
        raise ViewSpecificInterfaceError("v3 is exploration-only")
    system_prompt = (
        "You are a bounded reasoning-process reader. Inspect only exploration and "
        "alternatives; do not score quality or the final answer. Scan the complete "
        "annotated conversation chronologically from the earliest turn to the latest. "
        "Return up to four materially distinct alternatives, including earlier "
        "testable paths even when the conversation later preferred another direction. "
        "For each alternative, state its specifically attached condition, limit, "
        "tradeoff, or failure condition and cite that relationship with visible aliases. "
        "Do not replace an attached limit with a different general risk. Use only aliases "
        "such as e001; never invent or reproduce source quotes. The auxiliary ledger is "
        "fallible context, and deterministic code—not you—keeps every unselected item "
        "parked and recoverable."
    )
    user_prompt = (
        "Question: Which materially distinct alternatives were explored across the full "
        "chronology, and what specific condition or limit accompanied each one?\n\n"
        "Reader packet:\n"
        + canonical_json_bytes(packet).decode("utf-8")
    )
    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "system_prompt_sha256": sha256_bytes(system_prompt.encode("utf-8")),
        "user_prompt_sha256": sha256_bytes(user_prompt.encode("utf-8")),
    }
