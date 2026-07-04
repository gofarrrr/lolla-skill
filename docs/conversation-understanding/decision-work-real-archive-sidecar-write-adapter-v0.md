# Decision Work Real Archive Sidecar Write Adapter v0

Status: PR219 adapter
Date: 2026-07-04

Preceded by:
[Decision Work Real Archive Sidecar Write Plan](decision-work-real-archive-sidecar-write-plan-v0.md)

## Purpose

PR219 implements the first controlled explicit real archive sidecar write
adapter planned by PR218.

The adapter writes the PR209 allowed `decision_work/` sidecar file set into an
explicit operator-supplied completed-run archive directory only when every
precondition passes and the caller supplies
`--operator-confirm-real-archive-write`.

This is command-only operator behavior. It does not edit `scripts/archive_run.py`,
wire runtime, make runtime attachment default-on, approve resolver refs, mark
resolver refs usable, call providers/models, score answer quality, claim
product proof, claim human validation, validate advice correctness, certify
outputs, or authorize action.

## CLI

```bash
python3 scripts/evals/write_decision_work_real_archive_sidecar.py \
  --sidecar-update-packet /tmp/decision_work_resolver_candidate_sidecar_update_launch.json \
  --dry-run-result /tmp/decision_work_sidecar_write_dry_run_launch.json \
  --target-archive-dir /path/to/explicit/completed-run/archive-dir \
  --operator-confirm-real-archive-write \
  --out /tmp/decision_work_real_archive_sidecar_write_receipt_launch.json \
  --pretty
```

The command writes generated sidecar files under:

```text
<target-archive-dir>/decision_work/
```

Tests use temporary synthetic completed-run archive directories with archive
markers. They do not touch real historical archive folders.

## Output Schema

The adapter emits:

```text
lolla.decision_work_real_archive_sidecar_write_receipt.v0
```

The receipt records:

- source case;
- source sidecar update packet ref;
- source dry-run result ref;
- target archive dir ref;
- target sidecar dir ref;
- real archive write status;
- files written;
- blocker reasons;
- runtime and user-surface status;
- source refs;
- privacy and uncertainty summaries;
- custody flags;
- non-claims;
- downstream allowed and forbidden fields.

Successful command-only writes set:

- `actual_sidecar_write_performed: true`;
- `real_archive_mutated: true`;
- `historical_archive_mutated: true`.

Those fields mean only that the explicit command wrote the allowed
`decision_work/` file set into the supplied archive directory. They do not mean
runtime wiring, resolver approval, product proof, human validation, user
surface readiness, or action authorization.

Every receipt keeps:

- `runtime_wiring_changed: false`;
- `archive_hook_changed: false`;
- `resolver_refs_approved: false`;
- `product_proof: false`;
- `human_validated: false`;
- `answer_quality_scored: false`;
- `advice_correctness_validated: false`;
- `agent_action_authorized: false`;
- `automatic_action_authorized: false`.

## Statuses

The adapter uses:

- `real_archive_sidecar_write_completed`;
- `real_archive_sidecar_write_completed_blocked_state`;
- `blocked_operator_confirmation_missing`;
- `blocked_target_archive_invalid`;
- `blocked_archive_markers_missing`;
- `blocked_existing_decision_work_sidecar`;
- `blocked_target_path_unsafe`;
- `blocked_repo_path`;
- `blocked_packet_not_write_eligible`;
- `blocked_dry_run_missing`;
- `blocked_dry_run_mismatch`;
- `blocked_privacy_risk`;
- `blocked_authority_claim`;
- `failed_closed`.

## Expected Case Behavior

Launch-beta:

```text
real_archive_sidecar_write_completed
```

Deploy-intake:

```text
real_archive_sidecar_write_completed_blocked_state
```

Deploy-intake preserves runtime and user-surface blocked state. A blocked-state
sidecar is an explicit record that the generated-read path is not available
for runtime or user-surface use.

## Written Files

When a write succeeds, the adapter writes exactly:

- `decision_work/attachment_status.json`;
- `decision_work/user_receipt.md`;
- `decision_work/agent_handoff_packet.json`;
- `decision_work/safe_supply_summary.json`;
- `decision_work/sidecar_update_packet.json`;
- `decision_work/sidecar_write_receipt.json`.

Generated sidecar files are not checked into the repository.

## Path Safety

The adapter refuses:

- missing `--operator-confirm-real-archive-write`;
- relative targets;
- repo paths;
- runtime-looking paths;
- root, home, project root, or broad parent paths;
- targets that point directly at `decision_work`;
- targets that do not look archive-shaped;
- targets missing completed-run archive markers;
- targets with an existing `decision_work/` sidecar;
- packet/dry-run mismatches;
- privacy markers or local-path leaks;
- resolver approval, proof, scoring, advice-correctness, or action claims.

## Decision Gate

Selected gate:

```text
proceed_to_real_archive_sidecar_write_review
```

Recommended next PR:

```text
PR220 Real Archive Sidecar Write Review v0
```

Do not implement PR220 from this adapter. PR220 should review the launch/deploy
write outputs and receipts before any package gate.

## Implemented Follow-Up

PR220 implements the review as
[Decision Work Real Archive Sidecar Write Review](decision-work-real-archive-sidecar-write-review-v0.md).
It reviews fresh launch/deploy synthetic completed-run archive writes and
selects `proceed_to_real_archive_sidecar_write_package_gate` for PR221.

## Explicit Non-Claims

PR219 does not claim:

- runtime wiring;
- archive-hook integration;
- default-on behavior;
- resolver approval;
- resolver refs marked usable;
- customer/user-surface readiness;
- production automation;
- product proof;
- human validation;
- answer-quality scoring;
- advice correctness;
- proof that Lolla improved decisions;
- approval or certification;
- agent action authorization;
- automatic action authorization.
