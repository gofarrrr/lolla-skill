# Stability report — mid-level-consultant-decides-lane2-off

Generated: 2026-04-26T10:53:21Z
Runs: 3
Run IDs: 20260426T105321Zstab0, 20260426T105422Zstab1, 20260426T105522Zstab2
Prompt versions consistent across runs: True

## Per-stage stability (Jaccard)

> 1.0 is a WARNING, not a target — signals a specialist that stopped doing semantic judgment. Acceptance is a threshold band: stability moved up from baseline, no neighboring stage regressed, qualitative review confirms cards still do structural work.

| Stage | Mean | Min | Max |
|---|---|---|---|
| Pass 1 (tendencies) | 1.00 | 1.00 | 1.00 |
| Lane 2 — fingerprint moves | 0.05 | 0.00 | 0.08 |
| Lane 2 — recalled candidates | 0.68 | 0.64 | 0.71 |
| Lane 2 — accepted (pre-cap) | 0.16 | 0.00 | 0.33 |
| Lane 2 — detected (post-cap) | 0.16 | 0.00 | 0.33 |
| Lane 2 — capped (top-5 drops) | 1.00 | 1.00 | 1.00 |
| Lane 2 (cheat-sheet anchors) | 0.16 | 0.00 | 0.33 |
| Lane 3 (reframings) | 0.56 | 0.33 | 1.00 |
| Lane 4 (gap dims) | 0.31 | 0.17 | 0.60 |

Embedding mode per run: ['off', 'off', 'off']  ·  consistent: True

### Recall-source distribution per run

| Run | keyword | embedding | both | other |
|---|---|---|---|---|
| `20260426T105321Zstab0` | 60 | 0 | 0 | 0 |
| `20260426T105422Zstab1` | 60 | 0 | 0 | 0 |
| `20260426T105522Zstab2` | 60 | 0 | 0 | 0 |

## Step 6 anchor naming (per-run)

| Run | Named | Total | Rate |
|---|---|---|---|
| `20260426T105321Zstab0` | (no revised_answer) | — | — |
| `20260426T105422Zstab1` | (no revised_answer) | — | — |
| `20260426T105522Zstab2` | (no revised_answer) | — | — |

## Per-run item diff

### Pass 1 tendencies
- `20260426T105321Zstab0`: ['authority-misinfluence-tendency', 'reward-and-punishment-superresponse-tendency']
- `20260426T105422Zstab1`: ['authority-misinfluence-tendency', 'reward-and-punishment-superresponse-tendency']
- `20260426T105522Zstab2`: ['authority-misinfluence-tendency', 'reward-and-punishment-superresponse-tendency']

### Lane 2 fingerprint moves
- `20260426T105321Zstab0`: ['apply conditional filter criteria to compare internal vs external reporting paths', 'assess evidential strength by probing for confirmatory details to determine decision weight', 'isolate current obligation from extraneous prior actors to focus decision scope', 'sequence prioritized actions with timeline and behavioral constraints for risk minimization', 'structure decision into balanced multi-dimensional framework of risks and stakes', 'threshold confidence calibration to select optimal reporting channel', 'weigh observed facts against benign alternatives to gauge likelihood of misconduct']
- `20260426T105422Zstab1`: ['apply conditional filter to compare internal vs external reporting based on independence, track record, and urgency', 'assess evidential strength by probing for confirmatory details to determine decision weight', "isolate personal obligation from others' past decisions to avoid decision displacement", 'sequence actions into prioritized timeline balancing documentation, counsel, and normalcy', 'structure decision into triadic framework of legal, career, and moral dimensions', 'threshold confidence calibration to select reporting path', 'weigh likelihood of obstruction against benign alternatives based on contextual anomalies']
- `20260426T105522Zstab2`: ['assess evidential strength by probing for specifics to determine decision weight', 'compare internal vs external reporting using conditional criteria and confidence thresholds', "isolate user's obligation from others' past actions to focus on current decision", 'project long-term outcomes across probabilistic scenarios to set realistic expectations', 'sequence actions into prioritized timeline minimizing exposure and ensuring preparation', 'structure decision into balanced multi-dimensional framework of risks and stakes', 'weigh likelihood of misconduct against benign alternatives while acknowledging uncertainty']

