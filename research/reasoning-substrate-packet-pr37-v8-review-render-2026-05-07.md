# Reasoning Substrate Packet Review

- Packet: `pr37-v8-trust-negotiation-packet-review`
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
| Candidate cards | 10 |
| Reviewed cards | 10 |
| Graph-only cards | 0 |
| Missing reviewed records | 0 |
| Absence-only cards | 0 |
| Source-too-thin cards | 0 |
| Weak/conflicting cards | 0 |

## Candidate Cards

### `non-violent-communication`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane1_tendency_route`, `reviewer_note`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane1_tendency_route: The repair note risks mixing accusation, need, and request instead of making the relationship concern observable and actionable. Evidence: "be transparent and empathize"
- Reviewed handoff signals:
  - affordance_ids: non-violent-communication.needs-observations-request-clarifier
  - use_when: A disagreement is entangled with defensiveness, face-saving, mistrust, or fear of blame.
  - case_evidence_needed: The factual observation at issue.
  - do_not_use_when: The model would soften every edge of disagreement until boundaries, trade-offs, or accountability disappear.
  - misuse_guards: Do not turn non-violent wording into conflict avoidance.
  - source_evidence: non-violent-communication.needs-observations-request-clarifier: "stating directly what you want and how you see things without putting down or infringing on the rights of others"
  - treatment_requirements: separate-observation-need-and-request: Require the answer to state the observable issue, name the relevant need or relationship concern, and convert it into a concrete request or next action without accusation.
  - absence_record: conflict-avoidance-affordance (not_supported_by_source)

### `emotional-intelligence`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane1_tendency_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane1_tendency_route: The plan treats emotional landing as style rather than evidence about adoption, fairness, and trust.
- Reviewed handoff signals:
  - affordance_ids: emotional-intelligence.emotion-evidence-landing-check
  - use_when: The technical answer is not enough because trust, morale, conflict, or perceived fairness will shape whether a decision lands.
  - case_evidence_needed: The decision, change, conflict, or message that must land socially.
  - do_not_use_when: Empathy is being used as a substitute for standards, evidence, or hard conversations.
  - misuse_guards: Do not equate emotional intelligence with niceness.
  - source_evidence: emotional-intelligence.emotion-evidence-landing-check: "manage feelings so they are expressed **appropriately and effectively**"
  - treatment_requirements: validate-emotion-without-dropping-standards: Require the answer to name the emotional signal and likely cause, test that interpretation, and keep evidence and accountability requirements visible.
  - absence_record: empathy-substitutes-for-standards (not_supported_by_source)

### `understanding-motivations`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane4_gap_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane4_gap_route: The assistant infers resistance but does not test hidden drivers against observable behavior or disconfirming evidence. Evidence: "they may need more reassurance"
- Reviewed handoff signals:
  - affordance_ids: understanding-motivations.hidden-driver-hypothesis-test
  - use_when: Visible behavior appears irrational, inconsistent, or self-defeating until status, identity, fear, reward, or purpose is surfaced.
  - case_evidence_needed: The visible behavior or resistance that needs explanation.
  - do_not_use_when: The answer would over-psychologize a simple constraint, capability, or resource problem.
  - misuse_guards: Do not over-psychologize simple constraint or capability problems.
  - source_evidence: understanding-motivations.hidden-driver-hypothesis-test: "visible behavior looks irrational, inconsistent, or self-defeating until the real status, identity, fear, or reward structure is surfaced"
  - treatment_requirements: test-hidden-driver-before-intervention: Require the answer to state a motivational hypothesis, identify what evidence would support or disconfirm it, and avoid treating stated motives as final truth.
  - absence_record: over-psychologize-simple-constraints (not_supported_by_source)

### `boundaries`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane3_frame_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane3_frame_route: The internal reset needs a line between ownership, influence, and excluded work instead of a vague expectation reset. Evidence: "reset internal ownership boundaries"
- Reviewed handoff signals:
  - affordance_ids: boundaries.scope-ownership-decision-rights-filter
  - use_when: Scope, ownership, decision rights, or relevance criteria are fuzzy enough that effort is diffusing.
  - case_evidence_needed: The current scope or ownership ambiguity.
  - do_not_use_when: A boundary is being drawn mainly to avoid hard conversations, accountability, or inconvenient evidence.
  - misuse_guards: Do not draw scope lines to avoid accountability or evidence.
  - source_evidence: boundaries.scope-ownership-decision-rights-filter: "scope, ownership, decision rights, or relevance criteria are fuzzy enough that energy is being wasted in every direction at once"
  - treatment_requirements: define-inside-outside-and-influence: Require the answer to define the boundary, name what it protects, and test whether excluded work is truly irrelevant or merely uncomfortable.
  - absence_record: comfort-protection-boundary (not_supported_by_source)

### `authenticity`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane3_frame_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane3_frame_route: The founder wants candor that rebuilds trust, but candor must stay congruent with evidence and accountability.
- Reviewed handoff signals:
  - affordance_ids: authenticity.congruence-candor-substance-check
  - use_when: Trust depends on congruence rather than polish.
  - case_evidence_needed: The trust or credibility gap.
  - do_not_use_when: Authentic style is being used without factual or procedural substance.
  - misuse_guards: Do not confuse authentic style with reliable substance.
  - source_evidence: authenticity.congruence-candor-substance-check: "putting into words what one is genuinely experiencing during the work"
  - treatment_requirements: name-real-experience-and-ground-it: Require the answer to name the real experience or constraint that should be surfaced, then tie it to evidence and accountable action rather than mere self-expression.
  - absence_record: authentic-style-without-substance (not_supported_by_source)

