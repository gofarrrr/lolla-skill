from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from scripts.evals import build_case10_reasoning_receipt as receipt_builder
from scripts.evals import run_frozen_cold_reader as reader


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research/gate7-case10-cold-reader-2026-07-10"


def _json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def test_frozen_receipt_rebuilds_exactly_from_hash_locked_inputs() -> None:
    contract = _json(PACKAGE / "receipt-contract.json")
    paths = receipt_builder.validate_contract(contract, root=ROOT)
    rebuilt = receipt_builder.build_receipt(contract, paths=paths)
    observed = _json(PACKAGE / "receipt.json")
    assert rebuilt == observed
    assert receipt_builder.render_markdown(rebuilt) == (
        PACKAGE / "receipt.md"
    ).read_text(encoding="utf-8")


def test_receipt_contains_exact_source_and_blind_before_reveal_custody() -> None:
    receipt = _json(PACKAGE / "receipt.json")
    source = (ROOT / "research/test-cases/case_real_estate_conversation.txt").read_text(
        encoding="utf-8"
    )
    assert receipt["complete_conversation"] == source
    stage_b = receipt["stage_b"]
    assert [row["blind_label"] for row in stage_b["anonymous_outputs"]] == ["A", "B"]
    assert stage_b["blind_review_before_key"]["status"] == "sealed_before_arm_key"
    assert stage_b["reveal_mapping"] == {
        "A": "lolla_pressure_treatment",
        "B": "strong_reconsideration_control",
    }


def test_reader_contract_and_post_call_review_references_are_hash_valid() -> None:
    contract = _json(PACKAGE / "reader-contract.json")
    reader.validate_contract(contract)
    review = _json(PACKAGE / "source-first-review.json")
    for source in review["sources"].values():
        path = ROOT / source["path"]
        assert path.is_file()
        assert _hash(path) == source["sha256"]
    assert review["mechanical_execution"]["generation_calls"] == 1
    assert review["mechanical_execution"]["automatic_retries"] == 0
    assert review["mechanical_execution"]["evaluator_calls"] == 0


def test_gate7_decision_does_not_promote_partial_transfer() -> None:
    decision = _json(PACKAGE / "decision.json")
    assert decision["gate_7_read"]["fresh_agent_reconstruction"] == "partial_pass"
    assert decision["gate_7_read"]["human_reconstruction"] == "pending"
    assert decision["gate_7_read"]["full_gate_7_complete"] is False
    assert decision["authorizations"]["gate_8_runtime_integration"] is False
    assert decision["authorizations"]["retune_completed_case10"] is False
