# Stability report — mid-level-consultant-decides-prb-on

Generated: 2026-04-26T12:24:50Z
Runs: 3
Run IDs: 20260426T122450Zstab0, 20260426T122558Zstab1, 20260426T122710Zstab2
Prompt versions consistent across runs: True

## Per-stage stability (Jaccard)

> 1.0 is a WARNING, not a target — signals a specialist that stopped doing semantic judgment. Acceptance is a threshold band: stability moved up from baseline, no neighboring stage regressed, qualitative review confirms cards still do structural work.

| Stage | Mean | Min | Max |
|---|---|---|---|
| Pass 1 (tendencies) | 1.00 | 1.00 | 1.00 |
| Lane 2 — fingerprint moves | 0.06 | 0.00 | 0.17 |
| Lane 2 — recalled candidates | 0.75 | 0.71 | 0.79 |
| Lane 2 — accepted (pre-cap) | 0.65 | 0.50 | 0.92 |
| Lane 2 — shared-avail. accept agreement | 0.69 | 0.56 | 0.92 |
| Lane 2 — detected (post-cap) | 0.39 | 0.25 | 0.67 |
| Lane 2 — capped (top-5 drops) | 0.58 | 0.42 | 0.86 |
| Lane 2 (cheat-sheet anchors) | 0.39 | 0.25 | 0.67 |
| Lane 3 (reframings) | 0.33 | 0.33 | 0.33 |
| Lane 4 (gap dims) | 0.60 | 0.40 | 1.00 |

Embedding mode per run: ['on', 'on', 'on']  ·  consistent: True

### Recall-source distribution per run

| Run | keyword | embedding | both | other |
|---|---|---|---|---|
| `20260426T122450Zstab0` | 60 | 0 | 0 | 0 |
| `20260426T122558Zstab1` | 60 | 0 | 0 | 0 |
| `20260426T122710Zstab2` | 60 | 0 | 0 | 0 |

## Step 6 anchor naming (per-run)

| Run | Named | Total | Rate |
|---|---|---|---|
| `20260426T122450Zstab0` | (no revised_answer) | — | — |
| `20260426T122558Zstab1` | (no revised_answer) | — | — |
| `20260426T122710Zstab2` | (no revised_answer) | — | — |

## Per-run item diff

### Pass 1 tendencies
- `20260426T122450Zstab0`: ['authority-misinfluence-tendency', 'reward-and-punishment-superresponse-tendency']
- `20260426T122558Zstab1`: ['authority-misinfluence-tendency', 'reward-and-punishment-superresponse-tendency']
- `20260426T122710Zstab2`: ['authority-misinfluence-tendency', 'reward-and-punishment-superresponse-tendency']

### Lane 2 fingerprint moves
- `20260426T122450Zstab0`: ['apply conditional filter criteria to compare internal vs. external reporting paths', 'assess evidential strength by probing for confirmatory details to determine decision weight', 'evaluate evidence against benign alternatives to gauge likelihood of misconduct', 'isolate current obligation from extraneous prior actors to focus decision scope', 'sequence preparatory and protective actions into timed timeline', 'structure decision as multi-dimensional tradeoff of legal, career, and moral risks', 'threshold confidence calibration to select optimal reporting channel']
- `20260426T122558Zstab1`: ['apply threshold-based decision rule integrating live confidence level and situational factors', 'assess evidential strength by probing for specifics to determine decision weight', 'compare internal vs external reporting using conditional criteria and confidence thresholds', 'isolate current obligation from extraneous concerns to focus decision boundary', 'sequence actions into prioritized timeline minimizing exposure risks', 'structure decision into balanced multi-dimensional framework of risks and stakes', 'weigh likelihood of obstruction against benign explanations based on contextual factors']
- `20260426T122710Zstab2`: ['apply conditional filter to compare internal vs external reporting based on enumerated criteria', 'assess evidential strength by probing for specifics to determine decision weight', "isolate user's obligation by compartmentalizing unrelated prior events", 'sequence prioritized actions with timeline and rationale for normalcy preservation', 'structure decision into balanced multi-dimensional framework of risks and stakes', 'threshold confidence assessment to select optimal reporting path', 'weigh evidence against benign alternatives while acknowledging ambiguity']

