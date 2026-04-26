# Stability report — marcus-equity-lane2-on

Generated: 2026-04-26T10:41:28Z
Runs: 3
Run IDs: 20260426T104128Zstab0, 20260426T104251Zstab1, 20260426T104411Zstab2
Prompt versions consistent across runs: True

## Per-stage stability (Jaccard)

> 1.0 is a WARNING, not a target — signals a specialist that stopped doing semantic judgment. Acceptance is a threshold band: stability moved up from baseline, no neighboring stage regressed, qualitative review confirms cards still do structural work.

| Stage | Mean | Min | Max |
|---|---|---|---|
| Pass 1 (tendencies) | 1.00 | 1.00 | 1.00 |
| Lane 2 — fingerprint moves | 0.00 | 0.00 | 0.00 |
| Lane 2 — recalled candidates | 0.72 | 0.64 | 0.76 |
| Lane 2 — accepted (pre-cap) | 0.17 | 0.00 | 0.50 |
| Lane 2 — detected (post-cap) | 0.17 | 0.00 | 0.50 |
| Lane 2 — capped (top-5 drops) | 1.00 | 1.00 | 1.00 |
| Lane 2 (cheat-sheet anchors) | 0.17 | 0.00 | 0.50 |
| Lane 3 (reframings) | 0.33 | 0.33 | 0.33 |
| Lane 4 (gap dims) | 0.73 | 0.60 | 0.80 |

Embedding mode per run: ['on', 'on', 'on']  ·  consistent: True

### Recall-source distribution per run

| Run | keyword | embedding | both | other |
|---|---|---|---|---|
| `20260426T104128Zstab0` | 60 | 0 | 0 | 0 |
| `20260426T104251Zstab1` | 60 | 0 | 0 | 0 |
| `20260426T104411Zstab2` | 60 | 0 | 0 | 0 |

## Step 6 anchor naming (per-run)

| Run | Named | Total | Rate |
|---|---|---|---|
| `20260426T104128Zstab0` | (no revised_answer) | — | — |
| `20260426T104251Zstab1` | (no revised_answer) | — | — |
| `20260426T104411Zstab2` | (no revised_answer) | — | — |

## Per-run item diff

### Pass 1 tendencies
- `20260426T104128Zstab0`: ['availability-misweighing-tendency', 'contrast-misreaction-tendency', 'deprival-superreaction-tendency', 'liking-loving-tendency', 'reward-and-punishment-superresponse-tendency']
- `20260426T104251Zstab1`: ['availability-misweighing-tendency', 'contrast-misreaction-tendency', 'deprival-superreaction-tendency', 'liking-loving-tendency', 'reward-and-punishment-superresponse-tendency']
- `20260426T104411Zstab2`: ['availability-misweighing-tendency', 'contrast-misreaction-tendency', 'deprival-superreaction-tendency', 'liking-loving-tendency', 'reward-and-punishment-superresponse-tendency']

### Lane 2 fingerprint moves
- `20260426T104128Zstab0`: ['contrast cash-based retention incentives with ownership needs, arguing they fail to address desire for voice and alignment.', "differentiate marcus's unique, irreplaceable contributions from other employees to dismiss slippery slope precedent concerns.", "distinguish between equity for financial upside versus equity for voice and influence, tailoring solutions to marcus's true motivations.", 'perform scenario analysis comparing exit value with versus without marcus, showing equity cost is outweighed by downside protection and upside potential.', 'propose structured protections including vesting, governance limits, ip clauses, and buyback mechanisms to mitigate partnership risks.', "quantify marcus's value by estimating the business valuation gap created by his potential departure, framing equity as the cost to close that gap rather than a giveaway.", 'recommend low-risk, bounded experimentation on platform idea to validate potential without full commitment.']
- `20260426T104251Zstab1`: ['advocating bounded experimentation on the platform idea to validate potential without full commitment, using low-cost sprint to generate market signal.', 'differentiating marcus from other employees to dismiss precedent concerns by highlighting his unique tenure, infrastructure built, and non-interchangeability.', "identifying mismatch between retention alternatives and marcus's core ask for ownership and voice, arguing they fail to provide alignment or influence.", 'proposing structured protections like vesting, governance limits, ip clauses, and buyback mechanisms to mitigate risks of partnership regret.', "quantifying the financial cost of marcus's potential departure by contrasting current valuation with projected valuation loss due to talent drain, client risk, and capability degradation.", 'recognizing emotional decision-making impasse and prioritizing radical honesty over structured offers to realign trajectories.', "reframing the equity decision from a giveaway of earned value to payment for irreplaceable business dependency by quantifying marcus's contribution as central to the agency's product."]
- `20260426T104411Zstab2`: ["challenge the founder's emotional ownership narrative by reconciling the contradiction between marcus's indispensable contributions and denial of equity, emphasizing shared creation of current value.", 'differentiate marcus from other employees like tom or the head of design by highlighting his unique contributions, tenure, and irreplaceability to dismiss precedent and slippery slope concerns.', "interpret marcus's equity ask as primarily seeking ownership and voice rather than cash compensation, explaining why financial alternatives like bonuses or profit-sharing fail to address his core motivations.", "link marcus's disengagement and platform prototype to a deeper need for strategic influence, positioning the equity ask as a bid for partnership in a potential product pivot rather than mere retention.", 'propose concrete structural safeguards including vesting schedules, governance limits, ip clauses, buyback rights, and bounded experimentation to mitigate risks of partnership while enabling alignment.', "quantify the true cost of marcus's departure by estimating the valuation gap between the business with and without him, framing equity as protection against massive downside risk rather than a giveaway."]

