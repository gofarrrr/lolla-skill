# Decision Work Brief Enriched Pattern Review v0

Status: PR138 pattern review
Date: 2026-07-01
Schema: `lolla.decision_work_brief_enriched_pattern_review.v0`

## Purpose

PR138 compares the two enriched Decision Work Brief examples:

1. [Enriched launch-beta brief](decision-work-brief-enriched-launch-public-enterprise-beta-v0.md)
2. [Enriched intake-routing brief](decision-work-brief-enriched-deploy-assisted-intake-routing-v0.md)

Review artifact:

- [`review.json`](../../reviews/codex-assisted/decision-work-brief-enriched-pattern-review-v0/review.json)

PR138 decides what should happen next. It does not implement enrichment rules,
enrich more cases, create new interpretation reads, change runtime, or claim
product proof.

## Pattern Read

The enriched examples show the same useful pattern across two different
decision families.

In both cases, the added interpretation section helps a reader understand the
action consequence:

- launch beta: choose proof-producing buyer behavior over public-launch optics
  or logo size;
- intake routing: run an operable deployment test instead of treating AI routing
  as the backlog solution.

In both cases, the enrichment is useful because it separates:

- what may already have been present;
- what the audit process appears to have sharpened;
- what remains uncertain.

The enrichment does not need to expose field names or source-status machinery
in the main body. Evidence and source limits can stay in the Evidence and
limits section.

## Stable Fields

The fields that look stable enough for a future rules contract are:

- decision question;
- likely starting direction, only with visible uncertainty;
- revised action consequence;
- decision thresholds;
- evidence gates;
- useful friction, only as a descriptive read;
- what the final answer does not prove.

Fields that should remain evidence-only or unresolved for now:

- live options;
- abandoned or rejected options;
- noisy friction;
- lost value;
- user values;
- stakeholder obligations;
- assistant influence.

## Main Risks

The strongest risk is still overclaim through polish.

The enriched briefs are easier to read than the raw interpretation reads. That
is good for product usefulness, but it can also make provisional interpretation
feel more settled than it is.

The next step should therefore be a rules contract before any additional
enrichment, customer example, runtime plan, or product claim.

## Decision Gate

PR138 chooses:

```text
proceed_to_enrichment_rules_contract
```

Why:

- enrichment helped in both cases;
- it made action consequence clearer in both cases;
- it preserved uncertainty and non-claims;
- it avoided putting field/status machinery in the main body;
- two cases are enough to formalize conservative rules, not enough for runtime
  integration or product readiness.

## Boundary

PR138 does not:

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
- enrich more cases;
- implement a rules contract;
- implement PR139.

## Recommended Next Slice

Recommended next slice:

```text
PR139 Decision Work Brief Enrichment Rules Contract v0
```

That future PR should define conservative rules for turning interpretation
reads into brief enrichment. It should not run Lolla, call models, integrate
runtime, or treat enrichment as product proof.

## Follow-On Status

PR139 through PR141 have now followed this gate:

- PR139 defines the conservative enrichment rules contract.
- PR140 implements a deterministic offline builder and generates separate
  builder-enriched launch-beta and intake-routing Markdown outputs.
- PR141 reviews those builder outputs against the hand-built enriched examples
  and gates to `proceed_to_builder_rule_patch` because the useful signal and
  non-claims survive, but the generated language is still too templated.

None of those slices add runtime integration, model calls, new interpretation
reads, product proof, human validation, answer-quality scoring, or agent action
authorization.
