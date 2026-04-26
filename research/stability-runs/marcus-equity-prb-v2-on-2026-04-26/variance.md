# Stability report — marcus-equity-prb-v2-on

Generated: 2026-04-26T13:01:45Z
Runs: 3
Run IDs: 20260426T130145Zstab0, 20260426T130434Zstab1, 20260426T130647Zstab2
Prompt versions consistent across runs: True

## Per-stage stability (Jaccard)

> 1.0 is a WARNING, not a target — signals a specialist that stopped doing semantic judgment. Acceptance is a threshold band: stability moved up from baseline, no neighboring stage regressed, qualitative review confirms cards still do structural work.

| Stage | Mean | Min | Max |
|---|---|---|---|
| Pass 1 (tendencies) | 0.87 | 0.80 | 1.00 |
| Lane 2 — fingerprint moves | 0.00 | 0.00 | 0.00 |
| Lane 2 — recalled candidates | 0.76 | 0.74 | 0.79 |
| Lane 2 — accepted (pre-cap) | 0.21 | 0.17 | 0.25 |
| Lane 2 — shared-avail. accept agreement | 0.23 | 0.20 | 0.25 |
| Lane 2 — detected (post-cap) | 0.12 | 0.00 | 0.25 |
| Lane 2 — capped (top-5 drops) | 0.10 | 0.00 | 0.22 |
| Lane 2 (cheat-sheet anchors) | 0.12 | 0.00 | 0.25 |
| Lane 3 (reframings) | 0.56 | 0.33 | 1.00 |
| Lane 4 (gap dims) | 0.63 | 0.50 | 0.80 |

Embedding mode per run: ['on', 'on', 'on']  ·  consistent: True

### Recall-source distribution per run

| Run | keyword | embedding | both | other |
|---|---|---|---|---|
| `20260426T130145Zstab0` | 60 | 0 | 0 | 0 |
| `20260426T130434Zstab1` | 60 | 0 | 0 | 0 |
| `20260426T130647Zstab2` | 60 | 0 | 0 | 0 |

## Step 6 anchor naming (per-run)

| Run | Named | Total | Rate |
|---|---|---|---|
| `20260426T130145Zstab0` | (no revised_answer) | — | — |
| `20260426T130434Zstab1` | (no revised_answer) | — | — |
| `20260426T130647Zstab2` | (no revised_answer) | — | — |

## Per-run item diff

### Pass 1 tendencies
- `20260426T130145Zstab0`: ['availability-misweighing-tendency', 'contrast-misreaction-tendency', 'deprival-superreaction-tendency', 'liking-loving-tendency', 'reward-and-punishment-superresponse-tendency']
- `20260426T130434Zstab1`: ['availability-misweighing-tendency', 'contrast-misreaction-tendency', 'deprival-superreaction-tendency', 'liking-loving-tendency', 'reward-and-punishment-superresponse-tendency']
- `20260426T130647Zstab2`: ['availability-misweighing-tendency', 'deprival-superreaction-tendency', 'liking-loving-tendency', 'reward-and-punishment-superresponse-tendency']

