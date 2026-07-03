# Decision Work Sidecar Write Dry-Run Adapter v0

Status: PR206 implementation
Date: 2026-07-03

## Purpose

PR206 implements the default-off dry-run adapter planned by
[Decision Work Runtime Sidecar Write Plan](decision-work-runtime-sidecar-write-plan-v0.md).

The adapter emits `lolla.decision_work_sidecar_write_dry_run.v0` from a PR202
sidecar update packet. It simulates what a future sidecar write would consider
without writing `decision_work/`, mutating archives, approving resolver refs,
wiring runtime, calling providers/models, scoring answer quality, claiming
proof or advice correctness, or authorizing action.

Dry-run means:

- write a dry-run result JSON to an explicit `--out` path;
- optionally write preview files only under an explicit `--preview-dir`;
- reject archive-like or `decision_work/` output and preview paths;
- never modify the source packet;
- never claim that a sidecar write occurred.

## CLI

```bash
python3 scripts/evals/dry_run_decision_work_sidecar_write.py \
  --sidecar-update-packet /tmp/decision_work_resolver_candidate_sidecar_update_launch.json \
  --out /tmp/decision_work_sidecar_write_dry_run_launch.json \
  --preview-dir /tmp/decision_work_sidecar_write_preview_launch \
  --pretty
```

Only `dry_run_only` mode is supported.

The CLI returns a result JSON for accepted and blocked dry-run inputs. It
returns nonzero only when the requested output/preview operation itself is
unsafe or unwritable, such as attempting to write the result under a
`decision_work/` path.

## Statuses

The adapter supports:

- `dry_run_ready`;
- `dry_run_packet_with_runtime_block`;
- `blocked_not_sidecar_update_packet`;
- `blocked_privacy_risk`;
- `blocked_authority_claim`;
- `blocked_actual_write_attempt`;
- `blocked_archive_path`;
- `blocked_missing_required_fields`;
- `requires_operator_repair`.

`dry_run_ready` means the launch-beta sidecar update packet can produce a
dry-run result and optional preview files. It does not mean a sidecar was
written or that resolver refs were approved.

`dry_run_packet_with_runtime_block` means deploy-intake can produce a dry-run
preview while preserving runtime and user-surface blocking.

## Preview Files

When a safe preview directory is supplied and the input packet is dry-run
ready, the adapter writes these preview files under that directory only:

- `attachment_status.json`;
- `user_receipt.md`;
- `agent_handoff_packet.json`;
- `safe_supply_summary.json`;
- `sidecar_update_packet.json`.

These files are previews. They are not runtime sidecars, and they are not
written into an archive `decision_work/` directory.

## Case Behavior

`launch-public-enterprise-beta` produces `dry_run_ready` from its
`ready_for_sidecar_update_packet` input.

`deploy-assisted-intake-routing` produces
`dry_run_packet_with_runtime_block` from its `packet_with_runtime_block` input.
The dry-run result and preview preserve blocked runtime use, blocked
user-surface use, and agent-inspection-only status.

## Blockers

The adapter blocks when:

- the input is missing, unreadable, or not a sidecar update packet;
- required source refs are missing;
- privacy markers or local absolute paths appear;
- output or preview paths target archive-like or `decision_work/` paths;
- the packet claims actual sidecar write, archive mutation, runtime wiring,
  resolver approval, quality-label use, proof, human validation, advice
  correctness, or action authorization.

## Output Shape

The dry-run result includes:

- source case;
- source sidecar update packet ref;
- dry-run status;
- blocker reasons;
- would-write file names;
- preview files written;
- source refs;
- privacy summary;
- uncertainty summary;
- custody flags;
- non-claims;
- downstream allowed and forbidden fields.

Every output keeps these false:

- `actual_sidecar_write_performed`;
- `archive_mutated`;
- `runtime_wiring_changed`;
- `resolver_refs_approved`;
- `can_write_runtime_sidecar`;
- `can_write_decision_work_directory`;
- `can_mutate_archive`;
- `can_wire_runtime`;
- `can_be_used_as_quality_label`;
- `product_proof`;
- `human_validated`;
- `answer_quality_scored`;
- `advice_correctness_claimed`;
- `can_authorize_agent_action`;
- `can_authorize_automatic_action`.

## Decision Gate

Selected next step:

```text
proceed_to_sidecar_write_dry_run_review
```

Recommended next PR:

```text
PR207 Sidecar Write Dry-Run Review v0
```

Reason:

The adapter can show, in a temp/output-only preview, what a future write layer
would consider for launch-beta and deploy-intake while still preserving that
no sidecar write, archive mutation, resolver approval, runtime wiring, quality
label, proof claim, advice-correctness claim, or action authorization occurred.

Do not implement actual sidecar writes, archive mutation, resolver approval,
runtime wiring, model calls, scoring, proof claims, or action authorization
from this adapter.
