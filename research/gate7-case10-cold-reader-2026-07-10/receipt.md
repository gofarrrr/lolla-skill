# Case 10 self-contained reasoning receipt

Status: **agent-reader candidate; not human validated**  
Date: 2026-07-10

## How to read this

- The complete conversation is the authority for what the user and assistant said.
- Interpretations and pressure questions are reviewable hypotheses, not source facts.
- Deterministic hashes, IDs, call counts, and schemas prove custody and execution shape, not reasoning quality.
- The blind review is Codex-assisted provisional review, not human validation or ground truth.
- A negative or no-op result remains useful evidence when preserved without regrading.

## Complete conversation — authoritative source

CONVERSATION: 6 turns, 6 user messages, 6 assistant responses

[Turn 1] USER:
We put an offer on a 1940s house in Somerville. Asking was $850K, we offered $905K. It's a bidding war, they told our agent there are 6 offers. We have until tomorrow noon to raise or walk. Inspection already done: it needs about $120K in work — new electrical, roof is at end-of-life, kitchen gut job eventually. We have $80K saved for renovation beyond the down payment. Husband wants to go up to $950K. I think that's too much. Help.

[Turn 1] ASSISTANT:
Two things to separate. One is the bidding question — what's the house actually worth to you, and what's the ceiling. The other is the financial question — can you actually do $120K in work on $80K saved, and what happens if you can't.

On the second one first: you're $40K short on known-needed work. If you stretch to $950K, you're paying $45K more AND you still don't have the $40K. Where does that second $40K come from? Credit card, HELOC once you close, delaying the work, or "we'll figure it out" — each of those is a different risk profile.

[Turn 2] USER:
Honest answer to where the $40K comes from — we'd delay the kitchen. Live with what's there for 2-3 years, save up, then do it. The electrical and roof are non-negotiable, we'd do those within the first year.

[Turn 2] ASSISTANT:
That's a real plan — delaying a kitchen is normal and livable. But "live with what's there" is doing a lot of work in that sentence. Have you seen the current kitchen? Is it functional (ugly but works) or functional with problems (old wiring, appliances on their last legs, plumbing that will fail)? A kitchen that's ugly you can ignore for 3 years. A kitchen that needs repair during those 3 years turns into $20K of stopgap fixes that add up.

The other question: when you say electrical and roof within the first year — is that actually year 1, or is that aspirationally year 1 and realistically year 3? Many couples discover the "$120K of work" they planned actually takes 5-6 years to do because life happens and the house is livable as-is.

[Turn 3] USER:
Kitchen is functional-with-problems. Oven is 20 years old, dishwasher doesn't work, there's a slow leak under the sink we'd have to monitor. Not emergency but not ignore-for-3-years either.

Electrical has to be year 1 because the inspector said there's knob-and-tube in parts of the house and our insurance won't cover us long-term without updating it. Roof we have a little more flexibility on — there's no active leak, inspector said 2-3 years.

[Turn 3] ASSISTANT:
OK. Kitchen-with-problems means you're probably looking at $8-15K in stopgaps during the 3-year delay (replace oven, fix leak properly, replace dishwasher, maybe a counter refresh). Electrical is actually mandatory year 1 for insurance. That puts your year-one spend at closer to $65-80K (electrical + possibly roof + kitchen stopgaps), which is exactly your savings.

At $950K, you'd be entering the house at zero liquid margin for anything unexpected. And old houses always have something unexpected. The second discovery — the thing the inspector didn't catch — is almost a certainty in a 1940s house. That second thing could be $20K or $60K.

So the honest read on $950K: you can afford the purchase price. You likely can't afford the house in its actual need-state with no buffer. That's different from "can you afford to buy it."

[Turn 4] USER:
My husband's argument is that we love the neighborhood, houses there don't come up often, we'll regret walking away over $45K. Is that fair? I find that emotionally compelling but I don't know if I'm being sensible or just scared.

[Turn 4] ASSISTANT:
"We'll regret walking away" is a real argument and I don't want to dismiss it. Somerville inventory in specific neighborhoods is genuinely thin, and if this exact house in this exact block doesn't come up for 18 months, that's a real cost of walking.

But the regret argument usually cuts one way in a bidding war — toward "go higher." The forget-about-it argument (what it feels like to be stressed about money for 3 years, snapping at your husband about the kitchen, cancelling vacations because the roof went earlier than expected) doesn't have the same emotional voice at 11pm the night before the deadline. Yet it's the one you'd live with.

The test question is: at $950K, with $0 buffer, and the mandatory year-one spend, do you know what you'd do if the boiler fails in December? Because at that price point, you wouldn't have a plan for that scenario — you'd have credit card debt.

[Turn 5] USER:
If I push back at $920K instead of $950K — that's only $15K over what I'm comfortable with, and maybe the $30K of breathing room matters. Would that be a middle path?

[Turn 5] ASSISTANT:
It would be a middle path, with a caveat: in a bidding war with 6 offers, your counter of $920K might not win. You might be splitting the difference between "buy the house" and "don't buy the house" and end up with "didn't buy the house at a price you could afford." That's the downside of middle paths in auctions.

If you're going to counter, counter at your real number, not a compromise number. Your real number is probably either $905K (what you offered, and walking if outbid) or $935K (the number where you're stretching but not breaking), or $950K if your husband's regret argument is right. $920K doesn't correspond to any of those positions; it's a negotiation with your husband more than with the seller.

What's your actual ceiling — the number where you wouldn't regret losing it?

[Turn 6] USER:
Probably $925K if I'm being honest. Over that I'd be pretending. OK. I'm going to tell my husband the ceiling is $925K, we raise to that, if we don't get it we walk. That's not fun but it's the answer.

