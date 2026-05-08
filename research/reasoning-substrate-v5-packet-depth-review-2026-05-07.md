# Reasoning Substrate V5 Packet Depth Review

**Date:** 2026-05-07
**PR slice:** PR29 - v5 packet handoff-depth review
**Status:** review-only fixture comparison; no extraction, runtime, prompt, lane, model-call, judge, or user-facing surface
**Decision label:** `v5_packet_depth_improved`

## Principle

PR29 tests handoff quality, not final-answer quality.

The question is not whether PR28 produces a better Decision Pressure. That
would put evaluation at the wrong system boundary. The question is whether PR28
turned useful-but-thin graph-only shelves into source-backed cards that give the
next LLM clearer activation, evidence, misuse, treatment, dismissal, and
absence signals.

Python can count structure and enforce guardrails. It should not decide card
usefulness, semantic novelty, actionability, final pressure, or the best
reasoning path. This review uses counts as custody checks and uses reviewer
judgment for handoff-depth assessment.

## Fixtures Compared

Before fixture:

`tests/fixtures/reasoning_substrate_packet/pr27_mixed_packet_review.json`

After fixture:

`tests/fixtures/reasoning_substrate_packet/pr29_v5_mixed_packet_review.json`

The PR29 fixture keeps the same synthetic review transaction, same candidate
nominations, same candidate cap, same suppression case, and same snippet cap as
PR27 where possible. The only intended substrate change is that the packet
producer reads `data/compiled/model_affordances/affordances_v5.json` instead of
the PR27 v4 artifact.

## Before And After Shape

| Measure | PR27 packet | PR29 packet | Delta |
| --- | ---: | ---: | ---: |
| Candidate cards | 7 | 7 | 0 |
| Suppressed candidates | 1 | 1 | 0 |
| Reviewed cards | 3 | 7 | +4 |
| Graph-only cards | 4 | 0 | -4 |
| Missing reviewed records | 4 | 0 | -4 |
| Absence records visible in cards | 3 | 7 | +4 |
| Reviewed source-evidence references | 3 | 7 | +4 |
| JSON bytes | 33,848 | 42,756 | +8,908 |
| JSON lines | 773 | 959 | +186 |

The packet became larger by about one quarter, but not because more candidates
were added. The growth comes from reviewed operational fields on the four
formerly graph-only cards. That burden is acceptable for this fixture because
the receiving object now carries more dismissal, evidence, and treatment
signals without changing candidate count or allowing Python to pick a
conclusion.

## Coverage Delta

PR27 graph-only cards upgraded under v5:

- `chain-of-verification`
- `constraints`
- `confirmation-bias`
- `step-back`

All four now have:

- `reviewed_affordance_available` coverage status under the version-neutral
  packet label vocabulary;
- repo source custody;
- reviewed `use_when`;
- reviewed `do_not_use_when`;
- reviewed `case_evidence_needed`;
- reviewed `treatment_requirements`;
- reviewed `diagnostic_questions`;
- reviewed `misuse_guards`;
- reviewed source evidence;
- at least one absence record.

PR29 hardens the packet vocabulary so the coverage label no longer names a
specific compiled artifact version. In this fixture it means "reviewed
affordance available from the selected draft reviewed artifact," not runtime
promotion of v5 or a claim that v5 is live.

## Model-By-Model Review

### `chain-of-verification`

Before PR28, this card was a graph-only shelf hint: the case needed premise
verification because the assistant deferred risk tracking until after launch.
That was useful for recall but thin for operational treatment.

After PR28, the v5 card says when to use the model: a recommendation, forecast,
rollout, or diagnosis depends on linked premises that all need to hold. It also
says what evidence is required: the conclusion under review and the linked
premises it depends on. The treatment requirement is concrete: name the
conclusion, map the linked premises, and identify which premise would collapse
the conclusion before expressing confidence.

Review judgment:

| Dimension | Judgment |
| --- | --- |
| Activation clarity | Better |
| Evidence-needed clarity | Better |
| Do-not-use clarity | Better |
| Misuse guard usefulness | Better |
| Treatment usefulness | Better |
| Absence/overclaim protection | Better |
| Packet burden | Acceptable |
| Net handoff judgment | Useful added depth |

The useful depth is that the card no longer means generic "verify more." It
means audit make-or-break premises and avoid verification theater when a
bounded reversible test would teach more.

### `constraints`

Before PR28, this card was a graph-only hint that the case needed scope, budget,
or launch boundaries. That was relevant but broad.

After PR28, the v5 card gives the LLM a decision filter: use constraints when
too many goals, variables, stakeholders, or possible moves are competing for
attention and clarity is being lost. It requires evidence about the goal,
scope, decision, or problem surface being constrained. It also warns not to use
the model when the constraint is inherited, outdated, or untested after the
environment has changed.

Review judgment:

| Dimension | Judgment |
| --- | --- |
| Activation clarity | Better |
| Evidence-needed clarity | Better |
| Do-not-use clarity | Better |
| Misuse guard usefulness | Better |
| Treatment usefulness | Better |
| Absence/overclaim protection | Better |
| Packet burden | Acceptable |
| Net handoff judgment | Useful added depth |

