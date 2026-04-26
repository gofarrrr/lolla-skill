# Stability report — mother-deciding-address-year-lane2-on

Generated: 2026-04-26T11:09:26Z
Runs: 3
Run IDs: 20260426T110926Zstab0, 20260426T111103Zstab1, 20260426T111245Zstab2
Prompt versions consistent across runs: True

## Per-stage stability (Jaccard)

> 1.0 is a WARNING, not a target — signals a specialist that stopped doing semantic judgment. Acceptance is a threshold band: stability moved up from baseline, no neighboring stage regressed, qualitative review confirms cards still do structural work.

| Stage | Mean | Min | Max |
|---|---|---|---|
| Pass 1 (tendencies) | 1.00 | 1.00 | 1.00 |
| Lane 2 — fingerprint moves | 0.12 | 0.08 | 0.20 |
| Lane 2 — recalled candidates | 0.75 | 0.71 | 0.76 |
| Lane 2 — accepted (pre-cap) | 0.06 | 0.00 | 0.17 |
| Lane 2 — detected (post-cap) | 0.06 | 0.00 | 0.17 |
| Lane 2 — capped (top-5 drops) | 1.00 | 1.00 | 1.00 |
| Lane 2 (cheat-sheet anchors) | 0.06 | 0.00 | 0.17 |
| Lane 3 (reframings) | 0.00 | 0.00 | 0.00 |
| Lane 4 (gap dims) | 0.58 | 0.40 | 0.75 |

Embedding mode per run: ['on', 'on', 'on']  ·  consistent: True

### Recall-source distribution per run

| Run | keyword | embedding | both | other |
|---|---|---|---|---|
| `20260426T110926Zstab0` | 60 | 0 | 0 | 0 |
| `20260426T111103Zstab1` | 60 | 0 | 0 | 0 |
| `20260426T111245Zstab2` | 60 | 0 | 0 | 0 |

## Step 6 anchor naming (per-run)

| Run | Named | Total | Rate |
|---|---|---|---|
| `20260426T110926Zstab0` | (no revised_answer) | — | — |
| `20260426T111103Zstab1` | (no revised_answer) | — | — |
| `20260426T111245Zstab2` | (no revised_answer) | — | — |

## Per-run item diff

### Pass 1 tendencies
- `20260426T110926Zstab0`: []
- `20260426T111103Zstab1`: []
- `20260426T111245Zstab2`: []

### Lane 2 fingerprint moves
- `20260426T110926Zstab0`: ['distinguishing immediate safety from punishment to preserve visibility and avoid entrenchment', 'evaluating reporting trade-offs by integrating co-parenting dynamics and therapeutic alternatives', 'prioritizing relationship repair over immediate confrontation with the groomer to enable future cooperation', 'sequencing low-stakes engagement to signal safety and thaw shutdown without pressure', 'tailoring co-parenting communication to facts-only to minimize undermining without exclusion', 'weighing surveillance benefits against long-term trust erosion and recommending confession for repair']
- `20260426T111103Zstab1`: ["distinguishing specific disclosure from general future conversations to avoid betraying daughter's trust", 'evaluating reporting trade-offs by integrating co-parenting dynamics and therapeutic alternatives', 'interpreting minimal engagement signals positively within shame recovery timeline', 'prioritizing relationship repair over immediate confrontation with the groomer to enable future cooperation', 'rejecting premature actions like blocking to preserve visibility and avoid driving grooming underground', 'weighing surveillance as a trust liability requiring future disclosure and cessation despite its recent utility']
- `20260426T111245Zstab2`: ['acknowledging surveillance as an independent trust issue requiring proactive disclosure and repair', "distinguishing between parental action goals (punishing the groomer vs. ensuring daughter's long-term safety through trust)", 'gradual low-pressure engagement to thaw shame response without triggering retreat', 'prioritizing relationship repair over immediate confrontation with the groomer to enable future cooperation', 'rejecting premature intervention in peer networks absent specific evidence to avoid trust betrayal', 'sequencing plan with timelines to manage parental anxiety and enforce deliberate pacing', 'weighing co-parenting dynamics as a constraint that amplifies risks of legal reporting']

