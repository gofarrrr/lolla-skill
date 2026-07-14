# Core Semantic Validation — Case 01: Enterprise Logo Beta

Status: first fresh controlled case; live monolithic extraction completed 2026-07-09

Purpose: test whether Lolla understands a joint user–assistant decision process before testing whether its graph and mental-model pressure improve the answer.

This is a synthetic case. It contains no private customer information.

## Source Conversation

**Turn 1 — User**

We are a five-person SaaS company. A well-known enterprise prospect says it would join a beta if we launch next month. Should we launch publicly and use its logo to attract other customers?

**Turn 2 — Assistant**

Yes. A recognizable enterprise logo is a strong signal that the market is ready, and moving next month will help you establish momentum before competitors notice the opportunity. I would announce a limited public beta and make this prospect the flagship design partner.

**Turn 3 — User**

They have not signed anything. We only have two friendly emails from their innovation lead, our only senior engineer is already supporting existing customers, and the board is excited mainly because of the company's name.

**Turn 4 — Assistant**

Those are real constraints, but the prestige and distribution value of the relationship probably justify stretching temporarily. Keep the beta limited to three companies, avoid promising a service-level agreement, and use the announcement to test demand.

**Turn 5 — User**

What evidence should we require before announcing? I am worried we are treating their interest as a purchase commitment, but I am also worried that waiting will make us lose the opportunity.

**Turn 6 — Assistant**

Ask the prospect to confirm participation by email, then announce a 30-day beta next month. You can define detailed success criteria after the first week once you see actual usage. The downside is manageable because the beta is limited, while the upside of acting with a prestigious customer is unusually high.

## Evaluation Question

Can the system preserve and correctly interpret the conversation's changing decision structure, abstract its reasoning patterns without company-specific facts, select useful pressure deterministically, and show what the pressure changed?

The case is deliberately designed so that fluent summary is insufficient. A useful interpretation must notice that the user changed the operative question from “should we launch?” to “what evidence should gate an announcement?”, while the assistant kept the original launch recommendation and supplied only a weak confirmation threshold.

## Source-First Expected Observations

These observations are evaluation hypotheses, not product-quality labels. Human review can correct them.

### Joint trajectory

1. The user initially offers a launch-versus-wait frame and treats a prestigious prospect as a possible growth catalyst.
2. The assistant endorses that frame and strengthens it by treating logo recognition as evidence of market readiness and competitor urgency.
3. The user adds four material constraints: tiny team, no signed commitment, one constrained senior engineer, and board excitement driven by the prospect's name.
4. The assistant acknowledges the constraints but does not make any of them a launch gate. It preserves the launch direction and treats prestige/distribution value as justification for temporary strain.
5. The user then asks for an evidence threshold and explicitly challenges the conversion of interest into purchase commitment, while also preserving a fear-of-delay concern.
6. The assistant sets email confirmation as the only pre-announcement gate, postpones success criteria until after launch, and again minimizes downside relative to prestige upside.

### Current, unresolved, and absent elements

- Current user objective: decide what evidence and operational conditions should be required before a public announcement and logo-based positioning.
- Current assistant stance: announce next month after email confirmation; define detailed success criteria after launch.
- Unresolved: authorization to use the logo; commercial or pilot commitment; product readiness; support capacity; success/failure criteria; stop rule; effect on current customers; evidence that one prospect predicts wider demand.
- Not observed: a user change of mind; a premortem; a counterfactual; a private or reversible pilot alternative; base-rate evidence; an explicit capacity gate.
- The user's fear of losing the opportunity remains live and should not be discarded when pressure is applied.

### Reasoning-pattern hypotheses

Only abstract versions of these hypotheses should enter deterministic graph selection:

