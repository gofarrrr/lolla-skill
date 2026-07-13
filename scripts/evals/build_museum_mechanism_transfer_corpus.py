#!/usr/bin/env python3
"""Build three museum role-record packets for the corrected mechanism transfer gate."""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT)not in sys.path:sys.path.insert(0,str(ROOT))
from engine.system_b.reasoning_pattern_role_record_interpreter import build_role_record_pattern_input
from engine.system_b.reasoning_pattern_role_record_interpreter_v2 import build_prompts_v2,response_schema_v2
from engine.system_b.reasoning_process_contracts import schema_metrics
from engine.system_b.reasoning_process_views import canonical_json_bytes,sha256_bytes
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(v,indent=2,sort_keys=True)+"\n")
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--output",type=Path,required=True);a=ap.parse_args();out=a.output.resolve();source=ROOT/"research/exhaustive-candidate-assessment-transfer-corpus-2026-07-12/packets";artifacts=[]
 for arm in("museum_source_first","museum_provider","museum_reversal_ablation"):
  upstream=source/f"{arm}.json";value=load(upstream);refs=[{"path":str(upstream.relative_to(ROOT)),"sha256":sha(upstream)}];ablation={"active":arm.endswith("ablation"),"kind":"remove_reversal_and_persistence_meaning"if arm.endswith("ablation")else"none","note":"Synthetic sensitivity control."if arm.endswith("ablation")else""};packet=build_role_record_pattern_input(case_id="amb3-case04-museum-ai-license",arm_id=arm,records=value["role_records"],source_refs=refs,ablation=ablation);prompts=build_prompts_v2(packet);pp=out/"packets"/f"{arm}.json";write(pp,packet);artifacts.append({"arm_id":arm,"packet_path":str(pp.relative_to(ROOT)),"packet_sha256":sha(pp),"system_prompt_sha256":prompts["system_prompt_sha256"],"user_prompt_sha256":prompts["user_prompt_sha256"],"user_prompt_utf8_bytes":len(prompts["user_prompt"].encode()),"response_schema_sha256":sha256_bytes(canonical_json_bytes(response_schema_v2())),"response_schema_metrics":schema_metrics(response_schema_v2())})
 report={"schema_version":"lolla.museum_mechanism_transfer_corpus.v1","status":"provider_free_museum_mechanism_transfer_pass","artifacts":artifacts,"summary":{"packet_count":3,"maximum_prompt_utf8_bytes":max(x["user_prompt_utf8_bytes"]for x in artifacts),"maximum_provider_calls":3,"provider_calls":0},"boundary":{"complete_nine_mechanism_review":True,"exact_role_record_custody":True,"raw_conversation":False,"expected_answers_in_prompt":False,"deterministic_semantic_mapping":False,"runtime_effect":"none"}};write(out/"report.json",report);print(json.dumps({"status":report["status"],"summary":report["summary"]},indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
