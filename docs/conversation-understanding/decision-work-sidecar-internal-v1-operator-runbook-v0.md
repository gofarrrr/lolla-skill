# Decision Work Sidecar Internal v1 Operator Runbook v0

Status: PR222 runbook
Date: 2026-07-04

Review artifact:
[Decision Work Sidecar Internal v1 Operator Runbook review](../../reviews/codex-assisted/decision-work-sidecar-internal-v1-operator-runbook-v0/review.json)

## Purpose

PR222 documents the internal operator flow for Decision Work Sidecar Internal
v1 after the real archive sidecar write package gate. It explains how an
operator can take already-available, checked-in-safe Decision Work artifacts
through validation, supply packets, dry-run, and an explicit command-only
archive sidecar write.

This runbook does not add behavior. It does not generate interpretation reads,
call providers/models, create Lolla runs, edit `scripts/archive_run.py`, wire
runtime, make runtime attachment default-on, approve resolver refs, mark refs
usable, create workers, score answer quality, claim product proof, claim human
validation, validate advice correctness, certify outputs, or authorize action.

Use placeholders in local commands:

- `<completed-run-archive-dir>`;
- `<generated-read-json>`;
- `<safe-output-dir>`;
- `<case-id>`;
- `<generated-triage-json>`.

Do not paste raw private conversation text, raw revised answer text, raw memo
text, provider text, private ledgers, secrets, or local private paths into
checked-in artifacts.

## Preconditions

Before using this runbook, an operator needs:

- a completed-run archive directory that is explicit and intentionally chosen;
- an externally supplied or operator/Codex-assisted generated interpretation
  read JSON;
- a completed-run archive directory that has the markers required by
  [Decision Work Real Archive Sidecar Write Plan](decision-work-real-archive-sidecar-write-plan-v0.md);
- no existing `decision_work/` directory in the target archive for v1;
- a safe output directory for intermediate JSON and Markdown;
- willingness to inspect blocked/deferred statuses instead of forcing progress.

For validation and tests, use synthetic completed-run archive directories. Do
not use real historical archive paths unless a human operator has explicitly
chosen the target and the command's confirmation flag is supplied.

## Operator Flow

### 1. Start From A Completed Run

Identify the completed-run archive directory:

```text
<completed-run-archive-dir>
```

The directory must be a completed-run archive target, not a repo source/docs
directory, runtime path, broad parent directory, or `decision_work/` directory
itself. In v1 the write command refuses existing `decision_work/`.

### 2. Obtain A Generated Interpretation Read

Start with:

```text
<generated-read-json>
```

The read must be checked-in-safe or locally operator-safe according to the
chosen validation mode. It must preserve source refs, uncertainty, privacy
limits, custody flags, and non-claims.

### 3. Validate The Read Through PR182 Intake

```bash
python3 scripts/evals/validate_decision_work_generated_interpretation_read.py \
  --read <generated-read-json> \
  --mode checked_in_safe \
  --out <safe-output-dir>/<case-id>-intake.json \
  --pretty
```

Expected artifact:

```text
<safe-output-dir>/<case-id>-intake.json
```

Continue only if the intake result is accepted or otherwise explicitly allowed
by the current validator policy. Stop or repair if the result is rejected,
blocked, privacy-risked, missing source refs, missing uncertainty, or carrying
authority/proof/scoring/action claims.

### 4. Build Brief Supply Through PR186

```bash
python3 scripts/evals/build_decision_work_generated_read_brief_supply.py \
  --read <generated-read-json> \
  --intake <safe-output-dir>/<case-id>-intake.json \
  --out <safe-output-dir>/<case-id>-brief-supply.json \
  --pretty
```

Expected artifact:

```text
<safe-output-dir>/<case-id>-brief-supply.json
```

This copies allowed fields only. It does not generate new interpretation,
enrich a brief, create triage, update sidecars, score advice, or authorize
action.

### 5. Render The Generated-Read Brief Through PR187

```bash
python3 scripts/evals/render_decision_work_generated_read_brief.py \
  --supply <safe-output-dir>/<case-id>-brief-supply.json \
  --case-id <case-id> \
  --out <safe-output-dir>/<case-id>-generated-read-brief.md
```