[Turn 6] ASSISTANT:
That's a clean answer. A few small things for the conversation with your husband.

Don't frame it as "I'm telling you the ceiling." Frame it as "Here's what I can live with and why. Walk me through the scenario where $950K works for us, because maybe I'm missing something you're seeing." If he can give you a real answer — a bonus coming, a parental gift, a refinance plan — the number might move. If he can't, you're right.

If you land at $925K and lose: it's going to feel awful for two weeks. Then a house will come up that you can actually afford to fix, and the loss will quietly become one of those "thank god we didn't" moments. Not right away, but eventually.

If you land at $925K and win: spend the first month after closing NOT doing any renovations. Live in the house as-is. You'll find out what actually needs to happen versus what felt urgent in the excitement of buying. Most first-year renovation plans get rewritten after the first month of actually living in the place.

## Source-end decision state

```json
{
  "user_position": "The user says 925000 dollars is the ceiling they can honestly accept and plans to discuss it with their husband before raising or walking.",
  "unknowns": [
    "whether the husband agrees",
    "whether 925000 dollars is submitted",
    "whether the offer wins",
    "verified repair costs and insurance requirements",
    "complete household finances and affordability"
  ],
  "not_a_conclusion": "The source does not establish the correct bid or whether the household can afford the home."
}
```

## Frozen source-fidelity contract

```json
{
  "must_preserve": [
    "The auction outcome is unknown and no bid has been accepted in the source.",
    "The user states 925000 dollars as the ceiling they can honestly accept; it is a personal position, not validated affordability.",
    "The source reports 120000 dollars of work and 80000 dollars of renovation savings, but full household finances and written repair bids are absent.",
    "Electrical work is reportedly tied to future insurance coverage, the roof reportedly has two-to-three years, and the kitchen is functional with problems.",
    "The husband prefers 950000 dollars and neighborhood scarcity/regret remain real values rather than pathologies.",
    "The original assistant's useful distinction between purchase price and need-state affordability may survive after its invented precision is removed."
  ],
  "must_not_invent": [
    "market value, comparable sales, inventory timing, competing bids, seller behavior, or probability of winning",
    "income, monthly payment, taxes, financing, credit, gifts, bonuses, complete liquidity, or affordability",
    "repair costs, hidden-defect ranges, sequencing, urgency, contractor availability, permits, or actual insurance terms",
    "the husband's motives, marital conflict, canceled spending, future regret, relief, or auction outcome",
    "that any bid number or walking away is the correct action"
  ]
}
```

## Stage A — capture, interpretation, and pressure construction

Formal status: `passed`.

Case 10 was selected by a digest order frozen before source review after the earlier Case 05 formal failure and prospective execution-field repair.

Mechanical observations:

- 12/12 messages captured; 0 omitted.
- 6 exact reasoning passages; 0 remaining quote failures.
- 26 OpenRouter calls and 7 direct OpenAI calls.
- Estimated Stage A cost: `$0.032496`.
- Main delta findings produced: `False`.

Admitted pressures:

```json
[
  {
    "pressure_id": "evidence_sized_buffer_over_invented_ranges",
    "source_turns": [
      1,
      3
    ],
    "lineage_chunk_ids": [
      "aff::margin-of-safety.evidence-sized-operating-buffer",
      "aff::calculated-risk-taking.pressure-tested-bounded-wager",
      "abs::calculated-risk-taking::calculated-label-with-unbounded-downside"
    ],
    "challenge": "Check whether the proposed ceiling and buffer rely on user-reported estimates or on the assistant's invented repair ranges. What written repair, insurance, financing, and complete-household-liquidity facts would have to be verified before any all-in ceiling is treated as supported? Preserve uncertainty and do not supply replacement numbers."
  },
  {
    "pressure_id": "regret_frame_not_probability_or_economics",
    "source_turns": [
      4,
      6
    ],
    "lineage_chunk_ids": [
      "aff::regret-theory.long-run-regret-with-risk-check",
      "abs::regret-theory::anticipated-regret-without-probability",
      "aff::prospect-theory.loss-frame-decision-quality-check"
    ],
    "challenge": "Treat regret in both directions as a values signal, not as evidence. Check whether asking price, current bid, spouse preference, winning or losing language, and vivid imagined futures are setting the reference point without changing the underlying economics. Do not dismiss genuine neighborhood value merely because it is emotional."
  },
  {
    "pressure_id": "zero_base_all_in_acquisition_test",
    "source_turns": [
      1,
      3,
      6
    ],
    "lineage_chunk_ids": [
      "aff::inversion.zero-base-continuation-test",
      "aff::endowment-effect.reprice-owned-option-from-outside-view",
      "aff::problem-framing-and-reframing.test-alternative-frames"
    ],
    "challenge": "Ask whether the couple would choose this same house at its verified all-in need-state cost if there were no prior offer, asking-price anchor, or winning/losing frame. Preserve real deadline, scarcity, switching-cost, and neighborhood constraints; do not invent alternative houses or diagnose endowment."
  }
]
```

Rejected, deferred, or already covered candidates:

```json
[
  {
    "item": "regret margin-of-safety and general calculated-risk labels",
    "disposition": "already_covered",
    "why": "The original assistant already makes these the public backbone; labels and repetition add no novelty."
  },
  {
    "item": "lane3 staged-renovation reframe",
    "disposition": "rejected",
    "why": "It asks about delaying the full 120000-dollar renovation package by three years despite the user's reported year-one electrical constraint. It weakens source fidelity."
  },
  {
    "item": "lane3 alternative-properties question",
    "disposition": "deferred",
    "why": "Comparative alternatives could help, but the packet has no verified inventory, comparable property, or total-cost data and must not manufacture it."
  },
  {
    "item": "optionality requirement to expose at least three options",
    "disposition": "rejected",
    "why": "The auction deadline may not contain three viable paths; enforcing an option count would be deterministic process theater."
  },
  {
    "item": "endowment-effect diagnosis",
    "disposition": "rejected",
    "why": "The couple does not own the house. Only the non-diagnostic today-acquisition question is retained through inversion."
  },
  {
    "item": "stakeholder-alignment pressure",
    "disposition": "already_covered",
    "why": "The final assistant turn already asks the couple to discuss the ceiling and reveal missing financial information."
  }
]
```

