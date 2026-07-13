# Core Semantic Two-Path Comparison

Case: `case-05-parenting-teen`

## Initial result

| measure | compact path | shadow path |
| --- | ---: | ---: |
| repeated runs | 3 | 3 |
| exact-span gold recall | 0.125 | 0.542 |
| mean span repeatability | 0.174 | 0.518 |
| mean label repeatability | 0.174 | 0.481 |

Exact-span recall is deliberately strict. Compact summaries without literal source spans do not receive source-grounding credit even when their paraphrase is directionally correct.

## Repeatability by family

| path | family | counts by run | span Jaccard | labeled Jaccard |
| --- | --- | --- | ---: | ---: |
| compact | `dropped_threads` | [0, 2, 1] | 0.000 | 0.000 |
| compact | `live_constraints` | [4, 4, 4] | 0.000 | 0.000 |
| compact | `reasoning_passages` | [5, 6, 7] | 0.522 | 0.522 |
| shadow | `assistant_stance_events` | [5, 5, 5] | 0.508 | 0.508 |
| shadow | `dropped_thread_events` | [1, 1, 1] | 1.000 | 1.000 |
| shadow | `evidence_boundary_events` | [3, 3, 2] | 0.083 | 0.083 |
| shadow | `live_constraint_events` | [6, 6, 6] | 0.460 | 0.200 |
| shadow | `option_events` | [6, 4, 4] | 0.644 | 0.644 |
| shadow | `question_events` | [4, 4, 5] | 0.867 | 0.867 |
| shadow | `user_pressure_events` | [3, 3, 3] | 0.067 | 0.067 |

## Gold observations recovered by exact source span

### Compact

Mean recall: 0.125

Stable across all repeats: stance.relationship_first_reframe

Never source-grounded: boundary.no_known_physical_contact, constraint.coparent_disagreement, constraint.daughter_shutdown, pressure.ongoing_phone_monitoring, question.current_plan_summary, question.initial_parent_response, stance.defer_police

### Shadow

Mean recall: 0.542

Stable across all repeats: constraint.coparent_disagreement, question.initial_parent_response, stance.relationship_first_reframe

Never source-grounded: boundary.no_known_physical_contact, constraint.daughter_shutdown, question.current_plan_summary

## Limits

- exact_span_recall measures source-grounded recovery, not total semantic correctness
- compact paraphrases may be semantically useful while remaining unverified as source spans
- three repeats are an initial stability signal, not a production reliability estimate
- gold annotations are provisional source-first research judgments