### Lane 2 recalled candidates
- `20260426T122450Zstab0`: ['abstraction', 'active-listening', 'aleatory-epistemic-uncertainty-recognition', 'anchoring', 'authenticity', 'authority-bias', 'base-rates', 'bayesian', 'bias-blind-spot', 'boundaries', 'branch-solve-merge', 'chain-of-thought', 'chain-of-verification', 'checklists', 'circle-of-competence', 'cognitive-dissonance', 'combinatorial-effects', 'commitment-bias', 'confidence-calibration', 'constructive-feedback-models', 'critical-mass', 'cultural-intelligence', 'dunning-kruger-effect', 'emotional-intelligence', 'expertise-reversal-effect', 'false-precision-avoidance', 'feedback-loops', 'feynman-technique', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'inversion', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'liking-principle', 'mental-simulation', 'obligations-controls-mapping', 'occams-razor', 'opportunity-cost', 'optionality', 'probabilistic-thinking', 'prospect-theory', 'rationalization', 'reasoning-mode-router', 'regression-to-the-mean', 'regulatory-horizon-scanning', 'representativeness-heuristic', 'root-cause-analysis', 'second-order-thinking', 'social-proof', 'specialization', 'sunk-cost-fallacy', 'survivorship-bias', 'time-tested-validation', 'trade-offs', 'tradition-vs-innovation-balance', 'understanding-motivations', 'wysiati']
- `20260426T122558Zstab1`: ['abstraction', 'active-listening', 'aleatory-epistemic-uncertainty-recognition', 'authenticity', 'authority-bias', 'base-rates', 'bayesian', 'bias-blind-spot', 'boundaries', 'branch-solve-merge', 'calculated-risk-taking', 'chain-of-verification', 'checklists', 'circle-of-competence', 'cognitive-dissonance', 'combinatorial-effects', 'commitment-bias', 'confidence-calibration', 'constructive-feedback-models', 'critical-mass', 'cultural-intelligence', 'curse-of-knowledge', 'decision-trees', 'dunning-kruger-effect', 'emotional-intelligence', 'expertise-reversal-effect', 'false-precision-avoidance', 'feedback-loops', 'feynman-technique', 'formal-reasoning', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'inversion', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'margin-of-safety', 'mental-simulation', 'obligations-controls-mapping', 'occams-razor', 'opportunity-cost', 'optimism-bias-and-planning-fallacy', 'principal-agent-problem', 'probabilistic-thinking', 'prospect-theory', 'rationalization', 'regression-to-the-mean', 'regulatory-horizon-scanning', 'representativeness-heuristic', 'risk-assessment', 'root-cause-analysis', 'second-order-thinking', 'social-proof', 'specialization', 'step-back', 'sunk-cost-fallacy', 'trade-offs', 'wysiati']
- `20260426T122710Zstab2`: ['active-listening', 'agile-methodologies', 'aleatory-epistemic-uncertainty-recognition', 'anchoring', 'authenticity', 'authority-bias', 'base-rates', 'bayesian', 'bias-blind-spot', 'boundaries', 'branch-solve-merge', 'calculated-risk-taking', 'chain-of-thought', 'chain-of-verification', 'checklists', 'cognitive-dissonance', 'combinatorial-effects', 'commitment-bias', 'confidence-calibration', 'constructive-feedback-models', 'critical-mass', 'cultural-intelligence', 'curse-of-knowledge', 'dunning-kruger-effect', 'emotional-intelligence', 'experimentation', 'expertise-reversal-effect', 'false-precision-avoidance', 'feedback-loops', 'feynman-technique', 'five-whys-method', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'inversion', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'liking-principle', 'mental-simulation', 'obligations-controls-mapping', 'occams-razor', 'opportunity-cost', 'optionality', 'principal-agent-problem', 'probabilistic-thinking', 'prospect-theory', 'reasoning-mode-router', 'regression-to-the-mean', 'regulatory-horizon-scanning', 'representativeness-heuristic', 'root-cause-analysis', 'schema-acquisition', 'second-order-thinking', 'social-proof', 'specialization', 'sunk-cost-fallacy', 'tradition-vs-innovation-balance', 'wysiati']

