# Decision Work Runtime Sidecar Write Contract v0

Status: PR209 contract gate
Date: 2026-07-03
Schema: `lolla.decision_work_runtime_sidecar_write_contract.v0`

## Purpose

PR209 defines the contract for the first actual sidecar-write implementation,
but does not implement writes.

This contract follows the
[Decision Work Sidecar Write Dry-Run Package Gate](decision-work-sidecar-write-dry-run-package-gate-v0.md).
Dry-Run v1 can show what would be written from a sidecar update packet. PR209
defines what a future implementation must prove before any explicit operator
write adapter can mutate an archive.

This is docs, schema, and tests only. It does not write `decision_work/`,
mutate archives, approve resolver refs, wire runtime, call providers/models,
score answer quality, claim product proof, claim human validation, validate
advice correctness, or authorize action.

## Machine-Readable Contract

The machine-readable contract is:

- [Decision Work Runtime Sidecar Write Contract JSON](decision-work-runtime-sidecar-write-contract-v0.json)

It defines:

- allowed input schemas;
- required preconditions;
- write modes;
- sidecar write statuses;
- allowed write files;
- forbidden content and claims;
- launch/deploy handling;
- fail-closed rules;
- custody flags;
- audit receipt fields;
- non-claims.

## Allowed Inputs

A future write adapter may only consider:

- a PR202 sidecar update packet:
  `lolla.decision_work_resolver_candidate_sidecar_update_packet.v0`;
- a PR206 dry-run result:
  `lolla.decision_work_sidecar_write_dry_run.v0`.

The dry-run source must match the sidecar update packet. The dry-run must have
no blockers. The target archive path must be explicitly supplied and pass
allowlist/safety checks.

## Write Modes

The contract defines these modes:

- `disabled`;
- `dry_run_only`;
- `explicit_operator_write`;
- `future_runtime_hook_write_not_allowed_yet`.

`explicit_operator_write` is vocabulary for a later implementation PR. It is
not implemented here. `future_runtime_hook_write_not_allowed_yet` is explicitly
blocked; the existing runtime hook remains default-off.

## Statuses

The contract defines these statuses:

- `not_requested`;
- `blocked_dry_run_missing`;
- `blocked_packet_not_write_eligible`;
- `blocked_archive_path_unsafe`;
- `blocked_runtime_mode_not_allowed`;
- `blocked_privacy_risk`;
- `blocked_authority_claim`;
- `write_ready`;
- `write_ready_blocked_state_only`;
- `write_completed`;
- `failed_closed`.

`write_ready` can only apply to a launch-style `dry_run_ready` input. It does
not mean this PR wrote anything.

`write_ready_blocked_state_only` can only apply to a deploy-style
`dry_run_packet_with_runtime_block` input. Any future write must preserve
blocked runtime use, blocked user-surface use, and agent-inspection-only status.

## Allowed Files

A future implementation may only write:

- `attachment_status.json`;
- `user_receipt.md`;
- `agent_handoff_packet.json`;
- `safe_supply_summary.json`;
- `sidecar_update_packet.json`;
- `sidecar_write_receipt.json`.

The write receipt must record that archive mutation happened intentionally,
under explicit mode, with source packet refs and dry-run refs.

## Never Write

Future sidecar-write code must never write:

- raw conversation text;
- raw revised answer text;
- raw memo text;
- provider text;
- private ledgers;
- local absolute paths inside checked-in artifacts;
- secrets or credentials;
- approval or certification labels;
- answer-quality labels or scores;
- action authorization;
- provider/model outputs that are not already checked-in-safe.

## Resolver And Runtime Boundaries

The contract keeps resolver candidate state separate from approval:

- `resolver_refs_approved` must remain false;
- `resolver_refs_marked_usable` must remain false;
- candidate refs must be labeled candidate/proposed only;
- future writes must not convert candidate refs into approved refs;
- future writes must not make runtime attachment default-on;
- future writes must not change `LOLLA_DECISION_WORK_BRIEF_AFTER_ARCHIVE`.

## Launch And Deploy Handling

Launch-beta may become `write_ready` only when its dry-run is `dry_run_ready`,
its packet source matches, and the target path passes safety checks.

Deploy-intake may become `write_ready_blocked_state_only` only when its dry-run
is `dry_run_packet_with_runtime_block`. It must preserve:

- runtime use blocked;
- user-surface use blocked;
- agent-inspection-only status;
- domain/compliance caveats;
- no deployment authorization;
- no legal, compliance, or clinical clearance;
- no resolver approval.

## Fail Closed

Future implementation must fail closed when:

- dry-run result is missing;
- dry-run result does not match the source sidecar update packet;
- sidecar update packet is not write-eligible;
- target archive path is unsafe;
- mode is disabled or not allowed;
- privacy/local-path/provider/secret markers appear;
- authority, proof, scoring, advice-correctness, or action claims appear;
- runtime hook write is requested.

## Decision Gate

Selected next step:

```text
proceed_to_explicit_operator_sidecar_write_adapter
```

Recommended next PR:

```text
PR210 Explicit Operator Sidecar Write Adapter v0
```

Reason:

The dry-run package is precise enough to define the contract for a future
explicit operator write adapter. The next implementation must still be
separate, default-off, fail-closed, and constrained to controlled fixture or
operator-supplied paths.

Do not implement PR210 from this contract.
