# Model Affordance Quality Report v37

This report surfaces honesty signals for human reviewers. It does not grade quality, infer missing knowledge, or promote any affordance into runtime use.

## Honesty Signals

- Contributing records: `222`
- Compiled affordances: `271`
- Compiled absence records: `509`
- Affordance count distribution per model:
  - `1` affordance(s): abstraction, active-listening, adaptation, adverse-selection, agile-methodologies, algorithmic-thinking, analogies-and-metaphors, anchoring, antifragility, association, auditability-traceability, authenticity, authority-bias, base-rates, baseline-establishment, batna, bayesian, bias-blind-spot, blooms-taxonomy, bottlenecks, boundaries, brainstorming, branch-solve-merge, butterfly-effect, calculated-risk-taking, category-decisions, causal-attribution-resistance, chain-of-thought, chain-of-verification, chaos-theory, checklists, circle-of-competence, circle-of-control, cognitive-biases, cognitive-dissonance, cognitive-gaps-assessment, cognitive-load-theory, combinatorial-effects, comparative-advantage, comparative-political-systems-analysis, complexity-bias-resistance, compounding, confirmation-bias, conjunction-fallacy, constraints, constructive-feedback-models, consulting-firms-methodology, counterfactual-reasoning, creative-destruction, critical-mass, critical-thinking, cross-cultural-communication-frameworks, cultural-dimensions-theory, cultural-intelligence, curiosity, curse-of-knowledge, cybersecurity-thinking-models, data-science-reasoning-framework, debugging-strategies, delays, deliberate-practice, desirable-difficulties, devops-and-continuous-integration, dialectical-reasoning, divergent-vs-convergent-thinking, dunning-kruger-effect, einstellung-effect, elasticity, endowment-effect, evolutionary-pressure, expected-value, expertise-reversal-effect, extreme-performance-evaluation, false-precision-avoidance, falsifiability, feedback-models-sbi, feynman-technique, first-principles-thinking, five-whys-method, flow, formal-reasoning, game-theory-payoffs, generation-effect, gestalt-principles-of-perception, goal-setting, growth-mindset, habit-formation, hanlons-razor, hindsight-bias, information-theory, input-vs-output-goals, intellectual-humility, internal-locus-of-control, international-negotiation-and-diplomacy-models, iteration, jobs-to-be-done, johari-window, lateral-thinking, latticework-of-mental-models, lean-startup-methodology, learning-curve, liking-principle, lindy-effect, logical-fallacies, margin-of-safety, markov-chains, mental-models-of-reality, meta-cognitive-reflection, monte-carlo-methods, multi-criteria-decision-analysis, multicultural-team-dynamics, narratives, nash-equilibrium, natural-selection-analogy, non-linear-dynamics, non-violent-communication, obligations-controls-mapping, occams-razor, opportunity-cost, optimism-bias-and-planning-fallacy, pareto-principle, peer-review-your-perspectives, perceptual-learning, persistence-grit, persuasion-principles, peter-principle, power-laws, pre-suasion, premortem, price-discrimination, principal-agent-problem, prisoners-dilemma, probabilistic-thinking, prospect-theory, rationalization, reasoning-mode-router, reciprocity-principle, red-queen-effect, reframing-perspective, regression-to-the-mean, regret-theory, regulatory-horizon-scanning, representativeness-heuristic, resilience, risk-assessment, risk-vs-uncertainty, root-cause-analysis, scaffolding, scaffolding-educational, scale-economies, schema-acquisition, scientific-method-evidence-testing, second-order-thinking, self-control, self-determination-theory, self-organization-and-emergent-order, signaling, simplification, six-thinking-hats, specialization, statistical-learning-theory, statistics-concepts, status-quo-bias, step-back, storytelling-frameworks, sunk-cost-fallacy, supply-and-demand, synthesis-and-integration, system-1, system-2, theory-induced-blindness, tier-2-high-value, time-tested-validation, tipping-points, trade-offs, tradition-vs-innovation-balance, true-uncertainty-navigation, understanding-motivations, usability-heuristics, user-centered-design, user-experience-research-methods, variation-and-selection, varied-practice-interleaving, wysiati, zone-of-development
  - `2` affordance(s): aleatory-epistemic-uncertainty-recognition, black-swan-events, commitment-bias, correlation-vs-causation, decision-trees, decomposition, emergence, emotional-intelligence, experimentation, feedback-loops, incentives, information-asymmetry, law-of-large-numbers, lock-in, mental-simulation, metacognitive-questioning, moral-hazard, network-effects, optimization-theory, optionality, path-dependence, prioritization, psychological-safety, redundancy, social-proof, statistical-discipline, survivorship-bias, switching-costs, theory-of-constraints
  - `3` affordance(s): complex-adaptive-systems, confidence-calibration, empathy, power-dynamics, problem-framing-and-reframing
  - `4` affordance(s): leverage-points, systems-thinking
  - `5` affordance(s): inversion
- Absence record status counts:
  - `deferred_for_review`: `1`
  - `duplicate_of_existing_field`: `59`
  - `not_supported_by_source`: `432`
  - `source_too_thin`: `17`
- Affordance confidence counts:
  - `high`: `264`
  - `medium`: `7`
  - `weak`: `0`
  - `not_applicable`: `0`
