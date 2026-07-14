#!/usr/bin/env python3
"""Frozen one-case provider probe for two normalized turn-record architectures."""
from __future__ import annotations

import argparse, hashlib, json, os, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib import error, request

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))

from engine.system_b.conversation_event_harvesting import build_turn_pair_windows
from engine.system_b.conversation_state_candidate_pipeline import decompose_reviewed_handoff
from engine.system_b.conversation_state_candidates import build_source_catalog
from engine.system_b.conversation_turn_records import (
    build_consolidator_contract, build_single_reader_contract,
    build_turn_record_ledger, parse_turn_record,
)
from engine.system_b.pricing import estimate_chat_cost_usd, lookup_chat_price
from scripts.evals.replay_conversation_turn_record_architectures import _expected
from scripts.evals.run_conversation_state_microtask_probe import _load_env
from scripts.evals.run_fixed_safe_holdout_pool import _extract_json_object, _model_attribution

MODEL="google/gemini-3.1-flash-lite"
SCHEMA="lolla.conversation_turn_record_probe_contract.v1"
AUTH="lolla.conversation_turn_record_probe_authorization.v1"
RESULT="lolla.conversation_turn_record_probe_result.v1"

def _file_sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def _jsha(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def _write(p,v): Path(p).parent.mkdir(parents=True,exist_ok=True); Path(p).write_text(json.dumps(v,indent=2,ensure_ascii=False)+"\n")

def _context(case_path, lens_path):
    packet=json.loads(Path(case_path).read_text()); source_path=ROOT/packet["source"]["path"]
    text=source_path.read_text(); catalog=build_source_catalog(source_text=text,source_path=packet["source"]["path"])
    windows=build_turn_pair_windows(catalog); lens=json.loads(Path(lens_path).read_text())
    by_window={w.window_id:[e for e in lens["events"] if e["window_id"]==w.window_id and e["synthesis_eligible"]] for w in windows}
    return packet,text,catalog,windows,lens,by_window

def prepare(case_path:Path,lens_path:Path,out:Path):
    out=out.resolve(); packet,_text,_catalog,windows,_lens,by_window=_context(case_path,lens_path)
    jobs=[]
    for w in windows:
        for arch,micro in (
            ("single_reader",build_single_reader_contract(window=w)),
            ("three_lens_consolidation",build_consolidator_contract(window=w,input_events=by_window[w.window_id])),
        ):
            jobs.append({"job_id":f"{arch}--{w.window_id}","architecture":arch,"window_id":w.window_id,
                         "system_prompt_sha256":micro["system_prompt_sha256"],"user_prompt_sha256":micro["user_prompt_sha256"],
                         "schema_sha256":_jsha(micro["schema"]),"schema_metrics":micro["schema_metrics"],"input_event_count":len(micro["input_event_ids"])})
    contract={"schema_version":SCHEMA,"status":"frozen_before_calls","date":"2026-07-11","case_id":packet["case_id"],
              "repair_round":{"round":1,"maximum_rounds":1,"generic":True,"thresholds_changed":False,"measurement_correction":"source containment and compact synthesis payload bytes"},
              "case_path":str(case_path.resolve().relative_to(ROOT)),"case_sha256":_file_sha(case_path),
              "source_path":packet["source"]["path"],"source_sha256":_file_sha(ROOT/packet["source"]["path"]),
              "lens_ledger_path":str(lens_path.resolve().relative_to(ROOT)),"lens_ledger_sha256":_file_sha(lens_path),"jobs":jobs,
              "configuration":{"model":MODEL,"wire_mode":"json_object","temperature":0.0,"reasoning":{"enabled":False},
                               "max_tokens":1800,"timeout_seconds":90,"workers":4,"automatic_retries":0,"fallbacks":False,"response_healing":False},
              "success":{"operational_rate":1.0,"typed_rate":1.0,"invalid_items":0,"reviewed_move_survival_min":0.8,
                         "reviewed_thread_survival_min":0.8,"reviewed_claim_mode_survival_min":0.75,"target_item_budget":42,
                         "synthesis_payload_byte_budget":32000,"input_custody_invalid_windows":0},
              "budget":{"maximum_provider_calls":14,"cost_ceiling_usd":0.05},
              "practice_check":{"checked":"2026-07-11","model_page":"https://openrouter.ai/google/gemini-3.1-flash-lite",
                                "structured_outputs":"https://openrouter.ai/docs/guides/features/structured-outputs"},
              "locks":[{"path":"engine/system_b/conversation_turn_records.py","sha256":_file_sha(ROOT/"engine/system_b/conversation_turn_records.py")},
                       {"path":"scripts/evals/run_conversation_turn_record_probe.py","sha256":_file_sha(ROOT/"scripts/evals/run_conversation_turn_record_probe.py")},
                       {"path":"plans/conversation-turn-record-redesign-2026-07-11.md","sha256":_file_sha(ROOT/"plans/conversation-turn-record-redesign-2026-07-11.md")}],
              "non_claims":["development_probe_is_not_product_proof","local_survival_is_not_global_synthesis_quality","no_runtime_or_graph_authority"]}
    cp=out/"contract.json"; _write(cp,contract)
    _write(out/"authorization.json",{"schema_version":AUTH,"status":"authorized_under_active_goal","contract_sha256":_file_sha(cp),"maximum_provider_calls":14,"automatic_retries":0,"graph_calls":0})
    return contract

def validate(c,a,cp):
    if c["schema_version"]!=SCHEMA or c["status"]!="frozen_before_calls" or a["contract_sha256"]!=_file_sha(cp): raise ValueError("contract/auth invalid")
    for lock in c["locks"]:
        if _file_sha(ROOT/lock["path"])!=lock["sha256"]: raise ValueError("lock drift: "+lock["path"])
    if _file_sha(ROOT/c["case_path"])!=c["case_sha256"] or _file_sha(ROOT/c["lens_ledger_path"])!=c["lens_ledger_sha256"]: raise ValueError("case/lens drift")

def _call(job,c,windows,by_window):
    start=time.monotonic(); w=next(x for x in windows if x.window_id==job["window_id"])
    micro=build_single_reader_contract(window=w) if job["architecture"]=="single_reader" else build_consolidator_contract(window=w,input_events=by_window[w.window_id])
    key=os.getenv("LOLLA_OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")
    base={"job_id":job["job_id"],"architecture":job["architecture"],"window_id":job["window_id"],"requested_model":MODEL,
          "system_prompt_sha256":micro["system_prompt_sha256"],"user_prompt_sha256":micro["user_prompt_sha256"],"schema_sha256":_jsha(micro["schema"])}
    if not key:return {**base,"operational_status":"missing_api_key","provider_calls":0}
    body={"model":MODEL,"messages":[{"role":"system","content":micro["system_prompt"]},{"role":"user","content":micro["user_prompt"]}],
          "response_format":{"type":"json_object"},"provider":{"require_parameters":True,"allow_fallbacks":False},
          "temperature":0,"max_tokens":c["configuration"]["max_tokens"],"reasoning":{"enabled":False}}
    req=request.Request("https://openrouter.ai/api/v1/chat/completions",data=json.dumps(body).encode(),headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},method="POST")
    try:
        with request.urlopen(req,timeout=c["configuration"]["timeout_seconds"]) as r: provider=json.loads(r.read().decode())
    except error.HTTPError as exc:return {**base,"operational_status":f"http_error_{exc.code}","provider_calls":1,"duration_seconds":round(time.monotonic()-start,3)}
    except Exception as exc:return {**base,"operational_status":"provider_error","error_type":type(exc).__name__,"provider_calls":1,"duration_seconds":round(time.monotonic()-start,3)}
    choices=provider.get("choices",[]); choice=choices[0] if choices else {}; content=str(choice.get("message",{}).get("content","")); payload=_extract_json_object(content)
    typed,issues=parse_turn_record(payload); usage=provider.get("usage",{}); pt,ct,tt=usage.get("prompt_tokens"),usage.get("completion_tokens"),usage.get("total_tokens")
    served=str(provider.get("model","")); attribution=_model_attribution(MODEL,served); op=bool(choices) and all(isinstance(x,int) and x>0 for x in (pt,ct,tt)) and attribution in {"matched","served_version_alias"}
    price=lookup_chat_price("openrouter",MODEL); cost=estimate_chat_cost_usd(price=price,prompt_tokens=pt,completion_tokens=ct) if price and op else None
    return {**base,"operational_status":"ok" if op else "operational_failure","typed_status":"admitted" if typed and not issues else "quarantined",
            "candidate_payload":payload,"validation_issues":[x.to_dict() for x in issues],"served_model":served,"model_attribution":attribution,
            "prompt_tokens":pt,"completion_tokens":ct,"total_tokens":tt,"estimated_cost_usd":cost,"response_sha256":hashlib.sha256(content.encode()).hexdigest(),
            "provider_calls":1,"automatic_retries":0,"duration_seconds":round(time.monotonic()-start,3)}

