"""Prospective record-level custody for local exploration responses."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .reasoning_process_exploration_local import (
    TOP_FIELDS,
    ViewSpecificInterfaceError,
    compile_local_response,
    validate_local_response,
)
from .reasoning_process_views import canonical_json_bytes, sha256_bytes


def validate_local_response_envelope(
    payload: Mapping[str, Any], *, wrapper: Mapping[str, Any]
) -> dict[str, Any]:
    """Validate only response-level invariants; records retain separate custody."""

    if set(payload) != TOP_FIELDS:
        raise ViewSpecificInterfaceError("local response envelope fields do not match")
    status = payload.get("status")
    records = payload.get("records")
    if status not in {"supported", "unclear", "not_found"}:
        raise ViewSpecificInterfaceError("local response envelope status is invalid")
    if not isinstance(records, list) or len(records) > 2:
        raise ViewSpecificInterfaceError("local response envelope records are invalid")
    if status == "not_found" and records:
        raise ViewSpecificInterfaceError("not_found local response must be empty")
    if status == "supported" and not records:
        raise ViewSpecificInterfaceError("supported local response requires records")
    if not isinstance(payload.get("global_limitations"), str):
        raise ViewSpecificInterfaceError("local global limitations must be a string")
    return {
        "status": "local_response_envelope_valid",
        "window_id": wrapper["packet"]["window_id"],
        "record_count": len(records),
        "record_semantics_validated": False,
    }


def compile_local_response_recordwise(
    *,
    response: Mapping[str, Any],
    wrapper: Mapping[str, Any],
    producer_kind: str,
    producer_id: str,
    record_identity: str,
    call_metadata: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Admit valid records and quarantine invalid siblings without changing either."""

    envelope = validate_local_response_envelope(response, wrapper=wrapper)
    if response["status"] == "not_found":
        compiled = compile_local_response(
            response=response,
            wrapper=wrapper,
            producer_kind=producer_kind,
            producer_id=producer_id,
            record_identity=record_identity,
            call_metadata=call_metadata,
        )
        return {
            "status": "record_level_custody_complete",
            "envelope": envelope,
            "observations": [],
            "records": [],
            "window_terminal_disposition": compiled["window_terminal_disposition"],
            "boundary": {
                "model_records_changed": False,
                "record_level_validation_weakened": False,
                "semantic_merge_performed": False,
                "global_synthesis_performed": False,
            },
        }
    observations = []
    custody = []
    for index, record in enumerate(response["records"], start=1):
        singleton = {
            "status": "supported",
            "records": [record],
            "global_limitations": response["global_limitations"],
        }
        raw_sha = "sha256:" + sha256_bytes(canonical_json_bytes(record))
        try:
            validate_local_response(singleton, wrapper=wrapper)
            compiled = compile_local_response(
                response=singleton,
                wrapper=wrapper,
                producer_kind=producer_kind,
                producer_id=producer_id,
                record_identity=f"{record_identity}-record-{index:02d}",
                call_metadata=call_metadata,
            )
            observation = compiled["observations"][0]
            observations.append(observation)
            custody.append(
                {
                    "record_index": index,
                    "terminal_state": "admitted",
                    "observation_id": observation["observation_id"],
                    "raw_record_sha256": raw_sha,
                }
            )
        except Exception as exc:  # noqa: BLE001
            custody.append(
                {
                    "record_index": index,
                    "terminal_state": "quarantined",
                    "reason": f"{type(exc).__name__}: {exc}",
                    "raw_record_sha256": raw_sha,
                }
            )
    admitted = sum(item["terminal_state"] == "admitted" for item in custody)
    quarantined = len(custody) - admitted
    return {
        "status": "record_level_custody_complete",
        "envelope": envelope,
        "observations": observations,
        "records": custody,
        "window_terminal_disposition": (
            "partially_compiled"
            if admitted and quarantined
            else "compiled"
            if admitted
            else "quarantined"
        ),
        "boundary": {
            "model_records_changed": False,
            "record_level_validation_weakened": False,
            "semantic_merge_performed": False,
            "global_synthesis_performed": False,
        },
    }
