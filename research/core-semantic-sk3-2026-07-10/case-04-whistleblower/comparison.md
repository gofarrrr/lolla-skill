# Core Semantic Two-Path Comparison

Case: `case-04-whistleblower`

## Initial result

| measure | compact path | shadow path |
| --- | ---: | ---: |
| repeated runs | 3 | 3 |
| exact-span gold recall | 0.286 | 0.619 |
| mean span repeatability | 0.386 | 0.629 |
| mean label repeatability | 0.386 | 0.574 |

Exact-span recall is deliberately strict. Compact summaries without literal source spans do not receive source-grounding credit even when their paraphrase is directionally correct.

## Repeatability by family

| path | family | counts by run | span Jaccard | labeled Jaccard |
| --- | --- | --- | ---: | ---: |
| compact | `dropped_threads` | [1, 1, 1] | 0.333 | 0.333 |
| compact | `live_constraints` | [4, 4, 4] | 0.048 | 0.048 |
| compact | `reasoning_passages` | [5, 5, 5] | 0.778 | 0.778 |
| shadow | `assistant_stance_events` | [6, 6, 6] | 0.500 | 0.444 |
| shadow | `dropped_thread_events` | [1, 1, 1] | 1.000 | 1.000 |
| shadow | `evidence_boundary_events` | [3, 3, 3] | 0.467 | 0.133 |
| shadow | `live_constraint_events` | [3, 5, 5] | 0.543 | 0.543 |
| shadow | `option_events` | [3, 3, 4] | 0.600 | 0.600 |
| shadow | `question_events` | [8, 8, 6] | 0.630 | 0.630 |
| shadow | `user_pressure_events` | [3, 3, 3] | 0.667 | 0.667 |

## Gold observations recovered by exact source span

### Compact

Mean recall: 0.286

Stable across all repeats: stance.external_counsel_path, stance.internal_confidence_threshold

Never source-grounded: boundary.brief_visual_access, constraint.active_regulatory_audit, drop.former_manager_implication, pressure.partial_document_confidence, question.initial_what_to_do

### Shadow

Mean recall: 0.619

Stable across all repeats: drop.former_manager_implication, question.initial_what_to_do, stance.external_counsel_path

Never source-grounded: constraint.active_regulatory_audit, pressure.partial_document_confidence

## Limits

- exact_span_recall measures source-grounded recovery, not total semantic correctness
- compact paraphrases may be semantically useful while remaining unverified as source spans
- three repeats are an initial stability signal, not a production reliability estimate
- gold annotations are provisional source-first research judgments
