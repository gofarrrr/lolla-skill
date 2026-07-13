#!/usr/bin/env python3
"""Run the frozen three-arm housing challenge-card transfer probe."""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT)not in sys.path:sys.path.insert(0,str(ROOT))
from engine.system_b.canonical_model_selection import build_challenge_prompts,compile_response,response_schema
from engine.system_b.reasoning_process_views import canonical_json_bytes,sha256_bytes
from scripts.evals.reasoning_process_position_decomposition_transport import run_decomposed_task
from scripts.evals.run_conversation_state_microtask_probe import _load_env
REPORT="research/challenge-card-graph-provenance-transfer-corpus-2026-07-12/report.json";TARGET="docs/evals/challenge-card-graph-provenance-transfer-target-v1.json";ARMS=("housing_source_first","housing_provider","housing_reversal_ablation")
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,indent=2,sort_keys=True)+"\n")
def validate(c,cp):
 if c.get("status")!="frozen_before_exactly_three_no_retry_calls" or c["budget"]["maximum_provider_calls"]!=3 or c["budget"]["automatic_retries"]!=0:raise RuntimeError("contract not frozen")
 for x in c["frozen_inputs"]:
  if sha(ROOT/x["path"])!=x["sha256"]:raise RuntimeError("frozen input drifted")
 report=load(ROOT/REPORT);items={x["arm_id"]:x for x in report["artifacts"]}
 for arm in ARMS:
  x=items[arm];p=load(ROOT/x["packet_path"]);pr=build_challenge_prompts(p);ids=[v["model_id"] for v in p["candidate_cards"]]
  if sha(ROOT/x["packet_path"])!=x["packet_sha256"] or pr["system_prompt_sha256"]!=x["system_prompt_sha256"] or pr["user_prompt_sha256"]!=x["user_prompt_sha256"] or sha256_bytes(canonical_json_bytes(response_schema(ids)))!=x["response_schema_sha256"]:raise RuntimeError("request drifted")
 return items
def chosen(call,disposition="selected"):return {x["model_id"] for x in (call.get("compiled")or{}).get("selections",[]) if x["disposition"]==disposition}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--contract",type=Path,required=True);ap.add_argument("--authorization",type=Path);ap.add_argument("--env-file",type=Path);ap.add_argument("--output-dir",type=Path);ap.add_argument("--dry-run",action="store_true");a=ap.parse_args();cp=a.contract.resolve();c=load(cp);items=validate(c,cp)
 if a.dry_run:print(json.dumps({"status":"challenge_card_transfer_contract_valid","provider_calls":0},indent=2));return 0
 auth=load(a.authorization.resolve());expected={"schema_version":"lolla.challenge_card_graph_provenance_transfer_probe_authorization.v1","status":"authorized_once_after_challenge_card_provenance_and_transfer_gates","contract_path":str(cp.relative_to(ROOT)),"contract_sha256":sha(cp),"run_id":c["run_id"],"maximum_provider_calls":3,"automatic_retries":0,"fallback_models":0,"evaluator_calls":0,"embedding_calls":0,"graph_calls":0,"runtime_calls":0}
 if auth!=expected:raise RuntimeError("authorization drifted")
 out=a.output_dir.resolve()
 if not out.is_dir()or(out/"result.json").exists()or list(out.glob("call-*-started.json")):raise RuntimeError("output absent, complete, or started")
 _load_env(a.env_file.resolve());calls=[]
 for i,arm in enumerate(ARMS,1):
  p=load(ROOT/items[arm]["packet_path"]);pr=build_challenge_prompts(p);ids=[x["model_id"] for x in p["candidate_cards"]];write(out/f"call-{i:02d}-started.json",{"run_id":c["run_id"],"task_id":arm,"automatic_retries":0});call=run_decomposed_task(task_id=arm,contract=c,prompts=pr,schema=response_schema(ids),response_schema_name=f"lolla_challenge_transfer_{i}",compile_candidate=lambda candidate,p=p:compile_response(response=candidate,packet=p));write(out/f"call-{i:02d}-result.json",call);calls.append(call)
 by={x["task_id"]:x for x in calls};target=load(ROOT/TARGET);s,p,a1=(chosen(by[x])for x in ARMS);protected=set(target["protected_reversal_models"]);unsupported=set(target["unsupported_active_models"]);gates={"operational":all(x.get("operational_status")=="ok"and x.get("compiled")for x in calls),"canonical_custody":all(not(x.get("compiled")or{}).get("invented_ids")for x in calls),"source_provider_invariance":s==p,"premortem_source_provider":"premortem"in s and"premortem"in p,"protected_absent_ablation":not bool(a1&protected),"unsupported_not_selected":not bool((s|p|a1)&unsupported)};result={"schema_version":"lolla.challenge_card_graph_provenance_transfer_probe_result.v1","status":"frozen_probe_preserved","calls":calls,"evaluation":{"status":"all_gates_pass"if all(gates.values())else"one_or_more_gates_fail","gates":gates,"selected":{"source":sorted(s),"provider":sorted(p),"ablation":sorted(a1)},"ambiguous":{arm:sorted(chosen(by[arm],"ambiguous"))for arm in ARMS},"scalar_score":None},"provider_request_count":sum(x.get("provider_calls",0)for x in calls),"estimated_cost_usd":round(sum(float(x.get("estimated_cost_usd")or 0)for x in calls),12),"boundary":c["boundary"]};write(out/"result.json",result);print(json.dumps({"provider_request_count":result["provider_request_count"],"estimated_cost_usd":result["estimated_cost_usd"],"evaluation":result["evaluation"]},indent=2,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
