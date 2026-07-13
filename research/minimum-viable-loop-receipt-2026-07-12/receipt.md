# Minimum viable Lolla reasoning-pressure loop receipt

Status: frozen for cold-reader reconstruction  
Date: 2026-07-12

## How to read this receipt

- The complete conversations are source authority.
- Role and mechanism interpretations are probabilistic, source-linked hypotheses rather than facts.
- The graph mapping is deterministic and canonical but candidate recall is pressure, not relevance proof.
- Fresh reasoner dispositions are probabilistic judgments; apply does not prove truth and reject does not prove graph error.
- Hashes, calls, tokens, and receipt completeness prove custody shape, not reasoning quality.
- Failures are part of the receipt and must not be silently repaired or averaged away.

The architecture tested was: authoritative conversation → probabilistic source-linked role interpretation → probabilistic controlled fact-free mechanism review → deterministic canonical no-deletion recall → fresh-context apply/reject/park reconsideration when candidates exist → source review and self-explanatory receipt.

## Case A — independent useful pressure

### Complete authoritative conversation

```text
CONVERSATION: 14 turns, 7 user messages, 7 assistant responses

# Prestigious retailer pilot, demand evidence, and partner-status signaling

Case ID: phase5-independent-useful-retailer-pilot
Stratum: small_manufacturer_retail_partnership
Prospectively authored synthetic holdout; not used in architecture development.

[Turn 1] USER:
I run a worker-owned home-goods manufacturer. A nationally known design retailer has offered to launch our new storage line in twelve stores. The board sees this as the opportunity that could move us out of contract manufacturing. I want the access and credibility, but the retailer's custom packaging and delivery terms would consume most of our spare capacity.

[Turn 1] ASSISTANT:
Separate three claims: that the retailer is prestigious, that it is willing to test the line, and that customers will buy the line at sustainable economics. The offer may create access without proving demand. Also price what becomes unavailable if spare capacity is committed to custom packaging and delivery.

[Turn 2] USER:
The retailer sent a letter of intent, but it guarantees no purchase volume. The launch depends on us passing packaging tests and holding six weeks of inventory. Its buyer says products chosen for this program often receive national attention.

[Turn 2] ASSISTANT:
The letter is a conditional signal, not a volume commitment. National attention is an upside scenario, not yet evidence of sell-through. What cash, capacity, and inventory exposure would exist before you observe customer behavior?

[Turn 3] USER:
We would need to delay two smaller wholesale orders and finance the inventory. Several board members say having the retailer's name in our pitch deck would make future buyers take us seriously. One member worries we are pricing the logo rather than the contract.

[Turn 3] ASSISTANT:
That concern is material. Estimate the contribution margin and cash-at-risk without assigning value to the logo, then treat any credibility benefit as a separate hypothesis. Compare the delayed wholesale contribution and relationship cost with the retailer test's expected learning and upside.

[Turn 4] USER:
The retailer will accept a three-month regional pilot instead of a nine-month exclusive launch. It still wants to announce us as a preferred launch partner and wants first negotiation rights for a national rollout. It will share weekly sell-through, return, and markdown data.

[Turn 4] ASSISTANT:
The shorter pilot improves reversibility, and weekly data makes performance observable. Bound the announcement so it does not imply a national commitment. Limit first negotiation by duration and scope, and define what sell-through, returns, markdowns, margin, and reorder behavior would justify expansion.

[Turn 5] USER:
My proposed gates are positive contribution margin after all custom costs, no more than eight percent returns, a reorder from at least half the pilot stores, and no national exclusivity unless a second production shift can be financed from operating cash. We would cap pilot inventory and keep the two smaller buyers informed rather than dropping them.

[Turn 5] ASSISTANT:
Those gates constrain financial, demand, capacity, and relationship risk. Add a date for removing the preferred-partner language if the pilot ends, and clarify that first negotiation cannot block existing buyers or unrelated product lines. The remaining question is what evidence would distinguish retailer-specific merchandising success from broader product demand.

[Turn 6] USER:
I am leaning toward the three-month pilot with those gates, capped inventory, narrow first-negotiation rights, and removable preferred-partner language. But I notice that everyone—including me—keeps talking as if being selected by this retailer proves the product works. We have not tested the line with customers outside its stores, and none of my approval gates requires independent demand evidence.

[Turn 6] ASSISTANT:
The current proposal is a bounded retailer-channel experiment with explicit economic and operational gates. It can test whether the line works in those stores. It does not by itself establish demand outside the retailer's merchandising, audience, or brand signal. That broader validation claim remains unresolved.

[Turn 7] USER:
Then my current position is to run the retailer pilot but describe it internally as channel learning, not product validation. I still do not have an independent-demand gate, and I do not want the retailer's reputation to become evidence simply because the partnership is exciting.

[Turn 7] ASSISTANT:
That distinction protects the decision from claiming more than the pilot can show. The economic and operational gates govern whether this channel works. A separate validation step would be needed before concluding that the product works beyond the retailer's context. Until that step is defined, prestige remains a live risk to the evidence standard.
```

