from __future__ import annotations

import copy
import json
from pathlib import Path

from engine.system_b.reasoning_process_contracts import schema_metrics
from engine.system_b.reasoning_process_position_role_first_v2 import ROLE_ORDER
from engine.system_b.reasoning_process_position_role_first_v21 import (
    position_relation_response_schema_v21,
)
from engine.system_b.reasoning_process_position_role_first_v22 import (
    build_position_relation_packet_v22,
    build_position_role_packet_v22,
    build_position_role_prompts_v22,
    compile_position_relation_response_v22,
    compile_position_role_response_v22,
    join_position_role_first_v22,
    position_relation_response_schema_v22,
    position_role_response_schema_v22,
    project_parallel_role_response_v22,
)

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "research/reasoning-process-position-role-first-v22-2026-07-12/report.json"
SUCCESSION = (
    ROOT / "research/reasoning-process-position-role-first-v21-new-case-2026-07-12"
)
COOPERATIVE = ROOT / "research/reasoning-process-position-role-first-v22-new-case-2026-07-12"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _compile(role: str, response: dict, packet: dict) -> dict:
    return compile_position_role_response_v22(
        response=response,
        packet=packet,
        producer_kind="fixture",
        producer_id="v22-adversarial-test",
    )


def test_v22_role_schema_uses_nested_components_not_parallel_columns() -> None:
    for role in ROLE_ORDER:
        schema = position_role_response_schema_v22(role)
        serialized = json.dumps(schema, sort_keys=True)
        assert '"stance_components"' in serialized
        assert '"object_kinds"' not in serialized
        assert '"expression_kinds"' not in serialized
        assert schema_metrics(schema)["depth"] <= 11
        assert schema_metrics(schema)["bytes"] <= 1956


def test_provider_free_report_replays_ten_cases_and_keeps_calls_blocked() -> None:
    report = _load(REPORT)
    assert report["status"] == "provider_free_position_role_first_v22_pass"
    assert report["summary"]["reviewed_case_count"] == 10
    assert report["summary"]["complete_join_count"] == 10
    assert report["summary"]["admitted_role_record_count"] == 30
    assert report["summary"]["admitted_relation_record_count"] == 10
    assert report["summary"]["quarantined_record_count"] == 0
    assert report["summary"]["maximum_user_prompt_utf8_bytes"] == 5660
    assert report["summary"]["provider_calls"] == 0
    assert report["claims"]["automatic_semantic_extraction_improved"] is False
    assert report["decision"]["provider_probe_authorized"] is False


def test_v22_projects_and_compiles_the_pre_execution_succession_target() -> None:
    wrapper = _load(SUCCESSION / "position-endpoint.json")
    target = _load(SUCCESSION / "source-review-target.json")
    old = _load(SUCCESSION / "compiled-source-review-target.json")
    roles = {}
    for role in ROLE_ORDER:
        packet = build_position_role_packet_v22(wrapper=wrapper, role=role)
        response = project_parallel_role_response_v22(target["role_responses"][role])
        roles[role] = _compile(role, response, packet)
        assert roles[role]["records"][0]["terminal_state"] == "admitted"
        assert roles[role]["boundary"]["parallel_component_columns_used"] is False
        prompt = build_position_role_prompts_v22(packet)["user_prompt"]
        assert len(prompt.encode("utf-8")) <= 5660
    relation_packet = build_position_relation_packet_v22(
        role_compiled_by_role=roles
    )
    old_ids = {
        role: old["role_compiled"][role]["observations"][0]["role_record_id"]
        for role in ROLE_ORDER
    }
    new_ids = {
        role: roles[role]["observations"][0]["role_record_id"] for role in ROLE_ORDER
    }
    relation_response = copy.deepcopy(old["relation_response"])
    for role in ROLE_ORDER:
        field = f"{role}_role_record_id"
        assert relation_response["records"][0][field] == old_ids[role]
        relation_response["records"][0][field] = new_ids[role]
    relation = compile_position_relation_response_v22(
        response=relation_response,
        packet=relation_packet,
        producer_kind="fixture",
        producer_id="v22-adversarial-test",
    )
    joined = join_position_role_first_v22(
        role_compiled_by_role=roles,
        relation_compiled=relation,
    )
    assert joined["status"] == "position_role_first_join_complete"


def test_missing_component_property_is_quarantined_not_healed() -> None:
    wrapper = _load(SUCCESSION / "position-endpoint.json")
    target = _load(SUCCESSION / "source-review-target.json")
    packet = build_position_role_packet_v22(wrapper=wrapper, role="qualification")
    response = project_parallel_role_response_v22(target["role_responses"]["qualification"])
    response["records"][0]["stance_components"][0].pop("expression_kind")
    compiled = _compile("qualification", response, packet)
    assert compiled["records"][0]["terminal_state"] == "quarantined"
    assert "component fields" in compiled["records"][0]["reason"]


