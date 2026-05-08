# Decision Pressure Trace Adapter Smoke Test

**Date:** 2026-05-05
**Status:** Fixture-only adapter smoke test. No runtime integration, no UI
implementation, no live Observatory behavior, no prompt changes, no model
calls, no judge calls, no new extraction, no affordance-record rewrites, and no
user-facing promotion.

**Branch:** `feature/decision-pressure-pr21-trace-adapter-smoke-test`

**Decision label:** `fixture_adapter_smoke_ready`

**Doctrine:**

> Surface pulls extraction. Extraction does not push the product.

> Observatory before user surface.

> Coverage transparency is a feature, not an apology.

> A validated trace object is not runtime promotion.

> A producer/adapter plan is not a producer.

> A fixture-only adapter smoke test is not live Observatory.

## Product Question

Can deterministic code exercise the dormant PR19 `decision_pressure_trace.v1`
contract without creating live Observatory behavior or hidden product
promotion?

Short answer:

> Yes. PR21 can load the reviewed PR19 fixture, validate it against
> `affordances_v4.json`, and produce a review-only report with counts,
> identifiers, blocked-surface reminders, and coverage-blank custody. It does
> not select pressures, generate text, render UI, or touch runtime behavior.

## What PR21 Proves

PR21 proves a narrow mechanical path:

1. A reviewed trace fixture can be loaded from an explicit path.
2. The existing PR19 validator can validate the fixture and v4 source-affordance
   references.
3. A deterministic adapter can produce a review-only report object with:
   - `schema_version`
   - `trace_id`
   - `status`
   - `runtime_policy`
   - selected pressure, coverage panel, and suppressed candidate counts
   - selected pressure, coverage panel, and suppressed candidate IDs
   - source-affordance counts and unique IDs
   - blocked surfaces from `review_notes`
   - `validation_status: passed`
   - `adapter_policy: fixture_only_review_report`
4. The CLI writes a report only when `--report-out` is provided.
5. The report does not include pressure prose, generated user-facing copy, or
   rendered HTML fields.
6. The PhD competitive-dynamics coverage blank remains visible through the
   coverage panel ID.

## What PR21 Does Not Prove

PR21 does not prove:

- traces can be generated automatically;
- the runtime can choose Decision Pressures;
- Observatory can render the trace;
- users should see the trace;
- memo, Step 8, Step 6, Lane 4, or `/lolla` should consume it;
- Batch 3b should begin;
- paid Gate 4 should rerun;
- the selected pressure clusters should change.

The adapter exercises a reviewed fixture. It does not create a producer.

## Why This Is Still Dormant

The adapter requires explicit paths:

- `--fixture`
- `--affordances`

The adapter calls `validate_decision_pressure_trace_payload`, so PR19 rails
still own:

- `runtime_policy: runtime_dormant`
- `status: draft_review_only`
- maximum of three selected pressures
- source-affordance lookup against compiled v4
- coverage transparency missing model IDs
- suppression references
- principal-agent medium-confidence caution

The CLI is a smoke script:

- `scripts/smoke_decision_pressure_trace_adapter.py`

It is not imported by live Observatory or `/lolla`. It writes only when
`--report-out` is explicitly provided, and `--report-out` must point to a JSON
path rather than HTML or user-facing output. The expected report location for
manual smoke use is `.tmp/`, and `.tmp/` reports are not committed.

## Why The Adapter Is Deterministic, Not Semantic

The adapter only reads validated fields and counts or lists IDs.

It may:

- validate;
- count;
- list IDs;
- report blocked surfaces;
- write a review-only JSON report.

It must not:

- choose semantic pressure quality;
- select the best pressures;
- invent dismissal paths;
- generate tripwires;
- promote suppressed candidates;
- smooth over coverage gaps;
- render HTML;
- produce user-facing copy.

That keeps Python in the deterministic middle and leaves semantic judgment at
the reviewed artifact boundary.

## No Observatory Integration

PR21 does not create:

- Observatory route imports;
- Observatory HTML rendering;
- public cards;
- memo output;
- Step 8 output;
- Step 6 output;
- Lane 4 output;
- `/lolla` runtime behavior.

The report is review-only metadata. It is useful because it lets a reviewer
confirm that the fixture still carries the expected shape:

- `3` selected pressures;
- `1` coverage transparency panel;
- `6` suppressed candidates;
- `13` source-affordance references;
- `runtime_dormant` policy;
- the `phd-competitive-dynamics-coverage-gap` panel.

## What Remains Blocked

The following remain blocked after PR21:

- live Observatory rendering;
- memo integration;
- Step 8 integration;
- Step 6 integration;
- Lane 4 integration;
- `/lolla` runtime use;
- user-facing Decision Pressure blocks;
- prompt changes;
- generation changes;
- new extraction;
- Batch 3b;
- paid Gate 4 reruns by default.

## PR22 Options

Recommended next step:

> Stop and review whether the adapter report actually makes trace review
> easier before building a package function or Observatory-adjacent code.

If reviewers accept the report as useful, a later PR22 could define a
runtime-dormant package function that wraps the same reviewed report object for
future Observatory use, while proving it is not imported by live Observatory or
`/lolla`.

If reviewers find the report noisy or too close to a product object, stop and
compress the report fields before adding more code.

Do not make live UI the next PR.

## Verification

Focused tests:

- `PYTHONPATH=. pytest tests/test_decision_pressure_trace_adapter.py`
- `PYTHONPATH=. pytest tests/test_decision_pressure_trace_adapter.py tests/test_decision_pressure_trace_schema.py`

Manual smoke command:

```bash
PYTHONPATH=. python3 scripts/smoke_decision_pressure_trace_adapter.py \
  --fixture tests/fixtures/decision_pressure_trace/gate4_3case_pr18_valid.json \
  --affordances data/compiled/model_affordances/affordances_v4.json \
  --report-out .tmp/decision_pressure_trace_adapter_smoke_report.json
```

The `.tmp/` report is not a committed artifact.
