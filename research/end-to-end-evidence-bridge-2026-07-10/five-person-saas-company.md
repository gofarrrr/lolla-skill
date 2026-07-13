# End-to-End Evidence Bridge

Source run: `five-person-saas-company` / `20260709T201634Z_7a7930`

This is a read-only, review-safe bridge. It contains counts, hashes,
status fields, and existing review labels, not raw conversation or
private reasoning content.

## C0 — Capture and custody

- Run health: `healthy`; product output: `clean`.
- Captured 6 / 6 turns.
- Live-output health remains `not_checked`.

## C1-C3 — Semantic and temporal packet

| measure | weighted recall | stable observations |
| --- | ---: | ---: |
| `reasoning_concept_anywhere` | 0.733 | 3 / 5 |
| `reasoning_concept_acceptable_role` | 0.667 | 3 / 5 |
| `audit_first_introduction` | 0.667 | 3 / 5 |
| `audit_temporal_complete` | 0.667 | 3 / 5 |

## C4-C5 — Pressure and graph

- 109 raw lane signals became 60 candidates, 8 selected cards, and 16 selected chunks.
- Selected models: `authority-bias`, `first-principles-thinking`, `dialectical-reasoning`, `step-back`, `problem-framing-and-reframing`, `decision-trees`, `lean-startup-methodology`, `falsifiability`.
- 130 signals were suppressed; 0 candidates were left unadjudicated.

## C6 — Reconsideration utility

- Review relation: `analogous_case_not_exact_run`.
- Existing review: `pass`; improved: `yes`; useful friction: `present`.
- This supports a product-delta hypothesis, not causal credit for the new semantic kernel.

## C7-C8 — Receipt and operability

- Trace: `thin`; future-review ready: `false`; error-analysis ready: `true`.
- User usefulness review: `not_collected`; outcome review: `not_started`.
- Original run: 38 vendor calls; estimated cost `$0.03065`.

## Decision

The run is traceable and the analogous human review supports a real
action-changing delta. The missing proof is whether the offline semantic
kernel or Lolla pressure beats a strong fresh reconsideration control.
Do not spend more extraction calls before that downstream question is frozen.
