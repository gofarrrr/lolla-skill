#!/usr/bin/env python3
"""
Companion model catalog and recall for Lolla skill.

Two modes:
  1. Catalog mode (default): Returns all 224 models with select_when signals
     for companion fingerprinting — detecting which models are active in the answer.
  2. Recall mode (--model-ids): Returns detailed chunks for specific models,
     formatted for input to run_select_companion.py.

Usage:
    # Full catalog for fingerprinting
    python3 scripts/run_companion.py

    # Detailed recall for specific models (after fingerprinting)
    python3 scripts/run_companion.py --model-ids "systems-thinking,second-order-thinking,premortem"

Output: JSON model catalog or detailed recall data.
"""

import argparse
import json
import sys
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_kg():
    kg_path = DATA_DIR / "knowledge_graph.json"
    with open(kg_path) as f:
        return json.load(f)


def load_curation(model_id: str) -> dict:
    path = DATA_DIR / "curation" / f"{model_id}.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def load_intervention(model_id: str) -> dict:
    path = DATA_DIR / "curation" / "intervention_semantics" / f"{model_id}.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def load_relations(model_id: str) -> list:
    """Load relationship edges where this model is the source."""
    rg_path = DATA_DIR / "relationship_graph.json"
    if not rg_path.exists():
        return []
    with open(rg_path) as f:
        data = json.load(f)
    edges = data if isinstance(data, list) else data.get("edges", [])
    return [
        e for e in edges
        if e.get("source_model_id") == model_id or e.get("target_model_id") == model_id
    ]


def catalog_mode():
    """Return all models with select_when signals for fingerprinting."""
    kg = load_kg()
    models = kg.get("models", {})
    catalog = []

    for model_id, m in sorted(models.items()):
        entry = {
            "model_id": model_id,
            "core_idea": m.get("core_idea", ""),
        }

        curation = load_curation(model_id)
        if curation:
            entry["select_when"] = curation.get("select_when", "")
            entry["danger_when"] = curation.get("avoid_when", "")
            entry["input_type"] = curation.get("input_type", "")
            entry["output_type"] = curation.get("output_type", "")

        catalog.append(entry)

    return {
        "total_models": len(catalog),
        "models_with_curation": sum(1 for m in catalog if "select_when" in m),
        "catalog": catalog,
    }


def recall_mode(model_ids: list[str]):
    """Return detailed chunks for specific models, ready for run_select_companion.py.

    Output matches the --chunks-json schema expected by run_select_companion.py.
    """
    kg = load_kg()
    models_info = kg.get("models", {})
    result_models = []

    for model_id in model_ids:
        info = models_info.get(model_id, {})
        curation = load_curation(model_id)
        intervention = load_intervention(model_id)
        edges = load_relations(model_id)

        display_name = info.get("display_name", "") or curation.get("display_name", "") or model_id
        chunks = []

        # Wave 1: identity chunk
        if curation:
            parts = []
            sw = curation.get("select_when", "")
            if isinstance(sw, list) and sw:
                parts.append(f"Select when: {sw[0]}")
            elif isinstance(sw, str) and sw:
                parts.append(f"Select when: {sw}")
            aw = curation.get("avoid_when", "")
            if isinstance(aw, list) and aw:
                parts.append(f"Danger when: {aw[0]}")
            elif isinstance(aw, str) and aw:
                parts.append(f"Danger when: {aw}")
            rt = curation.get("reasoning_type", [])
            if rt:
                parts.append(f"Reasoning: {', '.join(rt) if isinstance(rt, list) else rt}")
            text = " | ".join(parts) if parts else display_name
            chunks.append({
                "chunk_type": "identity",
                "text": text,
                "source_layer": "wave1",
                "extraction_type": "explicit",
                "confidence": "high",
            })

        # Wave 2: failure modes, heuristics, premortems
        if intervention:
            for fm in intervention.get("failure_modes", [])[:3]:
                desc = fm.get("description", "")
                mitigation = fm.get("mitigation", "")
                text = f"{desc}" + (f" Mitigation: {mitigation}" if mitigation else "")
                chunks.append({
                    "chunk_type": "failure_mode",
                    "text": text,
                    "source_layer": "wave2",
                    "extraction_type": "explicit",
                    "confidence": "high",
                })
            for h in intervention.get("heuristics", [])[:3]:
                chunks.append({
                    "chunk_type": "heuristic",
                    "text": h.get("description", "") if isinstance(h, dict) else str(h),
                    "source_layer": "wave2",
                    "extraction_type": "explicit",
                    "confidence": "high",
                })
            for p in intervention.get("premortem_questions", [])[:3]:
                chunks.append({
                    "chunk_type": "premortem",
                    "text": p.get("question", "") if isinstance(p, dict) else str(p),
                    "source_layer": "wave2",
                    "extraction_type": "explicit",
                    "confidence": "high",
                })

        # Wave 3: relationship edges (allies and antagonists)
        for edge in edges[:6]:
            edge_type = edge.get("edge_type", "").lower()
            if edge_type in ("antagonist", "tension"):
                chunk_type = "antagonist"
            elif edge_type in ("ally", "compound"):
                chunk_type = "ally"
            else:
                continue
            other_id = (
                edge.get("target_model_id")
                if edge.get("source_model_id") == model_id
                else edge.get("source_model_id")
            )
            desc = (edge.get("source_description") or edge.get("target_description") or "")[:200]
            other_name = models_info.get(other_id, {}).get("display_name", other_id)
            chunks.append({
                "chunk_type": chunk_type,
                "text": f"{other_name}: {desc}" if desc else other_name,
                "source_layer": "wave3",
                "extraction_type": "explicit",
                "confidence": "high",
                "relation_target_id": other_id,
            })

        result_models.append({
            "model_id": model_id,
            "display_name": display_name,
            "chunks": chunks,
        })

    return {"models": result_models}


def main():
    parser = argparse.ArgumentParser(
        description="Companion model catalog and detailed recall for Lolla skill",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes:
  Default (no args): Returns full 217-model catalog with select_when signals
    for companion fingerprinting.

  --model-ids: Returns detailed chunks (identity, failure modes, heuristics,
    premortems, allies, antagonists) for specified models. Output format matches
    the --chunks-json input expected by run_select_companion.py.

Examples:
  python3 scripts/run_companion.py
  python3 scripts/run_companion.py --model-ids "systems-thinking,premortem"
""",
    )
    parser.add_argument("--model-ids", default="",
                        help="Comma-separated model IDs for detailed recall")
    args = parser.parse_args()

    if args.model_ids:
        ids = [mid.strip() for mid in args.model_ids.split(",") if mid.strip()]
        result = recall_mode(ids)
    else:
        result = catalog_mode()

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
