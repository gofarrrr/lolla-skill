# PR55 V18 Full-Corpus Distribution Audit

**Date:** 2026-05-08
**Status:** deterministic research audit; no runtime, prompt, lane, memo, UI,
Observatory, `/lolla`, or user-facing behavior changed
**Decision label:** `v18_distribution_audit_complete`
**Source artifact:** `data/compiled/model_affordances/affordances_v18.json`

## Verdict

v18 passes as a dormant reviewed substrate. It does not yet pass as a runtime
pickup substrate.

The distribution is strong enough to say the extraction program completed
reviewed source-backed coverage. It is not strong enough to say the receiver
packet can safely treat all reviewed records as equally ready for LLM use.

The main distribution risk is not missing coverage. It is false equality:

> After v18, every runtime shelf has a reviewed record, but the records differ
> in depth, support strength, absence pressure, and packet suitability.

## Input And Method

Inputs:

- `data/compiled/model_affordances/affordances_v18.json`
- `data/compiled/model_affordances/quality_report_v18.md`
- selected source files under `data/model_sources/`
- packet code under `engine/system_b/reasoning_substrate_packet.py`
- review renderer under `engine/system_b/reasoning_substrate_packet_review.py`

Method:

- local `jq` and read-only source inspection;
- no model calls;
- no judges;
- no extraction;
- no packet writes;
- no runtime imports.

## Top-Level Counts

| Measure | Count / value |
| --- | ---: |
| Artifact | `model_affordances_v18` |
| Status | `draft_review_only` |
| Reviewed model records | 222 |
| Reviewed affordances | 258 |
| Absence records | 429 |
| Schema validation failures | 0 |
| Source quote rejections | 0 |

## Record Status Distribution

| Record status | Count |
| --- | ---: |
| `supported` | 220 |
| `weak_support` | 2 |

The two weak-support records are:

| Model | Affordance | Confidence | Absences |
| --- | --- | --- | ---: |
| `devops-and-continuous-integration` | `devops-and-continuous-integration.build-observe-adjust-loop` | `medium` | 2 |
| `price-discrimination` | `price-discrimination.segment-offer-by-value-evidence` | `medium` | 2 |

Runtime implication: these must not render as ordinary high-confidence reviewed
cards. They need visible warning treatment before any receiver use.

## Affordance Status And Confidence

| Affordance status | Count |
| --- | ---: |
| `supported` | 256 |
| `weak_support` | 2 |

| Confidence | Count |
| --- | ---: |
| `high` | 251 |
| `medium` | 7 |
| `weak` | 0 |

Medium-confidence records:

| Model | Record status | Affordance |
| --- | --- | --- |
| `adverse-selection` | `supported` | `adverse-selection.verify-hidden-type-selection` |
| `batna` | `supported` | `batna.credible-walk-away-alternative-test` |
| `devops-and-continuous-integration` | `weak_support` | `devops-and-continuous-integration.build-observe-adjust-loop` |
| `markov-chains` | `supported` | `markov-chains.state-transition-boundary-check` |
| `price-discrimination` | `weak_support` | `price-discrimination.segment-offer-by-value-evidence` |
| `principal-agent-problem` | `supported` | `principal-agent-problem.delegated-alignment-drift-audit` |
| `six-thinking-hats` | `supported` | `six-thinking-hats.separate-modes-before-synthesis` |

Runtime implication: confidence must be visible in receiver handoff. The current
review renderer does not show it as a first-class line.

## Affordances Per Model

| Affordances per model | Model count |
| ---: | ---: |
| 1 | 194 |
| 2 | 21 |
| 3 | 6 |
| 4 | 1 |

This distribution is not accidental. The early v3 kernel was heterogeneous:

| Artifact | Distribution |
| --- | --- |
| `affordances_v3` | `1:22`, `2:21`, `3:6`, `4:1` |
| `affordances_v18` | `1:194`, `2:21`, `3:6`, `4:1` |

From v4 onward, every newly added model contributed exactly one affordance.
That was a useful coverage-mode rail. It is now a potential under-extraction
red flag for runtime pickup.

PR55 should not assume one affordance is wrong. It should ask whether the one
affordance preserves all transaction-distinct behavior needed by the receiver.

## Absence Records Per Model

| Absence records per model | Model count |
| ---: | ---: |
| 0 | 11 |
| 1 | 6 |
| 2 | 192 |
| 3 | 13 |

Records with zero absence records:

| Model | Affordances | Status |
| --- | ---: | --- |
| `confidence-calibration` | 3 | `supported` |
| `decision-trees` | 2 | `supported` |
| `inversion` | 3 | `supported` |
| `lindy-effect` | 1 | `supported` |
| `optionality` | 2 | `supported` |
| `power-dynamics` | 2 | `supported` |
| `premortem` | 1 | `supported` |
| `second-order-thinking` | 1 | `supported` |
| `sunk-cost-fallacy` | 1 | `supported` |
| `systems-thinking` | 4 | `supported` |
| `theory-of-constraints` | 2 | `supported` |

Interpretation:

- Zero absence does not automatically mean weak review.
- But zero absence plus broad scope should be red-flagged before runtime pickup.
- `systems-thinking`, `confidence-calibration`, and `inversion` already appear
  in `quality_report_v18.md` as do-not-runtime-promote-without-rewrite-review
  items.

## Source Evidence Span Distribution

