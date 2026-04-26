# Stability report — mid-level-consultant-decides-prb-v2-on

Generated: 2026-04-26T13:08:52Z
Runs: 3
Run IDs: 20260426T130852Zstab0, 20260426T131024Zstab1, 20260426T131135Zstab2
Prompt versions consistent across runs: True

## Per-stage stability (Jaccard)

> 1.0 is a WARNING, not a target — signals a specialist that stopped doing semantic judgment. Acceptance is a threshold band: stability moved up from baseline, no neighboring stage regressed, qualitative review confirms cards still do structural work.

| Stage | Mean | Min | Max |
|---|---|---|---|
| Pass 1 (tendencies) | 1.00 | 1.00 | 1.00 |
| Lane 2 — fingerprint moves | 0.11 | 0.08 | 0.17 |
| Lane 2 — recalled candidates | 0.84 | 0.79 | 0.88 |
| Lane 2 — accepted (pre-cap) | 0.33 | 0.27 | 0.43 |
| Lane 2 — shared-avail. accept agreement | 0.34 | 0.27 | 0.46 |
| Lane 2 — detected (post-cap) | 0.26 | 0.11 | 0.43 |
| Lane 2 — capped (top-5 drops) | 0.08 | 0.00 | 0.25 |
| Lane 2 (cheat-sheet anchors) | 0.26 | 0.11 | 0.43 |
| Lane 3 (reframings) | 0.33 | 0.33 | 0.33 |
| Lane 4 (gap dims) | 0.58 | 0.40 | 0.75 |

Embedding mode per run: ['on', 'on', 'on']  ·  consistent: True

### Recall-source distribution per run

| Run | keyword | embedding | both | other |
|---|---|---|---|---|
| `20260426T130852Zstab0` | 60 | 0 | 0 | 0 |
| `20260426T131024Zstab1` | 60 | 0 | 0 | 0 |
| `20260426T131135Zstab2` | 60 | 0 | 0 | 0 |

## Step 6 anchor naming (per-run)

| Run | Named | Total | Rate |
|---|---|---|---|
| `20260426T130852Zstab0` | (no revised_answer) | — | — |
| `20260426T131024Zstab1` | (no revised_answer) | — | — |
| `20260426T131135Zstab2` | (no revised_answer) | — | — |

## Per-run item diff

### Pass 1 tendencies
- `20260426T130852Zstab0`: ['authority-misinfluence-tendency', 'reward-and-punishment-superresponse-tendency']
- `20260426T131024Zstab1`: ['authority-misinfluence-tendency', 'reward-and-punishment-superresponse-tendency']
- `20260426T131135Zstab2`: ['authority-misinfluence-tendency', 'reward-and-punishment-superresponse-tendency']

### Lane 2 fingerprint moves
- `20260426T130852Zstab0`: ['apply conditional filter to compare internal vs external reporting based on trust levels and risks', 'assess evidential strength by probing for specifics to determine decision weight', "isolate current obligation from others' past actions to focus decision scope", 'sequence actions into prioritized timeline minimizing exposure', 'structure decision into balanced dimensions of legal, career, and moral risks', 'threshold confidence calibration to recommend path based on quantified trust in internal handling', 'weigh likelihood of obstruction against benign alternatives based on contextual factors']
- `20260426T131024Zstab1`: ['apply conditional filter to compare internal vs external reporting based on independence, track record, and urgency', 'assess evidential strength by probing for specifics to determine decision weight', 'isolate current obligation from ancillary concerns to focus decision scope', 'sequence actions into prioritized timeline with risk mitigation steps', 'set quantitative confidence threshold to select optimal reporting path', 'structure decision into triadic framework of legal, career, and moral dimensions', 'weigh likelihood of obstruction against benign alternatives based on contextual factors']
- `20260426T131135Zstab2`: ['assess evidential strength by probing for specifics to determine decision weight', 'compare internal vs. external reporting using conditional filter criteria', "isolate user's obligation from others' past actions to avoid decision paralysis", 'quantify confidence threshold to recommend path based on institutional incentives', 'sequence immediate actions into prioritized timeline with rationale for normalcy', 'structure decision into balanced multi-dimensional framework of risks and stakes', 'weigh likelihood of obstruction against benign alternatives based on context']

