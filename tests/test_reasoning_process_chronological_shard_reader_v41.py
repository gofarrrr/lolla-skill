from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from engine.system_b.reasoning_process_chronological_shard_reader_v2 import (
    build_shard_prompts_v2,
    shard_response_schema_v2,
)
from engine.system_b.reasoning_process_chronological_shard_reader_v41 import (
    build_shard_prompts_v41,
    compile_shard_response_recordwise_v41,
    shard_response_schema_v41,
    validate_shard_record_v41,
)
from engine.system_b.reasoning_process_contracts import schema_metrics
from engine.system_b.reasoning_process_view_specific import ViewSpecificInterfaceError
from scripts.evals.run_reasoning_process_stance_object_v41_probe import (
    validate_authorization as validate_probe_authorization,
    validate_contract as validate_probe_contract,
)

ROOT = Path(__file__).resolve().parents[1]
V41_ROOT = ROOT / "research/reasoning-process-stance-object-v41-2026-07-12"
FRESH_ROOT = ROOT / "research/reasoning-process-stance-object-v41-fresh-corpus-2026-07-12"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _fresh_wrapper(case_id: str) -> dict:
    return _load(FRESH_ROOT / "packets" / case_id / "position-endpoint.json")


def _fresh_fixture(case_id: str) -> dict:
    return _load(V41_ROOT / "fresh-protected-fixtures" / f"{case_id}.json")


def _components(record: dict) -> list[dict]:
    return [
        {
            "temporal_role": role,
            "stance_object_kind": object_kind,
            "stance_object_interpretation": interpretation,
            "stance_expression_kind": expression_kind,
            "source_evidence_id": evidence_id,
        }
        for role, object_kind, interpretation, expression_kind, evidence_id in zip(
            record["stance_temporal_roles"],
            record["stance_object_kinds"],
            record["stance_object_interpretations"],
            record["stance_expression_kinds"],
            record["stance_source_evidence_ids"],
            strict=True,
        )
    ]


def test_v41_schema_hits_shallow_compatibility_target() -> None:
    schema = shard_response_schema_v41("position_and_decision_trajectory")
    metrics = schema_metrics(schema)
    assert metrics["bytes"] == 3654
    assert metrics["depth"] == 9
    properties = schema["properties"]["records"]["items"]["properties"]
    assert "stance_components" not in properties
    for field in (
        "stance_temporal_roles",
        "stance_object_kinds",
        "stance_object_interpretations",
        "stance_expression_kinds",
        "stance_source_evidence_ids",
    ):
        assert properties[field]["type"] == "array"
        assert properties[field]["items"]["type"] == "string"
        assert properties[field]["minItems"] == 2
        assert properties[field]["maxItems"] == 13
    new_fields = {
        field: properties[field]
        for field in properties
        if field.startswith("stance_")
    }
    serialized = json.dumps(new_fields)
    for forbidden in ("oneOf", "anyOf", "allOf", "$ref", "$defs", "pattern", "uniqueItems"):
        assert f'"{forbidden}"' not in serialized


def test_v41_leaves_every_non_position_interface_unchanged() -> None:
    report = _load(V41_ROOT / "report.json")
    assert report["summary"]["non_position_prompt_and_schema_unchanged"] is True
    for case in report["legacy_cases"]:
        for artifact in case["artifacts"]:
            if artifact["view_kind"] == "position_and_decision_trajectory":
                continue
            wrapper = _load(ROOT / artifact["packet_path"])
            assert shard_response_schema_v41(artifact["view_kind"]) == shard_response_schema_v2(
                artifact["view_kind"]
            )
            assert build_shard_prompts_v41(wrapper) == build_shard_prompts_v2(wrapper)


def test_all_legacy_and_fresh_reviewed_fixtures_compile() -> None:
    report = _load(V41_ROOT / "report.json")
    summary = report["summary"]
    assert summary["legacy_protected_fixture_count"] == 20
    assert summary["fresh_protected_fixture_count"] == 3
    assert summary["protected_admitted_record_count"] == 23
    assert summary["protected_quarantined_record_count"] == 0
    assert report["decision"]["provider_free_stance_object_v41_gate"] == "pass"
    assert report["decision"]["documented_subset_compatibility_gate"] == "pass"


