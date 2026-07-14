# Core Semantic Two-Path Comparison

Case: `case-02-multi-offer-career`

## Initial result

| measure | compact path | shadow path |
| --- | ---: | ---: |
| repeated runs | 3 | 3 |
| exact-span gold recall | 0.000 | 0.583 |
| mean span repeatability | 0.425 | 0.453 |
| mean label repeatability | 0.425 | 0.411 |

Exact-span recall is deliberately strict. Compact summaries without literal source spans do not receive source-grounding credit even when their paraphrase is directionally correct.

## Repeatability by family

| path | family | counts by run | span Jaccard | labeled Jaccard |
| --- | --- | --- | ---: | ---: |
| compact | `dropped_threads` | [0, 0, 0] | 1.000 | 1.000 |
| compact | `live_constraints` | [4, 4, 4] | 0.111 | 0.111 |
| compact | `reasoning_passages` | [6, 6, 6] | 0.164 | 0.164 |
| shadow | `assistant_stance_events` | [9, 7, 7] | 0.602 | 0.496 |
| shadow | `dropped_thread_events` | [1, 1, 1] | 0.333 | 0.333 |
| shadow | `evidence_boundary_events` | [3, 3, 3] | 0.400 | 0.400 |
| shadow | `live_constraint_events` | [6, 6, 6] | 0.389 | 0.344 |
| shadow | `option_events` | [4, 4, 4] | 1.000 | 1.000 |
| shadow | `question_events` | [8, 5, 4] | 0.208 | 0.169 |
| shadow | `user_pressure_events` | [3, 4, 6] | 0.240 | 0.134 |

## Gold observations recovered by exact source span

### Compact

Mean recall: 0.000

Stable across all repeats: none

Never source-grounded: boundary.spouse_yes_may_not_be_real, constraint.spouse_primary_earner, drop.expected_value_argument, pressure.family_joint_decision, question.current_due_diligence, question.initial_three_offers, stance.final_conditional_choice, stance.financial_reframe

### Shadow

Mean recall: 0.583

Stable across all repeats: boundary.spouse_yes_may_not_be_real, constraint.spouse_primary_earner, question.current_due_diligence, stance.financial_reframe

Never source-grounded: drop.expected_value_argument, stance.final_conditional_choice

## Limits

- exact_span_recall measures source-grounded recovery, not total semantic correctness
- compact paraphrases may be semantically useful while remaining unverified as source spans
- three repeats are an initial stability signal, not a production reliability estimate
- gold annotations are provisional source-first research judgments
