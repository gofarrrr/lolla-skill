from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from engine.system_b.reasoning_process_chronological_shard_reader_v2 import (
    build_shard_prompts_v2,
    shard_response_schema_v2,
)
from engine.system_b.reasoning_process_chronological_shard_reader_v4 import (
    STANCE_EXPRESSION_KINDS,
    STANCE_OBJECT_KINDS,
    build_shard_prompts_v4,
    compile_shard_response_recordwise_v4,
    shard_response_schema_v4,
    validate_shard_record_v4,
)
from engine.system_b.reasoning_process_view_specific import ViewSpecificInterfaceError
from scripts.evals.run_reasoning_process_stance_object_v4_probe import (
    validate_authorization as validate_probe_authorization,
    validate_contract as validate_probe_contract,
)

ROOT = Path(__file__).resolve().parents[1]
V4_ROOT = ROOT / "research/reasoning-process-stance-object-v4-2026-07-12"
PACKET_ROOT = ROOT / "research/reasoning-process-chronological-shards-2026-07-11/cases"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _wrapper(case_id: str, view: str, shard: str = "shard-01.json") -> dict:
    return _load(PACKET_ROOT / case_id / view / shard)


def _position_fixture(case_id: str) -> dict:
    return _load(
        V4_ROOT
        / "protected-fixtures"
        / case_id
        / "position_and_decision_trajectory.json"
    )


def _components(record: dict, role: str) -> list[dict]:
    return [item for item in record["stance_components"] if item["temporal_role"] == role]


def test_v4_changes_only_the_position_interface() -> None:
    report = _load(V4_ROOT / "report.json")
    assert report["summary"]["non_position_schema_unchanged"] is True
    assert report["summary"]["non_position_prompt_unchanged"] is True
    assert report["summary"]["position_schema_changed"] is True
    assert report["summary"]["position_prompt_changed"] is True
    for case in report["cases"]:
        for artifact in case["artifacts"]:
            wrapper = _load(ROOT / artifact["packet_path"])
            if artifact["view_kind"] == "position_and_decision_trajectory":
                continue
            assert shard_response_schema_v4(artifact["view_kind"]) == shard_response_schema_v2(
                artifact["view_kind"]
            )
            assert build_shard_prompts_v4(wrapper) == build_shard_prompts_v2(wrapper)


def test_v4_schema_is_one_bounded_component_array_without_score_fields() -> None:
    schema = shard_response_schema_v4("position_and_decision_trajectory")
    properties = schema["properties"]["records"]["items"]["properties"]
    assert "stance_components" in properties
    assert "starting_position_force" not in properties
    assert "current_position_force" not in properties
    assert properties["stance_components"]["minItems"] == 2
    assert properties["stance_components"]["maxItems"] == 10
    component = properties["stance_components"]["items"]["properties"]
    assert component["stance_object_kind"]["enum"] == list(STANCE_OBJECT_KINDS)
    assert component["stance_expression_kind"]["enum"] == list(STANCE_EXPRESSION_KINDS)
    assert component["temporal_role"]["enum"] == ["starting", "current", "qualification"]
    serialized = json.dumps(schema).lower()
    assert '"score"' not in serialized
    assert '"confidence"' not in serialized
    assert '"oneof"' not in serialized


def test_all_twenty_reviewed_fixtures_compile_under_v4() -> None:
    report = _load(V4_ROOT / "report.json")
    assert report["summary"]["protected_fixture_count"] == 20
    assert report["summary"]["protected_admitted_record_count"] == 20
    assert report["summary"]["protected_quarantined_record_count"] == 0
    assert report["decision"]["provider_free_stance_object_gate"] == "pass"
    assert report["summary"]["maximum_response_schema_bytes"] < 5000
    for case in report["cases"]:
        for artifact in case["artifacts"]:
            if artifact["protected_fixture_path"]:
                fixture = _load(ROOT / artifact["protected_fixture_path"])
                assert fixture["compiled"]["shard_terminal_disposition"] == "compiled"


def test_case03_assessment_is_not_encoded_as_a_decision() -> None:
    record = _position_fixture("amb1-case03-creative-partnership")["response"]["records"][0]
    starting = _components(record, "starting")
    assert starting == [
        {
            "temporal_role": "starting",
            "stance_object_kind": "belief_or_assessment",
            "stance_object_interpretation": "The final third needs a major re-edit.",
            "stance_expression_kind": "held_assessment",
            "source_evidence_ids": ["e004"],
        }
    ]
    assert all(item["stance_expression_kind"] != "decision" for item in starting)


