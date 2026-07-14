from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from engine.system_b.reasoning_process_chronological_shard_reader_v41 import (
    build_shard_prompts_v41,
    shard_response_schema_v41,
    validate_shard_record_v41,
)
from engine.system_b.reasoning_process_chronological_shard_reader_v42 import (
    build_shard_prompts_v42,
    compile_shard_response_recordwise_v42,
    shard_response_schema_v42,
    validate_shard_record_v42,
)
from engine.system_b.reasoning_process_view_specific import ViewSpecificInterfaceError
from scripts.evals.run_reasoning_process_stance_object_v42_probe import (
    validate_authorization as validate_probe_authorization,
    validate_contract as validate_probe_contract,
)

ROOT = Path(__file__).resolve().parents[1]
V42_ROOT = ROOT / "research/reasoning-process-stance-object-v42-2026-07-12"
V41_ROOT = ROOT / "research/reasoning-process-stance-object-v41-2026-07-12"
FRESH_ROOT = ROOT / "research/reasoning-process-stance-object-v41-fresh-corpus-2026-07-12"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _fresh_wrapper(case_id: str) -> dict:
    return _load(FRESH_ROOT / "packets" / case_id / "position-endpoint.json")


def _v41_fresh_fixture(case_id: str) -> dict:
    return _load(V41_ROOT / "fresh-protected-fixtures" / f"{case_id}.json")


def _count_keyword(value: object, keyword: str) -> int:
    if isinstance(value, dict):
        return (1 if keyword in value else 0) + sum(
            _count_keyword(child, keyword) for child in value.values()
        )
    if isinstance(value, list):
        return sum(_count_keyword(child, keyword) for child in value)
    return 0


def _strip_unique_items(value: object) -> None:
    if isinstance(value, dict):
        value.pop("uniqueItems", None)
        for child in value.values():
            _strip_unique_items(child)
    elif isinstance(value, list):
        for child in value:
            _strip_unique_items(child)


def test_v42_position_schema_diff_is_only_unique_items_removal() -> None:
    v41 = shard_response_schema_v41("position_and_decision_trajectory")
    v42 = shard_response_schema_v42("position_and_decision_trajectory")
    assert _count_keyword(v41, "uniqueItems") == 3
    assert _count_keyword(v42, "uniqueItems") == 0
    expected = copy.deepcopy(v41)
    _strip_unique_items(expected)
    assert v42 == expected


def test_v42_prompts_and_semantic_validator_are_unchanged() -> None:
    wrapper = _fresh_wrapper("amb2-case02-community-space")
    assert build_shard_prompts_v42(wrapper) == build_shard_prompts_v41(wrapper)
    record = copy.deepcopy(_v41_fresh_fixture("amb2-case02-community-space")["response"]["records"][0])
    assert validate_shard_record_v42(record, wrapper=wrapper) == validate_shard_record_v41(
        record, wrapper=wrapper
    )


def test_v42_non_position_schema_is_byte_identical_to_v41() -> None:
    for view in (
        "evidence_and_assumption_discipline",
        "uncertainty_and_unresolved_state",
        "challenge_and_revision_response",
    ):
        assert shard_response_schema_v42(view) == shard_response_schema_v41(view)


def test_current_google_sdk_preflight_fails_v41_and_passes_v42() -> None:
    report = _load(V42_ROOT / "google-schema-preflight.json")
    assert report["status"] == "pass"
    assert report["sdk"] == {
        "package": "google-genai",
        "version": "2.11.0",
        "validator": "google.genai.types.Schema_after_process_schema",
    }
    assert report["v41"]["native_schema_status"] == "fail"
    assert report["v41"]["unique_items_keyword_count"] == 3
    assert report["v42"]["native_schema_status"] == "pass"
    assert report["v42"]["unique_items_keyword_count"] == 0
    assert report["calls"]["provider"] == 0


def test_all_twenty_three_reviewed_fixtures_replay_under_v42() -> None:
    report = _load(V42_ROOT / "report.json")
    summary = report["summary"]
    assert summary["prompt_count"] == 63
    assert summary["protected_fixture_count"] == 23
    assert summary["protected_admitted_record_count"] == 23
    assert summary["protected_quarantined_record_count"] == 0
    assert summary["all_prompts_byte_identical_to_v41"] is True
    assert summary["position_schema_change_is_only_three_unique_items_removals"] is True
    assert report["decision"]["provider_free_stance_object_v42_gate"] == "pass"
    assert report["decision"]["google_sdk_preflight_gate"] == "pass"


