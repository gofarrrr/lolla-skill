# Stability report — marcus-equity-prb-on

Generated: 2026-04-26T12:21:05Z
Runs: 3
Run IDs: 20260426T122105Zstab0, 20260426T122219Zstab1, 20260426T122331Zstab2
Prompt versions consistent across runs: True

## Per-stage stability (Jaccard)

> 1.0 is a WARNING, not a target — signals a specialist that stopped doing semantic judgment. Acceptance is a threshold band: stability moved up from baseline, no neighboring stage regressed, qualitative review confirms cards still do structural work.

| Stage | Mean | Min | Max |
|---|---|---|---|
| Pass 1 (tendencies) | 0.87 | 0.80 | 1.00 |
| Lane 2 — fingerprint moves | 0.00 | 0.00 | 0.00 |
| Lane 2 — recalled candidates | 0.71 | 0.69 | 0.74 |
| Lane 2 — accepted (pre-cap) | 0.30 | 0.25 | 0.37 |
| Lane 2 — shared-avail. accept agreement | 0.32 | 0.26 | 0.39 |
| Lane 2 — detected (post-cap) | 0.37 | 0.25 | 0.43 |
| Lane 2 — capped (top-5 drops) | 0.13 | 0.07 | 0.18 |
| Lane 2 (cheat-sheet anchors) | 0.37 | 0.25 | 0.43 |
| Lane 3 (reframings) | 0.44 | 0.33 | 0.50 |
| Lane 4 (gap dims) | 0.67 | 0.50 | 1.00 |

Embedding mode per run: ['on', 'on', 'on']  ·  consistent: True

### Recall-source distribution per run

| Run | keyword | embedding | both | other |
|---|---|---|---|---|
| `20260426T122105Zstab0` | 60 | 0 | 0 | 0 |
| `20260426T122219Zstab1` | 60 | 0 | 0 | 0 |
| `20260426T122331Zstab2` | 60 | 0 | 0 | 0 |

## Step 6 anchor naming (per-run)

| Run | Named | Total | Rate |
|---|---|---|---|
| `20260426T122105Zstab0` | (no revised_answer) | — | — |
| `20260426T122219Zstab1` | (no revised_answer) | — | — |
| `20260426T122331Zstab2` | (no revised_answer) | — | — |

## Per-run item diff

### Pass 1 tendencies
- `20260426T122105Zstab0`: ['availability-misweighing-tendency', 'contrast-misreaction-tendency', 'deprival-superreaction-tendency', 'liking-loving-tendency', 'reward-and-punishment-superresponse-tendency']
- `20260426T122219Zstab1`: ['availability-misweighing-tendency', 'contrast-misreaction-tendency', 'deprival-superreaction-tendency', 'liking-loving-tendency', 'reward-and-punishment-superresponse-tendency']
- `20260426T122331Zstab2`: ['availability-misweighing-tendency', 'deprival-superreaction-tendency', 'liking-loving-tendency', 'reward-and-punishment-superresponse-tendency']

### Lane 2 fingerprint moves
- `20260426T122105Zstab0`: ['differentiate the current situation from past negative experiences by highlighting unique scale of impact and non-interchangeability of the individual.', 'identify core motivation behind the ask by distinguishing between financial compensation and desire for strategic influence.', 'perform expected value calculation comparing equity dilution cost against quantified downside of departure and upside of retained growth.', 'propose risk-mitigated structures using vesting, governance limits, and repurchase rights to address fears of premature or permanent dilution.', 'quantify the true cost of key personnel departure by estimating the valuation gap between business continuity and disruption scenarios.', 'recognize pattern of resistance to core ask as signal of deeper incompatibility, prioritizing alignment over retention tactics.', 'reframe strategic opportunity by separating idea merit from ownership emotions and proposing bounded validation to minimize risk.']
- `20260426T122219Zstab1`: ['align incentives by matching proposed solutions to the actual underlying motivation rather than surface-level alternatives', 'differentiate the current situation from past negative experiences by highlighting unique scale of impact and non-interchangeability', 'prioritize radical honesty and clarity over tactical offers to resolve emotional standoff and alter decision trajectory', 'propose bounded experiments to validate high-upside ideas while mitigating risk through time-bound, low-cost testing', 'quantify the true cost of key personnel departure by estimating the valuation gap between retention and loss scenarios', 'recommend structural safeguards in equity grants to protect against common partnership failure modes like early departure or ip theft', 'reframe emotional ownership claims by attributing current company value to joint contributions rather than solo founder effort']
- `20260426T122331Zstab2`: ['differentiate marcus from other employees like tom by highlighting his unique, non-interchangeable contributions, dismissing slippery slope precedent concerns.', "interpret marcus's ask as seeking ownership and voice rather than cash, rejecting cash-based alternatives like bonuses or profit-sharing as misaligned with his motivations.", "link the platform idea to marcus's disengagement and equity ask, framing it as a strategic vision test rather than a side project, with departure posing competitive threat.", 'propose specific structural safeguards like vesting, governance limits, ip clauses, and buyback to mitigate risks of partnership while enabling alignment.', "quantify the true cost of marcus's departure by estimating the valuation gap between the business with and without him, framing equity as protection against massive downside rather than a giveaway.", "recognize user's pattern of proposing cash alternatives as avoidance of core ownership question, forcing decision on willingness to partner.", "recommend bounded experimentation on the platform to validate without full commitment, using low-cost sprint to generate data and signal value in marcus's idea."]

