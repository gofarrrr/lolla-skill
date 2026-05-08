# Reasoning Substrate Packet Review

- Packet: `pr43-v10-risk-reversibility-packet-review`
- Version: `reasoning_substrate_packet.v1`
- Status: `draft_review_only`
- Runtime policy: `runtime_dormant`
- Source artifacts: `data/knowledge_graph.json`, `data/compiled/model_affordances/affordances_v10.json`, `data/model_sources/manifest.json`

## Review Boundary

- Review-only handoff material.
- Compare candidate shelf usefulness; do not answer the user case.
- Do not choose user-visible output or final wording.
- Deterministic code labels, caps, references, and reports; the LLM/reviewer reasons.

## Packet Counts

| Measure | Count |
| --- | ---: |
| Candidate cards | 12 |
| Reviewed cards | 12 |
| Graph-only cards | 0 |
| Missing reviewed records | 0 |
| Absence-only cards | 0 |
| Source-too-thin cards | 0 |
| Weak/conflicting cards | 0 |

## Candidate Cards

### `risk-vs-uncertainty`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane1_tendency_route`, `reviewer_note`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane1_tendency_route: The advice treats the regulated market entry as measurable enough to fund, but the key drivers may still be ambiguous or unstable. Evidence: "approve the market-entry budget"
- Reviewed handoff signals:
  - affordance_ids: risk-vs-uncertainty.commitment-sizing-under-unknowns
  - use_when: A plan assigns forecast-like confidence while core drivers remain ambiguous, unstable, or only partly observable.
  - case_evidence_needed: The proposed commitment and its reversibility.
  - do_not_use_when: The decision already has stable reference classes, credible probabilities, and operator-level thresholds.
  - misuse_guards: Do not use uncertainty language to avoid execution when measurable risk is already available.
  - source_evidence: risk-vs-uncertainty.commitment-sizing-under-unknowns: "Most useful when confidence is outrunning evidence"
  - treatment_requirements: classify-risk-before-commitment: Require the answer to classify what is measurable risk versus unresolved uncertainty, then size the commitment around reversibility, buffers, no-regrets moves, and explicit stop/change evidence.
  - absence_record: uncertainty-as-execution-avoidance (not_supported_by_source)

### `switching-costs`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane4_gap_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane4_gap_route: The vendor migration is described as reversible, but the advice does not name dual-run drag, data history, integration dependencies, or unwind governance. Evidence: "start vendor migration"
- Reviewed handoff signals:
  - affordance_ids: switching-costs.reversibility-decay-exit-plan
  - use_when: A platform or ERP exit is framed as reversible while dual-run coexistence, partner workflows, and reporting dependencies shrink the rollback window.
  - case_evidence_needed: The incumbent state, alternative state, and proposed switch.
  - do_not_use_when: Switching cost is reduced to license price or headline migration budget.
  - misuse_guards: Do not treat license price as the full switching cost.
  - source_evidence: switching-costs.reversibility-decay-exit-plan: "a platform or ERP exit is framed as reversible even though dual-run coexistence, partner workflows, and reporting dependencies are quietly shrinking the rollback window"
  - treatment_requirements: map-dual-run-and-unwind-gates: Require the answer to treat the exit plan as a decision object by mapping dual-run dependencies, reversal-cost growth, rollback ownership, and unwind gates.
  - absence_record: license-price-as-switching-cost (not_supported_by_source)

### `redundancy`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane4_gap_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane4_gap_route: The plan says to add backups, but does not test whether the backup is independent, owned, usable, and worth the added cost. Evidence: "adding backups"
- Reviewed handoff signals:
  - affordance_ids: redundancy.single-point-failure-backup-test
  - use_when: Single-point failure is unacceptable because continuity, resilience, recall, or survival matters more than lean elegance.
  - case_evidence_needed: The component, decision path, memory, resource, or viewpoint that could fail.
  - do_not_use_when: Duplication is added by habit without a named failure mode.
  - misuse_guards: Do not treat duplication as free insurance.
  - source_evidence: redundancy.single-point-failure-backup-test: "Most useful when single-point failure is unacceptable"
  - treatment_requirements: tie-backup-to-failure-mode: Require the answer to justify redundancy by naming the specific failure mode it protects against, the backup path it creates, and the point where added duplication becomes drag.
  - absence_record: duplication-as-free-insurance (not_supported_by_source)

