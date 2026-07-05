# Mental Model Teacher Pilot Page Data Builder v0

Status: PR-P4 deterministic builder
Date: 2026-07-05
Decision gate: `proceed_to_static_model_relation_page_renderer`

## Purpose

This slice builds a small, deterministic, product-safe pilot page-data package
from existing checked-in substrate.

Builder:

```text
engine/system_b/mental_model_teacher_pilot_page_builder.py
```

The builder reads:

- `data/model_sources/manifest.json`;
- `data/curation/*.json`;
- `data/curation/intervention_semantics/*.json`;
- `data/curation/relation_semantics/*.json`.

It validates generated model and relation pages through:

```text
engine/system_b/mental_model_teacher_product_contracts.py
```

## Pilot Scope

Default pilot models:

- `base-rates`;
- `system-2`;
- `scientific-method-evidence-testing`.

These were selected because all three have canonical source, activation
curation, intervention semantics, and relation semantics. No checked-in Teacher
case artifacts are claimed or used in this slice.

Default generated relation pages:

- `base-rates__ally__scientific-method-evidence-testing`;
- `base-rates__ally__system-2`.

Only relations whose target model is inside the pilot subset are emitted.

## Output Shape

The CLI emits a JSON package with:

- `schema_version: lolla.mental_model_teacher.pilot_page_data.v0`;
- builder identity;
- contract refs;
- pilot scope;
- `model_pages`;
- `relation_pages`;
- build review;
- explicit non-claims.

The generated package is validation output, not a checked-in product artifact in
PR-P4. Later slices can generate it into a temp file and render from it.

Example command:

```bash
python3 -m engine.system_b.mental_model_teacher_pilot_page_builder --output /tmp/mental-model-teacher-pilot-pages.json
```

## Missingness Behavior

The builder does not invent copy where a source-backed field is absent.

Current missingness:

- model pages leave `common_misuse` empty and mark it missing;
- model pages leave `practice_prompts` empty and mark it missing;
- relation pages use visible generic missingness boundaries for
  source-specific misread risk and source-specific practice prompt.

This is intentional. PR-P4 proves that the data layer can preserve absence
rather than over-writing it with plausible teaching copy.

## Boundary Rules

The builder:

- does not use embeddings;
- does not use graph affinity or ranking;
- does not use Teacher artifacts unless they are checked in later and explicitly
  selected by a later slice;
- does not call providers or model APIs;
- does not render Markdown or HTML pages;
- does not create graph UI;
- does not wire runtime;
- does not claim product proof, human validation, answer correctness, or advice
  correctness.

## PR-P4 Stop Line

PR-P4 stops before:

- model page rendering;
- relation page rendering;
- Teacher lesson rendering;
- graph data building;
- graph UI;
- full-corpus graph work;
- runtime integration.

Recommended next gate:
`proceed_to_static_model_relation_page_renderer`
