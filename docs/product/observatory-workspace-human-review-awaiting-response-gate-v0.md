# Observatory Workspace Human Review Awaiting Response Gate

Status: awaiting real human hierarchy review response.

Date: 2026-07-07

Decision gate: `awaiting_real_human_hierarchy_review_response`

## Purpose

The Observatory workspace has enough review scaffolding to stop adding more UX
surface by default and ask a real human to evaluate what is already visible.

The review scaffold is ready, but the real human response is still absent.
This slice records that pause point. It does not add a completed review, does
not add a captured intake artifact, and does not treat the current UI as
validated.

## Current State

The current offline review path includes:

- the server-rendered Observatory workspace;
- the Review Guide entry point;
- the focused human hierarchy scorecard;
- the blank human review form;
- the reviewer and operator instructions;
- the deterministic capture command for a completed form.

The missing artifacts are:

```text
reviews/human/observatory-workspace/review.json
reviews/human/observatory-workspace/intake.json
```

Those files should appear only after a real human completes the scorecard and an
operator captures the intake.

## What The Human Should Judge

The review should answer whether the visible Observatory workspace works as one
clear user journey, not whether the underlying machinery is impressive.

The first read should make clear:

- what run or case the user is looking at;
- why the page starts with the outcome;
- what the Learn surface teaches;
- where model detail belongs;
- where relation detail belongs;
- how the map helps navigation without becoming proof;
- why Receipts exist and why technical inspection is optional.

The progression should move from general meaning to controlled detail:

```text
Outcome -> Learn -> Models -> Relations -> Map -> Receipts
```

If the reviewer cannot explain what the first page is asking them to do, the
next product slice should fix first-screen orientation before adding more
surfaces.

## Allowed Next Work

Allowed next work:

- collect a real human hierarchy review response;
- save it as `reviews/human/observatory-workspace/review.json`;
- run `capture_observatory_workspace_human_review.py`;
- inspect the resulting `reviews/human/observatory-workspace/intake.json`;
- fix a blocker found while attempting the review.

Do not add another UX expansion PR before the review response, unless it fixes a
blocker found while attempting the review.

## What Unblocks The Gate

The gate is unblocked by a real completed review response, followed by the
offline capture command:

```bash
python3 scripts/evals/capture_observatory_workspace_human_review.py \
  --review reviews/human/observatory-workspace/review.json \
  --out reviews/human/observatory-workspace/intake.json \
  --source-ref reviews/human/observatory-workspace/review.json
```

An accepted intake can plan the next product revision slice. A blocked intake is
also useful because it identifies what must be repaired before review evidence
can shape the next slice.

## Not Evidence Of

This gate is not evidence of:

- product proof;
- human validation;
- answer correctness;
- advice correctness;
- runtime readiness;
- action authorization;
- graph-edge truth;
- relation-confidence certification.

## Boundary

This slice:

- does not add a completed review or intake artifact;
- does not run Lolla;
- does not invoke the Lolla skill;
- does not call providers or model APIs;
- does not create a new run;
- does not generate or attach sidecars;
- does not wire skill runtime behavior;
- does not mutate archives;
- does not edit `observatory/build`;
- does not touch `SKILL.md`;
- does not touch `scripts/skill/*`;
- does not touch `scripts/archive_run.py`;
- does not claim product proof;
- does not claim human validation;
- does not claim answer correctness;
- does not claim advice correctness;
- does not authorize automatic action;
- does not treat graph edges as proof;
- does not treat relation confidence as certification.

## Decision

The next gate is:

```text
awaiting_real_human_hierarchy_review_response
```

This slice does not add a completed review or intake artifact.
