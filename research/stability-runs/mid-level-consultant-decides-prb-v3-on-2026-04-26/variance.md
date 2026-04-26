# Stability report — mid-level-consultant-decides-prb-v3-on

Generated: 2026-04-26T13:48:31Z
Runs: 3
Run IDs: 20260426T134831Zstab0, 20260426T134946Zstab1, 20260426T135059Zstab2
Prompt versions consistent across runs: True

## Per-stage stability (Jaccard)

> 1.0 is a WARNING, not a target — signals a specialist that stopped doing semantic judgment. Acceptance is a threshold band: stability moved up from baseline, no neighboring stage regressed, qualitative review confirms cards still do structural work.

| Stage | Mean | Min | Max |
|---|---|---|---|
| Pass 1 (tendencies) | 1.00 | 1.00 | 1.00 |
| Lane 2 — fingerprint moves | 0.00 | 0.00 | 0.00 |
| Lane 2 — recalled candidates | 0.79 | 0.74 | 0.90 |
| Lane 2 — accepted (pre-cap) | 0.28 | 0.22 | 0.36 |
| Lane 2 — shared-avail. accept agreement | 0.31 | 0.29 | 0.36 |
| Lane 2 — detected (post-cap) | 0.18 | 0.14 | 0.25 |
| Lane 2 — capped (top-5 drops) | 0.22 | 0.00 | 0.67 |
| Lane 2 (cheat-sheet anchors) | 0.18 | 0.14 | 0.25 |
| Lane 3 (reframings) | 0.33 | 0.33 | 0.33 |
| Lane 4 (gap dims) | 0.73 | 0.60 | 1.00 |

Embedding mode per run: ['on', 'on', 'on']  ·  consistent: True

### Recall-source distribution per run

| Run | keyword | embedding | both | other |
|---|---|---|---|---|
| `20260426T134831Zstab0` | 60 | 0 | 0 | 0 |
| `20260426T134946Zstab1` | 60 | 0 | 0 | 0 |
| `20260426T135059Zstab2` | 60 | 0 | 0 | 0 |

## Step 6 anchor naming (per-run)

| Run | Named | Total | Rate |
|---|---|---|---|
| `20260426T134831Zstab0` | (no revised_answer) | — | — |
| `20260426T134946Zstab1` | (no revised_answer) | — | — |
| `20260426T135059Zstab2` | (no revised_answer) | — | — |

## Per-run item diff

### Pass 1 tendencies
- `20260426T134831Zstab0`: ['authority-misinfluence-tendency', 'reward-and-punishment-superresponse-tendency']
- `20260426T134946Zstab1`: ['authority-misinfluence-tendency', 'reward-and-punishment-superresponse-tendency']
- `20260426T135059Zstab2`: ['authority-misinfluence-tendency', 'reward-and-punishment-superresponse-tendency']

### Lane 2 fingerprint moves
- `20260426T134831Zstab0`: ['apply conditional filter criteria to compare internal vs. external reporting paths', 'assess evidential strength by probing for specifics to determine decision weight', 'isolate current obligation from extraneous prior events to focus decision scope', 'quantify confidence threshold to select optimal reporting strategy', 'sequence immediate actions into prioritized timeline minimizing exposure', 'structure decision into balanced multi-dimensional framework of risks and stakes', 'weigh likelihood of obstruction against benign alternatives based on contextual factors']
- `20260426T134946Zstab1`: ['assess evidential strength by probing for specific details to determine decision weight', 'compare internal vs external reporting using conditional filters based on independence, track record, and urgency', "isolate current obligation from others' past decisions to avoid decision paralysis", 'quantify confidence threshold to select optimal reporting path', 'sequence immediate actions into prioritized timeline to minimize exposure', 'structure decision into balanced multi-dimensional framework of legal, career, and moral risks', 'weigh probability of obstruction against benign alternatives based on contextual factors']
- `20260426T135059Zstab2`: ['apply conditional filter to compare internal vs. external reporting based on leadership independence, firm track record, and urgency', 'assess evidential strength by probing for confirmatory details to determine decision weight', 'evaluate evidence against benign alternatives to gauge likelihood of misconduct', 'frame decision as multi-dimensional trade-off between legal risk, career cost, and moral imperative', 'isolate current obligation from secondary concerns to prioritize primary action', 'sequence immediate actions into prioritized timeline to operationalize decision while minimizing detection risk', 'set probabilistic threshold on confidence in internal handling to recommend path']

