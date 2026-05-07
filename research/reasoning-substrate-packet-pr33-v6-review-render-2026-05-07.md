# Reasoning Substrate Packet Review

- Packet: `pr33-v6-capability-gap-packet-review`
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
| Candidate cards | 10 |
| Reviewed cards | 10 |
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

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane4_gap_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane4_gap_route: The renewal advice treats staying with the incumbent as the only credible path without testing a walk-away option. Evidence: "renew the platform"
- Reviewed handoff signals:
  - affordance_ids: batna.credible-walk-away-alternative-test
  - use_when: Negotiation leverage depends on knowing the walk-away path before entering a pressured conversation.
  - case_evidence_needed: The proposed deal or agreement being considered.
  - do_not_use_when: The supposed BATNA is vague, unexecutable, or worse than continuing to negotiate.
  - misuse_guards: Do not treat a vague fallback as a BATNA.
  - source_evidence: batna.credible-walk-away-alternative-test: "negotiation leverage depends on knowing the walk-away path before entering a pressured conversation"
  - treatment_requirements: compare-deal-against-executable-fallback: Require the answer to name the walk-away option, test whether it is executable, and compare the deal against that option rather than against hope or sunk effort.
  - absence_record: textbook-batna-definition-affordance (not_supported_by_source)

### `game-theory-payoffs`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane2_companion_chunk`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane2_companion_chunk: The assistant assumes vendor and competitor responses will stay stable after the team commits publicly.
- Reviewed handoff signals:
  - affordance_ids: game-theory-payoffs.counterparty-response-payoff-map
  - use_when: A rival, partner, regulator, buyer, seller, or negotiating counterparty can change the value of the proposed action.
  - case_evidence_needed: The players or counterparties involved.
  - do_not_use_when: The actors are not actually playing the same game because reputation, ideology, politics, or internal incentives dominate.
  - misuse_guards: Do not assume both sides are optimizing the same payoff model.
  - source_evidence: game-theory-payoffs.counterparty-response-payoff-map: "identifying the players, the actions available to them, the information they possess, and the resultant payoff for each potential action"
  - treatment_requirements: name-players-moves-and-decisive-payoffs: Require the answer to map the relevant players, likely moves, and payoff drivers, while pruning branches that do not materially change the decision.
  - absence_record: same-game-assumption-affordance (not_supported_by_source)

### `red-queen-effect`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane3_frame_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane3_frame_route: The user frame treats speed as advantage without separating genuine progress from keeping up. Evidence: "we cannot afford to stand still"
- Reviewed handoff signals:
  - affordance_ids: red-queen-effect.relative-position-adaptation-test
  - use_when: Standing still effectively means losing ground because rivals, substitutes, or environmental pressures are improving.
  - case_evidence_needed: The rival, substitute, benchmark, or environmental pressure that changes the relative standard.
  - do_not_use_when: The situation is not relative-performance driven and effort can be judged on absolute outcomes.
  - misuse_guards: Do not frame every challenge as an arms race.
  - source_evidence: red-queen-effect.relative-position-adaptation-test: "continuous adaptation and evolution are necessary just to maintain one’s current state"
  - treatment_requirements: separate-maintenance-from-advantage: Require the answer to identify whether the proposed effort maintains relative position, creates advantage, or merely reacts to competitor motion.
  - absence_record: arms-race-everything-affordance (not_supported_by_source)

### `delays`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane4_gap_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane4_gap_route: The advice postpones adoption learning until after launch without naming the feedback lag or review window. Evidence: "handle adoption issues after rollout"
- Reviewed handoff signals:
  - affordance_ids: delays.lagged-feedback-timing-gate
  - use_when: A plan, intervention, workflow, or project has consequences that will arrive after a meaningful lag.
  - case_evidence_needed: The action, intervention, or commitment under review.
  - do_not_use_when: The next useful move is already clear and waiting would mainly defer ownership.
  - misuse_guards: Do not romanticize waiting when the next useful move is already clear.
  - source_evidence: delays.lagged-feedback-timing-gate: "time is a dynamic factor within any system"
  - treatment_requirements: name-lag-before-reacting: Require the answer to name the relevant delay, specify the feedback signal and review window, and separate patience from drift before recommending action or non-action.
  - absence_record: romanticized-waiting-affordance (not_supported_by_source)

