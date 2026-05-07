# Reasoning Substrate Packet Review

- Packet: `pr40-v9-execution-followthrough-packet-review`
- Version: `reasoning_substrate_packet.v1`
- Status: `draft_review_only`
- Runtime policy: `runtime_dormant`
- Source artifacts: `data/knowledge_graph.json`, `data/compiled/model_affordances/affordances_v9.json`, `data/model_sources/manifest.json`

## Review Boundary

- Review-only handoff material.
- Compare candidate shelf usefulness; do not answer the user case.
- Do not choose user-visible output or final wording.
- Deterministic code labels, caps, references, and reports; the LLM/reviewer reasons.

## Packet Counts

| Measure | Count |
| --- | ---: |
| Candidate cards | 12 |
| Reviewed cards | 11 |
| Graph-only cards | 0 |
| Missing reviewed records | 0 |
| Absence-only cards | 0 |
| Source-too-thin cards | 0 |
| Weak/conflicting cards | 1 |

## Candidate Cards

### `baseline-establishment`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane4_gap_route`, `reviewer_note`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane4_gap_route: The plan claims improvement without naming the starting condition, metric, time window, or comparison baseline. Evidence: "track progress"
- Reviewed handoff signals:
  - affordance_ids: baseline-establishment.starting-condition-comparison-gate
  - use_when: A team lacks a shared starting picture of the problem, the success criteria, or the facts that later comparisons should be judged against.
  - case_evidence_needed: The current starting condition.
  - do_not_use_when: The initial baseline has fossilized into doctrine and the team keeps optimizing around an outdated starting frame after the environment has shifted.
  - misuse_guards: Do not let an obsolete baseline become doctrine after context shifts.
  - source_evidence: baseline-establishment.starting-condition-comparison-gate: "a team lacks a shared starting picture of the problem, the success criteria, or the facts that later comparisons should be judged against"
  - treatment_requirements: define-baseline-before-improvement-claim: Require the answer to define what starting condition and comparison standard must exist before claims of improvement, diagnosis, or execution progress can be trusted.
  - absence_record: obsolete-baseline-as-doctrine (not_supported_by_source)

### `bottlenecks`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane4_gap_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane4_gap_route: The rescue plan says to focus on the bottleneck but does not prove which constraint actually limits throughput. Evidence: "focus on the bottleneck"
- Reviewed handoff signals:
  - affordance_ids: bottlenecks.binding-constraint-throughput-check
  - use_when: Local optimization is masking the true throughput limiter.
  - case_evidence_needed: The system, process, launch, migration, or handoff under review.
  - do_not_use_when: The team labels the noisiest queue, most visible complaint, or highest-status pain point as the bottleneck without verifying actual system throughput.
  - misuse_guards: Do not treat the noisiest queue or highest-status pain point as the bottleneck without throughput evidence.
  - source_evidence: bottlenecks.binding-constraint-throughput-check: "local optimization is masking the true throughput limiter"
  - treatment_requirements: verify-binding-throughput-limiter: Require the answer to distinguish the visible pain point from the verified binding constraint and name what evidence would prove the choke point is pacing the whole system.
  - absence_record: noisiest-pain-point-as-bottleneck (not_supported_by_source)

### `auditability-traceability`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane3_frame_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane3_frame_route: The team is about to assign owners and commit to actions, but the advice does not leave a trail of decision, evidence, owner, and change trigger. Evidence: "assign owners"
- Reviewed handoff signals:
  - affordance_ids: auditability-traceability.reconstructable-decision-trail
  - use_when: Decisions, outputs, or model behavior must be explained clearly enough that others can inspect how conclusions were reached.
  - case_evidence_needed: The recommendation, decision, or output that must later be inspected.
  - do_not_use_when: Traceability would become performative documentation that consumes attention without improving judgment, accountability, or learning.
  - misuse_guards: Do not treat documentation volume as proof of judgment quality.
  - source_evidence: auditability-traceability.reconstructable-decision-trail: "clear, reconstructable causal chain"
  - treatment_requirements: preserve-causal-decision-chain: Require the answer to state what would make the recommendation reconstructable later: inputs, assumptions, reasoning steps, owner changes, and the review question the trace must answer.
  - absence_record: performative-documentation-as-auditability (not_supported_by_source)

