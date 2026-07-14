from __future__ import annotations

import json
from pathlib import Path

from scripts.evals.run_strong_reconsideration_control import (
    build_prompt,
    validate_contract,
    validate_response,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    REPO_ROOT
    / "research/reasoning-portfolio-holdout-2026-07-10/case09-contract.json"
)


def _contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def test_control_is_one_call_no_retry_and_hash_locked() -> None:
    contract = _contract()
    validate_contract(contract, repo_root=REPO_ROOT)
    config = contract["strong_control"]["call_configuration"]
    assert config["generation_calls"] == 1
    assert config["evaluator_calls"] == 0
    assert config["automatic_retries"] == 0
    assert config["reasoning_effort"] == "none"


def test_prompt_contains_complete_conversation_but_no_portfolio_context() -> None:
    prompt = build_prompt(_contract(), repo_root=REPO_ROOT)
    assert "COMPLETE CONVERSATION" in prompt
    assert "Third-year PhD student in computational biology" in prompt
    assert "Reassess the prior reasoning from scratch" in prompt
    assert "SOURCE-GROUNDED CHALLENGE PRESSURE" not in prompt
    assert "V60" not in prompt
    assert "mental-model machinery" not in prompt


def test_response_validator_enforces_exact_shape() -> None:
    contract = _contract()
    valid = {
        "decision_state_read": "not decided",
        "updated_position": "conditional",
        "what_survived": [],
        "take_backs_or_set_aside": [],
        "material_shifts": [
            {
                "shift": "one",
                "source_basis": "turn",
                "action_consequence": "test",
            }
        ],
        "next_actions": [],
        "uncertainties": [],
    }
    assert validate_response(valid, contract) == []
    invalid = dict(valid, extra="not allowed")
    assert "unknown top-level keys: ['extra']" in validate_response(invalid, contract)
