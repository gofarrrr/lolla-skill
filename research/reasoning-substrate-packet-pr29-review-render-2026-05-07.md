# Reasoning Substrate Packet Review

- Packet: `pr29-v5-mixed-packet-depth-review`
- Version: `reasoning_substrate_packet.v1`
- Status: `draft_review_only`
- Runtime policy: `runtime_dormant`
- Source artifacts: `data/knowledge_graph.json`, `data/compiled/model_affordances/affordances_v5.json`, `data/model_sources/manifest.json`

## Review Boundary

- Review-only handoff material.
- Compare candidate shelf usefulness; do not answer the user case.
- Do not choose user-visible output or final wording.
- Deterministic code labels, caps, references, and reports; the LLM/reviewer reasons.

## Packet Counts

| Measure | Count |
| --- | ---: |
| Candidate cards | 7 |
| Reviewed cards | 7 |
| Graph-only cards | 0 |
| Missing reviewed records | 0 |
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

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane3_frame_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane3_frame_route: The case is moving from urgency into commitment before restating the governing purpose. Evidence: "we are running out of time"
- Reviewed handoff signals:
  - affordance_ids: step-back.reorientation-before-execution-gate
  - use_when: The team is too close to the details to see what actually matters.
  - case_evidence_needed: The immediate action, analysis, or detail work the team is immersed in.
  - do_not_use_when: Reflection is being used to postpone commitment, avoid trade-offs, or keep options abstract.
  - misuse_guards: Do not use step-back as a socially acceptable way to avoid commitment.
  - source_evidence: step-back.reorientation-before-execution-gate: "necessary pause"
  - treatment_requirements: find-governing-structure-before-action: Require the answer to step back from detail immersion and name the governing structure, core point, or problem-owner frame before recommending execution.
  - absence_record: indefinite-reflection-affordance (not_supported_by_source)

### `constraints`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane4_gap_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane4_gap_route: The plan does not state which scope, budget, or launch constraints govern the trade-off.
- Reviewed handoff signals:
  - affordance_ids: constraints.scope-boundary-decision-filter
  - use_when: Too many goals, variables, stakeholders, or possible moves are competing for attention and the team is losing clarity.
  - case_evidence_needed: The goal, scope, decision, or problem surface being constrained.
  - do_not_use_when: The constraint is inherited, outdated, or untested after the economics, technology, or stakeholder environment has changed.
  - misuse_guards: Do not treat old constraints as permanent without checking whether the environment changed.
  - source_evidence: constraints.scope-boundary-decision-filter: "boundary, rule, or limitation that defines the functional scope, responsibilities, or acceptable parameters of a system, problem, or endeavor"
  - treatment_requirements: name-boundaries-and-exclusions: Require the answer to state the scope boundary, success constraint, acceptable trade-off, and deliberate exclusion before recommending action.
  - absence_record: permanent-rule-compliance-affordance (not_supported_by_source)

### `chain-of-verification`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane2_companion_chunk`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane2_companion_chunk: The assistant defers verification until after action even though several premises must hold in sequence. Evidence: "track risks after launch"
- Reviewed handoff signals:
  - affordance_ids: chain-of-verification.make-or-break-premise-audit
  - use_when: A recommendation, forecast, rollout, or diagnosis depends on several linked premises that must all hold for the conclusion to survive.
  - case_evidence_needed: The conclusion or commitment under review and the linked premises it depends on.
  - do_not_use_when: The situation needs a reversible probe or flexible engagement more than exhaustive step-by-step verification.
  - misuse_guards: Do not use chain-of-verification to justify endless sign-offs when a bounded reversible test would create better learning.
  - source_evidence: chain-of-verification.make-or-break-premise-audit: "evidence to back up each link in that chain"
  - treatment_requirements: map-critical-links-before-confidence: Require the answer to name the conclusion, its linked premises, and the premise that would collapse the conclusion before expressing confidence.
  - absence_record: exhaustive-signoff-verification-affordance (not_supported_by_source)

### `confirmation-bias`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane1_tendency_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane1_tendency_route: The transaction suggests convergence on the preferred renewal answer before disconfirming evidence is named.
- Reviewed handoff signals:
  - affordance_ids: confirmation-bias.disconfirming-evidence-equality-check
  - use_when: A team is converging quickly on a favored recommendation before the evidence is fully in.
  - case_evidence_needed: The favored conclusion, sponsor-backed recommendation, or preferred thesis under review.
  - do_not_use_when: The answer would merely accuse others of bias without changing the evidence standard or decision test.
  - misuse_guards: Do not use confirmation-bias language to accuse other people while leaving your own evidence standard unchanged.
  - source_evidence: confirmation-bias.disconfirming-evidence-equality-check: "tendency to continuously filter for and focus on incoming data points that confirm our current beliefs, attitudes, and opinions"
  - treatment_requirements: surface-disconfirming-case-with-equal-weight: Require the answer to bring disconfirming observations, objections, failed cases, and quiet losses into the same comparison set as visible confirming evidence.
  - absence_record: accuse-others-of-confirmation-bias-affordance (not_supported_by_source)

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
