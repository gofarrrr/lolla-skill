#!/usr/bin/env python3
"""Run two frozen independent v2.4.1 role-extraction probes."""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT)not in sys.path:sys.path.insert(0,str(ROOT))
from engine.system_b.reasoning_process_position_role_first_v24 import build_position_relation_packet_v24,build_position_relation_prompts_v24,build_position_starting_packet_v24,build_position_starting_prompts_v24,compile_position_relation_response_v24,compile_position_starting_response_v24,join_position_role_first_v24,position_relation_response_schema_v24,position_starting_response_schema_v24
from engine.system_b.reasoning_process_position_role_first_v241 import build_position_current_qualification_packet_v241,build_position_current_qualification_prompts_v241,compile_position_current_qualification_response_v241,position_current_qualification_response_schema_v241
from engine.system_b.reasoning_process_views import canonical_json_bytes,sha256_bytes
from scripts.evals.reasoning_process_position_decomposition_transport import run_decomposed_task
from scripts.evals.run_conversation_state_microtask_probe import _load_env
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(v,indent=2,sort_keys=True)+"\n")
def call_passed(x):return x.get("operational_status")=="ok"and x.get("compiled")is not None
def validate(c,cp):
 if c.get("status")!="frozen_before_at_most_six_no_retry_calls"or c["budget"]["maximum_provider_calls"]!=6 or c["budget"]["automatic_retries"]!=0:raise RuntimeError("contract not frozen")
 for x in c["frozen_inputs"]:
  if sha(ROOT/x["path"])!=x["sha256"]:raise RuntimeError("frozen input drifted")
 for job in c["jobs"]:
  if sha(ROOT/job["packet_path"])!=job["packet_sha256"]or sha(ROOT/job["target_report_path"])!=job["target_report_sha256"]:raise RuntimeError("case artifact drifted")
  w=load(ROOT/job["packet_path"]);sp=build_position_starting_prompts_v24(build_position_starting_packet_v24(wrapper=w,role="starting"));pp=build_position_current_qualification_prompts_v241(build_position_current_qualification_packet_v241(wrapper=w));expected={"starting":{"system_prompt_sha256":sp["system_prompt_sha256"],"user_prompt_sha256":sp["user_prompt_sha256"],"response_schema_sha256":sha256_bytes(canonical_json_bytes(position_starting_response_schema_v24("starting")))},"current_qualification":{"system_prompt_sha256":pp["system_prompt_sha256"],"user_prompt_sha256":pp["user_prompt_sha256"],"response_schema_sha256":sha256_bytes(canonical_json_bytes(position_current_qualification_response_schema_v241()))},"relation_response_schema_sha256":sha256_bytes(canonical_json_bytes(position_relation_response_schema_v24()))}
  if job["request_contracts"]!=expected:raise RuntimeError("request contract drifted")
 return {"status":"independent_phase5_role_extraction_contract_valid","provider_calls":0}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--contract",type=Path,required=True);ap.add_argument("--authorization",type=Path);ap.add_argument("--env-file",type=Path);ap.add_argument("--output-dir",type=Path);ap.add_argument("--dry-run",action="store_true");a=ap.parse_args();cp=a.contract.resolve();c=load(cp);v=validate(c,cp)
 if a.dry_run:print(json.dumps(v,indent=2));return 0
 auth=load(a.authorization.resolve());expected={"schema_version":"lolla.independent_phase5_role_extraction_probe_authorization.v1","status":"authorized_once_after_two_source_targets_and_local_gates","contract_path":str(cp.relative_to(ROOT)),"contract_sha256":sha(cp),"run_id":c["run_id"],"maximum_provider_calls":6,"automatic_retries":0,"fallback_models":0,"evaluator_calls":0,"embedding_calls":0,"graph_calls":0,"runtime_calls":0}
 if auth!=expected:raise RuntimeError("authorization drifted")
 out=a.output_dir.resolve()
 if not out.is_dir()or(out/"result.json").exists()or list(out.rglob("call-*-started.json")):raise RuntimeError("output absent, complete, or started")
 _load_env(a.env_file.resolve());all_calls=[];case_results=[]
 for job in c["jobs"]:
  case_out=out/job["case_id"];case_out.mkdir();w=load(ROOT/job["packet_path"]);single={**c,"job":{**c["model_route"],"case_id":job["case_id"]}}
  spacket=build_position_starting_packet_v24(wrapper=w,role="starting");sp=build_position_starting_prompts_v24(spacket);write(case_out/"call-01-started.json",{"task_id":"starting","case_id":job["case_id"],"automatic_retries":0});scall=run_decomposed_task(task_id=f"{job['case_id']}:starting",contract=single,prompts=sp,schema=position_starting_response_schema_v24("starting"),response_schema_name="lolla_phase5_starting",compile_candidate=lambda candidate,p=spacket:compile_position_starting_response_v24(response=candidate,packet=p,producer_kind="model_operator_eval",producer_id=c["model_route"]["model"]));write(case_out/"call-01-result.json",scall)
  ppacket=build_position_current_qualification_packet_v241(wrapper=w);pp=build_position_current_qualification_prompts_v241(ppacket);write(case_out/"call-02-started.json",{"task_id":"current_qualification","case_id":job["case_id"],"automatic_retries":0});pcall=run_decomposed_task(task_id=f"{job['case_id']}:current_qualification",contract=single,prompts=pp,schema=position_current_qualification_response_schema_v241(),response_schema_name="lolla_phase5_current_qualification",compile_candidate=lambda candidate,w=w:compile_position_current_qualification_response_v241(response=candidate,wrapper=w,producer_kind="model_operator_eval",producer_id=c["model_route"]["model"]));write(case_out/"call-02-result.json",pcall);calls=[scall,pcall];roles={}
  if scall.get("compiled"):roles["starting"]=scall["compiled"]
  if pcall.get("compiled"):roles.update(pcall["compiled"]["role_compiled"])
  relation=None;block=""
  if call_passed(scall)and call_passed(pcall)and set(roles)=={"starting","current","qualification"}:
   rpacket=build_position_relation_packet_v24(role_compiled_by_role=roles);rp=build_position_relation_prompts_v24(rpacket);write(case_out/"call-03-started.json",{"task_id":"relation","case_id":job["case_id"],"automatic_retries":0});rcall=run_decomposed_task(task_id=f"{job['case_id']}:relation",contract=single,prompts=rp,schema=position_relation_response_schema_v24(),response_schema_name="lolla_phase5_relation",compile_candidate=lambda candidate,p=rpacket:compile_position_relation_response_v24(response=candidate,packet=p,producer_kind="model_operator_eval",producer_id=c["model_route"]["model"]));write(case_out/"call-03-result.json",rcall);calls.append(rcall);relation=rcall.get("compiled");block=""if call_passed(rcall)else"relation_failed"
  else:block="role_admission_failed"
  joined=join_position_role_first_v24(role_compiled_by_role=roles,relation_compiled=relation)if set(roles)=={"starting","current","qualification"}else None;case_results.append({"case_id":job["case_id"],"calls":calls,"joined":joined,"relation_block_reason":block,"semantic_review_status":"source_first_review_required"});all_calls.extend(calls)
 result={"schema_version":"lolla.independent_phase5_role_extraction_probe_result.v1","status":"frozen_probe_preserved","cases":case_results,"provider_request_count":sum(x.get("provider_calls",0)for x in all_calls),"estimated_cost_usd":round(sum(float(x.get("estimated_cost_usd")or 0)for x in all_calls),12),"boundary":c["boundary"]};write(out/"result.json",result);print(json.dumps({"provider_request_count":result["provider_request_count"],"estimated_cost_usd":result["estimated_cost_usd"],"cases":[{"case_id":x["case_id"],"join_status":x["joined"].get("status")if x["joined"]else None,"block":x["relation_block_reason"]}for x in case_results]},indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