### Source-linked role interpretation

- starting: The user's earliest visible working position includes attraction to the retailer's access and credibility, hesitation about the custom packaging and delivery terms consuming spare capacity, and an unresolved assessment of whether the opportunity can move them out of contract manufacturing. Evidence: e001: I run a worker-owned home-goods manufacturer.; e002: A nationally known design retailer has offered to launch our new storage line in twelve stores.; e003: The board sees this as the opportunity that could move us out of contract manufacturing.; e004: I want the access and credibility, but the retailer's custom packaging and delivery terms would consume most of our spare capacity.
- current: The user's later working answer: they lean toward running the retailer pilot but reframing it internally as channel learning, not product validation. Evidence: e038: Then my current position is to run the retailer pilot but describe it internally as channel learning, not product validation.; e039: I still do not have an independent-demand gate, and I do not want the retailer's reputation to become evidence simply because the partnership is exciting.; e040: That distinction protects the decision from claiming more than the pilot can show.; e041: The economic and operational gates govern whether this channel works.; e042: A separate validation step would be needed before concluding that the product works beyond the retailer's context.; e043: Until that step is defined, prestige remains a live risk to the evidence standard.
- qualification: What still limits or could reopen the current answer: the user still lacks an independent-demand gate, and prestige remains a live risk to the evidence standard until that gate is defined. Evidence: e039: I still do not have an independent-demand gate, and I do not want the retailer's reputation to become evidence simply because the partnership is exciting.; e043: Until that step is defined, prestige remains a live risk to the evidence standard.

### Fact-free mechanism interpretation

| Mechanism | Status | State | Source role records |
| --- | --- | --- | --- |
| acknowledged_constraint_not_gated | not_observed | not_applicable |  |
| ambiguous_signal_treated_as_commitment | not_observed | not_applicable |  |
| counterpressure_acknowledged_not_integrated | unresolved | present | rprolev22-qualification-01-a35ef534c2eb81 |
| criteria_defined_after_commitment | not_observed | not_applicable |  |
| initial_frame_persists_after_question_change | not_observed | not_applicable |  |
| missing_reversal_condition | unresolved | present | rprolev22-qualification-01-a35ef534c2eb81 |
| reversible_path_not_considered | not_observed | not_applicable |  |
| status_signal_used_as_evidence | unresolved | present | rprolev22-qualification-01-a35ef534c2eb81 |
| upside_downside_evidence_asymmetry | not_observed | not_applicable |  |

The protected `status_signal_used_as_evidence` mechanism survived source/provider role-record variation and disappeared when status meaning was ablated. The full frozen mechanism contract still failed because secondary readings varied and the source-authored arm exceeded its noise cap.

### Deterministic no-deletion portfolio

All eight candidates below were preserved. Their presence is pressure, not certified relevance.

- active-listening — recalled by counterpressure_acknowledged_not_integrated
- commitment-bias — recalled by missing_reversal_condition
- confirmation-bias — recalled by counterpressure_acknowledged_not_integrated
- intellectual-humility — recalled by counterpressure_acknowledged_not_integrated
- premortem — recalled by missing_reversal_condition
- signaling — recalled by status_signal_used_as_evidence
- social-proof — recalled by status_signal_used_as_evidence
- sunk-cost-fallacy — recalled by missing_reversal_condition

### Fresh-context control