### `hanlons-razor`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane4_gap_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane4_gap_route: The partner delay may be malice, overload, incentives, or coordination failure; the plan should not jump to intent attribution. Evidence: "they keep stalling"
- Reviewed handoff signals:
  - affordance_ids: hanlons-razor.non-malice-diagnostic-delay
  - use_when: A failure, delay, or conflict can plausibly be explained by coordination breakdown, poor incentives, missing training, or overloaded systems.
  - case_evidence_needed: The negative outcome or perceived slight.
  - do_not_use_when: Repeat harm, obvious deception, or incentives practically reward bad-faith behavior.
  - misuse_guards: Do not use Hanlon's Razor to excuse repeated harm.
  - source_evidence: hanlons-razor.non-malice-diagnostic-delay: "we should not attribute to malice that which is more easily explained by stupidity"
  - treatment_requirements: test-neglect-before-malice: Require the answer to state at least one non-malicious explanation, identify the evidence that would distinguish it from malice, and preserve an escalation path if bad faith remains plausible.
  - absence_record: repeat-harm-excuse (not_supported_by_source)

### `reciprocity-principle`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane2_detected_model`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane2_detected_model: The concession is meant to rebuild trust before an ask, but the packet needs to distinguish real value from obligation pressure. Evidence: "offer a concession"
- Reviewed handoff signals:
  - affordance_ids: reciprocity-principle.costly-value-trust-test
  - use_when: Trust or relationship depth must be built before a difficult ask, negotiation, or sale can be evaluated seriously.
  - case_evidence_needed: The ask, negotiation, or sale that needs trust before evaluation.
  - do_not_use_when: Reciprocity pressure creates obligation without informed evaluation.
  - misuse_guards: Do not use reciprocity to manufacture mindless compliance.
  - source_evidence: reciprocity-principle.costly-value-trust-test: "trust or relationship depth must be built before a difficult ask, negotiation, or sale can even be evaluated seriously"
  - treatment_requirements: distinguish-real-value-from-obligation-pressure: Require the answer to name the value offered, test whether it is costly and relevant, and protect the recipient's ability to evaluate the actual decision.
  - absence_record: obligation-without-evaluation (not_supported_by_source)

### `persuasion-principles`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane2_companion_chunk`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane2_companion_chunk: The adoption plan may need better framing, but only if persuasion preserves evidence, autonomy, and substance. Evidence: "make the case more compelling"
- Reviewed handoff signals:
  - affordance_ids: persuasion-principles.substance-preserving-adoption-design
  - use_when: The insight is already sound but attention, belief, or action is blocked by indifference, overload, or weak framing.
  - case_evidence_needed: The sound underlying insight or recommendation.
  - do_not_use_when: Persuasive technique would accelerate acceptance of a weak answer.
  - misuse_guards: Do not use persuasion to speed acceptance of a weak answer.
  - source_evidence: persuasion-principles.substance-preserving-adoption-design: "the insight is already sound but attention, belief, or action is still blocked by indifference, overload, or weak framing"
  - treatment_requirements: package-without-bypassing-judgment: Require the answer to simplify and frame the message for adoption while explicitly preserving the evidence standard and the audience's ability to evaluate the claim.
  - absence_record: better-packaging-for-weak-answer (not_supported_by_source)

### `international-negotiation-and-diplomacy-models`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane4_gap_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane4_gap_route: The rollout delay involves substance, signaling, stakeholders, concessions, and sequencing across more than one party.
- Reviewed handoff signals:
  - affordance_ids: international-negotiation-and-diplomacy-models.substance-signaling-settlement-map
  - use_when: Goals are interdependent and partially conflicting.
  - case_evidence_needed: The actors and their partially conflicting goals.
  - do_not_use_when: Tactical cleverness, point-scoring, posture, or symbolic wins are replacing strategic alignment.
  - misuse_guards: Do not optimize for symbolic wins that weaken the settlement.
  - source_evidence: international-negotiation-and-diplomacy-models.substance-signaling-settlement-map: "goals are interdependent and partially conflicting"
  - treatment_requirements: map-substance-signal-and-durable-alignment: Require the answer to separate the substantive deal problem from the signaling and relationship problem, then test whether proposed moves help the durable settlement rather than just winning a point.
  - absence_record: tactical-point-scoring-affordance (not_supported_by_source)

### `signaling`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane3_frame_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane3_frame_route: The public commitment request needs costly proof of intent rather than a cheap symbolic promise. Evidence: "ask for a public commitment"
- Reviewed handoff signals:
  - affordance_ids: signaling.costly-proof-of-intent-test
  - use_when: Quality, intent, or reliability cannot be directly observed and must be inferred from behavior, framing, and follow-through.
  - case_evidence_needed: The ambiguous quality, intent, reliability, or commitment claim.
  - do_not_use_when: Cheap symbolic signals are being allowed to substitute for real capability, accountability, or truth-aligned behavior.
  - misuse_guards: Do not treat polished surface signals as proof of capability.
  - source_evidence: signaling.costly-proof-of-intent-test: "quality, intent, or reliability cannot be directly observed and the receiver must infer them from behavior, framing, and follow-through"
  - treatment_requirements: ask-for-costly-unstaged-proof: Require the answer to name the current signal, judge whether it is cheap or costly, and specify the next proof of commitment or capability to demand.
  - absence_record: cheap-symbolic-signal-as-proof (not_supported_by_source)

## Suppressed Candidates

- `signaling` (duplicate_model_id; reviewed_affordance_available)

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
