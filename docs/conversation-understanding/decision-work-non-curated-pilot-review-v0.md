# Decision Work Non-Curated Pilot Review v0

Status: PR230 review
Date: 2026-07-04

[Review JSON](../../reviews/codex-assisted/decision-work-non-curated-pilot-review-v0/review.json)

## Purpose

PR230 reviews the first
[Decision Work Non-Curated Completed-Run Pilot](decision-work-non-curated-completed-run-pilot-v0.md)
before moving deeper into automation readiness.

The reviewed PR229 pilot used a synthetic/sanitized completed-run-like fixture
outside `launch-public-enterprise-beta` and
`deploy-assisted-intake-routing`. It intentionally had no generated read and no
generated triage, so the offline operator runner stopped at the generated-read
boundary with:

```text
deferred_missing_semantic_read
```

This review asks whether that deferred result is enough as the first
non-curated automation-readiness signal, or whether the next step should be a
second non-curated pilot with existing checked-in-safe semantic inputs.

## Reviewed Result

PR229 recorded:

- `final_status: deferred_missing_semantic_read`;
- `stopped_at: generated_read`;
- `missing_required_inputs: ["generated_read"]`;
- `deferred_reasons: ["generated_read_missing"]`;
- no completed deterministic chain steps;
- downstream steps skipped for intake, brief supply, rendered brief, triage
  supply, resolver supply, sidecar update packet, and dry-run.

The runner did not create or repair a generated read. It did not fabricate a
generated triage read. It did not invent a brief, triage supply packet,
resolver-supply candidate, sidecar update packet, dry-run, write receipt, or
sidecar output.

All write/archive/runtime/resolver/action/proof/scoring flags stayed false.

## Is The Deferred Result Acceptable?

Yes, as a first non-curated pilot signal.

A deferred result is not failure when it is honest, legible, and safe. PR229
shows that the runner can be pointed at a non-curated completed-run-like case
and stop before semantic interpretation when the required generated read is
absent.

That is useful because it proves the runner does not silently substitute
curated defaults, auto-discover private context, generate semantic meaning, or
continue into downstream artifacts without the required semantic input.

It is not sufficient for automation-readiness packaging. It does not exercise
the deeper chain on a non-curated case where generated read and generated triage
inputs already exist.

## Missingness Visibility

The runner made missingness visible enough for operator review:

- the missing input is explicit in `missing_required_inputs`;
- the deferred reason is explicit in `deferred_reasons`;
- the stop point is explicit in `stopped_at`;
- skipped downstream steps show what did not run;
- no blocker reason is invented beyond the deterministic missing-input result.

This is the right missingness/blocker/deferred-state lens. PR230 does not add a
new Unknowns Register schema, does not add a known-known / known-unknown
taxonomy, and does not infer semantic meaning from absence.

Put directly: it does not add a new Unknowns Register schema.
It also does not add a known-known / known-unknown taxonomy.

## Source Depth And Semantic Input Gaps

The review does not treat missing source-depth status as hidden knowledge.
Source-depth status is absent because the runner stopped before intake and
brief supply. Runtime and user-surface status are absent because the runner
never reached resolver supply, sidecar update packet, or dry-run.

That absence is preserved as absence. The pilot did not prove any non-curated
case is ready for sidecar write, runtime attachment, user surface, or operator
action.

Put more directly: this result does not show that a non-curated case is ready
for sidecar write.

For future searches: it does not show that a non-curated case is ready for sidecar write.

## Product Readiness Boundary

The result avoids product-readiness language. It does not imply:

- the advice was correct;
- the generated read was adequate;
- the sidecar should be written;
- runtime attachment is safe;
- resolver refs are approved;
- the case is user-surface ready;
- the product is validated;
- human review happened;
- answer quality was scored;
- any action is authorized.

The strongest useful signal is narrow: a non-curated missing-semantic-input
case deferred cleanly.

The strongest unresolved risk is also clear: this pilot does not show whether a
non-curated case with existing semantic inputs can travel deeper through the
runner without drifting.

## Decision

PR229 should count as a valid first non-curated pilot, but not as enough to move
straight to automation-readiness package gate.

The next meaningful test is a second non-curated completed-run pilot where the
generated read and generated triage already exist as checked-in-safe inputs.
That pilot should exercise deeper runner behavior without creating new semantic
interpretation, repairing missing reads, approving resolver refs, writing
sidecars, mutating archives, or wiring runtime.

Selected gate:

```text
proceed_to_second_non_curated_completed_run_pilot
```

Recommended next PR:

```text
PR231 Second Non-Curated Completed-Run Pilot v0
```

## Stop Lines

PR231 should stop if it would require:

- `$lolla` or Lolla skill invocation;
- provider/model API calls;
- new Lolla runs;
- generating or repairing interpretation reads;
- inventing missing semantic meaning;
- queue workers or daemons;
- runtime wiring;
- resolver approval;
- checked-in runner summaries or sidecar outputs;
- real historical archive mutation;
- product proof, human validation, advice-correctness claims,
  answer-quality scoring, approval/certification labels, or action
  authorization.
