from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from engine.system_b.r4_semantic_distinction import (
    SEMANTIC_DISTINCTION_PROMPT_CONTRACT,
)
from scripts.evals import build_r4_complementary_reader_preflight as base_preflight
from scripts.evals import build_r4_semantic_distinction_contract as builder
from scripts.evals import run_r4_complementary_reader_experiment as frozen
from scripts.evals import run_r4_semantic_distinction_experiment as runner


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs/evals/lolla-r4-semantic-distinction-contract-v1.json"
OUTPUT = ROOT / "research/lolla-r4-semantic-distinction-contract-2026-07-14"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _zero_uncertainty() -> dict:
    return {
        "reviews": [
            {
                "surface": "unresolved_matter",
                "outcome": "no_supported_record_observed",
                "records": [],
            },
            {
                "surface": "reopen_condition",
                "outcome": "no_supported_record_observed",
                "records": [],
            },
        ],
        "global_limitations": "Mock transport only.",
    }


def _zero_relationship() -> dict:
    return {
        "outcome": "no_supported_record_observed",
        "records": [],
        "global_limitations": "Mock transport only.",
    }


def test_provider_free_contract_rebuilds_byte_exactly() -> None:
    files = builder.build_files(OUTPUT)
    contract = builder.validate(OUTPUT)
    preflight = _load(OUTPUT / "preflight-result.json")

    assert files[str(CONTRACT.relative_to(ROOT))] == CONTRACT.read_bytes()
    assert contract["status"] == (
        "frozen_provider_free_new_call_authorization_required"
    )
    assert contract["decision_boundary"]["provider_calls_authorized"] is False
    assert contract["decision_boundary"]["authorization_file_present"] is False
    assert contract["review_contract"]["scalar_quality_score"] is None
    assert contract["prompt_contract"]["v1_historical_prompt_and_runner_changed"] is False
    assert preflight["provider_calls"] == 0
    assert preflight["provider_cost_usd"] == 0.0
    assert preflight["budget"]["conservative_estimated_total_cost_usd"] == 0.0280125
    assert all(row["case_cost_preflight_pass"] for row in preflight["cases"])


def test_runner_validates_exact_package_without_network() -> None:
    contract = runner.validate_contract(CONTRACT)

    assert contract["run_id"] == "lolla-r4-semantic-distinction-holdout-a3"
    assert contract["prompt_contract"]["version"] == (
        SEMANTIC_DISTINCTION_PROMPT_CONTRACT
    )
    assert contract["operator"]["model"] == "google/gemini-3.1-flash-lite"
    assert contract["operator"]["provider_slug"] == "google-vertex"
    assert [row["selection_role"] for row in contract["cases"]] == [
        "unseen_false_stand_down_target",
        "unseen_restraint_control",
    ]
    assert all("seeds" in row for row in contract["cases"])


def test_runner_never_loads_or_hashes_hidden_holdout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_load = runner._load
    original_file_sha = runner._file_sha
    holdout = builder.HOLDOUT.resolve()

    def guarded_load(path: Path):
        assert path.resolve() != holdout
        return original_load(path)

    def guarded_file_sha(path: Path):
        assert path.resolve() != holdout
        return original_file_sha(path)

    monkeypatch.setattr(runner, "_load", guarded_load)
    monkeypatch.setattr(runner, "_file_sha", guarded_file_sha)

    contract = runner.validate_contract(CONTRACT)

    assert contract["holdout_target"]["path"] == runner.HOLDOUT_RELATIVE


def test_mock_four_call_path_uses_v2_prompts_and_restores_frozen_module(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    contract = runner.validate_contract(CONTRACT)
    observed = []
    original_tasks = copy.deepcopy(base_preflight.TASKS)
    original_provider = frozen._provider_call
    original_relationship_builder = frozen.build_relationship_prompts_v1

    def relative(path: Path) -> str:
        try:
            return str(path.resolve().relative_to(ROOT))
        except ValueError:
            return str(path.resolve())

    monkeypatch.setattr(frozen, "_relative", relative)

    def fake_call(*, output, ordinal, case_id, task, preview, contract):
        body = preview["body"]
        observed.append(
            {
                "case_id": case_id,
                "task": task,
                "max_tokens": body["max_tokens"],
                "reasoning": body["reasoning"],
                "system": body["messages"][0]["content"],
            }
        )
        candidate = _zero_uncertainty() if task == "uncertainty" else _zero_relationship()
        call = {
            "operational_status": "candidate_parsed",
            "provider_calls": 1,
            "served_model": "google/gemini-3.1-flash-lite",
            "served_provider": "Google",
            "operator_attribution_ok": True,
            "provider_reported_cost_usd": 0.001,
            "candidate": candidate,
        }
        frozen._write(output / f"call-{ordinal:02d}-{task}-result.json", call)
        return call

    monkeypatch.setattr(runner, "_provider_call", fake_call)
    result = runner.run(contract, output=tmp_path / "mock-run")

    assert result["provider_calls"] == 4
    assert result["provider_reported_cost_usd"] == 0.004
    assert result["schema_version"] == runner.RESULT_SCHEMA
    assert result["strict_reasoning_shape_adapter_used"] is True
    assert [row["task"] for row in observed] == [
        "uncertainty",
        "relationship",
        "uncertainty",
        "relationship",
    ]
    assert all(row["reasoning"] == {"effort": "minimal", "exclude": True} for row in observed)
    assert all(
        "<semantic_contract>" in row["system"]
        and "It is correct to return no_supported_record_observed" in row["system"]
        for row in observed
    )
    assert base_preflight.TASKS == original_tasks
    assert frozen._provider_call is original_provider
    assert frozen.build_relationship_prompts_v1 is original_relationship_builder


class _FakeResponse:
    def __init__(self, payload: dict):
        self._raw = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self) -> bytes:
        return self._raw


