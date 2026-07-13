from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from engine.system_b.reasoning_process_position_role_first_v23 import (
    build_position_role_packet_v23,
    compile_position_role_response_v23,
)
from engine.system_b.reasoning_process_qualification_review_v1 import (
    build_qualification_review_packet_v1,
    compile_qualification_review_response_v1,
    join_decomposed_current_qualification_v1,
    qualification_review_response_schema_v1,
)
from engine.system_b.reasoning_process_view_specific import ViewSpecificInterfaceError


ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / (
    "research/simulated-reliability-corpus-v1-2026-07-12/"
    "provider-free-role-input-preflight/transfer/"
    "v1-case06-industry-funded-lab/position-wrapper.json"
)


def _wrapper() -> dict:
    return json.loads(CASE.read_text(encoding="utf-8"))


def _record(role: str, alias: str) -> dict:
    return {
        "role": role,
        "status": "supported",
        "evidence_ids": [alias],
        "role_interpretation": f"{role} meaning",
        "stance_components": [
            {
                "object_kind": "belief_or_assessment",
                "object_interpretation": f"{role} object",
                "expression_kind": "held_assessment",
                "source_evidence_id": alias,
            }
        ],
        "fidelity_note": "fixture",
        "limitations": "",
    }


def _compiled(role: str, records: list[dict]) -> dict:
    packet = build_position_role_packet_v23(wrapper=_wrapper(), role=role)
    response = {
        "status": "supported" if records else "not_found",
        "records": records,
        "global_limitations": "",
    }
    return compile_position_role_response_v23(
        response=response,
        packet=packet,
        producer_kind="test",
        producer_id="fixture",
    )


def _review(outcome: str) -> dict:
    packet = build_qualification_review_packet_v1(wrapper=_wrapper())
    return compile_qualification_review_response_v1(
        response={
            "outcome": outcome,
            "evidence_ids": ["e097"],
            "interpretation": "The effect on hiring and attention remains.",
            "limitations": "",
        },
        packet=packet,
        producer_kind="test",
        producer_id="fixture",
    )


def test_review_schema_is_small_and_source_linked() -> None:
    schema = qualification_review_response_schema_v1()
    assert schema["required"] == [
        "outcome",
        "evidence_ids",
        "interpretation",
        "limitations",
    ]
    assert schema["properties"]["evidence_ids"]["minItems"] == 1


def test_present_review_and_records_join_without_semantic_inference() -> None:
    joined = join_decomposed_current_qualification_v1(
        current_compiled=_compiled("current", [_record("current", "e095")]),
        qualification_compiled=_compiled(
            "qualification", [_record("qualification", "e097")]
        ),
        qualification_review=_review("unresolved_qualification_present"),
    )
    assert len(joined["observations"]) == 2
    assert joined["qualification_review"]["outcome"] == (
        "unresolved_qualification_present"
    )
    assert joined["boundary"]["deterministic_semantic_inference"] is False
    assert joined["boundary"]["semantic_repair_performed"] is False


def test_negative_review_can_join_only_an_empty_qualification_role() -> None:
    joined = join_decomposed_current_qualification_v1(
        current_compiled=_compiled("current", [_record("current", "e095")]),
        qualification_compiled=_compiled("qualification", []),
        qualification_review=_review("no_unresolved_qualification_observed"),
    )
    assert len(joined["role_compiled"]["qualification"]["observations"]) == 0


def test_review_record_conflicts_are_rejected_without_reading_prose() -> None:
    with pytest.raises(ViewSpecificInterfaceError, match="negative review conflicts"):
        join_decomposed_current_qualification_v1(
            current_compiled=_compiled("current", [_record("current", "e095")]),
            qualification_compiled=_compiled(
                "qualification", [_record("qualification", "e097")]
            ),
            qualification_review=_review("no_unresolved_qualification_observed"),
        )
    invalid = copy.deepcopy(_review("unresolved_qualification_present"))
    invalid["schema_version"] = "drifted"
    with pytest.raises(ViewSpecificInterfaceError, match="review is invalid"):
        join_decomposed_current_qualification_v1(
            current_compiled=_compiled("current", [_record("current", "e095")]),
            qualification_compiled=_compiled(
                "qualification", [_record("qualification", "e097")]
            ),
            qualification_review=invalid,
        )