### `regulatory-horizon-scanning`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane3_frame_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane3_frame_route: The advice says to monitor regulatory news but does not specify weak-signal thresholds, owners, response triggers, or present-day options. Evidence: "monitoring regulatory news"
- Reviewed handoff signals:
  - affordance_ids: regulatory-horizon-scanning.weak-signal-response-trigger
  - use_when: External rules, enforcement priorities, or policy narratives are moving early enough that waiting for certainty would create strategic or compliance lag.
  - case_evidence_needed: The rule, enforcement priority, policy narrative, or weak signal being monitored.
  - do_not_use_when: Horizon scanning would become trend-slide collection without thresholds, owners, or response triggers.
  - misuse_guards: Do not treat regulatory trend language as readiness.
  - source_evidence: regulatory-horizon-scanning.weak-signal-response-trigger: "external rules, enforcement priorities, or policy narratives are moving early enough that waiting for certainty would create strategic or compliance lag"
  - treatment_requirements: convert-signal-to-owner-trigger: Require the answer to translate regulatory weak signals into explicit scenarios, named owners, thresholds, preparatory options, and present-day decisions that would change if the signal strengthens.
  - absence_record: trend-slide-as-readiness (not_supported_by_source)

### `cybersecurity-thinking-models`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane2_detected_model`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane2_detected_model: The migration and launch plan mentions security, but does not map adversarial incentives, control owners, or cross-layer failure chains. Evidence: "improving security"
- Reviewed handoff signals:
  - affordance_ids: cybersecurity-thinking-models.adversarial-failure-chain-map
  - use_when: The problem is adversarial, fast-changing, and can cascade across technical, human, and governance layers.
  - case_evidence_needed: The asset, dependency, or surface being protected.
  - do_not_use_when: The team is fetishizing threat models, simulations, or mental frameworks while skipping asset specificity, attack surface reality, or operational ownership.
  - misuse_guards: Do not treat control enumeration as security.
  - source_evidence: cybersecurity-thinking-models.adversarial-failure-chain-map: "the problem is adversarial, fast-changing, and capable of cascading across technical, human, and governance layers at once"
  - treatment_requirements: name-adversary-asset-owner-chain: Require the answer to identify the asset, adversary or misaligned actor, attack or failure chain, control owner, and fallback dependency before treating the security plan as robust.
  - absence_record: control-enumeration-as-security (not_supported_by_source)

### `non-linear-dynamics`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane4_gap_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane4_gap_route: A local launch acceleration could amplify downstream support load, regulatory exposure, or adoption loops instead of producing a linear gain.
- Reviewed handoff signals:
  - affordance_ids: non-linear-dynamics.feedback-threshold-local-optimization-check
  - use_when: Modest interventions may trigger disproportionate upside, delayed blowback, or threshold crossings.
  - case_evidence_needed: The local intervention or optimization being proposed.
  - do_not_use_when: Complexity language is being used to avoid concrete levers, checkpoints, or experiments.
  - misuse_guards: Do not invoke complexity to avoid choosing a lever.
  - source_evidence: non-linear-dynamics.feedback-threshold-local-optimization-check: "Most useful when small moves can create outsized effects"
  - treatment_requirements: map-loop-delay-and-lever: Require the answer to name the feedback loop, delay, or threshold that makes the system non-linear, then state the concrete lever, checkpoint, or experiment that can still improve the system.
  - absence_record: complexity-as-choice-avoidance (not_supported_by_source)

### `tipping-points`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane3_frame_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane3_frame_route: Early customer interest is being treated as a possible breakthrough without naming the controlling threshold or prerequisite buildup. Evidence: "early customer interest"
- Reviewed handoff signals:
  - affordance_ids: tipping-points.threshold-prerequisite-test
  - use_when: Progress is not linear and one constrained variable, threshold, or social dynamic could unlock disproportionate change.
  - case_evidence_needed: The proposed threshold variable or social dynamic.
  - do_not_use_when: Leaders are romanticizing breakthrough moments while underinvesting in the prerequisite buildup.
  - misuse_guards: Do not romanticize breakthrough while ignoring slow prerequisite buildup.
  - source_evidence: tipping-points.threshold-prerequisite-test: "a threshold where a small quantitative change leads to a massive, non-linear qualitative shift"
  - treatment_requirements: name-threshold-and-prerequisite-buildup: Require the answer to identify the controlling threshold, the prerequisite buildup, and the evidence that a marginal move could become self-reinforcing instead of merely incremental.
  - absence_record: romantic-breakthrough-without-buildup (not_supported_by_source)

### `butterfly-effect`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane2_companion_chunk`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane2_companion_chunk: The advice could understate how one small migration or compliance choice propagates through dependencies unless a plausible cascade path is named.
- Reviewed handoff signals:
  - affordance_ids: butterfly-effect.cascade-path-trace
  - use_when: Seemingly local decisions could cascade through interdependence, delay, amplification, or sequencing.
  - case_evidence_needed: The local intervention or small initial condition.
  - do_not_use_when: Butterfly-effect language would justify vague fear or grandiosity without a plausible transmission path.
  - misuse_guards: Do not use butterfly-effect language for vague fear or grandiosity.
  - source_evidence: butterfly-effect.cascade-path-trace: "small changes in inputs can lead to massive, non-linear, and often unpredictable changes in outputs over time"
  - treatment_requirements: trace-plausible-cascade-path: Require the answer to trace how a small move could propagate through the system, naming the first-order effect, downstream dependency, amplification path, and where the chain becomes speculative.
  - absence_record: cascade-mysticism (not_supported_by_source)

