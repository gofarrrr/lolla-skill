# Stability report — mother-deciding-address-year-lane2-off

Generated: 2026-04-26T12:00:23Z
Runs: 3
Run IDs: 20260426T120023Zstab0, 20260426T120158Zstab1, 20260426T120336Zstab2
Prompt versions consistent across runs: True

## Per-stage stability (Jaccard)

> 1.0 is a WARNING, not a target — signals a specialist that stopped doing semantic judgment. Acceptance is a threshold band: stability moved up from baseline, no neighboring stage regressed, qualitative review confirms cards still do structural work.

| Stage | Mean | Min | Max |
|---|---|---|---|
| Pass 1 (tendencies) | 1.00 | 1.00 | 1.00 |
| Lane 2 — fingerprint moves | 0.08 | 0.08 | 0.08 |
| Lane 2 — recalled candidates | 0.81 | 0.76 | 0.85 |
| Lane 2 — accepted (pre-cap) | 0.20 | 0.11 | 0.33 |
| Lane 2 — shared-avail. accept agreement | 0.23 | 0.14 | 0.33 |
| Lane 2 — detected (post-cap) | 0.23 | 0.14 | 0.33 |
| Lane 2 — capped (top-5 drops) | 0.33 | 0.00 | 1.00 |
| Lane 2 (cheat-sheet anchors) | 0.23 | 0.14 | 0.33 |
| Lane 3 (reframings) | 0.11 | 0.00 | 0.33 |
| Lane 4 (gap dims) | 0.47 | 0.40 | 0.60 |

Embedding mode per run: ['off', 'off', 'off']  ·  consistent: True

### Recall-source distribution per run

| Run | keyword | embedding | both | other |
|---|---|---|---|---|
| `20260426T120023Zstab0` | 60 | 0 | 0 | 0 |
| `20260426T120158Zstab1` | 60 | 0 | 0 | 0 |
| `20260426T120336Zstab2` | 60 | 0 | 0 | 0 |

## Step 6 anchor naming (per-run)

| Run | Named | Total | Rate |
|---|---|---|---|
| `20260426T120023Zstab0` | (no revised_answer) | — | — |
| `20260426T120158Zstab1` | (no revised_answer) | — | — |
| `20260426T120336Zstab2` | (no revised_answer) | — | — |

## Per-run item diff

### Pass 1 tendencies
- `20260426T120023Zstab0`: []
- `20260426T120158Zstab1`: []
- `20260426T120336Zstab2`: []

### Lane 2 fingerprint moves
- `20260426T120023Zstab0`: ['acknowledging surveillance as a separate trust issue requiring proactive disclosure and apology', 'balancing protection goals by choosing therapy over reporting given family constraints', "deferring mia's mom contact to protect daughter's trust repair over speculative alerts", 'prioritizing relationship repair over immediate confrontation with the groomer to enable future cooperation', 'rejecting unilateral controls like blocking to avoid driving grooming underground', 'sequencing low-stakes engagement to thaw shutdown without pressure', 'weighing co-parenting dynamics as a constraint that amplifies risks of legal reporting']
- `20260426T120158Zstab1`: ["acknowledging surveillance's dual role (discovery benefit vs. trust erosion) to advocate timed confession", 'distinguishing specific evidence requirements from general risks to scope protective actions', 'enumerating co-parenting options and their projected outcomes to select least damaging path', 'evaluating reporting trade-offs in context of co-parenting dynamics and therapeutic alternatives', 'interpreting minimal engagement signals as incremental progress to sustain low-pressure strategy', 'prioritizing relationship repair over immediate confrontation with the groomer to enable future cooperation', 'weighing trade-offs between punitive controls and driving behavior underground, favoring visibility through trust-building']
- `20260426T120336Zstab2`: ['acknowledging surveillance as a separate trust issue requiring future confession and cessation', "deferring disclosure of others' risks to protect primary trust repair", 'graduated low-pressure engagement to thaw shutdown without overwhelming shame', 'prioritizing relationship repair over immediate confrontation with the groomer to enable future cooperation', 'rejecting unilateral controls like blocking or confiscation to avoid driving grooming underground', "weighing trade-offs of reporting to authorities against co-parenting dynamics and daughter's trauma"]

