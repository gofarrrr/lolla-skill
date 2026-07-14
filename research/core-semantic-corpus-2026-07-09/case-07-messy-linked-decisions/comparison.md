# Core Semantic Two-Path Comparison

Case: `case-07-messy-linked-decisions`

## Initial result

| measure | compact path | shadow path |
| --- | ---: | ---: |
| repeated runs | 3 | 3 |
| exact-span gold recall | 0.083 | 0.708 |
| mean span repeatability | 0.597 | 0.646 |
| mean label repeatability | 0.597 | 0.646 |

Exact-span recall is deliberately strict. Compact summaries without literal source spans do not receive source-grounding credit even when their paraphrase is directionally correct.

## Repeatability by family

| path | family | counts by run | span Jaccard | labeled Jaccard |
| --- | --- | --- | ---: | ---: |
| compact | `dropped_threads` | [0, 0, 0] | 1.000 | 1.000 |
| compact | `live_constraints` | [4, 4, 4] | 0.333 | 0.333 |
| compact | `reasoning_passages` | [5, 6, 5] | 0.458 | 0.458 |
| shadow | `assistant_stance_events` | [6, 6, 6] | 0.714 | 0.714 |
| shadow | `dropped_thread_events` | [3, 1, 2] | 0.222 | 0.222 |
| shadow | `evidence_boundary_events` | [3, 3, 3] | 0.300 | 0.300 |
| shadow | `live_constraint_events` | [5, 5, 5] | 0.778 | 0.778 |
| shadow | `option_events` | [4, 4, 4] | 0.733 | 0.733 |
| shadow | `question_events` | [2, 2, 2] | 1.000 | 1.000 |
| shadow | `user_pressure_events` | [5, 5, 5] | 0.778 | 0.778 |

## Gold observations recovered by exact source span

### Compact

Mean recall: 0.083

Stable across all repeats: none

Never source-grounded: boundary.boyfriend_commitment_untested, constraint.lease_deadline, drop.life_in_dc, pressure.claimed_but_not_actual_decision, question.current_plan_completeness, question.initial_where_to_start

### Shadow

Mean recall: 0.708

Stable across all repeats: constraint.lease_deadline, question.current_plan_completeness, question.initial_where_to_start, stance.lease_decoupling, stance.seattle_root_decision

Never source-grounded: pressure.claimed_but_not_actual_decision

## Limits

- exact_span_recall measures source-grounded recovery, not total semantic correctness
- compact paraphrases may be semantically useful while remaining unverified as source spans
- three repeats are an initial stability signal, not a production reliability estimate
- gold annotations are provisional source-first research judgments
