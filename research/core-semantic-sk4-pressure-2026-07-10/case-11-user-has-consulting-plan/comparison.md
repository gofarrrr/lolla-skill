# Core Semantic Two-Path Comparison

Case: `case-11-user-has-consulting-plan`

## Initial result

| measure | compact path | shadow path |
| --- | ---: | ---: |
| repeated runs | 3 | 3 |
| exact-span gold recall | 0.000 | 0.556 |
| mean span repeatability | 0.423 | 0.657 |
| mean label repeatability | 0.423 | 0.549 |

Exact-span recall is deliberately strict. Compact summaries without literal source spans do not receive source-grounding credit even when their paraphrase is directionally correct.

## Repeatability by family

| path | family | counts by run | span Jaccard | labeled Jaccard |
| --- | --- | --- | ---: | ---: |
| compact | `dropped_threads` | [1, 0, 0] | 0.333 | 0.333 |
| compact | `live_constraints` | [4, 4, 4] | 0.048 | 0.048 |
| compact | `reasoning_passages` | [5, 6, 5] | 0.889 | 0.889 |
| shadow | `assistant_stance_events` | [6, 6, 5] | 0.889 | 0.794 |
| shadow | `dropped_thread_events` | [1, 1, 1] | 1.000 | 0.333 |
| shadow | `evidence_boundary_events` | [3, 4, 4] | 0.311 | 0.311 |
| shadow | `live_constraint_events` | [4, 4, 5] | 0.544 | 0.544 |
| shadow | `option_events` | [4, 4, 4] | 0.429 | 0.429 |
| shadow | `question_events` | [4, 4, 4] | 1.000 | 1.000 |
| shadow | `user_pressure_events` | [3, 5, 5] | 0.429 | 0.429 |

## Gold observations recovered by exact source span

### Compact

Mean recall: 0.000

Stable across all repeats: none

Never source-grounded: boundary.friendly_interest_only, constraint.eight_month_runway, drop.requested_launch_tactics, pressure.no_actual_commitments, question.current_fractional_bridge, question.initial_launch_plan, stance.launch_condition, stance.network_not_pipeline, threshold.delay_rule

### Shadow

Mean recall: 0.556

Stable across all repeats: constraint.eight_month_runway, question.current_fractional_bridge, question.initial_launch_plan, stance.network_not_pipeline, threshold.delay_rule

Never source-grounded: boundary.friendly_interest_only, drop.requested_launch_tactics, pressure.no_actual_commitments, stance.launch_condition

## Limits

- exact_span_recall measures source-grounded recovery, not total semantic correctness
- compact paraphrases may be semantically useful while remaining unverified as source spans
- three repeats are an initial stability signal, not a production reliability estimate
- gold annotations are provisional source-first research judgments
