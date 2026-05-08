# Treatment Audit Calibration Report - PR6

**Status:** Activation-gated calibration artifact. This report compares PR5 v1 ungated audit output with PR6 v2 activation-gated audit output.

## Headline

PR6 reduced merge-gate candidate findings from 26 ungated candidates to 14 Tier 1 activation-gated net-new decision gaps. V2 also reports 11 Tier 2 additional-specificity items, 5 Tier 3 duplicate/quality notes, and 21 excluded items. That is a cleaner evidence map, not clean proof. The audit now separates selected-model affordances that were structurally active from affordances the judge marked inactive or set aside as misfit.

Lane 2 coder adjudication (`research/treatment-audit-v2-coder-adjudication-2026-05-04.md`, commit `b1c07d5`) accepted this as calibration-grade evidence: 12 of 14 Tier 1 calls agreed, 1 disagreed, 1 was inconclusive, and the casuistry watch found 0 casuistic activation notes across 28 reviewed items.

## V1 vs V2 counts

### Treatment status

| Treatment status | V1 count | V2 count |
| --- | ---: | ---: |
| duplicate_of_existing_pressure | 5 | 4 |
| not_applicable | 2 | 5 |
| not_treated | 19 | 6 |
| partially_treated | 13 | 25 |
| set_aside_with_reason | 3 | 2 |
| treated | 9 | 9 |

### Evidence tier

| Tier | V1 count | V2 count |
| --- | ---: | ---: |
| Raw merge-gate candidates / Tier 1 net-new decision gaps | 26 | 14 |
| Tier 2 additional operational specificity | n/a | 11 |
| Tier 3 duplicate or quality note | n/a | 5 |
| Excluded | n/a | 21 |

### Activation status

| Activation status | Count |
| --- | ---: |
| activated | 44 |
| not_activated | 5 |
| set_aside_as_misfit | 2 |

### Baseline coverage

| Baseline coverage | V1 count | V2 count |
| --- | ---: | ---: |
| additional_specificity | 12 | 17 |
| duplicate_of_existing_pressure | 6 | 6 |
| new_finding | 29 | 20 |
| not_a_finding | 4 | 8 |

## Merge-gate changes

| Run | Model | Affordance | V1 | V2 activation | V2 treatment | V2 tier |
| --- | --- | --- | --- | --- | --- | --- |
| founder-grant-marcus-equity__20260428T064421Z | optionality | optionality.preserve-reversible-learning | partially_treated | activated | partially_treated | tier_2_additional_operational_specificity |
| founder-grant-marcus-equity__20260428T064421Z | problem-framing-and-reframing | problem-framing-and-reframing.define-before-analysis | partially_treated | activated | partially_treated | tier_2_additional_operational_specificity |
| founder-grant-marcus-equity__20260428T064421Z | problem-framing-and-reframing | problem-framing-and-reframing.test-alternative-frames | not_treated | activated | partially_treated | tier_2_additional_operational_specificity |
| founder-grant-marcus-equity__20260428T064421Z | second-order-thinking | second-order-thinking.downstream-reversal-stress-test | not_treated | activated | partially_treated | tier_2_additional_operational_specificity |
| mid-level-consultant-report-2__20260429T144611Z | optionality | optionality.preserve-reversible-learning | partially_treated | activated | partially_treated | tier_2_additional_operational_specificity |
| mid-level-consultant-report-2__20260429T144611Z | systems-thinking | systems-thinking.metric-leverage-design | not_treated | not_activated | not_applicable | excluded |
| mother-deciding-address-year__20260430T113301Z | power-dynamics | power-dynamics.commitment-gradient-inversion | not_treated | not_activated | not_applicable | excluded |
| mother-deciding-address-year__20260430T113301Z | power-dynamics | power-dynamics.outside-option-credibility | not_treated | activated | duplicate_of_existing_pressure | tier_3_duplicate_or_quality_note |
| third-year-phd-student__20260430T140800Z | optionality | optionality.expand-before-evaluating | not_treated | activated | partially_treated | tier_2_additional_operational_specificity |
| third-year-phd-student__20260430T140800Z | optionality | optionality.preserve-reversible-learning | partially_treated | activated | partially_treated | tier_3_duplicate_or_quality_note |
| third-year-phd-student__20260430T140800Z | theory-of-constraints | theory-of-constraints.constraint-first-cap | partially_treated | activated | partially_treated | tier_2_additional_operational_specificity |
| user-launch-independent-fintech__20260424T123050Z | confidence-calibration | confidence-calibration.commitment-sizing-to-earned-range | partially_treated | activated | partially_treated | tier_2_additional_operational_specificity |

