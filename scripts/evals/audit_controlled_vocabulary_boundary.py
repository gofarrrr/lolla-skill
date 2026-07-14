#!/usr/bin/env python3
"""Provider-free audit of canonical model identity and selector reachability."""
from __future__ import annotations
import argparse, json, re, sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from engine.system_b.reasoning_mechanism_ontology import MECHANISMS

def norm(value): return re.sub(r"[^a-z0-9]+","",value.lower())
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",type=Path,required=True); a=ap.parse_args()
    kg=json.loads((ROOT/"data/knowledge_graph.json").read_text()); models=kg["models"]
    edges=json.loads((ROOT/"data/relationship_graph.json").read_text())
    chunks=json.loads((ROOT/"data/curated/compiled_chunks.json").read_text())["chunks"]
    routing=json.loads((ROOT/"docs/conversation-understanding/reasoning-pattern-shadow-routing-v0.json").read_text())["mechanism_seed_models"]
    names=defaultdict(list)
    for mid,m in models.items(): names[norm(m.get("display_name") or m.get("name") or mid)].append(mid)
    duplicate_names={k:v for k,v in names.items() if len(v)>1}
    graph_ids={x["source_model_id"] for x in edges}|{x["target_model_id"] for x in edges}
    chunk_ids={x["model_id"] for x in chunks}
    seed_ids={x for values in routing.values() for x in values}
    reasoning=defaultdict(set)
    for mid,m in models.items():
        for family in m.get("reasoning_types",[]): reasoning[family].add(mid)
    missing_seed=sorted(seed_ids-set(models)); missing_edge=sorted(graph_ids-set(models)); missing_chunk=sorted(chunk_ids-set(models))
    canonical_menu=[{"model_id":mid,"display_name":m.get("display_name") or m.get("name") or mid} for mid,m in sorted(models.items())]
    name_menu=json.dumps(canonical_menu,ensure_ascii=False,separators=(",",":"))
    definition_menu=json.dumps([{"model_id":mid,"display_name":m.get("display_name") or m.get("name") or mid,"select_when":m.get("select_when",[]),"danger_when":m.get("danger_when",[])} for mid,m in sorted(models.items())],ensure_ascii=False,separators=(",",":"))
    report={
      "schema_version":"lolla.controlled_vocabulary_boundary_audit.v1","status":"provider_free_audit_pass" if not (missing_seed or missing_edge or missing_chunk) else "provider_free_audit_integrity_fail",
      "canonical":{"declared_source_file_count":kg["metadata"]["source_file_count"],"model_count":len(models),"normalized_display_name_collision_count":len(duplicate_names),"normalized_display_name_collisions":duplicate_names,"canonical_id_unique":len(models)==len(set(models))},
      "graph":{"edge_count":len(edges),"model_count_with_any_edge":len(graph_ids),"isolated_model_count":len(set(models)-graph_ids),"isolated_model_ids":sorted(set(models)-graph_ids)},
      "chunks":{"chunk_count":len(chunks),"model_count":len(chunk_ids),"models_without_chunks":sorted(set(models)-chunk_ids)},
      "mechanism_bridge":{"mechanism_count":len(MECHANISMS),"mapped_mechanism_count":len(routing),"direct_seed_model_count":len(seed_ids),"direct_seed_fraction":round(len(seed_ids)/len(models),6),"seed_model_ids":sorted(seed_ids),"unseeded_directly_count":len(set(models)-seed_ids),"note":"Direct seeds are entry points; graph traversal can reach additional models and direct-seed fraction is not total graph reachability."},
      "hierarchy":{"reasoning_family_count":len(reasoning),"families":{k:{"model_count":len(v),"model_ids":sorted(v)} for k,v in sorted(reasoning.items())},"multi_family_model_count":sum(len(m.get("reasoning_types",[]))>1 for m in models.values()),"zero_family_model_count":sum(not m.get("reasoning_types") for m in models.values())},
      "menu_size":{"names_and_ids_utf8_bytes":len(name_menu.encode()),"names_ids_select_and_danger_utf8_bytes":len(definition_menu.encode()),"warning":"Names alone are canonical identity, not an adequate semantic selection contract."},
      "integrity":{"unknown_seed_ids":missing_seed,"unknown_edge_ids":missing_edge,"unknown_chunk_ids":missing_chunk},
      "non_claims":["direct_seed_fraction_is_not_graph_reachability","canonical_name_is_not_semantic_definition","coverage_is_not_selection_quality"]}
    a.output.mkdir(parents=True,exist_ok=True); (a.output/"report.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n"); (a.output/"canonical-menu.json").write_text(json.dumps(canonical_menu,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":report["status"],"canonical":report["canonical"],"graph":{k:v for k,v in report["graph"].items() if k!="isolated_model_ids"},"mechanism_bridge":{k:v for k,v in report["mechanism_bridge"].items() if not k.endswith("ids")},"hierarchy":{k:v for k,v in report["hierarchy"].items() if k!="families"},"menu_size":report["menu_size"]},indent=2))
    return 0 if report["status"].endswith("pass") else 1
if __name__=="__main__": raise SystemExit(main())
