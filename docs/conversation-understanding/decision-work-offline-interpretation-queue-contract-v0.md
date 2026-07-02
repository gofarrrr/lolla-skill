# Decision Work Offline Interpretation Queue Contract v0

Status: PR179 queue contract
Date: 2026-07-03
Schema: `lolla.decision_work_offline_interpretation_queue_contract.v0`

## Purpose

PR179 defines the contract for an offline interpretation queue item and queue
result in the Decision Work automatic semantic supply path.

This is the first slice after the
[Decision Work Automatic Semantic Supply PRD](decision-work-automatic-semantic-supply-prd-v0.md).
It names the object that represents a completed Lolla run needing semantic
Decision Work supply after archive completion.

This PR is docs, schema, and tests only. It does not implement a queue runner,
packet builder, provider worker, generated interpretation read, brief
generation, triage read, runtime hook update, or sidecar update.

## Product Boundary

Runtime-Attached Internal v1 can attach safe Decision Work refs when those refs
already exist. It does not automatically create those refs for arbitrary new
completed runs.

The automatic semantic supply path should be:

```text
completed archive
-> deterministic packet
-> offline interpretation queue
-> bounded LLM/Codex interpretation read
-> deterministic validation
-> Decision Work Brief render
-> enrichment
-> triage read
-> resolver-approved refs
-> runtime sidecar update or deferred/blocked state
```

PR179 defines only the `offline interpretation queue` contract in that chain.
The runtime hook remains a sidecar writer and status carrier, not a semantic
interpreter.

## Machine-Readable Contract

The machine-readable contract is:

- [Decision Work Offline Interpretation Queue Contract JSON](decision-work-offline-interpretation-queue-contract-v0.json)

It defines:

- queue item shape;
- queue result shape;
- queue modes;
- queue statuses;
- input refs;
- output refs;
- allowed source modes;
- privacy modes;
- allowed requested interpretation fields;
- blocked/deferred reasons;
- custody flags;
- validation requirements;
- non-claims.

## Queue Item Shape

A future queue item uses:

```text
lolla.decision_work_offline_interpretation_queue_item.v0
```

Required fields:

- `schema_version`;
- `queue_metadata`;
- `queue_mode`;
- `source_run_ref`;
- `source_packet_ref`;
- `allowed_source_refs`;
- `requested_interpretation_fields`;
- `privacy_mode`;
- `custody_flags`;
- `queue_status`;
- `blocked_or_deferred_reasons`;
- `output_destinations`;
- `validation_requirements`;
- `downstream_refs`;
- `non_claims`.

The item may carry refs, status, missingness, privacy policy, and requested
fields. It must not fill semantic interpretation fields.

## Queue Result Shape

A future queue result uses:

```text
lolla.decision_work_offline_interpretation_queue_result.v0
```

Required fields:

- `schema_version`;
- `queue_item_ref`;
- `status`;
- `produced_refs`;
- `validation_summary`;
- `blocked_reasons`;
- `privacy_summary`;
- `custody_flags`;
- `non_claims`.

The result may point to produced refs only after a later PR validates an
externally supplied or bounded generated interpretation read. PR179 produces no
such read.

## Queue Modes

Allowed modes:

- `disabled`;
- `checked_in_safe_metadata_only`;
- `local_private_operator`;
- `operator_codex_prompt_packet`;
- `external_interpretation_read_intake`;
- `future_provider_worker_not_implemented`.

`future_provider_worker_not_implemented` is reserved vocabulary only. It does
not authorize provider calls from repo code.

## Queue Statuses

Allowed statuses:

- `not_requested`;
- `queued`;
- `running`;
- `completed`;
- `blocked_missing_packet`;
- `blocked_privacy_risk`;
- `blocked_schema_invalid`;
- `failed_validation`;
- `requires_local_private_operator`;
- `unsafe_to_export`;
- `cancelled`.

Statuses describe custody and readiness. They are not quality labels, approval,
or proof of advice correctness.

## Input Contracts

PR179 links the queue item to existing checked-in-safe contracts:

- [Decision Work Conversation Interpretation Offline Packet](decision-work-conversation-interpretation-offline-packet-v0.md)
- [Decision Work Conversation Interpretation Read Schema](decision-work-conversation-interpretation-read-schema-v0.md)
- [Decision Work Brief Runtime Safe Supply Resolver Contract](decision-work-brief-runtime-safe-supply-resolver-contract-v0.md)

The source packet schema is:

```text
lolla.decision_work_conversation_interpretation_packets.v0
```

The future target read schema is:

```text
lolla.decision_work_conversation_interpretation_read.v0
```

## Requested Interpretation Fields

The contract allows a future queue item to request a bounded subset of the
fields already proven useful in the three curated reads:

- `decision_question`;
- `likely_starting_direction`;
- `revised_direction_or_action_consequence`;
- `decision_thresholds`;
- `evidence_gates`;
- `useful_friction`;
- `what_the_final_answer_does_not_prove`.

Every requested field must preserve source refs, uncertainty, privacy limits,
and `must_not_be_used_as_quality_label: true`.

## Privacy Policy

Checked-in-safe queue items may contain refs, statuses, missingness, and
non-claims. They must not contain:

- raw conversation text;
- raw revised-answer text;
- raw memo text;
- provider text;
- private ledger content;
- secrets;
- local absolute paths.

Local-private operator mode may record that private context is required, but it
still must not export private content into checked-in artifacts.

## Validation Requirements

Before a queue item can feed a later prompt packet, generated read intake, or
resolver-approved sidecar update, validation must confirm:

- supported source packet schema;
- relative or sanitized source refs;
- allowed requested fields;
- allowed privacy mode;
- no raw/private content;
- no provider text;
- no private ledgers;
- no local absolute paths;
- no secrets;
- conservative custody flags;
- explicit non-claims;
- no action authorization;
- no answer-quality scoring;
- no product-proof or human-validation claim.

## Custody Flags

The contract keeps conservative defaults:

- `runtime_invoked: false`;
- `skill_invoked: false`;
- `archive_mutated: false`;
- `model_calls: 0`;
- `human_validated: false`;
- `product_proof: false`;
- `answer_quality_scored: false`;
- `agent_action_authorized: false`;
- `automatic_action_authorized: false`;
- `raw_private_content_included: false`.

## Explicit Non-Claims

PR179 does not claim:

- product proof;
- human validation;
- answer-quality scoring;
- advice correctness;
- proof that Lolla improved the decision;
- agent or automatic action authorization;
- direct runtime interpretation;
- runtime model calls;
- customer readiness.

## Decision Gate

Selected next step:

```text
proceed_to_queue_packet_builder
```

Recommended next PR:

```text
PR180 Offline Interpretation Queue Packet Builder v0
```

Reason:

The contract is narrow enough for the next deterministic slice: a queue packet
builder that can emit checked-in-safe queue items from completed run refs and
existing PR130 packet refs without filling semantic fields or calling models.
