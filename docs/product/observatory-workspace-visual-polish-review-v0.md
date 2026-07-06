# Observatory Workspace Visual Polish Review v0

Status: implemented
Date: 2026-07-06
Decision gate: `proceed_to_observatory_workspace_user_review_packet`

## Purpose

This slice follows the workspace content simplification with a browser-visible
polish pass. The goal is not to add another Observatory surface. The goal is to
make the selected-run workspace easier to read when a user first opens it and
when they switch to Learn, Models, Relations, Map, or Receipts.

The product question for this slice:

```text
What should the first screen explain, and what should get out of the way once
the user chooses a surface?
```

## UX Audit Finding

The browser audit showed the right information architecture but too much
orientation copy competing with the selected section.

The workspace already has the correct progression:

```text
Outcome -> Learn -> Models -> Relations -> Map -> Receipts
```

The issue was presentation:

- the page title sounded like an internal workspace label;
- the lede explained several jobs at once;
- the Start Here panel stayed visible even when the user opened Learn or another
  focused section;
- the sidebar Surface Homes list repeated explanatory text that made the page
  feel more like an operator checklist than a product surface;
- mobile scanning required too much reading before the active section.

## Implemented Visual Polish

### Workspace Title

The title now says:

```text
Run Learning Workspace
```

This frames Observatory as a learning surface for a completed run, not as a raw
telemetry console or a separate Teacher app.

### First-Read Lede

The lede now says:

```text
Read the outcome, practice one reasoning move, then inspect the models,
relations, map, and receipts behind it.
```

This keeps the page promise short:

- Outcome is the first read;
- Learn is the practice move;
- Models, Relations, Map, and Receipts are optional inspection layers.

### Start Panel Behavior

The Start Here panel remains available on the default Outcome surface because
that is where a new user needs orientation.

When the user switches to Learn, Models, Relations, Map, or Receipts, the Start
Here panel is hidden from the visible reading flow and marked `aria-hidden`.
In short: the Start Here panel is hidden once a focused surface is selected.

This keeps the chosen surface in charge:

- Learn starts with the practice move;
- Models starts with model cards;
- Relations starts with relation stories;
- Map starts with wayfinding;
- Receipts starts with custody and non-claims.

### Sidebar Copy

The Surface Homes sidebar now lists the surface names only:

```text
Outcome
Learn
Models
Relations
Map
Receipts
```

The sidebar is a wayfinding aid, not a second explanation of the whole product.

## Information Hierarchy

This slice preserves the current information ladder:

```text
first read -> optional support -> drill-down page -> receipts/audit
```

What each surface should do:

- Outcome: show what changed or survived in the run.
- Learn: teach one case-anchored reasoning move.
- Models: let the user pick a reusable mental model to inspect.
- Relations: explain a model-pair lesson before taxonomy.
- Map: provide small-neighborhood wayfinding.
- Receipts: show custody, missingness, and non-claims.

What should not lead the page:

- raw JSON;
- raw telemetry;
- confidence as proof;
- graph edges as proof;
- extraction metadata as product copy;
- a duplicate standalone Teacher experience.

## Browser Check

The local browser check used an in-memory Observatory fixture for
`lolla-audit`. It did not run Lolla, invoke the skill, call providers, create a
new run, write sidecars, or edit the compiled SPA bundle.

Checked behavior:

- desktop `/workspace?case_id=lolla-audit` shows the new title, shorter lede,
  Start Here orientation, and compact Surface Homes list;
- desktop default surface still opens on Outcome;
- browser click-through covered Outcome, Learn, Models, Relations, Map, and
  Receipts;
- Start Here remains visible only on Outcome and is visually hidden on Learn,
  Models, Relations, Map, and Receipts;
- mobile `/workspace?case_id=lolla-audit#learn` shows Learn as the focused
  section without the Start Here panel taking the first read;
- mobile body width does not exceed viewport width;
- workspace navigation still switches between Outcome, Learn, Models,
  Relations, Map, and Receipts;
- Receipts and Advanced Audit links remain present.

## Strongest Useful Signal

The workspace is starting to behave like one product rather than a pile of
available artifacts. The default page explains the path, and focused sections
can now lead with their own content.

## Strongest Unresolved Risk

This is still a fixture-backed browser audit, not a human review. The next risk
is whether the hierarchy makes sense to a real user across multiple actual run
types, especially when model and relation coverage is partial.

## Recommended Next PR

Proceed to:

```text
proceed_to_observatory_workspace_user_review_packet
```

Expected next slice:

- create a user-review packet for the selected-run workspace;
- compare Outcome, Learn, Models, Relations, Map, and Receipts as one flow;
- ask what feels understandable, what feels technical, and what feels missing;
- do not pre-fill review as positive;
- keep diagnostic or synthetic review separate from human validation.

Stop before:

- runtime integration;
- provider or model API calls;
- new Lolla runs;
- full corpus graph;
- product readiness claims;
- human validation claims;
- answer or advice correctness claims;
- action authorization.

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