### Lane 2 recalled candidates
- `20260426T120023Zstab0`: ['abstraction', 'active-listening', 'adverse-selection', 'aleatory-epistemic-uncertainty-recognition', 'auditability-traceability', 'authenticity', 'base-rates', 'bias-blind-spot', 'black-swan-events', 'boundaries', 'branch-solve-merge', 'causal-attribution-resistance', 'chain-of-verification', 'circle-of-control', 'commitment-bias', 'confidence-calibration', 'constructive-feedback-models', 'cultural-intelligence', 'deliberate-practice', 'dunning-kruger-effect', 'einstellung-effect', 'emotional-intelligence', 'empathy', 'endowment-effect', 'feedback-loops', 'feynman-technique', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'jobs-to-be-done', 'lean-startup-methodology', 'learning-curve', 'liking-principle', 'meta-cognitive-reflection', 'metacognitive-questioning', 'nash-equilibrium', 'occams-razor', 'opportunity-cost', 'optimization-theory', 'path-dependence', 'power-dynamics', 'principal-agent-problem', 'prisoners-dilemma', 'probabilistic-thinking', 'prospect-theory', 'psychological-safety', 'rationalization', 'reasoning-mode-router', 'reciprocity-principle', 'representativeness-heuristic', 'schema-acquisition', 'second-order-thinking', 'signaling', 'social-proof', 'step-back', 'sunk-cost-fallacy', 'systems-thinking', 'theory-of-constraints', 'wysiati']
- `20260426T120158Zstab1`: ['abstraction', 'active-listening', 'aleatory-epistemic-uncertainty-recognition', 'anchoring', 'auditability-traceability', 'authenticity', 'base-rates', 'bias-blind-spot', 'black-swan-events', 'boundaries', 'causal-attribution-resistance', 'chain-of-verification', 'circle-of-control', 'cognitive-load-theory', 'commitment-bias', 'confidence-calibration', 'constructive-feedback-models', 'cross-cultural-communication-frameworks', 'cultural-intelligence', 'deliberate-practice', 'dunning-kruger-effect', 'einstellung-effect', 'emotional-intelligence', 'endowment-effect', 'feedback-loops', 'feynman-technique', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'inversion', 'jobs-to-be-done', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'liking-principle', 'metacognitive-questioning', 'nash-equilibrium', 'non-violent-communication', 'opportunity-cost', 'optimization-theory', 'power-dynamics', 'principal-agent-problem', 'prisoners-dilemma', 'probabilistic-thinking', 'prospect-theory', 'psychological-safety', 'rationalization', 'reasoning-mode-router', 'reciprocity-principle', 'representativeness-heuristic', 'schema-acquisition', 'second-order-thinking', 'signaling', 'social-proof', 'specialization', 'step-back', 'sunk-cost-fallacy', 'systems-thinking', 'variation-and-selection']
- `20260426T120336Zstab2`: ['abstraction', 'active-listening', 'adverse-selection', 'aleatory-epistemic-uncertainty-recognition', 'anchoring', 'auditability-traceability', 'authenticity', 'base-rates', 'bias-blind-spot', 'black-swan-events', 'boundaries', 'branch-solve-merge', 'causal-attribution-resistance', 'chain-of-verification', 'circle-of-control', 'commitment-bias', 'confidence-calibration', 'constructive-feedback-models', 'cross-cultural-communication-frameworks', 'cultural-intelligence', 'dunning-kruger-effect', 'einstellung-effect', 'emotional-intelligence', 'endowment-effect', 'feedback-loops', 'feynman-technique', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'jobs-to-be-done', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'liking-principle', 'meta-cognitive-reflection', 'nash-equilibrium', 'non-violent-communication', 'occams-razor', 'opportunity-cost', 'optimization-theory', 'power-dynamics', 'principal-agent-problem', 'prisoners-dilemma', 'probabilistic-thinking', 'prospect-theory', 'psychological-safety', 'rationalization', 'reciprocity-principle', 'representativeness-heuristic', 'schema-acquisition', 'second-order-thinking', 'signaling', 'social-proof', 'specialization', 'step-back', 'sunk-cost-fallacy', 'systems-thinking', 'variation-and-selection', 'wysiati']

### Lane 2 accepted (pre-cap)
- `20260426T120023Zstab0`: ['active-listening', 'opportunity-cost', 'path-dependence', 'principal-agent-problem', 'psychological-safety', 'second-order-thinking', 'theory-of-constraints']
- `20260426T120158Zstab1`: ['second-order-thinking']
- `20260426T120336Zstab2`: ['circle-of-control', 'liking-principle', 'second-order-thinking']

