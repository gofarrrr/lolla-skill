# Decision Work Offline Operator Runner Fixture Review v0

Status: PR227 fixture review
Date: 2026-07-04

## Purpose

PR227 reviews the PR226 offline operator runner over controlled temp fixtures
before any non-curated completed-run pilot.

This is a review-only pass over
[Decision Work Offline Operator Runner Adapter](decision-work-offline-operator-runner-adapter-v0.md).
It does not change runner behavior, write sidecars, mutate archives, wire
runtime, approve resolver refs, or generate semantic interpretation.

Plainly: the runner is useful only if it makes missingness and blockers easier
to inspect without hiding that an actual archive sidecar write remains a
separate explicit operator command.

## Reviewed Fixture States

The review covers:

- `launch-public-enterprise-beta` reaching
  `sidecar_ready_for_explicit_write` without writing;
- `deploy-assisted-intake-routing` reaching `sidecar_ready_blocked_state`;
- deploy preserving `runtime_use_status.status: blocked`;
- deploy preserving `user_surface_status.status: blocked`;
- missing generated read deferring as `deferred_missing_semantic_read`;
- missing generated triage deferring as `deferred_missing_triage`;
- rejected generated-read intake blocking as
  `blocked_schema_or_custody_failure`;
- privacy-marker input blocking as `blocked_privacy_risk`;
- local absolute path marker input blocking as `blocked_privacy_risk`;
- write requests stopping before explicit write as
  `stopped_before_explicit_write`.

All fixture outputs are temp-only. The review checks in no
`runner_summary.json` files, intermediate packets, dry-run results, sidecar
outputs, or `decision_work/` directories.

## Findings

The runner is useful as an operator convenience layer because it makes the
deterministic chain easier to execute while preserving step boundaries in
`runner_summary.json`.

The summary keeps these visible:

- completed steps;
- skipped steps;
- stopped step;
- artifact refs;
- missing required inputs;
- blocker reasons;
- deferred reasons;
- operator attention items;
- runtime and user-surface status when present;
- non-claims and custody flags.

The runner does not infer new unknowns or fill missing semantic fields. It
preserves missingness that is already visible from explicit inputs and
deterministic artifacts.

## Launch And Deploy Difference

Launch-beta reaches dry-run readiness for a later manual explicit write:

```text
sidecar_ready_for_explicit_write
```

Deploy-intake reaches blocked-state readiness:

```text
sidecar_ready_blocked_state
```

Deploy remains blocked for runtime use and user-surface use. This keeps the
higher-risk healthcare workflow/compliance case from being flattened into an
available sidecar state.

## Write Boundary

PR227 confirms that PR226 does not call the real archive sidecar write adapter.

If a write request is supplied, the runner stops before any write and records:

```text
stopped_before_explicit_write
```

with:

```text
write_mode_not_supported_in_runner_v0
```

The summary keeps:

- `write_attempted: false`;
- `actual_sidecar_write_performed: false`;
- `archive_mutated: false`;
- `historical_archive_mutated: false`;
- `resolver_refs_approved: false`;
- `runtime_wiring_changed: false`.

## Boundary Checks

The review confirms:

- no `$lolla` invocation;
- no Lolla skill invocation;
- no provider/model calls;
- no new Lolla runs;
- no prompt changes;
- no runtime wiring;
- no default-on attachment;
- no resolver approval;
- no queue worker or daemon;
- no checked-in sidecar outputs;
- no real historical archive mutation;
- no answer-quality scoring;
- no product proof;
- no human validation;
- no advice-correctness claim;
- no approval or certification label;
- no agent or automatic action authorization.

## Is The Runner Hiding Too Much?

The runner does not hide too much complexity in v0 because it records every
completed, skipped, blocked, and deferred step in the summary. The operator can
still inspect each intermediate artifact under the explicit safe output
directory.

The main remaining risk is language drift: `sidecar_ready_for_explicit_write`
can sound close to availability unless docs continue to say that it is dry-run
readiness only, not an archive write and not runtime attachment.

## Decision Gate

Selected next step:

```text
proceed_to_non_curated_completed_run_pilot_plan
```

Recommended next PR:

```text
PR228 Non-Curated Completed-Run Pilot Plan v0
```

Reason:

The launch and deploy fixture runs preserve missingness, blockers, deferred
states, launch/deploy distinctions, runtime/user-surface blocks, custody flags,
and non-claims while keeping actual sidecar writes, real archive mutation,
resolver approval, runtime wiring, default-on behavior, model calls, scoring,
proof claims, and action authorization closed.

Do not implement the non-curated pilot from this review. PR228 should plan that
next boundary first.