### Lane 2 fingerprint moves
- `20260426T130145Zstab0`: ["challenge emotional ownership narrative by attributing current company value jointly to founder and marcus, resolving contradiction between his irreplaceability and 'my company' claim.", "distinguish marcus's unique value from other employees to dismiss precedent concerns by establishing a non-replicable 'bar' based on tenure, infrastructure built, and irreplaceability.", "link the platform idea to marcus's equity ask as a signal of undervalued strategic vision rather than cynicism, positioning equity as alignment for potential company transformation.", 'propose specific structural safeguards (vesting, governance limits, ip clauses, buyback) to mitigate risks of partnership like early departure, ip theft, or decision blocking.', "quantify the true cost of marcus's departure by estimating the valuation impact and comparing it to the equity dilution cost to reframe equity as value protection rather than giveaway.", "recommend bounded experimentation on platform to validate without full commitment, using low-cost sprint to generate data and address 'pet project' dismissal.", "separate marcus's core ask for ownership and voice from compensation needs, arguing cash alternatives like bonuses fail to address his true motivations and risk accelerating departure."]
- `20260426T130434Zstab1`: ['analogizing inadequate retention tactics to treating a serious issue superficially to underscore the need for alignment via equity.', 'distinguishing the unique irreplaceability of marcus from other employees to dismiss slippery slope concerns about equity precedent.', 'identifying that marcus seeks ownership and voice rather than cash compensation, rendering financial alternatives like bonuses inadequate.', 'proposing structured safeguards like vesting, governance limits, ip clauses, and buyback rights to mitigate risks of partnership.', 'quantifying the true cost of key personnel departure by estimating the valuation impact and business disruption to reframe equity as a protective investment rather than a giveaway.', 'recognizing the conversation as a pivotal emotional turning point requiring radical honesty over tactical offers.', 'reframing the platform idea from a risky pet project to a bounded, low-cost validation experiment with high upside potential.']
- `20260426T130647Zstab2`: ["align the equity ask with marcus's core motivation for ownership and voice rather than cash, explaining why financial alternatives like bonuses fail to address it.", "challenge the founder's emotional ownership narrative by attributing current company value jointly to both parties' contributions, resolving the contradiction between marcus's importance and equity denial.", "differentiate marcus's unique, irreplaceable contributions from other employees to dismiss slippery slope concerns about equity precedent.", "prioritize radical honesty in the upcoming conversation over deal terms, recognizing marcus's disengagement as emotional decision-making that requires authentic resolution.", 'propose specific legal and structural safeguards like vesting, governance limits, ip clauses, and buyback rights to address fears of regret, misalignment, or ip theft.', "quantify the true cost of marcus's departure by estimating the valuation impact and comparing it to the equity dilution cost to reframe equity as a protective investment rather than a giveaway.", 'reframe the platform idea as a strategic opportunity to diversify valuation multiples rather than a risky pet project, using bounded experimentation to mitigate downside.']

### Lane 2 recalled candidates
- `20260426T130145Zstab0`: ['active-listening', 'aleatory-epistemic-uncertainty-recognition', 'algorithmic-thinking', 'association', 'base-rates', 'boundaries', 'calculated-risk-taking', 'causal-attribution-resistance', 'chain-of-verification', 'commitment-bias', 'comparative-political-systems-analysis', 'cultural-intelligence', 'delays', 'dunning-kruger-effect', 'einstellung-effect', 'empathy', 'endowment-effect', 'experimentation', 'false-precision-avoidance', 'feedback-loops', 'feynman-technique', 'game-theory-payoffs', 'information-asymmetry', 'information-theory', 'intellectual-humility', 'inversion', 'jobs-to-be-done', 'learning-curve', 'liking-principle', 'non-violent-communication', 'obligations-controls-mapping', 'opportunity-cost', 'optionality', 'perceptual-learning', 'power-dynamics', 'premortem', 'principal-agent-problem', 'prisoners-dilemma', 'probabilistic-thinking', 'problem-framing-and-reframing', 'prospect-theory', 'psychological-safety', 'reasoning-mode-router', 'reciprocity-principle', 'representativeness-heuristic', 'root-cause-analysis', 'scientific-method-evidence-testing', 'second-order-thinking', 'signaling', 'social-proof', 'specialization', 'statistical-discipline', 'status-quo-bias', 'step-back', 'sunk-cost-fallacy', 'survivorship-bias', 'systems-thinking', 'tier-2-high-value', 'user-centered-design', 'wysiati']
- `20260426T130434Zstab1`: ['active-listening', 'agile-methodologies', 'aleatory-epistemic-uncertainty-recognition', 'algorithmic-thinking', 'association', 'base-rates', 'bias-blind-spot', 'blooms-taxonomy', 'boundaries', 'calculated-risk-taking', 'causal-attribution-resistance', 'chain-of-verification', 'cognitive-load-theory', 'commitment-bias', 'confidence-calibration', 'cultural-intelligence', 'decomposition', 'einstellung-effect', 'empathy', 'endowment-effect', 'experimentation', 'feedback-loops', 'feynman-technique', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'inversion', 'jobs-to-be-done', 'johari-window', 'learning-curve', 'liking-principle', 'non-violent-communication', 'obligations-controls-mapping', 'opportunity-cost', 'optionality', 'perceptual-learning', 'power-dynamics', 'premortem', 'principal-agent-problem', 'probabilistic-thinking', 'problem-framing-and-reframing', 'psychological-safety', 'reasoning-mode-router', 'reciprocity-principle', 'representativeness-heuristic', 'root-cause-analysis', 'scientific-method-evidence-testing', 'signaling', 'social-proof', 'specialization', 'statistical-discipline', 'status-quo-bias', 'step-back', 'sunk-cost-fallacy', 'systems-thinking', 'tier-2-high-value', 'usability-heuristics', 'user-centered-design', 'wysiati']
- `20260426T130647Zstab2`: ['active-listening', 'aleatory-epistemic-uncertainty-recognition', 'algorithmic-thinking', 'association', 'base-rates', 'bias-blind-spot', 'boundaries', 'calculated-risk-taking', 'causal-attribution-resistance', 'chain-of-verification', 'cognitive-load-theory', 'commitment-bias', 'comparative-political-systems-analysis', 'complexity-bias-resistance', 'einstellung-effect', 'empathy', 'endowment-effect', 'experimentation', 'false-precision-avoidance', 'feedback-loops', 'feynman-technique', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'information-theory', 'intellectual-humility', 'inversion', 'learning-curve', 'liking-principle', 'non-violent-communication', 'obligations-controls-mapping', 'occams-razor', 'opportunity-cost', 'optionality', 'perceptual-learning', 'power-dynamics', 'premortem', 'principal-agent-problem', 'probabilistic-thinking', 'problem-framing-and-reframing', 'psychological-safety', 'rationalization', 'reasoning-mode-router', 'reciprocity-principle', 'representativeness-heuristic', 'root-cause-analysis', 'scientific-method-evidence-testing', 'second-order-thinking', 'signaling', 'social-proof', 'specialization', 'statistical-discipline', 'status-quo-bias', 'step-back', 'sunk-cost-fallacy', 'survivorship-bias', 'systems-thinking', 'tier-2-high-value', 'understanding-motivations', 'user-centered-design']

