# Decision Pressure Trace Data Shape

**Date:** 2026-05-05
**Status:** Runtime-dormant data contract. No runtime integration, no UI
implementation, no user-facing promotion, no model calls, no judge calls, no
new extraction, no prompt changes, and no affordance-record rewrites.

**Branch:** `feature/decision-pressure-pr19-decision-pressure-trace-contract`

**Decision label:** `decision_pressure_trace_contract_ready`

**Doctrine:**

> Surface pulls extraction. Extraction does not push the product.

> Observatory before user surface.

> Coverage transparency is a feature, not an apology.

> A validated trace object is not runtime promotion.

## What The Trace Object Is

`decision_pressure_trace` is a compact, validated object for representing the
PR18 manual Observatory prototype as structured data.

It preserves:

- the same three selected Decision Pressure clusters from PR13 and PR14;
- PR17 v4 sharpening without changing selection;
- field-level provenance for user-visible pressure fields;
- source route and source affordance custody;
- suppressed nearby candidates and why they stayed suppressed;
- coverage transparency panels, including zero-output behavior;
- explicit runtime dormancy and blocked surfaces.

The contract lives in:

- `data/schemas/decision_pressure_trace.schema.json`
- `engine/system_b/decision_pressure_trace_validation.py`
- `tests/fixtures/decision_pressure_trace/gate4_3case_pr18_valid.json`
- `tests/test_decision_pressure_trace_schema.py`

## What It Is Not

This is not:

- live Observatory integration;
- a UI card implementation;
- memo, Step 8, Step 6, Lane 4, or `/lolla` behavior;
- a generator contract for Arm C output;
- proof that future runs will produce the same trace;
- permission to add a fourth pressure;
- permission for Batch 3b;
- a replacement for reviewer judgment.

The fixture is hand-authored from PR18. It proves that the static trace can be
represented and validated. It does not claim that a runtime generator can
produce the trace.

## Why This Is Runtime-Dormant

The top-level object requires:

- `status: draft_review_only`
- `runtime_policy: runtime_dormant`

The validator rejects any other `runtime_policy`. The fixture also records the
blocked surfaces explicitly:

- live Observatory rendering;
- memo integration;
- Step 8 integration;
- Step 6 integration;
- `/lolla` runtime use;
- user-facing Decision Pressure blocks;
- Batch 3b;
- paid Gate 4 reruns by default.

This keeps the object inspectable without letting a schema quietly become a
product path.

## Contract Shape

Top-level fields:

- `schema_version`
- `trace_id`
- `status`
- `runtime_policy`
- `source_artifacts`
- `selected_pressures`
- `coverage_transparency_panels`
- `suppressed_candidates`
- `review_notes`

Each selected pressure carries:

- `pressure_id`
- `case_id`
- `route_ids`
- `pressure`
- `what_to_verify`
- `why_it_matters`
- `dismiss_if`
- `tripwire_or_next_action`
- `coverage_status`
- `provenance_by_field`
- `source_affordances`
- `v4_contribution`
- `suppressed_nearby_candidate_ids`
- `operator_note`
- `user_facing_readiness`

The contract intentionally does not include presentation layout, ranking
weights, user copy variants, prompt text, or future UI fields.

## Preserved PR18 Surface

The golden fixture represents exactly the same three selected pressure
clusters:

1. Equity / risk-response: governance deadlock before vesting.
2. Mother / uncertainty-type: safety plan relying on a gameable signal.
3. PhD / resource-allocation: shaping phase without a stop condition.

It also preserves the PR18 coverage transparency blank:

- PhD / competitive-dynamics remains `no_substrate_backed_pressure`.
- Missing models remain:
  - `game-theory-payoffs`
  - `nash-equilibrium`
  - `prisoners-dilemma`
  - `batna`
  - `red-queen-effect`

The validator requires missing model IDs when a coverage panel says
`no_substrate_backed_pressure`. That makes the blank explicit instead of
allowing the trace to sound complete.

## Validation Rails

Focused tests cover:

1. The schema file exists and names the required enums.
2. The PR18 golden fixture validates against compiled v4 affordances.
3. Any `runtime_policy` other than `runtime_dormant` is rejected.
4. More than three selected pressures are rejected.
5. Missing provenance for required user-visible fields is rejected.
6. Unknown `source_affordances` are rejected against `affordances_v4.json`.
7. A `no_substrate_backed_pressure` panel must include missing model IDs.
8. `merged_support` suppressed candidates must reference an existing selected
   pressure.
9. `principal-agent-problem` support must preserve a medium-confidence caution
   in `operator_note` or the explicit principal-agent review note.

The principal-agent rail is deliberately narrow. It does not allow an open
question to satisfy the caution requirement. The caution must live where an
operator would actually see or audit it.

## What Remains Blocked

PR19 does not unblock:

- live Observatory rendering;
- memo integration;
- Step 8 integration;
- Step 6 integration;
- `/lolla` runtime use;
- user-facing Decision Pressure blocks;
- prompt changes;
- generation changes;
- new extraction;
- Batch 3b;
- paid Gate 4 reruns by default.

The trace contract is a bridge from prose to interface. It is not a bridge from
interface to live product.

## PR20 Recommendation

If reviewers accept PR19, PR20 should stay dormant and answer the next concrete
interface question:

> Can a future trace producer or Observatory adapter preserve this contract
> without adding live behavior, UI drift, or hidden promotion?

The safest next slice is a small implementation plan or fixture-only adapter
spec for producing or rendering `decision_pressure_trace` objects from reviewed
artifacts. It should not connect to live `/lolla`, memo, Step 8, Step 6, Lane
4, or public Observatory behavior.

Stop condition:

If the contract feels too heavy in review, do not build a producer or renderer.
Return to PR18 and compress the trace fields before any implementation slice.
