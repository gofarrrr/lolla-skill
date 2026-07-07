# Observatory Review Guide Hierarchy Prompts

Status: implemented for review
Date: 2026-07-07
Decision gate: `ready_for_human_review_with_hierarchy_prompts`

## Purpose

The Observatory Workspace now has clearer hierarchy cues, but the human review
guide also needs to test whether those cues work for a cold user.

This slice updates the visible Review Guide so the reviewer is not only asked
whether the workspace feels unified. The reviewer is now asked to name the
information hierarchy:

- what is primary product content;
- what is reusable learning material;
- what is optional inspection;
- where technical detail becomes distracting.

## Product Question

The core user question is:

> Can I understand what I am looking at, what to read first, what to open next,
> and what is only there for inspection?

The expected visible progression remains:

Outcome state -> Learn -> Models -> Relations -> Map -> Receipts

Audit and extraction pages are still available, but they should be optional
inspection, not the first product task.

## UX Change

The `/review/observatory-workspace` page now includes a cold user hierarchy check:

- `primary: Outcome and Learn`
- `supporting: Models, Relations, and Map`
- `inspection: Receipts and Audit`

The guide also asks the reviewer to check whether they can tell:

- Outcome from Learn: result state versus teaching move;
- Library view from Run context on model pages;
- role labels as navigation cues, not proof;
- Map as navigation rather than proof;
- Receipts as custody and missingness rather than the main product;
- technical audit pages as optional inspection.

## What Reviewers Should Record

The reviewer should write down:

- the first thing they thought the workspace was for;
- the first surface or link they wanted to open next;
- any point where primary product content blurred into receipts, audit, or
  telemetry;
- any model or relation page where Library view and selected-run context were
  hard to separate;
- any technical detail that pulled attention away from the learning journey.

## Boundary

This slice:

- does not run Lolla;
- does not invoke the Lolla skill;
- does not call providers or model APIs;
- does not create a new run;
- does not wire skill runtime behavior;
- does not edit `observatory/build`;
- does not claim product proof;
- does not claim human validation;
- does not claim answer correctness;
- does not claim advice correctness;
- does not authorize automatic action.

## Relationship To Previous Slice

This follows [Observatory Workspace Hierarchy Cues](observatory-workspace-hierarchy-cues-v0.md).

That slice added visible cues. This slice adds the human-review questions that
make those cues auditable.

## Next Gate

Recommended next gate:

`ready_for_human_review_with_hierarchy_prompts`

The next reviewer task is to open the workspace cold, follow the Review Guide,
and mark where the information hierarchy is still confusing.
