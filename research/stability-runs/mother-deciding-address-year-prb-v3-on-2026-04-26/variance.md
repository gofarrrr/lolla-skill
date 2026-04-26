# Stability report — mother-deciding-address-year-prb-v3-on

Generated: 2026-04-26T13:56:36Z
Runs: 3
Run IDs: 20260426T135636Zstab0, 20260426T135738Zstab1, 20260426T135843Zstab2
Prompt versions consistent across runs: True

## Per-stage stability (Jaccard)

> 1.0 is a WARNING, not a target — signals a specialist that stopped doing semantic judgment. Acceptance is a threshold band: stability moved up from baseline, no neighboring stage regressed, qualitative review confirms cards still do structural work.

| Stage | Mean | Min | Max |
|---|---|---|---|
| Pass 1 (tendencies) | 1.00 | 1.00 | 1.00 |
| Lane 2 — fingerprint moves | 0.06 | 0.00 | 0.18 |
| Lane 2 — recalled candidates | 0.77 | 0.74 | 0.82 |
| Lane 2 — accepted (pre-cap) | 0.40 | 0.25 | 0.55 |
| Lane 2 — shared-avail. accept agreement | 0.42 | 0.27 | 0.60 |
| Lane 2 — detected (post-cap) | 0.26 | 0.11 | 0.43 |
| Lane 2 — capped (top-5 drops) | 0.13 | 0.00 | 0.40 |
| Lane 2 (cheat-sheet anchors) | 0.26 | 0.11 | 0.43 |
| Lane 3 (reframings) | 0.00 | 0.00 | 0.00 |
| Lane 4 (gap dims) | 0.67 | 0.50 | 0.75 |

Embedding mode per run: ['on', 'on', 'on']  ·  consistent: True

### Recall-source distribution per run

| Run | keyword | embedding | both | other |
|---|---|---|---|---|
| `20260426T135636Zstab0` | 60 | 0 | 0 | 0 |
| `20260426T135738Zstab1` | 60 | 0 | 0 | 0 |
| `20260426T135843Zstab2` | 60 | 0 | 0 | 0 |

## Step 6 anchor naming (per-run)

| Run | Named | Total | Rate |
|---|---|---|---|
| `20260426T135636Zstab0` | (no revised_answer) | — | — |
| `20260426T135738Zstab1` | (no revised_answer) | — | — |
| `20260426T135843Zstab2` | (no revised_answer) | — | — |

## Per-run item diff

### Pass 1 tendencies
- `20260426T135636Zstab0`: []
- `20260426T135738Zstab1`: []
- `20260426T135843Zstab2`: []

### Lane 2 fingerprint moves
- `20260426T135636Zstab0`: ["acknowledging surveillance as separate trust issue requiring future apology and negotiation despite its 'justification' by discovery", 'advising against blocking or confiscating phone to avoid driving grooming underground and eroding trust', 'gradual low-stakes engagement to signal safety and normalize interaction without pressure during shame phase', 'prioritizing relationship repair over immediate confrontation with the groomer to enable future cooperation and information sharing', 'recommending controlled disclosure to ex with factual limits to minimize undermining while avoiding exclusion backlash', "rejecting alerting mia's mom due to lack of evidence and risk of betraying daughter's trust during repair phase", 'weighing trade-offs between reporting risks (legal trauma, co-parent interference) and non-reporting benefits (therapy focus, protection via trust)']
- `20260426T135738Zstab1`: ['acknowledging surveillance as a separate trust issue requiring proactive confession to prevent larger future breach', 'dropping unilateral controls like blocking or phone confiscation to avoid driving grooming underground and eroding trust', 'prioritizing relationship repair over immediate confrontation with the groomer to enable future cooperation', "restricting disclosure to mia's mom absent concrete evidence to safeguard daughter's trust repair", 'sequencing low-stakes interactions to signal safety and routine amid shame, avoiding premature pressure', "weighing trade-offs between reporting to police and therapeutic intervention, factoring in co-parenting dynamics and daughter's trauma risk"]
- `20260426T135843Zstab2`: ['advising against blocking or confiscating phone to avoid driving grooming underground and eroding trust', "distinguishing appropriate general outreach from premature specific disclosure to avoid betraying daughter's trust", 'prioritizing relationship repair over immediate confrontation with the groomer to enable future cooperation and information sharing', 'recommending timed confession of surveillance to control narrative and model accountability', 'sequencing low-stakes interactions to gradually thaw shutdown without pressure', "weighing trade-offs of reporting to police versus therapeutic intervention, factoring in co-parenting dynamics and daughter's trauma risk"]

