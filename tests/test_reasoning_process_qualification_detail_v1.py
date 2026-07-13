from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.system_b.reasoning_process_qualification_detail_v1 import (
    build_qualification_detail_packet_v1,
    compile_qualification_detail_response_v1,
    materialize_quiet_qualification_role_v1,
    qualification_branch_from_review_v1,
)
from engine.system_b.reasoning_process_qualification_review_v1 import (
    build_qualification_review_packet_v1,
    compile_qualification_review_response_v1,
)
from engine.system_b.reasoning_process_view_specific import ViewSpecificInterfaceError


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / (
    "research/simulated-reliability-corpus-v1-2026-07-12/"
    "provider-free-role-input-preflight/transfer"
)


def _wrapper(case_id: str) -> dict:
    return json.loads(
        (BASE / case_id / "position-wrapper.json").read_text(encoding="utf-8")
    )


def _review(case_id: str, outcome: str, aliases: list[str]) -> dict:
    packet = build_qualification_review_packet_v1(wrapper=_wrapper(case_id))
    return compile_qualification_review_response_v1(
        response={
            "outcome": outcome,
            "evidence_ids": aliases,
            "interpretation": "Reviewed meaning.",
            "limitations": "",
        },
        packet=packet,
        producer_kind="test",
        producer_id="fixture",
    )


def test_branch_uses_only_explicit_provider_outcome() -> None:
    present = qualification_branch_from_review_v1(
        _review(
            "v1-case06-industry-funded-lab",
            "unresolved_qualification_present",
            ["e052", "e097"],
        )
    )
    quiet = qualification_branch_from_review_v1(
        _review(
            "v1-case07-cooperative-scheduling",
            "no_unresolved_qualification_observed",
            ["e095", "e096"],
        )
    )
    assert present["branch"] == "detail_required"
    assert quiet["branch"] == "stand_down"
    assert present["boundary"]["deterministic_semantic_inference"] is False


def test_detail_packet_contains_only_reviewed_evidence() -> None:
    review = _review(
        "v1-case06-industry-funded-lab",
        "unresolved_qualification_present",
        ["e052", "e097"],
    )
    packet = build_qualification_detail_packet_v1(
        wrapper=_wrapper("v1-case06-industry-funded-lab"), review=review
    )
    assert packet["focal_region"]["evidence_aliases"] == ["e052", "e097"]
    assert "e095\t" not in packet["focal_region"]["annotated_sentence_text"]
    assert packet["boundary"]["full_conversation_repeated_in_detail_task"] is False


def test_detail_compiler_admits_one_exact_reviewed_record() -> None:
    review = _review(
        "v1-case06-industry-funded-lab",
        "unresolved_qualification_present",
        ["e052", "e097"],
    )
    packet = build_qualification_detail_packet_v1(
        wrapper=_wrapper("v1-case06-industry-funded-lab"), review=review
    )
    response = {
        "status": "supported",
        "records": [
            {
                "role": "qualification",
                "status": "supported",
                "evidence_ids": ["e052", "e097"],
                "role_interpretation": "The funding can still shape attention.",
                "stance_components": [
                    {
                        "object_kind": "belief_or_assessment",
                        "object_interpretation": "Hiring and attention remain shaped.",
                        "expression_kind": "held_assessment",
                        "source_evidence_id": "e097",
                    }
                ],
                "fidelity_note": "fixture",
                "limitations": "",
            }
        ],
        "global_limitations": "",
    }
    compiled = compile_qualification_detail_response_v1(
        response=response,
        packet=packet,
        producer_kind="test",
        producer_id="fixture",
    )
    assert len(compiled["observations"]) == 1
    assert compiled["boundary"]["selected_review_evidence_only"] is True


def test_quiet_review_materializes_empty_role_without_detail() -> None:
    review = _review(
        "v1-case07-cooperative-scheduling",
        "no_unresolved_qualification_observed",
        ["e095", "e096", "e097"],
    )
    compiled = materialize_quiet_qualification_role_v1(
        wrapper=_wrapper("v1-case07-cooperative-scheduling"), review=review
    )
    assert compiled["observations"] == []
    assert compiled["response_status"] == "not_found"
    assert compiled["boundary"]["empty_role_from_explicit_provider_review"] is True
    with pytest.raises(ViewSpecificInterfaceError, match="not authorized"):
        build_qualification_detail_packet_v1(
            wrapper=_wrapper("v1-case07-cooperative-scheduling"), review=review
        )
