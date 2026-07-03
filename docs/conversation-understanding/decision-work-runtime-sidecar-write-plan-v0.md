# Decision Work Runtime Sidecar Write Plan v0

Status: PR205 plan gate
Date: 2026-07-03

## Purpose

PR205 plans the first actual runtime sidecar-write implementation, but does
not implement it.

The plan starts from the PR204 pre-write package:
[Decision Work Sidecar Update Packet Pre-Write Package Gate](decision-work-sidecar-update-packet-prewrite-package-gate-v0.md).

This is docs/review/tests only. It does not write `decision_work/`, mutate
archives, approve resolver refs, wire runtime, call providers/models, score
answer quality, claim product proof, claim human validation, validate advice
correctness, or authorize action.

## What Would Be Allowed To Write

A future implementation may only consider writing from a validated
`lolla.decision_work_resolver_candidate_sidecar_update_packet.v0` packet.

Eligible inputs must preserve:

- `resolver_refs_approved: false`;
- `actual_sidecar_write_performed: false` before the write layer starts;
- `archive_mutated: false` before the write layer starts;
- `runtime_wiring_changed: false`;
- source refs;
- uncertainty summary;
- privacy summary;
- custody flags;
- non-claims;
- downstream forbidden fields.

The write layer must not invent new semantic content. It may copy proposed
packet state into a sidecar-shaped dry-run or future default-off write path
only after separate implementation gates.

## Eligible And Blocked Packet Statuses

`ready_for_sidecar_update_packet` may be eligible for a future default-off
dry-run adapter.

`packet_with_runtime_block` must not write a normal available sidecar. A future
dry-run may write only blocked/deferred state if the implementation explicitly
proves that blocked state cannot be mistaken for user-surface readiness.

These statuses must remain blocked or deferred:

- `deferred_missing_resolver_supply`;
- `blocked_resolver_supply_not_candidate`;
- `blocked_privacy_risk`;
- `blocked_authority_claim`;
- `blocked_runtime_write_attempt`;
- `requires_operator_repair`.

## Deploy-Intake Handling

Deploy-intake currently produces `packet_with_runtime_block`. The future write
plan must preserve:

- runtime use blocked;
- user-surface use blocked;
- agent-inspection-only status;
- domain/compliance caveats;
- no deployment authorization;
- no legal, compliance, or clinical clearance;
- no resolver approval.

Deploy-intake may only produce a blocked/deferred sidecar state in a future
default-off dry-run, and only after another adapter proves the boundary.

## Never Copy

Future sidecar-write code must never copy:

- raw conversation text;
- raw revised answer text;
- raw memo text;
- provider text;
- private ledgers;
- local absolute paths;
- secrets or credentials;
- resolver approval labels;
- product proof claims;
- human-validation claims;
- answer-quality scores;
- advice-correctness claims;
- action authorization.

## Preventing Approved-Ref Confusion

The write plan keeps resolver candidate state separate from approval:

- sidecar update packets are not approved refs;
- `resolver_refs_approved` must remain false;
- `resolver_refs_marked_usable` must remain false;
- future writes must label candidate refs as candidate/proposed only;
- runtime/user-surface blockers must travel forward;
- no future sidecar may imply certification, approval, correctness, or
  permission to act.

## Archive Mutation And Runtime Hook Boundary

Any future actual write would mutate archive state. Therefore it must be behind
a separate, explicit implementation PR and a default-off mode.

The existing runtime hook remains unchanged here. PR205 does not add runtime
wiring, does not change `LOLLA_DECISION_WORK_BRIEF_AFTER_ARCHIVE`, and does
not make attachment default-on.

A future implementation should start with a dry-run adapter that writes no
archive files and proves exactly what would be written.

## Required Future Tests

Before implementation, the next PR should prove:

- launch ready packet produces a dry-run write proposal only;
- deploy runtime-block packet produces a blocked/deferred dry-run proposal only;
- rejected/blocked packet statuses cannot write available sidecar state;
- resolver refs are never approved;
- candidate refs are never marked usable;
- actual archive mutation stays false in dry-run;
- runtime wiring stays false;
- private/raw/local/provider/secret markers are blocked;
- no `decision_work/` directory is written in dry-run;
- source packet artifacts are not modified.

## Decision Gate

Selected next step:

```text
proceed_to_default_off_sidecar_write_dry_run_adapter
```

Recommended next PR:

```text
PR206 Default-Off Sidecar Write Dry-Run Adapter v0
```

Reason:

The pre-write package is coherent enough to plan a dry-run adapter. The next
implementation must still avoid real sidecar writes, archive mutation,
resolver approval, runtime wiring, default-on behavior, model calls, scoring,
proof claims, and action authorization.

Do not implement PR206 from this plan.
