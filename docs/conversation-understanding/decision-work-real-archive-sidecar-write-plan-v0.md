# Decision Work Real Archive Sidecar Write Plan v0

Status: PR218 plan gate
Date: 2026-07-04

Review artifact:
[real archive sidecar write plan review](../../reviews/codex-assisted/decision-work-real-archive-sidecar-write-plan-v0/review.json)

## Purpose

PR218 defines the first boundary where Decision Work sidecar files may move
from synthetic archive-shaped fixtures toward an explicitly supplied real
completed-run archive directory.

This is a plan/review/test gate only. It does not implement the write adapter,
write a real archive, mutate a completed-run folder, edit `scripts/archive_run.py`,
wire runtime, approve resolver refs, make the hook default-on, call providers
or models, score answer quality, claim product proof, claim human validation,
validate advice correctness, certify output, or authorize action.

The plan follows
[Decision Work Sidecar Internal v1 Completion PRD](decision-work-sidecar-internal-v1-completion-prd-v0.md)
and prepares the next implementation PR:
`PR219 Real Archive Sidecar Write Adapter v0`.

## Allowed Write Target

The future adapter may target only an explicit operator-supplied completed-run
archive directory.

The target must:

- be passed as an explicit command argument;
- be absolute;
- be an existing directory;
- look like an existing completed Lolla archive, case, or run folder according
  to repo archive conventions;
- contain required archive markers or artifacts before write;
- not be the repository root, home directory, filesystem root, or a broad
  parent folder;
- not be a repo source, docs, tests, review, or plans path;
- not be an arbitrary temp directory unless the caller is using the earlier
  PR214 synthetic fixture adapter instead;
- not point directly at a `decision_work` directory;
- not contain an existing `decision_work/` sidecar in v0.

The planned adapter should recognize archive shape from existing completed-run
markers such as `agent_result.json`, `reasoning_trace.json`,
`evaluation.json`, `memo.md`, `run_events.json`, or equivalent completed-run
metadata already present in a target archive directory.

## Required Preconditions

The future PR219 adapter must require:

- a PR202 sidecar update packet;
- a matching PR206 dry-run result;
- dry-run status compatible with the sidecar update packet status;
- an explicit target archive directory;
- an explicit `--operator-confirm-real-archive-write` flag;
- target archive markers proving this is a completed-run archive directory;
- no existing `decision_work/` sidecar;
- source refs present in the sidecar update packet and dry-run result;
- privacy and local-path checks passing;
- authority/proof/action/scoring flags false;
- `resolver_refs_approved: false`.

Launch-like available packets may write an available sidecar when all
preconditions pass.

Blocked or high-risk packets, including deploy-intake style packets, may write
only a blocked-state sidecar. The blocked-state write is allowed because it
preserves `runtime_use_status.status: blocked` and
`user_surface_status.status: blocked`; it must not make the case available.

## Allowed File Set

The adapter may write only this file set under the target archive's
`decision_work/` directory:

- `attachment_status.json`;
- `user_receipt.md`;
- `agent_handoff_packet.json`;
- `safe_supply_summary.json`;
- `sidecar_update_packet.json`;
- `sidecar_write_receipt.json`.

No raw conversation text, raw revised answer text, raw memo text, provider
text, private ledger content, secret material, local absolute paths, approval
labels, action authorization, or scoring fields may be copied into those files.

## Backup, Idempotency, And Overwrite Policy

The v0 policy is no-overwrite.

The future adapter must refuse the target when `decision_work/` already exists.
It should not delete, replace, merge, or patch an existing sidecar.

Any future overwrite mode must be a separate plan with:

- explicit operator confirmation;
- a backup directory or backup artifact;
- a receipt linking the backup;
- fail-closed restore expectations;
- tests proving no untracked files are silently removed.

PR219 should implement no-overwrite only.

## Refusal Rules

The future adapter must refuse:

