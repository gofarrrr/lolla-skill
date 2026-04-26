# Stability report — third-year-phd-student-lane2-off

Generated: 2026-04-26T11:00:25Z
Runs: 3
Run IDs: 20260426T110025Zstab0, 20260426T110204Zstab1, 20260426T110344Zstab2
Prompt versions consistent across runs: True

## Per-stage stability (Jaccard)

> 1.0 is a WARNING, not a target — signals a specialist that stopped doing semantic judgment. Acceptance is a threshold band: stability moved up from baseline, no neighboring stage regressed, qualitative review confirms cards still do structural work.

| Stage | Mean | Min | Max |
|---|---|---|---|
| Pass 1 (tendencies) | 1.00 | 1.00 | 1.00 |
| Lane 2 — fingerprint moves | 0.00 | 0.00 | 0.00 |
| Lane 2 — recalled candidates | 0.75 | 0.67 | 0.85 |
| Lane 2 — accepted (pre-cap) | 0.39 | 0.25 | 0.62 |
| Lane 2 — detected (post-cap) | 0.30 | 0.14 | 0.43 |
| Lane 2 — capped (top-5 drops) | 0.00 | 0.00 | 0.00 |
| Lane 2 (cheat-sheet anchors) | 0.30 | 0.14 | 0.43 |
| Lane 3 (reframings) | 0.11 | 0.00 | 0.33 |
| Lane 4 (gap dims) | 0.87 | 0.80 | 1.00 |

Embedding mode per run: ['off', 'off', 'off']  ·  consistent: True

### Recall-source distribution per run

| Run | keyword | embedding | both | other |
|---|---|---|---|---|
| `20260426T110025Zstab0` | 60 | 0 | 0 | 0 |
| `20260426T110204Zstab1` | 60 | 0 | 0 | 0 |
| `20260426T110344Zstab2` | 60 | 0 | 0 | 0 |

## Step 6 anchor naming (per-run)

| Run | Named | Total | Rate |
|---|---|---|---|
| `20260426T110025Zstab0` | (no revised_answer) | — | — |
| `20260426T110204Zstab1` | (no revised_answer) | — | — |
| `20260426T110344Zstab2` | (no revised_answer) | — | — |

## Per-run item diff

### Pass 1 tendencies
- `20260426T110025Zstab0`: ['social-proof-tendency']
- `20260426T110204Zstab1`: ['social-proof-tendency']
- `20260426T110344Zstab2`: ['social-proof-tendency']

### Lane 2 fingerprint moves
- `20260426T110025Zstab0`: ['develop contingency planning with explicit timelines and fallback sequences.', 'evaluate options by mapping risk-reward profiles to career pipelines and competition levels.', "gather clarifying information to assess options by asking targeted questions on career goals, advisor's intent for novelty, and lab's competitive positioning.", 'identify structural constraints like lab capabilities and advisor timeline to rule out high-risk paths.', 'pinpoint critical bottlenecks and propose sequenced actions to test feasibility.', 'prioritize action sequence to de-risk political and commitment issues.', 'reassess option viability based on refined user description, shifting from high-risk moonshot to conservative methodological application.', 'reframe risky options into viable hybrids by incorporating collaborations to mitigate weaknesses.']
- `20260426T110204Zstab1`: ['balance ambition and regret by aligning smart strategy with high-upside choice', 'evaluate options by comparing risk profiles, pipelines, and competition levels', 'gather clarifying information on key uncertainties before recommending', 'identify and prioritize highest-leverage next actions with sequenced contingencies', 'pre-plan failure scenarios and define explicit go/no-go criteria', 'reframe option based on new specifics to update risk assessment', 'surface overlooked factors like time-to-paper, funding, learning curve, and politics']
- `20260426T110344Zstab2`: ['evaluate options by mapping risk-reward profiles to career pipelines and lab constraints.', "gather critical clarifying information before recommending by asking targeted questions on career goals, advisor's intent, and lab positioning.", 'identify dealbreaker constraints like lab inexperience and advisor retirement to rule out high-risk paths.', 'pinpoint actionable bottlenecks and validation steps like data access.', 'prioritize conversation order to de-risk politics and assumptions.', 'propose sequenced decision tree with fallbacks and checkpoints to manage uncertainty.', 'reframe option 3 from vague moonshot to concrete hybrid leveraging strengths upon user clarification.']