### Lane 2 detected (post-cap)
- `20260426T120023Zstab0`: ['active-listening', 'opportunity-cost', 'psychological-safety', 'second-order-thinking', 'theory-of-constraints']
- `20260426T120158Zstab1`: ['second-order-thinking']
- `20260426T120336Zstab2`: ['circle-of-control', 'liking-principle', 'second-order-thinking']

### Lane 2 capped (top-5 drops)
- `20260426T120023Zstab0`: ['path-dependence', 'principal-agent-problem']
- `20260426T120158Zstab1`: []
- `20260426T120336Zstab2`: []

### Lane 2 cheat-sheet anchors
- `20260426T120023Zstab0`: ['active-listening', 'opportunity-cost', 'psychological-safety', 'second-order-thinking', 'theory-of-constraints']
- `20260426T120158Zstab1`: ['second-order-thinking']
- `20260426T120336Zstab2`: ['circle-of-control', 'liking-principle', 'second-order-thinking']

### Lane 3 reframings
- `20260426T120023Zstab0`: ['decision-trees', 'trade-offs']
- `20260426T120158Zstab1`: ['intellectual-humility', 'trade-offs']
- `20260426T120336Zstab2`: ['first-principles-thinking', 'trust-repair-prioritization']

### Lane 4 gap dims
- `20260426T120023Zstab0`: ['commitment-reversibility', 'competitive-dynamics', 'incentive-alignment', 'uncertainty-type']
- `20260426T120158Zstab1`: ['behavioral-intervention', 'commitment-reversibility', 'incentive-alignment', 'uncertainty-type']
- `20260426T120336Zstab2`: ['commitment-reversibility', 'incentive-alignment', 'risk-response']

## Cost per run (boundary-call tokens, lower bound when embeddings on)

| Run | Calls | Prompt tok | Completion tok | Total tok | Embedding-expansion observed |
|---|---|---|---|---|---|
| `20260426T120023Zstab0` | 12 | 71281 | 5521 | 76802 | 0 |
| `20260426T120158Zstab1` | 12 | 71458 | 5360 | 76818 | 0 |
| `20260426T120336Zstab2` | 12 | 71189 | 64494 | 135683 | 0 |

> Embedding-expansion calls (gpt-4o-mini, temp=0.7) bypass `BoundaryClient` tracing — reported here as 0 with a caveat. Treat boundary_only totals as a lower bound on Lane 2 cost when `embedding_mode = on`.

### Per-stage boundary token cost

#### `20260426T120023Zstab0`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 6196 |
| companion_verification | 1 | 12022 |
| frame_extraction | 1 | 6568 |
| frame_reframing | 1 | 1591 |
| pass1_cluster_authority | 1 | 6722 |
| pass1_cluster_availability | 1 | 6349 |
| pass1_cluster_closure | 1 | 6584 |
| pass1_cluster_incentive | 1 | 6385 |
| pass1_cluster_residual | 1 | 6428 |
| pass1_cluster_self_regard | 1 | 6511 |
| structural_coverage_classification | 1 | 5723 |
| structural_coverage_detection | 1 | 5723 |

#### `20260426T120158Zstab1`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 6345 |
| companion_verification | 1 | 11952 |
| frame_extraction | 1 | 6576 |
| frame_reframing | 1 | 1519 |
| pass1_cluster_authority | 1 | 6722 |
| pass1_cluster_availability | 1 | 6349 |
| pass1_cluster_closure | 1 | 6584 |
| pass1_cluster_incentive | 1 | 6385 |
| pass1_cluster_residual | 1 | 6428 |
| pass1_cluster_self_regard | 1 | 6472 |
| structural_coverage_classification | 1 | 5743 |
| structural_coverage_detection | 1 | 5743 |

#### `20260426T120336Zstab2`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 6116 |
| companion_verification | 1 | 11924 |
| frame_extraction | 1 | 6579 |
| frame_reframing | 1 | 1515 |
| pass1_cluster_authority | 1 | 6722 |
| pass1_cluster_availability | 1 | 6349 |
| pass1_cluster_closure | 1 | 6584 |
| pass1_cluster_incentive | 1 | 6385 |
| pass1_cluster_residual | 1 | 6428 |
| pass1_cluster_self_regard | 1 | 6501 |
| structural_coverage_classification | 1 | 35290 |
| structural_coverage_detection | 1 | 35290 |
