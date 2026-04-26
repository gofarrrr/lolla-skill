# Stability report — third-year-phd-student-lane2-on

Generated: 2026-04-26T10:56:19Z
Runs: 3
Run IDs: 20260426T105619Zstab0, 20260426T105741Zstab1, 20260426T105901Zstab2
Prompt versions consistent across runs: True

## Per-stage stability (Jaccard)

> 1.0 is a WARNING, not a target — signals a specialist that stopped doing semantic judgment. Acceptance is a threshold band: stability moved up from baseline, no neighboring stage regressed, qualitative review confirms cards still do structural work.

| Stage | Mean | Min | Max |
|---|---|---|---|
| Pass 1 (tendencies) | 1.00 | 1.00 | 1.00 |
| Lane 2 — fingerprint moves | 0.20 | 0.17 | 0.27 |
| Lane 2 — recalled candidates | 0.76 | 0.71 | 0.82 |
| Lane 2 — accepted (pre-cap) | 0.37 | 0.29 | 0.50 |
| Lane 2 — detected (post-cap) | 0.37 | 0.29 | 0.50 |
| Lane 2 — capped (top-5 drops) | 1.00 | 1.00 | 1.00 |
| Lane 2 (cheat-sheet anchors) | 0.37 | 0.29 | 0.50 |
| Lane 3 (reframings) | 0.11 | 0.00 | 0.33 |
| Lane 4 (gap dims) | 0.66 | 0.50 | 0.80 |

Embedding mode per run: ['on', 'on', 'on']  ·  consistent: True

### Recall-source distribution per run

| Run | keyword | embedding | both | other |
|---|---|---|---|---|
| `20260426T105619Zstab0` | 60 | 0 | 0 | 0 |
| `20260426T105741Zstab1` | 60 | 0 | 0 | 0 |
| `20260426T105901Zstab2` | 60 | 0 | 0 | 0 |

## Step 6 anchor naming (per-run)

| Run | Named | Total | Rate |
|---|---|---|---|
| `20260426T105619Zstab0` | (no revised_answer) | — | — |
| `20260426T105741Zstab1` | (no revised_answer) | — | — |
| `20260426T105901Zstab2` | (no revised_answer) | — | — |

## Per-run item diff

### Pass 1 tendencies
- `20260426T105619Zstab0`: ['inconsistency-avoidance-tendency', 'social-proof-tendency']
- `20260426T105741Zstab1`: ['inconsistency-avoidance-tendency', 'social-proof-tendency']
- `20260426T105901Zstab2`: ['inconsistency-avoidance-tendency', 'social-proof-tendency']

### Lane 2 fingerprint moves
- `20260426T105619Zstab0`: ['evaluate options by comparing risk profiles, pipelines, and competition levels', 'gather clarifying information on key uncertainties before recommending', 'identify dealbreaker constraints like lab infrastructure and advisor timeline', 'pinpoint and prioritize actionable bottlenecks', 'propose sequenced decision tree with fallbacks and checkpoints', 'reframe options based on new specifics to update risk assessment', 'surface overlooked factors like time-to-paper, funding, and political risks']
- `20260426T105741Zstab1`: ['align ambition with strategic optimality to counter regret framing', 'evaluate options by comparing risk profiles, pipelines, and competition levels', 'gather clarifying information on key uncertainties before recommending', 'identify dealbreaker constraints like lab infrastructure and timeline against advisor retirement', 'outline sequenced contingency plans with fallbacks at each stage', 'pinpoint highest-leverage next action to test feasibility', 'reframe option based on new specifics to update risk assessment']
- `20260426T105901Zstab2`: ['evaluate options by comparing risk profiles, pipelines, and competition levels', 'gather clarifying information on key uncertainties before recommending', 'identify dealbreaker constraints like lab infrastructure and timeline against advisor retirement', 'pinpoint actionable bottlenecks and validation steps', 'prioritize conversation order to de-risk political and commitment issues', 'propose sequenced contingency plans with fallbacks', 'reframe option based on new specificity to reassess risk profile']