### Lane 2 recalled candidates
- `20260426T130852Zstab0`: ['abstraction', 'active-listening', 'aleatory-epistemic-uncertainty-recognition', 'authenticity', 'authority-bias', 'base-rates', 'bayesian', 'bias-blind-spot', 'boundaries', 'branch-solve-merge', 'chain-of-thought', 'chain-of-verification', 'checklists', 'cognitive-dissonance', 'combinatorial-effects', 'commitment-bias', 'confidence-calibration', 'constructive-feedback-models', 'critical-mass', 'cultural-intelligence', 'curse-of-knowledge', 'dunning-kruger-effect', 'emotional-intelligence', 'expertise-reversal-effect', 'false-precision-avoidance', 'feedback-loops', 'feynman-technique', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'internal-locus-of-control', 'inversion', 'johari-window', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'liking-principle', 'margin-of-safety', 'mental-simulation', 'obligations-controls-mapping', 'opportunity-cost', 'optionality', 'prisoners-dilemma', 'probabilistic-thinking', 'prospect-theory', 'rationalization', 'reasoning-mode-router', 'reciprocity-principle', 'regression-to-the-mean', 'regulatory-horizon-scanning', 'representativeness-heuristic', 'root-cause-analysis', 'second-order-thinking', 'social-proof', 'specialization', 'sunk-cost-fallacy', 'trade-offs', 'variation-and-selection', 'wysiati']
- `20260426T131024Zstab1`: ['abstraction', 'active-listening', 'aleatory-epistemic-uncertainty-recognition', 'authenticity', 'authority-bias', 'base-rates', 'bayesian', 'bias-blind-spot', 'boundaries', 'branch-solve-merge', 'chain-of-thought', 'chain-of-verification', 'checklists', 'cognitive-dissonance', 'combinatorial-effects', 'commitment-bias', 'confidence-calibration', 'constructive-feedback-models', 'critical-mass', 'cultural-intelligence', 'curse-of-knowledge', 'dunning-kruger-effect', 'emotional-intelligence', 'expertise-reversal-effect', 'false-precision-avoidance', 'feedback-loops', 'feynman-technique', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'internal-locus-of-control', 'inversion', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'liking-principle', 'mental-simulation', 'obligations-controls-mapping', 'occams-razor', 'opportunity-cost', 'optionality', 'principal-agent-problem', 'probabilistic-thinking', 'prospect-theory', 'rationalization', 'reasoning-mode-router', 'regression-to-the-mean', 'regulatory-horizon-scanning', 'representativeness-heuristic', 'root-cause-analysis', 'second-order-thinking', 'social-proof', 'specialization', 'step-back', 'sunk-cost-fallacy', 'survivorship-bias', 'trade-offs', 'variation-and-selection', 'wysiati']
- `20260426T131135Zstab2`: ['abstraction', 'active-listening', 'aleatory-epistemic-uncertainty-recognition', 'authenticity', 'authority-bias', 'base-rates', 'bayesian', 'boundaries', 'branch-solve-merge', 'checklists', 'cognitive-dissonance', 'combinatorial-effects', 'commitment-bias', 'confidence-calibration', 'constructive-feedback-models', 'critical-mass', 'cultural-intelligence', 'curse-of-knowledge', 'dunning-kruger-effect', 'emotional-intelligence', 'expertise-reversal-effect', 'false-precision-avoidance', 'feedback-loops', 'feynman-technique', 'five-whys-method', 'formal-reasoning', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'internal-locus-of-control', 'inversion', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'liking-principle', 'margin-of-safety', 'mental-simulation', 'obligations-controls-mapping', 'occams-razor', 'opportunity-cost', 'optionality', 'principal-agent-problem', 'probabilistic-thinking', 'prospect-theory', 'rationalization', 'reasoning-mode-router', 'regression-to-the-mean', 'regulatory-horizon-scanning', 'representativeness-heuristic', 'root-cause-analysis', 'second-order-thinking', 'social-proof', 'specialization', 'step-back', 'sunk-cost-fallacy', 'trade-offs', 'tradition-vs-innovation-balance', 'understanding-motivations', 'wysiati']

### Lane 2 accepted (pre-cap)
- `20260426T130852Zstab0`: ['abstraction', 'authority-bias', 'boundaries', 'confidence-calibration', 'mental-simulation', 'probabilistic-thinking', 'second-order-thinking', 'wysiati']
- `20260426T131024Zstab1`: ['confidence-calibration', 'intellectual-humility', 'inversion', 'optionality', 'probabilistic-thinking', 'second-order-thinking']
- `20260426T131135Zstab2`: ['abstraction', 'authority-bias', 'confidence-calibration', 'game-theory-payoffs', 'intellectual-humility', 'inversion', 'mental-simulation', 'obligations-controls-mapping', 'principal-agent-problem', 'second-order-thinking', 'trade-offs', 'wysiati']

### Lane 2 detected (post-cap)
- `20260426T130852Zstab0`: ['boundaries', 'confidence-calibration', 'mental-simulation', 'probabilistic-thinking', 'second-order-thinking']
- `20260426T131024Zstab1`: ['confidence-calibration', 'intellectual-humility', 'inversion', 'probabilistic-thinking', 'second-order-thinking']
- `20260426T131135Zstab2`: ['authority-bias', 'game-theory-payoffs', 'inversion', 'obligations-controls-mapping', 'second-order-thinking']

### Lane 2 capped (top-5 drops)
- `20260426T130852Zstab0`: ['abstraction', 'authority-bias', 'wysiati']
- `20260426T131024Zstab1`: ['optionality']
- `20260426T131135Zstab2`: ['abstraction', 'confidence-calibration', 'intellectual-humility', 'mental-simulation', 'principal-agent-problem', 'trade-offs', 'wysiati']

