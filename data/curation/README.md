# Knowledge Substrate Authoring

This directory is the repository-local authoring authority for the compiled
Lolla knowledge substrate. It is not a second runtime graph.

The layers are:

1. `../model_sources/` — 222 canonical Markdown sources and their manifest.
2. root model JSON files — operational activation and routing curation.
3. `intervention_semantics/` — reviewed failure modes, premortem questions,
   and heuristics.
4. `relation_semantics/` — 222 active directed relation records plus two
   explicitly inactive historical identities.
5. `tendency_semantics/`, `reframing_semantics/`,
   `prerequisite_semantics/`, and `structural_coverage/` — the remaining
   reviewed compiler inputs.

`compiler_inputs_manifest.json` and
`relation_semantics_manifest.json` own inclusion and byte custody.
`graph_compiler_contract.json` freezes the current release reconstruction and
forbids compile-from-output fallback or automatic publication.

Build a candidate in an explicit, non-published directory:

```bash
PYTHONPATH=. python3 scripts/product/build_graph_substrate_candidate.py \
  --output-dir /tmp/lolla-graph-candidate
```

The current contract requires byte equivalence with
`data/knowledge_graph.json` and `data/relationship_graph.json`. A successful
candidate build proves reproducibility, not semantic correctness or product
usefulness. Publication of changed graph bytes remains a separate decision.
