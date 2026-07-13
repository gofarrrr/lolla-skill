from __future__ import annotations

import json
from pathlib import Path

from scripts.evals import build_r4_complementary_reader_preflight as builder
from scripts.evals import run_r4_complementary_reader_experiment as runner


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "docs/evals/lolla-r4-complementary-reader-experiment-contract-v1.json"
PREFLIGHT = ROOT / "research/lolla-r4-complementary-reader-preflight-2026-07-13"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_preflight_rebuild_is_byte_exact_and_call_free() -> None:
    files = builder.build_files(PREFLIGHT)
    builder._validate_files(files)
    report = _load(PREFLIGHT / "preflight-result.json")
    assert report["status"] == "provider_free_preflight_pass_call_authorization_required"
    assert report["local_gates"]["provider_calls"] == 0
    assert report["budget"]["maximum_provider_calls"] == 4
    assert report["budget"]["conservative_estimated_total_cost_usd"] == 0.0160615
    assert report["budget"]["maximum_provider_reported_cost_total_usd"] == 0.03
    assert report["decision"]["provider_calls_authorized"] is False


def test_frozen_contract_validates_without_authorization_or_network() -> None:
    contract = runner._validate_contract(CONTRACT_PATH)
    assert contract["decision_boundary"]["provider_calls_authorized"] is False
    assert contract["decision_boundary"]["authorization_file_present"] is False
    assert contract["operator"]["model"] == "google/gemini-3.1-flash-lite"
    assert contract["operator"]["provider_slug"] == "google-vertex"
    assert contract["task_limits"] == {
        "uncertainty": {"max_tokens": 900, "reasoning_effort": "low"},
        "relationship": {"max_tokens": 700, "reasoning_effort": "minimal"},
    }


def _packet_from_relationship_prompt(prompt: str) -> dict:
    prefix = "EXACT-ID RECORD PACKET\n"
    suffix = "\n\nTASK\n"
    return json.loads(prompt.split(prefix, 1)[1].split(suffix, 1)[0])


def test_fake_transport_exercises_dynamic_relationship_and_quiet_control(
    monkeypatch, tmp_path: Path
) -> None:
    contract = runner._validate_contract(CONTRACT_PATH)

    def relative(path: Path) -> str:
        try:
            return str(path.resolve().relative_to(ROOT))
        except ValueError:
            return str(path.resolve())

    monkeypatch.setattr(runner, "_relative", relative)

    def fake_call(*, output, ordinal, case_id, task, preview, contract):
        if task == "uncertainty":
            suffix = (
                "uncertainty-positive.json"
                if case_id == "v1-case02-discharge-transport"
                else "uncertainty-zero.json"
            )
            candidate = _load(
                ROOT / "tests/fixtures/r4_complementary_readers" / f"{case_id}-{suffix}"
            )
        else:
            packet = _packet_from_relationship_prompt(
                preview["body"]["messages"][1]["content"]
            )
            if case_id == "v1-case03-executive-hire":
                candidate = {
                    "outcome": "no_supported_record_observed",
                    "records": [],
                    "global_limitations": "Quiet structural fake.",
                }
            else:
                by_surface = {
                    row["surface"]: row["record_id"] for row in packet["record_catalog"]
                }
                candidate = {
                    "outcome": "records_present",
                    "records": [
                        {
                            "support": "supported",
                            "related_record_ids": [
                                by_surface["current_position"],
                                by_surface["unresolved_matter"],
                                by_surface["reopen_condition"],
                            ],
                            "relationship": "The bounded position is limited by the unresolved and reopening records.",
                            "evidence_ids": ["e032", "e048", "e094", "e098"],
                            "limitations": "Fake transport only.",
                        }
                    ],
                    "global_limitations": "Fake transport only.",
                }
        result = {
            "operational_status": "candidate_parsed",
            "provider_calls": 1,
            "served_model": "google/gemini-3.1-flash-lite",
            "served_provider": "Google",
            "operator_attribution_ok": True,
            "provider_reported_cost_usd": 0.001,
            "candidate": candidate,
        }
        runner._write(output / f"call-{ordinal:02d}-{task}-result.json", result)
        return result

    monkeypatch.setattr(runner, "_provider_call", fake_call)
    result = runner.run(contract, output=tmp_path / "fake-run")
    assert result["provider_calls"] == 4
    assert result["provider_reported_cost_usd"] == 0.004
    assert result["cost_ceiling_met"] is True
    target, control = result["cases"]
    assert target["reader_state_counts"] == {
        "complete": 5,
        "completed_zero": 1,
        "partial": 0,
        "failed": 0,
        "missing": 0,
    }
    assert control["reader_state_counts"] == {
        "complete": 2,
        "completed_zero": 4,
        "partial": 0,
        "failed": 0,
        "missing": 0,
    }
    assert control["record_count"] == 2


def test_authorization_shape_is_exact_and_cannot_expand_scope(tmp_path: Path) -> None:
    contract = runner._validate_contract(CONTRACT_PATH)
    expected = {
        "schema_version": runner.AUTH_SCHEMA,
        "status": "authorized_once_after_provider_free_preflight",
        "contract_path": str(CONTRACT_PATH.relative_to(ROOT)),
        "contract_sha256": runner._file_sha(CONTRACT_PATH),
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
    runner._validate_authorization(path, contract=contract, contract_path=CONTRACT_PATH)
    expected["maximum_provider_calls"] = 5
    path.write_text(json.dumps(expected), encoding="utf-8")
    try:
        runner._validate_authorization(path, contract=contract, contract_path=CONTRACT_PATH)
    except runner.R4ExperimentError as exc:
        assert "authorization drifted" in str(exc)
    else:
        raise AssertionError("expanded authorization unexpectedly validated")
