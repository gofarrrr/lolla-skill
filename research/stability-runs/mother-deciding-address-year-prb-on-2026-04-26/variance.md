# Stability report — mother-deciding-address-year-prb-on

Generated: 2026-04-26T12:32:01Z
Runs: 3
Run IDs: 20260426T123201Zstab0, 20260426T123258Zstab1, 20260426T123358Zstab2
Prompt versions consistent across runs: True

## Per-stage stability (Jaccard)

> 1.0 is a WARNING, not a target — signals a specialist that stopped doing semantic judgment. Acceptance is a threshold band: stability moved up from baseline, no neighboring stage regressed, qualitative review confirms cards still do structural work.

| Stage | Mean | Min | Max |
|---|---|---|---|
| Pass 1 (tendencies) | 1.00 | 1.00 | 1.00 |
| Lane 2 — fingerprint moves | 0.09 | 0.09 | 0.09 |
| Lane 2 — recalled candidates | 0.77 | 0.69 | 0.88 |
| Lane 2 — accepted (pre-cap) | 0.31 | 0.19 | 0.39 |
| Lane 2 — shared-avail. accept agreement | 0.36 | 0.25 | 0.43 |
| Lane 2 — detected (post-cap) | 0.26 | 0.11 | 0.43 |
| Lane 2 — capped (top-5 drops) | 0.21 | 0.11 | 0.29 |
| Lane 2 (cheat-sheet anchors) | 0.26 | 0.11 | 0.43 |
| Lane 3 (reframings) | 0.22 | 0.00 | 0.33 |
| Lane 4 (gap dims) | 0.45 | 0.20 | 0.75 |

Embedding mode per run: ['on', 'on', 'on']  ·  consistent: True

### Recall-source distribution per run

| Run | keyword | embedding | both | other |
|---|---|---|---|---|
| `20260426T123201Zstab0` | 60 | 0 | 0 | 0 |
| `20260426T123258Zstab1` | 60 | 0 | 0 | 0 |
| `20260426T123358Zstab2` | 60 | 0 | 0 | 0 |

## Step 6 anchor naming (per-run)

| Run | Named | Total | Rate |
|---|---|---|---|
| `20260426T123201Zstab0` | (no revised_answer) | — | — |
| `20260426T123258Zstab1` | (no revised_answer) | — | — |
| `20260426T123358Zstab2` | (no revised_answer) | — | — |

## Per-run item diff

### Pass 1 tendencies
- `20260426T123201Zstab0`: []
- `20260426T123258Zstab1`: []
- `20260426T123358Zstab2`: []

### Lane 2 fingerprint moves
- `20260426T123201Zstab0`: ['differentiating immediate protective instincts from evidence-based actions to avoid relational sabotage', 'distinguishing emotional satisfaction from long-term safety goals to guide decision trade-offs', 'evaluating reporting trade-offs by integrating co-parenting dynamics and therapeutic vs legal outcomes', 'prioritizing relationship repair over immediate confrontation with the groomer to enable future cooperation', 'sequencing low-pressure engagement to signal safety and normalize interaction without forcing resolution', 'weighing surveillance admission as a trust repair opportunity despite short-term anger, to preempt larger future breach']
- `20260426T123258Zstab1`: ['acknowledging surveillance as a separate trust issue requiring future confession and repair', "deferring disclosure to others without evidence to protect daughter's trust repair", 'distinguishing immediate safety from punitive controls to avoid driving grooming underground', 'prioritizing relationship repair over immediate confrontation with the groomer to enable future cooperation', 'sequencing low-stakes engagement to thaw shame without pressure', "weighing trade-offs of reporting to police against co-parenting dynamics and daughter's trauma risk"]
- `20260426T123358Zstab2`: ['calibrating parental action to adolescent shame psychology, using low-pressure signals to thaw shutdown', 'distinguishing therapeutic intervention from legal accountability as divergent paths with distinct outcomes for child protection', "evaluating co-parenting dynamics as constraint on reporting, predicting ex's minimization could undermine legal process", 'prioritizing relationship repair over immediate confrontation with the groomer to enable future cooperation', 'sequencing disclosure of surveillance breach to minimize compounded trust damage, timing it post-repair', 'weighing trade-offs between punitive controls and behavioral incentives, favoring trust-building to prevent evasion']

