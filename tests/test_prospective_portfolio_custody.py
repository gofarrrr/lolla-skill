from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.prospective_portfolio_custody import (
    ProspectivePortfolioCustodyError,
    build_prospective_portfolio_custody,
    validate_prospective_portfolio_custody,
)
from engine.system_b.published_knowledge_substrate import PublishedKnowledgeSubstrate


def _snapshot():
    return PublishedKnowledgeSubstrate.open(ROOT).require_snapshot()


def _candidates() -> list[dict[str, str]]:
    return [{"model_id": model_id} for model_id in sorted(_snapshot().models)[:60]]


def test_complete_candidate_preserves_scope_disposition_and_every_exact_path() -> None:
    custody = build_prospective_portfolio_custody(
        candidates=_candidates(),
        substrate=_snapshot(),
    )

    assert custody["status"] == "complete"
    assert custody["candidate_only"] is True
    assert custody["live_reasoner_connected"] is False
    assert custody["live_receipt_connected"] is False
    assert custody["decision_trail_connected"] is False
    assert custody["provider_calls"] == 0
    assert custody["scope"]["expansion_seed_rule"] == "direct_active_only"
    assert custody["scope"]["direction"] == "outgoing_authored_relations"
    assert custody["scope"]["hop_depth"] == 1
    assert len(custody["scope"]["expanded_direct_active_seed_ids"]) == 6
    assert custody["scope"]["unexpanded_direct_reserve_count"] == 54

    assert len(custody["unexpanded_direct_reserve"]) == 54
    assert all(
        row["neighborhood_status"] == "not_enumerated_by_current_policy"
        and row["neighborhood"] is None
        and row["semantic_rejection_performed"] is False
        for row in custody["unexpanded_direct_reserve"]
    )

    targets = custody["enumerated_graph_targets"]
    all_relation_ids: list[str] = []
    for target in targets:
        coverage = target["path_coverage"]
        assert coverage["status"] == "complete"
        assert coverage["omitted_path_count"] == 0
        assert coverage["serialized_path_count"] == coverage["exact_path_count"]
        paths = target["provenance_paths"]
        assert len(paths) == coverage["exact_path_count"]
        assert all(path["target_model_id"] == target["target_model_id"] for path in paths)
        assert all(path["direction"] == "outgoing_authored_relation" for path in paths)
        assert all(path["hop_count"] == 1 for path in paths)
        assert all(path["compiled_pointer"].startswith("data/relationship_graph.json#/") for path in paths)
        assert all(path["authoring_pointer"] is not None for path in paths)
        assert all(path["source_custody"] is not None for path in paths)
        all_relation_ids.extend(path["relation_id"] for path in paths)
        if target["disposition"] == "active_graph_slot":
            assert target["admission_path"] is not None
            assert target["admission_path"]["relation_id"] in {
                path["relation_id"] for path in paths
            }
        else:
            assert target["admission_path"] is None

    accounting = custody["path_accounting"]
    assert len(all_relation_ids) == accounting["exact_path_count"]
    assert len(set(all_relation_ids)) == len(all_relation_ids)
    assert accounting["exact_path_count"] == accounting["serialized_path_count"]
    assert accounting["omitted_path_count"] == 0
    assert custody["coverage"]["exact_path_serialization"] == "complete"
    assert custody["live_equivalence"]["active_identities_and_order_equal"] is True


def test_safety_bound_reports_partial_with_exact_omission_counts() -> None:
    custody = build_prospective_portfolio_custody(
        candidates=_candidates(),
        substrate=_snapshot(),
        max_serialized_paths=1,
    )

    accounting = custody["path_accounting"]
    assert custody["status"] == "partial"
    assert custody["coverage"]["exact_path_serialization"] == "partial"
    assert accounting["serialized_path_count"] == 1
    assert accounting["omitted_path_count"] == accounting["exact_path_count"] - 1
    assert accounting["partial_reason"] == "max_serialized_paths_safety_bound"
    assert any(
        target["path_coverage"]["status"] == "partial"
        and target["path_coverage"]["omitted_path_count"] > 0
        for target in custody["enumerated_graph_targets"]
    )
    assert custody["live_equivalence"]["active_identities_and_order_equal"] is True


def test_candidate_hash_and_live_equivalence_are_tamper_evident() -> None:
    custody = build_prospective_portfolio_custody(
        candidates=_candidates(),
        substrate=_snapshot(),
    )
    tampered = copy.deepcopy(custody)
    tampered["enumerated_graph_targets"][0]["disposition"] = "active_graph_slot"

    with pytest.raises(ProspectivePortfolioCustodyError, match="hash"):
        validate_prospective_portfolio_custody(tampered)


def test_corpus_baseline_accounts_for_all_previously_unserialized_paths() -> None:
    baseline = json.loads(
        (
            ROOT
            / "docs/evals/lolla-prospective-portfolio-custody-baseline-v1.json"
        ).read_text(encoding="utf-8")
    )
    aggregate = baseline["aggregate"]

    assert baseline["status"] == "complete"
    assert baseline["candidate_only"] is True
    assert baseline["live_connection_performed"] is False
    assert baseline["provider_calls"] == 0
    assert baseline["scope"]["window_count"] == 163
    assert aggregate["exact_path_count"] == 6_025
    assert aggregate["serialized_path_count"] == 6_025
    assert aggregate["omitted_path_count"] == 0
    assert aggregate["graph_active_additional_nonadmission_path_count"] == 808
    assert aggregate["frozen_previously_unserialized_additional_path_count"] == 808
    assert aggregate["previously_unserialized_paths_accounted_for"] is True
    assert aggregate["all_windows_live_active_equivalent"] is True
    assert aggregate["target_disposition_counts"] == {
        "active_graph_slot": 489,
        "reserve_duplicate_of_direct_active": 90,
        "reserve_graph_capacity": 3_144,
    }

    result = subprocess.run(
        [
            sys.executable,
            "scripts/evals/build_prospective_portfolio_custody_baseline.py",
            "--validate-only",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    summary = json.loads(result.stdout)
    assert summary["previously_unserialized_paths_accounted_for"] is True
    assert summary["provider_calls"] == 0


def test_candidate_custody_is_not_imported_by_the_live_pipeline() -> None:
    live_source = (ROOT / "engine/system_b/pipeline.py").read_text(encoding="utf-8")

    assert "prospective_portfolio_custody" not in live_source
    assert "build_prospective_portfolio_custody" not in live_source


def test_explicit_candidate_cli_writes_and_revalidates_offline(tmp_path: Path) -> None:
    candidate_ids = tmp_path / "candidate_ids.json"
    output = tmp_path / "candidate.json"
    candidate_ids.write_text(
        json.dumps(sorted(_snapshot().models)[:60]),
        encoding="utf-8",
    )

    base = [
        sys.executable,
        "scripts/evals/build_prospective_portfolio_custody_candidate.py",
        "--candidate-ids-json",
        str(candidate_ids),
        "--output",
        str(output),
    ]
    for extra in ([], ["--validate-only"]):
        result = subprocess.run(
            [*base, *extra],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        summary = json.loads(result.stdout)
        assert summary["candidate_only"] is True
        assert summary["live_active_equivalent"] is True
        assert summary["omitted_path_count"] == 0
        assert summary["provider_calls"] == 0
