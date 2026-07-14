from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from scripts.evals import build_case06_reasoning_run_receipt_v2 as builder
from scripts.evals import run_frozen_cold_reader as cold_reader
from scripts.evals.validate_reasoning_run_receipt_v2 import (
    validate_reasoning_run_receipt,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research/gate7-case06-receipt-v2-2026-07-10"


def _json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def test_repaired_contract_rebuilds_frozen_receipt_exactly() -> None:
    contract = PACKAGE / "receipt-contract-repaired.json"
    repaired, base, paths = builder._validate_contracts(contract)
    rebuilt = builder.build_receipt(repaired=repaired, base=base, paths=paths)
    observed = _json(PACKAGE / "receipt.json")
    assert rebuilt == observed
    assert builder.render_markdown(rebuilt) == (PACKAGE / "receipt.md").read_text(
        encoding="utf-8"
    )
    assert validate_reasoning_run_receipt(observed)["status"] == "cross_field_valid"


def test_receipt_preserves_exact_source_and_pair_payloads() -> None:
    receipt = _json(PACKAGE / "receipt.json")
    source = (ROOT / "research/test-cases/case_friendship_money_conversation.txt").read_text(
        encoding="utf-8"
    )
    blind = _json(
        ROOT
        / "research/core-development-batches-2026-07-10/batch2-stage-b/blind-outputs.json"
    )
    assert receipt["complete_conversation"] == source
    assert len(receipt["source_index"]) == 20
    exact = receipt["comparison_evidence"]["anonymous_outputs"]
    assert [row["response"] for row in exact] == [
        row["response"] for row in blind["outputs"]
    ]
    assert receipt["comparison_evidence"]["reveal_mapping"] == [
        {"blind_label": "A", "arm_id": "strong_reconsideration_control"},
        {"blind_label": "B", "arm_id": "lolla_pressure_treatment"},
    ]


def test_receipt_keeps_semantic_hearing_separate_from_identity_and_effect_failure() -> None:
    pressure = _json(PACKAGE / "receipt.json")["pressure_accountability"][0]
    assert pressure["pressure_id"] == "batch2-edge-empathy-confirm-before-diagnosis"
    assert pressure["observed_consumer_pressure_id"] == "confirmable-empathy-lens"
    assert pressure["identity_status"] == "mismatch"
    assert pressure["semantic_hearing_status"] == "substantive"
    assert pressure["consumer_disposition"] == "private_guardrail"
    assert pressure["effect_consistency_status"] == "inconsistent"
    assert pressure["origin"] == "v60_affordance"
    assert pressure["graph_pressure_ids"] == []


def test_receipt_reports_partial_tokens_and_unknown_graph_exposure_honestly() -> None:
    receipt = _json(PACKAGE / "receipt.json")
    operability = receipt["operability"]
    graph = receipt["graph_attribution"]
    assert operability["total_tokens"] == 6587
    assert operability["token_evidence_state"] == "partial"
    assert "Stage B" in operability["token_scope"]
    assert graph["exposure_status"] == "unknown"
    assert graph["exact_lineage_status"] == "none"
    assert graph["causal_contribution_status"] == "not_tested"


def test_stopped_application_and_reader_boundary_remain_visible() -> None:
    audit = _json(PACKAGE / "v2-application-audit.json")
    receipt = _json(PACKAGE / "receipt.json")
    assert audit["status"] == "stopped_before_receipt_assembly_contract_insufficient"
    assert audit["receipt_written"] is False
    assert receipt["authorization_snapshot"]["authorizations"]["reader_call"] is False
    assert receipt["authorization_snapshot"]["authorizations"]["pipeline_rerun"] is False
    assert "reader_call" in receipt["authorization_snapshot"][
        "future_events_not_covered"
    ]


def test_receipt_hashes_are_stable() -> None:
    assert _hash(PACKAGE / "receipt.json") == (
        "193e243be80bc29e65c14f7175a61dbf1755abc8b9f0de860e61de433cd63d5a"
    )
    assert _hash(PACKAGE / "receipt.md") == (
        "fddd7d5dfd3d2c39cc853250322ddca73207912925750d9e090300c64011c0b2"
    )


def test_reader_contract_and_single_call_custody_are_frozen() -> None:
    contract = _json(PACKAGE / "reader-contract.json")
    summary = _json(
        PACKAGE / "run/lolla_gate7_case06_reader_20260710_a1/run-summary.json"
    )
    assert contract["prompt_hashes"] == cold_reader._prompt_hashes(contract)
    assert contract["call_configuration"]["generation_calls"] == 1
    assert contract["call_configuration"]["automatic_retries"] == 0
    assert contract["call_configuration"]["evaluator_calls"] == 0
    assert summary["status"] == "passed"
    assert summary["call_count"] == 1
    assert summary["experiment_retries"] == 0
    assert summary["evaluator_calls"] == 0
    assert summary["contract_sha256"] == _hash(PACKAGE / "reader-contract.json")
    assert all(summary["gates"].values())


def test_reader_preserves_accountability_without_answer_or_graph_overclaim() -> None:
    output = _json(
        PACKAGE / "run/lolla_gate7_case06_reader_20260710_a1/reader-output.json"
    )["reconstruction"]
    pressure = output["pressure_reconstruction"][0]
    assert pressure["expected_pressure_id"] == (
        "batch2-edge-empathy-confirm-before-diagnosis"
    )
    assert pressure["observed_pressure_id"] == "confirmable-empathy-lens"
    assert pressure["identity_status"] == "mismatch"
    assert pressure["semantic_hearing_status"] == "substantive"
    assert pressure["disposition"] == "private_guardrail"
    assert pressure["effect_consistency"] == "inconsistent"
    assert output["paired_experiment_reconstruction"]["public_difference"].startswith(
        "None material"
    )
    assert output["graph_reconstruction"]["exposure"] == "unknown"
    assert output["graph_reconstruction"]["causal_read"] == "not tested"
    assert "do not establish correctness" in output["custody_vs_quality"]


def test_source_first_review_preserves_reader_losses_instead_of_retuning() -> None:
    review = _json(PACKAGE / "source-first-review.json")
    dimensions = {row["dimension"]: row for row in review["dimension_review"]}
    assert review["status"] == "complete_partial_transfer_pass"
    assert dimensions["source-end action and deadline"]["status"] == "partial"
    assert dimensions["source-end reasoning and prior-assistant claims"][
        "status"
    ] == "partial"
    assert dimensions["graph scope and lineage"]["status"] == "partial"
    assert dimensions["pressure accountability"]["status"] == "passed"
    assert dimensions["custody versus quality"]["status"] == "passed"
    assert review["overall_read"]["agent_transfer"] == (
        "partial_pass_stronger_than_case10"
    )


def test_post_reader_state_does_not_rewrite_receipt_snapshot() -> None:
    receipt = _json(PACKAGE / "receipt.json")
    status = _json(PACKAGE / "post-reader-status.json")
    assert receipt["authorization_snapshot"]["authorizations"]["reader_call"] is False
    assert status["receipt_snapshot_relation"][
        "receipt_snapshot_remains_valid_as_of_its_freeze"
    ] is True
    assert status["receipt_snapshot_relation"][
        "receipt_snapshot_is_not_current_authorization_state"
    ] is True
    assert status["completed_after_receipt_freeze"]["reader_call_completed"] is True
    assert status["current_authorizations"]["receipt_retune_after_reader"] is False


def test_reader_artifact_hashes_are_stable() -> None:
    assert _hash(PACKAGE / "reader-contract.json") == (
        "5aba8a85b4bcce86e6a76b4b4f8a3c2c614477ad35f9d299fcb123eb914c571c"
    )
    assert _hash(
        PACKAGE / "run/lolla_gate7_case06_reader_20260710_a1/reader-output.json"
    ) == "d2f838ae4aa639e8348dfda88723dc067be87ad7629747d5c8fc27213cba38d8"
    assert _hash(
        PACKAGE / "run/lolla_gate7_case06_reader_20260710_a1/call-custody.json"
    ) == "416680c90a0721a47201f25a98daa22a2e132123cca4ded21c201e510e4399d4"
    assert _hash(
        PACKAGE / "run/lolla_gate7_case06_reader_20260710_a1/run-summary.json"
    ) == "5e0cbae0af7b0d9ab46088db96b2c68b7ca9e5e86d35b96730864657e150f0ad"
