# Core Semantic Two-Path Comparison

Case: `case-06-friendship-money`

## Initial result

| measure | compact path | shadow path |
| --- | ---: | ---: |
| repeated runs | 3 | 3 |
| exact-span gold recall | 0.000 | 0.500 |
| mean span repeatability | 0.316 | 0.451 |
| mean label repeatability | 0.316 | 0.451 |

Exact-span recall is deliberately strict. Compact summaries without literal source spans do not receive source-grounding credit even when their paraphrase is directionally correct.

## Repeatability by family

| path | family | counts by run | span Jaccard | labeled Jaccard |
| --- | --- | --- | ---: | ---: |
| compact | `dropped_threads` | [1, 1, 1] | 0.333 | 0.333 |
| compact | `live_constraints` | [4, 3, 3] | 0.067 | 0.067 |
| compact | `reasoning_passages` | [5, 6, 6] | 0.548 | 0.548 |
| shadow | `assistant_stance_events` | [5, 6, 5] | 0.282 | 0.282 |
| shadow | `dropped_thread_events` | [1, 2, 1] | 0.333 | 0.333 |
| shadow | `evidence_boundary_events` | [3, 3, 3] | 0.300 | 0.300 |
| shadow | `live_constraint_events` | [5, 5, 6] | 0.282 | 0.282 |
| shadow | `option_events` | [5, 5, 4] | 0.392 | 0.392 |
| shadow | `question_events` | [2, 2, 2] | 1.000 | 1.000 |
| shadow | `user_pressure_events` | [7, 7, 7] | 0.569 | 0.569 |

## Gold observations recovered by exact source span

### Compact

Mean recall: 0.000

Stable across all repeats: none

Never source-grounded: boundary.social_worker_unknown, constraint.rent_arrears, drop.homelessness_stakes, pressure.not_financial_manager, question.current_drop_pattern_frame, question.initial_say_no_preserve_friendship, stance.intent_walkback, stance.smaller_help_script

### Shadow

Mean recall: 0.500

Stable across all repeats: boundary.social_worker_unknown, constraint.rent_arrears, question.current_drop_pattern_frame, question.initial_say_no_preserve_friendship

Never source-grounded: drop.homelessness_stakes, pressure.not_financial_manager, stance.intent_walkback, stance.smaller_help_script

## Limits

- exact_span_recall measures source-grounded recovery, not total semantic correctness
- compact paraphrases may be semantically useful while remaining unverified as source spans
- three repeats are an initial stability signal, not a production reliability estimate
- gold annotations are provisional source-first research judgments
