from __future__ import annotations

import json
from pathlib import Path

from scripts.evals.build_reasoning_process_phase4_transfer import (
    MODEL,
    SELECTED_CASES,
    validate_contract,
)
from scripts.evals.run_reasoning_process_phase4_transfer import (
    execute,
    validate_authorization,
)
from scripts.evals.review_reasoning_process_phase4_transfer import build_review

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "research/reasoning-process-phase4-transfer-design-2026-07-11/contract.json"
AUTHORIZATION = ROOT / "research/reasoning-process-phase4-transfer-design-2026-07-11/authorization.json"


def _contract() -> dict:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def test_phase4_contract_rebuilds_exactly_provider_free() -> None:
    result = validate_contract(_contract(), ROOT)
    assert result["status"] == "phase4_transfer_provider_free_gate_pass"
    assert result["provider_calls_made"] == 0
    assert result["calls_authorized_by_validation"] is False


def test_phase4_case_selection_is_mechanical_and_excludes_development() -> None:
    contract = _contract()
    assert SELECTED_CASES == (
        "amb1-case05-family-archive",
        "amb1-case01-product-scope",
    )
    assert contract["selection"]["selection_was_semantic"] is False
    assert contract["selection"]["development_case_excluded"] not in SELECTED_CASES


def test_phase4_has_four_full_readers_and_seven_local_windows_per_case() -> None:
    contract = _contract()
    for case_id in SELECTED_CASES:
        jobs = [item for item in contract["jobs"] if item["case_id"] == case_id]
        assert len(jobs) == 11
        assert sum(item["mechanism"] == "full_conversation_reader_v3" for item in jobs) == 4
        assert sum(item["mechanism"] == "local_exploration_v2" for item in jobs) == 7
        assert [
            item["focal_turn_index"]
            for item in jobs
            if item["mechanism"] == "local_exploration_v2"
        ] == list(range(1, 8))


def test_phase4_route_and_boundaries_do_not_drift() -> None:
    contract = _contract()
    config = contract["call_configuration"]
    assert config["provider"] == "openrouter"
    assert config["model"] == MODEL
    assert config["allow_provider_fallbacks"] is False
    assert config["automatic_retries"] == 0
    assert "openai" not in json.dumps(config).lower()
    assert contract["budget_amendment"]["amended_first_attempt_transfer_calls_max"] == 22
    assert contract["budget_amendment"]["maximum_total_provider_requests"] == 24
    assert contract["budget_amendment"]["graph_calls"] == 0
    assert contract["budget_amendment"]["runtime_calls"] == 0
    assert contract["boundary"]["stability_repeat_calls_authorized"] is False
    assert contract["boundary"]["graph_or_runtime_authorized"] is False


def test_phase4_schema_and_packet_budgets_are_bounded() -> None:
    for job in _contract()["jobs"]:
        ceiling = 24000 if job["mechanism"] == "full_conversation_reader_v3" else 8000
        assert job["input_utf8_bytes"] <= ceiling
        assert job["response_schema_metrics"]["bytes"] <= 12000
        assert job["response_schema_metrics"]["depth"] <= 8
        assert job["maximum_output_records"] in {2, 4}


def test_phase4_authorization_is_exact_and_one_shot() -> None:
    authorization = json.loads(AUTHORIZATION.read_text(encoding="utf-8"))
    validate_authorization(authorization, CONTRACT, _contract())


def test_phase4_missing_key_makes_no_provider_call(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.delenv("LOLLA_OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    result = execute(contract=_contract(), output=tmp_path / "missing-key")
    assert result["attempted_job_count"] == 1
    assert result["provider_request_count"] == 0
    assert result["stop_reason"] == "missing OpenRouter API key"


def test_phase4_eventual_mechanical_review_separates_dimension_floor_from_targets() -> None:
    run = ROOT / "research/reasoning-process-phase4-transfer-run-2026-07-11"
    retry = json.loads(
        (ROOT / "research/reasoning-process-phase4-transfer-retry-2026-07-11/result.json").read_text(encoding="utf-8")
    )
    review = build_review(_contract(), run, retry)
    assert review["summary"]["admitted_record_count"] == 52
    assert review["summary"]["critical_dimension_zero_count"] == 0
    assert review["summary"]["protected_visible_count"] == 5
    assert [item["protected_visible_count"] for item in review["cases"]] == [1, 4]
    assert all(item["critical_dimension_floor_gate"] == "pass" for item in review["cases"])
    assert all(item["protected_target_gate"] == "fail" for item in review["cases"])


def test_phase4_source_review_fires_stop_rule_without_overclaim() -> None:
    review = json.loads(
        (ROOT / "research/reasoning-process-phase4-transfer-review-2026-07-11/source-review.json").read_text(encoding="utf-8")
    )
    assert review["decision"]["phase4_transfer_gate"] == "fail"
    assert review["decision"]["stability_repeat_calls_authorized"] is False
    assert review["decision"]["completed_case_prompt_tuning_authorized"] is False
    assert review["decision"]["graph_or_runtime_authorized"] is False
    assert review["aggregate"]["critical_dimensions_with_zero_records"] == 0
    assert review["aggregate"]["protected_exact_visibility"] == "5_of_10"
    assert review["aggregate"]["same_load_bearing_failure_on_both_cases"]
    assert review["aggregate"]["source_strength_inflation_count"] == 0


def test_phase4_append_only_review_correction_preserves_frozen_original() -> None:
    correction = json.loads(
        (ROOT / "research/reasoning-process-phase4-transfer-review-2026-07-11/source-review-correction-v1.json").read_text(encoding="utf-8")
    )
    assert correction["original_source_review_sha256"] == "604aa6edc5da856290fea205026f576ead0f0463e88922f77e06ab8b6eabc88b"
    assert correction["correction"]["corrected_semantic_status"] == "supported"
    assert correction["corrected_aggregate"]["phase4_transfer_gate"] == "fail_unchanged"
    assert correction["boundary"]["original_review_changed"] is False
