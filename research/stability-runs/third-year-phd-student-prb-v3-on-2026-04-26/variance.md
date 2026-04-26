# Stability report — third-year-phd-student-prb-v3-on

Generated: 2026-04-26T13:52:18Z
Runs: 3
Run IDs: 20260426T135218Zstab0, 20260426T135347Zstab1, 20260426T135510Zstab2
Prompt versions consistent across runs: True

## Per-stage stability (Jaccard)

> 1.0 is a WARNING, not a target — signals a specialist that stopped doing semantic judgment. Acceptance is a threshold band: stability moved up from baseline, no neighboring stage regressed, qualitative review confirms cards still do structural work.

| Stage | Mean | Min | Max |
|---|---|---|---|
| Pass 1 (tendencies) | 0.67 | 0.50 | 1.00 |
| Lane 2 — fingerprint moves | 0.00 | 0.00 | 0.00 |
| Lane 2 — recalled candidates | 0.77 | 0.71 | 0.82 |
| Lane 2 — accepted (pre-cap) | 0.48 | 0.43 | 0.50 |
| Lane 2 — shared-avail. accept agreement | 0.71 | 0.57 | 0.80 |
| Lane 2 — detected (post-cap) | 0.51 | 0.43 | 0.67 |
| Lane 2 — capped (top-5 drops) | 0.33 | 0.00 | 1.00 |
| Lane 2 (cheat-sheet anchors) | 0.51 | 0.43 | 0.67 |
| Lane 3 (reframings) | 0.56 | 0.33 | 1.00 |
| Lane 4 (gap dims) | 0.87 | 0.80 | 1.00 |

Embedding mode per run: ['on', 'on', 'on']  ·  consistent: True

### Recall-source distribution per run

| Run | keyword | embedding | both | other |
|---|---|---|---|---|
| `20260426T135218Zstab0` | 60 | 0 | 0 | 0 |
| `20260426T135347Zstab1` | 60 | 0 | 0 | 0 |
| `20260426T135510Zstab2` | 60 | 0 | 0 | 0 |

## Step 6 anchor naming (per-run)

| Run | Named | Total | Rate |
|---|---|---|---|
| `20260426T135218Zstab0` | (no revised_answer) | — | — |
| `20260426T135347Zstab1` | (no revised_answer) | — | — |
| `20260426T135510Zstab2` | (no revised_answer) | — | — |

## Per-run item diff

### Pass 1 tendencies
- `20260426T135218Zstab0`: ['social-proof-tendency']
- `20260426T135347Zstab1`: ['inconsistency-avoidance-tendency', 'social-proof-tendency']
- `20260426T135510Zstab2`: ['inconsistency-avoidance-tendency', 'social-proof-tendency']

### Lane 2 fingerprint moves
- `20260426T135218Zstab0`: ['evaluate options by comparing risk profiles, pipelines, and competition levels', 'gather clarifying information on key uncertainties before recommending', 'identify dealbreaker constraints like lab capabilities and timeline against high-risk pivots', 'outline contingency plans and pre-commitment checkpoints for failure modes', 'pinpoint actionable bottlenecks and sequence dependency on them', 'prioritize information-gathering steps into a timed action plan', 'reframe options based on new specifics to update risk assessment']
- `20260426T135347Zstab1`: ['evaluate options by comparing risk profiles, pipelines, and competitive positioning', 'gather clarifying information on key uncertainties before recommending a direction', 'identify structural constraints as dealbreakers for high-risk paths', 'mitigate advisor retirement risk through diversified faculty relationships', 'pinpoint and prioritize actionable bottlenecks with concrete next steps', 'propose sequenced decision tree with fallbacks and contingencies', 'reframe option based on new specifics to reassess risk and novelty']
- `20260426T135510Zstab2`: ['align ambition with strategy by reframing preferred option as both smart and ambitious.', 'evaluate risk profiles by comparing pipeline breadth, competition, and lab readiness across options.', "gather clarifying information to assess options by asking targeted questions on career goals, advisor's intent, and lab positioning.", 'identify critical bottlenecks and enumerate access strategies with pros/cons.', 'propose sequenced action plan with contingencies and pre-commitments to manage uncertainty.', 'reframe high-risk option into viable collaborative variant to reduce infrastructure barriers.', 'update assessment based on refined project description, shifting from moonshot to conservative application.']

