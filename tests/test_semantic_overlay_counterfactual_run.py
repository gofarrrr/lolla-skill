from __future__ import annotations

import json
from pathlib import Path

from scripts.evals.run_semantic_overlay_counterfactual import (
    build_call_specs,
    validate_run_contract,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
RUN_CONTRACT = (
    REPO_ROOT
    / "research/semantic-overlay-counterfactual-case07-2026-07-10/run-contract.json"
)


def _contract() -> dict:
    return json.loads(RUN_CONTRACT.read_text(encoding="utf-8"))


def test_run_contract_is_hash_locked_and_three_call_bounded() -> None:
    design, packets = validate_run_contract(_contract())
    assert len(design["arms"]) == 3
    assert packets["actual_overlay"]["event_count"] == 27
    config = _contract()["call_configuration"]
    assert config["total_generation_calls"] == 3
    assert config["evaluator_calls"] == 0
    assert config["automatic_retries"] == 0


def test_specs_compare_control_actual_and_one_observation_oracle() -> None:
    specs = build_call_specs(_contract())
    assert len(specs) == 3
    by_arm = {spec["arm_id"]: spec for spec in specs}
    assert by_arm["strong_fresh_reconsideration_control"]["overlay_event_count"] == 0
    assert by_arm["actual_sk3_overlay"]["overlay_event_count"] == 27
    assert by_arm["actual_sk3_plus_reviewed_omission_oracle"]["overlay_event_count"] == 28
    assert "PROVISIONAL SEMANTIC NAVIGATION" not in by_arm[
        "strong_fresh_reconsideration_control"
    ]["user_prompt"]
    assert "PROVISIONAL SEMANTIC NAVIGATION" in by_arm["actual_sk3_overlay"][
        "user_prompt"
    ]


def test_generator_is_told_full_conversation_is_authoritative() -> None:
    for spec in build_call_specs(_contract()):
        combined = spec["system_prompt"] + spec["user_prompt"]
        assert "complete conversation as the authority" in combined
        assert "do not decide personal values for the user" in combined