- Affordance status counts:
  - `supported`: `269`
  - `weak_support`: `2`
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
| `abstraction` | 1 | 2 | `high` | none |
| `active-listening` | 1 | 4 | `high` | none |
| `adaptation` | 1 | 2 | `high` | none |
| `adverse-selection` | 1 | 4 | `medium` | none |
| `agile-methodologies` | 1 | 2 | `high` | none |
| `aleatory-epistemic-uncertainty-recognition` | 2 | 2 | `high` | none |
| `algorithmic-thinking` | 1 | 2 | `high` | none |
| `analogies-and-metaphors` | 1 | 2 | `high` | none |
| `anchoring` | 1 | 3 | `high` | none |
| `antifragility` | 1 | 3 | `high` | none |
| `association` | 1 | 2 | `high` | none |
| `auditability-traceability` | 1 | 2 | `high` | none |
| `authenticity` | 1 | 2 | `high` | none |
| `authority-bias` | 1 | 2 | `high` | none |
| `base-rates` | 1 | 2 | `high` | none |
| `baseline-establishment` | 1 | 3 | `high` | none |
| `batna` | 1 | 4 | `medium` | none |
| `bayesian` | 1 | 2 | `high` | none |
| `bias-blind-spot` | 1 | 2 | `high` | none |
| `black-swan-events` | 2 | 3 | `high` | none |
| `blooms-taxonomy` | 1 | 2 | `high` | none |
| `bottlenecks` | 1 | 2 | `high` | none |
| `boundaries` | 1 | 2 | `high` | none |
| `brainstorming` | 1 | 2 | `high` | none |
| `branch-solve-merge` | 1 | 2 | `high` | none |
| `butterfly-effect` | 1 | 2 | `high` | none |
| `calculated-risk-taking` | 1 | 2 | `high` | none |
| `category-decisions` | 1 | 3 | `high` | none |
| `causal-attribution-resistance` | 1 | 2 | `high` | none |
| `chain-of-thought` | 1 | 4 | `high` | none |
| `chain-of-verification` | 1 | 4 | `high` | none |
| `chaos-theory` | 1 | 3 | `high` | none |
| `checklists` | 1 | 2 | `high` | none |
| `circle-of-competence` | 1 | 2 | `high` | none |
| `circle-of-control` | 1 | 2 | `high` | none |
| `cognitive-biases` | 1 | 2 | `high` | none |
| `cognitive-dissonance` | 1 | 2 | `high` | none |
| `cognitive-gaps-assessment` | 1 | 2 | `high` | none |
| `cognitive-load-theory` | 1 | 2 | `high` | none |
| `combinatorial-effects` | 1 | 2 | `high` | none |
| `commitment-bias` | 2 | 2 | `high` | none |
| `comparative-advantage` | 1 | 2 | `high` | none |
| `comparative-political-systems-analysis` | 1 | 2 | `high` | none |
| `complex-adaptive-systems` | 3 | 2 | `high` | none |
| `complexity-bias-resistance` | 1 | 2 | `high` | none |
| `compounding` | 1 | 2 | `high` | none |
| `confidence-calibration` | 3 | 2 | `high` | `confidence-calibration.method-first-self-interrogation` |
| `confirmation-bias` | 1 | 2 | `high` | none |
| `conjunction-fallacy` | 1 | 4 | `high` | none |
| `constraints` | 1 | 2 | `high` | none |
| `constructive-feedback-models` | 1 | 3 | `high` | none |
| `consulting-firms-methodology` | 1 | 2 | `high` | none |
| `correlation-vs-causation` | 2 | 2 | `high` | none |
| `counterfactual-reasoning` | 1 | 2 | `high` | none |
| `creative-destruction` | 1 | 2 | `high` | none |
| `critical-mass` | 1 | 2 | `high` | none |
| `critical-thinking` | 1 | 4 | `high` | none |
| `cross-cultural-communication-frameworks` | 1 | 2 | `high` | none |
| `cultural-dimensions-theory` | 1 | 2 | `high` | none |
| `cultural-intelligence` | 1 | 2 | `high` | none |
| `curiosity` | 1 | 2 | `high` | none |
| `curse-of-knowledge` | 1 | 2 | `high` | none |
| `cybersecurity-thinking-models` | 1 | 2 | `high` | none |
| `data-science-reasoning-framework` | 1 | 2 | `high` | none |
| `debugging-strategies` | 1 | 2 | `high` | none |
| `decision-trees` | 2 | 3 | `high` | none |
| `decomposition` | 2 | 2 | `high` | none |
| `delays` | 1 | 2 | `high` | none |
| `deliberate-practice` | 1 | 2 | `high` | none |
| `desirable-difficulties` | 1 | 2 | `high` | none |
| `devops-and-continuous-integration` | 1 | 3 | `medium` | none |
| `dialectical-reasoning` | 1 | 2 | `high` | none |
| `divergent-vs-convergent-thinking` | 1 | 2 | `high` | none |
| `dunning-kruger-effect` | 1 | 2 | `high` | none |
| `einstellung-effect` | 1 | 2 | `high` | none |
| `elasticity` | 1 | 3 | `high` | none |
| `emergence` | 2 | 2 | `high` | none |
| `emotional-intelligence` | 2 | 2 | `high` | none |
| `empathy` | 3 | 2 | `high` | none |
| `endowment-effect` | 1 | 2 | `high` | none |
| `evolutionary-pressure` | 1 | 3 | `high` | none |
| `expected-value` | 1 | 3 | `high` | none |
| `experimentation` | 2 | 3 | `high` | none |
| `expertise-reversal-effect` | 1 | 2 | `high` | none |
| `extreme-performance-evaluation` | 1 | 2 | `high` | none |
| `false-precision-avoidance` | 1 | 2 | `high` | none |
| `falsifiability` | 1 | 2 | `high` | none |
| `feedback-loops` | 2 | 2 | `high` | none |
| `feedback-models-sbi` | 1 | 3 | `high` | none |
| `feynman-technique` | 1 | 2 | `high` | none |
| `first-principles-thinking` | 1 | 2 | `high` | none |
| `five-whys-method` | 1 | 2 | `high` | none |
| `flow` | 1 | 2 | `high` | none |
| `formal-reasoning` | 1 | 2 | `high` | none |
| `game-theory-payoffs` | 1 | 3 | `high` | none |
| `generation-effect` | 1 | 2 | `high` | none |
| `gestalt-principles-of-perception` | 1 | 2 | `high` | none |
| `goal-setting` | 1 | 2 | `high` | none |
| `growth-mindset` | 1 | 3 | `high` | none |
| `habit-formation` | 1 | 2 | `high` | none |
| `hanlons-razor` | 1 | 2 | `high` | none |
| `hindsight-bias` | 1 | 2 | `high` | none |
| `incentives` | 2 | 2 | `high` | none |
| `information-asymmetry` | 2 | 2 | `high` | none |
| `information-theory` | 1 | 3 | `high` | none |
| `input-vs-output-goals` | 1 | 2 | `high` | none |
| `intellectual-humility` | 1 | 2 | `high` | none |
| `internal-locus-of-control` | 1 | 3 | `high` | none |
| `international-negotiation-and-diplomacy-models` | 1 | 3 | `high` | none |
| `inversion` | 5 | 3 | `high` | `inversion.obstacle-removal-before-added-force` |
| `iteration` | 1 | 2 | `high` | none |
| `jobs-to-be-done` | 1 | 2 | `high` | none |
| `johari-window` | 1 | 2 | `high` | none |
| `lateral-thinking` | 1 | 2 | `high` | none |
| `latticework-of-mental-models` | 1 | 2 | `high` | none |
| `law-of-large-numbers` | 2 | 2 | `high` | none |
| `lean-startup-methodology` | 1 | 2 | `high` | none |
| `learning-curve` | 1 | 2 | `high` | none |
| `leverage-points` | 4 | 2 | `high` | none |
| `liking-principle` | 1 | 2 | `high` | none |
| `lindy-effect` | 1 | 2 | `high` | none |
| `lock-in` | 2 | 2 | `high` | none |
| `logical-fallacies` | 1 | 2 | `high` | none |
| `margin-of-safety` | 1 | 2 | `high` | none |
| `markov-chains` | 1 | 4 | `medium` | none |
| `mental-models-of-reality` | 1 | 4 | `high` | none |
| `mental-simulation` | 2 | 2 | `high` | none |
| `meta-cognitive-reflection` | 1 | 4 | `high` | none |
| `metacognitive-questioning` | 2 | 2 | `high` | none |
| `monte-carlo-methods` | 1 | 2 | `high` | none |
| `moral-hazard` | 2 | 3 | `high` | none |
| `multi-criteria-decision-analysis` | 1 | 3 | `high` | none |
| `multicultural-team-dynamics` | 1 | 2 | `high` | none |
| `narratives` | 1 | 3 | `high` | none |
| `nash-equilibrium` | 1 | 2 | `high` | none |
| `natural-selection-analogy` | 1 | 2 | `high` | none |
| `network-effects` | 2 | 2 | `high` | none |
| `non-linear-dynamics` | 1 | 2 | `high` | none |
| `non-violent-communication` | 1 | 2 | `high` | none |
| `obligations-controls-mapping` | 1 | 2 | `high` | none |
| `occams-razor` | 1 | 2 | `high` | none |
| `opportunity-cost` | 1 | 2 | `high` | none |
| `optimism-bias-and-planning-fallacy` | 1 | 2 | `high` | none |
| `optimization-theory` | 2 | 3 | `high` | none |
| `optionality` | 2 | 2 | `high` | none |
| `pareto-principle` | 1 | 3 | `high` | none |
| `path-dependence` | 2 | 2 | `high` | none |
| `peer-review-your-perspectives` | 1 | 2 | `high` | none |
| `perceptual-learning` | 1 | 2 | `high` | none |
| `persistence-grit` | 1 | 2 | `high` | none |
| `persuasion-principles` | 1 | 3 | `high` | none |
| `peter-principle` | 1 | 2 | `high` | none |
| `power-dynamics` | 3 | 2 | `high` | none |
| `power-laws` | 1 | 2 | `high` | none |
| `pre-suasion` | 1 | 2 | `high` | none |
| `premortem` | 1 | 2 | `high` | none |
| `price-discrimination` | 1 | 4 | `medium` | none |
| `principal-agent-problem` | 1 | 4 | `medium` | none |
| `prioritization` | 2 | 3 | `high` | none |
| `prisoners-dilemma` | 1 | 2 | `high` | none |
| `probabilistic-thinking` | 1 | 3 | `high` | none |
| `problem-framing-and-reframing` | 3 | 2 | `high` | none |
| `prospect-theory` | 1 | 2 | `high` | none |
| `psychological-safety` | 2 | 2 | `high` | none |
| `rationalization` | 1 | 2 | `high` | none |
| `reasoning-mode-router` | 1 | 3 | `high` | none |
| `reciprocity-principle` | 1 | 2 | `high` | none |
| `red-queen-effect` | 1 | 2 | `high` | none |
| `redundancy` | 2 | 2 | `high` | none |
| `reframing-perspective` | 1 | 2 | `high` | none |
| `regression-to-the-mean` | 1 | 2 | `high` | none |
| `regret-theory` | 1 | 2 | `high` | none |
| `regulatory-horizon-scanning` | 1 | 2 | `high` | none |
| `representativeness-heuristic` | 1 | 2 | `high` | none |
| `resilience` | 1 | 3 | `high` | none |
| `risk-assessment` | 1 | 2 | `high` | none |
| `risk-vs-uncertainty` | 1 | 2 | `high` | none |
| `root-cause-analysis` | 1 | 2 | `high` | none |
| `scaffolding` | 1 | 3 | `high` | none |
| `scaffolding-educational` | 1 | 3 | `high` | none |
| `scale-economies` | 1 | 2 | `high` | none |
| `schema-acquisition` | 1 | 2 | `high` | none |
| `scientific-method-evidence-testing` | 1 | 2 | `high` | none |
| `second-order-thinking` | 1 | 4 | `high` | none |
| `self-control` | 1 | 2 | `high` | none |
| `self-determination-theory` | 1 | 2 | `high` | none |
| `self-organization-and-emergent-order` | 1 | 2 | `high` | none |
| `signaling` | 1 | 2 | `high` | none |
| `simplification` | 1 | 2 | `high` | none |
| `six-thinking-hats` | 1 | 5 | `medium` | none |
| `social-proof` | 2 | 3 | `high` | none |
| `specialization` | 1 | 2 | `high` | none |
| `statistical-discipline` | 2 | 2 | `high` | none |
| `statistical-learning-theory` | 1 | 2 | `high` | none |
| `statistics-concepts` | 1 | 2 | `high` | none |
| `status-quo-bias` | 1 | 2 | `high` | none |
| `step-back` | 1 | 2 | `high` | none |
| `storytelling-frameworks` | 1 | 2 | `high` | none |
| `sunk-cost-fallacy` | 1 | 2 | `high` | none |
| `supply-and-demand` | 1 | 2 | `high` | none |
| `survivorship-bias` | 2 | 3 | `high` | none |
| `switching-costs` | 2 | 2 | `high` | none |
| `synthesis-and-integration` | 1 | 2 | `high` | none |
| `system-1` | 1 | 2 | `high` | none |
| `system-2` | 1 | 2 | `high` | none |
| `systems-thinking` | 4 | 3 | `high` | `systems-thinking.structure-over-events` |
| `theory-induced-blindness` | 1 | 2 | `high` | none |
| `theory-of-constraints` | 2 | 2 | `high` | none |
| `tier-2-high-value` | 1 | 2 | `high` | none |
| `time-tested-validation` | 1 | 2 | `high` | none |
| `tipping-points` | 1 | 2 | `high` | none |
| `trade-offs` | 1 | 3 | `high` | none |
| `tradition-vs-innovation-balance` | 1 | 2 | `high` | none |
| `true-uncertainty-navigation` | 1 | 2 | `high` | none |
| `understanding-motivations` | 1 | 2 | `high` | none |
| `usability-heuristics` | 1 | 2 | `high` | none |
| `user-centered-design` | 1 | 2 | `high` | none |
| `user-experience-research-methods` | 1 | 2 | `high` | none |
| `variation-and-selection` | 1 | 2 | `high` | none |
| `varied-practice-interleaving` | 1 | 2 | `high` | none |
| `wysiati` | 1 | 2 | `high` | none |
| `zone-of-development` | 1 | 2 | `high` | none |

