# Observatory Legacy Teacher Renderer Cleanup v0

Status: implemented cleanup slice
Date: 2026-07-06
Decision gate: `proceed_to_observatory_workspace_accessibility_text_noise_cleanup`

## Purpose

This slice removes the last code-level ambiguity left after Teacher Learn was
consolidated into the selected-run Observatory workspace.

Before this cleanup:

- `/teacher-learning` already redirected to `/workspace?case_id=<id>#learn`;
- `/api/case/<id>/teacher-learning` remained the read-only Teacher packet API;
- the old `_render_teacher_learning_html` direct renderer still existed for
  historical tests;
- old hash-drawer graph code and drawer CSS still appeared in the shared page
  source even though the visible product path no longer used them.

That was enough to keep a second Teacher UX alive as a maintenance contract.
This slice removes that ambiguity.

## Product Contract

There is one visible Teacher product path:

```text
/workspace?case_id=<selected-case-id>#learn
```

The compatibility route remains:

```text
/teacher-learning -> /workspace?case_id=<selected-case-id>#learn
```

The packet API remains:

```text
/api/case/<id>/teacher-learning
```

The API is data. The workspace is the visible product. The old all-in-one Teacher page is no longer a maintained renderer.

## Implemented Changes

### Removed Legacy Direct Renderer

The direct `_render_teacher_learning_html` renderer was removed from
`observatory/serve_result.py`.

The tests that previously used it now verify the selected-run workspace Learn,
Models, Relations, Map, and Receipts surfaces instead.

### Removed Old Drawer Graph Contract

The old Teacher graph used hash links such as:

```text
#model-authority-bias
#relation-authority-bias__first-principles-thinking__antagonist
```

The workspace graph now links to durable product pages:

```text
/models/<model-id>?case_id=<id>
/relations/<relation-id>?case_id=<id>
```

The old `data-teacher-graph`, drawer return-hash logic, and unused drawer CSS
were removed from the server-rendered source.

### Preserved Current Routes

This slice does not change the public route behavior:

- `/teacher-learning` still redirects into the workspace Learn surface;
- `/api/case/<id>/teacher-learning` still returns the Teacher packet payload;
- `/workspace` remains the selected-run product home;
- `/models/<id>` and `/relations/<id>` remain product page routes.

## What This Means For Users

Users should no longer encounter or maintain two different Teacher page shapes.

They see:

```text
Outcome -> Learn -> Models -> Relations -> Map -> Receipts
```

The Learn surface teaches the reasoning move. The model and relation pages are
durable drill-downs. The Map is wayfinding. Receipts handle custody,
missingness, and audit links.

## What This Means For Reviewers

Reviewers can still inspect the Teacher packet through:

```text
/api/case/<id>/teacher-learning
```

Reviewers can still inspect technical artifacts through Receipts and Advanced
Audit. The cleanup does not reduce auditability; it removes a redundant HTML
product renderer.

## Browser Check

The local browser check used a static in-memory Observatory fixture for
`lolla-audit`. It did not run Lolla, invoke the skill, call providers, create a
new run, write sidecars, or edit the compiled SPA bundle.

Checked routes and interactions:

- `/teacher-learning` redirects to `/workspace?case_id=lolla-audit#learn`;
- `/api/case/lolla-audit/teacher-learning` returns the Teacher packet adapter;
- the workspace exposes Outcome, Learn, Models, Relations, Map, and Receipts as
  the first-level progression;
- Models opens durable `/models/<id>?case_id=lolla-audit` pages;
- Relations opens durable `/relations/<id>?case_id=lolla-audit` pages;
- Map exposes search, relation filter, reset, and selected-node links through
  `data-observatory-graph`;
- Receipts shows trust status, visible non-claims, and deeper audit links;
- no `data-teacher-graph` or drawer panel appeared in the checked browser DOM.

## Strongest Useful Signal

The strongest useful signal is that the codebase now matches the user-facing
information architecture: Teacher is a mode inside the selected-run workspace,
not a separate all-in-one page with different navigation and graph behavior.

## Strongest Unresolved Risk

The remaining risk is text/accessibility noise from the workspace page source.
The visible browser path is clean, but raw text extraction can still include
hidden sections and scripts. The next slice should reduce that non-visible
technical noise without changing runtime behavior or weakening receipts.

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
proceed_to_observatory_workspace_accessibility_text_noise_cleanup
```

Stop before:

- runtime integration;
- provider or model API calls;
- default-on generation;
- product readiness claims;
- human validation claims;
- answer or advice correctness claims;
- action authorization.
