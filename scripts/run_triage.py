#!/usr/bin/env python3
"""
Triage helper for Lolla skill.

This script does NOT call an external LLM. It loads the tendency catalog
and returns the full list of tendencies with their descriptions and
activation contexts so Claude can perform triage reasoning natively.

Usage:
    python3 scripts/run_triage.py

Output: JSON tendency catalog suitable for Claude's triage reasoning.
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "engine"))

from system_b.published_knowledge_substrate import PublishedKnowledgeSubstrate


def load_tendency_catalog():
    """Load tendencies from the compiled knowledge graph."""
    kg = PublishedKnowledgeSubstrate.open(REPO_ROOT).require_snapshot().knowledge_graph_payload()

    tendencies = kg.get("tendencies", {})
    catalog = []
    for tid, t in sorted(tendencies.items()):
        antidotes = t.get("antidote_models", [])
        activation_contexts = [
            {"model": b["model"], "context": b.get("activation_context", "")}
            for b in antidotes
            if b.get("activation_context")
        ]
        catalog.append({
            "tendency_id": tid,
            "description": t.get("description", ""),
            "num_corrective_models": len(antidotes),
            "activation_contexts": activation_contexts,
        })
    return catalog


def main():
    catalog = load_tendency_catalog()
    print(json.dumps(catalog, indent=2))


if __name__ == "__main__":
    main()
