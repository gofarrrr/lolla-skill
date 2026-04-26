# Stability report — marcus-equity-lane2-off

Generated: 2026-04-26T10:45:46Z
Runs: 3
Run IDs: 20260426T104546Zstab0, 20260426T104700Zstab1, 20260426T104823Zstab2
Prompt versions consistent across runs: True

## Per-stage stability (Jaccard)

> 1.0 is a WARNING, not a target — signals a specialist that stopped doing semantic judgment. Acceptance is a threshold band: stability moved up from baseline, no neighboring stage regressed, qualitative review confirms cards still do structural work.

| Stage | Mean | Min | Max |
|---|---|---|---|
| Pass 1 (tendencies) | 0.87 | 0.80 | 1.00 |
| Lane 2 — fingerprint moves | 0.03 | 0.00 | 0.08 |
| Lane 2 — recalled candidates | 0.70 | 0.67 | 0.76 |
| Lane 2 — accepted (pre-cap) | 0.13 | 0.00 | 0.40 |
| Lane 2 — detected (post-cap) | 0.13 | 0.00 | 0.40 |
| Lane 2 — capped (top-5 drops) | 1.00 | 1.00 | 1.00 |
| Lane 2 (cheat-sheet anchors) | 0.13 | 0.00 | 0.40 |
| Lane 3 (reframings) | 0.56 | 0.33 | 1.00 |
| Lane 4 (gap dims) | 0.63 | 0.50 | 0.80 |

Embedding mode per run: ['off', 'off', 'off']  ·  consistent: True

### Recall-source distribution per run

| Run | keyword | embedding | both | other |
|---|---|---|---|---|
| `20260426T104546Zstab0` | 60 | 0 | 0 | 0 |
| `20260426T104700Zstab1` | 60 | 0 | 0 | 0 |
| `20260426T104823Zstab2` | 60 | 0 | 0 | 0 |

## Step 6 anchor naming (per-run)

| Run | Named | Total | Rate |
|---|---|---|---|
| `20260426T104546Zstab0` | (no revised_answer) | — | — |
| `20260426T104700Zstab1` | (no revised_answer) | — | — |
| `20260426T104823Zstab2` | (no revised_answer) | — | — |

## Per-run item diff

### Pass 1 tendencies
- `20260426T104546Zstab0`: ['availability-misweighing-tendency', 'contrast-misreaction-tendency', 'deprival-superreaction-tendency', 'liking-loving-tendency', 'reward-and-punishment-superresponse-tendency']
- `20260426T104700Zstab1`: ['availability-misweighing-tendency', 'contrast-misreaction-tendency', 'deprival-superreaction-tendency', 'liking-loving-tendency', 'reward-and-punishment-superresponse-tendency']
- `20260426T104823Zstab2`: ['availability-misweighing-tendency', 'contrast-misreaction-tendency', 'deprival-superreaction-tendency', 'liking-loving-tendency']

### Lane 2 fingerprint moves
- `20260426T104546Zstab0`: ['address slippery slope precedent concerns by establishing objective criteria that uniquely qualify the individual, preventing arbitrary demands.', 'differentiate the current situation from past negative experiences by highlighting unique scale of impact and non-interchangeability of the individual.', 'perform scenario-based valuation comparison showing that equity dilution cost is minor relative to downside risk of departure and upside of alignment.', 'propose bounded experimentation to validate product idea with minimal risk, focusing on customer signals over full commitment.', 'quantify the true cost of key personnel departure by estimating the valuation gap between the business with and without the individual, treating retention as payment for preserved value rather than a giveaway.', 'reframe emotional resistance by resolving apparent contradictions between acknowledged importance and denial of deserved equity through shared contribution to growth.', 'reject cash-based retention alternatives as misaligned with core ask for ownership and voice, using metaphor to illustrate inadequacy.']
- `20260426T104700Zstab1`: ["challenge emotional resistance by reconciling contradictions in user's valuation of marcus and proposing radical honesty to reset the relationship.", 'differentiate marcus from other employees like tom by highlighting his unique, irreplaceable contributions and risk profile, dismissing slippery slope precedent concerns.', "interpret marcus's equity ask as driven by desire for ownership, voice, and strategic influence rather than cash, making financial incentives like bonuses inadequate.", "link the platform idea to marcus's disengagement and equity ask, framing it as a test of his strategic value and opportunity for business transformation, not just retention.", 'propose specific structural safeguards like vesting, governance limits, ip clauses, and buyback rights to mitigate risks of partnership while enabling alignment.', "quantify the true cost of marcus's departure by estimating the valuation gap between the business with and without him, framing equity as protection against massive downside risk rather than a giveaway.", 'recommend bounded experimentation on the platform to validate potential without full commitment, using low-cost tests to de-risk the idea.']
- `20260426T104823Zstab2`: ['address precedent concerns by establishing a clear, unique performance bar that differentiates the individual from others.', 'differentiate the current situation from past negative experiences by highlighting unique scale of impact and non-interchangeability of the individual.', 'perform scenario analysis comparing exit value with equity grant versus departure downside, including multiple impacts like ebitda drop and competitive threat.', 'propose structured risk mitigation through vesting, governance limits, ip clauses, and buyback mechanisms to enable partnership without full exposure.', 'quantify the true cost of key personnel departure by estimating the valuation gap between business with and without the individual, framing equity as protection against downside risk rather than a giveaway.', 'reframe emotional ownership claim by attributing current company value to joint contributions, resolving contradiction between indispensability and non-deserving status.', "reject cash-based retention alternatives by aligning solution to the individual's stated non-monetary motivations for ownership and voice."]

