# Decision Work Resolver Candidate Sidecar Update Packet Adapter v0

Status: PR202 implementation
Date: 2026-07-03

## Purpose

PR202 implements the deterministic adapter planned by
[Decision Work Resolver Candidate Sidecar Update Plan](decision-work-resolver-candidate-sidecar-update-plan-v0.md).

The adapter emits
`lolla.decision_work_resolver_candidate_sidecar_update_packet.v0` from a PR198
resolver-supply candidate packet.

This packet is offline and proposed only. It is not written to any
`decision_work/` sidecar, does not mutate archives, does not approve resolver
refs, does not wire runtime, does not call providers/models, does not score
answer quality, does not claim proof or advice correctness, and does not
authorize action.

## CLI

```bash
python3 scripts/evals/build_decision_work_resolver_candidate_sidecar_update_packet.py \
  --resolver-supply /tmp/decision_work_generated_read_resolver_supply_launch.json \
  --out /tmp/decision_work_resolver_candidate_sidecar_update_launch.json \
  --pretty
```

The CLI writes a JSON packet to the requested output path. It refuses output
paths that target a `decision_work/` directory because this adapter must not
write runtime sidecars.

## Statuses

The adapter supports:

- `ready_for_sidecar_update_packet`;
- `packet_with_runtime_block`;
- `deferred_missing_resolver_supply`;
- `blocked_resolver_supply_not_candidate`;
- `blocked_privacy_risk`;
- `blocked_authority_claim`;
- `blocked_runtime_write_attempt`;
- `requires_operator_repair`.

`ready_for_sidecar_update_packet` means the proposed packet can be inspected by
a future sidecar-update review. It does not mean a sidecar was written.

`packet_with_runtime_block` means the packet is still useful for inspection,
but runtime and user-surface blockers must travel forward.

## Case Behavior

`launch-public-enterprise-beta` can produce
`ready_for_sidecar_update_packet` from its
`ready_for_resolver_candidate_packet` resolver-supply input. The output keeps
`resolver_refs_approved`, `actual_sidecar_write_performed`,
`archive_mutated`, and `runtime_wiring_changed` false.

`deploy-assisted-intake-routing` produces `packet_with_runtime_block` from its
`candidate_packet_with_runtime_block` resolver-supply input. The output
preserves blocked runtime use, blocked user-surface use, and agent-inspection-
only status.

## Blockers

The adapter blocks or defers when:

- resolver supply is missing;
- resolver supply schema is unsupported;
- resolver supply is not a candidate packet;
- privacy markers or local absolute paths appear;
- resolver approval, sidecar write, archive mutation, runtime wiring,
  product-proof, human-validation, quality-label, advice-correctness, or
  action-authorization claims appear.

## Output Shape

The packet includes:

- source case;
- source resolver-supply ref;
- sidecar update packet status;
- blocker reasons;
- proposed sidecar state;
- proposed receipt state;
- proposed agent handoff state;
- runtime-use status;
- user-surface status;
- agent-inspection status;
- source refs;
- uncertainty summary;
- privacy summary;
- custody flags;
- non-claims;
- downstream allowed and forbidden fields.

Every output keeps these false:

- `resolver_refs_approved`;
- `actual_sidecar_write_performed`;
- `archive_mutated`;
- `runtime_wiring_changed`;
- `can_update_sidecar`;
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
proceed_to_sidecar_update_packet_review
```

Recommended next PR:

```text
PR203 Decision Work Sidecar Update Packet Review v0
```

Reason:

The adapter can prepare proposed sidecar update packets for launch-beta and
deploy-intake while preserving that no sidecar write, archive mutation,
resolver approval, runtime wiring, quality label, proof claim, or action
authorization occurred.

Do not implement actual sidecar writes, archive mutation, resolver approval,
runtime wiring, model calls, scoring, proof claims, or action authorization
from this adapter.

## Implemented Follow-Up

PR203 implements the review gate as
[Decision Work Sidecar Update Packet Review](decision-work-sidecar-update-packet-review-v0.md).
The review covers launch-beta and deploy-intake proposed packets, confirms the
adapter preserves the ready/runtime-block split, and keeps resolver approval,
actual sidecar writes, archive mutation, runtime wiring, proof claims, scoring,
and action authorization closed before any pre-write package gate.