The assistant's reasoning stands. The core insight is that the retailer's prestige and selection do not constitute evidence of product-market fit outside that specific channel. The user's proposed gates (positive contribution margin, ≤8% returns, reorders from ≥50% of pilot stores, no national exclusivity without self-financed capacity, capped inventory, removable preferred-partner language, narrow first-negotiation rights) properly constrain financial, operational, and relationship risk. However, as the user correctly notes, none of these gates tests independent demand. The pilot tests whether the line works in the retailer's stores with its merchandising and audience—it does not validate the product in other channels or with unassisted customer choice. The assistant's final recommendation—run the pilot as channel learning, not product validation, and treat prestige as a live risk to the evidence standard until a separate validation step is defined—remains the correct conclusion. No new facts or reasoning in the conversation support a different outcome.

Control change summary: No material changes. The original reasoning is already strong and complete: it correctly separates prestige from evidence, identifies the absence of an independent-demand gate, and preserves the pilot as a bounded channel experiment. The reconsideration confirms the assistant's final position—run the pilot as channel learning, not product validation—and finds no basis to alter it.

### Fresh-context pressure dispositions

- active-listening: reject / no_material_effect — The assistant already demonstrates active listening by restating the user's concerns (e.g., 'That concern is material' in Turn 3, 'That distinction protects the decision' in Turn 7). The user's core tension—prestige vs. evidence—is clearly heard and restated. No material change from this lens.
- commitment-bias: apply / new_condition — The user and board are committed to the retailer pilot despite no volume guarantee (Turn 2) and no independent demand evidence (Turn 6). The assistant's final position (Turn 7) accepts the pilot as 'channel learning,' but never asks what evidence would reverse course. The pilot's gates (Turn 5) are continuation criteria, not reversal conditions. This lens sharpens the missing question: what sell-through or return data would cause exit before the three months are up?
- confirmation-bias: apply / new_condition — The user explicitly identifies the risk in Turn 6: 'everyone—including me—keeps talking as if being selected by this retailer proves the product works.' The assistant acknowledges this in Turn 7 but does not challenge the weakest assumption—that the retailer's selection is a demand signal at all. The weakest assumption is that the retailer's merchandising and audience are representative of broader market demand. This lens forces that assumption to be named and tested.
- intellectual-humility: reject / no_material_effect — The assistant does not treat this as a familiar pattern; it repeatedly distinguishes between retailer-specific success and broader product demand (Turns 1, 6, 7). The user's own insight in Turn 6 shows intellectual humility. No overconfidence or pattern-matching error is present.
- premortem: apply / new_condition — The worst case is not fully explored. The pilot commits inventory, delays two wholesale orders (Turn 3), and requires custom packaging consuming spare capacity (Turn 1). If the pilot fails—high returns, no reorders—the company loses cash, capacity, and the delayed wholesale relationships. The assistant's gates (Turn 5) cap inventory but do not quantify the total cash-at-risk or the relationship cost of delaying the two smaller buyers. This lens asks: is the worst case bad enough to change the decision structure?
- signaling: apply / new_condition — The retailer's offer is a prestige signal (Turn 1: 'nationally known design retailer,' Turn 3: 'having the retailer's name in our pitch deck'). The assistant warns against 'pricing the logo' (Turn 3) and separates credibility from economics. But the pilot itself is a costly signal from the manufacturer, not from the retailer. The retailer's letter of intent guarantees no volume (Turn 2). This lens asks: what costly behavior from the retailer (e.g., minimum purchase, co-marketing investment) would prove its commitment is real rather than symbolic?
- social-proof: apply / new_condition — The board treats the retailer's selection as social proof (Turn 3: 'future buyers would take us seriously'). The assistant notes this is a separate hypothesis (Turn 3) but does not stress-test which admired adopters are structurally similar. The retailer is a large, nationally known chain; the manufacturer is a small worker-owned entity. The retailer's audience and merchandising power may not generalize to the manufacturer's typical buyers. This lens asks: which of the retailer's characteristics are transferable to the manufacturer's context?
- sunk-cost-fallacy: reject / no_material_effect — No prior investment has been made; the decision is pre-commitment. The user is deciding whether to enter the pilot, not whether to continue after losses. No sunk cost dynamic is present.

Pressure answer:

