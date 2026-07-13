import pytest

from engine.system_b.reasoning_mechanism_user_factor_v1 import (
    build_user_factor_packet_v1,
    build_user_factor_prompts_v1,
    compile_user_factor_response_v1,
    user_factor_response_schema_v1,
)
from engine.system_b.simulated_reliability_v1 import SimulatedReliabilityError


MECHANISM = "counterpressure_acknowledged_not_integrated"


def _parent():
    return {
        "case_id": "case-1",
        "role_records": [
            {"role_record_id": "starting-1", "role": "starting"},
            {"role_record_id": "current-1", "role": "current"}
        ],
        "qualification_review": {"outcome": "unresolved_qualification_present"}
    }


def test_factor_packet_omits_anchoring_review_and_has_stable_schema():
    packet = build_user_factor_packet_v1(parent_packet=_parent(), mechanism_id=MECHANISM)
    assert "qualification_review" not in packet
    assert build_user_factor_prompts_v1(packet)["system_prompt_sha256"]
    assert set(user_factor_response_schema_v1(MECHANISM)["required"]) == {
        "mechanism_id", "mechanism_observation", "integration_status",
        "pattern_state", "source_role_record_ids"
    }


def test_observed_integrated_derives_resolved_without_semantic_code_reading():
    packet = build_user_factor_packet_v1(parent_packet=_parent(), mechanism_id=MECHANISM)
    result = compile_user_factor_response_v1(
        response={
            "mechanism_id": MECHANISM,
            "mechanism_observation": "observed",
            "integration_status": "integrated",
            "pattern_state": "not_applicable",
            "source_role_record_ids": ["starting-1", "current-1"]
        },
        packet=packet,
        producer_id="test"
    )
    assert result["assessment"]["user_process_status"] == "resolved"
    assert result["boundary"]["deterministic_semantic_inference"] is False


def test_observed_not_integrated_derives_unresolved():
    packet = build_user_factor_packet_v1(parent_packet=_parent(), mechanism_id=MECHANISM)
    result = compile_user_factor_response_v1(
        response={
            "mechanism_id": MECHANISM,
            "mechanism_observation": "observed",
            "integration_status": "not_integrated",
            "pattern_state": "present",
            "source_role_record_ids": ["current-1"]
        },
        packet=packet,
        producer_id="test"
    )
    assert result["assessment"]["user_process_status"] == "unresolved"


def test_not_observed_cannot_cite_evidence():
    packet = build_user_factor_packet_v1(parent_packet=_parent(), mechanism_id=MECHANISM)
    with pytest.raises(SimulatedReliabilityError, match="not-observed"):
        compile_user_factor_response_v1(
            response={
                "mechanism_id": MECHANISM,
                "mechanism_observation": "not_observed",
                "integration_status": "not_applicable",
                "pattern_state": "not_applicable",
                "source_role_record_ids": ["starting-1"]
            },
            packet=packet,
            producer_id="test"
        )
