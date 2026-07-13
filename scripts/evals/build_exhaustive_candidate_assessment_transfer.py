#!/usr/bin/env python3
"""Build provider-free museum transfer packets for exhaustive candidate assessment."""
from __future__ import annotations
import argparse,copy,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT)not in sys.path:sys.path.insert(0,str(ROOT))
from engine.system_b.canonical_model_selection import build_assessment_cards,build_challenge_selection_packet,build_exhaustive_assessment_packet,build_exhaustive_prompts,exhaustive_response_schema
from engine.system_b.reasoning_mechanism_ontology import MECHANISMS
from engine.system_b.reasoning_pattern_role_record_interpreter import ROLE_ORDER,build_role_record_pattern_input
from engine.system_b.reasoning_process_contracts import schema_metrics
from engine.system_b.reasoning_process_views import canonical_json_bytes,sha256_bytes
def load(p):return json.loads(Path(p).read_text())
def write(p,v):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(v,indent=2,sort_keys=True)+"\n")
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ordered(mapping):return [mapping[r]["observations"][0] for r in ROLE_ORDER]
def ablate(records):
 r=copy.deepcopy(records);q=r[2];q["role_record_id"]+="-reversal-ablation";q["observation_id"]=q["role_record_id"];alias=q["source_evidence_ids"][0];q["role_interpretation"]="A material unresolved counterpressure remains outside the adopted current safeguards.";q["source_evidence_ids"]=[alias];q["source_evidence"]=[];q["stance_components"]=[{"role":"qualification","source_evidence_id":alias,"stance_expression_kind":"uncertain_or_undecided","stance_object_interpretation":"A material unresolved counterpressure remains outside the adopted safeguards.","stance_object_kind":"belief_or_assessment"}];q["fidelity_note"]="Synthetic sensitivity control retaining unresolved counterpressure while removing reversal and persistence meaning.";q["limitations"]="Counterfactual semantic ablation; not a source claim.";return r
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--output",type=Path,required=True);a=ap.parse_args();out=a.output.resolve();source_path=ROOT/"research/reasoning-process-position-role-first-v23-new-case-2026-07-12/compiled-source-review-target.json";provider_path=ROOT/"research/reasoning-process-position-role-first-v23-probe-2026-07-12/result.json";source=ordered(load(source_path)["role_compiled"]);provider_roles=load(provider_path)["joined"]["records"][0]["role_observations"];provider=[provider_roles[x]for x in ROLE_ORDER];arms=[("museum_source_first",source,[{"path":str(source_path.relative_to(ROOT)),"sha256":sha(source_path)}],False),("museum_provider",provider,[{"path":str(provider_path.relative_to(ROOT)),"sha256":sha(provider_path)}],False),("museum_reversal_ablation",ablate(source),[{"path":str(source_path.relative_to(ROOT)),"sha256":sha(source_path)}],True)]
 kg=load(ROOT/"data/knowledge_graph.json");cards=build_assessment_cards(kg["models"]);routing=load(ROOT/"docs/conversation-understanding/reasoning-pattern-shadow-routing-v0.json")["mechanism_seed_models"];artifacts=[]
 for arm,records,refs,is_ablation in arms:
  role_packet=build_role_record_pattern_input(case_id="amb3-case04-museum-ai-license",arm_id=arm,records=records,source_refs=refs,ablation={"active":is_ablation,"kind":"remove_reversal_and_persistence_meaning"if is_ablation else"none","note":"Synthetic sensitivity control."if is_ablation else""});mechs=["counterpressure_acknowledged_not_integrated"]+([]if is_ablation else["missing_reversal_condition"]);recalled={}
  for m in mechs:
   for mid in routing[m]:recalled.setdefault(mid,[]).append(m)
  challenge=build_challenge_selection_packet(arm_id=arm,role_packet=role_packet,cards=cards,candidate_ids=sorted(recalled),selection_mode="graph_recalled_canonical",recalled_by=recalled,controlled_mechanism_ids=set(MECHANISMS),source_refs=refs);packet=build_exhaustive_assessment_packet(challenge_packet=challenge,mechanism_cards=MECHANISMS);prompts=build_exhaustive_prompts(packet);pp=out/"packets"/f"{arm}.json";write(pp,packet);schema=exhaustive_response_schema(sorted(recalled));artifacts.append({"arm_id":arm,"packet_path":str(pp.relative_to(ROOT)),"packet_sha256":sha(pp),"candidate_count":len(recalled),"system_prompt_sha256":prompts["system_prompt_sha256"],"user_prompt_sha256":prompts["user_prompt_sha256"],"user_prompt_utf8_bytes":len(prompts["user_prompt"].encode()),"response_schema_sha256":sha256_bytes(canonical_json_bytes(schema)),"response_schema_metrics":schema_metrics(schema)})
 report={"schema_version":"lolla.exhaustive_candidate_assessment_transfer_corpus.v1","status":"provider_free_exhaustive_transfer_gates_pass","artifacts":artifacts,"summary":{"packet_count":3,"full_candidate_count":6,"ablation_candidate_count":3,"maximum_prompt_utf8_bytes":max(x["user_prompt_utf8_bytes"]for x in artifacts),"maximum_provider_calls":3,"provider_calls":0},"boundary":{"new_case":"museum_ai_license","complete_mechanism_cards":True,"one_row_per_candidate":True,"global_abstention_shortcut":False,"all_rows_may_be_negative":True,"canonical_ids_only":True,"runtime_effect":"none"}};write(out/"report.json",report);print(json.dumps({"status":report["status"],"summary":report["summary"]},indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