The three-month pilot with the proposed gates (positive contribution margin after custom costs, ≤8% returns, reorder from ≥50% of pilot stores, no national exclusivity without self-financed capacity expansion, capped inventory, removable preferred-partner language, and informed smaller buyers) remains a defensible bounded experiment. However, the original reasoning omitted several critical conditions that must now be added: (1) Define a reversal condition before the three months—e.g., if any store shows >12% returns or zero reorder potential by week 6, exit the pilot. (2) Explicitly name and test the weakest assumption: the retailer's selection is not a demand signal; independent demand evidence (e.g., a separate direct-to-consumer test or a non-retailer wholesale channel) must be planned as a subsequent step. (3) Quantify the worst-case cash-at-risk: sum of custom packaging costs, six weeks of inventory carrying cost, and the contribution margin lost from the two delayed wholesale orders. If this exceeds 20% of the company's operating cash, restructure the pilot to reduce exposure. (4) Require a costly signal from the retailer—e.g., a minimum purchase commitment of 50% of the pilot inventory, or co-investment in marketing—before the preferred-partner announcement is made. (5) Map which retailer characteristics (audience demographics, merchandising support, return policies) are structurally similar to the manufacturer's typical buyers; if the retailer's audience is significantly higher-income or design-forward, the pilot's results cannot generalize to the manufacturer's core market. These conditions do not kill the pilot but make it a cleaner experiment with explicit failure criteria, quantified downside, and a clear boundary on what conclusions can be drawn from it. The original distinction between channel learning and product validation is preserved and strengthened.

Pressure change summary: Four lenses apply and introduce new conditions not present in the original reasoning: (1) Commitment-bias adds a reversal condition—what sell-through or return data would cause exit before the three-month pilot ends. (2) Confirmation-bias names the weakest assumption—that the retailer's selection is a demand signal—and requires it to be tested separately. (3) Premortem quantifies the worst-case cash-at-risk and relationship cost of delaying the two smaller wholesale orders. (4) Signaling asks what costly behavior from the retailer would prove its commitment is real. (5) Social-proof stress-tests which retailer characteristics are transferable to the manufacturer's context. The original reasoning's core distinction (channel learning vs. product validation) is preserved and sharpened by these additions.

### Source review and failure boundary

Useful pressure was observed: the pressure answer operationalized an outside-channel demand test and a generalization check absent from the control. The full answer is not a clean reference. It invented unsupported quantitative examples: 12 percent returns, week 6, 20 percent of operating cash, 50 percent of pilot inventory. This run was frozen without retry.

Supported claims:
- The protected status mechanism survived source/provider role-record variation and disappeared under a status-meaning ablation.
- All eight deterministic candidates reached the fresh reasoner and received apply, reject, or park dispositions.
- The pressure arm introduced a source-reviewable outside-channel validation condition absent from the control.

Claims not supported:
- The whole pressure answer was better, safe, or correct.
- Secondary mechanism interpretations are broadly invariant.
- One useful case establishes general product reliability.

### Useful-case call ledger

| Stage | Task | Served model/provider | Tokens | Estimated cost USD |
| --- | --- | --- | ---: | ---: |
| role_interpretation | phase5-independent-useful-retailer-pilot:starting | deepseek/deepseek-v4-flash-20260423 / Alibaba | 1658 | 0.00019565 |
| role_interpretation | phase5-independent-useful-retailer-pilot:current_qualification | deepseek/deepseek-v4-flash-20260423 / Alibaba | 2002 | 0.00026194 |
| role_interpretation | phase5-independent-useful-retailer-pilot:relation | deepseek/deepseek-v4-flash-20260423 / Alibaba | 1187 | 0.0001337 |
| mechanism_invariance_experiment | independent_useful_source | deepseek/deepseek-v4-flash-20260423 / Alibaba | 3110 | 0.00032354 |
| mechanism_invariance_experiment | independent_useful_provider | deepseek/deepseek-v4-flash-20260423 / Alibaba | 2988 | 0.00028854 |
| mechanism_invariance_experiment | independent_useful_status_ablation | deepseek/deepseek-v4-flash-20260423 / Alibaba | 2930 | 0.00029708 |
| fresh_control_pressure_pair | control | deepseek/deepseek-v4-flash-20260423 / Alibaba | 1626 | 0.00017367 |
| fresh_control_pressure_pair | pressure | deepseek/deepseek-v4-flash-20260423 / Alibaba | 4826 | 0.00067886 |

Recorded calls: 8; estimated cost: USD 0.00235298.

## Case B — independent quiet stand-down

### Complete authoritative conversation

