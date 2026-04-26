# Stability report — third-year-phd-student-prb-on

Generated: 2026-04-26T12:28:19Z
Runs: 3
Run IDs: 20260426T122819Zstab0, 20260426T122933Zstab1, 20260426T123048Zstab2
Prompt versions consistent across runs: True

## Per-stage stability (Jaccard)

> 1.0 is a WARNING, not a target — signals a specialist that stopped doing semantic judgment. Acceptance is a threshold band: stability moved up from baseline, no neighboring stage regressed, qualitative review confirms cards still do structural work.

| Stage | Mean | Min | Max |
|---|---|---|---|
| Pass 1 (tendencies) | 1.00 | 1.00 | 1.00 |
| Lane 2 — fingerprint moves | 0.00 | 0.00 | 0.00 |
| Lane 2 — recalled candidates | 0.77 | 0.71 | 0.82 |
| Lane 2 — accepted (pre-cap) | 0.31 | 0.22 | 0.44 |
| Lane 2 — shared-avail. accept agreement | 0.38 | 0.27 | 0.55 |
| Lane 2 — detected (post-cap) | 0.16 | 0.11 | 0.25 |
| Lane 2 — capped (top-5 drops) | 0.24 | 0.14 | 0.38 |
| Lane 2 (cheat-sheet anchors) | 0.16 | 0.11 | 0.25 |
| Lane 3 (reframings) | 0.22 | 0.00 | 0.33 |
| Lane 4 (gap dims) | 0.87 | 0.80 | 1.00 |

Embedding mode per run: ['on', 'on', 'on']  ·  consistent: True

### Recall-source distribution per run

| Run | keyword | embedding | both | other |
|---|---|---|---|---|
| `20260426T122819Zstab0` | 60 | 0 | 0 | 0 |
| `20260426T122933Zstab1` | 60 | 0 | 0 | 0 |
| `20260426T123048Zstab2` | 60 | 0 | 0 | 0 |

## Step 6 anchor naming (per-run)

| Run | Named | Total | Rate |
|---|---|---|---|
| `20260426T122819Zstab0` | (no revised_answer) | — | — |
| `20260426T122933Zstab1` | (no revised_answer) | — | — |
| `20260426T123048Zstab2` | (no revised_answer) | — | — |

## Per-run item diff

### Pass 1 tendencies
- `20260426T122819Zstab0`: ['inconsistency-avoidance-tendency', 'social-proof-tendency']
- `20260426T122933Zstab1`: ['inconsistency-avoidance-tendency', 'social-proof-tendency']
- `20260426T123048Zstab2`: ['inconsistency-avoidance-tendency', 'social-proof-tendency']

### Lane 2 fingerprint moves
- `20260426T122819Zstab0`: ['assess options by mapping to career pipelines and competitive landscapes under time constraints', 'gather critical clarifying information before recommending to understand risk profiles and fit with constraints', 'identify dealbreaker risks from lab capabilities and advisor retirement timeline', 'mitigate advisor retirement risk through relationship-building and structural safeguards', 'pinpoint key bottlenecks and viable paths to resolve them', 'propose sequenced high-leverage actions with contingencies and fallbacks', 'reframe option based on refined description to update risk-benefit assessment']
- `20260426T122933Zstab1`: ['balance ambition and regret by aligning smart strategy with high-upside choices', 'evaluate options by comparing risk profiles, pipelines, and competitive positioning', 'gather clarifying information on key uncertainties before recommending', 'identify dealbreaker constraints like lab infrastructure and timeline risks', 'outline sequential decision tree with fallbacks and checkpoints', 'pre-plan failure scenarios with salvageable pivots and predefined go/no-go criteria', 'reframe options based on new specifics to update risk assessment']
- `20260426T123048Zstab2`: ['assess risk profiles of options by comparing competitive positioning, infrastructure needs, and timelines against constraints', 'estimate base rates and selection biases for novel work to calibrate expectations', 'evaluate long-term career pipelines and opportunity costs beyond immediate defensibility', 'gather clarifying information on key uncertainties before recommending a direction', 'identify and prioritize bottlenecks that determine option viability', 'outline sequenced action plan with fallbacks and checkpoints to de-risk decision under time constraints', 'reframe options hierarchically from pure pivots to collaborative hybrids to leverage existing strengths']

