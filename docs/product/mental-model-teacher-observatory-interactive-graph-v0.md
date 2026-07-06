# Mental Model Teacher Observatory Interactive Graph v0

Status: offline interactive lesson graph
Date: 2026-07-06
Decision gate: `proceed_to_compiled_observatory_learn_source_port`

Current ownership note: this gate is superseded by
[Mental Model Teacher Observatory Ownership and Portability Boundary](mental-model-teacher-observatory-ownership-portability-boundary-v0.md).
The compiled source port is now treated as a source-owner verification question,
not the default next implementation path.

## Purpose

This slice upgrades the Teacher Learn map from a static lesson-neighborhood
SVG into a small Observatory-native graph workbench.

The goal is not to show the whole mental model corpus. The goal is to make the
current lesson relationship inspectable without turning the page into telemetry
or graph proof.

The graph remains inside:

```text
/teacher-learning
```

It uses only the already-built read-only Teacher learning packet:

```text
/api/case/<id>/teacher-learning
```

This does not run Lolla.
It does not invoke the Lolla skill.
It does not call providers or model APIs.
It does not create new runs, mutate archives, judge answer quality, authorize
action, or wire Lolla runtime behavior.

## User Experience

The graph now supports:

- node search;
- relation-type filters;
- selected node or edge panel;
- node links to mental model detail drawers;
- edge links to relation detail drawers;
- default focus on the lesson's primary model;
- visible graph non-claims.

The graph is still small by design. It should help the user understand the
lesson neighborhood, not invite them to wander the full corpus.

## Information Rules

Nodes are mental models from the selected Teacher lesson packet.

Edges are reviewed relation-page references from the selected Teacher lesson
packet.

The selected panel explains what the user clicked. It does not replace the
model or relation drawer. The drawer remains the deeper product-safe detail.

## Non-Claims

The graph is navigation, not proof.

Edge confidence is not certification.

Search and filters are local browser affordances only. They do not call
providers, embeddings, a model API, or a live relation judge.

## Stop Line

This PR stops before:

- full corpus graph;
- compiled SPA source rebuild;
- runtime integration;
- provider or model calls;
- live Lolla runs;
- embedding-similarity relation claims;
- product proof claims;
- human validation claims;
- answer or advice correctness scoring;
- action authorization.

Recommended next gate:

```text
proceed_to_compiled_observatory_learn_source_port
```
