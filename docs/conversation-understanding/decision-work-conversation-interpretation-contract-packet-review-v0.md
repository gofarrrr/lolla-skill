# Decision Work Conversation Interpretation Contract Packet Review v0

Status: PR129 contract packet review
Date: 2026-07-01
Schema: `lolla.decision_work_conversation_interpretation_contract_packet_review.v0`

## Purpose

PR129 tests the PR128 target contract against the current completed-run
artifact and Decision Work Brief packet surface.

The durable review artifact is:

- [`review.json`](../../reviews/codex-assisted/decision-work-conversation-interpretation-contract-packet-review-v0/review.json)

This is a feasibility review. It does not implement the PR128 contract.

## Source Contract

PR129 reviews:

- [Decision Work Conversation Interpretation Contract v0](decision-work-conversation-interpretation-contract-v0.md)
- [Decision Work Conversation Interpretation Contract JSON](decision-work-conversation-interpretation-contract-v0.json)

The contract asks future work to preserve conversation interpretation fields for
decision shape, options and paths, conversation process, context, stakeholders,
constraints, audit pressure, losses, evidence, and handoff boundaries.

## Cases Reviewed

PR129 uses the same three checked-in-safe Decision Work Brief cases:

- [CEO Remove Founding Cofounder](decision-work-brief-rendered-ceo-remove-founding-cofounder-v0.md)
- [Launch Public Enterprise Beta](decision-work-brief-rendered-launch-public-enterprise-beta-v0.md)
- [Deploy Assisted Intake Routing](decision-work-brief-rendered-deploy-assisted-intake-routing-v0.md)

For each case, PR129 inspected checked-in reviews and the current packet builder
surface. It also generated temporary metadata-only PR115 packet outputs outside
the repo to confirm that the packet builder can preserve source availability,
redaction, and private-artifact status without copying private text.

No temporary packet output is checked in.

## What Current Artifacts Can Support

The current artifacts and packets can already support:

- source refs and custody status;
- whether raw/private artifacts exist but are redacted or local-private only;
- the broad decision question, at least partially;
- provisional action-consequence reads from the existing brief pilots;
- what the final answer does not prove;
- some thresholds, stop rules, evidence gates, dropped-thread hints, and
  uncertainty/status fields;
- deterministic metadata such as archive/run identity and structured artifact
  availability.

That is enough to keep the current Decision Work Brief examples readable and
evidence-backed. It is not enough to populate the PR128 contract.

## What Is Partial

Several contract fields are present only as partial checked-in-safe reads:

- likely starting direction;
- live and abandoned options;
- decision thresholds and evidence gates;
- what Lolla pressed on;
- what changed;
- unresolved or dropped threads;
- timing, operational, legal, compliance, and safety constraints.

The current packet builder can point to possible sources for those fields, but
it does not yet create a field-by-field contract packet that says which fields
are available, private, redacted, missing, LLM-owned, or human-review-owned.

## What Is Local-Private Only

The load-bearing context often lives in local/private run artifacts:

- raw conversation context;
- raw revised answer context;
- raw memo context;
- private ledgers;
- pasted documents or external context;
- user-provided constraints and nuance;
- buyer, governance, compliance, clinic-capacity, or relationship details.

PR129 records only safe conclusions about those sources. It does not check in
raw/private content.

## What Requires LLM Interpretation

The main interpretation gaps are not deterministic metadata problems.

Future bounded LLM interpretation is needed for:

- likely starting direction;
- live, rejected, deferred, or abandoned options;
- option status;
- assistant influence on user framing;
- whether the user changed their mind;
- useful versus noisy friction;
- generic caution risk;
- false precision risk;
- overcorrection risk;
- what the conversation changed for action.

Those reads should remain provisional unless human reviewed.

## What Requires Human Review

Human review remains required for fields touching:

- user values or priorities;
- stakeholder obligations;
- relationship or political constraints;
- legal, compliance, or safety constraints;
- lost value;
- momentum or ambition loss;
- safe user-facing presentation;
- agent-inspection handoff boundaries.

The contract can mark those needs. It cannot satisfy them.

## What Deterministic Code Can Carry

Deterministic code can safely carry:

- source refs;
- source status;
- field status;
- missingness;
- redaction and local-private availability;
- whether a field requires LLM interpretation;
- whether a field requires human review;
- non-claims;
- conservative custody flags.

Deterministic code should not decide whether advice is good, whether Lolla made
the decision better, whether friction was useful, whether value was lost, or
whether an agent may act.

## What Must Not Become A Quality Label

The PR128 contract fields must not become labels of advice quality, readiness,
or approval.

Especially risky fields include:

- useful friction;
- noisy friction;
- lost value;
- overcorrection risk;
- safe user-facing presentation;
- safe agent-inspection handoff.

These fields can guide future interpretation and review, but they must not be
used as product proof, answer-quality measurement, or agent action
authorization.

## Decision Gate

PR129 chooses:

```text
build_offline_interpretation_packet
```

Why:

- the current packet builder can preserve source availability, redaction, and
  private-artifact status;
- the current brief pilots already provide bounded checked-in-safe examples;
- the PR128 contract needs a field-grouped offline packet before any LLM or
  human interpretation can be tested cleanly;
- runtime extraction would be premature because the field contract has not yet
  been exercised as an offline packet.

Rejected next steps:

- `patch_packet_builder_for_contract_status_refs`: useful later, but too narrow
  because the gap is not only status refs; it is a new contract-shaped packet.
- `build_offline_llm_specialist_read`: too early before bounded inputs exist.
- `run_more_local_private_adequacy_checks`: still useful, but the immediate
  need is a packet shape that can organize those checks.
- `patch_brief_schema`: the current brief can carry interpreted values and
  uncertainty; the missing layer is below it.
- `plan_future_runtime_extraction_extension`: not earned yet.
- `pause_until_human_review`: human review remains necessary, but the next
  offline packet step is clear.
- `stop_and_simplify`: the contract is broad, but useful if kept as a
  field-status and interpretation handoff layer.

## Boundary

PR129 does not:

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

PR130 now defines the read-only offline packet shape that maps current
completed-run artifacts and PR115 packet refs into the PR128 contract groups:

- [Decision Work Conversation Interpretation Offline Packet v0](decision-work-conversation-interpretation-offline-packet-v0.md)

That packet prepares bounded input for future LLM or human interpretation
without filling the contract semantically, calling models, changing runtime, or
checking in private content. The next slice should test one tiny offline
interpretation read against such a packet.

## Non-Claims

PR129 is not:

- contract implementation;
- runtime extraction;
- product proof;
- human validation;
- answer-quality measurement;
- a broad judge;
- agent action authorization;
- evidence that clean artifacts mean good advice;
- permission to attach Decision Work Briefs to live runs.
