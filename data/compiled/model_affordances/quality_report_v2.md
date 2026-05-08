# Model Affordance Quality Report v2

This report surfaces honesty signals for human reviewers. It does not grade quality, infer missing knowledge, or promote any affordance into runtime use.

## Honesty Signals

- Contributing records: `30`
- Compiled affordances: `52`
- Compiled absence records: `32`
- Affordance count distribution per model:
  - `1` affordance(s): anchoring, base-rates, calculated-risk-taking, circle-of-control, expected-value, flow, johari-window, lindy-effect, multi-criteria-decision-analysis, occams-razor, premortem, risk-assessment, second-order-thinking, sunk-cost-fallacy, trade-offs
  - `2` affordance(s): decision-trees, decomposition, emergence, incentives, information-asymmetry, network-effects, optionality, power-dynamics, theory-of-constraints
  - `3` affordance(s): complex-adaptive-systems, confidence-calibration, inversion, leverage-points, problem-framing-and-reframing
  - `4` affordance(s): systems-thinking
- Absence record status counts:
  - `deferred_for_review`: `1`
  - `duplicate_of_existing_field`: `9`
  - `not_supported_by_source`: `14`
  - `source_too_thin`: `8`
- Affordance confidence counts:
  - `high`: `52`
  - `medium`: `0`
  - `weak`: `0`
  - `not_applicable`: `0`
- Affordance status counts:
  - `supported`: `52`
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
| `anchoring` | 1 | 2 | `high` | none |
| `base-rates` | 1 | 1 | `high` | none |
| `calculated-risk-taking` | 1 | 2 | `high` | none |
| `circle-of-control` | 1 | 2 | `high` | none |
| `complex-adaptive-systems` | 3 | 2 | `high` | none |
| `confidence-calibration` | 3 | 0 | `high` | `confidence-calibration.method-first-self-interrogation` |
| `decision-trees` | 2 | 0 | `high` | none |
| `decomposition` | 2 | 2 | `high` | none |
| `emergence` | 2 | 2 | `high` | none |
| `expected-value` | 1 | 1 | `high` | none |
| `flow` | 1 | 2 | `high` | none |
| `incentives` | 2 | 1 | `high` | none |
| `information-asymmetry` | 2 | 2 | `high` | none |
| `inversion` | 3 | 0 | `high` | `inversion.obstacle-removal-before-added-force` |
| `johari-window` | 1 | 2 | `high` | none |
| `leverage-points` | 3 | 1 | `high` | none |
| `lindy-effect` | 1 | 0 | `high` | none |
| `multi-criteria-decision-analysis` | 1 | 2 | `high` | none |
| `network-effects` | 2 | 2 | `high` | none |
| `occams-razor` | 1 | 2 | `high` | none |
| `optionality` | 2 | 0 | `high` | none |
| `power-dynamics` | 2 | 0 | `high` | none |
| `premortem` | 1 | 0 | `high` | none |
| `problem-framing-and-reframing` | 3 | 1 | `high` | none |
| `risk-assessment` | 1 | 2 | `high` | none |
| `second-order-thinking` | 1 | 0 | `high` | none |
| `sunk-cost-fallacy` | 1 | 0 | `high` | none |
| `systems-thinking` | 4 | 0 | `high` | `systems-thinking.structure-over-events` |
| `theory-of-constraints` | 2 | 0 | `high` | none |
| `trade-offs` | 1 | 1 | `high` | none |

## Cross-Model Deterministic Observations

### Identical Extraction-Type Distributions

- calculated-risk-taking, occams-razor: `{'explicit': 14, 'not_supported_by_source': 4}`
- incentives, trade-offs: `{'explicit': 16, 'not_supported_by_source': 2}`
- lindy-effect, premortem: `{'explicit': 16}`
- emergence, flow: `{'explicit': 19, 'not_supported_by_source': 4}`
- confidence-calibration, decision-trees: `{'explicit': 20}`

