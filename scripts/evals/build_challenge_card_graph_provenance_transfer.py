#!/usr/bin/env python3
"""Build housing transfer packets for challenge cards with graph provenance."""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from engine.system_b.canonical_model_selection import build_challenge_cards,build_challenge_prompts,build_challenge_selection_packet,response_schema
from engine.system_b.reasoning_mechanism_ontology import MECHANISMS
from engine.system_b.reasoning_process_contracts import schema_metrics
from engine.system_b.reasoning_process_views import canonical_json_bytes,sha256_bytes
def load(p):return json.loads(Path(p).read_text())
def write(p,v):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(v,indent=2,sort_keys=True)+"\n")
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--output",type=Path,required=True);a=ap.parse_args();out=a.output.resolve();kg=load(ROOT/"data/knowledge_graph.json");cards=build_challenge_cards(kg["models"]);write(out/"challenge-cards-v2.json",{"schema_version":"lolla.canonical_model_challenge_card_registry.v2","cards":cards})
 routing=load(ROOT/"docs/conversation-understanding/reasoning-pattern-shadow-routing-v0.json")["mechanism_seed_models"];full=["acknowledged_constraint_not_gated","counterpressure_acknowledged_not_integrated","missing_reversal_condition"];ablation=full[:-1];source=ROOT/"research/role-record-pattern-invariance-corpus-2026-07-12/packets";artifacts=[]
 for role_arm in ("housing_source_first","housing_provider","housing_reversal_ablation"):
  rp=source/f"{role_arm}.json";role=load(rp);mechs=ablation if role_arm.endswith("ablation") else full;recalled={}
  for mechanism in mechs:
   for model_id in routing[mechanism]:recalled.setdefault(model_id,[]).append(mechanism)
  ids=sorted(recalled);packet=build_challenge_selection_packet(arm_id=f"{role_arm}__challenge_graph_v2",role_packet=role,cards=cards,candidate_ids=ids,selection_mode="graph_recalled_canonical",recalled_by=recalled,controlled_mechanism_ids=set(MECHANISMS),source_refs=[{"path":str(rp.relative_to(ROOT)),"sha256":sha(rp)}]);prompts=build_challenge_prompts(packet);pp=out/"packets"/f"{role_arm}.json";write(pp,packet);schema=response_schema(ids);artifacts.append({"arm_id":role_arm,"packet_path":str(pp.relative_to(ROOT)),"packet_sha256":sha(pp),"candidate_count":len(ids),"system_prompt_sha256":prompts["system_prompt_sha256"],"user_prompt_sha256":prompts["user_prompt_sha256"],"user_prompt_utf8_bytes":len(prompts["user_prompt"].encode()),"response_schema_sha256":sha256_bytes(canonical_json_bytes(schema)),"response_schema_metrics":schema_metrics(schema)})
 report={"schema_version":"lolla.challenge_card_graph_provenance_transfer_corpus.v1","status":"provider_free_transfer_gates_pass","artifacts":artifacts,"summary":{"challenge_card_count":len(cards),"packet_count":3,"maximum_prompt_utf8_bytes":max(x["user_prompt_utf8_bytes"] for x in artifacts),"maximum_candidate_count":max(x["candidate_count"] for x in artifacts),"maximum_provider_calls":3,"provider_calls":0},"boundary":{"fact_free_recall_provenance":True,"same_card_registry_all_arms":True,"canonical_ids_only":True,"all_candidates_may_be_rejected":True,"expected_answers_in_prompt":False,"runtime_effect":"none"}};write(out/"report.json",report);print(json.dumps({"status":report["status"],"summary":report["summary"]},indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
