"""Read-only adapters for portable Observatory product views.

The adapters translate existing selected-run and Teacher-learning payloads into
the product-safe Observatory view contracts. They do not render HTML, mutate
archives, create Lolla runs, invoke Lolla, call providers, change routes, or
touch the legacy SPA bundle.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any
from urllib.parse import quote

from engine.system_b.mental_model_teacher_observatory_packet_adapter import (
    build_teacher_learning_response,
)
from engine.system_b.observatory_decision_work_status import (
    build_observatory_decision_work_status,
)
from observatory.product_views import (
    ADVANCED_AUDIT_INDEX_SCHEMA_VERSION,
    ADVANCED_NON_CLAIMS,
    ADVANCED_SURFACE,
    COMMON_NON_CLAIMS,
    GRAPH_NEIGHBORHOOD_SCHEMA_VERSION,
    GRAPH_NON_CLAIMS,
    LEARNING_NON_CLAIMS,
    LEARNING_PACKET_SCHEMA_VERSION,
    MODEL_NON_CLAIMS,
    MODEL_PAGE_SCHEMA_VERSION,
    OUTCOME_SUMMARY_SCHEMA_VERSION,
    OUTCOME_VALUE_SCHEMA_VERSION,
    PORTABLE_RENDERING_DIRECTION,
    PRIMARY_SURFACES,
    RECEIPT_NON_CLAIMS,
    RECEIPT_SUMMARY_SCHEMA_VERSION,
    RELATION_NON_CLAIMS,
    RELATION_PAGE_SCHEMA_VERSION,
    SELECTED_RUN_SUMMARY_SCHEMA_VERSION,
    WORKSPACE_NON_CLAIMS,
    WORKSPACE_SCHEMA_VERSION,
    ObservatoryProductViewError,
    validate_workspace,
)


OBSERVATORY_PRODUCT_VIEW_ADAPTER_SCHEMA_VERSION = (
    "lolla.observatory.product_view_adapter.v0"
)


class ObservatoryProductViewAdapterError(ValueError):
    """Raised when a portable Observatory view adapter cannot build safely."""


def build_observatory_product_view_response(
    *,
    selected_case_id: str,
    result: Mapping[str, Any] | None = None,
    result_path: Path | str | None = None,
    teacher_learning_response: Mapping[str, Any] | None = None,
    decision_work_status: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a product-safe selected-run Observatory workspace response.

    The response is intentionally a wrapper. When a matching Teacher learning
    packet is absent, the adapter returns explicit missingness instead of
    inventing model, relation, lesson, or graph content.
    """

    selected_result = dict(result or {})
    selected_path = Path(result_path) if result_path is not None else None
    teacher_response = _teacher_response(
        selected_case_id=selected_case_id,
        result=selected_result,
        result_path=selected_path,
        supplied=teacher_learning_response,
    )
    selected_run_id = _selected_run_id(selected_result, selected_path, teacher_response)
    source_refs = [_result_source_ref(selected_path)]

    if not teacher_response.get("available"):
        return _unavailable_adapter_response(
            selected_case_id=selected_case_id,
            selected_run_id=selected_run_id,
            teacher_response=teacher_response,
            source_refs=source_refs,
        )

    decision_status = _decision_work_status(
        selected_case_id=selected_case_id,
        result=selected_result,
        result_path=selected_path,
        supplied=decision_work_status,
    )
    workspace = _workspace(
        selected_case_id=selected_case_id,
        selected_run_id=selected_run_id,
        result=selected_result,
        result_path=selected_path,
        teacher_response=dict(teacher_response),
        decision_work_status=decision_status,
    )

    try:
        workspace = validate_workspace(workspace)
    except ObservatoryProductViewError as exc:
        raise ObservatoryProductViewAdapterError(
            f"adapted Observatory workspace is invalid: {exc}"
        ) from exc

    response = {
        "schema_version": OBSERVATORY_PRODUCT_VIEW_ADAPTER_SCHEMA_VERSION,
        "available": True,
        "selected_case_id": selected_case_id,
        "selected_run_id": selected_run_id,
        "workspace_schema": WORKSPACE_SCHEMA_VERSION,
        "workspace": workspace,
        "source_refs": _dedupe_source_refs(
            [*source_refs, *_source_refs_from_workspace(workspace)]
        ),
        "missingness": workspace["missingness"],
        "adapter_guards": _adapter_guards(),
        "non_claims": sorted(WORKSPACE_NON_CLAIMS),
    }
    _assert_no_local_paths(response)
    return response