### Lane 2 recalled candidates
- `20260426T122105Zstab0`: ['active-listening', 'aleatory-epistemic-uncertainty-recognition', 'algorithmic-thinking', 'association', 'base-rates', 'boundaries', 'calculated-risk-taking', 'causal-attribution-resistance', 'chain-of-verification', 'commitment-bias', 'confidence-calibration', 'cultural-intelligence', 'delays', 'dunning-kruger-effect', 'einstellung-effect', 'empathy', 'endowment-effect', 'feedback-loops', 'feynman-technique', 'game-theory-payoffs', 'information-asymmetry', 'information-theory', 'intellectual-humility', 'inversion', 'jobs-to-be-done', 'lean-startup-methodology', 'learning-curve', 'liking-principle', 'moral-hazard', 'non-violent-communication', 'obligations-controls-mapping', 'opportunity-cost', 'optimization-theory', 'optionality', 'perceptual-learning', 'power-dynamics', 'premortem', 'principal-agent-problem', 'prisoners-dilemma', 'probabilistic-thinking', 'problem-framing-and-reframing', 'psychological-safety', 'rationalization', 'reasoning-mode-router', 'reciprocity-principle', 'representativeness-heuristic', 'root-cause-analysis', 'scientific-method-evidence-testing', 'second-order-thinking', 'signaling', 'social-proof', 'specialization', 'statistical-discipline', 'status-quo-bias', 'sunk-cost-fallacy', 'systems-thinking', 'time-tested-validation', 'trade-offs', 'usability-heuristics', 'user-centered-design']
- `20260426T122219Zstab1`: ['abstraction', 'active-listening', 'aleatory-epistemic-uncertainty-recognition', 'algorithmic-thinking', 'association', 'base-rates', 'bias-blind-spot', 'black-swan-events', 'boundaries', 'calculated-risk-taking', 'causal-attribution-resistance', 'chain-of-verification', 'cognitive-load-theory', 'commitment-bias', 'complex-adaptive-systems', 'einstellung-effect', 'emotional-intelligence', 'empathy', 'endowment-effect', 'experimentation', 'false-precision-avoidance', 'feedback-loops', 'feynman-technique', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'information-theory', 'intellectual-humility', 'inversion', 'jobs-to-be-done', 'lean-startup-methodology', 'learning-curve', 'liking-principle', 'non-violent-communication', 'obligations-controls-mapping', 'opportunity-cost', 'optimization-theory', 'optionality', 'power-dynamics', 'premortem', 'principal-agent-problem', 'probabilistic-thinking', 'problem-framing-and-reframing', 'psychological-safety', 'rationalization', 'reasoning-mode-router', 'reciprocity-principle', 'representativeness-heuristic', 'root-cause-analysis', 'scientific-method-evidence-testing', 'second-order-thinking', 'signaling', 'social-proof', 'specialization', 'statistical-discipline', 'status-quo-bias', 'sunk-cost-fallacy', 'systems-thinking', 'tier-2-high-value', 'user-centered-design']
- `20260426T122331Zstab2`: ['active-listening', 'agile-methodologies', 'aleatory-epistemic-uncertainty-recognition', 'algorithmic-thinking', 'association', 'base-rates', 'bias-blind-spot', 'boundaries', 'calculated-risk-taking', 'causal-attribution-resistance', 'chain-of-verification', 'cognitive-dissonance', 'commitment-bias', 'confidence-calibration', 'einstellung-effect', 'empathy', 'endowment-effect', 'experimentation', 'feedback-loops', 'feynman-technique', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'information-theory', 'intellectual-humility', 'inversion', 'lean-startup-methodology', 'learning-curve', 'liking-principle', 'non-violent-communication', 'obligations-controls-mapping', 'occams-razor', 'opportunity-cost', 'optionality', 'perceptual-learning', 'persistence-grit', 'persuasion-principles', 'power-dynamics', 'premortem', 'principal-agent-problem', 'probabilistic-thinking', 'problem-framing-and-reframing', 'psychological-safety', 'reasoning-mode-router', 'reciprocity-principle', 'representativeness-heuristic', 'root-cause-analysis', 'scientific-method-evidence-testing', 'second-order-thinking', 'signaling', 'social-proof', 'specialization', 'statistical-discipline', 'status-quo-bias', 'step-back', 'sunk-cost-fallacy', 'systems-thinking', 'tier-2-high-value', 'user-centered-design', 'wysiati']

