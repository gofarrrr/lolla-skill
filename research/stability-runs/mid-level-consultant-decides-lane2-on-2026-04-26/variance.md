# Stability report — mid-level-consultant-decides-lane2-on

Generated: 2026-04-26T10:49:43Z
Runs: 3
Run IDs: 20260426T104943Zstab0, 20260426T105102Zstab1, 20260426T105211Zstab2
Prompt versions consistent across runs: True

## Per-stage stability (Jaccard)

> 1.0 is a WARNING, not a target — signals a specialist that stopped doing semantic judgment. Acceptance is a threshold band: stability moved up from baseline, no neighboring stage regressed, qualitative review confirms cards still do structural work.

| Stage | Mean | Min | Max |
|---|---|---|---|
| Pass 1 (tendencies) | 1.00 | 1.00 | 1.00 |
| Lane 2 — fingerprint moves | 0.00 | 0.00 | 0.00 |
| Lane 2 — recalled candidates | 0.72 | 0.67 | 0.76 |
| Lane 2 — accepted (pre-cap) | 0.22 | 0.00 | 0.40 |
| Lane 2 — detected (post-cap) | 0.22 | 0.00 | 0.40 |
| Lane 2 — capped (top-5 drops) | 1.00 | 1.00 | 1.00 |
| Lane 2 (cheat-sheet anchors) | 0.22 | 0.00 | 0.40 |
| Lane 3 (reframings) | 0.56 | 0.33 | 1.00 |
| Lane 4 (gap dims) | 0.83 | 0.75 | 1.00 |

Embedding mode per run: ['on', 'on', 'on']  ·  consistent: True

### Recall-source distribution per run

| Run | keyword | embedding | both | other |
|---|---|---|---|---|
| `20260426T104943Zstab0` | 60 | 0 | 0 | 0 |
| `20260426T105102Zstab1` | 60 | 0 | 0 | 0 |
| `20260426T105211Zstab2` | 60 | 0 | 0 | 0 |

## Step 6 anchor naming (per-run)

| Run | Named | Total | Rate |
|---|---|---|---|
| `20260426T104943Zstab0` | (no revised_answer) | — | — |
| `20260426T105102Zstab1` | (no revised_answer) | — | — |
| `20260426T105211Zstab2` | (no revised_answer) | — | — |

## Per-run item diff

### Pass 1 tendencies
- `20260426T104943Zstab0`: ['authority-misinfluence-tendency', 'reward-and-punishment-superresponse-tendency']
- `20260426T105102Zstab1`: ['authority-misinfluence-tendency', 'reward-and-punishment-superresponse-tendency']
- `20260426T105211Zstab2`: ['authority-misinfluence-tendency', 'reward-and-punishment-superresponse-tendency']

### Lane 2 fingerprint moves
- `20260426T104943Zstab0`: ['compare internal vs external reporting by defining conditional criteria and applying them to case specifics like seniority and timing', "isolate current obligation from secondary concerns by distinguishing personal responsibility from others' past actions", 'project long-term outcomes across temporal phases to set realistic expectations for career and emotional trajectory', 'qualify evidential strength by assessing specificity and confidence levels while acknowledging alternative explanations to avoid premature conclusions', 'sequence actions into prioritized timeline emphasizing documentation, counsel, and normalcy to minimize exposure', 'structure decision framework by enumerating key dimensions of tradeoffs including legal, career, and moral factors to clarify the overall shape', 'threshold confidence in internal handling against institutional risks to recommend path based on probabilistic assessment']
- `20260426T105102Zstab1`: ['apply conditional filter to compare internal vs external reporting based on independence, track record, and urgency', 'assess evidential strength by probing for confirmatory details to determine decision weight', "isolate current obligation from prior actors' decisions to avoid decision displacement", 'sequence actions into prioritized timeline with risk mitigation steps', 'set probabilistic threshold for choosing reporting path based on confidence in internal handling', 'structure decision into triadic framework of legal, career, and moral dimensions', 'weigh likelihood of obstruction against benign alternatives based on contextual factors']
- `20260426T105211Zstab2`: ['apply confidence level to recommend path given institutional dynamics', 'assess evidential strength by probing for specifics to determine decision weight', 'compare internal vs external reporting using conditional criteria and confidence thresholds', "isolate current obligation from others' past actions to focus decision scope", 'sequence actions into prioritized timeline to minimize risks', 'structure decision into legal, career, and moral dimensions for comprehensive evaluation', 'weigh likelihood of obstruction against benign explanations based on context']

