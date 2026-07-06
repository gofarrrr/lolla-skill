# Observatory Server Rendered Root Workspace v0

Status: portable root workspace renderer
Date: 2026-07-06
Decision gate: `proceed_to_observatory_workspace_navigation_source_of_truth`

## Purpose

This slice turns the portable Observatory direction into a visible root
workspace.

The root `/` and `/workspace` routes now render one selected run through the
validated product workspace view model from:

```text
observatory/product_view_adapters.py
```

In plain route language, root / and /workspace are now the same portable
workspace family.

The page is not a raw dump of Teacher packets, telemetry, Markdown, curation
JSON, or review artifacts. It consumes the product-safe workspace object and
organizes the user flow as:

```text
Outcome -> Learn -> Models -> Relations -> Map -> Receipts
```

Advanced Audit remains available as the inspection surface for raw run
telemetry and internal evidence discipline.

## Routes Added Or Changed

New API route:

```text
/api/case/<id>/product-workspace
```

This route returns the same adapter wrapper used by the root renderer. It is
read-only and returns `available: false` with explicit missingness if no matching
Teacher learning packet exists.

Server-rendered workspace routes:

```text
/
/workspace
/workspace?case_id=<selected-case-id>
```

Legacy compiled SPA route:

```text
/index.html
```

The old compiled bundle is still served there, with the existing Observatory
overlays injected when `observatory/build/index.html` exists. This slice does
not edit `observatory/build`.

## UX Shape

The first viewport now answers:

```text
What run am I looking at, and what are the available product surfaces?
```

The main reading order is:

1. Outcome: what changed in the selected run.
2. Learn: the reasoning move the user can practice.
3. Models: formatted mental model pages from product-safe model objects.
4. Relations: model-pair lesson pages, with plain-language story before
   taxonomy or confidence.
5. Map: a small selected-run neighborhood summary for navigation only.
6. Receipts: custody, Conversation Understanding status, process brief status,
   missingness, non-claims, and Advanced Audit links.

The side rail keeps the selected run visible and lists recent selectable runs
without showing local result paths.

## Mental Model Clickthrough

Model chips and graph nodes resolve to in-page model anchors such as:

```text
#model-authority-bias
```

Each model section is a formatted page card with:

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

This is the first concrete answer to the UX gap where a user could see a model
name but had no clear way to inspect everything we know about that model.

## Relation Clickthrough

Relation chips and graph edges resolve to in-page relation anchors such as:

```text
#relation-authority-bias__first-principles-thinking__antagonist
```

Each relation section leads with the plain-language story, then why it matters,
misread risk, practice prompt, model links, and only then taxonomy and
confidence.

Relation confidence is not proof, certification, human validation, answer
correctness, or advice correctness.

## Styling

The root workspace borrows the existing Observatory Teacher Learn visual
language:

- deep indigo background;
- teal primary accent;
- quiet translucent panels;
- `Inter` and `JetBrains Mono`;
- compact server-rendered cards;
- no new standalone frontend framework;
- no compiled bundle edits.

The point is not to create a second Observatory aesthetic. The page is the same
portable Observatory family, reorganized into a clearer product reading order.

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
- does not authorize action.

## Stop Line

This PR stops before:

- standalone `/models/<id>` routes;
- standalone `/relations/<id>` routes;
- browser graph UI;
- full corpus graph;
- runtime integration;
- default-on Conversation Understanding generation;
- source-port work into any old Svelte app;
- product readiness claims.

Recommended next gate:
`proceed_to_observatory_workspace_navigation_source_of_truth`