Expected artifact:

```text
<safe-output-dir>/<case-id>-generated-read-brief.md
```

The rendered brief is reader-facing, but still caveated. It is not proof that
the advice is correct and not proof that Lolla improved the decision. It does not prove the advice is correct.

### 6. Build Triage Supply Through PR192

```bash
python3 scripts/evals/build_decision_work_generated_read_triage_supply.py \
  --read <generated-read-json> \
  --intake <safe-output-dir>/<case-id>-intake.json \
  --brief-supply <safe-output-dir>/<case-id>-brief-supply.json \
  --rendered-brief <safe-output-dir>/<case-id>-generated-read-brief.md \
  --out <safe-output-dir>/<case-id>-triage-supply.json \
  --pretty
```

Expected artifact:

```text
<safe-output-dir>/<case-id>-triage-supply.json
```

This prepares routing inputs for generated-read triage. It does not generate
triage by itself and does not score answer quality.

### 7. Use A Generated Triage Read

Use an existing checked-in-safe generated triage read or a separately reviewed
operator/Codex-assisted generated triage artifact:

```text
<generated-triage-json>
```

For the current two reference cases:

- launch-like cases can be ordinary caveated offline candidates;
- deploy/high-risk cases should preserve domain/compliance review needs,
  private-context dependency, overtrust risk, and runtime/user-surface
  blocking.

The triage read routes attention. It is not an approval label and not an
answer-quality score.

### 8. Build Resolver-Supply Candidate Through PR198

```bash
python3 scripts/evals/build_decision_work_generated_read_resolver_supply.py \
  --read <generated-read-json> \
  --intake <safe-output-dir>/<case-id>-intake.json \
  --brief-supply <safe-output-dir>/<case-id>-brief-supply.json \
  --rendered-brief <safe-output-dir>/<case-id>-generated-read-brief.md \
  --triage-supply <safe-output-dir>/<case-id>-triage-supply.json \
  --triage <generated-triage-json> \
  --out <safe-output-dir>/<case-id>-resolver-supply.json \
  --pretty
```

Expected artifact:

```text
<safe-output-dir>/<case-id>-resolver-supply.json
```

Resolver supply is only a candidate packet. It does not approve resolver refs,
mark refs usable, update sidecars, wire runtime, or authorize action.

### 9. Build The Sidecar Update Packet Through PR202

```bash
python3 scripts/evals/build_decision_work_resolver_candidate_sidecar_update_packet.py \
  --resolver-supply <safe-output-dir>/<case-id>-resolver-supply.json \
  --source-resolver-supply-ref <case-id>-resolver-supply.json \
  --out <safe-output-dir>/<case-id>-sidecar-update-packet.json \
  --pretty
```

Expected artifact:

```text
<safe-output-dir>/<case-id>-sidecar-update-packet.json
```

This packet proposes sidecar state. It is not an actual sidecar write, not
runtime readiness, not runtime availability, and not resolver approval.

### 10. Run Dry-Run Preview Through PR206

```bash
python3 scripts/evals/dry_run_decision_work_sidecar_write.py \
  --sidecar-update-packet <safe-output-dir>/<case-id>-sidecar-update-packet.json \
  --source-sidecar-update-packet-ref <case-id>-sidecar-update-packet.json \
  --preview-dir <safe-output-dir>/<case-id>-sidecar-preview \
  --out <safe-output-dir>/<case-id>-sidecar-dry-run.json \
  --pretty
```

Expected artifacts:

```text
<safe-output-dir>/<case-id>-sidecar-dry-run.json
<safe-output-dir>/<case-id>-sidecar-preview/
```

Dry-run preview files must remain under the explicit safe output directory.
They are not written into the completed-run archive and do not mutate
historical archives.

### 11. Write The Archive Sidecar Through PR219

Run this only after inspecting the dry-run and confirming the target archive
directory is correct:

```bash
python3 scripts/evals/write_decision_work_real_archive_sidecar.py \
  --sidecar-update-packet <safe-output-dir>/<case-id>-sidecar-update-packet.json \
  --dry-run-result <safe-output-dir>/<case-id>-sidecar-dry-run.json \
  --target-archive-dir <completed-run-archive-dir> \
  --operator-confirm-real-archive-write \
  --out <safe-output-dir>/<case-id>-sidecar-write-receipt.json \
  --pretty
```

