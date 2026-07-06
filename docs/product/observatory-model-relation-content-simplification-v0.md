# Observatory Model Relation Content Simplification v0

Status: implemented
Date: 2026-07-06
Decision gate: `proceed_to_observatory_workspace_visual_polish_review`

## Purpose

This slice implements the next step from the workspace content audit: reduce
the amount of model and relation detail shown inside the main selected-run
workspace, while preserving full drill-down pages.

The product intent:

```text
workspace = browse and choose
detail page = read and inspect
receipts = custody and technical evidence
```

## Implemented Changes

### Models Workspace Surface

Models workspace surface is now a light index.

Each model card shows:

- model name;
- one-sentence meaning;
- use-when cue;
- mislead cue;
- Open model page link.

The workspace no longer puts full model detail in the main flow.

full model detail remains on `/models/<model-id>`, including:

- What This Model Helps You See;
- helps-notice detail;
- use/avoid detail;
- practice and failure detail;
- source/status/boundaries;
- missingness and non-claims.

### Relations Workspace Surface

Relations workspace surface is now a story-first index.

Each relation card shows:

- relation title;
- plain-language relation story;
- why it matters;
- misread risk;
- practice prompt;
- model links;
- Open relation page link.

The workspace no longer leads with relation taxonomy, confidence, or custody.

full relation detail remains on `/relations/<relation-id>`, including:

- Plain Language Story;
- Why It Matters;
- Misread Risk;
- Practice prompt;
- Taxonomy, confidence, and custody;
- source refs, missingness, and non-claims.

## Browser Check

The local browser check used a static in-memory Observatory fixture for
`lolla-audit`. It did not run Lolla, invoke the skill, call providers, create a
new run, write sidecars, or edit the compiled SPA bundle.

Checked behavior:

- `/workspace?case_id=lolla-audit#models` shows model index cards and Open
  model page links;
- `/models/authority-bias?case_id=lolla-audit` still shows the full model page;
- `/workspace?case_id=lolla-audit#relations` shows relation story cards and
  Open relation page links;
- `/relations/authority-bias__first-principles-thinking__antagonist?case_id=lolla-audit`
  still shows taxonomy, confidence, custody, and missingness after the story;
- no legacy Teacher drawer or `data-teacher-graph` DOM appeared.

## User Experience Result

The workspace now reads more like a learning dashboard:

- Outcome anchors the case.
- Learn gives the practice move.
- Models lets the user choose a concept.
- Relations lets the user choose a pair lesson.
- Map remains wayfinding.
- Receipts remain custody and non-claims.

This avoids showing model encyclopedia detail and relation taxonomy before the
user has chosen to inspect them.

## Strongest Useful Signal

The strongest useful signal is that the workspace and drill-down pages now have
different jobs. The workspace helps a user choose what to inspect. The detail
routes carry the deeper model and relation knowledge.

## Strongest Unresolved Risk

The remaining risk is visual polish and copy density. The information hierarchy
is now cleaner, but the workspace still needs a focused visual review for
spacing, repeated labels, compact sidebar language, and mobile scanning.

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
proceed_to_observatory_workspace_visual_polish_review
```

Stop before:

- runtime integration;
- provider or model API calls;
- new Lolla runs;
- full corpus graph;
- product readiness claims;
- human validation claims;
- answer or advice correctness claims;
- action authorization.
