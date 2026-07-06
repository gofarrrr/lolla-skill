"""Selected-run learning packet contract for Observatory Teacher integration.

This module validates the product-safe packet that will let Observatory mount
Mental Model Teacher as a selected-run learning mode. It composes existing
Teacher product objects and adds tab ownership, receipts, and non-claim
guardrails. It does not read archives, build packets, render UI, call providers,
run Lolla, or wire runtime behavior.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .mental_model_teacher_product_contracts import (
    MentalModelTeacherContractError,
    validate_mental_model_page,
    validate_relation_page,
    validate_teacher_lesson,
    validate_visual_graph,
)


LEARNING_PACKET_SCHEMA_VERSION = "lolla.observatory_teacher.learning_packet.v0"

PRIMARY_TABS = ("Outcome", "Learn", "Models", "Relations", "Map", "Receipts")
ADVANCED_SURFACE = "Advanced"
ALLOWED_DEFAULT_TABS = {"Outcome", "Learn"}
ALLOWED_RUN_SOURCES = {"current", "archive", "contract_fixture"}
ALLOWED_RECEIPT_EXPOSURES = {"receipts", "advanced_only"}
ALLOWED_RECEIPT_HOME_TABS = {"Receipts", ADVANCED_SURFACE}
ALLOWED_MISSINGNESS_STATUSES = {
    "complete",
    "partial",
    "missing",
    "not_applicable",
    "needs_review",
}

REQUIRED_SINGLE_HOME_RULES = {
    "revised_answer": "Outcome",
    "structural_pressure_findings": "Outcome",
    "teacher_reasoning_move": "Learn",
    "canonical_model_explanation": "Models",
    "model_activation_evidence": "Outcome",
    "relation_explanation": "Relations",
    "graph_neighborhood": "Map",
    "source_custody": "Receipts",
    "usage_cost_telemetry": ADVANCED_SURFACE,
    "graph_survival_evals": ADVANCED_SURFACE,
}

REQUIRED_VISIBILITY_POLICY = {
    "raw_telemetry_in_primary_tabs": False,
    "raw_canonical_markdown_in_primary_tabs": False,
    "review_controls_in_learn_tab": False,
    "advanced_telemetry_separate": True,
    "receipts_custody_not_proof": True,
    "graph_edges_navigation_not_proof": True,
}

REQUIRED_PACKET_NON_CLAIMS = {
    "not_product_proof",
    "not_human_validation",
    "not_answer_correctness",
    "not_advice_correctness",
    "not_runtime_integration",
    "not_action_authorization",
    "learning_packet_is_not_runtime_wiring",
    "receipts_are_custody_not_proof",
    "telemetry_is_advanced_not_primary",
    "graph_is_navigation_not_proof",
}

RAW_PRIVATE_MARKERS = (
    "/" + "Users/",
    "Desktop/" + "Apps",
    "\\" + "Users\\",
    "SEC" + "RET",
    "api" + "_key",
    "client" + "_sec" + "ret",
    "OPEN" + "ROUTER" + "_API" + "_KEY",
    "OPEN" + "AI" + "_API" + "_KEY",
    "raw_message" + "_content",
    "provider_reasoning" + "_details",
)

FORBIDDEN_PACKET_KEYS = {
    "answer_quality_score",
    "advice_quality_score",
    "approval_status",
    "certification_status",
    "certified",
    "judge_score",
    "llm_judge_winner",
    "runtime_hook",
    "runtime_write_authorized",
    "safe_for_agent_use",
    "winner",
}


class MentalModelTeacherLearningPacketError(MentalModelTeacherContractError):
    """Raised when an Observatory learning packet is unsafe or malformed."""


def validate_learning_packet(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Validate a product-safe selected-run Teacher learning packet."""

    data = _copy_mapping(payload)
    _require_schema(data, LEARNING_PACKET_SCHEMA_VERSION)
    _require_fields(
        data,
        {
            "schema_version",
            "packet_id",
            "run_ref",
            "observatory_tabs",
            "default_tab",
            "lesson",
            "models",
            "relations",
            "graph",
            "receipts",
            "single_home_rules",
            "visibility_policy",
            "missingness",
            "non_claims",
            "product_proof",
            "human_validated",
            "runtime_integration_authorized",
            "provider_or_model_calls_used",
        },
    )
    _require_string(data, "packet_id")
    _require_run_ref(data)
    _require_exact_tabs(data)
    _require_default_tab(data)
    _require_false(data, "product_proof")
    _require_false(data, "human_validated")
    _require_false(data, "runtime_integration_authorized")
    _require_false(data, "provider_or_model_calls_used")

    data["lesson"] = _validate_nested(
        "lesson",
        validate_teacher_lesson,
        _require_mapping(data, "lesson"),
    )
    data["models"] = [
        _validate_nested(f"models[{index}]", validate_mental_model_page, item)
        for index, item in enumerate(
            _require_object_list(data, "models", allow_empty=False)
        )
    ]
    data["relations"] = [
        _validate_nested(f"relations[{index}]", validate_relation_page, item)
        for index, item in enumerate(
            _require_object_list(data, "relations", allow_empty=False)
        )
    ]
    data["graph"] = _validate_nested(
        "graph",
        validate_visual_graph,
        _require_mapping(data, "graph"),
    )

    _require_receipts(data)
    _require_single_home_rules(data)
    _require_visibility_policy(data)
    _require_missingness(data)
    _require_non_claims(data, REQUIRED_PACKET_NON_CLAIMS)
    _assert_no_forbidden_keys(data)
    _assert_payload_safe(data)
    return data


