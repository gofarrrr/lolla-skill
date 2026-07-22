# Wave 3 Relation Semantics

This directory defines the Wave 3 curated layer for first-order relation semantics.

Purpose:
- preserve source-backed ally relationships
- preserve source-backed antagonist relationships
- preserve source-backed structured tensions
- keep relation semantics inspectable and provenance-ready before any compiler integration

This layer is separate from:
- Wave 1 operational routing identity in `curation/*.json`
- Wave 2 intervention semantics in `curation/intervention_semantics/*.json`

It is also intentionally separate from higher-order relation logic such as:
- `compound_contracts`
- multihop motifs
- topology scoring
- runtime composition logic

## Authority Order

The authority order for this layer is:

1. repository-local raw Markdown in `data/model_sources/*.md`
2. reviewed relation curation in this directory
3. the lifecycle and inclusion boundary in
   `data/curation/relation_semantics_manifest.json`
4. candidate compiler outputs
5. explicitly promoted runtime artifacts

The current 222-record authoring set was reconciled once against the published
1,358-relation graph and admitted byte-for-byte. The temporary recovery
snapshot is not a project dependency. A fresh clone validates the complete set
with:

```bash
PYTHONPATH=. python3 scripts/product/adopt_relation_semantics_authoring.py --validate-only
```

Historical identity records remain in this directory as immutable source
evidence, but the manifest excludes them from active compilation. Runtime
aliasing is not authorized.

## Contract

Each curated file must be a single JSON object with these required top-level fields:
- `model_id`
- `source_file`
- `allies`
- `antagonists`
- `structured_tensions`

Optional top-level fields:
- `curation_notes`
- `deferred_higher_order_notes`

## Relation Families

The three families are distinct and must not be collapsed into one generic relation blob.

### `allies`

Supporting first-order relations where another model helps amplify, discipline, or operationalize the source model.

Each item must contain:
- `target_model_id`
- `rationale_text`
- `source_quote`
- `extraction_type`
- `confidence`

Optional:
- `note`
- `affinity_strength`
- `affinity_rationale`
- `activation_condition`

### `antagonists`

Conflicting first-order relations where another model, bias, or pattern interferes with or distorts the source model.

Each item must contain:
- `target_model_id`
- `rationale_text`
- `source_quote`
- `extraction_type`
- `confidence`

Optional:
- `note`
- `affinity_strength`
- `affinity_rationale`
- `activation_condition`

### `structured_tensions`

Explicit, source-backed tension statements that should remain separate from generic antagonists because the source names a concrete “X vs Y” conflict.

Each item must contain:
- `target_model_id`
- `tension_text`
- `source_quote`
- `extraction_type`
- `confidence`

Optional:
- `tension_type`
- `note`

## Provenance Discipline

This wave is designed for future pressure-bundle and typed-retrieval support, so every relation item must be provenance-ready.

Allowed `extraction_type` values:
- `explicit`
- `normalized`

Allowed `confidence` values:
- `high`
- `medium`
- `weak`

Rules:
- use `explicit` when the source states the relation in near-final form
- use `normalized` when reviewed curation compresses or clarifies a source-backed relation
- do not infer reciprocity unless the raw source independently supports it
- if a relation is source-rich but does not map cleanly to a canonical target model id, prefer omission plus a note over forced mapping

## Deferred Higher-Order Notes

`deferred_higher_order_notes` is optional and is only for preserving observations that may matter later for:
- relation clusters
- topology
- multihop motifs
- compound behavior

It must not be treated as compiled input in this wave.

Allowed keys:
- `allies`
- `antagonists`
- `structured_tensions`

Values must be short lists of meaningful strings.

## Current Wave Boundary

Wave 3 authoring is now repository-local and complete for the currently
published 222-model / 1,358-relation graph. That custody fact does not itself
authorize publication of new graph bytes or establish semantic correctness or
product usefulness.

This admission does not:

- change `data/knowledge_graph.json`
- change `data/relationship_graph.json`
- change runtime selection or portfolio behavior
- add, regenerate, or refresh embeddings
- infer reciprocity, reverse edges, or transitive relations
- authorize broader graph traversal

The quality bar is usefulness with inspectability, not relation volume.
