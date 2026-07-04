# Decision Work Sidecar Automation Readiness PRD v0

Status: PR224 automation-readiness phase PRD
Date: 2026-07-04

Review artifact:
[Decision Work Sidecar Automation Readiness PRD review](../../reviews/codex-assisted/decision-work-sidecar-automation-readiness-prd-v0/review.json)

## Purpose

PR224 starts the next Decision Work sidecar phase after Sidecar Internal v1.
It defines automation readiness as a conservative offline phase, not runtime
automation. The phase should make newly completed runs easier to process
through an operator/runner flow while preserving attachable, blocked, deferred,
and rejected Decision Work states.

This PRD does not implement a runner, queue worker, runtime hook, direct
runtime interpretation, provider/model call, resolver approval, sidecar write,
or checked-in sidecar output. It also does not claim product proof, human
validation, advice correctness, answer-quality scoring, certification, or
action authorization.

## Current Internal v1 Status

Decision Work Sidecar Internal v1 is complete in the narrow sense recorded by
PR217 and closed by PR223.

Internal v1 is functional as a command-only, explicit-operator, no-overwrite
sidecar pipeline for validated Decision Work artifacts, ending in a
`decision_work/` sidecar on a completed-run archive, with receipts and
non-claims preserved.

The current chain can reach:

```text
generated read
-> intake validation
-> brief supply
-> rendered Decision Work Brief
-> triage supply packet
-> generated triage read
-> resolver-supply candidate packet
-> sidecar update packet
-> dry-run sidecar preview
-> explicit real archive sidecar write
-> receipt inspection
```

The chain remains operator-driven. Generated-read semantic supply exists only
through checked-in-safe/operator-assisted examples. The launch case can reach
write-ready and sidecar-completed states. The deploy/high-risk case preserves
runtime/user-surface blocked state.

## Why Automation Readiness, Not Runtime Automation

The next phase should reduce operator toil without changing the product
boundary. It should make the internal command chain easier to run, inspect,
and stop, but it should not make Lolla automatically interpret arbitrary runs
or attach sidecars in runtime.

Automation readiness means:

- an operator can supply explicit inputs;
- a command can orchestrate existing deterministic CLIs;
- every boundary can stop with a clear status;
- missing semantic supply remains deferred rather than guessed;
- blocked high-risk outcomes remain blocked;
- no sidecar write happens unless explicitly enabled and preconditions pass;
- runtime hooks remain unchanged and default-off;
- resolver refs remain not approved.

Runtime automation would mean a different risk boundary: a hook or worker
acting on newly completed runs without the operator manually choosing the
inputs and mode. This PRD deliberately avoids that boundary.

## Target Outcome For Newly Completed Runs

The automation-readiness phase should make it possible for a newly completed
run to enter an offline operator/runner flow and end in one of these states:

- an attachable sidecar-ready packet for explicit operator write;
- a blocked-state sidecar-ready packet that preserves runtime/user-surface
  blocking;
- a deferred state because semantic input is missing;
- a rejected state because source, privacy, schema, or custody checks failed.

The phase should not promise that every completed run can be semantically
understood. It should preserve missingness and refusal as first-class
outcomes.

## Target Statuses

The next phase should use these status names consistently:

- `sidecar_ready_for_explicit_write`;
- `sidecar_ready_blocked_state`;
- `deferred_missing_semantic_read`;
- `deferred_missing_triage`;
- `blocked_privacy_risk`;
- `blocked_source_depth_insufficient`;
- `blocked_schema_or_custody_failure`;
- `blocked_runtime_or_user_surface_risk`.

These statuses are routing and custody states. They are not approval labels,
quality scores, product proof, or action authorization.

## Roadmap

Recommended conservative roadmap:

### PR224 Automation Readiness PRD

This PRD. It defines the phase, target statuses, non-goals, roadmap, bundling,
and gate.

### PR225 Offline Operator Runner Plan

Plan-only. Define a one-shot offline operator runner that orchestrates existing
CLIs from explicit inputs and safe output paths. No implementation.

