# Core Semantic Two-Path Comparison

Case: `case-03-startup-pivot`

## Initial result

| measure | compact path | shadow path |
| --- | ---: | ---: |
| repeated runs | 3 | 3 |
| exact-span gold recall | 0.125 | 0.458 |
| mean span repeatability | 0.547 | 0.659 |
| mean label repeatability | 0.547 | 0.630 |

Exact-span recall is deliberately strict. Compact summaries without literal source spans do not receive source-grounding credit even when their paraphrase is directionally correct.

## Repeatability by family

| path | family | counts by run | span Jaccard | labeled Jaccard |
| --- | --- | --- | ---: | ---: |
| compact | `dropped_threads` | [0, 0, 0] | 1.000 | 1.000 |
| compact | `live_constraints` | [4, 4, 4] | 0.333 | 0.333 |
| compact | `reasoning_passages` | [6, 6, 6] | 0.308 | 0.308 |
| shadow | `assistant_stance_events` | [6, 6, 6] | 0.667 | 0.460 |
| shadow | `dropped_thread_events` | [1, 1, 1] | 1.000 | 1.000 |
| shadow | `evidence_boundary_events` | [4, 3, 3] | 0.356 | 0.356 |
| shadow | `live_constraint_events` | [6, 5, 6] | 0.794 | 0.794 |
| shadow | `option_events` | [6, 2, 2] | 0.333 | 0.333 |
| shadow | `question_events` | [5, 5, 5] | 1.000 | 1.000 |
| shadow | `user_pressure_events` | [4, 4, 3] | 0.467 | 0.467 |

## Gold observations recovered by exact source span

### Compact

Mean recall: 0.125

Stable across all repeats: stance.prebuy_threshold

Never source-grounded: boundary.conversational_signal_only, constraint.runway, option.kill_current_product, pressure.no_price_or_timeline, question.current_plan_completeness, question.initial_pivot_or_push, stance.conversation_bottleneck_reframe

### Shadow

Mean recall: 0.458

Stable across all repeats: constraint.runway, question.current_plan_completeness, question.initial_pivot_or_push

Never source-grounded: boundary.conversational_signal_only, option.kill_current_product, stance.conversation_bottleneck_reframe, stance.prebuy_threshold

## Limits

- exact_span_recall measures source-grounded recovery, not total semantic correctness
- compact paraphrases may be semantically useful while remaining unverified as source spans
- three repeats are an initial stability signal, not a production reliability estimate
- gold annotations are provisional source-first research judgments
