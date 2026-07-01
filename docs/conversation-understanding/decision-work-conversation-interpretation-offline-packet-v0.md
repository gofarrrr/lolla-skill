# Decision Work Conversation Interpretation Offline Packet v0

Status: PR130 offline packet builder
Date: 2026-07-01
Schema: `lolla.decision_work_conversation_interpretation_packets.v0`

## Purpose

PR130 builds a safe dossier for future conversation interpretation.

PR128 defined the target contract:

- [Decision Work Conversation Interpretation Contract v0](decision-work-conversation-interpretation-contract-v0.md)
- [Decision Work Conversation Interpretation Contract JSON](decision-work-conversation-interpretation-contract-v0.json)

PR129 reviewed that contract against the current artifact and packet surface and
selected:

```text
build_offline_interpretation_packet
```

PR130 implements that packet layer. It does not interpret the conversation.

## What The Packet Is

The packet answers:

> If a future LLM or human reviewer tries to interpret the PR128 fields, what
> source refs, source status, privacy limits, and unanswered questions should
> they receive?

It records:

- the completed run identity;
- the PR128 contract reference;
- current completed-run artifact availability;
- optional Decision Work Brief packet, brief, rendered brief, receipt, Decision
  Trail, and Product Delta refs;
- the PR128 field groups and field policies;
- source refs or missing/private/redacted status for each field;
- future interpretation questions;
- custody flags and non-claims.

It does not fill field values.

## Relationship To Earlier Layers

The current offline stack is:

```text
completed Lolla run artifacts
-> PR115 Decision Work Brief packet
-> PR128 conversation interpretation contract
-> PR130 conversation interpretation offline packet
-> future bounded LLM or human interpretation read
-> future Decision Work Brief updates or review
```

PR115 prepares packets for the `lolla.decision_work_brief.v0` brief sections.
PR130 prepares packets for the richer PR128 conversation interpretation contract.

The two packet layers are related but not the same:

- PR115 asks what a future brief writer needs.
- PR130 asks what a future conversation interpreter needs before a brief writer
  can safely use richer conversation meaning.

## Schema Shape

PR130 emits:

```text
lolla.decision_work_conversation_interpretation_packets.v0
```

Top-level fields include:

- `schema_version`
- `packet_metadata`
- `mode`
- `source_run`
- `source_contract`
- `source_inventory`
- `custody_flags`
- `contract_field_groups`
- `future_interpretation_tasks`
- `required_future_output`
- `non_claims`

The required future output points to:

```text
lolla.decision_work_conversation_interpretation_read.v0
```

That future read does not exist yet.

## Field Group Handling

The packet carries every PR128 field group:

- decision shape;
- options and paths;
- conversation process;
- provided context and evidence;
- stakeholders and values;
- constraints and unknowns;
- audit pressure and change;
- losses and overcorrection;
- evidence and custody;
- handoff for the brief;
- handoff for agent inspection.

For every field, the packet records:

- field name and purpose;
- owner from the PR128 contract;
- whether interpretation is required;
- what deterministic code is allowed to preserve;
- privacy handling;
- checked-in-safe and local-private policy;
- whether the field may feed a brief or agent inspection;
- source refs and source status;
- future interpretation question;
- that the field value is not filled;
- that it must not be used as a quality label.

The packet builder may classify source and packet status. It must not decide
what the conversation meant.

## Modes

### `checked_in_safe`

This is the default mode.

It reads safe structured metadata and records source refs/status only. Raw or
private artifacts are not read or copied. The output may be checked in only if
it passes the normal privacy and boundary scans.

In this mode:

- `checked_in_safe: true`
- `raw_private_content_included: false`
- `provider_text_included: false`
- `semantic_fields_filled: false`
- `model_calls: 0`
- `archive_mutated: false`

### `local_private_metadata`

This mode remains metadata/status only.

It may be used by an operator to record that local/private context exists and
should be inspected later, but it still does not copy raw conversation text,
raw revised answer text, raw memo text, provider text, private ledgers, local
absolute paths, or secrets.

In this mode:

- `checked_in_safe: false`
- `requires_operator_review_before_share: true`
- `raw_private_content_included: false`
- `provider_text_included: false`
- `semantic_fields_filled: false`

PR130 intentionally does not add an include-text mode.

## Usage

Build a checked-in-safe packet:

```bash
python3 scripts/evals/build_decision_work_conversation_interpretation_packets.py \
  --run-dir <completed-run-dir> \
  --contract docs/conversation-understanding/decision-work-conversation-interpretation-contract-v0.json \
  --out /tmp/decision_work_conversation_interpretation_packets.json \
  --pretty
```