def render_learning_packet_json(
    payload: Mapping[str, Any],
    *,
    pretty: bool = True,
) -> str:
    indent = 2 if pretty else None
    return json.dumps(dict(payload), indent=indent, sort_keys=True) + "\n"


def load_learning_packet(path: Path | str) -> dict[str, Any]:
    input_path = Path(path)
    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise MentalModelTeacherLearningPacketError("learning packet was not found") from exc
    except json.JSONDecodeError as exc:
        raise MentalModelTeacherLearningPacketError(
            "learning packet JSON was malformed"
        ) from exc
    except UnicodeDecodeError as exc:
        raise MentalModelTeacherLearningPacketError(
            "learning packet JSON was not valid UTF-8"
        ) from exc
    if not isinstance(payload, dict):
        raise MentalModelTeacherLearningPacketError(
            "learning packet JSON root was not an object"
        )
    return payload


def _validate_nested(
    label: str,
    validator,
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    try:
        return validator(payload)
    except MentalModelTeacherContractError as exc:
        raise MentalModelTeacherLearningPacketError(
            f"{label} invalid: {exc}"
        ) from exc


def _copy_mapping(payload: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise MentalModelTeacherLearningPacketError("payload must be an object")
    return dict(payload)


def _require_schema(data: Mapping[str, Any], expected: str) -> None:
    if data.get("schema_version") != expected:
        raise MentalModelTeacherLearningPacketError(
            f"schema_version must be {expected}"
        )


def _require_fields(data: Mapping[str, Any], required: set[str]) -> None:
    missing = sorted(required - set(data))
    if missing:
        raise MentalModelTeacherLearningPacketError(
            "missing required fields: " + ", ".join(missing)
        )


def _require_string(data: Mapping[str, Any], key: str, *, parent: str | None = None) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        prefix = f"{parent}." if parent else ""
        raise MentalModelTeacherLearningPacketError(
            f"{prefix}{key} must be a non-empty string"
        )
    return value


def _require_mapping(data: Mapping[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key)
    if not isinstance(value, dict):
        raise MentalModelTeacherLearningPacketError(f"{key} must be an object")
    return value


def _require_object_list(
    data: Mapping[str, Any],
    key: str,
    *,
    allow_empty: bool,
) -> list[dict[str, Any]]:
    value = data.get(key)
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise MentalModelTeacherLearningPacketError(f"{key} must be a list of objects")
    if not allow_empty and not value:
        raise MentalModelTeacherLearningPacketError(f"{key} must not be empty")
    return value


def _require_string_list(
    data: Mapping[str, Any],
    key: str,
    *,
    allow_empty: bool,
) -> list[str]:
    value = data.get(key)
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        raise MentalModelTeacherLearningPacketError(f"{key} must be a list of strings")
    if not allow_empty and not value:
        raise MentalModelTeacherLearningPacketError(f"{key} must not be empty")
    return value


def _require_false(data: Mapping[str, Any], key: str) -> None:
    if data.get(key) is not False:
        raise MentalModelTeacherLearningPacketError(f"{key} must be false")


def _require_run_ref(data: Mapping[str, Any]) -> None:
    run_ref = _require_mapping(data, "run_ref")
    for key in ("run_id", "case_id", "source", "result_ref"):
        _require_string(run_ref, key, parent="run_ref")
    if run_ref["source"] not in ALLOWED_RUN_SOURCES:
        raise MentalModelTeacherLearningPacketError(
            "run_ref.source must be one of: " + ", ".join(sorted(ALLOWED_RUN_SOURCES))
        )
    _assert_relative_ref(run_ref["result_ref"], "run_ref.result_ref")


def _require_exact_tabs(data: Mapping[str, Any]) -> None:
    tabs = data.get("observatory_tabs")
    if tabs != list(PRIMARY_TABS):
        raise MentalModelTeacherLearningPacketError(
            "observatory_tabs must be exactly: " + ", ".join(PRIMARY_TABS)
        )


def _require_default_tab(data: Mapping[str, Any]) -> None:
    value = data.get("default_tab")
    if value not in ALLOWED_DEFAULT_TABS:
        raise MentalModelTeacherLearningPacketError(
            "default_tab must be Outcome or Learn"
        )


def _require_receipts(data: Mapping[str, Any]) -> None:
    receipts = _require_mapping(data, "receipts")
    _require_fields(
        receipts,
        {
            "source_refs",
            "artifact_refs",
            "missingness",
            "non_claims",
        },
    )
    source_refs = _require_object_list(receipts, "source_refs", allow_empty=False)
    for index, ref in enumerate(source_refs):
        _require_string(ref, "source_id", parent=f"receipts.source_refs[{index}]")
        _require_string(ref, "source_type", parent=f"receipts.source_refs[{index}]")
        path = _require_string(ref, "path", parent=f"receipts.source_refs[{index}]")
        _assert_relative_ref(path, f"receipts.source_refs[{index}].path")

    artifact_refs = _require_object_list(receipts, "artifact_refs", allow_empty=False)
    for index, artifact in enumerate(artifact_refs):
        _require_string(
            artifact,
            "artifact_id",
            parent=f"receipts.artifact_refs[{index}]",
        )
        _require_string(
            artifact,
            "artifact_type",
            parent=f"receipts.artifact_refs[{index}]",
        )
        path = _require_string(
            artifact,
            "path",
            parent=f"receipts.artifact_refs[{index}]",
        )
        _assert_relative_ref(path, f"receipts.artifact_refs[{index}].path")
        home_tab = _require_string(
            artifact,
            "home_tab",
            parent=f"receipts.artifact_refs[{index}]",
        )
        if home_tab not in ALLOWED_RECEIPT_HOME_TABS:
            raise MentalModelTeacherLearningPacketError(
                f"receipts.artifact_refs[{index}].home_tab must be Receipts or Advanced"
            )
        exposure = _require_string(
            artifact,
            "exposure",
            parent=f"receipts.artifact_refs[{index}]",
        )
        if exposure not in ALLOWED_RECEIPT_EXPOSURES:
            raise MentalModelTeacherLearningPacketError(
                f"receipts.artifact_refs[{index}].exposure is unsupported"
            )

    _require_missingness(receipts)
    _require_non_claims(
        receipts,
        {
            "receipts_are_custody_not_proof",
            "not_product_proof",
            "not_human_validation",
        },
    )


def _require_single_home_rules(data: Mapping[str, Any]) -> None:
    rules = _require_mapping(data, "single_home_rules")
    for key, expected in REQUIRED_SINGLE_HOME_RULES.items():
        if rules.get(key) != expected:
            raise MentalModelTeacherLearningPacketError(
                f"single_home_rules.{key} must be {expected}"
            )


def _require_visibility_policy(data: Mapping[str, Any]) -> None:
    policy = _require_mapping(data, "visibility_policy")
    for key, expected in REQUIRED_VISIBILITY_POLICY.items():
        if policy.get(key) is not expected:
            raise MentalModelTeacherLearningPacketError(
                f"visibility_policy.{key} must be {str(expected).lower()}"
            )


def _require_missingness(data: Mapping[str, Any]) -> None:
    missingness = _require_mapping(data, "missingness")
    status = missingness.get("status")
    if status not in ALLOWED_MISSINGNESS_STATUSES:
        raise MentalModelTeacherLearningPacketError(
            "missingness.status must be one of: "
            + ", ".join(sorted(ALLOWED_MISSINGNESS_STATUSES))
        )
    fields = missingness.get("missing_fields")
    if fields is not None and (
        not isinstance(fields, list)
        or not all(isinstance(item, str) for item in fields)
    ):
        raise MentalModelTeacherLearningPacketError(
            "missingness.missing_fields must be a list of strings"
        )
    notes = missingness.get("notes")
    if notes is not None and (
        not isinstance(notes, list)
        or not all(isinstance(item, str) for item in notes)
    ):
        raise MentalModelTeacherLearningPacketError(
            "missingness.notes must be a list of strings"
        )


def _require_non_claims(data: Mapping[str, Any], required: set[str]) -> None:
    non_claims = _require_string_list(data, "non_claims", allow_empty=False)
    missing = sorted(required - set(non_claims))
    if missing:
        raise MentalModelTeacherLearningPacketError(
            "missing non_claims: " + ", ".join(missing)
        )


def _assert_relative_ref(value: str, label: str) -> None:
    if value.startswith("/") or value.startswith("file:"):
        raise MentalModelTeacherLearningPacketError(f"{label} must be relative")


def _assert_no_forbidden_keys(payload: Any) -> None:
    for location, key in _walk_keys(payload):
        if key in FORBIDDEN_PACKET_KEYS or key.endswith("_score"):
            raise MentalModelTeacherLearningPacketError(
                f"forbidden packet key at {location}: {key}"
            )


def _assert_payload_safe(payload: Any) -> None:
    for location, value in _walk_strings(payload):
        lowered = value.lower()
        if any(marker.lower() in lowered for marker in RAW_PRIVATE_MARKERS):
            raise MentalModelTeacherLearningPacketError(
                f"unsafe raw/private marker at {location}"
            )


def _walk_keys(value: Any, location: str = "$") -> list[tuple[str, str]]:
    if isinstance(value, Mapping):
        results: list[tuple[str, str]] = []
        for key, item in value.items():
            key_text = str(key)
            results.append((location, key_text))
            results.extend(_walk_keys(item, f"{location}.{key_text}"))
        return results
    if isinstance(value, list):
        results = []
        for index, item in enumerate(value):
            results.extend(_walk_keys(item, f"{location}[{index}]"))
        return results
    return []


def _walk_strings(value: Any, location: str = "$") -> list[tuple[str, str]]:
    if isinstance(value, str):
        return [(location, value)]
    if isinstance(value, Mapping):
        results: list[tuple[str, str]] = []
        for key, item in value.items():
            results.extend(_walk_strings(str(key), f"{location}.<key>"))
            results.extend(_walk_strings(item, f"{location}.{key}"))
        return results
    if isinstance(value, list):
        results = []
        for index, item in enumerate(value):
            results.extend(_walk_strings(item, f"{location}[{index}]"))
        return results
    return []
