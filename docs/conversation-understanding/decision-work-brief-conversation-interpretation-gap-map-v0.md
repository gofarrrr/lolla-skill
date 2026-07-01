# Decision Work Brief Conversation Interpretation Gap Map v0

Status: PR127 conversation interpretation gap map
Date: 2026-07-01
Schema: `lolla.decision_work_brief_conversation_interpretation_gap_map.v0`

## Purpose

PR127 asks what conversation-level information the Decision Work Brief lane
needs but cannot yet reliably preserve or present.

The plain-language brief surface now works better. The remaining question is
not "can the Markdown read nicely?" It is:

> What important decision-work information is missing, private-only,
> provisional, or not structured yet?

The durable review artifact is:

- [`review.json`](../../reviews/codex-assisted/decision-work-brief-conversation-interpretation-gap-map-v0/review.json)

## Cases Reviewed

PR127 reviews the same three existing brief cases:

- [CEO Remove Founding Cofounder](decision-work-brief-rendered-ceo-remove-founding-cofounder-v0.md)
- [Launch Public Enterprise Beta](decision-work-brief-rendered-launch-public-enterprise-beta-v0.md)
- [Deploy Assisted Intake Routing](decision-work-brief-rendered-deploy-assisted-intake-routing-v0.md)

It also uses the checked-in review JSON for those cases and read-only local
structured artifact summaries where available. It checks in no raw/private
content.

## What We Want To Know

A useful Decision Work Brief eventually needs to preserve more than the final
answer.

It should help a reader understand:

- what decision was being made;
- what direction the conversation seemed to start from;
- what options were live, abandoned, rejected, or deferred;
- what evidence gates, thresholds, and stop rules mattered;
- what context the user supplied;
- what constraints, stakeholders, values, and unknowns shaped the decision;
- what Lolla pressed on;
- what changed for action;
- what may have been lost or overcorrected;
- what the final answer does not prove;
- where evidence and redaction boundaries live.

## What The System Currently Knows

The current artifacts can already preserve some useful structure:

- decision question, at least partially;
- revised action consequence, at least provisionally;
- capture and conversation-shape metadata;
- dropped-thread and frame-pressure hints;
- source refs and custody flags;
- which raw/private artifacts are present but not checked in;
- explicit non-claims.

That is enough to support the current plain-language brief examples. It is not
enough to make them product-ready.

## What Is Missing

The repeated gap across all three cases is not one missing file. It is missing
interpretation shape.

The current system does not yet have a first-class contract for:

- live options and option status;
- abandoned or rejected options;
- starting-direction overlap;
- whether the user changed their mind;
- assistant influence on user framing;
- useful versus noisy friction;
- lost value;
- overcorrection risk;
- user values and stakeholder obligations;
- safe user-facing versus agent-inspection handoff boundaries.

Those fields are visible as needs in the briefs, but they are not yet a stable
target contract.

## What Requires LLM Or Human Interpretation

Messy interpretation remains outside deterministic code.

LLMs or humans are needed for:

- likely starting direction;
- option status;
- abandoned paths;
- assistant influence;
- user stance changes;
- sycophancy or over-accommodation risk;
- useful versus noisy friction;
- lost value;
- overcorrection risk;
- values, stakeholder obligations, and political constraints.

Human review is especially important where the field touches legal, safety,
relationship, stakeholder, or values context.

## What Deterministic Code Should Preserve

Deterministic code can safely own custody, not messy meaning.

It should preserve:

- source refs;
- source status;
- field status;
- missingness;
- redaction/private availability;
- local-private-only status;
- whether a field requires LLM interpretation;
- whether a field requires human review;
- non-claims;
- conservative custody flags.

It should not decide whether Lolla improved the decision, whether friction was
useful, whether a stakeholder obligation is real, or whether an action is safe.

## Decision Gate

PR127 chooses:

```text
define_interpretation_target_contract
```

This means the next slice should define a future-facing but repo-grounded
contract for the conversation interpretation fields the Decision Work Brief
lane should eventually preserve.

Rejected outcomes:

- `run_more_local_private_gap_checks`: useful later, but the repeated field
  gaps are already clear enough to define the target.
- `patch_brief_schema`: the current brief schema can carry values and
  uncertainty; the missing piece is a conversation interpretation target below
  it.
- `patch_packet_builder`: packet changes should follow the target contract.
- `patch_renderer_language`: the surface language is not the current blocker.
- `pause_until_human_review`: human review remains required, but the contract
  gap is concrete enough to document.
- `stop_and_simplify`: the desired fields are broad, but they are product
  useful if kept as an interpretation/custody contract rather than runtime
  machinery.

## Boundary

PR127 does not:

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
PR128 Decision Work Conversation Interpretation Target Contract v0
```

PR128 should define the future contract only. It should not implement runtime
extraction, change prompts, call models, or create product-readiness claims.

Follow-on status:

PR128 is now implemented as a docs/schema/tests-only target contract:

- `docs/conversation-understanding/decision-work-conversation-interpretation-contract-v0.md`
- `docs/conversation-understanding/decision-work-conversation-interpretation-contract-v0.json`
- `tests/test_decision_work_conversation_interpretation_contract.py`

The next safe slice should review how completed-run packets or local/private
adequacy reads would align to that contract, still without runtime extraction
or checked-in private content.

PR129 is now implemented as that packet/artifact support review. It selects a
field-grouped offline interpretation packet as the next safe step before any
runtime extraction plan.

## Non-Claims

PR127 is not:

- human review;
- product proof;
- answer-quality measurement;
- automatic labeling;
- runtime integration;
- a new extractor;
- a claim that missing fields prove bad advice;
- a claim that clean artifacts mean good advice;
- agent action authorization.
