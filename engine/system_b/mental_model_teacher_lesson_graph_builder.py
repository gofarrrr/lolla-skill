"""Lesson-neighborhood graph data builder for Mental Model Teacher.

This PR-P7 builder emits a small Visual Graph object from already product-safe
lesson, model, and relation page contracts. It does not render browser graph UI,
use embeddings, call providers, or wire runtime behavior.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .mental_model_teacher_lesson_renderer import load_contract_fixture_lesson
from .mental_model_teacher_pilot_page_builder import REPO_ROOT, build_pilot_page_data
from .mental_model_teacher_product_contracts import (
    GRAPH_NON_CLAIMS,
    VISUAL_GRAPH_SCHEMA_VERSION,
    validate_mental_model_page,
    validate_relation_page,
    validate_teacher_lesson,
    validate_visual_graph,
)


DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs/product/mental-model-teacher-lesson-graph-v0"
LESSON_GRAPH_MANIFEST_SCHEMA_VERSION = (
    "lolla.mental_model_teacher.lesson_graph_data_manifest.v0"
)


class MentalModelTeacherLessonGraphBuilderError(ValueError):
    """Raised when lesson graph data cannot be built safely."""


def build_fixture_lesson_graph(root: Path | str | None = None) -> dict[str, Any]:
    """Build the default fixture lesson graph from checked-in product inputs."""

    repo_root = Path(root) if root is not None else REPO_ROOT
    lesson = load_contract_fixture_lesson(repo_root)
    page_package = build_pilot_page_data(repo_root)
    return build_lesson_neighborhood_graph(lesson, page_package)


def build_lesson_neighborhood_graph(
    lesson_payload: dict[str, Any],
    page_package: dict[str, Any],
) -> dict[str, Any]:
    """Build a Visual Graph object for one Teacher lesson neighborhood."""

    lesson = validate_teacher_lesson(lesson_payload)
    model_pages = [
        validate_mental_model_page(page) for page in page_package["model_pages"]
    ]
    relation_pages = [
        validate_relation_page(page) for page in page_package["relation_pages"]
    ]
    model_lookup = {page["model_id"]: page for page in model_pages}
    relation_lookup = {page["relation_id"]: page for page in relation_pages}

    model_ids = _ordered_model_ids(lesson)
    relation_ids = _ordered_relation_ids(lesson)

    missing_models = [model_id for model_id in model_ids if model_id not in model_lookup]
    missing_relations = [
        relation_id for relation_id in relation_ids if relation_id not in relation_lookup
    ]
    if missing_models:
        raise MentalModelTeacherLessonGraphBuilderError(
            "lesson graph missing model pages: " + ", ".join(missing_models)
        )
    if missing_relations:
        raise MentalModelTeacherLessonGraphBuilderError(
            "lesson graph missing relation pages: " + ", ".join(missing_relations)
        )

    nodes = [_node_from_model_page(model_lookup[model_id]) for model_id in model_ids]
    node_ids = {node["node_id"] for node in nodes}
    edges = []
    skipped_relations = []
    for relation_id in relation_ids:
        relation = relation_lookup[relation_id]
        if (
            relation["source_model_id"] not in node_ids
            or relation["target_model_id"] not in node_ids
        ):
            skipped_relations.append(relation_id)
            continue
        edges.append(_edge_from_relation_page(relation, model_lookup))

    graph = {
        "schema_version": VISUAL_GRAPH_SCHEMA_VERSION,
        "graph_id": f"lesson-neighborhood-{lesson['lesson_id']}",
        "graph_scope": "lesson_neighborhood",
        "lesson_id": lesson["lesson_id"],
        "case_id": lesson["case_id"],
        "nodes": nodes,
        "edges": edges,
        "source_artifacts": [
            {
                "artifact_id": "teacher-lesson-contract-fixture",
                "path": "docs/product/mental-model-teacher-product-contract-examples-v0.json",
                "source_type": "teacher_lesson_contract_fixture",
            },
            {
                "artifact_id": "pilot-render-manifest",
                "path": "docs/product/mental-model-teacher-pilot-render-v0/manifest.json",
                "source_type": "static_page_render_manifest",
            },
            {
                "artifact_id": "lesson-render-manifest",
                "path": "docs/product/mental-model-teacher-lesson-render-v0/manifest.json",
                "source_type": "lesson_render_manifest",
            },
        ],
        "layout_hint": "small_neighborhood",
        "default_focus": model_ids[0],
        "filters": {
            "relation_types": sorted({edge["relation_type"] for edge in edges}),
            "node_types": ["mental_model"],
            "max_nodes": 10,
        },
        "missingness": _graph_missingness(lesson, skipped_relations),
        "non_claims": sorted(GRAPH_NON_CLAIMS),
    }
    _assert_no_local_paths(graph)
    return validate_visual_graph(graph)


def write_fixture_lesson_graph_package(
    root: Path | str | None = None,
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
) -> dict[str, Any]:
    """Write the default fixture lesson graph JSON and manifest."""

    graph = build_fixture_lesson_graph(root)
    target_dir = Path(output_dir)
    graph_path = target_dir / f"{graph['lesson_id']}.graph.json"
    _write_json(graph_path, graph)

    manifest = {
        "schema_version": LESSON_GRAPH_MANIFEST_SCHEMA_VERSION,
        "builder": "engine.system_b.mental_model_teacher_lesson_graph_builder",
        "source_graph_schema": VISUAL_GRAPH_SCHEMA_VERSION,
        "graph_data_status": "fixture_lesson_neighborhood_graph_data_ready_for_review",
        "output_dir": "docs/product/mental-model-teacher-lesson-graph-v0",
        "graph_count": 1,
        "graphs": [
            {
                "graph_id": graph["graph_id"],
                "lesson_id": graph["lesson_id"],
                "path": _rel(graph_path, target_dir),
                "node_count": len(graph["nodes"]),
                "edge_count": len(graph["edges"]),
            }
        ],
        "browser_graph_ui_built": False,
        "embeddings_used": False,
        "teacher_artifacts_used": False,
        "real_teacher_case_claimed": False,
        "runtime_integration_authorized": False,
        "provider_or_model_calls_used": False,
        "non_claims": {
            "product_proof": False,
            "human_validated": False,
            "answer_correctness": False,
            "advice_correctness": False,
            "runtime_integration_authorized": False,
            "graph_edges_are_proof": False,
            "embedding_similarity_is_validated_relation_semantics": False,
            "agent_or_automatic_action_authorized": False,
        },
        "stop_before": [
            "browser graph UI",
            "full-corpus graph",
            "runtime integration",
            "provider or model calls",
            "product proof claims",
            "human validation claims",
        ],
    }
    _assert_no_local_paths(manifest)
    _write_json(target_dir / "manifest.json", manifest)
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build Mental Model Teacher fixture lesson graph data.",
    )
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    manifest = write_fixture_lesson_graph_package(args.root, args.output_dir)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def _ordered_model_ids(lesson: dict[str, Any]) -> list[str]:
    seen = set()
    result = []
    for item in lesson["model_stack"]:
        model_id = str(item["model_id"])
        if model_id not in seen:
            seen.add(model_id)
            result.append(model_id)
    return result


def _ordered_relation_ids(lesson: dict[str, Any]) -> list[str]:
    seen = set()
    result = []
    for link in lesson["relation_links"]:
        relation_id = Path(str(link["href"])).stem
        if relation_id not in seen:
            seen.add(relation_id)
            result.append(relation_id)
    return result


def _node_from_model_page(page: dict[str, Any]) -> dict[str, Any]:
    return {
        "node_id": page["model_id"],
        "model_id": page["model_id"],
        "label": page["display_name"],
        "node_type": "mental_model",
        "href": f"../mental-model-teacher-pilot-render-v0/models/{page['slug']}.md",
        "source_status": page["curation_status"],
        "missingness_status": page["missingness"]["status"],
    }


def _edge_from_relation_page(
    page: dict[str, Any],
    model_lookup: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    source = model_lookup[page["source_model_id"]]
    target = model_lookup[page["target_model_id"]]
    return {
        "edge_id": page["relation_id"],
        "source_node_id": page["source_model_id"],
        "target_node_id": page["target_model_id"],
        "relation_id": page["relation_id"],
        "relation_type": page["relation_type"],
        "label": f"{source['display_name']} and {target['display_name']}",
        "href": (
            "../mental-model-teacher-pilot-render-v0/relations/"
            f"{page['relation_id']}.md"
        ),
        "source_status": page["curation_status"],
        "missingness_status": page["missingness"]["status"],
        "confidence": page["confidence"],
    }


def _graph_missingness(
    lesson: dict[str, Any],
    skipped_relations: list[str],
) -> dict[str, Any]:
    fields = list(lesson["missingness"].get("missing_fields") or [])
    for field in ("browser_graph_ui", "rendered_layout"):
        if field not in fields:
            fields.append(field)
    notes = list(lesson["missingness"].get("notes") or [])
    notes.append("Graph data only; PR-P8 is the first browser graph UI slice.")
    if skipped_relations:
        fields.append("relations_outside_selected_neighborhood")
        notes.append(
            "Some lesson relation links were skipped because their endpoints were outside the selected nodes."
        )
    return {
        "status": "partial",
        "missing_fields": fields,
        "notes": notes,
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    _assert_no_local_paths(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.name


def _assert_no_local_paths(payload: Any) -> None:
    rendered = json.dumps(payload, sort_keys=True) if not isinstance(payload, str) else payload
    markers = (
        "/" + "Users/",
        "Desktop/" + "Apps",
        "\\" + "Users\\",
    )
    if any(marker in rendered for marker in markers):
        raise MentalModelTeacherLessonGraphBuilderError(
            "lesson graph data contains a local path marker"
        )


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
