# Stability report — marcus-equity-prb-v3-on

Generated: 2026-04-26T13:43:51Z
Runs: 3
Run IDs: 20260426T134351Zstab0, 20260426T134530Zstab1, 20260426T134707Zstab2
Prompt versions consistent across runs: True

## Per-stage stability (Jaccard)

> 1.0 is a WARNING, not a target — signals a specialist that stopped doing semantic judgment. Acceptance is a threshold band: stability moved up from baseline, no neighboring stage regressed, qualitative review confirms cards still do structural work.

| Stage | Mean | Min | Max |
|---|---|---|---|
| Pass 1 (tendencies) | 0.87 | 0.80 | 1.00 |
| Lane 2 — fingerprint moves | 0.05 | 0.00 | 0.08 |
| Lane 2 — recalled candidates | 0.79 | 0.74 | 0.88 |
| Lane 2 — accepted (pre-cap) | 0.29 | 0.22 | 0.33 |
| Lane 2 — shared-avail. accept agreement | 0.32 | 0.25 | 0.38 |
| Lane 2 — detected (post-cap) | 0.13 | 0.11 | 0.14 |
| Lane 2 — capped (top-5 drops) | 0.06 | 0.00 | 0.17 |
| Lane 2 (cheat-sheet anchors) | 0.13 | 0.11 | 0.14 |
| Lane 3 (reframings) | 0.56 | 0.33 | 1.00 |
| Lane 4 (gap dims) | 0.46 | 0.29 | 0.60 |

Embedding mode per run: ['on', 'on', 'on']  ·  consistent: True

### Recall-source distribution per run

| Run | keyword | embedding | both | other |
|---|---|---|---|---|
| `20260426T134351Zstab0` | 60 | 0 | 0 | 0 |
| `20260426T134530Zstab1` | 60 | 0 | 0 | 0 |
| `20260426T134707Zstab2` | 60 | 0 | 0 | 0 |

## Step 6 anchor naming (per-run)

| Run | Named | Total | Rate |
|---|---|---|---|
| `20260426T134351Zstab0` | (no revised_answer) | — | — |
| `20260426T134530Zstab1` | (no revised_answer) | — | — |
| `20260426T134707Zstab2` | (no revised_answer) | — | — |

## Per-run item diff

### Pass 1 tendencies
- `20260426T134351Zstab0`: ['availability-misweighing-tendency', 'contrast-misreaction-tendency', 'deprival-superreaction-tendency', 'liking-loving-tendency', 'reward-and-punishment-superresponse-tendency']
- `20260426T134530Zstab1`: ['availability-misweighing-tendency', 'contrast-misreaction-tendency', 'deprival-superreaction-tendency', 'liking-loving-tendency', 'reward-and-punishment-superresponse-tendency']
- `20260426T134707Zstab2`: ['availability-misweighing-tendency', 'deprival-superreaction-tendency', 'liking-loving-tendency', 'reward-and-punishment-superresponse-tendency']