### Lane 2 recalled candidates
- `20260426T123201Zstab0`: ['abstraction', 'active-listening', 'aleatory-epistemic-uncertainty-recognition', 'anchoring', 'auditability-traceability', 'authenticity', 'base-rates', 'bias-blind-spot', 'black-swan-events', 'boundaries', 'branch-solve-merge', 'butterfly-effect', 'causal-attribution-resistance', 'chain-of-verification', 'commitment-bias', 'confidence-calibration', 'constructive-feedback-models', 'cross-cultural-communication-frameworks', 'cultural-intelligence', 'desirable-difficulties', 'dunning-kruger-effect', 'einstellung-effect', 'emotional-intelligence', 'endowment-effect', 'feedback-loops', 'feynman-technique', 'five-whys-method', 'game-theory-payoffs', 'goal-setting', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'inversion', 'jobs-to-be-done', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'liking-principle', 'non-violent-communication', 'occams-razor', 'opportunity-cost', 'optimization-theory', 'power-dynamics', 'principal-agent-problem', 'prisoners-dilemma', 'probabilistic-thinking', 'prospect-theory', 'psychological-safety', 'rationalization', 'reciprocity-principle', 'red-queen-effect', 'representativeness-heuristic', 'second-order-thinking', 'signaling', 'social-proof', 'step-back', 'sunk-cost-fallacy', 'systems-thinking', 'variation-and-selection', 'wysiati']
- `20260426T123258Zstab1`: ['abstraction', 'active-listening', 'adverse-selection', 'aleatory-epistemic-uncertainty-recognition', 'anchoring', 'auditability-traceability', 'authenticity', 'base-rates', 'bias-blind-spot', 'black-swan-events', 'boundaries', 'branch-solve-merge', 'butterfly-effect', 'causal-attribution-resistance', 'chain-of-verification', 'circle-of-control', 'commitment-bias', 'confidence-calibration', 'constructive-feedback-models', 'cross-cultural-communication-frameworks', 'cultural-intelligence', 'dunning-kruger-effect', 'einstellung-effect', 'emotional-intelligence', 'endowment-effect', 'feedback-loops', 'feynman-technique', 'five-whys-method', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'inversion', 'jobs-to-be-done', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'liking-principle', 'non-violent-communication', 'occams-razor', 'opportunity-cost', 'power-dynamics', 'principal-agent-problem', 'prisoners-dilemma', 'probabilistic-thinking', 'prospect-theory', 'psychological-safety', 'rationalization', 'reciprocity-principle', 'red-queen-effect', 'representativeness-heuristic', 'schema-acquisition', 'second-order-thinking', 'signaling', 'social-proof', 'step-back', 'sunk-cost-fallacy', 'time-tested-validation', 'variation-and-selection', 'wysiati']
- `20260426T123358Zstab2`: ['active-listening', 'adverse-selection', 'aleatory-epistemic-uncertainty-recognition', 'anchoring', 'auditability-traceability', 'authenticity', 'base-rates', 'bias-blind-spot', 'black-swan-events', 'boundaries', 'butterfly-effect', 'causal-attribution-resistance', 'chain-of-verification', 'circle-of-control', 'commitment-bias', 'confidence-calibration', 'constructive-feedback-models', 'correlation-vs-causation', 'cross-cultural-communication-frameworks', 'cultural-intelligence', 'einstellung-effect', 'emotional-intelligence', 'feedback-loops', 'feynman-technique', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'inversion', 'jobs-to-be-done', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'liking-principle', 'meta-cognitive-reflection', 'metacognitive-questioning', 'nash-equilibrium', 'non-violent-communication', 'occams-razor', 'opportunity-cost', 'power-dynamics', 'principal-agent-problem', 'prisoners-dilemma', 'probabilistic-thinking', 'prospect-theory', 'psychological-safety', 'rationalization', 'reasoning-mode-router', 'reciprocity-principle', 'regression-to-the-mean', 'representativeness-heuristic', 'schema-acquisition', 'second-order-thinking', 'signaling', 'social-proof', 'specialization', 'step-back', 'sunk-cost-fallacy', 'systems-thinking', 'theory-of-constraints']