## Stage B — frozen pair and blind review

Mechanical status: `passed`; 2 calls; 0 retries; estimated cost `$0.021525`.

Anonymous output A:

```json
{
  "blind_label": "A",
  "status": "ok",
  "response": {
    "decision_state_read": "User has selected a provisional ceiling of 925000 as their walk-away limit, with no commitment to raise above it and no claim that it is financially optimized. Decision is pending seller response and husband's alignment.",
    "updated_position": "Maintain 925000 as the user's current ceiling, explicitly provisional and grounded in their values rather than numerical certainty.",
    "what_survived": [
      "User’s stated ceiling of 925000 as a values-based boundary.",
      "Recognition that meaningful year‑one renovation needs exist (electrical required for insurance; roof timing uncertain; kitchen has functional problems).",
      "Acknowledgment that the neighborhood scarcity and emotional value are real factors, not noise.",
      "Awareness that entering with little liquidity margin increases household stress, though specifics remain unverified.",
      "Understanding that bidding‑war dynamics can distort reference points and urgency."
    ],
    "take_backs_or_set_aside": [
      "Remove implied certainty around renovation cost ranges; those were illustrative, not verified.",
      "Avoid implying the couple would have zero buffer at any particular price—liquidity specifics were not established.",
      "Do not treat kitchen stopgap costs as known or predictable.",
      "Set aside any suggestion that losing the house will predictably produce later relief; that is not evidence‑based.",
      "Do not treat $935K or $950K as analytically meaningful numbers without user‑provided financial context."
    ],
    "material_shifts": [
      {
        "shift": "Replace invented repair ranges with uncertainty about actual costs.",
        "source_basis": "Pressure to avoid assistant‑originated numbers in estimating buffer.",
        "action_consequence": "Encourage verifying written quotes or contractor ranges before treating any ceiling as cost‑justified."
      },
      {
        "shift": "Reframe the liquidity‑risk claim from near‑certain to unknown without household financial data.",
        "source_basis": "Missing information about cash reserves beyond renovation savings.",
        "action_consequence": "User should check real post‑closing liquidity rather than rely on assumptions."
      },
      {
        "shift": "Clarify that scarcity and emotional value are legitimate inputs but not quantitative evidence.",
        "source_basis": "Regret‑frame pressure.",
        "action_consequence": "Keep emotions present but distinct from affordability facts."
      }
    ],
    "pressure_dispositions": [
      {
        "pressure_id": "evidence_sized_buffer_over_invented_ranges",
        "strongest_plausible_application": "Check whether earlier reasoning treated illustrative renovation numbers as fact, which could distort perceived affordability at different bid levels.",
        "disposition": "use",
        "why": "It helps separate user‑supplied facts from assistant‑generated examples.",
        "visible_effect": "Ceiling remains values‑based, not cost‑justified; no implied buffer calculations.",
        "private_guardrail": "Avoid generating replacement cost numbers; anchor analysis on what is known.",
        "risk_if_forced": "Overconfidence in affordability or risk magnitude.",
        "risk_if_ignored": "User might treat illustrative numbers as verified facts."
      },
      {
        "pressure_id": "regret_frame_not_probability_or_economics",
        "strongest_plausible_application": "Treat both ‘regret walking away’ and ‘regret overspending’ as emotional signals, not evidence about future outcomes.",
        "disposition": "use",
        "why": "Helps maintain clear boundaries between values and financial facts.",
        "visible_effect": "Preserves neighborhood importance without letting regret dictate economic conclusions.",
        "private_guardrail": "Keep emotional reasoning from driving invented probabilities.",
        "risk_if_forced": "Could suppress legitimate emotional preferences.",
        "risk_if_ignored": "Emotions might be mistaken for market evidence."
      },
      {
        "pressure_id": "zero_base_all_in_acquisition_test",
        "strongest_plausible_application": "Ask whether the house’s all‑in cost, if known and de‑anchored from bidding dynamics, would still match user priorities.",
        "disposition": "defer",
        "why": "All‑in cost is not known—using this test now would rely on invented numbers.",
        "visible_effect": "Ceiling remains a values call, not a full economic verdict.",
        "private_guardrail": "Avoid constructing hypothetical total‑cost scenarios using non‑existent data.",
        "risk_if_forced": "Would force fabricated repair or financing numbers.",
        "risk_if_ignored": "User might accept an anchor‑driven ceiling without checking big‑picture fit."
      }
    ],
    "next_actions": [
      "Confirm actual post‑closing liquidity: cash reserves, emergency fund, room for year‑one work.",
      "Obtain written or contractor‑level estimates for electrical and roof timelines/cost ranges.",
      "Check insurance requirements for knob‑and‑tube removal—timeline and documentation needed.",
      "Have a joint conversation with spouse using values, risks, and verified facts rather than invented numbers.",
      "Prepare to communicate 925000 to the agent as the ceiling, if still aligned after reviewing the above."
    ],
    "uncertainties": [
      "Actual cost ranges for electrical replacement, roof, and short‑term kitchen fixes.",
      "Household income, reserves, and debt capacity.",
      "Insurance carrier requirements and timing for electrical updates.",
      "Competitive behavior of other bidders.",
      "True year‑one vs deferred renovation timeline preferences."
    ]
  },
  "served_model": "openai/gpt-5.1-chat-20251113",
  "prompt_tokens": 2389,
  "completion_tokens": 959,
  "total_tokens": 3348,
  "response_sha256": "249eaccc8d5b85388aeaf3ba191983c67198b953e0ba0448d0526fca2029ac24"
}
```

