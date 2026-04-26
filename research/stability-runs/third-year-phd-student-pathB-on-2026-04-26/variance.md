# Stability report — third-year-phd-student-pathB-on

Generated: 2026-04-26T14:34:52Z
Runs: 3
Run IDs: 20260426T143452Zstab0, 20260426T143609Zstab1, 20260426T143732Zstab2
Prompt versions consistent across runs: True

## Per-stage stability (Jaccard)

> 1.0 is a WARNING, not a target — signals a specialist that stopped doing semantic judgment. Acceptance is a threshold band: stability moved up from baseline, no neighboring stage regressed, qualitative review confirms cards still do structural work.

| Stage | Mean | Min | Max |
|---|---|---|---|
| Pass 1 (tendencies) | 1.00 | 1.00 | 1.00 |
| Lane 2 — fingerprint moves | 0.05 | 0.00 | 0.08 |
| Lane 2 — recalled candidates | 0.77 | 0.76 | 0.79 |
| Lane 2 — accepted (pre-cap) | 0.15 | 0.08 | 0.20 |
| Lane 2 — shared-avail. accept agreement | 0.19 | 0.11 | 0.29 |
| Lane 2 — detected (post-cap) | 0.16 | 0.11 | 0.25 |
| Lane 2 — capped (top-5 drops) | 1.00 | 1.00 | 1.00 |
| Lane 2 (cheat-sheet anchors) | 0.16 | 0.11 | 0.25 |
| Lane 3 (reframings) | 0.22 | 0.00 | 0.33 |
| Lane 4 (gap dims) | 0.73 | 0.60 | 0.80 |

Embedding mode per run: ['on', 'on', 'on']  ·  consistent: True

### Recall-source distribution per run

| Run | keyword | embedding | both | other |
|---|---|---|---|---|
| `20260426T143452Zstab0` | 60 | 0 | 0 | 0 |
| `20260426T143609Zstab1` | 60 | 0 | 0 | 0 |
| `20260426T143732Zstab2` | 60 | 0 | 0 | 0 |

## Step 6 anchor naming (per-run)

| Run | Named | Total | Rate |
|---|---|---|---|
| `20260426T143452Zstab0` | (no revised_answer) | — | — |
| `20260426T143609Zstab1` | (no revised_answer) | — | — |
| `20260426T143732Zstab2` | (no revised_answer) | — | — |

## Per-run item diff

### Pass 1 tendencies
- `20260426T143452Zstab0`: ['inconsistency-avoidance-tendency', 'social-proof-tendency']
- `20260426T143609Zstab1`: ['inconsistency-avoidance-tendency', 'social-proof-tendency']
- `20260426T143732Zstab2`: ['inconsistency-avoidance-tendency', 'social-proof-tendency']

### Lane 2 fingerprint moves
- `20260426T143452Zstab0`: ['align ambition with strategic optimality to counter regret framing', 'evaluate options by comparing risk profiles, pipelines, and competitive positioning', 'gather clarifying information to refine decision criteria before advising', 'identify and prioritize bottlenecks that determine option viability', 'pre-plan failure scenarios with salvage strategies and decision checkpoints', 'propose sequenced high-leverage actions with contingencies and fallbacks', 'reframe option based on new specificity to update risk assessment']
- `20260426T143609Zstab1`: ['assess risk profiles of options by mapping to career pipelines and competition levels', 'gather clarifying information to refine decision criteria before recommending', 'identify structural constraints as dealbreakers for high-risk options', 'pinpoint actionable bottlenecks to test feasibility', 'pre-plan failure scenarios with salvage strategies and checkpoints', 'reframe option based on new specificity to update risk assessment', 'sequence high-leverage actions with contingencies and fallbacks']
- `20260426T143732Zstab2`: ['balance ambition and regret by aligning smart strategy with differentiated outcomes', 'evaluate options by comparing risk profiles, pipelines, and competition levels', 'gather clarifying information to refine decision criteria before recommending', 'identify critical bottlenecks and dealbreakers based on constraints like lab capabilities and timeline', 'pre-plan contingencies and failure modes with explicit checkpoints', 'prioritize actionable next steps and sequence to test feasibility while mitigating risks', 'reframe options based on new specifics to update risk assessment']

