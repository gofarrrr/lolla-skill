from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from engine.system_b.r3_fresh_consumer import (
    MAX_PROVIDER_COST_USD,
    REVIEW_DIMENSIONS,
    R3FreshConsumerError,
    build_source_review_template,
    compile_pressure_response,
    validate_pressure_bundle,
    validate_source_review,
    value_sha256,
)
from scripts.evals.build_r3_fresh_consumer_pressure import build
from scripts.evals.finalize_r3_fresh_consumer_failure import (
    R3FailureCloseoutError,
    build_failure_closeout,
)
from scripts.evals.run_r3_fresh_consumer_pressure import (
    run_once,
    validate_contract,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs/evals/lolla-r3-fresh-consumer-pressure-contract-v1.json"
AUTHORIZATION = (
    ROOT / "docs/evals/lolla-r3-fresh-consumer-pressure-authorization-v1.json"
)


class _Response:
    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


def _bundle() -> dict:
    _portfolio, merged = build()
    result = copy.deepcopy(merged)
    result.pop("preflight_summary")
    return result


def _valid_response(bundle: dict) -> dict:
    rows = []
    for item in bundle["packet"]["constitutional_graph_survival"][
        "active_pressure_items"
    ]:
        rows.append(
            {
                "pressure_id": item["pressure_id"],
                "model_id": item["model_id"],
                "disposition": "reject",
                "source_turn_numbers": [1],
                "effect": "no_material_effect",
                "strongest_plausible_application": "Test the strongest source-grounded use.",
                "attempted_application_condition": "The source would need to establish the mechanism.",
                "why": "The fixture does not establish the mechanism.",
                "failed_condition": "No supplied turn establishes it.",
                "reopen_condition": "",
                "visible_effect": "",
                "private_guardrail": "",
                "risk_if_forced": "It would turn a lens into a case fact.",
                "risk_if_ignored": "A real edge could remain untested.",
            }
        )
    return {
        "candidate_dispositions": rows,
        "reconsidered_answer": "Preserve the bounded source-grounded recommendation.",
        "change_summary": "No pressure earned a change in this fixture.",
        "original_answer_preservation": "preserved",
    }


def _passing_review(bundle: dict, call_sha: str) -> dict:
    review = build_source_review_template(
        bundle=bundle,
        call_result_sha256=call_sha,
    )
    first = bundle["packet"]["constitutional_graph_survival"][
        "active_pressure_items"
    ][0]["pressure_id"]
    for item in review["dimensions"]:
        item.update(
            {
                "verdict": "pass",
                "why": "Source-first fixture review passes this separate axis.",
                "source_turn_numbers": [1],
                "pressure_ids": [first],
                "response_evidence": "The compiled response preserves exact source custody.",
            }
        )
    review["value_signal"] = {
        "kind": "valuable_rejection",
        "pressure_ids": [first],
        "source_turn_numbers": [1],
        "why": "The rejection prevents the graph lens from becoming unsupported evidence.",
    }
    review["pressure_case_decision"] = "pass_authorize_quiet_control"
    review["quiet_control_authorized"] = True
    return review


def _preserved_http_failure(bundle: dict) -> tuple[dict, dict, dict, dict]:
    provider_error = {
        "provider_error": {
            "error": {
                "code": 400,
                "message": "Provider returned error",
                "metadata": {
                    "provider_name": "Google",
                    "raw": '{"error":{"status":"INVALID_ARGUMENT"}}',
                },
            },
            "user_id": "user_fixture_private",
        }
    }
    shared = {
        "run_id": "r3-fixture",
        "case_id": bundle["case_id"],
        "contract_sha256": "1" * 64,
        "authorization_sha256": "2" * 64,
        "bundle_sha256": bundle["bundle_sha256"],
        "request_body_sha256": bundle["hashes"]["request_body_sha256"],
        "budget_reservation_id": "reservation-fixture",
    }
    started = {
        **shared,
        "status": "started_before_network_transport",
        "provider_calls": 1,
        "automatic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
    }
    result = {
        **shared,
        "status": "http_error_400_preserved",
        "provider_calls": 1,
        "http_status": 400,
        "provider_error_sha256": value_sha256(provider_error["provider_error"]),
        "source_review_required": False,
        "quiet_control_authorized": False,
    }
    result["call_result_sha256"] = value_sha256(result)
    budget = {
        "limits": {
            "maximum_provider_calls": 1,
            "maximum_accounted_cost_usd": 0.01,
        },
        "attempted_provider_calls": 1,
        "accounted_cost_usd": 0.00816425,
        "exact_cost_call_count": 0,
        "reservations": [
            {
                "reservation_id": "reservation-fixture",
                "status": "finalized",
                "exact_cost_usd": None,
                "accounting_basis": "reserved_worst_case_unknown_charge",
            }
        ],
    }
    return result, started, budget, provider_error


def test_r3_bundle_replays_current_r2_portfolio_and_fits_one_cent() -> None:
    portfolio, merged = build()
    bundle = copy.deepcopy(merged)
    summary = bundle.pop("preflight_summary")

    validate_pressure_bundle(bundle)
    assert portfolio["path_counts"] == {
        "direct_active": 6,
        "direct_cap_reserve": 3,
        "graph_active": 3,
        "graph_cap_or_duplicate_reserve": 23,
        "duplicate_input": 0,
        "malformed_input": 0,
    }
    assert [
        item["model_id"] for item in portfolio["active_pressure_items"]
    ] == [
        "bottlenecks",
        "game-theory-payoffs",
        "inversion",
        "systems-thinking",
        "incentives",
        "margin-of-safety",
        "system-1",
        "confirmation-bias",
        "cognitive-load-theory",
    ]
    assert summary["maximum_estimated_call_cost_usd"] <= MAX_PROVIDER_COST_USD
    assert summary["provider_calls"] == 0
    assert bundle["request_body"]["provider"]["allow_fallbacks"] is False
    assert bundle["request_body"]["provider"]["data_collection"] == "deny"
    assert bundle["request_body"]["response_format"]["type"] == "json_schema"
    assert bundle["request_body"]["response_format"]["json_schema"]["strict"] is True


def test_r3_bundle_preserves_full_conversation_original_answer_and_hashes() -> None:
    first = _bundle()
    second = _bundle()
    packet = first["packet"]

    assert first == second
    assert packet["source_turn_numbers"] == list(range(1, 13))
    source_path = ROOT / (
        "research/simulated-reliability-corpus-v1-2026-07-12/"
        "naturalized-transfer-sources/v1-case01-flood-infrastructure.txt"
    )
    assert packet["authoritative_conversation"] == source_path.read_text(encoding="utf-8")
    assert packet["preservation_material"]["original_final_assistant_turn"] == 12
    assert packet["preservation_material"]["original_final_answer"] in packet[
        "authoritative_conversation"
    ]
    assert first["hashes"]["request_body_sha256"] == value_sha256(
        first["request_body"]
    )


def test_r3_bundle_detects_packet_or_portfolio_tampering() -> None:
    bundle = _bundle()
    tampered = copy.deepcopy(bundle)
    tampered["packet"]["constitutional_graph_survival"]["active_pressure_items"][0][
        "concrete_test"
    ] = "Substituted pressure"
    with pytest.raises((R3FreshConsumerError, ValueError), match="hash"):
        validate_pressure_bundle(tampered)


def test_r3_compiler_enforces_packet_order_and_disposition_semantics() -> None:
    bundle = _bundle()
    response = _valid_response(bundle)
    compiled = compile_pressure_response(response=response, packet=bundle["packet"])
    assert compiled["all_active_candidates_accounted_for"] is True
    assert compiled["disposition_counts"] == {"reject": 9}

    wrong_order = copy.deepcopy(response)
    wrong_order["candidate_dispositions"][0], wrong_order["candidate_dispositions"][1] = (
        wrong_order["candidate_dispositions"][1],
        wrong_order["candidate_dispositions"][0],
    )
    with pytest.raises(R3FreshConsumerError, match="packet order"):
        compile_pressure_response(response=wrong_order, packet=bundle["packet"])

    forced = copy.deepcopy(response)
    forced["candidate_dispositions"][0]["visible_effect"] = "Changed answer"
    with pytest.raises(R3FreshConsumerError, match="no claimed effect"):
        compile_pressure_response(response=forced, packet=bundle["packet"])


def test_r3_source_review_has_vector_gate_and_no_scalar() -> None:
    bundle = _bundle()
    call_sha = hashlib.sha256(b"call-result").hexdigest()
    review = _passing_review(bundle, call_sha)
    validation = validate_source_review(
        review,
        bundle=bundle,
        call_result_sha256=call_sha,
    )
    assert validation["status"] == "valid"
    assert validation["pressure_case_passed"] is True
    assert validation["quiet_control_authorized"] is True
    assert list(validation["dimension_verdicts"]) == list(REVIEW_DIMENSIONS)
    assert review["scalar_quality_score"] is None

    failed = copy.deepcopy(review)
    failed["dimensions"][0]["verdict"] = "uncertain"
    failed["pressure_case_decision"] = "fail_preserve_and_stop"
    failed["quiet_control_authorized"] = False
    validation = validate_source_review(
        failed,
        bundle=bundle,
        call_result_sha256=call_sha,
    )
    assert validation["status"] == "valid"
    assert validation["pressure_case_passed"] is False
    assert validation["quiet_control_authorized"] is False


def test_r3_frozen_contract_validates_provider_free() -> None:
    contract, bundle = validate_contract(
        contract_path=CONTRACT,
        authorization_path=AUTHORIZATION,
    )
    assert contract["budget"]["maximum_provider_calls"] == 1
    assert contract["budget"]["maximum_provider_reported_cost_usd"] == 0.01
    assert bundle["request_contract"]["automatic_retries"] == 0
    assert bundle["next_call_authorized"] is False


def test_r3_runner_makes_exactly_one_call_and_preserves_exact_cost(
    monkeypatch, tmp_path: Path
) -> None:
    contract, bundle = validate_contract(
        contract_path=CONTRACT,
        authorization_path=AUTHORIZATION,
    )
    response = _valid_response(bundle)
    payload = {
        "id": "gen-r3-fixture",
        "model": "google/gemini-3.1-flash-lite",
        "provider": "Google",
        "usage": {
            "prompt_tokens": 8100,
            "completion_tokens": 2200,
            "total_tokens": 10300,
            "cost": 0.005325,
        },
        "choices": [
            {
                "finish_reason": "stop",
                "message": {"content": json.dumps(response)},
            }
        ],
    }
    calls = 0

    def fake_urlopen(_request, timeout):
        nonlocal calls
        calls += 1
        assert timeout == 90.0
        return _Response(payload)

    monkeypatch.setenv("OPENROUTER_API_KEY", "fixture-key")
    monkeypatch.setenv(
        "LOLLA_PROVIDER_BUDGET_STATE", str(tmp_path / "preexisting-budget-path.json")
    )
    monkeypatch.setattr(
        "scripts.evals.run_r3_fresh_consumer_pressure.request.urlopen", fake_urlopen
    )
    result = run_once(
        contract=contract,
        bundle=bundle,
        contract_path=CONTRACT,
        authorization_path=AUTHORIZATION,
        output=tmp_path / "run",
    )

    assert calls == 1
    assert result["status"] == "pressure_response_mechanically_valid_source_review_required"
    assert result["provider_calls"] == 1
    assert result["provider_reported_cost_usd"] == 0.005325
    assert result["compiled"]["all_active_candidates_accounted_for"] is True
    budget = json.loads((tmp_path / "run/provider-budget.json").read_text())
    assert budget["attempted_provider_calls"] == 1
    assert budget["provider_reported_cost_usd"] == 0.005325
    assert (tmp_path / "run/pressure-call-started.json").is_file()
    assert (tmp_path / "run/provider-payload.json").is_file()


def test_r3_runner_does_not_heal_fenced_json(monkeypatch, tmp_path: Path) -> None:
    contract, bundle = validate_contract(
        contract_path=CONTRACT,
        authorization_path=AUTHORIZATION,
    )
    response = _valid_response(bundle)
    payload = {
        "id": "gen-r3-fenced-fixture",
        "model": "google/gemini-3.1-flash-lite",
        "provider": "Google",
        "usage": {
            "prompt_tokens": 8100,
            "completion_tokens": 2200,
            "total_tokens": 10300,
            "cost": 0.005325,
        },
        "choices": [
            {
                "finish_reason": "stop",
                "message": {"content": "```json\n" + json.dumps(response) + "\n```"},
            }
        ],
    }
    monkeypatch.setenv("OPENROUTER_API_KEY", "fixture-key")
    monkeypatch.setenv(
        "LOLLA_PROVIDER_BUDGET_STATE", str(tmp_path / "preexisting-budget-path.json")
    )
    monkeypatch.setattr(
        "scripts.evals.run_r3_fresh_consumer_pressure.request.urlopen",
        lambda _request, timeout: _Response(payload),
    )
    result = run_once(
        contract=contract,
        bundle=bundle,
        contract_path=CONTRACT,
        authorization_path=AUTHORIZATION,
        output=tmp_path / "run",
    )
    assert result["status"] == "pressure_response_invalid_preserved"
    assert result["provider_calls"] == 1
    assert result["compiled"] is None
    assert "not exact JSON" in result["validation_error"]


def test_r3_failure_closeout_preserves_one_attempt_and_redacts_private_id() -> None:
    bundle = _bundle()
    result, started, budget, provider_error = _preserved_http_failure(bundle)
    raw_file_sha = hashlib.sha256(
        (json.dumps(provider_error, sort_keys=True) + "\n").encode("utf-8")
    ).hexdigest()

    redacted, closeout, terminal = build_failure_closeout(
        call_result=result,
        call_started=started,
        provider_budget=budget,
        provider_error_file=provider_error,
        provider_error_file_sha256=raw_file_sha,
        bundle=bundle,
    )

    assert redacted["provider_error"]["user_id"] == "[redacted-private-identifier]"
    assert "user_fixture_private" not in json.dumps(redacted)
    assert closeout["execution_contract_result"] == {
        "provider_calls_attempted": 1,
        "provider_calls_succeeded": 0,
        "automatic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
        "quiet_control_authorized": False,
        "quiet_control_calls": 0,
    }
    assert closeout["source_review"]["scalar_quality_score"] is None
    assert closeout["source_review"]["dimensions"][0]["verdict"] == (
        "not_evaluable_before_inference"
    )
    assert closeout["source_review"]["dimensions"][-1]["verdict"] == "partial"
    assert closeout["decision"]["additional_provider_call_authorized"] is False
    assert terminal["status"] == "complete_negative_operational_result"
    assert terminal["next_call_authorized"] is False


def test_r3_failure_closeout_rejects_error_hash_drift() -> None:
    bundle = _bundle()
    result, started, budget, provider_error = _preserved_http_failure(bundle)
    provider_error["provider_error"]["error"]["message"] = "mutated"
    with pytest.raises(R3FailureCloseoutError, match="provider error hash drifted"):
        build_failure_closeout(
            call_result=result,
            call_started=started,
            provider_budget=budget,
            provider_error_file=provider_error,
            provider_error_file_sha256="3" * 64,
            bundle=bundle,
        )


def test_r3_checked_in_negative_result_chain_is_hash_locked() -> None:
    output = ROOT / "research/lolla-r3-fresh-consumer-2026-07-13/pressure-r1"
    redacted = json.loads((output / "provider-error-redacted.json").read_text())
    closeout = json.loads((output / "failure-closeout.json").read_text())
    terminal = json.loads((output / "r3-result.json").read_text())

    assert redacted["redacted_error_sha256"] == value_sha256(
        {key: item for key, item in redacted.items() if key != "redacted_error_sha256"}
    )
    assert closeout["failure_closeout_sha256"] == value_sha256(
        {
            key: item
            for key, item in closeout.items()
            if key != "failure_closeout_sha256"
        }
    )
    assert terminal["r3_result_sha256"] == value_sha256(
        {key: item for key, item in terminal.items() if key != "r3_result_sha256"}
    )
    assert closeout["provider_error"]["private_raw_file_sha256"] == redacted[
        "raw_provider_error_file_sha256"
    ]
    assert closeout["provider_error"]["checked_in_redacted_error_sha256"] == redacted[
        "redacted_error_sha256"
    ]
    assert terminal["failure_closeout_sha256"] == closeout[
        "failure_closeout_sha256"
    ]
    assert terminal["next_call_authorized"] is False