The useful depth is that "consider constraints" becomes "state the operating
boundary, trade-off, and deliberate exclusion, while checking whether the
constraint is stale or merely self-imposed."

### `confirmation-bias`

Before PR28, this card was a graph-only hint that the transaction might be
converging on the preferred renewal answer before disconfirming evidence was
named.

After PR28, the v5 card gives a clearer evidence discipline: use the model when
a team is converging quickly on a favored recommendation before the evidence is
fully in. It requires the favored conclusion and the confirming evidence that
currently carries it. The treatment requirement asks the answer to put
disconfirming observations, objections, failed cases, and quiet losses into the
same comparison set as visible confirming evidence.

Review judgment:

| Dimension | Judgment |
| --- | --- |
| Activation clarity | Better |
| Evidence-needed clarity | Better |
| Do-not-use clarity | Better |
| Misuse guard usefulness | Better |
| Treatment usefulness | Better |
| Absence/overclaim protection | Better |
| Packet burden | Acceptable |
| Net handoff judgment | Useful added depth |

The useful depth is that the card stops being a generic bias warning. It now
requires equal standing for disconfirming evidence and blocks the unhelpful
move of accusing other people of bias while leaving the evidence standard
unchanged.

### `step-back`

Before PR28, this card was a graph-only reminder that urgency was becoming
commitment before the governing purpose had been restated.

After PR28, the v5 card defines when the model applies: the team is too close
to details to see what actually matters. It requires evidence of the immediate
action, analysis, or detail work absorbing attention. The treatment requirement
asks the answer to name the governing structure, core point, or problem-owner
frame before recommending execution.

Review judgment:

| Dimension | Judgment |
| --- | --- |
| Activation clarity | Better |
| Evidence-needed clarity | Better |
| Do-not-use clarity | Better |
| Misuse guard usefulness | Better |
| Treatment usefulness | Better |
| Absence/overclaim protection | Better |
| Packet burden | Acceptable |
| Net handoff judgment | Useful added depth |

The useful depth is that "pause and reflect" becomes "reorient before execution
and return with a bounded next move." The absence record also prevents step-back
from becoming an excuse for indefinite reflection.

## Optional PR28 Targets

PR28 also added v5 reviewed records for:

- `scientific-method-evidence-testing`
- `five-whys-method`
- `root-cause-analysis`
- `first-principles-thinking`
- `intellectual-humility`
- `authority-bias`

PR29 intentionally did not add these to the fixture because the cleanest
before/after comparison keeps nominations constant. Their packet usefulness
should be tested in a separate mixed fixture or receiver-review exercise if the
next slice explores additional candidate mixes.

## What Improved

PR28 added real handoff depth for the four upgraded PR27 cards.

The improvement is not just "more fields." The cards now help the next LLM
answer:

- what case shape activates the model;
- what evidence must be present before leaning on it;
- when the model should be dismissed;
- what misuse looks like;
- what a good answer must do if the model applies;
- what the source does not support.

That is a better handoff object. It still leaves semantic choice to the
LLM/reviewer.

## What Became Clutter

No upgraded card became obvious clutter in this fixture.

The packet is heavier, and raw JSON remains an internal review format. The
burden stayed acceptable because:

- candidate count did not increase;
- duplicate suppression stayed separate;
- the snippet cap stayed at one;
- each upgraded card gained concrete operational constraints;
- absence records protected against overclaiming instead of filling fields for
  completeness.

The main shape caution from the first PR29 pass was vocabulary drift: labels
that named v4 described reviewed records coming from v5. PR29 now folds in the
version-neutral packet label `reviewed_affordance_available`, so later fixtures
do not need to reinterpret artifact-versioned fields when they read v5 or a
future draft artifact.

## Handoff Judgment

PR29 supports the label `v5_packet_depth_improved`.

The v5 packet is better reasoning material than the PR27 packet. It remains a
dormant handoff object. It does not prove final-answer quality, and it does not
authorize deterministic pressure selection. It proves the narrower and more
important point at this layer:

> Controlled extraction can turn selected graph-only shelves into compact,
> source-backed cards that make the next LLM's reasoning substrate clearer
> without making Python the reasoning actor.

## Recommendation

Do not jump to broad extraction yet.

The best next slice is a receiver-side packet review before scaling:

1. Keep runtime dormant.
2. Give PR27 and PR29 packets, or compact renderings of them, to an external
   LLM/reviewer only if explicitly approved.
3. Ask whether the v5 packet helps the receiver choose, merge, ignore, or set
   aside candidate shelves without being steered to a final pressure.
4. If that review agrees the added depth is useful, do the next extraction batch
   as another small controlled batch, not Batch 3b.

If model calls are not approved, the fallback next slice should harden packet
shape and compact rendering before more extraction. The reviewed-coverage label
vocabulary is already version-neutral after the PR29 hardening.

## Guardrails Confirmed

PR29 did not:

- run live `/lolla`;
- change prompts;
- rewrite lanes;
- build a live lane adapter;
- extract new records;
- create Batch 3b;
- modify affordance records;
- modify `affordances_v5.json`;
- call models;
- run judges;
- wire Observatory, memo, Step 8, Step 6, or Lane 4 runtime;
- create user-facing Decision Pressure;
- make Python choose final pressure.
