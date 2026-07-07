# Observatory Outcome Progressive Disclosure v0

Status: implemented UI slice.

Date: 2026-07-07

Decision gate:
`proceed_to_browser_review_outcome_flow`

Related design:
[Observatory Content Progression PRD](observatory-content-progression-prd-v0.md)

Previous slice:
[Observatory Outcome First Viewport](observatory-outcome-first-viewport-v0.md)

## Purpose

This slice tightens the first visible Outcome experience.

The previous Outcome viewport correctly moved the actual run result above run
contents and support details. Browser review still showed a product problem:
the center card presented the answer, three equal detail groups, and three
equal next actions. Combined with the sidebar path and header export button,
that made the first screen feel like options and ceremony instead of a simple
answer.

The new shape is:

1. result headline;
2. full plain-language answer;
3. one reason the answer changed;
4. one main reason to keep in mind;
5. one recommended continuation;
6. secondary actions behind disclosure;
7. run contents below the Outcome first read.

## What Changed

Outcome now renders one recommended continuation in the first-read card.

When Teacher surfaces are present, the primary continuation is:

```text
Practice the reasoning move
```

When Teacher surfaces are missing, the primary continuation becomes:

```text
Check what is available
```

That missing-packet path sends the user to Receipts rather than pretending a
lesson exists.

Secondary actions remain available behind `More outcome detail`. This includes
additional reason groups, confidence-boundary bullets, and alternate actions
such as Receipts or private agent-memory export.

## Information Hierarchy

Outcome remains the result-first surface. It should answer:

```text
What did this run conclude or change?
```

The first-read card should not force the user to choose between product paths
before they understand the answer. The page still supports progression, but the
progression is staged:

- first: understand the outcome;
- then: continue to Learn or Receipts depending on what exists;
- later: open more outcome detail if the user needs reasons, boundaries, or
  alternate actions;
- below that: inspect what the run contains.

## What We Show First

We show:

- the outcome stance;
- the outcome headline;
- the full plain-language answer;
- the first available `what_changed` point;
- the first available primary reason;
- one continuation action.

This is the general view. It is designed for a user who opened Observatory and
wants to know what the run is saying before seeing telemetry, inventory, or
review structure.

## What We Expand

Behind `More outcome detail`, we show:

- all available `what_changed` points;
- primary reasons;
- confidence-boundary points;
- secondary actions.

This keeps the information available without turning the first screen into a
table or audit panel.

## Download MD

Download MD stays visible in the workspace header. It is not hidden inside
Receipts. Outcome no longer needs to promote the same export as an equal
first-read choice because the header already gives the user the action.

The Markdown export remains a private agent-memory affordance. It is not a
product-proof claim, answer-correctness claim, or human-validation claim.

Browser verification for this slice also caught a narrow failure: a server
launched with only a standalone current `result.json` could show the visible
Download MD button but return a 500 because the archive-style memory builder
expected required sidecars. The route now falls back to a temporary read-only
current-result bundle, keeps missing artifacts explicit, and includes the full
captured transcript when the result contains captured turns and the user
requests the private raw-conversation export.

## Boundary

This slice:

- does not run Lolla;
- does not invoke the Lolla skill;
- does not call providers or model APIs;
- does not create a new run;
- does not generate sidecars;
- does not wire skill runtime behavior;
- does not mutate archives;
- does not edit `observatory/build/*`;
- does not touch `SKILL.md`;
- does not touch `scripts/skill/*`;
- does not touch `scripts/archive_run.py`;
- does not claim product proof;
- does not claim human validation;
- does not claim answer correctness;
- does not claim advice correctness;
- does not authorize automatic action.

## Recommended Next Gate

`proceed_to_browser_review_outcome_flow`

Reason: the source-rendered Outcome hierarchy now matches the intended content
progression. The next check should be browser review across at least one
Teacher-backed run and one run-only fallback to confirm that the page reads as
an answer first, not a table or review packet.