### Lane 2 accepted (pre-cap)
- `20260426T122450Zstab0`: ['aleatory-epistemic-uncertainty-recognition', 'authority-bias', 'base-rates', 'boundaries', 'chain-of-verification', 'confidence-calibration', 'intellectual-humility', 'obligations-controls-mapping', 'probabilistic-thinking', 'second-order-thinking', 'wysiati']
- `20260426T122558Zstab1`: ['aleatory-epistemic-uncertainty-recognition', 'authority-bias', 'base-rates', 'boundaries', 'chain-of-verification', 'confidence-calibration', 'information-asymmetry', 'intellectual-humility', 'obligations-controls-mapping', 'probabilistic-thinking', 'second-order-thinking', 'wysiati']
- `20260426T122710Zstab2`: ['aleatory-epistemic-uncertainty-recognition', 'anchoring', 'authority-bias', 'base-rates', 'chain-of-verification', 'confidence-calibration', 'five-whys-method', 'game-theory-payoffs', 'intellectual-humility', 'inversion', 'mental-simulation', 'principal-agent-problem', 'probabilistic-thinking', 'second-order-thinking', 'wysiati']

### Lane 2 detected (post-cap)
- `20260426T122450Zstab0`: ['aleatory-epistemic-uncertainty-recognition', 'boundaries', 'obligations-controls-mapping', 'probabilistic-thinking', 'second-order-thinking']
- `20260426T122558Zstab1`: ['aleatory-epistemic-uncertainty-recognition', 'information-asymmetry', 'obligations-controls-mapping', 'probabilistic-thinking', 'second-order-thinking']
- `20260426T122710Zstab2`: ['aleatory-epistemic-uncertainty-recognition', 'game-theory-payoffs', 'intellectual-humility', 'mental-simulation', 'second-order-thinking']

### Lane 2 capped (top-5 drops)
- `20260426T122450Zstab0`: ['authority-bias', 'base-rates', 'chain-of-verification', 'confidence-calibration', 'intellectual-humility', 'wysiati']
- `20260426T122558Zstab1`: ['authority-bias', 'base-rates', 'boundaries', 'chain-of-verification', 'confidence-calibration', 'intellectual-humility', 'wysiati']
- `20260426T122710Zstab2`: ['anchoring', 'authority-bias', 'base-rates', 'chain-of-verification', 'confidence-calibration', 'five-whys-method', 'inversion', 'principal-agent-problem', 'probabilistic-thinking', 'wysiati']

### Lane 2 cheat-sheet anchors
- `20260426T122450Zstab0`: ['aleatory-epistemic-uncertainty-recognition', 'boundaries', 'obligations-controls-mapping', 'probabilistic-thinking', 'second-order-thinking']
- `20260426T122558Zstab1`: ['aleatory-epistemic-uncertainty-recognition', 'information-asymmetry', 'obligations-controls-mapping', 'probabilistic-thinking', 'second-order-thinking']
- `20260426T122710Zstab2`: ['aleatory-epistemic-uncertainty-recognition', 'game-theory-payoffs', 'intellectual-humility', 'mental-simulation', 'second-order-thinking']

### Lane 3 reframings
- `20260426T122450Zstab0`: ['decision-trees', 'peer-review-your-perspectives']
- `20260426T122558Zstab1`: ['decision-trees', 'optionality']
- `20260426T122710Zstab2`: ['decision-trees', 'trade-offs']

### Lane 4 gap dims
- `20260426T122450Zstab0`: ['competitive-dynamics', 'information-quality', 'uncertainty-type']
- `20260426T122558Zstab1`: ['competitive-dynamics', 'incentive-alignment', 'stakeholder-alignment', 'uncertainty-type']
- `20260426T122710Zstab2`: ['competitive-dynamics', 'incentive-alignment', 'stakeholder-alignment', 'uncertainty-type']

