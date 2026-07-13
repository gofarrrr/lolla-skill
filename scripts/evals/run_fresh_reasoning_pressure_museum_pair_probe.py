#!/usr/bin/env python3
"""Run frozen transcript-only versus pressure fresh-context museum pair."""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT)not in sys.path:sys.path.insert(0,str(ROOT))
from engine.system_b.fresh_reasoning_pressure import build_control_prompts,build_prompts,compile_control_response,compile_response,control_response_schema,response_schema
from engine.system_b.reasoning_process_views import canonical_json_bytes,sha256_bytes
from scripts.evals.reasoning_process_position_decomposition_transport import run_decomposed_task
from scripts.evals.run_conversation_state_microtask_probe import _load_env
REPORT="research/fresh-reasoning-pressure-museum-packet-2026-07-12/report.json"
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,indent=2,sort_keys=True)+"\n")
def validate(c,cp):
 if c.get("status")!="frozen_before_exactly_two_fresh_no_retry_calls"or c["budget"]["maximum_provider_calls"]!=2 or c["budget"]["automatic_retries"]!=0:raise RuntimeError("contract not frozen")
 for x in c["frozen_inputs"]:
  if sha(ROOT/x["path"])!=x["sha256"]:raise RuntimeError("frozen input drifted")
 report=load(ROOT/REPORT);control=load(ROOT/report["arms"]["control"]["packet_path"]);pressure=load(ROOT/report["arms"]["pressure"]["packet_path"]);cprompts=build_control_prompts(control);pprompts=build_prompts(pressure);ids=[x["model_id"]for x in pressure["pressure_portfolio"]]
 for name,p,pr,schema in(("control",control,cprompts,control_response_schema()),("pressure",pressure,pprompts,response_schema(ids))):
  x=report["arms"][name]
  if sha(ROOT/x["packet_path"])!=x["packet_sha256"]or pr["system_prompt_sha256"]!=x["system_prompt_sha256"]or pr["user_prompt_sha256"]!=x["user_prompt_sha256"]or sha256_bytes(canonical_json_bytes(schema))!=x["response_schema_sha256"]:raise RuntimeError("request drifted")
 if control["authoritative_conversation"]!=pressure["authoritative_conversation"]:raise RuntimeError("conversation mismatch")
 return report,control,pressure,cprompts,pprompts,ids
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--contract",type=Path,required=True);ap.add_argument("--authorization",type=Path);ap.add_argument("--env-file",type=Path);ap.add_argument("--output-dir",type=Path);ap.add_argument("--dry-run",action="store_true");a=ap.parse_args();cp=a.contract.resolve();c=load(cp);report,control,pressure,cprompts,pprompts,ids=validate(c,cp)
 if a.dry_run:print(json.dumps({"status":"fresh_reasoning_pressure_pair_contract_valid","provider_calls":0},indent=2));return 0
 auth=load(a.authorization.resolve());expected={"schema_version":"lolla.fresh_reasoning_pressure_pair_probe_authorization.v1","status":"authorized_once_after_phase4_pair_and_source_target_gates","contract_path":str(cp.relative_to(ROOT)),"contract_sha256":sha(cp),"run_id":c["run_id"],"maximum_provider_calls":2,"automatic_retries":0,"fallback_models":0,"evaluator_calls":0,"embedding_calls":0,"graph_calls":0,"runtime_calls":0}
 if auth!=expected:raise RuntimeError("authorization drifted")
 out=a.output_dir.resolve()
 if not out.is_dir()or(out/"result.json").exists()or list(out.glob("call-*-started.json")):raise RuntimeError("output absent, complete, or started")
 _load_env(a.env_file.resolve());calls=[]
 for i,(arm,p,pr,schema,compiler)in enumerate((("control",control,cprompts,control_response_schema(),lambda candidate:compile_control_response(response=candidate,packet=control)),("pressure",pressure,pprompts,response_schema(ids),lambda candidate:compile_response(response=candidate,packet=pressure))),1):
  write(out/f"call-{i:02d}-started.json",{"run_id":c["run_id"],"task_id":arm,"fresh_context":True,"automatic_retries":0});call=run_decomposed_task(task_id=arm,contract=c,prompts=pr,schema=schema,response_schema_name=f"lolla_fresh_reasoning_{arm}",compile_candidate=compiler);write(out/f"call-{i:02d}-result.json",call);calls.append(call)
 by={x["task_id"]:x for x in calls};pc=by["pressure"].get("compiled");cc=by["control"].get("compiled");gates={"both_operational":all(x.get("operational_status")=="ok"and x.get("compiled")for x in calls),"pressure_complete_dispositions":bool(pc)and pc["all_candidates_accounted_for"]and len(pc["candidate_dispositions"])==len(ids),"control_no_external_portfolio":bool(cc)and cc["external_pressure_portfolio_included"]is False,"self_contained_answers":bool(pc and pc["reconsidered_answer"].strip()and cc and cc["reconsidered_answer"].strip()),"rejected_no_material_effect":bool(pc)and all(x["effect"]=="no_material_effect"for x in pc["candidate_dispositions"]if x["disposition"]=="reject")};result={"schema_version":"lolla.fresh_reasoning_pressure_pair_probe_result.v1","status":"frozen_pair_preserved","calls":calls,"evaluation":{"status":"phase4_mechanical_gates_pass_source_review_required"if all(gates.values())else"phase4_mechanical_gate_failure","gates":gates,"disposition_counts":({d:sum(x["disposition"]==d for x in pc["candidate_dispositions"])for d in("apply","reject","park")}if pc else{}),"scalar_score":None,"phase5_value_status":"source_review_required"},"provider_request_count":sum(x.get("provider_calls",0)for x in calls),"estimated_cost_usd":round(sum(float(x.get("estimated_cost_usd")or 0)for x in calls),12),"boundary":c["boundary"]};write(out/"result.json",result);print(json.dumps({"provider_request_count":result["provider_request_count"],"estimated_cost_usd":result["estimated_cost_usd"],"evaluation":result["evaluation"]},indent=2,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
