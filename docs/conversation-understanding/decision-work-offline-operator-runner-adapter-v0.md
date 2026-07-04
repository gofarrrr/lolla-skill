# Decision Work Offline Operator Runner Adapter v0

Status: PR226 adapter
Date: 2026-07-04

## Purpose

PR226 implements the first Decision Work Sidecar Automation Readiness adapter:
a one-shot, command-only offline operator runner.

The runner reduces operator toil by orchestrating existing deterministic
Decision Work CLIs from explicit input paths and writing a
`runner_summary.json` result. It is not runtime automation, not a daemon, not
a queue worker, not resolver approval, not a semantic generator, and not a
sidecar writer.

## Inputs

The runner accepts explicit paths only:

- `--completed-run-archive-dir`;
- `--generated-read`;
- `--generated-triage`;
- `--case-id`;
- `--safe-output-dir`;
- optional `--out`;
- optional `--write-sidecar`;
- optional `--operator-confirm-real-archive-write`;
- optional `--stop-before-write`.

The runner does not auto-discover private archive data, scan broad directories
for meaning, infer semantic context, or fill missing generated-read fields.

## Orchestrated Chain

PR226 calls the existing deterministic CLIs in order:

1. `scripts/evals/validate_decision_work_generated_interpretation_read.py`;
2. `scripts/evals/build_decision_work_generated_read_brief_supply.py`;
3. `scripts/evals/render_decision_work_generated_read_brief.py`;
4. `scripts/evals/build_decision_work_generated_read_triage_supply.py`;
5. `scripts/evals/build_decision_work_generated_read_resolver_supply.py`;
6. `scripts/evals/build_decision_work_resolver_candidate_sidecar_update_packet.py`;
7. `scripts/evals/dry_run_decision_work_sidecar_write.py`.

It deliberately does not call
`scripts/evals/write_decision_work_real_archive_sidecar.py`. A real archive
write remains a later explicit manual operator step.

## Output

The output schema is:

```text
lolla.decision_work_offline_operator_runner.v0
```

`runner_summary.json` includes:

- `case_id`;
- `final_status`;
- `completed_steps`;
- `skipped_steps`;
- `stopped_at`;
- `artifact_refs`;
- `missing_required_inputs`;
- `blocker_reasons`;
- `deferred_reasons`;
- `operator_attention_items`;
- `source_depth_status`;
- `runtime_use_status`;
- `user_surface_status`;
- `non_claims`;
- custody flags.

It also keeps these flags false:

- `write_attempted`;
- `actual_sidecar_write_performed`;
- `archive_mutated`;
- `historical_archive_mutated`;
- `resolver_refs_approved`;
- `runtime_wiring_changed`;
- `can_authorize_agent_action`;
- `can_authorize_automatic_action`;
- `can_be_used_as_quality_label`.

## Supported Final Statuses

The runner supports:

- `sidecar_ready_for_explicit_write`;
- `sidecar_ready_blocked_state`;
- `deferred_missing_semantic_read`;
- `deferred_missing_triage`;
- `blocked_privacy_risk`;
- `blocked_source_depth_insufficient`;
- `blocked_schema_or_custody_failure`;
- `blocked_runtime_or_user_surface_risk`;
- `stopped_before_explicit_write`;
- `runner_failed_closed`.

These are operational statuses. They are not answer-quality labels, approval
labels, product proof, user-surface readiness, or action authorization.

## Missingness Boundary

The runner may preserve missingness that is already visible from explicit
inputs or deterministic artifacts. It may record:

- a missing generated read;
- a missing generated triage read;
- a skipped step;
- a blocker reason;
- a deferred reason;
- an operator attention item;
- runtime/user-surface blocked status already present in artifacts.

It must not infer new unknowns, create a new unknowns schema, generate new
semantic interpretation, or add semantic conclusions not already present in
the supplied artifacts.

## Write Boundary

PR226 never writes a real archive sidecar. If `--write-sidecar`,
`--operator-confirm-real-archive-write`, or `--stop-before-write` is supplied,
the runner still stops before any archive write and returns:

```text
stopped_before_explicit_write
```

The blocker list records:

```text
write_mode_not_supported_in_runner_v0
```

This keeps the first automation layer useful without crossing into archive
mutation.

## CLI

Example launch-like run:

```bash
python3 scripts/evals/run_decision_work_offline_operator.py \
  --completed-run-archive-dir <completed-run-archive-dir> \
  --generated-read <generated-read-json> \
  --generated-triage <generated-triage-json> \
  --case-id launch-public-enterprise-beta \
  --safe-output-dir <safe-output-dir> \
  --out <safe-output-dir>/runner_summary.json \
  --pretty
```

The command writes intermediate artifacts and `runner_summary.json` under the
explicit safe output directory. It does not write `decision_work/`.

## Launch And Deploy Fixture Behavior

Launch-like artifacts reach:

```text
sidecar_ready_for_explicit_write
```

Deploy/high-risk artifacts reach:

```text
sidecar_ready_blocked_state
```

Deploy preserves `runtime_use_status.status: blocked` and
`user_surface_status.status: blocked`.

## Non-Claims

The runner does not:

- run `$lolla`;
- invoke the Lolla skill;
- create a new Lolla run;
- call providers or models;
- generate semantic interpretation;
- approve resolver refs;
- wire runtime;
- make runtime attachment default-on;
- create a queue worker or daemon;
- write sidecars;
- mutate archives;
- score answer quality;
- claim product proof;
- claim human validation;
- validate advice correctness;
- certify or approve outputs;
- authorize agent or automatic action.

## Decision Gate

Selected gate:

```text
proceed_to_offline_operator_runner_fixture_review
```

Recommended next PR:

```text
PR227 Offline Operator Runner Fixture Review v0
```
