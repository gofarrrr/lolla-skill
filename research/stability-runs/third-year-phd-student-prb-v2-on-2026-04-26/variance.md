# Stability report — third-year-phd-student-prb-v2-on

Generated: 2026-04-26T13:12:42Z
Runs: 3
Run IDs: 20260426T131242Zstab0, 20260426T131402Zstab1, 20260426T131516Zstab2
Prompt versions consistent across runs: True

## Per-stage stability (Jaccard)

> 1.0 is a WARNING, not a target — signals a specialist that stopped doing semantic judgment. Acceptance is a threshold band: stability moved up from baseline, no neighboring stage regressed, qualitative review confirms cards still do structural work.

| Stage | Mean | Min | Max |
|---|---|---|---|
| Pass 1 (tendencies) | 1.00 | 1.00 | 1.00 |
| Lane 2 — fingerprint moves | 0.00 | 0.00 | 0.00 |
| Lane 2 — recalled candidates | 0.77 | 0.74 | 0.82 |
| Lane 2 — accepted (pre-cap) | 0.34 | 0.29 | 0.40 |
| Lane 2 — shared-avail. accept agreement | 0.41 | 0.36 | 0.48 |
| Lane 2 — detected (post-cap) | 0.45 | 0.25 | 0.67 |
| Lane 2 — capped (top-5 drops) | 0.24 | 0.23 | 0.25 |
| Lane 2 (cheat-sheet anchors) | 0.45 | 0.25 | 0.67 |
| Lane 3 (reframings) | 0.17 | 0.00 | 0.50 |
| Lane 4 (gap dims) | 1.00 | 1.00 | 1.00 |

Embedding mode per run: ['on', 'on', 'on']  ·  consistent: True

### Recall-source distribution per run

| Run | keyword | embedding | both | other |
|---|---|---|---|---|
| `20260426T131242Zstab0` | 60 | 0 | 0 | 0 |
| `20260426T131402Zstab1` | 60 | 0 | 0 | 0 |
| `20260426T131516Zstab2` | 60 | 0 | 0 | 0 |

## Step 6 anchor naming (per-run)

| Run | Named | Total | Rate |
|---|---|---|---|
| `20260426T131242Zstab0` | (no revised_answer) | — | — |
| `20260426T131402Zstab1` | (no revised_answer) | — | — |
| `20260426T131516Zstab2` | (no revised_answer) | — | — |

## Per-run item diff

### Pass 1 tendencies
- `20260426T131242Zstab0`: ['inconsistency-avoidance-tendency', 'social-proof-tendency']
- `20260426T131402Zstab1`: ['inconsistency-avoidance-tendency', 'social-proof-tendency']
- `20260426T131516Zstab2`: ['inconsistency-avoidance-tendency', 'social-proof-tendency']

### Lane 2 fingerprint moves
- `20260426T131242Zstab0`: ['align ambition with strategic safety by reframing regret tradeoffs', 'evaluate options by comparing risk-reward profiles against constraints like lab capabilities and advisor retirement', 'gather critical clarifying information before recommending to understand risk profiles and fit', 'identify key bottlenecks and actionable next steps to test feasibility', 'prioritize sequenced actions to de-risk political and commitment issues', 'propose contingency planning with clear fallbacks and checkpoints to mitigate risks', 'reframe options based on new specifics to adjust risk assessment']
- `20260426T131402Zstab1`: ['assess risk profiles of options by mapping to career pipelines, competition, and lab constraints.', "gather critical clarifying information before recommending by asking targeted questions on career goals, advisor's intent for novelty, and lab positioning.", 'identify pivotal bottlenecks and sequence high-leverage actions with contingencies.', 'mitigate advisor retirement risk by building redundant faculty relationships.', 'pre-plan failure scenarios with salvage strategies and decision checkpoints.', 'reframe high-risk option into viable collaborative variant to reduce barriers.', 'update evaluation of option 3 upon new specificity, shifting from high-risk moonshot to conservative methodological application.']
- `20260426T131516Zstab2`: ['assess options by mapping risk profiles to career pipelines and competition levels', 'gather clarifying information to refine decision criteria before recommending', 'identify structural constraints like lab capabilities and advisor timeline as dealbreakers', 'pinpoint actionable bottlenecks and validation steps', 'pre-plan failure scenarios with salvage strategies and decision checkpoints', 'reframe option based on new specificity to update risk assessment', 'sequence high-leverage actions with contingencies and political considerations']

