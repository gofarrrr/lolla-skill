#!/usr/bin/env python3
"""Run frozen three-arm exhaustive candidate assessment transfer probe."""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT)not in sys.path:sys.path.insert(0,str(ROOT))
from engine.system_b.canonical_model_selection import build_exhaustive_prompts,compile_exhaustive_response,exhaustive_response_schema
from engine.system_b.reasoning_process_views import canonical_json_bytes,sha256_bytes
from scripts.evals.reasoning_process_position_decomposition_transport import run_decomposed_task
from scripts.evals.run_conversation_state_microtask_probe import _load_env
REPORT="research/exhaustive-candidate-assessment-transfer-corpus-2026-07-12/report.json";TARGET="docs/evals/exhaustive-candidate-assessment-transfer-target-v1.json";ARMS=("museum_source_first","museum_provider","museum_reversal_ablation")
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,indent=2,sort_keys=True)+"\n")
def validate(c,cp):
 if c.get("status")!="frozen_before_exactly_three_no_retry_calls"or c["budget"]["maximum_provider_calls"]!=3 or c["budget"]["automatic_retries"]!=0:raise RuntimeError("contract not frozen")
 for x in c["frozen_inputs"]:
  if sha(ROOT/x["path"])!=x["sha256"]:raise RuntimeError("frozen input drifted")
 items={x["arm_id"]:x for x in load(ROOT/REPORT)["artifacts"]}
 for arm in ARMS:
  x=items[arm];p=load(ROOT/x["packet_path"]);pr=build_exhaustive_prompts(p);ids=[v["model_id"]for v in p["candidate_cards"]]
  if sha(ROOT/x["packet_path"])!=x["packet_sha256"]or pr["system_prompt_sha256"]!=x["system_prompt_sha256"]or pr["user_prompt_sha256"]!=x["user_prompt_sha256"]or sha256_bytes(canonical_json_bytes(exhaustive_response_schema(ids)))!=x["response_schema_sha256"]:raise RuntimeError("request drifted")
 return items
def active(call):return set((call.get("compiled")or{}).get("active_model_ids",[]))
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--contract",type=Path,required=True);ap.add_argument("--authorization",type=Path);ap.add_argument("--env-file",type=Path);ap.add_argument("--output-dir",type=Path);ap.add_argument("--dry-run",action="store_true");a=ap.parse_args();cp=a.contract.resolve();c=load(cp);items=validate(c,cp)
 if a.dry_run:print(json.dumps({"status":"exhaustive_candidate_transfer_contract_valid","provider_calls":0},indent=2));return 0
 auth=load(a.authorization.resolve());expected={"schema_version":"lolla.exhaustive_candidate_assessment_transfer_probe_authorization.v1","status":"authorized_once_after_exhaustive_coverage_and_entailment_gates","contract_path":str(cp.relative_to(ROOT)),"contract_sha256":sha(cp),"run_id":c["run_id"],"maximum_provider_calls":3,"automatic_retries":0,"fallback_models":0,"evaluator_calls":0,"embedding_calls":0,"graph_calls":0,"runtime_calls":0}
 if auth!=expected:raise RuntimeError("authorization drifted")
 out=a.output_dir.resolve()
 if not out.is_dir()or(out/"result.json").exists()or list(out.glob("call-*-started.json")):raise RuntimeError("output absent, complete, or started")
 _load_env(a.env_file.resolve());calls=[]
 for i,arm in enumerate(ARMS,1):
  p=load(ROOT/items[arm]["packet_path"]);pr=build_exhaustive_prompts(p);ids=[x["model_id"]for x in p["candidate_cards"]];write(out/f"call-{i:02d}-started.json",{"run_id":c["run_id"],"task_id":arm,"automatic_retries":0});call=run_decomposed_task(task_id=arm,contract=c,prompts=pr,schema=exhaustive_response_schema(ids),response_schema_name=f"lolla_exhaustive_candidate_{i}",compile_candidate=lambda candidate,p=p:compile_exhaustive_response(response=candidate,packet=p));write(out/f"call-{i:02d}-result.json",call);calls.append(call)
 by={x["task_id"]:x for x in calls};target=load(ROOT/TARGET);s,p,a1=(active(by[x])for x in ARMS);must_not=set(target["must_not_be_applicable"]);coverage={arm:len((by[arm].get("compiled")or{}).get("assessments",[]))==items[arm]["candidate_count"]for arm in ARMS};gates={"operational":all(x.get("operational_status")=="ok"and x.get("compiled")for x in calls),"complete_coverage":all(coverage.values()),"canonical_custody":all(not(x.get("compiled")or{}).get("invented_ids")for x in calls),"source_provider_invariance":s==p,"premortem_source_provider":"premortem"in s and"premortem"in p,"ablation_no_active":not a1,"must_not_never_active":not bool((s|p|a1)&must_not)};statuses={arm:{x["model_id"]:x["status"]for x in(by[arm].get("compiled")or{}).get("assessments",[])}for arm in ARMS};result={"schema_version":"lolla.exhaustive_candidate_assessment_transfer_probe_result.v1","status":"frozen_probe_preserved","calls":calls,"evaluation":{"status":"all_gates_pass"if all(gates.values())else"one_or_more_gates_fail","gates":gates,"coverage":coverage,"active":{"source":sorted(s),"provider":sorted(p),"ablation":sorted(a1)},"statuses":statuses,"scalar_score":None},"provider_request_count":sum(x.get("provider_calls",0)for x in calls),"estimated_cost_usd":round(sum(float(x.get("estimated_cost_usd")or 0)for x in calls),12),"boundary":c["boundary"]};write(out/"result.json",result);print(json.dumps({"provider_request_count":result["provider_request_count"],"estimated_cost_usd":result["estimated_cost_usd"],"evaluation":result["evaluation"]},indent=2,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
