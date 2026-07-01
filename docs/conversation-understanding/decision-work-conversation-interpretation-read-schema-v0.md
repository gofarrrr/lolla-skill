# Decision Work Conversation Interpretation Read Schema v0

Status: PR133 schema contract
Date: 2026-07-01
Schema: `lolla.decision_work_conversation_interpretation_read.v0`

## Purpose

PR133 formalizes the shared shape that PR131 and PR132 used for tiny offline
conversation interpretation reads.

The machine-readable schema is:

- [Decision Work Conversation Interpretation Read JSON](decision-work-conversation-interpretation-read-v0.json)

This is a contract for future offline reads. It does not implement an
interpreter.

## Why This Schema Exists

PR131 tested one tiny read on `launch-public-enterprise-beta`.
PR132 tested the same read shape on `deploy-assisted-intake-routing`.

Both reads used the same small field subset, vocabularies, source-ref pattern,
privacy limits, human-review flags, non-claims, and unresolved-field handling.
Both also showed the same source-depth problem: checked-in-safe summaries can
support provisional reads of decision question and action consequence, but
starting direction, rejected options, and lost value remain partial or
insufficient-context without private source depth or human review.

That is enough to define a reusable read contract before running more reads.

## What The Read Captures

The read captures:

- read metadata;
- conservative custody flags;
- the PR130 packet reference and packet mode;
- the selected case;
- the interpretation scope;
- interpreted fields;
- unresolved fields;
- source limitations;
- brief implications;
- overclaim risk;
- a recommended next step;
- explicit non-claims.

It may also include `comparison_to_prior_reads` when a read is part of a small
sequence.

## Interpreted Field Shape

Every interpreted field requires:

- `field_group`
- `field_name`
- `status`
- `value`
- `uncertainty`
- `source_refs`
- `source_status`
- `interpretation_basis`
- `privacy_limit`
- `human_review_required`
- `could_feed_brief`
- `could_feed_agent_inspection`
- `must_not_be_used_as_quality_label`

This means a future read may add useful interpretation, but it must keep the
source trail and uncertainty attached to the interpretation.

## Vocabularies

Status values:

- `interpreted_provisional`
- `partial_interpretation`
- `insufficient_context`
- `not_interpreted`
- `not_applicable`

Uncertainty values:

- `low`
- `medium`
- `high`
- `insufficient_context`

Source-status values:

- `checked_in_safe_summary_only`
- `local_private_metadata_only`
- `local_private_context_not_checked_in`
- `mixed_safe_and_private_status`
- `missing_source`
- `unclear`

Interpretation-basis values:

- `checked_in_brief_and_reviews`
- `pr130_packet_source_refs`
- `local_private_metadata_status`
- `inferred_from_safe_summary`
- `insufficient_context`

## Custody Policy

The schema constrains reads to remain conservative:

- `human_validated: false`
- `product_proof: false`
- `model_calls: 0`
- `archive_mutated: false`
- `runtime_invoked: false`
- `skill_invoked: false`
- `answer_quality_scored: false`
- `agent_action_authorized: false`
- `raw_private_content_checked_in: false`
- `provider_text_checked_in: false`
- `semantic_read_is_provisional: true`

These fields are not decorative. They are the difference between a careful
offline interpretation read and an authority claim.

## How This Could Feed Briefs

A future Decision Work Brief enrichment pass may use this read to clarify:

- what the starting direction already seemed to contain;
- what the process appears to have sharpened;
- which options stayed live, became gated, or were abandoned;
- what possible lost value remains unresolved;
- what the final answer and brief do not prove.

That future pass is not implemented in PR133.

## How This Could Feed Agent Inspection

The read can also orient future agent inspection by preserving source status,
uncertainty, and human-review requirements.

It is not agent action authorization. The schema requires
`must_not_be_used_as_quality_label: true` on every interpreted field and keeps
`agent_action_authorized: false` in custody flags.

## Explicitly Not Implemented

PR133 does not:

- run `$lolla`;
- invoke the Lolla skill;
- call providers or model APIs from repo code;
- mutate archives;
- change runtime behavior;
- change prompts;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- add model-call code;
- add a broad judge;
- measure answer quality;
- create automatic labels;
- authorize agent action;
- claim product proof;
- add graph, memory, embedding, chunking, or GraphRAG work;
- create a dashboard;
- integrate the brief into runtime;
- implement an interpreter;
- implement a runtime extractor;
- change the live extraction schema;
- check in raw/private content.

## Non-Claims

This schema is not:

- human validation;
- product proof;
- answer-quality scoring;
- agent action authorization;
- runtime integration;
- runtime extraction;
- a correctness proof;
- a customer-facing brief;
- a quality label;
- evidence that clean artifacts mean good advice.

## Recommended Next Slice

Recommended next slice:

```text
PR134 Decision Work Conversation Interpretation Read Comparison v0
```

That slice should compare PR131 and PR132 through the shared schema and decide
whether to run another tiny read, test brief enrichment, patch the packet
builder, pause for human review, or simplify.

Follow-on status:

PR134 is now implemented as the comparison gate:

- [Decision Work Conversation Interpretation Read Comparison v0](decision-work-conversation-interpretation-read-comparison-v0.md)
- `reviews/codex-assisted/decision-work-conversation-interpretation-read-comparison-v0/review.json`
- `tests/test_decision_work_conversation_interpretation_read_comparison.py`

PR134 compares the launch-beta and intake-routing reads, finds stable useful
fields for action consequence, thresholds, evidence gates, useful friction, and
non-proof boundaries, keeps lost value and starting direction source-limited,
and chooses `proceed_to_brief_enrichment_test`.

Recommended next slice:

```text
PR135 Decision Work Brief Interpretation Enrichment Test v0
```
