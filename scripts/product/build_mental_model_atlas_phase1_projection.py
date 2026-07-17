#!/usr/bin/env python3
"""Build the source-bound Mental Model Atlas Phase 1 review package.

This module is deterministic custody machinery.  It copies existing source and
curation text into a bounded local review projection; it does not infer relation
meaning, repair missing content, call a provider, or authorize publication.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "lolla.atlas_projection.v1"
MANIFEST_SCHEMA_VERSION = "lolla.atlas_projection_manifest.v1"
MODEL_PAGE_SCHEMA_VERSION = "lolla.atlas_model_page.v1"
RELATION_PAGE_SCHEMA_VERSION = "lolla.atlas_relation_page.v1"
BUILDER_VERSION = "lolla.mental_model_atlas_phase1_builder.v1"
CANONICAL_DATA_COMMIT = "2f05fd1ca7081f602317d670faad8d1293d5b0ff"
PAGE_SIZE = 40

EXPECTED_SOURCE_HASHES = {
    "data/model_sources/manifest.json": (
        "140783b30cecc2fc65ce25e3fff7f38ac75f776367b15c9664bb078227c02b93"
    ),
    "data/knowledge_graph.json": (
        "5689b79868339ce9221b799eac88870a6053b69a67ba3aaef3f2ba5cd62efdae"
    ),
    "data/relationship_graph.json": (
        "89808c4585498f3880b4d7fa0110d64cd46f7acff312c0870fc6cb9a97e752cf"
    ),
}

ORDINARY_MODEL_IDS = (
    "abstraction",
    "active-listening",
    "authority-bias",
    "confirmation-bias",
    "critical-thinking",
    "decomposition",
    "feynman-technique",
    "first-principles-thinking",
    "intellectual-humility",
    "jobs-to-be-done",
    "prisoners-dilemma",
    "rationalization",
    "root-cause-analysis",
    "simplification",
    "systems-thinking",
    "theory-induced-blindness",
)

NON_CLAIMS = [
    "not_graph_relevance_proof",
    "not_relation_truth_certification",
    "not_importance_ranking",
    "not_mastery_certification",
    "not_publication_authorization",
    "not_runtime_or_observatory_integration",
    "not_product_usefulness_proof",
]

FORBIDDEN_RELATION_FIELDS = {
    "affinity",
    "composition_affinity",
    "rank",
    "score",
    "weight",
}


class AtlasProjectionError(ValueError):
    """Raised when source custody or projection structure is invalid."""


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def build_phase1_package(root: Path) -> dict[str, Any]:
    root = root.resolve()
    custody = _load_and_verify_sources(root)
    manifest_payload = _load_json(root / "data/model_sources/manifest.json")
    knowledge_graph = _load_json(root / "data/knowledge_graph.json")
    relationship_graph = _load_json(root / "data/relationship_graph.json")

    source_records = {
        item["model_id"]: item for item in manifest_payload["files"]
    }
    models = knowledge_graph["models"]
    relation_records = [
        _relation_record(root, item, index)
        for index, item in enumerate(relationship_graph)
    ]

    artifacts: dict[str, dict[str, Any]] = {}

    ordinary_set = set(ORDINARY_MODEL_IDS)
    ordinary_relations = [
        record
        for record in relation_records
        if record["source_model_id"] in ordinary_set
        and record["target_model_id"] in ordinary_set
    ]
    ordinary_relations = _ordered_relations(ordinary_relations)
    artifacts["ordinary-navigation.json"] = _projection(
        root=root,
        projection_id="phase1-ordinary-navigation-v1",
        fixture_id="ordinary_navigation",
        focus_model_id=None,
        model_ids=list(ORDINARY_MODEL_IDS),
        eligible_relations=ordinary_relations,
        relation_page=ordinary_relations[:PAGE_SIZE],
        models=models,
        source_records=source_records,
        custody=custody,
        layout_variant="ordinary",
        extra_scope={
            "description": "frozen_16_model_real_data_review_slice",
            "corpus_model_count": len(models),
        },
    )

    mixed_relations = [
        record
        for record in relation_records
        if record["source_model_id"] == "abstraction"
        and record["target_model_id"] == "first-principles-thinking"
        and record["relation_type"] in {"ally", "tension"}
    ]
    mixed_relations = _ordered_relations(mixed_relations)
    artifacts["mixed-parallel-relations.json"] = _projection(
        root=root,
        projection_id="phase1-mixed-parallel-relations-v1",
        fixture_id="mixed_parallel_relations",
        focus_model_id="abstraction",
        model_ids=["abstraction", "first-principles-thinking"],
        eligible_relations=mixed_relations,
        relation_page=mixed_relations,
        models=models,
        source_records=source_records,
        custody=custody,
        layout_variant="pair",
        extra_scope={"semantic_fixture": "parallel_ally_and_tension"},
    )

    bidirectional_relations = [
        record
        for record in relation_records
        if {record["source_model_id"], record["target_model_id"]}
        == {"active-listening", "prisoners-dilemma"}
    ]
    bidirectional_relations = _ordered_relations(bidirectional_relations)
    artifacts["explicit-bidirectionality.json"] = _projection(
        root=root,
        projection_id="phase1-explicit-bidirectionality-v1",
        fixture_id="explicit_bidirectionality",
        focus_model_id="active-listening",
        model_ids=["active-listening", "prisoners-dilemma"],
        eligible_relations=bidirectional_relations,
        relation_page=bidirectional_relations,
        models=models,
        source_records=source_records,
        custody=custody,
        layout_variant="pair",
        extra_scope={"semantic_fixture": "two_source_authored_directions"},
    )

    hub_relations = [
        record
        for record in relation_records
        if record["source_model_id"] == "confirmation-bias"
        or record["target_model_id"] == "confirmation-bias"
    ]
    hub_relations = _ordered_relations(hub_relations)
    hub_layout_model_ids = sorted(
        {
            endpoint
            for record in hub_relations
            for endpoint in (
                record["source_model_id"],
                record["target_model_id"],
            )
        },
        key=lambda value: (value != "confirmation-bias", value),
    )
    for page_number, start in enumerate(
        range(0, len(hub_relations), PAGE_SIZE), start=1
    ):
        hub_page = hub_relations[start : start + PAGE_SIZE]
        hub_model_ids = [
            model_id
            for model_id in hub_layout_model_ids
            if any(
                model_id
                in (record["source_model_id"], record["target_model_id"])
                for record in hub_page
            )
        ]
        artifacts[f"confirmation-bias-hub-page-{page_number}.json"] = _projection(
        root=root,
        projection_id=f"phase1-confirmation-bias-hub-page-{page_number}-v1",
        fixture_id="confirmation_bias_hub",
        focus_model_id="confirmation-bias",
        model_ids=hub_model_ids,
        eligible_relations=hub_relations,
        relation_page=hub_page,
        models=models,
        source_records=source_records,
        custody=custody,
        layout_variant="hub",
        page_number=page_number,
        layout_universe_ids=hub_layout_model_ids,
        extra_scope={
            "semantic_fixture": "high_fan_in_pagination",
            "unique_neighbor_count": len(
                {
                    record["target_model_id"]
                    if record["source_model_id"] == "confirmation-bias"
                    else record["source_model_id"]
                    for record in hub_relations
                }
            ),
        },
        )

    medium_relation = next(
        record
        for record in relation_records
        if record["source_model_id"] == "authenticity"
        and record["target_model_id"] == "rationalization"
        and record["relation_type"] == "antagonist"
        and record["confidence"] == "medium"
    )
    artifacts["medium-confidence-relation.json"] = _projection(
        root=root,
        projection_id="phase1-medium-confidence-relation-v1",
        fixture_id="medium_confidence_relation",
        focus_model_id="authenticity",
        model_ids=["authenticity", "rationalization"],
        eligible_relations=[medium_relation],
        relation_page=[medium_relation],
        models=models,
        source_records=source_records,
        custody=custody,
        layout_variant="pair",
        extra_scope={
            "semantic_fixture": "medium_confidence_not_certification"
        },
    )

    model_page = _model_page(
        root,
        models["abstraction"],
        source_records["abstraction"],
        custody,
    )
    artifacts["pages/model-abstraction.json"] = model_page

    relation_page = _relation_page(
        relationship_graph=relationship_graph,
        translated_relations=relation_records,
        custody=custody,
    )
    artifacts[
        "pages/relation-abstraction-first-principles-thinking-ally.json"
    ] = relation_page

    for payload in artifacts.values():
        if payload.get("schema_version") == SCHEMA_VERSION:
            validate_projection(payload)

    manifest_artifacts: list[dict[str, Any]] = []
    for path, payload in artifacts.items():
        entry: dict[str, Any] = {
            "path": path,
            "artifact_type": _artifact_type(payload["schema_version"]),
            "schema_version": payload["schema_version"],
            "sha256": sha256_bytes(canonical_json_bytes(payload)),
        }
        if payload["schema_version"] == SCHEMA_VERSION:
            entry.update(
                {
                    "projection_id": payload["projection_id"],
                    "node_count": len(payload["models"]),
                    "eligible_relation_count": payload["page"][
                        "eligible_count"
                    ],
                    "shown_relation_count": payload["page"]["shown_count"],
                    "omitted_relation_count": payload["page"]["omitted_count"],
                    "layout_id": payload["layout"]["layout_id"],
                    "coordinate_sha256": payload["layout"][
                        "coordinate_sha256"
                    ],
                }
            )
        manifest_artifacts.append(entry)

    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "package_status": "local_review_only",
        "builder": {
            "builder_id": BUILDER_VERSION,
            "provider_calls": 0,
            "provider_cost_usd": 0.0,
            "deterministic": True,
        },
        "source_custody": custody,
        "artifacts": manifest_artifacts,
        "publication_status": "blocked_pending_rights_and_human_review",
        "non_claims": NON_CLAIMS,
    }
    return {"artifacts": artifacts, "manifest": manifest}


def _load_and_verify_sources(root: Path) -> dict[str, Any]:
    for relative_path, expected in EXPECTED_SOURCE_HASHES.items():
        path = root / relative_path
        if not path.is_file():
            raise AtlasProjectionError(f"missing canonical source: {relative_path}")
        actual = sha256_path(path)
        if actual != expected:
            raise AtlasProjectionError(
                f"canonical source hash drift: {relative_path}: {actual}"
            )
    return {
        "canonical_data_commit": CANONICAL_DATA_COMMIT,
        "source_hash_status": "verified",
        "sources": [
            {"path": path, "sha256": sha256}
            for path, sha256 in sorted(EXPECTED_SOURCE_HASHES.items())
        ],
    }


def _model_record(
    root: Path,
    model_id: str,
    model: dict[str, Any],
    source_record: dict[str, Any],
) -> dict[str, Any]:
    source_ref = {
        "source_type": "canonical_model_markdown",
        "path": source_record["path"],
        "sha256": source_record["sha256"],
    }
    source_text = (root / source_record["path"]).read_text(encoding="utf-8")
    definition = _first_core_principle_paragraph(source_text)
    summary = _first_sentence(_source_plain_text(definition))
    helps_notice = model["select_when"][0]
    knowledge_ref = {
        "source_type": "compiled_checked_in_curation",
        "path": "data/knowledge_graph.json",
        "json_pointer": f"/models/{_json_pointer_escape(model_id)}/select_when/0",
        "sha256": EXPECTED_SOURCE_HASHES["data/knowledge_graph.json"],
    }
    status = _publication_status()
    return {
        "model_id": model_id,
        "slug": model["slug"],
        "display_name": model["display_name"],
        "summary": _text_block(
            summary, [source_ref], status="source_format_normalized"
        ),
        "helps_notice": _text_block(helps_notice, [knowledge_ref]),
        "source_ref": source_ref,
        "curation_refs": {
            "activation": _file_ref(root, f"data/curation/{model_id}.json"),
            "intervention": _file_ref(
                root, f"data/curation/intervention_semantics/{model_id}.json"
            ),
            "relations": _file_ref(
                root, f"data/curation/relation_semantics/{model_id}.json"
            ),
        },
        "status": status,
    }


def _relation_record(
    root: Path, raw: dict[str, Any], source_record_index: int
) -> dict[str, Any]:
    source_id = raw["source_model_id"]
    target_id = raw["target_model_id"]
    relation_type = raw["edge_type"]
    graph_ref = {
        "source_type": "curated_relationship_graph_record",
        "path": "data/relationship_graph.json",
        "json_pointer": f"/{source_record_index}",
        "sha256": EXPECTED_SOURCE_HASHES["data/relationship_graph.json"],
    }
    curation_path = f"data/curation/relation_semantics/{source_id}.json"
    refs = [graph_ref]
    if (root / curation_path).is_file():
        refs.append(_file_ref(root, curation_path, "relation_semantics_curation"))
    return {
        "relation_id": f"{source_id}__{target_id}__{relation_type}",
        "source_model_id": source_id,
        "target_model_id": target_id,
        "relation_type": relation_type,
        "direction": "source_authored",
        "is_reciprocal": bool(raw["is_reciprocal"]),
        "summary": raw["source_description"],
        "confidence": raw["confidence"],
        "curation_status": "curated_checked_in",
        "source_refs": refs,
        "missingness": _complete_missingness(),
        "source_record_index": source_record_index,
    }


def _projection(
    *,
    root: Path,
    projection_id: str,
    fixture_id: str,
    focus_model_id: str | None,
    model_ids: list[str],
    eligible_relations: list[dict[str, Any]],
    relation_page: list[dict[str, Any]],
    models: dict[str, dict[str, Any]],
    source_records: dict[str, dict[str, Any]],
    custody: dict[str, Any],
    layout_variant: str,
    extra_scope: dict[str, Any],
    page_number: int = 1,
    layout_universe_ids: list[str] | None = None,
) -> dict[str, Any]:
    layout = _layout(model_ids, layout_variant, layout_universe_ids)
    shown_count = len(relation_page)
    eligible_count = len(eligible_relations)
    before_count = (page_number - 1) * PAGE_SIZE
    after_count = eligible_count - before_count - shown_count
    scope = {
        "focus_model_id": focus_model_id,
        "model_selection": "frozen_development_fixture",
        "relation_types": ["ally", "antagonist", "tension"],
        "directions": ["incoming", "outgoing"],
        **extra_scope,
    }
    records = []
    for relation in relation_page:
        public_relation = dict(relation)
        public_relation.pop("source_record_index", None)
        records.append(public_relation)
    return {
        "schema_version": SCHEMA_VERSION,
        "projection_id": projection_id,
        "fixture_id": fixture_id,
        "projection_status": "development_fixture",
        "source_custody": custody,
        "scope": scope,
        "models": [
            _model_record(root, model_id, models[model_id], source_records[model_id])
            for model_id in model_ids
        ],
        "relations": records,
        "page": {
            "page_number": page_number,
            "page_size": PAGE_SIZE,
            "eligible_count": eligible_count,
            "shown_count": shown_count,
            "omitted_count": eligible_count - shown_count,
            "before_count": before_count,
            "after_count": after_count,
            "ordering": (
                "source_model_id,target_model_id,relation_type,source_record_index"
            ),
            "relation_ids": [item["relation_id"] for item in records],
        },
        "layout": layout,
        "missingness": _complete_missingness(),
        "non_claims": NON_CLAIMS,
    }


def _layout(
    model_ids: list[str],
    variant: str,
    universe_ids: list[str] | None = None,
) -> dict[str, Any]:
    layout_ids = universe_ids or model_ids
    configuration = {
        "variant": variant,
        "relation_weight_policy": "uniform",
        "browser_layout_recomputation": False,
        "coordinate_precision": 6,
        "layout_universe_count": len(layout_ids),
        "layout_universe_sha256": sha256_bytes(
            canonical_json_bytes(layout_ids)
        ),
    }
    universe_coordinates: list[dict[str, Any]] = []
    if len(layout_ids) == 2:
        universe_coordinates = [
            {"model_id": layout_ids[0], "x": -1.0, "y": 0.0},
            {"model_id": layout_ids[1], "x": 1.0, "y": 0.0},
        ]
    else:
        golden_angle = math.pi * (3 - math.sqrt(5))
        for index, model_id in enumerate(layout_ids):
            if index == 0 and variant == "hub":
                x, y = 0.0, 0.0
            else:
                adjusted = index if variant != "hub" else index - 1
                ring = 1 + adjusted // 8
                radius = 1.0 + (ring - 1) * 0.82
                angle = adjusted * golden_angle - math.pi / 2
                x = round(math.cos(angle) * radius, 6)
                y = round(math.sin(angle) * radius, 6)
            universe_coordinates.append(
                {"model_id": model_id, "x": x, "y": y}
            )
    visible_ids = set(model_ids)
    coordinates = [
        item
        for item in universe_coordinates
        if item["model_id"] in visible_ids
    ]
    config_hash = sha256_bytes(canonical_json_bytes(configuration))
    coordinate_hash = sha256_bytes(canonical_json_bytes(coordinates))
    return {
        "layout_id": f"phase1-{variant}-{coordinate_hash[:12]}",
        "algorithm": "deterministic_concentric_fixture",
        "algorithm_version": "1",
        "configuration": configuration,
        "configuration_sha256": config_hash,
        "coordinate_sha256": coordinate_hash,
        "coordinates": coordinates,
    }


def _model_page(
    root: Path,
    model: dict[str, Any],
    source_record: dict[str, Any],
    custody: dict[str, Any],
) -> dict[str, Any]:
    model_id = "abstraction"
    source_ref = {
        "source_type": "canonical_model_markdown",
        "path": source_record["path"],
        "sha256": source_record["sha256"],
    }
    source_text = (root / source_record["path"]).read_text(encoding="utf-8")
    knowledge_ref = {
        "source_type": "compiled_checked_in_curation",
        "path": "data/knowledge_graph.json",
        "json_pointer": f"/models/{model_id}",
        "sha256": EXPECTED_SOURCE_HASHES["data/knowledge_graph.json"],
    }
    sections = {
        "definition": _text_section(
            _source_plain_text(_first_core_principle_paragraph(source_text)),
            [source_ref],
            status="source_format_normalized",
        ),
        "use_when": _list_section(model["select_when"], [knowledge_ref]),
        "avoid_when": _list_section(model["danger_when"], [knowledge_ref]),
        "reasoning_profile": {
            "input_type": model["input_type"],
            "output_type": model["output_type"],
            "reasoning_types": model["reasoning_types"],
            "provenance": [knowledge_ref],
            "status": "source_copied",
            "missingness": _complete_missingness(),
        },
        "failure_modes": {
            "items": [
                {
                    "text": item["mode"],
                    "mitigation": item["mitigation"],
                    "source_quote": item["source_quote"],
                    "extraction_type": item["extraction_type"],
                    "confidence": item["confidence"],
                }
                for item in model["failure_modes"]
            ],
            "provenance": [knowledge_ref],
            "status": "source_copied",
            "missingness": _complete_missingness(),
        },
        "premortem_questions": _list_section(
            [item["description"] for item in model["premortem_questions"]],
            [knowledge_ref],
        ),
        "heuristics": _list_section(
            [item["description"] for item in model["heuristics"]],
            [knowledge_ref],
        ),
    }
    return {
        "schema_version": MODEL_PAGE_SCHEMA_VERSION,
        "page_id": "model-abstraction",
        "page_status": "local_review_only",
        "source_custody": custody,
        "model": {
            "model_id": model_id,
            "slug": model["slug"],
            "display_name": model["display_name"],
            "source_ref": source_ref,
        },
        "sections": sections,
        "status": {
            **_publication_status(),
            "content_generation": "source_copied_or_format_normalized_only",
        },
        "missingness": _complete_missingness(),
        "non_claims": NON_CLAIMS,
    }


def _relation_page(
    *,
    relationship_graph: list[dict[str, Any]],
    translated_relations: list[dict[str, Any]],
    custody: dict[str, Any],
) -> dict[str, Any]:
    selected_raw = next(
        item
        for item in relationship_graph
        if item["source_model_id"] == "abstraction"
        and item["target_model_id"] == "first-principles-thinking"
        and item["edge_type"] == "ally"
    )
    tension_raw = next(
        item
        for item in relationship_graph
        if item["source_model_id"] == "abstraction"
        and item["target_model_id"] == "first-principles-thinking"
        and item["edge_type"] == "tension"
    )
    selected = next(
        item
        for item in translated_relations
        if item["relation_id"]
        == "abstraction__first-principles-thinking__ally"
    )
    selected = dict(selected)
    selected.pop("source_record_index", None)
    graph_ref = selected["source_refs"][0]
    parallel_ids = sorted(
        item["relation_id"]
        for item in translated_relations
        if item["source_model_id"] == "abstraction"
        and item["target_model_id"] == "first-principles-thinking"
    )
    reverse_ids = sorted(
        item["relation_id"]
        for item in translated_relations
        if item["source_model_id"] == "first-principles-thinking"
        and item["target_model_id"] == "abstraction"
    )
    sections = {
        "relation_summary": _text_section(
            selected_raw["source_description"], [graph_ref]
        ),
        "why_it_matters": _text_section(
            selected_raw["affinity_rationale"], [graph_ref]
        ),
        "misread_risk": _text_section(
            tension_raw["source_description"],
            [
                {
                    "source_type": "parallel_tension_boundary",
                    "path": "data/relationship_graph.json",
                    "json_pointer": f"/{relationship_graph.index(tension_raw)}",
                    "sha256": EXPECTED_SOURCE_HASHES[
                        "data/relationship_graph.json"
                    ],
                }
            ],
        ),
        "activation_condition": _text_section(
            selected_raw.get("activation_condition", ""), [graph_ref]
        ),
        "source_excerpt": _text_section(selected_raw["source_quote"], [graph_ref]),
        "parallel_record_context": {
            "parallel_relation_ids": parallel_ids,
            "reverse_relation_ids": reverse_ids,
            "provenance": [graph_ref],
            "status": "source_copied",
            "missingness": _complete_missingness(),
        },
    }
    return {
        "schema_version": RELATION_PAGE_SCHEMA_VERSION,
        "page_id": "relation-abstraction-first-principles-thinking-ally",
        "page_status": "local_review_only",
        "source_custody": custody,
        "relation": selected,
        "sections": sections,
        "status": {
            **_publication_status(),
            "content_generation": "source_copied_only",
        },
        "missingness": _complete_missingness(),
        "non_claims": NON_CLAIMS,
    }


def validate_projection(projection: dict[str, Any]) -> None:
    if projection.get("schema_version") != SCHEMA_VERSION:
        raise AtlasProjectionError("projection schema version is invalid")
    models = projection.get("models")
    relations = projection.get("relations")
    if not isinstance(models, list) or not isinstance(relations, list):
        raise AtlasProjectionError("projection models and relations must be lists")
    model_ids = [item.get("model_id") for item in models]
    if len(model_ids) != len(set(model_ids)):
        raise AtlasProjectionError("projection model IDs must be unique")
    known = set(model_ids)
    relation_ids: set[str] = set()
    for relation in relations:
        if relation.get("source_model_id") not in known or relation.get(
            "target_model_id"
        ) not in known:
            raise AtlasProjectionError("relation endpoint is outside projection")
        relation_id = relation.get("relation_id")
        if relation_id in relation_ids:
            raise AtlasProjectionError("relation IDs must be unique")
        relation_ids.add(relation_id)
        if FORBIDDEN_RELATION_FIELDS.intersection(relation):
            raise AtlasProjectionError("forbidden visual score field in relation")
    page = projection.get("page", {})
    page_number = page.get("page_number")
    eligible = page.get("eligible_count")
    shown = page.get("shown_count")
    omitted = page.get("omitted_count")
    before = page.get("before_count")
    after = page.get("after_count")
    if not isinstance(page_number, int) or page_number < 1:
        raise AtlasProjectionError("page number must be a positive integer")
    if not all(isinstance(value, int) and value >= 0 for value in (eligible, shown, omitted, before, after)):
        raise AtlasProjectionError("page counts must be nonnegative integers")
    if eligible != shown + omitted or omitted != before + after:
        raise AtlasProjectionError("page counts do not reconcile")
    if shown != len(relations) or shown > PAGE_SIZE:
        raise AtlasProjectionError("page counts do not match relation records")
    if page.get("page_size") != PAGE_SIZE:
        raise AtlasProjectionError("projection page size must match frozen bound")
    if before != (page_number - 1) * PAGE_SIZE:
        raise AtlasProjectionError("page before count does not match page number")
    if page.get("relation_ids") != [item["relation_id"] for item in relations]:
        raise AtlasProjectionError("page relation IDs do not match relation records")
    layout = projection.get("layout", {})
    coordinates = layout.get("coordinates")
    if not isinstance(coordinates, list):
        raise AtlasProjectionError("layout coordinates must be a list")
    if {item.get("model_id") for item in coordinates} != known:
        raise AtlasProjectionError("layout coordinates must cover every model")
    expected_coordinate_hash = sha256_bytes(canonical_json_bytes(coordinates))
    if layout.get("coordinate_sha256") != expected_coordinate_hash:
        raise AtlasProjectionError("coordinate hash does not match coordinates")


def write_phase1_package(root: Path, output_dir: Path) -> dict[str, Any]:
    package = build_phase1_package(root)
    output_dir.mkdir(parents=True, exist_ok=True)
    for relative_path, payload in package["artifacts"].items():
        target = output_dir / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(canonical_json_bytes(payload))
    (output_dir / "manifest.json").write_bytes(
        canonical_json_bytes(package["manifest"])
    )
    return package


def _publication_status() -> dict[str, str]:
    return {
        "source": "verified_hash_bound",
        "curation": "checked_in_curated",
        "human_review": "pending_phase1_review",
        "licensing": "unknown",
        "publication": "blocked_pending_rights_review",
        "missingness": "complete",
    }


def _complete_missingness() -> dict[str, Any]:
    return {"status": "complete", "missing_fields": [], "notes": []}


def _text_block(
    text: str,
    provenance: list[dict[str, Any]],
    *,
    status: str = "source_copied",
) -> dict[str, Any]:
    return {
        "text": text,
        "provenance": provenance,
        "status": status,
        "missingness": _complete_missingness(),
    }


def _text_section(
    text: str,
    provenance: list[dict[str, Any]],
    *,
    status: str = "source_copied",
) -> dict[str, Any]:
    if not text:
        return {
            "text": "",
            "provenance": provenance,
            "status": "missing",
            "missingness": {
                "status": "missing",
                "missing_fields": ["text"],
                "notes": ["Source did not provide this field."],
            },
        }
    return _text_block(text, provenance, status=status)


def _list_section(
    items: list[str], provenance: list[dict[str, Any]]
) -> dict[str, Any]:
    return {
        "items": items,
        "provenance": provenance,
        "status": "source_copied",
        "missingness": _complete_missingness(),
    }


def _file_ref(
    root: Path, relative_path: str, source_type: str = "checked_in_curation"
) -> dict[str, str]:
    path = root / relative_path
    if not path.is_file():
        raise AtlasProjectionError(f"missing curation source: {relative_path}")
    return {
        "source_type": source_type,
        "path": relative_path,
        "sha256": sha256_path(path),
    }


def _ordered_relations(relations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        relations,
        key=lambda item: (
            item["source_model_id"],
            item["target_model_id"],
            item["relation_type"],
            item["source_record_index"],
        ),
    )


def _first_core_principle_paragraph(text: str) -> str:
    paragraphs = [
        re.sub(r"\s+", " ", item).strip()
        for item in re.split(r"\n\s*\n", text.strip())
        if item.strip()
    ]
    heading_pattern = re.compile(
        r"^\*{0,2}Core Principles(?: and Analogies)?\*{0,2}:?$",
        re.IGNORECASE,
    )
    for index, paragraph in enumerate(paragraphs):
        if not heading_pattern.fullmatch(paragraph):
            continue
        for candidate in paragraphs[index + 1 :]:
            if _is_source_prose(candidate):
                return candidate
    raise AtlasProjectionError(
        "canonical model source has no prose after Core Principles heading"
    )


def _is_source_prose(paragraph: str) -> bool:
    """Admit prose, not Markdown structure, as copied model-page text."""

    if re.fullmatch(r"[-*_]{3,}", paragraph):
        return False
    if paragraph.startswith(("#", "|", "•", "- ", "* ")):
        return False
    if len(paragraph.split()) < 8:
        return False
    return bool(re.search(r"[.!?]", paragraph))


def _source_plain_text(text: str) -> str:
    """Remove Markdown presentation markers without changing source wording."""

    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    text = re.sub(r"(?<!\\)(\*\*|__|`)", "", text)
    return re.sub(r"\s+", " ", text).strip()


def _first_sentence(text: str) -> str:
    match = re.match(r"^(.+?[.!?])(?:\s|$)", text)
    return match.group(1) if match else text


def _json_pointer_escape(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def _artifact_type(schema_version: str) -> str:
    return {
        SCHEMA_VERSION: "projection",
        MODEL_PAGE_SCHEMA_VERSION: "model_page",
        RELATION_PAGE_SCHEMA_VERSION: "relation_page",
    }[schema_version]


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AtlasProjectionError(f"could not load {path}: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output directory; defaults to the app's Phase 1 public data directory.",
    )
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output or root / "apps/mental-model-atlas/public/data/phase1"
    package = build_phase1_package(root)
    if not args.validate_only:
        write_phase1_package(root, output)
    print(
        json.dumps(
            {
                "artifact_count": len(package["artifacts"]),
                "output": str(output),
                "provider_calls": 0,
                "provider_cost_usd": 0.0,
                "status": "valid" if args.validate_only else "written",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
