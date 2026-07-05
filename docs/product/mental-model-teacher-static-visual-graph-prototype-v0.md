# Mental Model Teacher Static Visual Graph Prototype v0

Status: PR-P8 static visual graph prototype
Date: 2026-07-05
Decision gate: `proceed_to_three_case_teacher_product_pilot`
Prototype:
[Mental Model Teacher visual graph prototype](mental-model-teacher-visual-graph-prototype-v0/index.html)

## Purpose

This slice renders the PR-P7 lesson-neighborhood graph data as a local static
HTML prototype.

Prototype entrypoint:

```text
docs/product/mental-model-teacher-visual-graph-prototype-v0/index.html
```

Source graph:

```text
docs/product/mental-model-teacher-lesson-graph-v0/contract-fixture-base-rates-system-2.graph.json
```

The prototype embeds the graph data directly so the HTML can be opened from
disk without a dev server, external script, provider call, model call, or
runtime hook.

## Renderer Choice

Cytoscape.js remains the preferred renderer for a larger interactive graph once
there is a local frontend package or approved vendor path. PR-P8 uses a
dependency-free SVG renderer because this repository has no `package.json`,
lockfile, local Cytoscape dependency, or static vendor pattern, and the first
prototype must be reviewable offline from a single checked-in HTML file.

## Prototype Features

The checked-in prototype includes:

- visual graph rendering;
- selected node panel;
- selected edge panel;
- relation-type filter controls;
- model search;
- links to model pages;
- links to relation pages;
- link to the source graph JSON;
- link to the Teacher lesson page;
- visible source status and missingness in the side panels.

The graph edge links to:

- [Base Rates and System 2 relation page](mental-model-teacher-pilot-render-v0/relations/base-rates__ally__system-2.md).

The graph nodes link to:

- [Base Rates model page](mental-model-teacher-pilot-render-v0/models/base-rates.md);
- [System 2 model page](mental-model-teacher-pilot-render-v0/models/system-2.md).

## Boundary Rules

The prototype:

- does not build a full-corpus graph;
- does not use embeddings;
- does not expose relationship-graph affinity or rank;
- does not call providers or model APIs;
- does not wire runtime;
- does not claim product proof, human validation, answer correctness, or advice
  correctness;
- does not authorize agent or automatic action.

## PR-P8 Stop Line

PR-P8 stops before:

- full-corpus graph work;
- runtime integration;
- provider or model calls;
- product-readiness or human-validation claims;
- the three-case Teacher product pilot.

Recommended next gate:
`proceed_to_three_case_teacher_product_pilot`
