from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts/evals/validate_consumer_context_pressure_ablation.py"
CONTRACT_PATH = ROOT / "docs/evals/lolla-consumer-context-pressure-ablation-contract-v1.json"


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
        "design_shape_valid": True,
        "execution_ready": False,
        "fresh_graph_supply_arm_count": 4,
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
        "schema_version": "lolla.consumer_context_pressure_ablation_contract.v1",
        "single_draw_evidence_class": "single_draw_case_diagnostic",
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
    assert "consumer-context contract must preserve eight competing falsifiable hypotheses" in errors


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


def test_contract_rejects_direct_component_or_active_payload_custody_drift() -> None:
    validator = _load_validator()
    candidate = copy.deepcopy(_contract())
    candidate["experiment_design"]["execution_isolation"].remove(
        "hold_f2_direct_candidate_ids_content_order_format_and_source_label_visibility_"
        "byte_identical_to_the_direct_component_of_f3"
    )
    candidate["required_custody_before_execution"].remove(
        "active_planner_candidate_to_presented_payload_bijection_receipt"
    )

    errors, receipt = validator.validate(ROOT, contract_override=candidate)

    assert receipt["status"] == "invalid"
    assert "consumer-context contract is missing required isolation rules" in errors
    assert "consumer-context contract is missing required context or pressure custody" in errors


def test_contract_rejects_causal_readiness_or_self_justification_overclaim() -> None:
    validator = _load_validator()
    candidate = copy.deepcopy(_contract())
    candidate["readiness"]["execution_ready"] = True
    candidate["readiness"]["causal_interaction_identified"] = True
    candidate["claim_ledger"][4]["status"] = "verified"
    candidate["predecessor"] = "missing.json"

    errors, receipt = validator.validate(ROOT, contract_override=candidate)

    assert receipt["status"] == "invalid"
    assert "consumer-context readiness.execution_ready must be False" in errors
    assert "consumer-context readiness.causal_interaction_identified must be False" in errors
    assert "consumer-context contract must preserve the v0 predecessor boundary" in errors
    assert (
        "consumer-context claim context_interaction_establishes_self_justification "
        "must remain not_assumed"
    ) in errors


def test_contract_rejects_missing_human_rubric_or_quiet_case_overclaim() -> None:
    validator = _load_validator()
    candidate = copy.deepcopy(_contract())
    candidate["grounded_rejection_vs_coherence_defense_human_rubric"][
        "required_judgments"
    ] = []
    candidate["quiet_case_boundary"]["cannot_test"] = "nothing"
    candidate["reference_condition_boundary"]["not_an_oracle"] = False

    errors, receipt = validator.validate(ROOT, contract_override=candidate)

    assert receipt["status"] == "invalid"
    assert "consumer-context rejection rubric judgments drifted" in errors
    assert "consumer-context quiet case must not claim to test absent-payload absorption" in errors
    assert "consumer-context human reference condition must not be called an oracle" in errors


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