### Lane 2 accepted (pre-cap)
- `20260426T123201Zstab0`: ['active-listening', 'anchoring', 'emotional-intelligence', 'feedback-loops', 'goal-setting', 'information-asymmetry', 'intellectual-humility', 'jobs-to-be-done', 'liking-principle', 'opportunity-cost', 'optimization-theory', 'power-dynamics', 'probabilistic-thinking', 'psychological-safety', 'second-order-thinking', 'step-back']
- `20260426T123258Zstab1`: ['active-listening', 'anchoring', 'base-rates', 'boundaries', 'emotional-intelligence', 'game-theory-payoffs', 'intellectual-humility', 'inversion', 'liking-principle', 'non-violent-communication', 'probabilistic-thinking', 'psychological-safety', 'representativeness-heuristic', 'second-order-thinking', 'step-back', 'sunk-cost-fallacy']
- `20260426T123358Zstab2`: ['active-listening', 'aleatory-epistemic-uncertainty-recognition', 'circle-of-control', 'emotional-intelligence', 'game-theory-payoffs', 'intellectual-humility', 'inversion', 'latticework-of-mental-models', 'liking-principle', 'nash-equilibrium', 'power-dynamics', 'reasoning-mode-router', 'representativeness-heuristic', 'specialization', 'sunk-cost-fallacy']

### Lane 2 detected (post-cap)
- `20260426T123201Zstab0`: ['feedback-loops', 'intellectual-humility', 'opportunity-cost', 'psychological-safety', 'step-back']
- `20260426T123258Zstab1`: ['emotional-intelligence', 'intellectual-humility', 'psychological-safety', 'representativeness-heuristic', 'step-back']
- `20260426T123358Zstab2`: ['active-listening', 'aleatory-epistemic-uncertainty-recognition', 'intellectual-humility', 'power-dynamics', 'representativeness-heuristic']

### Lane 2 capped (top-5 drops)
- `20260426T123201Zstab0`: ['active-listening', 'anchoring', 'emotional-intelligence', 'goal-setting', 'information-asymmetry', 'jobs-to-be-done', 'liking-principle', 'optimization-theory', 'power-dynamics', 'probabilistic-thinking', 'second-order-thinking']
- `20260426T123258Zstab1`: ['active-listening', 'anchoring', 'base-rates', 'boundaries', 'game-theory-payoffs', 'inversion', 'liking-principle', 'non-violent-communication', 'probabilistic-thinking', 'second-order-thinking', 'sunk-cost-fallacy']
- `20260426T123358Zstab2`: ['circle-of-control', 'emotional-intelligence', 'game-theory-payoffs', 'inversion', 'latticework-of-mental-models', 'liking-principle', 'nash-equilibrium', 'reasoning-mode-router', 'specialization', 'sunk-cost-fallacy']

### Lane 2 cheat-sheet anchors
- `20260426T123201Zstab0`: ['feedback-loops', 'intellectual-humility', 'opportunity-cost', 'psychological-safety', 'step-back']
- `20260426T123258Zstab1`: ['emotional-intelligence', 'intellectual-humility', 'psychological-safety', 'representativeness-heuristic', 'step-back']
- `20260426T123358Zstab2`: ['active-listening', 'aleatory-epistemic-uncertainty-recognition', 'intellectual-humility', 'power-dynamics', 'representativeness-heuristic']

### Lane 3 reframings
- `20260426T123201Zstab0`: ['decision-trees', 'trade-offs']
- `20260426T123258Zstab1`: ['boundaries', 'decision-trees']
- `20260426T123358Zstab2`: ['boundaries', 'trust-repair-first-principles']

### Lane 4 gap dims
- `20260426T123201Zstab0`: ['commitment-reversibility', 'incentive-alignment', 'uncertainty-type']
- `20260426T123258Zstab1`: ['commitment-reversibility', 'incentive-alignment', 'risk-response', 'uncertainty-type']
- `20260426T123358Zstab2`: ['incentive-alignment', 'risk-response', 'stakeholder-alignment']

