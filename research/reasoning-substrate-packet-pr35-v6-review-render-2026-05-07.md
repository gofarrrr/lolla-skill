# Reasoning Substrate Packet Review

- Packet: `pr35-v6-communication-competition-packet-review`
- Version: `reasoning_substrate_packet.v1`
- Status: `draft_review_only`
- Runtime policy: `runtime_dormant`
- Source artifacts: `data/knowledge_graph.json`, `data/compiled/model_affordances/affordances_v6.json`, `data/model_sources/manifest.json`

## Review Boundary

- Review-only handoff material.
- Compare candidate shelf usefulness; do not answer the user case.
- Do not choose user-visible output or final wording.
- Deterministic code labels, caps, references, and reports; the LLM/reviewer reasons.

## Packet Counts

| Measure | Count |
| --- | ---: |
| Candidate cards | 9 |
| Reviewed cards | 2 |
| Graph-only cards | 7 |
| Missing reviewed records | 7 |
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

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane4_gap_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane4_gap_route: The plan assumes unilateral clarification will shift behavior without checking whether each party's current move is already a stable best response.
- Graph-only recall material:
  - select_when: Your best move depends on how other players are likely to respond rather than on your action in isolation.
  - danger_when: The equilibrium is computationally or behaviorally unreachable because the actors cannot actually discover or sustain it.
  - failure_modes: A theoretically stable equilibrium may be useless if real actors cannot compute or sustain it.
  - premortem_questions: Can the actual players find and sustain this equilibrium, or only the analyst?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `prisoners-dilemma`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane3_frame_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane3_frame_route: The partner conversation is framed as alignment, but both sides may have incentives to defect or withhold. Evidence: "they say they are aligned but keep delaying"
- Graph-only recall material:
  - select_when: Individually sensible moves are producing a collectively worse outcome because each actor has a credible incentive to defect.
  - danger_when: The behavior is better explained by simple process repair, shared identity, or non-adversarial coordination than by defection logic.
  - failure_modes: Teams can treat a bad payoff structure as if better individual behavior alone will rescue the outcome.
  - premortem_questions: What frame other than a competitive one could govern this interaction?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

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

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane1_tendency_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane1_tendency_route: The team plans to give feedback before proving it has heard the partner's actual constraint or disagreement. Evidence: "clarify expectations"
- Graph-only recall material:
  - select_when: Commitment, alignment, or conflict repair depends on understanding both the factual and emotional content of what another person is saying.
  - danger_when: The conversation has already produced enough evidence for a decision or reversible experiment, and more listening would mainly postpone commitment.
  - failure_modes: A listener can collect words without understanding the reasoning chain beneath them and end up with brittle, surface-level understanding.
  - premortem_questions: What truly matters to this person that I still have not heard clearly enough to restate back to them?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `constructive-feedback-models`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane4_gap_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane4_gap_route: The manager feedback plan lacks a specific behavior, standard, and correction path.
- Graph-only recall material:
  - select_when: Performance, learning, or trust depends on giving people information they can act on rather than vague reassurance.
  - danger_when: Feedback is technically accurate but so poorly timed, context-free, or disrespectful that defensiveness will overwhelm learning.
  - failure_modes: Defensiveness can overwhelm the learning if the feedback lands as adversarial threat instead of as respectful correction.
  - premortem_questions: What would you have to believe?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `feedback-models-sbi`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane2_detected_model`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane2_detected_model: The assistant recommends feedback without separating situation, behavior, impact, and invitation. Evidence: "give feedback"
- Graph-only recall material:
  - select_when: A feedback conversation needs to stay tied to specific observable behavior rather than personality labels or vague frustration.
  - danger_when: The structure is being used as a script for delivering judgment while skipping curiosity, listening, or the receiver's real constraints.
  - failure_modes: Feedback can become a dressed-up judgment if the structure skips curiosity about the receiver's actual constraints.
  - premortem_questions: What observable behavior am I actually pointing to, and what conclusion am I only inferring?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `analogies-and-metaphors`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane3_frame_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane3_frame_route: The team is tempted to copy the competitor launch as an analogy without testing structural fit. Evidence: "their launch playbook worked"
- Graph-only recall material:
  - select_when: The audience lacks a usable schema for the concept but does have adjacent experience that can carry the explanation.
  - danger_when: The comparison is catchy but distorts the structural boundaries of the target domain.
  - failure_modes: People can fail to understand a concept not because information is missing but because they still lack a usable mental bucket for it.
  - premortem_questions: What existing schema does the audience already have that could carry this new idea?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `natural-selection-analogy`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane3_frame_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane3_frame_route: The competitive story treats survival of a pattern as proof it is optimal rather than testing variation, selection, and retention conditions.
- Graph-only recall material:
  - select_when: A solution space is better explored by generating variants, testing them, and letting evidence eliminate weak options.
  - danger_when: The language of emergence is being used to avoid setting goals, decision rights, or fitness criteria in a human system.
  - failure_modes: Teams talk about selection and emergence without defining the fitness criteria the human system should actually optimize.
  - premortem_questions: What evidence would show this situation does not actually fit the selection process we are borrowing from biology?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

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
