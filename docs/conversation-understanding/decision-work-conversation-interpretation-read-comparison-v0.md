# Decision Work Conversation Interpretation Read Comparison v0

Status: PR134 comparison gate
Date: 2026-07-01
Schema: `lolla.decision_work_conversation_interpretation_read_comparison.v0`

## Purpose

PR134 compares the two tiny offline conversation interpretation reads created
by PR131 and PR132.

The review artifact is:

- [`review.json`](../../reviews/codex-assisted/decision-work-conversation-interpretation-read-comparison-v0/review.json)

This PR does not create another interpretation read, enrich a Decision Work
Brief, change runtime behavior, call models, or claim product proof.

## Compared Reads

PR134 compares exactly two reads:

1. `launch-public-enterprise-beta`
   - [`read.json`](../../reviews/codex-assisted/decision-work-conversation-interpretation-tiny-offline-read-v0/read.json)
   - [rendered brief](decision-work-brief-rendered-launch-public-enterprise-beta-v0.md)

2. `deploy-assisted-intake-routing`
   - [`read.json`](../../reviews/codex-assisted/decision-work-conversation-interpretation-second-tiny-offline-read-v0/read.json)
   - [rendered brief](decision-work-brief-rendered-deploy-assisted-intake-routing-v0.md)

Both reads predate the formal PR133 schema, but both use the same field shape
that PR133 codified.

## Stable Useful Fields

The strongest stable fields are:

- `decision_question`
- `revised_direction_or_action_consequence`
- `decision_thresholds`
- `evidence_gates`
- `useful_friction`
- `what_the_final_answer_does_not_prove`

The repeated useful pattern is action consequence.

In the launch-beta case, the read clarifies that the action consequence is not
"launch publicly because the larger logo looks good." It points toward equal
paid private-pilot offers and proof-producing buyer behavior.

In the intake-routing case, the read clarifies that the action consequence is
not "deploy AI routing as the backlog solution." It points toward a narrow
operating test, a backlog diagnostic, four must-pass gates, hard pause triggers,
and narrower sales meaning.

That is the product-relevant signal: the interpretation layer helps turn the
process into "what would I do differently?"

## Shared Uncertainties

The same fields stayed source-limited in both reads:

- `likely_starting_direction`
- `abandoned_or_rejected_options`
- `lost_value`

Starting direction remains partial because checked-in-safe summaries do not
show the full original conversation, original answer, revised answer, and memo
context.

Abandoned or rejected options remain source-limited because a safe summary can
show an option being de-emphasized, but cannot reliably tell whether it was
rejected, deferred, narrowed, or still live.

Lost value remains the hardest field. It requires private context or human
judgment about whether caution, narrowing, or gate compression removed
something valuable.

Values, stakeholders, and assistant influence stay outside this tiny comparison
because they need raw conversation interpretation, local-private context, or
human review.

## Brief Enrichment Read

The reads could help the Decision Work Brief, but only through a small
plain-language test.

Fields that can feed a brief-enrichment test now:

- decision question;
- likely starting direction, with uncertainty;
- revised action consequence;
- decision thresholds;
- evidence gates;
- useful friction, framed as what appears to have been sharpened rather than as
  a quality label;
- what the final answer does not prove.

Fields that should stay evidence-only or inspection-only for now:

- live options;
- abandoned or rejected options;
- noisy friction;
- lost value.

The smallest safe enrichment test is one existing brief, probably
`launch-public-enterprise-beta`, with a compact conversation-story note that
separates:

- what may already have been present;
- what appears to have been sharpened;
- what remains unresolved.

PR134 does not perform that enrichment.

## Decision Gate

PR134 chooses:

```text
proceed_to_brief_enrichment_test
```

Why:

- both reads used the same field shape successfully;
- both produced concrete action-consequence reads;
- both preserved uncertainty and non-claims;
- the packet builder and read schema did not show a blocking shape problem;
- another backend read is less useful than testing whether interpretation
  actually improves the user-facing brief.

## Main Risks

Source-depth risk:

Both reads depend on checked-in-safe summaries. Raw conversation, raw revised
answer, raw memo, provider text, and private ledgers were not checked in.

Overclaim risk:

A stable two-read pattern can make provisional interpretation feel like
validated conversation truth.

Product-language risk:

If the enrichment exposes field names, statuses, packet language, or source
machinery in the main body, the brief will regress toward internal artifact
inspection.

Quality-label risk:

Useful friction and noisy friction must stay descriptive. They must not become
answer-quality labels.

Runtime-integration risk:

Two provisional reads do not justify live runtime attachment.

## Boundary

PR134 does not:

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
- implement a runtime extractor;
- change the live extraction schema;
- check in raw/private content;
- create a third read;
- enrich a brief.

## Recommended Next Slice

Recommended next slice:

```text
PR135 Decision Work Brief Interpretation Enrichment Test v0
```

That slice should enrich exactly one existing rendered brief from one
interpretation read, probably `launch-public-enterprise-beta`, without changing
runtime behavior, calling models from repo code, checking in private content, or
claiming product proof.

## Follow-On Status

PR135 through PR138 have now followed this gate:

- PR135 creates a separate enriched launch-beta brief and gates to
  `proceed_to_original_vs_enriched_review`.
- PR136 compares the original and enriched launch-beta briefs and gates to
  `proceed_to_second_enriched_brief_test`.
- PR137 creates a separate enriched intake-routing brief and gates to
  `proceed_to_enriched_brief_pattern_review`.
- PR138 compares the two enriched briefs and gates to
  `proceed_to_enrichment_rules_contract`.
- PR139 formalizes the enrichment rules contract.
- PR140 implements the deterministic offline enriched-brief builder.
- PR141 reviews the builder output and gates to
  `proceed_to_builder_rule_patch`.

None of those slices add runtime integration, model calls, new interpretation
reads, product proof, human validation, answer-quality scoring, or agent action
authorization.
