# Mental Model Teacher Substrate Exposure Contract v0

Status: PR-P2 exposure contract
Date: 2026-07-05
Decision gate: `proceed_to_user_facing_model_relation_contracts`
Machine-readable policy:
[Mental Model Teacher substrate exposure policy](mental-model-teacher-substrate-exposure-contract-v0.json)

## Purpose

This slice maps the existing Lolla substrate into a product-safe exposure
contract for the separate Mental Model Teacher Product Surface / Visual Mental
Model Library lane.

It does not create product page contracts, render pages, build graph UI, call
providers, wire runtime behavior, or claim product proof. It only answers:

- what existing substrate exists in this repo;
- whether it is present or missing in this worktree;
- how it may be used later by product surfaces;
- what must remain internal;
- what must wait for a later review gate.

The contract follows the product principle from the PRD:

```text
case is the anchor
reasoning move is the subject
model relationship is the lesson
practice rep is the product value
```

## Classification Vocabulary

| Classification | Meaning |
|---|---|
| `product-safe` | A bounded, reviewed field or derived custody fact may appear in the product surface without exposing raw internal mechanics. |
| `product-safe-after-translation` | The asset may power user-facing pages only through a later product contract, with raw paths, routing metadata, extraction metadata, ranking internals, and unsupported claims removed or reframed. |
| `internal-only` | The asset may support implementation, validation, custody, or evidence discipline, but must not appear as product copy or visible proof. |
| `future/suggestion-only` | The asset may inform later navigation, clustering, suggestions, or advanced teaching after a separate review gate; it is not a v0 user-facing source of truth. |

## Current Deterministic Inventory

The Python inventory reader
`engine/system_b/mental_model_teacher_substrate_inventory.py` computes these
counts from the local repo without exposing raw source bodies, raw vectors,
local absolute paths, provider/model text, or page contracts.

Current PR-P2 substrate counts:

| Asset | Current count or shape | Exposure classification |
|---|---:|---|
| `data/model_sources/*.md` | 222 Markdown files | `product-safe-after-translation` |
| `data/model_sources/manifest.json` | 222 manifest file entries | `product-safe-after-translation` |
| `data/model_sources/manifest.json:files[].sha256` | 222 source hash records | `product-safe` |
| `data/curation/*.json` | 225 direct curation files | `product-safe-after-translation` |
| `data/curation/intervention_semantics/*.json` | 225 intervention files | `product-safe-after-translation` |
| `data/curation/relation_semantics/*.json` | 225 relation files | `product-safe-after-translation` |
| `data/relationship_graph.json` | 1,358 curated edges | `product-safe-after-translation` |
| `data/knowledge_graph.json` | 222 models, 25 tendencies, 1,742 edges | `future/suggestion-only` |
| `data/embeddings.db` | present, internal binary database | `internal-only` |
| `data/curated/*.json` | 4 curated files | `product-safe-after-translation` |
| `data/family_semantics/*.json` | 24 family files | `future/suggestion-only` |
| `data/compiled/model_affordances/affordances_v60.json` | 222 model records, 306 affordances, 697 absence records | `future/suggestion-only` |
| `engine/system_b/relation_graph.py` | present | `internal-only` |
| `engine/system_b/activation_matcher.py` | present | `internal-only` |
| Graph survival/eval artifacts | graph survival code/test present, eval JSON present | `internal-only` |
| `engine/system_b/model_affordance_validation.py` | present | `internal-only` |
| Checked-in Teacher artifact directories | not present in this worktree | `product-safe-after-translation` if later present |

Teacher artifacts are deliberately modeled as optional missingness in PR-P2.
The PRD mentions Teacher cards, notes, OKF bundles, relation deep dives, model
deep dives, practice labs, grounding audits, and human-gate scaffolding. Those
appear to live in a separate Teacher worktree, not in this branch. PR-P2 must
not fake them.

## Exposure Rules By Surface

### Model Pages

Allowed later inputs:

- canonical Markdown;
- source hash custody from the manifest;
- activation curation;
- intervention semantics;
- selected curated trusted-surface chunks.

Required translation:

- turn raw Markdown into bounded page fields;
- turn `select_when` and `avoid_when` into user-facing use/avoid sections;
- preserve source refs and missingness;
- keep routing labels and donor draft mechanics out of product copy;
- never show local source provenance paths.

### Relation Pages

Allowed later inputs:

- relation semantics;
- curated relationship graph edge identity;
- source quotes or source refs from relation semantics.

Required translation:

- explain the edge in plain language before taxonomy;
- preserve confidence and curation status;
- include a misread-risk boundary;
- never present edge existence, affinity, or graph rank as proof.

Unsupported relation speculation must not surface.

### Teacher Lesson Pages

Allowed later inputs:

- model page fields after PR-P3/PR-P4 contracts exist;
- relation page fields after PR-P3/PR-P4 contracts exist;
- intervention semantics for failure, premortem, heuristic, and practice
  material;
- checked-in Teacher artifacts only when present and reviewed.

Required translation:

- make the case the anchor;
- make the reasoning move the subject;
- make model relationships the lesson;
- make the practice rep the product value;
- show human-review status as status, not validation;
- show product proof as absent unless a later human process establishes it.

### Visual Graph Neighborhoods

Allowed later inputs:

- relation semantics;
- curated relationship graph edge identity;
- productized model and relation page refs after later contracts exist.

Required translation:

- default to small focused neighborhoods;
- make edges clickable through relation pages;
- carry source status and missingness;
- show non-claims near the graph;
- keep raw affinity, fan adjustment, embedding similarity, and candidate
  rejection traces internal.

The graph should teach navigation and distinction-making. It should not look
like proof.

### Future Global Navigation

Possible later inputs:

- knowledge graph;
- family semantics;
- V60 affordances;
- semantic neighbor suggestions from embeddings after review.

Required future gate:

- separate collection/global graph plan;
- explicit reviewed relation and missingness rules;
- no embedding similarity as validated relation semantics;
- no global topology as the first user surface.

## Asset-Specific Contract Notes

### Canonical Markdown

Canonical Markdown is the source of model doctrine and examples, but raw
Markdown is not the product UI. Model pages should later expose extracted,
bounded, reviewed fields with source refs.

### Manifest And Source Hashes

The raw manifest contains source custody information that is useful internally.
It also contains local provenance fields that must never be exposed. Only
repo-relative file names, hash algorithm, and hash values are eligible for
product custody receipts.

### Activation Curation

Activation curation can power use/avoid sections, input/output type, and
reasoning-type labels. It must not become a public explanation of internal
routing behavior.

### Intervention Semantics

Intervention semantics can power failure modes, premortem questions,
heuristics, mitigations, and practice prompts. Extraction metadata and curation
notes may support custody, but should not dominate the UI.

### Relation Semantics

Relation semantics can power relation pages and graph edges only when the
relation is supported. Confidence and source quote/ref should travel with the
relation. Approximate target-id mapping, deferred higher-order notes, and
unsupported relation ideas must stay out of the product surface until reviewed.

### Relationship Graph

The relationship graph can power graph neighborhoods, but raw affinity and
ranking fields are navigation internals. A product graph should link to
relation pages rather than asking the user to trust an edge label.

### Knowledge Graph

The knowledge graph is too broad for the first user surface. It can inform
future global navigation and collections, but should not be exposed as a full
topology before the smaller product pages and neighborhoods work.

### Embeddings

Embeddings are internal in v0. Semantic neighbors are suggestions only until a
reviewed relation semantics layer or another explicit gate supports them.

### Curated Chunks

Curated chunks can support teaching copy after source and privacy checks. Chunk
ids, guardrail tags, and internal trusted-surface structure should not become
the primary UI.

### Family Semantics

Family semantics can become future collections or graph filters, but family
membership and density are not quality labels or proof.

### V60 Affordances

V60 affordances can support advanced teaching pages later. Raw transaction JSON,
absence records, and runtime-promotion metadata are not product UI.

### Graph Survival And Evals

Graph survival and evaluation artifacts are internal evidence discipline. They
can caution later builders about noise, helpfulness, and failure modes, but they
are not product marketing, human validation, or correctness proof.

### Teacher Artifacts

No checked-in Teacher artifact directory is present in this worktree. If those
artifacts arrive later, they can seed Teacher lesson pages only after product
translation with source refs, missingness, visible review status, and explicit
non-claims.

## PR-P2 Stop Line

PR-P2 stops here.

Do not implement in this slice:

- Mental Model Product Page contracts;
- Relation Product Page contracts;
- Teacher Lesson Product contracts;
- Visual Graph contracts;
- model/relation data builders;
- page rendering;
- graph UI;
- runtime hooks;
- provider/model calls;
- product proof or human-validation claims.

## Decision Gate

Recommended next gate:
`proceed_to_user_facing_model_relation_contracts`

Reason: the important existing substrate is present and classified, the missing
Teacher artifacts are explicit, embeddings/evals remain internal, and the next
safe step is to define product-safe contracts before building any pages or
graphs.