Expected status for a launch-like case:

```text
real_archive_sidecar_write_completed
```

Expected status for a deploy/high-risk blocked-state case:

```text
real_archive_sidecar_write_completed_blocked_state
```

The command writes only:

- `decision_work/attachment_status.json`;
- `decision_work/user_receipt.md`;
- `decision_work/agent_handoff_packet.json`;
- `decision_work/safe_supply_summary.json`;
- `decision_work/sidecar_update_packet.json`;
- `decision_work/sidecar_write_receipt.json`.

The write command refuses missing operator confirmation, missing archive
markers, existing `decision_work/`, repo paths, mismatched packet/dry-run
inputs, privacy markers, resolver approval claims, proof/scoring/action claims,
and runtime wiring attempts.

### 12. Inspect The Written Sidecar

Inspect:

```text
<completed-run-archive-dir>/decision_work/attachment_status.json
<completed-run-archive-dir>/decision_work/user_receipt.md
<completed-run-archive-dir>/decision_work/sidecar_write_receipt.json
```

For `attachment_status.json`, check:

- `runtime_use_status.status`;
- `user_surface_status.status`;
- `resolver_refs_approved`;
- `runtime_wiring_changed`;
- `archive_hook_changed`;
- proof, validation, scoring, advice-correctness, and action flags.

For `user_receipt.md`, check that it is legible, caveated, and does not imply
approval, certification, runtime availability, customer readiness, or action
authorization.

For `sidecar_write_receipt.json`, check:

- `real_archive_write_status`;
- `files_written`;
- `blocker_reasons`;
- `actual_sidecar_write_performed`;
- `real_archive_mutated`;
- `historical_archive_mutated`;
- `runtime_wiring_changed: false`;
- `archive_hook_changed: false`;
- `resolver_refs_approved: false`.

## Blocked Or Deferred Status Handling

If any layer returns blocked, deferred, or repair-required status:

- stop the flow;
- preserve the result JSON;
- do not hand-edit generated outputs into passing form;
- do not overwrite an existing `decision_work/` sidecar;
- do not interpret blocked-state as user-surface readiness;
- repair only the specific source artifact or path condition that caused the
  block;
- rerun from the earliest affected step.

For deploy/high-risk cases, a blocked-state sidecar can be the correct outcome.
It records why the generated-read path is not runtime-available.

## Launch-Like Path

A launch-like case can reach:

```text
real_archive_sidecar_write_completed
```

That means the explicit command wrote the allowed file set into the supplied
archive directory. It still does not mean resolver approval, default-on runtime
attachment, product proof, human validation, advice correctness, answer-quality
scoring, certification, or action authorization.

## Deploy Or High-Risk Path

A deploy/high-risk case can reach:

```text
real_archive_sidecar_write_completed_blocked_state
```

That means the explicit command wrote a blocked-state sidecar for inspection.
It should preserve:

- `runtime_use_status.status: blocked`;
- `user_surface_status.status: blocked`;
- domain/compliance caveats;
- private-context need;
- overtrust risk;
- no action authorization.

It must not be treated as safe to deploy, clinically adequate, legally
adequate, compliance-cleared, approved, certified, or user-surface ready.

## Exact Non-Claims

Decision Work Sidecar Internal v1 does not claim:

- runtime wiring;
- archive-hook integration;
- default-on runtime behavior;
- automatic arbitrary-run semantic interpretation;
- direct runtime interpretation;
- queue worker behavior;
- resolver approval;
- resolver refs marked usable;
- customer readiness;
- product proof;
- human validation;
- answer-quality scoring;
- advice correctness;
- proof that Lolla improved decisions;
- approval or certification;
- agent action authorization;
- automatic action authorization.

## Decision Gate

Selected gate:

```text
proceed_to_current_state_limitations_narrative_refresh
```

Recommended next PR:

```text
PR223 Current State / Limitations Narrative Refresh v0
```

PR223 should refresh the board/product narrative for what Internal v1 can and
cannot claim. It should not add behavior or begin a new automation phase.
