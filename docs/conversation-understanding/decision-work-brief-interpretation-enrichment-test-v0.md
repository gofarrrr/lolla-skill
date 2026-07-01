# Decision Work Brief Interpretation Enrichment Test v0

Status: PR135 enrichment test
Date: 2026-07-01
Schema: `lolla.decision_work_brief_interpretation_enrichment_test.v0`

## Purpose

PR135 tests whether a tiny offline interpretation read can make one existing
Decision Work Brief more useful to a reader.

The test uses exactly one case:

- `launch-public-enterprise-beta/20260627T104146Z_7bfe79`

Inputs:

- [original rendered brief](decision-work-brief-rendered-launch-public-enterprise-beta-v0.md)
- [`read.json`](../../reviews/codex-assisted/decision-work-conversation-interpretation-tiny-offline-read-v0/read.json)
- [PR134 read comparison](decision-work-conversation-interpretation-read-comparison-v0.md)

Output:

- [enriched rendered brief](decision-work-brief-enriched-launch-public-enterprise-beta-v0.md)
- [`review.json`](../../reviews/codex-assisted/decision-work-brief-interpretation-enrichment-test-v0/review.json)

PR135 does not modify the original rendered brief.

## Enrichment Rule

PR135 uses only the fields PR134 said may cautiously feed the brief:

- `decision_question`
- `likely_starting_direction`, with visible uncertainty
- `revised_direction_or_action_consequence`
- `decision_thresholds`
- `evidence_gates`
- `useful_friction`
- `what_the_final_answer_does_not_prove`

It keeps these fields out of the main user-facing body:

- `live_options`
- `abandoned_or_rejected_options`
- `noisy_friction`
- `lost_value`
- user values
- stakeholder obligations
- assistant influence

The enriched brief adds one new plain-language section:

```text
What the interpretation adds
```

That section does not claim Lolla caused every change. It separates what may
already have been present from what appears to have been sharpened and what
remains uncertain.

## Result

The enriched launch-beta brief remains coherent enough to compare with the
original. The added section clarifies the action consequence and the
already-present-versus-sharpened distinction without turning the brief into a
field dump.

The PR135 review therefore chooses:

```text
proceed_to_original_vs_enriched_review
```

## Boundary

PR135 does not:

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
- modify the original rendered brief;
- check in raw/private content.

## Recommended Next Slice

Recommended next slice:

```text
PR136 Original vs Enriched Brief Review v0
```

That slice should compare the original and enriched launch-beta briefs and
decide whether enrichment should be tested on a second case, patched, kept
evidence-only, paused for human review, or simplified.

## Follow-On Status

PR136 is now implemented as the original-vs-enriched review:

- [Decision Work Brief Original vs Enriched Review v0](decision-work-brief-original-vs-enriched-review-v0.md)
- `reviews/codex-assisted/decision-work-brief-original-vs-enriched-review-v0/review.json`
- `tests/test_decision_work_brief_original_vs_enriched_review.py`

It chooses `proceed_to_second_enriched_brief_test`.