Link optional checked-in-safe or temporary metadata artifacts:

```bash
python3 scripts/evals/build_decision_work_conversation_interpretation_packets.py \
  --run-dir <completed-run-dir> \
  --decision-work-brief-packet /tmp/decision_work_brief_packets.json \
  --decision-work-brief reviews/codex-assisted/<review>/brief.json \
  --rendered-decision-work-brief docs/conversation-understanding/<rendered-brief>.md \
  --decision-work-receipt /tmp/decision_work_receipt.json \
  --decision-trail-report /tmp/decision_trail_report.json \
  --product-delta-report /tmp/product_delta_report.json \
  --out /tmp/decision_work_conversation_interpretation_packets.json \
  --pretty
```

Build a local-private metadata packet:

```bash
python3 scripts/evals/build_decision_work_conversation_interpretation_packets.py \
  --run-dir <completed-run-dir> \
  --mode local_private_metadata \
  --out /tmp/decision_work_conversation_interpretation_packets_private_metadata.json \
  --pretty
```

The CLI rejects output paths inside the run directory.

## What It Reads

PR130 reuses the PR115 metadata-only packet builder to inspect current
completed-run source availability.

The preferred structured artifacts are:

- `agent_result.json`
- `evaluation.json`
- `reasoning_trace.json`
- `extraction.json`
- `result.json`
- `memo_note.json`
- `graph_survival_report.json`

It may also reference optional metadata-only files supplied by path:

- a PR115 Decision Work Brief packet;
- a `lolla.decision_work_brief.v0` JSON object;
- a rendered Decision Work Brief Markdown file;
- a Decision Work Receipt JSON;
- a Decision Trail report JSON;
- a Product Delta report or review JSON.

Raw/private artifacts such as `conversation.txt`, `revised.txt`, `memo.md`,
`live_transcript.txt`, `operator.log`, private tables, and private ledgers are
not copied into PR130 outputs.

## What It Does Not Do

PR130 does not:

- run `$lolla`;
- invoke the Lolla skill;
- call providers or models;
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
- integrate the brief into runtime;
- implement a new runtime extractor;
- change the live extraction schema;
- fill PR128 fields semantically;
- infer live options, lost value, assistant influence, user values, or answer
  quality;
- check in raw/private content.

## Non-Claims

The packet is not:

- a conversation interpretation;
- a Decision Work Brief;
- product proof;
- human validation;
- answer-quality measurement;
- a judge;
- agent action authorization;
- evidence that clean artifacts mean good advice;
- runtime extraction;
- permission to attach Decision Work Briefs to live runs.

## Recommended Next Slice

Recommended next slice:

```text
PR132 Decision Work Conversation Interpretation Second Tiny Offline Read v0
```

Follow-on status:

PR131 is now implemented as the first tiny offline read:

- [Decision Work Conversation Interpretation Tiny Offline Read v0](decision-work-conversation-interpretation-tiny-offline-read-v0.md)
- `reviews/codex-assisted/decision-work-conversation-interpretation-tiny-offline-read-v0/read.json`
- `tests/test_decision_work_conversation_interpretation_tiny_offline_read.py`

PR131 used one generated local PR130 packet for `launch-public-enterprise-beta`
and checked in no packet fixture or private text. It found the tiny read useful
for decision question, action consequence, options, thresholds, evidence gates,
and non-claims, while keeping starting direction, abandoned options, noisy
friction, and lost value uncertain.

The next slice should run a second tiny offline read on a different case before
formalizing a durable interpretation-read schema or planning runtime work.

PR132 and PR133 follow-on status:

- [Decision Work Conversation Interpretation Second Tiny Offline Read v0](decision-work-conversation-interpretation-second-tiny-offline-read-v0.md)
- [Decision Work Conversation Interpretation Read Schema v0](decision-work-conversation-interpretation-read-schema-v0.md)
- [Decision Work Conversation Interpretation Read JSON](decision-work-conversation-interpretation-read-v0.json)

PR132 repeats the tiny read on `deploy-assisted-intake-routing`, confirms the
same narrow read shape is useful outside enterprise GTM, and gates to schema
formalization. PR133 defines the reusable
`lolla.decision_work_conversation_interpretation_read.v0` contract for future
offline reads. Neither PR adds an interpreter, model calls, runtime extraction,
product proof, or agent authorization.