### Lane 2 recalled candidates
- `20260426T135218Zstab0`: ['active-listening', 'adverse-selection', 'aleatory-epistemic-uncertainty-recognition', 'anchoring', 'base-rates', 'bayesian', 'bias-blind-spot', 'black-swan-events', 'blooms-taxonomy', 'boundaries', 'branch-solve-merge', 'calculated-risk-taking', 'cognitive-dissonance', 'commitment-bias', 'confidence-calibration', 'conjunction-fallacy', 'constructive-feedback-models', 'critical-mass', 'cultural-intelligence', 'decomposition', 'einstellung-effect', 'false-precision-avoidance', 'falsifiability', 'feedback-loops', 'game-theory-payoffs', 'information-asymmetry', 'intellectual-humility', 'inversion', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'margin-of-safety', 'mental-simulation', 'metacognitive-questioning', 'monte-carlo-methods', 'obligations-controls-mapping', 'opportunity-cost', 'optimism-bias-and-planning-fallacy', 'optimization-theory', 'optionality', 'path-dependence', 'power-dynamics', 'premortem', 'principal-agent-problem', 'probabilistic-thinking', 'problem-framing-and-reframing', 'psychological-safety', 'reasoning-mode-router', 'regret-theory', 'representativeness-heuristic', 'risk-assessment', 'second-order-thinking', 'signaling', 'social-proof', 'statistical-discipline', 'theory-of-constraints', 'time-tested-validation', 'true-uncertainty-navigation', 'variation-and-selection', 'wysiati']
- `20260426T135347Zstab1`: ['active-listening', 'adverse-selection', 'aleatory-epistemic-uncertainty-recognition', 'algorithmic-thinking', 'anchoring', 'base-rates', 'bayesian', 'bias-blind-spot', 'black-swan-events', 'blooms-taxonomy', 'boundaries', 'branch-solve-merge', 'calculated-risk-taking', 'cognitive-dissonance', 'commitment-bias', 'confidence-calibration', 'conjunction-fallacy', 'cultural-intelligence', 'decomposition', 'einstellung-effect', 'falsifiability', 'feedback-loops', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'inversion', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'mental-simulation', 'metacognitive-questioning', 'monte-carlo-methods', 'obligations-controls-mapping', 'occams-razor', 'opportunity-cost', 'optimism-bias-and-planning-fallacy', 'optimization-theory', 'optionality', 'power-dynamics', 'premortem', 'principal-agent-problem', 'probabilistic-thinking', 'problem-framing-and-reframing', 'prospect-theory', 'psychological-safety', 'reasoning-mode-router', 'regression-to-the-mean', 'regret-theory', 'representativeness-heuristic', 'risk-assessment', 'second-order-thinking', 'signaling', 'social-proof', 'statistical-discipline', 'systems-thinking', 'time-tested-validation', 'true-uncertainty-navigation', 'user-centered-design', 'variation-and-selection']
- `20260426T135510Zstab2`: ['adverse-selection', 'aleatory-epistemic-uncertainty-recognition', 'algorithmic-thinking', 'anchoring', 'base-rates', 'bayesian', 'bias-blind-spot', 'black-swan-events', 'blooms-taxonomy', 'boundaries', 'branch-solve-merge', 'calculated-risk-taking', 'cognitive-dissonance', 'commitment-bias', 'comparative-advantage', 'confidence-calibration', 'conjunction-fallacy', 'constructive-feedback-models', 'counterfactual-reasoning', 'cultural-intelligence', 'decomposition', 'einstellung-effect', 'experimentation', 'false-precision-avoidance', 'feedback-loops', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'inversion', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'mental-simulation', 'metacognitive-questioning', 'obligations-controls-mapping', 'occams-razor', 'opportunity-cost', 'optimism-bias-and-planning-fallacy', 'optimization-theory', 'optionality', 'power-dynamics', 'premortem', 'principal-agent-problem', 'probabilistic-thinking', 'problem-framing-and-reframing', 'reasoning-mode-router', 'regression-to-the-mean', 'representativeness-heuristic', 'risk-assessment', 'second-order-thinking', 'signaling', 'social-proof', 'statistical-discipline', 'status-quo-bias', 'systems-thinking', 'time-tested-validation', 'true-uncertainty-navigation', 'user-centered-design', 'variation-and-selection']

### Lane 2 accepted (pre-cap)
- `20260426T135218Zstab0`: ['base-rates', 'calculated-risk-taking', 'optionality', 'power-dynamics', 'premortem', 'regret-theory', 'theory-of-constraints']
- `20260426T135347Zstab1`: ['base-rates', 'calculated-risk-taking', 'falsifiability', 'optionality', 'regret-theory']
- `20260426T135510Zstab2`: ['base-rates', 'calculated-risk-taking', 'optionality', 'premortem', 'status-quo-bias']

### Lane 2 detected (post-cap)
- `20260426T135218Zstab0`: ['base-rates', 'calculated-risk-taking', 'optionality', 'power-dynamics', 'premortem']
- `20260426T135347Zstab1`: ['base-rates', 'calculated-risk-taking', 'falsifiability', 'optionality', 'regret-theory']
- `20260426T135510Zstab2`: ['base-rates', 'calculated-risk-taking', 'optionality', 'premortem', 'status-quo-bias']

