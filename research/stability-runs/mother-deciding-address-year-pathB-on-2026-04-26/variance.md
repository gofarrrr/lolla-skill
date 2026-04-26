# Stability report — mother-deciding-address-year-pathB-on

Generated: 2026-04-26T14:39:05Z
Runs: 3
Run IDs: 20260426T143905Zstab0, 20260426T144015Zstab1, 20260426T144118Zstab2
Prompt versions consistent across runs: True

## Per-stage stability (Jaccard)

> 1.0 is a WARNING, not a target — signals a specialist that stopped doing semantic judgment. Acceptance is a threshold band: stability moved up from baseline, no neighboring stage regressed, qualitative review confirms cards still do structural work.

| Stage | Mean | Min | Max |
|---|---|---|---|
| Pass 1 (tendencies) | 1.00 | 1.00 | 1.00 |
| Lane 2 — fingerprint moves | 0.06 | 0.00 | 0.17 |
| Lane 2 — recalled candidates | 0.75 | 0.69 | 0.88 |
| Lane 2 — accepted (pre-cap) | 0.26 | 0.07 | 0.55 |
| Lane 2 — shared-avail. accept agreement | 0.33 | 0.11 | 0.67 |
| Lane 2 — detected (post-cap) | 1.00 | 1.00 | 1.00 |
| Lane 2 — capped (top-5 drops) | 1.00 | 1.00 | 1.00 |
| Lane 2 (cheat-sheet anchors) | 1.00 | 1.00 | 1.00 |
| Lane 3 (reframings) | 0.56 | 0.33 | 1.00 |
| Lane 4 (gap dims) | 0.56 | 0.33 | 1.00 |

Embedding mode per run: ['on', 'on', 'on']  ·  consistent: True

### Recall-source distribution per run

| Run | keyword | embedding | both | other |
|---|---|---|---|---|
| `20260426T143905Zstab0` | 60 | 0 | 0 | 0 |
| `20260426T144015Zstab1` | 60 | 0 | 0 | 0 |
| `20260426T144118Zstab2` | 60 | 0 | 0 | 0 |

## Step 6 anchor naming (per-run)

| Run | Named | Total | Rate |
|---|---|---|---|
| `20260426T143905Zstab0` | (no revised_answer) | — | — |
| `20260426T144015Zstab1` | (no revised_answer) | — | — |
| `20260426T144118Zstab2` | (no revised_answer) | — | — |

## Per-run item diff

### Pass 1 tendencies
- `20260426T143905Zstab0`: []
- `20260426T144015Zstab1`: []
- `20260426T144118Zstab2`: []

### Lane 2 fingerprint moves
- `20260426T143905Zstab0`: ['acknowledging surveillance as separate trust issue requiring proactive confession and cessation for long-term repair', 'advising against blocking or confiscating phone to avoid driving grooming underground and preserve visibility', 'prioritizing relationship repair over immediate confrontation with the groomer to enable future cooperation and information sharing', 'recommending controlled disclosure to co-parent with factual limits to minimize undermining without full exclusion', "rejecting alerting friend's parent due to lack of evidence and risk of betraying daughter's trust", 'structuring low-pressure re-engagement to signal safety and normalize interactions amid shame', "weighing trade-offs of reporting to authorities versus therapeutic intervention, factoring in co-parenting dynamics and daughter's trauma risk"]
- `20260426T144015Zstab1`: ['acknowledging surveillance as a separate trust issue requiring proactive confession and cessation for long-term relationship integrity', 'distinguishing immediate punitive controls from sustainable protection via voluntary disclosure', 'evaluating co-parenting communication options by forecasting outcomes of each approach', 'prioritizing relationship repair over immediate confrontation with the groomer to enable future cooperation', 'sequencing low-pressure engagement to thaw shutdown without overwhelming shame response', 'weighing trade-offs of reporting to authorities, factoring in co-parenting dynamics and potential trauma to the daughter']
- `20260426T144118Zstab2`: ['acknowledging surveillance as a separate trust issue requiring future confession and cessation for authentic repair', 'advising against blocking or confiscating the phone to avoid driving grooming underground and eroding trust', 'distinguishing between immediate low-stakes engagement and premature deep talks to respect shame recovery pace', 'prioritizing relationship repair over immediate confrontation with the groomer to enable future cooperation and information sharing', 'recommending controlled disclosure to co-parent with factual limits to minimize undermining without full exclusion', "restricting disclosure about daughter's situation to protect ongoing trust repair, while allowing future general discussions", "weighing trade-offs between reporting to police and therapeutic intervention, factoring in co-parenting dynamics and daughter's potential trauma"]