### Lane 2 recalled candidates
- `20260426T131242Zstab0`: ['active-listening', 'adverse-selection', 'aleatory-epistemic-uncertainty-recognition', 'anchoring', 'base-rates', 'bias-blind-spot', 'black-swan-events', 'blooms-taxonomy', 'boundaries', 'branch-solve-merge', 'calculated-risk-taking', 'cognitive-dissonance', 'commitment-bias', 'comparative-advantage', 'confidence-calibration', 'conjunction-fallacy', 'cultural-intelligence', 'decomposition', 'einstellung-effect', 'false-precision-avoidance', 'falsifiability', 'feedback-loops', 'game-theory-payoffs', 'information-asymmetry', 'intellectual-humility', 'inversion', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'mental-simulation', 'meta-cognitive-reflection', 'metacognitive-questioning', 'monte-carlo-methods', 'obligations-controls-mapping', 'occams-razor', 'opportunity-cost', 'optimism-bias-and-planning-fallacy', 'optimization-theory', 'optionality', 'power-dynamics', 'premortem', 'principal-agent-problem', 'probabilistic-thinking', 'problem-framing-and-reframing', 'prospect-theory', 'psychological-safety', 'reasoning-mode-router', 'regression-to-the-mean', 'regret-theory', 'representativeness-heuristic', 'risk-assessment', 'second-order-thinking', 'signaling', 'social-proof', 'statistical-discipline', 'systems-thinking', 'time-tested-validation', 'true-uncertainty-navigation', 'user-centered-design', 'variation-and-selection']
- `20260426T131402Zstab1`: ['adverse-selection', 'aleatory-epistemic-uncertainty-recognition', 'anchoring', 'base-rates', 'bayesian', 'bias-blind-spot', 'black-swan-events', 'blooms-taxonomy', 'boundaries', 'branch-solve-merge', 'calculated-risk-taking', 'cognitive-dissonance', 'commitment-bias', 'comparative-advantage', 'confidence-calibration', 'conjunction-fallacy', 'constructive-feedback-models', 'critical-mass', 'cultural-intelligence', 'decomposition', 'einstellung-effect', 'falsifiability', 'feedback-loops', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'inversion', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'margin-of-safety', 'mental-simulation', 'monte-carlo-methods', 'obligations-controls-mapping', 'opportunity-cost', 'optimism-bias-and-planning-fallacy', 'optimization-theory', 'optionality', 'power-dynamics', 'premortem', 'principal-agent-problem', 'probabilistic-thinking', 'problem-framing-and-reframing', 'reasoning-mode-router', 'regression-to-the-mean', 'representativeness-heuristic', 'risk-assessment', 'scientific-method-evidence-testing', 'second-order-thinking', 'signaling', 'social-proof', 'statistical-discipline', 'system-1', 'systems-thinking', 'theory-of-constraints', 'tier-2-high-value', 'time-tested-validation', 'user-centered-design', 'variation-and-selection']
- `20260426T131516Zstab2`: ['active-listening', 'agile-methodologies', 'aleatory-epistemic-uncertainty-recognition', 'anchoring', 'base-rates', 'bayesian', 'bias-blind-spot', 'black-swan-events', 'blooms-taxonomy', 'boundaries', 'branch-solve-merge', 'calculated-risk-taking', 'cognitive-dissonance', 'commitment-bias', 'comparative-advantage', 'confidence-calibration', 'conjunction-fallacy', 'constructive-feedback-models', 'counterfactual-reasoning', 'cultural-intelligence', 'decomposition', 'einstellung-effect', 'false-precision-avoidance', 'feedback-loops', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'inversion', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'margin-of-safety', 'mental-simulation', 'monte-carlo-methods', 'obligations-controls-mapping', 'occams-razor', 'opportunity-cost', 'optimism-bias-and-planning-fallacy', 'optimization-theory', 'optionality', 'power-dynamics', 'premortem', 'principal-agent-problem', 'probabilistic-thinking', 'problem-framing-and-reframing', 'reasoning-mode-router', 'regression-to-the-mean', 'representativeness-heuristic', 'risk-assessment', 'second-order-thinking', 'signaling', 'social-proof', 'statistical-discipline', 'systems-thinking', 'tier-2-high-value', 'time-tested-validation', 'user-centered-design', 'variation-and-selection', 'wysiati']