### Lane 2 recalled candidates
- `20260426T134831Zstab0`: ['abstraction', 'active-listening', 'aleatory-epistemic-uncertainty-recognition', 'authenticity', 'authority-bias', 'base-rates', 'bayesian', 'bias-blind-spot', 'black-swan-events', 'boundaries', 'branch-solve-merge', 'calculated-risk-taking', 'chain-of-verification', 'checklists', 'cognitive-dissonance', 'combinatorial-effects', 'commitment-bias', 'confidence-calibration', 'constructive-feedback-models', 'critical-mass', 'cultural-intelligence', 'curse-of-knowledge', 'dunning-kruger-effect', 'emotional-intelligence', 'expertise-reversal-effect', 'false-precision-avoidance', 'feedback-loops', 'feynman-technique', 'five-whys-method', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'internal-locus-of-control', 'inversion', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'margin-of-safety', 'mental-simulation', 'obligations-controls-mapping', 'occams-razor', 'opportunity-cost', 'optimism-bias-and-planning-fallacy', 'optionality', 'probabilistic-thinking', 'prospect-theory', 'rationalization', 'regression-to-the-mean', 'regulatory-horizon-scanning', 'representativeness-heuristic', 'root-cause-analysis', 'second-order-thinking', 'social-proof', 'specialization', 'step-back', 'sunk-cost-fallacy', 'survivorship-bias', 'trade-offs', 'wysiati']
- `20260426T134946Zstab1`: ['abstraction', 'active-listening', 'aleatory-epistemic-uncertainty-recognition', 'authenticity', 'authority-bias', 'base-rates', 'bayesian', 'bias-blind-spot', 'black-swan-events', 'boundaries', 'branch-solve-merge', 'chain-of-thought', 'chain-of-verification', 'checklists', 'circle-of-competence', 'cognitive-dissonance', 'combinatorial-effects', 'commitment-bias', 'confidence-calibration', 'constructive-feedback-models', 'critical-mass', 'cultural-intelligence', 'curse-of-knowledge', 'dunning-kruger-effect', 'emotional-intelligence', 'expertise-reversal-effect', 'false-precision-avoidance', 'feedback-loops', 'feynman-technique', 'five-whys-method', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'internal-locus-of-control', 'inversion', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'margin-of-safety', 'mental-simulation', 'obligations-controls-mapping', 'occams-razor', 'opportunity-cost', 'optionality', 'probabilistic-thinking', 'prospect-theory', 'rationalization', 'reasoning-mode-router', 'regression-to-the-mean', 'regulatory-horizon-scanning', 'representativeness-heuristic', 'root-cause-analysis', 'second-order-thinking', 'social-proof', 'specialization', 'step-back', 'sunk-cost-fallacy', 'trade-offs', 'wysiati']
- `20260426T135059Zstab2`: ['active-listening', 'aleatory-epistemic-uncertainty-recognition', 'authenticity', 'authority-bias', 'base-rates', 'bayesian', 'bias-blind-spot', 'boundaries', 'branch-solve-merge', 'calculated-risk-taking', 'chain-of-thought', 'chain-of-verification', 'checklists', 'cognitive-dissonance', 'commitment-bias', 'confidence-calibration', 'constructive-feedback-models', 'critical-mass', 'cultural-intelligence', 'dunning-kruger-effect', 'emotional-intelligence', 'expertise-reversal-effect', 'false-precision-avoidance', 'feedback-loops', 'feynman-technique', 'five-whys-method', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'inversion', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'liking-principle', 'mental-simulation', 'moral-hazard', 'obligations-controls-mapping', 'opportunity-cost', 'optionality', 'premortem', 'probabilistic-thinking', 'prospect-theory', 'psychological-safety', 'rationalization', 'reasoning-mode-router', 'regression-to-the-mean', 'regulatory-horizon-scanning', 'representativeness-heuristic', 'root-cause-analysis', 'scientific-method-evidence-testing', 'second-order-thinking', 'social-proof', 'specialization', 'sunk-cost-fallacy', 'survivorship-bias', 'time-tested-validation', 'trade-offs', 'user-centered-design', 'wysiati']

### Lane 2 accepted (pre-cap)
- `20260426T134831Zstab0`: ['base-rates', 'boundaries', 'chain-of-verification', 'confidence-calibration', 'information-asymmetry', 'margin-of-safety', 'probabilistic-thinking', 'second-order-thinking']
- `20260426T134946Zstab1`: ['authority-bias', 'base-rates', 'bayesian', 'chain-of-verification', 'confidence-calibration', 'probabilistic-thinking', 'wysiati']
- `20260426T135059Zstab2`: ['chain-of-verification', 'probabilistic-thinking', 'scientific-method-evidence-testing']

### Lane 2 detected (post-cap)
- `20260426T134831Zstab0`: ['base-rates', 'boundaries', 'information-asymmetry', 'probabilistic-thinking', 'second-order-thinking']
- `20260426T134946Zstab1`: ['authority-bias', 'base-rates', 'bayesian', 'probabilistic-thinking', 'wysiati']
- `20260426T135059Zstab2`: ['chain-of-verification', 'probabilistic-thinking', 'scientific-method-evidence-testing']

