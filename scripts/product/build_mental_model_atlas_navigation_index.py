#!/usr/bin/env python3
"""Build the deterministic Atlas neighborhood-navigation index.

The index exposes sanitized, source-bound model and relationship records for
client-side incident-edge traversal. It does not infer new relationships,
score models, call a provider, or change the frozen Phase 1 fixtures.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.product.build_mental_model_atlas_phase1_projection import (
    NON_CLAIMS,
    _load_and_verify_sources,
    _load_json,
    _model_record,
    _relation_record,
    canonical_json_bytes,
    sha256_bytes,
)


SCHEMA_VERSION = "lolla.atlas_navigation_index.v1"
MANIFEST_SCHEMA_VERSION = "lolla.atlas_navigation_index_manifest.v1"
BUILDER_VERSION = "lolla.mental_model_atlas_navigation_index_builder.v1"


class AtlasNavigationIndexError(ValueError):
    """Raised when deterministic navigation-index custody is invalid."""


def build_navigation_package(root: Path) -> dict[str, Any]:
    root = root.resolve()
    custody = _load_and_verify_sources(root)
    source_manifest = _load_json(root / "data/model_sources/manifest.json")
    knowledge_graph = _load_json(root / "data/knowledge_graph.json")
    relationship_graph = _load_json(root / "data/relationship_graph.json")
    source_records = {
        item["model_id"]: item for item in source_manifest["files"]
    }
    model_ids = sorted(knowledge_graph["models"])
    models = [
        _model_record(
            root,
            model_id,
            knowledge_graph["models"][model_id],
            source_records[model_id],
        )
        for model_id in model_ids
    ]
    relations = []
    for source_record_index, raw in enumerate(relationship_graph):
        relation = _relation_record(root, raw, source_record_index)
        relation.pop("source_record_index", None)
        relations.append(relation)

    index = {
        "schema_version": SCHEMA_VERSION,
        "index_id": "atlas-canonical-neighborhood-navigation-v1",
        "index_status": "local_review_only",
        "source_custody": custody,
        "scope": {
            "corpus_model_count": len(models),
            "relation_record_count": len(relations),
            "relation_types": ["ally", "antagonist", "tension"],
            "directions": ["incoming", "outgoing"],
            "selection_operation": "exact_incident_edge_filter_only",
            "browser_semantic_inference": False,
            "page_size": 40,
        },
        "models": models,
        "relations": relations,
        "missingness": {
            "status": "complete",
            "missing_fields": [],
            "notes": [],
        },
        "non_claims": [
            *NON_CLAIMS,
            "not_relationship_discovery",
            "not_dynamic_semantic_inference",
            "not_complete_model_page_publication",
        ],
    }
    validate_navigation_index(index)
    index_bytes = canonical_json_bytes(index)
    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "package_status": "local_review_only",
        "builder_id": BUILDER_VERSION,
        "source_custody": custody,
        "index": {
            "path": "neighborhood-index.json",
            "sha256": sha256_bytes(index_bytes),
            "model_count": len(models),
            "relation_count": len(relations),
        },
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
        "publication_status": "blocked_pending_rights_and_human_review",
        "non_claims": index["non_claims"],
    }
    return {"index": index, "manifest": manifest}


def validate_navigation_index(index: dict[str, Any]) -> None:
    if index.get("schema_version") != SCHEMA_VERSION:
        raise AtlasNavigationIndexError("navigation index schema is invalid")
    models = index.get("models")
    relations = index.get("relations")
    if not isinstance(models, list) or not isinstance(relations, list):
        raise AtlasNavigationIndexError("models and relations must be lists")
    model_ids = [item.get("model_id") for item in models]
    if len(model_ids) != len(set(model_ids)):
        raise AtlasNavigationIndexError("model IDs must be unique")
    known = set(model_ids)
    relation_ids: set[str] = set()
    forbidden = {"affinity", "composition_affinity", "rank", "score", "weight"}
    for relation in relations:
        if relation.get("source_model_id") not in known or relation.get(
            "target_model_id"
        ) not in known:
            raise AtlasNavigationIndexError("relation endpoint is outside corpus")
        relation_id = relation.get("relation_id")
        if relation_id in relation_ids:
            raise AtlasNavigationIndexError("relation IDs must be unique")
        relation_ids.add(relation_id)
        if forbidden.intersection(relation):
            raise AtlasNavigationIndexError("navigation relation contains a score")
    scope = index.get("scope", {})
    if scope.get("corpus_model_count") != len(models) or scope.get(
        "relation_record_count"
    ) != len(relations):
        raise AtlasNavigationIndexError("declared index counts do not reconcile")


def write_navigation_package(root: Path, output_dir: Path) -> dict[str, Any]:
    package = build_navigation_package(root)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "neighborhood-index.json").write_bytes(
        canonical_json_bytes(package["index"])
    )
    (output_dir / "manifest.json").write_bytes(
        canonical_json_bytes(package["manifest"])
    )
    return package


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[2]
    )
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output or root / "apps/mental-model-atlas/public/data/navigation-v1"
    package = build_navigation_package(root)
    if not args.validate_only:
        write_navigation_package(root, output)
    print(
        json.dumps(
            {
                "model_count": len(package["index"]["models"]),
                "relation_count": len(package["index"]["relations"]),
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
