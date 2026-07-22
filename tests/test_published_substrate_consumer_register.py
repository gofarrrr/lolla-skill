from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTER_PATH = ROOT / "docs/evals/lolla-published-substrate-consumer-register-v1.json"


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_every_engine_graph_filename_reference_has_a_declared_disposition() -> None:
    register = _json(REGISTER_PATH)
    declared = {row["path"] for row in register["direct_reference_inventory"]}
    observed = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "engine/system_b").glob("*.py")
        if "knowledge_graph.json" in path.read_text(encoding="utf-8")
        or "relationship_graph.json" in path.read_text(encoding="utf-8")
    }

    assert observed == declared


def test_migrated_runtime_consumers_use_the_boundary_or_a_passed_snapshot() -> None:
    register = _json(REGISTER_PATH)
    migrated = register["migrated_runtime_consumers"]
    assert migrated
    assert all(row["semantic_output_change"] is False for row in migrated)
    assert all((ROOT / row["path"]).is_file() for row in migrated)

    direct_loaders = {
        "engine/system_b/pipeline.py",
        "engine/system_b/relation_graph.py",
        "engine/system_b/tendency_catalog.py",
        "engine/system_b/pressure_router.py",
        "engine/system_b/v60_enrichment.py",
        "engine/system_b/authority_phase1_builder.py",
        "engine/system_b/stress_phase1_builder.py",
        "scripts/run_route.py",
        "scripts/run_triage.py",
        "scripts/run_companion.py",
    }
    assert {row["path"] for row in migrated} == direct_loaders
    for path in direct_loaders:
        text = (ROOT / path).read_text(encoding="utf-8")
        assert "PublishedKnowledgeSubstrate" in text


def test_boundary_policy_forbids_runtime_compilation_repair_and_provider_use() -> None:
    policy = _json(REGISTER_PATH)["policy"]
    assert policy["publication_read_owner"] == (
        "engine/system_b/published_knowledge_substrate.py"
    )
    assert policy["runtime_compilation_allowed"] is False
    assert policy["runtime_semantic_repair_allowed"] is False
    assert policy["provider_calls_allowed"] == 0
