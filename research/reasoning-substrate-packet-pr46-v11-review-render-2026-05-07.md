# Reasoning Substrate Packet Review

- Packet: `pr46-v11-frame-correction-packet-review`
- Version: `reasoning_substrate_packet.v1`
- Status: `draft_review_only`
- Runtime policy: `runtime_dormant`
- Source artifacts: `data/knowledge_graph.json`, `data/compiled/model_affordances/affordances_v11.json`, `data/model_sources/manifest.json`

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

### `cognitive-gaps-assessment`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane4_gap_route`, `reviewer_note`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane4_gap_route: The plan assumes the team has enough context to act, but the missing evidence, capability, perspective, or transfer gap may be the real blocker. Evidence: "we have enough context to move"
- Reviewed handoff signals:
  - affordance_ids: cognitive-gaps-assessment.missing-reality-gap-audit
  - use_when: The advice is plausible, but the gap between the current explanation and reality is still not explicit.
  - case_evidence_needed: The current explanation or advice the user is considering.
  - do_not_use_when: The missing facts, assumptions, and capability limits are already named with evidence and decision consequences.
  - misuse_guards: Do not use gap language as a sophisticated way to postpone action without changing the decision condition.
  - source_evidence: cognitive-gaps-assessment.missing-reality-gap-audit: "Most useful when confidence is high, assumptions are implicit, and the gap between the current explanation and reality still feels under-specified."
  - treatment_requirements: convert-gap-to-decision-condition: Require the answer to convert a suspected cognitive gap into a named missing condition, the evidence needed to resolve it, and the plan change if the gap remains open.
  - absence_record: gap-mapping-without-plan-change (not_supported_by_source)

### `critical-thinking`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane2_detected_model`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane2_detected_model: The memo treats its explanation as clear, but claim, evidence, assumption, authority, emotion, and story may be doing different work. Evidence: "the right answer is clear"
- Reviewed handoff signals:
  - affordance_ids: critical-thinking.claim-evidence-assumption-check
  - use_when: The advice sounds plausible but may be leaning on story, authority, emotion, or first impressions.
  - case_evidence_needed: The central claim or recommendation.
  - do_not_use_when: The claim, evidence, assumptions, and causal links are already explicit and decision-relevant.
  - misuse_guards: Do not use critical thinking as a license for endless qualification or refusal to decide.
  - source_evidence: critical-thinking.claim-evidence-assumption-check: "Most useful when important judgments depend on separating evidence from story"
  - treatment_requirements: separate-claim-evidence-assumption: Require the answer to expose the core claim, supporting evidence, necessary assumptions, and any authority or emotional influence before treating the conclusion as action-ready.
  - absence_record: detachment-theater-as-critical-thinking (not_supported_by_source)

### `counterfactual-reasoning`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane3_frame_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane3_frame_route: The advice narrows quickly to one path without testing plausible alternatives, failure branches, or paths not taken before commitment. Evidence: "option B is unlikely"
- Reviewed handoff signals:
  - affordance_ids: counterfactual-reasoning.plausible-alternative-branch-test
  - use_when: A realized or preferred outcome is being treated as proof that the decision process is good.
  - case_evidence_needed: The actual or preferred path under review.
  - do_not_use_when: The alternative paths are fictional, implausible, or untethered from the real decision context.
  - misuse_guards: Do not invent fictional alternatives without causal structure, base rates, or real decision context.
  - source_evidence: counterfactual-reasoning.plausible-alternative-branch-test: "Most useful when one realized outcome is hiding the real decision quality"
  - treatment_requirements: recover-plausible-branches: Require the answer to recover realistic branches that the current story is suppressing, then connect each branch to assumptions, evidence, or failure paths that would change the recommendation.
  - absence_record: counterfactual-fiction-as-discipline (not_supported_by_source)

### `metacognitive-questioning`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane1_tendency_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane1_tendency_route: The team is ready to execute, but the next discriminating question could still change the path if it is bounded and action-linked. Evidence: "we should just execute"
- Reviewed handoff signals:
  - affordance_ids: metacognitive-questioning.process-inspection-next-question-gate
  - use_when: The path could change if the team asked a better question about assumptions, strategy choice, or evidence quality.
  - case_evidence_needed: The current answer or plan.
  - do_not_use_when: The next discriminating question is already explicit and tied to action.
  - misuse_guards: Do not add recursive self-questioning that delays commitment without sharpening the next move.
  - source_evidence: metacognitive-questioning.process-inspection-next-question-gate: "Most useful when better questions will change the path"
  - treatment_requirements: name-next-discriminating-question: Require the answer to name the next question that would change the path, explain why that question matters, and tie it to a bounded action, evidence check, or owner.
  - absence_record: self-questioning-as-infinite-deferral (not_supported_by_source)

