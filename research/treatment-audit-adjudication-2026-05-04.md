# Treatment Audit Adjudication - 2026-05-04

**Status:** v2 activation-gated evidence map. This replaces the inconsistent v1 PM pass and should be read as calibration evidence, not final semantic proof.
**Source data:** `data/treatment_audits/*.json` (schema `model_treatment_audit.v2`).
**Items adjudicated:** 51.

## Headline

Ungated PR5 reported 26 merge-gate candidates. Activation-gated PR6 reports 14 Tier 1 net-new decision gaps, 11 Tier 2 additional-specificity items, and 5 Tier 3 duplicate/quality notes.

The evidence is cleaner because inactive and set-aside affordances no longer count as treatment gaps. It is not clean proof because the judge still returns high confidence for every item, and reviewer-eye must still decide whether Tier 1 examples are decision-changing.

## Label distribution

| Label | Count |
| --- | ---: |
| active_additional_specificity | 11 |
| active_net_new_treatment_gap | 14 |
| baseline_duplicate_or_quality_note | 5 |
| correct_treatment | 9 |
| excluded_not_a_finding | 5 |
| inactive_or_unclear_activation | 5 |
| set_aside_as_misfit | 2 |

## Activation distribution

| Activation status | Count |
| --- | ---: |
| activated | 44 |
| not_activated | 5 |
| set_aside_as_misfit | 2 |

## Tier 1 items

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

## Items changed by activation gating

| Run | Model | Affordance | Activation | Treatment | Tier | Finding |
| --- | --- | --- | --- | --- | --- | --- |
| founder-grant-marcus-equity__20260428T064421Z | optionality | optionality.preserve-reversible-learning | activated | partially_treated | tier_2_additional_operational_specificity | Partially treats optionality by affirming 90-day platform validation sprint but omits reversibility classification and commitment boundary. |
| founder-grant-marcus-equity__20260428T064421Z | problem-framing-and-reframing | problem-framing-and-reframing.define-before-analysis | activated | partially_treated | tier_2_additional_operational_specificity | Partially treats problem-framing by stating core question but skips bounding analysis evidence needs. |
| founder-grant-marcus-equity__20260428T064421Z | problem-framing-and-reframing | problem-framing-and-reframing.test-alternative-frames | activated | partially_treated | tier_2_additional_operational_specificity | Partially treats problem-framing by affirming one reframe as key but skips systematic comparison of distinct frames and their assumptions. |
| founder-grant-marcus-equity__20260428T064421Z | second-order-thinking | second-order-thinking.downstream-reversal-stress-test | activated | partially_treated | tier_2_additional_operational_specificity | Partially treats downstream reversal by noting precedent risk of ad-hoc equity grants teaching pressure tactics to future seniors. |
| mid-level-consultant-report-2__20260429T144611Z | optionality | optionality.preserve-reversible-learning | activated | partially_treated | tier_2_additional_operational_specificity | Partially treats optionality by separating reversible counsel engagement from irreversible reporting commitment, but omits downside caps and commitment triggers. |
| mid-level-consultant-report-2__20260429T144611Z | systems-thinking | systems-thinking.metric-leverage-design | not_activated | not_applicable | excluded | No system map or causal story exists to convert into measured leverage points. |
| mother-deciding-address-year__20260430T113301Z | power-dynamics | power-dynamics.commitment-gradient-inversion | not_activated | not_applicable | excluded | No activation of commitment-gradient leverage inversion in family co-parenting context. |
| mother-deciding-address-year__20260430T113301Z | power-dynamics | power-dynamics.outside-option-credibility | activated | duplicate_of_existing_pressure | tier_3_duplicate_or_quality_note | Co-parent leverage mapping duplicates Pressure Check's ex information-weaponization coverage. |
| third-year-phd-student__20260430T140800Z | optionality | optionality.expand-before-evaluating | activated | partially_treated | tier_2_additional_operational_specificity | Partially treats optionality by noting narrowed space and suggesting search for new options but skips generating visible expanded set. |
| third-year-phd-student__20260430T140800Z | optionality | optionality.preserve-reversible-learning | activated | partially_treated | tier_3_duplicate_or_quality_note | Partially treats optionality via reversal triggers but skips naming cheap reversible learning moves. |
| third-year-phd-student__20260430T140800Z | theory-of-constraints | theory-of-constraints.constraint-first-cap | activated | partially_treated | tier_2_additional_operational_specificity | Theory-of-Constraints partially treated: names binding constraint but omits quantified cap and throughput forecasts. |
| user-launch-independent-fintech__20260424T123050Z | confidence-calibration | confidence-calibration.commitment-sizing-to-earned-range | activated | partially_treated | tier_2_additional_operational_specificity | Partially treats by resizing checkpoint to base rate uncertainty but misses full lower-bound action comparison. |

## Review notes

- `additional_specificity` is counted as substrate value at a lower tier than net-new decision gaps.
- `set_aside_with_reason` is positive audit signal but not treatment-gap evidence.
- Activation gating must stay semantic at the LLM edge. This artifact does not justify Python case-type rules.
- No affordance record edits were made; unclear activation shape would be separate reviewed-extraction work.
