from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.evals import run_reasoning_process_phase3_probe as runner


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "docs/evals/reasoning-process-phase3-probe-contract-v1.json"
AUTHORIZATION_PATH = (
    ROOT / "docs/evals/reasoning-process-phase3-probe-authorization-v1.json"
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _position_payload() -> dict:
    return {
        "status": "supported",
        "items": [
            {
                "interpretation": "The user moved to a conditional four-month program direction while leaving the partly-ready curriculum condition unresolved.",
                "status": "supported",
                "evidence_ids": ["e1", "e2"],
                "auxiliary_observation_ids": [],
                "limitations": "This records the working direction and qualification, not whether expansion is correct.",
            }
        ],
        "evidence": [
            {
                "evidence_id": "e1",
                "speaker": "user",
                "turn_index": 7,
                "quote": "I am leaning toward accepting a four-month, twice-monthly program at Willow Hub, but only if we recruit one named site coordinator and finish the first version of the drop-in curriculum before launch.",
            },
            {
                "evidence_id": "e2",
                "speaker": "assistant",
                "turn_index": 7,
                "quote": "That is a conditional direction, not a disguised final answer, and the unresolved point matters.",
            },
        ],
        "park_unselected_auxiliary_observations": True,
        "global_limitations": "One bounded process read.",
    }


class _FakeResponse:
    def __init__(self, payload: dict):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


def test_phase3_frozen_contract_and_authorization_validate() -> None:
    contract = _load(CONTRACT_PATH)
    result = runner.validate_contract(contract)
    assert result == {
        "status": "contract_valid",
        "selected_case_id": "amb1-case02-nonprofit-scale",
        "job_count": 5,
        "maximum_provider_calls": 5,
        "provider_calls_made": 0,
    }
    runner.validate_authorization(
        _load(AUTHORIZATION_PATH), contract=contract, contract_path=CONTRACT_PATH
    )


def test_phase3_selection_excludes_the_unique_easier_case_and_is_hash_mechanical() -> None:
    contract = _load(CONTRACT_PATH)
    selection = contract["selection"]
    assert "amb1-case05-family-archive" not in selection["eligible_case_ids"]
    assert selection["selected_case_id"] == "amb1-case02-nonprofit-scale"
    assert selection["ranking"][0]["sha256_case_id"] == min(
        item["sha256_case_id"] for item in selection["ranking"]
    )


def test_phase3_run_job_accepts_strict_exact_source_response_without_network(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contract = _load(CONTRACT_PATH)
    job = contract["jobs"][0]
    snapshot = _load(ROOT / contract["model_snapshot"]["path"])
    provider_payload = {
        "id": "fake-call",
        "model": "google/gemini-3.1-flash-lite-20260507",
        "choices": [
            {
                "finish_reason": "stop",
                "message": {"content": json.dumps(_position_payload())},
            }
        ],
        "usage": {
            "prompt_tokens": 4100,
            "completion_tokens": 450,
            "total_tokens": 4550,
            "prompt_tokens_details": {"cached_tokens": 1000},
            "cost": 0.002,
        },
    }
    monkeypatch.setenv("OPENROUTER_API_KEY", "fake-key")
    monkeypatch.setattr(
        runner.request, "urlopen", lambda request, timeout: _FakeResponse(provider_payload)
    )
    result = runner.run_job(contract=contract, job=job, snapshot=snapshot)
    assert result["operational_status"] == "ok"
    assert result["typed_status"] == "admitted"
    assert result["provider_calls"] == 1
    assert result["automatic_retries"] == 0
    assert result["fallback_models"] == 0
    assert result["estimated_cost_usd"] == pytest.approx(0.001475)
    assert result["compiled"]["view"]["budget"]["budget_exceeded"] is False
    assert result["compiled"]["model_addendum"]["boundary"][
        "direct_graph_routing_allowed"
    ] is False


def test_phase3_execute_stops_after_first_operational_failure_and_refuses_repeat(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    contract = _load(CONTRACT_PATH)

    def fail_job(**kwargs):
        job = kwargs["job"]
        return {
            "view_kind": job["view_kind"],
            "operational_status": "http_error_400",
            "typed_status": "not_observed",
            "provider_calls": 1,
            "estimated_cost_usd": None,
        }

    monkeypatch.setattr(runner, "run_job", fail_job)
    output = tmp_path / "phase3"
    result = runner.execute(contract=contract, output_dir=output)
    assert result["status"] == "baseline_stopped_operationally"
    assert result["attempted_call_count"] == 1
    assert result["provider_call_count"] == 1
    assert result["stop_reason"].startswith("operational failure")
    with pytest.raises(runner.Phase3RunnerError, match="repeat execution is forbidden"):
        runner.execute(contract=contract, output_dir=output)
