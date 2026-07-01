# Decision Work Conversation Interpretation Contract v0

Status: PR128 target contract
Date: 2026-07-01
Schema: `lolla.decision_work_conversation_interpretation_contract.v0`

## Purpose

PR128 follows the PR127 gate:

```text
define_interpretation_target_contract
```

PR127 found that the Decision Work Brief lane can now render readable decision
stories, but the richer conversation interpretation behind those stories is not
yet a stable target.

This contract defines what future interpretation/custody work should preserve.
It does not implement extraction.

The machine-readable contract is:

- [Decision Work Conversation Interpretation Contract JSON](decision-work-conversation-interpretation-contract-v0.json)

## Why This Contract Exists

The final AI answer is cheap. The valuable product layer is the decision work
behind it:

- what was discussed;
- what context was supplied;
- what options were live, rejected, or deferred;
- what Lolla pressed on;
- what changed for action;
- what value may have been lost;
- what remains uncertain;
- what the audit must not claim.

The current Decision Work Brief can show some of that story. It cannot yet
represent the full conversation interpretation target in a consistent way.

## What Information We Want To Preserve

The contract groups fields into:

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

Each field states:

- who owns it;
- whether interpretation is required;
- what deterministic code may preserve;
- when human review is required;
- whether source refs are required;
- what empty means;
- how privacy should be handled;
- whether the field can feed the user-facing brief;
- whether it can feed agent inspection;
- that it must not be used as a quality label.

## What Requires LLM Interpretation

LLMs may interpret messy conversation meaning such as:

- likely starting direction;
- live options and abandoned options;
- assistant influence on user framing;
- whether the user changed their mind;
- useful versus noisy friction;
- overcorrection risk;
- generic caution risk;
- what changed in action.

Those reads must remain provisional unless human reviewed.

## What Requires Human Review

Human review is required when fields touch:

- user values or priorities;
- stakeholder obligations;
- relationship or political constraints;
- legal, compliance, or safety constraints;
- lost value;
- momentum or ambition loss;
- user-facing publication;
- action-sensitive agent handoff.

The contract does not make those calls itself. It marks where they are needed.

## What Deterministic Code Can Own

Deterministic code can safely preserve custody facts:

- source refs;
- source status;
- field status;
- missingness;
- redaction/private availability;
- local-private-only status;
- schema validity;
- non-claims;
- conservative custody flags.

Deterministic code must not decide whether advice is good, whether Lolla
changed the decision for the better, whether friction was useful, or whether an
agent may act.

## How This Could Feed Briefs Later

Future Decision Work Brief work can use this contract as a target below the
brief schema:

```text
completed run artifacts
-> conversation interpretation contract-shaped read
-> Decision Work Brief sections
-> evidence and limits
```

That future path should still keep raw/private content local unless explicitly
safe, and it should keep source refs and non-claims attached to every
interpretation.

## How This Could Feed Agent Inspection

The contract can also support future agent inspection by making source status,
missingness, and human-review requirements explicit.

But agent inspection is not agent action authorization. A field can be useful
for inspection while still requiring human review before action.

## Explicitly Not Implemented

PR128 does not:

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
- integrate the brief into runtime;
- implement a new extractor;
- change the live extraction schema;
- check in raw/private content.

## Recommended Next Slice

Recommended next slice:

```text
PR131 Decision Work Conversation Interpretation Tiny Offline Read v0
```

Follow-on status:

PR129 is now implemented as a contract packet review:

- `docs/conversation-understanding/decision-work-conversation-interpretation-contract-packet-review-v0.md`
- `reviews/codex-assisted/decision-work-conversation-interpretation-contract-packet-review-v0/review.json`
- `tests/test_decision_work_conversation_interpretation_contract_packet_review.py`

PR129 found that existing packet/source artifacts can carry source and custody
status, but the next needed layer is a field-grouped offline interpretation
packet aligned to this contract.

PR130 now implements that offline packet:

- [Decision Work Conversation Interpretation Offline Packet v0](decision-work-conversation-interpretation-offline-packet-v0.md)
- `engine/system_b/decision_work_conversation_interpretation_packets.py`
- `scripts/evals/build_decision_work_conversation_interpretation_packets.py`
- `tests/test_decision_work_conversation_interpretation_packets.py`

PR130 still does not fill the contract semantically, call models, change
runtime extraction, or check in private content. The next step should test one
tiny offline interpretation read against a bounded packet.

## Non-Claims

PR128 is not:

- runtime extraction;
- product proof;
- human validation;
- answer-quality measurement;
- a broad judge;
- agent action authorization;
- a customer-facing brief;
- evidence that clean artifacts mean good advice;
- permission to attach Decision Work Briefs to live runs.