### Lane 2 accepted (pre-cap)
- `20260426T122105Zstab0`: ['association', 'einstellung-effect', 'empathy', 'inversion', 'optimization-theory', 'optionality', 'principal-agent-problem', 'reasoning-mode-router', 'representativeness-heuristic', 'statistical-discipline', 'sunk-cost-fallacy']
- `20260426T122219Zstab1`: ['association', 'boundaries', 'einstellung-effect', 'endowment-effect', 'information-asymmetry', 'inversion', 'opportunity-cost', 'optimization-theory', 'power-dynamics', 'representativeness-heuristic', 'root-cause-analysis', 'tier-2-high-value']
- `20260426T122331Zstab2`: ['association', 'base-rates', 'boundaries', 'einstellung-effect', 'feedback-loops', 'game-theory-payoffs', 'inversion', 'opportunity-cost', 'power-dynamics', 'principal-agent-problem', 'psychological-safety', 'representativeness-heuristic', 'signaling', 'status-quo-bias']

### Lane 2 detected (post-cap)
- `20260426T122105Zstab0`: ['einstellung-effect', 'inversion', 'principal-agent-problem', 'representativeness-heuristic', 'sunk-cost-fallacy']
- `20260426T122219Zstab1`: ['boundaries', 'inversion', 'opportunity-cost', 'power-dynamics', 'representativeness-heuristic']
- `20260426T122331Zstab2`: ['game-theory-payoffs', 'inversion', 'opportunity-cost', 'principal-agent-problem', 'representativeness-heuristic']

### Lane 2 capped (top-5 drops)
- `20260426T122105Zstab0`: ['association', 'empathy', 'optimization-theory', 'optionality', 'reasoning-mode-router', 'statistical-discipline']
- `20260426T122219Zstab1`: ['association', 'einstellung-effect', 'endowment-effect', 'information-asymmetry', 'optimization-theory', 'root-cause-analysis', 'tier-2-high-value']
- `20260426T122331Zstab2`: ['association', 'base-rates', 'boundaries', 'einstellung-effect', 'feedback-loops', 'power-dynamics', 'psychological-safety', 'signaling', 'status-quo-bias']

### Lane 2 cheat-sheet anchors
- `20260426T122105Zstab0`: ['einstellung-effect', 'inversion', 'principal-agent-problem', 'representativeness-heuristic', 'sunk-cost-fallacy']
- `20260426T122219Zstab1`: ['boundaries', 'inversion', 'opportunity-cost', 'power-dynamics', 'representativeness-heuristic']
- `20260426T122331Zstab2`: ['game-theory-payoffs', 'inversion', 'opportunity-cost', 'principal-agent-problem', 'representativeness-heuristic']

### Lane 3 reframings
- `20260426T122105Zstab0`: ['reframing-perspective']
- `20260426T122219Zstab1`: ['reframing-perspective', 'second-order-thinking']
- `20260426T122331Zstab2`: ['decision-trees', 'reframing-perspective']

