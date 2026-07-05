# Mental Model Teacher Visible Review Surface v0

Status: visible offline pilot review surface
Date: 2026-07-05

Open:
[Mental Model Teacher visible review surface](mental-model-teacher-visible-review-surface-v0/index.html)

Manifest:
[visible review surface manifest](mental-model-teacher-visible-review-surface-v0/manifest.json)

## Purpose

This slice adds an actual browser-visible review surface for the three-case
Mental Model Teacher pilot. It is built from the existing PR-P9 product lesson
objects and graph JSON, plus the imported Teacher card/note source artifacts.

The surface lets a reviewer inspect:

- the productized lesson;
- the model stack;
- the relation story;
- the graph neighborhood;
- raw Teacher card/note snapshots;
- blank human-review controls;
- visible non-claims.

## Boundary

This is a static offline UI. It does not call providers or models, run Lolla,
invoke the Lolla skill, wire runtime behavior, complete human review, claim
product proof, claim answer correctness, claim advice correctness, treat graph
edges as proof, or authorize action.

The selected gate remains:
`needs_human_review_before_expansion`
