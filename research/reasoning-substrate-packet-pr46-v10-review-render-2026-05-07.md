# Reasoning Substrate Packet Review

- Packet: `pr46-v10-frame-correction-packet-review`
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
| Reviewed cards | 0 |
| Graph-only cards | 12 |
| Missing reviewed records | 12 |
| Absence-only cards | 0 |
| Source-too-thin cards | 0 |
| Weak/conflicting cards | 0 |

## Candidate Cards

### `cognitive-gaps-assessment`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane4_gap_route`, `reviewer_note`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane4_gap_route: The plan assumes the team has enough context to act, but the missing evidence, capability, perspective, or transfer gap may be the real blocker. Evidence: "we have enough context to move"
- Graph-only recall material:
  - select_when: Confidence is high but the explanation still feels under-specified and the team may be missing something important.
  - danger_when: Gap mapping has become a performance ritual that labels uncertainty without changing the plan or evidence bar.
  - failure_modes: The bias blind spot can make sophisticated people less willing to see their own missing knowledge.
  - premortem_questions: What would need to be true for this idea to work, and which assumption in that chain is least grounded?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `critical-thinking`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane2_detected_model`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane2_detected_model: The memo treats its explanation as clear, but claim, evidence, assumption, authority, emotion, and story may be doing different work. Evidence: "the right answer is clear"
- Graph-only recall material:
  - select_when: Important judgments depend on separating evidence from story, authority, or emotional plausibility.
  - danger_when: Critical thinking is becoming detachment theater, where nuance and skepticism are used to avoid taking a position or making a recommendation.
  - failure_modes: Analysis paralysis can turn careful inquiry into a delay machine that never cashes out in action.
  - premortem_questions: Is the worst case bad enough?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `counterfactual-reasoning`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane3_frame_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane3_frame_route: The advice narrows quickly to one path without testing plausible alternatives, failure branches, or paths not taken before commitment. Evidence: "option B is unlikely"
- Graph-only recall material:
  - select_when: One realized outcome is hiding the actual quality of the decision process and the missing branches need to be recovered.
  - danger_when: The team is spinning imagined alternatives that are untethered from plausible causal structure, base rates, or the real decision context.
  - failure_modes: Outcome overfitting can make the past feel inevitable and hide the actual quality of the original decision.
  - premortem_questions: What would you have to believe to accept this conclusion?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `metacognitive-questioning`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane1_tendency_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane1_tendency_route: The team is ready to execute, but the next discriminating question could still change the path if it is bounded and action-linked. Evidence: "we should just execute"
- Graph-only recall material:
  - select_when: Better questions would change the path because the main constraint is weak inspection of assumptions, strategy choice, or evidence quality.
  - danger_when: Reflective questioning is turning into infinite deferral that postpones commitment, experimentation, or ownership.
  - failure_modes: Self-questioning can become infinite deferral that keeps postponing commitment, experimentation, or ownership.
  - premortem_questions: How do you define a problem in a precise way to meet the decision maker's needs?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `reasoning-mode-router`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane4_gap_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane4_gap_route: The same response is trying to diagnose, design, critique, and execute; the packet should check which reasoning mode fits the current task stage. Evidence: "diagnose, design, and execute all in one pass"
- Graph-only recall material:
  - select_when: The problem could be approached through diagnosis, creative exploration, adversarial critique, or execution planning, and choosing the wrong path would materially distort the work.
  - danger_when: Routing debate itself is becoming overhead and the team cannot name the next discriminating question or experiment.
  - failure_modes: Faulty pattern recognition can route a novel problem into a familiar frame and produce a disastrously wrong solution path.
  - premortem_questions: What are the assumptions embedded in the framework I am currently using?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `reframing-perspective`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane3_frame_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane3_frame_route: The case is framed as a pricing problem, but a different decision variable could expose a better action path. Evidence: "pricing problem"
- Graph-only recall material:
  - select_when: The first story is trapping the decision by making one option feel inevitable or impossible.
  - danger_when: Reframing is becoming euphemism that renames a hard reality without improving the option set or truth surface.
  - failure_modes: A plan can look inevitable only because the current story hides other valid lenses and success criteria.
  - premortem_questions: What different action becomes reasonable if we look at the same facts through a user, system, risk, or trade-off lens?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `theory-induced-blindness`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane2_companion_chunk`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane2_companion_chunk: The favored framework may explain the visible facts while filtering out disconfirming signals or a better cut of the problem. Evidence: "the chosen framework explains it"
