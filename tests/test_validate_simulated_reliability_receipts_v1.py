from pathlib import Path

from scripts.evals.validate_simulated_reliability_receipts_v1 import validate_one


ROOT = Path(__file__).resolve().parents[1]
RECEIPTS = ROOT / "research/simulated-reliability-v1-receipts-2026-07-13/t1"


def test_complete_receipt_integrity_passes_without_claiming_reader_success():
    case = RECEIPTS / "v1-case01-flood-infrastructure"
    result = validate_one(case / "receipt.json", case / "receipt.md")
    assert result["status"] == "integrity_pass"
    assert result["cold_reader_comprehension_tested"] is False
    assert all(result["checks"].values())


def test_failed_receipt_integrity_preserves_failure_and_passes():
    case = RECEIPTS / "v1-case09-software-migration"
    result = validate_one(case / "receipt.json", case / "receipt.md")
    assert result["status"] == "integrity_pass"
    assert result["checks"]["failure_custody"] is True
