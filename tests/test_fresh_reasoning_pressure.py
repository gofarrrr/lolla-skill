import json
from pathlib import Path
import pytest
from engine.system_b.canonical_model_selection import build_assessment_cards
from engine.system_b.fresh_reasoning_pressure import FreshPressureError,build_control_packet,build_control_packet_v2,build_control_prompts,build_control_prompts_v2,build_packet,build_packet_v2,build_prompts,build_prompts_v2,compile_control_response,compile_response,response_schema
ROOT=Path(__file__).resolve().parents[1]
def packet():
 conversation="[Turn 1] USER:\nA\n[Turn 1] ASSISTANT:\nB\n[Turn 2] USER:\nC\n[Turn 2] ASSISTANT:\nD\n";cards=build_assessment_cards(json.loads((ROOT/"data/knowledge_graph.json").read_text())["models"]);portfolio={"candidates":[{"model_id":"premortem","recalled_by_mechanism_ids":["missing_reversal_condition"]}]};return build_packet(case_id="x",conversation=conversation,portfolio=portfolio,challenge_cards=cards,source_refs=[])
def response(disposition="reject",effect="no_material_effect"):
 return {"candidate_dispositions":[{"model_id":"premortem","disposition":disposition,"source_turn_numbers":[2],"effect":effect,"disposition_note":"The lens does not materially change this bounded reasoning."}],"reconsidered_answer":"A self-contained answer.","change_summary":"No material change."}
def test_packet_preserves_all_candidates_and_authoritative_conversation():
 p=packet();assert p["authoritative_conversation"].startswith("[Turn 1]");assert p["instructions"]["candidate_deletion_before_reconsideration"]is False;assert p["pressure_portfolio"][0]["portfolio_status"]=="intentionally_noisy_pressure_hypothesis"
def test_schema_requires_exact_disposition_coverage():
 s=response_schema(["a","b"]);assert s["properties"]["candidate_dispositions"]["minItems"]==s["properties"]["candidate_dispositions"]["maxItems"]==2;assert s["properties"]["candidate_dispositions"]["items"]["properties"]["disposition_note"]["maxLength"]==1000
def test_reject_is_valid_and_preserved_with_no_material_effect():
 c=compile_response(response=response(),packet=packet());assert c["candidate_dispositions"][0]["disposition"]=="reject"and c["all_candidates_accounted_for"]
def test_unknown_turn_missing_candidate_and_material_reject_fail_closed():
 p=packet();r=response();r["candidate_dispositions"][0]["source_turn_numbers"]=[99]
 with pytest.raises(FreshPressureError,match="turn custody"):compile_response(response=r,packet=p)
 r=response();r["candidate_dispositions"]=[]
 with pytest.raises(FreshPressureError,match="coverage"):compile_response(response=r,packet=p)
 with pytest.raises(FreshPressureError,match="material effect"):compile_response(response=response(effect="reframe"),packet=p)
def test_prompt_states_noise_rejection_and_no_checklist_answer():
 text=" ".join(build_prompts(packet()).values());assert "intentionally noisy hypothesis"in text and"explicitly reject or park"in text and"must not appear as a mechanical checklist"in text
def test_control_contains_same_authoritative_source_but_no_graph_candidates():
 p=packet();c=build_control_packet(case_id="x",conversation=p["authoritative_conversation"],source_refs=[]);assert c["authoritative_conversation"]==p["authoritative_conversation"]and c["boundary"]["graph_candidates_included"]is False;assert "pressure_portfolio"not in c
 out=compile_control_response(response={"reconsidered_answer":"Answer","change_summary":"Changed"},packet=c);assert out["external_pressure_portfolio_included"]is False
 assert "no external mental-model pressure portfolio"in build_control_prompts(c)["user_prompt"]

def test_v2_preserves_v1_replay_and_forbids_unsupported_precision():
 p=packet();cards=build_assessment_cards(json.loads((ROOT/"data/knowledge_graph.json").read_text())["models"]);portfolio={"candidates":[{"model_id":"premortem","recalled_by_mechanism_ids":["missing_reversal_condition"]}]}
 v2=build_packet_v2(case_id="x",conversation=p["authoritative_conversation"],portfolio=portfolio,challenge_cards=cards,source_refs=[])
 assert v2["schema_version"].endswith(".v2")
 assert v2["instructions"]["unsupported_quantitative_thresholds_allowed"]is False
 assert "Never invent a numerical threshold"in build_prompts_v2(v2)["user_prompt"]
 control=build_control_packet_v2(case_id="x",conversation=p["authoritative_conversation"],source_refs=[])
 assert control["schema_version"].endswith(".v2")
 assert "leave the value unresolved"in build_control_prompts_v2(control)["user_prompt"]
 assert build_prompts(p)["user_prompt"].startswith("FRESH REASONING PRESSURE PACKET\n")
