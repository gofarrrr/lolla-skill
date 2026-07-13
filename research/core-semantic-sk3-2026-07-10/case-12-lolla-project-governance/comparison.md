# Core Semantic Two-Path Comparison

Case: `case-12-lolla-project-governance`

## Initial result

| measure | compact path | shadow path |
| --- | ---: | ---: |
| repeated runs | 3 | 3 |
| exact-span gold recall | 0.167 | 0.500 |
| mean span repeatability | 0.358 | 0.647 |
| mean label repeatability | 0.358 | 0.647 |

Exact-span recall is deliberately strict. Compact summaries without literal source spans do not receive source-grounding credit even when their paraphrase is directionally correct.

## Repeatability by family

| path | family | counts by run | span Jaccard | labeled Jaccard |
| --- | --- | --- | ---: | ---: |
| compact | `dropped_threads` | [1, 0, 1] | 0.000 | 0.000 |
| compact | `live_constraints` | [4, 4, 3] | 0.298 | 0.298 |
| compact | `reasoning_passages` | [5, 6, 5] | 0.778 | 0.778 |
| shadow | `assistant_stance_events` | [4, 3, 4] | 0.583 | 0.583 |
| shadow | `dropped_thread_events` | [1, 1, 1] | 0.333 | 0.333 |
| shadow | `evidence_boundary_events` | [2, 2, 2] | 1.000 | 1.000 |
| shadow | `live_constraint_events` | [1, 2, 3] | 0.500 | 0.500 |
| shadow | `option_events` | [2, 2, 2] | 0.333 | 0.333 |
| shadow | `question_events` | [3, 2, 3] | 0.778 | 0.778 |
| shadow | `user_pressure_events` | [2, 2, 2] | 1.000 | 1.000 |

## Gold observations recovered by exact source span

### Compact

Mean recall: 0.167

Stable across all repeats: stance.bounded_utility_claim

Never source-grounded: boundary.semantic_gate_before_graph, constraint.future_shareability, pressure.avoid_ad_hoc_work, question.big_picture_plan, stance.two_track_roadmap

### Shadow

Mean recall: 0.500

Stable across all repeats: constraint.future_shareability, pressure.avoid_ad_hoc_work, question.big_picture_plan

Never source-grounded: boundary.semantic_gate_before_graph, stance.bounded_utility_claim, stance.two_track_roadmap

## Limits

- exact_span_recall measures source-grounded recovery, not total semantic correctness
- compact paraphrases may be semantically useful while remaining unverified as source spans
- three repeats are an initial stability signal, not a production reliability estimate
- gold annotations are provisional source-first research judgments
