# Decision Pressure Trace Producer / Adapter Plan

**Date:** 2026-05-05
**Status:** Planning / fixture-only. No runtime integration, no UI
implementation, no live producer, no prompt changes, no model calls, no judge
calls, no new extraction, no affordance-record rewrites, and no user-facing
promotion.

**Branch:** `feature/decision-pressure-pr20-trace-producer-adapter-plan`

**Decision label:** `producer_adapter_plan_ready`

**Doctrine:**

> Surface pulls extraction. Extraction does not push the product.

> Observatory before user surface.

> Coverage transparency is a feature, not an apology.

> A validated trace object is not runtime promotion.

> A producer/adapter plan is not a producer.

## Product Question

Can a future producer or adapter preserve the PR19
`decision_pressure_trace.v1` contract without turning the dormant trace into
product behavior?

Short answer:

> Yes, but only if the next boundary is fixture-only and deterministic. The
> adapter may validate, normalize, package, and report on reviewed trace
> artifacts. It must not select pressures, invent pressure fields, smooth over
> coverage gaps, or render anything live.

PR19 says:

> Here is the shape of a valid trace.

PR20 says:

> Here is the boundary for moving from a reviewed fixture toward a deterministic
> adapter path without creating runtime behavior.

## Boundary Definitions

### Reviewer-Authored Trace

A reviewer-authored trace is a human/product-reviewed object like:

- `tests/fixtures/decision_pressure_trace/gate4_3case_pr18_valid.json`

It may be created from reviewed research artifacts, static prototypes, and
product judgment. It is the only current source of semantic pressure
selection.

Allowed work:

- write or revise reviewed trace content;
- preserve the same selected pressure clusters;
- state provenance and coverage gaps;
- explain suppression decisions;
- carry review notes and blocked surfaces.

Not allowed:

- treat the fixture as generated runtime output;
- treat the fixture as user-facing copy;
- use it to justify a fourth pressure or live product surface.

### Deterministic Adapter

A deterministic adapter is code that can validate, normalize, package, or
report on already-reviewed trace artifacts without semantic selection.

Python may:

- load a reviewed trace fixture;
- validate it with `engine/system_b/decision_pressure_trace_validation.py`;
- verify `source_affordances` against `affordances_v4.json`;
- enforce the three-pressure cap;
- enforce `draft_review_only` and `runtime_dormant`;
- check that coverage transparency panels name missing models;
- check that `merged_support` suppressed candidates reference selected
  pressures;
- produce a no-index validation report for review;
- package a reviewed trace object for a later dormant consumer.

Python must not:

- decide semantic pressure quality;
- select the "best" pressures;
- invent pressure text, dismissal paths, tripwires, or operator notes;
- choose whether a suppressed candidate should be promoted;
- infer missing coverage into a pressure;
- smooth over `no_substrate_backed_pressure` blanks;
- produce user-facing copy;
- render live Observatory UI.

### Future Producer

A future producer is not built in PR20. It is a possible later component that
might assemble candidate traces from reviewed artifacts.

Before any future producer exists, a separate review must decide:

- whether semantic selection belongs to a human reviewer, an LLM boundary, or a
  deterministic post-processor;
- whether generated candidates can be compared to the PR19 contract without
  prompt or runtime drift;
- how a reviewer approves or rejects candidate pressures;
- how failed coverage, unknown affordance IDs, and suppressed candidates are
  preserved.

A future producer must not choose final pressure quality semantically without
explicit reviewer or LLM-boundary approval.

## Input / Output Map

### Adapter Inputs

A fixture-only adapter may read:

- `tests/fixtures/decision_pressure_trace/gate4_3case_pr18_valid.json`
- `data/compiled/model_affordances/affordances_v4.json`
- `data/schemas/decision_pressure_trace.schema.json`
- `engine/system_b/decision_pressure_trace_validation.py`
- reviewed source artifact references listed inside the trace fixture
- `research/gate4-3case-decision-pressure-observatory-prototype-2026-05-05.md`
- `research/gate4-3case-decision-pressure-v4-dry-review-2026-05-05.md`
- `research/decision-pressure-trace-data-shape-2026-05-05.md`

