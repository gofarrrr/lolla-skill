from __future__ import annotations

import copy
import io
import json
from pathlib import Path
from urllib import error

import pytest

from scripts.evals import build_r3_collapsed_outcome_case_execution as execution
from scripts.evals import run_r3_collapsed_outcome_case as runner


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = execution.CONTRACT
AUTHORIZATION_TEMPLATE = execution.AUTHORIZATION_TEMPLATE


class _Response:
    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


def _contract_material() -> tuple[dict, dict]:
    return runner.validate_execution_contract(CONTRACT)


def _wire_response(material: dict) -> dict:
    rows = []
    for item in material["packet"]["constitutional_graph_survival"][
        "active_pressure_items"
    ]:
        rows.append(
            {
                "pressure_id": item["pressure_id"],
                "outcome": "reject",
                "source_turn_numbers": [1],
                "strongest_plausible_application": (
                    "Test the strongest source-grounded application."
                ),
                "attempted_application_condition": (
                    "The source must establish the proposed mechanism."
                ),
                "why": "The provider-free fixture does not establish it.",
                "disposition_boundary": "No supplied turn establishes it.",
                "visible_effect": "",
                "private_guardrail": "",
            }
        )
    return {
        "candidate_dispositions": rows,
        "reconsidered_answer": "Preserve the bounded original recommendation.",
        "change_summary": "All pressure stood down in this fixture.",
        "original_answer_preservation": "preserved",
    }


def _payload(material: dict, *, content: str | None = None) -> dict:
    return {
        "id": "gen-r3-collapsed-fixture",
        "model": runner.MODEL,
        "provider": "Google",
        "usage": {
            "prompt_tokens": 9400,
            "completion_tokens": 1700,
            "total_tokens": 11100,
            "cost": 0.0049,
        },
        "choices": [
            {
                "finish_reason": "stop",
                "message": {
                    "content": content or json.dumps(_wire_response(material))
                },
            }
        ],
    }


def test_execution_package_is_frozen_but_authorizes_zero_calls() -> None:
    contract, material = _contract_material()
    summary = execution.validate()

    assert contract["status"] == "frozen_awaiting_founder_authorization"
    assert contract["decision_state"] == {
        "founder_decision": "pending",
        "provider_calls_made": 0,
        "provider_calls_authorized_now": 0,
        "execution_requires_separate_authorization": True,
        "available_account_balance_does_not_expand_budget": True,
    }
    assert contract["budget"] == {
        "maximum_provider_calls": 1,
        "maximum_provider_reported_cost_usd": 0.01,
        "maximum_estimated_call_cost_usd": 0.00836875,
        "automatic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
        "premium_models": 0,
        "quiet_control_calls": 0,
    }
    assert contract["operator"]["model"] == runner.MODEL
    assert contract["operator"]["provider_order"] == ["google-vertex/global"]
    assert contract["operator"]["allow_fallbacks"] is False
    assert contract["operator"]["data_collection"] == "deny"
    assert material["bundle"]["next_call_authorized"] is False
    assert summary["provider_calls_authorized"] == 0


def test_protected_review_is_complete_and_absent_from_request() -> None:
    contract, material = _contract_material()
    review = json.loads(execution.REVIEW.read_text(encoding="utf-8"))
    request = json.dumps(material["request_body"], ensure_ascii=False)

    assert contract["protected_review"]["supplied_to_provider"] is False
    assert len(review["protected_opportunities"]) == 3
    assert len(review["strengths_to_preserve"]) == 5
    assert len(review["candidate_review_boundaries"]) == 9
    assert "t01_endogenous_customer_base_evidence" not in request
    assert "mixed_pressure_opportunity_with_required_restraint" not in request


def test_pending_template_cannot_authorize_execution() -> None:
    contract, _ = _contract_material()

    with pytest.raises(runner.R3CollapsedRunError, match="authorization drifted"):
        runner.validate_authorization(
            contract=contract,
            contract_path=CONTRACT,
            authorization_path=AUTHORIZATION_TEMPLATE,
        )


def test_exact_founder_authorization_shape_can_pass_after_future_decision(
    tmp_path: Path,
) -> None:
    contract, _ = _contract_material()
    authorization = json.loads(AUTHORIZATION_TEMPLATE.read_text(encoding="utf-8"))
    authorization.update(
        {
            "status": "authorized_once_by_founder_for_collapsed_outcome_case",
            "founder_decision": "authorize_one_call",
            "authorization_basis": "Fixture-only founder authorization evidence.",
        }
    )
    temporary = ROOT / ".tmp-r3-collapsed-authorization-test.json"
    temporary.write_text(json.dumps(authorization), encoding="utf-8")
    try:
        observed = runner.validate_authorization(
            contract=contract,
            contract_path=CONTRACT,
            authorization_path=temporary,
        )
    finally:
        temporary.unlink(missing_ok=True)
    assert observed["maximum_provider_calls"] == 1
    assert observed["quiet_control_authorized"] is False


