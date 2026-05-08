# PR 9 Batch 2 Quality Report - 2026-05-05

This report summarizes mechanical quality signals for the 20 Batch 2 affordance records. It does not compile `affordances_v3.json`, grade record quality, promote records into runtime use, or replace Marcin reviewer-eye.

## Headline

Batch 2 extracted all 20 approved Lane-4-frequency models. The result is 34 affordances and 51 absence records, with 0 schema/source validation failures. The shape is more absence-heavy than Pilot or Batch 1, which is directionally good for a coverage-first batch: frequent Lane 4 candidates did not automatically become dense knowledge records.

Gate 3 coverage remains the reason for this batch:

| Coverage metric | Current v2 | Projected after accepted Batch 2 |
| --- | ---: | ---: |
| Extracted models | 30 | 50 |
| Gap-route coverage | 67 / 87 = 77.0% | 80 / 87 = 92.0% |
| Candidate-appearance coverage | 99 / 444 = 22.3% | 334 / 444 = 75.2% |
| Run coverage | 21 / 21 = 100.0% | 21 / 21 = 100.0% |

No runtime consumer uses these Batch 2 records yet. Compilation to `affordances_v3.json` should wait until reviewer-eye accepts or annotates the records.

## Comparison To Earlier Extraction

| Metric | Pilot (10) | Batch 1 (20) | Batch 2 (20) |
| --- | ---: | ---: | ---: |
| Records | 10 | 20 | 20 |
| Total affordances | 22 | 30 | 34 |
| Total absence records | 2 | 30 | 51 |
| Affordance count distribution | 1: 3, 2: 3, 3: 3, 4: 1 | 1: 12, 2: 6, 3: 2 | 1: 7, 2: 12, 3: 1 |
| Absence count distribution | 0: 8, 1: 2 | 0: 3, 1: 4, 2: 13 | 2: 9, 3: 11 |
| Affordance confidence | 22 high | 30 high | 32 high, 2 medium |
| Quote/schema validation failures | 0 | 0 | 0 |
| 3+ affordance records | 4 | 2 | 1 |

## Batch 2 Per-Slice Shape

| Slice | Models | Affordances | Absences | Quality note |
| --- | ---: | ---: | ---: | --- |
| Risk-response continuation | 4 | 5 | 11 | Stayed sparse; risk records mostly rejected generic risk inventory and separated survival, improvement, tail exposure, and buffers. |
| Incentive alignment | 2 | 3 | 5 | Moral hazard is stronger than adverse selection; adverse selection needs reviewer-eye because named-model source support is caveated. |
| Stakeholder alignment | 4 | 8 | 10 | Did not collapse into generic warmth/facilitation. `empathy` is the one 3-affordance record and should be read first. |
| Resource allocation | 4 | 6 | 11 | Kept distinct from generic prioritization, but several boundary checks remain among Pareto, optimization, prioritization, trade-offs, and opportunity-cost. |
| Uncertainty type | 2 | 4 | 5 | Aleatory/epistemic and experimentation both refused generic uncertainty/learning loops. |
| Information quality | 4 | 8 | 9 | Base-rates duplication guard worked: reference-class/denominator anchoring was recorded as duplicate rather than re-extracted. |

## Per-Model Summary

| Model | Affordances | Absences | Confidence | Reviewer flag |
| --- | ---: | ---: | --- | --- |
| `adverse-selection` | 1 | 2 | 1 medium | Source explicitly caveats named-model support; consider downgrade or review note. |
| `aleatory-epistemic-uncertainty-recognition` | 2 | 2 | 2 high | Main boundary is activation only when uncertainty type changes method or commitment. |
| `antifragility` | 1 | 3 | 1 high | No blocking flag; kept to bounded stress learning. |
| `black-swan-events` | 2 | 3 | 2 high | Refused generic risk assessment. |
| `comparative-advantage` | 1 | 2 | 1 high | Check whether specialization-boundary treatment belongs in main affordance. |
| `correlation-vs-causation` | 2 | 2 | 2 high | Base-rates boundary explicit; prediction-vs-causation boundary remains. |
| `empathy` | 3 | 2 | 3 high | Only 3-affordance record; read for overlap with active listening/perspective-taking. |
| `experimentation` | 2 | 3 | 2 high | Generic learning-loop and standalone falsification splits recorded as absences. |
| `law-of-large-numbers` | 2 | 2 | 2 high | Base-rates duplicate correctly recorded as absence. |
| `margin-of-safety` | 1 | 2 | 1 high | Boundary with risk-assessment/calculated-risk-taking. |
| `moral-hazard` | 2 | 3 | 2 high | Short-termism kept as guard/absence. |
| `optimization-theory` | 2 | 3 | 2 high | Boundary checks with allocation and constraint records. |
| `pareto-principle` | 1 | 3 | 1 high | Check normalized protected-trial language. |
| `prioritization` | 2 | 3 | 2 high | Kept out of generic task ranking. |
| `psychological-safety` | 2 | 2 | 2 high | Accountability material merged rather than split. |
| `resilience` | 1 | 3 | 1 high | `challenge-recovery-story` is the main reviewer judgment point. |
| `six-thinking-hats` | 1 | 3 | 1 high | Source supports analogous mode separation; named-model support is caveated. |
| `social-proof` | 2 | 3 | 2 high | Boundary checks with authority, causation, and psychological safety. |
| `statistical-discipline` | 2 | 2 | 2 high | Boundary checks with LLN, causation, survivorship, and uncertainty records. |
| `survivorship-bias` | 2 | 3 | 2 high | Check failure-tail affordance against adjacent risk records. |

## Deterministic Observations

### Absence Status Counts

| Absence status | Count |
| --- | ---: |
| `duplicate_of_existing_field` | 23 |
| `not_supported_by_source` | 22 |
| `source_too_thin` | 6 |

### Affordance Confidence Counts

| Confidence | Count |
| --- | ---: |
| `high` | 32 |
| `medium` | 2 |
| `weak` | 0 |
| `not_applicable` | 0 |

### Repeated Diagnostic Question Openings

Only two openings repeated more than once:

| Opening | Count | Note |
| --- | ---: | --- |
| `what would we have to` | 3 | Still present but much less dominant than the v2 pilot+Batch1 repetition pattern. |
| `is the worst case bad` | 3 | Expected in risk-response records; reviewer should watch runtime coactivation later. |

Median source quote length across Batch 2 evidence: 138 characters.

## Reviewer-Eye Starting Points

Read these first:

1. `adverse-selection`: decide whether medium-supported hidden-type affordance should remain supported or downgrade to `weak_support`/review-only.
2. `empathy`: the only 3-affordance record; verify the third affordance is truly distinct.
3. `six-thinking-hats`: source-backed through analogous mode separation, but named-model support is caveated.
4. `pareto-principle`: check whether "protected trial" is faithful operational normalization.
5. `survivorship-bias`: verify failure-tail treatment stays survivorship-specific with adjacent risk records loaded.

## What This Report Deliberately Omits

- No `affordances_v3.json` compilation.
- No runtime promotion.
- No completeness grade.
- No semantic genericity score beyond deterministic observations.
- No automated rewrite recommendations.
- No user-facing Lane 4 experiment.
