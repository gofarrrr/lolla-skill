# Observatory Workspace Accessibility Text Noise Cleanup v0

Status: implemented cleanup slice
Date: 2026-07-06
Decision gate: `proceed_to_observatory_workspace_content_audit_and_simplification`

## Purpose

This slice makes the selected-run Observatory workspace match the product
progression at the document level, not only after the browser script runs.

The intended first read is:

```text
Start Here + Outcome
```

The user can then switch through:

```text
Outcome -> Learn -> Models -> Relations -> Map -> Receipts
```

Before this slice, the browser script hid non-active workspace surfaces after
load, but the server-rendered HTML shipped Outcome, Learn, Models, Relations,
Map, and Receipts as simultaneously visible sections. That made raw text
extraction and early accessibility snapshots noisier than the intended product
experience.

## Implemented Contract

The server default is Start Here plus Outcome.

The non-active surfaces are hidden:

- Learn;
- Models;
- Relations;
- Map;
- Receipts.

Each workspace section now carries `data-workspace-section`. The default Outcome
section is marked active. The other surfaces start with `hidden` and
`aria-hidden="true"`.

The browser navigation keeps the same route contract, but now also updates
`aria-hidden` when a user switches surfaces. This preserves the visible
workspace flow while reducing accidental text/accessibility overload.

## What Users See

The user starts with:

- the selected run context;
- a short Start Here path;
- Outcome as the first active surface.

The user can then choose Learn, Models, Relations, Map, or Receipts. The product
still allows drill-down, but it no longer presents every major surface as the
first accessible document state.

## What Reviewers Can Still Inspect

This slice does not remove data or routes.

Reviewers can still inspect:

- `/workspace?case_id=<id>#learn`;
- `/workspace?case_id=<id>#models`;
- `/workspace?case_id=<id>#relations`;
- `/workspace?case_id=<id>#map`;
- `/workspace?case_id=<id>#receipts`;
- `/models/<model-id>?case_id=<id>`;
- `/relations/<relation-id>?case_id=<id>`;
- `/api/case/<id>/teacher-learning`;
- `/audit`, `/audit/extraction`, and `/usage` from Receipts.

## Browser Check

The local browser check used a static in-memory Observatory fixture for
`lolla-audit`. It did not run Lolla, invoke the skill, call providers, create a
new run, write sidecars, or edit the compiled SPA bundle.

Checked behavior:

- default workspace snapshot exposed Outcome without dumping Learn, Models, Relations, Map, and Receipts into the accessibility tree;
- switching to Learn exposed the Learn first-read surface;
- switching to Map exposed the graph controls and `data-observatory-graph`;
- switching to Receipts exposed trust summary, visible non-claims, and technical
  inspection links;
- no `data-teacher-graph` or drawer panel appeared in the checked browser DOM.

## Strongest Useful Signal

The strongest useful signal is that the workspace now behaves like a progressive
product surface at first read: the page starts general, then the user chooses
more detail.

## Strongest Unresolved Risk

The remaining risk is content design, not route ownership. The workspace now has
the right progressive container, but the next PR should audit the actual content
of each surface:

- what data is shown;
- why it is shown;
- what belongs in the first read;
- what belongs behind expansion;
- what should be removed, renamed, or moved into Receipts.

## Boundaries

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

## Decision Gate

Proceed to:

```text
proceed_to_observatory_workspace_content_audit_and_simplification
```

Stop before:

- runtime integration;
- provider or model API calls;
- default-on generation;
- product readiness claims;
- human validation claims;
- answer or advice correctness claims;
- action authorization.