def test_runner_accepts_one_mocked_collapsed_result_and_requires_review(
    monkeypatch, tmp_path: Path
) -> None:
    contract, material = _contract_material()
    calls = 0

    def fake_urlopen(_request, timeout):
        nonlocal calls
        calls += 1
        assert timeout == 90.0
        return _Response(_payload(material))

    monkeypatch.setenv("OPENROUTER_API_KEY", "fixture-key")
    monkeypatch.setattr(runner.request, "urlopen", fake_urlopen)
    result = runner.run_once(
        contract=contract,
        material=material,
        contract_path=CONTRACT,
        authorization_path=AUTHORIZATION_TEMPLATE,
        output=tmp_path / "public",
        private_output=tmp_path / "private",
    )

    assert calls == 1
    assert result["status"] == (
        "pressure_response_mechanically_valid_source_review_required"
    )
    assert result["provider_reported_cost_usd"] == 0.0049
    assert result["mechanical_contract_valid"] is True
    assert result["source_review_required"] is True
    assert result["compiled"]["all_active_candidates_accounted_for"] is True
    assert (tmp_path / "private/provider-payload.json").is_file()
    assert not (tmp_path / "public/provider-payload.json").exists()
    budget = json.loads((tmp_path / "public/provider-budget.json").read_text())
    assert budget["attempted_provider_calls"] == 1
    assert budget["provider_reported_cost_usd"] == 0.0049


def test_runner_preserves_http_failure_without_retry(
    monkeypatch, tmp_path: Path
) -> None:
    contract, material = _contract_material()
    provider_error = {
        "error": {"code": 400, "message": "Provider rejected request"},
        "user_id": "private-fixture-id",
    }
    calls = 0

    def fake_urlopen(req, timeout):
        nonlocal calls
        calls += 1
        raise error.HTTPError(
            req.full_url,
            400,
            "Bad Request",
            {},
            io.BytesIO(json.dumps(provider_error).encode("utf-8")),
        )

    monkeypatch.setenv("OPENROUTER_API_KEY", "fixture-key")
    monkeypatch.setattr(runner.request, "urlopen", fake_urlopen)
    result = runner.run_once(
        contract=contract,
        material=material,
        contract_path=CONTRACT,
        authorization_path=AUTHORIZATION_TEMPLATE,
        output=tmp_path / "public",
        private_output=tmp_path / "private",
    )

    assert calls == 1
    assert result["status"] == "http_error_400_preserved"
    assert result["source_review_required"] is False
    private = (tmp_path / "private/provider-error.json").read_text()
    public = (tmp_path / "public/provider-error-redacted.json").read_text()
    assert "private-fixture-id" in private
    assert "private-fixture-id" not in public
    assert "[redacted-private-identifier]" in public


def test_runner_does_not_heal_fenced_json(monkeypatch, tmp_path: Path) -> None:
    contract, material = _contract_material()
    fenced = "```json\n" + json.dumps(_wire_response(material)) + "\n```"
    monkeypatch.setenv("OPENROUTER_API_KEY", "fixture-key")
    monkeypatch.setattr(
        runner.request,
        "urlopen",
        lambda _request, timeout: _Response(_payload(material, content=fenced)),
    )
    result = runner.run_once(
        contract=contract,
        material=material,
        contract_path=CONTRACT,
        authorization_path=AUTHORIZATION_TEMPLATE,
        output=tmp_path / "public",
        private_output=tmp_path / "private",
    )
    assert result["status"] == "pressure_response_invalid_preserved"
    assert result["mechanical_contract_valid"] is False
    assert "not exact JSON" in result["validation_error"]


def test_contract_and_review_tampering_fail_closed(
    monkeypatch, tmp_path: Path
) -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    contract["budget"]["automatic_retries"] = 1
    tampered_contract = tmp_path / "contract.json"
    tampered_contract.write_text(json.dumps(contract), encoding="utf-8")
    with pytest.raises(runner.R3CollapsedRunError, match="budget drifted"):
        runner.validate_execution_contract(tampered_contract)

    review = json.loads(execution.REVIEW.read_text(encoding="utf-8"))
    review["candidate_review_boundaries"] = review[
        "candidate_review_boundaries"
    ][:-1]
    tampered_review = tmp_path / "review.json"
    tampered_review.write_text(json.dumps(review), encoding="utf-8")
    monkeypatch.setattr(runner, "REVIEW", tampered_review)
    with pytest.raises(runner.R3CollapsedRunError, match="protected review"):
        runner.validate_execution_contract(CONTRACT)
