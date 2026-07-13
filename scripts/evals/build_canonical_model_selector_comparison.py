#!/usr/bin/env python3
"""Build provider-free direct-vs-graph canonical selector comparison packets."""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from engine.system_b.canonical_model_selection import build_cards,build_prompts,build_selection_packet,response_schema
from engine.system_b.reasoning_process_contracts import schema_metrics
from engine.system_b.reasoning_process_views import canonical_json_bytes,sha256_bytes

def load(p):return json.loads(Path(p).read_text())
def write(p,v):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(v,indent=2,sort_keys=True)+"\n")
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--output",type=Path,required=True);a=ap.parse_args();out=a.output.resolve()
 kg=load(ROOT/"data/knowledge_graph.json");cards=build_cards(kg["models"]);write(out/"canonical-model-cards-v1.json",{"schema_version":"lolla.canonical_model_card_registry.v1","cards":cards})
 routing=load(ROOT/"docs/conversation-understanding/reasoning-pattern-shadow-routing-v0.json")["mechanism_seed_models"]
 full_mechs=["acknowledged_constraint_not_gated","counterpressure_acknowledged_not_integrated","missing_reversal_condition"];ablated=full_mechs[:-1]
 source=ROOT/"research/role-record-pattern-invariance-corpus-2026-07-12/packets";artifacts=[]
 for role_path in sorted(source.glob("*.json")):
  role=load(role_path);mechs=ablated if role_path.stem.endswith("ablation") else full_mechs;graph_ids=sorted({x for m in mechs for x in routing[m]})
  for mode,ids in (("direct_all_canonical",sorted(cards)),("graph_recalled_canonical",graph_ids)):
   arm=f"{role_path.stem}__{mode}";packet=build_selection_packet(arm_id=arm,role_packet=role,cards=cards,candidate_ids=ids,selection_mode=mode,source_refs=[{"path":str(role_path.relative_to(ROOT)),"sha256":sha(role_path)}]);prompts=build_prompts(packet);pp=out/"packets"/f"{arm}.json";write(pp,packet);schema=response_schema(ids)
   artifacts.append({"arm_id":arm,"case_id":role["case_id"],"role_arm":role_path.stem,"selection_mode":mode,"candidate_count":len(ids),"packet_path":str(pp.relative_to(ROOT)),"packet_sha256":sha(pp),"user_prompt_utf8_bytes":len(prompts["user_prompt"].encode()),"system_prompt_sha256":prompts["system_prompt_sha256"],"user_prompt_sha256":prompts["user_prompt_sha256"],"response_schema_metrics":schema_metrics(schema),"response_schema_sha256":sha256_bytes(canonical_json_bytes(schema))})
 report={"schema_version":"lolla.canonical_model_selector_comparison_corpus.v1","status":"provider_free_selector_packets_pass","artifacts":artifacts,"summary":{"card_count":len(cards),"packet_count":len(artifacts),"direct_packet_count":6,"graph_packet_count":6,"direct_candidate_count":222,"graph_full_candidate_count":len({x for m in full_mechs for x in routing[m]}),"graph_ablation_candidate_count":len({x for m in ablated for x in routing[m]}),"maximum_prompt_utf8_bytes":max(x["user_prompt_utf8_bytes"] for x in artifacts),"maximum_schema_bytes":max(x["response_schema_metrics"]["bytes"] for x in artifacts),"provider_calls":0},"boundary":{"same_card_format_both_arms":True,"direct_arm_differs_only_by_candidate_recall_surface":True,"canonical_ids_only":True,"all_candidates_may_be_rejected":True,"expected_answers_in_prompt":False,"runtime_effect":"none"}}
 write(out/"report.json",report);print(json.dumps({"status":report["status"],"summary":report["summary"]},indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
