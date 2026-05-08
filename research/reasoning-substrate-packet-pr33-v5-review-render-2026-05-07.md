# Reasoning Substrate Packet Review

- Packet: `pr33-v5-capability-gap-packet-review`
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
| Candidate cards | 10 |
| Reviewed cards | 1 |
| Graph-only cards | 9 |
| Missing reviewed records | 9 |
| Absence-only cards | 0 |
| Source-too-thin cards | 0 |
| Weak/conflicting cards | 0 |

## Candidate Cards

### `opportunity-cost`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane4_gap_route`, `reviewer_note`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane4_gap_route: The advice commits the same team and launch window without naming the displaced alternative.
- Reviewed handoff signals:
  - affordance_ids: opportunity-cost.displaced-alternative-commitment-gate
  - use_when: A roadmap addition, renewal, sprint, vendor, project, or channel looks cheap because the explicit spend is small while the same people, budget, launch window, or attention are needed elsewhere.
  - case_evidence_needed: The decision under approval and the scarce resource it consumes: people, budget, calendar time, launch window, leadership attention, trust, or optionality.
  - do_not_use_when: The real alternatives, constraints, or objective function are not framed well enough for comparison without false precision.
  - misuse_guards: Do not count unrealistic alternatives that the team cannot actually fund, execute, or own.
  - source_evidence: opportunity-cost.displaced-alternative-commitment-gate: "The fundamental essence of this model is the value of the best alternative opportunity you didn't choose"
  - treatment_requirements: name-real-next-best-alternative: Require the answer to name the best real alternative displaced by the current yes, not a vague list of possibilities or a decorative comparison set.
  - absence_record: generic-alternative-comparison-affordance (duplicate_of_existing_field)

### `batna`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane4_gap_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane4_gap_route: The renewal advice treats staying with the incumbent as the only credible path without testing a walk-away option. Evidence: "renew the platform"
- Graph-only recall material:
  - select_when: Negotiation leverage depends on knowing the walk-away path before entering a pressured conversation.
  - danger_when: People are declaring a fallback as their BATNA even though it is vague, unexecutable, or worse than continuing to negotiate.
  - failure_modes: Confirmation bias can make the current deal look stronger by filtering the real quality of the walk-away option.
  - premortem_questions: What would we have to believe to accept a contrasting viewpoint, and are we truly open-minded enough to consider it?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `game-theory-payoffs`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane2_companion_chunk`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane2_companion_chunk: The assistant assumes vendor and competitor responses will stay stable after the team commits publicly.
- Graph-only recall material:
  - select_when: A recommendation cannot be judged in isolation because its value changes materially with how a rival, partner, regulator, or counterparty responds.
  - danger_when: The actors are not actually playing the same game and the visible payoff model is missing the ideology, politics, or internal incentive that is really driving behavior.
  - failure_modes: Teams can model the wrong game when one side is optimizing politics, ideology, or internal incentives that the payoff map does not capture.
  - premortem_questions: What evidence would show that we chose the wrong players, incentives, or payoff assumptions for this game?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `red-queen-effect`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane3_frame_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane3_frame_route: The user frame treats speed as advantage without separating genuine progress from keeping up. Evidence: "we cannot afford to stand still"
- Graph-only recall material:
  - select_when: Standing still effectively means losing ground because rivals, substitutes, or environmental pressures are improving at the same time.
  - danger_when: The pressure to keep running is pushing the team into analysis paralysis, feature creep, or action-first thrash without clear problem definition.
  - failure_modes: Teams can mistake heavy effort for real progress even when rivals' simultaneous adaptation is canceling out the gain.
  - premortem_questions: What would need to be true for this idea to work in a baseline that is still moving under us?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `delays`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane4_gap_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane4_gap_route: The advice postpones adoption learning until after launch without naming the feedback lag or review window. Evidence: "handle adoption issues after rollout"
- Graph-only recall material:
  - select_when: Actions and consequences are separated in time, so a naive short-term read could mistake no result yet for no effect.
  - danger_when: People are romanticizing waiting and reflection even though the next useful move is already clear and the real cost is execution drift.
  - failure_modes: Teams can treat delayed feedback as proof that an intervention failed and overcorrect before the system has time to respond.
  - premortem_questions: Are we reading no visible result yet as no effect, even though the system is known to respond with a lag?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `obligations-controls-mapping`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane4_gap_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane4_gap_route: The plan names international commitments without mapping the obligation owner, control, evidence, or cadence.
- Graph-only recall material:
  - select_when: The obligation is already known, but the controls, checkpoints, ownership, or operational boundaries needed to fulfill it are still vague.
  - danger_when: The situation is novel enough that forcing an existing control map would create false pattern recognition or suppress needed learning.
  - failure_modes: Confirmation bias can structure the map to confirm the preferred conclusion instead of exposing the real obligation gap.
  - premortem_questions: What would you have to believe?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `jobs-to-be-done`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane3_frame_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane3_frame_route: The advice treats requested features as demand without checking the customer progress job behind adoption. Evidence: "customers asked for easier integration"
- Graph-only recall material:
  - select_when: Customers are adopting, switching, or abandoning solutions for reasons that feature comparisons alone do not explain.
  - danger_when: Teams are calling every preference a job and skipping the discipline of distinguishing true progress from surface wants or internal strategy wishes.
  - failure_modes: Teams can call every preference a job and skip the work of separating true functional progress from surface wants or channel noise.
  - premortem_questions: What real progress is the user trying to make that feature comparisons alone are failing to explain?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `lock-in`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane4_gap_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane4_gap_route: The renewal advice defers reversal-cost analysis until after another integration cycle.
- Graph-only recall material:
  - select_when: Consistency, standardization, or deep commitment is creating compounding advantage, so the real question is which path should become sticky.
  - danger_when: The situation is genuinely novel, so reusing the incumbent frame would likely become an unhelpful or misleading default.
  - failure_modes: Temporary coexistence can quietly become the mechanism that keeps the organization trapped in the old path.
  - premortem_questions: What would you have to believe for the current sticky path to still be the best choice a year from now?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `path-dependence`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane2_detected_model`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane2_detected_model: The assistant treats the current installed path as neutral rather than as a constraint on future options.
- Graph-only recall material:
  - select_when: Early choices are constraining current options more than people realize, so history matters more than present-day preference alone.
  - danger_when: Path-lock is being diagnosed so broadly that it becomes an excuse for not redesigning anything that could actually change.
  - failure_modes: A system can keep reproducing old behavior even after intent changes because historical grooves are stronger than the latest plan.
  - premortem_questions: Which early choice is constraining current options more than people realize?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `cross-cultural-communication-frameworks`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane1_tendency_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane1_tendency_route: The international rollout assumes the same message will carry across regions without translating frames into action.
- Graph-only recall material:
  - select_when: The same message must survive translation across cultures, functions, or status differences without losing the intended action.
  - danger_when: Cultural models are being used as stereotype shortcuts instead of prompts to investigate the actual audience and local norms.
  - failure_modes: False pattern recognition can make a familiar communication frame look right even when the audience's actual context is different.
  - premortem_questions: What is my audience's frame of reference, and how will this message be interpreted through that lens?
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