### Lane 2 accepted (pre-cap)
- `20260426T130145Zstab0`: ['boundaries', 'experimentation', 'inversion', 'power-dynamics', 'principal-agent-problem', 'problem-framing-and-reframing', 'signaling', 'tier-2-high-value']
- `20260426T130434Zstab1`: ['active-listening', 'boundaries', 'game-theory-payoffs', 'power-dynamics', 'problem-framing-and-reframing', 'scientific-method-evidence-testing', 'step-back']
- `20260426T130647Zstab2`: ['association', 'base-rates', 'empathy', 'endowment-effect', 'occams-razor', 'opportunity-cost', 'power-dynamics', 'principal-agent-problem', 'problem-framing-and-reframing', 'second-order-thinking', 'status-quo-bias', 'step-back', 'tier-2-high-value', 'understanding-motivations']

### Lane 2 detected (post-cap)
- `20260426T130145Zstab0`: ['boundaries', 'inversion', 'power-dynamics', 'principal-agent-problem', 'problem-framing-and-reframing']
- `20260426T130434Zstab1`: ['active-listening', 'boundaries', 'game-theory-payoffs', 'power-dynamics', 'scientific-method-evidence-testing']
- `20260426T130647Zstab2`: ['base-rates', 'empathy', 'endowment-effect', 'opportunity-cost', 'principal-agent-problem']

### Lane 2 capped (top-5 drops)
- `20260426T130145Zstab0`: ['experimentation', 'signaling', 'tier-2-high-value']
- `20260426T130434Zstab1`: ['problem-framing-and-reframing', 'step-back']
- `20260426T130647Zstab2`: ['association', 'occams-razor', 'power-dynamics', 'problem-framing-and-reframing', 'second-order-thinking', 'status-quo-bias', 'step-back', 'tier-2-high-value', 'understanding-motivations']

### Lane 2 cheat-sheet anchors
- `20260426T130145Zstab0`: ['boundaries', 'inversion', 'power-dynamics', 'principal-agent-problem', 'problem-framing-and-reframing']
- `20260426T130434Zstab1`: ['active-listening', 'boundaries', 'game-theory-payoffs', 'power-dynamics', 'scientific-method-evidence-testing']
- `20260426T130647Zstab2`: ['base-rates', 'empathy', 'endowment-effect', 'opportunity-cost', 'principal-agent-problem']

### Lane 3 reframings
- `20260426T130145Zstab0`: ['reframing-perspective', 'second-order-thinking']
- `20260426T130434Zstab1`: ['reframing-perspective', 'second-order-thinking']
- `20260426T130647Zstab2`: ['counterfactual-reasoning', 'reframing-perspective']

