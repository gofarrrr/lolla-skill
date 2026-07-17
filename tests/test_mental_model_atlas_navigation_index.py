from __future__ import annotations

import json
from pathlib import Path

from scripts.product.build_mental_model_atlas_navigation_index import (
    build_navigation_package,
    canonical_json_bytes,
)


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "apps/mental-model-atlas/public/data/navigation-v1"


def test_checked_in_navigation_index_rebuilds_from_canonical_graph() -> None:
    package = build_navigation_package(ROOT)
    index = package["index"]

    assert index["schema_version"] == "lolla.atlas_navigation_index.v1"
    assert len(index["models"]) == 222
    assert len(index["relations"]) == 1_358
    assert (DATA_DIR / "neighborhood-index.json").read_bytes() == (
        canonical_json_bytes(index)
    )
    assert (DATA_DIR / "manifest.json").read_bytes() == canonical_json_bytes(
        package["manifest"]
    )


def test_navigation_index_preserves_exact_incident_records_and_source_order() -> None:
    index = build_navigation_package(ROOT)["index"]
    relationships = json.loads(
        (ROOT / "data/relationship_graph.json").read_text(encoding="utf-8")
    )
    by_model: dict[str, list[dict]] = {}
    for relation in index["relations"]:
        by_model.setdefault(relation["source_model_id"], []).append(relation)
        by_model.setdefault(relation["target_model_id"], []).append(relation)

    assert len(by_model["abstraction"]) == 12
    assert len(by_model["critical-thinking"]) == 48
    assert len(by_model["root-cause-analysis"]) == 14
    assert len(by_model["confirmation-bias"]) == 233
    assert [item["relation_id"] for item in index["relations"]] == [
        f"{item['source_model_id']}__{item['target_model_id']}__{item['edge_type']}"
        for item in relationships
    ]
    assert [item["source_refs"][0]["json_pointer"] for item in index["relations"]] == [
        f"/{index}" for index in range(len(relationships))
    ]


def test_navigation_index_excludes_visual_scores_and_declares_no_semantic_inference() -> None:
    package = build_navigation_package(ROOT)
    index = package["index"]
    forbidden = {"affinity", "composition_affinity", "rank", "score", "weight"}

    assert all(forbidden.isdisjoint(relation) for relation in index["relations"])
    assert index["scope"]["selection_operation"] == (
        "exact_incident_edge_filter_only"
    )
    assert index["scope"]["browser_semantic_inference"] is False
    assert index["scope"]["corpus_model_count"] == 222
    assert index["scope"]["relation_record_count"] == 1_358
    assert package["manifest"]["provider_calls"] == 0
    assert package["manifest"]["provider_cost_usd"] == 0.0