def test_fresh_corpus_is_three_complete_target_blind_conversations() -> None:
    report = _load(FRESH_ROOT / "report.json")
    assert report["summary"]["case_count"] == 3
    assert report["summary"]["conversation_messages_per_case"] == 14
    assert report["boundary"]["protected_targets_included_in_packets"] is False
    assert report["boundary"]["source_review_fixtures_included_in_packets"] is False
    for case in report["cases"]:
        wrapper = _load(ROOT / case["packet_path"])
        assert wrapper["packet"]["focal_turn_indices"] == [1, 7]
        assert wrapper["packet"]["boundary"]["protected_target_included"] is False
        assert wrapper["packet"]["boundary"]["source_review_fixture_included"] is False


def test_fresh_case_selection_is_mechanical_and_predeclared() -> None:
    selection = _load(FRESH_ROOT / "report.json")["selection"]
    assert selection["rule"] == "ascending_sha256_of_case_id_take_first_after_all_cases_are_frozen"
    assert selection["selected_case_id"] == "amb2-case01-career-transition"
    assert selection["selection_was_semantic"] is False
    assert [item["case_id"] for item in selection["eligible_case_ranking"]] == [
        "amb2-case01-career-transition",
        "amb2-case02-community-space",
        "amb2-case03-agency-acquisition",
    ]


def test_compiler_reconstructs_normal_component_objects_from_columns() -> None:
    fixture = _fresh_fixture("amb2-case01-career-transition")
    record = fixture["response"]["records"][0]
    compiled_components = fixture["compiled"]["observations"][0]["stance_objects"][
        "stance_components"
    ]
    assert compiled_components == _components(record)
    assert all(isinstance(item["source_evidence_id"], str) for item in compiled_components)


def test_unequal_stance_column_lengths_are_rejected() -> None:
    fixture = _fresh_fixture("amb2-case01-career-transition")
    wrapper = _fresh_wrapper("amb2-case01-career-transition")
    record = copy.deepcopy(fixture["response"]["records"][0])
    record["stance_expression_kinds"].pop()
    with pytest.raises(ViewSpecificInterfaceError, match="equal bounded lengths"):
        validate_shard_record_v41(record, wrapper=wrapper)


def test_component_alias_must_belong_to_its_parent_role() -> None:
    fixture = _fresh_fixture("amb2-case01-career-transition")
    wrapper = _fresh_wrapper("amb2-case01-career-transition")
    record = copy.deepcopy(fixture["response"]["records"][0])
    record["stance_source_evidence_ids"][2] = "e061"
    with pytest.raises(ViewSpecificInterfaceError, match="one parent-role alias"):
        validate_shard_record_v41(record, wrapper=wrapper)


def test_starting_components_move_with_starting_role_presence() -> None:
    fixture = _fresh_fixture("amb2-case01-career-transition")
    wrapper = _fresh_wrapper("amb2-case01-career-transition")
    record = copy.deepcopy(fixture["response"]["records"][0])
    keep = [role != "starting" for role in record["stance_temporal_roles"]]
    for field in (
        "stance_temporal_roles",
        "stance_object_kinds",
        "stance_object_interpretations",
        "stance_expression_kinds",
        "stance_source_evidence_ids",
    ):
        record[field] = [value for value, include in zip(record[field], keep, strict=True) if include]
    with pytest.raises(ViewSpecificInterfaceError, match="starting components"):
        validate_shard_record_v41(record, wrapper=wrapper)


def test_exact_duplicate_atomic_components_are_rejected() -> None:
    fixture = _fresh_fixture("amb2-case01-career-transition")
    wrapper = _fresh_wrapper("amb2-case01-career-transition")
    record = copy.deepcopy(fixture["response"]["records"][0])
    for field in (
        "stance_temporal_roles",
        "stance_object_kinds",
        "stance_object_interpretations",
        "stance_expression_kinds",
        "stance_source_evidence_ids",
    ):
        record[field].append(record[field][0])
    with pytest.raises(ViewSpecificInterfaceError, match="exactly duplicates"):
        validate_shard_record_v41(record, wrapper=wrapper)


