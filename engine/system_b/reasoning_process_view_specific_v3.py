"""Transfer-ready four-reader envelopes with mechanical custody removed."""
from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from typing import Any

from .conversation_state_candidates import SourceCatalog
from .reasoning_process_view_specific import ViewSpecificInterfaceError
from .reasoning_process_view_specific_v2 import (
    build_prompts_v2,
    response_schema_v2,
    validate_response_v2,
)
from .reasoning_process_view_specific_v2_compile import compile_response_v2
from .reasoning_process_views import canonical_json_bytes, sha256_bytes


SUPPORTED_VIEWS = (
    "position_and_decision_trajectory",
    "evidence_and_assumption_discipline",
    "uncertainty_and_unresolved_state",
    "challenge_and_revision_response",
)
TOP_FIELDS = {"status", "records", "global_limitations"}


def response_schema_v3(view_kind: str) -> dict[str, Any]:
    if view_kind not in SUPPORTED_VIEWS:
        raise ViewSpecificInterfaceError("v3 supports the four non-exploration readers")
    schema = deepcopy(response_schema_v2(view_kind))
    del schema["properties"]["park_unselected_auxiliary_observations"]
    schema["required"].remove("park_unselected_auxiliary_observations")
    schema["description"] += " Deterministic code parks the unselected complement."
    return schema


def build_prompts_v3(wrapper: Mapping[str, Any]) -> dict[str, str]:
    if wrapper["reader_packet"]["view_kind"] not in SUPPORTED_VIEWS:
        raise ViewSpecificInterfaceError("v3 supports the four non-exploration readers")
    return build_prompts_v2(wrapper)


def validate_envelope_v3(
    payload: Mapping[str, Any], *, wrapper: Mapping[str, Any]
) -> dict[str, Any]:
    if set(payload) != TOP_FIELDS:
        raise ViewSpecificInterfaceError("v3 response envelope fields do not match")
    status = payload.get("status")
    records = payload.get("records")
    if status not in {"supported", "mixed", "unclear", "not_found"}:
        raise ViewSpecificInterfaceError("v3 response status is invalid")
    if not isinstance(records, list) or len(records) > 4:
        raise ViewSpecificInterfaceError("v3 response records are invalid")
    if status == "not_found" and records:
        raise ViewSpecificInterfaceError("v3 not_found response must be empty")
    if status != "not_found" and not records:
        raise ViewSpecificInterfaceError("v3 non-empty status requires records")
    if not isinstance(payload.get("global_limitations"), str):
        raise ViewSpecificInterfaceError("v3 global limitations must be a string")
    return {
        "status": "v3_envelope_valid",
        "view_kind": wrapper["reader_packet"]["view_kind"],
        "record_count": len(records),
        "mechanical_parking_model_authored": False,
        "record_semantics_validated": False,
    }


def compile_response_v3_recordwise(
    *,
    response: Mapping[str, Any],
    wrapper: Mapping[str, Any],
    base_ledger: Mapping[str, Any],
    catalog: SourceCatalog,
    record_identity: str,
    producer_kind: str,
    producer_id: str,
    call_metadata: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    envelope = validate_envelope_v3(response, wrapper=wrapper)
    if response["status"] == "not_found":
        expanded = dict(response)
        expanded["park_unselected_auxiliary_observations"] = True
        validate_response_v2(expanded, wrapper=wrapper)
        return {
            "status": "v3_record_level_custody_complete",
            "envelope": envelope,
            "records": [],
            "observations": [],
            "window_terminal_disposition": "reviewed_empty",
            "boundary": {
                "mechanical_parking_added_by_code": True,
                "model_records_changed": False,
                "record_level_validation_weakened": False,
                "semantic_merge_performed": False,
                "global_synthesis_performed": False,
            },
        }
    custody = []
    observations = []
    for index, record in enumerate(response["records"], start=1):
        singleton = {
            "status": "supported",
            "records": [record],
            "park_unselected_auxiliary_observations": True,
            "global_limitations": response["global_limitations"],
        }
        raw_sha = "sha256:" + sha256_bytes(canonical_json_bytes(record))
        try:
            validate_response_v2(singleton, wrapper=wrapper)
            compiled = compile_response_v2(
                response=singleton,
                wrapper=wrapper,
                base_ledger=base_ledger,
                catalog=catalog,
                record_identity=f"{record_identity}-record-{index:02d}",
                producer_kind=producer_kind,
                producer_id=producer_id,
                call_metadata=call_metadata,
            )
            observation = compiled["model_addendum"]["observations"][0]
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
        "status": "v3_record_level_custody_complete",
        "envelope": envelope,
        "records": custody,
        "observations": observations,
        "window_terminal_disposition": (
            "partially_compiled"
            if admitted and quarantined
            else "compiled"
            if admitted
            else "quarantined"
        ),
        "boundary": {
            "mechanical_parking_added_by_code": True,
            "model_records_changed": False,
            "record_level_validation_weakened": False,
            "semantic_merge_performed": False,
            "global_synthesis_performed": False,
        },
    }


def remove_legacy_mechanical_parking(
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    """Replay-only projection; semantic records remain byte-equivalent."""

    if "park_unselected_auxiliary_observations" not in payload:
        raise ViewSpecificInterfaceError("legacy parking field is absent")
    projected = dict(payload)
    del projected["park_unselected_auxiliary_observations"]
    return projected