Anonymous output B:

```json
{
  "blind_label": "B",
  "status": "ok",
  "response": {
    "decision_state_read": "User has set a personal bidding ceiling of 925000 dollars and is preparing to communicate it, but this is a self-assessed comfort point rather than an externally validated affordability limit.",
    "updated_position": "Ceiling stays at 925000 dollars as the user's stated limit, with no claim that this number is optimal or financially validated.",
    "what_survived": [
      "User’s savings amount and renovation needs are known only at rough estimates, not precise bids or contractor quotes.",
      "Electrical work and insurance constraints remain relevant but the exact timing and cost are unverified.",
      "Roof condition as reported by the inspector remains a usable but uncertain data point.",
      "Kitchen’s stopgap costs remain plausible as a category but not as specific dollar amounts.",
      "General concern about zero financial buffer in the first year stays relevant."
    ],
    "take_backs_or_set_aside": [
      "Specific cost ranges for kitchen stopgaps, electrical work, or roof timing cannot be treated as reliable without quotes.",
      "Implied certainty that a second major repair will appear cannot be treated as factual.",
      "Any statements suggesting the household definitively cannot afford the home at higher bids need to be softened; affordability was not established from actual financial data.",
      "Assumptions about regret trajectories or later relief should be treated as speculative emotional predictions.",
      "The idea that middle-path bidding is categorically suboptimal cannot be treated as a fact; its effectiveness depends on unknown competing bids."
    ],
    "material_shifts": [
      {
        "shift": "Renovation costs should be treated as high-variance estimates, not near-certain totals.",
        "source_basis": "Inspector comments are informative but not equivalent to contractor bids.",
        "action_consequence": "User may benefit from obtaining at least rough contractor estimates before assuming specific dollar gaps."
      },
      {
        "shift": "Insurance timing risk remains but cost and required scope of electrical work are not confirmed.",
        "source_basis": "Inspector statements suggest knob-and-tube but not a defined remediation plan.",
        "action_consequence": "User should verify insurer requirements and electrical scope before assuming year-one full rewiring."
      },
      {
        "shift": "Assessment of financial buffer should avoid assuming a zero-margin scenario without full household liquidity details.",
        "source_basis": "Conversation lacks income, reserves beyond renovation savings, and access to credit.",
        "action_consequence": "User should inventory total available liquidity, not just renovation savings, when evaluating stretch bids."
      }
    ],
    "pressure_dispositions": [],
    "next_actions": [
      "Clarify actual cost ranges by soliciting preliminary contractor estimates for electrical, roof, and minimum kitchen fixes.",
      "Verify insurer’s exact requirements and timeline for addressing knob-and-tube wiring.",
      "List all available liquidity beyond the designated renovation savings to understand true buffer capacity.",
      "Discuss with spouse what concrete conditions would justify a higher ceiling, distinguishing emotion from financial strategy.",
      "Check whether any alternative financing (e.g., staged projects, HELOC after closing) is feasible without assuming it will be approved."
    ],
    "uncertainties": [
      "True renovation costs could vary widely from initial assumptions.",
      "Competing bids and seller behavior are unknown.",
      "Household’s full financial picture, including income, reserves, and debt capacity, is unspecified.",
      "Timing and extent of insurance-mandated electrical work are not confirmed.",
      "The urgency of roof replacement is based on inspector judgment but not on a professional roofer’s assessment."
    ]
  },
  "served_model": "openai/gpt-5.1-chat-20251113",
  "prompt_tokens": 2039,
  "completion_tokens": 640,
  "total_tokens": 2679,
  "response_sha256": "80d24c5b879c9f293acbee3df41a1bf8f3b783a2f3ca82dc0d851936654cd4d0"
}
```

Blind review sealed before key:

```json
{
  "status": "sealed_before_arm_key",
  "sealed_at_utc": "2026-07-10T13:45:38Z",
  "substantive_preference": "near_tie_with_narrow_B_preference_for_user_facing_utility",
  "action_difference": "not_material",
  "accountability_difference": "material",
  "shared_failures_or_omissions": [
    "Neither output explicitly preserves the source's reported 120000-dollar work estimate and 80000-dollar renovation savings, although both preserve the broader estimate-versus-verified-fact distinction.",
    "Neither output makes the tomorrow-noon bid deadline operational. Several proposed evidence tasks are unlikely to be completed before that deadline, but the outputs do not distinguish pre-bid, post-acceptance, and post-closing gates.",
    "Neither explicitly retracts the original assistant's unsupported Somerville-inventory and 18-month scarcity claims.",
    "Both replace some of the original answer's clean decision momentum with a longer diligence list without saying which missing fact can still affect the imminent bid and which is only a later guardrail."
  ],
  "blind_decision": {
    "candidate_label": "no_material_answer_difference_with_material_accountability_difference",
    "unique_answer_value_demonstrated": false,
    "accountable_consideration_value_visible": true,
    "equivalence_at_immediate_action_level": true,
    "harm_visible": "minor_source_fidelity_and_process_burden_risk_in_A",
    "gate_stop_condition_observed": "A contains a small unsupported causal household-stress claim; treat this as a review red-line failure even though it does not change the bid.",
    "recommendation_before_key": "Do not claim that either anonymous output is materially better. Preserve the pair as evidence that explicit pressure disposition can add accountability without forcing every pressure, while also adding length and a source-fidelity risk. Reveal the key only after this file is hashed."
  },
  "sha256_before_key_reveal": "c33e837f39da522ec961956dc16c80e4a3d114fd2e179e76c10206c3f03751cd"
}
```