## Cross-Model Deterministic Observations

### Identical Extraction-Type Distributions

- abstraction, adaptation, agile-methodologies, algorithmic-thinking, association, auditability-traceability, authenticity, bayesian, bias-blind-spot, blooms-taxonomy, bottlenecks, boundaries, brainstorming, branch-solve-merge, butterfly-effect, causal-attribution-resistance, circle-of-competence, cognitive-biases, cognitive-dissonance, cognitive-gaps-assessment, cognitive-load-theory, combinatorial-effects, comparative-political-systems-analysis, complexity-bias-resistance, compounding, consulting-firms-methodology, counterfactual-reasoning, creative-destruction, critical-mass, cultural-dimensions-theory, cultural-intelligence, curiosity, cybersecurity-thinking-models, data-science-reasoning-framework, debugging-strategies, deliberate-practice, desirable-difficulties, dialectical-reasoning, divergent-vs-convergent-thinking, dunning-kruger-effect, einstellung-effect, endowment-effect, expertise-reversal-effect, extreme-performance-evaluation, false-precision-avoidance, feynman-technique, generation-effect, gestalt-principles-of-perception, goal-setting, habit-formation, hanlons-razor, hindsight-bias, iteration, lateral-thinking, lean-startup-methodology, learning-curve, liking-principle, logical-fallacies, monte-carlo-methods, multicultural-team-dynamics, non-linear-dynamics, persistence-grit, peter-principle, power-laws, pre-suasion, prospect-theory, rationalization, reciprocity-principle, reframing-perspective, regression-to-the-mean, regret-theory, regulatory-horizon-scanning, representativeness-heuristic, risk-vs-uncertainty, scale-economies, schema-acquisition, self-control, self-determination-theory, self-organization-and-emergent-order, signaling, simplification, specialization, statistical-learning-theory, statistics-concepts, supply-and-demand, synthesis-and-integration, system-1, system-2, theory-induced-blindness, tier-2-high-value, time-tested-validation, tipping-points, tradition-vs-innovation-balance, understanding-motivations, usability-heuristics, user-experience-research-methods, variation-and-selection, varied-practice-interleaving, wysiati, zone-of-development: `{'explicit': 4, 'not_supported_by_source': 2}`
- analogies-and-metaphors, checklists, delays, formal-reasoning, jobs-to-be-done, natural-selection-analogy, obligations-controls-mapping, optimism-bias-and-planning-fallacy, peer-review-your-perspectives, prisoners-dilemma, status-quo-bias, user-centered-design: `{'explicit': 6, 'not_supported_by_source': 2}`
- curse-of-knowledge, emotional-intelligence, feedback-loops, redundancy, storytelling-frameworks, switching-costs: `{'explicit': 8, 'not_supported_by_source': 2}`
- confirmation-bias, constraints, intellectual-humility, scientific-method-evidence-testing, step-back: `{'explicit': 8, 'not_supported_by_source': 3}`
- growth-mindset, narratives, scaffolding, scaffolding-educational: `{'explicit': 4, 'not_supported_by_source': 2, 'review_note': 3}`
- chaos-theory, elasticity, input-vs-output-goals, internal-locus-of-control: `{'explicit': 4, 'not_supported_by_source': 3}`
- cross-cultural-communication-frameworks, nash-equilibrium, non-violent-communication, red-queen-effect: `{'explicit': 5, 'not_supported_by_source': 2}`
- commitment-bias, metacognitive-questioning, path-dependence: `{'explicit': 10, 'not_supported_by_source': 2}`
- calculated-risk-taking, occams-razor: `{'explicit': 14, 'not_supported_by_source': 4}`
- incentives, trade-offs: `{'explicit': 16, 'not_supported_by_source': 2, 'review_note': 3}`
- moral-hazard, psychological-safety: `{'explicit': 16, 'not_supported_by_source': 4, 'review_note': 1}`
- resilience, social-proof: `{'explicit': 19, 'not_supported_by_source': 3, 'review_note': 2}`
- emergence, flow: `{'explicit': 19, 'not_supported_by_source': 4}`
- confidence-calibration, premortem: `{'explicit': 20, 'not_supported_by_source': 2}`
- lindy-effect, network-effects: `{'explicit': 20, 'not_supported_by_source': 3}`
- decomposition, empathy: `{'explicit': 29, 'not_supported_by_source': 4}`
- baseline-establishment, category-decisions: `{'explicit': 4, 'not_supported_by_source': 4}`
- conjunction-fallacy, information-theory: `{'explicit': 4, 'not_supported_by_source': 6}`
- feedback-models-sbi, persuasion-principles: `{'explicit': 6, 'not_supported_by_source': 5}`
- latticework-of-mental-models, perceptual-learning: `{'explicit': 7, 'not_supported_by_source': 2}`
- opportunity-cost, true-uncertainty-navigation: `{'explicit': 7, 'not_supported_by_source': 2, 'review_note': 2}`
- falsifiability, five-whys-method: `{'explicit': 7, 'not_supported_by_source': 3, 'review_note': 1}`
- lock-in, mental-simulation: `{'explicit': 9, 'not_supported_by_source': 2}`