### Lane 2 recalled candidates
- `20260426T104128Zstab0`: ['active-listening', 'agile-methodologies', 'aleatory-epistemic-uncertainty-recognition', 'algorithmic-thinking', 'association', 'base-rates', 'boundaries', 'calculated-risk-taking', 'chain-of-verification', 'cognitive-dissonance', 'commitment-bias', 'comparative-political-systems-analysis', 'complexity-bias-resistance', 'confidence-calibration', 'cultural-intelligence', 'delays', 'einstellung-effect', 'empathy', 'endowment-effect', 'experimentation', 'feedback-loops', 'feynman-technique', 'game-theory-payoffs', 'information-asymmetry', 'information-theory', 'intellectual-humility', 'inversion', 'jobs-to-be-done', 'learning-curve', 'liking-principle', 'non-violent-communication', 'occams-razor', 'opportunity-cost', 'optionality', 'persuasion-principles', 'power-dynamics', 'premortem', 'principal-agent-problem', 'probabilistic-thinking', 'problem-framing-and-reframing', 'prospect-theory', 'psychological-safety', 'reasoning-mode-router', 'reciprocity-principle', 'representativeness-heuristic', 'root-cause-analysis', 'scientific-method-evidence-testing', 'second-order-thinking', 'signaling', 'social-proof', 'specialization', 'statistical-discipline', 'status-quo-bias', 'step-back', 'sunk-cost-fallacy', 'systems-thinking', 'tier-2-high-value', 'trade-offs', 'usability-heuristics', 'user-centered-design']
- `20260426T104251Zstab1`: ['active-listening', 'agile-methodologies', 'aleatory-epistemic-uncertainty-recognition', 'algorithmic-thinking', 'base-rates', 'bias-blind-spot', 'boundaries', 'branch-solve-merge', 'calculated-risk-taking', 'commitment-bias', 'complexity-bias-resistance', 'confidence-calibration', 'confirmation-bias', 'cultural-intelligence', 'delays', 'dunning-kruger-effect', 'einstellung-effect', 'empathy', 'endowment-effect', 'experimentation', 'false-precision-avoidance', 'feedback-loops', 'feynman-technique', 'game-theory-payoffs', 'information-asymmetry', 'information-theory', 'intellectual-humility', 'inversion', 'jobs-to-be-done', 'latticework-of-mental-models', 'learning-curve', 'liking-principle', 'moral-hazard', 'obligations-controls-mapping', 'occams-razor', 'opportunity-cost', 'power-dynamics', 'premortem', 'principal-agent-problem', 'probabilistic-thinking', 'problem-framing-and-reframing', 'prospect-theory', 'psychological-safety', 'reasoning-mode-router', 'reciprocity-principle', 'representativeness-heuristic', 'root-cause-analysis', 'scientific-method-evidence-testing', 'second-order-thinking', 'signaling', 'social-proof', 'specialization', 'status-quo-bias', 'step-back', 'sunk-cost-fallacy', 'systems-thinking', 'tier-2-high-value', 'usability-heuristics', 'user-centered-design', 'wysiati']
- `20260426T104411Zstab2`: ['active-listening', 'agile-methodologies', 'aleatory-epistemic-uncertainty-recognition', 'algorithmic-thinking', 'association', 'base-rates', 'bias-blind-spot', 'boundaries', 'calculated-risk-taking', 'causal-attribution-resistance', 'chain-of-verification', 'commitment-bias', 'comparative-political-systems-analysis', 'complex-adaptive-systems', 'complexity-bias-resistance', 'cultural-intelligence', 'desirable-difficulties', 'einstellung-effect', 'empathy', 'endowment-effect', 'experimentation', 'feedback-loops', 'feynman-technique', 'game-theory-payoffs', 'information-asymmetry', 'information-theory', 'intellectual-humility', 'inversion', 'lean-startup-methodology', 'learning-curve', 'liking-principle', 'natural-selection-analogy', 'non-violent-communication', 'obligations-controls-mapping', 'opportunity-cost', 'optionality', 'persuasion-principles', 'power-dynamics', 'premortem', 'principal-agent-problem', 'probabilistic-thinking', 'problem-framing-and-reframing', 'psychological-safety', 'reasoning-mode-router', 'reciprocity-principle', 'representativeness-heuristic', 'root-cause-analysis', 'scientific-method-evidence-testing', 'second-order-thinking', 'signaling', 'social-proof', 'specialization', 'statistical-discipline', 'status-quo-bias', 'step-back', 'sunk-cost-fallacy', 'systems-thinking', 'tier-2-high-value', 'understanding-motivations', 'user-centered-design']

