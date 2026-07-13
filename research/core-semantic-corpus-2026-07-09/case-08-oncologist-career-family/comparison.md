# Core Semantic Two-Path Comparison

Case: `case-08-oncologist-career-family`

## Initial result

| measure | compact path | shadow path |
| --- | ---: | ---: |
| repeated runs | 3 | 3 |
| exact-span gold recall | 0.000 | 0.500 |
| mean span repeatability | 0.179 | 0.751 |
| mean label repeatability | 0.179 | 0.731 |

Exact-span recall is deliberately strict. Compact summaries without literal source spans do not receive source-grounding credit even when their paraphrase is directionally correct.

## Repeatability by family

| path | family | counts by run | span Jaccard | labeled Jaccard |
| --- | --- | --- | ---: | ---: |
| compact | `dropped_threads` | [1, 1, 1] | 0.000 | 0.000 |
| compact | `live_constraints` | [5, 5, 4] | 0.280 | 0.280 |
| compact | `reasoning_passages` | [4, 6, 5] | 0.259 | 0.259 |
| shadow | `assistant_stance_events` | [6, 7, 6] | 0.367 | 0.288 |
| shadow | `dropped_thread_events` | [1, 1, 1] | 1.000 | 1.000 |
| shadow | `evidence_boundary_events` | [0, 0, 0] | 1.000 | 1.000 |
| shadow | `live_constraint_events` | [6, 6, 6] | 0.516 | 0.460 |
| shadow | `option_events` | [0, 0, 0] | 1.000 | 1.000 |
| shadow | `question_events` | [2, 2, 2] | 1.000 | 1.000 |
| shadow | `user_pressure_events` | [6, 7, 7] | 0.371 | 0.371 |

## Gold observations recovered by exact source span

### Compact

Mean recall: 0.000

Stable across all repeats: none

Never source-grounded: boundary.schedule_flexibility_verbal, constraint.decision_deadline, constraint.mother_finite_window, drop.stuck_feeling, pressure.husband_conversation_not_real, question.current_direct_call, question.initial_greedy_or_smart, stance.take_role_with_conditions

### Shadow

Mean recall: 0.500

Stable across all repeats: constraint.decision_deadline, question.current_direct_call, question.initial_greedy_or_smart, stance.take_role_with_conditions

Never source-grounded: boundary.schedule_flexibility_verbal, constraint.mother_finite_window, drop.stuck_feeling, pressure.husband_conversation_not_real

## Limits

- exact_span_recall measures source-grounded recovery, not total semantic correctness
- compact paraphrases may be semantically useful while remaining unverified as source spans
- three repeats are an initial stability signal, not a production reliability estimate
- gold annotations are provisional source-first research judgments