### Lane 2 accepted (pre-cap)
- `20260426T131242Zstab0`: ['aleatory-epistemic-uncertainty-recognition', 'anchoring', 'base-rates', 'falsifiability', 'feedback-loops', 'game-theory-payoffs', 'inversion', 'lean-startup-methodology', 'meta-cognitive-reflection', 'optimism-bias-and-planning-fallacy', 'optionality', 'premortem', 'problem-framing-and-reframing', 'regret-theory', 'risk-assessment', 'second-order-thinking', 'statistical-discipline']
- `20260426T131402Zstab1`: ['anchoring', 'base-rates', 'bayesian', 'calculated-risk-taking', 'falsifiability', 'feedback-loops', 'information-asymmetry', 'inversion', 'margin-of-safety', 'obligations-controls-mapping', 'optimism-bias-and-planning-fallacy', 'optimization-theory', 'optionality', 'power-dynamics', 'problem-framing-and-reframing', 'scientific-method-evidence-testing', 'theory-of-constraints', 'tier-2-high-value', 'time-tested-validation']
- `20260426T131516Zstab2`: ['base-rates', 'calculated-risk-taking', 'comparative-advantage', 'game-theory-payoffs', 'inversion', 'lean-startup-methodology', 'optimism-bias-and-planning-fallacy', 'optimization-theory', 'optionality', 'power-dynamics', 'premortem', 'principal-agent-problem', 'reasoning-mode-router', 'risk-assessment', 'second-order-thinking', 'statistical-discipline', 'tier-2-high-value', 'time-tested-validation']

### Lane 2 detected (post-cap)
- `20260426T131242Zstab0`: ['aleatory-epistemic-uncertainty-recognition', 'game-theory-payoffs', 'inversion', 'optionality', 'premortem']
- `20260426T131402Zstab1`: ['base-rates', 'calculated-risk-taking', 'information-asymmetry', 'inversion', 'optionality']
- `20260426T131516Zstab2`: ['base-rates', 'game-theory-payoffs', 'inversion', 'optionality', 'premortem']

### Lane 2 capped (top-5 drops)
- `20260426T131242Zstab0`: ['anchoring', 'base-rates', 'falsifiability', 'feedback-loops', 'lean-startup-methodology', 'meta-cognitive-reflection', 'optimism-bias-and-planning-fallacy', 'problem-framing-and-reframing', 'regret-theory', 'risk-assessment', 'second-order-thinking', 'statistical-discipline']
- `20260426T131402Zstab1`: ['anchoring', 'bayesian', 'falsifiability', 'feedback-loops', 'margin-of-safety', 'obligations-controls-mapping', 'optimism-bias-and-planning-fallacy', 'optimization-theory', 'power-dynamics', 'problem-framing-and-reframing', 'scientific-method-evidence-testing', 'theory-of-constraints', 'tier-2-high-value', 'time-tested-validation']
- `20260426T131516Zstab2`: ['calculated-risk-taking', 'comparative-advantage', 'lean-startup-methodology', 'optimism-bias-and-planning-fallacy', 'optimization-theory', 'power-dynamics', 'principal-agent-problem', 'reasoning-mode-router', 'risk-assessment', 'second-order-thinking', 'statistical-discipline', 'tier-2-high-value', 'time-tested-validation']

### Lane 2 cheat-sheet anchors
- `20260426T131242Zstab0`: ['aleatory-epistemic-uncertainty-recognition', 'game-theory-payoffs', 'inversion', 'optionality', 'premortem']
- `20260426T131402Zstab1`: ['base-rates', 'calculated-risk-taking', 'information-asymmetry', 'inversion', 'optionality']
- `20260426T131516Zstab2`: ['base-rates', 'game-theory-payoffs', 'inversion', 'optionality', 'premortem']

### Lane 3 reframings
- `20260426T131242Zstab0`: ['optionality', 'path-dependence']
- `20260426T131402Zstab1`: ['authority-bias', 'lateral-thinking']
- `20260426T131516Zstab2`: ['optionality']

### Lane 4 gap dims
- `20260426T131242Zstab0`: ['competitive-dynamics', 'incentive-alignment', 'information-quality', 'resource-allocation', 'uncertainty-type']
- `20260426T131402Zstab1`: ['competitive-dynamics', 'incentive-alignment', 'information-quality', 'resource-allocation', 'uncertainty-type']
- `20260426T131516Zstab2`: ['competitive-dynamics', 'incentive-alignment', 'information-quality', 'resource-allocation', 'uncertainty-type']

