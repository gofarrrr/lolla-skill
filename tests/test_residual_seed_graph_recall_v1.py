import json
from pathlib import Path

import pytest

from engine.system_b.residual_seed_graph_recall_v1 import (
    build_residual_seed_graph_recall_v1,
)
from engine.system_b.simulated_reliability_v1 import SimulatedReliabilityError


ROOT = Path(__file__).resolve().parents[1]


def _load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _inputs():
    result = _load("research/residual-challenge-seed-case01-probe-2026-07-13/t1/result.json")
    return {
        "seed_portfolio": result["joined_seed_portfolio"],
        "routing_contract": _load("docs/conversation-understanding/residual-challenge-seed-graph-routing-v1.json"),
        "knowledge_graph": _load("data/knowledge_graph.json"),
        "relationship_graph": _load("data/relationship_graph.json"),
    }


def test_every_actual_covered_seed_receives_deterministic_recall():
    recall = build_residual_seed_graph_recall_v1(**_inputs())
    assert recall["counts"]["seed_routes"] == 3
    assert recall["counts"]["covered_seed_routes"] == 3
    assert recall["counts"]["direct_active_candidates"] == 6
    assert recall["counts"]["direct_reserve_candidates"] == 3
    assert recall["boundary"]["joint_coverage_used_for_admission"] is False
    assert recall["boundary"]["probabilistic_applicability_filter"] is False
    for seed in recall["seed_custody"]:
        assert seed["joint_coverage"] == "operationalized"
        assert seed["coverage_used_for_graph_admission"] is False
        assert seed["direct_active_model_ids"]
        assert seed["direct_reserve_model_ids"]


def test_recall_is_deterministic_and_preserves_graph_provenance():
    inputs = _inputs()
    first = build_residual_seed_graph_recall_v1(**inputs)
    second = build_residual_seed_graph_recall_v1(**inputs)
    assert first == second
    assert first["result_sha256"] == second["result_sha256"]
    assert first["graph_ledger"]["selection_policy"]["probabilistic_prefilter_used"] is False
    assert first["graph_ledger"]["selection_policy"]["conversation_text_used_for_admission"] is False


def test_routing_rejects_missing_kind_or_noncanonical_model():
    inputs = _inputs()
    routing = json.loads(json.dumps(inputs["routing_contract"]))
    del routing["seed_kind_models"]["time_horizon"]
    with pytest.raises(SimulatedReliabilityError):
        build_residual_seed_graph_recall_v1(**{**inputs, "routing_contract": routing})
    routing = json.loads(json.dumps(inputs["routing_contract"]))
    routing["seed_kind_models"]["time_horizon"] = ["invented-model"]
    with pytest.raises(SimulatedReliabilityError):
        build_residual_seed_graph_recall_v1(**{**inputs, "routing_contract": routing})


def test_routing_rejects_coverage_or_semantic_admission_policy():
    inputs = _inputs()
    routing = json.loads(json.dumps(inputs["routing_contract"]))
    routing["selection_policy"]["coverage_used_for_admission"] = True
    with pytest.raises(SimulatedReliabilityError):
        build_residual_seed_graph_recall_v1(**{**inputs, "routing_contract": routing})