## Cost per run (boundary-call tokens, lower bound when embeddings on)

| Run | Calls | Prompt tok | Completion tok | Total tok | Embedding-expansion observed |
|---|---|---|---|---|---|
| `20260426T122450Zstab0` | 27 | 144494 | 7599 | 152093 | 0 |
| `20260426T122558Zstab1` | 27 | 145718 | 8538 | 154256 | 0 |
| `20260426T122710Zstab2` | 27 | 150452 | 9027 | 159479 | 0 |

> Embedding-expansion calls (gpt-4o-mini, temp=0.7) bypass `BoundaryClient` tracing — reported here as 0 with a caveat. Treat boundary_only totals as a lower bound on Lane 2 cost when `embedding_mode = on`.

### Per-stage boundary token cost

#### `20260426T122450Zstab0`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 5101 |
| companion_verification_analogical | 1 | 5736 |
| companion_verification_causal | 1 | 6189 |
| companion_verification_counterfactual | 1 | 6164 |
| companion_verification_deductive | 1 | 6041 |
| companion_verification_diagnostic | 1 | 7263 |
| companion_verification_metacognitive | 1 | 6591 |
| companion_verification_probabilistic | 1 | 6255 |
| companion_verification_systems | 1 | 6318 |
| frame_extraction | 1 | 5656 |
| frame_reframing | 1 | 1354 |
| pass1_cluster_authority | 1 | 5951 |
| pass1_cluster_availability | 1 | 5538 |
| pass1_cluster_closure | 1 | 5782 |
| pass1_cluster_incentive | 1 | 5580 |
| pass1_cluster_residual | 1 | 5570 |
| pass1_cluster_self_regard | 1 | 5658 |
| pass2 | 8 | 45864 |
| structural_coverage_classification | 1 | 4741 |
| structural_coverage_detection | 1 | 4741 |

#### `20260426T122558Zstab1`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 5229 |
| companion_verification_analogical | 1 | 5933 |
| companion_verification_causal | 1 | 6279 |
| companion_verification_counterfactual | 1 | 6304 |
| companion_verification_deductive | 1 | 6541 |
| companion_verification_diagnostic | 1 | 7120 |
| companion_verification_metacognitive | 1 | 6833 |
| companion_verification_probabilistic | 1 | 6455 |
| companion_verification_systems | 1 | 6847 |
| frame_extraction | 1 | 5647 |
| frame_reframing | 1 | 1417 |
| pass1_cluster_authority | 1 | 5950 |
| pass1_cluster_availability | 1 | 5538 |
| pass1_cluster_closure | 1 | 5786 |
| pass1_cluster_incentive | 1 | 5600 |
| pass1_cluster_residual | 1 | 5570 |
| pass1_cluster_self_regard | 1 | 5614 |
| pass2 | 8 | 45863 |
| structural_coverage_classification | 1 | 4865 |
| structural_coverage_detection | 1 | 4865 |

#### `20260426T122710Zstab2`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 5844 |
| companion_verification_analogical | 1 | 6560 |
| companion_verification_causal | 1 | 7294 |
| companion_verification_counterfactual | 1 | 6807 |
| companion_verification_deductive | 1 | 6967 |
| companion_verification_diagnostic | 1 | 7767 |
| companion_verification_metacognitive | 1 | 7306 |
| companion_verification_probabilistic | 1 | 7097 |
| companion_verification_systems | 1 | 7211 |
| frame_extraction | 1 | 5636 |
| frame_reframing | 1 | 1336 |
| pass1_cluster_authority | 1 | 5963 |
| pass1_cluster_availability | 1 | 5538 |
| pass1_cluster_closure | 1 | 5777 |
| pass1_cluster_incentive | 1 | 5578 |
| pass1_cluster_residual | 1 | 5570 |
| pass1_cluster_self_regard | 1 | 5614 |
| pass2 | 8 | 45872 |
| structural_coverage_classification | 1 | 4871 |
| structural_coverage_detection | 1 | 4871 |
