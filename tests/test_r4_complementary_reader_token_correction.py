from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.evals import build_r4_complementary_reader_preflight as base_preflight
from scripts.evals import build_r4_complementary_reader_token_correction as builder
from scripts.evals import run_r4_complementary_reader_experiment as frozen
from scripts.evals import run_r4_complementary_reader_token_correction as runner


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs/evals/lolla-r4-complementary-reader-token-correction-contract-v1.json"
OUTPUT = ROOT / "research/lolla-r4-complementary-reader-token-correction-2026-07-14"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_provider_free_correction_rebuilds_byte_exactly() -> None:
    files = builder.build_files(OUTPUT)
    builder.validate_files(files)
    report = _load(OUTPUT / "preflight-result.json")

    assert report["status"] == (
        "provider_free_token_correction_ready_call_authorization_required"
    )
    assert report["change_contract"]["uncertainty_changed_json_paths"] == [
        "/max_tokens",
        "/reasoning/effort",
    ]
    assert report["change_contract"]["uncertainty_after"] == {
        "max_tokens": 1600,
        "reasoning_effort": "minimal",
    }
    assert report["change_contract"]["relationship_unchanged"] == {
        "max_tokens": 700,
        "reasoning_effort": "minimal",
    }
    assert report["budget"]["conservative_estimated_total_cost_usd"] == 0.0181615
    assert report["budget"]["total_cost_preflight_pass"] is True
    assert report["decision"]["provider_calls_authorized"] is False
    assert report["local_gates"]["provider_calls"] == 0


def test_frozen_contract_validates_without_authorization_or_network() -> None:
    contract = runner.validate_contract(CONTRACT)

    assert contract["run_id"] == "lolla-r4-complementary-reader-token-correction-a2"
    assert contract["task_limits"] == {
        "uncertainty": {"max_tokens": 1600, "reasoning_effort": "minimal"},
        "relationship": {"max_tokens": 700, "reasoning_effort": "minimal"},
    }
    assert contract["operator"]["model"] == "google/gemini-3.1-flash-lite"
    assert contract["operator"]["provider_slug"] == "google-vertex"
    assert contract["decision_boundary"]["provider_calls_authorized"] is False
    assert contract["decision_boundary"]["authorization_file_present"] is False


@pytest.mark.parametrize(
    "case_id",
    ["v1-case02-discharge-transport", "v1-case03-executive-hire"],
)
def test_corrected_request_diff_is_limited_to_two_allocation_paths(case_id: str) -> None:
    base_contract = _load(
        ROOT / "docs/evals/lolla-r4-complementary-reader-experiment-contract-v1.json"
    )
    base_case = next(row for row in base_contract["cases"] if row["case_id"] == case_id)
    original = _load(ROOT / base_case["uncertainty_request_preview_path"])
    corrected = _load(OUTPUT / "cases" / case_id / "uncertainty-request-preview.json")

    assert builder._diff_paths(original["body"], corrected["body"]) == [
        "/max_tokens",
        "/reasoning/effort",
    ]
    assert corrected["body"]["max_tokens"] == 1600
    assert corrected["body"]["reasoning"] == {
        "effort": "minimal",
        "exclude": True,
    }


def _packet_from_relationship_prompt(prompt: str) -> dict:
    return json.loads(
        prompt.split("EXACT-ID RECORD PACKET\n", 1)[1].split("\n\nTASK\n", 1)[0]
    )


def test_fake_four_call_path_uses_corrected_limits_and_restores_globals(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    contract = runner.validate_contract(CONTRACT)
    observed = []
    original_tasks = json.loads(json.dumps(base_preflight.TASKS))

    def relative(path: Path) -> str:
        try:
            return str(path.resolve().relative_to(ROOT))
        except ValueError:
            return str(path.resolve())

    monkeypatch.setattr(frozen, "_relative", relative)

    def fake_call(*, output, ordinal, case_id, task, preview, contract):
        body = preview["body"]
        observed.append((case_id, task, body["max_tokens"], body["reasoning"]))
        if task == "uncertainty":
            suffix = (
                "uncertainty-positive.json"
                if case_id == "v1-case02-discharge-transport"
                else "uncertainty-zero.json"
            )
            candidate = _load(
                ROOT
                / "tests/fixtures/r4_complementary_readers"
                / f"{case_id}-{suffix}"
            )
        else:
            packet = _packet_from_relationship_prompt(body["messages"][1]["content"])
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

    monkeypatch.setattr(frozen, "_provider_call", fake_call)
    result = runner.run(contract, output=tmp_path / "fake-run")

    assert result["provider_calls"] == 4
    assert result["provider_reported_cost_usd"] == 0.004
    assert observed == [
        (
            "v1-case02-discharge-transport",
            "uncertainty",
            1600,
            {"effort": "minimal", "exclude": True},
        ),
        (
            "v1-case02-discharge-transport",
            "relationship",
            700,
            {"effort": "minimal", "exclude": True},
        ),
        (
            "v1-case03-executive-hire",
            "uncertainty",
            1600,
            {"effort": "minimal", "exclude": True},
        ),
        (
            "v1-case03-executive-hire",
            "relationship",
            700,
            {"effort": "minimal", "exclude": True},
        ),
    ]
    assert base_preflight.TASKS == original_tasks


def test_new_authorization_is_exact_and_cannot_expand_scope(
    tmp_path: Path,
) -> None:
    contract = runner.validate_contract(CONTRACT)
    expected = {
        "schema_version": runner.AUTH_SCHEMA,
        "status": "authorized_once_after_provider_free_token_correction",
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
        runner.R4TokenCorrectionRunError, match="authorization drifted"
    ):
        runner.validate_authorization(path, contract=contract, contract_path=CONTRACT)
