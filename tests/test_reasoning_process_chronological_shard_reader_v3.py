from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from engine.system_b.reasoning_process_chronological_shard_reader_v2 import (
    build_shard_prompts_v2,
    shard_response_schema_v2,
)
from engine.system_b.reasoning_process_chronological_shard_reader_v3 import (
    POSITION_FORCE_LABELS,
    QUALIFICATION_MODALITY_LABELS,
    build_shard_prompts_v3,
    compile_shard_response_recordwise_v3,
    shard_response_schema_v3,
    validate_shard_record_v3,
)
from engine.system_b.reasoning_process_view_specific import ViewSpecificInterfaceError
from scripts.evals.run_reasoning_process_modal_strength_v3_probe import (
    validate_authorization as validate_probe_authorization,
    validate_contract as validate_probe_contract,
)
from scripts.evals.run_reasoning_process_phase4_transfer import _job_material

ROOT = Path(__file__).resolve().parents[1]
V3_ROOT = ROOT / "research/reasoning-process-modal-strength-v3-2026-07-12"
PACKET_ROOT = ROOT / "research/reasoning-process-chronological-shards-2026-07-11/cases"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _wrapper(case_id: str, view: str, shard: str = "shard-01.json") -> dict:
    return _load(PACKET_ROOT / case_id / view / shard)


def _position_fixture(case_id: str) -> dict:
    return _load(
        V3_ROOT
        / "protected-fixtures"
        / case_id
        / "position_and_decision_trajectory.json"
    )


def test_v3_changes_only_the_position_interface() -> None:
    report = _load(V3_ROOT / "report.json")
    assert report["summary"]["non_position_schema_unchanged"] is True
    assert report["summary"]["non_position_prompt_unchanged"] is True
    assert report["summary"]["position_schema_changed"] is True
    assert report["summary"]["position_prompt_changed"] is True
    for case in report["cases"]:
        for artifact in case["artifacts"]:
            wrapper = _load(ROOT / artifact["packet_path"])
            if artifact["view_kind"] == "position_and_decision_trajectory":
                continue
            assert shard_response_schema_v3(artifact["view_kind"]) == shard_response_schema_v2(
                artifact["view_kind"]
            )
            assert build_shard_prompts_v3(wrapper) == build_shard_prompts_v2(wrapper)


def test_position_schema_exposes_categorical_force_without_a_score() -> None:
    schema = shard_response_schema_v3("position_and_decision_trajectory")
    properties = schema["properties"]["records"]["items"]["properties"]
    assert properties["starting_position_force"]["enum"] == list(POSITION_FORCE_LABELS)
    assert properties["current_position_force"]["enum"] == list(POSITION_FORCE_LABELS[:-1])
    assert properties["qualification_modalities"]["items"]["enum"] == list(
        QUALIFICATION_MODALITY_LABELS
    )
    serialized = json.dumps(schema).lower()
    assert '"score"' not in serialized
    assert '"confidence"' not in serialized


def test_all_twenty_reviewed_fixtures_compile_under_v3() -> None:
    report = _load(V3_ROOT / "report.json")
    assert report["summary"]["protected_fixture_count"] == 20
    assert report["summary"]["protected_admitted_record_count"] == 20
    assert report["summary"]["protected_quarantined_record_count"] == 0
    assert report["decision"]["provider_free_modal_strength_gate"] == "pass"
    for case in report["cases"]:
        for artifact in case["artifacts"]:
            if artifact["protected_fixture_path"]:
                fixture = _load(ROOT / artifact["protected_fixture_path"])
                assert fixture["compiled"]["shard_terminal_disposition"] == "compiled"


def test_case03_reviewed_fixture_repairs_force_inflation_without_mutating_v2() -> None:
    v3_record = _position_fixture("amb1-case03-creative-partnership")["response"]["records"][0]
    v2_record = _load(
        ROOT
        / "research/reasoning-process-chronological-shard-role-explicit-v2-2026-07-12"
        / "protected-fixtures/amb1-case03-creative-partnership/position_and_decision_trajectory.json"
    )["response"]["records"][0]
    assert v2_record["trajectory_interpretation"].startswith("The user moves from demanding")
    assert v3_record["trajectory_interpretation"].startswith("The user moves from stating")
    assert v3_record["starting_position_force"] == "preference_or_desire"
    assert v3_record["current_position_force"] == "provisional_plan"
    assert v3_record["qualification_modalities"] == ["possibility", "unresolved_question"]


def test_case05_preserves_preference_and_leaning_without_prompt_mutation() -> None:
    fixture = _position_fixture("amb1-case05-family-archive")
    record = fixture["response"]["records"][0]
    assert record["starting_position_force"] == "preference_or_desire"
    assert record["current_position_force"] == "leaning"
    report = _load(V3_ROOT / "report.json")
    assert report["boundary"]["completed_case05_prompt_changed"] is False


def test_missing_force_fields_are_rejected() -> None:
    fixture = _position_fixture("amb1-case03-creative-partnership")
    wrapper = _wrapper("amb1-case03-creative-partnership", "position_and_decision_trajectory")
    record = copy.deepcopy(fixture["response"]["records"][0])
    record.pop("current_position_force")
    with pytest.raises(ViewSpecificInterfaceError, match="force fields are missing"):
        validate_shard_record_v3(record, wrapper=wrapper)


