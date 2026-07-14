from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from engine.system_b.r3_fresh_consumer import value_sha256
from engine.system_b.r3_task_shape_counterfactual import (
    compile_collapsed_one_pass_response,
)
from scripts.evals import finalize_r3_collapsed_outcome_case as closeout
from scripts.evals import run_r3_collapsed_outcome_case as runner


ROOT = Path(__file__).resolve().parents[1]
RESULT_DIR = (
    ROOT / "research/lolla-r3-collapsed-outcome-case-2026-07-13/pressure-r1"
)


def _load(name: str) -> dict:
    return json.loads((RESULT_DIR / name).read_text(encoding="utf-8"))


def _without(value: dict, field: str) -> dict:
    return {key: item for key, item in value.items() if key != field}


def test_checked_in_closeout_is_hash_linked_and_terminal() -> None:
    redacted = _load("provider-payload-redacted.json")
    failure = _load("failure-closeout.json")
    terminal = _load("r3-terminal-result.json")
    call_result = _load("pressure-call-result.json")

    assert redacted["redacted_payload_sha256"] == value_sha256(
        _without(redacted, "redacted_payload_sha256")
    )
    assert failure["closeout_sha256"] == value_sha256(
        _without(failure, "closeout_sha256")
    )
    assert terminal["result_sha256"] == value_sha256(
        _without(terminal, "result_sha256")
    )
    assert terminal["call_result_sha256"] == call_result["call_result_sha256"]
    assert terminal["redacted_payload_sha256"] == redacted[
        "redacted_payload_sha256"
    ]
    assert terminal["closeout_sha256"] == failure["closeout_sha256"]
    assert terminal["status"] == (
        "r3_collapsed_attempt_closed_semantic_review_not_evaluable"
    )
    assert terminal["next_call_authorized"] is False
    assert terminal["quiet_control_authorized"] is False
    assert terminal["runtime_integration_authorized"] is False


def test_exact_candidate_recompiles_but_frozen_gate_blocks_review() -> None:
    _contract, material = runner.validate_execution_contract(closeout.CONTRACT)
    result = _load("pressure-call-result.json")

    reproduced = compile_collapsed_one_pass_response(
        response=result["candidate"],
        packet=material["packet"],
    )

    assert reproduced == result["compiled"]
    assert reproduced["all_active_candidates_accounted_for"] is True
    assert len(reproduced["candidate_dispositions"]) == 9
    assert result["provider_calls"] == 1
    assert result["provider_reported_cost_usd"] == 0.005517
    assert result["mechanical_contract_valid"] is False
    assert result["source_review_required"] is False
    assert result["status"] == (
        "pressure_response_valid_reasoning_exclusion_breached"
    )


def test_signature_only_metadata_is_redacted_and_not_plaintext() -> None:
    redacted = _load("provider-payload-redacted.json")
    result = _load("pressure-call-result.json")
    payload = redacted["provider_payload"]
    message = payload["choices"][0]["message"]
    detail = message["reasoning_details"][0]

    assert "reasoning" not in message
    assert set(detail) == {"format", "index", "signature", "type"}
    assert detail["signature"] == "[redacted-opaque-reasoning-signature]"
    assert detail["type"] == "reasoning.text"
    assert detail["format"] == "google-gemini-v1"
    assert "text" not in detail
    assert "summary" not in detail
    assert "data" not in detail
    assert redacted["raw_provider_payload_value_sha256"] == result[
        "provider_payload_sha256"
    ]
    assert redacted["redactions"] == [
        {
            "json_pointer": "/choices/0/message/reasoning_details/0/signature",
            "reason": "opaque provider reasoning-continuation metadata",
        }
    ]


@pytest.mark.parametrize("extra_field", ["text", "summary", "data"])
def test_reasoning_content_tampering_fails_closed(extra_field: str) -> None:
    payload = copy.deepcopy(_load("provider-payload-redacted.json")["provider_payload"])
    payload["choices"][0]["message"]["reasoning_details"][0][extra_field] = (
        "should fail"
    )

    with pytest.raises(
        closeout.R3CollapsedCloseoutError,
        match="reasoning signature metadata drifted",
    ):
        closeout._reasoning_observation(payload)


def test_exact_authorization_passes_but_pending_template_does_not() -> None:
    contract, _ = runner.validate_execution_contract(closeout.CONTRACT)

    authorization = runner.validate_authorization(
        contract=contract,
        contract_path=closeout.CONTRACT,
        authorization_path=closeout.AUTHORIZATION,
    )
    assert authorization["maximum_provider_calls"] == 1
    assert authorization["maximum_provider_reported_cost_usd"] == 0.01
    assert authorization["quiet_control_authorized"] is False

    with pytest.raises(runner.R3CollapsedRunError, match="authorization drifted"):
        runner.validate_authorization(
            contract=contract,
            contract_path=closeout.CONTRACT,
            authorization_path=(
                ROOT
                / "docs/evals/"
                "lolla-r3-collapsed-outcome-case-authorization-template-v1.json"
            ),
        )


def test_budget_and_call_result_tampering_fail_closed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    budget = _load("provider-budget.json")
    budget["provider_reported_cost_usd"] = 0.005518
    tampered_budget = tmp_path / "provider-budget.json"
    tampered_budget.write_text(json.dumps(budget), encoding="utf-8")
    monkeypatch.setattr(closeout, "PROVIDER_BUDGET", tampered_budget)
    with pytest.raises(
        closeout.R3CollapsedCloseoutError,
        match="provider budget custody drifted",
    ):
        closeout.validate()

    monkeypatch.setattr(
        closeout,
        "PROVIDER_BUDGET",
        RESULT_DIR / "provider-budget.json",
    )
    result = _load("pressure-call-result.json")
    result["candidate"]["change_summary"] = "tampered"
    tampered_result = tmp_path / "pressure-call-result.json"
    tampered_result.write_text(json.dumps(result), encoding="utf-8")
    monkeypatch.setattr(closeout, "CALL_RESULT", tampered_result)
    with pytest.raises(
        closeout.R3CollapsedCloseoutError,
        match="call result self-hash drifted",
    ):
        closeout.validate()


def test_checked_in_closeout_revalidates_without_private_payload() -> None:
    terminal = closeout.validate()

    assert terminal["provider_calls"] == 1
    assert terminal["provider_reported_cost_usd"] == 0.005517
    assert terminal["collapsed_compiler_accepted"] is True
    assert terminal["frozen_mechanical_contract_valid"] is False
    assert terminal["semantic_review_performed"] is False