### Lane 2 recalled candidates
- `20260426T105321Zstab0`: ['active-listening', 'agile-methodologies', 'aleatory-epistemic-uncertainty-recognition', 'authenticity', 'authority-bias', 'base-rates', 'bayesian', 'bias-blind-spot', 'boundaries', 'branch-solve-merge', 'calculated-risk-taking', 'chain-of-verification', 'checklists', 'cognitive-dissonance', 'commitment-bias', 'confidence-calibration', 'conjunction-fallacy', 'constraints', 'constructive-feedback-models', 'critical-mass', 'cultural-intelligence', 'curse-of-knowledge', 'dunning-kruger-effect', 'emotional-intelligence', 'expertise-reversal-effect', 'false-precision-avoidance', 'feedback-loops', 'feynman-technique', 'formal-reasoning', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'internal-locus-of-control', 'inversion', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'liking-principle', 'mental-simulation', 'meta-cognitive-reflection', 'obligations-controls-mapping', 'occams-razor', 'opportunity-cost', 'principal-agent-problem', 'probabilistic-thinking', 'prospect-theory', 'regression-to-the-mean', 'regulatory-horizon-scanning', 'representativeness-heuristic', 'root-cause-analysis', 'schema-acquisition', 'second-order-thinking', 'signaling', 'social-proof', 'specialization', 'step-back', 'sunk-cost-fallacy', 'understanding-motivations', 'wysiati']
- `20260426T105422Zstab1`: ['abstraction', 'active-listening', 'aleatory-epistemic-uncertainty-recognition', 'association', 'auditability-traceability', 'authenticity', 'authority-bias', 'base-rates', 'bayesian', 'bias-blind-spot', 'boundaries', 'branch-solve-merge', 'chain-of-thought', 'chain-of-verification', 'checklists', 'cognitive-dissonance', 'combinatorial-effects', 'commitment-bias', 'confidence-calibration', 'constructive-feedback-models', 'critical-mass', 'cultural-intelligence', 'curse-of-knowledge', 'dunning-kruger-effect', 'emotional-intelligence', 'expertise-reversal-effect', 'false-precision-avoidance', 'feedback-loops', 'feynman-technique', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'inversion', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'margin-of-safety', 'mental-simulation', 'obligations-controls-mapping', 'occams-razor', 'opportunity-cost', 'optionality', 'probabilistic-thinking', 'prospect-theory', 'rationalization', 'reasoning-mode-router', 'regression-to-the-mean', 'regulatory-horizon-scanning', 'representativeness-heuristic', 'root-cause-analysis', 'second-order-thinking', 'social-proof', 'specialization', 'step-back', 'sunk-cost-fallacy', 'survivorship-bias', 'trade-offs', 'understanding-motivations', 'wysiati']
- `20260426T105522Zstab2`: ['abstraction', 'active-listening', 'aleatory-epistemic-uncertainty-recognition', 'authenticity', 'base-rates', 'bayesian', 'bias-blind-spot', 'boundaries', 'branch-solve-merge', 'calculated-risk-taking', 'chain-of-verification', 'checklists', 'cognitive-dissonance', 'commitment-bias', 'constructive-feedback-models', 'critical-mass', 'cultural-intelligence', 'curse-of-knowledge', 'dunning-kruger-effect', 'emotional-intelligence', 'experimentation', 'expertise-reversal-effect', 'false-precision-avoidance', 'feedback-loops', 'five-whys-method', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'internal-locus-of-control', 'inversion', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'margin-of-safety', 'mental-simulation', 'moral-hazard', 'obligations-controls-mapping', 'occams-razor', 'opportunity-cost', 'optimism-bias-and-planning-fallacy', 'optionality', 'premortem', 'principal-agent-problem', 'probabilistic-thinking', 'prospect-theory', 'rationalization', 'regression-to-the-mean', 'regulatory-horizon-scanning', 'representativeness-heuristic', 'risk-assessment', 'root-cause-analysis', 'second-order-thinking', 'social-proof', 'specialization', 'sunk-cost-fallacy', 'survivorship-bias', 'trade-offs', 'user-centered-design', 'wysiati']

### Lane 2 accepted (pre-cap)
- `20260426T105321Zstab0`: ['chain-of-verification', 'confidence-calibration', 'occams-razor']
- `20260426T105422Zstab1`: ['confidence-calibration']
- `20260426T105522Zstab2`: ['chain-of-verification', 'information-asymmetry', 'principal-agent-problem', 'probabilistic-thinking', 'wysiati']

