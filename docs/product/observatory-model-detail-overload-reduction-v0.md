# Observatory Model Detail Overload Reduction

Status: implemented UX reduction slice.

Date: 2026-07-07

Decision gate: `ready_for_human_hierarchy_review_after_model_detail_reduction`

## Purpose

The browser audit found that Observatory now has the right objects, but a cold
user may still treat supporting model detail as equal to the main Learn journey.

This slice reduces that risk on model detail pages. The page now keeps the
first-read model explanation visible and moves long source-backed bullets into
a closed supporting-detail disclosure.

## Product Rule

The model detail page should answer one question first:

```text
What does this model help me notice in the selected lesson?
```

Everything after that is supporting material unless the user chooses to inspect
it.

## UX Change

The visible first read remains:

- `What This Model Helps You See`
- `Use when`
- `When it misleads`
- `Practice this`

The page now adds this hierarchy cue:

```text
Detailed bullets are supporting material, not the main lesson.
```

The longer source-backed lists now sit behind a closed disclosure:

```text
Use, avoid, and source-backed details
```

That disclosure contains:

- `Helps notice`
- `Use when`
- `Avoid when`

The existing `Practice and failure detail` and `Source, status, and boundaries`
sections remain disclosures.

## What This Improves

This reduces first-screen overload on model detail pages while preserving access
to all product-safe model information. A user can stop after the first read and
return to Learn, Relations, or Map without feeling that every bullet is equally
important.

## What It Does Not Solve

This does not prove that a human learner understands the hierarchy. It only
makes the hierarchy easier to evaluate in the next human review.

Remaining risks:

- model detail pages may still feel long after expansion;
- a user may still enter technical audit routes before understanding Learn;
- the selected-run reason for choosing each model remains partly implicit;
- human review is still pending.

## Boundary

This slice:

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

## Validation Target

The next human hierarchy review should specifically check whether the model
detail page now feels like supporting knowledge rather than a second main
product page.

Recommended next gate:

`ready_for_human_hierarchy_review_after_model_detail_reduction`
