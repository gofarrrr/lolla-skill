import json
from pathlib import Path

from scripts.evals.build_simulated_reliability_receipts_v1 import build_receipt, markdown


ROOT = Path(__file__).resolve().parents[1]
TRANSFER = ROOT / "research/simulated-reliability-v1-transfer-2026-07-12/t1"
SOURCES = ROOT / "research/simulated-reliability-corpus-v1-2026-07-12/naturalized-transfer-sources"
CONTRACT = ROOT / "docs/evals/simulated-reliability-v1-runtime-contract-v14-transfer.json"


def receipt(case_id: str):
    return build_receipt(
        case_dir=TRANSFER / f"{case_id}-primary",
        case_id=case_id,
        source_path=SOURCES / f"{case_id}.txt",
        contract_path=CONTRACT,
    )


def test_complete_receipt_preserves_full_source_interpretation_standdown_and_cost():
    value = receipt("v1-case01-flood-infrastructure")
    assert "[Turn 12] USER:" in value["source"]["authoritative_conversation"]
    assert value["interpretation"]["joined_role_records"] is not None
    assert len(value["interpretation"]["mechanism_assessments"]) == 9
    assert value["public_arms"]["direct_pressure"]["call_required"] is False
    assert value["public_arms"]["graph_expanded_pressure"]["call_required"] is False
    assert value["public_arms"]["transcript_only"]["provider_attempted"] is True
    assert value["usage"]["provider_attempts"] == 4
    assert value["usage"]["provider_reported_cost_usd"] > 0
    assert value["failures"] == []
    assert "not_a_trust_score_or_badge" in value["non_claims"]
    rendered = markdown(value)
    assert "## Authoritative conversation" in rendered
    assert "## Controlled mechanism assessments" in rendered
    assert "quality score" not in rendered.lower()


def test_role_join_failure_receipt_preserves_partial_semantics_and_failure():
    value = receipt("v1-case06-industry-funded-lab")
    assert value["attempt_status"] == "stopped_after_role_join_failure"
    assert value["interpretation"]["joined_role_records"] is None
    assert any(item["task_id"] == "role_join" for item in value["failures"])
    assert len(value["interpretation"]["role_calls"]) == 2
    assert value["public_arms"] == {}


def test_credit_failure_receipt_preserves_provider_error_and_zero_cost():
    value = receipt("v1-case09-software-migration")
    assert value["attempt_status"] == "stopped_after_starting_failure"
    assert value["usage"]["provider_attempts"] == 1
    assert value["usage"]["provider_reported_cost_usd"] == 0
    assert value["failures"][0]["operational_status"] == "http_error_402"
    serialized = json.dumps(value["failures"][0])
    assert "more credits" in serialized