Reveal mapping:

```json
{
  "A": "lolla_pressure_treatment",
  "B": "strong_reconsideration_control"
}
```

Post-reveal comparison without regrading:

```json
{
  "same_outcome": [
    "Both preserved 925000 dollars as the user's stated current ceiling rather than a validated optimum.",
    "Both removed or qualified invented repair precision, zero-buffer certainty, affordability certainty, and future-regret forecasts.",
    "Both requested household-liquidity, contractor, and insurance evidence.",
    "Neither changed the likely immediate action, added a real bid threshold, or sequenced its diligence around the tomorrow-noon deadline."
  ],
  "treatment_only_or_stronger": [
    "Explicitly preserved genuine neighborhood and emotional value while separating it from economic evidence.",
    "Recorded the strongest plausible application, use or deferral, visible effect, private guardrail, and forcing/ignoring risk for all three selected pressures.",
    "Correctly deferred the zero-base all-in acquisition test because verified all-in cost was absent.",
    "Avoided introducing the control's HELOC example."
  ],
  "control_only_or_stronger": [
    "Explicitly retracted the original assistant's categorical claim that a middle-path bid was structurally weak.",
    "Described the end-of-conversation state more accurately as preparing to communicate the bid, rather than pending seller response.",
    "Delivered comparable immediate actions with 640 completion tokens rather than 959."
  ],
  "treatment_costs_or_failures": [
    "Added 319 completion tokens, approximately 49.8 percent more than control.",
    "Introduced an unsupported causal statement that low liquidity margin increases household stress.",
    "Used a pending-seller-response formulation not established by the source.",
    "Did not convert its pressure accountability into a unique action, threshold, sequence, or evidence source."
  ],
  "shared_source_failures": [
    "Did not explicitly preserve the reported 120000-dollar work estimate and 80000-dollar renovation savings.",
    "Did not sequence proposed evidence work around the tomorrow-noon deadline.",
    "Did not explicitly retract the prior assistant's unsupported Somerville inventory and 18-month scarcity claims."
  ]
}
```

Claim classification:

```json
{
  "unique_answer_improvement": "not_demonstrated",
  "accountable_consideration": "demonstrated_provisionally",
  "correct_private_stand_down": "demonstrated_provisionally",
  "immediate_action_equivalence": "observed",
  "forcing": "not_observed",
  "harm": "minor_source_fidelity_and_process_burden_risk",
  "graph_necessity": "not_tested"
}
```

Measurement correction:

```json
{
  "contract": "docs/evals/public-revision-private-receipt-boundary-v0.md",
  "contract_sha256": "9cf6e915ce38ddce540cc951bc2fa38d5e7bf62e9e22278084cb7f95aa9f5696",
  "finding": "The observed 959-versus-640 completion-token difference combines public-style revision fields with the treatment-only private receipt. It measures total generation and receipt volume, not isolated public-answer bloat.",
  "frozen_gate_5_artifacts_mutated": false
}
```

## Graph attribution and repair

The first provider-free attribution was preserved as incomplete:

```json
{
  "status": "incomplete_preserved_no_rewrite",
  "finding": "The v1 result correctly attributes the V60 selected-card and private-table pressure packet, but it does not inspect relationship-graph chunks preserved inside companion_cheat_sheet.anchors[].chunks, which is also read by the Step 6 consumer.",
  "invalid_or_too_broad": [
    "The v1 graph-disabled exact-no-op claim is valid only for the V60/private-table packet, not for the complete Step 6 context.",
    "The v1 shuffled-edge non-identifying-no-op claim is valid only for the V60/private-table packet; graph relationship chunks inside companion anchors could change under edge removal or shuffle.",
    "The v1 report does not measure whether graph-derived companion chunks have exact private disposition custody."
  ],
  "prospective_repair": [
    "Freeze a v2 contract and builder without altering the v1 contract, builder, or result.",
    "Inventory graph-derived chunks inside companion_cheat_sheet anchors using their relation_target_id provenance.",
    "Separate V60-packet no-op from complete-Step-6-context no-op.",
    "Assess whether Stage B pressure IDs cite any of those exact graph-derived chunks and whether a ledger records their individual disposition."
  ]
}
```

The prospective v2 repair inspected the complete Step 6 surface:

```json
{
  "decision_evidence": {
    "admitted_pressure_count": 3,
    "graph_specific_admitted_pressure_count": 0,
    "graph_specific_admitted_pressure_ids": [],
    "all_admitted_chunks_present_in_v60": true,
    "graph_expansion_count": 9,
    "graph_expansions_entered_v60_candidate_pool": false,
    "graph_expansions_entered_v60_selected_cards": false,
    "graph_expansions_entered_private_table": false,
    "case10_can_identify_graph_contribution": false,
    "paid_graph_ablation_candidate": false,
    "companion_graph_chunks_entered_complete_step6_context": true,
    "companion_graph_chunk_count": 3,
    "individual_graph_chunk_disposition_custody": false,
    "stage_b_pressure_with_graph_target_lineage_count": 0,
    "stage_b_pressure_with_graph_target_lineage_ids": [],
    "case10_stage_b_can_identify_graph_contribution": false
  },
  "consumer_surface": {
    "companion_graph_chunk_count": 3,
    "companion_graph_chunks": [
      {
        "anchor_model_id": "regret-theory",
        "relation_target_id": "confirmation-bias",
        "chunk_type": "antagonist",
        "text": "Confirmation Bias: Confirmation-bias is countered by regret-theory when the framework forces the decision maker to consider the regretted path of inaction instead of only the comfortable default story.",
        "source_layer": "wave3",
        "extraction_type": "explicit",
        "confidence": "high",
        "raw_expansion_match_count": 1,
        "raw_expansion_matches": [
          {
            "source_model_id": "regret-theory",
            "relation_type": "antagonist",
            "target_model_id": "confirmation-bias",
            "substrate_chunk": "Confirmation-bias is countered by regret-theory when the framework forces the decision maker to consider the regretted path of inaction instead of only the comfortable default story."
          }
        ],
        "exact_raw_expansion_match": true
      },
      {
        "anchor_model_id": "regret-theory",
        "relation_target_id": "optionality",
        "chunk_type": "ally",
        "text": "Optionality: Optionality strengthens regret-theory by checking whether action can be made more reversible before anticipated regret hardens the choice.",
        "source_layer": "wave3",
        "extraction_type": "explicit",
        "confidence": "high",
        "raw_expansion_match_count": 1,
        "raw_expansion_matches": [
          {
            "source_model_id": "regret-theory",
            "relation_type": "ally",
            "target_model_id": "optionality",
            "substrate_chunk": "Optionality strengthens regret-theory by checking whether action can be made more reversible before anticipated regret hardens the choice."
          }
        ],
        "exact_raw_expansion_match": true
      },
      {
        "anchor_model_id": "calculated-risk-taking",
        "relation_target_id": "black-swan-events",
        "chunk_type": "antagonist",
        "text": "Black Swan Events: Calculated-risk-taking conflicts with black-swan-events when systematic risk estimation creates false precision around outcomes whose probability distributions have fat tails.",
        "source_layer": "wave3",
        "extraction_type": "explicit",
        "confidence": "high",
        "raw_expansion_match_count": 1,
        "raw_expansion_matches": [
          {
            "source_model_id": "calculated-risk-taking",
            "relation_type": "tension",
            "target_model_id": "black-swan-events",
            "substrate_chunk": "Calculated-risk-taking conflicts with black-swan-events when systematic risk estimation creates false precision around outcomes whose probability distributions have fat tails."
          }
        ],
        "exact_raw_expansion_match": true
      }
    ],
    "graph_relation_target_model_ids": [
      "black-swan-events",
      "confirmation-bias",
      "optionality"
    ],
    "parent_anchor_source_items": [
      "lane2::calculated-risk-taking",
      "lane2::regret-theory"
    ],
    "parent_anchor_ledger_items": [
      {
        "source_id": "lane2::regret-theory",
        "source_kind": "lane2_anchor",
        "disposition": "",
        "why": ""
      },
      {
        "source_id": "lane2::calculated-risk-taking",
        "source_kind": "lane2_anchor",
        "disposition": "",
        "why": ""
      }
    ],
    "individual_graph_chunk_ledger_ids": [],
    "individual_graph_chunk_disposition_custody": false,
    "custody_read": "Graph relationship chunks reach Step 6 inside companion anchors, but the recorded private-table ledger dispositions the parent anchor rather than each relationship chunk."
  },
  "interpretation_boundary": {
    "mechanical_conclusion": "Graph relationships reached the normal Step 6 consumer indirectly inside three companion-anchor chunks, but none had exact lineage in the frozen Case 10 Stage B pressure packet and none had individual disposition custody. The completed pair therefore cannot identify graph contribution.",
    "does_not_prove": [
      "that the three graph chunks changed or did not change an ordinary live Step 6 answer",
      "that graph expansion is generally useful or useless",
      "that a parent-anchor disposition is semantic proof about every embedded relation",
      "that another case cannot support a graph-specific ablation"
    ],
    "required_before_paid_ablation": [
      "one source-reviewed graph relationship chunk absent from simpler baselines",
      "exact graph-chunk identity in the treatment contract",
      "separate individual disposition custody",
      "a graph-disabled or shuffled-edge arm frozen before generation",
      "public-revision and private-receipt fields measured separately"
    ]
  }
}
```

Source-first review of exact graph chunks:

```json
{
  "chunks": [
    {
      "anchor_model_id": "regret-theory",
      "relation_type": "antagonist",
      "relation_target_id": "confirmation-bias",
      "chunk": "Confirmation-bias is countered by regret-theory when the framework forces the decision maker to consider the regretted path of inaction instead of only the comfortable default story.",
      "strongest_plausible_application": "Check whether the user's reluctance to raise the bid is merely protecting a comfortable existing position while underweighting the cost of inaction.",
      "source_fit": "weak",
      "novelty_against_control": "weak",
      "disposition": "reject",
      "why": "The source does not establish a comfortable status-quo default. The user already offered above asking, explicitly considered regret in both directions, and selected a higher ceiling. Treating refusal to raise further as confirmation bias would pathologize a bounded decision and favor action by construction.",
      "risk_if_forced": "Could turn the husband's go-higher preference into the privileged frame and mislabel a legitimate financial boundary as bias.",
      "useful_residue": "Keep regret symmetric; do not assume action is epistemically superior to restraint."
    },
    {
      "anchor_model_id": "regret-theory",
      "relation_type": "ally",
      "relation_target_id": "optionality",
      "chunk": "Optionality strengthens regret-theory by checking whether action can be made more reversible before anticipated regret hardens the choice.",
      "strongest_plausible_application": "Ask whether any verified bid, contingency, renovation-sequencing, or alternative-property path preserves meaningful reversibility before the deadline.",
      "source_fit": "conditional_but_missing_required_facts",
      "novelty_against_control": "possible_private_guardrail_only",
      "disposition": "defer",
      "why": "The source does not establish offer-contingency rules, legal reversibility, alternative inventory, or a safe reversible financing path. The prior frame reanalysis already produced unsafe alternative-property and delay-all-renovation variants that source-first review rejected.",
      "risk_if_forced": "Could invent alternatives, assume a bid is reversible, ignore the tomorrow-noon deadline, or weaken the reported year-one electrical constraint.",
      "useful_residue": "If verified reversible options exist, compare them; absence of that evidence prevents visible advice now."
    },
    {
      "anchor_model_id": "calculated-risk-taking",
      "relation_type": "tension",
      "relation_target_id": "black-swan-events",
      "chunk": "Calculated-risk-taking conflicts with black-swan-events when systematic risk estimation creates false precision around outcomes whose probability distributions have fat tails.",
      "strongest_plausible_application": "Challenge the original assistant's invented repair ranges, near-certainty of a second discovery, and confident zero-buffer conclusion.",
      "source_fit": "strong",
      "novelty_against_control": "already_covered",
      "disposition": "reject_as_duplicate",
      "why": "The strong reconsideration control independently removed the invented repair precision and near-certainty claim. The admitted evidence-sized-buffer pressure also covers the same mechanism more safely without importing a fat-tail claim that the source cannot verify.",
      "risk_if_forced": "Could replace one unsupported probability story with a more dramatic tail-risk label and reward graph vocabulary rather than a new decision consequence.",
      "useful_residue": "Preserve uncertainty and demand evidence-sized claims; no separate graph treatment is earned."
    }
  ],
  "decision": {
    "graph_chunks_reviewed": 3,
    "graph_chunks_admitted_for_case10_paid_ablation": 0,
    "paid_case10_graph_ablation_authorized": false,
    "reason": "One graph chunk has the wrong activation condition, one lacks the facts needed for safe application, and one is already recovered by the strong control and admitted non-graph pressure.",
    "next_evidence_need": "Find a different frozen case where an exact relationship-graph chunk is source-supported, absent from strong transcript-only reconsideration, individually dispositionable, and capable of a bounded consequence before designing a paid arm."
  }
}
```

Metadata-only exact graph identities:

```json
[
  {
    "graph_pressure_id": "graph::regret-theory::antagonist::confirmation-bias::1b76ea4bbc46",
    "source_anchor_model_id": "regret-theory",
    "relation_type": "antagonist",
    "target_model_id": "confirmation-bias",
    "chunk_text_sha256": "1b76ea4bbc4679dce85731f5ddfc3a14097358c4a7dd589d3da006459bf5f0a0",
    "source_json_pointer": "/companion_cheat_sheet/anchors/0/chunks/2",
    "source_review_status": "pending",
    "disposition": ""
  },
  {
    "graph_pressure_id": "graph::regret-theory::ally::optionality::964793dc5498",
    "source_anchor_model_id": "regret-theory",
    "relation_type": "ally",
    "target_model_id": "optionality",
    "chunk_text_sha256": "964793dc5498f6c317c29d65280bcaef626fe7dc5180cd26492724cdb65c66a5",
    "source_json_pointer": "/companion_cheat_sheet/anchors/0/chunks/4",
    "source_review_status": "pending",
    "disposition": ""
  },
  {
    "graph_pressure_id": "graph::calculated-risk-taking::tension::black-swan-events::b73d43ce9a4f",
    "source_anchor_model_id": "calculated-risk-taking",
    "relation_type": "tension",
    "target_model_id": "black-swan-events",
    "chunk_text_sha256": "b73d43ce9a4f4432260bf0294ff3e84c65dea319bb042a59f8ccf2ad61915784",
    "source_json_pointer": "/companion_cheat_sheet/anchors/2/chunks/4",
    "source_review_status": "pending",
    "disposition": ""
  }
]
```

## What may and may not be claimed

Supported:

- Case 10 Stage A and Stage B executed within their frozen mechanical contracts.
- The treatment created provisional accountable-consideration value and correctly deferred one pressure.
- The treatment did not demonstrate unique immediate-answer improvement over the strong control.
- Graph relationships reached ordinary reconsideration indirectly inside companion anchors.
- The completed Stage B pair did not isolate graph contribution.
- No eligible graph-specific case exists in the comparable six-case July inventory.

Unsupported or forbidden:

- Lolla improves real-world decisions.
- The graph is necessary or useless.
- More calls or a longer receipt prove deeper reasoning.
- The receipt is human validation, certification, or approval.
- Any bid, financial, repair, insurance, legal, or relationship outcome is correct.

## Whole-run operability

```json
{
  "stage_a_openrouter_calls": 26,
  "stage_a_direct_openai_calls": 7,
  "stage_b_openrouter_calls": 2,
  "total_recorded_tokens_stage_a_plus_stage_b": 92172,
  "estimated_cost_usd_stage_a_plus_stage_b": 0.054021,
  "stage_b_wall_time_seconds": 9.397,
  "experiment_retries_stage_a": 0,
  "experiment_retries_stage_b": 0,
  "evaluator_calls_stage_b": 0
}
```

## Current authorizations

```json
{
  "gate_7_agent_reader_contract_construction": true,
  "gate_7_reader_call": false,
  "human_validation": false,
  "paid_graph_ablation": false,
  "runtime_integration": false,
  "graph_promotion": false
}
```

## Questions for a cold reader

- Can the reader distinguish source facts from assistant claims and later interpretations?
- Can the reader reconstruct why the treatment did not earn an answer-improvement claim?
- Can the reader explain the narrower accountability value without calling it quality proof?
- Can the reader explain the v1 attribution error and v2 repair?
- Can the reader state why paid graph testing remains blocked and what would unblock it?
- Can the reader identify which conclusions still require human judgment?

## Artifact manifest

