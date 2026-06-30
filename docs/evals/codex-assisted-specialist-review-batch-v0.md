# Codex-Assisted Specialist Review Batch v0

Status: docs/review fixture
Date: 2026-06-29
Review capacity mode: `codex_assisted_provisional`
Slice: PR83 Codex-Assisted Specialist Review Batch v0

## Purpose

PR83 runs the first provisional specialist-review batch over the Product Delta
eval lane.

The research question is:

```text
Does decomposing Product Delta review into narrow specialist reads produce more
disciplined provisional evidence than the broad PR76 semantic fill?
```

Disciplined means:

- less over-inference;
- more explicit uncertainty;
- better lost-value detection;
- better interpretation-adequacy detection;
- more willingness to downgrade or mark inconclusive;
- clearer human follow-up questions;
- fewer overclaim risks;
- better source-status tracking.

Disciplined does not mean more positive candidate reads.

Machine-readable output:

```text
reviews/codex-assisted/specialist-review-batch-v0/review.json
```

## Boundary

PR83 is Codex-assisted provisional review. It is not human review, ground truth,
judge calibration data, product proof, answer-quality scoring, automatic
labeling, runtime integration, or agent approval.

This slice did not run `$lolla`, invoke the Lolla skill, call providers, mutate
archives, read raw transcripts, read raw revised answers, read raw memos,
change prompts, touch `SKILL.md`, change `scripts/skill/*`, change runtime
behavior, launch Observatory, persist revised answers, add a judge, add a
score, create automatic labels, or add agent-use authority.

The output preserves:

- `human_validated: false`
- `ground_truth: false`
- `judge_calibration_eligible: false`
- `product_proof: false`
- `answer_quality_scored: false`
- `agent_action_authorized: false`
- `model_calls: 0`
- `archive_mutated: false`
- `runtime_invoked: false`
- `skill_invoked: false`

## Inputs

PR83 used only checked-in safe artifacts:

- [Context-Engineered Provisional Review Architecture v0](context-engineered-provisional-review-architecture-v0.md)
- [Product Delta Specialist Review Contracts v0](product-delta-specialist-review-contracts-v0.md)
- [Product Delta Specialist Review Contracts JSON v0](product-delta-specialist-review-contracts-v0.json)
- [Product Delta Specialist Packet Builder v0](product-delta-specialist-packet-builder-v0.md)
- [PR81 packet fixture](../../reviews/codex-assisted/product-delta-specialist-packets-v0/packets.json)
- [Provisional Reviewer Trap Set v0](provisional-reviewer-trap-set-v0.md)
- [Provisional Reviewer Trap Set JSON v0](provisional-reviewer-trap-set-v0.json)
- [Codex-Assisted Product Delta Batch v0](codex-assisted-product-delta-batch-v0.md)
- [PR76 broad batch JSON](../../reviews/codex-assisted/product-delta-batch-v0/review.json)
- [PR75 provisional run JSON](../../reviews/codex-assisted/product-delta-provisional-run-v0/review.json)
- [PR33 human-review JSON](../../reviews/human/corpus-batch-v0/review.json)

PR76 broad reads and PR33 human-review records are used as review-safe source
context. PR83 does not treat them as new human validation, ground truth,
product proof, or specialist answers.

## Method

PR83 has two parts.

First, the trap discipline pass checks all ten PR82 trap families. This pass is
synthetic contract expectation checking. It asks whether the specialist
architecture can say "thin," "no material change," "lost value," "interpretation
concern," or "do not harden this claim" when the fixture calls for it.

Second, the real-case specialist pass fills PR80-style specialist reads for the
two cases in the PR81 checked-in packet fixture:

- `ceo-remove-founding-cofounder`
- `accept-operations-role-startup`

Each case includes:

- conversation interpretation;
- vanilla likely next action;
- Lolla likely next action;
- structural delta;
- useful/noisy friction and lost value;
- interpretation adequacy;
- advisory overclaim;
- conservative fan-in.

The fan-in preserves disagreement. It does not vote, score, average, or claim
that specialist agreement is correctness.

## Trap Discipline Result

| discipline result | count |
|---|---:|
| `met_expected_behavior` | 8 |
| `partly_met_expected_behavior` | 2 |
| `missed_expected_behavior` | 0 |
| `inconclusive` | 0 |

The two partial trap results are informative:

- `ambition_buried_by_generic_prudence`: Codex can name ambition/momentum loss,
  but cannot decide whether the user's urgency was wise without human context.
