from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping


DEFAULT_CANONICAL_SOURCE_DIR = Path(
    "/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216"
)
RUNTIME_GRAPH_FIELDS = (
    "select_when",
    "danger_when",
    "failure_modes",
    "premortem_questions",
    "heuristics",
    "reasoning_types",
)


def build_enrichment_coverage_audit(
    root: Path,
    *,
    knowledge_graph_path: Path | None = None,
    affordances_path: Path | None = None,
    source_manifest_path: Path | None = None,
    compiled_chunks_path: Path | None = None,
    canonical_source_dir: Path | None = DEFAULT_CANONICAL_SOURCE_DIR,
) -> dict[str, Any]:
    """Report deterministic breadth/depth coverage for the reasoning substrate.

    This function only counts and cross-references existing artifacts. It does
    not infer affordances, score model usefulness, or select final pressures.
    """

    root = Path(root)
    knowledge_graph = _load_json(knowledge_graph_path or root / "data" / "knowledge_graph.json")
    affordances = _load_json(
        affordances_path
        or root / "data" / "compiled" / "model_affordances" / "affordances_v4.json"
    )
    source_manifest = _load_json(
        source_manifest_path or root / "data" / "model_sources" / "manifest.json"
    )
    compiled_chunks = _load_json(
        compiled_chunks_path or root / "data" / "curated" / "compiled_chunks.json"
    )

    models = _mapping(knowledge_graph.get("models"))
    runtime_model_ids = set(str(model_id) for model_id in models)
    v4_records = [_mapping(record) for record in _list(affordances.get("model_records"))]
    v4_model_ids = {
        str(record.get("model_id"))
        for record in v4_records
        if str(record.get("model_id", "")).strip()
    }
    source_custody_model_ids = {
        str(item.get("model_id"))
        for item in _list(source_manifest.get("files"))
        if str(item.get("model_id", "")).strip()
    }

    missing_v4 = sorted(runtime_model_ids - v4_model_ids)
    missing_source_custody = sorted(runtime_model_ids - source_custody_model_ids)
    graph_field_coverage = _runtime_graph_field_coverage(models)
    reasoning_type_gaps = _reasoning_type_coverage_gaps(models, v4_model_ids)
    static_lane_priorities = _static_lane_signal_priorities(
        knowledge_graph=knowledge_graph,
        compiled_chunks=compiled_chunks,
        graph_only_model_ids=set(missing_v4),
    )
    canonical_availability = _canonical_markdown_availability(
        models=models,
        canonical_source_dir=canonical_source_dir,
    )

    return {
        "audit_version": "reasoning_substrate_coverage.v1",
        "runtime_model_count": len(runtime_model_ids),
        "v4_reviewed_model_count": len(v4_model_ids),
        "graph_only_runtime_model_count": len(missing_v4),
        "source_custody_model_count": len(source_custody_model_ids & runtime_model_ids),
        "runtime_model_ids_missing_source_custody_count": len(missing_source_custody),
        "runtime_model_ids_missing_source_custody": missing_source_custody,
        "runtime_model_ids_missing_v4": missing_v4,
        "v4_model_ids_outside_runtime_graph": sorted(v4_model_ids - runtime_model_ids),
        "runtime_graph_field_coverage": graph_field_coverage,
        "reasoning_type_coverage_gaps": reasoning_type_gaps,
        "canonical_markdown_availability": canonical_availability,
        "static_lane_signal_graph_only_priorities": static_lane_priorities,
        "recommended_expansion_batches": _recommended_expansion_batches(
            missing_v4_model_ids=missing_v4,
            static_lane_priorities=static_lane_priorities,
            canonical_available_model_ids=set(canonical_availability["available_model_ids"]),
        ),
    }


def _runtime_graph_field_coverage(models: Mapping[str, Any]) -> dict[str, dict[str, int]]:
    coverage: dict[str, dict[str, int]] = {}
    for field in RUNTIME_GRAPH_FIELDS:
        models_with_field = 0
        total_items = 0
        for model in (_mapping(value) for value in models.values()):
            value = model.get(field)
            item_count = _field_item_count(value)
            if item_count > 0:
                models_with_field += 1
                total_items += item_count
        coverage[field] = {
            "models_with_field": models_with_field,
            "total_items": total_items,
        }
    return coverage


