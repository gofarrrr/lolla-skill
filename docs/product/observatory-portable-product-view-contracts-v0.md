# Observatory Portable Product View Contracts v0

Status: product view model contract layer
Date: 2026-07-06
Decision gate: `proceed_to_observatory_portable_view_model_adapters`
Example bundle:
[Observatory portable product view contract examples](observatory-portable-product-view-contract-examples-v0.json)

## Purpose

This slice defines the product-safe view contracts for the portable
server-rendered Observatory direction.

The contracts live in:

```text
observatory/product_views.py
```

They validate the objects that should feed one selected-run Observatory
workspace:

```text
Outcome | Learn | Models | Relations | Map | Receipts
Advanced Audit
```

The validator is intentionally only a contract layer. It does not read run
archives, build adapters, render pages, call providers, invoke Lolla, create a
new run, mutate runtime behavior, touch `observatory/build/*`, or revive the
legacy Svelte root app.

## Why This Exists

The recent product work made a clear global decision: Observatory is the
portable skill presentation shell, and Teacher belongs inside it as Learn plus
Models, Relations, Map, and Receipts surfaces.

That still leaves a practical design problem. If the UI consumes raw audit
telemetry, raw Teacher notes, raw model Markdown, relation metadata, receipt
status, and graph nodes directly, the page becomes everything at once. The user
cannot tell what they are meant to learn, inspect, click, or trust.

This contract layer inserts the missing translation boundary:

```text
raw run and substrate artifacts
  -> read-only adapters
  -> product-safe view models
  -> portable Observatory UI
```

Primary UI surfaces should consume these product-safe view models. Advanced
Audit may keep inspecting raw artifacts because that is its job.

## Shared Requirements

Every product view object must carry:

- user-facing explanation or navigation purpose;
- source or custody reference;
- missingness or availability state;
- explicit non-claims.

Every object is rejected if it contains raw local paths, private/provider
markers, product-proof claims, runtime authorization claims, action
authorization claims, answer/advice correctness claims, Svelte revival flags,
or graph/relation proof language.

## View Models

| View model | Feeds | Job |
| --- | --- | --- |
| `selected_run_summary` | Header, Outcome | Identify the selected run, state, health, and available surfaces. |
| `outcome_summary` | Outcome compatibility | Preserve the older compact headline, clipped summary, strongest pressure, and model chips. |
| `outcome_value` | Outcome | Present the full practical run answer, what changed, primary reasons, confidence boundary, next moves, source refs, missingness, and non-claims. |
| `learning_packet` | Learn | Teach one reasoning move from the selected run. |
| `model_page` | Models | Present formatted durable mental model knowledge from canonical source and curation. |
| `relation_page` | Relations | Explain a model pair in plain language before taxonomy or confidence. |
| `graph_neighborhood` | Map | Navigate a small selected-run model and relation neighborhood. |
| `receipt_summary` | Receipts | Show custody, sidecar status, missingness, and visible non-claims. |
| `advanced_audit_index` | Advanced Audit | Enumerate raw inspection routes and artifact availability. |
| `product_workspace` | Root shell | Compose all selected-run surfaces under portable server rendering. |

## Workspace Contract

Required fields:

- `schema_version`;
- `rendering_direction`;
- `primary_surfaces`;
- `advanced_surface`;
- `selected_run_summary`;
- `outcome_summary`;
- `outcome_value`;
- `learning_packet`;
- `model_pages`;
- `relation_pages`;
- `graph_neighborhood`;
- `receipt_summary`;
- `advanced_audit_index`;
- `source_refs`;
- `missingness`;
- `non_claims`.

The contract requires:

```text
rendering_direction = portable_python_server_rendered_html
primary_surfaces = Outcome, Learn, Models, Relations, Map, Receipts
advanced_surface = Advanced Audit
```

This preserves the current product decision: keep rendering through the
portable Python/server HTML path for now. A Svelte revival or bundle sync would
require a separate explicit decision.

## Surface Contracts

### Outcome

Outcome answers:

```text
What happened in this run?
```