### Lane 2 recalled candidates
- `20260426T143452Zstab0`: ['adverse-selection', 'aleatory-epistemic-uncertainty-recognition', 'anchoring', 'base-rates', 'bayesian', 'bias-blind-spot', 'black-swan-events', 'blooms-taxonomy', 'boundaries', 'branch-solve-merge', 'calculated-risk-taking', 'cognitive-dissonance', 'commitment-bias', 'comparative-advantage', 'confidence-calibration', 'conjunction-fallacy', 'constructive-feedback-models', 'counterfactual-reasoning', 'critical-mass', 'cultural-intelligence', 'decomposition', 'einstellung-effect', 'false-precision-avoidance', 'feedback-loops', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'inversion', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'margin-of-safety', 'mental-simulation', 'monte-carlo-methods', 'obligations-controls-mapping', 'occams-razor', 'opportunity-cost', 'optimism-bias-and-planning-fallacy', 'optimization-theory', 'optionality', 'power-dynamics', 'premortem', 'principal-agent-problem', 'probabilistic-thinking', 'problem-framing-and-reframing', 'reasoning-mode-router', 'reciprocity-principle', 'regression-to-the-mean', 'representativeness-heuristic', 'risk-assessment', 'second-order-thinking', 'signaling', 'social-proof', 'statistical-discipline', 'survivorship-bias', 'systems-thinking', 'tier-2-high-value', 'time-tested-validation', 'variation-and-selection']
- `20260426T143609Zstab1`: ['aleatory-epistemic-uncertainty-recognition', 'anchoring', 'base-rates', 'bayesian', 'bias-blind-spot', 'black-swan-events', 'blooms-taxonomy', 'boundaries', 'branch-solve-merge', 'calculated-risk-taking', 'cognitive-dissonance', 'commitment-bias', 'comparative-advantage', 'confidence-calibration', 'conjunction-fallacy', 'critical-mass', 'cultural-intelligence', 'decomposition', 'einstellung-effect', 'falsifiability', 'feedback-loops', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'inversion', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'margin-of-safety', 'mental-simulation', 'monte-carlo-methods', 'obligations-controls-mapping', 'occams-razor', 'opportunity-cost', 'optimism-bias-and-planning-fallacy', 'optimization-theory', 'optionality', 'path-dependence', 'power-dynamics', 'premortem', 'principal-agent-problem', 'probabilistic-thinking', 'problem-framing-and-reframing', 'reasoning-mode-router', 'regression-to-the-mean', 'regret-theory', 'representativeness-heuristic', 'risk-assessment', 'scale-economies', 'second-order-thinking', 'signaling', 'social-proof', 'statistical-discipline', 'systems-thinking', 'theory-of-constraints', 'time-tested-validation', 'true-uncertainty-navigation', 'user-centered-design', 'variation-and-selection']
- `20260426T143732Zstab2`: ['active-listening', 'agile-methodologies', 'aleatory-epistemic-uncertainty-recognition', 'algorithmic-thinking', 'anchoring', 'base-rates', 'bayesian', 'bias-blind-spot', 'black-swan-events', 'blooms-taxonomy', 'boundaries', 'branch-solve-merge', 'calculated-risk-taking', 'cognitive-dissonance', 'commitment-bias', 'comparative-advantage', 'confidence-calibration', 'conjunction-fallacy', 'constructive-feedback-models', 'counterfactual-reasoning', 'cultural-intelligence', 'decomposition', 'falsifiability', 'feedback-loops', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'inversion', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'margin-of-safety', 'mental-simulation', 'metacognitive-questioning', 'obligations-controls-mapping', 'occams-razor', 'opportunity-cost', 'optimism-bias-and-planning-fallacy', 'optimization-theory', 'optionality', 'power-dynamics', 'premortem', 'principal-agent-problem', 'probabilistic-thinking', 'problem-framing-and-reframing', 'psychological-safety', 'reasoning-mode-router', 'regression-to-the-mean', 'representativeness-heuristic', 'risk-assessment', 'second-order-thinking', 'signaling', 'social-proof', 'survivorship-bias', 'systems-thinking', 'time-tested-validation', 'true-uncertainty-navigation', 'user-centered-design', 'variation-and-selection']

### Lane 2 accepted (pre-cap)
- `20260426T143452Zstab0`: ['base-rates', 'decomposition', 'opportunity-cost', 'optionality', 'premortem', 'second-order-thinking', 'tier-2-high-value']
- `20260426T143609Zstab1`: ['base-rates', 'optimism-bias-and-planning-fallacy', 'premortem', 'regret-theory', 'theory-of-constraints']
- `20260426T143732Zstab2`: ['comparative-advantage', 'margin-of-safety', 'optionality', 'power-dynamics', 'premortem', 'problem-framing-and-reframing', 'risk-assessment', 'survivorship-bias']

### Lane 2 detected (post-cap)
- `20260426T143452Zstab0`: ['base-rates', 'decomposition', 'optionality', 'premortem', 'tier-2-high-value']
- `20260426T143609Zstab1`: ['base-rates', 'optimism-bias-and-planning-fallacy', 'premortem', 'regret-theory', 'theory-of-constraints']
- `20260426T143732Zstab2`: ['comparative-advantage', 'power-dynamics', 'premortem', 'problem-framing-and-reframing', 'risk-assessment']

