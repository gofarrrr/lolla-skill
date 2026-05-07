# Reasoning Substrate Packet Review

- Packet: `pr37-v7-trust-negotiation-packet-review`
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
| Candidate cards | 10 |
| Reviewed cards | 0 |
| Graph-only cards | 10 |
| Missing reviewed records | 10 |
| Absence-only cards | 0 |
| Source-too-thin cards | 0 |
| Weak/conflicting cards | 0 |

## Candidate Cards

### `non-violent-communication`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane1_tendency_route`, `reviewer_note`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane1_tendency_route: The repair note risks mixing accusation, need, and request instead of making the relationship concern observable and actionable. Evidence: "be transparent and empathize"
- Graph-only recall material:
  - select_when: Completion and synchronization matter more than winning an argument, and the team needs a clearer split between content and relationship data.
  - danger_when: The conversation is being softened so much that real boundaries, trade-offs, or accountability requests never become explicit.
  - failure_modes: Teams can soften conflict language enough to avoid argument while still failing to make the real boundary or trade-off discussable.
  - premortem_questions: Are we trying to convince each other that we are right, or are we trying to hear each perspective to figure out what is true and what to do?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `emotional-intelligence`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane1_tendency_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane1_tendency_route: The plan treats emotional landing as style rather than evidence about adoption, fairness, and trust.
- Graph-only recall material:
  - select_when: The technical answer is not enough because trust, morale, conflict, or perceived fairness will shape whether the decision lands.
  - danger_when: Empathy is being treated as a substitute for standards, evidence, or hard conversations.
  - failure_modes: Emotional intelligence can be misread as niceness, leaving hard but necessary truth unsaid.
  - premortem_questions: What emotion is present here, and what do I think is causing it?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `understanding-motivations`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane4_gap_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane4_gap_route: The assistant infers resistance but does not test hidden drivers against observable behavior or disconfirming evidence. Evidence: "they may need more reassurance"
- Graph-only recall material:
  - select_when: Observed behavior is easy to name, but the real decision quality depends on identifying the why beneath it.
  - danger_when: The team is over-psychologizing a problem that is better explained by simple constraints, incentives, or capability gaps.
  - failure_modes: Teams can treat publicly stated reasons as the whole truth even when image management, politics, or self-deception are shaping the answer.
  - premortem_questions: What would you have to believe for this motive explanation to be true?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `boundaries`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane3_frame_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane3_frame_route: The internal reset needs a line between ownership, influence, and excluded work instead of a vague expectation reset. Evidence: "reset internal ownership boundaries"
- Graph-only recall material:
  - select_when: A project, analysis, or negotiation needs explicit scope lines before effort spreads into unowned terrain.
  - danger_when: Scope lines are being drawn mainly to avoid inconvenient evidence, hard conversations, or accountability.
  - failure_modes: Boundaries fail when they are drawn to protect comfort, politics, or convenience instead of the actual purpose of the work.
  - premortem_questions: What is this work actually supposed to cover, and what is deliberately out of scope?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `authenticity`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane3_frame_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane3_frame_route: The founder wants candor that rebuilds trust, but candor must stay congruent with evidence and accountability.
- Graph-only recall material:
  - select_when: Trust depends on whether words, incentives, and behavior line up under pressure rather than on whether the presentation sounds polished.
  - danger_when: Authenticity is being used as a shield against evidence, preparation, or accountability for consequences.
  - failure_modes: A team can spend energy managing impressions instead of surfacing the truth that would actually let the work improve.
  - premortem_questions: What conclusions would unbiased others draw if they saw the exact same facts?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `hanlons-razor`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane4_gap_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane4_gap_route: The partner delay may be malice, overload, incentives, or coordination failure; the plan should not jump to intent attribution. Evidence: "they keep stalling"
- Graph-only recall material:
  - select_when: A failure, delay, or conflict could plausibly be explained by poor clarity, coordination breakdown, overload, or neglect rather than hostile intent.
  - danger_when: The principle is becoming a reflexive excuse for repeat harm, obvious deception, or incentive structures that reward bad-faith behavior.
  - failure_modes: Teams escalate conflict when they assign hostile intent before checking for simpler explanations like poor clarity, overload, or process breakdown.
  - premortem_questions: What simpler operational explanation could plausibly account for this failure before we infer hostile intent?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `reciprocity-principle`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane2_detected_model`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane2_detected_model: The concession is meant to rebuild trust before an ask, but the packet needs to distinguish real value from obligation pressure. Evidence: "offer a concession"
- Graph-only recall material:
  - select_when: Trust or relationship depth must be built before a difficult ask, negotiation, or sale can be evaluated seriously.
  - danger_when: Gifts, favors, or access are becoming a distraction from the substance, economics, or ethics of the underlying decision.
  - failure_modes: A team can mistake reciprocity pressure for genuine agreement and push people toward yes before they have judged the merits.
  - premortem_questions: If the other side accepts now, is the acceptance coming from thoughtful analysis or from the pressure to reciprocate?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `persuasion-principles`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane2_companion_chunk`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane2_companion_chunk: The adoption plan may need better framing, but only if persuasion preserves evidence, autonomy, and substance. Evidence: "make the case more compelling"
- Graph-only recall material:
  - select_when: The insight is already sound but attention, belief, or action is still blocked by indifference, overload, or weak framing.
  - danger_when: Persuasive technique is being used to accelerate acceptance of a weak answer.
  - failure_modes: A communicator can accelerate acceptance of a weak answer, turning better packaging into worse downstream decisions.
  - premortem_questions: What do I want the audience to think, feel, and do?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `international-negotiation-and-diplomacy-models`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane4_gap_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane4_gap_route: The rollout delay involves substance, signaling, stakeholders, concessions, and sequencing across more than one party.
- Graph-only recall material:
  - select_when: No party can simply impose its will without triggering response, retaliation, or coalition effects.
  - danger_when: Political signaling pressure is displacing fact-grounded option analysis.
  - failure_modes: A negotiation can look efficient on paper while failing because positions, concessions, and credibility are interpreted differently by different audiences.
  - premortem_questions: How will each relevant audience interpret this concession or sequence step differently?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `signaling`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane3_frame_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane3_frame_route: The public commitment request needs costly proof of intent rather than a cheap symbolic promise. Evidence: "ask for a public commitment"
- Graph-only recall material:
  - select_when: A strategy, offer, or position needs to communicate credibility under uncertainty, and the current message may not align with the actual underlying quality.
  - danger_when: The work is mostly impression management, and better signaling would only make a weak underlying offer look cleaner.
  - failure_modes: Cheap symbolic signals can substitute for real capability, accountability, or truth-aligned behavior.
  - premortem_questions: What costly behavior would prove this signal is real rather than symbolic?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

## Suppressed Candidates

- `signaling` (duplicate_model_id; graph_only_runtime_card)

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
