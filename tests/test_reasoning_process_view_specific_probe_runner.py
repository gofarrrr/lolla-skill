from __future__ import annotations

import json
from pathlib import Path

from scripts.evals.run_reasoning_process_view_specific_probe import (
    _load,
    execute,
    run_job,
    validate_authorization,
    validate_contract,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT / "docs/evals/reasoning-process-view-specific-probe-contract-v1.json"
)
AUTHORIZATION_PATH = (
    ROOT / "docs/evals/reasoning-process-view-specific-probe-authorization-v1.json"
)


def test_view_specific_probe_contract_is_frozen_and_gemini_openrouter_only() -> None:
    contract = _load(CONTRACT_PATH)
    result = validate_contract(contract)
    assert result == {
        "status": "contract_valid",
        "case_id": "amb1-case02-nonprofit-scale",
        "job_count": 5,
        "provider": "openrouter",
        "model": "google/gemini-3.1-flash-lite",
        "provider_calls_made": 0,
    }
    config = contract["call_configuration"]
    assert config["provider"] == "openrouter"
    assert config["model"].startswith("google/gemini-")
    assert "openai" not in json.dumps(config).lower()
    assert contract["budget"]["embedding_calls"] == 0
    assert contract["stop_rules"]["no_repair_authorized_by_this_contract"] is True


def test_view_specific_probe_authorization_matches_contract() -> None:
    contract = _load(CONTRACT_PATH)
    validate_authorization(
        _load(AUTHORIZATION_PATH), contract=contract, contract_path=CONTRACT_PATH
    )


def test_missing_openrouter_key_makes_no_call(monkeypatch) -> None:
    monkeypatch.delenv("LOLLA_OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    contract = _load(CONTRACT_PATH)
    snapshot = _load(ROOT / contract["model_snapshot"]["path"])
    result = run_job(contract=contract, job=contract["jobs"][0], snapshot=snapshot)
    assert result["operational_status"] == "missing_api_key"
    assert result["provider_calls"] == 0
    assert result["requested_model"] == "google/gemini-3.1-flash-lite"


def test_execute_stops_without_key_and_preserves_zero_call_custody(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.delenv("LOLLA_OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    result = execute(contract=_load(CONTRACT_PATH), output_dir=tmp_path / "probe")
    assert result["status"] == "probe_stopped"
    assert result["attempted_call_count"] == 1
    assert result["provider_call_count"] == 0
    assert result["stop_reason"] == "missing OpenRouter API key"
    assert result["calls"] == {
        "automatic_retries": 0,
        "fallback_models": 0,
        "evaluator": 0,
        "embedding": 0,
        "graph": 0,
        "pipeline": 0,
        "runtime": 0,
    }
