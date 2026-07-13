from __future__ import annotations

import io
import json
from pathlib import Path
from urllib import error

import pytest

from scripts.evals.run_r3_repaired_pressure import (
    run_once,
    validate_execution_contract,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs/evals/lolla-r3-repaired-pressure-execution-contract-v1.json"
AUTHORIZATION = ROOT / "docs/evals/lolla-r3-repaired-pressure-authorization-v1.json"


class _Response:
    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


def _contract_bundle() -> tuple[dict, dict]:
    return validate_execution_contract(
        contract_path=CONTRACT,
        authorization_path=AUTHORIZATION,
    )


def _valid_response(bundle: dict) -> dict:
    rows = []
    active = bundle["packet"]["constitutional_graph_survival"][
        "active_pressure_items"
    ]
    for item in active:
        rows.append(
            {
                "pressure_id": item["pressure_id"],
                "disposition": "reject",
                "source_turn_numbers": [1],
                "effect": "no_material_effect",
                "strongest_plausible_application": (
                    "Test the strongest source-grounded use of this pressure."
                ),
                "attempted_application_condition": (
                    "The supplied source would need to establish its mechanism."
                ),
                "why": "The fixture source does not establish that mechanism.",
                "disposition_boundary": "No supplied turn establishes it.",
                "visible_effect": "",
                "private_guardrail": "",
            }
        )
    return {
        "candidate_dispositions": rows,
        "reconsidered_answer": "Preserve the bounded source-grounded recommendation.",
        "change_summary": "No pressure earned a change in this fixture.",
        "original_answer_preservation": "preserved",
    }


def _payload(bundle: dict, *, content: str | None = None) -> dict:
    response = _valid_response(bundle)
    return {
        "id": "gen-r3-repaired-fixture",
        "model": "google/gemini-3.1-flash-lite",
        "provider": "Google",
        "usage": {
            "prompt_tokens": 8200,
            "completion_tokens": 2100,
            "total_tokens": 10300,
            "cost": 0.0052,
        },
        "choices": [
            {
                "finish_reason": "stop",
                "message": {"content": content or json.dumps(response)},
            }
        ],
    }


def test_repaired_execution_contract_freezes_one_pressure_call_and_no_quiet() -> None:
    contract, bundle = _contract_bundle()

    assert contract["status"] == "frozen_before_one_repaired_pressure_call"
    assert contract["budget"] == {
        "maximum_provider_calls": 1,
        "maximum_provider_reported_cost_usd": 0.01,
        "maximum_estimated_call_cost_usd": 0.0081855,
        "automatic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
    }
    assert contract["operator"]["model"] == "google/gemini-3.1-flash-lite"
    assert contract["operator"]["provider_order"] == ["google-vertex/global"]
    assert contract["operator"]["allow_fallbacks"] is False
    assert contract["execution_policy"]["quiet_control_authorized_now"] is False
    assert bundle["request_contract"]["provider_calls_authorized"] == 0


def test_repaired_runner_makes_one_call_and_requires_source_review(
    monkeypatch, tmp_path: Path
) -> None:
    contract, bundle = _contract_bundle()
    calls = 0

    def fake_urlopen(_request, timeout):
        nonlocal calls
        calls += 1
        assert timeout == 90.0
        return _Response(_payload(bundle))

    monkeypatch.setenv("OPENROUTER_API_KEY", "fixture-key")
    monkeypatch.setattr(
        "scripts.evals.run_r3_repaired_pressure.request.urlopen", fake_urlopen
    )
    result = run_once(
        contract=contract,
        bundle=bundle,
        contract_path=CONTRACT,
        authorization_path=AUTHORIZATION,
        output=tmp_path / "public",
        private_output=tmp_path / "private",
    )

    assert calls == 1
    assert result["status"] == (
        "pressure_response_mechanically_valid_source_review_required"
    )
    assert result["provider_calls"] == 1
    assert result["provider_reported_cost_usd"] == 0.0052
    assert result["operator_identity_valid"] is True
    assert result["reasoning_content_returned"] is False
    assert result["mechanical_contract_valid"] is True
    assert result["source_review_required"] is True
    assert result["quiet_control_authorized"] is False
    assert result["compiled"]["all_active_candidates_accounted_for"] is True
    budget = json.loads((tmp_path / "public/provider-budget.json").read_text())
    assert budget["attempted_provider_calls"] == 1
    assert budget["provider_reported_cost_usd"] == 0.0052


def test_repaired_runner_preserves_and_redacts_http_failure_without_retry(
    monkeypatch, tmp_path: Path
) -> None:
    contract, bundle = _contract_bundle()
    provider_error = {
        "error": {
            "code": 400,
            "message": "Provider returned error",
            "metadata": {"provider_name": "Google"},
        },
        "user_id": "user_fixture_private_identifier",
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
    monkeypatch.setattr(
        "scripts.evals.run_r3_repaired_pressure.request.urlopen", fake_urlopen
    )
    result = run_once(
        contract=contract,
        bundle=bundle,
        contract_path=CONTRACT,
        authorization_path=AUTHORIZATION,
        output=tmp_path / "public",
        private_output=tmp_path / "private",
    )

    assert calls == 1
    assert result["status"] == "http_error_400_preserved"
    assert result["source_review_required"] is False
    assert result["quiet_control_authorized"] is False
    private = (tmp_path / "private/provider-error.json").read_text()
    public = (tmp_path / "public/provider-error-redacted.json").read_text()
    assert "user_fixture_private_identifier" in private
    assert "user_fixture_private_identifier" not in public
    assert "[redacted-private-identifier]" in public
    budget = json.loads((tmp_path / "public/provider-budget.json").read_text())
    assert budget["attempted_provider_calls"] == 1
    assert budget["exact_cost_call_count"] == 0


def test_repaired_runner_does_not_heal_fenced_json(monkeypatch, tmp_path: Path) -> None:
    contract, bundle = _contract_bundle()
    fenced = "```json\n" + json.dumps(_valid_response(bundle)) + "\n```"
    monkeypatch.setenv("OPENROUTER_API_KEY", "fixture-key")
    monkeypatch.setattr(
        "scripts.evals.run_r3_repaired_pressure.request.urlopen",
        lambda _request, timeout: _Response(_payload(bundle, content=fenced)),
    )
    result = run_once(
        contract=contract,
        bundle=bundle,
        contract_path=CONTRACT,
        authorization_path=AUTHORIZATION,
        output=tmp_path / "public",
        private_output=tmp_path / "private",
    )
    assert result["status"] == "pressure_response_invalid_preserved"
    assert result["compiled"] is None
    assert result["mechanical_contract_valid"] is False
    assert "not exact JSON" in result["validation_error"]
    assert result["source_review_required"] is False


def test_repaired_runner_missing_key_is_a_zero_call_result(
    monkeypatch, tmp_path: Path
) -> None:
    contract, bundle = _contract_bundle()
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("LOLLA_OPENROUTER_API_KEY", raising=False)
    result = run_once(
        contract=contract,
        bundle=bundle,
        contract_path=CONTRACT,
        authorization_path=AUTHORIZATION,
        output=tmp_path / "public",
        private_output=tmp_path / "private",
    )
    assert result["status"] == "missing_api_key_no_call"
    assert result["provider_calls"] == 0
    assert result["provider_attempted"] is False
    assert result["source_review_required"] is False
    assert not (tmp_path / "public/provider-budget.json").exists()


def test_repaired_runner_rejects_non_google_operator_identity(
    monkeypatch, tmp_path: Path
) -> None:
    contract, bundle = _contract_bundle()
    payload = _payload(bundle)
    payload["provider"] = "Unexpected"
    monkeypatch.setenv("OPENROUTER_API_KEY", "fixture-key")
    monkeypatch.setattr(
        "scripts.evals.run_r3_repaired_pressure.request.urlopen",
        lambda _request, timeout: _Response(payload),
    )
    result = run_once(
        contract=contract,
        bundle=bundle,
        contract_path=CONTRACT,
        authorization_path=AUTHORIZATION,
        output=tmp_path / "public",
        private_output=tmp_path / "private",
    )
    assert result["status"] == "pressure_response_valid_operator_identity_drifted"
    assert result["mechanical_contract_valid"] is False
    assert result["source_review_required"] is False