## Cost per run (boundary-call tokens, lower bound when embeddings on)

| Run | Calls | Prompt tok | Completion tok | Total tok | Embedding-expansion observed |
|---|---|---|---|---|---|
| `20260426T131242Zstab0` | 27 | 204967 | 10615 | 215582 | 0 |
| `20260426T131402Zstab1` | 27 | 208651 | 10896 | 219547 | 0 |
| `20260426T131516Zstab2` | 27 | 204729 | 9174 | 213903 | 0 |

> Embedding-expansion calls (gpt-4o-mini, temp=0.7) bypass `BoundaryClient` tracing — reported here as 0 with a caveat. Treat boundary_only totals as a lower bound on Lane 2 cost when `embedding_mode = on`.

### Per-stage boundary token cost

#### `20260426T131242Zstab0`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 7274 |
| companion_verification_abductive | 1 | 8032 |
| companion_verification_analogical | 1 | 8571 |
| companion_verification_causal | 1 | 8641 |
| companion_verification_counterfactual | 1 | 9229 |
| companion_verification_deductive | 1 | 8466 |
| companion_verification_diagnostic | 1 | 9686 |
| companion_verification_metacognitive | 1 | 9274 |
| companion_verification_probabilistic | 1 | 9155 |
| companion_verification_systems | 1 | 9547 |
| frame_extraction | 1 | 7870 |
| frame_reframing | 1 | 1380 |
| pass1_cluster_authority | 1 | 8127 |
| pass1_cluster_availability | 1 | 7766 |
| pass1_cluster_closure | 1 | 7967 |
| pass1_cluster_incentive | 1 | 7698 |
| pass1_cluster_residual | 1 | 7811 |
| pass1_cluster_self_regard | 1 | 7829 |
| pass2 | 7 | 56651 |
| structural_coverage_classification | 1 | 7304 |
| structural_coverage_detection | 1 | 7304 |

#### `20260426T131402Zstab1`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 7651 |
| companion_verification_abductive | 1 | 8433 |
| companion_verification_analogical | 1 | 8708 |
| companion_verification_causal | 1 | 9620 |
| companion_verification_counterfactual | 1 | 9586 |
| companion_verification_deductive | 1 | 8883 |
| companion_verification_diagnostic | 1 | 10570 |
| companion_verification_metacognitive | 1 | 9055 |
| companion_verification_probabilistic | 1 | 9674 |
| companion_verification_systems | 1 | 9751 |
| frame_extraction | 1 | 7876 |
| frame_reframing | 1 | 1435 |
| pass1_cluster_authority | 1 | 8140 |
| pass1_cluster_availability | 1 | 7710 |
| pass1_cluster_closure | 1 | 7970 |
| pass1_cluster_incentive | 1 | 7698 |
| pass1_cluster_residual | 1 | 7815 |
| pass1_cluster_self_regard | 1 | 7820 |
| pass2 | 7 | 56560 |
| structural_coverage_classification | 1 | 7296 |
| structural_coverage_detection | 1 | 7296 |

#### `20260426T131516Zstab2`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 7254 |
| companion_verification_abductive | 1 | 8019 |
| companion_verification_analogical | 1 | 8123 |
| companion_verification_causal | 1 | 8760 |
| companion_verification_counterfactual | 1 | 9335 |
| companion_verification_deductive | 1 | 8435 |
| companion_verification_diagnostic | 1 | 9743 |
| companion_verification_metacognitive | 1 | 8747 |
| companion_verification_probabilistic | 1 | 9020 |
| companion_verification_systems | 1 | 9435 |
| frame_extraction | 1 | 7772 |
| frame_reframing | 1 | 941 |
| pass1_cluster_authority | 1 | 8147 |
| pass1_cluster_availability | 1 | 7754 |
| pass1_cluster_closure | 1 | 7969 |
| pass1_cluster_incentive | 1 | 7698 |
| pass1_cluster_residual | 1 | 7811 |
| pass1_cluster_self_regard | 1 | 7837 |
| pass2 | 7 | 56541 |
| structural_coverage_classification | 1 | 7281 |
| structural_coverage_detection | 1 | 7281 |
