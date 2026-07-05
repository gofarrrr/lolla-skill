# Mental Model Teacher Static Page Renderer v0

Status: PR-P5 static pilot renderer
Date: 2026-07-05
Decision gate: `proceed_to_teacher_lesson_product_renderer`
Pilot render:
[Mental Model Teacher pilot render](mental-model-teacher-pilot-render-v0/index.md)

## Purpose

This slice renders the PR-P4 pilot model and relation page data into readable
static Markdown pages.

Renderer:

```text
engine/system_b/mental_model_teacher_static_renderer.py
```

Checked-in pilot output:

```text
docs/product/mental-model-teacher-pilot-render-v0/
```

The renderer consumes PR-P4 product-page data and validates it through the PR-P3
contracts before writing Markdown. It does not render Teacher lessons, build
graph data, create graph UI, call providers, use embeddings, or wire runtime
behavior.

## Rendered Pages

The checked-in pilot render contains:

- one index page;
- three model pages;
- two relation pages;
- one render manifest.

Model pages:

- [Base Rates](mental-model-teacher-pilot-render-v0/models/base-rates.md);
- [System 2](mental-model-teacher-pilot-render-v0/models/system-2.md);
- [Scientific Method Evidence Testing](mental-model-teacher-pilot-render-v0/models/scientific-method-evidence-testing.md).

Relation pages:

- [Base Rates and Scientific Method Evidence Testing](mental-model-teacher-pilot-render-v0/relations/base-rates__ally__scientific-method-evidence-testing.md);
- [Base Rates and System 2](mental-model-teacher-pilot-render-v0/relations/base-rates__ally__system-2.md).

## Rendering Rules

Model pages must show:

- plain one-sentence meaning;
- helps-notice section;
- use-when section;
- avoid-when section;
- failure modes;
- premortem questions;
- heuristics;
- common misuse with missingness visible when absent;
- practice prompts with missingness visible when absent;
- local relation links;
- source custody;
- non-claims.

Relation pages must show:

- plain-language story before taxonomy;
- why it matters;
- practice prompt;
- misread risk;
- source and target model links;
- relation type, confidence, and curation status;
- source quote or ref;
- missingness;
- non-claims.

The renderer must not expose raw JSON as the main UI. The render manifest is a
machine-readable receipt only.

## Boundary Rules

The renderer:

- does not use embeddings;
- does not use graph affinity or ranking;
- does not render Teacher lesson pages;
- does not build graph data;
- does not create graph UI;
- does not call providers or model APIs;
- does not wire runtime;
- does not claim product proof, human validation, answer correctness, or advice
  correctness.

## PR-P5 Stop Line

PR-P5 stops before:

- Teacher lesson page rendering;
- graph data building;
- graph UI;
- full-corpus graph work;
- runtime integration.

Recommended next gate:
`proceed_to_teacher_lesson_product_renderer`
