# Decision Work Brief Third Builder Case v0

Status: PR147 blocking review

Date: 2026-07-01

Review schema: `lolla.decision_work_brief_third_builder_case.v0`

## Purpose

PR147 was meant to run the deterministic offline enriched-brief builder on the
third Decision Work Brief decision family:

```text
ceo-remove-founding-cofounder/20260627T093131Z_59d153
```

This would have produced a third builder-generated enriched example, parallel
to the existing launch-beta and intake-routing builder outputs.

PR147 did not create that output.

## Why The Builder Did Not Run

The deterministic builder requires three inputs:

- an original rendered Decision Work Brief;
- a PR139 enrichment rules contract;
- a builder-compatible conversation interpretation read.

The cofounder case has the first two ingredients:

- rendered brief:
  [Decision Work Brief Rendered Example: CEO Remove Founding Cofounder](decision-work-brief-rendered-ceo-remove-founding-cofounder-v0.md)
- rules contract:
  [Decision Work Brief Enrichment Rules Contract JSON](decision-work-brief-enrichment-rules-contract-v0.json)

It does not have the third ingredient. The only checked-in builder-compatible
interpretation reads are:

- `reviews/codex-assisted/decision-work-conversation-interpretation-tiny-offline-read-v0/read.json`
  for `launch-public-enterprise-beta`;
- `reviews/codex-assisted/decision-work-conversation-interpretation-second-tiny-offline-read-v0/read.json`
  for `deploy-assisted-intake-routing`.

The cofounder case has useful checked-in review material from PR116, PR118,
PR120, PR122, and PR146, but those are not PR133-shaped interpretation reads
with `interpreted_fields`. Feeding them to the builder would force the wrong
schema into a user-facing enriched brief.

## Source Availability

Available:

- rendered cofounder Decision Work Brief;
- PR139 enrichment rules contract;
- PR146 safe local-private adequacy conclusion:
  `adequate_with_private_nuance`;
- prior cofounder reviews and pattern reads.

Missing:

- a cofounder interpretation read using one of the builder-supported schemas:
  - `lolla.decision_work_conversation_interpretation_tiny_offline_read.v0`;
  - `lolla.decision_work_conversation_interpretation_second_tiny_offline_read.v0`;
  - `lolla.decision_work_conversation_interpretation_read.v0`.

## Product Read

This is a good block. The builder should not quietly convert draft-pilot,
pattern-review, or local-private adequacy material into a fielded
interpretation layer. The whole point of the Decision Work Brief lane is to
preserve evidence and limits, not to make missing interpretation look smoother.

The cofounder case is also a high-risk enrichment target. It involves founder
governance, authority transition, relationship cost, customer continuity, team
trust, equity, legal, board, and employment nuance. PR146 found the checked-in
brief adequate with private nuance, but that does not replace a bounded
interpretation read.

## Decision Gate

PR147 chooses:

```text
create_third_interpretation_read_first
```

Recommended next PR:

```text
PR147A Decision Work Conversation Interpretation Third Tiny Offline Read v0
```

That PR should create a small PR133-shaped interpretation read for the
cofounder case before any third builder output is generated.

Follow-up status: PR147A now creates that formal-schema cofounder read at
`reviews/codex-assisted/decision-work-conversation-interpretation-third-tiny-offline-read-v0/read.json`.
The builder output still belongs in a separate future PR.

## Boundary

PR147 does not:

- run `$lolla`;
- invoke the Lolla skill;
- call provider or model APIs;
- mutate archives;
- change runtime behavior;
- change prompts;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- create a new Lolla run;
- create a new interpretation read;
- run the enrichment builder on an unsupported schema;
- create a cofounder builder-enriched output;
- check in local-private text;
- add answer-quality scoring;
- create automatic labels;
- authorize agent action;
- claim product proof;
- claim human validation.

## Non-Claims

This PR does not prove the cofounder brief is wrong. It also does not prove the
builder is weak. It says only that the third builder case is missing a valid
interpretation-read input, and the safe next step is to create that input
explicitly rather than smuggling another review shape into the builder.