The compact `outcome_summary` remains available for compatibility, but the
product-facing Outcome source is now `outcome_value`.

`outcome_value` carries:

- `outcome_headline`;
- `stance`;
- `plain_language_answer`;
- `what_changed`;
- `primary_reasons`;
- `confidence_boundary`;
- `recommended_next_moves`;
- `source_refs`;
- `missingness`;
- `non_claims`.

Outcome should not duplicate the Teacher lesson body, canonical model pages,
relation taxonomy wall, receipts inventory, graph surface, or raw audit
telemetry. The first viewport should render the full answer and explanation
from `outcome_value`, not a clipped paragraph surrounded by navigation
ceremony.

### Learn

Learn answers:

```text
What reasoning move can I learn from this run?
```

It must carry the case anchor, reasoning trap, thinking move, relation story,
worked example, practice rep, do-not-overlearn boundary, model links, relation
links, source refs, human review status, missingness, and non-claims.

The contract requires `product_proof: false` and
`runtime_integration_authorized: false`.

### Models

Models answers:

```text
What does this mental model help me notice?
```

The model page contract carries formatted product sections:

- `one_sentence_meaning`;
- `helps_notice`;
- `use_when`;
- `avoid_when`;
- `common_misuse`;
- `failure_modes`;
- `practice_prompts`;
- `selected_run_backlinks`;
- `source_refs`;
- `source_hashes`;
- `curation_status`;
- `missingness`;
- `non_claims`.

Canonical Markdown can power these pages, but raw Markdown is not the product
UI. Selected-run activation can explain why the model appeared in a run, but
activation is not the durable model definition.

### Relations

Relations answers:

```text
What does this model pair teach?
```

The relation page contract carries source model, target model, relation type,
plain-language story, why it matters, misread risk, practice prompt, model
links, source refs, confidence, curation status, missingness, and non-claims.

The relation page must explain the edge in plain language before taxonomy.
Relation confidence is not proof, certification, human validation, answer
correctness, or advice correctness.

### Map

Map answers:

```text
How can I navigate the selected-run neighborhood?
```

The graph neighborhood contract carries graph id, scope, nodes, edges, source
refs, layout hint, default focus, filters, search availability, missingness,
and non-claims.

Edges are navigation. They must not expose raw affinity, rank, embedding
similarity, score, pagerank, or weight fields. They must link to relation pages
instead of trying to explain the whole relation in an edge label.

### Receipts

Receipts answers:

```text
What can I trust, inspect, or treat as missing?
```

The receipt summary contract carries learning packet status, Conversation
Understanding status, process brief status, source refs, missingness, advanced
links, visible non-claims, and machine-readable non-claims.

Receipts are custody and missingness, not product marketing, approval, or
certification.

### Advanced Audit

Advanced Audit answers:

```text
What happened inside the system?
```

It can link to raw inspection routes and artifact statuses. It remains
advanced inspection, not the normal user landing page and not learner copy.

## Rejection Coverage

The validator rejects:

- unsupported schema versions;
- missing required fields;
- malformed source refs;
- absolute local paths;
- private/provider markers;
- missing missingness;
- missing non-claims;
- `product_proof: true`;
- `human_validated: true`;
- `answer_correctness: true`;
- `advice_correctness: true`;
- `runtime_integration_authorized: true`;
- `action_authorized: true`;
- `graph_edges_are_proof: true`;
- `embedding_similarity_is_validated_relation_semantics: true`;
- `svelte_revival_authorized: true`;
- non-portable workspace rendering direction;
- graph edge ranking or affinity fields;
- relation or graph proof language.

## PR Stop Line

This PR stops before:

- read-only view model adapters;
- root workspace rendering;
- page rendering;
- graph UI;
- runtime integration;
- provider/model calls;
- Lolla invocation;
- new Lolla runs;
- archive mutation;
- legacy Svelte source changes;
- compiled bundle edits;
- product proof claims;
- human validation claims.

Recommended next gate:
`proceed_to_observatory_portable_view_model_adapters`
