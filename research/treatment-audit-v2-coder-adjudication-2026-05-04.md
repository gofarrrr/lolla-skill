# Treatment Audit v2 Coder Adjudication - 2026-05-04

## Status Header

**Status:** Lane 2 research artifact, not measurement output.
**Tool used:** Codex CLI / GPT-5 coding agent as interactive reviewer. No additional boundary judge calls were made for this adjudication.
**Date:** 2026-05-04.
**Protocol source:** "Coder Task - Lane 2 Adjudication of v2 Activation-Gated Audit."
**Source data read:** current `data/treatment_audits/*__*.json` v2 files, `data/treatment_audits/summary.json`, and `data/compiled/model_affordances/affordances_v1.json`.
**Memory read note:** Requested `memory/feedback_*.md` files were not present as repo files in this checkout. I used the doctrine restated in the task brief: mechanistic substrate, activation before treatment, Lane 2 interactive adjudication, and the known Grok all-high-confidence pattern.

This file is a labeled reviewer-eye artifact. It does not mutate `data/`, `engine/`, or `scripts/`, and it should not be treated as generated audit metric data.

## Pre-commit Verdict Bars

Copied before adjudicating the per-item rows:

**Directionally good (proceed; finish PR 6 with grok, name limits in closeout):**
- Coder agrees with >=10 of the 13 Tier 1 calls.
- Activation calls hold up on >=6 of the 8 not_activated items (case structure genuinely doesn't fit).
- Activation notes are mostly structural (<=2 show case-type casuistry like "in family decisions" or "for negotiations").
- Confidence-distribution problem (all-high) is a known limit, not a deal-breaker for this evidence tier.

**Too noisy (rerun script with stronger judge):**
- Coder disagrees with >=4 Tier 1 calls.
- Activation calls fail on >=3 not_activated items (the case actually does fit; judge missed it).
- 2 activation notes show case-type casuistry.
- The judge's reasoning is opaque or bare-assertion-shaped on multiple items.

**Inconclusive (split verdict):**
- Anything between the two bars. Default to "directionally good with named caveats" rather than rerunning, unless the casuistry rail is breached.

**Current-data denominator note:** The raw v2 files on disk after the prompt-tightened rerun contain 14 Tier 1 rows, 5 not_activated rows, and 2 set_aside_as_misfit rows, not the 13/8/2 distribution assumed by the brief. I did not move the verdict bars. I adjudicated all current Tier 1, all current not_activated, all current set_aside rows, and 7 Tier 2/Tier 3 spot-checks to preserve the intended 28-item depth.

## Aggregate Verdict

**Verdict:** directionally good with named caveats.

The Tier 1 bar passes: I agree with 12 of 14 Tier 1 calls, mark 1 inconclusive, and disagree with 1. That clears the pre-commit >=10 agreement threshold even with the expanded current denominator. The not_activated bar is non-identical because only 5 not_activated rows exist in the current data, but all 5 hold up. The casuistry bar passes: 0 activation notes are casuistic, 4 are mixed, 24 are structural, and 0 are bare. The all-high confidence distribution remains a real limitation, but not enough to discard this PR 6 calibration evidence.

**Do not overclaim:** This says activation gating is directionally working. It does not say Grok is a good final judge for promotion-grade evidence. The confidence bucket is still informationless, and one Tier 1 call (`theory-of-constraints.constraint-shift-cadence` on the PhD case) looks like a real activation mistake.

Aggregate counts from the per-item tables:

| Category | Items | Agree | Disagree | Inconclusive |
| --- | ---: | ---: | ---: | ---: |
| Tier 1 | 14 | 12 | 1 | 1 |
| not_activated | 5 | 5 | 0 | 0 |
| set_aside_as_misfit | 2 | 2 | 0 | 0 |
| Tier 2/Tier 3 spot-checks | 7 | 7 | 0 | 0 |
| Total | 28 | 26 | 1 | 1 |

## Per-item Adjudication Tables

### Tier 1

| case | affordance | judge_call | your_label | confidence | disconfirming_sentence | activation_note_type | one-line rationale |
| --- | --- | --- | --- | --- | --- | --- | --- |
| founder-grant-marcus-equity | systems-thinking.feedback-loop-mapping | activated / not_treated / new_finding | agree_with_judge | medium | This call would be wrong if the route-trace or output already represented the equity decision as a reinforcing or balancing loop rather than a sequence of risks. | structural | The case has interacting actors, incentives, delays, and follow-on risk; the output critiques pieces without mapping loop dynamics. |
| founder-grant-marcus-equity | systems-thinking.metric-leverage-design | activated / not_treated / new_finding | agree_with_judge | medium | This call would be wrong if metric-leverage-design requires a pre-existing formal system map rather than a causal story with goal, process, levers, and progress signals. | structural | The case has retention/platform metrics and intervention choices, but the output does not turn them into a goal-process-lever-signal chain. |
| mid-level-consultant-report-2 | optionality.expand-before-evaluating | activated / partially_treated / new_finding | agree_with_judge | high | This call would be wrong if the output's mention of alternate career paths already counted as a visible option array with economic comparison. | structural | The output names binary collapse but still lacks three viable paths and explicit payoff/cost comparison before recommendation. |
| mid-level-consultant-report-2 | second-order-thinking.downstream-reversal-stress-test | activated / partially_treated / new_finding | agree_with_judge | high | This call would be wrong if modeling the partner's possible reaction is enough without checking repeated adaptations by counsel, firm leadership, or surrounding actors. | structural | The answer catches the partner-reaction reversal threshold but does not fully stress-test behavioral adaptation. |
| mid-level-consultant-report-2 | systems-thinking.feedback-loop-mapping | activated / not_treated / new_finding | agree_with_judge | medium | This call would be wrong if the reporting decision is sufficiently linear that loop mapping would add only decorative complexity. | structural | The case has delayed effects across partner, counsel, firm, regulator, and career incentives; no loop or delay map appears. |
| mother-deciding-address-year | confidence-calibration.commitment-sizing-to-earned-range | activated / not_treated / new_finding | agree_with_judge | medium | This call would be wrong if commitment-sizing requires an explicit numerical confidence claim rather than action thresholds sized to uncertainty. | structural | The output recommends high-stakes commitments and triggers without naming confidence ranges or lower-bound action changes. |
| mother-deciding-address-year | confidence-calibration.instrument-trust-before-precision | activated / partially_treated / new_finding | agree_with_judge | medium | This call would be wrong if replacing a vague timeline with behavior triggers fully satisfies instrument-trust auditing. | structural | The output questions behavioral-signal trust, but does not audit the surveillance/data-generating process enough to close the affordance. |
| third-year-phd-student | base-rates.outside-view-reference-class-anchor | activated / partially_treated / new_finding | agree_with_judge | high | This call would be wrong if naming "20-30% success on novel combinations" already defines and tests the reference class. | structural | The output uses a prior but skips structural fit testing and explicit updates from lab/advisor constraints. |
| third-year-phd-student | confidence-calibration.commitment-sizing-to-earned-range | activated / partially_treated / new_finding | agree_with_judge | medium | This call would be wrong if the dissertation recommendation is only exploratory and not a commitment controlled by forecast bounds. | structural | Forecast numbers and timelines drive a major direction choice, but the action is not resized to earned uncertainty bounds. |
| third-year-phd-student | confidence-calibration.instrument-trust-before-precision | activated / partially_treated / new_finding | inconclusive | low | Evidence available cannot distinguish "instrument-trust gap" from "general epistemic-source critique" because the row points to social-proof and consensus more than a clean metric/model output. | structural | There is a data-process concern, but the affordance fit is less clean than the judge's high confidence suggests. |
| third-year-phd-student | problem-framing-and-reframing.define-before-analysis | activated / partially_treated / new_finding | agree_with_judge | high | This call would be wrong if the output's statement that the option space needs testing already states the core decision question and minimum analysis output. | structural | The output notices fixed-option framing but does not restate the decision-worthy question, actors, constraints, and needed evidence. |
| third-year-phd-student | problem-framing-and-reframing.test-alternative-frames | activated / partially_treated / new_finding | agree_with_judge | high | This call would be wrong if naming the fixed-option problem is equivalent to comparing distinct frames. | structural | The output flags narrow framing but does not generate and compare alternative frames. |
| third-year-phd-student | theory-of-constraints.constraint-shift-cadence | activated / not_treated / new_finding | disagree_with_judge | high | This call would be right if there were already post-change evidence showing an original bottleneck moved and a new constraint needed retesting. | structural | The affordance requires retesting after a bottleneck shift; this is a pre-decision case, so activation looks premature. |
| user-launch-independent-fintech | base-rates.outside-view-reference-class-anchor | activated / partially_treated / new_finding | agree_with_judge | high | This call would be wrong if applying the under-1-in-5 conversion frequency already defines and tests the reference class. | structural | The output applies a frequency to pipeline math but skips reference-class fit assumptions and update discipline. |

### not_activated

| case | affordance | judge_call | your_label | confidence | disconfirming_sentence | activation_note_type | one-line rationale |
| --- | --- | --- | --- | --- | --- | --- | --- |
| founder-grant-marcus-equity | systems-thinking.architecture-misdiagnosis-test | not_activated / not_applicable / excluded | agree_with_judge | high | This call would be wrong if the equity-platform decision actually proposed a technical rewrite in response to recurring failures. | mixed | The note includes domain nouns, but its operative reason is structural absence of recurring failure and architecture rewrite. |
| mid-level-consultant-report-2 | systems-thinking.architecture-misdiagnosis-test | not_activated / not_applicable / excluded | agree_with_judge | high | This call would be wrong if the reporting case contained a proposed redesign meant to solve recurring system failures. | structural | No rewrite, recurring architecture failure, or social-system-before-rewrite test is present. |
| mid-level-consultant-report-2 | systems-thinking.metric-leverage-design | not_activated / not_applicable / excluded | agree_with_judge | medium | This call would be wrong if the firm-reporting causal story already gave enough of a system map to require metric-lever design. | structural | The case has multi-actor dynamics but not a system map being converted into measured intervention points. |
| mother-deciding-address-year | confidence-calibration.method-first-self-interrogation | not_activated / not_applicable / excluded | agree_with_judge | high | This call would be wrong if the output or case contained a stated confidence number plus reasons and a method needing self-interrogation. | structural | The case has uncertainty, but not the confidence-claim/method-audit shape of this affordance. |
| mother-deciding-address-year | power-dynamics.commitment-gradient-inversion | not_activated / not_applicable / excluded | agree_with_judge | medium | This call would be wrong if custody, therapy, or surveillance created a true leverage-inversion milestone comparable to deal lock-in. | structural | There are commitments and rising costs, but not counterparty leverage inversion through operational lock-in milestones. |

### set_aside_as_misfit

| case | affordance | judge_call | your_label | confidence | disconfirming_sentence | activation_note_type | one-line rationale |
| --- | --- | --- | --- | --- | --- | --- | --- |
| mid-level-consultant-report-2 | power-dynamics.commitment-gradient-inversion | set_aside_as_misfit / set_aside_with_reason / excluded | agree_with_judge | high | This call would be wrong if the output merely ignored the affordance instead of explicitly explaining why its leverage vocabulary did not fit. | mixed | The output explicitly sets aside the leverage lens and reroutes the reversibility instinct to commitment staging. |
| mid-level-consultant-report-2 | power-dynamics.outside-option-credibility | set_aside_as_misfit / set_aside_with_reason / excluded | agree_with_judge | high | This call would be wrong if the reporting decision actually depended on credible walk-away, fallback capacity, or bargaining terms. | mixed | The output says the power lens does not fit; the domain wording is mixed, but the reason is structural absence of bargaining leverage. |

### Tier 2 / Tier 3 Spot-checks

| case | affordance | judge_call | your_label | confidence | disconfirming_sentence | activation_note_type | one-line rationale |
| --- | --- | --- | --- | --- | --- | --- | --- |
| founder-grant-marcus-equity | base-rates.outside-view-reference-class-anchor | activated / duplicate_of_existing_pressure / tier_3 | agree_with_judge | high | This call would be wrong if the Pressure Check only gestured at valuation risk without covering reference-class/multiple testing. | structural | The baseline already questions the exit multiple and its fit, so duplicate classification is fair. |
| founder-grant-marcus-equity | optionality.expand-before-evaluating | activated / duplicate_of_existing_pressure / tier_3 | agree_with_judge | high | This call would be wrong if the Pressure Check did not actually surface the missing middle option set. | structural | Pressure Check directly names skipped middle options, including phantom equity and milestone grants. |
| founder-grant-marcus-equity | optionality.preserve-reversible-learning | activated / partially_treated / tier_2 | agree_with_judge | medium | This call would be wrong if the 90-day validation sprint already states the commitment boundary and downside cap. | structural | The output has a reversible experiment shape but still lacks full reversibility classification and threshold discipline. |
| mother-deciding-address-year | base-rates.outside-view-reference-class-anchor | activated / duplicate_of_existing_pressure / tier_3 | agree_with_judge | medium | This call would be wrong if mentioning base rates to persuade the co-parent is not enough to duplicate the Pressure Check's existing coverage. | structural | Duplicate is plausible, but the row also shows why duplicate examples still need reviewer-eye because structural reference-class testing is thin. |
| third-year-phd-student | optionality.expand-before-evaluating | activated / partially_treated / tier_2 | agree_with_judge | high | This call would be wrong if saying the option space needs testing already generated the expanded option set. | structural | The output recognizes the narrowed option space but does not visibly expand and compare it. |
| third-year-phd-student | theory-of-constraints.constraint-first-cap | activated / partially_treated / tier_2 | agree_with_judge | medium | This call would be wrong if naming data access as the bottleneck without quantification is enough to satisfy constraint-first treatment. | structural | Constraint-first activation is cleaner than constraint-shift-cadence here; the output names a bottleneck but not a cap or movement forecast. |
| user-launch-independent-fintech | optionality.preserve-reversible-learning | activated / partially_treated / tier_2 | agree_with_judge | medium | This call would be wrong if the signed-LOI checkpoint already states full reversibility, expected learning, downside cap, and expiration. | structural | The answer uses a reversible learning gate but does not fully specify optionality boundaries. |

## Casuistry Watch Summary

Activation-note type counts across the 28 adjudicated rows:

| activation_note_type | Count |
| --- | ---: |
| structural | 24 |
| mixed | 4 |
| casuistic | 0 |
| bare | 0 |

No activation note crossed my threshold for true casuistry: none says, in effect, "because this is a family/startup/negotiation case, apply or skip the affordance." Four notes are mixed because they include domain or setting language while still giving structural reasons:

- `systems-thinking.architecture-misdiagnosis-test` on founder-grant: mentions the equity/title context, but the actual reason is absence of recurring failure and architecture rewrite.
- `power-dynamics.commitment-gradient-inversion` on consultant-report: mentions non-negotiated reporting, but the structural point is absence of operational lock-in / leverage inversion.
- `power-dynamics.outside-option-credibility` on consultant-report: mentions reporting/crime context, but the structural point is absence of walk-away bargaining.
- Some reference-class rows name their domain to identify a reference class. I counted those as structural, not casuistic, when the domain noun served the mechanism.

The strongest casuistry warning is not in the adjudicated metric itself but in phrasing hygiene: the judge still reaches for domain nouns even after being told not to. That is a prompt-quality limitation, not yet a reason to discard the v2 evidence.

## Second-pass Disagreement List

Five labels I least trust:

1. `third-year-phd-student / theory-of-constraints.constraint-shift-cadence` - I disagree high-confidence, but it is still possible that the output's staged probes create enough of a retest cadence to count as weak activation.
2. `third-year-phd-student / confidence-calibration.instrument-trust-before-precision` - inconclusive; the row blends social-proof critique, base-rate reliability, and data-process auditing.
3. `founder-grant-marcus-equity / systems-thinking.metric-leverage-design` - agree medium; the activation depends on treating the equity-retention causal story as enough of a system map.
4. `mother-deciding-address-year / confidence-calibration.commitment-sizing-to-earned-range` - agree medium; the affordance fit is real, but less clean without a named forecast number.
5. `mid-level-consultant-report-2 / systems-thinking.feedback-loop-mapping` - agree medium; useful if the operator wants dynamic diagnosis, but there is risk of systems-thinking over-breadth.

Three labels most likely to change after Marcin review:

1. `third-year-phd-student / confidence-calibration.instrument-trust-before-precision`.
2. `founder-grant-marcus-equity / systems-thinking.metric-leverage-design`.
3. `mother-deciding-address-year / confidence-calibration.commitment-sizing-to-earned-range`.

Prior-influence pattern:

I came in sensitized to casuistry because this task was explicitly framed around that rail. That could make me over-penalize activation notes that merely contain domain nouns. I tried to counteract that by separating "mixed" from "casuistic" and reserving "casuistic" for rules that use case type as the reason rather than structural fit.

## Implications For PR 6

PR 6 can continue toward closeout with the current Grok-generated v2 audit as calibration evidence, but the closeout must name limits clearly:

- The evidence map is cleaner after activation gating: current raw v2 has 14 Tier 1 rows, 5 not_activated rows, and 2 set_aside_as_misfit rows.
- The judge still returns high confidence for every row, so confidence remains information-poor.
- One Tier 1 row appears wrongly activated (`theory-of-constraints.constraint-shift-cadence` on the PhD case). This is not enough to rerun by the pre-commit bars, but it should be named as a review candidate.
- The stale generated adjudication artifacts that assumed 13 Tier 1 and 8 not_activated rows should not be treated as current after the prompt-tightened rerun. Future PR 6 reports should use the current raw v2 summary, not the stale counts.

Recommended next move: resume PR 6 implementation, finish the calibration report/tests using the current v2 data, and explicitly mark Grok as acceptable for calibration-grade evidence but not yet promotion-grade evidence. A stronger judge rerun is justified before any PR 7 promotion claim, not required to complete PR 6's calibration purpose.