### Lane 2 recalled candidates
- `20260426T110025Zstab0`: ['active-listening', 'adverse-selection', 'aleatory-epistemic-uncertainty-recognition', 'algorithmic-thinking', 'anchoring', 'base-rates', 'bayesian', 'bias-blind-spot', 'blooms-taxonomy', 'boundaries', 'branch-solve-merge', 'calculated-risk-taking', 'cognitive-dissonance', 'commitment-bias', 'confidence-calibration', 'conjunction-fallacy', 'constraints', 'cultural-intelligence', 'decomposition', 'einstellung-effect', 'false-precision-avoidance', 'falsifiability', 'feedback-loops', 'game-theory-payoffs', 'information-asymmetry', 'intellectual-humility', 'inversion', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'mental-simulation', 'metacognitive-questioning', 'obligations-controls-mapping', 'opportunity-cost', 'optimism-bias-and-planning-fallacy', 'optimization-theory', 'optionality', 'path-dependence', 'power-dynamics', 'premortem', 'principal-agent-problem', 'probabilistic-thinking', 'problem-framing-and-reframing', 'prospect-theory', 'psychological-safety', 'reasoning-mode-router', 'regret-theory', 'representativeness-heuristic', 'risk-assessment', 'scientific-method-evidence-testing', 'second-order-thinking', 'signaling', 'social-proof', 'statistical-discipline', 'theory-of-constraints', 'time-tested-validation', 'true-uncertainty-navigation', 'user-centered-design', 'variation-and-selection', 'wysiati']
- `20260426T110204Zstab1`: ['aleatory-epistemic-uncertainty-recognition', 'anchoring', 'base-rates', 'bayesian', 'bias-blind-spot', 'black-swan-events', 'blooms-taxonomy', 'boundaries', 'branch-solve-merge', 'calculated-risk-taking', 'cognitive-dissonance', 'commitment-bias', 'comparative-advantage', 'confidence-calibration', 'conjunction-fallacy', 'constructive-feedback-models', 'counterfactual-reasoning', 'cultural-intelligence', 'decomposition', 'einstellung-effect', 'false-precision-avoidance', 'falsifiability', 'feedback-loops', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'inversion', 'jobs-to-be-done', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'margin-of-safety', 'mental-simulation', 'metacognitive-questioning', 'obligations-controls-mapping', 'occams-razor', 'opportunity-cost', 'optimism-bias-and-planning-fallacy', 'optimization-theory', 'optionality', 'power-dynamics', 'premortem', 'principal-agent-problem', 'probabilistic-thinking', 'problem-framing-and-reframing', 'reasoning-mode-router', 'regression-to-the-mean', 'representativeness-heuristic', 'risk-assessment', 'second-order-thinking', 'signaling', 'social-proof', 'statistical-discipline', 'survivorship-bias', 'systems-thinking', 'tier-2-high-value', 'time-tested-validation', 'true-uncertainty-navigation', 'variation-and-selection']
- `20260426T110344Zstab2`: ['active-listening', 'adverse-selection', 'aleatory-epistemic-uncertainty-recognition', 'anchoring', 'base-rates', 'bayesian', 'bias-blind-spot', 'black-swan-events', 'blooms-taxonomy', 'boundaries', 'branch-solve-merge', 'calculated-risk-taking', 'cognitive-dissonance', 'commitment-bias', 'confidence-calibration', 'conjunction-fallacy', 'constraints', 'constructive-feedback-models', 'counterfactual-reasoning', 'cultural-intelligence', 'curiosity', 'decomposition', 'einstellung-effect', 'false-precision-avoidance', 'falsifiability', 'feedback-loops', 'game-theory-payoffs', 'information-asymmetry', 'intellectual-humility', 'inversion', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'mental-simulation', 'metacognitive-questioning', 'monte-carlo-methods', 'obligations-controls-mapping', 'opportunity-cost', 'optimism-bias-and-planning-fallacy', 'optimization-theory', 'optionality', 'power-dynamics', 'premortem', 'principal-agent-problem', 'probabilistic-thinking', 'problem-framing-and-reframing', 'prospect-theory', 'psychological-safety', 'reasoning-mode-router', 'representativeness-heuristic', 'risk-assessment', 'second-order-thinking', 'signaling', 'social-proof', 'statistical-discipline', 'time-tested-validation', 'true-uncertainty-navigation', 'user-centered-design', 'variation-and-selection', 'wysiati']

### Lane 2 accepted (pre-cap)
- `20260426T110025Zstab0`: ['base-rates', 'constraints', 'optionality', 'premortem', 'problem-framing-and-reframing', 'regret-theory', 'theory-of-constraints']
- `20260426T110204Zstab1`: ['base-rates', 'optionality', 'survivorship-bias']
- `20260426T110344Zstab2`: ['base-rates', 'constraints', 'optionality', 'power-dynamics', 'premortem', 'problem-framing-and-reframing']

