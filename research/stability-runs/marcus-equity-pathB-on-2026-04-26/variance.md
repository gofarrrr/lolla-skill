# Stability report — marcus-equity-pathB-on

Generated: 2026-04-26T14:27:10Z
Runs: 3
Run IDs: 20260426T142710Zstab0, 20260426T142835Zstab1, 20260426T142958Zstab2
Prompt versions consistent across runs: True

## Per-stage stability (Jaccard)

> 1.0 is a WARNING, not a target — signals a specialist that stopped doing semantic judgment. Acceptance is a threshold band: stability moved up from baseline, no neighboring stage regressed, qualitative review confirms cards still do structural work.

| Stage | Mean | Min | Max |
|---|---|---|---|
| Pass 1 (tendencies) | 0.87 | 0.80 | 1.00 |
| Lane 2 — fingerprint moves | 0.03 | 0.00 | 0.09 |
| Lane 2 — recalled candidates | 0.77 | 0.74 | 0.85 |
| Lane 2 — accepted (pre-cap) | 0.19 | 0.11 | 0.25 |
| Lane 2 — shared-avail. accept agreement | 0.19 | 0.11 | 0.25 |
| Lane 2 — detected (post-cap) | 0.08 | 0.00 | 0.25 |
| Lane 2 — capped (top-5 drops) | 1.00 | 1.00 | 1.00 |
| Lane 2 (cheat-sheet anchors) | 0.08 | 0.00 | 0.25 |
| Lane 3 (reframings) | 0.56 | 0.33 | 1.00 |
| Lane 4 (gap dims) | 0.51 | 0.33 | 0.60 |

Embedding mode per run: ['on', 'on', 'on']  ·  consistent: True

### Recall-source distribution per run

| Run | keyword | embedding | both | other |
|---|---|---|---|---|
| `20260426T142710Zstab0` | 60 | 0 | 0 | 0 |
| `20260426T142835Zstab1` | 60 | 0 | 0 | 0 |
| `20260426T142958Zstab2` | 60 | 0 | 0 | 0 |

## Step 6 anchor naming (per-run)

| Run | Named | Total | Rate |
|---|---|---|---|
| `20260426T142710Zstab0` | (no revised_answer) | — | — |
| `20260426T142835Zstab1` | (no revised_answer) | — | — |
| `20260426T142958Zstab2` | (no revised_answer) | — | — |

## Per-run item diff

### Pass 1 tendencies
- `20260426T142710Zstab0`: ['availability-misweighing-tendency', 'contrast-misreaction-tendency', 'deprival-superreaction-tendency', 'liking-loving-tendency']
- `20260426T142835Zstab1`: ['availability-misweighing-tendency', 'contrast-misreaction-tendency', 'deprival-superreaction-tendency', 'liking-loving-tendency', 'reward-and-punishment-superresponse-tendency']
- `20260426T142958Zstab2`: ['availability-misweighing-tendency', 'contrast-misreaction-tendency', 'deprival-superreaction-tendency', 'liking-loving-tendency', 'reward-and-punishment-superresponse-tendency']

### Lane 2 fingerprint moves
- `20260426T142710Zstab0`: ["analyze marcus's core motivation as seeking ownership and voice rather than cash, invalidating financial incentives like bonuses or profit-sharing as misaligned solutions.", "differentiate marcus's unique value from other employees to dismiss slippery slope concerns about equity precedent by establishing a clear, non-replicable bar.", "link the platform idea to marcus's disengagement and equity ask as a unified desire for strategic partnership, reframing it from side project to potential value multiplier.", 'propose specific structural safeguards like vesting, governance limits, ip clauses, and buyback rights to mitigate risks of partnership regret, enabling calculated yes.', "quantify the true cost of marcus's departure by estimating the valuation gap between the current business and a post-departure scenario to reframe equity as value protection rather than giveaway.", 'recognize the conversation as a pivotal emotional decision point requiring radical honesty over structured offers to realign trajectories.', "recommend bounded experimentation on the platform to validate without full commitment, using low-cost sprint to generate data and signal value in marcus's idea."]
- `20260426T142835Zstab1`: ["challenge emotional 'my company' framing by reconciling founder's early risk with marcus's indispensable contributions to current value.", 'differentiate marcus from other employees like tom by scale of impact and uniqueness, dismissing slippery slope precedent concerns as inapplicable.', "link the platform idea to marcus's ask as a signal of desired strategic partnership, reframing equity decision as choice between retaining employee vs. embracing co-builder for pivot potential.", 'propose specific structural safeguards (vesting, governance limits, buyback, ip clauses) to mitigate risks of partnership while enabling alignment.', "quantify the true cost of marcus's departure by estimating the valuation gap between the business with and without him, framing equity as protection against massive downside risk rather than a giveaway.", 'recommend bounded experimentation on platform to validate without full commitment, turning risk into low-cost learning.']
- `20260426T142958Zstab2`: ["challenge the founder's emotional ownership narrative by reconciling his dual calculations, attributing current value to joint contributions rather than solo founder myth.", 'differentiate marcus from other employees by his unique contributions and irreplaceability to preempt slippery slope concerns about equity precedent.', "link disengagement and platform rejection to marcus's unmet need for strategic influence, positioning equity+platform commitment as the path to re-engagement and competitive defense.", 'propose concrete structural safeguards (vesting, governance limits, buyback clauses) to mitigate risks of partnership while enabling upside from platform experimentation.', "quantify the true cost of marcus's departure by estimating the valuation gap between the business with and without him, framing equity as protection against massive downside risk rather than a giveaway.", "reframe marcus's equity ask as a demand for voice and strategic alignment rather than mere compensation, explaining why cash alternatives like bonuses fail to address his core motivation."]