### Lane 2 fingerprint moves
- `20260426T134351Zstab0`: ["challenge founder's pattern of proposing cash alternatives as avoidance of core ownership question, forcing reflection on willingness to share control.", 'differentiate marcus from other employees like tom or head of design by highlighting his unique contributions, tenure, and irreplaceability to dismiss slippery slope and precedent concerns.', "interpret marcus's equity ask as primarily seeking ownership and voice rather than cash, explaining why financial alternatives like bonuses or profit-sharing fail to address his core motivations.", "link marcus's disengagement and platform prototype to a deeper need for strategic voice, positioning equity as alignment for pursuing the platform opportunity rather than retention alone.", 'propose concrete structural safeguards like vesting, governance limits, ip clauses, and buyback rights to mitigate risks of partnership such as early departure, spinouts, or decision blocks.', "quantify the true cost of marcus's departure by estimating the valuation gap between the business with and without him, framing equity as protection against massive downside risk rather than a giveaway.", "recommend bounded experimentation on the platform to validate potential without full commitment, using low-cost tests to de-risk while signaling value in marcus's idea."]
- `20260426T134530Zstab1`: ["challenge emotional founder ownership narrative by attributing current company value jointly, resolving contradiction between marcus's indispensability and non-founder status.", "differentiate marcus's unique value from other employees to dismiss slippery slope concerns about equity precedent by establishing a clear, non-replicable bar.", "identify mismatch between marcus's core ask for ownership and voice versus cash-based alternatives, arguing they fail to address alignment and signal undervaluation.", 'propose specific structural safeguards like vesting, governance limits, ip clauses, and buyback rights to mitigate risks of partnership while enabling it.', "quantify the true cost of marcus's departure by estimating the valuation impact and comparing it to the equity grant to reframe equity as value protection rather than giveaway.", 'recommend bounded experimentation on the platform to validate without full commitment, balancing caution with opportunity testing.', 'reframe the platform idea as intertwined with retention and growth opportunity rather than a side distraction, linking it to equity for mutual alignment.']
- `20260426T134707Zstab2`: ["differentiate marcus's unique, non-interchangeable value from other employees to dismiss precedent concerns, setting a clear high bar that others cannot meet.", 'identify that marcus seeks ownership and voice rather than cash, rendering financial incentives like bonuses or profit-sharing inadequate for alignment.', "link marcus's disengagement to rejection of his platform vision, interpreting equity ask as demand for strategic influence, not just compensation.", 'propose specific structural safeguards like vesting, governance limits, ip clauses, and buyback rights to mitigate risks of partnership while enabling it.', "quantify the true cost of marcus's departure by estimating the valuation gap between the business with and without him, framing equity as protection against massive downside risk rather than a giveaway.", 'recognize emotional decision point where honesty about willingness to partner outweighs offer details to reset trajectory.', 'recommend bounded experimentation on platform to validate without full commitment, turning risk into low-cost learning.']

### Lane 2 recalled candidates
- `20260426T134351Zstab0`: ['adverse-selection', 'agile-methodologies', 'aleatory-epistemic-uncertainty-recognition', 'algorithmic-thinking', 'association', 'base-rates', 'bias-blind-spot', 'boundaries', 'calculated-risk-taking', 'causal-attribution-resistance', 'chain-of-verification', 'cognitive-dissonance', 'commitment-bias', 'comparative-political-systems-analysis', 'complexity-bias-resistance', 'desirable-difficulties', 'einstellung-effect', 'empathy', 'endowment-effect', 'experimentation', 'feedback-loops', 'feynman-technique', 'game-theory-payoffs', 'information-asymmetry', 'information-theory', 'intellectual-humility', 'inversion', 'learning-curve', 'liking-principle', 'natural-selection-analogy', 'non-violent-communication', 'obligations-controls-mapping', 'opportunity-cost', 'optionality', 'persuasion-principles', 'power-dynamics', 'premortem', 'principal-agent-problem', 'probabilistic-thinking', 'problem-framing-and-reframing', 'prospect-theory', 'psychological-safety', 'reasoning-mode-router', 'reciprocity-principle', 'representativeness-heuristic', 'risk-assessment', 'risk-vs-uncertainty', 'root-cause-analysis', 'scientific-method-evidence-testing', 'second-order-thinking', 'signaling', 'social-proof', 'specialization', 'statistical-discipline', 'status-quo-bias', 'step-back', 'sunk-cost-fallacy', 'systems-thinking', 'user-centered-design', 'wysiati']
- `20260426T134530Zstab1`: ['active-listening', 'agile-methodologies', 'aleatory-epistemic-uncertainty-recognition', 'algorithmic-thinking', 'association', 'base-rates', 'bias-blind-spot', 'boundaries', 'calculated-risk-taking', 'causal-attribution-resistance', 'chain-of-verification', 'commitment-bias', 'comparative-political-systems-analysis', 'complexity-bias-resistance', 'confidence-calibration', 'cultural-intelligence', 'delays', 'einstellung-effect', 'empathy', 'endowment-effect', 'experimentation', 'feedback-loops', 'feynman-technique', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'information-theory', 'intellectual-humility', 'inversion', 'learning-curve', 'liking-principle', 'non-violent-communication', 'obligations-controls-mapping', 'opportunity-cost', 'optionality', 'power-dynamics', 'premortem', 'principal-agent-problem', 'probabilistic-thinking', 'problem-framing-and-reframing', 'psychological-safety', 'reasoning-mode-router', 'reciprocity-principle', 'representativeness-heuristic', 'root-cause-analysis', 'scientific-method-evidence-testing', 'second-order-thinking', 'signaling', 'social-proof', 'specialization', 'statistical-discipline', 'status-quo-bias', 'step-back', 'sunk-cost-fallacy', 'survivorship-bias', 'systems-thinking', 'tier-2-high-value', 'usability-heuristics', 'user-centered-design', 'wysiati']
- `20260426T134707Zstab2`: ['active-listening', 'agile-methodologies', 'aleatory-epistemic-uncertainty-recognition', 'algorithmic-thinking', 'base-rates', 'bias-blind-spot', 'boundaries', 'calculated-risk-taking', 'chain-of-verification', 'cognitive-dissonance', 'commitment-bias', 'comparative-political-systems-analysis', 'complexity-bias-resistance', 'confidence-calibration', 'cultural-intelligence', 'einstellung-effect', 'emotional-intelligence', 'empathy', 'endowment-effect', 'experimentation', 'feedback-loops', 'feynman-technique', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'information-theory', 'intellectual-humility', 'inversion', 'johari-window', 'lean-startup-methodology', 'learning-curve', 'liking-principle', 'non-violent-communication', 'obligations-controls-mapping', 'opportunity-cost', 'optionality', 'power-dynamics', 'premortem', 'principal-agent-problem', 'probabilistic-thinking', 'problem-framing-and-reframing', 'psychological-safety', 'reasoning-mode-router', 'reciprocity-principle', 'representativeness-heuristic', 'root-cause-analysis', 'scientific-method-evidence-testing', 'second-order-thinking', 'signaling', 'social-proof', 'specialization', 'statistical-discipline', 'status-quo-bias', 'step-back', 'sunk-cost-fallacy', 'systems-thinking', 'tier-2-high-value', 'usability-heuristics', 'user-centered-design', 'wysiati']