### `debugging-strategies`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane2_detected_model`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane2_detected_model: The plan responds to bug churn but does not define the failure condition, isolate observed behavior, or verify the root cause before fixing. Evidence: "bug churn"
- Reviewed handoff signals:
  - affordance_ids: debugging-strategies.failure-condition-root-cause-trace
  - use_when: Failures are real but the cause is ambiguous, distributed, or hidden behind several interacting components.
  - case_evidence_needed: The observed failure or suboptimal outcome.
  - do_not_use_when: People start debugging before agreeing on the actual failure condition, so they optimize noise, symptoms, or tools instead of the broken behavior.
  - misuse_guards: Do not debug noise before agreeing on broken behavior.
  - source_evidence: debugging-strategies.failure-condition-root-cause-trace: "failures are real but the cause is ambiguous, distributed, or hidden behind several interacting components"
  - treatment_requirements: define-failure-before-fixing: Require the answer to state the failure condition first, then test root-cause hypotheses against evidence before recommending a fix.
  - absence_record: debugging-before-failure-condition (not_supported_by_source)

### `feedback-loops`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane1_tendency_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane1_tendency_route: The assistant says to get feedback but does not say which signal arrives soon enough to change the next action. Evidence: "getting feedback"
- Reviewed handoff signals:
  - affordance_ids: feedback-loops.closed-loop-action-signal
  - use_when: Outcomes should shape the next action.
  - case_evidence_needed: The action or intervention that will produce feedback.
  - do_not_use_when: Feedback is collected but not used to change behavior, priorities, or design.
  - misuse_guards: Do not instrument the system heavily without changing behavior.
  - source_evidence: feedback-loops.closed-loop-action-signal: "outcomes should shape the next action"
  - treatment_requirements: connect-signal-to-next-adjustment: Require the answer to define the feedback signal, arrival window, decision lever, and next behavior change so measurement becomes a loop rather than passive reporting.
  - absence_record: collected-feedback-without-behavior-change (not_supported_by_source)

### `input-vs-output-goals`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane3_frame_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane3_frame_route: The plan mixes lagging output goals with controllable inputs, so the team may count activity as value. Evidence: "setting goals"
- Reviewed handoff signals:
  - affordance_ids: input-vs-output-goals.controllable-input-output-alignment
  - use_when: Teams know the destination but not the operating discipline.
  - case_evidence_needed: The desired output or strategic destination.
  - do_not_use_when: Input metrics become a substitute for outcomes.
  - misuse_guards: Do not treat activity counts as value delivery.
  - source_evidence: input-vs-output-goals.controllable-input-output-alignment: "teams know the destination but not the operating discipline"
  - treatment_requirements: separate-result-from-controllable-behavior: Require the answer to distinguish the outcome from the controllable inputs and state how those inputs will be checked against the result they are supposed to produce.
  - absence_record: activity-counts-as-value (not_supported_by_source)

### `iteration`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane2_companion_chunk`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane2_companion_chunk: Weekly iteration needs a hypothesis, feedback signal, adjustment rule, and stop/change threshold, not an endless loop of local polishing. Evidence: "iterating weekly"
- Reviewed handoff signals:
  - affordance_ids: iteration.bounded-learning-cycle-gate
  - use_when: The first version is unlikely to be correct and the cheapest path to quality is repeated prototype-test-learn cycles.
  - case_evidence_needed: The hypothesis, prototype, or plan being iterated.
  - do_not_use_when: Iteration continues without stop rules, success thresholds, or a decision about what evidence is strong enough to commit.
  - misuse_guards: Do not let iteration become endless polishing.
  - source_evidence: iteration.bounded-learning-cycle-gate: "repeated prototype-test-learn cycles"
  - treatment_requirements: bound-each-learning-loop: Require the answer to define the next iteration as a bounded learning loop with objective, scope, comparison, threshold, and commitment/reset condition.
  - absence_record: iteration-without-stop-rules (not_supported_by_source)

### `lean-startup-methodology`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane4_gap_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane4_gap_route: The first customer feedback cycle should reduce uncertainty with a real learning metric and a pivot/persevere threshold, not vanity validation. Evidence: "first customer feedback cycle"
- Reviewed handoff signals:
  - affordance_ids: lean-startup-methodology.validated-learning-kill-pivot-gate
  - use_when: A product, market, or behavior hypothesis is still fragile enough that learning speed matters more than polished completeness.
  - case_evidence_needed: The fragile product, market, or behavior hypothesis.
  - do_not_use_when: Teams call any customer contact or usage blip validated learning even though the metric is weak, vanity-driven, or disconnected from real adoption.
  - misuse_guards: Do not call weak usage blips validated learning.
  - source_evidence: lean-startup-methodology.validated-learning-kill-pivot-gate: "validated learning** through rapid, focused experimentation aimed at reducing uncertainty and waste"
  - treatment_requirements: define-validated-learning-threshold: Require the answer to turn the product or market bet into a narrow hypothesis test with honest evidence and a precommitted continuation, pivot, or kill threshold.
  - absence_record: vanity-metric-as-validated-learning (not_supported_by_source)

