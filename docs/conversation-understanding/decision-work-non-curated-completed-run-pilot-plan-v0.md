# Decision Work Non-Curated Completed-Run Pilot Plan v0

Status: PR228 plan
Date: 2026-07-04

[Review JSON](../../reviews/codex-assisted/decision-work-non-curated-completed-run-pilot-plan-v0/review.json)

## Purpose

PR228 plans the first non-curated completed-run pilot for the
[Decision Work Offline Operator Runner](decision-work-offline-operator-runner-adapter-v0.md).

This is plan/review/test work only. It does not run the pilot, generate or
repair semantic reads, call models/providers, run `$lolla`, invoke the Lolla
skill, create queue workers, wire runtime, approve resolver refs, write
sidecars, mutate archives, or create checked-in sidecar outputs.

The purpose is to define how a completed run outside the curated launch/deploy
examples can enter the offline operator flow while preserving missingness,
blockers, deferred reasons, source-depth limits, runtime/user-surface block
states, custody flags, and non-claims.

## Candidate Qualification

A PR229 non-curated pilot candidate must be:

- not `launch-public-enterprise-beta`;
- not `deploy-assisted-intake-routing`;
- a completed-run case selected explicitly by an operator;
- safe to reference without copying raw/private conversation text into the
  repository;
- backed by existing generated Decision Work artifacts, or expected to defer
  when those artifacts are absent;
- small enough that the runner outputs can be inspected by one reviewer;
- free of known privacy/private/provider markers in the supplied artifacts;
- free of product-proof, answer-quality, advice-correctness, approval,
  certification, or action-authorization claims.

Non-curated does not mean arbitrary automatic interpretation. It only means the
case was not one of the two curated fixture cases already used to build the
runner path.

## Fixture Policy

PR229 should use a synthetic or sanitized archive-like fixture as the default
completed-run archive input.

The fixture may preserve completed-run shape and marker files, but it must not
include raw conversation text, raw revised answer text, raw memo text, provider
text, private ledgers, secrets, or local absolute paths.

An explicit local completed-run archive may be referenced only as read-only
operator context when the operator has already supplied checked-in-safe
generated read and generated triage artifacts. The runner must not auto-discover
private archive data, scan broad directories, or copy raw archive content.

PR229 must not write to the explicit local archive. The runner should stop at
dry-run readiness or blocked/deferred status.

## Required Archive Markers

The pilot fixture should contain only minimal completed-run markers needed to
prove that the operator selected a completed-run-shaped target. The exact marker
set should be recorded by PR229, but the recommended v0 set is:

- a fixture archive root directory;
- a case/run metadata file with a sanitized case id;
- a completed-run marker such as `completed.json` or equivalent fixture marker;
- no existing `decision_work/` directory;
- no raw/private content files;
- no provider-output files;
- no local absolute path references.

If a real local completed-run archive is referenced read-only, PR229 should
record only sanitized path refs such as `<completed-run-archive-dir>` in docs and
operator notes. It should not check in absolute paths.

## Required Inputs

PR229 should invoke the runner only from explicit paths:

- `completed_run_archive_dir_or_sanitized_fixture`;
- `generated_read_json`;
- `generated_triage_json`;
- `case_id`;
- `safe_output_dir`;

These correspond to the runner arguments:

- `--completed-run-archive-dir <synthetic-or-sanitized-completed-run-fixture>`;
- `--generated-read <generated-read-json>`;
- `--generated-triage <generated-triage-json>`;
- `--case-id <non-curated-case-id>`;
- `--safe-output-dir <safe-temp-output-dir>`;
- `--out <safe-temp-output-dir>/runner_summary.json`;
- `--pretty`.

The generated read and generated triage must already exist before the pilot.
PR229 must not generate, infer, or repair semantic interpretation.

If generated read is missing, the expected final status is:

```text
deferred_missing_semantic_read
```

If generated triage is missing, the expected final status is:

```text
deferred_missing_triage
```

## Runner Command Shape

PR229 should use a command shaped like:

```bash
python3 scripts/evals/run_decision_work_offline_operator.py \
  --completed-run-archive-dir <synthetic-or-sanitized-completed-run-fixture> \
  --generated-read <generated-read-json> \
  --generated-triage <generated-triage-json> \
  --case-id <non-curated-case-id> \
  --safe-output-dir <safe-temp-output-dir> \
  --out <safe-temp-output-dir>/runner_summary.json \
  --pretty
```

Do not pass `--write-sidecar` in PR229. If a write flag is accidentally
supplied, the runner should return `stopped_before_explicit_write` or fail
closed. PR229 should treat that as evidence that the write boundary held, not
as a successful pilot outcome.

## Expected Outputs

Allowed temp/operator-local outputs:

- `runner_summary.json`;
- generated-read intake result;
- brief-supply packet;
- rendered generated-read brief;
- triage-supply packet;
- resolver-supply candidate packet;
- sidecar update packet;
- dry-run result;
- optional dry-run preview files under a safe temp output directory.

Outputs that must not be checked in:

- `runner_summary.json`;
- intermediate supply packets generated for the pilot;
- dry-run result JSON;
- dry-run preview files;
- any `decision_work/` sidecar files;
- real completed-run archive files;
- raw/private/provider content;
- local absolute path refs.

Outputs that must remain temp/operator-local:

- all runner outputs;
- all intermediate generated packets;
- all dry-run preview files;
- any operator notes that contain local paths or case-private context.

## Status Semantics

Success means the runner summary reaches one of the expected non-write readiness
states without crossing a boundary:

- `sidecar_ready_for_explicit_write`;
- `sidecar_ready_blocked_state`.