### `reasoning-mode-router`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane4_gap_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane4_gap_route: The same response is trying to diagnose, design, critique, and execute; the packet should check which reasoning mode fits the current task stage. Evidence: "diagnose, design, and execute all in one pass"
- Reviewed handoff signals:
  - affordance_ids: reasoning-mode-router.context-driven-mode-selection-check
  - use_when: The problem could be solved through very different reasoning modes with different failure modes.
  - case_evidence_needed: The current problem stage: goal, problem, diagnosis, design, doing, critique, or exploration.
  - do_not_use_when: The right mode is already explicit and the next discriminating question is clear.
  - misuse_guards: Do not turn this card into deterministic reasoning-mode routing.
  - source_evidence: reasoning-mode-router.context-driven-mode-selection-check: "conscious selection of a processing strategy"
  - treatment_requirements: name-stage-and-mode-fit: Require the answer to name the current reasoning stage, the mode being used, why that mode fits the task, and what evidence would trigger a mode switch.
  - absence_record: deterministic-case-type-mode-router (not_supported_by_source)

### `reframing-perspective`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane3_frame_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane3_frame_route: The case is framed as a pricing problem, but a different decision variable could expose a better action path. Evidence: "pricing problem"
- Reviewed handoff signals:
  - affordance_ids: reframing-perspective.decision-variable-reframe-test
  - use_when: The current language makes one option look inevitable, impossible, or obviously correct.
  - case_evidence_needed: The current problem frame and the option it makes natural.
  - do_not_use_when: The proposed reframe is only a vivid slogan or euphemism for the same hard reality.
  - misuse_guards: Do not reframe for cleverness unless it changes evidence, action, or dismissal conditions.
  - source_evidence: reframing-perspective.decision-variable-reframe-test: "Most useful when the first story is trapping the decision"
  - treatment_requirements: show-variable-changed-by-frame: Require the answer to show what decision variable, success criterion, trade-off, or next action changes if the problem is reframed.
  - absence_record: reframing-as-euphemism (not_supported_by_source)

### `theory-induced-blindness`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane2_companion_chunk`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane2_companion_chunk: The favored framework may explain the visible facts while filtering out disconfirming signals or a better cut of the problem. Evidence: "the chosen framework explains it"
- Reviewed handoff signals:
  - affordance_ids: theory-induced-blindness.favored-framework-blindness-check
  - use_when: A favored framework might be hiding reality or filtering inconvenient evidence.
  - case_evidence_needed: The framework, theory, or model currently shaping the advice.
  - do_not_use_when: The current framework's assumptions, omissions, and limits are already explicit.
  - misuse_guards: Do not treat all frameworks as suspect; test fit, omissions, and assumptions.
  - source_evidence: theory-induced-blindness.favored-framework-blindness-check: "Most useful when a favored framework might be hiding reality"
  - treatment_requirements: name-what-framework-filters-out: Require the answer to name the favored framework, what it makes visible, what it filters out, and what alternative cut would test whether the current map is hiding reality.
  - absence_record: endless-theory-shopping (not_supported_by_source)

### `einstellung-effect`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane1_tendency_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane1_tendency_route: The team is reusing a familiar playbook, so the packet should test whether fluency is being mistaken for real fit. Evidence: "reuse last quarter's playbook"
- Reviewed handoff signals:
  - affordance_ids: einstellung-effect.familiar-solution-lock-in-interrupt
  - use_when: An experienced team keeps reaching for the same proven frame even though the situation feels structurally different.
  - case_evidence_needed: The familiar solution or frame currently being applied.
  - do_not_use_when: The familiar pattern has been tested against the current case and the assumptions still hold.
  - misuse_guards: Do not reject prior knowledge merely because novelty is possible.
  - source_evidence: einstellung-effect.familiar-solution-lock-in-interrupt: "existing or previously learned solution prevents an individual from perceiving, or being open to, alternative solutions"
  - treatment_requirements: test-familiar-template-fit: Require the answer to name the familiar template, identify what makes the case different, and specify the test or alternative frame that would reveal stale pattern lock-in.
  - absence_record: reject-all-prior-knowledge (not_supported_by_source)