### Lane 2 recalled candidates
- `20260426T142710Zstab0`: ['active-listening', 'agile-methodologies', 'aleatory-epistemic-uncertainty-recognition', 'algorithmic-thinking', 'association', 'base-rates', 'bias-blind-spot', 'boundaries', 'calculated-risk-taking', 'causal-attribution-resistance', 'chain-of-verification', 'commitment-bias', 'comparative-political-systems-analysis', 'einstellung-effect', 'empathy', 'endowment-effect', 'experimentation', 'false-precision-avoidance', 'feedback-loops', 'feynman-technique', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'information-theory', 'intellectual-humility', 'inversion', 'jobs-to-be-done', 'learning-curve', 'liking-principle', 'non-violent-communication', 'obligations-controls-mapping', 'opportunity-cost', 'optionality', 'perceptual-learning', 'power-dynamics', 'premortem', 'principal-agent-problem', 'prisoners-dilemma', 'probabilistic-thinking', 'problem-framing-and-reframing', 'prospect-theory', 'psychological-safety', 'rationalization', 'reasoning-mode-router', 'reciprocity-principle', 'representativeness-heuristic', 'root-cause-analysis', 'scientific-method-evidence-testing', 'second-order-thinking', 'signaling', 'social-proof', 'specialization', 'statistical-discipline', 'status-quo-bias', 'step-back', 'sunk-cost-fallacy', 'systems-thinking', 'tier-2-high-value', 'user-centered-design', 'wysiati']
- `20260426T142835Zstab1`: ['active-listening', 'agile-methodologies', 'aleatory-epistemic-uncertainty-recognition', 'algorithmic-thinking', 'association', 'base-rates', 'bias-blind-spot', 'boundaries', 'calculated-risk-taking', 'chain-of-verification', 'cognitive-dissonance', 'commitment-bias', 'comparative-advantage', 'confidence-calibration', 'einstellung-effect', 'emotional-intelligence', 'empathy', 'endowment-effect', 'experimentation', 'feedback-loops', 'feynman-technique', 'game-theory-payoffs', 'information-asymmetry', 'information-theory', 'intellectual-humility', 'inversion', 'lean-startup-methodology', 'learning-curve', 'liking-principle', 'moral-hazard', 'non-violent-communication', 'obligations-controls-mapping', 'opportunity-cost', 'optionality', 'persistence-grit', 'power-dynamics', 'premortem', 'principal-agent-problem', 'probabilistic-thinking', 'problem-framing-and-reframing', 'prospect-theory', 'psychological-safety', 'reasoning-mode-router', 'reciprocity-principle', 'representativeness-heuristic', 'risk-vs-uncertainty', 'root-cause-analysis', 'scientific-method-evidence-testing', 'second-order-thinking', 'signaling', 'social-proof', 'specialization', 'statistical-discipline', 'status-quo-bias', 'step-back', 'sunk-cost-fallacy', 'systems-thinking', 'tier-2-high-value', 'usability-heuristics', 'user-centered-design']
- `20260426T142958Zstab2`: ['active-listening', 'aleatory-epistemic-uncertainty-recognition', 'algorithmic-thinking', 'association', 'base-rates', 'bias-blind-spot', 'boundaries', 'calculated-risk-taking', 'causal-attribution-resistance', 'chain-of-verification', 'commitment-bias', 'comparative-political-systems-analysis', 'complexity-bias-resistance', 'cultural-intelligence', 'desirable-difficulties', 'einstellung-effect', 'emotional-intelligence', 'empathy', 'endowment-effect', 'experimentation', 'feedback-loops', 'feynman-technique', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'information-theory', 'intellectual-humility', 'inversion', 'lean-startup-methodology', 'learning-curve', 'liking-principle', 'non-violent-communication', 'obligations-controls-mapping', 'opportunity-cost', 'optionality', 'power-dynamics', 'premortem', 'principal-agent-problem', 'prisoners-dilemma', 'probabilistic-thinking', 'problem-framing-and-reframing', 'psychological-safety', 'rationalization', 'reasoning-mode-router', 'reciprocity-principle', 'representativeness-heuristic', 'root-cause-analysis', 'scientific-method-evidence-testing', 'second-order-thinking', 'signaling', 'social-proof', 'specialization', 'statistical-discipline', 'status-quo-bias', 'step-back', 'sunk-cost-fallacy', 'systems-thinking', 'tier-2-high-value', 'user-centered-design', 'wysiati']

