from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from engine.system_b.simulated_reliability_v1 import (
    SimulatedReliabilityError,
    compile_pressure_response,
)


ROOT = Path(__file__).resolve().parents[1]
BUILDER_PATH = (
    ROOT / "scripts/evals/build_consumer_context_case_freeze_candidate.py"
)
VALIDATOR_PATH = (
    ROOT / "scripts/evals/validate_consumer_context_case_freeze_candidate.py"
)
OUTPUT = (
    ROOT
    / "research/consumer-context-role-attribution-case-candidate-2026-07-23"
)


def _load_builder():
    spec = importlib.util.spec_from_file_location(
        "consumer_context_case_builder",
        BUILDER_PATH,
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load(relative: str) -> dict:
    return json.loads((OUTPUT / relative).read_text(encoding="utf-8"))


def test_case_candidate_validates_from_cli() -> None:
    completed = subprocess.run(
        [sys.executable, str(VALIDATOR_PATH)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout) == {
        "blocked_preview_count": 1,
        "case_id": "phase5-independent-useful-retailer-pilot",
        "complete_provider_neutral_preview_count": 5,
        "execution_ready": False,
        "mechanical_gates_pass": True,
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
        "request_preview_count": 6,
        "schema_version": (
            "lolla.consumer_context_role_attribution_case_candidate.v1"
        ),
        "status": "valid",
    }


def test_case_candidate_reuses_current_policy_and_preserves_bijection() -> None:
    manifest = _load("manifest.json")
    receipts = _load("custody-receipts.json")

    assert manifest["current_graph_projection"]["direct_active_model_ids"] == [
        "signaling",
        "social-proof",
    ]
    assert manifest["current_graph_projection"]["graph_active_model_ids"] == [
        "confirmation-bias",
        "incentives",
        "abstraction",
    ]
    assert manifest["current_graph_projection"]["direction"] == (
        "outgoing_authored_relations"
    )
    assert manifest["current_graph_projection"]["hop_depth"] == 1
    assert manifest["current_graph_projection"]["policy_changed"] is False
    bijection = receipts["active_candidate_to_presented_payload_bijection"]
    assert bijection["passed"] is True
    assert bijection["planner_active_pressure_ids"] == bijection[
        "presented_pressure_ids"
    ]
    assert bijection["missing"] == []
    assert bijection["extra"] == []
    assert bijection["duplicate_presented_ids"] == []


def test_case_candidate_preserves_required_byte_identities() -> None:
    builder = _load_builder()
    components = _load("pressure-components.json")
    receipts = _load("custody-receipts.json")
    f2 = _load(
        "request-previews/"
        "f2_fresh_human_controlled_fact_free_direct_only.json"
    )
    f3 = _load(
        "request-previews/"
        "f3_fresh_human_controlled_fact_free_plus_current_graph.json"
    )
    t3 = _load(
        "request-previews/"
        "t3_trajectory_continuation_human_controlled_plus_current_graph.json"
    )

    assert receipts["f2_f3_direct_component_identity"]["passed"] is True
    assert receipts["f3_t3_pressure_presentation_identity"]["passed"] is True
    assert components["direct_component"]["canonical_json"] in (
        components["presentations"]["direct_only"]["text"]
    )
    assert components["direct_component"]["canonical_json"] in (
        components["presentations"]["complete"]["text"]
    )
    assert f2["injection"]["pressure_block_sha256"] != f3["injection"][
        "pressure_block_sha256"
    ]
    assert f3["injection"]["pressure_block_sha256"] == t3["injection"][
        "pressure_block_sha256"
    ]
    assert f3["injection"]["final_instruction_sha256"] == t3["injection"][
        "final_instruction_sha256"
    ]

    f0 = _load("request-previews/f0_fresh_transcript_only.json")
    t0 = _load("request-previews/t0_trajectory_continuation_transcript_only.json")
    assert f0["request_body_projection"]["messages"][0] == t0[
        "request_body_projection"
    ]["messages"][0]
    assert f3["request_body_projection"]["messages"][0] == t3[
        "request_body_projection"
    ]["messages"][0]
    for preview in (f0, f2, f3, t0, t3):
        system_prompt = preview["request_body_projection"]["messages"][0]["content"]
        assert system_prompt.startswith("You are a reconsidering reasoner.")
        assert "fresh-context reasoner" not in system_prompt

    bundle = _load("portfolio-bundle.json")
    pressure_cases = (
        (f2, "direct_pressure"),
        (f3, "graph_expanded_pressure"),
        (t3, "graph_expanded_pressure"),
    )
    for preview, arm_id in pressure_cases:
        packet = bundle["arms"][arm_id]["packet"]
        expected_ids = [
            row["model_id"] for row in packet["pressure_portfolio"]
        ]
        validation = preview["response_validation"]
        dispositions = preview["request_body_projection"]["response_schema"][
            "properties"
        ]["candidate_dispositions"]
        constrained_ids = [
            constraint["contains"]["properties"]["model_id"]["const"]
            for constraint in dispositions["allOf"]
        ]
        assert validation["validator_owner"] == (
            builder.PRESSURE_RESPONSE_VALIDATOR_OWNER
        )
        assert validation["expected_model_ids"] == expected_ids
        assert constrained_ids == expected_ids
        assert all(
            constraint["minContains"] == constraint["maxContains"] == 1
            for constraint in dispositions["allOf"]
        )

    packet = bundle["arms"]["direct_pressure"]["packet"]
    expected_ids = [row["model_id"] for row in packet["pressure_portfolio"]]
    valid_rows = [
        {
            "model_id": model_id,
            "disposition": "reject",
            "source_turn_numbers": [1],
            "effect": "no_material_effect",
            "strongest_plausible_application": "A plausible application.",
            "disposition_reason": "The source does not support using it.",
            "risk_if_forced": "It would manufacture leverage.",
            "reopen_condition": "Reopen if new source evidence appears.",
        }
        for model_id in expected_ids
    ]

    def compile_rows(rows: list[dict]) -> None:
        compile_pressure_response(
            response={
                "candidate_dispositions": rows,
                "reconsidered_answer": "Preserve the source-grounded answer.",
                "change_summary": "No material change.",
            },
            packet=packet,
        )

    compile_rows(valid_rows)
    invalid_rows = (
        valid_rows[:-1],
        [valid_rows[0], {**valid_rows[-1], "model_id": valid_rows[0]["model_id"]}],
        [valid_rows[0], {**valid_rows[-1], "model_id": "unexpected-model"}],
    )
    for rows in invalid_rows:
        with pytest.raises(SimulatedReliabilityError):
            compile_rows(rows)


def test_case_candidate_keeps_f1_human_and_provider_gates_missing() -> None:
    manifest = _load("manifest.json")
    readiness = _load("readiness.json")
    target = _load("principal-human-target-template.json")
    f1 = _load(
        "request-previews/"
        "f1_fresh_current_live_bridge_plus_current_graph.json"
    )

    assert manifest["evidence_class"].startswith(
        "retrospective_mechanism_replay"
    )
    assert manifest["reference_condition_candidate"][
        "principal_human_authority_established"
    ] is False
    assert f1["status"] == (
        "blocked_missing_current_live_semantic_bridge_supply"
    )
    assert f1["provider_request_eligible"] is False
    assert f1["request_body_projection"]["response_schema"] is None
    assert target["status"] == "missing_principal_human_source_first_target"
    assert target["principal_human_fields_filled_by_builder"] is False
    assert readiness["execution_ready"] is False
    assert {
        row["id"] for row in readiness["blocking_prerequisites"]
    } == {
        "principal_human_source_first_target",
        "principal_human_reference_condition_approval",
        "f1_current_live_semantic_bridge_supply",
        "exact_provider_model_interface_and_generation_contract",
        "provider_call_and_usd_ceiling_authorization",
        "provider_token_counts_and_request_cost_estimate",
    }
    assert readiness["provider_calls"] == 0
    assert readiness["runtime_change"] is False
    assert readiness["graph_policy_change"] is False


def test_case_candidate_rebuild_detects_artifact_drift(tmp_path: Path) -> None:
    builder = _load_builder()
    root_copy = tmp_path / "repo"
    shutil.copytree(
        ROOT,
        root_copy,
        ignore=shutil.ignore_patterns(".git", "node_modules", "__pycache__"),
    )
    drifted = (
        root_copy
        / builder.OUTPUT_RELATIVE
        / "request-previews/f3_fresh_human_controlled_fact_free_plus_current_graph.json"
    )
    drifted.write_text(drifted.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    errors, receipt = builder.validate_checked_in(root=root_copy)

    assert receipt["status"] == "invalid"
    assert any("artifact drifted" in error for error in errors)
