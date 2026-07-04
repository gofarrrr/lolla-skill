# Decision Work Offline Operator Runner Plan v0

Status: PR225 plan-only gate
Date: 2026-07-04

Review artifact:
[Decision Work Offline Operator Runner Plan review](../../reviews/codex-assisted/decision-work-offline-operator-runner-plan-v0/review.json)

## Purpose

PR225 defines the first implementation slice for the Decision Work Sidecar
Automation Readiness phase: a one-shot offline operator runner.

This is a plan, not an adapter. It does not implement a runner, queue worker,
runtime hook, direct runtime interpretation, semantic generation, provider or
model call, resolver approval, sidecar write, or checked-in sidecar output.

The future runner should reduce operator toil by orchestrating existing
deterministic CLIs from explicit inputs. It should keep every boundary visible
and fail closed when a required artifact, source ref, schema, custody marker,
or privacy boundary is missing.

## Source Phase

PR224 defines automation readiness as an offline/operator phase. It selected:

```text
proceed_to_offline_operator_runner_plan
```

This plan keeps that boundary. The next slice should be command-only and
one-shot before any queue worker is considered.

## Runner Shape

The future PR226 runner should be:

- command-only;
- offline;
- explicit-input only;
- one-shot;
- deterministic;
- summary-producing;
- allowed to stop at each boundary;
- not a daemon or queue worker;
- not runtime wiring;
- not semantic interpretation;
- not resolver approval;
- not default-on behavior.

The runner should orchestrate existing CLIs rather than reimplementing their
logic. It should preserve the same artifacts and refusal semantics operators
already use manually.

## Expected Future Inputs

PR226 should accept:

- `--completed-run-archive-dir`;
- `--generated-read`;
- `--generated-triage`;
- `--case-id`;
- `--safe-output-dir`;
- `--operator-confirm-real-archive-write` as an optional gated flag;
- `--write-sidecar` as optional and default `false`;
- `--stop-before-write` as optional.

The runner should require explicit paths. It should not infer private source
paths, discover historical archives broadly, or scan for arbitrary completed
runs.

## Expected Future Outputs

PR226 should produce:

- `runner_summary.json`;
- paths to generated read intake result;
- paths to brief supply;
- paths to rendered generated-read brief;
- paths to triage supply;
- paths to resolver supply;
- paths to sidecar update packet;
- paths to dry-run result;
- optional path to real archive sidecar write receipt when write mode is
  explicitly enabled and preconditions pass;
- final status;
- blocker reasons;
- non-claims.

The runner summary should not include raw/private conversation text, raw
revised answer text, raw memo text, provider text, private ledgers, local
absolute path leaks in checked-in artifacts, secrets, proof claims, scoring
claims, approval labels, or action authorization.

## Orchestration Steps

PR226 should call existing CLIs in order:

1. `scripts/evals/validate_decision_work_generated_interpretation_read.py`;
2. `scripts/evals/build_decision_work_generated_read_brief_supply.py`;
3. `scripts/evals/render_decision_work_generated_read_brief.py`;
4. `scripts/evals/build_decision_work_generated_read_triage_supply.py`;
5. `scripts/evals/build_decision_work_generated_read_resolver_supply.py`;
6. `scripts/evals/build_decision_work_resolver_candidate_sidecar_update_packet.py`;
7. `scripts/evals/dry_run_decision_work_sidecar_write.py`;
8. optionally `scripts/evals/write_decision_work_real_archive_sidecar.py`.

The optional write step should remain disabled by default. It should require
both `--write-sidecar` and `--operator-confirm-real-archive-write`, unless a
later contract deliberately changes that requirement.

## Status Mapping

Runner statuses should align with PR224:

- `sidecar_ready_for_explicit_write`;
- `sidecar_ready_blocked_state`;
- `deferred_missing_semantic_read`;
- `deferred_missing_triage`;
- `blocked_privacy_risk`;
- `blocked_source_depth_insufficient`;
- `blocked_schema_or_custody_failure`;
- `blocked_runtime_or_user_surface_risk`.