## Tier 1 activation-gated wins

| Run | Model | Affordance | Activation | Treatment | Tier | Finding |
| --- | --- | --- | --- | --- | --- | --- |
| founder-grant-marcus-equity__20260428T064421Z | systems-thinking | systems-thinking.feedback-loop-mapping | activated | not_treated | tier_1_net_new_decision_gap | Failed to map feedback loops in retention risk and equity decision despite distributed actors and downstream effects. |
| founder-grant-marcus-equity__20260428T064421Z | systems-thinking | systems-thinking.metric-leverage-design | activated | not_treated | tier_1_net_new_decision_gap | Failed to convert retention and platform risks into goal-process-lever-metric chains with progress signals. |
| mid-level-consultant-report-2__20260429T144611Z | optionality | optionality.expand-before-evaluating | activated | partially_treated | tier_1_net_new_decision_gap | Partially treats optionality by noting binary career collapse but fails to expand to three+ options with economic comparison. |
| mid-level-consultant-report-2__20260429T144611Z | second-order-thinking | second-order-thinking.downstream-reversal-stress-test | activated | partially_treated | tier_1_net_new_decision_gap | Partially treats downstream reversal by modeling partner reaction threshold but misses behavioral adaptation check. |
| mid-level-consultant-report-2__20260429T144611Z | systems-thinking | systems-thinking.feedback-loop-mapping | activated | not_treated | tier_1_net_new_decision_gap | Missing dynamic feedback loop mapping for distributed actors and delayed effects in reporting decision. |
| mother-deciding-address-year__20260430T113301Z | confidence-calibration | confidence-calibration.commitment-sizing-to-earned-range | activated | not_treated | tier_1_net_new_decision_gap | Output recommends actions with triggers but does not calibrate commitments to earned confidence ranges. |
| mother-deciding-address-year__20260430T113301Z | confidence-calibration | confidence-calibration.instrument-trust-before-precision | activated | partially_treated | tier_1_net_new_decision_gap | Partially treated surveillance metric trust by questioning signal reliability but missing full process audit. |
| third-year-phd-student__20260430T140800Z | base-rates | base-rates.outside-view-reference-class-anchor | activated | partially_treated | tier_1_net_new_decision_gap | Partially treats base-rates by naming novel PhD success rate prior but skips reference class fit test and case-specific updating. |
| third-year-phd-student__20260430T140800Z | confidence-calibration | confidence-calibration.commitment-sizing-to-earned-range | activated | partially_treated | tier_1_net_new_decision_gap | Partially treats confidence calibration by naming base rate forecast driving commitment but skips sizing action to earned uncertainty range. |
| third-year-phd-student__20260430T140800Z | confidence-calibration | confidence-calibration.instrument-trust-before-precision | activated | partially_treated | tier_1_net_new_decision_gap | Partially treated by auditing social-proof but missed scrutinizing data processes behind base rates and consensus claims. |
| third-year-phd-student__20260430T140800Z | problem-framing-and-reframing | problem-framing-and-reframing.define-before-analysis | activated | partially_treated | tier_1_net_new_decision_gap | Partially treats problem-framing by naming the issue of unexamined option assumptions but skips stating decision question and required analysis. |
| third-year-phd-student__20260430T140800Z | problem-framing-and-reframing | problem-framing-and-reframing.test-alternative-frames | activated | partially_treated | tier_1_net_new_decision_gap | Partially treats problem-framing by noting fixed options limit but skips frame comparison and assumption testing. |
| third-year-phd-student__20260430T140800Z | theory-of-constraints | theory-of-constraints.constraint-shift-cadence | activated | not_treated | tier_1_net_new_decision_gap | Missing retest of shifted constraints after probing data access bottleneck before committing to option 3. |
| user-launch-independent-fintech__20260424T123050Z | base-rates | base-rates.outside-view-reference-class-anchor | activated | partially_treated | tier_1_net_new_decision_gap | Partially treats base rates by applying conversion frequency to pipeline but skips defining/testing reference class fit. |

