# Mental Model Teacher Three-Case Source Package v0

Status: PR-P9 source-custody unblocker
Date: 2026-07-05
Decision gate: `proceed_to_three_case_teacher_product_pilot_retry`

## Purpose

PR-P9 found that current `origin/main` did not contain the Teacher artifacts
needed to render the three-case Teacher product pilot. This unblocker imports a
narrow source package for those three cases without merging the broader external
branch.

Imported source root:

```text
reviews/codex-assisted/mental-model-teacher-knowledge-mesh-v2/
```

Imported cases:

- `launch-public-enterprise-beta`
- `deploy-assisted-intake-routing`
- `ceo-remove-founding-cofounder`

## Provenance

The source artifacts were copied from the local Teacher offline package
worktree identified by PR-P9:

```text
Worktree: /private/tmp/lolla-teacher-package-worktree
Branch: feature/mental-model-teacher-offline-review-package-v2
Commit: 1ebfe24f6ceef8b0481f70f718e3607e31d1e1e8
Source package root: reviews/codex-assisted/mental-model-teacher-knowledge-mesh-v2/
```

This PR does not merge that branch, rebase it, or import its engine modules,
scripts, coach artifacts, broad docs, or package-level human/synthetic review
files.

## Import Scope

This source-custody import includes only the three case directories. Each case
directory carries Teacher source artifacts such as:

- `mental_model_teacher_lesson.json`
- `mental_model_teacher_card.md`
- `mental_model_teacher.md`
- `mental_model_teacher_model_deep_dive.json`
- `mental_model_teacher_model_deep_dive.md`
- `mental_model_teacher_relation_deep_dive.json`
- `mental_model_teacher_relation_deep_dive.md`
- `mental_model_teacher_practice_lab.json`
- `mental_model_teacher_practice_lab.md`
- `mental_model_teacher_okf_manifest.json`
- `mental_model_teacher_okf_conformance.json`

Package-level review artifacts such as `pilot_review.json`,
`human_review_gate.json`, `human_review_response.json`, and
`synthetic_human_review_panel.md` are intentionally not imported in this slice.
PR-P10 must create its own review packet from the productized pages produced by
the visual-library lane, and must not treat an older package-level review as
human validation.

## Product Boundary

These imported files are source artifacts for deterministic product builders and
reviewers. They are not the product UI.

The source package:

- does not render product pages;
- does not render graph neighborhoods;
- does not claim product proof;
- does not claim human validation;
- does not claim answer correctness or advice correctness;
- does not authorize runtime integration or automatic action;
- does not make graph edges proof;
- does not make embedding similarity validated relation semantics.

## Recommended Next Gate

`proceed_to_three_case_teacher_product_pilot_retry`

The next PR should retry PR-P9 against current main, using these source
artifacts to build productized Teacher lesson pages and small graph
neighborhoods for the three cases.
