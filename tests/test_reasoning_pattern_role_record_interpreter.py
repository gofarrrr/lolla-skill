import copy
import json
from pathlib import Path

import pytest

from engine.system_b.reasoning_pattern_role_record_interpreter import (
    RoleRecordPatternError,
    build_role_record_pattern_input,
    compile_role_record_pattern_response,
)


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "research/role-record-pattern-invariance-corpus-2026-07-12/packets"


def _packet(name="registry_source_first"):
    return json.loads((CORPUS / f"{name}.json").read_text())


def _response(packet, mechanism="acknowledged_constraint_not_gated"):
    return {
        "patterns": [{
            "mechanism_id": mechanism,
            "subject_scope": "joint_process",
            "state": "tension",
            "source_role_record_ids": [
                packet["role_records"][1]["role_record_id"],
                packet["role_records"][2]["role_record_id"],
            ],
        }]
    }


def test_packets_exclude_raw_conversation_and_source_evidence_text():
    for path in CORPUS.glob("*.json"):
        packet = json.loads(path.read_text())
        serialized = json.dumps(packet)
        assert "source_evidence\"" not in serialized
        assert "conversation" not in packet
        assert packet["boundary"]["raw_conversation_included"] is False
        assert packet["boundary"]["source_evidence_text_included"] is False
        assert packet["boundary"]["expected_patterns_included"] is False
        assert "expected_patterns" not in packet


def test_builder_requires_exactly_one_ordered_record_per_role():
    packet = _packet()
    records = packet["role_records"]
    with pytest.raises(RoleRecordPatternError, match="exactly one ordered"):
        build_role_record_pattern_input(
            case_id="x", arm_id="x", records=records[:2], source_refs=[]
        )
    with pytest.raises(RoleRecordPatternError, match="exactly one ordered"):
        build_role_record_pattern_input(
            case_id="x", arm_id="x", records=[records[1], records[0], records[2]], source_refs=[]
        )


def test_compiler_rejects_unknown_role_record_custody():
    packet = _packet()
    response = _response(packet)
    response["patterns"][0]["source_role_record_ids"] = ["invented"]
    with pytest.raises(RoleRecordPatternError, match="custody"):
        compile_role_record_pattern_response(
            response=response, packet=packet, producer_kind="test", producer_id="test"
        )


def test_compiler_rejects_packet_hash_drift():
    packet = _packet()
    packet["role_records"][0]["role_interpretation"] += " altered"
    with pytest.raises(RoleRecordPatternError, match="hash drifted"):
        compile_role_record_pattern_response(
            response=_response(packet), packet=packet, producer_kind="test", producer_id="test"
        )


def test_compiler_seals_fact_free_projection_and_mechanically_merges_duplicates():
    packet = _packet()
    response = _response(packet)
    duplicate = copy.deepcopy(response["patterns"][0])
    duplicate["source_role_record_ids"] = [packet["role_records"][0]["role_record_id"]]
    response["patterns"].append(duplicate)
    compiled = compile_role_record_pattern_response(
        response=response, packet=packet, producer_kind="test", producer_id="test"
    )
    assert compiled["lint"]["status"] == "passed"
    assert compiled["routing_projection"]["contains_case_context"] is False
    assert len(compiled["routing_projection"]["pattern_nodes"]) == 1
    assert len(compiled["provenance"]["pattern_sources"][0]["source_semantic_item_ids"]) == 3
    projection_text = json.dumps(compiled["routing_projection"])
    for record in packet["role_records"]:
        assert record["role_interpretation"] not in projection_text


def test_other_review_required_is_retained_but_never_routes():
    packet = _packet()
    compiled = compile_role_record_pattern_response(
        response=_response(packet, "other_review_required"),
        packet=packet,
        producer_kind="test",
        producer_id="test",
    )
    assert compiled["pattern_hypotheses"][0]["routing_eligible"] is False
    assert compiled["routing_projection"]["pattern_nodes"] == []


def test_structurally_valid_wrong_semantics_are_not_deterministically_gated():
    packet = _packet()
    compiled = compile_role_record_pattern_response(
        response=_response(packet, "status_signal_used_as_evidence"),
        packet=packet,
        producer_kind="test",
        producer_id="test",
    )
    assert compiled["pattern_hypotheses"][0]["mechanism_id"] == "status_signal_used_as_evidence"
    assert compiled["non_claims"][0] == "patterns_are_probabilistic_hypotheses"