## Correctly inactive or set aside

These items are not treatment-gap evidence after activation gating.

### Not activated

| Run | Model | Affordance | Activation | Treatment | Tier | Finding |
| --- | --- | --- | --- | --- | --- | --- |
| founder-grant-marcus-equity__20260428T064421Z | systems-thinking | systems-thinking.architecture-misdiagnosis-test | not_activated | not_applicable | excluded | Not activated: no recurring failure or architecture rewrite in equity grant decision. |
| mid-level-consultant-report-2__20260429T144611Z | systems-thinking | systems-thinking.architecture-misdiagnosis-test | not_activated | not_applicable | excluded | No activation of architecture-misdiagnosis-test affordance due to lack of rewrite proposal or recurring failure pattern in case. |
| mid-level-consultant-report-2__20260429T144611Z | systems-thinking | systems-thinking.metric-leverage-design | not_activated | not_applicable | excluded | No system map or causal story exists to convert into measured leverage points. |
| mother-deciding-address-year__20260430T113301Z | confidence-calibration | confidence-calibration.method-first-self-interrogation | not_activated | not_applicable | excluded | No confidence calibration affordance activated in case or output. |
| mother-deciding-address-year__20260430T113301Z | power-dynamics | power-dynamics.commitment-gradient-inversion | not_activated | not_applicable | excluded | No activation of commitment-gradient leverage inversion in family co-parenting context. |

### Set aside as misfit

| Run | Model | Affordance | Activation | Treatment | Tier | Finding |
| --- | --- | --- | --- | --- | --- | --- |
| mid-level-consultant-report-2__20260429T144611Z | power-dynamics | power-dynamics.commitment-gradient-inversion | set_aside_as_misfit | set_aside_with_reason | excluded | Power-dynamics commitment-gradient inversion explicitly set aside as misfit for non-negotiated reporting decision. |
| mid-level-consultant-report-2__20260429T144611Z | power-dynamics | power-dynamics.outside-option-credibility | set_aside_as_misfit | set_aside_with_reason | excluded | Power-dynamics affordance correctly set aside as structurally misfit to non-negotiated crime-reporting scenario. |

## Review candidates

- unclear_activation: 0
- activation_shape_missing: 0

No affordance records were edited in this PR. Any recurring unclear or missing activation shape is a candidate for separate reviewed-extraction work, not an in-place calibration edit.

## Token cost

| Version | Prompt tokens | Completion tokens | Total tokens |
| --- | ---: | ---: | ---: |
| v1 ungated | 271871 | 7787 | 279658 |
| v2 activation-gated | 323813 | 13051 | 336864 |
| Delta | n/a | n/a | +57206 |

V2 judge: `x-ai/grok-4.1-fast` via `openrouter`. V2 required 53 judge calls and produced 2 validation rejections.

## Named limitations

- The judge (`x-ai/grok-4.1-fast`) returned `confidence: high` for every item. The confidence axis is informationless and must not be used for prioritization.
- This is calibration-grade evidence, not promotion-grade evidence. Any user-facing promotion experiment needs a stronger judge model through the same OpenRouter boundary before relying on these counts.
- Lane 2 disagreement: One Tier 1 row appears wrongly activated (`theory-of-constraints.constraint-shift-cadence` on the PhD case). This is not enough to rerun by the pre-commit bars, but it should be named as a review candidate.
- No affordance record was edited for that disagreement; it is a review candidate only.

## What this report deliberately omits

- No completeness scoring.
- No quality grade.
- No promotion recommendation.
- No automated affordance edits.

## Doctrine checks

- Python did not determine activation. It passed activation_shape and case context to the judge, then validated enum values, exact quotes, and deterministic evidence tiers.
- No case-category exception lists were added.
- No affordance JSON files were modified.
- set_aside_with_reason is excluded from Tier 1 merge-gate evidence.
- The all-high confidence pattern remains: v2 confidence distribution is still high for every item, so confidence remains information-poor.