### Lane 2 recalled candidates
- `20260426T105619Zstab0`: ['active-listening', 'adverse-selection', 'aleatory-epistemic-uncertainty-recognition', 'anchoring', 'base-rates', 'bayesian', 'bias-blind-spot', 'black-swan-events', 'blooms-taxonomy', 'boundaries', 'branch-solve-merge', 'calculated-risk-taking', 'cognitive-dissonance', 'commitment-bias', 'confidence-calibration', 'conjunction-fallacy', 'constructive-feedback-models', 'cultural-intelligence', 'decomposition', 'einstellung-effect', 'false-precision-avoidance', 'falsifiability', 'feedback-loops', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'inversion', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'margin-of-safety', 'meta-cognitive-reflection', 'metacognitive-questioning', 'monte-carlo-methods', 'obligations-controls-mapping', 'occams-razor', 'opportunity-cost', 'optimism-bias-and-planning-fallacy', 'optimization-theory', 'optionality', 'pareto-principle', 'path-dependence', 'power-dynamics', 'premortem', 'principal-agent-problem', 'probabilistic-thinking', 'problem-framing-and-reframing', 'reasoning-mode-router', 'regression-to-the-mean', 'representativeness-heuristic', 'risk-assessment', 'second-order-thinking', 'signaling', 'social-proof', 'tier-2-high-value', 'time-tested-validation', 'true-uncertainty-navigation', 'variation-and-selection', 'wysiati']
- `20260426T105741Zstab1`: ['active-listening', 'aleatory-epistemic-uncertainty-recognition', 'anchoring', 'base-rates', 'bayesian', 'bias-blind-spot', 'black-swan-events', 'blooms-taxonomy', 'boundaries', 'branch-solve-merge', 'calculated-risk-taking', 'cognitive-dissonance', 'commitment-bias', 'comparative-advantage', 'confidence-calibration', 'conjunction-fallacy', 'cultural-intelligence', 'decomposition', 'einstellung-effect', 'endowment-effect', 'falsifiability', 'feedback-loops', 'feynman-technique', 'game-theory-payoffs', 'information-asymmetry', 'intellectual-humility', 'inversion', 'iteration', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'mental-simulation', 'metacognitive-questioning', 'obligations-controls-mapping', 'occams-razor', 'opportunity-cost', 'optimism-bias-and-planning-fallacy', 'optimization-theory', 'optionality', 'pareto-principle', 'path-dependence', 'power-dynamics', 'premortem', 'principal-agent-problem', 'probabilistic-thinking', 'problem-framing-and-reframing', 'reasoning-mode-router', 'regression-to-the-mean', 'regret-theory', 'representativeness-heuristic', 'risk-assessment', 'scale-economies', 'second-order-thinking', 'signaling', 'social-proof', 'systems-thinking', 'theory-of-constraints', 'time-tested-validation', 'true-uncertainty-navigation', 'variation-and-selection']
- `20260426T105901Zstab2`: ['active-listening', 'adverse-selection', 'aleatory-epistemic-uncertainty-recognition', 'anchoring', 'base-rates', 'bayesian', 'bias-blind-spot', 'black-swan-events', 'blooms-taxonomy', 'boundaries', 'branch-solve-merge', 'calculated-risk-taking', 'cognitive-dissonance', 'commitment-bias', 'comparative-advantage', 'confidence-calibration', 'conjunction-fallacy', 'constraints', 'constructive-feedback-models', 'cultural-intelligence', 'decomposition', 'einstellung-effect', 'false-precision-avoidance', 'falsifiability', 'feedback-loops', 'game-theory-payoffs', 'information-asymmetry', 'intellectual-humility', 'inversion', 'iteration', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'margin-of-safety', 'metacognitive-questioning', 'monte-carlo-methods', 'obligations-controls-mapping', 'opportunity-cost', 'optimism-bias-and-planning-fallacy', 'optimization-theory', 'optionality', 'power-dynamics', 'premortem', 'principal-agent-problem', 'probabilistic-thinking', 'problem-framing-and-reframing', 'psychological-safety', 'reasoning-mode-router', 'regression-to-the-mean', 'representativeness-heuristic', 'risk-assessment', 'second-order-thinking', 'signaling', 'social-proof', 'statistical-discipline', 'time-tested-validation', 'true-uncertainty-navigation', 'user-centered-design', 'variation-and-selection', 'wysiati']

### Lane 2 accepted (pre-cap)
- `20260426T105619Zstab0`: ['base-rates', 'decomposition', 'optionality', 'premortem', 'problem-framing-and-reframing']
- `20260426T105741Zstab1`: ['base-rates', 'optionality', 'regret-theory', 'theory-of-constraints']
- `20260426T105901Zstab2`: ['base-rates', 'optionality', 'power-dynamics', 'premortem']