def _reasoning_type_coverage_gaps(
    models: Mapping[str, Any],
    v4_model_ids: set[str],
) -> dict[str, dict[str, int]]:
    by_type: dict[str, set[str]] = defaultdict(set)
    for model_id, model in models.items():
        for reasoning_type in _list(_mapping(model).get("reasoning_types")):
            text = str(reasoning_type).strip()
            if text:
                by_type[text].add(str(model_id))

    gaps: dict[str, dict[str, int]] = {}
    for reasoning_type in sorted(
        by_type,
        key=lambda key: (-len(by_type[key] - v4_model_ids), key),
    ):
        runtime_ids = by_type[reasoning_type]
        reviewed_ids = runtime_ids & v4_model_ids
        graph_only_ids = runtime_ids - v4_model_ids
        gaps[reasoning_type] = {
            "runtime_model_count": len(runtime_ids),
            "v4_reviewed_model_count": len(reviewed_ids),
            "graph_only_model_count": len(graph_only_ids),
        }
    return gaps


def _static_lane_signal_priorities(
    *,
    knowledge_graph: Mapping[str, Any],
    compiled_chunks: Mapping[str, Any],
    graph_only_model_ids: set[str],
) -> list[dict[str, Any]]:
    sources: dict[str, Counter[str]] = defaultdict(Counter)

    for chunk in _list(compiled_chunks.get("chunks")):
        model_id = str(_mapping(chunk).get("model_id", "")).strip()
        if model_id:
            sources[model_id]["lane1_compiled_chunk"] += 1

    for tendency in _mapping(knowledge_graph.get("tendencies")).values():
        item = _mapping(tendency)
        for model_id in _list(item.get("antidote_models")):
            sources[str(model_id)]["lane1_tendency_antidote"] += 1
        for model_id in _list(item.get("core_models")):
            sources[str(model_id)]["lane1_tendency_core"] += 1

    for model_ids in _mapping(knowledge_graph.get("reframing_routing")).values():
        for model_id in _list(model_ids):
            sources[str(model_id)]["lane3_reframing_route"] += 1

    dimensions = _mapping(
        _mapping(knowledge_graph.get("structural_coverage_routing")).get("dimensions")
    )
    for dimension in dimensions.values():
        for model_id in _list(_mapping(dimension).get("models")):
            sources[str(model_id)]["lane4_structural_route"] += 1

    rows = []
    for model_id, source_counts in sources.items():
        if model_id not in graph_only_model_ids:
            continue
        rows.append(
            {
                "model_id": model_id,
                "static_lane_signal_count": sum(source_counts.values()),
                "static_lane_signal_sources": dict(sorted(source_counts.items())),
            }
        )
    return sorted(
        rows,
        key=lambda row: (-int(row["static_lane_signal_count"]), str(row["model_id"])),
    )


def _canonical_markdown_availability(
    *,
    models: Mapping[str, Any],
    canonical_source_dir: Path | None,
) -> dict[str, Any]:
    if canonical_source_dir is None:
        return {
            "canonical_source_dir": "",
            "directory_exists": False,
            "available_model_count": 0,
            "missing_model_count": len(models),
            "available_model_ids": [],
            "missing_model_ids": sorted(str(model_id) for model_id in models),
        }

    source_dir = Path(canonical_source_dir)
    available: list[str] = []
    missing: list[str] = []
    directory_exists = source_dir.exists()
    for model_id, model in models.items():
        source_file = str(_mapping(model).get("source_file", "")).strip()
        if source_file and directory_exists and (source_dir / source_file).exists():
            available.append(str(model_id))
        else:
            missing.append(str(model_id))
    return {
        "canonical_source_dir": str(source_dir),
        "directory_exists": directory_exists,
        "available_model_count": len(available),
        "missing_model_count": len(missing),
        "available_model_ids": sorted(available),
        "missing_model_ids": sorted(missing),
    }


def _recommended_expansion_batches(
    *,
    missing_v4_model_ids: list[str],
    static_lane_priorities: list[Mapping[str, Any]],
    canonical_available_model_ids: set[str],
    batch_size: int = 25,
) -> list[dict[str, Any]]:
    priority_ids = [
        str(row.get("model_id"))
        for row in static_lane_priorities
        if str(row.get("model_id")) in canonical_available_model_ids
    ]
    remaining = [
        model_id
        for model_id in missing_v4_model_ids
        if model_id in canonical_available_model_ids and model_id not in set(priority_ids)
    ]
    selected = (priority_ids + remaining)[:batch_size]
    return [
        {
            "batch_id": "static-lane-signal-graph-only-custody-batch-1",
            "selection_rule": (
                "graph-only runtime models with existing static lane-route signals, "
                "source availability, and no reviewed v4 record"
            ),
            "batch_size": len(selected),
            "model_ids": selected,
        }
    ]


def _field_item_count(value: Any) -> int:
    if isinstance(value, list):
        return len(value)
    if isinstance(value, dict):
        return len(value)
    return 1 if str(value or "").strip() else 0


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: expected JSON object")
    return payload


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []
