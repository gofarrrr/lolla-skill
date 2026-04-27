# Source-first cluster labeling — `mother-deciding-address-year`

Status: **STEP 1–3 only** (per design memo §6.1–§6.3). Lane 2 outputs (`result.json`, `companion_cheat_sheet`, `revised.txt`) NOT opened for this case.

Case: `mother-deciding-address-year`
Run timestamp: `20260424T124626Z`
Bucket hypothesis: failure-rich (parent-teen safety-planning crisis; mid Step 6 consumption rate at 60%; tests F1''' across power-dynamics / opportunity-cost / second-order / feedback-loops content)
Source consulted: `conversation.txt` Turn 1–12 ASSISTANT messages only.

## Honesty disclosure

Claude has seen this case's anchor set during the corpus survey (Feedback Loops, Opportunity Cost, Second Order Thinking, Power Dynamics, Principal Agent Problem). Less direct exposure than consultant-decides; medium bias risk. Source-first discipline applied below.

## Clusters

### C1 — Reframe priority: relationship-repair before threat-management

`source_quotes`:
- Turn 2 ASSISTANT: "The first move here isn't to push on the 19-year-old. It's to create a way for her to re-enter the relationship without losing all face."
- Turn 2 ASSISTANT: "The 19-year-old is the bigger problem medium-term, but in the next 48 hours, the priority is re-opening communication."
- Turn 6 ASSISTANT: "Treat normal as the goal. She needs to see that the relationship can go back to functioning without the thing being solved yet."

`reasoning_shape`: framing_reframing

`expected_primary_models`: *Problem Framing And Reframing*

`acceptable_secondary_models`: *Theory Of Constraints* (relationship is the binding constraint on every other downstream action; secondary only)

`should_reject_models`: *Status Quo Bias*, *Sunk Cost Fallacy*

`ambiguous`: no

### C2 — Surveillance as feedback loop; relationship as the information source

`source_quotes`:
- Turn 3 ASSISTANT: "The answer is not tighter surveillance; it's rebuilding enough of a relationship that she wants to tell you when the next guy appears."
- Turn 5 ASSISTANT: "I don't think you can build a better relationship with her on the scaffolding of ongoing secret surveillance — at some point she figures it out, usually around 15-16 when kids get more technically sophisticated, and then the breach of trust is much bigger than this one."

`reasoning_shape`: systems_feedback

`expected_primary_models`: *Feedback Loops*

`acceptable_secondary_models`: *Second Order Thinking* (the surveillance → discovery → larger-breach chain), *Information Asymmetry* (surveillance creates an unstable information regime)

`should_reject_models`: *Hindsight Bias*

`ambiguous`: no

### C3 — Block-the-guy → communication goes underground

`source_quotes`:
- Turn 3 ASSISTANT: "Sometimes blocking drives the communication underground on a different platform or device, and you lose visibility entirely."

`reasoning_shape`: systems_feedback / second_order

`expected_primary_models`: *Second Order Thinking*

`acceptable_secondary_models`: *Feedback Loops* (related; the move is a specific consequence chain rather than a general loop)

`should_reject_models`: *Optionality* (the move is predicting consequences, not generating options)

`ambiguous`: no — distinct from C2 because C2 is the strategic frame ("relationship over surveillance") and C3 is a tactical consequence chain ("if you block him, you lose visibility").

### C4 — Ex-spouse's competing power during custody

`source_quotes`:
- Turn 4 ASSISTANT: "He minimizes, gets in her ear during his custody days, tells her you're overreacting, and she learns that her dad is the safe one and you're the hysterical one. Bad outcome."
- Turn 4 ASSISTANT: "The fact that you even have to worry about your ex's reaction is a constraint on your options, not a choice."
- Turn 7 ASSISTANT: "your ex will be involved as a co-parent, and his minimization could actively harm her through the process (his statements to investigators, his influence on her during custody days). That's a real consideration that parents in intact households don't have."

`reasoning_shape`: power_social_dynamics

`expected_primary_models`: *Power Dynamics*

`acceptable_secondary_models`: *Principal Agent Problem* (the ex is acting as a co-parent agent for the daughter but with misaligned incentives; secondary only — PD is the load-bearing read because the mechanism is competing-influence-during-custody, not fiduciary misalignment)

`should_reject_models`: *Authority Bias* (user isn't deferring to ex's authority; she's recognizing his competing power)

`ambiguous`: no

### C5 — Goal reframe: "he's gone" vs "she's safe"

`source_quotes`:
- Turn 4 ASSISTANT: "he's gone is a different goal from she's safe. She's safe requires her to trust you with information about him and about the next person who tries something. He's gone just removes this one person, and doesn't protect her from the next one."

`reasoning_shape`: framing_reframing

`expected_primary_models`: *Problem Framing And Reframing*

`acceptable_secondary_models`: *Inversion* (testing the reframe by inverting which goal you're optimizing)

`should_reject_models`: *Status Quo Bias*

`ambiguous`: no — distinct from C1: C1 reframes WHEN to address the problem; C5 reframes WHAT the goal is.

### C6 — Tradeoff: protection vs accountability are mutually exclusive

`source_quotes`:
- Turn 7 ASSISTANT: "the obvious right answer doesn't exist here."
- Turn 7 ASSISTANT: "If your goal is protecting her, not reporting and getting her to a specialized therapist is probably the better path given your co-parenting situation. If your goal is accountability for him, you'll never fully get that, and reporting may not produce it either."
- Turn 7 ASSISTANT: "The hardest thing about this moment is accepting that there's no version where he's properly punished AND she's fully protected. You have to pick the one that matters more to you, knowing you won't get both."

`reasoning_shape`: tradeoff_opportunity_sizing

`expected_primary_models`: *Opportunity Cost*

`acceptable_secondary_models`: *Inversion* (testing each goal as primary), *Problem Framing And Reframing* (forcing user to choose the goal)

`should_reject_models`: *Loss Aversion* (tempting fit but the move is mutual-exclusion tradeoff)

`ambiguous`: no

### C7 — Don't call Mia's mom: protective instinct's action would undo repair (`no_clean_primary`)

`source_quotes`:
- Turn 9 ASSISTANT: "Your protective instinct wants to warn every other parent of every other 14-year-old girl. That instinct is good; the action that comes from it, in this moment, would be wrong."
- Turn 9 ASSISTANT: "If you ever have concrete, specific evidence that Mia is in harm's way — that's different. Then you'd have a direct obligation to alert her parents. But 'she's 14 and on social media' isn't specific evidence of harm."

`reasoning_shape`: incentives_agency / other

`expected_primary_models`: **`no_clean_primary`**

`acceptable_secondary_models`: *Confidence Calibration* (the conditional gate "if you ever have concrete, specific evidence" is calibration-shaped; secondary only)

`should_reject_models`: *Principal Agent Problem*

`ambiguous`: no — primary is deliberately `no_clean_primary`. The move "your instinct is right; the action would be wrong" is real reasoning but doesn't map cleanly to a 222 model. Forcing one would inflate the gold set.

### C8 — Premortem on panic; redefine the success criterion

`source_quotes`:
- Turn 12 ASSISTANT: "You are going to second-guess every single one of these steps this week. You're going to wake up at 3am convinced you should have called the police. You're going to read her one-word text and convince yourself it means she hates you. You're going to be tempted to take her phone, block the guy, and lock things down because it feels like doing something."
- Turn 12 ASSISTANT: "When that happens, remember: the goal isn't to feel like you did enough. The goal is for her to come out the other side of this as a kid who can tell you things. Those are not the same goal, and the first one — the 'doing enough' feeling — will actively work against the second one."

`reasoning_shape`: counterfactual / failure-planning

`expected_primary_models`: *Premortem*

`acceptable_secondary_models`: *Confidence Calibration* (separating "feeling like you did enough" from "actual success criterion" is calibration-flavored)

`should_reject_models`: *Hindsight Bias*

`ambiguous`: no

`note`: This cluster is the **key F1''' test** Marcin pre-registered. The source contains explicit "When [predicted failure mode] happens, [pre-registered correction]" structure — literal if-when-then reversal language and an explicit goal redefinition ("the goal isn't X, the goal is Y"). Per F1''', operational-language presence here is high. If Premortem still rejects, that's evidence of a model-specific verifier blind spot, not the operational-language hypothesis.

## Cluster summary (pre-attribution)

| Cluster | Primary | Secondary | Key boundary |
|---|---|---|---|
| C1 — Reframe priority | *Problem Framing And Reframing* | *Theory Of Constraints* | Relationship-first sequencing |
| C2 — Surveillance feedback loop | *Feedback Loops* | *Second Order Thinking*, *Information Asymmetry* | Self-undermining loop, not single chain |
| C3 — Block-the-guy → underground | *Second Order Thinking* | *Feedback Loops* | Specific consequence chain |
| C4 — Ex's custody-day power | *Power Dynamics* | *Principal Agent Problem* | Competing influence, not fiduciary misalignment |
| C5 — Goal reframe | *Problem Framing And Reframing* | *Inversion* | Goal-definition reframe, not just sequencing |
| C6 — Protection vs accountability | *Opportunity Cost* | *Inversion*, *Problem Framing And Reframing* | Mutual exclusion explicitly named |
| C7 — Don't call Mia's mom | `no_clean_primary` | *Confidence Calibration* | No clean 222 fit |
| C8 — Premortem on panic + success criterion | *Premortem* | *Confidence Calibration* | Literal if/when-then reversal language |

### Counts

- 8 clusters
- 7 with non-ambiguous expected primary
- 1 (`C7`) with non-ambiguous `no_clean_primary`
- Distinct expected_primary_models: 6 (*Problem Framing And Reframing* ×2, *Feedback Loops*, *Second Order Thinking*, *Power Dynamics*, *Opportunity Cost*, *Premortem*)

## Pre-registered F1''' prediction table

This table is recorded **before opening Lane 2 outputs** to test the replacement hypothesis from case 3:

> *The verifier accepts a model when the source quote contains operationalized mechanism language for that model — explicit numbers, named processes, or observable behaviors that map directly to the model's mechanism. Rejects when the model's mechanism requires interpretive translation between the source language and the model concept.*

Operationalization levels:
- **high** — explicit numbers, named process, direct causal phrase, institutional incentive, observable behavior, or clear if/then action rule
- **medium** — concrete facts, but the model still requires some conceptual translation
- **low** — model fit depends mostly on the reader recognizing the abstract reasoning pattern

| Cluster | Expected primary | Source-quote operationalization | Prediction | Reason |
|---|---|---|---|---|
| C1 | *Problem Framing And Reframing* | medium ("the first move ISN'T X. It's Y" is direct reframe phrasing, but the PFR mechanism is inherently interpretive) | **recall-risk** | PFR has been absent on all 3 prior cases via different mechanisms (recall ×3, verifier ×1). The recall hole is the dominant pattern; operational language hasn't saved PFR before. |
| C2 | *Feedback Loops* | medium-to-high (causal chains explicit; "self-undermining loop" mechanism named) | **accept** | Per F1''', operational mechanism language is present. *Feedback Loops* has not appeared in prior cases — first test of this model. |
| C3 | *Second Order Thinking* | high (explicit causal chain "blocking → underground → lose visibility") | **accept**, **with "too generic" hedge** | Operational language strong, but case 3 had Second Order Thinking rejected with "too generic" (rejection reason: rejection_reason = "too generic"). The verifier may have a model-specific rule that flags SOT as too broad, regardless of source operationalization. If C3 rejects despite operational language, that's a Second-Order-Thinking-specific verifier behavior. |
| C4 | *Power Dynamics* | high (specific mechanism: "custody days" + "she learns that her dad is the safe one and you're the hysterical one" — observable behavior, explicit power transfer) | **accept** | Per F1'''. Note: PD has been rejected on cases 1+3 ("mechanism absent" / not in candidates). Whether F1''' overrides that history is a key test. |
| C5 | *Problem Framing And Reframing* | medium ("X is a different goal from Y" is direct reframe phrasing) | **recall-risk** | Same PFR pattern as C1. |
| C6 | *Opportunity Cost* | medium-to-high (explicit mutual-exclusion: "no version where X AND Y", "you have to pick"; explicit tradeoff named) | **reject** | Opportunity Cost has been consistently rejected on cases 1+2 ("mechanism absent") even when source had explicit tradeoff numbers (case 1 fractional dollars; case 2 mother-time priced against money). The "comparing values is interpretive" issue. If C6 passes here with the explicit mutual-exclusion phrasing, that updates F1''' to "mutual-exclusion language is sufficient to operationalize OC." |
| C7 | `no_clean_primary` | n/a | n/a | Lane 2 should not surface a model for this cluster. |
| C8 | *Premortem* | **HIGH** ("When [predicted failure] happens, [pre-registered correction]" — literal if-when-then reversal language; explicit goal redefinition "the goal isn't X, the goal is Y") | **accept** per F1''' | **KEY TEST** Marcin flagged. Premortem has been rejected on cases 1 + 3 ("mechanism absent"). Source operationalization here is the highest in the audit so far (literal if-when-then). If Premortem rejects despite this, the rejection is **not** explained by operational-language presence — it's a Premortem-specific verifier behavior, and F1''' would need refinement (e.g., operational-language matters EXCEPT for certain models with idiosyncratic rejection rules). |

### Pre-registered hypothesis-test interpretation

Stop conditions for revising F1''':

- If C2 *Feedback Loops* rejects despite the explicit causal-chain language, F1''' weakens — operational language doesn't save the loop-shape mechanism.
- If C8 *Premortem* rejects despite the literal if-when-then language, F1''' has model-specific exceptions; refinement needed.
- If C6 *Opportunity Cost* passes with the mutual-exclusion phrasing, F1''' is supported and operational-language sufficiency is broader than first thought.
- If C3 *Second Order Thinking* rejects despite the explicit consequence chain, the "too generic" rejection reason looks like a model-specific blind spot.
- If C4 *Power Dynamics* passes, that's the first PD acceptance in the audit and supports F1''' overriding mental-model category history.

PFR clusters (C1, C5) are predicted to fail at recall. If they reach candidates and pass the verifier, that would be a bigger update than this prediction table contemplates — would suggest PFR's recall hole is conversation-specific, not systematic.

## What I'm holding for step 2

- 8 clusters, 6 distinct primaries, 1 `no_clean_primary`.
- Pre-registered predictions: 4 expected ACCEPT (C2, C3, C4, C8), 1 expected REJECT (C6), 2 expected RECALL-RISK (C1, C5).
- Three model-specific blind-spot tests embedded: C3 SOT "too generic" history vs operationalized chain; C6 OC tradeoff history vs explicit mutual-exclusion; C8 Premortem rejection history vs literal if-when-then language.
- After opening Lane 2 artifacts, attribution will compare actual outcomes to this table and update F1''' accordingly.
