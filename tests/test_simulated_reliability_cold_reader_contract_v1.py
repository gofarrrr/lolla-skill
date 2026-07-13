from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs/evals/simulated-reliability-v1-cold-reader-contract-v1.json"


def test_cold_reader_sample_is_hash_locked_and_spans_success_and_failure() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert contract["status"] == "frozen_after_t1_before_any_cold_reader_review"
    assert contract["execution_policy"]["provider_calls_authorized"] == 0
    assert contract["response_contract"]["scalar_score"] is None
    assert contract["response_contract"]["winner_label"] is None

    reasons = set()
    for row in contract["sample"]:
        path = ROOT / row["receipt_markdown_path"]
        assert path.is_file()
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row["receipt_markdown_sha256"]
        reasons.add(row["reason_for_selection"])

    assert len(contract["sample"]) == 4
    assert any("false stand-down" in reason for reason in reasons)
    assert any("correct stand-down" in reason for reason in reasons)
    assert any("role extraction" in reason for reason in reasons)
    assert any("credit" in reason for reason in reasons)


def test_cold_reader_contract_keeps_custody_separate_from_quality() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    forbidden = set(contract["reader_context"]["withheld"])
    assert "diagnostic source review" in forbidden
    assert "expected answer" in forbidden
    assert contract["review_axes"]["custody_vs_quality_boundary"] == [
        "preserved",
        "inflated",
    ]
    assert "receipt_integrity_is_not_reader_comprehension" in contract["non_claims"]