### `obligations-controls-mapping`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane4_gap_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane4_gap_route: The plan names international commitments without mapping the obligation owner, control, evidence, or cadence.
- Reviewed handoff signals:
  - affordance_ids: obligations-controls-mapping.obligation-to-control-trace
  - use_when: A team knows what must be true or delivered but has not mapped how the obligation will be controlled in practice.
  - case_evidence_needed: The obligation, requirement, responsibility, or success criterion being translated.
  - do_not_use_when: The proposed mapping would create documentation theater without changing live decision points or behavior.
  - misuse_guards: Do not treat a control map as useful unless it is tied to an actual obligation, decision point, or operating behavior.
  - source_evidence: obligations-controls-mapping.obligation-to-control-trace: "ensuring that a system's structure and behavior are inherently aligned with its mandated goals, responsibilities, and constraints"
  - treatment_requirements: trace-obligation-to-live-control: Require the answer to name the obligation, the control that enforces it, the owner or checkpoint, and how the control will be observed in real operation.
  - absence_record: documentation-theater-control-map (not_supported_by_source)

### `jobs-to-be-done`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane3_frame_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane3_frame_route: The advice treats requested features as demand without checking the customer progress job behind adoption. Evidence: "customers asked for easier integration"
- Reviewed handoff signals:
  - affordance_ids: jobs-to-be-done.real-progress-job-discovery
  - use_when: Customers are adopting, switching, or abandoning solutions for reasons that feature comparisons alone do not explain.
  - case_evidence_needed: Evidence of adoption, switching, abandonment, workaround, or repeated use.
  - do_not_use_when: The answer would call every preference a job.
  - misuse_guards: Do not call every preference a job.
  - source_evidence: jobs-to-be-done.real-progress-job-discovery: "customers "hire" a product or service to fulfill a specific task or achieve a desired outcome"
  - treatment_requirements: separate-job-from-feature-preference: Require the answer to name the customer's real progress goal and distinguish it from feature requests or internal product assumptions.
  - absence_record: preference-as-job-affordance (not_supported_by_source)

### `lock-in`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane4_gap_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane4_gap_route: The renewal advice defers reversal-cost analysis until after another integration cycle.
- Reviewed handoff signals:
  - affordance_ids: lock-in.reversal-cost-dependency-audit
  - use_when: A vendor exit, platform shift, ERP migration, or infrastructure decision is being framed as normal implementation effort.
  - case_evidence_needed: The platform, vendor, architecture, or path being locked in.
  - do_not_use_when: The current path is deliberately sticky because stability, standardization, or commitment is still compounding advantage.
  - misuse_guards: Do not treat future switching as equally cheap after custom workflows and contracts harden.
  - source_evidence: lock-in.reversal-cost-dependency-audit: "persistent adherence to a previous state"
  - treatment_requirements: price-reversal-cost-before-deferring-switch: Require the answer to price the reversal and coexistence costs before accepting claims that the team can switch later.
  - absence_record: switch-later-same-cost-affordance (not_supported_by_source)

### `path-dependence`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane2_detected_model`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane2_detected_model: The assistant treats the current installed path as neutral rather than as a constraint on future options.
- Reviewed handoff signals:
  - affordance_ids: path-dependence.installed-dependency-unwind-map
  - use_when: Early choices are constraining current options more than people realize.
  - case_evidence_needed: The historical path, early choice, or inherited architecture shaping the current option set.
  - do_not_use_when: The reset is genuinely cheap and reversible because the installed base is shallow and switching costs are paid down.
  - misuse_guards: Do not use path history as an excuse to avoid redesign or responsibility.
  - source_evidence: path-dependence.installed-dependency-unwind-map: "initial conditions and historical sequential choices significantly shape outcomes"
  - treatment_requirements: price-inherited-dependencies-before-target-state: Require the answer to map dependencies created by the existing path and price the unwind before comparing target options.
  - absence_record: clean-slate-comparison-affordance (not_supported_by_source)

### `cross-cultural-communication-frameworks`

- Coverage: `reviewed_affordance_available`
- Pulled by: `lane1_tendency_route`
- Source custody: `repo_source_custodied` / reviewed record: `true`
- Why pulled:
  - lane1_tendency_route: The international rollout assumes the same message will carry across regions without translating frames into action.
- Reviewed handoff signals:
  - affordance_ids: cross-cultural-communication-frameworks.frame-translation-action-check
  - use_when: The same message must survive translation across cultures, functions, or status differences without losing the intended action.
  - case_evidence_needed: The message, decision, or action that must be understood.
  - do_not_use_when: Cultural models are being used as stereotype shortcuts instead of prompts to investigate the actual audience.
  - misuse_guards: Do not use cultural models as stereotype shortcuts.
  - source_evidence: cross-cultural-communication-frameworks.frame-translation-action-check: "to bridge the inherent disconnect between the sender's intricate understanding and the receiver's often simplified, emotionally filtered processing of information"
  - treatment_requirements: translate-frame-without-hiding-action: Require the answer to adapt message framing for the actual audience while preserving the core action and hard trade-offs.
  - absence_record: stereotype-shortcut-communication (not_supported_by_source)

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