### Lane 2 recalled candidates
- `20260426T143905Zstab0`: ['active-listening', 'adverse-selection', 'aleatory-epistemic-uncertainty-recognition', 'anchoring', 'auditability-traceability', 'authenticity', 'base-rates', 'bias-blind-spot', 'boundaries', 'branch-solve-merge', 'causal-attribution-resistance', 'chain-of-verification', 'commitment-bias', 'confidence-calibration', 'constructive-feedback-models', 'cross-cultural-communication-frameworks', 'cultural-intelligence', 'dunning-kruger-effect', 'einstellung-effect', 'emotional-intelligence', 'endowment-effect', 'feedback-loops', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'inversion', 'jobs-to-be-done', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'liking-principle', 'meta-cognitive-reflection', 'nash-equilibrium', 'non-violent-communication', 'occams-razor', 'opportunity-cost', 'optimization-theory', 'persistence-grit', 'power-dynamics', 'premortem', 'principal-agent-problem', 'prisoners-dilemma', 'prospect-theory', 'psychological-safety', 'rationalization', 'reasoning-mode-router', 'reciprocity-principle', 'red-queen-effect', 'regression-to-the-mean', 'representativeness-heuristic', 'schema-acquisition', 'second-order-thinking', 'signaling', 'social-proof', 'step-back', 'sunk-cost-fallacy', 'systems-thinking', 'theory-of-constraints', 'wysiati']
- `20260426T144015Zstab1`: ['abstraction', 'active-listening', 'aleatory-epistemic-uncertainty-recognition', 'anchoring', 'auditability-traceability', 'authenticity', 'base-rates', 'bias-blind-spot', 'black-swan-events', 'boundaries', 'branch-solve-merge', 'butterfly-effect', 'causal-attribution-resistance', 'chain-of-verification', 'circle-of-control', 'commitment-bias', 'conjunction-fallacy', 'constructive-feedback-models', 'cross-cultural-communication-frameworks', 'cultural-intelligence', 'desirable-difficulties', 'dunning-kruger-effect', 'einstellung-effect', 'emotional-intelligence', 'endowment-effect', 'feedback-loops', 'feynman-technique', 'five-whys-method', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'inversion', 'jobs-to-be-done', 'latticework-of-mental-models', 'learning-curve', 'liking-principle', 'meta-cognitive-reflection', 'nash-equilibrium', 'non-violent-communication', 'occams-razor', 'opportunity-cost', 'power-dynamics', 'principal-agent-problem', 'prisoners-dilemma', 'probabilistic-thinking', 'prospect-theory', 'psychological-safety', 'rationalization', 'reciprocity-principle', 'regulatory-horizon-scanning', 'representativeness-heuristic', 'schema-acquisition', 'second-order-thinking', 'signaling', 'social-proof', 'step-back', 'sunk-cost-fallacy', 'variation-and-selection', 'wysiati']
- `20260426T144118Zstab2`: ['abstraction', 'active-listening', 'adverse-selection', 'aleatory-epistemic-uncertainty-recognition', 'anchoring', 'auditability-traceability', 'authenticity', 'base-rates', 'bias-blind-spot', 'black-swan-events', 'boundaries', 'branch-solve-merge', 'causal-attribution-resistance', 'chain-of-verification', 'commitment-bias', 'confidence-calibration', 'constructive-feedback-models', 'cross-cultural-communication-frameworks', 'cultural-intelligence', 'dunning-kruger-effect', 'einstellung-effect', 'emotional-intelligence', 'empathy', 'endowment-effect', 'feedback-loops', 'game-theory-payoffs', 'hindsight-bias', 'information-asymmetry', 'intellectual-humility', 'jobs-to-be-done', 'latticework-of-mental-models', 'lean-startup-methodology', 'learning-curve', 'liking-principle', 'meta-cognitive-reflection', 'nash-equilibrium', 'non-violent-communication', 'occams-razor', 'opportunity-cost', 'optimization-theory', 'power-dynamics', 'premortem', 'principal-agent-problem', 'prisoners-dilemma', 'prospect-theory', 'psychological-safety', 'rationalization', 'reasoning-mode-router', 'reciprocity-principle', 'regression-to-the-mean', 'representativeness-heuristic', 'schema-acquisition', 'second-order-thinking', 'signaling', 'social-proof', 'specialization', 'step-back', 'sunk-cost-fallacy', 'systems-thinking', 'theory-of-constraints']

### Lane 2 accepted (pre-cap)
- `20260426T143905Zstab0`: ['emotional-intelligence', 'feedback-loops', 'game-theory-payoffs', 'inversion', 'principal-agent-problem', 'psychological-safety', 'reasoning-mode-router', 'second-order-thinking']
- `20260426T144015Zstab1`: ['circle-of-control', 'emotional-intelligence', 'game-theory-payoffs', 'nash-equilibrium', 'reciprocity-principle', 'variation-and-selection']
- `20260426T144118Zstab2`: ['emotional-intelligence', 'empathy', 'feedback-loops', 'liking-principle', 'principal-agent-problem', 'psychological-safety', 'reasoning-mode-router', 'second-order-thinking', 'theory-of-constraints']