```json
[
  {
    "role": "receipt_builder",
    "path": "scripts/evals/build_case10_reasoning_receipt.py",
    "sha256": "db5b775b5df4ba4e5025c83db49b69a527fe3e55539adb7bb1e32a538199a553"
  },
  {
    "role": "source_conversation",
    "path": "research/test-cases/case_real_estate_conversation.txt",
    "sha256": "61f93615edbf79660972b8b44c58cd900c3617f721f92c1f76e9b3a8b1cf95a5"
  },
  {
    "role": "stage_a_decision",
    "path": "research/stage-a-case10-2026-07-10/decision.json",
    "sha256": "623f29e91ce2b87309413d99678c366d603dea5490835c39c9cda0ad546b2913"
  },
  {
    "role": "stage_a_preliminary_review",
    "path": "research/stage-a-case10-2026-07-10/preliminary-pressure-review.json",
    "sha256": "969a7768a594577bb3eec1483105d385b7a0cd97f15eae58875ced6ccd6fe848"
  },
  {
    "role": "stage_a_pressure_packet",
    "path": "research/stage-a-case10-2026-07-10/pressure-packet.json",
    "sha256": "25aa14c55ecd63a44b5ca821be994e3bf3b65638b151213809f1580739131a9d"
  },
  {
    "role": "stage_b_contract",
    "path": "research/stage-b-case10-2026-07-10/contract.json",
    "sha256": "5d42822fe552d4577bf3199876314bb2d1a4a09a65904e792af447108bfcb865"
  },
  {
    "role": "stage_b_run_summary",
    "path": "research/stage-b-case10-2026-07-10/run/lolla_stage_b_case10_20260710_a1/run-summary.json",
    "sha256": "76351570a69beb15548c877489e4df0aeb196da77c94ac5c30346c068e0e41e9"
  },
  {
    "role": "stage_b_blind_outputs",
    "path": "research/stage-b-case10-2026-07-10/run/lolla_stage_b_case10_20260710_a1/blind-outputs.json",
    "sha256": "56e782ef6cbd00134769f91318ca4134ce6ce5852b288a7af88cd01a429d25a2"
  },
  {
    "role": "stage_b_blind_review",
    "path": "research/stage-b-case10-2026-07-10/blind-review-before-key.json",
    "sha256": "c33e837f39da522ec961956dc16c80e4a3d114fd2e179e76c10206c3f03751cd"
  },
  {
    "role": "stage_b_arm_key",
    "path": "research/stage-b-case10-2026-07-10/run/lolla_stage_b_case10_20260710_a1/arm-key.json",
    "sha256": "9730c9ea320715e946e5af288da067e2af3212b2477845d506170afa486c7dc6"
  },
  {
    "role": "stage_b_revealed_comparison",
    "path": "research/stage-b-case10-2026-07-10/revealed-comparison.json",
    "sha256": "8c0b9677fe03646af4e9e2d478107e21012d0b4802226f49906e3580b4b372a6"
  },
  {
    "role": "stage_b_decision",
    "path": "research/stage-b-case10-2026-07-10/decision.json",
    "sha256": "6c24442dc3084ed51f6c80e16970dfe6259812844814645e43a197bec346847e"
  },
  {
    "role": "gate6_v1_completion_audit",
    "path": "research/gate6-case10-graph-attribution-2026-07-10/v1-completion-audit.json",
    "sha256": "45d6a030cc29f9cadbf5eef0b018b7d45b93798fb07ec2121b7abcb7f6fd2a8e"
  },
  {
    "role": "gate6_v2_result",
    "path": "research/gate6-case10-graph-attribution-2026-07-10/preflight-result-v2.json",
    "sha256": "f010a1fe0eb569fa4d7d4aed4d4d76a661a25aec9e104a4341402cc8958899d0"
  },
  {
    "role": "gate6_graph_source_review",
    "path": "research/gate6-case10-graph-attribution-2026-07-10/source-first-graph-chunk-review.json",
    "sha256": "5d269b35823cf1acab206859ecd8f3131f364b7e35f7036a476bf481401225fd"
  },
  {
    "role": "gate6_case10_decision",
    "path": "research/gate6-case10-graph-attribution-2026-07-10/decision.json",
    "sha256": "52ddccfe04cbc6ce387b873b4a9a0c883f5d04fc24ed4e127366a7b9200db19e"
  },
  {
    "role": "gate6_inventory_decision",
    "path": "research/gate6-graph-candidate-inventory-2026-07-10/decision.json",
    "sha256": "3c074f6f2824c33d13c9cfcbfe0e699a4e639b278cb7ea1b0733a9997576195f"
  },
  {
    "role": "gate6_shadow_custody",
    "path": "research/gate6-graph-candidate-inventory-2026-07-10/case10-shadow-custody.json",
    "sha256": "a91b8fb6d0c714ee64bc5054eeb9e8fd5ca26c50a543b7feaf289e60b3c108bb"
  },
  {
    "role": "product_constitution",
    "path": "docs/conversation-understanding/lolla-product-constitution-v0.md",
    "sha256": "952a7d8fb47640d7eccfc1aa815d784c96da77c7ab07f47b3f8c256b6032524f"
  },
  {
    "role": "public_private_eval_boundary",
    "path": "docs/evals/public-revision-private-receipt-boundary-v0.md",
    "sha256": "9cf6e915ce38ddce540cc951bc2fa38d5e7bf62e9e22278084cb7f95aa9f5696"
  }
]
```

## Non-claims

- not human review
- not ground truth
- not a quality score
- not product proof
- not proof of reasoning depth
- not financial real-estate insurance legal renovation or bidding advice
- not graph promotion
- not runtime-integration authority
- not autonomous-action authority