### Repeated Diagnostic Question Openings

- `is the worst case bad` appears in `8` affordance(s): `anchoring.provisional-anchor-with-correction`, `calculated-risk-taking.pressure-tested-bounded-wager`, `expected-value.probability-weighted-payoff-boundary`, `leverage-points.resistance-bias-execution-hardening`, `multi-criteria-decision-analysis.auditable-weighted-tradeoff-matrix`, `optionality.preserve-reversible-learning`, `premortem.simulated-failure-to-plan-change`, `risk-assessment.thresholded-downside-governance`
- `what would you have to` appears in `6` affordance(s): `anchoring.provisional-anchor-with-correction`, `decomposition.test-cuts-and-assumptions`, `expected-value.probability-weighted-payoff-boundary`, `premortem.simulated-failure-to-plan-change`, `problem-framing-and-reframing.falsify-frame-assumptions`, `trade-offs.allocation-backed-sacrifice`
- `what assumptions are embedded in` appears in `2` affordance(s): `decomposition.test-cuts-and-assumptions`, `occams-razor.lowest-assumption-evidence-pruning`
- `what is the single core` appears in `2` affordance(s): `decomposition.mece-key-driver-action-map`, `problem-framing-and-reframing.define-before-analysis`
- `what other disciplines or frameworks` appears in `2` affordance(s): `anchoring.provisional-anchor-with-correction`, `problem-framing-and-reframing.test-alternative-frames`
- `what would have to be` appears in `2` affordance(s): `complex-adaptive-systems.assumption-and-bias-exposure`, `leverage-points.resistance-bias-execution-hardening`
- `what would we have to` appears in `2` affordance(s): `calculated-risk-taking.pressure-tested-bounded-wager`, `network-effects.critical-mass-feedback-proof`

### Affordances With Short Source Quotes

Median affordance-level source quote length: `136` characters.