Deferred means required semantic artifacts are absent or the runner lacks enough
deterministic input to proceed:

- `deferred_missing_semantic_read`;
- `deferred_missing_triage`.

Blocked means deterministic checks identified an unsafe or non-actionable
condition:

- `blocked_privacy_risk`;
- `blocked_source_depth_insufficient`;
- `blocked_schema_or_custody_failure`;
- `blocked_runtime_or_user_surface_risk`.

Failure means the runner cannot produce a coherent summary or has to fail
closed:

- `runner_failed_closed`;
- malformed input;
- unreadable artifact;
- unsafe output path;
- attempted write mode that does not stop before write.

## Source Depth, Privacy, And Custody Handling

If source depth is insufficient, PR229 should preserve the existing
source-depth status from deterministic artifacts and treat the pilot as blocked
or deferred. It must not infer missing source context.

If privacy, custody, or schema checks fail, PR229 should preserve the runner
status and blocker reasons, stop the pilot, and check in no generated output.

If runtime/user-surface status is blocked, PR229 should preserve that blocked
state and avoid wording that suggests user-surface readiness or runtime
availability.

## Missingness Lens

PR229 must preserve practical missingness fields already used by the runner:

- `missing_required_inputs`;
- `blocker_reasons`;
- `deferred_reasons`;
- `operator_attention_items`;
- `source_depth_status`;
- `runtime_use_status`;
- `user_surface_status`.

PR229 must not introduce a new Unknowns Register schema, a
known-known / known-unknown taxonomy, or any new semantic conclusion not
already present in the supplied artifacts.

In short, PR229 must not add model/provider calls, must not run `$lolla`, must
not invoke the Lolla skill, must not add semantic interpretation generation,
must not create queue workers, must not add runtime wiring, must not perform
resolver approval, must not write sidecars, must not mutate archives, must not
claim product proof, must not claim human validation, must not add
answer-quality scoring, must not make an advice-correctness claim, and must
not grant action authorization.

## Runner Summary Requirements

The PR229 runner summary must preserve:

- schema version;
- case id;
- final status;
- completed steps;
- skipped steps;
- stopped step;
- artifact refs;
- missing required inputs;
- blocker reasons;
- deferred reasons;
- operator attention items;
- source-depth status when available;
- runtime-use status when available;
- user-surface status when available;
- non-claims;
- custody flags;
- false write/archive/runtime/resolver/action/scoring/proof flags.

The summary must keep:

- `write_attempted: false`;
- `actual_sidecar_write_performed: false`;
- `archive_mutated: false`;
- `historical_archive_mutated: false`;
- `resolver_refs_approved: false`;
- `runtime_wiring_changed: false`;
- `can_authorize_agent_action: false`;
- `can_be_used_as_quality_label: false`.

## Refusal Rules

PR229 should stop or fail closed if:

- generated read is missing;
- generated triage is missing;
- source depth is insufficient;
- privacy/private/provider markers appear;
- local absolute path refs would be checked in;
- schema or custody checks fail;
- runner output path is unsafe;
- a `decision_work/` sidecar output would be checked in;
- a real archive write is attempted;
- `resolver_refs_approved` is true;
- product proof, human validation, answer-quality scoring,
  advice-correctness, approval/certification, or action authorization appears;
- the pilot would require model/provider calls, `$lolla`, the Lolla skill, or
  semantic interpretation generation.

## Validation For PR229

PR229 should validate:

- py_compile for any pilot test;
- focused pytest for the pilot and Product Delta boundary lint;
- runner CLI over the selected non-curated fixture;
- jq over runner summary and review JSON;
- final status matches expected success/deferred/blocked outcome;
- no checked-in `decision_work/` sidecar output;
- no checked-in temp runner outputs;
- no real historical archive mutation;
- Product Delta boundary lint reports 0 blocking errors, 0 warnings, 0 info;
- git diff check is clean;
- Markdown local links are clean;
- trailing whitespace scan is clean;
- privacy/content marker scan is clean;
- `SKILL.md`, `scripts/skill/*`, and `scripts/archive_run.py` are untouched;
- staged area is empty after commit.

## Stop Conditions

PR229 should stop if:

- the candidate requires creating a new generated read;
- the candidate requires creating a new generated triage read;
- the candidate requires a model/provider call;
- the candidate requires `$lolla` or the Lolla skill;
- the candidate requires broad archive discovery;
- the candidate requires copying raw/private content;
- the candidate requires a real sidecar write;
- the candidate requires runtime wiring;
- the candidate requires resolver approval;
- the runner summary hides missingness, blockers, deferred reasons, or
  runtime/user-surface block state.

## Decision Gate

Selected gate:

```text
proceed_to_non_curated_completed_run_pilot
```

Recommended next PR:

```text
PR229 Non-Curated Completed-Run Pilot v0
```

PR229 should run exactly one non-curated pilot through the offline operator
runner using explicit safe paths, temp/operator-local outputs, and no write
step. It should stop at runner readiness, blocked state, deferred state, or
fail-closed state, then review whether the runner is ready for broader
automation-readiness packaging.

## Implemented Follow-Up

[Decision Work Non-Curated Completed-Run Pilot](decision-work-non-curated-completed-run-pilot-v0.md)
runs a synthetic non-curated completed-run-like fixture with missing generated
read and missing generated triage inputs. The runner stops at the generated-read
boundary with:

```text
deferred_missing_semantic_read
```

The pilot records the result in review JSON, keeps generated runner summaries
temp/operator-local, checks in no sidecar outputs, and selects:

```text
proceed_to_non_curated_pilot_review
```