## Cost per run (boundary-call tokens, lower bound when embeddings on)

| Run | Calls | Prompt tok | Completion tok | Total tok | Embedding-expansion observed |
|---|---|---|---|---|---|
| `20260426T123201Zstab0` | 20 | 122152 | 6844 | 128996 | 0 |
| `20260426T123258Zstab1` | 20 | 122938 | 7059 | 129997 | 0 |
| `20260426T123358Zstab2` | 19 | 115832 | 6577 | 122409 | 0 |

> Embedding-expansion calls (gpt-4o-mini, temp=0.7) bypass `BoundaryClient` tracing — reported here as 0 with a caveat. Treat boundary_only totals as a lower bound on Lane 2 cost when `embedding_mode = on`.

### Per-stage boundary token cost

#### `20260426T123201Zstab0`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 6066 |
| companion_verification_abductive | 1 | 6487 |
| companion_verification_analogical | 1 | 6809 |
| companion_verification_causal | 1 | 7192 |
| companion_verification_counterfactual | 1 | 7075 |
| companion_verification_deductive | 1 | 6898 |
| companion_verification_diagnostic | 1 | 8229 |
| companion_verification_metacognitive | 1 | 7610 |
| companion_verification_probabilistic | 1 | 6827 |
| companion_verification_systems | 1 | 7586 |
| frame_extraction | 1 | 6581 |
| frame_reframing | 1 | 1520 |
| pass1_cluster_authority | 1 | 6722 |
| pass1_cluster_availability | 1 | 6349 |
| pass1_cluster_closure | 1 | 6584 |
| pass1_cluster_incentive | 1 | 6385 |
| pass1_cluster_residual | 1 | 6428 |
| pass1_cluster_self_regard | 1 | 6472 |
| structural_coverage_classification | 1 | 5588 |
| structural_coverage_detection | 1 | 5588 |

#### `20260426T123258Zstab1`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 6168 |
| companion_verification_abductive | 1 | 6548 |
| companion_verification_analogical | 1 | 6785 |
| companion_verification_causal | 1 | 6963 |
| companion_verification_counterfactual | 1 | 7232 |
| companion_verification_deductive | 1 | 6851 |
| companion_verification_diagnostic | 1 | 8615 |
| companion_verification_metacognitive | 1 | 7708 |
| companion_verification_probabilistic | 1 | 7180 |
| companion_verification_systems | 1 | 7480 |
| frame_extraction | 1 | 6592 |
| frame_reframing | 1 | 1459 |
| pass1_cluster_authority | 1 | 6722 |
| pass1_cluster_availability | 1 | 6349 |
| pass1_cluster_closure | 1 | 6584 |
| pass1_cluster_incentive | 1 | 6385 |
| pass1_cluster_residual | 1 | 6428 |
| pass1_cluster_self_regard | 1 | 6502 |
| structural_coverage_classification | 1 | 5723 |
| structural_coverage_detection | 1 | 5723 |

#### `20260426T123358Zstab2`

| Stage | Calls | Total tok |
|---|---|---|
| companion_fingerprint | 1 | 6120 |
| companion_verification_analogical | 1 | 6667 |
| companion_verification_causal | 1 | 7379 |
| companion_verification_counterfactual | 1 | 7172 |
| companion_verification_deductive | 1 | 6677 |
| companion_verification_diagnostic | 1 | 8339 |
| companion_verification_metacognitive | 1 | 7612 |
| companion_verification_probabilistic | 1 | 7020 |
| companion_verification_systems | 1 | 7495 |
| frame_extraction | 1 | 6528 |
| frame_reframing | 1 | 1380 |
| pass1_cluster_authority | 1 | 6722 |
| pass1_cluster_availability | 1 | 6349 |
| pass1_cluster_closure | 1 | 6584 |
| pass1_cluster_incentive | 1 | 6385 |
| pass1_cluster_residual | 1 | 6428 |
| pass1_cluster_self_regard | 1 | 6472 |
| structural_coverage_classification | 1 | 5540 |
| structural_coverage_detection | 1 | 5540 |