### Lane 2 recalled candidates
- `20260426T104943Zstab0`: ['active-listening', 'aleatory-epistemic-uncertainty-recognition', 'anchoring', 'association', 'auditability-traceability', 'authenticity', 'base-rates', 'bayesian', 'bias-blind-spot', 'boundaries', 'chain-of-thought', 'chain-of-verification', 'checklists', 'circle-of-competence', 'cognitive-dissonance', 'combinatorial-effects', 'commitment-bias', 'confidence-calibration', 'constructive-feedback-models', 'critical-mass', 'cultural-intelligence', 'curse-of-knowledge', 'dunning-kruger-effect', 'emotional-intelligence', 'expertise-reversal-effect', 'false-precision-avoidance', 'feedback-loops', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'internal-locus-of-control', 'inversion', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'mental-simulation', 'moral-hazard', 'obligations-controls-mapping', 'occams-razor', 'opportunity-cost', 'optionality', 'power-dynamics', 'principal-agent-problem', 'probabilistic-thinking', 'prospect-theory', 'reasoning-mode-router', 'regression-to-the-mean', 'regulatory-horizon-scanning', 'representativeness-heuristic', 'root-cause-analysis', 'scientific-method-evidence-testing', 'second-order-thinking', 'signaling', 'social-proof', 'specialization', 'sunk-cost-fallacy', 'survivorship-bias', 'tradition-vs-innovation-balance', 'wysiati']
- `20260426T105102Zstab1`: ['active-listening', 'aleatory-epistemic-uncertainty-recognition', 'authenticity', 'authority-bias', 'base-rates', 'bayesian', 'boundaries', 'branch-solve-merge', 'chain-of-thought', 'chain-of-verification', 'checklists', 'cognitive-dissonance', 'combinatorial-effects', 'commitment-bias', 'confidence-calibration', 'critical-mass', 'cultural-intelligence', 'curse-of-knowledge', 'dunning-kruger-effect', 'emotional-intelligence', 'expertise-reversal-effect', 'false-precision-avoidance', 'feedback-loops', 'feynman-technique', 'formal-reasoning', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'internal-locus-of-control', 'inversion', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'liking-principle', 'margin-of-safety', 'mental-simulation', 'obligations-controls-mapping', 'occams-razor', 'opportunity-cost', 'optionality', 'principal-agent-problem', 'prisoners-dilemma', 'probabilistic-thinking', 'prospect-theory', 'psychological-safety', 'rationalization', 'reasoning-mode-router', 'regression-to-the-mean', 'regulatory-horizon-scanning', 'representativeness-heuristic', 'root-cause-analysis', 'schema-acquisition', 'second-order-thinking', 'social-proof', 'specialization', 'step-back', 'sunk-cost-fallacy', 'variation-and-selection', 'wysiati']
- `20260426T105211Zstab2`: ['abstraction', 'active-listening', 'aleatory-epistemic-uncertainty-recognition', 'authenticity', 'authority-bias', 'base-rates', 'bayesian', 'bias-blind-spot', 'boundaries', 'branch-solve-merge', 'chain-of-thought', 'chain-of-verification', 'checklists', 'cognitive-dissonance', 'commitment-bias', 'confidence-calibration', 'constructive-feedback-models', 'critical-mass', 'cultural-intelligence', 'curse-of-knowledge', 'dunning-kruger-effect', 'emotional-intelligence', 'expertise-reversal-effect', 'false-precision-avoidance', 'feedback-loops', 'feynman-technique', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'internal-locus-of-control', 'inversion', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'margin-of-safety', 'mental-simulation', 'obligations-controls-mapping', 'occams-razor', 'opportunity-cost', 'optimism-bias-and-planning-fallacy', 'optionality', 'principal-agent-problem', 'probabilistic-thinking', 'prospect-theory', 'rationalization', 'reasoning-mode-router', 'regression-to-the-mean', 'regulatory-horizon-scanning', 'representativeness-heuristic', 'root-cause-analysis', 'scientific-method-evidence-testing', 'second-order-thinking', 'social-proof', 'specialization', 'sunk-cost-fallacy', 'trade-offs', 'tradition-vs-innovation-balance', 'understanding-motivations', 'wysiati']

### Lane 2 accepted (pre-cap)
- `20260426T104943Zstab0`: ['scientific-method-evidence-testing']
- `20260426T105102Zstab1`: ['chain-of-verification', 'probabilistic-thinking', 'wysiati']
- `20260426T105211Zstab2`: ['chain-of-verification', 'confidence-calibration', 'probabilistic-thinking', 'scientific-method-evidence-testing']