### Lane 2 capped (top-5 drops)
- `20260426T143452Zstab0`: []
- `20260426T143609Zstab1`: []
- `20260426T143732Zstab2`: []

### Lane 2 cheat-sheet anchors
- `20260426T143452Zstab0`: ['base-rates', 'decomposition', 'optionality', 'premortem', 'tier-2-high-value']
- `20260426T143609Zstab1`: ['base-rates', 'optimism-bias-and-planning-fallacy', 'premortem', 'regret-theory', 'theory-of-constraints']
- `20260426T143732Zstab2`: ['comparative-advantage', 'power-dynamics', 'premortem', 'problem-framing-and-reframing', 'risk-assessment']

### Lane 3 reframings
- `20260426T143452Zstab0`: ['base-rates', 'optionality']
- `20260426T143609Zstab1`: ['einstellung-effect', 'path-dependence']
- `20260426T143732Zstab2`: ['optionality', 'path-dependence']

### Lane 4 gap dims
- `20260426T143452Zstab0`: ['competitive-dynamics', 'incentive-alignment', 'information-quality', 'resource-allocation', 'uncertainty-type']
- `20260426T143609Zstab1`: ['competitive-dynamics', 'incentive-alignment', 'resource-allocation', 'uncertainty-type']
- `20260426T143732Zstab2`: ['competitive-dynamics', 'incentive-alignment', 'information-quality', 'uncertainty-type']

## Cost per run (boundary-call tokens, lower bound when embeddings on)

| Run | Calls | Prompt tok | Completion tok | Total tok | Embedding-expansion observed |
|---|---|---|---|---|---|
| `20260426T143452Zstab0` | 22 | 163752 | 8324 | 172076 | 0 |
| `20260426T143609Zstab1` | 21 | 157713 | 7602 | 165315 | 0 |
| `20260426T143732Zstab2` | 22 | 163806 | 7834 | 171640 | 0 |

> Embedding-expansion calls (gpt-4o-mini, temp=0.7) bypass `BoundaryClient` tracing — reported here as 0 with a caveat. Treat boundary_only totals as a lower bound on Lane 2 cost when `embedding_mode = on`.

### Per-stage boundary token cost

#### `20260426T143452Zstab0`

| Stage | Calls | Total tok |
|---|---|---|
| companion_calibrator | 1 | 6233 |
| companion_fingerprint | 1 | 7318 |
| companion_verification_shard_0 | 1 | 10431 |
| companion_verification_shard_1 | 1 | 10419 |
| companion_verification_shard_2 | 1 | 10200 |
| frame_extraction | 1 | 7784 |
| frame_reframing | 1 | 1262 |
| pass1_cluster_authority | 1 | 8129 |
| pass1_cluster_availability | 1 | 7761 |
| pass1_cluster_closure | 1 | 7962 |
| pass1_cluster_incentive | 1 | 7698 |
| pass1_cluster_residual | 1 | 7812 |
| pass1_cluster_self_regard | 1 | 7835 |
| pass2 | 7 | 56660 |
| structural_coverage_classification | 1 | 7286 |
| structural_coverage_detection | 1 | 7286 |

#### `20260426T143609Zstab1`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 7243 |
| companion_verification_shard_0 | 1 | 10179 |
| companion_verification_shard_1 | 1 | 10335 |
| companion_verification_shard_2 | 1 | 10298 |
| frame_extraction | 1 | 7876 |
| frame_reframing | 1 | 1370 |
| pass1_cluster_authority | 1 | 8123 |
| pass1_cluster_availability | 1 | 7758 |
| pass1_cluster_closure | 1 | 7957 |
| pass1_cluster_incentive | 1 | 7698 |
| pass1_cluster_residual | 1 | 7810 |
| pass1_cluster_self_regard | 1 | 7838 |
| pass2 | 7 | 56528 |
| structural_coverage_classification | 1 | 7151 |
| structural_coverage_detection | 1 | 7151 |

#### `20260426T143732Zstab2`

| Stage | Calls | Total tok |
|---|---|---|
| companion_calibrator | 1 | 6527 |
| companion_fingerprint | 1 | 7332 |
| companion_verification_shard_0 | 1 | 10416 |
| companion_verification_shard_1 | 1 | 10294 |
| companion_verification_shard_2 | 1 | 10490 |
| frame_extraction | 1 | 7778 |
| frame_reframing | 1 | 1110 |
| pass1_cluster_authority | 1 | 8115 |
| pass1_cluster_availability | 1 | 7768 |
| pass1_cluster_closure | 1 | 7931 |
| pass1_cluster_incentive | 1 | 7698 |
| pass1_cluster_residual | 1 | 7791 |
| pass1_cluster_self_regard | 1 | 7840 |
| pass2 | 7 | 56588 |
| structural_coverage_classification | 1 | 6981 |
| structural_coverage_detection | 1 | 6981 |
