# Observatory Focused Workspace Narration v0

Status: focused server-rendered Observatory UX implementation
Date: 2026-07-06
Decision gate: `proceed_to_observatory_focused_workspace_browser_review`

## Purpose

This slice implements the next recommendation from
[Observatory Progressive Workspace Browser Review](observatory-progressive-workspace-browser-review-v0.md).

The problem was not missing data. The problem was that the selected-run
workspace still behaved like a full artifact browser with product cards layered
on top. This slice keeps the portable Python/server-rendered Observatory owner,
keeps every route, and makes the browser experience feel more like a guided
workspace.

The intended first read is now:

```text
Start here:
  read the answer change
  practice one reasoning move
  inspect models and relations only when useful
  check receipts for trust and boundaries
```

## What Changed

### Focused Workspace Mode

The server still renders all workspace sections for portability and no-JS
fallback. In the browser, the workspace navigation script now activates one
surface at a time:

- Outcome;
- Learn;
- Models;
- Relations;
- Map;
- Receipts.

Inactive sections receive `hidden` in the browser. This turns the existing
anchor navigation into a focused surface switcher while preserving the same
route family and server-rendered fallback.

### Start-Here Narration

The workspace hero now includes a visible start path:

```text
Use this run as a short lesson.
Read the answer change first. Then practice one reasoning move...
```

It also shows four compact steps:

- read outcome;
- practice lesson;
- inspect models;
- check receipts.

This gives the user a reason for the page before they encounter the full data
stack.

### Outcome Markdown Cleanup

The product-view adapter now strips Markdown headings and inline Markdown
scaffolding before revised-answer text enters first-read outcome summaries.

This prevents archived results from showing headings such as `## Updated
position` inside the product card.

### Clearer Page Actions

Ambiguous actions changed from:

```text
Open standalone page
```

to:

```text
Open model page
Open relation page
```

The destination is now clear without requiring the user to understand the
implementation distinction between embedded cards and standalone routes.

### Map Narration And Labels

The Map now starts with a short wayfinding sentence:

```text
This map is a small wayfinding view for the current lesson.
```

Map SVG links now carry human `aria-label` values such as `Open model:
Authority Bias`, while technical type text is marked `aria-hidden`. This avoids
labels that read like `Authority Biasmental_model` in browser/accessibility
snapshots.

### Relation Filter Focus

When the user clicks a relation-type filter, the selected panel now prefers the
first visible relation edge instead of keeping a still-visible model selected.

This better matches user intent: filtering by relation type should foreground
the relation story.

## Routes Preserved

The slice keeps the same route family:

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
/audit/extraction
/usage
```

No compiled SPA bundle, runtime hook, provider call, archive mutation, sidecar
write, or skill invocation is introduced.

## User-Experience Decision

The current Observatory direction is:

```text
server-rendered, portable, selected-run workspace
  -> one active product surface at a time
  -> expandable custody and support details
  -> Advanced Audit only for technical inspection
```

This is still not a full public mental model library. The mental model pages
remain selected-run scoped, not canonical corpus pages.

## Remaining UX Risks

- The selected-run sidebar still shows recent runs early in the experience.
- Advanced Audit is still visible in the top nav, though visually marked as
  advanced.
- The standalone model page still leads with selected-run boundary copy before
  the model's deeper learning value.
- Receipts source refs remain dense when expanded.
- The focused mode should be checked in a real browser before adding more
  product data.

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
- provider/model API calls;
- product readiness claims;
- human validation claims;
- answer/advice correctness claims;
- action authorization.

Recommended next gate:
`proceed_to_observatory_focused_workspace_browser_review`