### Lane 2 accepted (pre-cap)
- `20260426T134351Zstab0`: ['power-dynamics', 'principal-agent-problem', 'problem-framing-and-reframing']
- `20260426T134530Zstab1`: ['endowment-effect', 'experimentation', 'game-theory-payoffs', 'optionality', 'power-dynamics', 'principal-agent-problem', 'problem-framing-and-reframing', 'signaling', 'tier-2-high-value']
- `20260426T134707Zstab2`: ['cognitive-dissonance', 'empathy', 'opportunity-cost', 'optionality', 'power-dynamics', 'problem-framing-and-reframing', 'second-order-thinking', 'tier-2-high-value']

### Lane 2 detected (post-cap)
- `20260426T134351Zstab0`: ['power-dynamics', 'principal-agent-problem', 'problem-framing-and-reframing']
- `20260426T134530Zstab1`: ['endowment-effect', 'game-theory-payoffs', 'optionality', 'principal-agent-problem', 'signaling']
- `20260426T134707Zstab2`: ['empathy', 'opportunity-cost', 'optionality', 'power-dynamics', 'tier-2-high-value']

### Lane 2 capped (top-5 drops)
- `20260426T134351Zstab0`: []
- `20260426T134530Zstab1`: ['experimentation', 'power-dynamics', 'problem-framing-and-reframing', 'tier-2-high-value']
- `20260426T134707Zstab2`: ['cognitive-dissonance', 'problem-framing-and-reframing', 'second-order-thinking']

### Lane 2 cheat-sheet anchors
- `20260426T134351Zstab0`: ['power-dynamics', 'principal-agent-problem', 'problem-framing-and-reframing']
- `20260426T134530Zstab1`: ['endowment-effect', 'game-theory-payoffs', 'optionality', 'principal-agent-problem', 'signaling']
- `20260426T134707Zstab2`: ['empathy', 'opportunity-cost', 'optionality', 'power-dynamics', 'tier-2-high-value']

