# Decision Work Controlled Archive Sidecar Write Fixture Adapter v0

Status: PR214 adapter
Date: 2026-07-04

Preceded by:
[Decision Work Controlled Archive Sidecar Write Fixture Plan](decision-work-controlled-archive-sidecar-write-fixture-plan-v0.md)

## Purpose

PR214 implements the deterministic adapter planned by PR213.

The adapter writes the PR209 allowed sidecar file set into a synthetic
archive-shaped fixture directory under an explicit safe temp/operator output
root. It is meant to prove archive-shaped layout mechanics before any real
archive-write planning.

This is still not real archive mutation. It does not write real completed-run
archives, mutate historical archives, edit the archive hook, wire runtime,
approve resolver refs, mark refs usable, call providers/models, score answer
quality, claim proof, claim human validation, validate advice correctness, or
authorize action.

## CLI

```bash
python3 scripts/evals/write_decision_work_controlled_archive_sidecar_fixture.py \
  --sidecar-update-packet /tmp/decision_work_resolver_candidate_sidecar_update_launch.json \
  --dry-run-result /tmp/decision_work_sidecar_write_dry_run_launch.json \
  --fixture-archive-dir /tmp/decision_work_archive_fixture_launch/archive/cases/example-run \
  --out /tmp/decision_work_controlled_archive_sidecar_write_fixture_launch.json \
  --pretty
```

The command writes generated fixture files under:

```text
<fixture-archive-dir>/decision_work/
```

Only synthetic fixture paths under safe temp/operator output roots are allowed.

## Output Schema

The adapter emits:

```text
lolla.decision_work_controlled_archive_sidecar_write_fixture.v0
```

The receipt records:

- source case;
- source sidecar update packet ref;
- source dry-run result ref;
- fixture archive dir ref;
- fixture sidecar dir ref;
- fixture write status;
- files written;
- blocker reasons;
- runtime and user-surface status;
- source refs;
- privacy and uncertainty summaries;
- custody flags;
- non-claims;
- downstream allowed and forbidden fields.

## Statuses

The adapter uses:

- `fixture_write_completed`;
- `fixture_write_completed_blocked_state`;
- `blocked_real_archive_path`;
- `blocked_repo_path`;
- `blocked_existing_archive_path`;
- `blocked_target_path_unsafe`;
- `blocked_packet_not_write_eligible`;
- `blocked_dry_run_missing`;
- `blocked_dry_run_mismatch`;
- `blocked_privacy_risk`;
- `blocked_authority_claim`;
- `failed_closed`.

## Expected Case Behavior

Launch-beta:

```text
fixture_write_completed
```

Deploy-intake:

```text
fixture_write_completed_blocked_state
```

Deploy-intake preserves runtime and user-surface blocked state. A blocked-state
fixture is still useful for inspection, but it is not runtime availability and
not a recommendation to deploy.

## Written Fixture Files

When a fixture write succeeds, the adapter writes exactly:

- `attachment_status.json`;
- `user_receipt.md`;
- `agent_handoff_packet.json`;
- `safe_supply_summary.json`;
- `sidecar_update_packet.json`;
- `sidecar_write_receipt.json`.

Generated fixture files are not checked into the repository.

## Path Safety

The adapter refuses:

- relative targets;
- repo paths;
- runtime-looking paths;
- real archive-looking paths without a fixture marker;
- existing historical archive paths;
- target dirs that point directly at `decision_work`;
- fixture dirs outside safe temp/operator output roots;
- fixture dirs whose existing `decision_work` folder contains untrusted files.

## Boundary Preservation

Every receipt keeps:

- `real_archive_mutated: false`;
- `historical_archive_mutated: false`;
- `archive_hook_changed: false`;
- `runtime_wiring_changed: false`;
- `resolver_refs_approved: false`;
- `product_proof: false`;
- `human_validated: false`;
- `answer_quality_scored: false`;
- `advice_correctness_claimed: false`;
- `agent_action_authorized: false`;
- `automatic_action_authorized: false`.

## Decision Gate

Selected gate:

```text
proceed_to_controlled_archive_sidecar_write_fixture_review
```

Recommended next PR:

```text
PR215 Controlled Archive Sidecar Write Fixture Review v0
```

Do not implement real archive writes from this adapter. PR215 should review the
synthetic fixture outputs and path-safety behavior before any package gate.

## Implemented Follow-Up

PR215 implements that review as
[Decision Work Controlled Archive Sidecar Write Fixture Review](decision-work-controlled-archive-sidecar-write-fixture-review-v0.md).
The review confirms the launch/deploy synthetic archive-shaped fixture outputs,
the deploy blocked-state boundary, unsafe target rejections, and the
no-real-archive, no-runtime, no-resolver-approval, no-proof, no-scoring, and
no-action-authority constraints.
