# Decision Pressure Trace Adapter Report Usefulness Review

**Date:** 2026-05-05
**Status:** Docs-only review artifact. No code changes, no runtime
integration, no UI implementation, no product promotion, no model calls, no
judge calls, no extraction, no prompt changes, and no affordance-record
changes.

**Branch:** `feature/decision-pressure-pr22-adapter-report-usefulness-review`

## Decision

`adapter_report_useful_as_smoke_guard`

## Question

Does the PR21 adapter report make trace review easier, or does it only prove
mechanical validation?

## Answer

The adapter report is useful as a mechanical drift guard, not as the main
product-quality review surface.

Short version:

> The adapter report is a smoke alarm, not the product review surface.

It should help reviewers notice if a reviewed trace fixture stops matching the
PR19 contract or starts drifting toward product behavior. It should not replace
the trace fixture, PR18 prototype, PR19 contract, or PR21 smoke-test research
doc as the place where product quality is judged.

## Findings

1. No blocking product or architecture issues were found.

2. PR21 stays inside the PR20 boundary. It validates, counts, lists IDs, and
   optionally writes a review-only JSON report. It does not select pressures,
   generate pressure text, render Observatory UI, import live Observatory, or
   touch `/lolla` behavior.

3. The report catches structural drift:
   - selected pressure count drift;
   - missing competitive-dynamics coverage panel ID;
   - suppressed-candidate count drift;
   - unresolved source-affordance IDs;
   - non-dormant runtime policy;
   - accidental movement toward HTML or user-facing output.

4. The report preserves the important trust rails:
   - `3` selected pressure IDs;
   - `1` coverage blank ID;
   - `6` suppressed candidate IDs;
   - `13` unique source-affordance IDs;
   - `runtime_dormant`;
   - `validation_status: passed`;
   - blocked surfaces.

5. The report intentionally excludes product-shaped fields:
   - `pressure`;
   - `what_to_verify`;
   - `dismiss_if`;
   - `tripwire_or_next_action`;
   - `operator_note`;
   - user-facing copy;
   - HTML.

6. The report is too thin to judge whether the pressures are good. That is
   correct. It proves the reviewed fixture still has the expected mechanical
   shape; it does not judge pressure wording, action quality, dismissal quality,
   tone, or product usefulness.

7. The main product review artifact remains the trace fixture plus the PR18,
   PR19, and PR21 research docs. The adapter report is supporting review
   infrastructure.

8. Do not tighten blocked-surface enumeration yet unless future fixtures drift.
   Over-tightening would turn the adapter into policy logic instead of a smoke
   check. The PR19 validator and reviewed fixture should remain the owners of
   trace policy.

## Recommendation

Accept PR21.

Do not build a package function yet.

Do not add or remove adapter report fields right now. The current report shape
is boring in the useful way: counts, IDs, source-affordance references, blocked
surfaces, validation status, and adapter policy.

Do not add pressure summaries, route prose, readiness explanations, operator
notes, or user-facing text to the report. Those additions would make the report
too product-shaped.

Do not build live Observatory.

Treat the adapter report as a smoke alarm: it warns that a reviewed trace has
drifted structurally. It does not decide whether the trace is product-good.

## What Remains Blocked

The following remain blocked:

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

## PR23 Options

1. `stop_and_review`

   Preferred default. Pause after PR22 and decide as a human/product question
   whether the dormant infrastructure is enough for now, whether Decision
   Pressure needs another real case/readout, or whether eventual Observatory
   work is justified.

2. `package_function_later`

   Consider only if reviewers explicitly ask for a dormant package boundary
   after reviewing PR21 and PR22. This should still avoid live Observatory,
   memo, Step 8, Step 6, Lane 4, and `/lolla` imports.

3. `compress_trace_or_report_fields_first`

   Choose this if the trace fixture or adapter report feels too heavy, too
   noisy, or too close to a product surface.

Recommendation:

> `stop_and_review` unless reviewers explicitly ask for `package_function_later`.

## Doctrine

> Surface pulls extraction. Extraction does not push the product.

> Observatory before user surface.

> Coverage transparency is a feature, not an apology.

> A fixture-only adapter smoke test is not live Observatory.

> A smoke report is not product-quality review.