def test_case04_distinguishes_reported_landscape_from_user_actions() -> None:
    record = _position_fixture("amb1-case04-research-tool-release")["response"]["records"][0]
    starting = _components(record, "starting")
    current = _components(record, "current")
    assert starting[0]["stance_object_kind"] == "reported_position_landscape"
    assert starting[0]["stance_expression_kind"] == "reported_without_endorsement"
    assert [item["stance_expression_kind"] for item in current] == [
        "leaning",
        "provisional_intention_or_plan",
    ]


def test_missing_stance_object_fields_are_rejected() -> None:
    fixture = _position_fixture("amb1-case04-research-tool-release")
    wrapper = _wrapper("amb1-case04-research-tool-release", "position_and_decision_trajectory")
    record = copy.deepcopy(fixture["response"]["records"][0])
    record.pop("stance_components")
    with pytest.raises(ViewSpecificInterfaceError, match="stance-object fields are missing"):
        validate_shard_record_v4(record, wrapper=wrapper)


def test_starting_components_must_match_starting_role_presence() -> None:
    fixture = _position_fixture("amb1-case04-research-tool-release")
    wrapper = _wrapper("amb1-case04-research-tool-release", "position_and_decision_trajectory")
    record = copy.deepcopy(fixture["response"]["records"][0])
    record["stance_components"] = _components(record, "current") + _components(
        record, "qualification"
    )
    with pytest.raises(ViewSpecificInterfaceError, match="starting components"):
        validate_shard_record_v4(record, wrapper=wrapper)


@pytest.mark.parametrize("removed_role", ["current", "qualification"])
def test_current_and_qualification_components_are_required(removed_role: str) -> None:
    fixture = _position_fixture("amb1-case04-research-tool-release")
    wrapper = _wrapper("amb1-case04-research-tool-release", "position_and_decision_trajectory")
    record = copy.deepcopy(fixture["response"]["records"][0])
    record["stance_components"] = [
        item for item in record["stance_components"] if item["temporal_role"] != removed_role
    ]
    with pytest.raises(ViewSpecificInterfaceError, match=f"{removed_role} stance component count"):
        validate_shard_record_v4(record, wrapper=wrapper)


def test_component_evidence_must_be_a_parent_role_subset() -> None:
    fixture = _position_fixture("amb1-case04-research-tool-release")
    wrapper = _wrapper("amb1-case04-research-tool-release", "position_and_decision_trajectory")
    record = copy.deepcopy(fixture["response"]["records"][0])
    _components(record, "current")[0]["source_evidence_ids"] = ["e064"]
    with pytest.raises(ViewSpecificInterfaceError, match="parent-role subset"):
        validate_shard_record_v4(record, wrapper=wrapper)


def test_exact_duplicate_components_are_rejected_without_semantic_merge() -> None:
    fixture = _position_fixture("amb1-case04-research-tool-release")
    wrapper = _wrapper("amb1-case04-research-tool-release", "position_and_decision_trajectory")
    record = copy.deepcopy(fixture["response"]["records"][0])
    record["stance_components"].append(copy.deepcopy(record["stance_components"][0]))
    with pytest.raises(ViewSpecificInterfaceError, match="exactly duplicates"):
        validate_shard_record_v4(record, wrapper=wrapper)


def test_enum_valid_but_wrong_belief_decision_pair_remains_source_reviewable() -> None:
    fixture = _position_fixture("amb1-case03-creative-partnership")
    wrapper = _wrapper("amb1-case03-creative-partnership", "position_and_decision_trajectory")
    response = copy.deepcopy(fixture["response"])
    response["records"][0]["stance_components"][0]["stance_expression_kind"] = "decision"
    compiled = compile_shard_response_recordwise_v4(
        response=response,
        wrapper=wrapper,
        producer_kind="adversarial_fixture",
        producer_id="wrong-pair-remains-visible-to-source-review",
        record_identity="wrong-object-expression-pair",
    )
    assert compiled["shard_terminal_disposition"] == "compiled"
    assert compiled["observations"][0]["stance_objects"]["stance_components"][0][
        "stance_expression_kind"
    ] == "decision"
    assert compiled["boundary"]["object_expression_compatibility_gate_added"] is False
    assert compiled["boundary"]["stance_expression_correctness_inferred_by_code"] is False
    assert compiled["boundary"]["prose_keyword_gate_added"] is False


