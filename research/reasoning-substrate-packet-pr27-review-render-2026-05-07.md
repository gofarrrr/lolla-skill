# Reasoning Substrate Packet Review

- Packet: `pr27-mixed-packet-review`
- Version: `reasoning_substrate_packet.v1`
- Status: `draft_review_only`
- Runtime policy: `runtime_dormant`
- Source artifacts: `data/knowledge_graph.json`, `data/compiled/model_affordances/affordances_v4.json`, `data/model_sources/manifest.json`

## Review Boundary

- Review-only handoff material.
- Compare candidate shelf usefulness; do not answer the user case.
- Do not choose user-visible output or final wording.
- Deterministic code labels, caps, references, and reports; the LLM/reviewer reasons.

## Packet Counts

| Measure | Count |
| --- | ---: |
| Candidate cards | 7 |
| Reviewed cards | 3 |
| Graph-only cards | 4 |
| Missing reviewed records | 4 |
| Absence-only cards | 0 |
| Source-too-thin cards | 0 |
| Weak/conflicting cards | 0 |

## Candidate Cards

### `opportunity-cost`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane4_gap_route`, `reviewer_note`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane4_gap_route: The advice commits the same budget and launch window without naming the displaced alternative.
- Reviewed handoff signals:
  - affordance_ids: opportunity-cost.displaced-alternative-commitment-gate
  - use_when: A roadmap addition, renewal, sprint, vendor, project, or channel looks cheap because the explicit spend is small while the same people, budget, launch window, or attention are needed elsewhere.
  - case_evidence_needed: The decision under approval and the scarce resource it consumes: people, budget, calendar time, launch window, leadership attention, trust, or optionality.
  - do_not_use_when: The real alternatives, constraints, or objective function are not framed well enough for comparison without false precision.
  - misuse_guards: Do not count unrealistic alternatives that the team cannot actually fund, execute, or own.
  - source_evidence: opportunity-cost.displaced-alternative-commitment-gate: "The fundamental essence of this model is the value of the best alternative opportunity you didn't choose"
  - treatment_requirements: name-real-next-best-alternative: Require the answer to name the best real alternative displaced by the current yes, not a vague list of possibilities or a decorative comparison set.
  - absence_record: generic-alternative-comparison-affordance (duplicate_of_existing_field)

### `falsifiability`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane2_detected_model`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane2_detected_model: The assistant treats the rollout thesis as plausible without naming what evidence would reverse it. Evidence: "move quickly"
- Reviewed handoff signals:
  - affordance_ids: falsifiability.disconfirming-reversal-gate
  - use_when: A recommendation, hypothesis, plan, or strategic thesis is strong enough to shape commitment but has not named what would prove it wrong.
  - case_evidence_needed: The live hypothesis, recommendation, assumption, or theory that could be wrong.
  - do_not_use_when: The work is still so vague that a hypothesis would be decorative rather than testable.
  - misuse_guards: Do not use falsifiability language without naming an actual disconfirming test, threshold, or observation.
  - source_evidence: falsifiability.disconfirming-reversal-gate: "The fundamental essence of Falsifiability is the principle that **a theory or hypothesis must be capable of being proven false**."
  - treatment_requirements: state-reversal-condition-before-commitment: Require the answer to state the concrete observation, threshold, or fact that would cause the thesis or recommendation to be abandoned before commitment proceeds.
  - absence_record: generic-skepticism-affordance (not_supported_by_source)

### `probabilistic-thinking`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane3_frame_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane3_frame_route: The user frame collapses uncertain renewal and launch outcomes into a go/no-go decision. Evidence: "we probably just need to decide now"
- Reviewed handoff signals:
  - affordance_ids: probabilistic-thinking.range-and-sensitivity-decision-gate
  - use_when: The decision is more-likely-or-less-likely rather than yes-or-no, and binary framing would hide a meaningful uncertainty range.
  - case_evidence_needed: The decision, bet, forecast, or recommendation currently being framed as certain or binary.
  - do_not_use_when: Probability language is postponing a commitment after the key economics, downside, and action threshold are already clear.
  - misuse_guards: Do not present exact-looking numbers with more precision than the evidence supports.
  - source_evidence: probabilistic-thinking.range-and-sensitivity-decision-gate: "Probabilistic Thinking (PT) is a mental model centered on **estimating the parameters of uncertainty**."
  - treatment_requirements: express-decision-relevant-range: Require the answer to state an honest probability or confidence range only when the range will change the commitment, not as decorative precision.
  - absence_record: exact-point-estimate-affordance (not_supported_by_source)

### `step-back`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane3_frame_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane3_frame_route: The case is moving from urgency into commitment before restating the governing purpose. Evidence: "we are running out of time"
- Graph-only recall material:
  - select_when: Immediate immersion is obscuring the structure of the problem and a deliberate pause would likely improve the next move.
  - danger_when: The pause is becoming a hiding place for avoiding commitment, trade-offs, or concrete next steps.
  - failure_modes: Reflection can become a hiding place that postpones commitment, trade-offs, or the next concrete move.
  - premortem_questions: What's the one-day answer?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `constraints`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane4_gap_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane4_gap_route: The plan does not state which scope, budget, or launch constraints govern the trade-off.
- Graph-only recall material:
  - select_when: A team is losing clarity because too many goals, variables, or stakeholders are competing for attention at once.
  - danger_when: Old constraints are remaining unquestioned after the economics, technology, or stakeholder environment has changed.
  - failure_modes: Stale constraints can quietly mislead action when the environment changed but the boundary never did.
  - premortem_questions: How does what you’re doing solve the problem?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `chain-of-verification`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane2_companion_chunk`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane2_companion_chunk: The assistant defers verification until after action even though several premises must hold in sequence. Evidence: "track risks after launch"
- Graph-only recall material:
  - select_when: A case depends on several premises in sequence and one weak link could collapse the whole conclusion.
  - danger_when: Verification is becoming theater through extra checks and sign-offs that do not materially improve the truth of the chain.
  - failure_modes: A flawed foundation can survive upward because teams fail to challenge weak assumptions at the earliest link.
  - premortem_questions: Which links are make-or-break enough that the whole conclusion collapses if they fail?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `confirmation-bias`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane1_tendency_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane1_tendency_route: The transaction suggests convergence on the preferred renewal answer before disconfirming evidence is named.
- Graph-only recall material:
  - select_when: A team is converging on a favored answer before the evidence has been fully tested.
  - danger_when: The review is already structured around explicit falsification, equal treatment of confirming and disconfirming evidence, and adversarial challenge.
  - failure_modes: Bias blind spot amplification lets the team audit everyone else's evidence standards while sparing its own.
  - premortem_questions: What would we have to believe for this conclusion to be true, and which of those assumptions is weakest?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

## Suppressed Candidates

- `opportunity-cost` (duplicate_model_id; reviewed_affordance_available)

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
