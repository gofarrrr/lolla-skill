# Mental Model Teacher Three-Case Product Pilot Retry v0

Status: PR-P9 retry product pilot ready for review
Date: 2026-07-05
Decision gate: `proceed_to_ux_review_packet`

Product pilot:
[Mental Model Teacher three-case product pilot](mental-model-teacher-three-case-product-pilot-v0/index.md)

## Purpose

This slice retries PR-P9 after the three-case Teacher source package was
imported into current main. It translates the imported Teacher case artifacts
into productized lesson pages and small graph-neighborhood JSON.

Cases:

- `launch-public-enterprise-beta`
- `deploy-assisted-intake-routing`
- `ceo-remove-founding-cofounder`

## Outputs

The checked-in product pilot package lives at:

```text
docs/product/mental-model-teacher-three-case-product-pilot-v0/
```

It includes:

- `index.md`
- `manifest.json`
- one Teacher Lesson Product JSON object per case;
- one rendered lesson page per case;
- one small graph-neighborhood JSON file per case.

The rendered lesson pages foreground:

- case anchor;
- thinking move;
- why the move mattered;
- model stack;
- relation story;
- relation clickthrough;
- worked example;
- practice rep;
- do-not-overlearn boundary;
- high-risk caveat for the CEO cofounder case;
- source trail;
- visible non-claims.

## Source Policy

The source package is:

```text
reviews/codex-assisted/mental-model-teacher-knowledge-mesh-v2/
```

The builder reads only checked-in source artifacts. It does not use Decision
Work artifacts as Teacher source, does not call providers or model APIs, does
not create a new Lolla run, and does not wire runtime behavior.

Model and relation clickthroughs point to imported OKF source views in this
retry. Full product model pages and relation pages for every model in the three
cases remain outside this slice.

## Graph Scope

Each graph neighborhood is deliberately small:

- 3 model nodes from the case model stack;
- 1 relation edge from the Teacher relation deep-dive artifact;
- no embeddings;
- no relationship-graph affinity or rank;
- no graph UI;
- no full-corpus graph.

Graph edges are navigation and teaching context only. They are not proof.

## PR-P9 Stop Line

This retry stops before:

- UX review packet;
- human review;
- package gate;
- product-readiness claim;
- human-validation claim;
- browser graph UI;
- full-corpus graph;
- runtime integration.

Recommended next gate:
`proceed_to_ux_review_packet`
