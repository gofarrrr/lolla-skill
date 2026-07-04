# Decision Work Non-Curated Completed-Run Pilot v0

Status: PR229 pilot
Date: 2026-07-04

[Review JSON](../../reviews/codex-assisted/decision-work-non-curated-completed-run-pilot-v0/review.json)

## Purpose

PR229 runs the
[Decision Work Offline Operator Runner](decision-work-offline-operator-runner-adapter-v0.md)
against one non-curated completed-run pilot fixture, following the
[Non-Curated Completed-Run Pilot Plan](decision-work-non-curated-completed-run-pilot-plan-v0.md).

This is an honesty test, not a victory lap. The pilot uses a synthetic
completed-run-shaped fixture and intentionally accepts a deferred result when
the required generated semantic read is absent.

It does not run `$lolla`, invoke the Lolla skill, call models/providers, create
new Lolla runs, generate or repair interpretation reads, create a queue worker,
wire runtime, approve resolver refs, write sidecars, mutate archives, check in
runner outputs, or create checked-in `decision_work/` directories.

## Non-Curated Case

The pilot case id is:

```text
non-curated-sanitized-missing-read-fixture
```

It is non-curated because it is not `launch-public-enterprise-beta` and not
`deploy-assisted-intake-routing`. It is not `deploy-assisted-intake-routing`
and is also not used to prove semantic quality. It is a synthetic/sanitized
completed-run-like fixture that exercises runner missingness behavior outside
the two curated examples.

## Fixture Shape

The fixture exists only under temp paths during tests and validation. It is not
checked in.

The synthetic completed-run-like fixture contains:

- `metadata.json` with a sanitized case id;
- `completed.json` with a minimal completed marker;
- no `decision_work/` directory;
- no raw conversation text;
- no raw revised answer text;
- no raw memo text;
- no provider text;
- no private ledgers;
- no secrets;
- no local absolute paths.

This fixture is intentionally lightweight because PR229 is testing runner
missingness behavior, not archive parsing.

## Inputs Available

Available:

- explicit completed-run-like fixture path;
- explicit case id;
- explicit safe temp output directory;
- runner CLI/module from PR226.

Missing:

- generated read JSON;
- generated triage JSON.

The runner stops at the missing generated read before attempting intake,
brief-supply, render, triage-supply, resolver-supply, sidecar update, or dry-run
steps.

## Runner Command Shape

Validation uses a command shaped like:

```bash
python3 scripts/evals/run_decision_work_offline_operator.py \
  --completed-run-archive-dir <synthetic-completed-run-fixture> \
  --generated-read <missing-generated-read-json> \
  --generated-triage <missing-generated-triage-json> \
  --case-id non-curated-sanitized-missing-read-fixture \
  --safe-output-dir <safe-temp-output-dir> \
  --out <safe-temp-output-dir>/runner_summary.json \
  --pretty
```

The generated summary remains temp/operator-local only. PR229 checks in no
`runner_summary.json`.

## Observed Outcome

The pilot outcome is:

```text
deferred_missing_semantic_read
```

The runner summary records:

- `missing_required_inputs: ["generated_read"]`;
- `deferred_reasons: ["generated_read_missing"]`;
- `stopped_at: "generated_read"`;
- all deterministic chain steps skipped;
- `write_attempted: false`;
- `actual_sidecar_write_performed: false`;
- `archive_mutated: false`;
- `historical_archive_mutated: false`;
- `resolver_refs_approved: false`;
- `runtime_wiring_changed: false`.

This is a clean deferred result. It does not pretend the runner knows what the
conversation means when the generated semantic read is absent. Put directly:
it does not pretend the runner knows what the conversation means.

## Missingness And Blockers

Missingness is visible enough for operator review:

- the missing generated read appears in `missing_required_inputs`;
- the deferred reason appears in `deferred_reasons`;
- the stopped boundary is visible through `stopped_at`;
- skipped steps make clear that no downstream artifacts were created;
- no blocker reason is invented beyond the deterministic missing-input result.

`operator_attention_items` is empty for this pilot. That is acceptable because
the only required operator action is obvious: provide an existing
checked-in-safe generated read before retrying.

## Source Depth And Runtime/User Surface Status

No source-depth status is available because the runner stops before intake and
supply generation.

No runtime/user-surface status is available because the runner never reaches
resolver supply, sidecar update packet, or dry-run. The absence is preserved as
absence; the pilot does not infer a runtime or user-surface state.

## Approval And Readiness Boundary

The runner summary does not create a misleading sense of approval or readiness.
It returns a deferred status, keeps downstream artifacts absent, and keeps all
write/archive/runtime/resolver flags false.

This means PR229 does not show that a non-curated case is ready for sidecar
write. It shows that the runner can fail usefully before semantic inputs exist.

## What This Does Not Prove

This pilot does not prove:

- the advice was correct;
- the generated read was adequate;
- Lolla improved a decision;
- a sidecar should be written;
- runtime attachment is safe;
- resolver refs are approved;
- the case is user-surface ready;
- the product is validated;
- human review happened;
- answer quality was scored;
- any action is authorized.

## Next Step

Selected gate:

```text
proceed_to_non_curated_pilot_review
```

Recommended next PR:

```text
PR230 Non-Curated Pilot Review v0
```

PR230 should review whether this deferred non-curated pilot is useful enough as
the first real automation-readiness signal, or whether PR229 should be patched
to add a second non-curated fixture with existing checked-in-safe generated
semantic artifacts.

## Implemented Follow-Up

[Decision Work Non-Curated Pilot Review](decision-work-non-curated-pilot-review-v0.md)
accepts this deferred result as an honest first non-curated signal. It does not
treat the result as enough for package readiness, and it selects:

```text
proceed_to_second_non_curated_completed_run_pilot
```

The recommended next PR is:

```text
PR231 Second Non-Curated Completed-Run Pilot v0
```
