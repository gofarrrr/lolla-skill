# Reasoning Substrate Packet Review

- Packet: `pr40-v8-execution-followthrough-packet-review`
- Version: `reasoning_substrate_packet.v1`
- Status: `draft_review_only`
- Runtime policy: `runtime_dormant`
- Source artifacts: `data/knowledge_graph.json`, `data/compiled/model_affordances/affordances_v8.json`, `data/model_sources/manifest.json`

## Review Boundary

- Review-only handoff material.
- Compare candidate shelf usefulness; do not answer the user case.
- Do not choose user-visible output or final wording.
- Deterministic code labels, caps, references, and reports; the LLM/reviewer reasons.

## Packet Counts

| Measure | Count |
| --- | ---: |
| Candidate cards | 12 |
| Reviewed cards | 0 |
| Graph-only cards | 12 |
| Missing reviewed records | 12 |
| Absence-only cards | 0 |
| Source-too-thin cards | 0 |
| Weak/conflicting cards | 0 |

## Candidate Cards

### `baseline-establishment`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane4_gap_route`, `reviewer_note`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane4_gap_route: The plan claims improvement without naming the starting condition, metric, time window, or comparison baseline. Evidence: "track progress"
- Graph-only recall material:
  - select_when: A team lacks a shared starting picture of the problem, success criteria, or the facts that later comparisons should be judged against.
  - danger_when: The initial baseline has fossilized into doctrine even though the environment or goal has materially shifted.
  - failure_modes: Teams waste effort when they launch analysis or execution without agreeing on the starting condition, target outcome, or frame for comparison.
  - premortem_questions: What exactly is our starting condition, and what evidence says that starting picture is accurate enough to compare against later?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `bottlenecks`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane4_gap_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane4_gap_route: The rescue plan says to focus on the bottleneck but does not prove which constraint actually limits throughput. Evidence: "focus on the bottleneck"
- Graph-only recall material:
  - select_when: Local optimization is masking the true throughput limiter.
  - danger_when: The team is labeling the noisiest queue, most visible complaint, or highest-status pain point as the bottleneck without verifying actual throughput.
  - failure_modes: Teams can mistake the noisiest queue or highest-status pain point for the real constraint.
  - premortem_questions: Which step would still throttle the whole system if I funded every other improvement on the list?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `auditability-traceability`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane3_frame_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane3_frame_route: The team is about to assign owners and commit to actions, but the advice does not leave a trail of decision, evidence, owner, and change trigger. Evidence: "assign owners"
- Graph-only recall material:
  - select_when: Decisions, outputs, or model behavior must be explained clearly enough that others can inspect how the conclusion was reached.
  - danger_when: Traceability is becoming performative documentation that consumes attention without improving judgment, accountability, or learning.
  - failure_modes: Traceability can become performative documentation that consumes attention without improving judgment, accountability, or learning.
  - premortem_questions: Is the worst case bad enough?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `debugging-strategies`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane2_detected_model`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane2_detected_model: The plan responds to bug churn but does not define the failure condition, isolate observed behavior, or verify the root cause before fixing. Evidence: "bug churn"
- Graph-only recall material:
  - select_when: A failure is real but the cause is ambiguous, distributed, or hidden behind several interacting components.
  - danger_when: People have not agreed on the actual failure condition, so debugging would optimize noise, symptoms, or tools instead of broken behavior.
  - failure_modes: Debugging can optimize noise when the team has not agreed on the actual failure condition.
  - premortem_questions: What's the one-day answer?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `feedback-loops`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane1_tendency_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane1_tendency_route: The assistant says to get feedback but does not say which signal arrives soon enough to change the next action. Evidence: "getting feedback"
- Graph-only recall material:
  - select_when: Outcomes should shape the next action and the system can observe consequences quickly enough to learn instead of repeating the same move blindly.
  - danger_when: The organization is collecting signal but never translating it into changed behavior, priorities, or design.
  - failure_modes: A system can drift to low performance when bad results quietly reset the standard instead of triggering correction.
  - premortem_questions: What core standards have we failed to meet in the past, and how are we ensuring those same metrics remain absolute this quarter?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `input-vs-output-goals`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane3_frame_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane3_frame_route: The plan mixes lagging output goals with controllable inputs, so the team may count activity as value. Evidence: "setting goals"
- Graph-only recall material:
  - select_when: The desired result is clear, but the team still cannot translate it into repeatable behaviors, habits, and checkpoints.
  - danger_when: Visible effort is being rewarded regardless of whether the activity produces value.
  - failure_modes: Teams can keep hitting activity targets long after it is obvious that the outcome is not moving.
  - premortem_questions: Which of our current input metrics would still look good even if the real outcome kept deteriorating?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `iteration`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane2_companion_chunk`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane2_companion_chunk: Weekly iteration needs a hypothesis, feedback signal, adjustment rule, and stop/change threshold, not an endless loop of local polishing. Evidence: "iterating weekly"
