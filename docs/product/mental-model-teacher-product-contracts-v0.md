# Mental Model Teacher Product Contracts v0

Status: PR-P3 contract layer
Date: 2026-07-05
Decision gate: `proceed_to_pilot_model_relation_page_data_builder`
Example bundle:
[Mental Model Teacher product contract examples](mental-model-teacher-product-contract-examples-v0.json)

## Purpose

This slice defines the product-safe object contracts for the Mental Model
Teacher Product Surface / Visual Mental Model Library lane.

The contracts live in:

```text
engine/system_b/mental_model_teacher_product_contracts.py
```

They validate four user-facing object shapes:

- Mental Model Product Page object;
- Relation Product Page object;
- Teacher Lesson Product object;
- Visual Graph object.

The validator is intentionally only a contract layer. It does not read the substrate.
It does not build product data, render pages, create graph UI, call providers,
or wire runtime behavior.

## Shared Requirements

Every product object must carry:

- user-facing explanation;
- source or custody reference;
- missingness or uncertainty state;
- explicit non-claims.

Every object is rejected if it contains raw local paths, private/provider
markers, product-proof claims, runtime authorization claims, action
authorization claims, or graph/relation proof language.

## Mental Model Product Page

Required fields:

- `schema_version`;
- `model_id`;
- `slug`;
- `display_name`;
- `one_sentence_meaning`;
- `helps_notice`;
- `use_when`;
- `avoid_when`;
- `common_misuse`;
- `failure_modes`;
- `premortem_questions`;
- `heuristics`;
- `practice_prompts`;
- `reasoning_types`;
- `source_refs`;
- `source_hashes`;
- `curation_status`;
- `missingness`;
- `non_claims`.

The object can later be built from canonical Markdown, manifest hashes,
activation curation, and intervention semantics. PR-P3 does not build it.

## Relation Product Page

Required fields:

- `schema_version`;
- `relation_id`;
- `source_model_id`;
- `target_model_id`;
- `relation_type`;
- `plain_language_story`;
- `why_it_matters`;
- `misread_risk`;
- `practice_prompt`;
- `source_quote_or_ref`;
- `confidence`;
- `curation_status`;
- `missingness`;
- `non_claims`.

The relation page must explain the edge in plain language before taxonomy. It
must carry `relation_is_not_proof` and `confidence_is_not_certification`.
Relation confidence is not product proof, human validation, or correctness.

## Teacher Lesson Product

Required fields:

- `schema_version`;
- `lesson_id`;
- `case_id`;
- `case_anchor`;
- `thinking_move`;
- `model_stack`;
- `relation_story`;
- `model_links`;
- `relation_links`;
- `practice_rep`;
- `do_not_overlearn`;
- `source_refs`;
- `human_review_status`;
- `product_proof`;
- `runtime_integration_authorized`;
- `missingness`;
- `non_claims`.

The contract requires `product_proof: false` and
`runtime_integration_authorized: false`. A lesson may teach a reasoning move,
but it is not advice, product proof, human validation, or action authorization.

## Visual Graph

Required fields:

- `schema_version`;
- `graph_id`;
- `graph_scope`;
- `nodes`;
- `edges`;
- `source_artifacts`;
- `layout_hint`;
- `default_focus`;
- `filters`;
- `missingness`;
- `non_claims`.

The graph object must carry `graph_is_navigation_not_proof` and
`edge_is_not_proof`. Edges must not expose raw affinity, rank, embedding
similarity, or score fields.

## PR-P3 Stop Line

PR-P3 stops before:

- data builders;
- model page rendering;
- relation page rendering;
- Teacher lesson rendering;
- graph data building;
- graph UI;
- full-corpus graph work;
- runtime integration;
- provider/model calls.

Recommended next gate:
`proceed_to_pilot_model_relation_page_data_builder`