- missing archive markers;
- unsafe target path;
- relative target path;
- repository source/docs/tests/review/plans path;
- root, home, project root, or broad parent target;
- target that points directly at `decision_work`;
- existing `decision_work/` sidecar;
- mismatched sidecar update packet and dry-run result;
- dry-run status that does not match the packet status;
- privacy, private, provider, or secret markers;
- local absolute path leaks;
- `resolver_refs_approved: true` without an explicit later resolver-approval
  PR;
- product proof, human validation, answer-quality scoring, advice-correctness,
  approval/certification, or action-authorization claims;
- runtime wiring attempts;
- default-on behavior attempts;
- archive-hook edits.

Every refusal must fail closed by returning or writing a receipt with no
sidecar files written.

## Receipts

The receipt schema should be:

```text
lolla.decision_work_real_archive_sidecar_write_receipt.v0
```

The receipt must distinguish a real archive sidecar write from runtime wiring.

For successful PR219 writes, the receipt may set:

- `actual_sidecar_write_performed: true`;
- `real_archive_mutated: true`;
- `historical_archive_mutated: true`.

Those fields mean only that an explicit operator command wrote the allowed
`decision_work/` file set into the supplied completed-run archive directory.
They do not mean runtime wiring, resolver approval, product readiness, user
surface availability, or action authorization.

The receipt must always preserve:

- `runtime_wiring_changed: false`;
- `archive_hook_changed: false`;
- `resolver_refs_approved: false`;
- `product_proof: false`;
- `human_validated: false`;
- `answer_quality_scored: false`;
- `advice_correctness_validated: false`;
- `agent_action_authorized: false`;
- `automatic_action_authorized: false`.

The receipt should include:

- source case;
- source sidecar update packet ref;
- source dry-run result ref;
- target archive dir ref;
- target sidecar dir ref;
- write status;
- blocker reasons;
- files written;
- runtime and user-surface status;
- source refs;
- privacy summary;
- uncertainty summary;
- custody flags;
- non-claims;
- downstream allowed and forbidden fields.

Path refs in checked-in test/review artifacts should be sanitized. Generated
temporary validation receipts may contain temporary refs, but checked-in
artifacts must not leak local absolute paths.

## Planned Statuses

PR219 should use these statuses:

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

Expected launch-beta behavior:

```text
real_archive_sidecar_write_completed
```

Expected deploy-intake behavior:

```text
real_archive_sidecar_write_completed_blocked_state
```

Deploy-intake must preserve runtime and user-surface blocked state.

## Validation Requirements

PR219 should prove:

- launch synthetic completed-run archive writes
  `real_archive_sidecar_write_completed`;
- deploy synthetic completed-run archive writes
  `real_archive_sidecar_write_completed_blocked_state`;
- deploy written `attachment_status.json` keeps
  `runtime_use_status.status: blocked`;
- deploy written `attachment_status.json` keeps
  `user_surface_status.status: blocked`;
- missing operator confirmation is blocked;
- missing archive markers are blocked;
- existing `decision_work/` sidecar is blocked;
- repo paths are blocked;
- broad parent paths are blocked;
- packet/dry-run mismatch is blocked;
- privacy and local-path markers are blocked;
- proof, scoring, resolver approval, and action-authorization claims are
  blocked;
- only the allowed file set is written;
- no repo `decision_work/` sidecar is written;
- `SKILL.md`, `scripts/skill/*`, and `scripts/archive_run.py` remain untouched.

The tests should use temporary synthetic completed-run archive directories with
the minimum archive markers needed by this plan. They must not touch real
historical archive folders.

## Decision Gate

PR218 selects one of:

- `proceed_to_real_archive_sidecar_write_adapter`;
- `pause_for_path_safety_review`;
- `revise_finish_line`;
- `stop_real_archive_write_work`.

Selected gate:

```text
proceed_to_real_archive_sidecar_write_adapter
```

Recommended next PR:

```text
PR219 Real Archive Sidecar Write Adapter v0
```

Do not implement PR220 from this plan. PR220 should review the adapter outputs
after PR219 exists.

## Explicit Non-Claims

PR218 does not claim:

- a write adapter exists yet;
- archive mutation has occurred;
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