### Repeated Diagnostic Question Openings

- `is the worst case bad` appears in `13` affordance(s): `aleatory-epistemic-uncertainty-recognition.commitment-gating-by-reducibility`, `anchoring.provisional-anchor-with-correction`, `calculated-risk-taking.pressure-tested-bounded-wager`, `expected-value.probability-weighted-payoff-boundary`, `leverage-points.resistance-bias-execution-hardening`, `monte-carlo-methods.distributional-range-stress-test`, `multi-criteria-decision-analysis.auditable-weighted-tradeoff-matrix`, `optionality.preserve-reversible-learning`, `premortem.simulated-failure-to-plan-change`, `probabilistic-thinking.range-and-sensitivity-decision-gate`, `risk-assessment.thresholded-downside-governance`, `statistical-discipline.distributional-inference-stress-test`, `survivorship-bias.restore-failure-tail-outcomes`
- `what would you have to` appears in `6` affordance(s): `anchoring.provisional-anchor-with-correction`, `decomposition.test-cuts-and-assumptions`, `expected-value.probability-weighted-payoff-boundary`, `premortem.simulated-failure-to-plan-change`, `problem-framing-and-reframing.falsify-frame-assumptions`, `trade-offs.allocation-backed-sacrifice`
- `what would we have to` appears in `5` affordance(s): `aleatory-epistemic-uncertainty-recognition.commitment-gating-by-reducibility`, `calculated-risk-taking.pressure-tested-bounded-wager`, `network-effects.critical-mass-feedback-proof`, `resilience.disciplined-recovery-with-continued-function`, `statistical-discipline.distributional-inference-stress-test`
- `what is the oneday answer` appears in `4` affordance(s): `chain-of-thought.audit-stepwise-reasoning`, `optimization-theory.leverage-bounded-analysis`, `second-order-thinking.downstream-reversal-stress-test`, `step-back.reorientation-before-execution-gate`
- `what assumptions are embedded in` appears in `3` affordance(s): `decomposition.test-cuts-and-assumptions`, `occams-razor.lowest-assumption-evidence-pruning`, `pareto-principle.measured-vital-few-allocation`
- `what would have to be` appears in `3` affordance(s): `complex-adaptive-systems.assumption-and-bias-exposure`, `leverage-points.resistance-bias-execution-hardening`, `true-uncertainty-navigation.scenario-bound-robust-action`
- `what would need to be` appears in `3` affordance(s): `antifragility.bounded-stress-learning-design`, `first-principles-thinking.elemental-truth-rebuild-gate`, `problem-framing-and-reframing.falsify-frame-assumptions`
- `what evidence shows this is` appears in `2` affordance(s): `bottlenecks.binding-constraint-throughput-check`, `supply-and-demand.model-market-pressure-first`
- `what is the proximate cause` appears in `2` affordance(s): `correlation-vs-causation.trace-root-cause-machine`, `root-cause-analysis.machine-level-recurrence-diagnosis`
- `what is the single core` appears in `2` affordance(s): `decomposition.mece-key-driver-action-map`, `problem-framing-and-reframing.define-before-analysis`
- `what other disciplines or frameworks` appears in `2` affordance(s): `anchoring.provisional-anchor-with-correction`, `problem-framing-and-reframing.test-alternative-frames`
- `what support is temporary and` appears in `2` affordance(s): `scaffolding-educational.stage-support-toward-autonomy`, `scaffolding.temporary-support-with-fade-plan`

