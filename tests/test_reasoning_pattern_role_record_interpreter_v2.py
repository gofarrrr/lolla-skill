import json
from pathlib import Path

import pytest

from engine.system_b.reasoning_mechanism_ontology import MECHANISMS, ontology_packet
from engine.system_b.reasoning_pattern_role_record_interpreter import RoleRecordPatternError
from engine.system_b.reasoning_pattern_role_record_interpreter_v2 import (
    build_prompts_v2, compile_response_v2, response_schema_v2,
)

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "research/role-record-pattern-invariance-corpus-2026-07-12/packets/registry_source_first.json"


def _packet():
    return json.loads(PACKET.read_text())


def _all_not_observed():
    return {"assessments": [{"mechanism_id": mechanism, "joint_status": "not_observed", "pattern_state": "not_applicable", "source_role_record_ids": []} for mechanism in sorted(MECHANISMS)]}


def test_ontology_is_complete_and_has_discriminating_contracts():
    value = ontology_packet()
    assert len(value["mechanisms"]) == 9
    for card in value["mechanisms"].values():
        assert set(card) == {"definition", "requires", "excludes", "near_neighbor"}
        assert all(card.values())
    assert value["routing_rule"] == "Only joint status unresolved is routing eligible."


def test_prompt_reviews_every_mechanism_and_explains_exhaustive_does_not_mean_positive():
    prompt = build_prompts_v2(_packet())["user_prompt"]
    for mechanism in MECHANISMS:
        assert mechanism in prompt
    assert "not an instruction to find nine weaknesses" in prompt
    assert "mental-model names" in prompt


def test_schema_is_bounded_to_exactly_nine_rows():
    schema = response_schema_v2()
    assessments = schema["properties"]["assessments"]
    assert assessments["minItems"] == assessments["maxItems"] == 9


def test_all_not_observed_compiles_to_empty_routing_projection():
    compiled = compile_response_v2(response=_all_not_observed(), packet=_packet(), producer_kind="test", producer_id="test")
    assert compiled["routing_projection"]["pattern_nodes"] == []
    assert compiled["lint"]["status"] == "passed"


def test_only_unresolved_routes_and_scope_is_joint_process():
    packet, response = _packet(), _all_not_observed()
    row = next(x for x in response["assessments"] if x["mechanism_id"] == "missing_reversal_condition")
    row.update(joint_status="unresolved", pattern_state="missing_protection", source_role_record_ids=[packet["role_records"][2]["role_record_id"]])
    compiled = compile_response_v2(response=response, packet=packet, producer_kind="test", producer_id="test")
    assert compiled["routing_projection"]["pattern_nodes"] == [{"pattern_id": row_id, "mechanism_id": "missing_reversal_condition", "subject_scope": "joint_process", "state": "missing_protection"} for row_id in [next(x["pattern_id"] for x in compiled["pattern_hypotheses"] if x["mechanism_id"] == "missing_reversal_condition")]]


@pytest.mark.parametrize("status,state,ids,error", [
    ("unresolved", "tension", ["valid"], "unresolved"),
    ("ambiguous", "present", ["valid"], "ambiguous"),
    ("resolved_in_conversation", "not_applicable", [], "resolved"),
    ("not_observed", "not_applicable", ["valid"], "not-observed"),
])
def test_status_state_custody_combinations_fail_closed(status, state, ids, error):
    packet, response = _packet(), _all_not_observed()
    valid = packet["role_records"][0]["role_record_id"]
    row = response["assessments"][0]
    row.update(joint_status=status, pattern_state=state, source_role_record_ids=[valid if x == "valid" else x for x in ids])
    with pytest.raises(RoleRecordPatternError, match=error):
        compile_response_v2(response=response, packet=packet, producer_kind="test", producer_id="test")


def test_duplicate_mechanism_cannot_hide_missing_coverage():
    response = _all_not_observed()
    response["assessments"][-1]["mechanism_id"] = response["assessments"][0]["mechanism_id"]
    with pytest.raises(RoleRecordPatternError, match="identity"):
        compile_response_v2(response=response, packet=_packet(), producer_kind="test", producer_id="test")
