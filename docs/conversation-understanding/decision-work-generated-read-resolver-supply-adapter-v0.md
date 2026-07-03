# Decision Work Generated Read Resolver Supply Adapter v0

Status: PR198 implementation
Date: 2026-07-03

## Purpose

PR198 implements the deterministic generated-read resolver-supply adapter
planned by
[Decision Work Generated Read Resolver Supply Plan](decision-work-generated-read-resolver-supply-plan-v0.md).

The adapter emits
`lolla.decision_work_generated_read_resolver_supply.v0` candidate packets from:

- generated read JSON;
- PR182 intake result JSON;
- PR186 generated-read brief supply JSON;
- PR187 generated-read rendered brief Markdown;
- PR192 generated-read triage supply JSON;
- PR193 or PR195 generated triage JSON;
- optional queue item or prompt packet refs.

It validates and normalizes refs, statuses, route categories, source refs,
uncertainty, privacy, custody flags, and non-claims. It does not approve
resolver refs, update runtime sidecars, wire runtime, call providers/models,
generate triage, score answer quality, claim semantic correctness, claim
product proof, claim human validation, validate advice correctness, or
authorize action.

## CLI

```bash
python3 scripts/evals/build_decision_work_generated_read_resolver_supply.py \
  --read reviews/codex-assisted/decision-work-operator-codex-generated-read-pilot-v0/read.json \
  --intake reviews/codex-assisted/decision-work-operator-codex-generated-read-pilot-v0/intake.json \
  --brief-supply /tmp/decision_work_generated_read_brief_supply_launch.json \
  --rendered-brief docs/conversation-understanding/decision-work-generated-read-rendered-launch-public-enterprise-beta-v0.md \
  --triage-supply /tmp/decision_work_generated_read_triage_supply_launch.json \
  --triage reviews/codex-assisted/decision-work-generated-read-triage-generation-pilot-v0/triage.json \
  --out /tmp/decision_work_generated_read_resolver_supply_launch.json \
  --pretty
```

The CLI writes a result JSON for ready, deferred, and blocked states. Rejected
inputs do not cause resolver approval; they produce blocked/deferred status in
the packet.

## Statuses

The adapter supports:

- `ready_for_resolver_candidate_packet`;
- `candidate_packet_with_runtime_block`;
- `deferred_missing_triage`;
- `deferred_missing_rendered_brief`;
- `deferred_missing_brief_supply`;
- `blocked_intake_not_accepted`;
- `blocked_triage_missing`;
- `blocked_privacy_risk`;
- `blocked_authority_claim`;
- `requires_operator_repair`.

`ready_for_resolver_candidate_packet` means future resolver review may inspect
the candidate packet. It does not mean resolver refs are approved.

`candidate_packet_with_runtime_block` means a candidate packet can still be
prepared, but triage routes such as `agent_inspection_only`,
`not_ready_for_user_surface`, domain/compliance review, or runtime blockers
must travel forward. This is the expected deploy-intake pattern.

## Output Shape

The output includes:

- source case and source refs;
- resolver supply status and blocker reasons;
- safe ref candidates;
- evidence-only refs;
- route summary;
- runtime-use status;
- user-surface status;
- agent-inspection status;
- required operator review;
- source-ref summary;
- uncertainty summary;
- privacy summary;
- custody flags;
- non-claims;
- downstream allowed/forbidden flags.

Safe ref candidates are refs and statuses only. They cannot be read as
approved refs, runtime refs, user-surface readiness, proof, or quality labels.

## Case Behavior

`launch-public-enterprise-beta` can produce
`ready_for_resolver_candidate_packet`. Runtime sidecar update still remains
blocked by the packet's downstream flags and route summary. The candidate is
for future resolver review only.

`deploy-assisted-intake-routing` produces
`candidate_packet_with_runtime_block` because the generated triage read carries
domain/compliance review, agent-inspection-only, user-surface blocking, and
runtime attachment blocking routes. The packet preserves those blockers rather
than flattening them into approval.

## Blockers

The adapter blocks or defers when:

- intake is not accepted;
- brief supply is missing or not ready;
- rendered brief is missing;
- triage supply is missing or not ready;
- triage read is missing or malformed;
- source refs are missing;
- uncertainty is missing;
- privacy markers or local absolute paths appear;
- authority, proof, scoring, resolver-approval, sidecar-update, model-call, or
  action-authorization claims appear.

## Decision Gate

Selected next step:

```text
proceed_to_generated_read_resolver_supply_review
```

Recommended next PR:

```text
PR199 Decision Work Generated Read Resolver Supply Review v0
```

Reason:

The deterministic adapter can prepare resolver-candidate packets for both
launch-beta and deploy-intake while preserving that candidate supply is not
resolver approval, runtime sidecar permission, user-surface readiness, product
proof, scoring, advice correctness, or action authorization.

Do not implement resolver approval, runtime sidecar updates, runtime wiring,
model calls, scoring, proof claims, or action authorization from this adapter.
