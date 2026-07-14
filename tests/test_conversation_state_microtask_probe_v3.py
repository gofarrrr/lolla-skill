from __future__ import annotations

import json
from pathlib import Path

from scripts.evals.run_conversation_state_microtask_probe_v3 import (
    KINDS,
    expected_prompt_hashes,
    validate_authorization,
    validate_contract,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research/conversation-state-microtask-probe-v3-2026-07-11"
CONTRACT_PATH = PACKAGE / "contract.json"
AUTHORIZATION_PATH = PACKAGE / "call-authorization.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_json_mode_program_stage_is_frozen_and_authorized() -> None:
    contract = _load(CONTRACT_PATH)
    validate_contract(contract)
    assert contract["microtask_order"] == list(KINDS)
    assert contract["call_configuration"]["wire_mode"] == "json_object"
    assert contract["call_configuration"]["typed_schema_in_prompt"] is True
    assert contract["call_configuration"]["local_typed_validation"] is True
    assert contract["transport_delta"]["silent_repair"] is False
    assert expected_prompt_hashes(contract) == contract["prompt_hashes"]
    validate_authorization(
        _load(AUTHORIZATION_PATH), contract_path=CONTRACT_PATH, contract=contract
    )


def test_json_mode_stage_retains_fail_closed_program_envelope() -> None:
    contract = _load(CONTRACT_PATH)
    assert contract["call_budget"]["maximum_provider_calls"] == 3
    assert contract["call_budget"]["program_maximum_provider_calls"] == 12
    assert contract["call_configuration"]["automatic_retries"] == 0
    assert contract["call_configuration"]["graph_calls"] == 0
    assert contract["call_configuration"]["pipeline_calls"] == 0
    assert contract["call_configuration"]["evaluator_calls"] == 0
    assert contract["stop_rules"]["operational_failure_stops_remaining_calls"] is True
