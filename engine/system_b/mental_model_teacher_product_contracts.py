"""Product-safe contracts for the Mental Model Teacher product lane.

This module defines validation for the user-facing contract layer only. It does
not read source data, build page objects, render pages, build graph UI, call
providers, or wire runtime behavior.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any


MENTAL_MODEL_PAGE_SCHEMA_VERSION = "lolla.mental_model_teacher.mental_model_page.v0"
RELATION_PAGE_SCHEMA_VERSION = "lolla.mental_model_teacher.relation_page.v0"
TEACHER_LESSON_SCHEMA_VERSION = "lolla.mental_model_teacher.teacher_lesson.v0"
VISUAL_GRAPH_SCHEMA_VERSION = "lolla.mental_model_teacher.visual_graph.v0"

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

ALLOWED_MISSINGNESS_STATUSES = {
    "complete",
    "partial",
    "missing",
    "not_applicable",
    "needs_review",
}

ALLOWED_RELATION_TYPES = {
    "ally",
    "antagonist",
    "tension",
    "compound",
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

RELATION_NON_CLAIMS = COMMON_NON_CLAIMS | {
    "relation_is_not_proof",
    "confidence_is_not_certification",
}

GRAPH_NON_CLAIMS = COMMON_NON_CLAIMS | {
    "graph_is_navigation_not_proof",
    "edge_is_not_proof",
}

TEACHER_NON_CLAIMS = COMMON_NON_CLAIMS | {
    "lesson_is_not_advice",
    "practice_is_not_validation",
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


class MentalModelTeacherContractError(ValueError):
    """Raised when a product contract object is unsafe or malformed."""


def validate_mental_model_page(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = _copy_mapping(payload)
    _require_schema(data, MENTAL_MODEL_PAGE_SCHEMA_VERSION)
    _require_fields(
        data,
        {
            "model_id",
            "slug",
            "display_name",
            "one_sentence_meaning",
            "helps_notice",
            "use_when",
            "avoid_when",
            "common_misuse",
            "failure_modes",
            "premortem_questions",
            "heuristics",
            "practice_prompts",
            "reasoning_types",
            "source_refs",
            "source_hashes",
            "curation_status",
            "missingness",
            "non_claims",
        },
    )
    _require_string(data, "model_id")
    _require_string(data, "slug")
    _require_string(data, "display_name")
    _require_string(data, "one_sentence_meaning")
    _require_string_list(data, "helps_notice", allow_empty=False)
    _require_string_list(data, "use_when", allow_empty=False)
    _require_string_list(data, "avoid_when", allow_empty=True)
    _require_string_list(data, "common_misuse", allow_empty=True)
    _require_string_list(data, "failure_modes", allow_empty=True)
    _require_string_list(data, "premortem_questions", allow_empty=True)
    _require_string_list(data, "heuristics", allow_empty=True)
    _require_string_list(data, "practice_prompts", allow_empty=True)
    _require_string_list(data, "reasoning_types", allow_empty=True)
    _require_source_refs(data)
    _require_source_hashes(data)
    _require_enum(data, "curation_status", ALLOWED_CURATION_STATUSES)
    _require_missingness(data)
    _require_non_claims(data, COMMON_NON_CLAIMS)
    _assert_payload_safe(data)
    return data


def validate_relation_page(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = _copy_mapping(payload)
    _require_schema(data, RELATION_PAGE_SCHEMA_VERSION)
    _require_fields(
        data,
        {
            "relation_id",
            "source_model_id",
            "target_model_id",
            "relation_type",
            "plain_language_story",
            "why_it_matters",
            "misread_risk",
            "practice_prompt",
            "source_quote_or_ref",
            "confidence",
            "curation_status",
            "missingness",
            "non_claims",
        },
    )
    _require_string(data, "relation_id")
    _require_string(data, "source_model_id")
    _require_string(data, "target_model_id")
    _require_enum(data, "relation_type", ALLOWED_RELATION_TYPES)
    for key in (
        "plain_language_story",
        "why_it_matters",
        "misread_risk",
        "practice_prompt",
        "source_quote_or_ref",
    ):
        _require_string(data, key)
    _require_enum(data, "confidence", ALLOWED_CONFIDENCE)
    _require_enum(data, "curation_status", ALLOWED_CURATION_STATUSES)
    _require_missingness(data)
    _require_non_claims(data, RELATION_NON_CLAIMS)
    _assert_no_relation_overclaim(data)
    _assert_payload_safe(data)
    return data


def validate_teacher_lesson(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = _copy_mapping(payload)
    _require_schema(data, TEACHER_LESSON_SCHEMA_VERSION)
    _require_fields(
        data,
        {
            "lesson_id",
            "case_id",
            "case_anchor",
            "thinking_move",
            "model_stack",
            "relation_story",
            "model_links",
            "relation_links",
            "practice_rep",
            "do_not_overlearn",
            "source_refs",
            "human_review_status",
            "product_proof",
            "runtime_integration_authorized",
            "missingness",
            "non_claims",
        },
    )
    for key in ("lesson_id", "case_id", "case_anchor", "thinking_move", "relation_story"):
        _require_string(data, key)
    _require_object_list(data, "model_stack", allow_empty=False)
    _require_link_list(data, "model_links", allow_empty=False)
    _require_link_list(data, "relation_links", allow_empty=True)
    _require_mapping(data, "practice_rep")
    _require_string(data["practice_rep"], "prompt", parent="practice_rep")
    _require_string(data["practice_rep"], "user_action", parent="practice_rep")
    _require_string_list(data, "do_not_overlearn", allow_empty=False)
    _require_source_refs(data)
    _require_enum(data, "human_review_status", ALLOWED_HUMAN_REVIEW_STATUSES)
    _require_false(data, "product_proof")
    _require_false(data, "runtime_integration_authorized")
    _require_missingness(data)
    _require_non_claims(data, TEACHER_NON_CLAIMS)
    _assert_payload_safe(data)
    return data


def validate_visual_graph(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = _copy_mapping(payload)
    _require_schema(data, VISUAL_GRAPH_SCHEMA_VERSION)
    _require_fields(
        data,
        {
            "graph_id",
            "graph_scope",
            "nodes",
            "edges",
            "source_artifacts",
            "layout_hint",
            "default_focus",
            "filters",
            "missingness",
            "non_claims",
        },
    )
    _require_string(data, "graph_id")
    _require_string(data, "graph_scope")
    _require_object_list(data, "nodes", allow_empty=False)
    _require_object_list(data, "edges", allow_empty=True)
    _require_source_artifacts(data)
    _require_string(data, "layout_hint")
    _require_string(data, "default_focus")
    _require_mapping(data, "filters")
    _require_missingness(data)
    _require_non_claims(data, GRAPH_NON_CLAIMS)
    _assert_graph_edges_safe(data)
    _assert_payload_safe(data)
    return data


def validate_product_object(payload: Mapping[str, Any]) -> dict[str, Any]:
    schema = _text(payload.get("schema_version"))
    if schema == MENTAL_MODEL_PAGE_SCHEMA_VERSION:
        return validate_mental_model_page(payload)
    if schema == RELATION_PAGE_SCHEMA_VERSION:
        return validate_relation_page(payload)
    if schema == TEACHER_LESSON_SCHEMA_VERSION:
        return validate_teacher_lesson(payload)
    if schema == VISUAL_GRAPH_SCHEMA_VERSION:
        return validate_visual_graph(payload)
    raise MentalModelTeacherContractError("unsupported schema_version")


def render_contract_json(payload: Mapping[str, Any], *, pretty: bool = True) -> str:
    indent = 2 if pretty else None
    return json.dumps(dict(payload), indent=indent, sort_keys=True) + "\n"


def load_json_object(path: Path | str) -> dict[str, Any]:
    input_path = Path(path)
    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise MentalModelTeacherContractError("JSON file was not found") from exc
    except json.JSONDecodeError as exc:
        raise MentalModelTeacherContractError("JSON file was malformed") from exc
    except UnicodeDecodeError as exc:
        raise MentalModelTeacherContractError("JSON file was not valid UTF-8") from exc
    if not isinstance(payload, dict):
        raise MentalModelTeacherContractError("JSON root was not an object")
    return payload


def _copy_mapping(payload: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise MentalModelTeacherContractError("payload must be an object")
    return dict(payload)


def _require_schema(data: Mapping[str, Any], expected: str) -> None:
    if data.get("schema_version") != expected:
        raise MentalModelTeacherContractError(f"schema_version must be {expected}")


def _require_fields(data: Mapping[str, Any], required: set[str]) -> None:
    missing = sorted(required - set(data))
    if missing:
        raise MentalModelTeacherContractError(
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
        raise MentalModelTeacherContractError(f"{prefix}{key} must be a non-empty string")
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
        raise MentalModelTeacherContractError(f"{key} must be a list of strings")
    if not allow_empty and not value:
        raise MentalModelTeacherContractError(f"{key} must not be empty")
    return value


def _require_object_list(
    data: Mapping[str, Any],
    key: str,
    *,
    allow_empty: bool,
) -> list[dict[str, Any]]:
    value = data.get(key)
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise MentalModelTeacherContractError(f"{key} must be a list of objects")
    if not allow_empty and not value:
        raise MentalModelTeacherContractError(f"{key} must not be empty")
    return value


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
    return links


def _require_mapping(data: Mapping[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key)
    if not isinstance(value, dict):
        raise MentalModelTeacherContractError(f"{key} must be an object")
    return value


def _require_enum(data: Mapping[str, Any], key: str, allowed: set[str]) -> None:
    value = data.get(key)
    if value not in allowed:
        raise MentalModelTeacherContractError(
            f"{key} must be one of: {', '.join(sorted(allowed))}"
        )


def _require_false(data: Mapping[str, Any], key: str) -> None:
    if data.get(key) is not False:
        raise MentalModelTeacherContractError(f"{key} must be false")


def _require_source_refs(data: Mapping[str, Any]) -> None:
    refs = data.get("source_refs")
    if not isinstance(refs, list) or not refs:
        raise MentalModelTeacherContractError("source_refs must be a non-empty list")
    for index, ref in enumerate(refs):
        if not isinstance(ref, dict):
            raise MentalModelTeacherContractError(
                f"source_refs[{index}] must be an object"
            )
        _require_string(ref, "source_id", parent=f"source_refs[{index}]")
        _require_string(ref, "path", parent=f"source_refs[{index}]")
        _require_string(ref, "source_type", parent=f"source_refs[{index}]")
        if ref.get("path", "").startswith("/"):
            raise MentalModelTeacherContractError(
                f"source_refs[{index}].path must be repo-relative"
            )


def _require_source_hashes(data: Mapping[str, Any]) -> None:
    hashes = data.get("source_hashes")
    if not isinstance(hashes, dict) or not hashes:
        raise MentalModelTeacherContractError("source_hashes must be a non-empty object")
    for path, digest in hashes.items():
        if not isinstance(path, str) or not path.strip():
            raise MentalModelTeacherContractError("source_hashes keys must be strings")
        if path.startswith("/"):
            raise MentalModelTeacherContractError("source_hashes paths must be relative")
        if not isinstance(digest, str) or len(digest) < 32:
            raise MentalModelTeacherContractError(
                "source_hashes values must look like digests"
            )


def _require_source_artifacts(data: Mapping[str, Any]) -> None:
    artifacts = data.get("source_artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise MentalModelTeacherContractError(
            "source_artifacts must be a non-empty list"
        )
    for index, artifact in enumerate(artifacts):
        if not isinstance(artifact, dict):
            raise MentalModelTeacherContractError(
                f"source_artifacts[{index}] must be an object"
            )
        _require_string(artifact, "artifact_id", parent=f"source_artifacts[{index}]")
        _require_string(artifact, "path", parent=f"source_artifacts[{index}]")
        _require_string(artifact, "source_type", parent=f"source_artifacts[{index}]")
        if artifact.get("path", "").startswith("/"):
            raise MentalModelTeacherContractError(
                f"source_artifacts[{index}].path must be repo-relative"
            )


def _require_missingness(data: Mapping[str, Any]) -> None:
    missingness = data.get("missingness")
    if not isinstance(missingness, dict):
        raise MentalModelTeacherContractError("missingness must be an object")
    status = missingness.get("status")
    if status not in ALLOWED_MISSINGNESS_STATUSES:
        raise MentalModelTeacherContractError(
            "missingness.status must be one of: "
            + ", ".join(sorted(ALLOWED_MISSINGNESS_STATUSES))
        )
    fields = missingness.get("missing_fields")
    if fields is not None and (
        not isinstance(fields, list)
        or not all(isinstance(item, str) for item in fields)
    ):
        raise MentalModelTeacherContractError(
            "missingness.missing_fields must be a list of strings"
        )
    notes = missingness.get("notes")
    if notes is not None and (
        not isinstance(notes, list)
        or not all(isinstance(item, str) for item in notes)
    ):
        raise MentalModelTeacherContractError(
            "missingness.notes must be a list of strings"
        )


def _require_non_claims(data: Mapping[str, Any], required: set[str]) -> None:
    non_claims = data.get("non_claims")
    if not isinstance(non_claims, list) or not all(
        isinstance(item, str) and item.strip() for item in non_claims
    ):
        raise MentalModelTeacherContractError("non_claims must be a list of strings")
    missing = sorted(required - set(non_claims))
    if missing:
        raise MentalModelTeacherContractError(
            "missing non_claims: " + ", ".join(missing)
        )


def _assert_payload_safe(payload: Any) -> None:
    for location, value in _walk_strings(payload):
        lowered = value.lower()
        if any(marker.lower() in lowered for marker in RAW_PRIVATE_MARKERS):
            raise MentalModelTeacherContractError(
                f"unsafe raw/private marker at {location}"
            )


def _assert_no_relation_overclaim(data: Mapping[str, Any]) -> None:
    if data.get("confidence") not in ALLOWED_CONFIDENCE:
        raise MentalModelTeacherContractError("relation confidence is invalid")
    if _text(data.get("confidence")).lower() in {"proof", "certain", "certified"}:
        raise MentalModelTeacherContractError("relation confidence must not claim proof")
    for key in (
        "plain_language_story",
        "why_it_matters",
        "misread_risk",
        "practice_prompt",
    ):
        value = _text(data.get(key)).lower()
        if any(phrase in value for phrase in PROOF_LANGUAGE):
            raise MentalModelTeacherContractError(
                f"{key} must not use relation-proof language"
            )


def _assert_graph_edges_safe(data: Mapping[str, Any]) -> None:
    edges = data.get("edges")
    if not isinstance(edges, list):
        raise MentalModelTeacherContractError("edges must be a list")
    for index, edge in enumerate(edges):
        if not isinstance(edge, dict):
            raise MentalModelTeacherContractError(f"edges[{index}] must be an object")
        relation_type = edge.get("relation_type")
        if relation_type not in ALLOWED_RELATION_TYPES:
            raise MentalModelTeacherContractError(
                f"edges[{index}].relation_type must be supported"
            )
        for forbidden_key in ("affinity", "rank", "embedding_similarity", "score"):
            if forbidden_key in edge:
                raise MentalModelTeacherContractError(
                    f"edges[{index}] must not expose {forbidden_key}"
                )
        label = _text(edge.get("label")).lower()
        if any(phrase in label for phrase in PROOF_LANGUAGE):
            raise MentalModelTeacherContractError(
                f"edges[{index}].label must not claim proof"
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


def _text(value: Any) -> str:
    return value if isinstance(value, str) else ""
