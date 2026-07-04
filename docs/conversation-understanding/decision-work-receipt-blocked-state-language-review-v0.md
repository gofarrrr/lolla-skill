# Decision Work Receipt / Blocked-State Language Review v0

Status: PR234 review
Date: 2026-07-04

[Review JSON](../../reviews/codex-assisted/decision-work-receipt-blocked-state-language-review-v0/review.json)

## Purpose

PR234 reviews the language introduced and packaged by
[Decision Work Sidecar Automation Readiness Package Gate](decision-work-sidecar-automation-readiness-package-gate-v0.md).
It focuses on runner statuses, receipt/summary wording, blocked-state wording,
and package/narrative phrasing before the project moves into a separate Product
Delta evaluation-readiness phase.

This is a review and language-boundary PR only. It does not change runner
behavior, runtime behavior, sidecar write behavior, resolver refs, prompts,
queue behavior, or archive mutation behavior.

## Terms Reviewed

PR234 reviewed these terms:

- `sidecar_ready_for_explicit_write`;
- `sidecar_ready_blocked_state`;
- `deferred_missing_semantic_read`;
- `deferred_missing_triage`;
- `blocked_runtime_or_user_surface_risk`;
- dry-run readiness;
- automation readiness;
- explicit write;
- sidecar-ready;
- blocked-state sidecar;
- `runner_summary.json`;
- `operator_attention_items`.

## Main Finding

The current language is acceptable with explicit limitations preserved.

No runner behavior change is needed. The words are safe enough for internal
operator use because the PR233 package gate, PR224 PRD, PR232 review, and
overview docs repeatedly bind the terms to these constraints:

- the runner never writes sidecars by itself;
- dry-run readiness is not an actual sidecar write;
- sidecar-ready means ready for a later explicit operator decision, not
  resolver approval;
- automation readiness is an offline/operator milestone, not runtime
  automation;
- semantic inputs must already exist;
- missing semantic input defers rather than being guessed;
- PR231 reused launch-like semantic inputs and does not prove arbitrary
  non-curated semantic understanding;
- blocked-state sidecars preserve runtime/user-surface blocking;
- product proof, human validation, advice correctness, scoring, certification,
  approval, and action authorization remain non-claims.

PR234 adds a review layer rather than changing code. It also leaves the
practical language intact: missingness, blockers, deferred reasons, operator
attention, source-depth limits, and runtime/user-surface blocked state.

It does not introduce a new Unknowns Register.
It does not add a known-known / known-unknown taxonomy.

## Term-by-Term Review

### `sidecar_ready_for_explicit_write`

This term carries the highest overread risk.

It could be mistaken for resolver approval if detached from the surrounding
limits. It could also be mistaken for permission to write automatically if the
word "ready" is read without "explicit write."

It remains acceptable because current docs bind it to:

- dry-run completion;
- explicit operator action as a later manual step;
- no runner-side sidecar write;
- no resolver approval;
- no runtime/user-surface readiness;
- false write/archive/runtime/resolver/action/proof/scoring flags.

Preferred reading:

```text
The deterministic runner reached dry-run readiness. A separate explicit
operator write command may be considered later if all write preconditions pass.
```

Forbidden reading:

```text
The sidecar is approved, available, or automatically writable.
```

### `sidecar_ready_blocked_state`

This term is acceptable because it says both "ready" and "blocked state."
The important caveat is that "ready" refers to preparing or preserving a
blocked-state sidecar shape, not making the case available for runtime or user
surface.

Preferred reading:

```text
The runner can preserve a blocked Decision Work state through dry-run without
turning it into availability.
```

Forbidden reading:

```text
The case is ready for user-facing use.
```

### `deferred_missing_semantic_read`

This term is safe and useful. It names missing semantic input directly and
helps prevent the runner from becoming a hidden semantic generator.

### `deferred_missing_triage`

This term is safe and useful for the same reason. It preserves missingness
rather than repairing or fabricating triage.

### `blocked_runtime_or_user_surface_risk`

This term is safe and conservative. It may be broad, but the direction is
correct: fail closed when runtime or user-surface risk is unresolved.

### Dry-Run Readiness