### Affordances With Short Source Quotes

Median affordance-level source quote length: `108` characters.

- `premortem.simulated-failure-to-plan-change`: shortest quote `14` chars across `17` quote(s)
- `consulting-firms-methodology.structure-uncertainty-into-testable-questions`: shortest quote `15` chars across `3` quote(s)
- `step-back.reorientation-before-execution-gate`: shortest quote `15` chars across `6` quote(s)
- `category-decisions.precommit-boundaries-before-repeat-choice`: shortest quote `16` chars across `3` quote(s)
- `intellectual-humility.corrigible-confidence-review`: shortest quote `16` chars across `6` quote(s)
- `price-discrimination.segment-offer-by-value-evidence`: shortest quote `17` chars across `5` quote(s)
- `system-1.treat-intuition-as-first-pass-signal`: shortest quote `17` chars across `3` quote(s)
- `chain-of-thought.audit-stepwise-reasoning`: shortest quote `18` chars across `7` quote(s)
- `switching-costs.reversibility-decay-exit-plan`: shortest quote `19` chars across `3` quote(s)
- `five-whys-method.evidence-bound-causal-chain-drilldown`: shortest quote `20` chars across `5` quote(s)
- `blooms-taxonomy.mastery-level-diagnosis-before-tasking`: shortest quote `21` chars across `3` quote(s)
- `social-proof.contain-consensus-contagion`: shortest quote `21` chars across `6` quote(s)
- `wysiati.missing-evidence-denominator-audit`: shortest quote `21` chars across `3` quote(s)
- `active-listening.hidden-disagreement-diagnostic-loop`: shortest quote `23` chars across `8` quote(s)
- `feedback-models-sbi.situation-impact-invitation-structure`: shortest quote `23` chars across `4` quote(s)
- `information-theory.signal-preserving-compression`: shortest quote `23` chars across `3` quote(s)
- `perceptual-learning.train-cue-discrimination`: shortest quote `23` chars across `6` quote(s)
- `critical-thinking.claim-evidence-assumption-check`: shortest quote `25` chars across `10` quote(s)
- `persistence-grit.sustained-effort-with-stop-rules`: shortest quote `25` chars across `3` quote(s)
- `lindy-effect.longevity-prior-with-baseline-break-check`: shortest quote `26` chars across `16` quote(s)
- `persuasion-principles.substance-preserving-adoption-design`: shortest quote `26` chars across `5` quote(s)
- `checklists.omission-risk-execution-gate`: shortest quote `27` chars across `4` quote(s)
- `constructive-feedback-models.specific-standard-correction`: shortest quote `27` chars across `7` quote(s)
- `scientific-method-evidence-testing.falsifiable-hypothesis-threshold-test`: shortest quote `27` chars across `6` quote(s)
- `desirable-difficulties.calibrated-struggle-for-transfer`: shortest quote `28` chars across `3` quote(s)
- `storytelling-frameworks.structure-behavior-change-message`: shortest quote `28` chars across `7` quote(s)
- `aleatory-epistemic-uncertainty-recognition.commitment-gating-by-reducibility`: shortest quote `29` chars across `8` quote(s)
- `anchoring.provisional-anchor-with-correction`: shortest quote `29` chars across `15` quote(s)
- `authority-bias.domain-bound-deference-audit`: shortest quote `29` chars across `6` quote(s)
- `batna.credible-walk-away-alternative-test`: shortest quote `29` chars across `7` quote(s)
- `cognitive-biases.debiasing-process-before-confident-judgment`: shortest quote `29` chars across `3` quote(s)
- `dialectical-reasoning.bounded-antithesis-synthesis-test`: shortest quote `29` chars across `3` quote(s)
- `hindsight-bias.predecision-record-for-learning-review`: shortest quote `29` chars across `3` quote(s)
- `optionality.preserve-reversible-learning`: shortest quote `29` chars across `10` quote(s)
- `representativeness-heuristic.similarity-vs-base-rate-check`: shortest quote `29` chars across `3` quote(s)
- `devops-and-continuous-integration.build-observe-adjust-loop`: shortest quote `30` chars across `4` quote(s)
- `meta-cognitive-reflection.check-thinking-before-more-motion`: shortest quote `30` chars across `3` quote(s)
- `optimization-theory.leverage-bounded-analysis`: shortest quote `30` chars across `11` quote(s)
- `second-order-thinking.downstream-reversal-stress-test`: shortest quote `30` chars across `13` quote(s)
- `calculated-risk-taking.pressure-tested-bounded-wager`: shortest quote `31` chars across `10` quote(s)
- `jobs-to-be-done.real-progress-job-discovery`: shortest quote `31` chars across `4` quote(s)
- `markov-chains.state-transition-boundary-check`: shortest quote `31` chars across `6` quote(s)
- `problem-framing-and-reframing.falsify-frame-assumptions`: shortest quote `31` chars across `8` quote(s)
- `theory-of-constraints.constraint-shift-cadence`: shortest quote `31` chars across `8` quote(s)
- `trade-offs.allocation-backed-sacrifice`: shortest quote `31` chars across `11` quote(s)
- `understanding-motivations.hidden-driver-hypothesis-test`: shortest quote `31` chars across `3` quote(s)
- `boundaries.scope-ownership-decision-rights-filter`: shortest quote `32` chars across `3` quote(s)
- `causal-attribution-resistance.separate-blame-from-cause`: shortest quote `32` chars across `3` quote(s)
- `elasticity.adapt-skill-deployment-with-invariants`: shortest quote `32` chars across `3` quote(s)
- `power-dynamics.weakest-link-constraint-map`: shortest quote `32` chars across `4` quote(s)
- `pre-suasion.set-context-with-merit-and-consent-check`: shortest quote `32` chars across `3` quote(s)
- `constraints.scope-boundary-decision-filter`: shortest quote `33` chars across `6` quote(s)
- `habit-formation.automatic-action-design-check`: shortest quote `33` chars across `3` quote(s)
- `complex-adaptive-systems.ordered-adaptive-learning-loop`: shortest quote `34` chars across `5` quote(s)
- `first-principles-thinking.elemental-truth-rebuild-gate`: shortest quote `34` chars across `5` quote(s)
- `power-dynamics.commitment-gradient-inversion`: shortest quote `34` chars across `9` quote(s)
- `statistical-learning-theory.prediction-fit-generalization-check`: shortest quote `34` chars across `3` quote(s)
- `auditability-traceability.reconstructable-decision-trail`: shortest quote `35` chars across `3` quote(s)
- `emotional-intelligence.self-regulation-under-emotional-activation`: shortest quote `35` chars across `3` quote(s)
- `international-negotiation-and-diplomacy-models.substance-signaling-settlement-map`: shortest quote `35` chars across `3` quote(s)
- `natural-selection-analogy.variation-selection-retention-loop`: shortest quote `35` chars across `4` quote(s)
- `pareto-principle.measured-vital-few-allocation`: shortest quote `35` chars across `14` quote(s)
- `curse-of-knowledge.audience-starting-state-reconstruction`: shortest quote `36` chars across `7` quote(s)
- `emotional-intelligence.emotion-evidence-landing-check`: shortest quote `36` chars across `3` quote(s)
- `iteration.bounded-learning-cycle-gate`: shortest quote `36` chars across `3` quote(s)
- `optimism-bias-and-planning-fallacy.outside-view-premortem-forecast`: shortest quote `36` chars across `4` quote(s)
- `dunning-kruger-effect.objective-calibration-before-trust`: shortest quote `37` chars across `3` quote(s)
- `feedback-loops.closed-loop-action-signal`: shortest quote `37` chars across `3` quote(s)
- `root-cause-analysis.machine-level-recurrence-diagnosis`: shortest quote `37` chars across `5` quote(s)
- `usability-heuristics.lower-friction-with-checked-shortcuts`: shortest quote `38` chars across `3` quote(s)
- `bayesian.explicit-prior-evidence-update`: shortest quote `39` chars across `3` quote(s)
- `flow.calibrated-immersion-channel`: shortest quote `39` chars across `15` quote(s)
- `leverage-points.hypothesis-bounded-analysis`: shortest quote `39` chars across `7` quote(s)
- `optimization-theory.objective-constraint-tradeoff-fit`: shortest quote `39` chars across `11` quote(s)
- `leverage-points.value-driver-sensitivity-tree`: shortest quote `40` chars across `4` quote(s)
- `lock-in.reversal-cost-dependency-audit`: shortest quote `40` chars across `3` quote(s)
- `monte-carlo-methods.distributional-range-stress-test`: shortest quote `40` chars across `3` quote(s)
- `narratives.make-causal-meaning-actionable`: shortest quote `40` chars across `3` quote(s)
- `peter-principle.validate-next-role-fit`: shortest quote `40` chars across `3` quote(s)
- `scaffolding-educational.stage-support-toward-autonomy`: shortest quote `40` chars across `3` quote(s)
- `information-asymmetry.extract-tacit-knowledge-for-recipient`: shortest quote `41` chars across `15` quote(s)
- `psychological-safety.surface-withheld-risk-signals`: shortest quote `41` chars across `6` quote(s)
- `risk-assessment.thresholded-downside-governance`: shortest quote `41` chars across `13` quote(s)
- `scaffolding.temporary-support-with-fade-plan`: shortest quote `41` chars across `3` quote(s)
- `delays.lagged-feedback-timing-gate`: shortest quote `42` chars across `4` quote(s)
- `signaling.costly-proof-of-intent-test`: shortest quote `42` chars across `3` quote(s)
- `status-quo-bias.incumbent-option-inertia-test`: shortest quote `42` chars across `4` quote(s)
- `chain-of-verification.make-or-break-premise-audit`: shortest quote `43` chars across `5` quote(s)
- `comparative-political-systems-analysis.compare-institutions-by-function`: shortest quote `43` chars across `3` quote(s)
- `cultural-dimensions-theory.coordinate-across-default-norms`: shortest quote `43` chars across `3` quote(s)
- `data-science-reasoning-framework.question-measure-model-handoff`: shortest quote `43` chars across `3` quote(s)
- `formal-reasoning.explicit-premise-chain-test`: shortest quote `43` chars across `4` quote(s)
- `input-vs-output-goals.controllable-input-output-alignment`: shortest quote `43` chars across `3` quote(s)
- `mental-simulation.skill-rehearsal-response-prep`: shortest quote `43` chars across `5` quote(s)
- `metacognitive-questioning.process-inspection-next-question-gate`: shortest quote `43` chars across `6` quote(s)
- `power-dynamics.outside-option-credibility`: shortest quote `43` chars across `12` quote(s)
- `statistics-concepts.sample-structure-before-inference`: shortest quote `43` chars across `3` quote(s)
- `extreme-performance-evaluation.stress-test-against-high-variance-standards`: shortest quote `44` chars across `3` quote(s)
- `reasoning-mode-router.context-driven-mode-selection-check`: shortest quote `44` chars across `4` quote(s)
- `correlation-vs-causation.test-causal-claim-before-intervention`: shortest quote `45` chars across `9` quote(s)
- `lateral-thinking.frame-escape-before-obvious-path`: shortest quote `45` chars across `3` quote(s)
- `authenticity.congruence-candor-substance-check`: shortest quote `46` chars across `3` quote(s)
- `black-swan-events.post-shock-aberration-learning-discipline`: shortest quote `46` chars across `9` quote(s)
- `compounding.durable-base-before-growth-curve`: shortest quote `46` chars across `3` quote(s)
- `deliberate-practice.specific-reps-feedback-and-error-correction`: shortest quote `46` chars across `3` quote(s)
- `expected-value.probability-weighted-payoff-boundary`: shortest quote `46` chars across `16` quote(s)
- `latticework-of-mental-models.cross-check-causal-layers`: shortest quote `46` chars across `6` quote(s)
- `logical-fallacies.test-persuasive-argument-validity`: shortest quote `46` chars across `3` quote(s)
- `non-linear-dynamics.feedback-threshold-local-optimization-check`: shortest quote `46` chars across `3` quote(s)
- `red-queen-effect.relative-position-adaptation-test`: shortest quote `46` chars across `3` quote(s)
- `self-determination-theory.motivation-architecture-diagnosis`: shortest quote `46` chars across `3` quote(s)
- `theory-induced-blindness.favored-framework-blindness-check`: shortest quote `46` chars across `3` quote(s)
- `butterfly-effect.cascade-path-trace`: shortest quote `47` chars across `3` quote(s)
- `cultural-intelligence.translate-human-worlds-before-adoption`: shortest quote `47` chars across `3` quote(s)
- `specialization.focus-depth-with-boundary-checks`: shortest quote `47` chars across `3` quote(s)
- `system-2.engage-deliberation-when-asymmetry-demands-it`: shortest quote `47` chars across `3` quote(s)
- `tradition-vs-innovation-balance.separate-standards-from-experiments`: shortest quote `47` chars across `3` quote(s)
- `power-laws.dominant-driver-tail-check`: shortest quote `48` chars across `3` quote(s)
- `zone-of-development.calibrate-next-reachable-stretch`: shortest quote `48` chars across `3` quote(s)
- `cognitive-dissonance.commitment-evidence-revision-check`: shortest quote `49` chars across `3` quote(s)
- `complexity-bias-resistance.compress-with-causal-spine`: shortest quote `49` chars across `3` quote(s)
- `critical-mass.viability-threshold-density-test`: shortest quote `49` chars across `3` quote(s)
- `gestalt-principles-of-perception.reveal-right-whole-before-detail`: shortest quote `49` chars across `3` quote(s)
- `optionality.expand-before-evaluating`: shortest quote `49` chars across `8` quote(s)
- `path-dependence.installed-dependency-unwind-map`: shortest quote `49` chars across `4` quote(s)
- `redundancy.cognitive-reinforcement-for-retention`: shortest quote `49` chars across `4` quote(s)
- `regret-theory.long-run-regret-with-risk-check`: shortest quote `49` chars across `3` quote(s)
- `simplification.distill-core-with-boundaries`: shortest quote `49` chars across `3` quote(s)
- `cognitive-load-theory.reduce-extraneous-load-without-erasing-discrimination`: shortest quote `50` chars across `3` quote(s)
- `curiosity.decision-bound-inquiry-loop`: shortest quote `50` chars across `3` quote(s)
- `risk-vs-uncertainty.commitment-sizing-under-unknowns`: shortest quote `50` chars across `3` quote(s)
- `variation-and-selection.variation-with-selection-rule`: shortest quote `50` chars across `3` quote(s)
- `circle-of-competence.calibrate-judgment-boundary`: shortest quote `51` chars across `3` quote(s)
- `growth-mindset.feedback-loop-for-expandable-capability`: shortest quote `51` chars across `3` quote(s)
- `time-tested-validation.reuse-proven-method-with-fit-check`: shortest quote `51` chars across `3` quote(s)
- `varied-practice-interleaving.contrast-frames-before-commitment`: shortest quote `51` chars across `3` quote(s)
- `analogies-and-metaphors.structural-fit-transfer-test`: shortest quote `52` chars across `4` quote(s)
- `baseline-establishment.starting-condition-comparison-gate`: shortest quote `52` chars across `3` quote(s)
- `commitment-bias.recommitment-stop-rule-review`: shortest quote `52` chars across `4` quote(s)
- `endowment-effect.reprice-owned-option-from-outside-view`: shortest quote `52` chars across `3` quote(s)
- `path-dependence.old-behavior-reproduction-map`: shortest quote `52` chars across `4` quote(s)
- `problem-framing-and-reframing.define-before-analysis`: shortest quote `52` chars across `10` quote(s)
- `user-centered-design.prototype-user-evidence-loop`: shortest quote `52` chars across `4` quote(s)
- `base-rates.outside-view-reference-class-anchor`: shortest quote `53` chars across `16` quote(s)
- `combinatorial-effects.make-or-break-interaction-map`: shortest quote `53` chars across `3` quote(s)
- `rationalization.rationale-vs-real-driver-test`: shortest quote `53` chars across `3` quote(s)
- `redundancy.single-point-failure-backup-test`: shortest quote `53` chars across `3` quote(s)
- `scale-economies.validate-reusable-capability-before-volume`: shortest quote `53` chars across `3` quote(s)
- `confirmation-bias.disconfirming-evidence-equality-check`: shortest quote `54` chars across `6` quote(s)
- `internal-locus-of-control.controllable-lever-ownership-map`: shortest quote `54` chars across `3` quote(s)
- `metacognitive-questioning.expert-process-elicitation`: shortest quote `54` chars across `3` quote(s)
- `multi-criteria-decision-analysis.auditable-weighted-tradeoff-matrix`: shortest quote `54` chars across `12` quote(s)
- `sunk-cost-fallacy.future-value-recommitment`: shortest quote `54` chars across `18` quote(s)
- `agile-methodologies.feedback-loop-delivery-control`: shortest quote `55` chars across `3` quote(s)
- `black-swan-events.tail-exposure-preparation-under-deep-uncertainty`: shortest quote `55` chars across `10` quote(s)
- `bottlenecks.binding-constraint-throughput-check`: shortest quote `55` chars across `3` quote(s)
- `inversion.disconfirmation-before-defense`: shortest quote `55` chars across `7` quote(s)
- `obligations-controls-mapping.obligation-to-control-trace`: shortest quote `55` chars across `4` quote(s)
- `peer-review-your-perspectives.independent-dissent-review`: shortest quote `55` chars across `4` quote(s)
- `problem-framing-and-reframing.test-alternative-frames`: shortest quote `55` chars across `9` quote(s)
- `regression-to-the-mean.baseline-before-causal-story`: shortest quote `55` chars across `3` quote(s)
- `schema-acquisition.build-usable-patterns-with-reality-checks`: shortest quote `55` chars across `3` quote(s)
- `survivorship-bias.restore-failure-tail-outcomes`: shortest quote `55` chars across `10` quote(s)
- `game-theory-payoffs.counterparty-response-payoff-map`: shortest quote `56` chars across `3` quote(s)
- `lock-in.productive-standardization-commitment`: shortest quote `56` chars across `4` quote(s)
- `correlation-vs-causation.trace-root-cause-machine`: shortest quote `57` chars across `9` quote(s)
- `empathy.confirm-reflection-before-treatment`: shortest quote `57` chars across `8` quote(s)
- `reframing-perspective.decision-variable-reframe-test`: shortest quote `57` chars across `3` quote(s)
- `synthesis-and-integration.governing-thought-integration-check`: shortest quote `57` chars across `3` quote(s)
- `chaos-theory.resilience-over-precision-bet-sizing`: shortest quote `58` chars across `3` quote(s)
- `evolutionary-pressure.identify-selection-environment`: shortest quote `58` chars across `3` quote(s)
- `expertise-reversal-effect.match-support-to-expertise-level`: shortest quote `58` chars across `3` quote(s)
- `network-effects.pre-threshold-adoption-path`: shortest quote `59` chars across `8` quote(s)
- `brainstorming.bounded-divergence-before-selection`: shortest quote `60` chars across `3` quote(s)
- `self-control.system-design-for-follow-through`: shortest quote `60` chars across `3` quote(s)
- `commitment-bias.constructive-commitment-architecture`: shortest quote `61` chars across `4` quote(s)
- `feynman-technique.plain-language-gap-test`: shortest quote `61` chars across `3` quote(s)
- `inversion.survivor-absence-signal`: shortest quote `61` chars across `4` quote(s)
- `self-organization-and-emergent-order.shape-conditions-for-local-adaptation`: shortest quote `61` chars across `3` quote(s)
- `abstraction.evidence-anchored-compression-check`: shortest quote `62` chars across `3` quote(s)
- `liking-principle.build-receptivity-with-substance-check`: shortest quote `62` chars across `3` quote(s)
- `multicultural-team-dynamics.turn-difference-into-decision-quality`: shortest quote `63` chars across `3` quote(s)
- `prioritization.capacity-constrained-exclusion-and-sequencing`: shortest quote `63` chars across `15` quote(s)
- `six-thinking-hats.separate-modes-before-synthesis`: shortest quote `63` chars across `10` quote(s)
- `prisoners-dilemma.defection-incentive-reframe-test`: shortest quote `64` chars across `4` quote(s)
- `resilience.disciplined-recovery-with-continued-function`: shortest quote `64` chars across `15` quote(s)
- `generation-effect.active-articulation-before-belief`: shortest quote `65` chars across `3` quote(s)
- `prospect-theory.loss-frame-decision-quality-check`: shortest quote `65` chars across `3` quote(s)
- `psychological-safety.convert-candor-into-correction`: shortest quote `65` chars across `6` quote(s)
- `supply-and-demand.model-market-pressure-first`: shortest quote `65` chars across `3` quote(s)
- `circle-of-control.control-influence-action-map`: shortest quote `66` chars across `13` quote(s)
- `decomposition.test-cuts-and-assumptions`: shortest quote `66` chars across `11` quote(s)
- `emergence.design-conditions-feedback-not-script`: shortest quote `66` chars across `9` quote(s)
- `systems-thinking.structure-over-events`: shortest quote `66` chars across `6` quote(s)
- `incentives.reward-structure-before-behavior-judgment`: shortest quote `67` chars across `5` quote(s)
- `inversion.zero-base-continuation-test`: shortest quote `67` chars across `5` quote(s)
- `law-of-large-numbers.repeated-sample-stability-before-inference`: shortest quote `67` chars across `9` quote(s)
- `user-experience-research-methods.test-user-assumptions-before-commitment`: shortest quote `67` chars across `3` quote(s)
- `confidence-calibration.instrument-trust-before-precision`: shortest quote `68` chars across `6` quote(s)
- `decomposition.mece-key-driver-action-map`: shortest quote `68` chars across `13` quote(s)
- `empathy.ground-reframing-in-stakeholder-evidence`: shortest quote `68` chars across `8` quote(s)
- `johari-window.specific-feedback-disclosure-loop`: shortest quote `68` chars across `17` quote(s)
- `debugging-strategies.failure-condition-root-cause-trace`: shortest quote `70` chars across `3` quote(s)
- `lean-startup-methodology.validated-learning-kill-pivot-gate`: shortest quote `70` chars across `3` quote(s)
- `mental-models-of-reality.compare-frame-to-territory`: shortest quote `70` chars across `3` quote(s)
- `systems-thinking.feedback-loop-mapping`: shortest quote `70` chars across `7` quote(s)
- `tier-2-high-value.prune-to-leverage-drivers`: shortest quote `70` chars across `3` quote(s)
- `adaptation.feedback-triggered-course-correction`: shortest quote `72` chars across `3` quote(s)
- `tipping-points.threshold-prerequisite-test`: shortest quote `72` chars across `3` quote(s)
- `adverse-selection.verify-hidden-type-selection`: shortest quote `73` chars across `7` quote(s)
- `antifragility.bounded-stress-learning-design`: shortest quote `73` chars across `18` quote(s)
- `confidence-calibration.method-first-self-interrogation`: shortest quote `73` chars across `6` quote(s)
- `counterfactual-reasoning.plausible-alternative-branch-test`: shortest quote `73` chars across `3` quote(s)
- `nash-equilibrium.stable-best-response-map`: shortest quote `73` chars across `3` quote(s)
- `statistical-discipline.hypothesis-first-tool-fit`: shortest quote `73` chars across `8` quote(s)
- `aleatory-epistemic-uncertainty-recognition.type-specific-tool-routing`: shortest quote `74` chars across `6` quote(s)
- `inversion.anti-goal-failure-mechanism-map`: shortest quote `74` chars across `8` quote(s)
- `mental-simulation.assumption-bound-scenario-rehearsal`: shortest quote `75` chars across `3` quote(s)
- `switching-costs.adoption-friction-incumbent-loyalty-map`: shortest quote `75` chars across `4` quote(s)
- `complex-adaptive-systems.assumption-and-bias-exposure`: shortest quote `78` chars across `7` quote(s)
- `network-effects.critical-mass-feedback-proof`: shortest quote `78` chars across `7` quote(s)
- `reciprocity-principle.costly-value-trust-test`: shortest quote `78` chars across `3` quote(s)
- `social-proof.verify-context-matched-proof`: shortest quote `78` chars across `8` quote(s)
- `non-violent-communication.needs-observations-request-clarifier`: shortest quote `79` chars across `3` quote(s)
- `branch-solve-merge.branch-evidence-merge-rule`: shortest quote `80` chars across `3` quote(s)
- `conjunction-fallacy.sequence-probability-stress-test`: shortest quote `80` chars across `3` quote(s)
- `creative-destruction.disciplined-replacement-before-novelty`: shortest quote `81` chars across `3` quote(s)
- `falsifiability.disconfirming-reversal-gate`: shortest quote `81` chars across `5` quote(s)
- `goal-setting.outcome-checkpoint-alignment-gate`: shortest quote `81` chars across `3` quote(s)
- `empathy.substitute-perspective-taking-under-strategic-risk`: shortest quote `82` chars across `8` quote(s)
- `hanlons-razor.non-malice-diagnostic-delay`: shortest quote `82` chars across `3` quote(s)
- `statistical-discipline.distributional-inference-stress-test`: shortest quote `82` chars across `10` quote(s)
- `inversion.obstacle-removal-before-added-force`: shortest quote `86` chars across `6` quote(s)
- `principal-agent-problem.delegated-alignment-drift-audit`: shortest quote `86` chars across `6` quote(s)
- `cross-cultural-communication-frameworks.frame-translation-action-check`: shortest quote `87` chars across `3` quote(s)
- `bias-blind-spot.self-bias-accountability-check`: shortest quote `88` chars across `3` quote(s)
- `association.structural-association-test`: shortest quote `90` chars across `3` quote(s)
- `divergent-vs-convergent-thinking.mode-separated-option-cycle`: shortest quote `90` chars across `3` quote(s)
- `probabilistic-thinking.range-and-sensitivity-decision-gate`: shortest quote `90` chars across `5` quote(s)
- `decision-trees.branch-trigger-map`: shortest quote `92` chars across `9` quote(s)
- `survivorship-bias.recover-hidden-denominator-selection`: shortest quote `92` chars across `11` quote(s)
- `experimentation.hypothesis-bound-decision-test`: shortest quote `93` chars across `12` quote(s)
- `occams-razor.lowest-assumption-evidence-pruning`: shortest quote `93` chars across `10` quote(s)
- `feedback-loops.loop-polarity-intervention-map`: shortest quote `94` chars across `4` quote(s)
- `systems-thinking.metric-leverage-design`: shortest quote `95` chars across `4` quote(s)
- `moral-hazard.proxy-hidden-effort-with-noisy-outcomes`: shortest quote `99` chars across `5` quote(s)
- `learning-curve.measure-capability-compounding-over-time`: shortest quote `100` chars across `3` quote(s)
- `algorithmic-thinking.repeatable-handoff-procedure-gate`: shortest quote `102` chars across `3` quote(s)
- `regulatory-horizon-scanning.weak-signal-response-trigger`: shortest quote `103` chars across `3` quote(s)
- `opportunity-cost.displaced-alternative-commitment-gate`: shortest quote `104` chars across `5` quote(s)
- `information-asymmetry.redesign-party-controlled-evidence`: shortest quote `106` chars across `18` quote(s)

### Review Notes With Empty Dropped Material

- None.

## What This Report Deliberately Omits

- No completeness ratios.
- No coverage-style scoring.
- No quality grade.
- No automated drop or rewrite recommendations.
- No semantic genericity scoring beyond PR 1 validation.
