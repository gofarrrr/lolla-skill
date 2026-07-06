# Observatory Workspace Navigation Source Of Truth v0

Status: portable navigation source of truth and selected-run detail routes
Date: 2026-07-06
Decision gate: `proceed_to_observatory_workspace_map_interaction_slice`

## Purpose

This slice makes the server-rendered Observatory workspace the canonical
portable navigation surface for the selected run.

The previous root workspace made the product flow readable:

```text
Outcome -> Learn -> Models -> Relations -> Map -> Receipts
```

But model and relation clickthroughs still collapsed into in-page anchors. That
made the user experience feel half-built: the user could see "Authority Bias" or
a relation edge, but could not open a stable page for that object.

This slice adds shared Observatory route helpers and selected-run detail routes
for model and relation pages.

## Routes Added Or Settled

Shared workspace navigation now resolves the primary product surfaces as:

```text
/workspace?case_id=<selected-case-id>#outcome
/workspace?case_id=<selected-case-id>#learn
/workspace?case_id=<selected-case-id>#models
/workspace?case_id=<selected-case-id>#relations
/workspace?case_id=<selected-case-id>#map
/workspace?case_id=<selected-case-id>#receipts
/audit
```

Durable selected-run object routes:

```text
/models/<id>?case_id=<selected-case-id>
/relations/<id>?case_id=<selected-case-id>
```

The object routes are selected-run scoped. They do not claim to be a full-corpus
public library, and they do not expose raw canonical Markdown, curation JSON,
embedding records, or raw relation ranking as the product UI.

## What Changed

The server renderer now has shared Observatory route helpers for:

- workspace section links;
- Teacher Learn links back into the same workspace route family;
- model detail URLs;
- relation detail URLs;
- product object links emitted by the adapter.

The workspace renderer no longer converts adapter `/models/...` and
`/relations/...` links into local anchors. Model chips, relation chips, map
nodes, and map edges now resolve to durable selected-run URLs.

The old in-page `id="model-..."` and `id="relation-..."` anchors remain on the
workspace page because they are useful local landmarks, but they are no longer
the primary clickthrough target.

## Mental Model Page UX

A model URL such as:

```text
/models/authority-bias?case_id=lolla-audit
```

renders a readable mental model page for the selected run:

- display name;
- one-sentence meaning;
- helps-notice bullets;
- use-when bullets;
- avoid-when bullets;
- common misuse;
- failure modes;
- practice prompts;
- curation status;
- source custody;
- missingness;
- non-claims.

This is still product-safe translation, not a raw Markdown reader. Canonical
Markdown can power the model object, but the UI presents the product object.

## Relation Page UX

A relation URL such as:

```text
/relations/authority-bias__first-principles-thinking__antagonist?case_id=lolla-audit
```

renders the selected-run relation page with story before taxonomy:

1. plain-language relation story;
2. why it matters;
3. misread risk;
4. practice prompt;
5. model links;
6. taxonomy;
7. confidence;
8. source custody;
9. missingness;
10. non-claims.

Relation confidence is displayed as context only. It is not proof,
certification, answer correctness, advice correctness, or human validation.

## One-System Rule

This does not create a second Observatory UX.

The intended product homes are:

- Outcome: what changed in the selected run.
- Learn: the reasoning move worth practicing.
- Models: durable mental model knowledge.
- Relations: model-pair lesson pages.
- Map: selected-run navigation neighborhood.
- Receipts: custody, missingness, and process status.
- Advanced Audit: raw telemetry and inspection details.

The Teacher Learn page now points back to this same route family in its top
navigation. It remains available as a focused Learn page, but the workspace is
the main product reading order.

## Boundary Confirmation

This slice:

- does not run Lolla;
- does not invoke the Lolla skill;
- does not call providers or model APIs;
- does not create new Lolla runs;
- does not wire runtime behavior;
- does not mutate archives;
- does not write sidecars;
- does not edit `observatory/build`;
- does not edit observatory/build;
- does not touch `SKILL.md`;
- does not touch `scripts/skill/*`;
- does not touch `scripts/archive_run.py`;
- does not claim product proof;
- does not claim human validation;
- does not claim answer correctness;
- does not claim advice correctness;
- does not authorize action;
- does not treat graph edges as proof.

## Stop Line

This PR stops before:

- browser graph UI interaction;
- full corpus graph;
- full corpus mental model library;
- runtime integration;
- default-on Conversation Understanding generation;
- source-port work into any old Svelte app;
- product readiness claims;
- human validation claims.

Recommended next gate:
`proceed_to_observatory_workspace_map_interaction_slice`