def test_component_source_must_be_parent_record_alias() -> None:
    wrapper = _load(SUCCESSION / "position-endpoint.json")
    target = _load(SUCCESSION / "source-review-target.json")
    packet = build_position_role_packet_v22(wrapper=wrapper, role="current")
    response = project_parallel_role_response_v22(target["role_responses"]["current"])
    response["records"][0]["stance_components"][0]["source_evidence_id"] = "e056"
    compiled = _compile("current", response, packet)
    assert compiled["records"][0]["terminal_state"] == "quarantined"
    assert "parent-record alias" in compiled["records"][0]["reason"]


def test_exact_duplicate_nested_component_is_quarantined() -> None:
    wrapper = _load(SUCCESSION / "position-endpoint.json")
    target = _load(SUCCESSION / "source-review-target.json")
    packet = build_position_role_packet_v22(wrapper=wrapper, role="qualification")
    response = project_parallel_role_response_v22(target["role_responses"]["qualification"])
    response["records"][0]["stance_components"][1] = copy.deepcopy(
        response["records"][0]["stance_components"][0]
    )
    compiled = _compile("qualification", response, packet)
    assert compiled["records"][0]["terminal_state"] == "quarantined"
    assert "exactly duplicates" in compiled["records"][0]["reason"]


def test_semantically_dubious_nested_category_pair_remains_source_review_work() -> None:
    wrapper = _load(SUCCESSION / "position-endpoint.json")
    target = _load(SUCCESSION / "source-review-target.json")
    packet = build_position_role_packet_v22(wrapper=wrapper, role="starting")
    response = project_parallel_role_response_v22(target["role_responses"]["starting"])
    component = response["records"][0]["stance_components"][0]
    component["object_kind"] = "acceptance_or_willingness"
    component["expression_kind"] = "commitment"
    compiled = _compile("starting", response, packet)
    assert compiled["records"][0]["terminal_state"] == "admitted"
    assert compiled["boundary"]["object_expression_compatibility_gate_added"] is False
    assert compiled["boundary"]["semantic_role_or_category_correctness_inferred_by_code"] is False


def test_relation_schema_is_unchanged_by_component_wire_amendment() -> None:
    assert position_relation_response_schema_v22() == position_relation_response_schema_v21()


def test_fresh_cooperative_target_was_source_first_and_compiles_without_provider() -> None:
    report = _load(COOPERATIVE / "target-report.json")
    target = _load(COOPERATIVE / "source-review-target.json")
    compiled = _load(COOPERATIVE / "compiled-source-review-target.json")
    assert report["status"] == "pre_execution_target_gate_pass"
    assert report["admitted_role_record_count"] == 3
    assert report["admitted_relation_record_count"] == 1
    assert report["quarantined_record_count"] == 0
    assert report["provider_calls"] == 0
    assert target["boundary"]["written_before_provider_execution"] is True
    assert target["boundary"]["included_in_provider_context"] is False
    qualification = target["role_responses"]["qualification"]["records"][0]
    assert qualification["evidence_ids"] == ["e052", "e055", "e056"]
    assert qualification["stance_components"][-1]["source_evidence_id"] == "e056"
    assert compiled["joined"]["status"] == "position_role_first_join_complete"


def test_fresh_cooperative_packet_keeps_target_out_and_call_blocked() -> None:
    case_report = _load(COOPERATIVE / "case-report.json")
    packet = _load(COOPERATIVE / "position-endpoint.json")
    assert case_report["provider_calls"] == 0
    assert case_report["boundary"]["protected_target_included"] is False
    assert case_report["boundary"]["provider_probe_authorized"] is False
    assert packet["packet"]["focal_turn_indices"] == [1, 7]
    assert len(packet["focal_alias_map"]) == 17


def test_v22_probe_is_preserved_as_structural_pass_semantic_failure() -> None:
    probe = ROOT / "research/reasoning-process-position-role-first-v22-probe-2026-07-12"
    result = _load(probe / "result.json")
    review = _load(probe / "source-review.json")
    assert result["provider_request_count"] == 4
    assert result["joined"]["status"] == "position_role_first_join_complete"
    assert review["status"] == "structural_hypothesis_confirmed_semantic_gate_failed"
    assert review["operational_result"]["nested_component_alignment_failure_repeated"] is False
    assert review["role_review"]["qualification"]["protected_target_survived"] is True
    assert review["role_review"]["current"]["role_boundary"] == "fail"
    assert review["decision"]["provider_retry_or_model_control_authorized"] is False
    assert review["decision"]["graph_or_runtime_integration_authorized"] is False