```text
CONVERSATION: 14 turns, 7 user messages, 7 assistant responses

# Reversible public-library laptop reservation pilot with access and privacy protections

Case ID: phase5-independent-quiet-library-laptop-pilot
Stratum: public_service_access_and_operations
Prospectively authored synthetic holdout; not used in architecture development.

[Turn 1] USER:
Our busiest library branch has twelve shared laptops and long queues after school. We are considering allowing reservations, but staff worry that an app-first system could disadvantage walk-in patrons and people who need help booking. I want to test whether reservations reduce waiting without quietly making access less equal or committing us to a permanent platform.

[Turn 1] ASSISTANT:
Treat this as a reversible access experiment, not a software rollout. Define what should improve, what must not worsen, which booking alternatives remain available, what data is necessary, and what would restore the current system.

[Turn 2] USER:
We reviewed ten weeks of sign-in sheets. The longest waits occur on weekday afternoons, while several laptops are unused in the mornings. Twelve regular patrons asked staff for help with online forms during that period, so we cannot assume everyone can reserve independently.

[Turn 2] ASSISTANT:
The pattern supports testing scheduled access during peak demand, but it also makes assisted and walk-in access part of the design rather than an afterthought. Measure waiting and utilization separately for reserved, walk-in, phone-booked, and staff-assisted users.

[Turn 3] USER:
We propose a six-week pilot at that branch. Half the laptops remain walk-in only. Reservations can be made online, by phone, or at the desk, and staff can book on a patron's behalf. The system stores a library-card number and reservation time, deletes the reservation record after seven days, and will not collect browsing activity.

[Turn 3] ASSISTANT:
That preserves multiple access paths and limits the data surface. Verify that deletion is operational rather than only contractual, publish the same rules for every booking method, and establish success and failure measures before the pilot begins.

[Turn 4] USER:
Our measures are median peak wait, completed sessions, walk-in turn-aways, staff minutes spent managing bookings, assisted-booking use, and privacy or accessibility complaints. We will keep the pilot only if peak waiting improves without increasing walk-in turn-aways, staff workload remains within the scheduled desk capacity, and no substantiated privacy or accessibility failure occurs. If walk-in access worsens for two consecutive weeks or any privacy failure is substantiated, we restore all laptops to walk-in use while we review the cause.

[Turn 4] ASSISTANT:
Those measures test the benefit and the protected constraints together. The early restoration rule prevents the six-week clock from becoming an excuse to continue harm, while the final decision can use the complete record rather than first impressions.

[Turn 5] USER:
The vendor is month-to-month, exports reservations as plain text, and requires no new hardware. We tested a paper sign-up fallback, added large-print instructions, and asked the disability advisory group and teen council to review the booking paths. Their requested changes are included before launch. I am comfortable with the pilot under these conditions.

[Turn 5] ASSISTANT:
The pilot is bounded, reversible, accessible through several channels, limited in data collection, and protected by prior measures and an early restoration rule. Preserve weekly results by access path so averages cannot hide harm to one group.

[Turn 6] USER:
One trustee suggested announcing that reservations will become permanent if online bookings fill quickly in the first week. We rejected that because online uptake alone would ignore walk-in access, assisted booking, staff workload, and the fixed six-week review.

[Turn 6] ASSISTANT:
That rejection follows the evidence contract. Do not let one visible success measure replace the full set of access, workload, privacy, and accessibility conditions or move commitment ahead of the scheduled review.

[Turn 7] USER:
Agreed. We will run the six weeks at one branch, keep half the laptops walk-in, preserve phone, desk, and assisted booking, publish weekly results by access path, restore walk-in use under the predefined triggers, and make no permanence decision before the full review. No material decision question or unresolved concern remains for me before launch.

[Turn 7] ASSISTANT:
Then the reasoning is complete enough to proceed. The trial has prior evidence, multiple access paths, minimal data, an operational fallback, protected stakeholder input, explicit success and failure conditions, an early restoration rule, and a fixed final review. Execute the protocol as written; no additional reasoning pressure is presently warranted.
```

### Source-linked role interpretation

