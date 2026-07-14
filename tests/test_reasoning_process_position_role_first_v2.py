from __future__ import annotations

import copy
import json
from pathlib import Path

from engine.system_b.reasoning_process_chronological_shard_reader_v43 import (
    shard_response_schema_v43,
)
from engine.system_b.reasoning_process_contracts import schema_metrics
from engine.system_b.reasoning_process_position_role_first_v2 import (
    ROLE_ORDER,
    build_position_relation_packet_v2,
    build_position_relation_prompts_v2,
    build_position_role_prompts_v2,
    compile_position_relation_response_v2,
    compile_position_role_response_v2,
    join_position_role_first_v2,
    position_relation_response_schema_v2,
    position_role_response_schema_v2,
)
from scripts.evals.build_reasoning_process_position_role_first_v2 import build
from scripts.evals.run_reasoning_process_position_role_first_v2_probe import (
    validate_authorization,
    validate_contract,
)
from scripts.evals.run_reasoning_process_position_role_first_v2_glm_control import (
    validate_authorization as validate_glm_authorization,
    validate_contract as validate_glm_contract,
)

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "research/reasoning-process-position-role-first-v2-2026-07-12/report.json"
FIXTURE = (
    ROOT
    / "research/reasoning-process-position-role-first-v2-2026-07-12/fixtures/amb2-case03-agency-acquisition.json"
)
NEW_CASE = (
    ROOT / "research/reasoning-process-position-role-first-v2-new-case-2026-07-12"
)
PROBE = ROOT / "research/reasoning-process-position-role-first-v2-probe-2026-07-12"
GLM_CONTROL = (
    ROOT / "research/reasoning-process-position-role-first-v2-glm-control-2026-07-12"
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _fixture() -> dict:
    return _load(FIXTURE)


def test_role_and_relation_schemas_are_smaller_than_closed_monolith() -> None:
    monolithic = schema_metrics(shard_response_schema_v43("position_and_decision_trajectory"))
    schemas = [
        *(position_role_response_schema_v2(role) for role in ROLE_ORDER),
        position_relation_response_schema_v2(),
    ]
    assert all(schema_metrics(schema)["bytes"] < monolithic["bytes"] for schema in schemas)
    serialized = json.dumps(schemas, sort_keys=True)
    assert "trajectory_type" not in serialized
    assert "uniqueItems" not in serialized


def test_provider_free_role_first_replay_covers_all_eight_reviewed_positions(
    tmp_path: Path,
) -> None:
    report = build(tmp_path / "role-first")
    assert report["status"] == "provider_free_position_role_first_pass"
    assert report["summary"]["reviewed_position_fixture_count"] == 8
    assert report["summary"]["complete_join_count"] == 8
    assert report["summary"]["admitted_role_record_count"] == 24
    assert report["summary"]["admitted_relation_record_count"] == 8
    assert report["summary"]["quarantined_record_count"] == 0
    assert report["summary"]["maximum_provider_calls_per_shard"] == 4
    assert report["summary"]["maximum_user_prompt_utf8_bytes"] <= 4017
    assert report["summary"]["provider_calls"] == 0


def test_each_role_prompt_asks_only_one_role_and_not_a_trajectory_category() -> None:
    fixture = _fixture()
    for role in ROLE_ORDER:
        packet = fixture["role_packets"][role]
        prompt = build_position_role_prompts_v2(packet)["user_prompt"]
        assert packet["role"] == role
        assert packet["boundary"]["one_semantic_role_only"] is True
        assert packet["boundary"]["trajectory_relation_requested"] is False
        assert "trajectory_type" not in prompt


def test_relation_packet_is_compact_projection_not_full_compiled_custody() -> None:
    fixture = _fixture()
    packet = build_position_relation_packet_v2(
        role_compiled_by_role=fixture["role_compiled"]
    )
    prompt = build_position_relation_prompts_v2(packet)["user_prompt"]
    record = packet["role_records"]["current"][0]
    assert set(record) == {
        "role_record_id",
        "role",
        "semantic_status",
        "role_interpretation",
        "source_evidence",
        "limitations",
    }
    assert "raw_record_sha256" not in prompt
    assert "provenance" not in prompt
    assert len(prompt.encode("utf-8")) <= 4017


def test_wrong_fixed_role_is_quarantined_without_semantic_repair() -> None:
    fixture = _fixture()
    packet = fixture["role_packets"]["current"]
    response = copy.deepcopy(fixture["role_responses"]["current"])
    response["records"][0]["role"] = "starting"
    compiled = compile_position_role_response_v2(
        response=response,
        packet=packet,
        producer_kind="fixture",
        producer_id="adversarial-test",
    )
    assert compiled["records"][0]["terminal_state"] == "quarantined"
    assert "does not match packet" in compiled["records"][0]["reason"]


def test_invisible_alias_is_quarantined_but_semantic_alias_choice_is_not_gated() -> None:
    fixture = _fixture()
    packet = fixture["role_packets"]["qualification"]
    invalid = copy.deepcopy(fixture["role_responses"]["qualification"])
    invalid["records"][0]["evidence_ids"][0] = "e999"
    compiled = compile_position_role_response_v2(
        response=invalid,
        packet=packet,
        producer_kind="fixture",
        producer_id="adversarial-test",
    )
    assert compiled["records"][0]["terminal_state"] == "quarantined"

    structurally_valid = copy.deepcopy(fixture["role_responses"]["qualification"])
    structurally_valid["records"][0]["object_kinds"][0] = "acceptance_or_willingness"
    structurally_valid["records"][0]["expression_kinds"][0] = "commitment"
    admitted = compile_position_role_response_v2(
        response=structurally_valid,
        packet=packet,
        producer_kind="fixture",
        producer_id="adversarial-test",
    )
    assert admitted["records"][0]["terminal_state"] == "admitted"
    assert admitted["boundary"]["object_expression_compatibility_gate_added"] is False


def test_relation_cannot_use_a_current_id_as_a_starting_id() -> None:
    fixture = _fixture()
    packet = fixture["relation_packet"]
    response = copy.deepcopy(fixture["relation_response"])
    response["records"][0]["starting_role_record_id"] = response["records"][0][
        "current_role_record_id"
    ]
    compiled = compile_position_relation_response_v2(
        response=response,
        packet=packet,
        producer_kind="fixture",
        producer_id="adversarial-test",
    )
    assert compiled["records"][0]["terminal_state"] == "quarantined"
    assert "starting role ID" in compiled["records"][0]["reason"]


def test_quarantined_role_record_makes_join_incomplete_not_false_complete() -> None:
    fixture = _fixture()
    roles = copy.deepcopy(fixture["role_compiled"])
    roles["starting"]["records"].append(
        {"record_index": 99, "terminal_state": "quarantined", "reason": "fixture"}
    )
    joined = join_position_role_first_v2(
        role_compiled_by_role=roles,
        relation_compiled=fixture["relation_compiled"],
    )
    assert joined["status"] == "position_role_first_join_incomplete"
    assert joined["custody"]["quarantined_role_record_count"] == 1
    assert joined["boundary"]["missing_or_quarantined_records_filled"] is False


def test_missing_relation_is_explicitly_incomplete() -> None:
    fixture = _fixture()
    joined = join_position_role_first_v2(
        role_compiled_by_role=fixture["role_compiled"],
        relation_compiled=None,
    )
    assert joined["status"] == "position_role_first_join_incomplete"
    assert joined["custody"]["relation_missing_despite_current_role"] is True
    assert joined["unreferenced_role_record_ids"]["current"]


def test_result_makes_no_automatic_extraction_or_provider_claim() -> None:
    report = _load(REPORT)
    assert report["claims"]["reviewed_semantics_are_representable"] is True
    assert report["claims"]["automatic_role_extraction_improved"] is False
    assert report["claims"]["automatic_relation_extraction_improved"] is False
    assert report["claims"]["provider_acceptance_proven"] is False
    assert report["decision"]["provider_probe_authorized"] is False


def test_new_ambiguous_case_and_source_review_target_are_frozen_before_calls() -> None:
    case = _load(NEW_CASE / "case-report.json")
    target_report = _load(NEW_CASE / "target-report.json")
    target = _load(NEW_CASE / "source-review-target.json")
    packet = _load(NEW_CASE / "position-endpoint.json")
    compiled = _load(NEW_CASE / "compiled-source-review-target.json")
    assert case["conversation_message_count"] == 14
    assert case["boundary"]["protected_target_included"] is False
    assert case["provider_calls"] == 0
    assert target["status"] == "source_reviewed_and_frozen_before_provider_execution"
    assert target["protected_target"]["evidence_id"] == "e056"
    assert target["boundary"]["included_in_provider_context"] is False
    assert target_report["status"] == "pre_execution_target_gate_pass"
    assert target_report["provider_calls"] == 0
    assert compiled["joined"]["status"] == "position_role_first_join_complete"
    assert "source-review-target" not in json.dumps(packet)


def test_new_case_probe_contract_freezes_route_target_boundary_and_budget() -> None:
    contract_path = PROBE / "contract.json"
    contract = _load(contract_path)
    validation = validate_contract(contract, contract_path)
    validate_authorization(
        _load(PROBE / "authorization.json"),
        contract=contract,
        contract_path=contract_path,
    )
    assert validation["provider_calls_made"] == 0
    assert contract["job"]["case_id"] == "amb3-case01-journalism-platform-pilot"
    assert contract["job"]["provider_slug"] == "alibaba"
    assert contract["protected_source_review"]["included_in_provider_context"] is False
    assert contract["budget"]["maximum_provider_calls"] == 4
    assert contract["budget"]["maximum_estimated_cost_usd"] == 0.01
    assert contract["boundary"]["deterministic_semantic_gate_added"] is False


def test_glm_control_keeps_contract_and_changes_only_model_operator() -> None:
    contract_path = GLM_CONTROL / "contract.json"
    contract = _load(contract_path)
    validation = validate_glm_contract(contract, contract_path)
    validate_glm_authorization(
        _load(GLM_CONTROL / "authorization.json"),
        contract=contract,
        contract_path=contract_path,
    )
    deepseek = _load(PROBE / "contract.json")
    assert validation["provider_calls_made"] == 0
    assert contract["job"]["role_request_contracts"] == deepseek["job"][
        "role_request_contracts"
    ]
    assert contract["job"]["relation_response_schema_sha256"] == deepseek["job"][
        "relation_response_schema_sha256"
    ]
    assert contract["job"]["model"] == "z-ai/glm-5.2"
    assert contract["job"]["provider_slug"] == "deepinfra"
    assert contract["boundary"]["prompt_or_schema_changed_from_deepseek_run"] is False
