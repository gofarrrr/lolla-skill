# Reasoning Substrate Packet Review

- Packet: `pr43-v9-risk-reversibility-packet-review`
- Version: `reasoning_substrate_packet.v1`
- Status: `draft_review_only`
- Runtime policy: `runtime_dormant`
- Source artifacts: `data/knowledge_graph.json`, `data/compiled/model_affordances/affordances_v9.json`, `data/model_sources/manifest.json`

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

### `risk-vs-uncertainty`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane1_tendency_route`, `reviewer_note`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane1_tendency_route: The advice treats the regulated market entry as measurable enough to fund, but the key drivers may still be ambiguous or unstable. Evidence: "approve the market-entry budget"
- Graph-only recall material:
  - select_when: Confidence is outrunning evidence and the core drivers remain ambiguous, unstable, or only partly observable.
  - danger_when: Stable reference classes, credible probabilities, and operator-level thresholds already exist, so continued uncertainty framing would only avoid disciplined execution.
  - failure_modes: Conjunction-fallacy style optimism can make a complex plan look safer than the uncertainty really permits.
  - premortem_questions: Is the worst case bad enough?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `switching-costs`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane4_gap_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane4_gap_route: The vendor migration is described as reversible, but the advice does not name dual-run drag, data history, integration dependencies, or unwind governance. Evidence: "start vendor migration"
- Graph-only recall material:
  - select_when: A seemingly better alternative exists, but economic, psychological, or operational friction is keeping people on the incumbent path.
  - danger_when: The situation is genuinely novel enough that clinging to the incumbent frame would mainly reinforce cognitive entrenchment.
  - failure_modes: Temporary coexistence can quietly become the architecture that traps the organization in both the old and new path.
  - premortem_questions: What specific capability, workflow, or partner dependency would force both the old and new path to stay alive longer than planned?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `redundancy`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane4_gap_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane4_gap_route: The plan says to add backups, but does not test whether the backup is independent, owned, usable, and worth the added cost. Evidence: "adding backups"
- Graph-only recall material:
  - select_when: Single-point failure is unacceptable and a backup path would materially change survival or recovery quality.
  - danger_when: Duplication is being added by habit without a clear failure mode that justifies its cost.
  - failure_modes: Repeated content can increase cognitive load when the duplication adds no real protection or clarification.
  - premortem_questions: What exact failure mode justifies this extra layer, copy, or backup path?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `regulatory-horizon-scanning`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane3_frame_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane3_frame_route: The advice says to monitor regulatory news but does not specify weak-signal thresholds, owners, response triggers, or present-day options. Evidence: "monitoring regulatory news"
- Graph-only recall material:
  - select_when: External rules, enforcement priorities, or policy narratives are moving early enough that waiting for certainty would create strategic lag.
  - danger_when: Horizon scanning has become a trend-slide ritual without thresholds, response triggers, or accountable owners.
  - failure_modes: Trend language without thresholds or owners creates slide theater rather than anticipatory readiness.
  - premortem_questions: What weak signal would actually force a change in product, operating, or capital decisions if it strengthened?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `cybersecurity-thinking-models`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane2_detected_model`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane2_detected_model: The migration and launch plan mentions security, but does not map adversarial incentives, control owners, or cross-layer failure chains. Evidence: "improving security"
- Graph-only recall material:
  - select_when: The problem is adversarial, fast-changing, and capable of cascading across technical, human, and governance layers at once.
  - danger_when: Threat-model language is being fetishized while asset specificity, attack-surface reality, and operational ownership stay vague.
  - failure_modes: Teams can optimize for appearing secure instead of being secure when stakeholder incentives are misaligned with the measured outcome.
  - premortem_questions: Which stakeholder gains if this plan underperforms quietly rather than fails visibly?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `non-linear-dynamics`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane4_gap_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane4_gap_route: A local launch acceleration could amplify downstream support load, regulatory exposure, or adoption loops instead of producing a linear gain.
- Graph-only recall material:
  - select_when: Small interventions could create outsized effects because feedback loops, delays, or threshold crossings dominate the system.
  - danger_when: Complexity language is being used to avoid naming concrete levers, checkpoints, or experiments.
  - failure_modes: Straight-line plans can miss threshold crossings, delayed blowback, and outsized effects from small moves.
  - premortem_questions: Which feedback loops or delays could make a small move create an outsized effect later?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `tipping-points`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane3_frame_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane3_frame_route: Early customer interest is being treated as a possible breakthrough without naming the controlling threshold or prerequisite buildup. Evidence: "early customer interest"
- Graph-only recall material:
  - select_when: Progress is not linear and one constrained variable or threshold could unlock disproportionate change.
  - danger_when: Leaders are romanticizing breakthrough moments while underinvesting in the slow prerequisite buildup required for a real threshold crossing.
  - failure_modes: Teams waste effort on incremental fixes when one constrained threshold or leverage point is actually controlling the system shift.
  - premortem_questions: What specific variable, condition, or social threshold would need to change for this system to shift disproportionately?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `butterfly-effect`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane2_companion_chunk`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane2_companion_chunk: The advice could understate how one small migration or compliance choice propagates through dependencies unless a plausible cascade path is named.
