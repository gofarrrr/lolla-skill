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
1. raw markdown in `MM_CANONICAL_216/*.md`
2. reviewed relation curation in this directory
3. preview-only compiled relation artifacts
4. any future compiler or runtime use

Donor relation artifacts may be consulted as draft reference only.
They are not canonical truth and must not be bulk-imported.

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

Wave 3 in this repo is preview-only.

This run does not:
- integrate into the main compiler
- change `build/knowledge_graph.json`
- change `build/relationship_graph.json`
- change runtime behavior
- add embeddings

The quality bar is usefulness with inspectability, not relation volume.
