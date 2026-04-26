# Stability report — mother-deciding-address-year-prb-v2-on

Generated: 2026-04-26T13:16:28Z
Runs: 3
Run IDs: 20260426T131628Zstab0, 20260426T131726Zstab1, 20260426T131824Zstab2
Prompt versions consistent across runs: True

## Per-stage stability (Jaccard)

> 1.0 is a WARNING, not a target — signals a specialist that stopped doing semantic judgment. Acceptance is a threshold band: stability moved up from baseline, no neighboring stage regressed, qualitative review confirms cards still do structural work.

| Stage | Mean | Min | Max |
|---|---|---|---|
| Pass 1 (tendencies) | 1.00 | 1.00 | 1.00 |
| Lane 2 — fingerprint moves | 0.09 | 0.08 | 0.09 |
| Lane 2 — recalled candidates | 0.81 | 0.79 | 0.85 |
| Lane 2 — accepted (pre-cap) | 0.38 | 0.18 | 0.62 |
| Lane 2 — shared-avail. accept agreement | 0.43 | 0.22 | 0.71 |
| Lane 2 — detected (post-cap) | 0.30 | 0.11 | 0.67 |
| Lane 2 — capped (top-5 drops) | 0.17 | 0.00 | 0.50 |
| Lane 2 (cheat-sheet anchors) | 0.30 | 0.11 | 0.67 |
| Lane 3 (reframings) | 0.00 | 0.00 | 0.00 |
| Lane 4 (gap dims) | 0.46 | 0.29 | 0.60 |

Embedding mode per run: ['on', 'on', 'on']  ·  consistent: True

### Recall-source distribution per run

| Run | keyword | embedding | both | other |
|---|---|---|---|---|
| `20260426T131628Zstab0` | 60 | 0 | 0 | 0 |
| `20260426T131726Zstab1` | 60 | 0 | 0 | 0 |
| `20260426T131824Zstab2` | 60 | 0 | 0 | 0 |

## Step 6 anchor naming (per-run)

| Run | Named | Total | Rate |
|---|---|---|---|
| `20260426T131628Zstab0` | (no revised_answer) | — | — |
| `20260426T131726Zstab1` | (no revised_answer) | — | — |
| `20260426T131824Zstab2` | (no revised_answer) | — | — |

## Per-run item diff

### Pass 1 tendencies
- `20260426T131628Zstab0`: []
- `20260426T131726Zstab1`: []
- `20260426T131824Zstab2`: []

### Lane 2 fingerprint moves
- `20260426T131628Zstab0`: ['distinguishing specific evidence requirements before escalating to third-party alerts', "evaluating reporting trade-offs in context of co-parenting dynamics and child's trauma", 'framing controlled co-parenting communication to minimize undermining without exclusion', 'prioritizing relationship repair over immediate confrontation with the groomer to enable future cooperation', 'sequencing low-pressure engagement to thaw shutdown without triggering retreat', 'weighing surveillance benefits against long-term trust erosion and recommending timed disclosure']
- `20260426T131726Zstab1`: ['acknowledging surveillance as separate trust issue requiring future apology and negotiation', 'advising against blocking or confiscating phone to avoid driving grooming underground and eroding trust', 'gradual low-pressure re-engagement to thaw shame without overwhelming', 'prioritizing relationship repair over immediate confrontation with the groomer to enable future cooperation', 'recommending controlled disclosure to co-parent to minimize undermining while avoiding debate', "rejecting alerting friend's parent without evidence to protect daughter's trust repair", 'weighing trade-offs of reporting to authorities versus therapeutic intervention, considering co-parenting dynamics and trauma risks']
- `20260426T131824Zstab2`: ['acknowledging surveillance as a separate trust issue requiring proactive confession and cessation to prevent larger future breach', 'differentiating immediate punitive controls from long-term relational strategies that foster voluntary disclosure', 'prioritizing relationship repair over immediate confrontation with the groomer to enable future cooperation', 'restricting information shared with ex to facts only to minimize undermining while maintaining co-parenting necessity', 'sequencing low-pressure engagement to signal safety and normalize interactions without forcing resolution', "weighing trade-offs of reporting to authorities versus therapeutic intervention, factoring in co-parenting dynamics and daughter's trauma risk"]

