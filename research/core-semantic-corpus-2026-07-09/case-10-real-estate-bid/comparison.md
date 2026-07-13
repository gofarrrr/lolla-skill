# Core Semantic Two-Path Comparison

Case: `case-10-real-estate-bid`

## Initial result

| measure | compact path | shadow path |
| --- | ---: | ---: |
| repeated runs | 3 | 3 |
| exact-span gold recall | 0.125 | 0.500 |
| mean span repeatability | 0.209 | 0.667 |
| mean label repeatability | 0.209 | 0.644 |

Exact-span recall is deliberately strict. Compact summaries without literal source spans do not receive source-grounding credit even when their paraphrase is directionally correct.

## Repeatability by family

| path | family | counts by run | span Jaccard | labeled Jaccard |
| --- | --- | --- | ---: | ---: |
| compact | `dropped_threads` | [1, 1, 1] | 0.000 | 0.000 |
| compact | `live_constraints` | [4, 4, 4] | 0.111 | 0.111 |
| compact | `reasoning_passages` | [6, 6, 6] | 0.516 | 0.516 |
| shadow | `assistant_stance_events` | [5, 5, 5] | 0.667 | 0.508 |
| shadow | `dropped_thread_events` | [1, 1, 1] | 1.000 | 1.000 |
| shadow | `evidence_boundary_events` | [2, 2, 0] | 0.000 | 0.000 |
| shadow | `live_constraint_events` | [4, 4, 4] | 1.000 | 1.000 |
| shadow | `option_events` | [3, 3, 0] | 0.333 | 0.333 |
| shadow | `question_events` | [1, 1, 1] | 1.000 | 1.000 |
| shadow | `user_pressure_events` | [2, 2, 4] | 0.667 | 0.667 |

## Gold observations recovered by exact source span

### Compact

Mean recall: 0.125

Stable across all repeats: stance.need_state_affordability

Never source-grounded: boundary.sensible_or_scared, constraint.renovation_gap, drop.regret_argument, option.final_ceiling, pressure.insurance_requirement, question.current_middle_path, question.initial_raise_or_walk

### Shadow

Mean recall: 0.500

Stable across all repeats: constraint.renovation_gap, pressure.insurance_requirement, stance.need_state_affordability

Never source-grounded: drop.regret_argument, question.current_middle_path, question.initial_raise_or_walk

## Limits

- exact_span_recall measures source-grounded recovery, not total semantic correctness
- compact paraphrases may be semantically useful while remaining unverified as source spans
- three repeats are an initial stability signal, not a production reliability estimate
- gold annotations are provisional source-first research judgments