def test_enum_valid_but_wrong_semantic_pair_remains_source_reviewable() -> None:
    fixture = _fresh_fixture("amb2-case01-career-transition")
    wrapper = _fresh_wrapper("amb2-case01-career-transition")
    response = copy.deepcopy(fixture["response"])
    response["records"][0]["stance_expression_kinds"][0] = "decision"
    compiled = compile_shard_response_recordwise_v41(
        response=response,
        wrapper=wrapper,
        producer_kind="adversarial_fixture",
        producer_id="semantic-error-remains-visible",
        record_identity="wrong-belief-decision-pair",
    )
    assert compiled["shard_terminal_disposition"] == "compiled"
    components = compiled["observations"][0]["stance_objects"]["stance_components"]
    assert components[0]["stance_expression_kind"] == "decision"
    assert compiled["boundary"]["object_expression_compatibility_gate_added"] is False
    assert compiled["boundary"]["stance_expression_correctness_inferred_by_code"] is False


def test_equal_length_but_semantically_permuted_column_remains_source_reviewable() -> None:
    fixture = _fresh_fixture("amb2-case01-career-transition")
    wrapper = _fresh_wrapper("amb2-case01-career-transition")
    response = copy.deepcopy(fixture["response"])
    expressions = response["records"][0]["stance_expression_kinds"]
    expressions[2], expressions[4] = expressions[4], expressions[2]
    compiled = compile_shard_response_recordwise_v41(
        response=response,
        wrapper=wrapper,
        producer_kind="adversarial_fixture",
        producer_id="semantic-column-alignment-remains-source-reviewable",
        record_identity="permuted-expression-column",
    )
    assert compiled["shard_terminal_disposition"] == "compiled"
    assert compiled["boundary"]["stance_expression_correctness_inferred_by_code"] is False
    assert compiled["boundary"]["object_expression_compatibility_gate_added"] is False


def test_fresh_cases_encode_action_acceptance_and_qualification_separately() -> None:
    for case_id in (
        "amb2-case01-career-transition",
        "amb2-case02-community-space",
        "amb2-case03-agency-acquisition",
    ):
        record = _fresh_fixture(case_id)["response"]["records"][0]
        components = _components(record)
        assert any(item["temporal_role"] == "current" for item in components)
        assert any(item["temporal_role"] == "qualification" for item in components)
        assert len({item["stance_object_kind"] for item in components}) >= 3


def test_recordwise_custody_preserves_valid_sibling() -> None:
    fixture = _fresh_fixture("amb2-case01-career-transition")
    wrapper = _fresh_wrapper("amb2-case01-career-transition")
    valid = copy.deepcopy(fixture["response"]["records"][0])
    invalid = copy.deepcopy(valid)
    invalid["stance_source_evidence_ids"][2] = "e061"
    compiled = compile_shard_response_recordwise_v41(
        response={
            "status": "mixed",
            "records": [valid, invalid],
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


def test_frozen_v41_probe_contract_and_authorization_validate_without_calls() -> None:
    root = ROOT / "research/reasoning-process-stance-object-v41-probe-2026-07-12"
    contract_path = root / "contract.json"
    contract = _load(contract_path)
    validation = validate_probe_contract(contract, contract_path)
    assert validation["provider_calls_made"] == 0
    validate_probe_authorization(
        _load(root / "authorization.json"),
        contract=contract,
        contract_path=contract_path,
    )


def test_v41_operational_failure_and_sdk_diagnosis_are_preserved() -> None:
    root = ROOT / "research/reasoning-process-stance-object-v41-probe-2026-07-12"
    result = _load(root / "result.json")
    call = result["call"]
    assert result["provider_request_count"] == 1
    assert result["semantic_review_status"] == "not_applicable_no_model_output"
    assert call["operational_status"] == "http_error_400"
    assert call["typed_status"] == "not_observed"
    assert call["provider_calls"] == 1
    assert call["automatic_retries"] == 0
    assert call["fallback_models"] == 0
    assert "candidate_payload" not in call
    assert "compiled" not in call
    diagnosis = _load(root / "compatibility-diagnosis.json")
    assert diagnosis["local_current_sdk_audit"]["sdk_version"] == "2.11.0"
    assert diagnosis["local_current_sdk_audit"]["v41_full_schema_validation"] == "fail"
    assert (
        diagnosis["local_current_sdk_audit"]["v41_schema_after_removing_only_uniqueItems"]
        == "pass"
    )
    assert diagnosis["hypothesis_update"]["inherited_unique_items_as_probable_cause"] is True
    assert diagnosis["hypothesis_update"]["root_cause_proven_at_provider"] is False
    assert diagnosis["decision"]["career_transition_retry_authorized"] is False
    assert diagnosis["decision"]["additional_provider_calls_authorized"] is False
