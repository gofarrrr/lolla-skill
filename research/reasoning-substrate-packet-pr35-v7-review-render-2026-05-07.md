# Reasoning Substrate Packet Review

- Packet: `pr35-v7-communication-competition-packet-review`
- Version: `reasoning_substrate_packet.v1`
- Status: `draft_review_only`
- Runtime policy: `runtime_dormant`
- Source artifacts: `data/knowledge_graph.json`, `data/compiled/model_affordances/affordances_v7.json`, `data/model_sources/manifest.json`

## Review Boundary

- Review-only handoff material.
- Compare candidate shelf usefulness; do not answer the user case.
- Do not choose user-visible output or final wording.
- Deterministic code labels, caps, references, and reports; the LLM/reviewer reasons.

## Packet Counts

| Measure | Count |
| --- | ---: |
| Candidate cards | 9 |
| Reviewed cards | 9 |
| Graph-only cards | 0 |
| Missing reviewed records | 0 |
| Absence-only cards | 0 |
| Source-too-thin cards | 0 |
| Weak/conflicting cards | 0 |

## Candidate Cards

### `game-theory-payoffs`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane2_companion_chunk`, `reviewer_note`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane2_companion_chunk: The assistant assumes partner and competitor responses will stay stable after the team escalates.
- Reviewed handoff signals:
  - affordance_ids: game-theory-payoffs.counterparty-response-payoff-map
  - use_when: A rival, partner, regulator, buyer, seller, or negotiating counterparty can change the value of the proposed action.
  - case_evidence_needed: The players or counterparties involved.
  - do_not_use_when: The actors are not actually playing the same game because reputation, ideology, politics, or internal incentives dominate.
  - misuse_guards: Do not assume both sides are optimizing the same payoff model.
  - source_evidence: game-theory-payoffs.counterparty-response-payoff-map: "identifying the players, the actions available to them, the information they possess, and the resultant payoff for each potential action"
  - treatment_requirements: name-players-moves-and-decisive-payoffs: Require the answer to map the relevant players, likely moves, and payoff drivers, while pruning branches that do not materially change the decision.
  - absence_record: same-game-assumption-affordance (not_supported_by_source)

### `nash-equilibrium`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane4_gap_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane4_gap_route: The plan assumes unilateral clarification will shift behavior without checking whether each party's current move is already a stable best response.
- Reviewed handoff signals:
  - affordance_ids: nash-equilibrium.stable-best-response-map
  - use_when: A decision only makes sense relative to the likely stable responses of other players, not in isolation.
  - case_evidence_needed: The players whose responses matter.
  - do_not_use_when: The equilibrium is computationally or behaviorally unreachable for the actual actors.
  - misuse_guards: Do not assume a stable outcome is a good outcome.
  - source_evidence: nash-equilibrium.stable-best-response-map: "no player can increase their payoff by unilaterally changing their action"
  - treatment_requirements: separate-stable-from-good-and-reachable: Require the answer to distinguish whether the proposed equilibrium is stable, reachable, and desirable as three separate claims.
  - absence_record: stable-outcome-equals-good-affordance (not_supported_by_source)

### `prisoners-dilemma`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane3_frame_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane3_frame_route: The partner conversation is framed as alignment, but both sides may have incentives to defect or withhold. Evidence: "they say they are aligned but keep delaying"
- Reviewed handoff signals:
  - affordance_ids: prisoners-dilemma.defection-incentive-reframe-test
  - use_when: Each actor has a credible incentive to defect even though everyone would benefit from stable cooperation.
  - case_evidence_needed: The actors and choices available to each.
  - do_not_use_when: The situation is a coordination or process repair problem rather than a betrayal dynamic.
  - misuse_guards: Do not treat every coordination problem as betrayal.
  - source_evidence: prisoners-dilemma.defection-incentive-reframe-test: "conflict between individual rationality and collective optimality"
  - treatment_requirements: redesign-game-before-blaming-actors: Require the answer to test whether bad collective behavior is produced by flawed rules before assigning bad intent to individual actors.
  - absence_record: every-coordination-problem-is-betrayal (not_supported_by_source)

### `cross-cultural-communication-frameworks`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane1_tendency_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane1_tendency_route: The feedback and partner messages must carry across function, status, and regional frames.
- Reviewed handoff signals:
  - affordance_ids: cross-cultural-communication-frameworks.frame-translation-action-check
  - use_when: The same message must survive translation across cultures, functions, or status differences without losing the intended action.
  - case_evidence_needed: The message, decision, or action that must be understood.
  - do_not_use_when: Cultural models are being used as stereotype shortcuts instead of prompts to investigate the actual audience.
  - misuse_guards: Do not use cultural models as stereotype shortcuts.
  - source_evidence: cross-cultural-communication-frameworks.frame-translation-action-check: "to bridge the inherent disconnect between the sender's intricate understanding and the receiver's often simplified, emotionally filtered processing of information"
  - treatment_requirements: translate-frame-without-hiding-action: Require the answer to adapt message framing for the actual audience while preserving the core action and hard trade-offs.
  - absence_record: stereotype-shortcut-communication (not_supported_by_source)