### Lane 4 gap dims
- `20260426T122105Zstab0`: ['incentive-alignment', 'information-quality', 'resource-allocation', 'risk-response', 'stakeholder-alignment']
- `20260426T122219Zstab1`: ['information-quality', 'resource-allocation', 'risk-response', 'timing-sequencing']
- `20260426T122331Zstab2`: ['information-quality', 'resource-allocation', 'risk-response', 'timing-sequencing']

## Cost per run (boundary-call tokens, lower bound when embeddings on)

| Run | Calls | Prompt tok | Completion tok | Total tok | Embedding-expansion observed |
|---|---|---|---|---|---|
| `20260426T122105Zstab0` | 27 | 199684 | 9964 | 209648 | 0 |
| `20260426T122219Zstab1` | 27 | 204358 | 11107 | 215465 | 0 |
| `20260426T122331Zstab2` | 25 | 191442 | 12692 | 204134 | 0 |

> Embedding-expansion calls (gpt-4o-mini, temp=0.7) bypass `BoundaryClient` tracing — reported here as 0 with a caveat. Treat boundary_only totals as a lower bound on Lane 2 cost when `embedding_mode = on`.

### Per-stage boundary token cost

#### `20260426T122105Zstab0`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 7433 |
| companion_verification_analogical | 1 | 7922 |
| companion_verification_causal | 1 | 8773 |
| companion_verification_counterfactual | 1 | 8675 |
| companion_verification_deductive | 1 | 8468 |
| companion_verification_diagnostic | 1 | 9739 |
| companion_verification_metacognitive | 1 | 8715 |
| companion_verification_probabilistic | 1 | 8425 |
| companion_verification_systems | 1 | 8892 |
| frame_extraction | 1 | 7748 |
| frame_reframing | 1 | 1107 |
| pass1_cluster_authority | 1 | 7994 |
| pass1_cluster_availability | 1 | 7682 |
| pass1_cluster_closure | 1 | 7922 |
| pass1_cluster_incentive | 1 | 7673 |
| pass1_cluster_residual | 1 | 7628 |
| pass1_cluster_self_regard | 1 | 7727 |
| pass2 | 8 | 63183 |
| structural_coverage_classification | 1 | 6971 |
| structural_coverage_detection | 1 | 6971 |

#### `20260426T122219Zstab1`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 8134 |
| companion_verification_analogical | 1 | 8559 |
| companion_verification_causal | 1 | 9526 |
| companion_verification_counterfactual | 1 | 9136 |
| companion_verification_deductive | 1 | 9294 |
| companion_verification_diagnostic | 1 | 10368 |
| companion_verification_metacognitive | 1 | 9477 |
| companion_verification_probabilistic | 1 | 8933 |
| companion_verification_systems | 1 | 9600 |
| frame_extraction | 1 | 7677 |
| frame_reframing | 1 | 1450 |
| pass1_cluster_authority | 1 | 8022 |
| pass1_cluster_availability | 1 | 7718 |
| pass1_cluster_closure | 1 | 7911 |
| pass1_cluster_incentive | 1 | 7717 |
| pass1_cluster_residual | 1 | 7628 |
| pass1_cluster_self_regard | 1 | 7672 |
| pass2 | 8 | 62777 |
| structural_coverage_classification | 1 | 6933 |
| structural_coverage_detection | 1 | 6933 |

#### `20260426T122331Zstab2`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 8396 |
| companion_verification_analogical | 1 | 8812 |
| companion_verification_causal | 1 | 10217 |
| companion_verification_counterfactual | 1 | 9635 |
| companion_verification_deductive | 1 | 9414 |
| companion_verification_diagnostic | 1 | 10957 |
| companion_verification_metacognitive | 1 | 9735 |
| companion_verification_probabilistic | 1 | 9763 |
| companion_verification_systems | 1 | 9863 |
| frame_extraction | 1 | 7862 |
| frame_reframing | 1 | 1744 |
| pass1_cluster_authority | 1 | 7997 |
| pass1_cluster_availability | 1 | 7715 |
| pass1_cluster_closure | 1 | 7900 |
| pass1_cluster_incentive | 1 | 7684 |
| pass1_cluster_residual | 1 | 7628 |
| pass1_cluster_self_regard | 1 | 7713 |
| pass2 | 6 | 47239 |
| structural_coverage_classification | 1 | 6930 |
| structural_coverage_detection | 1 | 6930 |
