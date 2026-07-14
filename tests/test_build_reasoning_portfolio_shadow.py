from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts/evals/build_reasoning_portfolio_shadow.py"
SPEC = REPO_ROOT / "research/reasoning-portfolio-case01-2026-07-10/portfolio-spec.json"
HANDOFF = (
    REPO_ROOT
    / "research/reasoning-pressure-handoff-v0-2026-07-10/lineage-backed-handoff.json"
)


def _module():
    spec = importlib.util.spec_from_file_location("portfolio_builder", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _graph_report(path: Path) -> None:
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    refs = {
        item["graph_trace_ref"]
        for group in ("edge_items", "parked_items")
        for item in spec[group]
    }
    refs.update(
        ref
        for item in spec["weak_items"]
        for ref in item["evidence_refs"]
        if ref.startswith("graph_survival.model.")
    )
    rows = [
        {
            "model_id": ref.removeprefix("graph_survival.model."),
            "survival_state": "synthetic_test_candidate",
            "selected_for_v60": False,
            "sources": ["test"],
        }
        for ref in sorted(refs)
    ]
    path.write_text(
        json.dumps(
            {
                "schema_version": "lolla.graph_survival_report.test.v0",
                "candidate_survival": rows,
            }
        ),
        encoding="utf-8",
    )


def test_builder_preserves_complete_active_slice_and_edge_reserve(
    tmp_path: Path,
) -> None:
    graph_path = tmp_path / "graph.json"
    _graph_report(graph_path)
    portfolio, graph_index, validation = _module().build_reasoning_portfolio_shadow(
        spec_path=SPEC,
        active_handoff_path=HANDOFF,
        graph_report_path=graph_path,
    )
    assert validation["active_handoff_coverage_complete"] is True
    assert validation["active_item_count"] == 5
    assert validation["edge_item_count"] == 7
    assert validation["weak_item_count"] == 3
    assert validation["parked_item_count"] == 4
    assert validation["additional_preserved_graph_ref_count"] == 11
    assert validation["rendered_character_limit"] == 4200
    assert validation["rendered_character_headroom"] > 0
    assert validation["rendered_budget_utilization"] < 1
    assert validation["rendered_budget_warning"] == "near_limit"
    assert validation["builder_model_calls"] == 0
    assert validation["semantic_relevance_validated"] is False
    assert validation["runtime_integration_authorized"] is False
    assert portfolio["runtime_policy"] == "runtime_dormant"
    assert graph_index["raw_graph_text_included"] is False


def test_builder_rejects_silent_active_item_loss(tmp_path: Path) -> None:
    graph_path = tmp_path / "graph.json"
    _graph_report(graph_path)
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    spec["active_items"] = spec["active_items"][:-1]
    spec_path = tmp_path / "spec.json"
    spec_path.write_text(json.dumps(spec), encoding="utf-8")
    with pytest.raises(Exception, match="active handoff coverage mismatch"):
        _module().build_reasoning_portfolio_shadow(
            spec_path=spec_path,
            active_handoff_path=HANDOFF,
            graph_report_path=graph_path,
        )


def test_builder_rejects_unknown_graph_candidate(tmp_path: Path) -> None:
    graph_path = tmp_path / "graph.json"
    _graph_report(graph_path)
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    spec["edge_items"][0]["graph_trace_ref"] = "graph_survival.model.missing"
    spec_path = tmp_path / "spec.json"
    spec_path.write_text(json.dumps(spec), encoding="utf-8")
    with pytest.raises(Exception, match="unknown graph candidate"):
        _module().build_reasoning_portfolio_shadow(
            spec_path=spec_path,
            active_handoff_path=HANDOFF,
            graph_report_path=graph_path,
        )