### Lane 2 recalled candidates
- `20260426T104546Zstab0`: ['active-listening', 'agile-methodologies', 'aleatory-epistemic-uncertainty-recognition', 'algorithmic-thinking', 'association', 'base-rates', 'black-swan-events', 'boundaries', 'calculated-risk-taking', 'causal-attribution-resistance', 'chain-of-verification', 'cognitive-dissonance', 'commitment-bias', 'complexity-bias-resistance', 'confidence-calibration', 'cultural-intelligence', 'delays', 'dunning-kruger-effect', 'einstellung-effect', 'empathy', 'endowment-effect', 'experimentation', 'feedback-loops', 'feynman-technique', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'inversion', 'jobs-to-be-done', 'lean-startup-methodology', 'learning-curve', 'liking-principle', 'non-violent-communication', 'obligations-controls-mapping', 'occams-razor', 'opportunity-cost', 'optionality', 'power-dynamics', 'premortem', 'principal-agent-problem', 'probabilistic-thinking', 'problem-framing-and-reframing', 'psychological-safety', 'reasoning-mode-router', 'reciprocity-principle', 'representativeness-heuristic', 'root-cause-analysis', 'scientific-method-evidence-testing', 'signaling', 'social-proof', 'statistical-discipline', 'status-quo-bias', 'step-back', 'sunk-cost-fallacy', 'systems-thinking', 'theory-of-constraints', 'trade-offs', 'usability-heuristics', 'user-centered-design']
- `20260426T104700Zstab1`: ['active-listening', 'agile-methodologies', 'aleatory-epistemic-uncertainty-recognition', 'algorithmic-thinking', 'association', 'base-rates', 'bias-blind-spot', 'boundaries', 'calculated-risk-taking', 'causal-attribution-resistance', 'chain-of-verification', 'cognitive-dissonance', 'commitment-bias', 'comparative-political-systems-analysis', 'complex-adaptive-systems', 'complexity-bias-resistance', 'cultural-intelligence', 'einstellung-effect', 'emotional-intelligence', 'empathy', 'endowment-effect', 'experimentation', 'feedback-loops', 'feynman-technique', 'game-theory-payoffs', 'information-asymmetry', 'information-theory', 'intellectual-humility', 'inversion', 'lean-startup-methodology', 'learning-curve', 'liking-principle', 'non-violent-communication', 'opportunity-cost', 'optionality', 'persistence-grit', 'power-dynamics', 'premortem', 'principal-agent-problem', 'prisoners-dilemma', 'probabilistic-thinking', 'problem-framing-and-reframing', 'prospect-theory', 'psychological-safety', 'reasoning-mode-router', 'reciprocity-principle', 'representativeness-heuristic', 'root-cause-analysis', 'scientific-method-evidence-testing', 'signaling', 'social-proof', 'specialization', 'statistical-discipline', 'step-back', 'sunk-cost-fallacy', 'systems-thinking', 'tier-2-high-value', 'time-tested-validation', 'user-centered-design', 'wysiati']
- `20260426T104823Zstab2`: ['active-listening', 'agile-methodologies', 'aleatory-epistemic-uncertainty-recognition', 'algorithmic-thinking', 'base-rates', 'black-swan-events', 'boundaries', 'calculated-risk-taking', 'chain-of-verification', 'commitment-bias', 'cultural-intelligence', 'dunning-kruger-effect', 'einstellung-effect', 'empathy', 'endowment-effect', 'experimentation', 'feedback-loops', 'feynman-technique', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'inversion', 'lean-startup-methodology', 'learning-curve', 'moral-hazard', 'non-violent-communication', 'obligations-controls-mapping', 'occams-razor', 'opportunity-cost', 'optionality', 'power-dynamics', 'premortem', 'principal-agent-problem', 'prisoners-dilemma', 'probabilistic-thinking', 'problem-framing-and-reframing', 'prospect-theory', 'psychological-safety', 'reasoning-mode-router', 'reciprocity-principle', 'red-queen-effect', 'representativeness-heuristic', 'root-cause-analysis', 'scientific-method-evidence-testing', 'second-order-thinking', 'signaling', 'social-proof', 'specialization', 'statistical-discipline', 'status-quo-bias', 'step-back', 'sunk-cost-fallacy', 'systems-thinking', 'theory-of-constraints', 'tier-2-high-value', 'trade-offs', 'usability-heuristics', 'user-centered-design', 'wysiati']