### Lane 2 detected (post-cap)
- `20260426T105321Zstab0`: ['chain-of-verification', 'confidence-calibration', 'occams-razor']
- `20260426T105422Zstab1`: ['confidence-calibration']
- `20260426T105522Zstab2`: ['chain-of-verification', 'information-asymmetry', 'principal-agent-problem', 'probabilistic-thinking', 'wysiati']

### Lane 2 capped (top-5 drops)
- `20260426T105321Zstab0`: []
- `20260426T105422Zstab1`: []
- `20260426T105522Zstab2`: []

### Lane 2 cheat-sheet anchors
- `20260426T105321Zstab0`: ['chain-of-verification', 'confidence-calibration', 'occams-razor']
- `20260426T105422Zstab1`: ['confidence-calibration']
- `20260426T105522Zstab2`: ['chain-of-verification', 'information-asymmetry', 'principal-agent-problem', 'probabilistic-thinking', 'wysiati']

### Lane 3 reframings
- `20260426T105321Zstab0`: ['decision-trees', 'optionality']
- `20260426T105422Zstab1`: ['boundaries', 'decision-trees']
- `20260426T105522Zstab2`: ['decision-trees', 'optionality']

### Lane 4 gap dims
- `20260426T105321Zstab0`: ['incentive-alignment', 'information-quality', 'stakeholder-alignment', 'uncertainty-type']
- `20260426T105422Zstab1`: ['competitive-dynamics', 'incentive-alignment', 'stakeholder-alignment', 'uncertainty-type']
- `20260426T105522Zstab2`: ['commitment-reversibility', 'risk-response', 'stakeholder-alignment']

## Cost per run (boundary-call tokens, lower bound when embeddings on)

| Run | Calls | Prompt tok | Completion tok | Total tok | Embedding-expansion observed |
|---|---|---|---|---|---|
| `20260426T105321Zstab0` | 15 | 78061 | 5841 | 83902 | 0 |
| `20260426T105422Zstab1` | 15 | 78127 | 5646 | 83773 | 0 |
| `20260426T105522Zstab2` | 14 | 72513 | 5846 | 78359 | 0 |

> Embedding-expansion calls (gpt-4o-mini, temp=0.7) bypass `BoundaryClient` tracing — reported here as 0 with a caveat. Treat boundary_only totals as a lower bound on Lane 2 cost when `embedding_mode = on`.

### Per-stage boundary token cost

#### `20260426T105321Zstab0`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 5143 |
| companion_verification | 1 | 11089 |
| frame_extraction | 1 | 5641 |
| frame_reframing | 1 | 1313 |
| pass1_cluster_authority | 1 | 5959 |
| pass1_cluster_availability | 1 | 5536 |
| pass1_cluster_closure | 1 | 5780 |
| pass1_cluster_incentive | 1 | 5574 |
| pass1_cluster_residual | 1 | 5570 |
| pass1_cluster_self_regard | 1 | 5614 |
| pass2 | 3 | 16901 |
| structural_coverage_classification | 1 | 4891 |
| structural_coverage_detection | 1 | 4891 |

#### `20260426T105422Zstab1`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 5278 |
| companion_verification | 1 | 10939 |
| frame_extraction | 1 | 5617 |
| frame_reframing | 1 | 1312 |
| pass1_cluster_authority | 1 | 5947 |
| pass1_cluster_availability | 1 | 5538 |
| pass1_cluster_closure | 1 | 5770 |
| pass1_cluster_incentive | 1 | 5580 |
| pass1_cluster_residual | 1 | 5570 |
| pass1_cluster_self_regard | 1 | 5614 |
| pass2 | 3 | 16964 |
| structural_coverage_classification | 1 | 4822 |
| structural_coverage_detection | 1 | 4822 |

#### `20260426T105522Zstab2`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 5211 |
| companion_verification | 1 | 11578 |
| frame_extraction | 1 | 5569 |
| frame_reframing | 1 | 1085 |
| pass1_cluster_authority | 1 | 5970 |
| pass1_cluster_availability | 1 | 5533 |
| pass1_cluster_closure | 1 | 5783 |
| pass1_cluster_incentive | 1 | 5577 |
| pass1_cluster_residual | 1 | 5570 |
| pass1_cluster_self_regard | 1 | 5656 |
| pass2 | 2 | 11383 |
| structural_coverage_classification | 1 | 4722 |
| structural_coverage_detection | 1 | 4722 |