### Lane 2 detected (post-cap)
- `20260426T104943Zstab0`: ['scientific-method-evidence-testing']
- `20260426T105102Zstab1`: ['chain-of-verification', 'probabilistic-thinking', 'wysiati']
- `20260426T105211Zstab2`: ['chain-of-verification', 'confidence-calibration', 'probabilistic-thinking', 'scientific-method-evidence-testing']

### Lane 2 capped (top-5 drops)
- `20260426T104943Zstab0`: []
- `20260426T105102Zstab1`: []
- `20260426T105211Zstab2`: []

### Lane 2 cheat-sheet anchors
- `20260426T104943Zstab0`: ['scientific-method-evidence-testing']
- `20260426T105102Zstab1`: ['chain-of-verification', 'probabilistic-thinking', 'wysiati']
- `20260426T105211Zstab2`: ['chain-of-verification', 'confidence-calibration', 'probabilistic-thinking', 'scientific-method-evidence-testing']

### Lane 3 reframings
- `20260426T104943Zstab0`: ['decision-trees', 'optionality']
- `20260426T105102Zstab1`: ['decision-trees', 'optionality']
- `20260426T105211Zstab2`: ['decision-trees', 'second-order-thinking']

### Lane 4 gap dims
- `20260426T104943Zstab0`: ['commitment-reversibility', 'risk-response', 'stakeholder-alignment']
- `20260426T105102Zstab1`: ['commitment-reversibility', 'incentive-alignment', 'risk-response', 'stakeholder-alignment']
- `20260426T105211Zstab2`: ['commitment-reversibility', 'risk-response', 'stakeholder-alignment']

## Cost per run (boundary-call tokens, lower bound when embeddings on)

| Run | Calls | Prompt tok | Completion tok | Total tok | Embedding-expansion observed |
|---|---|---|---|---|---|
| `20260426T104943Zstab0` | 19 | 101197 | 6419 | 107616 | 0 |
| `20260426T105102Zstab1` | 19 | 101120 | 6347 | 107467 | 0 |
| `20260426T105211Zstab2` | 20 | 106519 | 6368 | 112887 | 0 |

> Embedding-expansion calls (gpt-4o-mini, temp=0.7) bypass `BoundaryClient` tracing — reported here as 0 with a caveat. Treat boundary_only totals as a lower bound on Lane 2 cost when `embedding_mode = on`.

### Per-stage boundary token cost

#### `20260426T104943Zstab0`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 5367 |
| companion_verification | 1 | 11382 |
| frame_extraction | 1 | 5646 |
| frame_reframing | 1 | 1444 |
| pass1_cluster_authority | 1 | 5974 |
| pass1_cluster_availability | 1 | 5527 |
| pass1_cluster_closure | 1 | 5776 |
| pass1_cluster_incentive | 1 | 5583 |
| pass1_cluster_residual | 1 | 5570 |
| pass1_cluster_self_regard | 1 | 5614 |
| pass2 | 7 | 40327 |
| structural_coverage_classification | 1 | 4703 |
| structural_coverage_detection | 1 | 4703 |

#### `20260426T105102Zstab1`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 5175 |
| companion_verification | 1 | 11105 |
| frame_extraction | 1 | 5644 |
| frame_reframing | 1 | 1353 |
| pass1_cluster_authority | 1 | 5979 |
| pass1_cluster_availability | 1 | 5536 |
| pass1_cluster_closure | 1 | 5779 |
| pass1_cluster_incentive | 1 | 5591 |
| pass1_cluster_residual | 1 | 5570 |
| pass1_cluster_self_regard | 1 | 5614 |
| pass2 | 7 | 40335 |
| structural_coverage_classification | 1 | 4893 |
| structural_coverage_detection | 1 | 4893 |

#### `20260426T105211Zstab2`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 5223 |
| companion_verification | 1 | 11376 |
| frame_extraction | 1 | 5636 |
| frame_reframing | 1 | 1270 |
| pass1_cluster_authority | 1 | 5993 |
| pass1_cluster_availability | 1 | 5537 |
| pass1_cluster_closure | 1 | 5781 |
| pass1_cluster_incentive | 1 | 5569 |
| pass1_cluster_residual | 1 | 5570 |
| pass1_cluster_self_regard | 1 | 5614 |
| pass2 | 8 | 45818 |
| structural_coverage_classification | 1 | 4750 |
| structural_coverage_detection | 1 | 4750 |