### Lane 2 detected (post-cap)
- `20260426T110025Zstab0`: ['base-rates', 'constraints', 'premortem', 'regret-theory', 'theory-of-constraints']
- `20260426T110204Zstab1`: ['base-rates', 'optionality', 'survivorship-bias']
- `20260426T110344Zstab2`: ['base-rates', 'constraints', 'optionality', 'premortem', 'problem-framing-and-reframing']

### Lane 2 capped (top-5 drops)
- `20260426T110025Zstab0`: ['optionality', 'problem-framing-and-reframing']
- `20260426T110204Zstab1`: []
- `20260426T110344Zstab2`: ['power-dynamics']

### Lane 2 cheat-sheet anchors
- `20260426T110025Zstab0`: ['base-rates', 'constraints', 'premortem', 'regret-theory', 'theory-of-constraints']
- `20260426T110204Zstab1`: ['base-rates', 'optionality', 'survivorship-bias']
- `20260426T110344Zstab2`: ['base-rates', 'constraints', 'optionality', 'premortem', 'problem-framing-and-reframing']

### Lane 3 reframings
- `20260426T110025Zstab0`: ['decision-trees', 'lateral-thinking']
- `20260426T110204Zstab1`: ['base-rates', 'optionality']
- `20260426T110344Zstab2`: ['optionality', 'path-dependence']

### Lane 4 gap dims
- `20260426T110025Zstab0`: ['competitive-dynamics', 'incentive-alignment', 'information-quality', 'resource-allocation', 'uncertainty-type']
- `20260426T110204Zstab1`: ['competitive-dynamics', 'incentive-alignment', 'resource-allocation', 'uncertainty-type']
- `20260426T110344Zstab2`: ['competitive-dynamics', 'incentive-alignment', 'information-quality', 'resource-allocation', 'uncertainty-type']

## Cost per run (boundary-call tokens, lower bound when embeddings on)

| Run | Calls | Prompt tok | Completion tok | Total tok | Embedding-expansion observed |
|---|---|---|---|---|---|
| `20260426T110025Zstab0` | 14 | 101484 | 6650 | 108134 | 0 |
| `20260426T110204Zstab1` | 14 | 101373 | 6405 | 107778 | 0 |
| `20260426T110344Zstab2` | 14 | 101387 | 6234 | 107621 | 0 |

> Embedding-expansion calls (gpt-4o-mini, temp=0.7) bypass `BoundaryClient` tracing — reported here as 0 with a caveat. Treat boundary_only totals as a lower bound on Lane 2 cost when `embedding_mode = on`.

### Per-stage boundary token cost

#### `20260426T110025Zstab0`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 7521 |
| companion_verification | 1 | 13661 |
| frame_extraction | 1 | 7881 |
| frame_reframing | 1 | 1441 |
| pass1_cluster_authority | 1 | 8136 |
| pass1_cluster_availability | 1 | 7715 |
| pass1_cluster_closure | 1 | 7965 |
| pass1_cluster_incentive | 1 | 7698 |
| pass1_cluster_residual | 1 | 7794 |
| pass1_cluster_self_regard | 1 | 7828 |
| pass2 | 2 | 15906 |
| structural_coverage_classification | 1 | 7294 |
| structural_coverage_detection | 1 | 7294 |

#### `20260426T110204Zstab1`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 7529 |
| companion_verification | 1 | 13735 |
| frame_extraction | 1 | 7854 |
| frame_reframing | 1 | 1417 |
| pass1_cluster_authority | 1 | 8129 |
| pass1_cluster_availability | 1 | 7713 |
| pass1_cluster_closure | 1 | 7931 |
| pass1_cluster_incentive | 1 | 7698 |
| pass1_cluster_residual | 1 | 7792 |
| pass1_cluster_self_regard | 1 | 7830 |
| pass2 | 2 | 15902 |
| structural_coverage_classification | 1 | 7124 |
| structural_coverage_detection | 1 | 7124 |

#### `20260426T110344Zstab2`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 7468 |
| companion_verification | 1 | 13467 |
| frame_extraction | 1 | 7880 |
| frame_reframing | 1 | 1319 |
| pass1_cluster_authority | 1 | 8128 |
| pass1_cluster_availability | 1 | 7706 |
| pass1_cluster_closure | 1 | 7974 |
| pass1_cluster_incentive | 1 | 7698 |
| pass1_cluster_residual | 1 | 7793 |
| pass1_cluster_self_regard | 1 | 7809 |
| pass2 | 2 | 15879 |
| structural_coverage_classification | 1 | 7250 |
| structural_coverage_detection | 1 | 7250 |
