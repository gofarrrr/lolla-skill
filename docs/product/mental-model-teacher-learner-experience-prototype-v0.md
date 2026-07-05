# Mental Model Teacher Learner Experience Prototype v0

Status: learner-first static prototype
Date: 2026-07-05

Open:
[Mental Model Teacher learner experience prototype](mental-model-teacher-learner-experience-prototype-v0/index.html)

Manifest:
[learner experience prototype manifest](mental-model-teacher-learner-experience-prototype-v0/manifest.json)

Design inputs:

- [Mental Model Teacher Learner Experience Design](mental-model-teacher-learner-experience-design-v0.md)
- [Mental Model Teacher PKM Reference Synthesis](mental-model-teacher-pkm-reference-synthesis-v0.md)

## Purpose

This slice turns the Mental Model Teacher design research into a visible offline
prototype focused on presentation.

The prototype uses the existing three-case Teacher lesson objects and graph
objects, but changes the first screen from review/dashboard mode to learner mode.
The default experience is:

```text
case anchor -> reasoning trap -> thinking move -> model relation -> practice rep
```

## What Is Functional

- `Learn` mode is the default.
- The user can switch between three Teacher pilot cases.
- The first screen explains the situation, trap, move, relation, and practice rep.
- `Models` mode presents reusable mental-model cards with lesson backlinks.
- Clicking a model opens a formatted model detail view sourced from canonical
  Markdown, activation curation, intervention semantics, and relation semantics.
- Canonical model names are primary; Teacher lesson labels appear only as
  contextual lesson labels.
- `Relations` mode presents relation cards as first-class teaching objects.
- `Map` mode presents a focused lesson neighborhood, not a full-corpus graph.
- `Review` mode is separate from the learner surface.
- Search returns typed learner objects: lesson, model, relation, and practice.
- Receipts and boundaries are present but collapsed by default in Learn mode.

## What This Changes From The Prior Visible Surface

The prior visible review surface was useful for inspection, but it mixed learner
content, graph data, raw source snapshots, review controls, package status, and
non-claim tags in one view.

This prototype separates those jobs:

- teaching belongs in `Learn`;
- reusable concepts and canonical model detail belong in `Models`;
- model-pair explanations belong in `Relations`;
- spatial exploration belongs in `Map`;
- source fidelity and missingness belong in `Review` or receipts.

## Boundary

This is a static offline prototype. It does not run Lolla, invoke the Lolla
skill, call providers or models, create new Lolla runs, wire runtime behavior,
complete human review, claim product proof, claim answer correctness, claim
advice correctness, treat graph edges as proof, treat embeddings as validated
relations, or authorize action.

## Next Gate

Recommended gate:

```text
evaluate_learner_first_presentation_before_expansion
```