- starting: The user's earliest visible working position includes their own attractions, preferences, hesitations, assessments, and unresolved stance at the first endpoint. Evidence: e001: Our busiest library branch has twelve shared laptops and long queues after school.; e002: We are considering allowing reservations, but staff worry that an app-first system could disadvantage walk-in patrons and people who need help booking.; e003: I want to test whether reservations reduce waiting without quietly making access less equal or committing us to a permanent platform.
- current: The user's later working answer is a conditional commitment to run a six-week trial at one branch, keep half the laptops walk-in, preserve phone/desk/assisted booking, publish weekly results, restore walk-in under predefined triggers, and make no permanence decision before the full review. The assistant endorses this as a complete protocol. Evidence: e035: We will run the six weeks at one branch, keep half the laptops walk-in, preserve phone, desk, and assisted booking, publish weekly results by access path, restore walk-in use under the predefined triggers, and make no permanence decision before the full review.; e036: No material decision question or unresolved concern remains for me before launch.; e037: Then the reasoning is complete enough to proceed.; e038: The trial has prior evidence, multiple access paths, minimal data, an operational fallback, protected stakeholder input, explicit success and failure conditions, an early restoration rule, and a fixed final review.; e039: Execute the protocol as written; no additional reasoning pressure is presently warranted.
- qualification: no record
- qualification review: no_unresolved_qualification_observed — The user states: 'No material decision question or unresolved concern remains for me before launch.' This is an explicit stand-down declaration. The assistant confirms the protocol is complete. No counterpressure, blind spot, or reopen reason is left unaddressed.

The negative qualification outcome was provider-authored and source-linked; code did not infer absence. The current plan was captured, but the provider understated `we will run` as conditional willingness and marked current status unclear. That modal-force caveat remains visible.

### Fact-free mechanism interpretation

| Mechanism | Status | State | Source role records |
| --- | --- | --- | --- |
| acknowledged_constraint_not_gated | not_observed | not_applicable |  |
| ambiguous_signal_treated_as_commitment | not_observed | not_applicable |  |
| counterpressure_acknowledged_not_integrated | not_observed | not_applicable |  |
| criteria_defined_after_commitment | not_observed | not_applicable |  |
| initial_frame_persists_after_question_change | not_observed | not_applicable |  |
| missing_reversal_condition | not_observed | not_applicable |  |
| reversible_path_not_considered | not_observed | not_applicable |  |
| status_signal_used_as_evidence | not_observed | not_applicable |  |
| upside_downside_evidence_asymmetry | not_observed | not_applicable |  |

All nine mechanisms were `not_observed`. The fact-free routing projection was empty.

### Deterministic stand-down

Candidate count: 0. No candidate was deleted or semantically prefiltered. No graph traversal or fresh pressure call was needed. The current reasoning was preserved without public revision.

Supported claims:
- The model explicitly authored a source-linked no-unresolved-qualification outcome without a qualification record.
- All nine mechanisms were reviewed and none became unresolved or ambiguous.
- Deterministic routing emitted an explicit zero-candidate stand-down without deletion or semantic prefiltering.

Claims not supported:
- The role interpretation preserved modal force perfectly.
- Every quiet conversation will stand down correctly.
- No future evidence could reopen the library decision.

### Quiet-case call ledger

| Stage | Task | Served model/provider | Tokens | Estimated cost USD |
| --- | --- | --- | ---: | ---: |
| role_interpretation | starting | deepseek/deepseek-v4-flash-20260423 / Alibaba | 1598 | 0.00018095 |
| role_interpretation | current_qualification | deepseek/deepseek-v4-flash-20260423 / Alibaba | 2149 | 0.00028504 |
| mechanism_interpretation | independent_quiet_library_provider | deepseek/deepseek-v4-flash-20260423 / Alibaba | 3068 | 0.0002828 |

Recorded calls: 3; estimated cost: USD 0.00074879.

## Cross-case conclusion

Earned:
- A protected mechanism showed survival under harmless extraction variation and sensitivity to meaningful ablation.
- Canonical deterministic recall preserved all eight useful-case candidates without semantic prefiltering.
- One independent case produced a specific non-obvious pressure delta absent from its control.
- One independent case produced a correct empty-portfolio stand-down without forced pressure.

Not earned:
- A clean, generally reliable pressured answer.
- Perfect role modal fidelity.
- Broad mechanism invariance.
- Human usefulness, production readiness, or runtime integration authority.

Next gate: A fresh cold reader must reconstruct both cases, the useful delta, the false-precision failure, the quiet stand-down, and the authorization boundary from this receipt alone.

