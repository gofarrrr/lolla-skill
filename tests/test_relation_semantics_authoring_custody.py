from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data" / "curation" / "relation_semantics_manifest.json"
SOURCE_ANCHOR_PATH = ROOT / "data" / "curation" / "relation_source_anchor_register.json"


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_relation_authoring_manifest_is_complete_and_repository_local() -> None:
    manifest = _json(MANIFEST_PATH)

    assert manifest["status"] == "complete"
    assert manifest["authority"] == {
        "authoring_directory": "data/curation/relation_semantics",
        "machine_specific_path_recorded": False,
        "other_repository_required": False,
        "repository_role": "sole_active_project_authority",
    }
    assert manifest["coverage"]["canonical_model_count"] == 222
    assert manifest["coverage"]["active_record_count"] == 222
    assert manifest["coverage"]["relation_count"] == 1_358
    assert manifest["coverage"]["relation_counts_by_family"] == {
        "ally": 523,
        "antagonist": 344,
        "tension": 491,
    }
    assert (
        manifest["coverage"]["active_record_set_sha256"]
        == "a779626577a3f373a6882b68f5c0621e3cc2fb62935c13b3421ca2b2ca2ca3cd"
    )
    raw = MANIFEST_PATH.read_text(encoding="utf-8")
    assert "/Users/" not in raw
    assert "other_repository_required\": true" not in raw


def test_every_active_record_is_hash_locked_and_enriched() -> None:
    manifest = _json(MANIFEST_PATH)
    active = manifest["active_records"]
    model_ids = set(_json(ROOT / "data" / "knowledge_graph.json")["models"])

    assert {entry["model_id"] for entry in active} == model_ids
    relation_count = 0
    enriched_count = 0
    for entry in active:
        path = ROOT / entry["path"]
        assert path.is_file()
        assert path.stat().st_size == entry["bytes"]
        assert _sha256(path) == entry["sha256"]
        record = _json(path)
        assert record["model_id"] == entry["model_id"]
        for family in ("allies", "antagonists"):
            for relation in record[family]:
                assert set(
                    ("affinity_strength", "affinity_rationale", "activation_condition")
                ).issubset(relation)
                enriched_count += 1
        relation_count += sum(
            len(record[family])
            for family in ("allies", "antagonists", "structured_tensions")
        )

    assert relation_count == 1_358
    assert enriched_count == 867


def test_every_relation_has_truthful_source_anchor_and_compiled_pointers() -> None:
    register = _json(SOURCE_ANCHOR_PATH)

    assert register["status"] == "complete"
    assert register["classification_authority"] == "mechanical_only_no_semantic_repair"
    assert set(register["state_definitions"]) == {
        "exact_span",
        "normalized_excerpt",
        "synthesized_or_multi_span",
        "unresolved",
        "missing",
    }
    assert register["coverage"] == {
        "relation_count": 1_358,
        "state_counts": {
            "exact_span": 605,
            "normalized_excerpt": 14,
            "synthesized_or_multi_span": 0,
            "unresolved": 739,
            "missing": 0,
        },
        "all_relations_classified": True,
        "provider_calls": 0,
        "semantic_repair_performed": False,
    }

    relation_ids = set()
    for relation in register["relations"]:
        assert relation["relation_id"] not in relation_ids
        relation_ids.add(relation["relation_id"])
        assert (ROOT / relation["authoring_pointer"]["path"]).is_file()
        assert relation["published_pointer"]["path"] == "data/relationship_graph.json"
        assert (ROOT / relation["source"]["path"]).is_file()
        if relation["source_anchor_state"] == "exact_span":
            assert relation["exact_span"] is not None
        else:
            assert relation["exact_span"] is None
    assert len(relation_ids) == 1_358

    manifest = _json(MANIFEST_PATH)
    identity = manifest["source_anchor_register"]
    assert identity["path"] == "data/curation/relation_source_anchor_register.json"
    assert identity["sha256"] == _sha256(SOURCE_ANCHOR_PATH)
    assert identity["bytes"] == SOURCE_ANCHOR_PATH.stat().st_size


def test_historical_identity_records_are_explicitly_excluded() -> None:
    manifest = _json(MANIFEST_PATH)
    inactive = {entry["model_id"]: entry for entry in manifest["inactive_records"]}

    assert set(inactive) == {
        "commitment-and-consistency-bias",
        "representativeness-bias",
    }
    assert inactive["commitment-and-consistency-bias"]["canonical_model_id"] == "commitment-bias"
    assert (
        inactive["representativeness-bias"]["canonical_model_id"]
        == "representativeness-heuristic"
    )
    assert all(entry["lifecycle"] == "historical_superseded_identity" for entry in inactive.values())
    assert all(entry["compiler_included"] is False for entry in inactive.values())
    assert all(entry["runtime_aliasing_authorized"] is False for entry in inactive.values())

    migrations = _json(ROOT / "data" / "curated" / "canonical_id_migrations.json")
    migration_pairs = {
        (entry["from_model_id"], entry["to_model_id"])
        for entry in migrations["migrations"]
    }
    assert migration_pairs == {
        ("commitment-and-consistency-bias", "commitment-bias"),
        ("representativeness-bias", "representativeness-heuristic"),
    }


def test_repository_local_authoring_revalidates_without_recovery_input() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/product/adopt_relation_semantics_authoring.py",
            "--validate-only",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    summary = json.loads(result.stdout)
    assert summary["active_record_count"] == 222
    assert summary["relation_count"] == 1_358
    assert summary["other_repository_required"] is False


def test_relation_admission_did_not_change_published_graph_bytes() -> None:
    baseline = _json(ROOT / "docs" / "evals" / "lolla-graph-substrate-baseline-v1.json")
    artifacts = {entry["path"]: entry for entry in baseline["artifacts"].values()}

    for relative_path in ("data/knowledge_graph.json", "data/relationship_graph.json"):
        assert _sha256(ROOT / relative_path) == artifacts[relative_path]["sha256"]