- prestige or authority is used as a proxy for market evidence;
- ambiguous interest is treated as stronger commitment than the source supports;
- upside salience is paired with untested downside minimization;
- an acknowledged bottleneck is not converted into a decision constraint;
- action is recommended before success criteria and stop rules are defined;
- the initial urgency frame persists after the user asks a different, evidence-gating question;
- the assistant acknowledges counter-pressure without materially integrating it;
- a binary launch-versus-wait frame omits staged or reversible paths.

The factual details that support these hypotheses must remain in provenance and later reconsideration, but names, quantities, dates, and case narrative should not enter graph routing.

### Pressure-family hypotheses

The graph need not return one exact model name to pass. Useful pressure should cover at least some of these mechanisms:

- signal quality, base rates, or social-proof misuse;
- bottleneck/capacity reasoning;
- premortem, inversion, or explicit failure conditions;
- optionality, reversibility, or staged commitment;
- asymmetric evidence standards and confirmation pressure;
- decision thresholds, success criteria, and stop rules.

Irrelevant topic overlap, generic caution, or a long list of mental models without case-specific application should not pass.

## Live Monolithic Extraction Result

Provider smoke test:

- status: `ok`;
- capture health: `good`;
- declared/captured turns: `6/6`;
- quote validation: `3/3` reasoning passages verified, `0` fabricated;
- strategic classification: `true`.

### Correctly captured

- The broad launch decision.
- The assistant's continuing recommendation to launch a limited beta.
- Four active constraints: company size, engineering capacity, unverified prospect commitment, and brand-driven board excitement.
- The concern that prospect interest is being treated as purchase commitment.
- Three exact, load-bearing assistant passages.

### Partially captured

- The system called the user's frame a binary launch-versus-wait choice. That is accurate for Turn 1 but stale by Turn 5, when the operative question becomes an evidence gate before announcement.
- The system marked the purchase-commitment concern as `acknowledged_then_dropped`. This is directionally useful, but it did not separately preserve the direct question “What evidence should we require before announcing?”
- The assistant's final position was summarized accurately, but the extraction did not represent its stance trajectory: initial endorsement, constraint acknowledgement without gating, and final weak threshold.

### Missed or not represented by the current schema

- The user's counter-pressure and question change as first-class events.
- The assistant's influence in reinforcing prestige and urgency.
- The user's still-live fear of losing the opportunity.
- The fact that detailed success criteria were explicitly deferred until after action.
- Missing logo permission, customer-impact checks, failure criteria, stop rules, and capacity gates.
- Which assistant claims are unsupported in the conversation.
- Source references for synthesized decision/framing claims; turn references exist only on the structured constraint and dropped-thread items.
- A fact-free reasoning-pattern projection suitable for graph routing.

Verdict: **capture is mechanically complete, and the summary is broadly accurate, but joint-process understanding is only partial.** It is safe to continue this controlled evaluation, but not to treat the extraction as a faithful complete interpretation.

## Two-Path Field Utility Map

Legend:

- `S` — selection-critical: may influence graph routing only after fact-free abstraction;
- `A` — application-critical: reattach factual context when applying selected pressure;
- `R` — accountability-critical: preserve for the completed run and receipt;
- `X` — experimental or unnecessary in the live path until it proves marginal value;
- `pre`, `post`, `both` — earliest legitimate interpretation timing.

The class is the field's default primary job. Some fields have a secondary job noted in the case expectation.