### Lane 2 recalled candidates
- `20260426T122819Zstab0`: ['active-listening', 'adverse-selection', 'aleatory-epistemic-uncertainty-recognition', 'anchoring', 'base-rates', 'bayesian', 'bias-blind-spot', 'black-swan-events', 'blooms-taxonomy', 'boundaries', 'branch-solve-merge', 'calculated-risk-taking', 'cognitive-dissonance', 'commitment-bias', 'comparative-advantage', 'confidence-calibration', 'conjunction-fallacy', 'constructive-feedback-models', 'cultural-intelligence', 'decomposition', 'einstellung-effect', 'falsifiability', 'feedback-loops', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'inversion', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'metacognitive-questioning', 'monte-carlo-methods', 'obligations-controls-mapping', 'occams-razor', 'opportunity-cost', 'optimism-bias-and-planning-fallacy', 'optimization-theory', 'optionality', 'power-dynamics', 'premortem', 'principal-agent-problem', 'probabilistic-thinking', 'problem-framing-and-reframing', 'reasoning-mode-router', 'reciprocity-principle', 'representativeness-heuristic', 'risk-assessment', 'second-order-thinking', 'signaling', 'social-proof', 'statistical-discipline', 'statistical-learning-theory', 'systems-thinking', 'theory-of-constraints', 'tier-2-high-value', 'time-tested-validation', 'true-uncertainty-navigation', 'user-centered-design', 'variation-and-selection']
- `20260426T122933Zstab1`: ['aleatory-epistemic-uncertainty-recognition', 'anchoring', 'base-rates', 'bayesian', 'bias-blind-spot', 'black-swan-events', 'blooms-taxonomy', 'boundaries', 'branch-solve-merge', 'calculated-risk-taking', 'cognitive-dissonance', 'commitment-bias', 'comparative-advantage', 'confidence-calibration', 'conjunction-fallacy', 'constructive-feedback-models', 'counterfactual-reasoning', 'cultural-intelligence', 'decomposition', 'einstellung-effect', 'feedback-loops', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'inversion', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'margin-of-safety', 'mental-simulation', 'metacognitive-questioning', 'monte-carlo-methods', 'obligations-controls-mapping', 'occams-razor', 'opportunity-cost', 'optimism-bias-and-planning-fallacy', 'optimization-theory', 'optionality', 'power-dynamics', 'premortem', 'principal-agent-problem', 'probabilistic-thinking', 'problem-framing-and-reframing', 'reasoning-mode-router', 'reciprocity-principle', 'regression-to-the-mean', 'representativeness-heuristic', 'risk-assessment', 'second-order-thinking', 'signaling', 'social-proof', 'statistical-discipline', 'survivorship-bias', 'systems-thinking', 'theory-of-constraints', 'time-tested-validation', 'true-uncertainty-navigation', 'variation-and-selection', 'wysiati']
- `20260426T123048Zstab2`: ['active-listening', 'adverse-selection', 'agile-methodologies', 'aleatory-epistemic-uncertainty-recognition', 'anchoring', 'base-rates', 'bayesian', 'bias-blind-spot', 'black-swan-events', 'blooms-taxonomy', 'boundaries', 'branch-solve-merge', 'calculated-risk-taking', 'commitment-bias', 'comparative-advantage', 'confidence-calibration', 'conjunction-fallacy', 'constraints', 'constructive-feedback-models', 'counterfactual-reasoning', 'cultural-intelligence', 'decomposition', 'einstellung-effect', 'false-precision-avoidance', 'falsifiability', 'feedback-loops', 'game-theory-payoffs', 'information-asymmetry', 'intellectual-humility', 'inversion', 'latticework-of-mental-models', 'learning-curve', 'margin-of-safety', 'metacognitive-questioning', 'obligations-controls-mapping', 'occams-razor', 'opportunity-cost', 'optimism-bias-and-planning-fallacy', 'optimization-theory', 'optionality', 'pareto-principle', 'power-dynamics', 'premortem', 'principal-agent-problem', 'probabilistic-thinking', 'reasoning-mode-router', 'regression-to-the-mean', 'regret-theory', 'representativeness-heuristic', 'risk-assessment', 'second-order-thinking', 'signaling', 'social-proof', 'statistical-discipline', 'survivorship-bias', 'theory-of-constraints', 'time-tested-validation', 'true-uncertainty-navigation', 'variation-and-selection', 'wysiati']

