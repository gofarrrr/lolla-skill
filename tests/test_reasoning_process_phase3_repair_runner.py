from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.evals import run_reasoning_process_phase3_probe as baseline
from scripts.evals import run_reasoning_process_phase3_repair as repair


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "docs/evals/reasoning-process-phase3-repair-contract-v1.json"
AUTHORIZATION_PATH = (
    ROOT / "docs/evals/reasoning-process-phase3-repair-authorization-v1.json"
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class _FakeResponse:
    def __init__(self, payload: dict):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


def _candidate() -> dict:
    return {
        "status": "supported",
        "items": [
            {
                "interpretation": "The user moved from uncertainty to a conditional four-month program while leaving the incomplete-materials condition unresolved.",
                "status": "supported",
                "evidence_ids": ["e1", "e2"],
                "auxiliary_observation_ids": [],
                "limitations": "Process description only.",
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
                "speaker": "user",
                "turn_index": 7,
                "quote": "I have not decided what happens if we find the coordinator but the materials are only partly ready.",
            },
        ],
        "park_unselected_auxiliary_observations": True,
        "global_limitations": "No final-answer evaluation.",
    }


def test_phase3_repair_contract_and_authorization_validate() -> None:
    contract = _load(CONTRACT_PATH)
    assert repair.validate_contract(contract) == {
        "status": "repair_contract_valid",
        "selected_case_id": "amb1-case02-nonprofit-scale",
        "job_count": 5,
        "maximum_provider_calls": 5,
        "provider_calls_made": 0,
    }
    repair.validate_authorization(
        _load(AUTHORIZATION_PATH), contract=contract, contract_path=CONTRACT_PATH
    )


def test_phase3_repair_changes_only_prompt_hashes() -> None:
    contract = _load(CONTRACT_PATH)
    baseline_contract = _load(
        ROOT / contract["baseline_contract"]["path"]
    )
    baseline_jobs = {item["view_kind"]: item for item in baseline_contract["jobs"]}
    for job in contract["jobs"]:
        old = baseline_jobs[job["view_kind"]]
        assert job["packet_sha256"] == old["packet_sha256"]
        assert job["response_schema_sha256"] == old["response_schema_sha256"]
        assert job["system_prompt_sha256"] != old["system_prompt_sha256"]
        assert job["user_prompt_sha256"] != old["user_prompt_sha256"]
    assert contract["call_configuration"] == baseline_contract["call_configuration"]
    assert contract["model_snapshot"] == baseline_contract["model_snapshot"]


def test_phase3_repair_job_uses_gemini_and_rekeys_attempt_ids(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contract = _load(CONTRACT_PATH)
    snapshot = _load(ROOT / contract["model_snapshot"]["path"])
    provider = {
        "model": "google/gemini-3.1-flash-lite-20260507",
        "choices": [
            {"finish_reason": "stop", "message": {"content": json.dumps(_candidate())}}
        ],
        "usage": {
            "prompt_tokens": 5300,
            "completion_tokens": 400,
            "total_tokens": 5700,
            "cost": 0.002,
        },
    }
    monkeypatch.setenv("OPENROUTER_API_KEY", "fake")
    monkeypatch.setattr(
        baseline.request, "urlopen", lambda request, timeout: _FakeResponse(provider)
    )
    result = repair.run_job(
        contract=contract, job=contract["jobs"][0], snapshot=snapshot
    )
    assert result["operational_status"] == "ok"
    assert result["typed_status"] == "admitted"
    assert result["requested_model"] == "google/gemini-3.1-flash-lite"
    assert result["prompt_version"].endswith("generic_repair_prompt.v1")
    ids = [
        item["observation_id"]
        for item in result["compiled"]["model_addendum"]["observations"]
    ]
    assert all(item.startswith("phase3-repair-") for item in ids)
    assert result["compiled"]["view_validation"]["exact_input_accounting"] is True