### Lane 2 cheat-sheet anchors
- `20260426T130852Zstab0`: ['boundaries', 'confidence-calibration', 'mental-simulation', 'probabilistic-thinking', 'second-order-thinking']
- `20260426T131024Zstab1`: ['confidence-calibration', 'intellectual-humility', 'inversion', 'probabilistic-thinking', 'second-order-thinking']
- `20260426T131135Zstab2`: ['authority-bias', 'game-theory-payoffs', 'inversion', 'obligations-controls-mapping', 'second-order-thinking']

### Lane 3 reframings
- `20260426T130852Zstab0`: ['counterfactual-reasoning', 'decision-trees']
- `20260426T131024Zstab1`: ['decision-trees', 'optionality']
- `20260426T131135Zstab2`: ['decision-trees', 'second-order-thinking']

### Lane 4 gap dims
- `20260426T130852Zstab0`: ['commitment-reversibility', 'competitive-dynamics', 'incentive-alignment', 'stakeholder-alignment']
- `20260426T131024Zstab1`: ['commitment-reversibility', 'risk-response', 'stakeholder-alignment']
- `20260426T131135Zstab2`: ['commitment-reversibility', 'competitive-dynamics', 'risk-response', 'stakeholder-alignment']

## Cost per run (boundary-call tokens, lower bound when embeddings on)

| Run | Calls | Prompt tok | Completion tok | Total tok | Embedding-expansion observed |
|---|---|---|---|---|---|
| `20260426T130852Zstab0` | 28 | 153694 | 8459 | 162153 | 0 |
| `20260426T131024Zstab1` | 28 | 154274 | 7750 | 162024 | 0 |
| `20260426T131135Zstab2` | 27 | 148377 | 9017 | 157394 | 0 |

> Embedding-expansion calls (gpt-4o-mini, temp=0.7) bypass `BoundaryClient` tracing — reported here as 0 with a caveat. Treat boundary_only totals as a lower bound on Lane 2 cost when `embedding_mode = on`.

### Per-stage boundary token cost

#### `20260426T130852Zstab0`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 5155 |
| companion_verification_abductive | 1 | 5953 |
| companion_verification_analogical | 1 | 5969 |
| companion_verification_causal | 1 | 6451 |
| companion_verification_counterfactual | 1 | 6866 |
| companion_verification_deductive | 1 | 6635 |
| companion_verification_diagnostic | 1 | 7730 |
| companion_verification_metacognitive | 1 | 7276 |
| companion_verification_probabilistic | 1 | 6319 |
| companion_verification_systems | 1 | 7046 |
| frame_extraction | 1 | 5664 |
| frame_reframing | 1 | 1354 |
| pass1_cluster_authority | 1 | 6011 |
| pass1_cluster_availability | 1 | 5536 |
| pass1_cluster_closure | 1 | 5776 |
| pass1_cluster_incentive | 1 | 5598 |
| pass1_cluster_residual | 1 | 5570 |
| pass1_cluster_self_regard | 1 | 5614 |
| pass2 | 8 | 45872 |
| structural_coverage_classification | 1 | 4879 |
| structural_coverage_detection | 1 | 4879 |

#### `20260426T131024Zstab1`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 5232 |
| companion_verification_abductive | 1 | 6025 |
| companion_verification_analogical | 1 | 6406 |
| companion_verification_causal | 1 | 6523 |
| companion_verification_counterfactual | 1 | 6983 |
| companion_verification_deductive | 1 | 6561 |
| companion_verification_diagnostic | 1 | 7204 |
| companion_verification_metacognitive | 1 | 7459 |
| companion_verification_probabilistic | 1 | 6485 |
| companion_verification_systems | 1 | 6842 |
| frame_extraction | 1 | 5645 |
| frame_reframing | 1 | 1334 |
| pass1_cluster_authority | 1 | 5962 |
| pass1_cluster_availability | 1 | 5533 |
| pass1_cluster_closure | 1 | 5792 |
| pass1_cluster_incentive | 1 | 5580 |
| pass1_cluster_residual | 1 | 5570 |
| pass1_cluster_self_regard | 1 | 5614 |
| pass2 | 8 | 45842 |
| structural_coverage_classification | 1 | 4716 |
| structural_coverage_detection | 1 | 4716 |

#### `20260426T131135Zstab2`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 5221 |
| companion_verification_analogical | 1 | 6377 |
| companion_verification_causal | 1 | 6612 |
| companion_verification_counterfactual | 1 | 7115 |
| companion_verification_deductive | 1 | 6679 |
| companion_verification_diagnostic | 1 | 7690 |
| companion_verification_metacognitive | 1 | 7441 |
| companion_verification_probabilistic | 1 | 6389 |
| companion_verification_systems | 1 | 7379 |
| frame_extraction | 1 | 5626 |
| frame_reframing | 1 | 1269 |
| pass1_cluster_authority | 1 | 5966 |
| pass1_cluster_availability | 1 | 5541 |
| pass1_cluster_closure | 1 | 5791 |
| pass1_cluster_incentive | 1 | 5601 |
| pass1_cluster_residual | 1 | 5570 |
| pass1_cluster_self_regard | 1 | 5614 |
| pass2 | 8 | 45821 |
| structural_coverage_classification | 1 | 4846 |
| structural_coverage_detection | 1 | 4846 |