- `anchoring.provisional-anchor-with-correction`: shortest quote `29` chars across `15` quote(s)
- `optionality.preserve-reversible-learning`: shortest quote `29` chars across `10` quote(s)
- `calculated-risk-taking.pressure-tested-bounded-wager`: shortest quote `31` chars across `10` quote(s)
- `premortem.simulated-failure-to-plan-change`: shortest quote `31` chars across `13` quote(s)
- `problem-framing-and-reframing.falsify-frame-assumptions`: shortest quote `31` chars across `8` quote(s)
- `theory-of-constraints.constraint-shift-cadence`: shortest quote `31` chars across `8` quote(s)
- `trade-offs.allocation-backed-sacrifice`: shortest quote `31` chars across `11` quote(s)
- `complex-adaptive-systems.ordered-adaptive-learning-loop`: shortest quote `34` chars across `5` quote(s)
- `power-dynamics.commitment-gradient-inversion`: shortest quote `34` chars across `9` quote(s)
- `flow.calibrated-immersion-channel`: shortest quote `39` chars across `15` quote(s)
- `leverage-points.hypothesis-bounded-analysis`: shortest quote `39` chars across `7` quote(s)
- `information-asymmetry.extract-tacit-knowledge-for-recipient`: shortest quote `41` chars across `15` quote(s)
- `risk-assessment.thresholded-downside-governance`: shortest quote `41` chars across `13` quote(s)
- `power-dynamics.outside-option-credibility`: shortest quote `43` chars across `12` quote(s)
- `expected-value.probability-weighted-payoff-boundary`: shortest quote `46` chars across `16` quote(s)
- `optionality.expand-before-evaluating`: shortest quote `49` chars across `8` quote(s)
- `problem-framing-and-reframing.define-before-analysis`: shortest quote `52` chars across `10` quote(s)
- `base-rates.outside-view-reference-class-anchor`: shortest quote `53` chars across `16` quote(s)
- `multi-criteria-decision-analysis.auditable-weighted-tradeoff-matrix`: shortest quote `54` chars across `12` quote(s)
- `sunk-cost-fallacy.future-value-recommitment`: shortest quote `54` chars across `18` quote(s)
- `inversion.disconfirmation-before-defense`: shortest quote `55` chars across `7` quote(s)
- `problem-framing-and-reframing.test-alternative-frames`: shortest quote `55` chars across `9` quote(s)
- `network-effects.pre-threshold-adoption-path`: shortest quote `59` chars across `8` quote(s)
- `circle-of-control.control-influence-action-map`: shortest quote `66` chars across `13` quote(s)
- `decomposition.test-cuts-and-assumptions`: shortest quote `66` chars across `11` quote(s)
- `emergence.design-conditions-feedback-not-script`: shortest quote `66` chars across `9` quote(s)
- `systems-thinking.structure-over-events`: shortest quote `66` chars across `6` quote(s)
- `incentives.reward-structure-before-behavior-judgment`: shortest quote `67` chars across `5` quote(s)
- `confidence-calibration.instrument-trust-before-precision`: shortest quote `68` chars across `6` quote(s)
- `decomposition.mece-key-driver-action-map`: shortest quote `68` chars across `13` quote(s)
- `johari-window.specific-feedback-disclosure-loop`: shortest quote `68` chars across `17` quote(s)
- `systems-thinking.feedback-loop-mapping`: shortest quote `70` chars across `7` quote(s)
- `lindy-effect.longevity-prior-with-baseline-break-check`: shortest quote `71` chars across `12` quote(s)
- `confidence-calibration.method-first-self-interrogation`: shortest quote `73` chars across `6` quote(s)
- `inversion.anti-goal-failure-mechanism-map`: shortest quote `74` chars across `8` quote(s)
- `complex-adaptive-systems.assumption-and-bias-exposure`: shortest quote `78` chars across `7` quote(s)
- `network-effects.critical-mass-feedback-proof`: shortest quote `78` chars across `7` quote(s)
- `inversion.obstacle-removal-before-added-force`: shortest quote `86` chars across `6` quote(s)
- `decision-trees.branch-trigger-map`: shortest quote `92` chars across `9` quote(s)
- `occams-razor.lowest-assumption-evidence-pruning`: shortest quote `93` chars across `10` quote(s)
- `systems-thinking.metric-leverage-design`: shortest quote `95` chars across `4` quote(s)
- `information-asymmetry.redesign-party-controlled-evidence`: shortest quote `106` chars across `18` quote(s)
- `decision-trees.branch-kill-hardening`: shortest quote `117` chars across `8` quote(s)
- `theory-of-constraints.constraint-first-cap`: shortest quote `118` chars across `9` quote(s)
- `leverage-points.structural-point-proof`: shortest quote `124` chars across `8` quote(s)
- `second-order-thinking.downstream-reversal-stress-test`: shortest quote `124` chars across `8` quote(s)
- `emergence.map-interaction-produced-behavior`: shortest quote `125` chars across `6` quote(s)
- `systems-thinking.architecture-misdiagnosis-test`: shortest quote `126` chars across `6` quote(s)
- `incentives.task-fit-and-second-order-reward-design`: shortest quote `129` chars across `7` quote(s)
- `confidence-calibration.commitment-sizing-to-earned-range`: shortest quote `131` chars across `6` quote(s)
- `complex-adaptive-systems.adaptive-feedback-leverage-choice`: shortest quote `134` chars across `5` quote(s)
- `leverage-points.resistance-bias-execution-hardening`: shortest quote `135` chars across `9` quote(s)

### Review Notes With Empty Dropped Material

- None.

## What This Report Deliberately Omits

- No completeness ratios.
- No coverage-style scoring.
- No quality grade.
- No automated drop or rewrite recommendations.
- No semantic genericity scoring beyond PR 1 validation.