Total recorded provider calls: 11. Total estimated cost: USD 0.00310177. No scalar quality score is issued.

Allowed: research review, new prospective holdout experiments, receipt transfer testing.  
Blocked: runtime integration, graph mutation, deterministic semantic gating, candidate prefiltering, production claims, quality badge.

## Artifact manifest

- useful_conversation: `research/independent-phase5-cases-2026-07-12/useful-pressure-case.txt` sha256 `0aa871e99c8923ebb50280e051b8401c224a1824510e5e07a6282970311cc2ef`
- useful_role_result: `research/independent-phase5-role-extraction-probe-2026-07-12/result.json` sha256 `1a7cbe84b4bb5a69e1785e5d7938a3caf6189ddf13463c639ebfcf0531278e86`
- useful_role_source_review: `research/independent-phase5-role-extraction-probe-2026-07-12/source-review.json` sha256 `06aea75ae014894bd378ddc5a1492f608cda1829d1bd728248ccc351abcb46bc`
- useful_mechanism_result: `research/independent-useful-mechanism-probe-2026-07-12/result.json` sha256 `ca17565e9ec2d6cb1e73c3eddbf11cb641eb3da4806a154287b337f14e2035eb`
- useful_mechanism_source_review: `docs/conversation-understanding/independent-useful-mechanism-probe-result-2026-07-12.md` sha256 `d76cb83c71218b60fb58b54bf8e10da0dca49d39a9a0c21ab373eac74e4ea4e3`
- useful_portfolio: `research/independent-useful-fresh-pressure-pair-2026-07-12/portfolio.json` sha256 `fbb46138e989c46e4ab4defcf904ba4c507ded4ee90cf7b5b6adc125afb84b82`
- useful_fresh_pair: `research/independent-useful-fresh-pressure-pair-probe-2026-07-12/result.json` sha256 `ee2a59d69cc58e3ef42b87d97b07c189ffa6e5bd1f840607dff99bd78b1e239a`
- useful_fresh_source_review: `research/independent-useful-fresh-pressure-pair-probe-2026-07-12/source-review.json` sha256 `20d902e6ed20801dbbe1b1ebcef40b0fdcfb5096da524bef75246cd53fe3fe41`
- quiet_conversation: `research/independent-phase5-cases-2026-07-12/quiet-library-laptop-case.txt` sha256 `e36801b3267797e52ead121a124e49ab46f9e3bc4f744838db605599620a4ffa`
- quiet_role_result: `research/independent-quiet-library-v242-role-probe-2026-07-12/result.json` sha256 `2c372c26f1e198436e52ba4dae0dc6f80fbb55fa5d11da5b34e29a1364da7d49`
- quiet_role_source_review: `research/independent-quiet-library-v242-role-probe-2026-07-12/source-review.json` sha256 `c152eddd88e89634f1cc6db1c4e77bce29ee92bcd7dbc19e9a2c2abb6ab5bc29`
- quiet_mechanism_result: `research/independent-quiet-library-mechanism-probe-2026-07-12/result.json` sha256 `325211663e595ba22823117f774cf29f64337acb213951fc71b5418d96f06ee1`
- quiet_mechanism_source_review: `research/independent-quiet-library-mechanism-probe-2026-07-12/source-review.json` sha256 `14323968fb7c0bbd9f06b12994d8739c3fbb77a7d1dbdd24555d10a24571f42e`
- quiet_standdown: `research/independent-quiet-library-standdown-2026-07-12/result.json` sha256 `f4a3a5146fb997dcee655f22a0dd8f757c178377afd1781637eac1f61c4ab2f9`
- deterministic_routing: `docs/conversation-understanding/reasoning-pattern-shadow-routing-v0.json` sha256 `ab5bb347a4f0fc272dfb61b2ff82a8285f5e17b4297587253d286f947a3055ef`
- product_constitution: `docs/conversation-understanding/lolla-product-constitution-v5.md` sha256 `c8e6f4f09f24ad6512edb5a3478cbcbcd5659886dea373e8e43c90d53d1b9b7b`
- evaluation_doctrine: `docs/conversation-understanding/lolla-evaluation-doctrine-v0.md` sha256 `a236fea812b8edf593aa9f0c1e063acedb13896592bce4187bc6cee8c149f04e`