### Lane 2 detected (post-cap)
- `20260426T105619Zstab0`: ['base-rates', 'decomposition', 'optionality', 'premortem', 'problem-framing-and-reframing']
- `20260426T105741Zstab1`: ['base-rates', 'optionality', 'regret-theory', 'theory-of-constraints']
- `20260426T105901Zstab2`: ['base-rates', 'optionality', 'power-dynamics', 'premortem']

### Lane 2 capped (top-5 drops)
- `20260426T105619Zstab0`: []
- `20260426T105741Zstab1`: []
- `20260426T105901Zstab2`: []

### Lane 2 cheat-sheet anchors
- `20260426T105619Zstab0`: ['base-rates', 'decomposition', 'optionality', 'premortem', 'problem-framing-and-reframing']
- `20260426T105741Zstab1`: ['base-rates', 'optionality', 'regret-theory', 'theory-of-constraints']
- `20260426T105901Zstab2`: ['base-rates', 'optionality', 'power-dynamics', 'premortem']

### Lane 3 reframings
- `20260426T105619Zstab0`: ['authority-bias', 'brainstorming']
- `20260426T105741Zstab1`: ['brainstorming', 'second-order-thinking']
- `20260426T105901Zstab2`: ['base-rates', 'lateral-thinking']

### Lane 4 gap dims
- `20260426T105619Zstab0`: ['competitive-dynamics', 'incentive-alignment', 'information-quality', 'resource-allocation', 'uncertainty-type']
- `20260426T105741Zstab1`: ['competitive-dynamics', 'incentive-alignment', 'information-quality', 'uncertainty-type']
- `20260426T105901Zstab2`: ['competitive-dynamics', 'incentive-alignment', 'resource-allocation', 'scope-boundary', 'uncertainty-type']

## Cost per run (boundary-call tokens, lower bound when embeddings on)

| Run | Calls | Prompt tok | Completion tok | Total tok | Embedding-expansion observed |
|---|---|---|---|---|---|
| `20260426T105619Zstab0` | 19 | 141242 | 6448 | 147690 | 0 |
| `20260426T105741Zstab1` | 19 | 141004 | 6453 | 147457 | 0 |
| `20260426T105901Zstab2` | 19 | 141250 | 6908 | 148158 | 0 |

> Embedding-expansion calls (gpt-4o-mini, temp=0.7) bypass `BoundaryClient` tracing — reported here as 0 with a caveat. Treat boundary_only totals as a lower bound on Lane 2 cost when `embedding_mode = on`.

### Per-stage boundary token cost

#### `20260426T105619Zstab0`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 7254 |
| companion_verification | 1 | 13164 |
| frame_extraction | 1 | 7884 |
| frame_reframing | 1 | 1431 |
| pass1_cluster_authority | 1 | 8139 |
| pass1_cluster_availability | 1 | 7758 |
| pass1_cluster_closure | 1 | 7961 |
| pass1_cluster_incentive | 1 | 7698 |
| pass1_cluster_residual | 1 | 7817 |
| pass1_cluster_self_regard | 1 | 7842 |
| pass2 | 7 | 56518 |
| structural_coverage_classification | 1 | 7112 |
| structural_coverage_detection | 1 | 7112 |

#### `20260426T105741Zstab1`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 7283 |
| companion_verification | 1 | 13533 |
| frame_extraction | 1 | 7808 |
| frame_reframing | 1 | 1277 |
| pass1_cluster_authority | 1 | 8132 |
| pass1_cluster_availability | 1 | 7732 |
| pass1_cluster_closure | 1 | 7964 |
| pass1_cluster_incentive | 1 | 7698 |
| pass1_cluster_residual | 1 | 7801 |
| pass1_cluster_self_regard | 1 | 7828 |
| pass2 | 7 | 56513 |
| structural_coverage_classification | 1 | 6944 |
| structural_coverage_detection | 1 | 6944 |

#### `20260426T105901Zstab2`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 7261 |
| companion_verification | 1 | 13219 |
| frame_extraction | 1 | 7885 |
| frame_reframing | 1 | 1463 |
| pass1_cluster_authority | 1 | 8152 |
| pass1_cluster_availability | 1 | 7756 |
| pass1_cluster_closure | 1 | 7958 |
| pass1_cluster_incentive | 1 | 7698 |
| pass1_cluster_residual | 1 | 7819 |
| pass1_cluster_self_regard | 1 | 7837 |
| pass2 | 7 | 56510 |
| structural_coverage_classification | 1 | 7300 |
| structural_coverage_detection | 1 | 7300 |