### Lane 2 recalled candidates
- `20260426T135636Zstab0`: ['abstraction', 'active-listening', 'adverse-selection', 'aleatory-epistemic-uncertainty-recognition', 'anchoring', 'auditability-traceability', 'authenticity', 'base-rates', 'bias-blind-spot', 'black-swan-events', 'boundaries', 'branch-solve-merge', 'causal-attribution-resistance', 'chain-of-verification', 'circle-of-control', 'commitment-bias', 'confidence-calibration', 'constructive-feedback-models', 'cultural-intelligence', 'dunning-kruger-effect', 'einstellung-effect', 'emotional-intelligence', 'endowment-effect', 'feedback-loops', 'five-whys-method', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'jobs-to-be-done', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'liking-principle', 'non-violent-communication', 'occams-razor', 'opportunity-cost', 'optimization-theory', 'optionality', 'power-dynamics', 'premortem', 'principal-agent-problem', 'prisoners-dilemma', 'prospect-theory', 'psychological-safety', 'rationalization', 'reciprocity-principle', 'red-queen-effect', 'representativeness-heuristic', 'schema-acquisition', 'second-order-thinking', 'signaling', 'social-proof', 'specialization', 'step-back', 'sunk-cost-fallacy', 'systems-thinking', 'theory-of-constraints', 'variation-and-selection', 'wysiati']
- `20260426T135738Zstab1`: ['abstraction', 'active-listening', 'aleatory-epistemic-uncertainty-recognition', 'auditability-traceability', 'authenticity', 'base-rates', 'bias-blind-spot', 'black-swan-events', 'boundaries', 'branch-solve-merge', 'causal-attribution-resistance', 'chain-of-verification', 'circle-of-control', 'commitment-bias', 'confidence-calibration', 'constructive-feedback-models', 'correlation-vs-causation', 'cultural-intelligence', 'desirable-difficulties', 'dunning-kruger-effect', 'einstellung-effect', 'emotional-intelligence', 'endowment-effect', 'feedback-loops', 'feynman-technique', 'game-theory-payoffs', 'goal-setting', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'jobs-to-be-done', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'liking-principle', 'meta-cognitive-reflection', 'metacognitive-questioning', 'nash-equilibrium', 'non-violent-communication', 'opportunity-cost', 'optimization-theory', 'power-dynamics', 'principal-agent-problem', 'prisoners-dilemma', 'probabilistic-thinking', 'prospect-theory', 'psychological-safety', 'rationalization', 'reasoning-mode-router', 'reciprocity-principle', 'representativeness-heuristic', 'schema-acquisition', 'second-order-thinking', 'signaling', 'social-proof', 'specialization', 'step-back', 'sunk-cost-fallacy', 'systems-thinking', 'wysiati']
- `20260426T135843Zstab2`: ['abstraction', 'active-listening', 'adverse-selection', 'aleatory-epistemic-uncertainty-recognition', 'anchoring', 'auditability-traceability', 'authenticity', 'base-rates', 'bias-blind-spot', 'black-swan-events', 'boundaries', 'branch-solve-merge', 'butterfly-effect', 'causal-attribution-resistance', 'chain-of-verification', 'circle-of-control', 'commitment-bias', 'confidence-calibration', 'constructive-feedback-models', 'cross-cultural-communication-frameworks', 'cultural-intelligence', 'deliberate-practice', 'dunning-kruger-effect', 'einstellung-effect', 'emotional-intelligence', 'empathy', 'endowment-effect', 'feedback-loops', 'feynman-technique', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'inversion', 'jobs-to-be-done', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'liking-principle', 'non-violent-communication', 'occams-razor', 'opportunity-cost', 'optimization-theory', 'power-dynamics', 'principal-agent-problem', 'prisoners-dilemma', 'prospect-theory', 'psychological-safety', 'rationalization', 'reciprocity-principle', 'red-queen-effect', 'representativeness-heuristic', 'schema-acquisition', 'second-order-thinking', 'signaling', 'social-proof', 'specialization', 'step-back', 'sunk-cost-fallacy', 'wysiati']

### Lane 2 accepted (pre-cap)
- `20260426T135636Zstab0`: ['circle-of-control', 'emotional-intelligence', 'game-theory-payoffs', 'liking-principle', 'optimization-theory', 'principal-agent-problem', 'psychological-safety', 'second-order-thinking']
- `20260426T135738Zstab1`: ['circle-of-control', 'emotional-intelligence', 'liking-principle', 'nash-equilibrium', 'opportunity-cost', 'principal-agent-problem', 'psychological-safety', 'reciprocity-principle', 'second-order-thinking']
- `20260426T135843Zstab2`: ['boundaries', 'circle-of-control', 'emotional-intelligence', 'game-theory-payoffs', 'power-dynamics', 'second-order-thinking']

### Lane 2 detected (post-cap)
- `20260426T135636Zstab0`: ['emotional-intelligence', 'game-theory-payoffs', 'liking-principle', 'psychological-safety', 'second-order-thinking']
- `20260426T135738Zstab1`: ['emotional-intelligence', 'liking-principle', 'opportunity-cost', 'reciprocity-principle', 'second-order-thinking']
- `20260426T135843Zstab2`: ['boundaries', 'circle-of-control', 'game-theory-payoffs', 'power-dynamics', 'second-order-thinking']

