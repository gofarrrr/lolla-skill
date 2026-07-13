# Core Semantic Two-Path Comparison

Case: `case-09-phd-dissertation`

## Initial result

| measure | compact path | shadow path |
| --- | ---: | ---: |
| repeated runs | 3 | 3 |
| exact-span gold recall | 0.000 | 0.519 |
| mean span repeatability | 0.431 | 0.705 |
| mean label repeatability | 0.431 | 0.705 |

Exact-span recall is deliberately strict. Compact summaries without literal source spans do not receive source-grounding credit even when their paraphrase is directionally correct.

## Repeatability by family

| path | family | counts by run | span Jaccard | labeled Jaccard |
| --- | --- | --- | ---: | ---: |
| compact | `dropped_threads` | [0, 1, 0] | 0.333 | 0.333 |
| compact | `live_constraints` | [3, 4, 4] | 0.700 | 0.700 |
| compact | `reasoning_passages` | [6, 6, 5] | 0.259 | 0.259 |
| shadow | `assistant_stance_events` | [5, 6, 5] | 0.538 | 0.538 |
| shadow | `dropped_thread_events` | [1, 1, 0] | 0.333 | 0.333 |
| shadow | `evidence_boundary_events` | [3, 3, 2] | 0.778 | 0.778 |
| shadow | `live_constraint_events` | [5, 5, 5] | 1.000 | 1.000 |
| shadow | `option_events` | [4, 4, 4] | 0.511 | 0.511 |
| shadow | `question_events` | [6, 6, 6] | 1.000 | 1.000 |
| shadow | `user_pressure_events` | [2, 3, 3] | 0.778 | 0.778 |

## Gold observations recovered by exact source span

### Compact

Mean recall: 0.000

Stable across all repeats: none

Never source-grounded: boundary.data_access_gate, constraint.advisor_retirement, drop.option_two_closure, pressure.no_single_cell_advantage, question.current_overthinking, question.initial_dissertation_direction, stance.hybrid_reframe, stance.option_two_qualification, threshold.eighteen_month_checkpoint

### Shadow

Mean recall: 0.519

Stable across all repeats: constraint.advisor_retirement, pressure.no_single_cell_advantage, question.initial_dissertation_direction, threshold.eighteen_month_checkpoint

Never source-grounded: boundary.data_access_gate, drop.option_two_closure, question.current_overthinking

## Limits

- exact_span_recall measures source-grounded recovery, not total semantic correctness
- compact paraphrases may be semantically useful while remaining unverified as source spans
- three repeats are an initial stability signal, not a production reliability estimate
- gold annotations are provisional source-first research judgments
