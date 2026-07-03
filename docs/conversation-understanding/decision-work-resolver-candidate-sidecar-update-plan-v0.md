# Decision Work Resolver Candidate Sidecar Update Plan v0

Status: PR201 plan gate
Date: 2026-07-03

## Purpose

PR201 plans how a generated-read resolver-supply candidate packet could
eventually produce a runtime sidecar update packet without actually writing a
sidecar, approving resolver refs, wiring runtime, or mutating archives.

This is a plan/gate only. It does not implement sidecar update packet code,
write `decision_work/`, update archive sidecars, approve resolver refs, wire
runtime behavior, call providers/models, create workers, claim semantic
correctness, score answer quality, claim product proof, claim human
validation, validate advice correctness, or authorize action.

Plainly: a sidecar update packet is a proposed offline packet, not an actual runtime sidecar update.

Source artifacts reviewed:

- [Decision Work Automatic Semantic Supply Pre-Runtime v1 Package Gate](decision-work-automatic-semantic-supply-pre-runtime-v1-package-gate-v0.md);
- [Decision Work Generated Read Resolver Supply Review](decision-work-generated-read-resolver-supply-review-v0.md);
- [Decision Work Generated Read Resolver Supply Adapter](decision-work-generated-read-resolver-supply-adapter-v0.md);
- [Decision Work Generated Read Resolver Supply Plan](decision-work-generated-read-resolver-supply-plan-v0.md).

## Sidecar Update Packet

A sidecar update packet is an offline, inspectable, proposed packet that
summarizes what a future runtime sidecar update could consider.

It may preserve:

- resolver-supply candidate status;
- source resolver-supply ref;
- source generated-read, intake, brief-supply, rendered-brief, triage-supply,
  and generated-triage refs;
- proposed sidecar state;
- proposed receipt state;
- proposed agent handoff state;
- runtime-use status;
- user-surface status;
- agent-inspection status;
- source refs;
- uncertainty and privacy summaries;
- custody flags;
- non-claims;
- blocker/defer reasons.

It explicitly does not mean:

- resolver refs are approved;
- resolver refs are marked usable;
- `decision_work/` was written;
- an archive sidecar was mutated;
- runtime was wired;
- the generated-read chain is semantically correct;
- the brief is customer-ready;
- triage is a quality label;
- an agent or automatic system may act.

## Launch-Beta Behavior

`launch-public-enterprise-beta` can produce
`ready_for_sidecar_update_packet` when its resolver-supply candidate status is
`ready_for_resolver_candidate_packet`.

That status still does not write a sidecar. It means a future review may
inspect the proposed packet. The packet must keep resolver refs unapproved,
actual sidecar write false, archive mutation false, runtime wiring false, and
action authorization false.

## Deploy-Intake Behavior

`deploy-assisted-intake-routing` should produce
`packet_with_runtime_block` because its resolver-supply status is
`candidate_packet_with_runtime_block`.

The packet may still be useful for inspection, but it must preserve:

- runtime use blocked;
- user-surface use blocked;
- agent inspection only;
- domain review requirement;
- legal/compliance review requirement;
- no sidecar write;
- no resolver approval;
- no deployment or action authorization.

## Planned Packet Statuses

Future sidecar update packet code should support:

- `ready_for_sidecar_update_packet`;
- `packet_with_runtime_block`;
- `deferred_missing_resolver_supply`;
- `blocked_resolver_supply_not_candidate`;
- `blocked_privacy_risk`;
- `blocked_authority_claim`;
- `blocked_runtime_write_attempt`;
- `requires_operator_repair`.

## Allowed Inputs

The future adapter may consume:

- PR198 resolver-supply candidate packet JSON;
- optional rendered-brief ref;
- optional generated-triage ref;
- optional source resolver-supply packet ref.

The adapter must validate that the resolver-supply packet is a candidate packet
and that its downstream flags still forbid resolver approval, sidecar writes,
runtime wiring, quality-label use, proof claims, and action authorization.

## Allowed Packet Fields

Allowed sidecar update packet fields are:

- `schema_version`;
- `source_case`;
- `source_resolver_supply_ref`;
- `sidecar_update_packet_status`;
- `blocker_reasons`;
- `proposed_sidecar_state`;
- `proposed_receipt_state`;
- `proposed_agent_handoff_state`;
- `runtime_use_status`;
- `user_surface_status`;
- `agent_inspection_status`;
- `resolver_refs_approved: false`;
- `actual_sidecar_write_performed: false`;
- `archive_mutated: false`;
- `runtime_wiring_changed: false`;
- `source_refs`;
- `uncertainty_summary`;
- `privacy_summary`;
- `custody_flags`;
- `non_claims`;
- `downstream_allowed`;
- `downstream_forbidden`.

## Forbidden Fields

The packet must block or refuse to emit any state that claims:

- resolver ref approval;
- resolver refs marked usable;
- actual sidecar write;
- archive mutation;
- runtime wiring;
- default-on runtime behavior;
- product proof;
- human validation;
- answer-quality score;
- advice correctness;
- proof that Lolla improved the decision;
- customer readiness;
- safe-to-act or safe-to-deploy;
- agent action authorization;
- automatic action authorization.

## Deterministic Allowances

A future adapter may:

- validate the resolver-supply packet schema;
- read explicit resolver-supply status;
- copy safe refs and summaries;
- copy blocker/defer reasons;
- preserve runtime, user-surface, and agent-inspection state;
- derive packet status from explicit resolver-supply status only;
- preserve source refs, uncertainty, privacy limits, custody flags, and
  non-claims;
- block attempted runtime writes or authority claims.

It must not:

- approve resolver refs;
- update sidecars;
- write `decision_work/`;
- mutate archives;
- wire runtime;
- infer new semantic meaning;
- judge answer quality;
- judge advice correctness;
- call providers/models;
- authorize action.

## Decision Gate

Selected next step:

```text
proceed_to_resolver_candidate_sidecar_update_packet_adapter
```

Recommended next PR:

```text
PR202 Resolver Candidate Sidecar Update Packet Adapter v0
```

Reason:

The PR200 package provides a stable pre-runtime chain ending in resolver-supply
candidate packets. The next safe implementation is a deterministic offline
adapter that turns those candidates into proposed sidecar update packets while
still forbidding actual sidecar writes, archive mutation, resolver approval,
runtime wiring, proof claims, scoring, and action authorization.

Do not write sidecars, mutate archives, approve resolver refs, wire runtime,
call models, score answer quality, claim proof, or authorize action from this
plan.

## Implemented Follow-Up

PR202 implements this plan as
[Decision Work Resolver Candidate Sidecar Update Packet Adapter](decision-work-resolver-candidate-sidecar-update-packet-adapter-v0.md).
The adapter emits
`lolla.decision_work_resolver_candidate_sidecar_update_packet.v0` from PR198
resolver-supply candidate packets. It can prepare launch-beta and deploy-intake
offline packet artifacts while preserving that no actual sidecar write, archive
mutation, resolver approval, runtime wiring, quality label, proof claim, or
action authorization occurred.