def test_starting_not_applicable_must_match_starting_role_presence() -> None:
    fixture = _position_fixture("amb1-case03-creative-partnership")
    wrapper = _wrapper("amb1-case03-creative-partnership", "position_and_decision_trajectory")
    record = copy.deepcopy(fixture["response"]["records"][0])
    record["starting_position_force"] = "not_applicable"
    with pytest.raises(ViewSpecificInterfaceError, match="cannot be not_applicable"):
        validate_shard_record_v3(record, wrapper=wrapper)


@pytest.mark.parametrize(
    "modalities",
    [[], ["possibility", "possibility"], ["certainty"], ["possibility"] * 4],
)
def test_invalid_qualification_modalities_are_rejected(modalities: list[str]) -> None:
    fixture = _position_fixture("amb1-case03-creative-partnership")
    wrapper = _wrapper("amb1-case03-creative-partnership", "position_and_decision_trajectory")
    record = copy.deepcopy(fixture["response"]["records"][0])
    record["qualification_modalities"] = modalities
    with pytest.raises(ViewSpecificInterfaceError, match="qualification modalities are invalid"):
        validate_shard_record_v3(record, wrapper=wrapper)


def test_semantically_wrong_but_enum_valid_force_is_source_review_not_code_inference() -> None:
    fixture = _position_fixture("amb1-case03-creative-partnership")
    wrapper = _wrapper("amb1-case03-creative-partnership", "position_and_decision_trajectory")
    response = copy.deepcopy(fixture["response"])
    response["records"][0]["current_position_force"] = "commitment"
    compiled = compile_shard_response_recordwise_v3(
        response=response,
        wrapper=wrapper,
        producer_kind="adversarial_fixture",
        producer_id="semantic-error-remains-visible-to-source-review",
        record_identity="wrong-force-valid-shape",
    )
    assert compiled["shard_terminal_disposition"] == "compiled"
    assert compiled["observations"][0]["source_force"]["current_position_force"] == "commitment"
    assert compiled["boundary"]["source_force_correctness_inferred_by_code"] is False
    assert compiled["boundary"]["force_labels_compared_or_scored_by_code"] is False
    assert compiled["boundary"]["prose_keyword_gate_added"] is False


def test_record_level_custody_quarantines_only_the_malformed_sibling() -> None:
    fixture = _position_fixture("amb1-case03-creative-partnership")
    wrapper = _wrapper("amb1-case03-creative-partnership", "position_and_decision_trajectory")
    valid = copy.deepcopy(fixture["response"]["records"][0])
    malformed = copy.deepcopy(valid)
    malformed["qualification_modalities"] = []
    compiled = compile_shard_response_recordwise_v3(
        response={
            "status": "mixed",
            "records": [valid, malformed],
            "global_limitations": "Adversarial sibling-custody fixture.",
        },
        wrapper=wrapper,
        producer_kind="adversarial_fixture",
        producer_id="recordwise-custody",
        record_identity="mixed-siblings",
    )
    assert compiled["shard_terminal_disposition"] == "partially_compiled"
    assert [item["terminal_state"] for item in compiled["records"]] == [
        "admitted",
        "quarantined",
    ]
    assert len(compiled["observations"]) == 1


def test_fresh_case_selection_is_mechanical_and_excludes_completed_position_calls() -> None:
    selection = _load(V3_ROOT / "report.json")["fresh_case_selection"]
    assert selection["rule"] == "ascending_sha256_of_case_id_take_first"
    assert selection["selected_case_id"] == "amb1-case03-creative-partnership"
    assert selection["selection_was_semantic"] is False
    assert "amb1-case05-family-archive" in selection["excluded_completed_position_cases"]


def test_frozen_fresh_probe_contract_authorization_and_generic_runner_material() -> None:
    contract_path = (
        ROOT / "research/reasoning-process-modal-strength-v3-probe-2026-07-12/contract.json"
    )
    contract = _load(contract_path)
    validation = validate_probe_contract(contract, contract_path)
    assert validation["provider_calls_made"] == 0
    validate_probe_authorization(
        _load(
            ROOT
            / "research/reasoning-process-modal-strength-v3-probe-2026-07-12/authorization.json"
        ),
        contract=contract,
        contract_path=contract_path,
    )
    wrapper, prompts, schema = _job_material(contract["job"])
    assert wrapper["packet"]["case_id"] == "amb1-case03-creative-partnership"
    assert prompts["user_prompt_sha256"] == contract["job"]["user_prompt_sha256"]
    assert schema["properties"]["records"]["items"]["properties"][
        "current_position_force"
    ]["enum"] == list(POSITION_FORCE_LABELS[:-1])


def test_one_call_result_is_preserved_and_source_review_blocks_integration() -> None:
    root = ROOT / "research/reasoning-process-modal-strength-v3-probe-2026-07-12"
    result = _load(root / "result.json")
    call = result["call"]
    assert result["provider_request_count"] == 1
    assert call["operational_status"] == "ok"
    assert call["typed_status"] == "admitted"
    assert call["admitted_record_count"] == 2
    assert call["quarantined_record_count"] == 0
    assert call["automatic_retries"] == 0
    assert call["fallback_models"] == 0
    assert call["evaluator_calls"] == 0
    assert call["embedding_calls"] == 0
    assert call["graph_calls"] == 0
    assert call["runtime_calls"] == 0
    review = _load(root / "source-review.json")
    assert review["gate_results"]["overall_semantic_gate"] == "fail"
    assert review["protected_target_review"]["status"] == "not_present_in_either_record"
    assert review["decision"]["modal_strength_v3_ready_for_integration"] is False
    assert review["decision"]["same_case_repair_or_retry_authorized"] is False
    assert review["decision"]["additional_provider_calls_authorized"] is False
