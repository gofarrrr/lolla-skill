# Core Semantic Two-Path Comparison

Case: `case-02-multi-offer-career`

## Initial result

| measure | compact path | shadow path |
| --- | ---: | ---: |
| repeated runs | 3 | 3 |
| exact-span gold recall | 0.000 | 0.375 |
| mean span repeatability | 0.425 | 0.335 |
| mean label repeatability | 0.425 | 0.320 |

Exact-span recall is deliberately strict. Compact summaries without literal source spans do not receive source-grounding credit even when their paraphrase is directionally correct.

## Repeatability by family

| path | family | counts by run | span Jaccard | labeled Jaccard |
| --- | --- | --- | ---: | ---: |
| compact | `dropped_threads` | [0, 0, 0] | 1.000 | 1.000 |
| compact | `live_constraints` | [4, 4, 4] | 0.111 | 0.111 |
| compact | `reasoning_passages` | [6, 6, 6] | 0.164 | 0.164 |
| shadow | `assistant_stance_events` | [5, 6, 5] | 0.458 | 0.348 |
| shadow | `dropped_thread_events` | [0, 0, 1] | 0.333 | 0.333 |
| shadow | `evidence_boundary_events` | [3, 3, 3] | 0.067 | 0.067 |
| shadow | `live_constraint_events` | [6, 5, 5] | 0.312 | 0.312 |
| shadow | `option_events` | [4, 4, 4] | 0.733 | 0.733 |
| shadow | `question_events` | [3, 4, 4] | 0.444 | 0.444 |
| shadow | `user_pressure_events` | [3, 2, 3] | 0.000 | 0.000 |

## Gold observations recovered by exact source span

### Compact

Mean recall: 0.000

Stable across all repeats: none

Never source-grounded: boundary.spouse_yes_may_not_be_real, constraint.spouse_primary_earner, drop.expected_value_argument, pressure.family_joint_decision, question.current_due_diligence, question.initial_three_offers, stance.final_conditional_choice, stance.financial_reframe

### Shadow

Mean recall: 0.375

Stable across all repeats: stance.financial_reframe

Never source-grounded: drop.expected_value_argument, question.initial_three_offers

## Limits

- exact_span_recall measures source-grounded recovery, not total semantic correctness
- compact paraphrases may be semantically useful while remaining unverified as source spans
- three repeats are an initial stability signal, not a production reliability estimate
- gold annotations are provisional source-first research judgments
