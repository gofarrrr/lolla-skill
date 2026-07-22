from __future__ import annotations

import json
from pathlib import Path

from scripts.evals.build_graph_substrate_baseline import (
    SCHEMA_VERSION,
    build_graph_substrate_baseline,
    main,
)


ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "docs/evals/lolla-graph-substrate-baseline-v1.json"


def test_graph_substrate_baseline_freezes_current_structural_inventory() -> None:
    baseline = build_graph_substrate_baseline(ROOT)

    assert baseline["schema_version"] == SCHEMA_VERSION
    assert baseline["status"] == "complete"
    assert baseline["repository_authority"] == {
        "status": "sole_active_authority",
        "canonical_source_root": "data/model_sources",
        "canonical_source_authority": "repository_local",
        "external_runtime_dependency": False,
    }
    inventory = baseline["graph_inventory"]
    assert inventory["canonical_model_count"] == 222
    assert inventory["tendency_count"] == 25
    assert inventory["compact_edge_count"] == 1742
    assert inventory["rich_relation_count"] == 1358
    assert inventory["rich_relation_type_counts"] == {
        "ally": 523,
        "antagonist": 344,
        "tension": 491,
    }
    assert inventory["compact_rich_relation_identity_match"] is True
    assert inventory["self_edge_count"] == 0
    assert inventory["noncanonical_endpoint_count"] == 0


def test_graph_substrate_baseline_freezes_current_portfolio_characterization() -> None:
    baseline = build_graph_substrate_baseline(ROOT)
    sweep = baseline["current_portfolio_characterization"]

    assert sweep["window_size"] == 60
    assert sweep["window_count"] == 163
    assert sweep["graph_active_count"] == 489
    assert sweep["graph_active_with_multiple_exact_paths_count"] == 265
    assert sweep["additional_exact_paths_not_on_outer_active_item_count"] == 808
    assert len(sweep["windows"]) == 163
    assert all(len(window["direct_active_model_ids"]) == 6 for window in sweep["windows"])
    assert all(len(window["graph_active"]) == 3 for window in sweep["windows"])


def test_checked_baseline_register_matches_provider_free_rebuild() -> None:
    assert main(["--root", str(ROOT), "--register", str(REGISTER), "--validate-only"]) == 0


def test_baseline_register_contains_no_machine_specific_project_path() -> None:
    payload = json.loads(REGISTER.read_text(encoding="utf-8"))
    serialized = json.dumps(payload, ensure_ascii=False)

    assert "/Users/" not in serialized