### Lane 2 capped (top-5 drops)
- `20260426T134831Zstab0`: ['chain-of-verification', 'confidence-calibration', 'margin-of-safety']
- `20260426T134946Zstab1`: ['chain-of-verification', 'confidence-calibration']
- `20260426T135059Zstab2`: []

### Lane 2 cheat-sheet anchors
- `20260426T134831Zstab0`: ['base-rates', 'boundaries', 'information-asymmetry', 'probabilistic-thinking', 'second-order-thinking']
- `20260426T134946Zstab1`: ['authority-bias', 'base-rates', 'bayesian', 'probabilistic-thinking', 'wysiati']
- `20260426T135059Zstab2`: ['chain-of-verification', 'probabilistic-thinking', 'scientific-method-evidence-testing']

### Lane 3 reframings
- `20260426T134831Zstab0`: ['decision-trees', 'optionatility']
- `20260426T134946Zstab1`: ['decision-trees', 'optionality']
- `20260426T135059Zstab2`: ['decision-trees', 'multi-criteria-decision-analysis']

### Lane 4 gap dims
- `20260426T134831Zstab0`: ['commitment-reversibility', 'competitive-dynamics', 'incentive-alignment', 'risk-response', 'stakeholder-alignment']
- `20260426T134946Zstab1`: ['commitment-reversibility', 'risk-response', 'stakeholder-alignment']
- `20260426T135059Zstab2`: ['commitment-reversibility', 'risk-response', 'stakeholder-alignment']

## Cost per run (boundary-call tokens, lower bound when embeddings on)

| Run | Calls | Prompt tok | Completion tok | Total tok | Embedding-expansion observed |
|---|---|---|---|---|---|
| `20260426T134831Zstab0` | 21 | 113811 | 7655 | 121466 | 0 |
| `20260426T134946Zstab1` | 21 | 113667 | 7247 | 120914 | 0 |
| `20260426T135059Zstab2` | 21 | 113637 | 7385 | 121022 | 0 |

> Embedding-expansion calls (gpt-4o-mini, temp=0.7) bypass `BoundaryClient` tracing — reported here as 0 with a caveat. Treat boundary_only totals as a lower bound on Lane 2 cost when `embedding_mode = on`.

### Per-stage boundary token cost

#### `20260426T134831Zstab0`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 5188 |
| companion_verification_shard_0 | 1 | 8297 |
| companion_verification_shard_1 | 1 | 8338 |
| companion_verification_shard_2 | 1 | 8240 |
| frame_extraction | 1 | 5653 |
| frame_reframing | 1 | 1306 |
| pass1_cluster_authority | 1 | 5982 |
| pass1_cluster_availability | 1 | 5538 |
| pass1_cluster_closure | 1 | 5777 |
| pass1_cluster_incentive | 1 | 5572 |
| pass1_cluster_residual | 1 | 5570 |
| pass1_cluster_self_regard | 1 | 5614 |
| pass2 | 7 | 40391 |
| structural_coverage_classification | 1 | 5000 |
| structural_coverage_detection | 1 | 5000 |

#### `20260426T134946Zstab1`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 5191 |
| companion_verification_shard_0 | 1 | 8605 |
| companion_verification_shard_1 | 1 | 8245 |
| companion_verification_shard_2 | 1 | 7984 |
| frame_extraction | 1 | 5640 |
| frame_reframing | 1 | 1329 |
| pass1_cluster_authority | 1 | 5952 |
| pass1_cluster_availability | 1 | 5540 |
| pass1_cluster_closure | 1 | 5766 |
| pass1_cluster_incentive | 1 | 5606 |
| pass1_cluster_residual | 1 | 5570 |
| pass1_cluster_self_regard | 1 | 5614 |
| pass2 | 7 | 40368 |
| structural_coverage_classification | 1 | 4752 |
| structural_coverage_detection | 1 | 4752 |

#### `20260426T135059Zstab2`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 5248 |
| companion_verification_shard_0 | 1 | 8564 |
| companion_verification_shard_1 | 1 | 8036 |
| companion_verification_shard_2 | 1 | 8170 |
| frame_extraction | 1 | 5653 |
| frame_reframing | 1 | 1430 |
| pass1_cluster_authority | 1 | 5986 |
| pass1_cluster_availability | 1 | 5541 |
| pass1_cluster_closure | 1 | 5754 |
| pass1_cluster_incentive | 1 | 5573 |
| pass1_cluster_residual | 1 | 5570 |
| pass1_cluster_self_regard | 1 | 5614 |
| pass2 | 7 | 40317 |
| structural_coverage_classification | 1 | 4783 |
| structural_coverage_detection | 1 | 4783 |