### Lane 2 recalled candidates
- `20260426T131628Zstab0`: ['abstraction', 'active-listening', 'adverse-selection', 'aleatory-epistemic-uncertainty-recognition', 'anchoring', 'auditability-traceability', 'authenticity', 'base-rates', 'bias-blind-spot', 'black-swan-events', 'boundaries', 'branch-solve-merge', 'butterfly-effect', 'causal-attribution-resistance', 'chain-of-verification', 'circle-of-control', 'commitment-bias', 'confidence-calibration', 'constructive-feedback-models', 'cross-cultural-communication-frameworks', 'cultural-intelligence', 'desirable-difficulties', 'dunning-kruger-effect', 'einstellung-effect', 'emotional-intelligence', 'endowment-effect', 'feedback-loops', 'feynman-technique', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'jobs-to-be-done', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'liking-principle', 'meta-cognitive-reflection', 'non-violent-communication', 'occams-razor', 'opportunity-cost', 'optionality', 'power-dynamics', 'principal-agent-problem', 'probabilistic-thinking', 'prospect-theory', 'psychological-safety', 'rationalization', 'reasoning-mode-router', 'reciprocity-principle', 'representativeness-heuristic', 'schema-acquisition', 'second-order-thinking', 'signaling', 'social-proof', 'step-back', 'sunk-cost-fallacy', 'time-tested-validation', 'variation-and-selection', 'wysiati']
- `20260426T131726Zstab1`: ['abstraction', 'active-listening', 'adverse-selection', 'aleatory-epistemic-uncertainty-recognition', 'anchoring', 'auditability-traceability', 'authenticity', 'base-rates', 'bias-blind-spot', 'black-swan-events', 'boundaries', 'branch-solve-merge', 'causal-attribution-resistance', 'chain-of-verification', 'commitment-bias', 'confidence-calibration', 'constructive-feedback-models', 'cross-cultural-communication-frameworks', 'cultural-intelligence', 'desirable-difficulties', 'dunning-kruger-effect', 'einstellung-effect', 'emotional-intelligence', 'empathy', 'endowment-effect', 'feedback-loops', 'feynman-technique', 'five-whys-method', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'jobs-to-be-done', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'liking-principle', 'meta-cognitive-reflection', 'non-violent-communication', 'occams-razor', 'opportunity-cost', 'power-dynamics', 'premortem', 'principal-agent-problem', 'prisoners-dilemma', 'probabilistic-thinking', 'prospect-theory', 'psychological-safety', 'rationalization', 'reasoning-mode-router', 'reciprocity-principle', 'representativeness-heuristic', 'schema-acquisition', 'second-order-thinking', 'signaling', 'social-proof', 'step-back', 'sunk-cost-fallacy', 'systems-thinking', 'variation-and-selection']
- `20260426T131824Zstab2`: ['abstraction', 'active-listening', 'adverse-selection', 'aleatory-epistemic-uncertainty-recognition', 'anchoring', 'auditability-traceability', 'authenticity', 'base-rates', 'bias-blind-spot', 'black-swan-events', 'boundaries', 'branch-solve-merge', 'causal-attribution-resistance', 'chain-of-verification', 'circle-of-control', 'commitment-bias', 'confidence-calibration', 'constructive-feedback-models', 'cross-cultural-communication-frameworks', 'cultural-intelligence', 'decomposition', 'dunning-kruger-effect', 'einstellung-effect', 'emotional-intelligence', 'feedback-loops', 'feynman-technique', 'five-whys-method', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'jobs-to-be-done', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'liking-principle', 'non-violent-communication', 'occams-razor', 'opportunity-cost', 'optimization-theory', 'optionality', 'power-dynamics', 'premortem', 'principal-agent-problem', 'prospect-theory', 'psychological-safety', 'rationalization', 'reciprocity-principle', 'red-queen-effect', 'regression-to-the-mean', 'representativeness-heuristic', 'schema-acquisition', 'second-order-thinking', 'signaling', 'social-proof', 'step-back', 'sunk-cost-fallacy', 'systems-thinking', 'variation-and-selection', 'wysiati']

### Lane 2 accepted (pre-cap)
- `20260426T131628Zstab0`: ['circle-of-control', 'emotional-intelligence', 'game-theory-payoffs', 'liking-principle', 'opportunity-cost', 'psychological-safety', 'reasoning-mode-router', 'second-order-thinking']
- `20260426T131726Zstab1`: ['emotional-intelligence', 'game-theory-payoffs', 'psychological-safety', 'reasoning-mode-router', 'second-order-thinking']
- `20260426T131824Zstab2`: ['active-listening', 'anchoring', 'circle-of-control', 'emotional-intelligence', 'intellectual-humility', 'liking-principle', 'second-order-thinking', 'step-back']

### Lane 2 detected (post-cap)
- `20260426T131628Zstab0`: ['emotional-intelligence', 'game-theory-payoffs', 'opportunity-cost', 'psychological-safety', 'second-order-thinking']
- `20260426T131726Zstab1`: ['emotional-intelligence', 'game-theory-payoffs', 'psychological-safety', 'reasoning-mode-router', 'second-order-thinking']
- `20260426T131824Zstab2`: ['active-listening', 'anchoring', 'intellectual-humility', 'second-order-thinking', 'step-back']

### Lane 2 capped (top-5 drops)
- `20260426T131628Zstab0`: ['circle-of-control', 'liking-principle', 'reasoning-mode-router']
- `20260426T131726Zstab1`: []
- `20260426T131824Zstab2`: ['circle-of-control', 'emotional-intelligence', 'liking-principle']