### `dialectical-reasoning`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane3_frame_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane3_frame_route: The advice collapses tension into one side winning, but both positions may preserve partial truths that should shape the next move. Evidence: "one side must be right"
- Reviewed handoff signals:
  - affordance_ids: dialectical-reasoning.bounded-antithesis-synthesis-test
  - use_when: The situation contains live disagreement, partial truths, or competing interpretations that need to be surfaced rather than flattened.
  - case_evidence_needed: The thesis or current recommendation.
  - do_not_use_when: The opposing position is already represented and the decision criterion is clear.
  - misuse_guards: Do not turn dialectic into endless contrarianism.
  - source_evidence: dialectical-reasoning.bounded-antithesis-synthesis-test: "thesis, antithesis, synthesis"
  - treatment_requirements: turn-tension-into-bounded-synthesis: Require the answer to state the thesis, strongest antithesis, evidence each preserves, and the bounded synthesis or next step that prevents conflict from becoming endless debate.
  - absence_record: endless-contrarianism-as-dialectic (not_supported_by_source)

### `bias-blind-spot`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane1_tendency_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane1_tendency_route: The memo diagnoses the partner as biased while not testing the advising team's own incentives, status, or self-protective interpretation. Evidence: "they are being irrational"
- Reviewed handoff signals:
  - affordance_ids: bias-blind-spot.self-bias-accountability-check
  - use_when: Decision-makers are confident in their own objectivity before judging ambiguous evidence, trade-offs, or rival interpretations.
  - case_evidence_needed: The judgment or critique being made.
  - do_not_use_when: The answer already names how the reviewer's own incentives, emotions, or perspective may distort judgment.
  - misuse_guards: Do not use bias labels only against other people.
  - source_evidence: bias-blind-spot.self-bias-accountability-check: "the tendency to be much better at recognizing biased reasoning in others than in oneself"
  - treatment_requirements: turn-bias-check-inward: Require the answer to identify where the reviewer or advising party may be biased, what evidence would challenge that bias, and what external check prevents critique from pointing only outward.
  - absence_record: performative-self-knowledge-as-mitigation (not_supported_by_source)

### `false-precision-avoidance`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane2_detected_model`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane2_detected_model: The recommendation uses crisp dates and uplift claims, but the exactness may create confidence without changing the decision. Evidence: "ship by June 30 with 35% uplift"
- Reviewed handoff signals:
  - affordance_ids: false-precision-avoidance.decision-relevant-precision-boundary
  - use_when: A decision needs directional clarity, bounded ranges, or operating thresholds more than exact certainty.
  - case_evidence_needed: The estimate, claim, or recommendation that appears precise.
  - do_not_use_when: The domain genuinely requires precise calculation, engineering tolerance, surgery-level accuracy, or a quantitative update.
  - misuse_guards: Do not use simplicity to skip underlying analysis.
  - source_evidence: false-precision-avoidance.decision-relevant-precision-boundary: "a decision needs directional clarity, bounded ranges, or operating thresholds more than an illusion of exact certainty."
  - treatment_requirements: replace-fake-exactness-with-threshold: Require the answer to identify where precision is not decision-relevant, preserve necessary rigor, and express the result as a range, threshold, or approximation that changes action.
  - absence_record: simplicity-that-hides-uncertainty (not_supported_by_source)

### `wysiati`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane4_gap_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane4_gap_route: The visible story is coherent, but the packet should force attention to missing evidence, denominators, disconfirming cases, and absent briefing sides. Evidence: "we only have the visible wins"
- Reviewed handoff signals:
  - affordance_ids: wysiati.missing-evidence-denominator-audit
  - use_when: The available evidence forms a coherent story that feels complete.
  - case_evidence_needed: The coherent story or conclusion under review.
  - do_not_use_when: The answer already names the missing evidence and why its absence is random or structured.
  - misuse_guards: Do not treat narrative coherence as evidence completeness.
  - source_evidence: wysiati.missing-evidence-denominator-audit: "Confidence tracks story quality, not evidence completeness."
  - treatment_requirements: audit-missing-denominator: Require the answer to separate story coherence from evidence completeness by naming the missing denominator, absent disconfirming case, and why the absence matters before commitment.
  - absence_record: coherent-story-as-proof (not_supported_by_source)

## Suppressed Candidates

- `reasoning-mode-router` (duplicate_model_id; reviewed_affordance_available)

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