### Lane 3 reframings
- `20260426T134351Zstab0`: ['reframing-perspective', 'second-order-thinking']
- `20260426T134530Zstab1`: ['empathy', 'reframing-perspective']
- `20260426T134707Zstab2`: ['reframing-perspective', 'second-order-thinking']

### Lane 4 gap dims
- `20260426T134351Zstab0`: ['resource-allocation', 'scope-boundary', 'stakeholder-alignment', 'timing-sequencing']
- `20260426T134530Zstab1`: ['information-quality', 'resource-allocation', 'risk-response', 'stakeholder-alignment', 'uncertainty-type']
- `20260426T134707Zstab2`: ['resource-allocation', 'stakeholder-alignment', 'timing-sequencing', 'uncertainty-type']

## Cost per run (boundary-call tokens, lower bound when embeddings on)

| Run | Calls | Prompt tok | Completion tok | Total tok | Embedding-expansion observed |
|---|---|---|---|---|---|
| `20260426T134351Zstab0` | 21 | 158087 | 10066 | 168153 | 0 |
| `20260426T134530Zstab1` | 22 | 162465 | 8911 | 171376 | 0 |
| `20260426T134707Zstab2` | 21 | 155438 | 8769 | 164207 | 0 |

> Embedding-expansion calls (gpt-4o-mini, temp=0.7) bypass `BoundaryClient` tracing — reported here as 0 with a caveat. Treat boundary_only totals as a lower bound on Lane 2 cost when `embedding_mode = on`.

### Per-stage boundary token cost

#### `20260426T134351Zstab0`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 8372 |
| companion_verification_shard_0 | 1 | 11399 |
| companion_verification_shard_1 | 1 | 11803 |
| companion_verification_shard_2 | 1 | 11323 |
| frame_extraction | 1 | 7914 |
| frame_reframing | 1 | 1859 |
| pass1_cluster_authority | 1 | 8007 |
| pass1_cluster_availability | 1 | 7711 |
| pass1_cluster_closure | 1 | 7916 |
| pass1_cluster_incentive | 1 | 7676 |
| pass1_cluster_residual | 1 | 7628 |
| pass1_cluster_self_regard | 1 | 7672 |
| pass2 | 7 | 55095 |
| structural_coverage_classification | 1 | 6889 |
| structural_coverage_detection | 1 | 6889 |

#### `20260426T134530Zstab1`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 7387 |
| companion_verification_shard_0 | 1 | 10346 |
| companion_verification_shard_1 | 1 | 10705 |
| companion_verification_shard_2 | 1 | 10326 |
| frame_extraction | 1 | 7787 |
| frame_reframing | 1 | 1561 |
| pass1_cluster_authority | 1 | 7986 |
| pass1_cluster_availability | 1 | 7695 |
| pass1_cluster_closure | 1 | 7917 |
| pass1_cluster_incentive | 1 | 7685 |
| pass1_cluster_residual | 1 | 7628 |
| pass1_cluster_self_regard | 1 | 7672 |
| pass2 | 8 | 62783 |
| structural_coverage_classification | 1 | 6949 |
| structural_coverage_detection | 1 | 6949 |

#### `20260426T134707Zstab2`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 7462 |
| companion_verification_shard_0 | 1 | 10894 |
| companion_verification_shard_1 | 1 | 10353 |
| companion_verification_shard_2 | 1 | 10552 |
| frame_extraction | 1 | 7802 |
| frame_reframing | 1 | 1594 |
| pass1_cluster_authority | 1 | 8009 |
| pass1_cluster_availability | 1 | 7680 |
| pass1_cluster_closure | 1 | 7873 |
| pass1_cluster_incentive | 1 | 7693 |
| pass1_cluster_residual | 1 | 7628 |
| pass1_cluster_self_regard | 1 | 7746 |
| pass2 | 7 | 55179 |
| structural_coverage_classification | 1 | 6871 |
| structural_coverage_detection | 1 | 6871 |
