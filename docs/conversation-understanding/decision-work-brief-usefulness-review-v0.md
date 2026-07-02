# Decision Work Brief Usefulness Review v0

Status: PR118 usefulness review and delivery gate
Date: 2026-07-01
Schema: `lolla.decision_work_brief_usefulness_review.v0`

## Purpose

PR118 reviews the first rendered Decision Work Brief pilot and decides what
should happen next.

It asks:

> Does the rendered Decision Work Brief finally answer what this process made
> the decision-maker see or do differently?

The answer is: partly, and promisingly, but not enough for product readiness.
The rendered brief is useful enough to try one more tiny case. It is not ready
for runtime integration, broad batching, customer-facing demo use, or product
claims.

## Inputs Reviewed

PR118 reviews three layers:

- [Decision Work Receipt Debug Summary](decision-work-receipt-debug-summary-v0.md)
- [Decision Work Brief Draft Pilot](decision-work-brief-draft-pilot-v0.md)
- [Decision Work Brief Rendered Example: CEO Remove Founding Cofounder](decision-work-brief-rendered-ceo-remove-founding-cofounder-v0.md)

The durable review artifact is:

- [`review.json`](../../reviews/codex-assisted/decision-work-brief-usefulness-review-v0/review.json)

The structured draft source is:

- [`PR116 review.json`](../../reviews/codex-assisted/decision-work-brief-draft-pilot-v0/review.json)

## Boundary

PR118 is offline and downstream from the Lolla runtime.

It does not:

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
- treat clean artifacts as proof of good advice;
- create runtime integration;
- create a broad batch;
- create customer marketing copy.

## Review Result

The rendered brief is materially more useful than the receipt/debug-summary
layer for a reader trying to understand decision consequence.

The receipt/debug-summary layer is good at internal questions:

- what artifacts exist;
- what was missing or private;
- what source/custody state is visible;
- what still needs interpretation.

The rendered Decision Work Brief is better at the user-facing question:

```text
What changed in the decision?
```

For the pilot case, the rendered brief makes this answer visible:

```text
move authority before more cooperation testing;
narrow the cofounder's transition support;
set stop conditions before the conversation;
keep relationship, governance, and source-boundary uncertainty visible.
```

That is the strongest useful signal.

## Main Risks

The strongest missingness/thinness risk is that this is still one
Codex-assisted, checked-in-safe case with no human validation. The review cannot
know whether the starting direction, vanilla overlap, user intent, and
lost-value severity are accurate.

The strongest overclaim risk is that Markdown makes the provisional read feel
more complete than the source boundary permits. Clean custody, clear prose, and
a strong action story can be mistaken for proof that the advice was good.

PR117 mitigates that risk by rendering:

- high uncertainty;
- source status;
- human validation false;
- product proof false;
- answer-quality measurement false;
- agent action authorization false;
- explicit non-claims.

But the risk remains.

## Decision Gate

PR118 chooses:

```text
proceed_to_tiny_second_case
```

This means the shape is promising enough to try once more, but not ready for
customer-facing use or runtime planning.

Rejected outcomes:

- `proceed_to_runtime_integration_plan_later`: not justified after one
  non-human-validated case.
- `stop_and_simplify`: too harsh; the brief does answer what changed.
- `pause_until_human_review`: reasonable, but a second tiny case can test
  whether the shape generalizes before human review capacity is spent.

## What Must Be True Before Customer-Facing Use

Before the Decision Work Brief becomes a customer-facing example, the project
needs at least:

- one additional diverse case;
- a check that the brief still names action consequence without hiding
  uncertainty;
- human review of the starting-direction and action-delta reads;
- less internal artifact language in the rendered surface;
- visible source and custody limits so clean artifacts are not mistaken for
  good advice.

## Recommended Next Slice

Recommended next slice:

```text
PR119 Decision Work Brief Second Tiny Case Pilot v0
```

PR119 should repeat the PR115 to PR117 path on one additional completed run and
compare whether the rendered brief still answers:

```text
What did this process make me see or do differently?
```

PR119 should not add runtime integration, broaden to a batch, publish a
customer-facing demo, or claim product proof.

## Follow-On Status

PR119 has now completed that second tiny case:

- [Decision Work Brief Second Tiny Case Pilot v0](decision-work-brief-second-tiny-case-pilot-v0.md)
- [Decision Work Brief Rendered Example: Launch Public Enterprise Beta](decision-work-brief-rendered-launch-public-enterprise-beta-v0.md)

The second case uses `launch-public-enterprise-beta/20260627T104146Z_7bfe79`,
keeps local-private text out of checked-in artifacts, compares against
`ceo-remove-founding-cofounder`, and chooses:

```text
proceed_to_small_pattern_review
```

That follow-on result does not change the PR118 conclusion: the first rendered
brief was promising but thin, and one case was not enough for product readiness.

PR120 and PR121A have now continued the lane:

- [Decision Work Brief Small Pattern Review v0](decision-work-brief-small-pattern-review-v0.md)
- [Decision Work Brief Third Diversity Case Pilot v0](decision-work-brief-third-diversity-case-pilot-v0.md)

PR120 chose `proceed_to_third_diversity_case`. PR121A added
`deploy-assisted-intake-routing/20260627T130339Z_4cd3cb` and chose
`proceed_to_three_case_pattern_review`. These follow-ons still do not make the
brief customer-ready or runtime-integrated.

## Non-Claims

PR118 is not:

- human review;
- ground truth;
- product proof;
- answer-quality measurement;
- automatic labeling;
- runtime integration;
- a broad judge;
- evidence that clean artifacts mean good advice;
- agent action authorization;
- general evidence from more than one case.
