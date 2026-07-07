# Observatory Workspace Hierarchy Cues

Status: implemented as a narrow Observatory presentation slice.

Date: 2026-07-07

Decision gate: `ready_for_human_review_with_hierarchy_cues`

## Purpose

The diagnostic audit found that Observatory now has the right product direction,
but first-class product information, supporting exploration, and inspection data
still sit too close together.

This slice implements the first hierarchy repair:

- Outcome missingness is now a purposeful state, not an empty-feeling first
  product moment.
- Model cards now show selected-run role cues.
- Model detail pages now separate Library view from Run context.

## Browser Finding Addressed

The previous browser audit found that Outcome can lead with absence when the
served result has no revised-answer artifact. That behavior is technically
correct, but it can make the first screen feel broken.

The same audit found that model pages are readable, but the UI does not clearly
separate:

- mental model as reusable library knowledge;
- model as part of this selected-run lesson;
- model role as navigation, not proof.

## Change

Outcome now says when the revised-answer artifact is unavailable and tells the
user to continue to Learn to review the teaching surface. Receipts remains the
place to inspect what is present, missing, and not claimed.

Model cards now display small selected-run role cues:

- Primary model;
- Contrast model;
- Partner model;
- Tension model;
- Supporting model;
- Model in this run.

Role labels are inferred from the selected-run lesson order and relation
endpoints. They are a navigation cue, not proof, scoring, validation, or
certification.

Model detail pages now start with:

Library view first, run context second.

That tells the user that the page first explains the mental model as reusable
knowledge, then shows how the selected run is using it.

## What This Improves

This slice makes the information ladder more explicit:

- Outcome says whether the run-result artifact is present or missing.
- Learn remains the primary teaching surface.
- Models become supporting knowledge with visible role cues.
- Model detail pages distinguish general model knowledge from selected-run
  context.
- Receipts remains the place for missingness, custody, and non-claims.

## What It Does Not Do

This slice does not add model-role fields to the product contract. It only
renders conservative role cues from existing product-safe workspace data.

It does not claim that the role labels are canonical, human-reviewed, or proof
of answer quality.

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

## Next Gate

Recommended next gate:

`ready_for_human_review_with_hierarchy_cues`

The next useful review question is whether a cold user can now explain the
difference between Outcome, Learn, Models, model detail, Map, Receipts, and
technical audit without being overwhelmed.
