# Core Semantic Two-Path Comparison

Case: `case-02-multi-offer-career`

## Initial result

| measure | compact path | shadow path |
| --- | ---: | ---: |
| repeated runs | 3 | 3 |
| exact-span gold recall | 0.000 | 0.208 |
| mean span repeatability | 0.425 | 0.464 |
| mean label repeatability | 0.425 | 0.444 |

Exact-span recall is deliberately strict. Compact summaries without literal source spans do not receive source-grounding credit even when their paraphrase is directionally correct.

## Repeatability by family

| path | family | counts by run | span Jaccard | labeled Jaccard |
| --- | --- | --- | ---: | ---: |
| compact | `dropped_threads` | [0, 0, 0] | 1.000 | 1.000 |
| compact | `live_constraints` | [4, 4, 4] | 0.111 | 0.111 |
| compact | `reasoning_passages` | [6, 6, 6] | 0.164 | 0.164 |
| shadow | `assistant_stance_events` | [5, 0, 5] | 0.222 | 0.143 |
| shadow | `dropped_thread_events` | [1, 1, 1] | 0.333 | 0.333 |
| shadow | `evidence_boundary_events` | [3, 0, 0] | 0.333 | 0.333 |
| shadow | `live_constraint_events` | [7, 6, 5] | 0.637 | 0.577 |
| shadow | `option_events` | [4, 0, 0] | 0.333 | 0.333 |
| shadow | `question_events` | [3, 3, 3] | 1.000 | 1.000 |
| shadow | `user_pressure_events` | [5, 4, 6] | 0.392 | 0.392 |

## Gold observations recovered by exact source span

### Compact

Mean recall: 0.000

Stable across all repeats: none

Never source-grounded: boundary.spouse_yes_may_not_be_real, constraint.spouse_primary_earner, drop.expected_value_argument, pressure.family_joint_decision, question.current_due_diligence, question.initial_three_offers, stance.final_conditional_choice, stance.financial_reframe

### Shadow

Mean recall: 0.208

Stable across all repeats: question.current_due_diligence

Never source-grounded: boundary.spouse_yes_may_not_be_real, constraint.spouse_primary_earner, drop.expected_value_argument, pressure.family_joint_decision, question.initial_three_offers, stance.final_conditional_choice

## Limits

- exact_span_recall measures source-grounded recovery, not total semantic correctness
- compact paraphrases may be semantically useful while remaining unverified as source spans
- three repeats are an initial stability signal, not a production reliability estimate
- gold annotations are provisional source-first research judgments
