# Stability report — mid-level-consultant-decides-pathB-on

Generated: 2026-04-26T14:31:27Z
Runs: 3
Run IDs: 20260426T143127Zstab0, 20260426T143234Zstab1, 20260426T143344Zstab2
Prompt versions consistent across runs: True

## Per-stage stability (Jaccard)

> 1.0 is a WARNING, not a target — signals a specialist that stopped doing semantic judgment. Acceptance is a threshold band: stability moved up from baseline, no neighboring stage regressed, qualitative review confirms cards still do structural work.

| Stage | Mean | Min | Max |
|---|---|---|---|
| Pass 1 (tendencies) | 1.00 | 1.00 | 1.00 |
| Lane 2 — fingerprint moves | 0.18 | 0.08 | 0.40 |
| Lane 2 — recalled candidates | 0.80 | 0.74 | 0.94 |
| Lane 2 — accepted (pre-cap) | 0.46 | 0.38 | 0.57 |
| Lane 2 — shared-avail. accept agreement | 0.48 | 0.43 | 0.57 |
| Lane 2 — detected (post-cap) | 0.37 | 0.25 | 0.43 |
| Lane 2 — capped (top-5 drops) | 1.00 | 1.00 | 1.00 |
| Lane 2 (cheat-sheet anchors) | 0.37 | 0.25 | 0.43 |
| Lane 3 (reframings) | 0.11 | 0.00 | 0.33 |
| Lane 4 (gap dims) | 0.73 | 0.60 | 1.00 |

Embedding mode per run: ['on', 'on', 'on']  ·  consistent: True

### Recall-source distribution per run

| Run | keyword | embedding | both | other |
|---|---|---|---|---|
| `20260426T143127Zstab0` | 60 | 0 | 0 | 0 |
| `20260426T143234Zstab1` | 60 | 0 | 0 | 0 |
| `20260426T143344Zstab2` | 60 | 0 | 0 | 0 |

## Step 6 anchor naming (per-run)

| Run | Named | Total | Rate |
|---|---|---|---|
| `20260426T143127Zstab0` | (no revised_answer) | — | — |
| `20260426T143234Zstab1` | (no revised_answer) | — | — |
| `20260426T143344Zstab2` | (no revised_answer) | — | — |

## Per-run item diff

### Pass 1 tendencies
- `20260426T143127Zstab0`: ['authority-misinfluence-tendency', 'reward-and-punishment-superresponse-tendency']
- `20260426T143234Zstab1`: ['authority-misinfluence-tendency', 'reward-and-punishment-superresponse-tendency']
- `20260426T143344Zstab2`: ['authority-misinfluence-tendency', 'reward-and-punishment-superresponse-tendency']

### Lane 2 fingerprint moves
- `20260426T143127Zstab0`: ['apply threshold-based decision rule integrating user-provided confidence against institutional risks', 'assess evidential strength by probing for confirmatory details to determine decision weight', 'compare internal vs external reporting using conditional criteria and confidence thresholds', 'evaluate evidence against benign alternatives to gauge likelihood of misconduct', 'frame decision as multi-dimensional trade-off of legal, career, and moral risks', 'isolate current obligation from secondary concerns to maintain focus on primary duty', 'sequence actions into prioritized timeline balancing preparation, normalcy, and risk mitigation']
- `20260426T143234Zstab1`: ["apply threshold to user's confidence level to recommend optimal reporting path", 'assess evidential strength by probing for specifics to determine decision weight', 'compare internal vs external reporting using conditional criteria and confidence thresholds', "isolate user's primary obligation from secondary concerns about others' past actions", 'sequence immediate actions into prioritized timeline to minimize risks', 'structure decision into balanced multi-dimensional framework of risks and stakes', 'weigh likelihood of obstruction against benign alternatives based on contextual factors']
- `20260426T143344Zstab2`: ['apply threshold-based decision rule integrating user-provided confidence against institutional risks', 'assess evidential strength by probing for confirmatory details to determine decision weight', 'compare internal vs external reporting using conditional criteria and confidence thresholds', 'evaluate evidence against benign alternatives to gauge likelihood of misconduct', 'isolate current obligation from extraneous concerns to focus on primary duty', 'sequence actions into prioritized timeline balancing preparation, normalcy, and risk minimization', 'structure decision as multi-dimensional tradeoff of legal, career, and moral risks']

