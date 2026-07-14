import json
from pathlib import Path
import pytest
from engine.system_b.canonical_model_selection import CanonicalSelectionError,build_assessment_cards,build_challenge_selection_packet,build_exhaustive_assessment_packet,build_exhaustive_prompts,compile_exhaustive_response,exhaustive_response_schema
from engine.system_b.reasoning_mechanism_ontology import MECHANISMS
ROOT=Path(__file__).resolve().parents[1]
def base():
 models=json.loads((ROOT/"data/knowledge_graph.json").read_text())["models"];role=json.loads((ROOT/"research/role-record-pattern-invariance-corpus-2026-07-12/packets/housing_source_first.json").read_text());cards=build_assessment_cards(models);recall={"premortem":["missing_reversal_condition"],"confirmation-bias":["counterpressure_acknowledged_not_integrated"]};challenge=build_challenge_selection_packet(arm_id="x",role_packet=role,cards=cards,candidate_ids=sorted(recall),selection_mode="graph_recalled_canonical",recalled_by=recall,controlled_mechanism_ids=set(MECHANISMS),source_refs=[]);return build_exhaustive_assessment_packet(challenge_packet=challenge,mechanism_cards=MECHANISMS)
def negative():return {"assessments":[{"model_id":"confirmation-bias","status":"not_applicable","source_role_record_ids":[]},{"model_id":"premortem","status":"not_applicable","source_role_record_ids":[]}]}

def test_every_candidate_contains_complete_operational_mechanism_cards():
 p=base()
 for candidate in p["candidate_cards"]:
  for card in candidate["recall_mechanism_cards"]:
   assert set(card)=={"mechanism_id","definition","requires","excludes","near_neighbor"};assert all(card.values())
 assert p["boundary"]["global_abstention_shortcut"]is False

def test_assessment_card_separates_applicability_from_optional_failure_signal():
 cards=build_assessment_cards(json.loads((ROOT/"data/knowledge_graph.json").read_text())["models"]);premortem=cards["premortem"]
 assert "pre-commitment failure-exposure problem" in premortem["challenge_when"]
 assert "superficial" in premortem["failure_signal"]
 assert set(premortem)=={"schema_version","model_id","display_name","challenge_when","failure_signal","do_not_apply_when","pressure_question"}

def test_schema_requires_exactly_one_row_per_candidate_without_global_outcome():
 s=exhaustive_response_schema(["a","b"]);assert set(s["properties"])=={"assessments"};assert s["properties"]["assessments"]["minItems"]==s["properties"]["assessments"]["maxItems"]==2

def test_all_negative_rows_remain_valid_without_forced_activation():
 c=compile_exhaustive_response(response=negative(),packet=base());assert c["active_model_ids"]==[];assert len(c["assessments"])==2

def test_omission_duplicate_unknown_and_bad_custody_fail_closed():
 p=base();r=negative();r["assessments"].pop()
 with pytest.raises(CanonicalSelectionError,match="coverage"):compile_exhaustive_response(response=r,packet=p)
 r=negative();r["assessments"][1]["model_id"]="confirmation-bias"
 with pytest.raises(CanonicalSelectionError,match="identity"):compile_exhaustive_response(response=r,packet=p)
 r=negative();r["assessments"][0].update(status="applicable",source_role_record_ids=["unknown"])
 with pytest.raises(CanonicalSelectionError,match="custody"):compile_exhaustive_response(response=r,packet=p)

def test_applicable_requires_evidence_and_not_applicable_forbids_it():
 p=base();rid=p["role_records"][0]["role_record_id"];r=negative();r["assessments"][1].update(status="applicable")
 with pytest.raises(CanonicalSelectionError,match="lacks evidence"):compile_exhaustive_response(response=r,packet=p)
 r=negative();r["assessments"][0]["source_role_record_ids"]=[rid]
 with pytest.raises(CanonicalSelectionError,match="cannot cite"):compile_exhaustive_response(response=r,packet=p)

def test_prompt_requires_every_candidate_and_treats_recall_as_hypothesis():
 text=" ".join(build_exhaustive_prompts(base()).values());assert "every recalled canonical mental model exactly once"in text and"hypotheses, not proof"in text and"Negative assessment is valid"in text
