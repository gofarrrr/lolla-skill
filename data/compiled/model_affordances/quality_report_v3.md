# Model Affordance Quality Report v3

This report surfaces honesty signals for human reviewers. It does not grade quality, infer missing knowledge, or promote any affordance into runtime use.

## Honesty Signals

- Contributing records: `50`
- Compiled affordances: `86`
- Compiled absence records: `83`
- Affordance count distribution per model:
  - `1` affordance(s): adverse-selection, anchoring, antifragility, base-rates, calculated-risk-taking, circle-of-control, comparative-advantage, expected-value, flow, johari-window, lindy-effect, margin-of-safety, multi-criteria-decision-analysis, occams-razor, pareto-principle, premortem, resilience, risk-assessment, second-order-thinking, six-thinking-hats, sunk-cost-fallacy, trade-offs
  - `2` affordance(s): aleatory-epistemic-uncertainty-recognition, black-swan-events, correlation-vs-causation, decision-trees, decomposition, emergence, experimentation, incentives, information-asymmetry, law-of-large-numbers, moral-hazard, network-effects, optimization-theory, optionality, power-dynamics, prioritization, psychological-safety, social-proof, statistical-discipline, survivorship-bias, theory-of-constraints
  - `3` affordance(s): complex-adaptive-systems, confidence-calibration, empathy, inversion, leverage-points, problem-framing-and-reframing
  - `4` affordance(s): systems-thinking
- Absence record status counts:
  - `deferred_for_review`: `1`
  - `duplicate_of_existing_field`: `32`
  - `not_supported_by_source`: `36`
  - `source_too_thin`: `14`
- Affordance confidence counts:
  - `high`: `84`
  - `medium`: `2`
  - `weak`: `0`
  - `not_applicable`: `0`
- Affordance status counts:
  - `supported`: `86`
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
| `adverse-selection` | 1 | 2 | `medium` | none |
| `aleatory-epistemic-uncertainty-recognition` | 2 | 2 | `high` | none |
| `anchoring` | 1 | 2 | `high` | none |
| `antifragility` | 1 | 3 | `high` | none |
| `base-rates` | 1 | 1 | `high` | none |
| `black-swan-events` | 2 | 3 | `high` | none |
| `calculated-risk-taking` | 1 | 2 | `high` | none |
| `circle-of-control` | 1 | 2 | `high` | none |
| `comparative-advantage` | 1 | 2 | `high` | none |
| `complex-adaptive-systems` | 3 | 2 | `high` | none |
| `confidence-calibration` | 3 | 0 | `high` | `confidence-calibration.method-first-self-interrogation` |
| `correlation-vs-causation` | 2 | 2 | `high` | none |
| `decision-trees` | 2 | 0 | `high` | none |
| `decomposition` | 2 | 2 | `high` | none |
| `emergence` | 2 | 2 | `high` | none |
| `empathy` | 3 | 2 | `high` | none |
| `expected-value` | 1 | 1 | `high` | none |
| `experimentation` | 2 | 3 | `high` | none |
| `flow` | 1 | 2 | `high` | none |
| `incentives` | 2 | 1 | `high` | none |
| `information-asymmetry` | 2 | 2 | `high` | none |
| `inversion` | 3 | 0 | `high` | `inversion.obstacle-removal-before-added-force` |
| `johari-window` | 1 | 2 | `high` | none |
| `law-of-large-numbers` | 2 | 2 | `high` | none |
| `leverage-points` | 3 | 1 | `high` | none |
| `lindy-effect` | 1 | 0 | `high` | none |
| `margin-of-safety` | 1 | 2 | `high` | none |
| `moral-hazard` | 2 | 3 | `high` | none |
| `multi-criteria-decision-analysis` | 1 | 2 | `high` | none |
| `network-effects` | 2 | 2 | `high` | none |
| `occams-razor` | 1 | 2 | `high` | none |
| `optimization-theory` | 2 | 3 | `high` | none |
| `optionality` | 2 | 0 | `high` | none |
| `pareto-principle` | 1 | 3 | `high` | none |
| `power-dynamics` | 2 | 0 | `high` | none |
| `premortem` | 1 | 0 | `high` | none |
| `prioritization` | 2 | 3 | `high` | none |
| `problem-framing-and-reframing` | 3 | 1 | `high` | none |
| `psychological-safety` | 2 | 2 | `high` | none |
| `resilience` | 1 | 3 | `high` | none |
| `risk-assessment` | 1 | 2 | `high` | none |
| `second-order-thinking` | 1 | 0 | `high` | none |
| `six-thinking-hats` | 1 | 3 | `medium` | none |
| `social-proof` | 2 | 3 | `high` | none |
| `statistical-discipline` | 2 | 2 | `high` | none |
| `sunk-cost-fallacy` | 1 | 0 | `high` | none |
| `survivorship-bias` | 2 | 3 | `high` | none |
| `systems-thinking` | 4 | 0 | `high` | `systems-thinking.structure-over-events` |
| `theory-of-constraints` | 2 | 0 | `high` | none |
| `trade-offs` | 1 | 1 | `high` | none |

