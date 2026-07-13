from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/evals/lolla-product-measurement-map-v0.md"
CONTRACT = REPO_ROOT / "docs/evals/lolla-downstream-utility-experiment-v0.json"


def test_downstream_experiment_uses_a_strong_control_and_no_single_score() -> None:
    payload = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "lolla.downstream_utility_experiment.v0"
    assert payload["status"] == "frozen_protocol_no_calls_run"
    assert [arm["arm_id"] for arm in payload["arms"]] == [
        "strong_reconsideration_control",
        "lolla_pressure_treatment",
    ]
    assert payload["unit"]["generation_context"] == "fresh_session"
    assert payload["unit"]["review_separate_from_generation"] is True
    assert "unique_delta_beyond_control" in payload["scorecard"]
    assert "lost_value" in payload["scorecard"]
    assert "correct_standdown" in payload["scorecard"]
    assert "single_quality_score" not in payload["scorecard"]


def test_pilot_is_call_bounded_and_cannot_promote_runtime() -> None:
    payload = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert payload["pilot"]["initial_generation_calls"] == 2
    assert payload["pilot"]["evaluator_calls"] == 0
    assert payload["pilot"]["maximum_generation_calls_before_new_decision"] == 6
    boundary = payload["promotion_boundary"]
    assert boundary["two_call_pilot_can_authorize_runtime_change"] is False
    assert boundary["two_call_pilot_can_authorize_semantic_kernel_integration"] is False
    assert boundary["requires_positive_and_quiet_cases_before_product_claim"] is True
    assert boundary["requires_exact_run_human_review_before_product_claim"] is True


def test_measurement_map_preserves_hybrid_boundary_and_anti_goodhart_rules() -> None:
    text = DOC.read_text(encoding="utf-8")
    assert "Scorecard, never a badge" in text
    assert "Actionability theater" in text
    assert "Mandatory-consideration absorption" in text
    assert "Trust inflation" in text
    assert "The response to unknown unknowns is not another deterministic gate" in text
    assert "Extraction metrics alone" in text
    assert "cannot authorize it." in text
    assert "two generation calls and zero evaluator calls" in text
