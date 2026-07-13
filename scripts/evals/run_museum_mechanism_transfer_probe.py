#!/usr/bin/env python3
"""Run frozen three-arm museum mechanism transfer probe."""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT)not in sys.path:sys.path.insert(0,str(ROOT))
from engine.system_b.reasoning_pattern_role_record_interpreter_v2 import build_prompts_v2,compile_response_v2,response_schema_v2
from engine.system_b.reasoning_process_views import canonical_json_bytes,sha256_bytes
from scripts.evals.reasoning_process_position_decomposition_transport import run_decomposed_task
from scripts.evals.run_conversation_state_microtask_probe import _load_env
REPORT="research/museum-mechanism-transfer-corpus-2026-07-12/report.json";TARGET="docs/evals/minimum-viable-loop-mechanism-baseline-v1.json";ARMS=("museum_source_first","museum_provider","museum_reversal_ablation")
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,indent=2,sort_keys=True)+"\n")
def validate(c,cp):
 if c.get("status")!="frozen_before_exactly_three_no_retry_calls"or c["budget"]["maximum_provider_calls"]!=3 or c["budget"]["automatic_retries"]!=0:raise RuntimeError("contract not frozen")
 for x in c["frozen_inputs"]:
  if sha(ROOT/x["path"])!=x["sha256"]:raise RuntimeError("frozen input drifted")
 items={x["arm_id"]:x for x in load(ROOT/REPORT)["artifacts"]};schema_sha=sha256_bytes(canonical_json_bytes(response_schema_v2()))
 for arm in ARMS:
  x=items[arm];p=load(ROOT/x["packet_path"]);pr=build_prompts_v2(p)
  if sha(ROOT/x["packet_path"])!=x["packet_sha256"]or pr["system_prompt_sha256"]!=x["system_prompt_sha256"]or pr["user_prompt_sha256"]!=x["user_prompt_sha256"]or schema_sha!=x["response_schema_sha256"]:raise RuntimeError("request drifted")
 return items
def status(call):return {x["mechanism_id"]:x["joint_status"]for x in(call.get("candidate_payload")or{}).get("assessments",[])}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--contract",type=Path,required=True);ap.add_argument("--authorization",type=Path);ap.add_argument("--env-file",type=Path);ap.add_argument("--output-dir",type=Path);ap.add_argument("--dry-run",action="store_true");a=ap.parse_args();cp=a.contract.resolve();c=load(cp);items=validate(c,cp)
 if a.dry_run:print(json.dumps({"status":"museum_mechanism_transfer_contract_valid","provider_calls":0},indent=2));return 0
 auth=load(a.authorization.resolve());expected={"schema_version":"lolla.museum_mechanism_transfer_probe_authorization.v1","status":"authorized_once_after_phase1_baseline_and_museum_local_gates","contract_path":str(cp.relative_to(ROOT)),"contract_sha256":sha(cp),"run_id":c["run_id"],"maximum_provider_calls":3,"automatic_retries":0,"fallback_models":0,"evaluator_calls":0,"embedding_calls":0,"graph_calls":0,"runtime_calls":0}
 if auth!=expected:raise RuntimeError("authorization drifted")
 out=a.output_dir.resolve()
 if not out.is_dir()or(out/"result.json").exists()or list(out.glob("call-*-started.json")):raise RuntimeError("output absent, complete, or started")
 _load_env(a.env_file.resolve());calls=[]
 for i,arm in enumerate(ARMS,1):
  p=load(ROOT/items[arm]["packet_path"]);pr=build_prompts_v2(p);write(out/f"call-{i:02d}-started.json",{"run_id":c["run_id"],"task_id":arm,"automatic_retries":0});call=run_decomposed_task(task_id=arm,contract=c,prompts=pr,schema=response_schema_v2(),response_schema_name=f"lolla_museum_mechanism_{i}",compile_candidate=lambda candidate,p=p:compile_response_v2(response=candidate,packet=p,producer_kind="model_operator_eval",producer_id=c["job"]["model"]));write(out/f"call-{i:02d}-result.json",call);calls.append(call)
 by={x["task_id"]:x for x in calls};s,p,ab=(status(by[x])for x in ARMS);target=load(ROOT/TARGET);full=target["source_reviewed_statuses"]["full"];abl=target["source_reviewed_statuses"]["reversal_ablation"];protected=target["protected_mechanism"];persistent=target["persistent_mechanism"];noise=lambda observed,expected:sorted(k for k,v in observed.items()if v=="unresolved"and expected[k]!="unresolved");noises={"source":noise(s,full),"provider":noise(p,full),"ablation":noise(ab,abl)};gates={"operational":all(x.get("operational_status")=="ok"and x.get("compiled")for x in calls),"protected_source_provider":s.get(protected)==p.get(protected)=="unresolved","protected_removed_ablation":ab.get(protected)!="unresolved","persistent_all_arms":s.get(persistent)==p.get(persistent)==ab.get(persistent)=="unresolved","complete_assessment_coverage":len(s)==len(p)==len(ab)==9,"bounded_noise":max(map(len,noises.values()))<=2};result={"schema_version":"lolla.museum_mechanism_transfer_probe_result.v1","status":"frozen_probe_preserved","calls":calls,"evaluation":{"status":"all_revised_gates_pass"if all(gates.values())else"one_or_more_revised_gates_fail","gates":gates,"additional_unresolved_noise":noises,"statuses":{"source":s,"provider":p,"ablation":ab},"scalar_score":None},"provider_request_count":sum(x.get("provider_calls",0)for x in calls),"estimated_cost_usd":round(sum(float(x.get("estimated_cost_usd")or 0)for x in calls),12),"boundary":c["boundary"]};write(out/"result.json",result);print(json.dumps({"provider_request_count":result["provider_request_count"],"estimated_cost_usd":result["estimated_cost_usd"],"evaluation":result["evaluation"]},indent=2,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
