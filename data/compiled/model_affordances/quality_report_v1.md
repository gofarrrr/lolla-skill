# Model Affordance Quality Report v1

This report surfaces honesty signals for human reviewers. It does not grade quality, infer missing knowledge, or promote any affordance into runtime use.

## Honesty Signals

- Contributing records: `10`
- Compiled affordances: `22`
- Compiled absence records: `2`
- Affordance count distribution per model:
  - `1` affordance(s): base-rates, premortem, second-order-thinking
  - `2` affordance(s): optionality, power-dynamics, theory-of-constraints
  - `3` affordance(s): confidence-calibration, inversion, problem-framing-and-reframing
  - `4` affordance(s): systems-thinking
- Absence record status counts:
  - `source_too_thin`: `2`
- Affordance confidence counts:
  - `high`: `22`
  - `medium`: `0`
  - `weak`: `0`
  - `not_applicable`: `0`
- Affordance status counts:
  - `supported`: `22`
  - `weak_support`: `0`
  - `duplicate_of_existing_field`: `0`
  - `deferred_for_review`: `0`
- Source-quote rejection count from compile run: `0`
- Schema-validation failure count from compile run: `0`

## Do Not Runtime Promote Without Rewrite Review

| affordance_id | reason | future trigger condition |
| --- | --- | --- |
| `systems-thinking.structure-over-events` | Broad-overlay risk; reviewers disagreed on whether it should remain separate from feedback-loop-mapping. | Merge or rewrite only if archived-case evaluation shows 80%+ coactivation with systems-thinking.feedback-loop-mapping. |
| `confidence-calibration.method-first-self-interrogation` | Broad scope; reviewers disagreed on whether breadth-from-source is acceptable as-is. | Split only if future runtime cases show learning/mastery calibration and business-claim confidence require different treatment. |
| `inversion.obstacle-removal-before-added-force` | Likely sub-affordance rather than peer affordance; reviewers broadly agree this needs rewrite review before runtime promotion. | Introduce parent_affordance_id or granularity only if a second sub-affordance case appears. |

## Per-Model Summary

| model_id | affordance count | absence count | dominant confidence | flags |
| --- | ---: | ---: | --- | --- |
| `base-rates` | 1 | 1 | `high` | none |
| `confidence-calibration` | 3 | 0 | `high` | `confidence-calibration.method-first-self-interrogation` |
| `inversion` | 3 | 0 | `high` | `inversion.obstacle-removal-before-added-force` |
| `optionality` | 2 | 0 | `high` | none |
| `power-dynamics` | 2 | 0 | `high` | none |
| `premortem` | 1 | 0 | `high` | none |
| `problem-framing-and-reframing` | 3 | 1 | `high` | none |
| `second-order-thinking` | 1 | 0 | `high` | none |
| `systems-thinking` | 4 | 0 | `high` | `systems-thinking.structure-over-events` |
| `theory-of-constraints` | 2 | 0 | `high` | none |

## Cross-Model Deterministic Observations

### Identical Extraction-Type Distributions

- None.

### Affordances With Short Source Quotes

Median affordance-level source quote length: `131` characters.

- `optionality.preserve-reversible-learning`: shortest quote `29` chars across `10` quote(s)
- `premortem.simulated-failure-to-plan-change`: shortest quote `31` chars across `13` quote(s)
- `problem-framing-and-reframing.falsify-frame-assumptions`: shortest quote `31` chars across `8` quote(s)
- `theory-of-constraints.constraint-shift-cadence`: shortest quote `31` chars across `8` quote(s)
- `power-dynamics.commitment-gradient-inversion`: shortest quote `34` chars across `9` quote(s)
- `power-dynamics.outside-option-credibility`: shortest quote `43` chars across `12` quote(s)
- `optionality.expand-before-evaluating`: shortest quote `49` chars across `8` quote(s)
- `problem-framing-and-reframing.define-before-analysis`: shortest quote `52` chars across `10` quote(s)
- `base-rates.outside-view-reference-class-anchor`: shortest quote `53` chars across `16` quote(s)
- `inversion.disconfirmation-before-defense`: shortest quote `55` chars across `7` quote(s)
- `problem-framing-and-reframing.test-alternative-frames`: shortest quote `55` chars across `9` quote(s)
- `systems-thinking.structure-over-events`: shortest quote `66` chars across `6` quote(s)
- `confidence-calibration.instrument-trust-before-precision`: shortest quote `68` chars across `6` quote(s)
- `systems-thinking.feedback-loop-mapping`: shortest quote `70` chars across `7` quote(s)
- `confidence-calibration.method-first-self-interrogation`: shortest quote `73` chars across `6` quote(s)
- `inversion.anti-goal-failure-mechanism-map`: shortest quote `74` chars across `8` quote(s)
- `inversion.obstacle-removal-before-added-force`: shortest quote `86` chars across `6` quote(s)
- `systems-thinking.metric-leverage-design`: shortest quote `95` chars across `4` quote(s)
- `theory-of-constraints.constraint-first-cap`: shortest quote `118` chars across `9` quote(s)
- `second-order-thinking.downstream-reversal-stress-test`: shortest quote `124` chars across `8` quote(s)
- `systems-thinking.architecture-misdiagnosis-test`: shortest quote `126` chars across `6` quote(s)

### Review Notes With Empty Dropped Material

- None.

## What This Report Deliberately Omits

- No completeness ratios.
- No coverage-style scoring.
- No quality grade.
- No automated drop or rewrite recommendations.
- No semantic genericity scoring beyond PR 1 validation.
