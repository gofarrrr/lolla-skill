from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts.evals import run_frozen_cold_reader as reader


def _write(path: Path, value: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict:
    monkeypatch.setattr(reader, "REPO_ROOT", tmp_path)
    receipt_md = tmp_path / "receipt.md"
    receipt_json = tmp_path / "receipt.json"
    receipt_md_hash = _write(receipt_md, "# Receipt\n\nnot product proof\n")
    receipt_json_hash = _write(receipt_json, json.dumps({"status": "complete"}))
    locks = []
    for role in ("reader_runner", "receipt_contract", "pricing"):
        path = tmp_path / "locks" / f"{role}.txt"
        locks.append(
            {
                "role": role,
                "path": str(path.relative_to(tmp_path)),
                "sha256": _write(path, role),
            }
        )
    contract = {
        "schema_version": reader.CONTRACT_SCHEMA,
        "status": "frozen_before_call",
        "run_id": "reader_test_a1",
        "receipt": {
            "markdown_path": "receipt.md",
            "markdown_sha256": receipt_md_hash,
            "json_path": "receipt.json",
            "json_sha256": receipt_json_hash,
        },
        "system_prompt": "Reconstruct only from the receipt and return JSON.",
        "reader_instruction": "Explain what happened, what is known, and what is not proven.",
        "output_contract": {
            "required_keys": [
                "source_decision_state",
                "source_vs_prior_assistant_claims",
                "stage_a_reconstruction",
                "pressure_reconstruction",
                "paired_experiment_reconstruction",
                "graph_reconstruction",
                "custody_vs_quality",
                "supported_claims",
                "claims_not_supported",
                "current_authorizations",
                "uncertainties",
                "human_questions",
                "reconstruction_failures_or_ambiguities",
            ],
            "field_types": {
                "source_decision_state": "string",
                "source_vs_prior_assistant_claims": "array_of_objects",
                "stage_a_reconstruction": "string",
                "pressure_reconstruction": "array_of_objects",
                "paired_experiment_reconstruction": "object",
                "graph_reconstruction": "object",
                "custody_vs_quality": "string",
                "supported_claims": "array_of_strings",
                "claims_not_supported": "array_of_strings",
                "current_authorizations": "object",
                "uncertainties": "array_of_strings",
                "human_questions": "array_of_strings",
                "reconstruction_failures_or_ambiguities": "array_of_strings",
            },
            "object_contracts": {
                "paired_experiment_reconstruction": {
                    "required_keys": ["control", "treatment", "difference", "limits"]
                },
                "graph_reconstruction": {
                    "required_keys": ["v1_issue", "v2_repair", "current_read", "limits"]
                },
                "current_authorizations": {
                    "required_keys": ["allowed", "blocked", "human_status", "next_gate"]
                },
            },
            "object_array_contracts": {
                "source_vs_prior_assistant_claims": {
                    "required_keys": ["item", "status", "basis"],
                    "maximum_items": 10,
                },
                "pressure_reconstruction": {
                    "required_keys": ["pressure", "origin", "status", "consequence", "limits"],
                    "maximum_items": 8,
                },
            },
        },
        "call_configuration": {
            "provider": "openrouter",
            "model": "openai/gpt-5.1-chat",
            "temperature": 0.1,
            "max_output_tokens": 2200,
            "reasoning_effort": "none",
            "generation_calls": 1,
            "evaluator_calls": 0,
            "automatic_retries": 0,
            "provider_timeout_seconds": 10,
            "wall_clock_timeout_seconds": 20,
        },
        "call_budget": {
            "estimated_cost_ceiling_usd": 0.1,
            "pricing_table_version": "2026-05-25",
        },
        "hash_locks": locks,
        "artifacts": {
            "output_dir": "run",
            "reader_output_path": "run/reader-output.json",
            "call_custody_path": "run/call-custody.json",
            "run_summary_path": "run/run-summary.json",
        },
        "review_after_call": {"not_passed_to_reader": True},
        "non_claims": ["not human review", "not product proof"],
    }
    contract["prompt_hashes"] = reader._prompt_hashes(contract)
    return contract


def _response() -> dict:
    return {
        "source_decision_state": "unresolved outcome",
        "source_vs_prior_assistant_claims": [
            {"item": "ceiling", "status": "source fact", "basis": "user said it"}
        ],
        "stage_a_reconstruction": "captured and produced pressure",
        "pressure_reconstruction": [
            {
                "pressure": "check evidence",
                "origin": "receipt",
                "status": "considered",
                "consequence": "verify",
                "limits": "not proof",
            }
        ],
        "paired_experiment_reconstruction": {
            "control": "baseline",
            "treatment": "pressure",
            "difference": "process",
            "limits": "one case",
        },
        "graph_reconstruction": {
            "v1_issue": "omission",
            "v2_repair": "complete surface",
            "current_read": "unproven",
            "limits": "no causal claim",
        },
        "custody_vs_quality": "custody is not quality",
        "supported_claims": ["execution happened"],
        "claims_not_supported": ["better decisions"],
        "current_authorizations": {
            "allowed": "review",
            "blocked": "integration",
            "human_status": "not reviewed",
            "next_gate": "receipt",
        },
        "uncertainties": ["outcome"],
        "human_questions": ["is it useful"],
        "reconstruction_failures_or_ambiguities": [],
    }


def test_contract_freezes_single_call_and_prompt_hashes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    contract = _fixture(tmp_path, monkeypatch)
    reader.validate_contract(contract)
    assert contract["call_configuration"]["generation_calls"] == 1
    assert contract["call_configuration"]["automatic_retries"] == 0


def test_typed_reader_response_is_enforced(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    contract = _fixture(tmp_path, monkeypatch)
    assert reader._validate_response(_response(), contract) == []
    broken = _response()
    broken["graph_reconstruction"].pop("limits")
    assert "graph_reconstruction object shape invalid" in reader._validate_response(
        broken, contract
    )


def test_one_call_run_preserves_custody_and_operability(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    contract = _fixture(tmp_path, monkeypatch)

    def fake_call(_: object) -> dict:
        return {
            "call_attempted": True,
            "requested_model": "openai/gpt-5.1-chat",
            "status": "ok",
            "response": _response(),
            "validation_errors": [],
            "served_model": "openai/gpt-5.1-chat-20251113",
            "model_attribution_status": "served_version_alias",
            "prompt_tokens": 1000,
            "completion_tokens": 500,
            "total_tokens": 1500,
            "reasoning_tokens": 0,
            "usage_evidence_state": "complete",
            "duration_seconds": 1.0,
        }

    output, custody, summary = reader.run_reader(contract, call_fn=fake_call)
    assert output["status"] == "ok"
    assert custody["recorded_call_count"] == 1
    assert summary["status"] == "passed"
    assert summary["estimated_cost_usd"] is not None


def test_receipt_hash_drift_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    contract = _fixture(tmp_path, monkeypatch)
    (tmp_path / "receipt.md").write_text("drift", encoding="utf-8")
    with pytest.raises(reader.ReaderContractError, match="receipt hash mismatch"):
        reader.validate_contract(contract)