### Lane 2 detected (post-cap)
- `20260426T143905Zstab0`: []
- `20260426T144015Zstab1`: []
- `20260426T144118Zstab2`: []

### Lane 2 capped (top-5 drops)
- `20260426T143905Zstab0`: []
- `20260426T144015Zstab1`: []
- `20260426T144118Zstab2`: []

### Lane 2 cheat-sheet anchors
- `20260426T143905Zstab0`: []
- `20260426T144015Zstab1`: []
- `20260426T144118Zstab2`: []

### Lane 3 reframings
- `20260426T143905Zstab0`: ['counterfactual-reasoning', 'decision-trees']
- `20260426T144015Zstab1`: ['decision-trees', 'intellectual-humility']
- `20260426T144118Zstab2`: ['counterfactual-reasoning', 'decision-trees']

### Lane 4 gap dims
- `20260426T143905Zstab0`: ['feedback-system-dynamics', 'incentive-alignment', 'risk-response', 'uncertainty-type']
- `20260426T144015Zstab1`: ['behavioral-intervention', 'incentive-alignment', 'information-quality', 'uncertainty-type']
- `20260426T144118Zstab2`: ['behavioral-intervention', 'incentive-alignment', 'information-quality', 'uncertainty-type']

## Cost per run (boundary-call tokens, lower bound when embeddings on)

| Run | Calls | Prompt tok | Completion tok | Total tok | Embedding-expansion observed |
|---|---|---|---|---|---|
| `20260426T143905Zstab0` | 15 | 91766 | 6352 | 98118 | 0 |
| `20260426T144015Zstab1` | 15 | 91682 | 6349 | 98031 | 0 |
| `20260426T144118Zstab2` | 15 | 91517 | 6660 | 98177 | 0 |

> Embedding-expansion calls (gpt-4o-mini, temp=0.7) bypass `BoundaryClient` tracing — reported here as 0 with a caveat. Treat boundary_only totals as a lower bound on Lane 2 cost when `embedding_mode = on`.

### Per-stage boundary token cost

#### `20260426T143905Zstab0`

| Stage | Calls | Total tok |
|---|---|---|
| companion_calibrator | 1 | 5809 |
| companion_fingerprint | 1 | 6227 |
| companion_verification_shard_0 | 1 | 9168 |
| companion_verification_shard_1 | 1 | 9257 |
| companion_verification_shard_2 | 1 | 9187 |
| frame_extraction | 1 | 6563 |
| frame_reframing | 1 | 1515 |
| pass1_cluster_authority | 1 | 6722 |
| pass1_cluster_availability | 1 | 6349 |
| pass1_cluster_closure | 1 | 6584 |
| pass1_cluster_incentive | 1 | 6385 |
| pass1_cluster_residual | 1 | 6428 |
| pass1_cluster_self_regard | 1 | 6472 |
| structural_coverage_classification | 1 | 5726 |
| structural_coverage_detection | 1 | 5726 |

#### `20260426T144015Zstab1`

| Stage | Calls | Total tok |
|---|---|---|
| companion_calibrator | 1 | 6023 |
| companion_fingerprint | 1 | 6113 |
| companion_verification_shard_0 | 1 | 9137 |
| companion_verification_shard_1 | 1 | 9452 |
| companion_verification_shard_2 | 1 | 8999 |
| frame_extraction | 1 | 6571 |
| frame_reframing | 1 | 1476 |
| pass1_cluster_authority | 1 | 6722 |
| pass1_cluster_availability | 1 | 6349 |
| pass1_cluster_closure | 1 | 6584 |
| pass1_cluster_incentive | 1 | 6385 |
| pass1_cluster_residual | 1 | 6428 |
| pass1_cluster_self_regard | 1 | 6508 |
| structural_coverage_classification | 1 | 5642 |
| structural_coverage_detection | 1 | 5642 |

#### `20260426T144118Zstab2`

| Stage | Calls | Total tok |
|---|---|---|
| companion_calibrator | 1 | 5825 |
| companion_fingerprint | 1 | 6168 |
| companion_verification_shard_0 | 1 | 9050 |
| companion_verification_shard_1 | 1 | 9378 |
| companion_verification_shard_2 | 1 | 9411 |
| frame_extraction | 1 | 6591 |
| frame_reframing | 1 | 1510 |
| pass1_cluster_authority | 1 | 6722 |
| pass1_cluster_availability | 1 | 6349 |
| pass1_cluster_closure | 1 | 6584 |
| pass1_cluster_incentive | 1 | 6385 |
| pass1_cluster_residual | 1 | 6428 |
| pass1_cluster_self_regard | 1 | 6498 |
| structural_coverage_classification | 1 | 5639 |
| structural_coverage_detection | 1 | 5639 |
