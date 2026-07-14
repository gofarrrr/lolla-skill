import json
from pathlib import Path

import pytest

from engine.system_b.reasoning_mechanism_ontology import MECHANISMS
from engine.system_b.reasoning_pattern_role_record_interpreter import RoleRecordPatternError
from engine.system_b.reasoning_pattern_role_record_interpreter_v3 import (
    build_input_v3,
    build_prompts_v3,
    compile_response_v3,
)


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "research/independent-quiet-library-v242-role-probe-2026-07-12/result.json"


def packet():
    joined = json.loads(RESULT.read_text())["joined"]
    return build_input_v3(case_id="quiet", arm_id="quiet_provider", joined=joined, source_refs=[])


def all_not_observed():
    return {"assessments": [{"mechanism_id": mechanism, "joint_status": "not_observed", "pattern_state": "not_applicable", "source_role_record_ids": []} for mechanism in sorted(MECHANISMS)]}


def test_negative_review_requires_two_roles_and_preserves_no_raw_evidence_text():
    value = packet()
    assert [record["role"] for record in value["role_records"]] == ["starting", "current"]
    assert value["qualification_review"]["outcome"] == "no_unresolved_qualification_observed"
    assert "source_evidence" not in value["qualification_review"]
    assert value["boundary"]["negative_review_is_not_a_deterministic_veto"] is True


def test_prompt_distinguishes_adopted_safeguards_from_unresolved_qualification():
    prompt = build_prompts_v3(packet())["user_prompt"]
    assert "is evidence of integration" in prompt
    assert "not an instruction to find weaknesses" in prompt


def test_all_not_observed_compiles_to_empty_fact_free_projection():
    compiled = compile_response_v3(response=all_not_observed(), packet=packet(), producer_kind="test", producer_id="test")
    assert compiled["routing_projection"]["pattern_nodes"] == []
    assert compiled["fact_boundary"]["raw_text_included"] is False
    assert compiled["provenance"]["qualification_review_outcome"] == "no_unresolved_qualification_observed"


def test_negative_review_cannot_coexist_with_qualification_record():
    value = packet()
    value["role_records"].append({**value["role_records"][1], "role": "qualification", "role_record_id": "q"})
    value.pop("packet_sha256")
    from engine.system_b.reasoning_pattern_role_record_interpreter import _sha
    value["packet_sha256"] = _sha(value)
    with pytest.raises(RoleRecordPatternError, match="negative review role count"):
        build_prompts_v3(value)
