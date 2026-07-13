# Controlled vocabulary selection boundary v1

Status: provider-free architectural decision  
Date: 2026-07-12  
Runtime: unchanged

## Decision

Lolla must use canonical IDs at every routing and pressure-selection boundary. An LLM may select or reject controlled items; it may not invent mechanism names, mental-model names, aliases, or graph nodes.

The recommended architecture is **mechanism interpretation → deterministic graph recall → canonical model adjudication**. Direct selection from the complete 222-name list is retained as a future comparison arm, not adopted as the main architecture. The current nine `reasoning_types` are unsuitable as a hierarchy.

## Corpus audit

`data/knowledge_graph.json` contains exactly 222 unique canonical model IDs and 222 collision-free display names. Every model participates in the 1,358-edge relationship graph.

The compact ID/name menu is 15,797 UTF-8 bytes. It is technically easy to place in a prompt. That only solves identity normalization. Names such as “Inversion,” “Optionality,” or “Constraints” do not specify when the model is applicable, what evidence is necessary, or when it would be misleading.

Adding the existing `select_when` and `danger_when` material produces a 185,492-byte menu before conversation records or instructions. The issue is therefore not whether 222 phrases fit. It is whether phrase-only selection is semantically disciplined.

The curated chunk layer currently covers 63 canonical models and contains one unknown historical ID, `commitment-and-consistency-bias`, where the canonical graph uses `commitment-bias`. This is a custody defect. It must not be silently repaired inside a run. Direct selection and downstream output must validate against the 222-ID registry and quarantine unknown IDs.

## Three contracts compared

### Mechanism-first

The model interprets source-linked role records against nine operationally defined mechanisms. Deterministic code maps accepted mechanisms to canonical seed IDs.

Advantages:

- compact reasoning-specific semantic task;
- facts remain outside graph routing;
- deterministic machinery introduces external pressure;
- model names cannot drift.

Limits:

- nine mechanisms directly seed only 19/222 models;
- current interpretation is not yet invariant;
- the mechanism vocabulary may encode the designers' blind spots.

This remains the strongest first-stage boundary, but not a complete selection system.

### Direct canonical-model selection

The model receives all 222 canonical IDs and display names and returns a bounded set or abstains.

Advantages:

- no naming variation;
- full canonical surface is available;
- simple output validation.

Limits:

- names alone encourage association and factual-topic matching;
- full operational cards are too large for the intended small reliable job;
- direct selection collapses interpretation and lens choice into one probabilistic decision;
- it weakens the graph's purpose as an external, partly non-obvious pressure source.

This is a valuable control arm. It is not presently the preferred production shape.

### Existing reasoning-family hierarchy

The knowledge graph exposes nine reasoning types, but all 222 models belong to at least two families. The largest families contain 102 diagnostic, 87 systems, and 77 causal or metacognitive models. Selecting a family therefore leaves an excessively broad and overlapping candidate set.

The metadata is useful for describing models, not for a discriminating first-stage selector. It should not be promoted into routing merely because it already exists.

## Recommended four-boundary flow

```text
source-linked role records
  → probabilistic selection from controlled reasoning mechanisms
  → deterministic canonical seed and graph-neighborhood recall
  → probabilistic selection/rejection from that bounded canonical model menu
  → downstream pressure composition with canonical IDs only
```

The final model adjudicator receives canonical ID, display name, and a compact model card for only the graph-recalled candidates. It must support `selected`, `ambiguous`, `not_applicable`, and `insufficient_evidence`. It may reject every candidate. It cannot introduce a model that the deterministic recall did not supply.

This preserves both halves of the product idea: LLMs interpret messy conversation and semantic applicability; deterministic machinery supplies controlled external recall and provenance.

## Why no provider comparison is authorized yet

The local gate is intentionally failed for two reasons:

1. the curated chunk substrate contains a noncanonical historical model ID;
2. the three arms do not yet receive semantically comparable information—names-only direct selection is under-specified, while full 222-card selection is much larger than the mechanism task.

Running calls now would compare prompt information volume rather than architecture. The next provider-free goal should define compact canonical model cards, quarantine the stale alias at the registry boundary, and build equal-information fixtures for a bounded direct-selection control versus graph-recalled candidate adjudication.

## Non-claims

- Canonical identity does not prove semantic applicability.
- Reachability does not prove usefulness.
- A graph candidate is a recall hypothesis, not a recommendation.
- A rejected candidate is not permanently removed from the corpus.
- This decision does not authorize runtime or graph integration.