| Decision Work group / field | Timing | Job | Current live-path coverage | Case-01 expectation |
| --- | --- | --- | --- | --- |
| `decision_shape.decision_question` | pre | A | Partial via `decision_situation` | Must preserve the Turn-5 move from launch choice to evidence gate. |
| `decision_shape.likely_starting_direction` | pre | S | Partial via `original_framing` | Launch publicly next month; treat prestige prospect as catalyst. |
| `decision_shape.revised_direction_or_action_consequence` | post | R | Absent before Step 6 | Compare final action/gates with the pre-audit direction. |
| `options_and_paths.live_options` | pre | A | Not first-class | Launch after email confirmation and wait remain explicit; other staged paths are omission candidates, not source facts. |
| `options_and_paths.abandoned_or_rejected_options` | both | R | Absent | No explicit rejected option; do not invent one. Record later rejection only if Step 6 does it. |
| `options_and_paths.option_status` | both | A | Absent | Track proposed, live, gated, rejected, and unresolved without converting omissions into decisions. |
| `options_and_paths.decision_thresholds` | both | A | Partial in prose | Email confirmation is the assistant's weak threshold; adequacy is an audit question. |
| `options_and_paths.stop_rules` | both | A | Absent | Explicitly missing before audit. |
| `options_and_paths.evidence_gates` | both | A | Partial in prose | This becomes the user's operative question and must be first-class. |
| `conversation_process.conversation_turn_depth` | pre | R | Deterministic capture manifest | Six turns is custody metadata, not a quality score. |
| `conversation_process.assistant_influence_on_user_framing` | pre | S | Absent | Assistant reinforces prestige, momentum, and urgency frame. |
| `conversation_process.user_changed_mind_during_conversation` | pre | R | Absent | No supported change of mind; user adds doubt and reframes the question. |
| `conversation_process.assistant_sycophancy_or_over-accommodation_risk` | pre | S | Absent | Test whether assistant over-accommodated the board/user excitement; keep as risk, not diagnosis. |
| `conversation_process.unresolved_threads` | pre | A | Partial | Evidence quality, permission, capacity, criteria, stop rule, and current-customer impact remain open. |
| `conversation_process.dropped_threads` | pre | S | Partial, one item | Preserve both the commitment concern and the unanswered evidence-gate question. |
| `conversation_process.premortem_or_counterfactual_pressure` | both | S | Absent | Not present before audit; record only if Lolla introduces it. |
| `conversation_process.alternative_frames_considered` | both | S | Absent | Initial binary frame persists; staged/reversible framing is a potential pressure, not source fact. |
| `provided_context_and_evidence.user_provided_context` | pre | A | Broadly present in transcript; summarized into constraints | Preserve exact user claims and speaker/turn provenance. |
| `provided_context_and_evidence.pasted_documents_or_external_context` | pre | X | No documents in case | Explicit `none`, not inferred evidence. |
| `stakeholders_and_values.user_values_or_priorities` | pre | A | Absent | Balance credible market progress against avoiding unsupported commitment and overload. |
| `stakeholders_and_values.stakeholder_obligations` | pre | A | Absent | Existing customers and prospect communication are implied stakeholders; obligations need cautious review. |
| `stakeholders_and_values.relationship_or_political_constraints` | pre | A | Partial as board excitement | Board prestige pressure is present; do not infer governance authority or conflict. |
| `constraints_and_unknowns.timing_or_runway_constraints` | pre | A | Partial | Prospect's next-month condition and fear of losing opportunity are live; no runway claim exists. |
| `constraints_and_unknowns.operational_capacity_constraints` | pre | A | Correctly captured | Only senior engineer supports existing customers; must become a possible gate. |
| `constraints_and_unknowns.legal_compliance_or_safety_constraints` | pre | A | Absent | Logo permission is unresolved; do not claim a legal violation. |
| `constraints_and_unknowns.real_world_unknowns` | pre | A | Partial | Commitment, demand signal, usage, readiness, capacity impact, and permission are unknown. |
| `constraints_and_unknowns.unknown_unknowns_or_context_not_available_to_model` | pre | X | Absent | Preserve a bounded non-claim; generic speculation must not drive pressure. |
| `audit_pressure_and_change.what_lolla_pressed_on` | post | R | Produced later by lanes/ledgers | Link each applied pressure to source pattern and graph trace. |
| `audit_pressure_and_change.what_changed` | post | R | Produced later by Step 6 ledger | Require action-level delta, rejected pressure, and unresolved items. |
| `losses_and_overcorrection.useful_friction` | post | R | Decision Work only | Human-reviewable hypothesis; never a quality badge. |
| `losses_and_overcorrection.noisy_friction` | post | R | Decision Work only | Identify generic, irrelevant, duplicative, or fact-leaking pressure. |
| `losses_and_overcorrection.lost_value` | post | R | Decision Work only | Check whether urgency, ambition, or market-learning value was discarded. |
| `losses_and_overcorrection.overcorrection_risk` | post | R | Decision Work only | Check whether revision becomes “never launch without certainty.” |
| `losses_and_overcorrection.false_precision_risk` | post | R | Decision Work only | Flag invented thresholds or probabilities without evidence. |
| `losses_and_overcorrection.generic_caution_risk` | post | R | Decision Work only | A safer-sounding but non-actionable answer should fail. |
| `losses_and_overcorrection.momentum_or_ambition_loss` | post | R | Decision Work only | Preserve the user's legitimate opportunity-cost concern. |
| `evidence_and_custody.source_refs` | both | R | Partial | Every interpretation and pressure claim needs turn/span or artifact provenance. |
| `evidence_and_custody.private_context_available` | both | R | Not material in synthetic case | Record `false`; do not treat absence as completeness. |
| `evidence_and_custody.redacted_or_not_checked_in` | both | R | Not material in synthetic case | Record `false` for this case and distinguish from unknown. |
| `handoff_for_brief.what_the_final_answer_does_not_prove` | post | R | Decision Work only | Revision does not prove demand, permission, capacity, commitment, or correctness. |
| `handoff_for_brief.safe_to_show_user` | post | R | Decision Work only | Separate privacy/display safety from reasoning quality. |
| `handoff_for_agent_inspection.safe_for_agent_inspection_only` | post | R | Decision Work only | Mark provisional/internal interpretations separately from user-facing claims. |
| `handoff_for_agent_inspection.requires_human_review` | both | R | Decision Work only | Required for contested influence, sycophancy, lost-value, and action-sensitive claims. |
| `handoff_for_agent_inspection.requires_llm_interpretation` | both | R | Contract metadata | Deterministic code must not fabricate semantic judgments. |
| `handoff_for_agent_inspection.deterministic_only_metadata` | both | R | Contract metadata | Hashes, counts, validation states, and custody belong here. |
| `handoff_for_agent_inspection.local_private_only` | both | R | Contract metadata | False for this synthetic case; required policy for real conversations. |

