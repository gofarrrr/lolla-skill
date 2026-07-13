from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from scripts.evals.run_conversation_state_microtask_probe import MicrotaskProbeError
from scripts.evals.run_conversation_state_microtask_probe_v2 import (
    KINDS,
    build_adapted_micro_contract,
    expected_prompt_hashes,
    validate_authorization,
    validate_contract,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research/conversation-state-microtask-probe-v2-2026-07-11"
CONTRACT_PATH = PACKAGE / "contract.json"
AUTHORIZATION_PATH = PACKAGE / "call-authorization.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_case05_transfer_contract_and_authorization_are_frozen() -> None:
    contract = _load(CONTRACT_PATH)
    validate_contract(contract)
    assert contract["microtask_order"] == list(KINDS)
    assert contract["case"]["case_id"] == "amb1-case05-family-archive"
    assert contract["repair_delta"]["direct_gemini_projection_changed"] is False
    assert contract["repair_delta"]["silent_span_id_normalization"] is False
    validate_authorization(
        _load(AUTHORIZATION_PATH),
        contract_path=CONTRACT_PATH,
        contract=contract,
    )


def test_adapter_uses_anyof_and_source_specific_full_span_id_enum() -> None:
    contract = _load(CONTRACT_PATH)
    from scripts.evals import run_conversation_state_microtask_probe as v1

    catalog = v1._catalog(contract)
    micro = build_adapted_micro_contract("threads", catalog=catalog)
    superseded = micro["schema"]["$defs"]["ThreadCandidate"]["properties"][
        "superseded_by"
    ]
    assert "anyOf" in superseded
    assert "type" not in superseded
    span_ids = micro["schema"]["$defs"]["EvidenceRef"]["properties"][
        "span_id"
    ]["enum"]
    assert len(span_ids) == 65
    assert all(value.startswith("span-") for value in span_ids)
    assert micro["allowed_span_id_count"] == 65
    assert expected_prompt_hashes(contract) == contract["prompt_hashes"]


def test_positions_repair_is_generic_not_case02_text() -> None:
    contract = _load(CONTRACT_PATH)
    from scripts.evals import run_conversation_state_microtask_probe as v1

    micro = build_adapted_micro_contract("positions", catalog=v1._catalog(contract))
    assert "qualification" in micro["system_prompt"]
    assert "focal position" in micro["system_prompt"]
    assert "Willow" not in micro["system_prompt"]
    assert "Case 02" not in micro["system_prompt"]


def test_v2_mutated_lock_or_expanded_authorization_fails_closed() -> None:
    contract = copy.deepcopy(_load(CONTRACT_PATH))
    contract["hash_locks"][0]["sha256"] = "0" * 64
    with pytest.raises(MicrotaskProbeError, match="artifact lock mismatch"):
        validate_contract(contract)
    contract = _load(CONTRACT_PATH)
    authorization = copy.deepcopy(_load(AUTHORIZATION_PATH))
    authorization["automatic_retries"] = 1
    with pytest.raises(MicrotaskProbeError, match="forbidden calls"):
        validate_authorization(
            authorization, contract_path=CONTRACT_PATH, contract=contract
        )


def test_closed_v2_preserves_operational_failure_and_stop_rule() -> None:
    failure = _load(PACKAGE / "pre-provider-runner-failure.json")
    threads = _load(PACKAGE / "threads-result.json")
    review = _load(PACKAGE / "source-review.json")
    decision = _load(PACKAGE / "decision.json")
    assert failure["provider_calls"] == 0
    assert failure["semantic_prompt_changed"] is False
    assert threads["operational_status"] == "http_error_400"
    assert threads["semantic_status"] == "not_observed"
    assert threads["constraints_call_status"] == "not_run_budget_preserved"
    assert threads["positions_call_status"] == "not_run_budget_preserved"
    assert not (PACKAGE / "constraints-result.json").exists()
    assert not (PACKAGE / "positions-result.json").exists()
    assert review["calls"]["attempted"] == 1
    assert review["calls"]["successful_provider_inference"] == 0
    assert review["composition"]["accepted_observed_path_allowed"] is False
    assert decision["status"] == "closed_operational_failure"
    assert decision["next_call_authorization"] == "not_granted"