### `chaos-theory`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane2_companion_chunk`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane2_companion_chunk: The environment may be too unstable for exact six-week forecasts, so the packet should favor robustness, monitoring, slack, and reversibility. Evidence: "within six weeks"
- Reviewed handoff signals:
  - affordance_ids: chaos-theory.resilience-over-precision-bet-sizing
  - use_when: Local interventions, timing shifts, or minor shocks can propagate unpredictably.
  - case_evidence_needed: The nonlinear system or environment under decision.
  - do_not_use_when: Chaos language is being used as a reason to avoid prioritization, bounded bets, or accountability.
  - misuse_guards: Do not use chaos as an excuse for helplessness or lack of accountability.
  - source_evidence: chaos-theory.resilience-over-precision-bet-sizing: "Works when resilience matters more than precise prediction"
  - treatment_requirements: size-bet-for-adaptation-not-forecast: Require the answer to shift from exact prediction to bounded exposure: name the bet size, buffer, monitoring signal, reversibility path, and adaptation trigger.
  - absence_record: chaos-as-accountability-escape (not_supported_by_source)

### `combinatorial-effects`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane4_gap_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane4_gap_route: Regulation, vendor migration, security exposure, and early demand may interact non-additively, so the packet should find make-or-break combinations.
- Reviewed handoff signals:
  - affordance_ids: combinatorial-effects.make-or-break-interaction-map
  - use_when: The visible result comes from several reinforcing forces rather than one dominant driver.
  - case_evidence_needed: The candidate interacting forces.
  - do_not_use_when: Combination thinking becomes complexity worship.
  - misuse_guards: Do not make the analysis more complex mainly to sound sophisticated.
  - source_evidence: combinatorial-effects.make-or-break-interaction-map: "Most useful when no single cause explains the outcome"
  - treatment_requirements: identify-few-critical-interactions: Require the answer to isolate the few interactions that could create emergent lift or fragility, rather than expanding the variable list for sophistication.
  - absence_record: complexity-worship (not_supported_by_source)

### `critical-mass`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane3_frame_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane3_frame_route: Early adoption may not become self-sustaining unless the minimum density of customers, workflow, trust, or support exists. Evidence: "early customer interest"
- Reviewed handoff signals:
  - affordance_ids: critical-mass.viability-threshold-density-test
  - use_when: Adoption, liquidity, trust, or participation only starts working once activity crosses a minimum density.
  - case_evidence_needed: The threshold variable and the area, segment, or network boundary.
  - do_not_use_when: Early energy, launch excitement, or one-off seeding is being mistaken for durable mass.
  - misuse_guards: Do not treat launch excitement as threshold security.
  - source_evidence: critical-mass.viability-threshold-density-test: "threshold that determines viability and sustained momentum"
  - treatment_requirements: define-threshold-boundary-and-loop: Require the answer to define the minimum viable threshold, the boundary where it must hold, and the reinforcement loop that turns isolated wins into self-sustaining momentum.
  - absence_record: launch-energy-as-durable-mass (not_supported_by_source)

### `prospect-theory`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane1_tendency_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane1_tendency_route: The team may double down or unwind under loss-frame pressure, so the packet should distinguish decision quality from reference-point distortion. Evidence: "double down or unwind"
- Reviewed handoff signals:
  - affordance_ids: prospect-theory.loss-frame-decision-quality-check
  - use_when: The choice depends heavily on reference points, recent expectations, or fear of losing what people think they already have.
  - case_evidence_needed: The current reference point or perceived entitlement.
  - do_not_use_when: Framing is being used to manipulate rather than clarify.
  - misuse_guards: Do not use loss framing to force compliance.
  - source_evidence: prospect-theory.loss-frame-decision-quality-check: "Most useful when behavior is being driven by perceived losses and gains, not objective value"
  - treatment_requirements: separate-frame-from-economics: Require the answer to identify the reference point and loss/gain frame, then compare it against objective economics, long-term value, and manipulation risk.
  - absence_record: manipulative-loss-framing (not_supported_by_source)

## Suppressed Candidates

- `switching-costs` (duplicate_model_id; reviewed_affordance_available)

## Blocked Surfaces

- `live_observatory_rendering`
- `memo_integration`
- `step8_integration`
- `step6_integration`
- `lane4_integration`
- `lolla_runtime_use`
- `user_facing_decision_pressure_block`
- `prompt_changes`
- `generation_changes`
- `new_extraction`
- `batch_3b`
- `paid_gate4_reruns_by_default`
