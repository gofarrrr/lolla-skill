"""Product-safe contracts for the portable Observatory workspace.

This module defines validation for presentation-layer view objects only. It
does not read run archives, build adapters, render HTML, call providers, invoke
Lolla, create runs, mutate runtime behavior, or touch the legacy SPA bundle.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any


WORKSPACE_SCHEMA_VERSION = "lolla.observatory.product_workspace.v0"
SELECTED_RUN_SUMMARY_SCHEMA_VERSION = "lolla.observatory.selected_run_summary.v0"
OUTCOME_SUMMARY_SCHEMA_VERSION = "lolla.observatory.outcome_summary.v0"
LEARNING_PACKET_SCHEMA_VERSION = "lolla.observatory.learning_packet.v0"
MODEL_PAGE_SCHEMA_VERSION = "lolla.observatory.model_page.v0"
RELATION_PAGE_SCHEMA_VERSION = "lolla.observatory.relation_page.v0"
GRAPH_NEIGHBORHOOD_SCHEMA_VERSION = "lolla.observatory.graph_neighborhood.v0"
RECEIPT_SUMMARY_SCHEMA_VERSION = "lolla.observatory.receipt_summary.v0"
ADVANCED_AUDIT_INDEX_SCHEMA_VERSION = "lolla.observatory.advanced_audit_index.v0"

PORTABLE_RENDERING_DIRECTION = "portable_python_server_rendered_html"
PRIMARY_SURFACES = ("Outcome", "Learn", "Models", "Relations", "Map", "Receipts")
ADVANCED_SURFACE = "Advanced Audit"

ALLOWED_RUN_STATES = {
    "current",
    "archived",
    "fixture",
    "unknown",
}

ALLOWED_HEALTH_LABELS = {
    "ok",
    "partial",
    "degraded",
    "blocked",
    "unknown",
}

ALLOWED_MISSINGNESS_STATUSES = {
    "complete",
    "partial",
    "missing",
    "not_requested",
    "deferred",
    "blocked",
    "internal_only",
    "needs_review",
    "not_applicable",
}

ALLOWED_AVAILABILITY_STATUSES = {
    "available",
    "partial",
    "missing",
    "absent",
    "not_requested",
    "deferred",
    "blocked",
    "internal_only",
}

ALLOWED_CURATION_STATUSES = {
    "contract_fixture",
    "draft",
    "reviewed",
    "needs_review",
    "missing_source",
}

ALLOWED_HUMAN_REVIEW_STATUSES = {
    "not_reviewed",
    "pending",
    "reviewed_with_caveats",
    "blocked_missing_inputs",
}

ALLOWED_RELATION_TYPES = {
    "ally",
    "antagonist",
    "tension",
    "compound",
    "guardrail",
    "contrast",
    "sequence",
    "unknown",
}

ALLOWED_CONFIDENCE = {
    "unknown",
    "low",
    "medium",
    "high",
}

COMMON_NON_CLAIMS = {
    "not_product_proof",
    "not_human_validation",
    "not_answer_correctness",
    "not_advice_correctness",
    "not_runtime_integration",
    "not_action_authorization",
}

WORKSPACE_NON_CLAIMS = COMMON_NON_CLAIMS | {
    "observatory_is_not_product_proof",
    "telemetry_is_advanced_not_primary",
    "graph_is_navigation_not_proof",
}

LEARNING_NON_CLAIMS = COMMON_NON_CLAIMS | {
    "lesson_is_not_advice",
    "practice_is_not_validation",
}

MODEL_NON_CLAIMS = COMMON_NON_CLAIMS | {
    "raw_markdown_is_not_product_ui",
    "activation_is_not_definition",
}

RELATION_NON_CLAIMS = COMMON_NON_CLAIMS | {
    "relation_is_not_proof",
    "confidence_is_not_certification",
}

GRAPH_NON_CLAIMS = COMMON_NON_CLAIMS | {
    "graph_is_navigation_not_proof",
    "edge_is_not_proof",
}

RECEIPT_NON_CLAIMS = COMMON_NON_CLAIMS | {
    "receipts_are_custody_not_certification",
    "status_is_not_product_proof",
}

ADVANCED_NON_CLAIMS = COMMON_NON_CLAIMS | {
    "advanced_audit_is_internal_inspection",
    "telemetry_is_not_product_copy",
}

RAW_PRIVATE_MARKERS = (
    "/" + "Users/",
    "Desktop/" + "Apps",
    "\\" + "Users\\",
    "SEC" + "RET",
    "api" + "_key",
    "client" + "_secret",
    "OPENROUTER" + "_API_KEY",
    "OPENAI" + "_API_KEY",
    "raw_message" + "_content",
    "provider_reasoning" + "_details",
)

PROOF_LANGUAGE = (
    "proves",
    "proven",
    "guarantees",
    "certifies",
    "validated relation",
    "validated as true",
    "ground truth",
    "truth score",
)

FORBIDDEN_TRUE_KEYS = {
    "product_proof",
    "human_validated",
    "answer_correctness",
    "advice_correctness",
    "runtime_integration_authorized",
    "action_authorized",
    "approval_or_certification",
    "graph_edges_are_proof",
    "embedding_similarity_is_validated_relation_semantics",
    "svelte_revival_authorized",
    "provider_or_model_calls",
    "runtime_behavior_changed",
}

FORBIDDEN_GRAPH_EDGE_KEYS = {
    "affinity",
    "rank",
    "embedding_similarity",
    "score",
    "pagerank",
    "weight",
}


class ObservatoryProductViewError(ValueError):
    """Raised when a portable Observatory product view is unsafe or malformed."""


def validate_selected_run_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = _copy_mapping(payload)
    _require_schema(data, SELECTED_RUN_SUMMARY_SCHEMA_VERSION)
    _require_fields(
        data,
        {
            "schema_version",
            "run_id",
            "case_id",
            "display_title",
            "run_state",
            "health_label",
            "primary_surfaces",
            "source_refs",
            "missingness",
            "non_claims",
        },
    )
    for key in ("run_id", "case_id", "display_title"):
        _require_string(data, key)
    _require_enum(data, "run_state", ALLOWED_RUN_STATES)
    _require_enum(data, "health_label", ALLOWED_HEALTH_LABELS)
    _require_primary_surfaces(data)
    _require_source_refs(data)
    _require_missingness(data)
    _require_non_claims(data, COMMON_NON_CLAIMS)
    _assert_no_forbidden_true_claims(data)
    _assert_payload_safe(data)
    return data


def validate_outcome_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = _copy_mapping(payload)
    _require_schema(data, OUTCOME_SUMMARY_SCHEMA_VERSION)
    _require_fields(
        data,
        {
            "schema_version",
            "run_id",
            "answer_headline",
            "revised_answer_summary",
            "strongest_pressure",
            "model_chips",
            "source_refs",
            "missingness",
            "non_claims",
        },
    )
    for key in (
        "run_id",
        "answer_headline",
        "revised_answer_summary",
        "strongest_pressure",
    ):
        _require_string(data, key)
    _require_model_chips(data, "model_chips", allow_empty=True)
    _require_source_refs(data)
    _require_missingness(data)
    _require_non_claims(data, COMMON_NON_CLAIMS)
    _assert_no_forbidden_true_claims(data)
    _assert_payload_safe(data)
    return data


def validate_learning_packet(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = _copy_mapping(payload)
    _require_schema(data, LEARNING_PACKET_SCHEMA_VERSION)
    _require_fields(
        data,
        {
            "schema_version",
            "run_id",
            "case_anchor",
            "reasoning_trap",
            "thinking_move",
            "relation_story",
            "worked_example",
            "practice_rep",
            "do_not_overlearn",
            "model_links",
            "relation_links",
            "source_refs",
            "human_review_status",
            "product_proof",
            "runtime_integration_authorized",
            "missingness",
            "non_claims",
        },
    )
    for key in (
        "run_id",
        "case_anchor",
        "reasoning_trap",
        "thinking_move",
        "relation_story",
        "worked_example",
    ):
        _require_string(data, key)
    _require_mapping(data, "practice_rep")
    _require_string(data["practice_rep"], "prompt", parent="practice_rep")
    _require_string(data["practice_rep"], "user_action", parent="practice_rep")
    _require_string_list(data, "do_not_overlearn", allow_empty=False)
    _require_link_list(data, "model_links", allow_empty=False)
    _require_link_list(data, "relation_links", allow_empty=True)
    _require_source_refs(data)
    _require_enum(data, "human_review_status", ALLOWED_HUMAN_REVIEW_STATUSES)
    _require_false(data, "product_proof")
    _require_false(data, "runtime_integration_authorized")
    _require_missingness(data)
    _require_non_claims(data, LEARNING_NON_CLAIMS)
    _assert_no_forbidden_true_claims(data)
    _assert_payload_safe(data)
    return data


def validate_model_page(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = _copy_mapping(payload)
    _require_schema(data, MODEL_PAGE_SCHEMA_VERSION)
    _require_fields(
        data,
        {
            "schema_version",
            "model_id",
            "slug",
            "display_name",
            "one_sentence_meaning",
            "helps_notice",
            "use_when",
            "avoid_when",
            "common_misuse",
            "failure_modes",
            "practice_prompts",
            "selected_run_backlinks",
            "source_refs",
            "source_hashes",
            "curation_status",
            "missingness",
            "non_claims",
        },
    )
    for key in ("model_id", "slug", "display_name", "one_sentence_meaning"):
        _require_string(data, key)
    _require_string_list(data, "helps_notice", allow_empty=False)
    _require_string_list(data, "use_when", allow_empty=False)
    _require_string_list(data, "avoid_when", allow_empty=True)
    _require_string_list(data, "common_misuse", allow_empty=True)
    _require_string_list(data, "failure_modes", allow_empty=True)
    _require_string_list(data, "practice_prompts", allow_empty=True)
    _require_link_list(data, "selected_run_backlinks", allow_empty=True)
    _require_source_refs(data)
    _require_source_hashes(data)
    _require_enum(data, "curation_status", ALLOWED_CURATION_STATUSES)
    _require_missingness(data)
    _require_non_claims(data, MODEL_NON_CLAIMS)
    _assert_no_forbidden_true_claims(data)
    _assert_payload_safe(data)
    return data


def validate_relation_page(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = _copy_mapping(payload)
    _require_schema(data, RELATION_PAGE_SCHEMA_VERSION)
    _require_fields(
        data,
        {
            "schema_version",
            "relation_id",
            "source_model_id",
            "target_model_id",
            "relation_type",
            "plain_language_story",
            "why_it_matters",
            "misread_risk",
            "practice_prompt",
            "model_links",
            "source_refs",
            "confidence",
            "curation_status",
            "missingness",
            "non_claims",
        },
    )
    for key in (
        "relation_id",
        "source_model_id",
        "target_model_id",
        "plain_language_story",
        "why_it_matters",
        "misread_risk",
        "practice_prompt",
    ):
        _require_string(data, key)
    _require_enum(data, "relation_type", ALLOWED_RELATION_TYPES)
    _require_link_list(data, "model_links", allow_empty=False)
    _require_source_refs(data)
    _require_enum(data, "confidence", ALLOWED_CONFIDENCE)
    _require_enum(data, "curation_status", ALLOWED_CURATION_STATUSES)
    _require_missingness(data)
    _require_non_claims(data, RELATION_NON_CLAIMS)
    _assert_no_relation_overclaim(data)
    _assert_no_forbidden_true_claims(data)
    _assert_payload_safe(data)
    return data


def validate_graph_neighborhood(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = _copy_mapping(payload)
    _require_schema(data, GRAPH_NEIGHBORHOOD_SCHEMA_VERSION)
    _require_fields(
        data,
        {
            "schema_version",
            "graph_id",
            "graph_scope",
            "nodes",
            "edges",
            "source_refs",
            "layout_hint",
            "default_focus",
            "filters",
            "search_enabled",
            "missingness",
            "non_claims",
        },
    )
    for key in ("graph_id", "graph_scope", "layout_hint", "default_focus"):
        _require_string(data, key)
    _require_graph_nodes(data, "nodes", allow_empty=False)
    _require_graph_edges(data, "edges", allow_empty=True)
    _require_source_refs(data)
    _require_mapping(data, "filters")
    if not isinstance(data.get("search_enabled"), bool):
        raise ObservatoryProductViewError("search_enabled must be a boolean")
    _require_missingness(data)
    _require_non_claims(data, GRAPH_NON_CLAIMS)
    _assert_no_forbidden_true_claims(data)
    _assert_payload_safe(data)
    return data


def validate_receipt_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = _copy_mapping(payload)
    _require_schema(data, RECEIPT_SUMMARY_SCHEMA_VERSION)
    _require_fields(
        data,
        {
            "schema_version",
            "run_id",
            "learning_packet_status",
            "conversation_understanding_status",
            "process_brief_status",
            "source_refs",
            "missingness",
            "advanced_links",
            "visible_non_claims",
            "non_claims",
        },
    )
    _require_string(data, "run_id")
    for key in (
        "learning_packet_status",
        "conversation_understanding_status",
        "process_brief_status",
    ):
        _require_enum(data, key, ALLOWED_AVAILABILITY_STATUSES)
    _require_source_refs(data)
    _require_missingness(data)
    _require_link_list(data, "advanced_links", allow_empty=True)
    _require_string_list(data, "visible_non_claims", allow_empty=False)
    _require_non_claims(data, RECEIPT_NON_CLAIMS)
    _assert_no_forbidden_true_claims(data)
    _assert_payload_safe(data)
    return data


def validate_advanced_audit_index(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = _copy_mapping(payload)
    _require_schema(data, ADVANCED_AUDIT_INDEX_SCHEMA_VERSION)
    _require_fields(
        data,
        {
            "schema_version",
            "run_id",
            "advanced_links",
            "artifact_statuses",
            "source_refs",
            "missingness",
            "non_claims",
        },
    )
    _require_string(data, "run_id")
    _require_link_list(data, "advanced_links", allow_empty=True)
    _require_artifact_statuses(data, "artifact_statuses", allow_empty=True)
    _require_source_refs(data)
    _require_missingness(data)
    _require_non_claims(data, ADVANCED_NON_CLAIMS)
    _assert_no_forbidden_true_claims(data)
    _assert_payload_safe(data)
    return data


def validate_workspace(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = _copy_mapping(payload)
    _require_schema(data, WORKSPACE_SCHEMA_VERSION)
    _require_fields(
        data,
        {
            "schema_version",
            "rendering_direction",
            "primary_surfaces",
            "advanced_surface",
            "selected_run_summary",
            "outcome_summary",
            "learning_packet",
            "model_pages",
            "relation_pages",
            "graph_neighborhood",
            "receipt_summary",
            "advanced_audit_index",
            "source_refs",
            "missingness",
            "non_claims",
        },
    )
    if data.get("rendering_direction") != PORTABLE_RENDERING_DIRECTION:
        raise ObservatoryProductViewError(
            "rendering_direction must be portable_python_server_rendered_html"
        )
    _require_primary_surfaces(data)
    if data.get("advanced_surface") != ADVANCED_SURFACE:
        raise ObservatoryProductViewError("advanced_surface must be Advanced Audit")

    validate_selected_run_summary(_require_mapping(data, "selected_run_summary"))
    validate_outcome_summary(_require_mapping(data, "outcome_summary"))
    validate_learning_packet(_require_mapping(data, "learning_packet"))
    for index, model_page in enumerate(
        _require_object_list(data, "model_pages", allow_empty=True)
    ):
        try:
            validate_model_page(model_page)
        except ObservatoryProductViewError as exc:
            raise ObservatoryProductViewError(f"model_pages[{index}]: {exc}") from exc
    for index, relation_page in enumerate(
        _require_object_list(data, "relation_pages", allow_empty=True)
    ):
        try:
            validate_relation_page(relation_page)
        except ObservatoryProductViewError as exc:
            raise ObservatoryProductViewError(
                f"relation_pages[{index}]: {exc}"
            ) from exc
    validate_graph_neighborhood(_require_mapping(data, "graph_neighborhood"))
    validate_receipt_summary(_require_mapping(data, "receipt_summary"))
    validate_advanced_audit_index(_require_mapping(data, "advanced_audit_index"))

    _require_source_refs(data)
    _require_missingness(data)
    _require_non_claims(data, WORKSPACE_NON_CLAIMS)
    _assert_no_forbidden_true_claims(data)
    _assert_payload_safe(data)
    return data


def validate_product_view(payload: Mapping[str, Any]) -> dict[str, Any]:
    schema = _text(payload.get("schema_version"))
    if schema == WORKSPACE_SCHEMA_VERSION:
        return validate_workspace(payload)
    if schema == SELECTED_RUN_SUMMARY_SCHEMA_VERSION:
        return validate_selected_run_summary(payload)
    if schema == OUTCOME_SUMMARY_SCHEMA_VERSION:
        return validate_outcome_summary(payload)
    if schema == LEARNING_PACKET_SCHEMA_VERSION:
        return validate_learning_packet(payload)
    if schema == MODEL_PAGE_SCHEMA_VERSION:
        return validate_model_page(payload)
    if schema == RELATION_PAGE_SCHEMA_VERSION:
        return validate_relation_page(payload)
    if schema == GRAPH_NEIGHBORHOOD_SCHEMA_VERSION:
        return validate_graph_neighborhood(payload)
    if schema == RECEIPT_SUMMARY_SCHEMA_VERSION:
        return validate_receipt_summary(payload)
    if schema == ADVANCED_AUDIT_INDEX_SCHEMA_VERSION:
        return validate_advanced_audit_index(payload)
    raise ObservatoryProductViewError("unsupported schema_version")


def render_view_json(payload: Mapping[str, Any], *, pretty: bool = True) -> str:
    indent = 2 if pretty else None
    return json.dumps(dict(payload), indent=indent, sort_keys=True) + "\n"


def load_json_object(path: Path | str) -> dict[str, Any]:
    input_path = Path(path)
    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ObservatoryProductViewError("JSON file was not found") from exc
    except json.JSONDecodeError as exc:
        raise ObservatoryProductViewError("JSON file was malformed") from exc
    except UnicodeDecodeError as exc:
        raise ObservatoryProductViewError("JSON file was not valid UTF-8") from exc
    if not isinstance(payload, dict):
        raise ObservatoryProductViewError("JSON root was not an object")
    return payload


def _copy_mapping(payload: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise ObservatoryProductViewError("payload must be an object")
    return dict(payload)


def _require_schema(data: Mapping[str, Any], expected: str) -> None:
    if data.get("schema_version") != expected:
        raise ObservatoryProductViewError(f"schema_version must be {expected}")


def _require_fields(data: Mapping[str, Any], required: set[str]) -> None:
    missing = sorted(required - set(data))
    if missing:
        raise ObservatoryProductViewError(
            "missing required fields: " + ", ".join(missing)
        )


def _require_string(
    data: Mapping[str, Any],
    key: str,
    *,
    parent: str | None = None,
) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        prefix = f"{parent}." if parent else ""
        raise ObservatoryProductViewError(f"{prefix}{key} must be a non-empty string")
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
        raise ObservatoryProductViewError(f"{key} must be a list of strings")
    if not allow_empty and not value:
        raise ObservatoryProductViewError(f"{key} must not be empty")
    return value


def _require_object_list(
    data: Mapping[str, Any],
    key: str,
    *,
    allow_empty: bool,
) -> list[dict[str, Any]]:
    value = data.get(key)
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise ObservatoryProductViewError(f"{key} must be a list of objects")
    if not allow_empty and not value:
        raise ObservatoryProductViewError(f"{key} must not be empty")
    return value


def _require_mapping(data: Mapping[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key)
    if not isinstance(value, dict):
        raise ObservatoryProductViewError(f"{key} must be an object")
    return value


def _require_enum(data: Mapping[str, Any], key: str, allowed: set[str]) -> None:
    value = data.get(key)
    if value not in allowed:
        raise ObservatoryProductViewError(
            f"{key} must be one of: {', '.join(sorted(allowed))}"
        )


def _require_false(data: Mapping[str, Any], key: str) -> None:
    if data.get(key) is not False:
        raise ObservatoryProductViewError(f"{key} must be false")


def _require_primary_surfaces(data: Mapping[str, Any]) -> None:
    surfaces = _require_string_list(data, "primary_surfaces", allow_empty=False)
    if tuple(surfaces) != PRIMARY_SURFACES:
        raise ObservatoryProductViewError(
            "primary_surfaces must be Outcome, Learn, Models, Relations, Map, Receipts"
        )


def _require_source_refs(data: Mapping[str, Any]) -> None:
    refs = data.get("source_refs")
    if not isinstance(refs, list) or not refs:
        raise ObservatoryProductViewError("source_refs must be a non-empty list")
    for index, ref in enumerate(refs):
        if not isinstance(ref, dict):
            raise ObservatoryProductViewError(
                f"source_refs[{index}] must be an object"
            )
        _require_string(ref, "source_id", parent=f"source_refs[{index}]")
        _require_string(ref, "source_type", parent=f"source_refs[{index}]")
        _require_string(ref, "path", parent=f"source_refs[{index}]")
        path = ref.get("path", "")
        if path.startswith("/") or "://" in path:
            raise ObservatoryProductViewError(
                f"source_refs[{index}].path must be repo-relative or portable"
            )


def _require_source_hashes(data: Mapping[str, Any]) -> None:
    hashes = data.get("source_hashes")
    if not isinstance(hashes, dict) or not hashes:
        raise ObservatoryProductViewError("source_hashes must be a non-empty object")
    for path, digest in hashes.items():
        if not isinstance(path, str) or not path.strip():
            raise ObservatoryProductViewError("source_hashes keys must be strings")
        if path.startswith("/") or "://" in path:
            raise ObservatoryProductViewError("source_hashes paths must be relative")
        if not isinstance(digest, str) or len(digest) < 32:
            raise ObservatoryProductViewError(
                "source_hashes values must look like digests"
            )


def _require_missingness(data: Mapping[str, Any]) -> None:
    missingness = data.get("missingness")
    if not isinstance(missingness, dict):
        raise ObservatoryProductViewError("missingness must be an object")
    status = missingness.get("status")
    if status not in ALLOWED_MISSINGNESS_STATUSES:
        raise ObservatoryProductViewError(
            "missingness.status must be one of: "
            + ", ".join(sorted(ALLOWED_MISSINGNESS_STATUSES))
        )
    fields = missingness.get("missing_fields")
    if fields is not None and (
        not isinstance(fields, list)
        or not all(isinstance(item, str) for item in fields)
    ):
        raise ObservatoryProductViewError(
            "missingness.missing_fields must be a list of strings"
        )
    notes = missingness.get("notes")
    if notes is not None and (
        not isinstance(notes, list)
        or not all(isinstance(item, str) for item in notes)
    ):
        raise ObservatoryProductViewError(
            "missingness.notes must be a list of strings"
        )


def _require_non_claims(data: Mapping[str, Any], required: set[str]) -> None:
    non_claims = data.get("non_claims")
    if not isinstance(non_claims, list) or not all(
        isinstance(item, str) and item.strip() for item in non_claims
    ):
        raise ObservatoryProductViewError("non_claims must be a list of strings")
    missing = sorted(required - set(non_claims))
    if missing:
        raise ObservatoryProductViewError(
            "missing non_claims: " + ", ".join(missing)
        )


def _require_link_list(
    data: Mapping[str, Any],
    key: str,
    *,
    allow_empty: bool,
) -> list[dict[str, Any]]:
    links = _require_object_list(data, key, allow_empty=allow_empty)
    for index, link in enumerate(links):
        _require_string(link, "label", parent=f"{key}[{index}]")
        _require_string(link, "href", parent=f"{key}[{index}]")
        _assert_safe_href(link["href"], f"{key}[{index}].href")
    return links


def _require_model_chips(
    data: Mapping[str, Any],
    key: str,
    *,
    allow_empty: bool,
) -> list[dict[str, Any]]:
    chips = _require_object_list(data, key, allow_empty=allow_empty)
    for index, chip in enumerate(chips):
        for field in ("model_id", "label", "role", "href"):
            _require_string(chip, field, parent=f"{key}[{index}]")
        _assert_safe_href(chip["href"], f"{key}[{index}].href")
    return chips


def _require_graph_nodes(
    data: Mapping[str, Any],
    key: str,
    *,
    allow_empty: bool,
) -> list[dict[str, Any]]:
    nodes = _require_object_list(data, key, allow_empty=allow_empty)
    for index, node in enumerate(nodes):
        for field in ("node_id", "label", "node_type", "href"):
            _require_string(node, field, parent=f"{key}[{index}]")
        _assert_safe_href(node["href"], f"{key}[{index}].href")
    return nodes


def _require_graph_edges(
    data: Mapping[str, Any],
    key: str,
    *,
    allow_empty: bool,
) -> list[dict[str, Any]]:
    edges = _require_object_list(data, key, allow_empty=allow_empty)
    for index, edge in enumerate(edges):
        for field in (
            "edge_id",
            "source_node_id",
            "target_node_id",
            "relation_type",
            "navigation_label",
            "href",
        ):
            _require_string(edge, field, parent=f"{key}[{index}]")
        if edge["relation_type"] not in ALLOWED_RELATION_TYPES:
            raise ObservatoryProductViewError(
                f"{key}[{index}].relation_type must be supported"
            )
        _assert_safe_href(edge["href"], f"{key}[{index}].href")
        forbidden = sorted(FORBIDDEN_GRAPH_EDGE_KEYS & set(edge))
        if forbidden:
            raise ObservatoryProductViewError(
                f"{key}[{index}] must not expose {', '.join(forbidden)}"
            )
        label = _text(edge.get("navigation_label")).lower()
        if any(phrase in label for phrase in PROOF_LANGUAGE):
            raise ObservatoryProductViewError(
                f"{key}[{index}].navigation_label must not claim proof"
            )
    return edges


def _require_artifact_statuses(
    data: Mapping[str, Any],
    key: str,
    *,
    allow_empty: bool,
) -> list[dict[str, Any]]:
    statuses = _require_object_list(data, key, allow_empty=allow_empty)
    for index, status in enumerate(statuses):
        for field in ("artifact_id", "label", "status", "home_route"):
            _require_string(status, field, parent=f"{key}[{index}]")
        if status["status"] not in ALLOWED_AVAILABILITY_STATUSES:
            raise ObservatoryProductViewError(
                f"{key}[{index}].status must be a supported availability status"
            )
        _assert_safe_href(status["home_route"], f"{key}[{index}].home_route")
    return statuses


def _assert_safe_href(value: str, location: str) -> None:
    if "://" in value:
        raise ObservatoryProductViewError(f"{location} must be an internal href")
    lowered = value.lower()
    if any(marker.lower() in lowered for marker in RAW_PRIVATE_MARKERS):
        raise ObservatoryProductViewError(f"unsafe raw/private marker at {location}")


def _assert_no_relation_overclaim(data: Mapping[str, Any]) -> None:
    if _text(data.get("confidence")).lower() in {"proof", "certain", "certified"}:
        raise ObservatoryProductViewError("relation confidence must not claim proof")
    for key in (
        "plain_language_story",
        "why_it_matters",
        "misread_risk",
        "practice_prompt",
    ):
        value = _text(data.get(key)).lower()
        if any(phrase in value for phrase in PROOF_LANGUAGE):
            raise ObservatoryProductViewError(
                f"{key} must not use relation-proof language"
            )


def _assert_no_forbidden_true_claims(payload: Any) -> None:
    for location, key, value in _walk_key_values(payload):
        if isinstance(key, str) and key in FORBIDDEN_TRUE_KEYS and value is True:
            raise ObservatoryProductViewError(f"{location}.{key} must not be true")


def _assert_payload_safe(payload: Any) -> None:
    for location, value in _walk_strings(payload):
        lowered = value.lower()
        if any(marker.lower() in lowered for marker in RAW_PRIVATE_MARKERS):
            raise ObservatoryProductViewError(
                f"unsafe raw/private marker at {location}"
            )


def _walk_strings(value: Any, location: str = "$") -> list[tuple[str, str]]:
    if isinstance(value, str):
        return [(location, value)]
    if isinstance(value, Mapping):
        results: list[tuple[str, str]] = []
        for key, item in value.items():
            results.extend(_walk_strings(key, f"{location}.<key>"))
            results.extend(_walk_strings(item, f"{location}.{key}"))
        return results
    if isinstance(value, list):
        results = []
        for index, item in enumerate(value):
            results.extend(_walk_strings(item, f"{location}[{index}]"))
        return results
    return []


def _walk_key_values(value: Any, location: str = "$") -> list[tuple[str, Any, Any]]:
    if isinstance(value, Mapping):
        results: list[tuple[str, Any, Any]] = []
        for key, item in value.items():
            results.append((location, key, item))
            results.extend(_walk_key_values(item, f"{location}.{key}"))
        return results
    if isinstance(value, list):
        results = []
        for index, item in enumerate(value):
            results.extend(_walk_key_values(item, f"{location}[{index}]"))
        return results
    return []


def _text(value: Any) -> str:
    return value if isinstance(value, str) else ""