| Source refs per affordance | Affordance count |
| ---: | ---: |
| 3 | 140 |
| 4 | 19 |
| 5 | 14 |
| 6 | 18 |
| 7 | 8 |
| 8 | 15 |
| 9 | 11 |
| 10 | 7 |
| 11 | 6 |
| 12 | 4 |
| 13 | 4 |
| 14 | 1 |
| 15 | 5 |
| 16 | 2 |
| 17 | 1 |
| 18 | 3 |

One-affordance records with high source-evidence count:

| Model | Affordance | Source refs | Absences |
| --- | --- | ---: | ---: |
| `antifragility` | `antifragility.bounded-stress-learning-design` | 18 | 3 |
| `sunk-cost-fallacy` | `sunk-cost-fallacy.future-value-recommitment` | 18 | 0 |
| `johari-window` | `johari-window.specific-feedback-disclosure-loop` | 17 | 2 |
| `base-rates` | `base-rates.outside-view-reference-class-anchor` | 16 | 1 |
| `expected-value` | `expected-value.probability-weighted-payoff-boundary` | 16 | 1 |
| `anchoring` | `anchoring.provisional-anchor-with-correction` | 15 | 2 |
| `flow` | `flow.calibrated-immersion-channel` | 15 | 2 |
| `resilience` | `resilience.disciplined-recovery-with-continued-function` | 15 | 3 |
| `pareto-principle` | `pareto-principle.measured-vital-few-allocation` | 14 | 3 |
| `circle-of-control` | `circle-of-control.control-influence-action-map` | 13 | 2 |
| `premortem` | `premortem.simulated-failure-to-plan-change` | 13 | 0 |
| `risk-assessment` | `risk-assessment.thresholded-downside-governance` | 13 | 2 |
| `lindy-effect` | `lindy-effect.longevity-prior-with-baseline-break-check` | 12 | 0 |
| `multi-criteria-decision-analysis` | `multi-criteria-decision-analysis.auditable-weighted-tradeoff-matrix` | 12 | 2 |

High source-ref count is not a defect. It can mean the affordance is
well-supported. But in PR55 it is a useful sampling signal: one card may be
carrying a lot of source territory.

## Multi-Affordance Records

| Model | Affordances | Absences |
| --- | ---: | ---: |
| `systems-thinking` | 4 | 0 |
| `complex-adaptive-systems` | 3 | 2 |
| `confidence-calibration` | 3 | 0 |
| `empathy` | 3 | 2 |
| `inversion` | 3 | 0 |
| `leverage-points` | 3 | 1 |
| `problem-framing-and-reframing` | 3 | 1 |
| `aleatory-epistemic-uncertainty-recognition` | 2 | 2 |
| `black-swan-events` | 2 | 3 |
| `correlation-vs-causation` | 2 | 2 |
| `decision-trees` | 2 | 0 |
| `decomposition` | 2 | 2 |
| `emergence` | 2 | 2 |
| `experimentation` | 2 | 3 |
| `incentives` | 2 | 1 |
| `information-asymmetry` | 2 | 2 |
| `law-of-large-numbers` | 2 | 2 |
| `moral-hazard` | 2 | 3 |
| `network-effects` | 2 | 2 |
| `optimization-theory` | 2 | 3 |
| `optionality` | 2 | 0 |
| `power-dynamics` | 2 | 0 |
| `prioritization` | 2 | 3 |
| `psychological-safety` | 2 | 2 |
| `social-proof` | 2 | 3 |
| `statistical-discipline` | 2 | 2 |
| `survivorship-bias` | 2 | 3 |
| `theory-of-constraints` | 2 | 0 |

These records are the first stress set for per-affordance grouping, because the
current packet flattens multiple affordances into shared card fields.

## Records Already Flagged By Quality Report

`quality_report_v18.md` explicitly marks these as not safe to runtime-promote
without rewrite review:

| Affordance | Reason |
| --- | --- |
| `systems-thinking.structure-over-events` | Broad-overlay risk; disputed separation from feedback-loop mapping. |
| `confidence-calibration.method-first-self-interrogation` | Broad scope; disputed whether breadth from source is acceptable as-is. |
| `inversion.obstacle-removal-before-added-force` | Likely sub-affordance rather than peer affordance. |

These are not compile failures. They are exactly the kind of quality signal
PR55 should keep visible.

## Distribution Red Flags

| Red flag | Evidence | Recommended PR55 treatment |
| --- | --- | --- |
| False equality after full coverage | 222/222 models now have reviewed records | Make confidence, support, absences, and flags visible. |
| One-affordance dominance | 194/222 records have one affordance | Run source-vs-record richness audit. |
| Weak support too quiet | 2 weak records, both medium confidence | Add `weak_support_warning_required` label in audit. |
| Absences may be underweighted | 429 absences, renderer shows only first | Run absence-first handoff review. |
| Broad cards need caps | v18 quality report flags broad pilot records | Stress broad/meta packet. |
| High source-ref one-card records | 14 one-affordance records with 12+ refs | Sample for possible over-compression. |

## Audit Conclusion

v18 is complete. The substrate is real. The next danger is not missing records.

The next danger is that the receiver sees a pile of polished reviewed cards and
forgets that reviewed means "source-backed handoff material," not "runtime-ready
judgment."

PR55 should therefore move from coverage counting to pickup-quality auditing.