### `algorithmic-thinking`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane2_detected_model`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane2_detected_model: The rescue plan needs an explicit repeatable procedure with inputs, ordered steps, outputs, and failure handling before it can be handed off.
- Reviewed handoff signals:
  - affordance_ids: algorithmic-thinking.repeatable-handoff-procedure-gate
  - use_when: The task can be decomposed into repeatable steps with clear handoffs, inputs, and output quality checks.
  - case_evidence_needed: The work item or advice that must be executed.
  - do_not_use_when: Novelty, ambiguity, or human emotion is doing most of the causal work and a rigid procedure is being mistaken for actual understanding.
  - misuse_guards: Do not treat a checklist or algorithm as proof of understanding.
  - source_evidence: algorithmic-thinking.repeatable-handoff-procedure-gate: "the task can be decomposed into repeatable steps with clear handoffs, inputs, and output quality checks"
  - treatment_requirements: write-executable-procedure-boundary: Require the answer to turn the proposed action into a bounded procedure with inputs, ordered steps, handoffs, and quality checks, while naming where procedure should stop because context needs judgment.
  - absence_record: procedure-as-understanding (not_supported_by_source)

### `devops-and-continuous-integration`

- Coverage: `conflicting_or_weak_support`
- Pulled by: `lane2_companion_chunk`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane2_companion_chunk: The advice mentions improving CI, but the packet must protect reliability and rollback instead of optimizing local delivery speed alone. Evidence: "improving CI"
- Reviewed handoff signals:
  - affordance_ids: devops-and-continuous-integration.build-observe-adjust-loop
  - use_when: Delivery speed and reliability have to coexist.
  - case_evidence_needed: The delivery system or operational process under review.
  - do_not_use_when: Local pipeline optimization hides system fragility.
  - misuse_guards: Do not treat merge speed, ticket throughput, or release cadence as the whole system outcome.
  - source_evidence: devops-and-continuous-integration.build-observe-adjust-loop: "Most useful when delivery speed and reliability have to coexist"
  - treatment_requirements: map-build-observe-diagnose-adjust-loop: Require the answer to identify the operating loop that connects delivery changes to observation, diagnosis, adjustment, and rollback/reliability protection.
  - absence_record: full-devops-ci-doctrine (not_supported_by_source)

### `goal-setting`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane1_tendency_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane1_tendency_route: The plan asks for goals, but goals need purpose, metric, time boundary, progress check, and conflict with other objectives. Evidence: "setting goals"
- Reviewed handoff signals:
  - affordance_ids: goal-setting.outcome-checkpoint-alignment-gate
  - use_when: Effort is scattered and the team needs one explicit outcome to align trade-offs, sequencing, and measurement.
  - case_evidence_needed: The desired outcome and the larger purpose it serves.
  - do_not_use_when: Goals are sticky enough to organize action but not revisited often enough to reflect changed evidence, constraints, or strategic reality.
  - misuse_guards: Do not confuse verbal commitment with owned execution checkpoints.
  - source_evidence: goal-setting.outcome-checkpoint-alignment-gate: "effort is scattered and the team needs one explicit outcome to align trade-offs, sequencing, and measurement"
  - treatment_requirements: turn-aspiration-into-owned-checkpoints: Require the answer to convert the goal from aspiration into a concrete operating target with owner, checkpoint, threshold, cadence, and revision condition.
  - absence_record: stale-goal-as-commitment (not_supported_by_source)

### `habit-formation`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane3_frame_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane3_frame_route: The team wants better execution habits, but the packet should ask for cue, routine, reward, environment, friction, and repeatability.
- Reviewed handoff signals:
  - affordance_ids: habit-formation.automatic-action-design-check
  - use_when: Execution quality depends on repeating the right small behaviors.
  - case_evidence_needed: The repeated behavior the plan depends on.
  - do_not_use_when: Automation replaces judgment because the environment has changed enough that automatic behavior is now solving yesterday's problem.
  - misuse_guards: Do not treat habit as moral virtue or willpower.
  - source_evidence: habit-formation.automatic-action-design-check: "execution quality depends on repeating the right small behaviors"
  - treatment_requirements: design-repeatable-behavior-loop: Require the answer to turn the execution need into a cue-response-reward behavior loop that reduces friction while preserving judgment when context changes.
  - absence_record: automaticity-as-permanent-good (not_supported_by_source)

## Suppressed Candidates

- `iteration` (duplicate_model_id; reviewed_affordance_available)

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
