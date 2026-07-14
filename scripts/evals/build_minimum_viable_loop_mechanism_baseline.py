#!/usr/bin/env python3
"""Build the provider-free three-case mechanism-bridge baseline."""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT)not in sys.path:sys.path.insert(0,str(ROOT))
from engine.system_b.reasoning_mechanism_ontology import MECHANISMS
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(v,indent=2,sort_keys=True)+"\n")
PACKET_ROOT="research/role-record-pattern-invariance-corpus-2026-07-12/packets"
MUSEUM_ROOT="research/exhaustive-candidate-assessment-transfer-corpus-2026-07-12/packets"
def statuses(call):return {x["mechanism_id"]:x["joint_status"]for x in(call.get("candidate_payload")or{}).get("assessments",[])}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--target",type=Path,required=True);ap.add_argument("--output",type=Path,required=True);a=ap.parse_args();target=load(a.target.resolve())
 full=target["source_reviewed_statuses"]["full"];ablation=target["source_reviewed_statuses"]["reversal_ablation"]
 if set(full)!=set(MECHANISMS)or set(ablation)!=set(MECHANISMS)or len(full)!=9:raise RuntimeError("source-reviewed mechanism coverage invalid")
 packet_paths={
  "registry_source_first":f"{PACKET_ROOT}/registry_source_first.json","registry_provider":f"{PACKET_ROOT}/registry_provider.json","registry_reversal_ablation":f"{PACKET_ROOT}/registry_reversal_ablation.json",
  "housing_source_first":f"{PACKET_ROOT}/housing_source_first.json","housing_provider":f"{PACKET_ROOT}/housing_provider.json","housing_reversal_ablation":f"{PACKET_ROOT}/housing_reversal_ablation.json",
  "museum_source_first":f"{MUSEUM_ROOT}/museum_source_first.json","museum_provider":f"{MUSEUM_ROOT}/museum_provider.json","museum_reversal_ablation":f"{MUSEUM_ROOT}/museum_reversal_ablation.json"}
 artifacts=[]
 for arm,path in packet_paths.items():
  packet=load(ROOT/path);roles=packet["role_records"]
  if [x["role"]for x in roles]!=["starting","current","qualification"]or len({x["role_record_id"]for x in roles})!=3:raise RuntimeError(f"role custody invalid: {arm}")
  serialized=json.dumps(packet)
  if "source_evidence\""in serialized or packet["boundary"].get("raw_conversation_included")or packet["boundary"].get("source_evidence_text_included",False):raise RuntimeError(f"fact boundary invalid: {arm}")
  artifacts.append({"arm_id":arm,"packet_path":path,"packet_sha256":sha(ROOT/path),"role_record_ids":[x["role_record_id"]for x in roles],"ablation_active":bool(packet.get("ablation",{}).get("active",arm.endswith("ablation")))})
 preserved=load(ROOT/"research/role-record-pattern-ontology-v1-probe-2026-07-12/result.json");calls={x["task_id"]:x for x in preserved["calls"]};protected=target["protected_mechanism"];persistent=target["persistent_mechanism"];case_results={}
 for case in target["cases"]:
  if case["case_id"].endswith("museum-ai-license"):
   case_results[case["case_id"]]={"status":"provider_probe_required","provider_calls_already_made":0,"revised_gates":None};continue
  s,p,ab=(statuses(calls[case[k]])for k in("source_arm","provider_arm","ablation_arm"));noise_source=sorted(k for k,v in s.items()if v=="unresolved"and full[k]!="unresolved");noise_provider=sorted(k for k,v in p.items()if v=="unresolved"and full[k]!="unresolved");noise_ablation=sorted(k for k,v in ab.items()if v=="unresolved"and ablation[k]!="unresolved")
  gates={"protected_source_provider":s.get(protected)==p.get(protected)=="unresolved","protected_removed_ablation":ab.get(protected)!="unresolved","persistent_all_arms":s.get(persistent)==p.get(persistent)==ab.get(persistent)=="unresolved","complete_assessment_coverage":set(s)==set(p)==set(ab)==set(MECHANISMS),"bounded_noise":max(len(noise_source),len(noise_provider),len(noise_ablation))<=2}
  case_results[case["case_id"]]={"status":"revised_mechanism_gates_pass"if all(gates.values())else"revised_mechanism_gates_fail","revised_gates":gates,"additional_unresolved_noise":{"source":noise_source,"provider":noise_provider,"ablation":noise_ablation},"provider_calls_already_made":3}
 report={"schema_version":"lolla.minimum_viable_loop_mechanism_baseline_report.v1","status":"phase1_provider_free_baseline_pass_museum_transfer_pending"if all(x["status"]=="revised_mechanism_gates_pass"for x in case_results.values()if x["revised_gates"]is not None)else"phase1_baseline_fail","target_path":str(a.target.resolve().relative_to(ROOT)),"target_sha256":sha(a.target.resolve()),"artifacts":artifacts,"case_results":case_results,"summary":{"case_count":3,"arm_count":9,"preserved_cases_reinterpreted":2,"new_transfer_cases_pending":1,"new_provider_calls":0,"protected_mechanism":protected,"persistent_mechanism":persistent},"decision":{"exact_full_set_invariance_required":False,"protected_and_ablation_gates_required":True,"additional_controlled_noise_preserved":True,"museum_provider_probe_authorized":False,"next_action":"Freeze one three-call exhaustive ontology probe for museum source/provider/ablation packets."},"non_claims":["revised_gates_do_not_rewrite_preserved_outputs","bounded_noise_is_not_semantic_correctness","not_runtime_authorization"]};write(a.output.resolve()/"report.json",report);print(json.dumps({"status":report["status"],"summary":report["summary"],"case_results":case_results},indent=2));return 0 if report["status"].startswith("phase1_provider_free")else 1
if __name__=="__main__":raise SystemExit(main())