- Graph-only recall material:
  - select_when: A favored framework might be hiding reality by shaping attention too aggressively and filtering out inconvenient evidence.
  - danger_when: Reframing has turned into endless theory shopping that avoids evidence, testable claims, or operational decisions.
  - failure_modes: Illusion of understanding can make experts stop investigating because they confuse familiarity with reality access.
  - premortem_questions: What framework is this analysis missing?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `einstellung-effect`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane1_tendency_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane1_tendency_route: The team is reusing a familiar playbook, so the packet should test whether fluency is being mistaken for real fit. Evidence: "reuse last quarter's playbook"
- Graph-only recall material:
  - select_when: An experienced team keeps reaching for the same proven frame even though the situation feels structurally different.
  - danger_when: Avoid-fixation language is becoming a reason to reject all prior knowledge instead of distinguishing helpful pattern recognition from stale lock-in.
  - failure_modes: A familiar solution path can block better alternatives because the first successful frame becomes hard to unsee.
  - premortem_questions: What if the reason this answer arrived so fast is that we are reusing a familiar template rather than seeing the actual structure?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `dialectical-reasoning`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane3_frame_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane3_frame_route: The advice collapses tension into one side winning, but both positions may preserve partial truths that should shape the next move. Evidence: "one side must be right"
- Graph-only recall material:
  - select_when: A strong claim needs an explicit counterclaim before the team can trust the conclusion.
  - danger_when: The team is confusing productive dialectic with endless contrarianism and never converting tension into a bounded decision.
  - failure_modes: Dialectical reasoning fails when teams mistake endless contrarianism for real synthesis work.
  - premortem_questions: What is the strongest antithesis to our current thesis?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `bias-blind-spot`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane1_tendency_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane1_tendency_route: The memo diagnoses the partner as biased while not testing the advising team's own incentives, status, or self-protective interpretation. Evidence: "they are being irrational"
- Graph-only recall material:
  - select_when: A review or debate risks turning into a diagnosis of everyone else's distortions while leaving the team's own reasoning unexamined.
  - danger_when: The model is being used mainly to brand other people as biased rather than to create a process that can expose the local blind spot.
  - failure_modes: Awareness of the bias blind spot can become performative self-knowledge that sounds humble without changing how evidence is weighed.
  - premortem_questions: What if our awareness of this bias changes nothing about how we are currently weighing evidence?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `false-precision-avoidance`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane2_detected_model`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane2_detected_model: The recommendation uses crisp dates and uplift claims, but the exactness may create confidence without changing the decision. Evidence: "ship by June 30 with 35% uplift"
- Graph-only recall material:
  - select_when: A decision needs directional clarity, bounded ranges, or operating thresholds more than an illusion of exact certainty.
  - danger_when: Simplicity is being used to hide uncertainty, skip the underlying analysis, or present a rounded answer as if the variance no longer matters.
  - failure_modes: Teams can use simplicity to hide uncertainty and present a rounded answer as if the underlying variance no longer matters.
  - premortem_questions: If this was cut, would anything be lost?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `wysiati`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane4_gap_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane4_gap_route: The visible story is coherent, but the packet should force attention to missing evidence, denominators, disconfirming cases, and absent briefing sides. Evidence: "we only have the visible wins"
- Graph-only recall material:
  - select_when: A confident conclusion has been reached from evidence that may be incomplete, non-random, or selectively presented.
  - danger_when: Evidence has been explicitly audited for completeness and the gaps are known and acknowledged — the closure is warranted.
  - failure_modes: Confidence of ignorance makes less-informed decision-makers more confident than better-informed ones, because fewer contradictions and gaps allow a more coherent story to form.
  - premortem_questions: What evidence would we need to see to be confident in this conclusion — and do we know why that evidence is not in front of us?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

## Suppressed Candidates

- `reasoning-mode-router` (duplicate_model_id; graph_only_runtime_card)

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