## Cross-Model Deterministic Observations

### Identical Extraction-Type Distributions

- calculated-risk-taking, occams-razor: `{'explicit': 14, 'not_supported_by_source': 4}`
- incentives, trade-offs: `{'explicit': 16, 'not_supported_by_source': 2}`
- moral-hazard, psychological-safety: `{'explicit': 16, 'not_supported_by_source': 4, 'review_note': 1}`
- lindy-effect, premortem: `{'explicit': 16}`
- resilience, social-proof: `{'explicit': 19, 'not_supported_by_source': 3, 'review_note': 2}`
- emergence, flow: `{'explicit': 19, 'not_supported_by_source': 4}`
- confidence-calibration, decision-trees: `{'explicit': 20}`
- decomposition, empathy: `{'explicit': 29, 'not_supported_by_source': 4}`

### Repeated Diagnostic Question Openings

- `is the worst case bad` appears in `11` affordance(s): `aleatory-epistemic-uncertainty-recognition.commitment-gating-by-reducibility`, `anchoring.provisional-anchor-with-correction`, `calculated-risk-taking.pressure-tested-bounded-wager`, `expected-value.probability-weighted-payoff-boundary`, `leverage-points.resistance-bias-execution-hardening`, `multi-criteria-decision-analysis.auditable-weighted-tradeoff-matrix`, `optionality.preserve-reversible-learning`, `premortem.simulated-failure-to-plan-change`, `risk-assessment.thresholded-downside-governance`, `statistical-discipline.distributional-inference-stress-test`, `survivorship-bias.restore-failure-tail-outcomes`
- `what would you have to` appears in `6` affordance(s): `anchoring.provisional-anchor-with-correction`, `decomposition.test-cuts-and-assumptions`, `expected-value.probability-weighted-payoff-boundary`, `premortem.simulated-failure-to-plan-change`, `problem-framing-and-reframing.falsify-frame-assumptions`, `trade-offs.allocation-backed-sacrifice`
- `what would we have to` appears in `5` affordance(s): `aleatory-epistemic-uncertainty-recognition.commitment-gating-by-reducibility`, `calculated-risk-taking.pressure-tested-bounded-wager`, `network-effects.critical-mass-feedback-proof`, `resilience.disciplined-recovery-with-continued-function`, `statistical-discipline.distributional-inference-stress-test`
- `what assumptions are embedded in` appears in `3` affordance(s): `decomposition.test-cuts-and-assumptions`, `occams-razor.lowest-assumption-evidence-pruning`, `pareto-principle.measured-vital-few-allocation`
- `what is the single core` appears in `2` affordance(s): `decomposition.mece-key-driver-action-map`, `problem-framing-and-reframing.define-before-analysis`
- `what other disciplines or frameworks` appears in `2` affordance(s): `anchoring.provisional-anchor-with-correction`, `problem-framing-and-reframing.test-alternative-frames`
- `what would have to be` appears in `2` affordance(s): `complex-adaptive-systems.assumption-and-bias-exposure`, `leverage-points.resistance-bias-execution-hardening`
- `what would need to be` appears in `2` affordance(s): `antifragility.bounded-stress-learning-design`, `problem-framing-and-reframing.falsify-frame-assumptions`

