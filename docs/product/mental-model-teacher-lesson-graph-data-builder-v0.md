# Mental Model Teacher Lesson Graph Data Builder v0

Status: PR-P7 lesson-neighborhood graph data builder
Date: 2026-07-05
Decision gate: `proceed_to_static_visual_graph_prototype`
Pilot graph package:
[Mental Model Teacher lesson graph data](mental-model-teacher-lesson-graph-v0/manifest.json)

## Purpose

This slice builds deterministic Visual Graph JSON for one Teacher lesson
neighborhood.

Builder:

```text
engine/system_b/mental_model_teacher_lesson_graph_builder.py
```

Checked-in pilot output:

```text
docs/product/mental-model-teacher-lesson-graph-v0/
```

The builder consumes the PR-P6 fixture lesson and the PR-P4/PR-P5 product-safe
model and relation page layer. It validates the graph through the PR-P3 Visual
Graph contract before writing JSON. It does not build browser graph UI, call
providers, use embeddings, read raw relationship graph ranking, or wire runtime
behavior.

## Graph Shape

The checked-in graph package contains:

- one package manifest;
- one lesson-neighborhood graph JSON file;
- two mental-model nodes;
- one relation edge.

Graph data:

- [contract-fixture-base-rates-system-2 graph JSON](mental-model-teacher-lesson-graph-v0/contract-fixture-base-rates-system-2.graph.json).

The graph nodes come from selected model pages:

- [Base Rates](mental-model-teacher-pilot-render-v0/models/base-rates.md);
- [System 2](mental-model-teacher-pilot-render-v0/models/system-2.md).

The graph edge comes from the selected relation page:

- [Base Rates and System 2](mental-model-teacher-pilot-render-v0/relations/base-rates__ally__system-2.md).

## Build Rules

Graph data must preserve:

- `graph_scope: lesson_neighborhood`;
- small-neighborhood layout hint;
- default focus;
- node page hrefs;
- edge page hrefs;
- relation-type filters;
- source status;
- missingness;
- source artifacts;
- graph non-claims.

Edge hrefs must resolve to relation pages. Edge confidence remains a source
label, not a truth claim, proof claim, certification, score, ranking, affinity,
or embedding-similarity claim.

## Boundary Rules

The builder:

- does not create browser graph UI;
- does not build a full-corpus graph;
- does not use embeddings;
- does not expose relationship-graph affinity or rank;
- does not call providers or model APIs;
- does not wire runtime;
- does not claim product proof, human validation, answer correctness, or advice
  correctness;
- does not authorize agent or automatic action.

## PR-P7 Stop Line

PR-P7 stops before:

- browser graph UI;
- Cytoscape or any other graph renderer;
- full-corpus graph work;
- runtime integration;
- provider or model calls;
- product-readiness or human-validation claims.

Recommended next gate:
`proceed_to_static_visual_graph_prototype`
