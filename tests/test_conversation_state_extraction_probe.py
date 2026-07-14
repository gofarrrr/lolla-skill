from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from scripts.evals import run_conversation_state_extraction_probe as probe


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT
    / "research/conversation-state-extraction-probe-v1-2026-07-11/contract.json"
)


def _contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def _raw_from_reviewed(case: dict) -> dict:
    reviewed_path = ROOT / case["reviewed_packet_path"]
    reviewed = json.loads(reviewed_path.read_text(encoding="utf-8"))
    return {
        "schema_version": probe.RAW_OUTPUT_SCHEMA,
        "decision_summary": reviewed["decision_summary"],
        "positions": [
            {
                key: value
                for key, value in row.items()
                if key not in {"position_id", "graph_routing_eligible"}
            }
            for row in reviewed["positions"]
        ],
        "threads": [
            {
                key: value
                for key, value in row.items()
                if key not in {"thread_id", "graph_routing_eligible"}
            }
            for row in reviewed["threads"]
        ],
        "constraints": [
            {
                key: value
                for key, value in row.items()
                if key not in {"constraint_id", "graph_routing_eligible"}
            }
            for row in reviewed["constraints"]
        ],
    }


def _completed_review(contract: dict) -> dict:
    case_results = [
        {
            "case_id": case["case_id"],
            "status": "ok",
            "sealed_packet_path": f"research/fake/{case['case_id']}.json",
            "custody_violation_count": 0,
        }
        for case in contract["cases"]
    ]
    review = probe.build_source_review_shell(contract, case_results=case_results)
    review["status"] = "completed_source_first_review"
    review["review_sequence_attestation"] = {
        key: True for key in review["review_sequence_attestation"]
    }
    for case, row in zip(contract["cases"], review["cases"], strict=True):
        axes = row["axes"]
        axes["position_ownership"].update(
            status="reviewed", observed=case["expected_position_ownership"]
        )
        axes["thread_disposition"].update(
            status="reviewed", observed=case["expected_thread_disposition"]
        )
        axes["source_strength"].update(
            status="reviewed", material_strengthening_breaches=0
        )
        axes["constraint_coverage"].update(
            status="reviewed",
            matched_constraint_count=case["reviewed_constraint_count"],
            precision=1.0,
            recall=1.0,
        )
        axes["late_turn_trajectory"].update(
            status="reviewed",
            user_turn_7_represented=True,
            assistant_turn_7_represented=True,
        )
    return review


def test_checked_in_contract_and_prompt_hashes_are_frozen() -> None:
    contract = _contract()
    probe.validate_contract(contract)
    assert probe.prompt_hashes(contract) == contract["prompt_hashes"]
    assert contract["call_budget"]["maximum_provider_calls"] == 2
    assert contract["call_configuration"]["automatic_retries"] == 0
    assert contract["call_configuration"]["graph_calls"] == 0


def test_reviewed_packet_can_be_sealed_as_unreviewed_probe_output() -> None:
    contract = _contract()
    case = contract["cases"][0]
    packet, violations = probe.seal_raw_response(
        _raw_from_reviewed(case), case=case
    )
    assert violations == []
    assert packet["status"] == "model_probe_unreviewed"
    assert packet["routing_boundary"]["direct_graph_routing_allowed"] is False
    assert all(not row["graph_routing_eligible"] for row in packet["constraints"])


def test_authorization_is_separate_one_time_hash_bound_artifact() -> None:
    contract = _contract()
    authorization = {
        "schema_version": probe.AUTHORIZATION_SCHEMA,
        "status": "authorized_once",
        "contract_path": str(CONTRACT_PATH.relative_to(ROOT)),
        "contract_sha256": probe._hash_file(CONTRACT_PATH),
        "run_id": contract["run_id"],
        "maximum_provider_calls": 2,
        "automatic_retries": 0,
        "pipeline_calls": 0,
        "graph_calls": 0,
    }
    probe.validate_authorization(
        authorization, contract_path=CONTRACT_PATH, contract=contract
    )
    authorization["contract_sha256"] = "0" * 64
    with pytest.raises(probe.ConversationStateProbeError, match="hash mismatch"):
        probe.validate_authorization(
            authorization, contract_path=CONTRACT_PATH, contract=contract
        )


def test_provider_finish_error_is_preserved_and_never_sealed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contract = _contract()
    monkeypatch.setenv("LOLLA_OPENROUTER_API_KEY", "test-only")

    class FakeResponse:
        def __enter__(self) -> "FakeResponse":
            return self

        def __exit__(self, *_args: object) -> None:
            return None

        def read(self) -> bytes:
            return json.dumps(
                {
                    "model": contract["call_configuration"]["model"],
                    "choices": [
                        {
                            "finish_reason": "error",
                            "message": {"content": "partial provider output"},
                        }
                    ],
                    "usage": {
                        "prompt_tokens": 10,
                        "completion_tokens": 1,
                        "total_tokens": 11,
                    },
                }
            ).encode("utf-8")

    monkeypatch.setattr(probe.request, "urlopen", lambda *_args, **_kwargs: FakeResponse())
    result = probe._call_openrouter(contract, contract["cases"][0])
    assert result["status"] == "provider_finish_error"
    assert result["sealed_packet"] == {}
    assert "provider returned finish_reason=error" in result["validation_errors"]
    assert result["raw_provider_content_included"] is False


def test_source_first_review_seals_axes_without_composite_score() -> None:
    contract = _contract()
    result = probe.seal_source_review(contract, _completed_review(contract))
    assert result["status"] == "passed"
    assert result["composite_score"] is None
    assert result["aggregate_decision"]["full_pipeline_authorized"] is False
    assert result["aggregate_decision"]["graph_calls_authorized"] is False


def test_source_first_review_exposes_failed_axis_without_hiding_it() -> None:
    contract = _contract()
    review = _completed_review(contract)
    review["cases"][1]["axes"]["source_strength"][
        "material_strengthening_breaches"
    ] = 1
    result = probe.seal_source_review(contract, review)
    assert result["status"] == "failed"
    assert result["aggregate_decision"]["failed_axes"] == ["source_strength"]
    assert result["cases"][1]["failed_axes"] == ["source_strength"]