def execute(cp,ap,env,out):
    cp,ap,out=cp.resolve(),ap.resolve(),out.resolve(); c=json.loads(cp.read_text());a=json.loads(ap.read_text());validate(c,a,cp);_load_env(env)
    packet,_text,catalog,windows,_lens,by_window=_context(ROOT/c["case_path"],ROOT/c["lens_ledger_path"])
    calls=out/"calls"
    if calls.exists() and any(calls.glob("*.json")):raise ValueError("refusing overwrite")
    results=[]
    with ThreadPoolExecutor(max_workers=c["configuration"]["workers"]) as pool:
        fs={pool.submit(_call,j,c,windows,by_window):j for j in c["jobs"]}
        for f in as_completed(fs): r=f.result();_write(calls/(r["job_id"]+".json"),r);results.append(r)
    migration=json.loads((ROOT/"research/conversation-state-recovery-v1-2026-07-11/atomic-migration.json").read_text())
    extracted=decompose_reviewed_handoff(packet,catalog=catalog,atomic_migrations=migration); expected=_expected(extracted); rows=[]
    source_by_id=catalog.by_id()
    def overlaps(left_id,right_id):
        left,right=source_by_id[left_id],source_by_id[right_id]
        return left.speaker==right.speaker and left.turn_index==right.turn_index and (left.text in right.text or right.text in left.text)
    def source_recall(expected_ids,observed_ids):
        return sum(any(overlaps(e,o) for o in observed_ids) for e in expected_ids)/len(expected_ids) if expected_ids else 1.0
    def claim_recall(expected_pairs,observed_pairs):
        return sum(any(mode==omode and overlaps(span,ospan) for ospan,omode in observed_pairs) for span,mode in expected_pairs)/len(expected_pairs) if expected_pairs else 1.0
    for arch in ("single_reader","three_lens_consolidation"):
        records={}
        for r in results:
            if r["architecture"]==arch and r.get("typed_status")=="admitted":
                value,issues=parse_turn_record(r["candidate_payload"])
                if value and not issues:records[r["window_id"]]=value
        ledger=build_turn_record_ledger(architecture=arch,case_id=packet["case_id"],catalog=catalog,windows=windows,records=records,input_events_by_window=by_window if arch=="three_lens_consolidation" else None)
        moves={s["span_id"] for i in ledger["items"] if i["kind"]=="directional_move" and i["event_snapshot"] for s in i["event_snapshot"]["resolved_source"]}
        threads={s["span_id"] for i in ledger["items"] if i["kind"]=="thread_signal" and i["event_snapshot"] for s in i["event_snapshot"]["resolved_source"]}
        claims={(s["span_id"],i["event_snapshot"]["claim_mode"]) for i in ledger["items"] if i["kind"]=="claim" and i["event_snapshot"] for s in i["event_snapshot"]["resolved_source"]}
        ac=[r for r in results if r["architecture"]==arch]; row={"architecture":arch,"expected_calls":7,"provider_calls":sum(r.get("provider_calls",0) for r in ac),
            "operational_rate":sum(r.get("operational_status")=="ok" for r in ac)/7,"typed_rate":sum(r.get("typed_status")=="admitted" for r in ac)/7,
            "reviewed_move_survival":source_recall(expected["moves"],moves),"reviewed_thread_survival":source_recall(expected["threads"],threads),
            "reviewed_claim_mode_survival":claim_recall(expected["claims"],claims),"item_count":ledger["metrics"]["item_count"],
            "serialized_item_bytes":ledger["metrics"]["serialized_item_bytes"],"synthesis_payload_bytes":ledger["metrics"]["synthesis_payload_bytes"],"invalid_items":ledger["metrics"]["invalid_item_count"],
            "input_custody_invalid_windows":ledger["metrics"]["input_custody_invalid_window_count"]}
        req=c["success"];row["passed"]=row["operational_rate"]==1 and row["typed_rate"]==1 and row["invalid_items"]==0 and row["reviewed_move_survival"]>=req["reviewed_move_survival_min"] and row["reviewed_thread_survival"]>=req["reviewed_thread_survival_min"] and row["reviewed_claim_mode_survival"]>=req["reviewed_claim_mode_survival_min"] and row["item_count"]<=req["target_item_budget"] and row["synthesis_payload_bytes"]<=req["synthesis_payload_byte_budget"] and row["input_custody_invalid_windows"]==0
        _write(out/"architectures"/arch/"turn-record-ledger.json",ledger);_write(out/"architectures"/arch/"result.json",row);rows.append(row)
    summary={"schema_version":RESULT,"status":"pass" if any(r["passed"] for r in rows) else "fail","case_id":packet["case_id"],"provider_calls":sum(r.get("provider_calls",0) for r in results),
             "automatic_retries":0,"estimated_cost_usd":round(sum(r.get("estimated_cost_usd") or 0 for r in results),8),"architectures":rows,"graph_calls":0,"runtime_modified":False}
    _write(out/"result.json",summary);return summary

def main():
    p=argparse.ArgumentParser();p.add_argument("--prepare",action="store_true");p.add_argument("--execute",action="store_true");p.add_argument("--case",type=Path);p.add_argument("--lens-ledger",type=Path);p.add_argument("--output-dir",type=Path,required=True);p.add_argument("--contract",type=Path);p.add_argument("--authorization",type=Path);p.add_argument("--env-file",type=Path);a=p.parse_args()
    print(json.dumps(prepare(a.case,a.lens_ledger,a.output_dir) if a.prepare else execute(a.contract,a.authorization,a.env_file,a.output_dir),indent=2))
if __name__=="__main__":main()