### Lane 2 capped (top-5 drops)
- `20260426T135218Zstab0`: ['regret-theory', 'theory-of-constraints']
- `20260426T135347Zstab1`: []
- `20260426T135510Zstab2`: []

### Lane 2 cheat-sheet anchors
- `20260426T135218Zstab0`: ['base-rates', 'calculated-risk-taking', 'optionality', 'power-dynamics', 'premortem']
- `20260426T135347Zstab1`: ['base-rates', 'calculated-risk-taking', 'falsifiability', 'optionality', 'regret-theory']
- `20260426T135510Zstab2`: ['base-rates', 'calculated-risk-taking', 'optionality', 'premortem', 'status-quo-bias']

### Lane 3 reframings
- `20260426T135218Zstab0`: ['optionality', 'path-dependence']
- `20260426T135347Zstab1`: ['authority-bias', 'optionality']
- `20260426T135510Zstab2`: ['authority-bias', 'optionality']

### Lane 4 gap dims
- `20260426T135218Zstab0`: ['competitive-dynamics', 'incentive-alignment', 'information-quality', 'resource-allocation', 'uncertainty-type']
- `20260426T135347Zstab1`: ['competitive-dynamics', 'incentive-alignment', 'information-quality', 'resource-allocation', 'uncertainty-type']
- `20260426T135510Zstab2`: ['competitive-dynamics', 'incentive-alignment', 'resource-allocation', 'uncertainty-type']

## Cost per run (boundary-call tokens, lower bound when embeddings on)

| Run | Calls | Prompt tok | Completion tok | Total tok | Embedding-expansion observed |
|---|---|---|---|---|---|
| `20260426T135218Zstab0` | 21 | 158128 | 7988 | 166116 | 0 |
| `20260426T135347Zstab1` | 21 | 158339 | 8503 | 166842 | 0 |
| `20260426T135510Zstab2` | 21 | 158849 | 8354 | 167203 | 0 |

> Embedding-expansion calls (gpt-4o-mini, temp=0.7) bypass `BoundaryClient` tracing — reported here as 0 with a caveat. Treat boundary_only totals as a lower bound on Lane 2 cost when `embedding_mode = on`.

### Per-stage boundary token cost

#### `20260426T135218Zstab0`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 7425 |
| companion_verification_shard_0 | 1 | 10512 |
| companion_verification_shard_1 | 1 | 10467 |
| companion_verification_shard_2 | 1 | 10491 |
| frame_extraction | 1 | 7779 |
| frame_reframing | 1 | 1120 |
| pass1_cluster_authority | 1 | 8108 |
| pass1_cluster_availability | 1 | 7769 |
| pass1_cluster_closure | 1 | 8010 |
| pass1_cluster_incentive | 1 | 7698 |
| pass1_cluster_residual | 1 | 7813 |
| pass1_cluster_self_regard | 1 | 7843 |
| pass2 | 7 | 56455 |
| structural_coverage_classification | 1 | 7313 |
| structural_coverage_detection | 1 | 7313 |

#### `20260426T135347Zstab1`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 7395 |
| companion_verification_shard_0 | 1 | 10795 |
| companion_verification_shard_1 | 1 | 10426 |
| companion_verification_shard_2 | 1 | 10563 |
| frame_extraction | 1 | 7939 |
| frame_reframing | 1 | 1435 |
| pass1_cluster_authority | 1 | 8127 |
| pass1_cluster_availability | 1 | 7730 |
| pass1_cluster_closure | 1 | 7970 |
| pass1_cluster_incentive | 1 | 7698 |
| pass1_cluster_residual | 1 | 7813 |
| pass1_cluster_self_regard | 1 | 7828 |
| pass2 | 7 | 56601 |
| structural_coverage_classification | 1 | 7261 |
| structural_coverage_detection | 1 | 7261 |

#### `20260426T135510Zstab2`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 7573 |
| companion_verification_shard_0 | 1 | 10889 |
| companion_verification_shard_1 | 1 | 10668 |
| companion_verification_shard_2 | 1 | 10966 |
| frame_extraction | 1 | 7873 |
| frame_reframing | 1 | 1371 |
| pass1_cluster_authority | 1 | 8106 |
| pass1_cluster_availability | 1 | 7753 |
| pass1_cluster_closure | 1 | 7974 |
| pass1_cluster_incentive | 1 | 7698 |
| pass1_cluster_residual | 1 | 7797 |
| pass1_cluster_self_regard | 1 | 7837 |
| pass2 | 7 | 56524 |
| structural_coverage_classification | 1 | 7087 |
| structural_coverage_detection | 1 | 7087 |
