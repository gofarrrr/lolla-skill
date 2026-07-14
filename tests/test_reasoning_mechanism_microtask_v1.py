from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.system_b.reasoning_mechanism_microtask_v1 import (
    build_mechanism_microtask_packet_v1,
    compile_mechanism_microtask_response_v1,
    mechanism_microtask_response_schema_v1,
)
from engine.system_b.simulated_reliability_v1 import SimulatedReliabilityError


ROOT = Path(__file__).resolve().parents[1]
REQUEST = ROOT / (
    "research/simulated-reliability-v1-lite-mechanism-2026-07-13/a1/"
    "mechanism-request.json"
)


def _parent() -> dict:
    return json.loads(REQUEST.read_text(encoding="utf-8"))["packet"]


def _compile(mechanism_id: str, **overrides):
    packet = build_mechanism_microtask_packet_v1(
        parent_packet=_parent(), mechanism_id=mechanism_id
    )
    response = {
        "mechanism_id": mechanism_id,
        "user_process_status": "unresolved",
        "vanilla_answer_coverage": "acknowledged_only",
        "pattern_state": "missing_protection",
        "source_role_record_ids": [packet["role_records"][2]["role_record_id"]],
        "source_assistant_contribution_ids": [
            packet["assistant_contributions"][0]["contribution_id"]
        ],
        **overrides,
    }
    return compile_mechanism_microtask_response_v1(
        response=response,
        packet=packet,
        producer_kind="test",
        producer_id="fixture",
    )


def test_single_schema_omits_model_authored_routing() -> None:
    schema = mechanism_microtask_response_schema_v1("missing_reversal_condition")
    assert "routing_disposition" not in schema["properties"]
    assert schema["properties"]["mechanism_id"]["enum"] == [
        "missing_reversal_condition"
    ]


def test_uncovered_unresolved_status_derives_route_mechanically() -> None:
    compiled = _compile("missing_reversal_condition")
    assert compiled["assessment"]["routing_disposition"] == (
        "route_uncovered_pressure"
    )
    assert compiled["boundary"]["routing_disposition_model_authored"] is False
    assert compiled["boundary"]["deterministic_semantic_inference"] is False


def test_operationalized_unresolved_status_stands_down() -> None:
    compiled = _compile(
        "missing_reversal_condition", vanilla_answer_coverage="operationalized"
    )
    assert compiled["assessment"]["routing_disposition"] == "preserve_no_route"


def test_resolved_status_requires_role_evidence_and_not_applicable_state() -> None:
    compiled = _compile(
        "counterpressure_acknowledged_not_integrated",
        user_process_status="resolved",
        pattern_state="not_applicable",
        vanilla_answer_coverage="operationalized",
    )
    assert compiled["assessment"]["routing_disposition"] == "preserve_no_route"
    with pytest.raises(SimulatedReliabilityError, match="lacks user-process evidence"):
        _compile(
            "counterpressure_acknowledged_not_integrated",
            user_process_status="resolved",
            pattern_state="not_applicable",
            source_role_record_ids=[],
        )


def test_not_observed_requires_no_evidence_and_not_applicable_coverage() -> None:
    compiled = _compile(
        "criteria_defined_after_commitment",
        user_process_status="not_observed",
        vanilla_answer_coverage="not_applicable",
        pattern_state="not_applicable",
        source_role_record_ids=[],
        source_assistant_contribution_ids=[],
    )
    assert compiled["assessment"]["routing_disposition"] == "preserve_no_route"