### Lane 2 accepted (pre-cap)
- `20260426T122819Zstab0`: ['base-rates', 'boundaries', 'calculated-risk-taking', 'falsifiability', 'feedback-loops', 'information-asymmetry', 'inversion', 'latticework-of-mental-models', 'opportunity-cost', 'optimism-bias-and-planning-fallacy', 'optimization-theory', 'optionality', 'power-dynamics', 'probabilistic-thinking', 'risk-assessment', 'statistical-discipline', 'theory-of-constraints', 'tier-2-high-value', 'variation-and-selection']
- `20260426T122933Zstab1`: ['base-rates', 'confidence-calibration', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'margin-of-safety', 'optimization-theory', 'premortem', 'risk-assessment', 'statistical-discipline', 'survivorship-bias', 'theory-of-constraints', 'time-tested-validation', 'wysiati']
- `20260426T123048Zstab2`: ['base-rates', 'boundaries', 'comparative-advantage', 'confidence-calibration', 'constraints', 'falsifiability', 'feedback-loops', 'intellectual-humility', 'opportunity-cost', 'optimization-theory', 'pareto-principle', 'power-dynamics', 'probabilistic-thinking', 'reasoning-mode-router', 'regret-theory', 'risk-assessment', 'statistical-discipline', 'survivorship-bias', 'theory-of-constraints', 'variation-and-selection']

### Lane 2 detected (post-cap)
- `20260426T122819Zstab0`: ['base-rates', 'calculated-risk-taking', 'inversion', 'opportunity-cost', 'optionality']
- `20260426T122933Zstab1`: ['base-rates', 'confidence-calibration', 'learning-curve', 'premortem', 'risk-assessment']
- `20260426T123048Zstab2`: ['base-rates', 'intellectual-humility', 'opportunity-cost', 'optimization-theory', 'power-dynamics']

### Lane 2 capped (top-5 drops)
- `20260426T122819Zstab0`: ['boundaries', 'falsifiability', 'feedback-loops', 'information-asymmetry', 'latticework-of-mental-models', 'optimism-bias-and-planning-fallacy', 'optimization-theory', 'power-dynamics', 'probabilistic-thinking', 'risk-assessment', 'statistical-discipline', 'theory-of-constraints', 'tier-2-high-value', 'variation-and-selection']
- `20260426T122933Zstab1`: ['latticework-of-mental-models', 'lean-startup-methodology', 'margin-of-safety', 'optimization-theory', 'statistical-discipline', 'survivorship-bias', 'theory-of-constraints', 'time-tested-validation', 'wysiati']
- `20260426T123048Zstab2`: ['boundaries', 'comparative-advantage', 'confidence-calibration', 'constraints', 'falsifiability', 'feedback-loops', 'pareto-principle', 'probabilistic-thinking', 'reasoning-mode-router', 'regret-theory', 'risk-assessment', 'statistical-discipline', 'survivorship-bias', 'theory-of-constraints', 'variation-and-selection']

### Lane 2 cheat-sheet anchors
- `20260426T122819Zstab0`: ['base-rates', 'calculated-risk-taking', 'inversion', 'opportunity-cost', 'optionality']
- `20260426T122933Zstab1`: ['base-rates', 'confidence-calibration', 'learning-curve', 'premortem', 'risk-assessment']
- `20260426T123048Zstab2`: ['base-rates', 'intellectual-humility', 'opportunity-cost', 'optimization-theory', 'power-dynamics']

### Lane 3 reframings
- `20260426T122819Zstab0`: ['lateral-thinking', 'optionality']
- `20260426T122933Zstab1`: ['brainstorming', 'optionality']
- `20260426T123048Zstab2`: ['brainstorming', 'second-order-thinking']

### Lane 4 gap dims
- `20260426T122819Zstab0`: ['competitive-dynamics', 'incentive-alignment', 'information-quality', 'resource-allocation', 'uncertainty-type']
- `20260426T122933Zstab1`: ['competitive-dynamics', 'incentive-alignment', 'information-quality', 'resource-allocation', 'uncertainty-type']
- `20260426T123048Zstab2`: ['competitive-dynamics', 'incentive-alignment', 'information-quality', 'resource-allocation']