### Affordances With Short Source Quotes

Median affordance-level source quote length: `137` characters.

- `social-proof.contain-consensus-contagion`: shortest quote `21` chars across `6` quote(s)
- `aleatory-epistemic-uncertainty-recognition.commitment-gating-by-reducibility`: shortest quote `29` chars across `8` quote(s)
- `anchoring.provisional-anchor-with-correction`: shortest quote `29` chars across `15` quote(s)
- `optionality.preserve-reversible-learning`: shortest quote `29` chars across `10` quote(s)
- `optimization-theory.leverage-bounded-analysis`: shortest quote `30` chars across `11` quote(s)
- `calculated-risk-taking.pressure-tested-bounded-wager`: shortest quote `31` chars across `10` quote(s)
- `premortem.simulated-failure-to-plan-change`: shortest quote `31` chars across `13` quote(s)
- `problem-framing-and-reframing.falsify-frame-assumptions`: shortest quote `31` chars across `8` quote(s)
- `theory-of-constraints.constraint-shift-cadence`: shortest quote `31` chars across `8` quote(s)
- `trade-offs.allocation-backed-sacrifice`: shortest quote `31` chars across `11` quote(s)
- `complex-adaptive-systems.ordered-adaptive-learning-loop`: shortest quote `34` chars across `5` quote(s)
- `power-dynamics.commitment-gradient-inversion`: shortest quote `34` chars across `9` quote(s)
- `pareto-principle.measured-vital-few-allocation`: shortest quote `35` chars across `14` quote(s)
- `flow.calibrated-immersion-channel`: shortest quote `39` chars across `15` quote(s)
- `leverage-points.hypothesis-bounded-analysis`: shortest quote `39` chars across `7` quote(s)
- `optimization-theory.objective-constraint-tradeoff-fit`: shortest quote `39` chars across `11` quote(s)
- `information-asymmetry.extract-tacit-knowledge-for-recipient`: shortest quote `41` chars across `15` quote(s)
- `psychological-safety.surface-withheld-risk-signals`: shortest quote `41` chars across `6` quote(s)
- `risk-assessment.thresholded-downside-governance`: shortest quote `41` chars across `13` quote(s)
- `power-dynamics.outside-option-credibility`: shortest quote `43` chars across `12` quote(s)
- `correlation-vs-causation.test-causal-claim-before-intervention`: shortest quote `45` chars across `9` quote(s)
- `black-swan-events.post-shock-aberration-learning-discipline`: shortest quote `46` chars across `9` quote(s)
- `expected-value.probability-weighted-payoff-boundary`: shortest quote `46` chars across `16` quote(s)
- `optionality.expand-before-evaluating`: shortest quote `49` chars across `8` quote(s)
- `problem-framing-and-reframing.define-before-analysis`: shortest quote `52` chars across `10` quote(s)
- `base-rates.outside-view-reference-class-anchor`: shortest quote `53` chars across `16` quote(s)
- `multi-criteria-decision-analysis.auditable-weighted-tradeoff-matrix`: shortest quote `54` chars across `12` quote(s)
- `sunk-cost-fallacy.future-value-recommitment`: shortest quote `54` chars across `18` quote(s)
- `black-swan-events.tail-exposure-preparation-under-deep-uncertainty`: shortest quote `55` chars across `10` quote(s)
- `inversion.disconfirmation-before-defense`: shortest quote `55` chars across `7` quote(s)
- `problem-framing-and-reframing.test-alternative-frames`: shortest quote `55` chars across `9` quote(s)
- `survivorship-bias.restore-failure-tail-outcomes`: shortest quote `55` chars across `10` quote(s)
- `correlation-vs-causation.trace-root-cause-machine`: shortest quote `57` chars across `9` quote(s)
- `empathy.confirm-reflection-before-treatment`: shortest quote `57` chars across `8` quote(s)
- `network-effects.pre-threshold-adoption-path`: shortest quote `59` chars across `8` quote(s)
- `prioritization.capacity-constrained-exclusion-and-sequencing`: shortest quote `63` chars across `15` quote(s)
- `resilience.disciplined-recovery-with-continued-function`: shortest quote `64` chars across `15` quote(s)
- `psychological-safety.convert-candor-into-correction`: shortest quote `65` chars across `6` quote(s)
- `circle-of-control.control-influence-action-map`: shortest quote `66` chars across `13` quote(s)
- `decomposition.test-cuts-and-assumptions`: shortest quote `66` chars across `11` quote(s)
- `emergence.design-conditions-feedback-not-script`: shortest quote `66` chars across `9` quote(s)
- `systems-thinking.structure-over-events`: shortest quote `66` chars across `6` quote(s)
- `incentives.reward-structure-before-behavior-judgment`: shortest quote `67` chars across `5` quote(s)
- `law-of-large-numbers.repeated-sample-stability-before-inference`: shortest quote `67` chars across `9` quote(s)
- `confidence-calibration.instrument-trust-before-precision`: shortest quote `68` chars across `6` quote(s)
- `decomposition.mece-key-driver-action-map`: shortest quote `68` chars across `13` quote(s)
- `empathy.ground-reframing-in-stakeholder-evidence`: shortest quote `68` chars across `8` quote(s)
- `johari-window.specific-feedback-disclosure-loop`: shortest quote `68` chars across `17` quote(s)
- `systems-thinking.feedback-loop-mapping`: shortest quote `70` chars across `7` quote(s)
- `lindy-effect.longevity-prior-with-baseline-break-check`: shortest quote `71` chars across `12` quote(s)
- `antifragility.bounded-stress-learning-design`: shortest quote `73` chars across `18` quote(s)
- `confidence-calibration.method-first-self-interrogation`: shortest quote `73` chars across `6` quote(s)
- `statistical-discipline.hypothesis-first-tool-fit`: shortest quote `73` chars across `8` quote(s)
- `aleatory-epistemic-uncertainty-recognition.type-specific-tool-routing`: shortest quote `74` chars across `6` quote(s)
- `inversion.anti-goal-failure-mechanism-map`: shortest quote `74` chars across `8` quote(s)
- `complex-adaptive-systems.assumption-and-bias-exposure`: shortest quote `78` chars across `7` quote(s)
- `network-effects.critical-mass-feedback-proof`: shortest quote `78` chars across `7` quote(s)
- `social-proof.verify-context-matched-proof`: shortest quote `78` chars across `8` quote(s)
- `empathy.substitute-perspective-taking-under-strategic-risk`: shortest quote `82` chars across `8` quote(s)
- `statistical-discipline.distributional-inference-stress-test`: shortest quote `82` chars across `10` quote(s)
- `inversion.obstacle-removal-before-added-force`: shortest quote `86` chars across `6` quote(s)
- `decision-trees.branch-trigger-map`: shortest quote `92` chars across `9` quote(s)
- `survivorship-bias.recover-hidden-denominator-selection`: shortest quote `92` chars across `11` quote(s)
- `experimentation.hypothesis-bound-decision-test`: shortest quote `93` chars across `12` quote(s)
- `occams-razor.lowest-assumption-evidence-pruning`: shortest quote `93` chars across `10` quote(s)
- `systems-thinking.metric-leverage-design`: shortest quote `95` chars across `4` quote(s)
- `moral-hazard.proxy-hidden-effort-with-noisy-outcomes`: shortest quote `99` chars across `5` quote(s)
- `six-thinking-hats.separate-modes-before-synthesis`: shortest quote `99` chars across `7` quote(s)
- `information-asymmetry.redesign-party-controlled-evidence`: shortest quote `106` chars across `18` quote(s)
- `moral-hazard.align-decision-rights-with-downside`: shortest quote `108` chars across `6` quote(s)
- `adverse-selection.verify-hidden-type-selection`: shortest quote `110` chars across `4` quote(s)
- `decision-trees.branch-kill-hardening`: shortest quote `117` chars across `8` quote(s)
- `theory-of-constraints.constraint-first-cap`: shortest quote `118` chars across `9` quote(s)
- `law-of-large-numbers.population-and-distribution-fit-before-large-n-confidence`: shortest quote `119` chars across `5` quote(s)
- `leverage-points.structural-point-proof`: shortest quote `124` chars across `8` quote(s)
- `second-order-thinking.downstream-reversal-stress-test`: shortest quote `124` chars across `8` quote(s)
- `emergence.map-interaction-produced-behavior`: shortest quote `125` chars across `6` quote(s)
- `systems-thinking.architecture-misdiagnosis-test`: shortest quote `126` chars across `6` quote(s)
- `margin-of-safety.evidence-sized-operating-buffer`: shortest quote `128` chars across `9` quote(s)
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