def test_mixed_proposal_and_acceptance_sentence_is_representable_as_two_objects() -> None:
    failed = _load(
        ROOT / "research/reasoning-process-modal-strength-v3-probe-2026-07-12/result.json"
    )["call"]["candidate_payload"]["records"][1]
    wrapper = _wrapper("amb1-case03-creative-partnership", "position_and_decision_trajectory")
    record = {key: value for key, value in failed.items() if key not in {
        "starting_position_force",
        "current_position_force",
        "qualification_modalities",
        "strength_fidelity_note",
    }}
    record["stance_components"] = [
        {
            "temporal_role": "starting",
            "stance_object_kind": "reported_position_landscape",
            "stance_object_interpretation": "The collaborators were avoiding the credit conversation.",
            "stance_expression_kind": "reported_without_endorsement",
            "source_evidence_ids": ["e006"],
        },
        {
            "temporal_role": "current",
            "stance_object_kind": "action_or_proposal",
            "stance_object_interpretation": "Propose equal top-line authorship with detailed role credits.",
            "stance_expression_kind": "provisional_intention_or_plan",
            "source_evidence_ids": ["e065"],
        },
        {
            "temporal_role": "current",
            "stance_object_kind": "acceptance_or_willingness",
            "stance_object_interpretation": "Accept the credit arrangement if structural authority remains unequal.",
            "stance_expression_kind": "conditional_willingness",
            "source_evidence_ids": ["e065"],
        },
        {
            "temporal_role": "qualification",
            "stance_object_kind": "belief_or_assessment",
            "stance_object_interpretation": "Current-film credit may not be separable from future collaboration rules.",
            "stance_expression_kind": "uncertain_or_undecided",
            "source_evidence_ids": ["e066"],
        },
    ]
    record["stance_object_fidelity_note"] = (
        "The proposal action and willingness to accept its outcome are distinct objects."
    )
    validated = validate_shard_record_v4(record, wrapper=wrapper)
    current = [
        item
        for item in validated["stance_objects"]["stance_components"]
        if item["temporal_role"] == "current"
    ]
    assert [item["stance_object_kind"] for item in current] == [
        "action_or_proposal",
        "acceptance_or_willingness",
    ]


def test_record_level_custody_preserves_valid_sibling() -> None:
    fixture = _position_fixture("amb1-case04-research-tool-release")
    wrapper = _wrapper("amb1-case04-research-tool-release", "position_and_decision_trajectory")
    valid = copy.deepcopy(fixture["response"]["records"][0])
    invalid = copy.deepcopy(valid)
    invalid["stance_components"][0]["source_evidence_ids"] = ["e064"]
    compiled = compile_shard_response_recordwise_v4(
        response={
            "status": "mixed",
            "records": [valid, invalid],
            "global_limitations": "Adversarial recordwise custody fixture.",
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


def test_case04_is_the_only_fresh_position_candidate() -> None:
    selection = _load(V4_ROOT / "report.json")["fresh_case_selection"]
    assert selection["selected_case_id"] == "amb1-case04-research-tool-release"
    assert selection["selection_was_semantic"] is False
    assert selection["excluded_completed_position_cases"] == [
        "amb1-case01-product-scope",
        "amb1-case02-nonprofit-scale",
        "amb1-case03-creative-partnership",
        "amb1-case05-family-archive",
    ]


def test_frozen_case04_probe_contract_and_authorization_validate_without_calls() -> None:
    root = ROOT / "research/reasoning-process-stance-object-v4-probe-2026-07-12"
    contract_path = root / "contract.json"
    contract = _load(contract_path)
    validation = validate_probe_contract(contract, contract_path)
    assert validation["provider_calls_made"] == 0
    validate_probe_authorization(
        _load(root / "authorization.json"),
        contract=contract,
        contract_path=contract_path,
    )


def test_case04_operational_failure_is_preserved_without_semantic_claims() -> None:
    root = ROOT / "research/reasoning-process-stance-object-v4-probe-2026-07-12"
    result = _load(root / "result.json")
    call = result["call"]
    assert result["provider_request_count"] == 1
    assert call["operational_status"] == "http_error_400"
    assert call["http_status"] == 400
    assert call["typed_status"] == "not_observed"
    assert call["provider_calls"] == 1
    assert call["automatic_retries"] == 0
    assert call["fallback_models"] == 0
    assert "candidate_payload" not in call
    assert "compiled" not in call
    review = _load(root / "operational-review.json")
    assert review["gate_results"]["operational_provider_gate"] == "fail"
    assert review["gate_results"]["semantic_stance_object_gate"] == "not_observed"
    assert review["decision"]["stance_object_v4_ready_for_integration"] is False
    assert review["decision"]["case04_repair_or_retry_authorized"] is False
    assert review["provider_free_compatibility_audit"]["exact_invalid_argument_identified"] is False
