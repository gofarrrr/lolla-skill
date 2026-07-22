from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "engine"
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))

from system_b.published_knowledge_substrate import (
    PublishedKnowledgeSubstrate,
    PublishedSubstrateError,
)
from system_b.relation_graph import RelationGraph, RelationNeighbor
from system_b.pipeline import PipelineConfig, SystemBPipeline


def _write_minimal_publication(root: Path, *, empty: bool = False) -> None:
    data = root / "data"
    data.mkdir(parents=True)
    models = {} if empty else {"a": {"display_name": "A"}, "b": {"display_name": "B"}}
    relations = [] if empty else [
        {
            "source_model_id": "a",
            "target_model_id": "b",
            "edge_type": "ally",
            "composition_affinity": 0.9,
        }
    ]
    (data / "knowledge_graph.json").write_text(
        json.dumps({"models": models, "tendencies": {}}),
        encoding="utf-8",
    )
    (data / "relationship_graph.json").write_text(
        json.dumps(relations),
        encoding="utf-8",
    )


def test_current_published_substrate_is_complete_immutable_and_directional() -> None:
    result = PublishedKnowledgeSubstrate.open(ROOT)

    assert result.status == "complete"
    assert result.provider_calls == 0
    assert result.runtime_generation_attempted is False
    assert set(result.coverage.values()) == {"complete"}
    snapshot = result.require_snapshot()
    assert snapshot.release_id == "lolla-graph-2026-04-21-v1"
    assert len(snapshot.models) == 222
    assert len(snapshot.relations) == 1_358
    assert snapshot.knowledge_graph_payload() == json.loads(
        (ROOT / "data" / "knowledge_graph.json").read_text(encoding="utf-8")
    )
    assert snapshot.relationship_graph_payload() == json.loads(
        (ROOT / "data" / "relationship_graph.json").read_text(encoding="utf-8")
    )

    relation = snapshot.relations[0]
    assert relation in snapshot.outgoing(relation.source_model_id)
    assert relation in snapshot.incoming_references(relation.target_model_id)
    assert relation not in snapshot.outgoing(relation.target_model_id)
    assert relation.source_model_id != relation.target_model_id
    assert relation.compiled_pointer == "data/relationship_graph.json#/0"
    assert relation.custody is not None
    assert relation.custody.compiled_pointer == relation.compiled_pointer
    assert relation.custody.authoring_path.startswith("data/curation/relation_semantics/")
    assert relation.custody.source_path.startswith("data/model_sources/")

    with pytest.raises(KeyError):
        snapshot.model("Commitment Bias")
    with pytest.raises(TypeError):
        snapshot.models["new"] = snapshot.models["abstraction"]  # type: ignore[index]
    with pytest.raises(TypeError):
        relation.payload["edge_type"] = "reversed"  # type: ignore[index]


def test_loader_preserves_missing_failed_partial_and_completed_zero(tmp_path: Path) -> None:
    missing = PublishedKnowledgeSubstrate.open(tmp_path / "missing")
    assert missing.status == "missing"
    with pytest.raises(PublishedSubstrateError, match="missing"):
        missing.require_snapshot()

    failed_root = tmp_path / "failed"
    (failed_root / "data").mkdir(parents=True)
    (failed_root / "data" / "knowledge_graph.json").write_text("not-json", encoding="utf-8")
    (failed_root / "data" / "relationship_graph.json").write_text("[]", encoding="utf-8")
    failed = PublishedKnowledgeSubstrate.open(failed_root)
    assert failed.status == "failed"

    partial_root = tmp_path / "partial"
    _write_minimal_publication(partial_root)
    partial = PublishedKnowledgeSubstrate.open(partial_root)
    assert partial.status == "partial"
    assert partial.coverage["published_release_identity"] == "missing"
    assert partial.coverage["relation_source_custody"] == "missing"
    with pytest.raises(PublishedSubstrateError, match="partial"):
        partial.require_snapshot()
    partial_snapshot = partial.require_snapshot(allow_partial=True)
    assert partial_snapshot.outgoing("a")[0].target_model_id == "b"
    assert partial_snapshot.incoming_references("b")[0].source_model_id == "a"

    zero_root = tmp_path / "zero"
    _write_minimal_publication(zero_root, empty=True)
    completed_zero = PublishedKnowledgeSubstrate.open(zero_root)
    assert completed_zero.status == "completed_zero"
    assert completed_zero.require_snapshot().relations == ()
    assert completed_zero.coverage["model_registry"] == "completed_zero"


def test_build_layout_and_repository_data_layout_resolve_to_identical_payloads(
    tmp_path: Path,
) -> None:
    (tmp_path / "build").symlink_to(ROOT / "data", target_is_directory=True)
    snapshot = PublishedKnowledgeSubstrate.open(tmp_path).require_snapshot()

    assert snapshot.knowledge_graph_payload() == json.loads(
        (ROOT / "data" / "knowledge_graph.json").read_text(encoding="utf-8")
    )
    assert snapshot.relationship_graph_payload() == json.loads(
        (ROOT / "data" / "relationship_graph.json").read_text(encoding="utf-8")
    )


def test_relation_graph_consumer_is_object_equivalent_after_boundary_migration() -> None:
    raw_edges = json.loads(
        (ROOT / "data" / "relationship_graph.json").read_text(encoding="utf-8")
    )
    legacy_adjacency: dict[str, list[RelationNeighbor]] = {}
    for edge in raw_edges:
        source = str(edge.get("source_model_id", "")).strip()
        target = str(edge.get("target_model_id", "")).strip()
        if not source or not target:
            continue
        legacy_adjacency.setdefault(source, []).append(
            RelationNeighbor(
                model_id=target,
                edge_type=str(edge.get("edge_type", "")).strip().lower(),
                composition_affinity=float(edge.get("composition_affinity", 0.0) or 0.0),
                source_description=str(edge.get("source_description", "") or ""),
                affinity_rationale=str(edge.get("affinity_rationale", "") or ""),
                activation_condition=str(edge.get("activation_condition", "") or ""),
            )
        )
    expected = {source: tuple(neighbors) for source, neighbors in legacy_adjacency.items()}

    migrated = RelationGraph.load(ROOT)
    assert migrated._graph == expected
    assert migrated._degree_counts == RelationGraph(expected)._degree_counts


def test_live_pipeline_loads_one_repository_publication_without_provider_use(
    tmp_path: Path,
) -> None:
    class BoundaryThatMustNotRun:
        def run_json(self, *_args, **_kwargs):
            raise AssertionError("pipeline loading must not call a provider boundary")

        def run_json_with_metadata(self, *_args, **_kwargs):
            raise AssertionError("pipeline loading must not call a provider boundary")

    (tmp_path / "build").symlink_to(ROOT / "data", target_is_directory=True)
    pipeline = SystemBPipeline.load(
        tmp_path,
        BoundaryThatMustNotRun(),
        config=PipelineConfig(enable_embeddings=False, enable_deep_checks=False),
    )

    assert len(pipeline._companion_knowledge_graph["models"]) == 222
    assert len(pipeline._companion_relation_graph) == 1_358
    assert pipeline._relation_graph._graph == RelationGraph.load(tmp_path)._graph