def test_deterministic_duplicate_evidence_validation_remains_authoritative() -> None:
    wrapper = _fresh_wrapper("amb2-case02-community-space")
    record = copy.deepcopy(_v41_fresh_fixture("amb2-case02-community-space")["response"]["records"][0])
    record["current_position_evidence_ids"] = ["e050", "e050"]
    with pytest.raises(ViewSpecificInterfaceError, match="duplicate or role-forbidden aliases"):
        validate_shard_record_v42(record, wrapper=wrapper)


def test_v42_compiler_versions_custody_without_changing_raw_record() -> None:
    wrapper = _fresh_wrapper("amb2-case02-community-space")
    response = copy.deepcopy(_v41_fresh_fixture("amb2-case02-community-space")["response"])
    compiled = compile_shard_response_recordwise_v42(
        response=response,
        wrapper=wrapper,
        producer_kind="source_reviewer",
        producer_id="v42-wire-only-test",
        record_identity="case02-v42",
    )
    assert compiled["schema_version"].endswith(".v4_2")
    assert compiled["status"] == "chronological_shard_v42_record_custody_complete"
    assert compiled["observations"][0]["schema_version"].endswith(".v4_2")
    assert compiled["observations"][0]["observation_id"].startswith("rpshardv42-")
    assert compiled["observations"][0]["raw_record"]["record"] == response["records"][0]
    assert compiled["boundary"]["provider_wire_unique_items_removed"] is True
    assert compiled["boundary"]["record_validator_changed_from_v41"] is False


def test_enum_valid_semantic_error_remains_source_reviewable_under_v42() -> None:
    wrapper = _fresh_wrapper("amb2-case02-community-space")
    response = copy.deepcopy(_v41_fresh_fixture("amb2-case02-community-space")["response"])
    response["records"][0]["stance_expression_kinds"][0] = "decision"
    compiled = compile_shard_response_recordwise_v42(
        response=response,
        wrapper=wrapper,
        producer_kind="adversarial_fixture",
        producer_id="semantic-error-remains-visible",
        record_identity="wrong-belief-decision-v42",
    )
    assert compiled["shard_terminal_disposition"] == "compiled"
    assert compiled["boundary"]["stance_expression_correctness_inferred_by_code"] is False
    assert compiled["boundary"]["semantic_contract_changed_from_v41"] is False


def test_community_space_is_mechanically_selected_from_reserved_cases() -> None:
    selection = _load(V42_ROOT / "report.json")["reserved_case_selection"]
    assert selection["selected_case_id"] == "amb2-case02-community-space"
    assert selection["selection_was_semantic"] is False
    assert [item["case_id"] for item in selection["eligible_case_ranking"]] == [
        "amb2-case02-community-space",
        "amb2-case03-agency-acquisition",
    ]
    assert "amb2-case01-career-transition" in selection["excluded_closed_position_cases"]


def test_frozen_v42_probe_contract_and_authorization_validate_without_calls() -> None:
    root = ROOT / "research/reasoning-process-stance-object-v42-probe-2026-07-12"
    contract_path = root / "contract.json"
    contract = _load(contract_path)
    validation = validate_probe_contract(contract, contract_path)
    assert validation["provider_calls_made"] == 0
    validate_probe_authorization(
        _load(root / "authorization.json"),
        contract=contract,
        contract_path=contract_path,
    )


def test_v42_probe_result_and_compatibility_stop_are_preserved() -> None:
    root = ROOT / "research/reasoning-process-stance-object-v42-probe-2026-07-12"
    result = _load(root / "result.json")
    diagnosis = _load(root / "compatibility-diagnosis.json")

    assert result["provider_request_count"] == 1
    assert result["call"]["automatic_retries"] == 0
    assert result["call"]["fallback_models"] == 0
    assert result["call"]["operational_status"] == "http_error_400"
    assert result["call"]["http_status"] == 400
    assert result["call"]["typed_status"] == "not_observed"
    assert result["semantic_review_status"] == "not_applicable_no_model_output"

    observation = diagnosis["provider_observation"]
    assert observation["provider_request_count"] == 1
    assert observation["candidate_payload_present"] is False
    assert observation["compiled_payload_present"] is False
    assert observation["model_inference_observed"] is False
    assert diagnosis["hypothesis_update"]["unique_items_as_sufficient_cause"] is False
    assert diagnosis["hypothesis_update"]["root_cause_proven_at_provider"] is False
    assert diagnosis["decision"]["community_space_retry_authorized"] is False
    assert diagnosis["decision"]["agency_acquisition_call_authorized_under_v42"] is False
    assert diagnosis["decision"]["additional_provider_calls_authorized"] is False
    assert diagnosis["decision"]["graph_or_runtime_authorized"] is False
