# Mental Model Teacher Lesson Product Renderer v0

Status: PR-P6 Teacher lesson product renderer
Date: 2026-07-05
Decision gate: `proceed_to_lesson_neighborhood_graph_data_builder`
Pilot lesson render:
[Mental Model Teacher lesson render](mental-model-teacher-lesson-render-v0/index.md)

## Purpose

This slice renders a Teacher Lesson Product object into a readable static
Markdown lesson page.

Renderer:

```text
engine/system_b/mental_model_teacher_lesson_renderer.py
```

Checked-in pilot output:

```text
docs/product/mental-model-teacher-lesson-render-v0/
```

The renderer consumes the PR-P3 Teacher Lesson Product contract fixture and
validates it before writing Markdown. It does not claim that a real Teacher case
artifact exists in this branch. It does not build graph data, create graph UI,
call providers, use embeddings, or wire runtime behavior.

## Product Framing

The lesson page keeps the Mental Model Teacher product lane separate:

- case is the anchor;
- reasoning move is the subject;
- model relationship is the lesson;
- practice rep is the product value.

The rendered fixture is a teaching surface for one reasoning move. It is not a
second advice engine, a product-readiness claim, a human validation claim, a
runtime hook, or an approval surface.

## Rendered Pages

The checked-in lesson render contains:

- one lesson index page;
- one Teacher lesson fixture page;
- one render manifest.

Lesson page:

- [Separate the vivid inside view from the outside-view prior before updating](mental-model-teacher-lesson-render-v0/lessons/contract-fixture-base-rates-system-2.md).

The lesson links to the PR-P5 pilot model and relation pages:

- [Base Rates model page](mental-model-teacher-pilot-render-v0/models/base-rates.md);
- [System 2 model page](mental-model-teacher-pilot-render-v0/models/system-2.md);
- [Base Rates and System 2 relation page](mental-model-teacher-pilot-render-v0/relations/base-rates__ally__system-2.md).

## Rendering Rules

Lesson pages must show:

- case anchor;
- thinking move;
- model stack;
- relation story;
- model clickthroughs;
- relation clickthroughs;
- worked example;
- practice rep;
- do-not-overlearn boundary;
- human gate status;
- missingness;
- source refs;
- visible non-claims.

The worked example must say that the fixture applies the move and is not a
completed real Teacher case artifact. The human gate block must keep
`human_review_status: not_reviewed`, `product_proof: false`, and
`runtime_integration_authorized: false` visible.

## Boundary Rules

The renderer:

- does not read or create real Teacher case artifacts;
- does not use embeddings;
- does not use graph affinity or ranking;
- does not build graph data;
- does not create graph UI;
- does not call providers or model APIs;
- does not wire runtime;
- does not claim product proof, human validation, answer correctness, or advice
  correctness;
- does not authorize agent or automatic action.

## PR-P6 Stop Line

PR-P6 stops before:

- graph data building;
- browser graph UI;
- full-corpus graph work;
- runtime integration;
- provider or model calls;
- real three-case Teacher product pilot work.

Recommended next gate:
`proceed_to_lesson_neighborhood_graph_data_builder`
