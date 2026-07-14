from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_single_window_probe_recovers_repeatedly_missed_pair() -> None:
    call = _load(
        ROOT / "research/reasoning-process-exploration-local-probe-2026-07-11/call.json"
    )
    assert call["operational_status"] == "ok"
    assert call["typed_status"] == "admitted"
    record = next(
        item
        for item in call["candidate_payload"]["records"]
        if item["alternative_evidence_ids"] == ["e026"]
    )
    assert record["attached_condition_or_limit_evidence_ids"] == ["e027"]
    assert "not cover all the ownership" in record[
        "attached_condition_or_limit_interpretation"
    ]


def test_record_level_replay_preserves_failure_and_valid_sibling() -> None:
    replay = _load(
        ROOT
        / "research/reasoning-process-exploration-local-case02-replay-2026-07-11/replay-report.json"
    )
    assert replay["status"] == "record_level_custody_replay_complete"
    assert replay["summary"]["operational_success_count"] == 6
    assert replay["summary"]["operational_failure_count"] == 1
    assert replay["summary"]["admitted_record_count"] == 11
    assert replay["summary"]["quarantined_record_count"] == 1
    assert replay["summary"]["exact_role_alias_duplicate_count"] == 1
    turn4 = [item for item in replay["record_custody"] if item["focal_turn_index"] == 4]
    assert [item["terminal_state"] for item in turn4] == ["admitted", "quarantined"]
    assert turn4[1]["exact_role_alias_duplicate_of"]
    turn5 = next(item for item in replay["windows"] if item["focal_turn_index"] == 5)
    assert turn5["terminal_disposition"] == "failed_operationally"


def test_cooled_retry_keeps_original_429_immutable() -> None:
    original = (
        ROOT
        / "research/reasoning-process-exploration-local-case02-2026-07-11/calls/turn-005.json"
    )
    expected = "803666f4efc6a5c39f0a579e1393709325accd15bca71306ac7c429b6441f4e6"
    assert hashlib.sha256(original.read_bytes()).hexdigest() == expected
    retry = _load(
        ROOT
        / "research/reasoning-process-exploration-local-turn5-retry-2026-07-11/result.json"
    )
    assert retry["original_failure_sha256"] == expected
    assert retry["observed_cooloff_seconds"] >= 60
    assert retry["operational_status"] == "ok"
    assert retry["typed_status"] == "admitted"
    assert retry["boundary"]["prompt_schema_model_or_packet_changed"] is False
    assert retry["boundary"]["automatic_retry"] is False


def test_terminal_case_result_passes_without_hiding_operational_or_record_failure() -> None:
    result = _load(
        ROOT
        / "research/reasoning-process-exploration-local-terminal-2026-07-11/terminal-result.json"
    )
    assert result["status"] == "development_case_complete_local_exploration_pass"
    summary = result["summary"]
    assert summary["first_attempt_operational_success_count"] == 6
    assert summary["eventual_completed_window_count"] == 7
    assert summary["provider_request_count_including_operational_retry"] == 8
    assert summary["cooled_operational_retry_count"] == 1
    assert summary["admitted_record_count"] == 13
    assert summary["quarantined_record_count"] == 1
    assert summary["invalid_admitted_record_count"] == 0
    assert summary["estimated_cost_usd"] == 0.00698625
    assert result["decision"]["prospective_transfer_contract_may_be_designed"] is True
    assert result["decision"]["transfer_calls_authorized_by_this_result"] is False
    assert result["boundary"]["original_rate_limit_failure_preserved"] is True


def test_terminal_source_review_preserves_product_boundary() -> None:
    review = _load(
        ROOT
        / "research/reasoning-process-exploration-local-terminal-2026-07-11/source-review.json"
    )
    assert review["status"] == "development_case_source_review_pass"
    assert review["complete_case_evidence_vector"]["admitted_stable_alias_references"] == (
        "32/32"
    )
    assert review["decision"]["development_case_gate_passed"] is True
    assert review["decision"]["transfer_provider_calls_authorized"] is False
    assert review["decision"]["graph_or_runtime_authorized"] is False