### Lane 2 recalled candidates
- `20260426T143127Zstab0`: ['active-listening', 'aleatory-epistemic-uncertainty-recognition', 'authenticity', 'authority-bias', 'base-rates', 'bayesian', 'bias-blind-spot', 'boundaries', 'branch-solve-merge', 'chain-of-verification', 'checklists', 'circle-of-competence', 'cognitive-dissonance', 'commitment-bias', 'confidence-calibration', 'constraints', 'constructive-feedback-models', 'critical-mass', 'cultural-intelligence', 'curse-of-knowledge', 'decision-trees', 'dunning-kruger-effect', 'emotional-intelligence', 'expertise-reversal-effect', 'false-precision-avoidance', 'feedback-loops', 'feynman-technique', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'internal-locus-of-control', 'inversion', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'liking-principle', 'mental-simulation', 'moral-hazard', 'obligations-controls-mapping', 'occams-razor', 'opportunity-cost', 'optimism-bias-and-planning-fallacy', 'optionality', 'premortem', 'probabilistic-thinking', 'prospect-theory', 'psychological-safety', 'rationalization', 'regression-to-the-mean', 'regulatory-horizon-scanning', 'representativeness-heuristic', 'root-cause-analysis', 'second-order-thinking', 'social-proof', 'specialization', 'survivorship-bias', 'time-tested-validation', 'trade-offs', 'wysiati']
- `20260426T143234Zstab1`: ['abstraction', 'active-listening', 'aleatory-epistemic-uncertainty-recognition', 'authenticity', 'authority-bias', 'bayesian', 'bias-blind-spot', 'boundaries', 'branch-solve-merge', 'chain-of-verification', 'checklists', 'cognitive-dissonance', 'combinatorial-effects', 'commitment-bias', 'confidence-calibration', 'critical-mass', 'cultural-intelligence', 'curse-of-knowledge', 'decision-trees', 'dunning-kruger-effect', 'emotional-intelligence', 'expertise-reversal-effect', 'false-precision-avoidance', 'feedback-loops', 'feynman-technique', 'five-whys-method', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'internal-locus-of-control', 'inversion', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'margin-of-safety', 'mental-simulation', 'obligations-controls-mapping', 'occams-razor', 'opportunity-cost', 'optimism-bias-and-planning-fallacy', 'optionality', 'principal-agent-problem', 'probabilistic-thinking', 'prospect-theory', 'rationalization', 'reasoning-mode-router', 'regression-to-the-mean', 'regulatory-horizon-scanning', 'representativeness-heuristic', 'risk-assessment', 'root-cause-analysis', 'second-order-thinking', 'social-proof', 'specialization', 'step-back', 'sunk-cost-fallacy', 'survivorship-bias', 'trade-offs', 'wysiati']
- `20260426T143344Zstab2`: ['abstraction', 'active-listening', 'aleatory-epistemic-uncertainty-recognition', 'authenticity', 'authority-bias', 'base-rates', 'bayesian', 'bias-blind-spot', 'boundaries', 'branch-solve-merge', 'chain-of-verification', 'checklists', 'circle-of-competence', 'cognitive-dissonance', 'commitment-bias', 'confidence-calibration', 'constructive-feedback-models', 'critical-mass', 'cultural-intelligence', 'curse-of-knowledge', 'decision-trees', 'dunning-kruger-effect', 'emotional-intelligence', 'expertise-reversal-effect', 'false-precision-avoidance', 'feedback-loops', 'feynman-technique', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'internal-locus-of-control', 'inversion', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'liking-principle', 'mental-simulation', 'moral-hazard', 'obligations-controls-mapping', 'occams-razor', 'opportunity-cost', 'optimism-bias-and-planning-fallacy', 'optionality', 'premortem', 'probabilistic-thinking', 'prospect-theory', 'psychological-safety', 'rationalization', 'regression-to-the-mean', 'regulatory-horizon-scanning', 'representativeness-heuristic', 'root-cause-analysis', 'second-order-thinking', 'social-proof', 'specialization', 'survivorship-bias', 'time-tested-validation', 'tradition-vs-innovation-balance', 'wysiati']

### Lane 2 accepted (pre-cap)
- `20260426T143127Zstab0`: ['authority-bias', 'base-rates', 'confidence-calibration', 'occams-razor', 'probabilistic-thinking']
- `20260426T143234Zstab1`: ['authority-bias', 'chain-of-verification', 'confidence-calibration', 'obligations-controls-mapping', 'probabilistic-thinking', 'second-order-thinking']
- `20260426T143344Zstab2`: ['authority-bias', 'bayesian', 'chain-of-verification', 'confidence-calibration', 'probabilistic-thinking']

### Lane 2 detected (post-cap)
- `20260426T143127Zstab0`: ['authority-bias', 'base-rates', 'confidence-calibration', 'occams-razor', 'probabilistic-thinking']
- `20260426T143234Zstab1`: ['authority-bias', 'chain-of-verification', 'obligations-controls-mapping', 'probabilistic-thinking', 'second-order-thinking']
- `20260426T143344Zstab2`: ['authority-bias', 'bayesian', 'chain-of-verification', 'confidence-calibration', 'probabilistic-thinking']