- Graph-only recall material:
  - select_when: A small local decision could propagate through a tightly connected system and create outsized downstream effects.
  - danger_when: Butterfly-effect language is being used to justify vague fear or grandiosity without naming a plausible transmission path.
  - failure_modes: A decision can look safe locally while still creating dangerous downstream effects once it propagates through the broader system.
  - premortem_questions: If this small move goes wrong, through which specific chain of dependencies, delays, or feedback loops does the damage spread?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `chaos-theory`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane2_companion_chunk`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane2_companion_chunk: The environment may be too unstable for exact six-week forecasts, so the packet should favor robustness, monitoring, slack, and reversibility. Evidence: "within six weeks"
- Graph-only recall material:
  - select_when: The environment is unstable enough that simple linear prediction is giving false confidence.
  - danger_when: Teams are using chaos rhetoric to imply nothing can be understood or improved.
  - failure_modes: Linear forecasting creates false confidence when the system is actually sensitive, nonlinear, and hard to predict over long horizons.
  - premortem_questions: Where are we confusing forecast precision with actual control over a nonlinear environment?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `combinatorial-effects`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane4_gap_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane4_gap_route: Regulation, vendor migration, security exposure, and early demand may interact non-additively, so the packet should find make-or-break combinations.
- Graph-only recall material:
  - select_when: Several forces are interacting so the outcome is larger or stranger than any single driver would predict alone.
  - danger_when: The situation is being forced into a dramatic synergy story before the interacting mechanisms have been identified clearly.
  - failure_modes: Treating a lollapalooza outcome as if it had one cause hides the interacting forces that actually made it possible.
  - premortem_questions: Which forces are aligned here, and what happens if one of the supposedly minor drivers is removed from the combination?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `critical-mass`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane3_frame_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane3_frame_route: Early adoption may not become self-sustaining unless the minimum density of customers, workflow, trust, or support exists. Evidence: "early customer interest"
- Graph-only recall material:
  - select_when: Viability is threshold-dependent, so adoption, liquidity, trust, or participation only works after activity crosses a minimum density.
  - danger_when: Early launch energy or one-off seeding is being mistaken for durable threshold security before the reinforcement loop is actually stable.
  - failure_modes: False pattern recognition can force a threshold explanation onto a problem whose real structure does not match critical-mass dynamics.
  - premortem_questions: Is this merely an analogy, or is the underlying structure truly the same?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

### `prospect-theory`

- Coverage: `graph_only_runtime_card`
- Pulled by: `lane1_tendency_route`
- Source custody: `repo_source_custodied` / reviewed record: `false`
- Why pulled:
  - lane1_tendency_route: The team may double down or unwind under loss-frame pressure, so the packet should distinguish decision quality from reference-point distortion. Evidence: "double down or unwind"
- Graph-only recall material:
  - select_when: A choice is being driven more by perceived gains, losses, or reference points than by objective value.
  - danger_when: The analysis still needs a normative decision framework and prospect-theory language would only redescribe behavior without improving the choice.
  - failure_modes: Leaders can exploit loss aversion or threat framing to force compliance without improving the underlying economics, truth, or decision quality.
  - premortem_questions: What changes if these same economics are reframed as gains, losses, or a different reference point?
- Do not overclaim:
  - No reviewed affordance record is available in the current corpus.

## Suppressed Candidates

- `switching-costs` (duplicate_model_id; graph_only_runtime_card)

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
