# Decision Work Brief Small Pattern Review v0

Status: PR120 small pattern review
Date: 2026-07-01
Schema: `lolla.decision_work_brief_small_pattern_review.v0`

## Purpose

PR120 compares the first two checked-in-safe Decision Work Brief pilots and
decides the next narrow follow-on.

The review question is:

> Do the first two briefs show a useful enough pattern to continue, or do they
> need renderer copy repair, local-private adequacy work, human review, or
> simplification first?

The answer is provisional: the two-case pattern is strong enough for exactly
one third diversity case. It is not product proof, human validation, runtime
integration, answer-quality measurement, or evidence that Lolla improved the
decisions as fact.

## Cases Reviewed

PR120 reviews exactly two cases.

1. `ceo-remove-founding-cofounder/20260627T093131Z_59d153`

   Sources:

   - [`PR116 review.json`](../../reviews/codex-assisted/decision-work-brief-draft-pilot-v0/review.json)
   - [Rendered cofounder brief](decision-work-brief-rendered-ceo-remove-founding-cofounder-v0.md)
   - [PR118 usefulness review](decision-work-brief-usefulness-review-v0.md)

2. `launch-public-enterprise-beta/20260627T104146Z_7bfe79`

   Sources:

   - [`PR119 review.json`](../../reviews/codex-assisted/decision-work-brief-second-tiny-case-pilot-v0/review.json)
   - [Rendered launch-beta brief](decision-work-brief-rendered-launch-public-enterprise-beta-v0.md)
   - [PR119 second tiny case pilot](decision-work-brief-second-tiny-case-pilot-v0.md)

The durable review artifact is:

- [`review.json`](../../reviews/codex-assisted/decision-work-brief-small-pattern-review-v0/review.json)

## Pattern Read

PR120 selects:

```text
strong_enough_for_third_case
```

The reason is narrow. Both briefs name a concrete action consequence:

- the cofounder brief says the CEO would move authority first, narrow the
  transition role, and define stop conditions before the hard conversation;
- the launch-beta brief says the team would stop defaulting to the largest logo
  or public launch, give both prospects the same paid and scoped private-pilot
  offer, and choose based on proof-producing buyer behavior plus tripwire gates.

Both cases also preserve uncertainty, missingness, source limits, and explicit
non-claims.

That is enough to learn from one more diverse case. It is not enough to claim
product readiness.

## What The Pattern Shows

The strongest useful signal is action consequence. The brief format makes the
value of the process easier to understand when it answers:

```text
What would I do differently now?
```

The two cases are different enough to matter:

- founder governance and operating authority;
- enterprise launch timing, buyer selection, runway, and product-readiness
  gating.

The shared useful pattern is not internal evidence inventory. It is that both
briefs turn process pressure into a reader-visible action shift.

## Risks

The strongest missingness and thinness risk is that checked-in-safe artifacts
cannot verify the private context that would decide whether the provisional read
is fair:

- starting-direction overlap;
- user intent;
- buyer reality;
- board, investor, legal, governance, relationship, or customer constraints;
- lost-value severity.

The strongest overclaim risk is that clean Markdown and clear action language
can create false confidence before human validation or local-private adequacy
checks.

There is also a renderer-language risk. The body is readable as a decision
story, but field labels, source-status lines, and source refs still feel
internal. That does not block one more diversity case, but it should remain on
the repair list if the third case confirms the product shape.

## Decision Gate

PR120 chooses:

```text
proceed_to_third_diversity_case
```

This triggers exactly one PR121 path:

```text
PR121A Decision Work Brief Third Diversity Case Pilot v0
```

Rejected outcomes:

- `proceed_to_renderer_language_patch`: plausible later, but the copy issue is
  not blocking the reader from seeing action consequence.
- `proceed_to_local_private_adequacy_check`: important later, but not the next
  smallest learning step.
- `pause_until_human_review`: reasonable eventually, but one more diversity
  case can test the shape before spending human review capacity.
- `stop_and_simplify`: too harsh; both briefs answer what changed in action.

PR120 does not recommend runtime integration.

## Boundary

PR120 does not:

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
- create a dashboard;
- broaden to a batch;
- create customer marketing copy.

## Recommended Next Slice

Recommended next slice:

```text
PR121A Decision Work Brief Third Diversity Case Pilot v0
```

PR121A should run exactly one more checked-in-safe tiny brief pilot on a third
decision type, preferably `deploy-assisted-intake-routing`, then decide whether
three cases justify a pattern review, renderer patch, local-private adequacy
check, human review pause, or simplification.

## Follow-On Status

PR121A has now completed the selected follow-on:

- [Decision Work Brief Third Diversity Case Pilot v0](decision-work-brief-third-diversity-case-pilot-v0.md)
- [Decision Work Brief Rendered Example: Deploy Assisted Intake Routing](decision-work-brief-rendered-deploy-assisted-intake-routing-v0.md)

It used `deploy-assisted-intake-routing/20260627T130339Z_4cd3cb` and chose:

```text
proceed_to_three_case_pattern_review
```

That result still does not recommend runtime integration or product readiness.

PR122 has now completed the three-case review:

- [Decision Work Brief Three-Case Pattern Review v0](decision-work-brief-three-case-pattern-review-v0.md)

It found a consistent action-consequence signal across all three tiny pilots,
but chose:

```text
proceed_to_plain_language_renderer_patch
```

The blocker is not that the brief shape failed. The blocker is that the rendered
surface still sounds too much like internal machinery for a board/customer
reader. The next responsible slice is PR123 Decision Work Brief
Plain-Language Renderer Patch v0.

## Non-Claims

PR120 is not:

- human review;
- ground truth;
- product proof;
- answer-quality measurement;
- automatic labeling;
- runtime integration;
- a broad judge;
- evidence that clean rendered briefs mean good advice;
- agent action authorization;
- general evidence from two cases.
