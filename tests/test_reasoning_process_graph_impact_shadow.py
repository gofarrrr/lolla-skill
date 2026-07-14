from __future__ import annotations

import json
from pathlib import Path

from scripts.evals.run_reasoning_pattern_embedding_impact_shadow import validate_contract
from scripts.evals.run_reasoning_process_graph_impact_shadow import run

ROOT = Path(__file__).resolve().parents[1]
GRAPH_CONTRACT = ROOT / "docs/evals/reasoning-process-graph-impact-shadow-v1.json"
GRAPH_RESULT = ROOT / "research/reasoning-process-graph-impact-shadow-2026-07-12/result.json"
EMBED_CONTRACT = ROOT / "research/reasoning-pattern-embedding-impact-shadow-2026-07-12/contract.json"
EMBED_RESULT = ROOT / "research/reasoning-pattern-embedding-impact-shadow-2026-07-12/embedding-result.json"
REVIEW = ROOT / "research/reasoning-process-graph-impact-shadow-2026-07-12/impact-review.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_deterministic_shadow_replays_and_preserves_source_provider_invariance() -> None:
    replay = run(GRAPH_CONTRACT)
    checked = _load(GRAPH_RESULT)
    assert replay["status"] == "provider_free_deterministic_graph_impact_shadow_pass"
    assert replay["comparisons"] == checked["comparisons"]
    for comparison in replay["comparisons"]:
        assert all(comparison["source_provider"].values())
        assert comparison["sensitivity_control"]["projection_differs_after_missing_reversal_ablation"] is True
        assert comparison["sensitivity_control"]["removed_seed_candidates"] == ["commitment-bias", "premortem", "sunk-cost-fallacy"]
    assert replay["boundary"]["provider_calls"] == 0
    assert replay["boundary"]["embedding_calls"] == 0
    assert replay["boundary"]["runtime_mutations"] == 0


def test_graph_shadow_uses_real_nonempty_declared_graph() -> None:
    result = _load(GRAPH_RESULT)
    full = result["arms"]["housing_source_first"]
    assert result["relationship_graph_path"] == "data/relationship_graph.json"
    assert full["deterministic_neighborhood"]["selected_supporting_model_ids"]
    assert full["deterministic_neighborhood"]["selected_risk_model_ids"]
    assert "second-order-thinking" in full["deterministic_neighborhood"]["selected_supporting_model_ids"]


def test_embedding_contract_remains_valid_after_one_completed_request() -> None:
    validation = validate_contract(_load(EMBED_CONTRACT), EMBED_CONTRACT)
    assert validation["status"] == "reasoning_pattern_embedding_shadow_contract_valid"
    assert validation["embedding_requests_made"] == 0


def test_embedding_result_is_fact_free_and_did_not_override_selection() -> None:
    result = _load(EMBED_RESULT)
    assert result["status"] == "fact_free_embedding_impact_shadow_complete"
    assert result["embedding_http_requests"] == 1
    assert result["embedding_input_count"] == 2
    assert result["vector_dimensions"] == [3072, 3072]
    assert result["usage"]["prompt_tokens"] == 65
    assert result["source_provider_full_projection_embedding_reused"] is True
    assert result["sensitivity"]["full_tiebreaker_fired_count"] == 0
    assert result["sensitivity"]["ablation_tiebreaker_fired_count"] == 0
    assert result["boundary"]["raw_role_prose_embedded"] is False
    assert result["boundary"]["facts_embedded"] is False
    assert result["boundary"]["production_integration_authorized"] is False


def test_impact_review_keeps_conditional_result_and_names_unproven_bridge() -> None:
    review = _load(REVIEW)
    assert review["status"] == "read_only_shadow_complete_abstraction_bridge_unproven"
    assert review["deterministic_findings"]["source_provider_fact_free_projection_equal_in_both_cases"] is True
    assert review["graph_pressure_preservation"]["protected_reversal_changes_selected_neighborhood"] is True
    assert review["graph_pressure_preservation"]["provider_extraction_noise_changes_selected_neighborhood_after_reviewed_abstraction"] is False
    assert review["critical_limit"]["automatic_role_record_to_pattern_abstraction_proven"] is False
    assert review["decision"]["production_graph_integration_authorized"] is False
    assert review["decision"]["selected_next_experiment"] == "provider_free_role_record_to_pattern_abstraction_contract_then_bounded_source_provider_invariance_probe"
