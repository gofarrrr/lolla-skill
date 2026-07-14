# Core Semantic Two-Path Comparison

Case: `case-01-enterprise-logo-beta`

## Initial result

| measure | compact path | shadow path |
| --- | ---: | ---: |
| repeated runs | 3 | 3 |
| exact-span gold recall | 0.000 | 0.733 |
| mean span repeatability | 0.460 | 0.896 |
| mean label repeatability | 0.460 | 0.858 |

Exact-span recall is deliberately strict. Compact summaries without literal source spans do not receive source-grounding credit even when their paraphrase is directionally correct.

## Repeatability by family

| path | family | counts by run | span Jaccard | labeled Jaccard |
| --- | --- | --- | ---: | ---: |
| compact | `dropped_threads` | [1, 1, 1] | 0.333 | 0.333 |
| compact | `live_constraints` | [3, 4, 4] | 0.048 | 0.048 |
| compact | `reasoning_passages` | [3, 3, 3] | 1.000 | 1.000 |
| shadow | `assistant_stance_events` | [4, 4, 4] | 1.000 | 1.000 |
| shadow | `dropped_thread_events` | [2, 2, 2] | 1.000 | 1.000 |
| shadow | `evidence_boundary_events` | [2, 2, 2] | 0.556 | 0.556 |
| shadow | `live_constraint_events` | [6, 5, 5] | 0.714 | 0.714 |
| shadow | `option_events` | [2, 2, 2] | 1.000 | 1.000 |
| shadow | `question_events` | [2, 2, 2] | 1.000 | 1.000 |
| shadow | `user_pressure_events` | [4, 4, 4] | 1.000 | 0.733 |

## Gold observations recovered by exact source span

### Compact

Mean recall: 0.000

Stable across all repeats: none

Never source-grounded: boundary.success_criteria_deferred, constraint.engineering_capacity, drop.board_pressure_under_carried, drop.commitment_concern_under_carried, drop.evidence_question_not_answered, pressure.board_brand_excitement, pressure.no_signed_commitment, pressure.purchase_commitment_concern, pressure.weak_email_evidence, question.change_to_evidence_gate, question.initial_public_launch, stance.initial_public_beta_commitment, stance.qualification_without_direction_change, threshold.email_confirmation, value.opportunity_loss_concern

### Shadow

Mean recall: 0.733

Stable across all repeats: boundary.success_criteria_deferred, constraint.engineering_capacity, drop.commitment_concern_under_carried, pressure.no_signed_commitment, pressure.purchase_commitment_concern, question.change_to_evidence_gate, question.initial_public_launch, stance.initial_public_beta_commitment, stance.qualification_without_direction_change, threshold.email_confirmation, value.opportunity_loss_concern

Never source-grounded: drop.board_pressure_under_carried, drop.evidence_question_not_answered, pressure.board_brand_excitement, pressure.weak_email_evidence

## Limits

- exact_span_recall measures source-grounded recovery, not total semantic correctness
- compact paraphrases may be semantically useful while remaining unverified as source spans
- three repeats are an initial stability signal, not a production reliability estimate
- gold annotations are provisional source-first research judgments
