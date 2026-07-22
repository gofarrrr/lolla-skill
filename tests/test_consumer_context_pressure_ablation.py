from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts/evals/validate_consumer_context_pressure_ablation.py"
CONTRACT_PATH = ROOT / "docs/evals/lolla-consumer-context-pressure-ablation-contract-v0.json"


def _load_validator():
    spec = importlib.util.spec_from_file_location("consumer_context_validator", VALIDATOR_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def test_consumer_context_contract_validates_from_cli() -> None:
    completed = subprocess.run(
        [sys.executable, str(VALIDATOR_PATH)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    receipt = json.loads(completed.stdout)
    assert receipt == {
        "cell_count": 6,
        "context_ablation_cell_count": 4,
        "fresh_graph_supply_arm_count": 4,
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
        "schema_version": "lolla.consumer_context_pressure_ablation_contract.v0",
        "status": "valid",
    }


def test_contract_rejects_naive_fresh_context_claim_and_lost_counterhypothesis() -> None:
    validator = _load_validator()
    candidate = copy.deepcopy(_contract())
    candidate["claim_ledger"][3]["status"] = "verified"
    candidate["competing_hypotheses"] = candidate["competing_hypotheses"][:1]

    errors, receipt = validator.validate(ROOT, contract_override=candidate)

    assert receipt["status"] == "invalid"
    assert (
        "consumer-context claim fresh_context_eliminates_the_vanilla_frame "
        "must remain not_assumed"
    ) in errors
    assert "consumer-context contract must preserve four competing falsifiable hypotheses" in errors


def test_contract_rejects_sequential_same_session_control_or_cell_drift() -> None:
    validator = _load_validator()
    candidate = copy.deepcopy(_contract())
    candidate["experiment_design"]["execution_isolation"].remove(
        "never_run_control_after_treatment_in_the_same_session"
    )
    candidate["experiment_design"]["cells"][5]["consumer_context_mode"] = "same_session"

    errors, receipt = validator.validate(ROOT, contract_override=candidate)

    assert receipt["status"] == "invalid"
    assert "consumer-context contract is missing required isolation rules" in errors
    assert (
        "consumer-context cell has unknown context mode: "
        "t3_trajectory_continuation_human_controlled_plus_current_graph"
    ) in errors


def test_contract_rejects_pressure_payload_or_comparison_drift() -> None:
    validator = _load_validator()
    candidate = copy.deepcopy(_contract())
    candidate["experiment_design"]["execution_isolation"].remove(
        "hold_f3_and_t3_pressure_content_order_format_and_source_label_visibility_byte_identical"
    )
    candidate["paired_comparisons"][4]["right"] = "f3_fresh_human_controlled_fact_free_plus_current_graph"

    errors, receipt = validator.validate(ROOT, contract_override=candidate)

    assert receipt["status"] == "invalid"
    assert "consumer-context contract is missing required isolation rules" in errors
    assert "consumer-context paired comparisons drifted" in errors


def test_contract_rejects_provider_or_runtime_authorization() -> None:
    validator = _load_validator()
    candidate = copy.deepcopy(_contract())
    candidate["authorization"]["provider_calls"] = 6
    candidate["authorization"]["runtime_change"] = True
    candidate["authorization"]["fresh_context_promotion"] = True

    errors, receipt = validator.validate(ROOT, contract_override=candidate)

    assert receipt["status"] == "invalid"
    assert "consumer-context authorization.provider_calls must be 0" in errors
    assert "consumer-context authorization.runtime_change must be False" in errors
    assert "consumer-context authorization.fresh_context_promotion must be False" in errors
