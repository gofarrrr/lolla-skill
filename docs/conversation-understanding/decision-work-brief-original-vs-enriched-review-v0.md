# Decision Work Brief Original vs Enriched Review v0

Status: PR136 comparison gate
Date: 2026-07-01
Schema: `lolla.decision_work_brief_original_vs_enriched_review.v0`

## Purpose

PR136 compares the original launch-beta Decision Work Brief against the PR135
enriched version.

Original:

- [Decision Work Brief Rendered Launch Beta](decision-work-brief-rendered-launch-public-enterprise-beta-v0.md)

Enriched:

- [Decision Work Brief Enriched Launch Beta](decision-work-brief-enriched-launch-public-enterprise-beta-v0.md)

Review artifact:

- [`review.json`](../../reviews/codex-assisted/decision-work-brief-original-vs-enriched-review-v0/review.json)

PR136 does not modify either brief, enrich another case, change runtime, call
models, or claim product proof.

## Review Read

The enriched brief appears more useful than the original for one narrow reason:
it makes the action consequence easier to connect to the conversation story.

The original already names the decision, the action direction, source limits,
and non-claims. The enriched version adds a compact explanation of:

- what may already have been present in the safe summary;
- what the audit process appears to have sharpened;
- why buyer behavior, thresholds, and evidence gates matter for action;
- what remains uncertain.

That addition is useful enough to test on a second case. It is not evidence
that the enrichment rules are durable, customer-ready, or human validated.

## Main Risk

The main risk is false confidence. Cleaner prose can make a provisional
interpretation feel more settled than the source context supports.

The enriched version reduces machinery language, but it still depends on
checked-in-safe summaries and one Codex-assisted interpretation read. Raw
conversation, revised answer, memo, provider text, and private ledgers remain
outside the checked-in artifact.

## Decision Gate

PR136 chooses:

```text
proceed_to_second_enriched_brief_test
```

Why:

- the enriched brief appears clearer about what changed for action;
- it keeps uncertainty and non-claims visible;
- it does not expose field/status machinery in the main body;
- one case is not enough to formalize enrichment rules;
- testing one second case is more informative than writing a rules contract now.

## Boundary

PR136 does not:

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
- create a new Lolla run;
- create a new interpretation read;
- modify the original or enriched brief;
- enrich a second case.

## Recommended Next Slice

Recommended next slice:

```text
PR137 Second Enriched Brief Test v0
```

That slice should enrich exactly one second existing brief,
`deploy-assisted-intake-routing`, using the PR132 tiny interpretation read and
the same conservative enrichment rules.

## Follow-On Status

PR137 is now implemented as the second enrichment test:

- [Decision Work Brief Second Enrichment Test v0](decision-work-brief-second-enrichment-test-v0.md)
- [Decision Work Brief Enriched Intake Routing](decision-work-brief-enriched-deploy-assisted-intake-routing-v0.md)
- `reviews/codex-assisted/decision-work-brief-second-enrichment-test-v0/review.json`
- `tests/test_decision_work_brief_second_enrichment_test.py`

It chooses `proceed_to_enriched_brief_pattern_review`.
