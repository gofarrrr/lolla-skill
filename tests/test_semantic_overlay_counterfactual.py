from __future__ import annotations

from pathlib import Path

from scripts.evals.build_semantic_overlay_counterfactual import build_packets


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT = (
    REPO_ROOT
    / "research/semantic-overlay-counterfactual-case07-2026-07-10/contract.json"
)


def test_counterfactual_preserves_actual_overlay_and_keeps_oracle_separate() -> None:
    payload = build_packets(CONTRACT)
    assert payload["schema_version"] == "lolla.semantic_overlay_counterfactual_packets.v0"
    assert payload["status"] == "packets_built_no_model_calls"
    assert payload["actual_overlay"]["event_count"] == 27
    assert payload["reviewed_oracle_addition"]["event_count"] == 1
    oracle = payload["reviewed_oracle_addition"]["events"][0]
    assert oracle["missing_from_actual_overlay"] is True
    assert oracle["quote"] == (
        "I keep telling myself I've decided on Seattle but I haven't actually decided."
    )


def test_counterfactual_has_three_non_promoting_arms_and_bounded_future_calls() -> None:
    payload = build_packets(CONTRACT)
    assert [arm["arm_id"] for arm in payload["arms"]] == [
        "strong_fresh_reconsideration_control",
        "actual_sk3_overlay",
        "actual_sk3_plus_reviewed_omission_oracle",
    ]
    assert payload["future_call_budget_if_separately_authorized"] == {
        "generation_calls": 3,
        "evaluator_calls": 0,
        "samples_per_arm": 1,
        "automatic_retries": 0,
    }
    assert "oracle_is_not_current_system_output" in payload["non_claims"]