## Cost per run (boundary-call tokens, lower bound when embeddings on)

| Run | Calls | Prompt tok | Completion tok | Total tok | Embedding-expansion observed |
|---|---|---|---|---|---|
| `20260426T122819Zstab0` | 27 | 201782 | 9009 | 210791 | 0 |
| `20260426T122933Zstab1` | 27 | 201931 | 8923 | 210854 | 0 |
| `20260426T123048Zstab2` | 27 | 203492 | 9528 | 213020 | 0 |

> Embedding-expansion calls (gpt-4o-mini, temp=0.7) bypass `BoundaryClient` tracing — reported here as 0 with a caveat. Treat boundary_only totals as a lower bound on Lane 2 cost when `embedding_mode = on`.

### Per-stage boundary token cost

#### `20260426T122819Zstab0`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 7276 |
| companion_verification_abductive | 1 | 7883 |
| companion_verification_analogical | 1 | 7902 |
| companion_verification_causal | 1 | 8213 |
| companion_verification_counterfactual | 1 | 8587 |
| companion_verification_deductive | 1 | 8130 |
| companion_verification_diagnostic | 1 | 9565 |
| companion_verification_metacognitive | 1 | 8502 |
| companion_verification_probabilistic | 1 | 8916 |
| companion_verification_systems | 1 | 8822 |
| frame_extraction | 1 | 7785 |
| frame_reframing | 1 | 1256 |
| pass1_cluster_authority | 1 | 8121 |
| pass1_cluster_availability | 1 | 7757 |
| pass1_cluster_closure | 1 | 7981 |
| pass1_cluster_incentive | 1 | 7698 |
| pass1_cluster_residual | 1 | 7787 |
| pass1_cluster_self_regard | 1 | 7833 |
| pass2 | 7 | 56579 |
| structural_coverage_classification | 1 | 7099 |
| structural_coverage_detection | 1 | 7099 |

#### `20260426T122933Zstab1`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 7287 |
| companion_verification_abductive | 1 | 7796 |
| companion_verification_analogical | 1 | 7857 |
| companion_verification_causal | 1 | 8429 |
| companion_verification_counterfactual | 1 | 8552 |
| companion_verification_deductive | 1 | 8108 |
| companion_verification_diagnostic | 1 | 9344 |
| companion_verification_metacognitive | 1 | 8588 |
| companion_verification_probabilistic | 1 | 8699 |
| companion_verification_systems | 1 | 8741 |
| frame_extraction | 1 | 7789 |
| frame_reframing | 1 | 1244 |
| pass1_cluster_authority | 1 | 8129 |
| pass1_cluster_availability | 1 | 7767 |
| pass1_cluster_closure | 1 | 8021 |
| pass1_cluster_incentive | 1 | 7698 |
| pass1_cluster_residual | 1 | 7813 |
| pass1_cluster_self_regard | 1 | 7829 |
| pass2 | 7 | 56515 |
| structural_coverage_classification | 1 | 7324 |
| structural_coverage_detection | 1 | 7324 |

#### `20260426T123048Zstab2`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 7503 |
| companion_verification_abductive | 1 | 8142 |
| companion_verification_analogical | 1 | 8151 |
| companion_verification_causal | 1 | 8567 |
| companion_verification_counterfactual | 1 | 8973 |
| companion_verification_deductive | 1 | 8429 |
| companion_verification_diagnostic | 1 | 9393 |
| companion_verification_metacognitive | 1 | 8767 |
| companion_verification_probabilistic | 1 | 8877 |
| companion_verification_systems | 1 | 9184 |
| frame_extraction | 1 | 7785 |
| frame_reframing | 1 | 1204 |
| pass1_cluster_authority | 1 | 8146 |
| pass1_cluster_availability | 1 | 7722 |
| pass1_cluster_closure | 1 | 7990 |
| pass1_cluster_incentive | 1 | 7698 |
| pass1_cluster_residual | 1 | 7810 |
| pass1_cluster_self_regard | 1 | 7832 |
| pass2 | 7 | 56567 |
| structural_coverage_classification | 1 | 7140 |
| structural_coverage_detection | 1 | 7140 |