### Lane 2 accepted (pre-cap)
- `20260426T104128Zstab0`: ['representativeness-heuristic']
- `20260426T104251Zstab1`: ['endowment-effect', 'principal-agent-problem']
- `20260426T104411Zstab2`: ['representativeness-heuristic', 'understanding-motivations']

### Lane 2 detected (post-cap)
- `20260426T104128Zstab0`: ['representativeness-heuristic']
- `20260426T104251Zstab1`: ['endowment-effect', 'principal-agent-problem']
- `20260426T104411Zstab2`: ['representativeness-heuristic', 'understanding-motivations']

### Lane 2 capped (top-5 drops)
- `20260426T104128Zstab0`: []
- `20260426T104251Zstab1`: []
- `20260426T104411Zstab2`: []

### Lane 2 cheat-sheet anchors
- `20260426T104128Zstab0`: ['representativeness-heuristic']
- `20260426T104251Zstab1`: ['endowment-effect', 'principal-agent-problem']
- `20260426T104411Zstab2`: ['representativeness-heuristic', 'understanding-motivations']

### Lane 3 reframings
- `20260426T104128Zstab0`: ['lateral-thinking', 'reframing-perspective']
- `20260426T104251Zstab1`: ['decision-trees', 'reframing-perspective']
- `20260426T104411Zstab2`: ['empathy', 'reframing-perspective']

### Lane 4 gap dims
- `20260426T104128Zstab0`: ['information-quality', 'resource-allocation', 'risk-response', 'stakeholder-alignment', 'timing-sequencing']
- `20260426T104251Zstab1`: ['information-quality', 'resource-allocation', 'stakeholder-alignment', 'timing-sequencing']
- `20260426T104411Zstab2`: ['information-quality', 'resource-allocation', 'risk-response', 'timing-sequencing']

## Cost per run (boundary-call tokens, lower bound when embeddings on)

| Run | Calls | Prompt tok | Completion tok | Total tok | Embedding-expansion observed |
|---|---|---|---|---|---|
| `20260426T104128Zstab0` | 19 | 138874 | 8239 | 147113 | 0 |
| `20260426T104251Zstab1` | 19 | 138191 | 7211 | 145402 | 0 |
| `20260426T104411Zstab2` | 19 | 138674 | 7954 | 146628 | 0 |

> Embedding-expansion calls (gpt-4o-mini, temp=0.7) bypass `BoundaryClient` tracing — reported here as 0 with a caveat. Treat boundary_only totals as a lower bound on Lane 2 cost when `embedding_mode = on`.

### Per-stage boundary token cost

#### `20260426T104128Zstab0`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 7807 |
| companion_verification | 1 | 13733 |
| frame_extraction | 1 | 7862 |
| frame_reframing | 1 | 1929 |
| pass1_cluster_authority | 1 | 7990 |
| pass1_cluster_availability | 1 | 7692 |
| pass1_cluster_closure | 1 | 7919 |
| pass1_cluster_incentive | 1 | 7676 |
| pass1_cluster_residual | 1 | 7628 |
| pass1_cluster_self_regard | 1 | 7703 |
| pass2 | 7 | 55200 |
| structural_coverage_classification | 1 | 6987 |
| structural_coverage_detection | 1 | 6987 |

#### `20260426T104251Zstab1`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 7398 |
| companion_verification | 1 | 13324 |
| frame_extraction | 1 | 7785 |
| frame_reframing | 1 | 1549 |
| pass1_cluster_authority | 1 | 8009 |
| pass1_cluster_availability | 1 | 7706 |
| pass1_cluster_closure | 1 | 7952 |
| pass1_cluster_incentive | 1 | 7687 |
| pass1_cluster_residual | 1 | 7628 |
| pass1_cluster_self_regard | 1 | 7703 |
| pass2 | 7 | 55171 |
| structural_coverage_classification | 1 | 6745 |
| structural_coverage_detection | 1 | 6745 |

#### `20260426T104411Zstab2`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 7674 |
| companion_verification | 1 | 13561 |
| frame_extraction | 1 | 7882 |
| frame_reframing | 1 | 1837 |
| pass1_cluster_authority | 1 | 8016 |
| pass1_cluster_availability | 1 | 7683 |
| pass1_cluster_closure | 1 | 7915 |
| pass1_cluster_incentive | 1 | 7678 |
| pass1_cluster_residual | 1 | 7628 |
| pass1_cluster_self_regard | 1 | 7672 |
| pass2 | 7 | 55276 |
| structural_coverage_classification | 1 | 6903 |
| structural_coverage_detection | 1 | 6903 |