## Cumulative Corpus Shape

| Batch | Models | Affordances | Absence Records |
| --- | ---: | ---: | ---: |
| Pilot | 10 | 22 | 2 |
| Batch 1 | 20 | 30 | 30 |
| Batch 2 | 20 | 34 | 51 |
| **Total (v3)** | **50** | **86** | **83** |

Absence-record density has grown with each batch: Pilot averaged 0.2 per model, Batch 1 averaged 1.5, Batch 2 averaged 2.6. This is directionally correct — the extraction contract is refusing generic field promotion rather than vacuuming up candidate material.

## Reviewer-Eye Acceptance Notes — Batch 2

These notes record the PM/reviewer judgment calls from the Batch 2 reviewer-eye pass (2026-05-05). They are not part of the mechanical compilation output.

- **`adverse-selection`** — `medium` affordance confidence accepted. Source explicitly states the named model is not present in the provided materials; the operational mechanism (hidden-type rent capture) is nonetheless source-backed with high-confidence quotes. Medium confidence is the correct signal. Do not downgrade to `weak_support` without a second review that finds the mechanism itself unsupported.
- **`empathy`** — Three-affordance record accepted. The third affordance (`empathy.substitute-perspective-taking-under-strategic-risk`) passed the structural differentiation test: it activates specifically when emotional empathy threatens strategic clarity or creates self-interest blind spots, a distinct treatment requirement from the first two affordances. Read this record first when the corpus reaches runtime evaluation.
- **`six-thinking-hats`** — Named-model caveat accepted. The affordance is source-backed through analogous role and mode separation; the named model is not explicitly present in the underlying materials. `medium` confidence on the affordance is the correct signal. If future runtime distinguishes human deliberation from AI-agent orchestration, the AI advisory-board example may deserve a separate reviewed source.
- **`pareto-principle`** — "Protected trial" normalization accepted with promotion note. The language is acceptable operational normalization of the source's 80/20 selection mechanism. When this affordance is considered for runtime promotion, the treatment requirement `retest-and-protect-future-drivers` should be reviewed to confirm the protected-trial framing holds under test.
- **`survivorship-bias`** — Failure-tail affordance accepted. The `base-rates` boundary is explicit in `do_not_use_when`. The failure-tail affordance (`survivorship-bias.restore-failure-tail-outcomes`) is survivorship-specific — it requires a selection mechanism that systematically excluded the failed cases, not generic risk assessment. Adjacent risk records verified: the boundary holds.

## Gate 3 Status

**Gate 3: cleared.**

50 models extracted across pilot, Batch 1, and Batch 2. Projected candidate-appearance coverage: **75.2%** across 21 archived Lane 4 runs (334 / 444 candidate appearances covered). Gap-route coverage: **92.0%** (80 / 87 gap-route rows).

Gate 3 cleared does not mean runtime value is proven. The gate ladder continues:

| Gate | Criterion | Status |
| --- | --- | --- |
| 1 | Instrument works (pilot calibrated) | ✅ cleared |
| 2 | Batch scales without quality collapse | ✅ cleared |
| 3 | Coverage reaches meaningful runtime slice | ✅ cleared |
| 4 | User-facing output beats baseline on archived cases | ⬜ not started |
| 5 | Stack merges to main | ⬜ blocked on Gate 4 |

No runtime consumer uses v3 records yet. Compilation to `affordances_v3.json` is the mechanical closeout of Gate 3. Gate 4 work — surfacing, baseline selection, judging archived cases — begins in the next PR.
