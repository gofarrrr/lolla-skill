#!/usr/bin/env python3
"""Build source/provider/status-ablation mechanism packets for the independent useful case."""
from __future__ import annotations
import argparse,copy,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT)not in sys.path:sys.path.insert(0,str(ROOT))
from engine.system_b.reasoning_pattern_role_record_interpreter import ROLE_ORDER,build_role_record_pattern_input
from engine.system_b.reasoning_pattern_role_record_interpreter_v2 import build_prompts_v2,response_schema_v2
from engine.system_b.reasoning_process_contracts import schema_metrics
from engine.system_b.reasoning_process_views import canonical_json_bytes,sha256_bytes
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(v,indent=2,sort_keys=True)+"\n")
def ordered(mapping):return [mapping[r]["observations"][0]for r in ROLE_ORDER]
def ablate(records):
 r=copy.deepcopy(records);q=r[2];q["role_record_id"]+="-status-ablation";q["observation_id"]=q["role_record_id"];alias=q["source_evidence_ids"][0];q["role_interpretation"]="No independent-demand gate has been defined, so the broader validation claim remains unsupported outside the pilot channel.";q["source_evidence_ids"]=[alias];q["source_evidence"]=[];q["stance_components"]=[{"role":"qualification","source_evidence_id":alias,"stance_expression_kind":"uncertain_or_undecided","stance_object_interpretation":"The broader validation claim lacks an independent-demand gate outside the pilot channel.","stance_object_kind":"belief_or_assessment"}];q["fidelity_note"]="Synthetic sensitivity control preserves the missing independent-demand gate while removing retailer prestige and status-signal meaning.";q["limitations"]="Counterfactual semantic ablation; not a source claim.";return r
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--output",type=Path,required=True);a=ap.parse_args();out=a.output.resolve();source_path=ROOT/"research/independent-phase5-useful-role-case-2026-07-12/compiled-source-review-target.json";provider_path=ROOT/"research/independent-phase5-role-extraction-probe-2026-07-12/result.json";source=ordered(load(source_path)["role_compiled"]);case=next(x for x in load(provider_path)["cases"]if x["case_id"]=="phase5-independent-useful-retailer-pilot");provider_roles=case["joined"]["records"][0]["role_observations"];provider=[provider_roles[r]for r in ROLE_ORDER];arms=[("independent_useful_source",source,False),("independent_useful_provider",provider,False),("independent_useful_status_ablation",ablate(source),True)];artifacts=[]
 for arm,records,is_ablation in arms:
  refs=[{"path":str((source_path if arm!="independent_useful_provider"else provider_path).relative_to(ROOT)),"sha256":sha(source_path if arm!="independent_useful_provider"else provider_path)}];packet=build_role_record_pattern_input(case_id="phase5-independent-useful-retailer-pilot",arm_id=arm,records=records,source_refs=refs,ablation={"active":is_ablation,"kind":"remove_status_signal_meaning"if is_ablation else"none","note":"Preserves missing independent-demand gate."if is_ablation else""});prompts=build_prompts_v2(packet);pp=out/"packets"/f"{arm}.json";write(pp,packet);artifacts.append({"arm_id":arm,"packet_path":str(pp.relative_to(ROOT)),"packet_sha256":sha(pp),"system_prompt_sha256":prompts["system_prompt_sha256"],"user_prompt_sha256":prompts["user_prompt_sha256"],"response_schema_sha256":sha256_bytes(canonical_json_bytes(response_schema_v2())),"response_schema_metrics":schema_metrics(response_schema_v2()),"user_prompt_utf8_bytes":len(prompts["user_prompt"].encode())})
 report={"schema_version":"lolla.independent_useful_mechanism_corpus.v1","status":"provider_free_independent_useful_mechanism_corpus_pass","artifacts":artifacts,"summary":{"packet_count":3,"maximum_prompt_utf8_bytes":max(x["user_prompt_utf8_bytes"]for x in artifacts),"maximum_provider_calls":3,"provider_calls":0},"boundary":{"protected_mechanism":"status_signal_used_as_evidence","persistent_mechanisms":["acknowledged_constraint_not_gated","counterpressure_acknowledged_not_integrated"],"expected_answers_in_prompt":False,"deterministic_semantic_mapping":False,"runtime_effect":"none"}};write(out/"report.json",report);print(json.dumps({"status":report["status"],"summary":report["summary"]},indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