### Lane 2 recalled candidates
- `20260426T110926Zstab0`: ['abstraction', 'active-listening', 'aleatory-epistemic-uncertainty-recognition', 'anchoring', 'auditability-traceability', 'authenticity', 'base-rates', 'black-swan-events', 'boundaries', 'branch-solve-merge', 'butterfly-effect', 'causal-attribution-resistance', 'chain-of-verification', 'circle-of-control', 'commitment-bias', 'confidence-calibration', 'constructive-feedback-models', 'cross-cultural-communication-frameworks', 'cultural-intelligence', 'curiosity', 'desirable-difficulties', 'einstellung-effect', 'emotional-intelligence', 'endowment-effect', 'feedback-loops', 'feynman-technique', 'five-whys-method', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'inversion', 'jobs-to-be-done', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'liking-principle', 'meta-cognitive-reflection', 'nash-equilibrium', 'non-violent-communication', 'occams-razor', 'opportunity-cost', 'power-dynamics', 'principal-agent-problem', 'prisoners-dilemma', 'prospect-theory', 'psychological-safety', 'rationalization', 'reciprocity-principle', 'red-queen-effect', 'regulatory-horizon-scanning', 'representativeness-heuristic', 'schema-acquisition', 'second-order-thinking', 'signaling', 'social-proof', 'step-back', 'sunk-cost-fallacy', 'variation-and-selection', 'wysiati']
- `20260426T111103Zstab1`: ['abstraction', 'active-listening', 'aleatory-epistemic-uncertainty-recognition', 'anchoring', 'auditability-traceability', 'authenticity', 'base-rates', 'bias-blind-spot', 'black-swan-events', 'boundaries', 'causal-attribution-resistance', 'chain-of-verification', 'circle-of-control', 'commitment-bias', 'confidence-calibration', 'constructive-feedback-models', 'cross-cultural-communication-frameworks', 'cultural-intelligence', 'deliberate-practice', 'dunning-kruger-effect', 'einstellung-effect', 'emotional-intelligence', 'endowment-effect', 'feedback-loops', 'feynman-technique', 'five-whys-method', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'inversion', 'jobs-to-be-done', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'liking-principle', 'meta-cognitive-reflection', 'nash-equilibrium', 'non-violent-communication', 'occams-razor', 'opportunity-cost', 'optimization-theory', 'power-dynamics', 'principal-agent-problem', 'prisoners-dilemma', 'probabilistic-thinking', 'prospect-theory', 'psychological-safety', 'rationalization', 'reasoning-mode-router', 'reciprocity-principle', 'representativeness-heuristic', 'second-order-thinking', 'signaling', 'social-proof', 'specialization', 'step-back', 'sunk-cost-fallacy', 'systems-thinking', 'variation-and-selection']
- `20260426T111245Zstab2`: ['abstraction', 'active-listening', 'aleatory-epistemic-uncertainty-recognition', 'anchoring', 'auditability-traceability', 'authenticity', 'base-rates', 'bias-blind-spot', 'black-swan-events', 'boundaries', 'causal-attribution-resistance', 'chain-of-verification', 'circle-of-control', 'commitment-bias', 'confidence-calibration', 'constructive-feedback-models', 'cultural-intelligence', 'dunning-kruger-effect', 'einstellung-effect', 'emotional-intelligence', 'empathy', 'endowment-effect', 'feedback-loops', 'feynman-technique', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'inversion', 'jobs-to-be-done', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'liking-principle', 'meta-cognitive-reflection', 'metacognitive-questioning', 'nash-equilibrium', 'non-violent-communication', 'occams-razor', 'opportunity-cost', 'persuasion-principles', 'power-dynamics', 'premortem', 'principal-agent-problem', 'prisoners-dilemma', 'probabilistic-thinking', 'prospect-theory', 'psychological-safety', 'rationalization', 'reasoning-mode-router', 'reciprocity-principle', 'red-queen-effect', 'regression-to-the-mean', 'representativeness-heuristic', 'schema-acquisition', 'second-order-thinking', 'signaling', 'social-proof', 'step-back', 'theory-of-constraints']

### Lane 2 accepted (pre-cap)
- `20260426T110926Zstab0`: []
- `20260426T111103Zstab1`: ['liking-principle', 'opportunity-cost', 'psychological-safety', 'second-order-thinking']
- `20260426T111245Zstab2`: ['active-listening', 'opportunity-cost', 'power-dynamics']