### Lane 2 cheat-sheet anchors
- `20260426T131628Zstab0`: ['emotional-intelligence', 'game-theory-payoffs', 'opportunity-cost', 'psychological-safety', 'second-order-thinking']
- `20260426T131726Zstab1`: ['emotional-intelligence', 'game-theory-payoffs', 'psychological-safety', 'reasoning-mode-router', 'second-order-thinking']
- `20260426T131824Zstab2`: ['active-listening', 'anchoring', 'intellectual-humility', 'second-order-thinking', 'step-back']

### Lane 3 reframings
- `20260426T131628Zstab0`: ['intellectual-humility']
- `20260426T131726Zstab1`: ['problem-framing-and-reframing']
- `20260426T131824Zstab2`: ['decision-trees', 'latticework-of-mental-models']

### Lane 4 gap dims
- `20260426T131628Zstab0`: ['competitive-dynamics', 'incentive-alignment', 'risk-response', 'uncertainty-type']
- `20260426T131726Zstab1`: ['behavioral-intervention', 'commitment-reversibility', 'incentive-alignment', 'information-quality', 'uncertainty-type']
- `20260426T131824Zstab2`: ['commitment-reversibility', 'competitive-dynamics', 'incentive-alignment', 'uncertainty-type']

## Cost per run (boundary-call tokens, lower bound when embeddings on)

| Run | Calls | Prompt tok | Completion tok | Total tok | Embedding-expansion observed |
|---|---|---|---|---|---|
| `20260426T131628Zstab0` | 20 | 125048 | 6263 | 131311 | 0 |
| `20260426T131726Zstab1` | 20 | 126564 | 6792 | 133356 | 0 |
| `20260426T131824Zstab2` | 20 | 125548 | 6933 | 132481 | 0 |

> Embedding-expansion calls (gpt-4o-mini, temp=0.7) bypass `BoundaryClient` tracing — reported here as 0 with a caveat. Treat boundary_only totals as a lower bound on Lane 2 cost when `embedding_mode = on`.

### Per-stage boundary token cost

#### `20260426T131628Zstab0`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 6080 |
| companion_verification_abductive | 1 | 6810 |
| companion_verification_analogical | 1 | 6900 |
| companion_verification_causal | 1 | 7141 |
| companion_verification_counterfactual | 1 | 7695 |
| companion_verification_deductive | 1 | 7074 |
| companion_verification_diagnostic | 1 | 8941 |
| companion_verification_metacognitive | 1 | 7921 |
| companion_verification_probabilistic | 1 | 7178 |
| companion_verification_systems | 1 | 7708 |
| frame_extraction | 1 | 6549 |
| frame_reframing | 1 | 992 |
| pass1_cluster_authority | 1 | 6722 |
| pass1_cluster_availability | 1 | 6349 |
| pass1_cluster_closure | 1 | 6584 |
| pass1_cluster_incentive | 1 | 6385 |
| pass1_cluster_residual | 1 | 6428 |
| pass1_cluster_self_regard | 1 | 6472 |
| structural_coverage_classification | 1 | 5691 |
| structural_coverage_detection | 1 | 5691 |

#### `20260426T131726Zstab1`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 6253 |
| companion_verification_abductive | 1 | 6966 |
| companion_verification_analogical | 1 | 7067 |
| companion_verification_causal | 1 | 7309 |
| companion_verification_counterfactual | 1 | 7706 |
| companion_verification_deductive | 1 | 7520 |
| companion_verification_diagnostic | 1 | 8841 |
| companion_verification_metacognitive | 1 | 7947 |
| companion_verification_probabilistic | 1 | 7334 |
| companion_verification_systems | 1 | 8300 |
| frame_extraction | 1 | 6449 |
| frame_reframing | 1 | 986 |
| pass1_cluster_authority | 1 | 6722 |
| pass1_cluster_availability | 1 | 6383 |
| pass1_cluster_closure | 1 | 6584 |
| pass1_cluster_incentive | 1 | 6385 |
| pass1_cluster_residual | 1 | 6428 |
| pass1_cluster_self_regard | 1 | 6498 |
| structural_coverage_classification | 1 | 5839 |
| structural_coverage_detection | 1 | 5839 |

#### `20260426T131824Zstab2`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 6124 |
| companion_verification_abductive | 1 | 6867 |
| companion_verification_analogical | 1 | 7114 |
| companion_verification_causal | 1 | 7385 |
| companion_verification_counterfactual | 1 | 7705 |
| companion_verification_deductive | 1 | 7726 |
| companion_verification_diagnostic | 1 | 8697 |
| companion_verification_metacognitive | 1 | 8038 |
| companion_verification_probabilistic | 1 | 7235 |
| companion_verification_systems | 1 | 7564 |
| frame_extraction | 1 | 6452 |
| frame_reframing | 1 | 1174 |
| pass1_cluster_authority | 1 | 6722 |
| pass1_cluster_availability | 1 | 6388 |
| pass1_cluster_closure | 1 | 6584 |
| pass1_cluster_incentive | 1 | 6385 |
| pass1_cluster_residual | 1 | 6428 |
| pass1_cluster_self_regard | 1 | 6513 |
| structural_coverage_classification | 1 | 5690 |
| structural_coverage_detection | 1 | 5690 |