### Adapter Outputs

A fixture-only adapter may output:

- a validated `decision_pressure_trace.v1` object;
- an optional validation report for review;
- deterministic metadata such as validation timestamp, checked fixture path, or
  checked compiled affordance artifact path.

A fixture-only adapter must not output:

- user-facing copy;
- live Observatory HTML;
- memo content;
- Step 8, Step 6, Lane 4, or `/lolla` payloads;
- generated pressure selection;
- modified affordance records.

If a validation report is produced in a later PR, it should be no-index and
review-only. A `.tmp/` report is acceptable for smoke testing. A committed
report should be considered only if it becomes a stable review artifact.

## Invariants

These invariants must never be broken:

- `runtime_policy` remains `runtime_dormant`.
- `status` remains `draft_review_only`.
- `selected_pressures` has a maximum of `3`.
- coverage transparency panels with `no_substrate_backed_pressure` name missing
  models.
- unknown `source_affordance` IDs fail against `affordances_v4.json`.
- `merged_support` candidates reference existing selected pressures.
- `principal-agent-problem` support keeps the medium-confidence caution visible
  in an operator note or explicit review note.
- suppressed candidates remain audit information, not extra user-facing
  pressures.
- coverage blanks are preserved.
- the three selected PR13/PR14 pressure clusters remain unchanged unless a
  separate reviewer pass explicitly changes selection.
- deterministic code does not perform semantic pressure selection.

## Non-Goals

PR20 explicitly rejects:

- live Observatory UI;
- memo integration;
- Step 8 integration;
- Step 6 integration;
- Lane 4 integration;
- `/lolla` runtime behavior;
- user-facing Decision Pressure blocks;
- Batch 3b;
- paid Gate 4 reruns by default;
- prompt changes;
- LLM generation changes;
- affordance extraction;
- semantic pressure selection in deterministic code.

## Possible PR21 Options

Ranked options:

### A. Fixture-Only Adapter Smoke Test

Build a tiny deterministic script or test that loads the PR19 fixture,
validates it against v4, and writes a no-index validation report under `.tmp/`
or test output.

This is the preferred PR21 if reviewers accept the PR20 boundary.

Why:

- proves the contract can be exercised mechanically;
- keeps the output review-only;
- does not touch runtime imports;
- gives future work a concrete adapter boundary without UI or product behavior.

Hard limits:

- no live Observatory import;
- no generated trace content;
- no semantic pressure choice;
- no committed `.tmp/` report unless explicitly reviewed as a fixture.

### B. Runtime-Dormant Package Function

Create a small library function that packages a reviewed trace fixture for a
future Observatory consumer, while keeping it unimported by live Observatory.

This is second-best because it creates code that is closer to runtime. It
should happen only if option A proves too trivial or reviewers want a stable
library boundary before any producer work.

Hard limits:

- function remains dormant;
- tests prove it is not imported by live `/lolla` or Observatory routes;
- no rendering;
- no user-facing output.

### C. Stop And Review

Stop if reviewers think the PR19 trace contract is too heavy or too close to a
future UI object.

In that case, do not build an adapter. Return to PR18/PR19 and compress the
trace fields first.

## Recommendation

Proceed only to option A after PR20 review:

> PR21 should be a fixture-only adapter smoke test, not live Observatory
> rendering.

Do not recommend live UI as PR21. Do not start Batch 3b. Do not run paid Gate
4. Do not treat the adapter boundary as permission to generate or display
Decision Pressure.

## Verification Plan

PR20 is docs/fixture-boundary planning only.

Required before merge:

- `git diff --check`
- confirm only intended PR20 docs/fixture-note files are staged

No tests are required unless PR20 adds executable code. A fixture README does
not require tests.