def _provider_payload(*, message: dict) -> dict:
    return {
        "id": "generation-test",
        "model": "google/gemini-3.1-flash-lite",
        "provider": "Google",
        "choices": [{"finish_reason": "stop", "message": message}],
        "usage": {"cost": 0.001},
    }


def test_provider_call_accepts_metadata_only_reasoning_without_preserving_values(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    contract = runner.validate_contract(CONTRACT)
    preview = _load(ROOT / contract["cases"][0]["uncertainty_request_preview_path"])
    message = {
        "content": json.dumps(_zero_uncertainty()),
        "reasoning_details": [
            {
                "type": "reasoning.text",
                "format": "google-gemini-v1",
                "index": 0,
                "signature": "opaque-signature-must-not-be-preserved",
            }
        ],
    }
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-only")
    monkeypatch.setattr(
        runner.request,
        "urlopen",
        lambda *args, **kwargs: _FakeResponse(_provider_payload(message=message)),
    )

    result = runner._provider_call(
        output=tmp_path / "metadata",
        ordinal=1,
        case_id=contract["cases"][0]["case_id"],
        task="uncertainty",
        preview=preview,
        contract=contract,
    )

    assert result["operational_status"] == "candidate_parsed"
    assert result["reasoning_custody"]["status"] == "reasoning_metadata_only"
    assert result["reasoning_custody"]["exclusion_satisfied"] is True
    assert result["reasoning_values_preserved"] is False
    assert "opaque-signature" not in json.dumps(result)


def test_provider_call_fails_closed_on_reasoning_content(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    contract = runner.validate_contract(CONTRACT)
    preview = _load(ROOT / contract["cases"][0]["uncertainty_request_preview_path"])
    message = {
        "content": json.dumps(_zero_uncertainty()),
        "reasoning": "private reasoning must not be admitted or preserved",
    }
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-only")
    monkeypatch.setattr(
        runner.request,
        "urlopen",
        lambda *args, **kwargs: _FakeResponse(_provider_payload(message=message)),
    )

    result = runner._provider_call(
        output=tmp_path / "content",
        ordinal=1,
        case_id=contract["cases"][0]["case_id"],
        task="uncertainty",
        preview=preview,
        contract=contract,
    )

    assert result["operational_status"] == "reasoning_custody_failed"
    assert result["reasoning_custody"]["status"] == "reasoning_content_present"
    assert result["reasoning_custody"]["exclusion_satisfied"] is False
    assert "private reasoning" not in json.dumps(result)


def test_relationship_size_boundary_stops_before_transport(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    contract = runner.validate_contract(CONTRACT)
    preview = _load(ROOT / contract["cases"][0]["uncertainty_request_preview_path"])
    preview["body"]["messages"][1]["content"] = "x" * (
        runner.MAX_RELATIONSHIP_PROMPT_UTF8_BYTES + 1
    )
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-only")
    monkeypatch.setattr(
        runner.request,
        "urlopen",
        lambda *args, **kwargs: pytest.fail("transport must not be reached"),
    )

    result = runner._provider_call(
        output=tmp_path / "oversize",
        ordinal=1,
        case_id=contract["cases"][0]["case_id"],
        task="relationship",
        preview=preview,
        contract=contract,
    )

    assert result["provider_calls"] == 0
    assert result["operational_status"] == (
        "relationship_prompt_size_preflight_failed"
    )
    assert not (tmp_path / "oversize" / "call-01-relationship-started.json").exists()


def test_authorization_is_exact_and_cannot_expand_scope(tmp_path: Path) -> None:
    contract = runner.validate_contract(CONTRACT)
    expected = {
        "schema_version": runner.AUTH_SCHEMA,
        "status": "authorized_once_after_semantic_distinction_preflight",
        "contract_path": str(CONTRACT.relative_to(ROOT)),
        "contract_sha256": runner._file_sha(CONTRACT),
        "run_id": contract["run_id"],
        "authorized_case_ids": [row["case_id"] for row in contract["cases"]],
        "maximum_provider_calls": 4,
        "maximum_provider_reported_cost_per_case_usd": 0.015,
        "maximum_provider_reported_cost_total_usd": 0.03,
        "automatic_retries": 0,
        "semantic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
        "evaluator_calls": 0,
        "embedding_calls": 0,
        "graph_calls": 0,
        "pipeline_calls": 0,
        "runtime_calls": 0,
    }
    path = tmp_path / "authorization.json"
    path.write_text(json.dumps(expected), encoding="utf-8")
    runner.validate_authorization(path, contract=contract, contract_path=CONTRACT)
    expected["maximum_provider_calls"] = 5
    path.write_text(json.dumps(expected), encoding="utf-8")

    with pytest.raises(
        runner.R4SemanticDistinctionRunError, match="authorization drifted"
    ):
        runner.validate_authorization(path, contract=contract, contract_path=CONTRACT)