### Lane 2 capped (top-5 drops)
- `20260426T135636Zstab0`: ['circle-of-control', 'optimization-theory', 'principal-agent-problem']
- `20260426T135738Zstab1`: ['circle-of-control', 'nash-equilibrium', 'principal-agent-problem', 'psychological-safety']
- `20260426T135843Zstab2`: ['emotional-intelligence']

### Lane 2 cheat-sheet anchors
- `20260426T135636Zstab0`: ['emotional-intelligence', 'game-theory-payoffs', 'liking-principle', 'psychological-safety', 'second-order-thinking']
- `20260426T135738Zstab1`: ['emotional-intelligence', 'liking-principle', 'opportunity-cost', 'reciprocity-principle', 'second-order-thinking']
- `20260426T135843Zstab2`: ['boundaries', 'circle-of-control', 'game-theory-payoffs', 'power-dynamics', 'second-order-thinking']

### Lane 3 reframings
- `20260426T135636Zstab0`: ['trade-offs']
- `20260426T135738Zstab1`: ['decision-trees']
- `20260426T135843Zstab2`: ['creative-destruction', 'first-principles-thinking']

### Lane 4 gap dims
- `20260426T135636Zstab0`: ['commitment-reversibility', 'competitive-dynamics', 'uncertainty-type']
- `20260426T135738Zstab1`: ['commitment-reversibility', 'incentive-alignment', 'uncertainty-type']
- `20260426T135843Zstab2`: ['commitment-reversibility', 'competitive-dynamics', 'incentive-alignment', 'uncertainty-type']

## Cost per run (boundary-call tokens, lower bound when embeddings on)

| Run | Calls | Prompt tok | Completion tok | Total tok | Embedding-expansion observed |
|---|---|---|---|---|---|
| `20260426T135636Zstab0` | 14 | 85784 | 6165 | 91949 | 0 |
| `20260426T135738Zstab1` | 14 | 85334 | 6116 | 91450 | 0 |
| `20260426T135843Zstab2` | 14 | 85555 | 5817 | 91372 | 0 |

> Embedding-expansion calls (gpt-4o-mini, temp=0.7) bypass `BoundaryClient` tracing — reported here as 0 with a caveat. Treat boundary_only totals as a lower bound on Lane 2 cost when `embedding_mode = on`.

### Per-stage boundary token cost

#### `20260426T135636Zstab0`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 6234 |
| companion_verification_shard_0 | 1 | 9060 |
| companion_verification_shard_1 | 1 | 9280 |
| companion_verification_shard_2 | 1 | 9097 |
| frame_extraction | 1 | 6571 |
| frame_reframing | 1 | 1608 |
| pass1_cluster_authority | 1 | 6722 |
| pass1_cluster_availability | 1 | 6349 |
| pass1_cluster_closure | 1 | 6584 |
| pass1_cluster_incentive | 1 | 6385 |
| pass1_cluster_residual | 1 | 6428 |
| pass1_cluster_self_regard | 1 | 6499 |
| structural_coverage_classification | 1 | 5566 |
| structural_coverage_detection | 1 | 5566 |

#### `20260426T135738Zstab1`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 6116 |
| companion_verification_shard_0 | 1 | 9271 |
| companion_verification_shard_1 | 1 | 9295 |
| companion_verification_shard_2 | 1 | 9217 |
| frame_extraction | 1 | 6459 |
| frame_reframing | 1 | 996 |
| pass1_cluster_authority | 1 | 6722 |
| pass1_cluster_availability | 1 | 6349 |
| pass1_cluster_closure | 1 | 6584 |
| pass1_cluster_incentive | 1 | 6385 |
| pass1_cluster_residual | 1 | 6428 |
| pass1_cluster_self_regard | 1 | 6472 |
| structural_coverage_classification | 1 | 5578 |
| structural_coverage_detection | 1 | 5578 |

#### `20260426T135843Zstab2`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 6096 |
| companion_verification_shard_0 | 1 | 8655 |
| companion_verification_shard_1 | 1 | 9045 |
| companion_verification_shard_2 | 1 | 9315 |
| frame_extraction | 1 | 6484 |
| frame_reframing | 1 | 1407 |
| pass1_cluster_authority | 1 | 6722 |
| pass1_cluster_availability | 1 | 6389 |
| pass1_cluster_closure | 1 | 6584 |
| pass1_cluster_incentive | 1 | 6385 |
| pass1_cluster_residual | 1 | 6428 |
| pass1_cluster_self_regard | 1 | 6472 |
| structural_coverage_classification | 1 | 5695 |
| structural_coverage_detection | 1 | 5695 |