### Lane 2 capped (top-5 drops)
- `20260426T143127Zstab0`: []
- `20260426T143234Zstab1`: []
- `20260426T143344Zstab2`: []

### Lane 2 cheat-sheet anchors
- `20260426T143127Zstab0`: ['authority-bias', 'base-rates', 'confidence-calibration', 'occams-razor', 'probabilistic-thinking']
- `20260426T143234Zstab1`: ['authority-bias', 'chain-of-verification', 'obligations-controls-mapping', 'probabilistic-thinking', 'second-order-thinking']
- `20260426T143344Zstab2`: ['authority-bias', 'bayesian', 'chain-of-verification', 'confidence-calibration', 'probabilistic-thinking']

### Lane 3 reframings
- `20260426T143127Zstab0`: ['brainstorming', 'decision-trees']
- `20260426T143234Zstab1`: ['second-order-thinking', 'trade-offs']
- `20260426T143344Zstab2`: ['decision-trees', 'optionality']

### Lane 4 gap dims
- `20260426T143127Zstab0`: ['commitment-reversibility', 'incentive-alignment', 'resource-allocation', 'risk-response', 'stakeholder-alignment']
- `20260426T143234Zstab1`: ['commitment-reversibility', 'risk-response', 'stakeholder-alignment']
- `20260426T143344Zstab2`: ['commitment-reversibility', 'risk-response', 'stakeholder-alignment']

## Cost per run (boundary-call tokens, lower bound when embeddings on)

| Run | Calls | Prompt tok | Completion tok | Total tok | Embedding-expansion observed |
|---|---|---|---|---|---|
| `20260426T143127Zstab0` | 21 | 113602 | 7626 | 121228 | 0 |
| `20260426T143234Zstab1` | 22 | 117929 | 7774 | 125703 | 0 |
| `20260426T143344Zstab2` | 21 | 113419 | 7001 | 120420 | 0 |

> Embedding-expansion calls (gpt-4o-mini, temp=0.7) bypass `BoundaryClient` tracing — reported here as 0 with a caveat. Treat boundary_only totals as a lower bound on Lane 2 cost when `embedding_mode = on`.

### Per-stage boundary token cost

#### `20260426T143127Zstab0`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 5151 |
| companion_verification_shard_0 | 1 | 8229 |
| companion_verification_shard_1 | 1 | 8456 |
| companion_verification_shard_2 | 1 | 8098 |
| frame_extraction | 1 | 5652 |
| frame_reframing | 1 | 1275 |
| pass1_cluster_authority | 1 | 5947 |
| pass1_cluster_availability | 1 | 5527 |
| pass1_cluster_closure | 1 | 5798 |
| pass1_cluster_incentive | 1 | 5579 |
| pass1_cluster_residual | 1 | 5570 |
| pass1_cluster_self_regard | 1 | 5614 |
| pass2 | 7 | 40344 |
| structural_coverage_classification | 1 | 4994 |
| structural_coverage_detection | 1 | 4994 |

#### `20260426T143234Zstab1`

| Stage | Calls | Total tok |
|---|---|---|
| companion_calibrator | 1 | 4513 |
| companion_fingerprint | 1 | 5231 |
| companion_verification_shard_0 | 1 | 8309 |
| companion_verification_shard_1 | 1 | 8315 |
| companion_verification_shard_2 | 1 | 8650 |
| frame_extraction | 1 | 5632 |
| frame_reframing | 1 | 1104 |
| pass1_cluster_authority | 1 | 5985 |
| pass1_cluster_availability | 1 | 5536 |
| pass1_cluster_closure | 1 | 5781 |
| pass1_cluster_incentive | 1 | 5581 |
| pass1_cluster_residual | 1 | 5570 |
| pass1_cluster_self_regard | 1 | 5614 |
| pass2 | 7 | 40376 |
| structural_coverage_classification | 1 | 4753 |
| structural_coverage_detection | 1 | 4753 |

#### `20260426T143344Zstab2`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 5143 |
| companion_verification_shard_0 | 1 | 8091 |
| companion_verification_shard_1 | 1 | 8124 |
| companion_verification_shard_2 | 1 | 8063 |
| frame_extraction | 1 | 5654 |
| frame_reframing | 1 | 1488 |
| pass1_cluster_authority | 1 | 5972 |
| pass1_cluster_availability | 1 | 5536 |
| pass1_cluster_closure | 1 | 5777 |
| pass1_cluster_incentive | 1 | 5591 |
| pass1_cluster_residual | 1 | 5570 |
| pass1_cluster_self_regard | 1 | 5614 |
| pass2 | 7 | 40385 |
| structural_coverage_classification | 1 | 4706 |
| structural_coverage_detection | 1 | 4706 |
