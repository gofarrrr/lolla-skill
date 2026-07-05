# Mental Model Teacher Three-Case Product Pilot v0

Status: PR-P9 deferred because required Teacher case artifacts are not present
on current `origin/main`
Date: 2026-07-05
Decision gate: `deferred_until_teacher_offline_package_merged`

## Purpose

PR-P9 is meant to render productized Teacher lesson pages and lesson graph
neighborhoods for three existing Teacher pilot cases:

- `launch-public-enterprise-beta`
- `deploy-assisted-intake-routing`
- `ceo-remove-founding-cofounder`

Current `origin/main` does not contain the required Teacher source package for
those cases. It does contain Decision Work and evaluation artifacts with the
same case IDs, but those are not Teacher lesson artifacts and are not safe
substitutes for this product lane.

This slice therefore stops at a deferred review packet instead of generating
three case pages or graph neighborhoods.

## Current Main Findings

The current branch is based on `origin/main` after PR-P8. The available Mental
Model Teacher Product Surface artifacts on current main are the PR-P1 through
PR-P8 planning, contract, pilot, fixture, renderer, lesson-graph, and static
visual graph prototype outputs.

The current main branch does not include tracked files under a Teacher
three-case source package such as:

```text
reviews/codex-assisted/mental-model-teacher-knowledge-mesh-v2/<case-id>/
```

The case IDs do appear in Decision Work files under `docs/conversation-
understanding/` and related review artifacts. Those artifacts answer a different
question: what decision artifact should be preserved. The Teacher product lane
asks what reasoning move a user can learn. Reusing Decision Work outputs here
would collapse the product boundary.

## Required Case Status

| Case | Current main Teacher artifacts | Product lesson page | Product graph neighborhood | Status |
| --- | --- | --- | --- | --- |
| `launch-public-enterprise-beta` | Missing | Not generated | Not generated | Deferred |
| `deploy-assisted-intake-routing` | Missing | Not generated | Not generated | Deferred |
| `ceo-remove-founding-cofounder` | Missing | Not generated | Not generated | Deferred |

## Source Located Outside Current Main

A separate local worktree appears to contain the expected Teacher source
package:

```text
Worktree: /private/tmp/lolla-teacher-package-worktree
Branch: feature/mental-model-teacher-offline-review-package-v2
Commit: 1ebfe24f6ceef8b0481f70f718e3607e31d1e1e8
Package root: reviews/codex-assisted/mental-model-teacher-knowledge-mesh-v2/
```

Observed case-level Teacher artifacts in that package include:

- `mental_model_teacher.md`
- `mental_model_teacher_card.md`
- `mental_model_teacher_lesson.json`
- `mental_model_teacher_learning_review.md`
- `mental_model_teacher_model_deep_dive.json`
- `mental_model_teacher_relation_deep_dive.json`
- `mental_model_teacher_practice_lab.json`
- `mental_model_teacher_okf_manifest.json`
- `mental_model_teacher_okf_conformance.json`

This PR does not merge, import, or normalize that package. The user explicitly
warned that separate local branches and worktrees may exist, and this goal must
not overwrite or mix unrelated branch work. PR-P9 remains blocked until the
Teacher package is intentionally merged or otherwise made available on the fresh
`origin/main` branch for this product lane.

## Boundary Decision

PR-P9 does not:

- create substitute Teacher lessons from Decision Work briefs;
- convert evaluation artifacts into user-facing Teacher product copy;
- generate graph neighborhoods from unmerged source artifacts;
- claim product proof;
- claim human validation;
- claim answer correctness or advice correctness;
- authorize runtime integration or automatic action.

This is a product-surface custody decision, not a statement that the external
Teacher package is invalid. The only claim is narrower: current main does not
yet provide the required Teacher three-case inputs for PR-P9.

## High-Risk Case Caveat

The CEO cofounder-removal case is a high-risk scenario. When the Teacher source
package is available, any productized lesson for that case should preserve
domain caveats, uncertainty, and visible non-claims. It must teach reasoning
moves without implying legal, HR, governance, or interpersonal advice
correctness.

## Recommended Next Gate

`deferred_until_teacher_offline_package_merged`

Before PR-P10, decide whether to merge or intentionally import the Teacher
offline package into the current product lane. Without that source, a UX review
packet comparing productized Teacher pages against current Teacher cards would
be empty or misleading.
