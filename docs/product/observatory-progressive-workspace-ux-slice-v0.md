# Observatory Progressive Workspace UX Slice v0

Status: portable workspace progressive-disclosure implementation
Date: 2026-07-06
Decision gate: `proceed_to_observatory_progressive_workspace_browser_review`

## Purpose

This slice implements the product-flow audit recommendation from
[Observatory Workspace Product Flow Audit](observatory-workspace-product-flow-audit-v0.md).

The selected-run Observatory workspace keeps the same route family, but the
page now starts from readable first-pass product cards and moves support data
behind disclosure blocks.

The product intent is:

```text
first read: what changed, what to practice, what model/relation explains it
second read: supporting model details, relation taxonomy, custody, missingness
advanced read: telemetry and raw audit inspection
```

## What Changed

### First-Read Cards

The workspace now marks primary product cards with `data-first-read-card`:

- Outcome leads with the revised answer summary and next actions.
- Learn leads with the practice rep and reasoning move.
- Model pages lead with "What This Model Helps You See".
- Relation pages keep the plain-language story first.
- Receipts lead with a trust summary.

These cards are not proof, review approval, or correctness claims. They are
the first layer of product reading.

### Disclosure Blocks

The workspace now uses server-rendered disclosure blocks for support material:

- Outcome support details.
- Lesson steps and boundaries.
- Model practice and failure detail.
- Model source, status, and boundaries.
- Relation taxonomy, confidence, and custody.
- Map custody and boundaries.
- Receipt source refs and missing fields.
- Advanced inspection index.
- Workspace boundary.

This keeps the data available without making the first screen feel like a raw
artifact browser.

### Model Page Language

The model-page heading changed from:

```text
Everything We Know
```

to:

```text
What This Model Helps You See
```

This avoids implying that the selected-run page is a complete canonical public
library entry.

### Advanced Audit Demotion

Advanced Audit remains linked, but the top navigation marks it as advanced
inspection rather than a peer of Outcome, Learn, Models, Relations, Map, and
Receipts.

Advanced Audit is still the correct place for:

- extraction;
- route traces;
- usage;
- graph survival;
- provider and prompt telemetry;
- older raw artifact inspection.

It is not the learner's first-read path.

### Map Selection Fix

The Map now updates the selected panel after search or relation filters:

- if the current selection remains visible, it stays selected;
- if the current selection is filtered out, the first visible node or edge is
  selected;
- if nothing remains visible, the panel shows a no-results state.

This prevents the selection panel from describing a hidden model or relation.

## Routes Preserved

The slice keeps the current route family:

```text
/
/workspace?case_id=<id>#outcome
/workspace?case_id=<id>#learn
/workspace?case_id=<id>#models
/workspace?case_id=<id>#relations
/workspace?case_id=<id>#map
/workspace?case_id=<id>#receipts
/models/<id>?case_id=<id>
/relations/<id>?case_id=<id>
/audit
```

No new runtime hook, provider call, archive mutation, or compiled SPA edit is
introduced.

## User-Experience Decision

Keep one long server-rendered workspace for portability, but make every surface
read in two layers:

```text
clear first-read card
  -> expandable support detail
```

This is a better next step than adding more pages because the backbone already
works. The problem identified by the audit was hierarchy, not missing routes.

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
- does not touch `SKILL.md`;
- does not touch `scripts/skill/*`;
- does not touch `scripts/archive_run.py`;
- does not claim product proof;
- does not claim human validation;
- does not claim answer correctness;
- does not claim advice correctness;
- does not authorize action;
- does not treat graph edges as proof;
- does not treat relation confidence as certification.

## Stop Line

This slice stops before:

- full corpus mental model library browsing;
- full corpus graph;
- runtime integration;
- default-on Conversation Understanding generation;
- new provider/model calls;
- product readiness claims;
- human validation claims;
- answer/advice correctness claims;
- action authorization.

Recommended next gate:
`proceed_to_observatory_progressive_workspace_browser_review`