Implemented follow-up:
[Decision Work Offline Operator Runner Plan](decision-work-offline-operator-runner-plan-v0.md)
selects `proceed_to_offline_operator_runner_adapter` for PR226. It keeps the
future runner one-shot, command-only, explicit-input only, and default no-write
while still excluding queue workers, runtime wiring, semantic interpretation,
resolver approval, provider/model calls, scoring, proof claims, and action
authorization.

### PR226 Offline Operator Runner Adapter

Implement the command-only runner. The runner should call existing CLIs and
produce a summary JSON. It should not add semantic interpretation.

Implemented follow-up:
[Decision Work Offline Operator Runner Adapter](decision-work-offline-operator-runner-adapter-v0.md)
implements this no-write runner and selects
`proceed_to_offline_operator_runner_fixture_review`.

### PR227 Runner Fixture Review

Review runner fixture outputs for launch-like and blocked/high-risk cases.
Confirm status mapping, stop behavior, and non-claims.

Implemented follow-up:
[Decision Work Offline Operator Runner Fixture Review](decision-work-offline-operator-runner-fixture-review-v0.md)
reviews controlled launch/deploy and blocker fixtures, confirms the no-write
boundary, and selects `proceed_to_non_curated_completed_run_pilot_plan`.

### PR228 Non-Curated Completed-Run Pilot Plan

Plan a first non-curated completed-run pilot. Define safe inputs, privacy
limits, expected stop points, and review criteria.

Implemented follow-up:
[Decision Work Non-Curated Completed-Run Pilot Plan](decision-work-non-curated-completed-run-pilot-plan-v0.md)
chooses a synthetic or sanitized archive-like fixture by default, preserves
missingness/blocker/deferred fields, keeps outputs temp/operator-local, and
selects `proceed_to_non_curated_completed_run_pilot`.

### PR229 Non-Curated Completed-Run Pilot

Run the offline path on one non-curated completed-run case using safe supplied
semantic artifacts. No runtime hook and no provider/model call.

Implemented follow-up:
[Decision Work Non-Curated Completed-Run Pilot](decision-work-non-curated-completed-run-pilot-v0.md)
runs a synthetic non-curated completed-run-like fixture with no generated read,
keeps the runner summary temp-only, records `deferred_missing_semantic_read`,
and selects `proceed_to_non_curated_pilot_review`.

### PR230 Non-Curated Pilot Review

Review whether the non-curated pilot preserved missingness, source limits,
blocked states, and non-claims.

Implemented follow-up:
[Decision Work Non-Curated Pilot Review](decision-work-non-curated-pilot-review-v0.md)
accepts PR229's deferred result as an honest first non-curated signal, decides
it is not enough for package readiness, and selects
`proceed_to_second_non_curated_completed_run_pilot`.

### PR231 Second Non-Curated Completed-Run Pilot

Run a second non-curated case with existing checked-in-safe generated read and
generated triage inputs, so the runner can exercise deeper chain behavior
without inventing semantics.

### PR232 Second Non-Curated Pilot Review

Review whether the second non-curated pilot preserves missingness, source
limits, blocked states, and non-claims while traveling deeper than PR229.

### PR233 Automation Readiness Package Gate

Package the readiness layer if PR226 through PR232 are clean. This is still
not runtime integration.

### Optional PR234 Receipt / Blocked-State Language Review

Review whether receipts and blocked-state language stay legible without
implying product readiness, advice correctness, approval, or availability.

### Optional PR235 Runtime Hook Integration Plan

Plan runtime hook integration only after the offline runner and non-curated
pilot reviews show stable boundaries. No implementation in this optional plan.

### Optional PR236 Automation Phase Closure / Next Decision Gate

Decide whether to pause, add another non-curated pilot, plan runtime hook
integration, or revise the automation-readiness scope.

Historical PR224 roadmap labels retained for traceability:

- PR224 Automation Readiness PRD;
- PR225 Offline Operator Runner Plan;
- PR226 Offline Operator Runner Adapter;
- PR227 Runner Fixture Review;
- PR228 Non-Curated Completed-Run Pilot Plan;
- PR229 Non-Curated Completed-Run Pilot;
- PR230 Non-Curated Pilot Review;
- PR231 Automation Readiness Package Gate, now deferred by PR230;
- PR232 Receipt / Blocked-State Language Review, now deferred by PR230;
- optional PR233 Second Non-Curated Pilot, now promoted by PR230;
- optional PR234 Runtime Hook Integration Plan;
- optional PR235 Automation Phase Closure / Next Decision Gate.

## Bundling Recommendation

Recommended bundles:

- Bundle A: PR224 Automation Readiness PRD and PR225 Offline Operator Runner
  Plan.
- Bundle B: PR226 Offline Operator Runner Adapter and PR227 Runner Fixture
  Review.
- Bundle C: PR228 Non-Curated Completed-Run Pilot Plan, PR229 Non-Curated
  Completed-Run Pilot, and PR230 Non-Curated Pilot Review.
- Bundle D: PR231 Second Non-Curated Completed-Run Pilot and PR232 Second
  Non-Curated Pilot Review.
- Bundle E: PR233 Automation Readiness Package Gate and optional PR234
  Receipt / Blocked-State Language Review.
- Optional Bundle F: PR235 Runtime Hook Integration Plan and PR236 Automation
  Phase Closure / Next Decision Gate.

Original Optional Bundle E is retained as a traceability label for the PR224
roadmap, but PR230 promotes the second non-curated pilot ahead of package
readiness.

Do not bundle runtime wiring, default-on behavior, provider/model calls,
resolver approval, queue workers, or direct runtime interpretation into this
phase.

## Explicit Non-Goals

Automation readiness is not:

- customer readiness;
- default-on runtime behavior;
- direct runtime interpretation;
- runtime model/provider calls;
- automatic arbitrary-run correctness;
- resolver approval;
- answer-quality scoring;
- product proof;
- human validation;
- advice correctness;
- certification;
- action authorization.

It is also not proof that Lolla improved a decision, and it is not permission
for an agent to act.

## Acceptance Criteria

The automation-readiness phase is acceptable when:

- a one-shot offline runner can orchestrate the existing deterministic command
  chain from explicit inputs;
- a newly completed run can end in sidecar-ready, blocked, deferred, or
  rejected state without hidden interpretation;
- missing semantic reads and missing triage remain deferred rather than
  guessed;
- blocked high-risk cases preserve runtime/user-surface blocking;
- runner output records source refs, blocker reasons, and non-claims;
- no provider/model calls are introduced;
- no runtime wiring or default-on behavior is introduced;
- resolver refs remain not approved;
- product proof, human validation, advice correctness, scoring, approval, and
  action authorization remain false.

## Risks

Main risks:

- an offline runner could be mistaken for a queue worker or runtime hook;
- operator convenience could hide semantic missingness;
- sidecar-ready states could be overread as user/customer readiness;
- blocked-state sidecars could be mistaken for available sidecars;
- generated-read fluency could create overtrust;
- non-curated runs may expose source-depth gaps not visible in curated cases;
- target path handling could become too permissive if runner write mode is
  enabled too early.

## Stop Conditions

Stop automation-readiness work if:

- the next slice requires provider/model calls;
- runner design requires direct runtime interpretation;
- runtime hook changes are needed to make progress;
- queue worker behavior is needed before one-shot operator flow is proven;
- semantic reads are missing and the design would guess around them;
- privacy/private/provider markers would enter checked-in artifacts;
- resolver refs would be marked approved;
- product proof, human validation, advice correctness, scoring, certification,
  or action authorization language appears.

## Decision Gate

Selected gate:

```text
proceed_to_offline_operator_runner_plan
```

Alternative gates:

- `pause_for_review`;
- `revise_automation_readiness_scope`;
- `stop_automation_phase`.

Recommended next PR:

```text
PR225 Offline Operator Runner Plan v0
```