Suggested PR226 internal stop mapping:

- missing `--generated-read` -> `deferred_missing_semantic_read`;
- intake rejection -> `blocked_schema_or_custody_failure`;
- missing `--generated-triage` -> `deferred_missing_triage`;
- privacy marker rejection -> `blocked_privacy_risk`;
- source-depth failure -> `blocked_source_depth_insufficient`;
- sidecar update packet with runtime/user-surface block ->
  `sidecar_ready_blocked_state`;
- launch-like ready dry-run with write disabled ->
  `sidecar_ready_for_explicit_write`;
- deploy/high-risk blocked-state dry-run with write disabled ->
  `sidecar_ready_blocked_state`;
- write requested without explicit confirmation ->
  `blocked_schema_or_custody_failure`;
- runtime/user-surface risk without blocked-state preservation ->
  `blocked_runtime_or_user_surface_risk`.

Statuses should be operational states, not labels about answer quality.

## Stop Behavior

The runner should stop at the earliest failed boundary and write a
`runner_summary.json` describing:

- the step that stopped;
- status;
- blocker reasons;
- source artifact refs available so far;
- missing required inputs;
- non-claims;
- whether a sidecar write was skipped;
- whether runtime wiring changed, always false;
- whether resolver refs were approved, always false.

It should not repair semantic content, infer missing generated reads, create
generated triage, approve refs, or hand-edit outputs into a passing form.

## Write Mode

Default PR226 behavior should be no write:

```text
--write-sidecar false
```

When write mode is disabled, the runner may still produce a dry-run and a
sidecar-ready status.

When write mode is enabled in a future adapter, it must still require explicit
operator confirmation, target archive markers, no existing `decision_work/`,
matching sidecar update packet and dry-run result, and the PR219 safety checks.

The runner should never overwrite an existing `decision_work/` sidecar in this
phase.

## Launch And Deploy Behavior

Launch-like available cases may reach:

```text
sidecar_ready_for_explicit_write
```

If write mode is explicitly enabled and all PR219 preconditions pass, a future
runner may call the command-only real archive sidecar write adapter.

Deploy or high-risk cases should preserve blocked state:

```text
sidecar_ready_blocked_state
```

Blocked state is not failure, not readiness, and not permission to expose the
sidecar on a user surface.

## Non-Claims

The runner summary and docs must keep these false:

- `runtime_wired`;
- `archive_hook_changed`;
- `resolver_refs_approved`;
- `product_proof`;
- `human_validated`;
- `answer_quality_scored`;
- `advice_correctness_validated`;
- `agent_action_authorized`;
- `automatic_action_authorized`.

The future runner must not claim customer readiness, automatic arbitrary-run
correctness, resolver approval, answer quality, product proof, human
validation, advice correctness, certification, approval, or action
authorization.

## Refusal Rules

The future runner should refuse or stop when:

- required input paths are missing;
- generated read intake is rejected;
- generated triage is missing;
- source refs are missing;
- privacy/private/provider markers appear;
- schema or custody checks fail;
- dry-run and sidecar update packet do not match;
- real archive write is requested without explicit confirmation;
- existing `decision_work/` sidecar would be overwritten;
- runtime/user-surface risk is present without blocked-state preservation;
- resolver refs would be marked approved;
- proof/scoring/action/certification language appears.

## Decision Gate

Selected gate:

```text
proceed_to_offline_operator_runner_adapter
```

Recommended next PR:

```text
PR226 Offline Operator Runner Adapter v0
```

Implemented follow-up:
[Decision Work Offline Operator Runner Adapter](decision-work-offline-operator-runner-adapter-v0.md)
implements the one-shot command-only runner and selects
`proceed_to_offline_operator_runner_fixture_review`. PR226 intentionally stops
at dry-run readiness and does not call the real archive write adapter.