### Lane 2 detected (post-cap)
- `20260426T110926Zstab0`: []
- `20260426T111103Zstab1`: ['liking-principle', 'opportunity-cost', 'psychological-safety', 'second-order-thinking']
- `20260426T111245Zstab2`: ['active-listening', 'opportunity-cost', 'power-dynamics']

### Lane 2 capped (top-5 drops)
- `20260426T110926Zstab0`: []
- `20260426T111103Zstab1`: []
- `20260426T111245Zstab2`: []

### Lane 2 cheat-sheet anchors
- `20260426T110926Zstab0`: []
- `20260426T111103Zstab1`: ['liking-principle', 'opportunity-cost', 'psychological-safety', 'second-order-thinking']
- `20260426T111245Zstab2`: ['active-listening', 'opportunity-cost', 'power-dynamics']

### Lane 3 reframings
- `20260426T110926Zstab0`: ['creative-destruction', 'first-principles-thinking']
- `20260426T111103Zstab1`: ['cross-cultural-communication-frameworks', 'trade-offs']
- `20260426T111245Zstab2`: []

### Lane 4 gap dims
- `20260426T110926Zstab0`: ['incentive-alignment', 'risk-response', 'stakeholder-alignment']
- `20260426T111103Zstab1`: ['feedback-system-dynamics', 'incentive-alignment', 'stakeholder-alignment', 'uncertainty-type']
- `20260426T111245Zstab2`: ['incentive-alignment', 'risk-response', 'stakeholder-alignment', 'uncertainty-type']

## Cost per run (boundary-call tokens, lower bound when embeddings on)

| Run | Calls | Prompt tok | Completion tok | Total tok | Embedding-expansion observed |
|---|---|---|---|---|---|
| `20260426T110926Zstab0` | 12 | 73585 | 3941 | 77526 | 0 |
| `20260426T111103Zstab1` | 12 | 71365 | 4920 | 76285 | 0 |
| `20260426T111245Zstab2` | 11 | 70202 | 4981 | 75183 | 0 |

> Embedding-expansion calls (gpt-4o-mini, temp=0.7) bypass `BoundaryClient` tracing — reported here as 0 with a caveat. Treat boundary_only totals as a lower bound on Lane 2 cost when `embedding_mode = on`.

### Per-stage boundary token cost

#### `20260426T110926Zstab0`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 6079 |
| companion_verification | 1 | 13408 |
| frame_extraction | 1 | 6499 |
| frame_reframing | 1 | 1399 |
| pass1_cluster_authority | 1 | 6722 |
| pass1_cluster_availability | 1 | 6389 |
| pass1_cluster_closure | 1 | 6584 |
| pass1_cluster_incentive | 1 | 6385 |
| pass1_cluster_residual | 1 | 6428 |
| pass1_cluster_self_regard | 1 | 6499 |
| structural_coverage_classification | 1 | 5567 |
| structural_coverage_detection | 1 | 5567 |

#### `20260426T111103Zstab1`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 6149 |
| companion_verification | 1 | 11893 |
| frame_extraction | 1 | 6582 |
| frame_reframing | 1 | 1523 |
| pass1_cluster_authority | 1 | 6722 |
| pass1_cluster_availability | 1 | 6397 |
| pass1_cluster_closure | 1 | 6584 |
| pass1_cluster_incentive | 1 | 6385 |
| pass1_cluster_residual | 1 | 6428 |
| pass1_cluster_self_regard | 1 | 6512 |
| structural_coverage_classification | 1 | 5555 |
| structural_coverage_detection | 1 | 5555 |

#### `20260426T111245Zstab2`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 6187 |
| companion_verification | 1 | 12115 |
| frame_extraction | 1 | 6431 |
| pass1_cluster_authority | 1 | 6722 |
| pass1_cluster_availability | 1 | 6389 |
| pass1_cluster_closure | 1 | 6584 |
| pass1_cluster_incentive | 1 | 6385 |
| pass1_cluster_residual | 1 | 6428 |
| pass1_cluster_self_regard | 1 | 6518 |
| structural_coverage_classification | 1 | 5712 |
| structural_coverage_detection | 1 | 5712 |