def build_observatory_run_only_workspace_preview(
    *,
    selected_case_id: str,
    result: Mapping[str, Any] | None = None,
    result_path: Path | str | None = None,
    teacher_learning_response: Mapping[str, Any] | None = None,
    decision_work_status: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return the run-readable part of the workspace without faking Teacher data.

    This object is intentionally not the full product workspace contract. It is
    used by the portable server when the selected run has an Outcome/Receipts
    surface but no matching Teacher learning packet for Learn, Models,
    Relations, or Map.
    """

    selected_result = dict(result or {})
    selected_path = Path(result_path) if result_path is not None else None
    teacher_response = _teacher_response(
        selected_case_id=selected_case_id,
        result=selected_result,
        result_path=selected_path,
        supplied=teacher_learning_response,
    )
    decision_status = _decision_work_status(
        selected_case_id=selected_case_id,
        result=selected_result,
        result_path=selected_path,
        supplied=decision_work_status,
    )
    selected_run_id = _selected_run_id(selected_result, selected_path, teacher_response)
    missing_fields = _dedupe(
        [
            "teacher_learning_packet",
            "learn_surface",
            "model_pages",
            "relation_pages",
            "graph_neighborhood",
        ]
    )
    preview = {
        "schema_version": WORKSPACE_SCHEMA_VERSION,
        "rendering_direction": PORTABLE_RENDERING_DIRECTION,
        "primary_surfaces": list(PRIMARY_SURFACES),
        "advanced_surface": ADVANCED_SURFACE,
        "selected_run_summary": _selected_run_summary(
            selected_case_id=selected_case_id,
            selected_run_id=selected_run_id,
            result=selected_result,
            result_path=selected_path,
        ),
        "outcome_summary": _outcome_summary(
            selected_run_id=selected_run_id,
            result=selected_result,
            teacher_models=[],
        ),
        "outcome_value": _outcome_value(
            selected_case_id=selected_case_id,
            selected_run_id=selected_run_id,
            result=selected_result,
        ),
        "learning_packet": _missing_learning_packet(selected_run_id),
        "model_pages": [],
        "relation_pages": [],
        "graph_neighborhood": _missing_graph_neighborhood(selected_run_id),
        "receipt_summary": _receipt_summary(
            selected_run_id=selected_run_id,
            teacher_response=teacher_response,
            decision_work_status=decision_status,
        ),
        "advanced_audit_index": _advanced_audit_index(
            selected_run_id=selected_run_id,
            result=selected_result,
            decision_work_status=decision_status,
        ),
        "source_refs": _dedupe_source_refs([_result_source_ref(selected_path)]),
        "missingness": {
            "status": "partial",
            "missing_fields": missing_fields,
            "notes": [
                "Outcome and Receipts were adapted from the selected run.",
                "Teacher lesson, model pages, relation pages, and graph were not faked because no matching Teacher packet was available.",
            ],
        },
        "non_claims": sorted(WORKSPACE_NON_CLAIMS),
    }
    _assert_no_local_paths(preview)
    return preview


def _workspace(
    *,
    selected_case_id: str,
    selected_run_id: str,
    result: Mapping[str, Any],
    result_path: Path | None,
    teacher_response: dict[str, Any],
    decision_work_status: Mapping[str, Any],
) -> dict[str, Any]:
    tab_payloads = _mapping(teacher_response.get("tab_payloads"))
    learn_tab = _mapping(tab_payloads.get("Learn"))
    models_tab = _mapping(tab_payloads.get("Models"))
    relations_tab = _mapping(tab_payloads.get("Relations"))
    map_tab = _mapping(tab_payloads.get("Map"))

    lesson = _mapping(learn_tab.get("lesson"))
    teacher_models = _object_list(models_tab.get("models"))
    teacher_relations = _object_list(relations_tab.get("relations"))
    teacher_graph = _mapping(map_tab.get("graph"))
    model_lookup = {
        _text(model.get("model_id")): _text(model.get("display_name"))
        for model in teacher_models
    }

    model_pages = [
        _model_page(model, selected_case_id=selected_case_id)
        for model in teacher_models
    ]
    relation_pages = [
        _relation_page(relation, model_lookup)
        for relation in teacher_relations
    ]
    graph_neighborhood = _graph_neighborhood(teacher_graph, model_lookup)

    source_refs = _dedupe_source_refs(
        [
            _result_source_ref(result_path),
            *_source_refs_from_mapping(lesson),
            *_source_refs_from_objects(teacher_models),
            *_source_refs_from_objects(relation_pages),
            *_source_refs_from_mapping(graph_neighborhood),
        ]
    )
    missing_fields = _dedupe(
        [
            *_missing_fields_from_mapping(lesson),
            *_missing_fields_from_objects(teacher_models),
            *_missing_fields_from_objects(teacher_relations),
            *_missing_fields_from_mapping(teacher_graph),
        ]
    )
    if not _text(result.get("revised_answer")):
        missing_fields.append("revised_answer")
    missing_fields = _dedupe(missing_fields)

    workspace = {
        "schema_version": WORKSPACE_SCHEMA_VERSION,
        "rendering_direction": PORTABLE_RENDERING_DIRECTION,
        "primary_surfaces": list(PRIMARY_SURFACES),
        "advanced_surface": ADVANCED_SURFACE,
        "selected_run_summary": _selected_run_summary(
            selected_case_id=selected_case_id,
            selected_run_id=selected_run_id,
            result=result,
            result_path=result_path,
        ),
        "outcome_summary": _outcome_summary(
            selected_run_id=selected_run_id,
            result=result,
            teacher_models=teacher_models,
        ),
        "outcome_value": _outcome_value(
            selected_case_id=selected_case_id,
            selected_run_id=selected_run_id,
            result=result,
        ),
        "learning_packet": _learning_packet(
            selected_run_id=selected_run_id,
            lesson=lesson,
            model_lookup=model_lookup,
        ),
        "model_pages": model_pages,
        "relation_pages": relation_pages,
        "graph_neighborhood": graph_neighborhood,
        "receipt_summary": _receipt_summary(
            selected_run_id=selected_run_id,
            teacher_response=teacher_response,
            decision_work_status=decision_work_status,
        ),
        "advanced_audit_index": _advanced_audit_index(
            selected_run_id=selected_run_id,
            result=result,
            decision_work_status=decision_work_status,
        ),
        "source_refs": source_refs,
        "missingness": {
            "status": "partial" if missing_fields else "complete",
            "missing_fields": missing_fields,
            "notes": [
                "Workspace was adapted read-only from existing run, Teacher packet, and sidecar status artifacts.",
                "Primary surfaces receive product-safe view objects, not raw telemetry.",
            ],
        },
        "non_claims": sorted(WORKSPACE_NON_CLAIMS),
    }
    return workspace


def _missing_learning_packet(selected_run_id: str) -> dict[str, Any]:
    return {
        "schema_version": LEARNING_PACKET_SCHEMA_VERSION,
        "run_id": selected_run_id,
        "case_anchor": "Teacher lesson is unavailable for this selected run.",
        "reasoning_trap": "No Teacher packet is attached to this selected run.",
        "thinking_move": "No source-backed thinking move is available.",
        "relation_story": "No source-backed relation story is available.",
        "worked_example": "No source-backed worked example is available.",
        "practice_rep": {
            "prompt": "No practice prompt is available for this selected run.",
            "user_action": "No practice action is available for this selected run.",
        },
        "do_not_overlearn": ["Do not infer a Teacher lesson from a missing packet."],
        "model_links": [
            {
                "label": "No Teacher model links available",
                "href": "#models",
            }
        ],
        "relation_links": [],
        "source_refs": [
            _portable_source_ref(
                "teacher-learning-packet",
                "missing_source",
                "selected_run/teacher-learning-packet.json",
            )
        ],
        "human_review_status": "blocked_missing_inputs",
        "product_proof": False,
        "runtime_integration_authorized": False,
        "missingness": {
            "status": "missing",
            "missing_fields": ["teacher_learning_packet"],
            "notes": [
                "No matching Teacher learning packet was available for this selected run."
            ],
        },
        "non_claims": sorted(LEARNING_NON_CLAIMS),
    }


def _missing_graph_neighborhood(selected_run_id: str) -> dict[str, Any]:
    return {
        "schema_version": GRAPH_NEIGHBORHOOD_SCHEMA_VERSION,
        "graph_id": f"{selected_run_id}-missing-graph",
        "graph_scope": "selected_run_learning_neighborhood",
        "nodes": [],
        "edges": [],
        "source_refs": [
            _portable_source_ref(
                "graph-neighborhood",
                "missing_source",
                "selected_run/teacher-learning-packet.json",
            )
        ],
        "layout_hint": "missing",
        "default_focus": "missing-focus",
        "filters": {"relation_types": []},
        "search_enabled": False,
        "missingness": {
            "status": "missing",
            "missing_fields": ["graph_neighborhood", "teacher_learning_packet"],
            "notes": [
                "No selected-run graph is available without a matching Teacher packet."
            ],
        },
        "non_claims": sorted(GRAPH_NON_CLAIMS),
    }


def _selected_run_summary(
    *,
    selected_case_id: str,
    selected_run_id: str,
    result: Mapping[str, Any],
    result_path: Path | None,
) -> dict[str, Any]:
    return {
        "schema_version": SELECTED_RUN_SUMMARY_SCHEMA_VERSION,
        "run_id": selected_run_id,
        "case_id": selected_case_id,
        "display_title": _display_title(selected_case_id, result),
        "run_state": _run_state(selected_case_id),
        "health_label": _health_label(result),
        "primary_surfaces": list(PRIMARY_SURFACES),
        "source_refs": [_result_source_ref(result_path)],
        "missingness": {
            "status": "complete" if result.get("run_health") else "partial",
            "missing_fields": [] if result.get("run_health") else ["run_health"],
            "notes": [
                "Run summary is adapted from selected result metadata without exposing local paths."
            ],
        },
        "non_claims": sorted(COMMON_NON_CLAIMS),
    }


def _outcome_summary(
    *,
    selected_run_id: str,
    result: Mapping[str, Any],
    teacher_models: list[dict[str, Any]],
) -> dict[str, Any]:
    revised_answer = _text(result.get("revised_answer"))
    missing_fields = []
    if not revised_answer:
        missing_fields.append("revised_answer")
    strongest_pressure = _strongest_pressure(result)
    if not strongest_pressure:
        strongest_pressure = "No compact pressure summary is available in the selected result."
        missing_fields.append("strongest_pressure")
    return {
        "schema_version": OUTCOME_SUMMARY_SCHEMA_VERSION,
        "run_id": selected_run_id,
        "answer_headline": _answer_headline(revised_answer),
        "revised_answer_summary": _compact_text(
            revised_answer,
            fallback="No revised answer artifact is available for this selected run.",
        ),
        "strongest_pressure": strongest_pressure,
        "model_chips": [
            {
                "model_id": _text(model.get("model_id")),
                "label": _text(model.get("display_name"), _text(model.get("model_id"))),
                "role": "appears in the selected-run learning packet",
                "href": f"/models/{_text(model.get('model_id'))}",
            }
            for model in teacher_models[:6]
            if _text(model.get("model_id"))
        ],
        "source_refs": [_result_source_ref(None)],
        "missingness": {
            "status": "partial" if missing_fields else "complete",
            "missing_fields": missing_fields,
            "notes": [
                "Outcome owns run result summary; Learn owns the reasoning lesson."
            ],
        },
        "non_claims": sorted(COMMON_NON_CLAIMS),
    }


def _outcome_value(
    *,
    selected_case_id: str,
    selected_run_id: str,
    result: Mapping[str, Any],
) -> dict[str, Any]:
    revised_answer = _full_plain_text(_text(result.get("revised_answer")))
    strongest_pressure = _strongest_pressure(result)
    missing_fields = []
    if not revised_answer:
        missing_fields.append("revised_answer")
    if not _text(result.get("memo_what_changed")):
        missing_fields.append("memo_what_changed")
    if not strongest_pressure:
        missing_fields.append("strongest_pressure")

    plain_language_answer = revised_answer or (
        "No revised answer artifact is available for this selected run."
    )
    what_changed = _what_changed_points(result, strongest_pressure)
    primary_reasons = _primary_reason_points(revised_answer, strongest_pressure)
    confidence_boundary = _confidence_boundary_points(
        revised_answer,
        strongest_pressure,
    )

    return {
        "schema_version": OUTCOME_VALUE_SCHEMA_VERSION,
        "run_id": selected_run_id,
        "case_id": selected_case_id,
        "outcome_headline": _outcome_headline(revised_answer),
        "stance": _outcome_stance(revised_answer),
        "plain_language_answer": plain_language_answer,
        "what_changed": what_changed,
        "primary_reasons": primary_reasons,
        "confidence_boundary": confidence_boundary,
        "recommended_next_moves": [
            {
                "label": "Practice the reasoning move",
                "href": "#learn",
                "reason": "Use Learn to see the thinking move behind this outcome.",
            },
            {
                "label": "Inspect receipts",
                "href": "#receipts",
                "reason": "Check source custody, missingness, and non-claims before relying on the run.",
            },
            {
                "label": "Download MD",
                "href": _agent_memory_download_href(selected_case_id),
                "reason": "Create a private Markdown memory for deeper agent review without rerunning Lolla.",
            },
        ],
        "source_refs": [_result_source_ref(None)],
        "missingness": {
            "status": "partial" if missing_fields else "complete",
            "missing_fields": _dedupe(missing_fields),
            "notes": [
                "Outcome value is adapted from existing run artifacts only.",
                "Missing fields are named instead of filled with generated copy.",
            ],
        },
        "non_claims": sorted(COMMON_NON_CLAIMS),
    }


def _learning_packet(
    *,
    selected_run_id: str,
    lesson: Mapping[str, Any],
    model_lookup: Mapping[str, str],
) -> dict[str, Any]:
    missing_fields = _missing_fields_from_mapping(lesson)
    reasoning_trap = _text(lesson.get("reasoning_trap"))
    if not reasoning_trap:
        reasoning_trap = "Not supplied by the current Teacher learning packet."
        missing_fields.append("reasoning_trap")
    worked_example = _text(lesson.get("worked_example"))
    if not worked_example:
        worked_example = "Not supplied by the current Teacher learning packet."
        missing_fields.append("worked_example")

    model_ids = [
        _text(item.get("model_id"))
        for item in _object_list(lesson.get("model_stack"))
        if _text(item.get("model_id"))
    ]
    relation_ids = [
        _relation_id_from_href_or_label(link)
        for link in _object_list(lesson.get("relation_links"))
    ]
    return {
        "schema_version": LEARNING_PACKET_SCHEMA_VERSION,
        "run_id": selected_run_id,
        "case_anchor": _text(lesson.get("case_anchor"), "No case anchor supplied."),
        "reasoning_trap": reasoning_trap,
        "thinking_move": _text(
            lesson.get("thinking_move"),
            "No thinking move supplied by the current Teacher packet.",
        ),
        "relation_story": _text(
            lesson.get("relation_story"),
            "No relation story supplied by the current Teacher packet.",
        ),
        "worked_example": worked_example,
        "practice_rep": _practice_rep(lesson),
        "do_not_overlearn": _string_list(
            lesson.get("do_not_overlearn"),
            fallback=["Do not treat this lesson as advice or proof."],
        ),
        "model_links": [
            {
                "label": model_lookup.get(model_id) or model_id,
                "href": f"/models/{model_id}",
            }
            for model_id in model_ids
        ],
        "relation_links": [
            {
                "label": relation_id.replace("-", " ").replace("__", " plus "),
                "href": f"/relations/{relation_id}",
            }
            for relation_id in relation_ids
            if relation_id
        ],
        "source_refs": _source_refs_from_mapping(lesson)
        or [_portable_source_ref("teacher-lesson", "teacher_learning_packet", "selected_run/teacher-learning-packet.json")],
        "human_review_status": _text(lesson.get("human_review_status"), "not_reviewed"),
        "product_proof": False,
        "runtime_integration_authorized": False,
        "missingness": {
            "status": "partial" if missing_fields else "complete",
            "missing_fields": _dedupe(missing_fields),
            "notes": [
                "Learning packet is adapted from existing Teacher artifacts and keeps absent teaching fields explicit."
            ],
        },
        "non_claims": sorted(LEARNING_NON_CLAIMS),
    }


def _model_page(
    model: Mapping[str, Any],
    *,
    selected_case_id: str,
) -> dict[str, Any]:
    model_id = _text(model.get("model_id"))
    return {
        "schema_version": MODEL_PAGE_SCHEMA_VERSION,
        "model_id": model_id,
        "slug": _text(model.get("slug"), model_id),
        "display_name": _text(model.get("display_name"), model_id),
        "one_sentence_meaning": _text(
            model.get("one_sentence_meaning"),
            "No source-backed one-sentence meaning is available.",
        ),
        "helps_notice": _string_list(
            model.get("helps_notice"),
            fallback=["No source-backed helps-notice bullets are available."],
        ),
        "use_when": _string_list(
            model.get("use_when"),
            fallback=["No source-backed use-when bullets are available."],
        ),
        "avoid_when": _string_list(model.get("avoid_when")),
        "common_misuse": _string_list(model.get("common_misuse")),
        "failure_modes": _string_list(model.get("failure_modes")),
        "practice_prompts": _string_list(model.get("practice_prompts")),
        "selected_run_backlinks": [
            {
                "label": "Selected run Learn surface",
                "href": f"/runs/{_safe_fragment(selected_case_id)}#learn",
            }
        ],
        "source_refs": _source_refs_from_mapping(model)
        or [_portable_source_ref(model_id, "model_source", "data/model_sources/manifest.json")],
        "source_hashes": _source_hashes(model),
        "curation_status": _text(model.get("curation_status"), "needs_review"),
        "missingness": _missingness(model),
        "non_claims": sorted(MODEL_NON_CLAIMS),
    }


def _relation_page(
    relation: Mapping[str, Any],
    model_lookup: Mapping[str, str],
) -> dict[str, Any]:
    relation_id = _text(relation.get("relation_id"))
    source_model_id = _text(relation.get("source_model_id"))
    target_model_id = _text(relation.get("target_model_id"))
    return {
        "schema_version": RELATION_PAGE_SCHEMA_VERSION,
        "relation_id": relation_id,
        "source_model_id": source_model_id,
        "target_model_id": target_model_id,
        "relation_type": _text(relation.get("relation_type"), "unknown"),
        "plain_language_story": _text(
            relation.get("plain_language_story"),
            "No source-backed plain-language relation story is available.",
        ),
        "why_it_matters": _text(
            relation.get("why_it_matters"),
            "No source-backed why-it-matters note is available.",
        ),
        "misread_risk": _text(
            relation.get("misread_risk"),
            "No source-backed misread risk is available.",
        ),
        "practice_prompt": _text(
            relation.get("practice_prompt"),
            "No source-backed practice prompt is available.",
        ),
        "model_links": [
            {
                "label": model_lookup.get(source_model_id) or source_model_id,
                "href": f"/models/{source_model_id}",
            },
            {
                "label": model_lookup.get(target_model_id) or target_model_id,
                "href": f"/models/{target_model_id}",
            },
        ],
        "source_refs": _source_refs_from_mapping(relation)
        or [_relation_source_ref(relation)],
        "confidence": _text(relation.get("confidence"), "unknown"),
        "curation_status": _text(relation.get("curation_status"), "needs_review"),
        "missingness": _missingness(relation),
        "non_claims": sorted(RELATION_NON_CLAIMS),
    }


def _graph_neighborhood(
    graph: Mapping[str, Any],
    model_lookup: Mapping[str, str],
) -> dict[str, Any]:
    nodes = []
    for node in _object_list(graph.get("nodes")):
        model_id = _text(node.get("model_id"), _text(node.get("node_id")))
        if not model_id:
            continue
        nodes.append(
            {
                "node_id": model_id,
                "label": model_lookup.get(model_id)
                or _text(node.get("label"), model_id),
                "node_type": _text(node.get("node_type"), "model"),
                "href": f"/models/{model_id}",
            }
        )
    edges = []
    for edge in _object_list(graph.get("edges")):
        relation_id = _text(edge.get("relation_id"), _text(edge.get("edge_id")))
        if not relation_id:
            continue
        edges.append(
            {
                "edge_id": relation_id,
                "source_node_id": _text(edge.get("source_node_id")),
                "target_node_id": _text(edge.get("target_node_id")),
                "relation_type": _text(edge.get("relation_type"), "unknown"),
                "navigation_label": _text(edge.get("label"), relation_id),
                "href": f"/relations/{relation_id}",
            }
        )
    return {
        "schema_version": GRAPH_NEIGHBORHOOD_SCHEMA_VERSION,
        "graph_id": _text(graph.get("graph_id"), "selected-run-learning-neighborhood"),
        "graph_scope": _text(graph.get("graph_scope"), "selected_run_learning_neighborhood"),
        "nodes": nodes,
        "edges": edges,
        "source_refs": _source_refs_from_mapping(graph)
        or _source_refs_from_artifacts(graph.get("source_artifacts"))
        or [_portable_source_ref("graph-neighborhood", "graph_source", "selected_run/teacher-learning-packet.json")],
        "layout_hint": _text(graph.get("layout_hint"), "small_neighborhood"),
        "default_focus": _text(
            graph.get("default_focus"),
            nodes[0]["node_id"] if nodes else "missing-focus",
        ),
        "filters": _mapping(graph.get("filters")) or {
            "relation_types": sorted(
                {
                    _text(edge.get("relation_type"))
                    for edge in edges
                    if _text(edge.get("relation_type"))
                }
            )
        },
        "search_enabled": True,
        "missingness": _missingness(graph),
        "non_claims": sorted(GRAPH_NON_CLAIMS),
    }


def _receipt_summary(
    *,
    selected_run_id: str,
    teacher_response: Mapping[str, Any],
    decision_work_status: Mapping[str, Any],
) -> dict[str, Any]:
    decision_status = _text(decision_work_status.get("decision_work_status"))
    source_refs = _dedupe_source_refs(
        [
            *_source_refs_from_teacher_receipts(teacher_response),
            *_source_refs_from_decision_work(decision_work_status),
        ]
    ) or [_portable_source_ref("receipts", "receipt_status", "selected_run/receipts")]
    return {
        "schema_version": RECEIPT_SUMMARY_SCHEMA_VERSION,
        "run_id": selected_run_id,
        "learning_packet_status": "available"
        if teacher_response.get("available")
        else "missing",
        "conversation_understanding_status": _conversation_understanding_status(
            decision_work_status
        ),
        "process_brief_status": _process_brief_status(decision_status),
        "source_refs": source_refs,
        "missingness": {
            "status": "partial"
            if decision_status != "decision_work_available"
            else "complete",
            "missing_fields": _dedupe(
                [
                    *_string_list(decision_work_status.get("missingness")),
                    *(
                        ["decision_work_process_brief"]
                        if decision_status != "decision_work_available"
                        else []
                    ),
                ]
            ),
            "notes": [
                "Receipts summarize custody and status; they do not certify the run."
            ],
        },
        "advanced_links": [
            {"label": "Extraction audit", "href": "/audit/extraction"},
            {"label": "Usage", "href": "/usage"},
            {"label": "Advanced audit", "href": "/audit"},
        ],
        "visible_non_claims": [
            "Not product proof",
            "Not human validation",
            "Not answer correctness",
            "No runtime action authorized",
        ],
        "non_claims": sorted(RECEIPT_NON_CLAIMS),
    }


def _advanced_audit_index(
    *,
    selected_run_id: str,
    result: Mapping[str, Any],
    decision_work_status: Mapping[str, Any],
) -> dict[str, Any]:
    statuses = [
        {
            "artifact_id": "result-json",
            "label": "Result JSON",
            "status": "available" if result else "missing",
            "home_route": "/audit",
        },
        {
            "artifact_id": "extraction",
            "label": "Extraction",
            "status": "available" if result.get("extraction") else "missing",
            "home_route": "/audit/extraction",
        },
        {
            "artifact_id": "usage",
            "label": "Usage",
            "status": "available" if result.get("usage_summary") else "missing",
            "home_route": "/usage",
        },
    ]
    for artifact in _object_list(decision_work_status.get("source_artifacts")):
        artifact_id = _text(artifact.get("artifact_id"))
        if not artifact_id:
            continue
        statuses.append(
            {
                "artifact_id": f"decision-work-{artifact_id}",
                "label": artifact_id.replace("_", " ").title(),
                "status": _text(artifact.get("status"), "available"),
                "home_route": "/audit/extraction",
            }
        )
    return {
        "schema_version": ADVANCED_AUDIT_INDEX_SCHEMA_VERSION,
        "run_id": selected_run_id,
        "advanced_links": [
            {"label": "Audit index", "href": "/audit"},
            {"label": "Extraction audit", "href": "/audit/extraction"},
            {"label": "Usage", "href": "/usage"},
        ],
        "artifact_statuses": statuses,
        "source_refs": [
            _portable_source_ref("advanced-audit-index", "advanced_audit", "selected_run/advanced-audit-index")
        ],
        "missingness": {
            "status": "partial"
            if any(item["status"] != "available" for item in statuses)
            else "complete",
            "missing_fields": [
                item["artifact_id"]
                for item in statuses
                if item["status"] != "available"
            ],
            "notes": [
                "Advanced Audit remains an inspection index, not normal learner copy."
            ],
        },
        "non_claims": sorted(ADVANCED_NON_CLAIMS),
    }


def _teacher_response(
    *,
    selected_case_id: str,
    result: Mapping[str, Any],
    result_path: Path | None,
    supplied: Mapping[str, Any] | None,
) -> dict[str, Any]:
    if supplied is not None:
        return dict(supplied)
    return build_teacher_learning_response(
        selected_case_id,
        dict(result),
        result_path,
    )


def _decision_work_status(
    *,
    selected_case_id: str,
    result: Mapping[str, Any],
    result_path: Path | None,
    supplied: Mapping[str, Any] | None,
) -> dict[str, Any]:
    if supplied is not None:
        return dict(supplied)
    return build_observatory_decision_work_status(
        selected_case_id=selected_case_id,
        result=result,
        result_path=result_path,
    )


def _unavailable_adapter_response(
    *,
    selected_case_id: str,
    selected_run_id: str,
    teacher_response: Mapping[str, Any],
    source_refs: list[dict[str, str]],
) -> dict[str, Any]:
    response = {
        "schema_version": OBSERVATORY_PRODUCT_VIEW_ADAPTER_SCHEMA_VERSION,
        "available": False,
        "selected_case_id": selected_case_id,
        "selected_run_id": selected_run_id,
        "unavailable_reason": _text(
            teacher_response.get("unavailable_reason"),
            "teacher_learning_packet_unavailable",
        ),
        "workspace_schema": WORKSPACE_SCHEMA_VERSION,
        "workspace": None,
        "source_refs": source_refs,
        "missingness": {
            "status": "missing",
            "missing_fields": ["teacher_learning_packet", "product_workspace"],
            "notes": [
                "No matching Teacher learning packet was available, so the adapter did not fake a product workspace."
            ],
        },
        "adapter_guards": _adapter_guards(),
        "non_claims": sorted(WORKSPACE_NON_CLAIMS),
    }
    _assert_no_local_paths(response)
    return response


def _selected_run_id(
    result: Mapping[str, Any],
    result_path: Path | None,
    teacher_response: Mapping[str, Any],
) -> str:
    for candidate in (
        _text(teacher_response.get("selected_run_id")),
        _text(_mapping(result.get("usage_summary")).get("run_id")),
        _text(result.get("run_id")),
        result_path.parent.name if result_path is not None else "",
    ):
        if candidate:
            return candidate
    return "unknown-run"


def _display_title(selected_case_id: str, result: Mapping[str, Any]) -> str:
    extraction = _mapping(result.get("extraction"))
    decision_situation = _text(extraction.get("decision_situation"))
    if decision_situation:
        return _compact_text(decision_situation, limit=140)
    if selected_case_id.startswith("archive:"):
        parts = selected_case_id.split(":", 2)
        if len(parts) == 3 and parts[1]:
            return parts[1].replace("-", " ").title()
    return selected_case_id or "Selected run"


def _run_state(selected_case_id: str) -> str:
    if selected_case_id.startswith("archive:"):
        return "archived"
    if selected_case_id:
        return "current"
    return "unknown"


def _health_label(result: Mapping[str, Any]) -> str:
    health = _mapping(result.get("run_health"))
    overall = _text(health.get("overall")).lower()
    if overall == "healthy":
        return "ok"
    if overall in {"partial", "degraded", "blocked", "unknown"}:
        return overall
    if overall == "critical":
        return "blocked"
    return "unknown"


def _answer_headline(revised_answer: str) -> str:
    if not revised_answer:
        return "No revised answer artifact is available."
    for line in revised_answer.splitlines():
        candidate = _compact_text(line, limit=120)
        if candidate and candidate.lower() not in {
            "updated position",
            "what survived",
            "what changed",
        }:
            return candidate
    return _compact_text(revised_answer, limit=120)


def _outcome_headline(revised_answer: str) -> str:
    if not revised_answer:
        return "No revised answer artifact is available."
    sentences = _sentence_points(revised_answer, limit=1)
    if sentences:
        return sentences[0]
    return _full_plain_text(revised_answer)


def _outcome_stance(revised_answer: str) -> str:
    text = revised_answer.lower()
    if not text:
        return "missing_revised_answer"
    if any(phrase in text for phrase in ("do not launch", "don't launch", "not launch")):
        return "hold_or_do_not_launch"
    if any(word in text for word in ("stage", "staged", "phased", "gate", "narrow")):
        return "stage_or_gate"
    if "launch" in text:
        return "launch_with_conditions"
    if any(word in text for word in ("pause", "hold", "wait")):
        return "hold_or_pause"
    return "answer_available"


def _what_changed_points(
    result: Mapping[str, Any],
    strongest_pressure: str,
) -> list[str]:
    for key in (
        "memo_what_changed",
        "revised_answer_change_reason",
        "memo_take_back_or_set_aside",
        "memo_orientation_note",
    ):
        points = _sentence_points(_text(result.get(key)), limit=4)
        if points:
            return points
    if strongest_pressure:
        return [f"The run made this pressure explicit: {strongest_pressure}"]
    return [
        "No separate what-changed artifact is available for this selected run."
    ]


def _primary_reason_points(revised_answer: str, strongest_pressure: str) -> list[str]:
    sentences = _sentence_points(revised_answer, limit=5)
    if len(sentences) > 1:
        return sentences[1:4]
    if sentences:
        return sentences[:1]
    if strongest_pressure:
        return [strongest_pressure]
    return [
        "No source-backed primary reason artifact is available for this selected run."
    ]


def _confidence_boundary_points(
    revised_answer: str,
    strongest_pressure: str,
) -> list[str]:
    keywords = (
        "if",
        "until",
        "unless",
        "evidence",
        "risk",
        "gate",
        "ready",
        "readiness",
        "support",
        "diligence",
        "depends",
        "confidence",
    )
    boundaries = [
        sentence
        for sentence in _sentence_points(revised_answer, limit=8)
        if any(keyword in sentence.lower() for keyword in keywords)
    ][:3]
    if boundaries:
        return boundaries
    if strongest_pressure:
        return [
            f"Confidence should stay bounded by this pressure: {strongest_pressure}"
        ]
    return [
        "No separate confidence-boundary artifact is available for this selected run."
    ]


def _sentence_points(value: str, *, limit: int) -> list[str]:
    text = _full_plain_text(value)
    if not text:
        return []
    chunks = re.split(r"(?<=[.!?])\s+", text)
    points = []
    for chunk in chunks:
        cleaned = chunk.strip(" -\n\t")
        if cleaned:
            points.append(cleaned)
        if len(points) >= limit:
            break
    return points


def _full_plain_text(value: str) -> str:
    return " ".join(_plain_product_text(_text(value)).split())


def _strongest_pressure(result: Mapping[str, Any]) -> str:
    delta = _mapping(result.get("delta_card"))
    for key in ("top_findings", "findings", "secondary_findings"):
        for item in _object_list(delta.get(key)):
            for field in (
                "description",
                "challenge_statement",
                "summary",
                "finding",
                "title",
            ):
                value = _text(item.get(field))
                if value:
                    return _compact_text(value)
    audit = _mapping(result.get("audit_summary"))
    for item in _object_list(audit.get("deep_check_results")):
        if item.get("detected"):
            value = _text(item.get("finding")) or _text(item.get("summary"))
            if value:
                return _compact_text(value)
    return ""


def _compact_text(value: str, *, fallback: str = "", limit: int = 240) -> str:
    text = " ".join(_plain_product_text(_text(value, fallback)).split())
    if not text:
        return fallback
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0] + "..."


def _plain_product_text(value: str) -> str:
    """Remove Markdown scaffolding before text enters product-view summaries."""

    if not value:
        return ""
    kept_lines: list[str] = []
    heading_fallback: list[str] = []
    for line in value.splitlines():
        stripped = line.strip()
        if re.match(r"#{1,6}\s+", stripped):
            heading = re.sub(r"^#{1,6}\s+", "", stripped).strip()
            if heading:
                heading_fallback.append(heading)
            continue
        kept_lines.append(stripped)
    text = "\n".join(line for line in kept_lines if line).strip()
    if not text:
        text = " ".join(heading_fallback)
    text = re.sub(r"(?m)^\s*[-*+]\s+", "", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    return text.strip()


def _practice_rep(lesson: Mapping[str, Any]) -> dict[str, str]:
    practice = _mapping(lesson.get("practice_rep"))
    return {
        "prompt": _text(practice.get("prompt"), "No practice prompt supplied."),
        "user_action": _text(
            practice.get("user_action"),
            "No practice action supplied.",
        ),
    }


def _relation_id_from_href_or_label(link: Mapping[str, Any]) -> str:
    href = _text(link.get("href"))
    if href:
        stem = href.rstrip("/").rsplit("/", 1)[-1]
        if stem:
            return stem.replace(".md", "")
    label = _text(link.get("label"))
    return _safe_fragment(label)


def _relation_source_ref(relation: Mapping[str, Any]) -> dict[str, str]:
    relation_id = _text(relation.get("relation_id"), "relation-source")
    raw_ref = _text(relation.get("source_quote_or_ref"))
    path = raw_ref.split(":", 1)[0] if raw_ref else "selected_run/relation-source"
    return _portable_source_ref(relation_id, "relation_source_ref", path)


def _source_hashes(model: Mapping[str, Any]) -> dict[str, str]:
    hashes = model.get("source_hashes")
    if isinstance(hashes, dict) and hashes:
        return {str(key): str(value) for key, value in hashes.items()}
    model_id = _text(model.get("model_id"), "unknown-model")
    return {
        f"data/model_sources/{model_id}.md": (
            "0000000000000000000000000000000000000000000000000000000000000000"
        )
    }


def _missingness(payload: Mapping[str, Any]) -> dict[str, Any]:
    missingness = _mapping(payload.get("missingness"))
    status = _text(missingness.get("status"), "partial")
    fields = _string_list(missingness.get("missing_fields"))
    notes = _string_list(missingness.get("notes"))
    return {
        "status": status,
        "missing_fields": fields,
        "notes": notes
        or ["Missingness was preserved from the source artifact when available."],
    }


def _source_refs_from_workspace(workspace: Mapping[str, Any]) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    for key in (
        "selected_run_summary",
        "outcome_summary",
        "outcome_value",
        "learning_packet",
        "graph_neighborhood",
        "receipt_summary",
        "advanced_audit_index",
    ):
        refs.extend(_source_refs_from_mapping(_mapping(workspace.get(key))))
    refs.extend(_source_refs_from_objects(_object_list(workspace.get("model_pages"))))
    refs.extend(_source_refs_from_objects(_object_list(workspace.get("relation_pages"))))
    refs.extend(_source_refs_from_mapping(workspace))
    return _dedupe_source_refs(refs)


def _source_refs_from_objects(items: list[Mapping[str, Any]]) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    for item in items:
        refs.extend(_source_refs_from_mapping(item))
    return refs


def _source_refs_from_mapping(payload: Mapping[str, Any]) -> list[dict[str, str]]:
    refs = []
    for ref in _object_list(payload.get("source_refs")):
        source_id = _text(ref.get("source_id"), _text(ref.get("artifact_id")))
        source_type = _text(
            ref.get("source_type"),
            _text(ref.get("artifact_type"), "source_ref"),
        )
        if source_type == "canonical_markdown":
            source_type = "canonical_model_markdown"
        path = _text(ref.get("path"), _text(ref.get("ref"), "selected_run/source"))
        if source_id and path:
            refs.append(_portable_source_ref(source_id, source_type, path))
    return refs


def _source_refs_from_artifacts(value: Any) -> list[dict[str, str]]:
    refs = []
    for artifact in _object_list(value):
        artifact_id = _text(artifact.get("artifact_id"))
        artifact_type = _text(artifact.get("artifact_type"), "artifact")
        path = _text(artifact.get("path"), _text(artifact.get("ref")))
        if artifact_id and path:
            refs.append(_portable_source_ref(artifact_id, artifact_type, path))
    return refs


def _source_refs_from_teacher_receipts(
    teacher_response: Mapping[str, Any],
) -> list[dict[str, str]]:
    receipts = _mapping(
        _mapping(_mapping(teacher_response.get("tab_payloads")).get("Receipts")).get(
            "receipts"
        )
    )
    return _dedupe_source_refs(
        [
            *_source_refs_from_mapping(receipts),
            *_source_refs_from_artifacts(receipts.get("artifact_refs")),
        ]
    )


def _source_refs_from_decision_work(
    decision_work_status: Mapping[str, Any],
) -> list[dict[str, str]]:
    refs = []
    for artifact in _object_list(decision_work_status.get("source_artifacts")):
        artifact_id = _text(artifact.get("artifact_id"))
        ref = _text(artifact.get("ref"))
        if artifact_id and ref:
            refs.append(_portable_source_ref(artifact_id, "decision_work_artifact", ref))
    return refs


def _result_source_ref(result_path: Path | None) -> dict[str, str]:
    path = "selected_run/result.json"
    if result_path is not None:
        path = f"selected_run/{result_path.name}"
    return _portable_source_ref("selected-run-result", "run_artifact", path)


def _portable_source_ref(
    source_id: str,
    source_type: str,
    path: str,
) -> dict[str, str]:
    portable_path = path.replace("\\", "/")
    if portable_path.startswith("/") or "://" in portable_path:
        portable_path = portable_path.rsplit("/", 1)[-1] or "selected_run/source"
    if portable_path.startswith("../"):
        portable_path = portable_path.lstrip("./")
    return {
        "source_id": source_id,
        "source_type": source_type,
        "path": portable_path,
    }


def _missing_fields_from_objects(items: list[Mapping[str, Any]]) -> list[str]:
    fields: list[str] = []
    for item in items:
        fields.extend(_missing_fields_from_mapping(item))
    return fields


def _missing_fields_from_mapping(payload: Mapping[str, Any]) -> list[str]:
    return _string_list(_mapping(payload.get("missingness")).get("missing_fields"))


def _conversation_understanding_status(
    decision_work_status: Mapping[str, Any],
) -> str:
    live = _text(decision_work_status.get("live_extraction_status"))
    richer = _text(decision_work_status.get("decision_work_status"))
    if richer == "decision_work_available" or live == "available":
        return "available"
    if richer == "decision_work_deferred":
        return "deferred"
    if richer in {"decision_work_blocked", "decision_work_malformed"}:
        return "blocked"
    return "missing"


def _process_brief_status(decision_work_status: str) -> str:
    if decision_work_status == "decision_work_available":
        return "available"
    if decision_work_status == "decision_work_deferred":
        return "deferred"
    if decision_work_status in {"decision_work_blocked", "decision_work_malformed"}:
        return "blocked"
    return "not_requested"


def _agent_memory_download_href(selected_case_id: str) -> str:
    return (
        "/api/case/"
        + quote(str(selected_case_id), safe="")
        + "/conversation-memory.md?include_raw_conversation=1"
    )


def _adapter_guards() -> dict[str, Any]:
    return {
        "read_only": True,
        "provider_or_model_calls": False,
        "lolla_skill_invoked": False,
        "new_lolla_run_created": False,
        "runtime_behavior_changed": False,
        "archive_mutated": False,
        "ui_rendering_added": False,
        "legacy_spa_or_bundle_touched": False,
    }


def _safe_fragment(value: str) -> str:
    fragment = "".join(
        char.lower() if char.isalnum() else "-" for char in _text(value)
    )
    while "--" in fragment:
        fragment = fragment.replace("--", "-")
    return fragment.strip("-") or "selected-run"


def _mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _object_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [dict(item) for item in value if isinstance(item, Mapping)]


def _string_list(value: Any, *, fallback: list[str] | None = None) -> list[str]:
    if isinstance(value, list):
        result = [str(item) for item in value if isinstance(item, str) and item.strip()]
        if result:
            return result
    return list(fallback or [])


def _text(value: Any, fallback: str = "") -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return fallback


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item and item not in seen:
            result.append(item)
            seen.add(item)
    return result


def _dedupe_source_refs(refs: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[tuple[str, str, str]] = set()
    result: list[dict[str, str]] = []
    for ref in refs:
        key = (ref["source_id"], ref["source_type"], ref["path"])
        if key in seen:
            continue
        result.append(ref)
        seen.add(key)
    return result


def _assert_no_local_paths(payload: Any) -> None:
    rendered = json.dumps(payload, sort_keys=True)
    markers = (
        "/" + "Users/",
        "Desktop/" + "Apps",
        "\\" + "Users\\",
    )
    if any(marker in rendered for marker in markers):
        raise ObservatoryProductViewAdapterError(
            "Observatory product view adapter response contains a local path marker"
        )


__all__ = [
    "OBSERVATORY_PRODUCT_VIEW_ADAPTER_SCHEMA_VERSION",
    "ObservatoryProductViewAdapterError",
    "build_observatory_product_view_response",
]