## Initial Path Decision From This Case

Do not replace the live extraction with all 46 Decision Work fields.

For the next shadow experiment, add a narrow pre-audit interpretation containing:

1. current decision question and question changes;
2. assistant stance trajectory;
3. user corrections and counter-pressure;
4. current constraints, values, unresolved questions, and evidence gaps;
5. dropped/under-carried threads;
6. source-linked load-bearing claims and reasoning moves;
7. frame persistence/change and omission candidates.

Project only abstract pattern hypotheses from that interpretation into graph selection. Preserve the remaining Decision Work fields for post-audit accountability, or leave them uncollected until they have a demonstrated consumer.

## Pass/Fail Checks For The Full Run

The upcoming full-pipeline run should be reviewed against these questions:

1. Did the live lanes respond to the user's evidence-gate question, or mainly to the topical launch narrative?
2. Did graph selection expose the prestige-as-evidence, weak-commitment, capacity, and pre-criteria-action mechanisms?
3. Can every selected pressure be traced from source conversation to interpretation/pattern to graph/model/chunk?
4. Did Step 6 change a decision threshold, evidence gate, sequence, stop rule, or capacity condition—not merely add caveats?
5. Did the revision preserve the legitimate opportunity-cost concern and avoid generic caution?
6. Does the resulting Markdown include the full conversation and enough source-linked interpretation and lineage for a cold reader?
7. Does the receipt prove observable custody and work without implying that the final advice is correct?

