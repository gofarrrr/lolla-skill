from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "engine"
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))

from system_b.compilation_bundle import (
    GraphCompilationError,
    KnowledgeCompiler,
    _embedding_staleness_report,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_candidate_compiler_reconstructs_both_published_graphs_exactly(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    result = KnowledgeCompiler.load(ROOT).compile(output_dir=output)

    assert result.is_valid, result.errors
    assert result.bundle.model_count == 222
    assert result.bundle.knowledge_edge_count == 1_742
    assert result.bundle.relationship_edge_count == 1_358
    for name in ("knowledge_graph.json", "relationship_graph.json"):
        assert (output / name).read_bytes() == (ROOT / "data" / name).read_bytes()

    manifest = json.loads((output / "compilation_manifest.json").read_text(encoding="utf-8"))
    assert manifest["candidate_only"] is True
    assert manifest["published_overwrite_performed"] is False
    assert manifest["automatic_promotion_allowed"] is False
    assert all(
        comparison["byte_equivalent"] is True
        for comparison in manifest["published_comparison"].values()
    )
    assert set(manifest["coverage_state_definitions"]) == {
        "complete",
        "completed_zero",
        "partial",
        "failed",
        "missing",
    }
    assert set(manifest["coverage"].values()) == {"complete"}
    assert manifest["embedding_staleness"] == {
        "status": "current",
        "coverage_state": "complete",
        "path": "data/embeddings.db",
        "expected_record_count": 867,
        "observed_record_count": 867,
        "current_record_count": 867,
        "missing_record_count": 0,
        "extra_record_count": 0,
        "stale_record_count": 0,
        "missing_identities": [],
        "extra_identities": [],
        "stale_identities": [],
        "provider_calls": 0,
        "automatic_rebuild_attempted": False,
    }


def test_embedding_staleness_preserves_missing_stale_and_failed_states(
    tmp_path: Path,
) -> None:
    graph = [
        {
            "source_model_id": "source",
            "target_model_id": "target",
            "edge_type": "ally",
            "activation_condition": "Use when the evidence converges.",
        }
    ]

    missing = _embedding_staleness_report(
        ROOT,
        graph,
        database_path=tmp_path / "missing.db",
    )
    assert missing["status"] == "missing"
    assert missing["coverage_state"] == "missing"
    assert missing["provider_calls"] == 0

    stale_path = tmp_path / "stale.db"
    connection = sqlite3.connect(stale_path)
    try:
        connection.execute(
            "CREATE TABLE edge_activation_conditions ("
            "source_model_id TEXT, target_model_id TEXT, edge_type TEXT, "
            "activation_condition_text TEXT, content_hash TEXT)"
        )
        connection.execute(
            "INSERT INTO edge_activation_conditions VALUES (?, ?, ?, ?, ?)",
            ("source", "target", "ally", "Old activation text.", "old-hash"),
        )
        connection.commit()
    finally:
        connection.close()

    stale = _embedding_staleness_report(ROOT, graph, database_path=stale_path)
    assert stale["status"] == "stale"
    assert stale["coverage_state"] == "partial"
    assert stale["expected_record_count"] == 1
    assert stale["observed_record_count"] == 1
    assert stale["current_record_count"] == 0
    assert stale["stale_record_count"] == 1
    assert stale["provider_calls"] == 0
    assert stale["automatic_rebuild_attempted"] is False

    unreadable_database = tmp_path / "unreadable.db"
    unreadable_database.write_bytes(b"not-a-sqlite-database")
    failed = _embedding_staleness_report(
        ROOT,
        graph,
        database_path=unreadable_database,
    )
    assert failed["status"] == "failed"
    assert failed["coverage_state"] == "failed"
    assert failed["reason"] == "DatabaseError"
    assert failed["provider_calls"] == 0


def test_two_candidate_builds_are_byte_identical(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    compiler = KnowledgeCompiler.load(ROOT)
    assert compiler.compile(output_dir=first).is_valid
    assert compiler.compile(output_dir=second).is_valid

    names = (
        "knowledge_graph.json",
        "relationship_graph.json",
        "compilation_report.md",
        "compilation_manifest.json",
    )
    assert {name: _sha256(first / name) for name in names} == {
        name: _sha256(second / name) for name in names
    }


def test_compiler_requires_explicit_nonpublished_output() -> None:
    compiler = KnowledgeCompiler.load(ROOT)
    with pytest.raises(GraphCompilationError, match="explicit candidate output"):
        compiler.compile()
    with pytest.raises(GraphCompilationError, match="may not overwrite published"):
        compiler.compile(output_dir=ROOT / "data")


def test_compiler_never_falls_back_to_published_outputs(tmp_path: Path) -> None:
    (tmp_path / "data" / "curation").mkdir(parents=True)
    shutil.copyfile(
        ROOT / "data" / "curation" / "graph_compiler_contract.json",
        tmp_path / "data" / "curation" / "graph_compiler_contract.json",
    )
    shutil.copyfile(
        ROOT / "data" / "knowledge_graph.json",
        tmp_path / "data" / "knowledge_graph.json",
    )
    shutil.copyfile(
        ROOT / "data" / "relationship_graph.json",
        tmp_path / "data" / "relationship_graph.json",
    )

    with pytest.raises(GraphCompilationError, match="compile-from-published-output is forbidden"):
        KnowledgeCompiler.load(tmp_path).compile(output_dir=tmp_path / "candidate")


def test_compiler_input_manifest_revalidates_without_recovery_source() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/product/adopt_graph_compiler_inputs.py",
            "--validate-only",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    summary = json.loads(result.stdout)
    assert summary == {
        "input_set_count": 5,
        "other_repository_required": False,
        "provider_calls": 0,
        "status": "valid",
    }


def test_candidate_cli_builds_and_validates_without_promotion(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    for extra in ([], ["--validate-only"]):
        result = subprocess.run(
            [
                sys.executable,
                "scripts/product/build_graph_substrate_candidate.py",
                "--output-dir",
                str(output),
                *extra,
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        summary = json.loads(result.stdout)
        assert summary["published_byte_equivalent"] is True
        assert summary["published_overwrite_performed"] is False
        assert summary["provider_calls"] == 0