### Lane 2 accepted (pre-cap)
- `20260426T142710Zstab0`: ['opportunity-cost', 'power-dynamics']
- `20260426T142835Zstab1`: ['optionality', 'power-dynamics', 'problem-framing-and-reframing']
- `20260426T142958Zstab2`: ['empathy', 'game-theory-payoffs', 'inversion', 'power-dynamics', 'problem-framing-and-reframing', 'signaling', 'step-back', 'tier-2-high-value']

### Lane 2 detected (post-cap)
- `20260426T142710Zstab0`: ['opportunity-cost', 'power-dynamics']
- `20260426T142835Zstab1`: ['optionality', 'power-dynamics', 'problem-framing-and-reframing']
- `20260426T142958Zstab2`: []

### Lane 2 capped (top-5 drops)
- `20260426T142710Zstab0`: []
- `20260426T142835Zstab1`: []
- `20260426T142958Zstab2`: []

### Lane 2 cheat-sheet anchors
- `20260426T142710Zstab0`: ['opportunity-cost', 'power-dynamics']
- `20260426T142835Zstab1`: ['optionality', 'power-dynamics', 'problem-framing-and-reframing']
- `20260426T142958Zstab2`: []

### Lane 3 reframings
- `20260426T142710Zstab0`: ['decision-trees', 'reframing-perspective']
- `20260426T142835Zstab1`: ['empathy', 'reframing-perspective']
- `20260426T142958Zstab2`: ['decision-trees', 'reframing-perspective']

### Lane 4 gap dims
- `20260426T142710Zstab0`: ['incentive-alignment', 'information-quality', 'resource-allocation', 'stakeholder-alignment']
- `20260426T142835Zstab1`: ['information-quality', 'resource-allocation', 'risk-response', 'timing-sequencing']
- `20260426T142958Zstab2`: ['information-quality', 'resource-allocation', 'stakeholder-alignment', 'timing-sequencing']

## Cost per run (boundary-call tokens, lower bound when embeddings on)

| Run | Calls | Prompt tok | Completion tok | Total tok | Embedding-expansion observed |
|---|---|---|---|---|---|
| `20260426T142710Zstab0` | 22 | 165610 | 10452 | 176062 | 0 |
| `20260426T142835Zstab1` | 21 | 156007 | 9047 | 165054 | 0 |
| `20260426T142958Zstab2` | 22 | 163512 | 9689 | 173201 | 0 |

> Embedding-expansion calls (gpt-4o-mini, temp=0.7) bypass `BoundaryClient` tracing — reported here as 0 with a caveat. Treat boundary_only totals as a lower bound on Lane 2 cost when `embedding_mode = on`.

### Per-stage boundary token cost

#### `20260426T142710Zstab0`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 8499 |
| companion_verification_shard_0 | 1 | 11515 |
| companion_verification_shard_1 | 1 | 11708 |
| companion_verification_shard_2 | 1 | 11986 |
| frame_extraction | 1 | 7797 |
| frame_reframing | 1 | 1538 |
| pass1_cluster_authority | 1 | 8001 |
| pass1_cluster_availability | 1 | 7733 |
| pass1_cluster_closure | 1 | 7918 |
| pass1_cluster_incentive | 1 | 7696 |
| pass1_cluster_residual | 1 | 7628 |
| pass1_cluster_self_regard | 1 | 7672 |
| pass2 | 8 | 62635 |
| structural_coverage_classification | 1 | 6868 |
| structural_coverage_detection | 1 | 6868 |

#### `20260426T142835Zstab1`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 7888 |
| companion_verification_shard_0 | 1 | 10840 |
| companion_verification_shard_1 | 1 | 10719 |
| companion_verification_shard_2 | 1 | 10719 |
| frame_extraction | 1 | 7804 |
| frame_reframing | 1 | 1573 |
| pass1_cluster_authority | 1 | 8003 |
| pass1_cluster_availability | 1 | 7734 |
| pass1_cluster_closure | 1 | 7914 |
| pass1_cluster_incentive | 1 | 7679 |
| pass1_cluster_residual | 1 | 7628 |
| pass1_cluster_self_regard | 1 | 7672 |
| pass2 | 7 | 55189 |
| structural_coverage_classification | 1 | 6846 |
| structural_coverage_detection | 1 | 6846 |

#### `20260426T142958Zstab2`

| Stage | Calls | Total tok |
|---|---|---|
| companion_calibrator | 1 | 6861 |
| companion_fingerprint | 1 | 7911 |
| companion_verification_shard_0 | 1 | 11105 |
| companion_verification_shard_1 | 1 | 10966 |
| companion_verification_shard_2 | 1 | 11079 |
| frame_extraction | 1 | 7877 |
| frame_reframing | 1 | 1812 |
| pass1_cluster_authority | 1 | 8008 |
| pass1_cluster_availability | 1 | 7694 |
| pass1_cluster_closure | 1 | 7906 |
| pass1_cluster_incentive | 1 | 7691 |
| pass1_cluster_residual | 1 | 7628 |
| pass1_cluster_self_regard | 1 | 7672 |
| pass2 | 7 | 55213 |
| structural_coverage_classification | 1 | 6889 |
| structural_coverage_detection | 1 | 6889 |
