from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from scripts.evals.run_conversation_state_microtask_probe import (
    KINDS,
    MicrotaskProbeError,
    expected_prompt_hashes,
    validate_authorization,
    validate_contract,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research/conversation-state-microtask-probe-v1-2026-07-11"
CONTRACT_PATH = PACKAGE / "contract.json"
AUTHORIZATION_PATH = PACKAGE / "call-authorization.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_frozen_case02_microtask_contract_is_valid_and_provider_free() -> None:
    contract = _load(CONTRACT_PATH)
    validate_contract(contract)
    assert contract["microtask_order"] == list(KINDS)
    assert contract["case"]["case_id"] == "amb1-case02-nonprofit-scale"
    assert contract["call_budget"]["maximum_provider_calls"] == 3
    assert contract["call_configuration"]["automatic_retries"] == 0
    assert expected_prompt_hashes(contract) == contract["prompt_hashes"]


def test_one_time_authorization_is_bound_to_exact_contract() -> None:
    contract = _load(CONTRACT_PATH)
    validate_authorization(
        _load(AUTHORIZATION_PATH),
        contract=contract,
        contract_path=CONTRACT_PATH,
    )


def test_mutated_contract_lock_fails_before_provider_execution() -> None:
    contract = copy.deepcopy(_load(CONTRACT_PATH))
    contract["hash_locks"][0]["sha256"] = "0" * 64
    with pytest.raises(MicrotaskProbeError, match="artifact lock mismatch"):
        validate_contract(contract)


def test_authorization_cannot_expand_calls_or_retries() -> None:
    contract = _load(CONTRACT_PATH)
    authorization = copy.deepcopy(_load(AUTHORIZATION_PATH))
    authorization["maximum_provider_calls"] = 4
    with pytest.raises(MicrotaskProbeError, match="call ceiling"):
        validate_authorization(
            authorization, contract=contract, contract_path=CONTRACT_PATH
        )
    authorization = copy.deepcopy(_load(AUTHORIZATION_PATH))
    authorization["automatic_retries"] = 1
    with pytest.raises(MicrotaskProbeError, match="forbidden calls"):
        validate_authorization(
            authorization, contract=contract, contract_path=CONTRACT_PATH
        )


def test_closed_probe_preserves_two_calls_and_stop_before_constraints() -> None:
    positions = _load(PACKAGE / "positions-result.json")
    threads = _load(PACKAGE / "threads-result.json")
    review = _load(PACKAGE / "source-review.json")
    decision = _load(PACKAGE / "decision.json")
    assert positions["operational_status"] == "ok"
    assert positions["semantic_status"] == "candidate_quarantined"
    assert positions["candidate_custody"]["invalid_candidate_count"] == 3
    assert positions["candidate_custody"]["current_view_candidate_count"] == 0
    encoded = json.dumps(
        positions["candidate_payload"],
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    assert hashlib.sha256(encoded).hexdigest() == positions["candidate_payload_sha256"]
    assert threads["operational_status"] == "http_error_400"
    assert threads["semantic_status"] == "not_observed"
    assert threads["constraints_call_status"] == "not_run_budget_preserved"
    assert not (PACKAGE / "constraints-result.json").exists()
    assert review["calls"]["attempted"] == 2
    assert review["calls"]["automatic_retries"] == 0
    assert review["aggregate"]["probe_passed"] is False
    assert decision["status"] == "closed_informative_failure"
    assert decision["observed"]["attempted_provider_calls"] == 2


def test_failed_positions_never_enter_accepted_observed_state() -> None:
    positions = _load(PACKAGE / "positions-result.json")
    assert all(
        row["terminal_state"] == "invalid_evidence"
        and row["event_snapshot"] is None
        for row in positions["candidate_custody"]["terminal_states"]
    )
    review = _load(PACKAGE / "source-review.json")
    assert review["composition"]["attempted"] is False
    assert review["composition"]["accepted_observed_path_allowed"] is False
    assert review["composition"]["graph_routing_allowed"] is False
