from copy import deepcopy

import pytest

from engine.system_b.reasoning_mechanism_submicrotask_v1 import (
    assistant_coverage_response_schema_v1,
    build_assistant_coverage_packet_v1,
    build_assistant_coverage_prompts_v1,
    build_user_status_packet_v1,
    build_user_status_prompts_v1,
    compile_assistant_coverage_response_v1,
    compile_user_status_response_v1,
    join_split_mechanism_assessment_v1,
    user_status_response_schema_v1,
)
from engine.system_b.simulated_reliability_v1 import SimulatedReliabilityError


MECHANISM = "counterpressure_acknowledged_not_integrated"


def _parent():
    return {
        "case_id": "case-1",
        "role_records": [
            {"role_record_id": "starting-1", "role": "starting"},
            {"role_record_id": "current-1", "role": "current"},
        ],
        "assistant_contributions": [
            {"contribution_id": "assistant-turn-001", "text": "Add a test."}
        ],
    }


def _user_result(status="resolved", state="not_applicable", ids=None):
    packet = build_user_status_packet_v1(parent_packet=_parent(), mechanism_id=MECHANISM)
    result = compile_user_status_response_v1(
        response={
            "mechanism_id": MECHANISM,
            "user_process_status": status,
            "pattern_state": state,
            "source_role_record_ids": ["starting-1", "current-1"] if ids is None else ids,
        },
        packet=packet,
        producer_id="test",
    )
    return packet, result


def test_split_prompts_and_schemas_are_stable_and_qualification_review_is_omitted():
    parent = {**_parent(), "qualification_review": {"outcome": "unresolved"}}
    packet = build_user_status_packet_v1(parent_packet=parent, mechanism_id=MECHANISM)
    assert "qualification_review" not in packet
    assert set(user_status_response_schema_v1(MECHANISM)["required"]) == {
        "mechanism_id", "user_process_status", "pattern_state", "source_role_record_ids"
    }
    assert build_user_status_prompts_v1(packet)["system_prompt_sha256"]

    _, result = _user_result()
    coverage_packet = build_assistant_coverage_packet_v1(
        parent_packet=parent, user_status=result["assessment"]
    )
    assert set(assistant_coverage_response_schema_v1(MECHANISM)["required"]) == {
        "mechanism_id", "vanilla_answer_coverage", "source_assistant_contribution_ids"
    }
    assert build_assistant_coverage_prompts_v1(coverage_packet)["user_prompt_sha256"]


def test_join_derives_standdown_from_resolved_and_operationalized():
    _, user_result = _user_result()
    packet = build_assistant_coverage_packet_v1(
        parent_packet=_parent(), user_status=user_result["assessment"]
    )
    coverage_result = compile_assistant_coverage_response_v1(
        response={
            "mechanism_id": MECHANISM,
            "vanilla_answer_coverage": "operationalized",
            "source_assistant_contribution_ids": ["assistant-turn-001"],
        },
        packet=packet,
        producer_id="test",
    )
    joined = join_split_mechanism_assessment_v1(
        user_result=user_result, coverage_result=coverage_result
    )
    assert joined["assessment"]["routing_disposition"] == "preserve_no_route"
    assert joined["boundary"]["routing_disposition_model_authored"] is False


def test_join_routes_only_explicit_unresolved_and_uncovered():
    _, user_result = _user_result("unresolved", "present", ["current-1"])
    packet = build_assistant_coverage_packet_v1(
        parent_packet=_parent(), user_status=user_result["assessment"]
    )
    coverage_result = compile_assistant_coverage_response_v1(
        response={
            "mechanism_id": MECHANISM,
            "vanilla_answer_coverage": "not_covered",
            "source_assistant_contribution_ids": [],
        },
        packet=packet,
        producer_id="test",
    )
    joined = join_split_mechanism_assessment_v1(
        user_result=user_result, coverage_result=coverage_result
    )
    assert joined["assessment"]["routing_disposition"] == "route_uncovered_pressure"


def test_tampered_packet_is_rejected():
    packet = build_user_status_packet_v1(parent_packet=_parent(), mechanism_id=MECHANISM)
    packet = deepcopy(packet)
    packet["case_id"] = "changed"
    with pytest.raises(SimulatedReliabilityError, match="hash drifted"):
        build_user_status_prompts_v1(packet)
