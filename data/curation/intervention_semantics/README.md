# Intervention Semantics Curation Layer

This directory is the Wave 2 deepening layer for already curated models.

It sits after the Wave 1 operational routing contract in the parent `curation/` directory
and before any future chunk compilation, pressure-bundle assembly, or typed retrieval work.

This layer is separate on purpose:

- Wave 1 stays focused on routing identity and activation semantics
- Wave 2 focuses on intervention content that can become provenance-rich chunks

## Authority Order

1. raw markdown in `MM_CANONICAL_216/`
2. Wave 1 reviewed operational curation in `curation/*.json`
3. Wave 2 reviewed intervention semantics in `curation/intervention_semantics/*.json`
4. compiled preview artifacts under `.tmp/`
5. runtime interpretation

If a deepened item disagrees materially with the raw markdown, the markdown wins semantically.
The disagreement should be documented in notes, not hidden in code.

## File Layout

- `schema.json`: machine-readable contract for Wave 2 files
- `{model_id}.json`: one intervention-semantics file per already curated model

This pilot is intentionally bounded to a small subset of the already curated models.

## Required Fields

- `model_id`
- `source_file`
- `failure_modes`
- `premortem_questions`
- `heuristics`

Each list item must be provenance-ready and chunk-compilable.

## Item Contract

Every `failure_modes`, `premortem_questions`, and `heuristics` item must contain:

- `text`
- `source_quote`
- `extraction_type`
- `confidence`

Optional per item:

- `note`

### `text`

- Short, chunk-ready intervention content
- Should stay close to source meaning
- May be normalized for chunk use, but not invented

### `source_quote`

- Exact supporting quote or source span from the raw markdown
- This is required because Wave 2 is for provenance-rich chunk compilation, not pretty summaries

### `extraction_type`

Allowed values:

- `explicit`
- `normalized`

Use `explicit` when the chunk text is essentially the raw intervention content.
Use `normalized` when the chunk text compresses or lightly restructures the source into a cleaner chunk-ready form.

### `confidence`

Allowed values:

- `high`
- `medium`
- `weak`

Confidence should reflect how directly the chunk is supported by the raw source, not how useful it feels.

### `note`

- Optional short explanation of what was normalized, compressed, or deferred

## Optional Top-Level Fields

### `curation_notes`

Human review context only. Allowed keys:

- `summary`
- `donor_drops`
- `open_questions`

### `deferred_richness_notes`

Brief notes capturing raw-source richness that should not be lost during the read, even though this wave does not compile it yet.

Allowed keys:

- `allies`
- `antagonists`
- `structured_tensions`

These notes are for future curation planning only. They must not become live graph or runtime inputs in this wave.

## Explicit Non-Goals For This Wave

- no changes to Wave 1 contract fields
- no `compound_contracts`
- no allies / antagonists compilation
- no topology or multihop logic
- no embeddings implementation
- no runtime use
- no silent integration into the main compiler

## Review Standard

A Wave 2 file is acceptable only if:

- the intervention content is visibly grounded in the raw markdown
- each item is chunk-ready for later RFC 0004-style compilation
- explicit and normalized items are distinguishable
- low-confidence content is surfaced rather than padded
- future richness is noted without being prematurely compiled