### `active-listening`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane1_tendency_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane1_tendency_route: The team plans to give feedback before proving it has heard the partner's actual constraint or disagreement. Evidence: "clarify expectations"
- Reviewed handoff signals:
  - affordance_ids: active-listening.hidden-disagreement-diagnostic-loop
  - use_when: The surface objection may be hiding fear, misaligned incentives, identity threat, unstated constraints, or different success criteria.
  - case_evidence_needed: The visible disagreement, objection, or emotional signal.
  - do_not_use_when: Listening language is being used performatively to manage optics or extract information after the answer is already decided.
  - misuse_guards: Do not use listening language performatively when the answer is already decided.
  - source_evidence: active-listening.hidden-disagreement-diagnostic-loop: "comprehending your conversation partner 100 percent clearly and certainly"
  - treatment_requirements: diagnose-before-rebuttal-or-advice: Require the answer to ask how the other side thinks, reflect the content and emotion, and confirm understanding before moving to solution or rebuttal.
  - absence_record: performative-listening-affordance (not_supported_by_source)

### `constructive-feedback-models`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane4_gap_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane4_gap_route: The manager feedback plan lacks a specific behavior, standard, and correction path.
- Reviewed handoff signals:
  - affordance_ids: constructive-feedback-models.specific-standard-correction
  - use_when: Performance, learning, or trust depends on giving people information they can act on rather than vague reassurance.
  - case_evidence_needed: The action, output, or behavior being evaluated.
  - do_not_use_when: Feedback is technically accurate but delivered without timing, context, or respect.
  - misuse_guards: Do not use rank or authority as a substitute for observation quality.
  - source_evidence: constructive-feedback-models.specific-standard-correction: "structured process for evaluating an action, output, or behavior against an objective standard"
  - treatment_requirements: tie-feedback-to-standard-and-adjustment: Require the answer to name the observed deviation, the standard it missed, the impact, and the actionable adjustment without turning correction into rank pressure or vague advice.
  - absence_record: rank-backed-feedback-affordance (not_supported_by_source)

### `feedback-models-sbi`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane2_detected_model`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane2_detected_model: The assistant recommends feedback without separating situation, behavior, impact, and invitation. Evidence: "give feedback"
- Reviewed handoff signals:
  - affordance_ids: feedback-models-sbi.situation-impact-invitation-structure
  - use_when: A feedback conversation needs to stay tied to specific observable behavior rather than personality labels or vague frustration.
  - case_evidence_needed: The concrete situation or incident.
  - do_not_use_when: The model is being used as a script to deliver judgment while skipping curiosity, listening, or the receiver's constraints.
  - misuse_guards: Do not use the structure as a script for judgment while skipping curiosity.
  - source_evidence: feedback-models-sbi.situation-impact-invitation-structure: "clear link between a specific action and its observed consequence"
  - treatment_requirements: anchor-feedback-in-observable-incident: Require the answer to keep feedback tied to concrete observation, impact, invitation, and implications while preserving curiosity about the receiver's constraints.
  - absence_record: scripted-judgment-feedback (not_supported_by_source)

### `analogies-and-metaphors`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane3_frame_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane3_frame_route: The team is tempted to copy the competitor launch as an analogy without testing structural fit. Evidence: "their launch playbook worked"
- Reviewed handoff signals:
  - affordance_ids: analogies-and-metaphors.structural-fit-transfer-test
  - use_when: The audience lacks a usable schema for a new concept but has adjacent experience that can carry the explanation.
  - case_evidence_needed: The target concept or decision that needs explanation.
  - do_not_use_when: The analogy is based on superficial similarity rather than shared mechanism.
  - misuse_guards: Do not let a vivid analogy become proof.
  - source_evidence: analogies-and-metaphors.structural-fit-transfer-test: "**bridges**, connecting what an audience already understands to the new ideas"
  - treatment_requirements: test-reference-class-fit-before-transfer: Require the answer to line up assumptions in the source analogy against the target case and name at least one limitation before relying on the comparison.
  - absence_record: analogy-as-proof-affordance (not_supported_by_source)

### `natural-selection-analogy`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane3_frame_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane3_frame_route: The competitive story treats survival of a pattern as proof it is optimal rather than testing variation, selection, and retention conditions.
- Reviewed handoff signals:
  - affordance_ids: natural-selection-analogy.variation-selection-retention-loop
  - use_when: The team can generate multiple credible variants and let real feedback, market response, or operational evidence eliminate weak options.
  - case_evidence_needed: The variants or options to test.
  - do_not_use_when: Leaders use emergence language to excuse weak goals, absent decision rights, or undefined fitness criteria.
  - misuse_guards: Do not use emergence as an excuse for weak goals or absent decision rights.
  - source_evidence: natural-selection-analogy.variation-selection-retention-loop: "variation, selection, and retention"
  - treatment_requirements: define-fitness-before-letting-feedback-select: Require the answer to define variants, fitness criteria, feedback channels, and retention rules before invoking adaptation or emergence.
  - absence_record: survival-proves-optimal-design (not_supported_by_source)

## Suppressed Candidates

- `game-theory-payoffs` (duplicate_model_id; reviewed_affordance_available)

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