Dry-run readiness is acceptable only when paired with "not an actual write."
The PR233 package gate makes that boundary visible. PR234 keeps it.

### Automation Readiness

Automation readiness is acceptable because PR224 and PR233 define it as an
offline/operator readiness milestone. It is not runtime automation, queue
worker behavior, or default-on attachment.

### Explicit Write

Explicit write is acceptable because it points away from hidden automation.
It should keep carrying the operator-action implication.

### Sidecar-Ready

Sidecar-ready is acceptable only as shorthand inside docs that also say:

- explicit operator action is required for writes;
- resolver refs are not approved;
- runtime use remains separate;
- user-surface readiness is not established.

### Blocked-State Sidecar

Blocked-state sidecar is acceptable. It is one of the clearer terms because it
keeps the blocked outcome in the noun phrase.

### `runner_summary.json`

This term is safe. The summary is a custody and routing artifact, not a proof
or approval artifact.

### `operator_attention_items`

This term is safe. It routes human/operator attention without scoring answer
quality or authorizing action.

## Review Questions

Could `sidecar_ready_for_explicit_write` be mistaken for resolver approval?
Yes, if isolated from caveats. In the current docs it is acceptable because
the no-approval caveats are repeated and test-covered.

Could it be mistaken for permission to write automatically?
Yes, if "ready" is read without "explicit." In current docs, it is acceptable
because the runner is repeatedly described as no-write and command-only.

Could `sidecar_ready_blocked_state` be mistaken for user-surface readiness?
The risk is lower, but still possible if "ready" is overread. The current docs
make the blocked-state meaning explicit enough for internal use.

Could dry-run readiness be mistaken for an actual sidecar write?
Yes, if the dry-run qualifier is omitted. Current docs preserve the qualifier
and false write/archive flags.

Could automation readiness be mistaken for runtime automation?
Yes, which is why PR224 and PR233 explicitly define it as offline/operator
readiness and not runtime automation.

Do docs clearly say the runner never writes sidecars by itself?
Yes.

Do docs clearly say semantic inputs must already exist?
Yes.

Do docs clearly say this is not arbitrary-run semantic generation?
Yes.

Do docs clearly say this is not product proof, human validation, scoring,
advice correctness, certification, or action authorization?
Yes.

Are PR229 and PR231 limitations visible enough in package docs?
Yes. PR233 records that PR229 deferred on missing semantic input and PR231
reused existing launch-like semantic inputs.

Is the language clear enough for a smart non-engineer in the first 30 seconds?
Mostly yes for internal readers. The strongest first-30-second sentence is:

```text
The runner can stop safely when semantic inputs are missing and can reach
dry-run readiness when safe semantic inputs already exist; it still does not
write sidecars, approve refs, wire runtime, or prove correctness.
```

## Doc-Only Clarification

PR234 does not require code or constant changes. The main clarification is this
review itself: it pins the intended readings and forbidden readings before the
next Product Delta evaluation-readiness phase begins.

Future docs should keep the phrase "sidecar-ready" adjacent to "explicit
operator write" or "dry-run readiness." They should avoid shortening it to
"ready" in titles, receipts, or summaries.

## Decision

The language review is complete and safe enough to move to the next separate
phase: Product Delta evaluation readiness.

Selected gate:

```text
proceed_to_product_delta_evaluation_readiness_prd
```

Recommended next PR:

```text
Product Delta Evaluation Readiness PRD v0
```

The next PR should be a new evaluation phase PRD. It should not be mixed into
this closeout review, and it should not jump directly to a live model-judge
harness.

Put directly: Product Delta evaluation work should not be mixed into this closeout review.
It also should not jump directly to a live model-judge harness.

## Boundary Confirmation

PR234 does not:

- run `$lolla`;
- invoke the Lolla skill;
- call provider/model APIs;
- create new Lolla runs;
- change prompts;
- wire runtime;
- make runtime attachment default-on;
- approve resolver refs;
- create a queue worker or daemon;
- write sidecars;
- mutate archives;
- create checked-in sidecar outputs;
- create product proof;
- claim human validation;
- score answer quality;
- validate advice correctness;
- add approval or certification labels;
- authorize agent or automatic action.
