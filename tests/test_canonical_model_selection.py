import copy,json
from pathlib import Path
import pytest
from engine.system_b.canonical_model_selection import CanonicalSelectionError,build_cards,build_prompts,build_selection_packet,compile_response,response_schema

ROOT=Path(__file__).resolve().parents[1]
def models():return json.loads((ROOT/"data/knowledge_graph.json").read_text())["models"]
def role():return json.loads((ROOT/"research/role-record-pattern-invariance-corpus-2026-07-12/packets/registry_source_first.json").read_text())

def test_all_222_cards_are_canonical_compact_complete_and_distinct():
 cards=build_cards(models());assert len(cards)==222;assert set(cards)==set(models())
 assert all(len(json.dumps(x))<650 for x in cards.values())
 for field in ("use_when","avoid_when","input_type","output_type"):
  values=[x[field] for x in cards.values()];assert all(values);assert len(values)==len(set(values))

def test_direct_and_graph_packets_use_identical_cards_for_shared_candidates():
 cards=build_cards(models());rp=role();ids=sorted(cards)[:8]
 direct=build_selection_packet(arm_id="d",role_packet=rp,cards=cards,candidate_ids=sorted(cards),selection_mode="direct_all_canonical",source_refs=[])
 graph=build_selection_packet(arm_id="g",role_packet=rp,cards=cards,candidate_ids=ids,selection_mode="graph_recalled_canonical",source_refs=[])
 dm={x["model_id"]:x for x in direct["candidate_cards"]}
 assert graph["candidate_cards"]==[dm[x] for x in ids]

def test_unknown_candidate_and_invented_response_fail_closed():
 cards=build_cards(models());rp=role()
 with pytest.raises(CanonicalSelectionError,match="candidate custody"):
  build_selection_packet(arm_id="x",role_packet=rp,cards=cards,candidate_ids=["invented"],selection_mode="direct_all_canonical",source_refs=[])
 packet=build_selection_packet(arm_id="x",role_packet=rp,cards=cards,candidate_ids=["premortem"],selection_mode="graph_recalled_canonical",source_refs=[])
 with pytest.raises(CanonicalSelectionError,match="ID custody"):
  compile_response(response={"outcome":"candidates_selected","selections":[{"model_id":"invented","disposition":"selected","source_role_record_ids":[rp["role_records"][0]["role_record_id"]]}]},packet=packet)

def test_abstention_requires_empty_selection_and_selected_requires_nonempty():
 cards=build_cards(models());rp=role();packet=build_selection_packet(arm_id="x",role_packet=rp,cards=cards,candidate_ids=["premortem"],selection_mode="graph_recalled_canonical",source_refs=[])
 assert compile_response(response={"outcome":"all_not_applicable","selections":[]},packet=packet)["selections"]==[]
 with pytest.raises(CanonicalSelectionError,match="disagree"):
  compile_response(response={"outcome":"candidates_selected","selections":[]},packet=packet)

def test_selection_requires_exact_role_record_custody_and_never_free_text():
 cards=build_cards(models());rp=role();packet=build_selection_packet(arm_id="x",role_packet=rp,cards=cards,candidate_ids=["premortem"],selection_mode="graph_recalled_canonical",source_refs=[])
 schema=response_schema(["premortem"]);assert "rationale" not in json.dumps(schema)
 bad={"outcome":"candidates_selected","selections":[{"model_id":"premortem","disposition":"selected","source_role_record_ids":["unknown"]}]}
 with pytest.raises(CanonicalSelectionError,match="evidence custody"):compile_response(response=bad,packet=packet)

def test_prompt_says_six_is_cap_and_all_candidates_can_be_rejected():
 cards=build_cards(models());packet=build_selection_packet(arm_id="x",role_packet=role(),cards=cards,candidate_ids=["premortem"],selection_mode="graph_recalled_canonical",source_refs=[]);p=build_prompts(packet)
 assert "six is a hard cap, not a target" in p["user_prompt"] and "Every candidate may be rejected" in p["system_prompt"]
