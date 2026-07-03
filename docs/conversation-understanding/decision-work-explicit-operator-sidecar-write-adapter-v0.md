# Decision Work Explicit Operator Sidecar Write Adapter v0

Status: PR210 implementation
Date: 2026-07-03
Schema: `lolla.decision_work_explicit_operator_sidecar_write_receipt.v0`

## Purpose

PR210 implements the explicit operator sidecar write adapter planned by
[Decision Work Runtime Sidecar Write Contract](decision-work-runtime-sidecar-write-contract-v0.md).

This is the first actual write implementation in the Decision Work automatic
semantic supply path, but it is deliberately fixture-only. It writes
sidecar-shaped files only to an explicit caller-supplied controlled
fixture/output directory that passes conservative safety checks.

It does not write real historical archives, mutate existing Lolla case
folders, wire runtime, update the post-archive hook, approve resolver refs,
make writes automatic, call providers/models, score answer quality, claim
proof or advice correctness, or authorize action.

## CLI

```bash
python3 scripts/evals/write_decision_work_sidecar_explicit_operator.py \
  --sidecar-update-packet /tmp/decision_work_resolver_candidate_sidecar_update_launch.json \
  --dry-run-result /tmp/decision_work_sidecar_write_dry_run_launch.json \
  --target-sidecar-dir /tmp/decision_work_explicit_operator_sidecar_launch/decision_work \
  --out /tmp/decision_work_explicit_operator_sidecar_write_receipt_launch.json \
  --pretty
```

Only `explicit_operator_write` mode is supported in PR210.

The CLI writes a receipt JSON for accepted and blocked requests. A blocked
receipt does not create fixture sidecar files. A successful request writes the
allowed files only under the explicit target sidecar directory.

## Input Requirements

The adapter requires:

- a PR202 sidecar update packet:
  `lolla.decision_work_resolver_candidate_sidecar_update_packet.v0`;
- a PR206 dry-run result:
  `lolla.decision_work_sidecar_write_dry_run.v0`;
- a target directory named `decision_work`;
- a target directory under a safe temp/output root;
- matching sidecar update packet and dry-run source refs/statuses;
- no packet or dry-run blockers;
- no privacy, local-path, provider-text, authority, proof, scoring, or action
  claims.

## Statuses

The receipt supports:

- `write_completed_fixture_only`;
- `write_completed_blocked_state_fixture_only`;
- `blocked_target_path_unsafe`;
- `blocked_dry_run_missing`;
- `blocked_dry_run_not_matching_packet`;
- `blocked_packet_not_write_eligible`;
- `blocked_privacy_risk`;
- `blocked_authority_claim`;
- `blocked_real_archive_path`;
- `blocked_runtime_path`;
- `failed_closed`.

`write_completed_fixture_only` is the launch-beta success status. It means the
adapter wrote sidecar-shaped files to a controlled fixture/output directory. It
does not mean a real archive sidecar exists.

`write_completed_blocked_state_fixture_only` is the deploy-intake success
status. It preserves runtime blocking, user-surface blocking, and
agent-inspection-only state.

## Written Files

Successful fixture-only writes create exactly:

- `attachment_status.json`;
- `user_receipt.md`;
- `agent_handoff_packet.json`;
- `safe_supply_summary.json`;
- `sidecar_update_packet.json`;
- `sidecar_write_receipt.json`.

The write receipt records:

- source sidecar update packet ref;
- source dry-run result ref;
- target sidecar directory ref;
- fixture-only write status;
- files written;
- blocker reasons;
- mode;
- custody flags;
- privacy and uncertainty summaries;
- source refs;
- non-claims.

## Path Safety

The adapter refuses:

- relative target paths;
- targets not named `decision_work`;
- targets inside the repository;
- archive-looking paths;
- runtime-looking paths;
- paths outside safe temp/output roots;
- receipt outputs under `decision_work` or archive-looking paths.

Tests use temp directories only and do not check in generated sidecar files.

## Boundary

Every receipt keeps:

- `real_archive_mutated: false`;
- `historical_archive_mutated: false`;
- `runtime_wiring_changed: false`;
- `resolver_refs_approved: false`;
- `can_authorize_agent_action: false`;
- `can_authorize_automatic_action: false`;
- `can_be_used_as_quality_label: false`;
- `product_proof: false`;
- `human_validated: false`;
- `answer_quality_scored: false`;
- `advice_correctness_claimed: false`.

For successful fixture-only writes,
`actual_sidecar_write_performed` is true only in the fixture sense. The receipt
also records `fixture_only: true`.

## Case Behavior

`launch-public-enterprise-beta` writes a controlled fixture sidecar with:

```text
write_completed_fixture_only
```

`deploy-assisted-intake-routing` writes a controlled blocked-state fixture
sidecar with:

```text
write_completed_blocked_state_fixture_only
```

Deploy-intake remains blocked from runtime and user-surface use.

## Decision Gate

Selected next step:

```text
proceed_to_explicit_operator_sidecar_write_review
```

Recommended next PR:

```text
PR211 Explicit Operator Sidecar Write Review v0
```

Reason:

The adapter proves the mechanics of explicit operator writes against
controlled fixture/output directories without crossing into real historical
archives, runtime wiring, resolver approval, or automatic sidecar writes.

Do not implement real archive writes, runtime hook integration, resolver
approval, model calls, scoring, proof claims, or action authorization from this
adapter.