- Graph-only recall material:
  - select_when: The first version is unlikely to be correct, so the cheapest path to quality is repeated prototype-test-learn cycles.
  - danger_when: The team is iterating without stop rules, success thresholds, or a decision about what evidence is strong enough to commit.
  - failure_modes: Iteration can become endless refinement when there are no stop rules or commitment thresholds.
  - premortem_questions: What's the one-day answer?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `lean-startup-methodology`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane4_gap_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane4_gap_route: The first customer feedback cycle should reduce uncertainty with a real learning metric and a pivot/persevere threshold, not vanity validation. Evidence: "first customer feedback cycle"
- Graph-only recall material:
  - select_when: A product or market hypothesis is still fragile enough that learning speed matters more than polished completeness.
  - danger_when: Weak usage blips or vanity metrics are being mislabeled as validated learning.
  - failure_modes: Jumping to conclusions can turn speed into the Othello fault where the team moves fast on the wrong framing.
  - premortem_questions: What is the one-day answer?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `algorithmic-thinking`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane2_detected_model`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane2_detected_model: The rescue plan needs an explicit repeatable procedure with inputs, ordered steps, outputs, and failure handling before it can be handed off.
- Graph-only recall material:
  - select_when: The task can be decomposed into repeatable steps with clear handoffs, inputs, and output quality checks.
  - danger_when: Novelty, ambiguity, or human emotion is doing most of the causal work and a rigid procedure is being mistaken for actual understanding.
  - failure_modes: Rigid procedure can fail when novelty or ambiguity is doing most of the causal work and the team mistakes repeatability for understanding.
  - premortem_questions: Which edge case or exception would break this procedure even if the happy path looks clean?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `devops-and-continuous-integration`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane2_companion_chunk`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane2_companion_chunk: The advice mentions improving CI, but the packet must protect reliability and rollback instead of optimizing local delivery speed alone. Evidence: "improving CI"
- Graph-only recall material:
  - select_when: Delivery speed and reliability have to coexist, and the bottleneck is integration friction rather than lack of ideas.
  - danger_when: Pipeline optimization is being treated as an abstract slogan without specific failure paths, rollback realities, or operator constraints.
  - failure_modes: Maslow's-hammer style framework use can optimize the wrong delivery problem because the team mistakes a familiar pipeline story for the real system.
  - premortem_questions: What would you have to believe?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `goal-setting`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane1_tendency_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane1_tendency_route: The plan asks for goals, but goals need purpose, metric, time boundary, progress check, and conflict with other objectives. Evidence: "setting goals"
- Graph-only recall material:
  - select_when: Effort is scattered and the team needs one explicit outcome to align trade-offs, sequencing, and measurement.
  - danger_when: The chosen goal is organizing action but is not being revisited often enough to reflect changed evidence, constraints, or strategic reality.
  - failure_modes: Abstract mission language can sound accurate while remaining useless for frontline decisions and execution.
  - premortem_questions: Is the worst case bad enough?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `habit-formation`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane3_frame_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane3_frame_route: The team wants better execution habits, but the packet should ask for cue, routine, reward, environment, friction, and repeatability.
- Graph-only recall material:
  - select_when: Execution quality depends on repeating the right small behaviors rather than on one heroic effort.
  - danger_when: The environment has changed enough that yesterday's automatic behavior is now solving the wrong problem.
  - failure_modes: Automatic behavior can keep solving yesterday's problem when the environment has changed.
  - premortem_questions: What cue, feeling, or belief is firing right before the unwanted behavior starts?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

## Suppressed Candidates

- `iteration` (duplicate_model_id; graph_only_runtime_card)

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
