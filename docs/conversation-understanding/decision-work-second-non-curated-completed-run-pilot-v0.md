# Decision Work Second Non-Curated Completed-Run Pilot v0

Status: PR231 pilot
Date: 2026-07-04

[Review JSON](../../reviews/codex-assisted/decision-work-second-non-curated-completed-run-pilot-v0/review.json)

## Purpose

PR231 runs the offline operator runner against a second non-curated
completed-run-like fixture where semantic inputs already exist. It follows the
decision from
[Decision Work Non-Curated Pilot Review](decision-work-non-curated-pilot-review-v0.md):
PR229 proved the runner stops honestly when the generated read is missing, so
the next pilot should test whether the runner can travel deeper when a
checked-in-safe generated read and generated triage are supplied.

This remains an offline pilot. It does not run `$lolla`, invoke the Lolla
skill, call models/providers, create new Lolla runs, generate a new
interpretation read, generate a new triage read, repair semantic artifacts,
infer new semantic meaning, create a queue worker, wire runtime, approve
resolver refs, write sidecars, mutate archives, or check in runner outputs.

## Non-Curated Fixture

The pilot case id is:

```text
second-non-curated-existing-semantic-input-fixture
```

The completed-run-like fixture is synthetic and temp-only. It is non-curated in
the runner-fixture sense: it is not one of the original polished launch/deploy
archive fixtures and it is not checked in.

The fixture contains only minimal sanitized markers:

- `metadata.json` with the pilot case id and fixture kind;
- `completed.json` with a minimal completed marker;
- no `decision_work/` directory;
- no raw conversation text;
- no raw revised answer text;
- no raw memo text;
- no provider text;
- no private ledgers;
- no secrets;
- no local absolute paths.

## Semantic Inputs

PR231 uses existing checked-in-safe semantic inputs:

- generated read:
  `reviews/codex-assisted/decision-work-operator-codex-generated-read-pilot-v0/read.json`;
- generated triage:
  `reviews/codex-assisted/decision-work-generated-read-triage-generation-pilot-v0/triage.json`.

This reuse is deliberate and limited. PR231 does not create new semantic
material. The semantic input pair is launch-like, while the completed-run
fixture is non-curated. Therefore the pilot tests runner orchestration depth
with already-safe semantic artifacts; it does not prove that a new non-curated
conversation has been semantically understood.

For searchability: the inputs are existing checked-in-safe launch-like
artifacts, while the archive-like fixture is synthetic and non-curated.
Exact boundary phrase: inputs are existing checked-in-safe launch-like artifacts.
Exact limitation: does not prove that a new non-curated conversation has been semantically understood.

## Runner Command Shape

Validation uses a command shaped like:

```bash
python3 scripts/evals/run_decision_work_offline_operator.py \
  --completed-run-archive-dir <synthetic-completed-run-fixture> \
  --generated-read reviews/codex-assisted/decision-work-operator-codex-generated-read-pilot-v0/read.json \
  --generated-triage reviews/codex-assisted/decision-work-generated-read-triage-generation-pilot-v0/triage.json \
  --case-id second-non-curated-existing-semantic-input-fixture \
  --safe-output-dir <safe-temp-output-dir> \
  --out <safe-temp-output-dir>/runner_summary.json \
  --pretty
```

The generated summary and intermediate artifacts remain temp/operator-local.
PR231 checks in no `runner_summary.json`, dry-run output, preview files,
sidecar output, or `decision_work/` directory.

## Observed Outcome

The pilot outcome is:

```text
sidecar_ready_for_explicit_write
```

The runner progressed beyond the generated-read boundary and completed:

- `generated_read_intake`;
- `brief_supply`;
- `rendered_brief`;
- `triage_supply`;
- `resolver_supply`;
- `sidecar_update_packet`;
- `sidecar_write_dry_run`.

It stopped at:

```text
dry_run_complete
```

No actual write was performed:

- `write_attempted: false`;
- `actual_sidecar_write_performed: false`;
- `archive_mutated: false`;
- `historical_archive_mutated: false`;
- `resolver_refs_approved: false`;
- `runtime_wiring_changed: false`.

## Runtime And User-Surface Status

The runner summary preserved conservative downstream status. The dry-run path
made a later manual explicit write visible as the next operator step, but it
did not perform that write and did not establish runtime availability.

The summary preserved:

- runtime use remains blocked from automatic sidecar update or runtime write;
- user-surface readiness is not established;
- resolver refs are not approved;
- the result is not a product proof, human validation, answer-quality score,
  advice-correctness claim, approval label, certification, or action
  authorization.

## Missingness And Blockers

For this second pilot:

- `missing_required_inputs` is empty;
- `deferred_reasons` is empty;
- `blocker_reasons` is empty;
- `operator_attention_items` contains the manual explicit-write next-step
  reminder;
- no skipped deterministic steps remain.

That is the expected contrast with PR229. PR229 showed clean deferral when
semantic material was missing. PR231 shows the same runner can travel through
the deterministic chain when semantic material is supplied, while still
stopping before any write.

## Approval And Write Boundary

The runner summary could be misread if someone treats
`sidecar_ready_for_explicit_write` as runtime success. PR231 therefore keeps the
phrase tied to manual operator review only. It means the dry-run completed and a
separate explicit write command could be considered later. It does not mean an
archive sidecar was written.

The dry-run output could also be mistaken for an actual write if detached from
the receipt flags. PR231 keeps the false write/archive/runtime/resolver flags
visible and checks in no dry-run output.

## Does This Prove Enough For Package Readiness?

Not yet. PR231 is enough to justify a review, not a package gate.

It provides a deeper non-curated fixture signal than PR229, but it still uses
existing checked-in-safe launch-like semantic inputs. PR232 should review
whether that limitation is acceptable, whether another non-curated pilot is
needed, or whether automation-readiness package work can begin.

## What This Does Not Prove

This pilot does not prove:

- the advice was correct;
- the generated read was adequate for a new non-curated conversation;
- the generated triage was adequate for a new non-curated conversation;
- Lolla improved a decision;
- resolver refs are approved;
- a sidecar was written;
- runtime attachment is safe;
- the case is user-surface ready;
- the product is validated;
- human review happened;
- answer quality was scored;
- any action is authorized.

## Decision Gate

Selected gate:

```text
proceed_to_second_non_curated_pilot_review
```

Recommended next PR:

```text
PR232 Second Non-Curated Pilot Review v0
```
