# Decision Trail Specialist Contracts v0

Status: PR90 docs/schema contract
Date: 2026-06-29
Schema: `lolla.decision_trail_specialist_contracts.v0`

## Purpose

PR90 defines the contract layer for narrow offline Decision Trail
interpretation specialists.

PR89 decided that the current Decision Trail shell is useful for custody,
source refs, missingness, redaction/private availability, and non-claims, but
too sparse for the full answer-plus-process product. The missing fields are
messy interpretation fields. They should not be filled by deterministic rules.

PR90 therefore defines typed contracts for future bounded LLM specialist reads.
It does not run those specialists.

## What This Is Not

PR90 is not:

- a packet builder;
- a specialist review batch;
- fan-in execution;
- runtime integration;
- a local-private mode implementation;
- an LLM judge;
- answer-quality scoring;
- automatic labeling;
- agent action authorization;
- graph DB, memory, embeddings, chunking, or GraphRAG;
- proof that Lolla improved a decision.

The contracts define what a future output must look like before any future
agent, reviewer, or report builder is allowed to consume it.

## Contract Family

The companion schema is:

```text
docs/conversation-understanding/decision-trail-specialist-contracts-v0.json
```

The schema version is:

```text
lolla.decision_trail_specialist_contracts.v0
```

It defines exactly four specialist roles:

- `conversation_shape_reader`
- `likely_action_reader`
- `friction_lost_value_reader`
- `conservative_fan_in_reader`

No extra specialist role is required in PR90.

## Runtime Boundary

The Decision Trail specialist lane is offline and downstream.

```text
Lolla runtime:
  produces revised answer and completed artifacts

Decision Trail shell:
  preserves custody, source refs, missingness, redaction, and non-claims

Future specialist lane:
  interprets messy decision-story fields under typed contracts
```

PR90 does not invoke `$lolla`, invoke the Lolla skill, call providers, mutate
archives, change prompts, change runtime behavior, touch `SKILL.md`, or touch
`scripts/skill/*`.

## Shared Contract Requirements

Every future specialist output must include:

- specialist role;
- contract version;
- input mode;
- allowed input refs;
- read status;
- source refs;
- source status;
- uncertainty;
- evidence strength;
- fields;
- limitations;
- non-claims;
- boundary metadata.

The point is not to make LLM interpretation authoritative. The point is to make
it inspectable.

## Input Modes

PR90 defines three modes:

- `checked_in_safe_mode`
- `local_private_mode`
- `future_runtime_mode_not_implemented`

`checked_in_safe_mode` excludes raw transcripts, raw memos, raw revised
answers, provider text, private ledgers, local absolute paths, secrets, and
private local content.

`local_private_mode` was vocabulary only in PR90. PR95 now implements it for
the Decision Trail specialist packet builder only:

- [Decision Trail Local-Private Packet Mode v0](decision-trail-local-private-packet-mode-v0.md)

That implementation remains offline, explicit, unsafe for commit by default,
and separate from runtime integration or specialist-output generation.

`future_runtime_mode_not_implemented` reserves vocabulary only. It is not an
approval for runtime integration.

## Specialist Roles

### Conversation Shape Reader

Purpose:

Identify the shape of the messy conversation for Decision Trail use.

Covered fields:

- decision question;
- live options;
- option status;
- constraints;
- stakeholders;
- values or priorities;
- assistant influence;
- dropped threads;
- unresolved questions;
- uncertainty.

This role should preserve ambiguity. It must not collapse thin context into a
confident interpretation.

### Likely Action Reader

Purpose:

Identify likely next actions before and after Lolla without claiming those
actions are good.

Covered fields:

- vanilla likely next action;
- revised likely next action;
- action delta;
- threshold delta;
- sequence delta;
- evidence-gate delta;
- stop-rule delta;
- uncertainty.

This role must be allowed to say `unclear`. It must not pretend to know what
the user truly would have done.

### Friction And Lost Value Reader

Purpose:

Separate useful friction from noisy friction and preserve lost value.

Covered fields:

- useful friction;
- noisy friction;
- missing friction;
- lost value;
- value-overwrite risk;
- momentum or simplicity loss;
- overcaution or diligence theater;
- uncertainty.

This role exists because a more cautious revised answer is not automatically a
better decision answer.

### Conservative Fan-In Reader

Purpose:

Preserve disagreement and produce a conservative Decision Trail interpretation
summary without voting, scoring, or judging answer quality.

Covered fields:

- areas of agreement;
- disagreements preserved;
- high-uncertainty fields;
- fields ready for report;
- fields not ready for report;
- human follow-up questions;
- overtrust risks;
- next review priority.

Fan-in must not become majority rule. It must not turn specialist agreement
into correctness.

## Fan-In Non-Rule

The conservative fan-in contract forbids:

- voting;
- averaging;
- scoring;
- certification;
- approval;
- winner selection;
- correctness from agreement;
- decision-quality claims.

It should preserve tensions such as:

- structural delta looks strong but lost value is unresolved;
- likely action changed but values/priorities are unclear;
- useful friction may also create momentum loss;
- checked-in safe context is too thin to read assistant influence.

## Boundary Metadata

Every future contract-conforming output must preserve lower-claim boundary
metadata:

- `human_validated: false`
- `ground_truth: false`
- `judge_calibration_eligible: false`
- `product_proof: false`
- `answer_quality_scored: false`
- `agent_action_authorized: false`
- `model_calls: 0` for docs/schema fixtures
- `archive_mutated: false`
- `runtime_invoked: false`
- `skill_invoked: false`
- `automatic_labels_created: false`
- `raw_private_content_included: false` for checked-in safe fixtures

Future local-private work may have different content-read flags, but it must
still be explicit and must not be checked in if it contains private content.

## Relationship To PR87 And PR88

PR87 exports the deterministic shell.

PR88 showed the shell is useful but sparse. It leaves these fields unfilled:

- vanilla likely next action;
- revised likely next action;
- option map;
- stakeholders;
- values or priorities;
- assistant influence;
- useful/noisy friction;
- lost value.

PR90 defines the contracts that may later fill those fields through bounded
LLM interpretation.

## Relationship To PR91

PR91 implements the first packet-builder slice against these contracts:

[`Decision Trail Specialist Packet Builder v0`](decision-trail-specialist-packet-builder-v0.md)

It builds checked-in-safe input scaffolds for the four PR90 roles without model
calls, specialist outputs, fan-in execution, runtime integration, archive
mutation, or product-proof claims.

## Next Step

PR92, PR93, PR94, PR95, PR96, PR97, and PR98 have now exercised the contracts
through traps, a dry run, local-private packet mode, packet smoke review, a
one-case local-private specialist-output pilot, and a pilot review. The latest
review is:

[`Decision Trail Specialist Output Pilot Review v0`](decision-trail-specialist-output-pilot-review-v0.md)

PR97 shows the four-role contract surface can be filled from one
operator-selected local-private packet, but it does not prove the contracts are
final or suitable for a broad batch. PR98 keeps the useful signal and requires
contract changes before reuse.

The next recommended PR is:

**PR99 Decision Trail Specialist Contract And Packet Patch v0**

PR99 should add or clarify the contract fields surfaced by PR98:

- `vanilla_overlap_read`;
- `lost_value_severity_read`;
- `assistant_influence_source_status`;
- `source_scope_and_truncation_impact`;
- `downgrade_triggers`;
- `not_ready_reason`.

It should still avoid model calls, runtime integration, archive mutation,
answer-quality measurement, automatic labels, and product-proof claims.
