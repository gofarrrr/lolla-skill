# Decision Work Real Archive Sidecar Write Review v0

Status: PR220 review gate
Date: 2026-07-04

## Purpose

PR220 reviews the command-only real archive sidecar write adapter introduced by
[Decision Work Real Archive Sidecar Write Adapter](decision-work-real-archive-sidecar-write-adapter-v0.md).

This is a review-only pass over fresh temp-generated launch-beta and
deploy-intake writes into synthetic completed-run archive directories. It does
not check in generated sidecar files, mutate real historical archives, edit the
archive hook, wire runtime, make runtime attachment default-on, approve
resolver refs, mark refs usable, call providers/models, score answer quality,
claim product proof, claim human validation, validate advice correctness,
certify outputs, or authorize action.

Plainly: PR219 proves that a command can write the allowed `decision_work/`
file set into an archive-markered completed-run directory when explicit
operator confirmation and safety preconditions pass. PR220 checks that behavior
using synthetic completed-run archive directories only, before any package
gate.

## Reviewed Cases

The review covers two generated-read chains:

- `launch-public-enterprise-beta`;
- `deploy-assisted-intake-routing`.

For launch-beta, the real archive sidecar write adapter can produce:

```text
real_archive_sidecar_write_completed
```

For deploy-intake, the adapter can produce:

```text
real_archive_sidecar_write_completed_blocked_state
```

Deploy-intake preserves runtime blocking, user-surface blocking, and
agent-inspection-only posture. A blocked-state sidecar is a record for future
inspection, not runtime availability.

## Written Files

Successful synthetic completed-run writes create exactly:

- `decision_work/attachment_status.json`;
- `decision_work/user_receipt.md`;
- `decision_work/agent_handoff_packet.json`;
- `decision_work/safe_supply_summary.json`;
- `decision_work/sidecar_update_packet.json`;
- `decision_work/sidecar_write_receipt.json`.

The review does not check in generated sidecar files or generated write
receipts. Validation writes only under temp synthetic completed-run archive
directories.

## Boundary Checks

The review confirms:

- the adapter remains command-only;
- writes require explicit operator confirmation;
- validation uses synthetic completed-run archive directories;
- no real historical archive path was touched;
- no repo `decision_work/` sidecar directory was written;
- launch writes the expected allowed file set;
- deploy writes the expected allowed file set in blocked-state form;
- deploy preserves runtime and user-surface blocked state in
  `attachment_status.json`;
- `sidecar_write_receipt.json` keeps runtime wiring, archive hook edits, and
  resolver approval false;
- no-overwrite behavior blocks an existing `decision_work/` directory;
- missing operator confirmation is blocked;
- missing archive markers are blocked;
- repo paths are blocked;
- mismatched dry-run and packet inputs are blocked;
- privacy markers are blocked;
- resolver approval, proof, scoring, and action claims are blocked;
- receipt semantics are clear enough for a package gate.

## What Remains Missing

The real archive sidecar write adapter has not yet been packaged as a
capability. There is no manifest or package gate summarizing PR218 through
PR220.

There is still no runtime wiring, no archive-hook integration, no default-on
behavior, no resolver approval, no resolver refs marked usable, no automatic
arbitrary-run semantic interpretation, no queue worker, no model call path, no
product proof, no human validation, no answer-quality scoring, no
advice-correctness validation, and no action authorization.

## Decision Gate

Selected next step:

```text
proceed_to_real_archive_sidecar_write_package_gate
```

Recommended next PR:

```text
PR221 Real Archive Sidecar Write Package Gate v0
```

Reason:

Fresh launch and deploy synthetic completed-run writes preserve the intended
distinction between explicit command-only archive mutation and runtime
integration. They preserve source refs, uncertainty, privacy limits, deploy
blocking, custody flags, and non-claims. The adapter is ready for a package
gate before any operator runbook or broader demo.

Do not implement runtime hook integration, default-on behavior, resolver
approval, model calls, scoring, proof claims, user-surface readiness, or action
authorization from this review.
