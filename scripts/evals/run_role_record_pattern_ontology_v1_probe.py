#!/usr/bin/env python3
"""Run the frozen six-arm ontology-guided pattern probe."""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))

from engine.system_b.reasoning_pattern_role_record_interpreter_v2 import build_prompts_v2, compile_response_v2, response_schema_v2
from engine.system_b.reasoning_pattern_shadow import normalized_projection_signature
from engine.system_b.reasoning_process_views import canonical_json_bytes, sha256_bytes
from scripts.evals.reasoning_process_position_decomposition_transport import run_decomposed_task
from scripts.evals.run_conversation_state_microtask_probe import _load_env

ARMS=("registry_source_first","registry_provider","registry_reversal_ablation","housing_source_first","housing_provider","housing_reversal_ablation")
REPORT="research/role-record-pattern-ontology-v1-corpus-2026-07-12/report.json"
TARGET="docs/evals/role-record-pattern-ontology-v1-target.json"

def load(p): return json.loads(Path(p).read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v): Path(p).write_text(json.dumps(v,indent=2,sort_keys=True)+"\n")

def validate(contract, path):
    if contract.get("status") != "frozen_before_exactly_six_no_retry_calls" or contract["budget"]["maximum_provider_calls"] != 6 or contract["budget"]["automatic_retries"] != 0: raise RuntimeError("contract not frozen")
    for x in contract["frozen_inputs"]:
        if sha(ROOT/x["path"]) != x["sha256"]: raise RuntimeError("frozen input drifted")
    report=load(ROOT/REPORT); schema_sha=sha256_bytes(canonical_json_bytes(response_schema_v2()))
    if [x["arm_id"] for x in report["artifacts"]] != list(ARMS): raise RuntimeError("arm order drifted")
    for x in report["artifacts"]:
        packet=load(ROOT/x["packet_path"]); prompts=build_prompts_v2(packet)
        if sha(ROOT/x["packet_path"]) != x["packet_sha256"] or prompts["system_prompt_sha256"] != x["system_prompt_sha256"] or prompts["user_prompt_sha256"] != x["user_prompt_sha256"] or schema_sha != x["response_schema_sha256"]: raise RuntimeError("request drifted")
    return report

def nodes(call):
    compiled=call.get("compiled")
    return set() if not compiled else {(x["mechanism_id"],x["subject_scope"],x["state"]) for x in compiled["routing_projection"]["pattern_nodes"]}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--contract",type=Path,required=True); ap.add_argument("--authorization",type=Path); ap.add_argument("--env-file",type=Path); ap.add_argument("--output-dir",type=Path); ap.add_argument("--dry-run",action="store_true"); a=ap.parse_args()
    cp=a.contract.resolve(); c=load(cp); report=validate(c,cp)
    if a.dry_run: print(json.dumps({"status":"ontology_probe_contract_valid","provider_calls":0},indent=2)); return 0
    auth=load(a.authorization.resolve()); expected={"schema_version":"lolla.role_record_pattern_ontology_probe_authorization.v1","status":"authorized_once_after_ontology_and_adversarial_gates","contract_path":str(cp.relative_to(ROOT)),"contract_sha256":sha(cp),"run_id":c["run_id"],"maximum_provider_calls":6,"automatic_retries":0,"fallback_models":0,"evaluator_calls":0,"embedding_calls":0,"graph_calls":0,"runtime_calls":0}
    if auth != expected: raise RuntimeError("authorization drifted")
    out=a.output_dir.resolve()
    if not out.is_dir() or (out/"result.json").exists() or list(out.glob("call-*-started.json")): raise RuntimeError("output absent, complete, or started")
    _load_env(a.env_file.resolve()); artifacts={x["arm_id"]:x for x in report["artifacts"]}; calls=[]
    for i,arm in enumerate(ARMS,1):
        packet=load(ROOT/artifacts[arm]["packet_path"]); prompts=build_prompts_v2(packet); write(out/f"call-{i:02d}-started.json",{"run_id":c["run_id"],"task_id":arm,"automatic_retries":0})
        call=run_decomposed_task(task_id=arm,contract=c,prompts=prompts,schema=response_schema_v2(),response_schema_name="lolla_reasoning_ontology_v1",compile_candidate=lambda candidate,p=packet:compile_response_v2(response=candidate,packet=p,producer_kind="model_operator_eval",producer_id=c["job"]["model"]))
        write(out/f"call-{i:02d}-result.json",call); calls.append(call)
    by={x["task_id"]:x for x in calls}; target=load(ROOT/TARGET); full={tuple(x) for x in target["expected_unresolved"]}; ablated={tuple(x) for x in target["expected_ablation_unresolved"]}
    exact={arm:nodes(by[arm])==(ablated if arm.endswith("ablation") else full) for arm in ARMS}; cases={}
    for case in ("registry","housing"):
        s,p,a1=(by[f"{case}_{suffix}"] for suffix in ("source_first","provider","reversal_ablation")); sn,pn,an=nodes(s),nodes(p),nodes(a1)
        cases[case]={"invariant":sn==pn and bool(s.get("compiled")) and bool(p.get("compiled")) and normalized_projection_signature(s["compiled"])==normalized_projection_signature(p["compiled"]),"protected_preserved":any(x[0]=="missing_reversal_condition" for x in sn) and any(x[0]=="missing_reversal_condition" for x in pn),"selective_ablation":an=={x for x in sn if x[0]!="missing_reversal_condition"}}
    gates={"operational":all(x.get("operational_status")=="ok" and x.get("compiled") for x in calls),"prospective_targets":all(exact.values()),"invariance":all(x["invariant"] for x in cases.values()),"protected":all(x["protected_preserved"] for x in cases.values()),"selective_ablation":all(x["selective_ablation"] for x in cases.values())}
    result={"schema_version":"lolla.role_record_pattern_ontology_probe_result.v1","status":"frozen_probe_preserved","calls":calls,"evaluation":{"status":"all_gates_pass" if all(gates.values()) else "one_or_more_gates_fail","gates":gates,"exact_target_by_arm":exact,"cases":cases,"observed":{arm:[list(x) for x in sorted(nodes(by[arm]))] for arm in ARMS},"scalar_score":None},"provider_request_count":sum(x.get("provider_calls",0) for x in calls),"estimated_cost_usd":round(sum(float(x.get("estimated_cost_usd") or 0) for x in calls),12),"boundary":c["boundary"]}
    write(out/"result.json",result); print(json.dumps({"provider_request_count":result["provider_request_count"],"estimated_cost_usd":result["estimated_cost_usd"],"evaluation":result["evaluation"]},indent=2,sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