### Lane 4 gap dims
- `20260426T130145Zstab0`: ['existing-vs-new', 'information-quality', 'resource-allocation', 'risk-response']
- `20260426T130434Zstab1`: ['information-quality', 'resource-allocation', 'risk-response', 'timing-sequencing']
- `20260426T130647Zstab2`: ['information-quality', 'resource-allocation', 'risk-response', 'timing-sequencing', 'uncertainty-type']

## Cost per run (boundary-call tokens, lower bound when embeddings on)

| Run | Calls | Prompt tok | Completion tok | Total tok | Embedding-expansion observed |
|---|---|---|---|---|---|
| `20260426T130145Zstab0` | 26 | 200875 | 11289 | 212164 | 0 |
| `20260426T130434Zstab1` | 26 | 197284 | 10448 | 207732 | 0 |
| `20260426T130647Zstab2` | 25 | 186276 | 9913 | 196189 | 0 |

> Embedding-expansion calls (gpt-4o-mini, temp=0.7) bypass `BoundaryClient` tracing — reported here as 0 with a caveat. Treat boundary_only totals as a lower bound on Lane 2 cost when `embedding_mode = on`.

### Per-stage boundary token cost

#### `20260426T130145Zstab0`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 8329 |
| companion_verification_analogical | 1 | 8923 |
| companion_verification_causal | 1 | 9726 |
| companion_verification_counterfactual | 1 | 9905 |
| companion_verification_deductive | 1 | 9578 |
| companion_verification_diagnostic | 1 | 11107 |
| companion_verification_metacognitive | 1 | 10198 |
| companion_verification_probabilistic | 1 | 9327 |
| companion_verification_systems | 1 | 9922 |
| frame_extraction | 1 | 7886 |
| frame_reframing | 1 | 1860 |
| pass1_cluster_authority | 1 | 7979 |
| pass1_cluster_availability | 1 | 7676 |
| pass1_cluster_closure | 1 | 7903 |
| pass1_cluster_incentive | 1 | 7673 |
| pass1_cluster_residual | 1 | 7628 |
| pass1_cluster_self_regard | 1 | 7672 |
| pass2 | 7 | 55190 |
| structural_coverage_classification | 1 | 6841 |
| structural_coverage_detection | 1 | 6841 |

#### `20260426T130434Zstab1`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 7847 |
| companion_verification_analogical | 1 | 8442 |
| companion_verification_causal | 1 | 9299 |
| companion_verification_counterfactual | 1 | 9499 |
| companion_verification_deductive | 1 | 8872 |
| companion_verification_diagnostic | 1 | 11071 |
| companion_verification_metacognitive | 1 | 9516 |
| companion_verification_probabilistic | 1 | 8746 |
| companion_verification_systems | 1 | 9594 |
| frame_extraction | 1 | 7673 |
| frame_reframing | 1 | 1452 |
| pass1_cluster_authority | 1 | 8000 |
| pass1_cluster_availability | 1 | 7734 |
| pass1_cluster_closure | 1 | 7912 |
| pass1_cluster_incentive | 1 | 7679 |
| pass1_cluster_residual | 1 | 7628 |
| pass1_cluster_self_regard | 1 | 7713 |
| pass2 | 7 | 55341 |
| structural_coverage_classification | 1 | 6857 |
| structural_coverage_detection | 1 | 6857 |

#### `20260426T130647Zstab2`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 7552 |
| companion_verification_analogical | 1 | 8206 |
| companion_verification_causal | 1 | 8680 |
| companion_verification_counterfactual | 1 | 9029 |
| companion_verification_deductive | 1 | 8705 |
| companion_verification_diagnostic | 1 | 10383 |
| companion_verification_metacognitive | 1 | 9077 |
| companion_verification_probabilistic | 1 | 8559 |
| companion_verification_systems | 1 | 8794 |
| frame_extraction | 1 | 7800 |
| frame_reframing | 1 | 1613 |
| pass1_cluster_authority | 1 | 7984 |
| pass1_cluster_availability | 1 | 7674 |
| pass1_cluster_closure | 1 | 7909 |
| pass1_cluster_incentive | 1 | 7670 |
| pass1_cluster_residual | 1 | 7628 |
| pass1_cluster_self_regard | 1 | 7699 |
| pass2 | 6 | 47281 |
| structural_coverage_classification | 1 | 6973 |
| structural_coverage_detection | 1 | 6973 |