### Lane 2 accepted (pre-cap)
- `20260426T104546Zstab0`: ['einstellung-effect', 'endowment-effect', 'opportunity-cost', 'representativeness-heuristic']
- `20260426T104700Zstab1`: []
- `20260426T104823Zstab2`: ['endowment-effect', 'representativeness-heuristic', 'sunk-cost-fallacy']

### Lane 2 detected (post-cap)
- `20260426T104546Zstab0`: ['einstellung-effect', 'endowment-effect', 'opportunity-cost', 'representativeness-heuristic']
- `20260426T104700Zstab1`: []
- `20260426T104823Zstab2`: ['endowment-effect', 'representativeness-heuristic', 'sunk-cost-fallacy']

### Lane 2 capped (top-5 drops)
- `20260426T104546Zstab0`: []
- `20260426T104700Zstab1`: []
- `20260426T104823Zstab2`: []

### Lane 2 cheat-sheet anchors
- `20260426T104546Zstab0`: ['einstellung-effect', 'endowment-effect', 'opportunity-cost', 'representativeness-heuristic']
- `20260426T104700Zstab1`: []
- `20260426T104823Zstab2`: ['endowment-effect', 'representativeness-heuristic', 'sunk-cost-fallacy']

### Lane 3 reframings
- `20260426T104546Zstab0`: ['reframing-perspective', 'second-order-thinking']
- `20260426T104700Zstab1`: ['reframing-perspective', 'second-order-thinking']
- `20260426T104823Zstab2`: ['reframing-perspective', 'systems-thinking']

### Lane 4 gap dims
- `20260426T104546Zstab0`: ['information-quality', 'resource-allocation', 'risk-response', 'stakeholder-alignment']
- `20260426T104700Zstab1`: ['information-quality', 'resource-allocation', 'risk-response', 'timing-sequencing']
- `20260426T104823Zstab2`: ['information-quality', 'resource-allocation', 'risk-response', 'stakeholder-alignment', 'uncertainty-type']

## Cost per run (boundary-call tokens, lower bound when embeddings on)

| Run | Calls | Prompt tok | Completion tok | Total tok | Embedding-expansion observed |
|---|---|---|---|---|---|
| `20260426T104546Zstab0` | 19 | 137702 | 7112 | 144814 | 0 |
| `20260426T104700Zstab1` | 18 | 130538 | 7330 | 137868 | 0 |
| `20260426T104823Zstab2` | 19 | 138183 | 7593 | 145776 | 0 |

> Embedding-expansion calls (gpt-4o-mini, temp=0.7) bypass `BoundaryClient` tracing — reported here as 0 with a caveat. Treat boundary_only totals as a lower bound on Lane 2 cost when `embedding_mode = on`.

### Per-stage boundary token cost

#### `20260426T104546Zstab0`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 7354 |
| companion_verification | 1 | 13188 |
| frame_extraction | 1 | 7786 |
| frame_reframing | 1 | 1547 |
| pass1_cluster_authority | 1 | 8018 |
| pass1_cluster_availability | 1 | 7678 |
| pass1_cluster_closure | 1 | 7917 |
| pass1_cluster_incentive | 1 | 7730 |
| pass1_cluster_residual | 1 | 7628 |
| pass1_cluster_self_regard | 1 | 7672 |
| pass2 | 7 | 54626 |
| structural_coverage_classification | 1 | 6835 |
| structural_coverage_detection | 1 | 6835 |

#### `20260426T104700Zstab1`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 7826 |
| companion_verification | 1 | 13333 |
| frame_extraction | 1 | 7745 |
| frame_reframing | 1 | 1586 |
| pass1_cluster_authority | 1 | 8012 |
| pass1_cluster_availability | 1 | 7719 |
| pass1_cluster_closure | 1 | 7888 |
| pass1_cluster_incentive | 1 | 7678 |
| pass1_cluster_residual | 1 | 7628 |
| pass1_cluster_self_regard | 1 | 7699 |
| pass2 | 6 | 47014 |
| structural_coverage_classification | 1 | 6870 |
| structural_coverage_detection | 1 | 6870 |

#### `20260426T104823Zstab2`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 7558 |
| companion_verification | 1 | 13668 |
| frame_extraction | 1 | 7677 |
| frame_reframing | 1 | 1444 |
| pass1_cluster_authority | 1 | 7984 |
| pass1_cluster_availability | 1 | 7705 |
| pass1_cluster_closure | 1 | 7865 |
| pass1_cluster_incentive | 1 | 7672 |
| pass1_cluster_residual | 1 | 7628 |
| pass1_cluster_self_regard | 1 | 7724 |
| pass2 | 7 | 54823 |
| structural_coverage_classification | 1 | 7014 |
| structural_coverage_detection | 1 | 7014 |