- `assistant_influence_blindness`: Codex can flag assistant influence as a
  required field, but checked-in safe summaries may compress away the stance
  shift needed to detect it in real cases.

That is a good sign for the scaffold. The trap pass did not merely find
expected "wins"; it identified where the future reviewer setup remains brittle.

## Real-Case Specialist Pass

| case | PR76 broad read | PR83 specialist fan-in | PR83 discipline delta |
|---|---|---|---|
| `ceo-remove-founding-cofounder` | `material_improvement_candidate` | `material_improvement_candidate` | Same net candidate, but interpretation adequacy is downgraded from adequate to partly adequate because checked-in safe context lacks raw conversation detail. |
| `accept-operations-role-startup` | `material_improvement_candidate` | `partial_improvement_candidate` | Downgraded because written gates look useful but lost value, value-overwrite risk, and gate proportion remain unresolved. |

Candidate distribution:

| PR83 candidate read | count |
|---|---:|
| `material_improvement_candidate` | 1 |
| `partial_improvement_candidate` | 1 |
| `no_material_change_candidate` | 0 |
| `lolla_added_noise_candidate` | 0 |
| `lolla_worse_candidate` | 0 |
| `inconclusive` | 0 |

This tiny real-case slice does not contain a no-change, noise, worse, or
inconclusive real-case read. That is a selection-risk warning, not a success
claim. Both cases came from the two-case PR81 fixture and both had prior
positive review-safe context.

PR78 lint result for the PR83 Markdown and JSON artifacts: zero blocking
errors, zero warnings, zero info findings. That result means the artifacts stay
inside the Product Delta evidence boundary; it does not validate the semantic
reads or prove product value.

## What Decomposition Improved

Compared with PR76, PR83 improved the review surface in four ways:

1. It made PR76 broad reads explicit source context rather than truth.
2. It separated structural delta from lost value and interpretation adequacy.
3. It downgraded one PR76 material candidate to partial.
4. It made source-status limits more visible, especially where raw vanilla and
   revised answers were not read.

The clearest improvement is `accept-operations-role-startup`. PR76 called it a
material improvement candidate. PR83 still sees useful written-term and
capacity gates, but the specialist split makes ambition, momentum, household
capacity, and value-overwrite risk too important to leave the net read at
material without human review.

## Lost Value And Interpretation Adequacy

Both real cases record lost-value concerns:

- `ceo-remove-founding-cofounder`: simplicity and momentum may be weaker if
  authority moves first.
- `accept-operations-role-startup`: momentum, courage, and user-specific
  ambition may be weaker if written gates over-process the decision.

Both real cases record interpretation-adequacy concerns:

- `ceo-remove-founding-cofounder`: PR76's adequate read is downgraded to partly
  adequate because raw conversation options, assistant influence, and full
  stakeholder texture are not visible in checked-in safe mode.
- `accept-operations-role-startup`: value overwrite and constraint flattening
  remain live concerns.

## What PR83 Does Not Prove

PR83 does not prove:

- Lolla improves decisions;
- PR76 was wrong;
- the specialist method is calibrated;
- trap expectations are human labels;
- the real-case reads are product evidence;
- clean artifacts imply good advice;
- an agent may act on these reads.

The strongest current claim is:

```text
Specialist decomposition appears to make the provisional review harness more
willing to preserve uncertainty, lost value, and disagreement than the broad
PR76 fill.
```

Even that claim is provisional and based on a tiny batch.

## What Future Human Review Must Check

A future human reviewer should check:

- whether the `ceo-remove-founding-cofounder` vanilla answer already required
  authority transfer and stop conditions;
- whether moving authority first preserved enough trust and momentum;
- whether the `accept-operations-role-startup` vanilla answer already required
  written operating terms;
- whether written gates protected ambition or diluted it;
- whether the PR83 downgrade is too cautious or appropriately disciplined;
- whether assistant influence and value overwrite are better detected by
  specialist decomposition than by PR76's broad fill.

## Next PR

Follow-on report:

```text
PR84 Fan-In / Disagreement Report v0
```

PR84 has now compared PR83 specialist outputs against PR76 broad reads:
[Product Delta Fan-In / Disagreement Report v0](product-delta-fan-in-disagreement-report-v0.md).

It keeps the one PR83 downgrade, both lost-value and interpretation-adequacy
concern surfaces, and the remaining positive-distribution risk visible without
creating new specialist reads or deciding that either PR76 or PR83 is correct.
