# Source-first cluster labeling — `marcus-equity`

Status: **STEP 1–3 only** (per design memo §6.1–§6.3). Lane 2 outputs (`result.json`, `companion_cheat_sheet`, `revised.txt`) NOT opened for this case.

Case: `marcus-equity`
Run timestamp: `20260422T091837Z`
Bucket hypothesis: failure-rich, but a *different* failure shape than cases 1–4. **High Step 6 consumption (100%) with very low Lane 2 stability (Accepted-pre 0.13 across N=3 runs)**. Step 6 happily consumes whatever Lane 2 hands it; Lane 2 hands different things each run. The audit's question on Marcus is whether the source itself is genuinely underdetermined (multiple honest reads compete) or whether the producer chain has a stability problem.
Source consulted: `conversation.txt` Turn 1–7 ASSISTANT messages only.

## Honesty disclosures

1. **Author bias:** Claude has seen marcus-equity references throughout this audit. The current archived run's anchors (Sunk Cost Fallacy, Representativeness Heuristic) are familiar.

2. **Permissive ambiguity rule applied here.** Per Marcin's case-5 instruction: this conversation is allowed to use `no_clean_primary`, multiple `acceptable_secondary_models`, and explicit `gold_ambiguity_note` more freely than prior cases. The danger Marcin flagged: forcing a single canonical model onto a genuinely underdetermined equity conversation would make the audit look cleaner while lying about the product problem.

## Clusters

### C1 — Reframe: equity is paying the actual cost of business dependency

`source_quotes`:
- Turn 1 ASSISTANT: "the first question isn't 'should I give Marcus equity?' It's: what happens to this business without Marcus?"
- Turn 1 ASSISTANT: "You're not giving away something you earned. You're paying the actual cost of what your business depends on. Right now, you're getting Marcus at a below-market cash price AND without equity. That's a subsidy. Subsidies don't last forever."

`reasoning_shape`: framing_reframing

`expected_primary_models`: *Problem Framing And Reframing*

`acceptable_secondary_models`: *Inversion* (testing the inverse: what's the cost of him leaving)

`should_reject_models`: *Sunk Cost Fallacy* (this is forward-cost framing, not past-cost)

`ambiguous`: no

`gold_ambiguity_note`: PFR is the load-bearing read; the "subsidy" framing is somewhat metaphorical but the cluster's structural move is reframing the question's category.

### C2 — Two problems tangled: equity ask is inseparable from the platform

`source_quotes`:
- Turn 2 ASSISTANT: "OK, this changes things significantly. You don't just have an equity question. You have two problems tangled together and you need to untangle them."
- Turn 2 ASSISTANT: "He's not just asking for equity. He's asking: does my vision for where this company could go matter to you, or am I just here to execute your vision?"
- Turn 2 ASSISTANT: "What you're actually deciding is whether Marcus is an employee you need to retain, or a partner who could help you build something bigger than an agency."

`reasoning_shape`: framing_reframing / problem_decomposition

`expected_primary_models`: ambiguous — *Problem Framing And Reframing* OR *Decomposition*

`acceptable_secondary_models`: whichever is not primary

`should_reject_models`: *Theory Of Constraints* (no single binding constraint named yet)

`ambiguous`: **yes**

`gold_ambiguity_note`: The cluster is doing two things at once — *decomposing* "the equity question" into two distinct problems (employment vs vision) AND *reframing* the user's surface question as the wrong question. Either *Problem Framing And Reframing* or *Decomposition* is defensible as primary. PFR feels slightly more load-bearing because the move is "you're seeing this wrong," not just "let me split this in two." Marcin's call.

### C3 — Departure as competitive threat (second-order chain)

`source_quotes`:
- Turn 2 ASSISTANT: "the platform play creates a scenario where Marcus leaving isn't just a talent loss. It's a competitive threat. He walks out with Jake and Lina, builds the platform himself, and now he's selling to YOUR competitors."
- Turn 4 ASSISTANT: "If Marcus leaves: You lose 3 of your top 5 engineers immediately. Client delivery capacity drops, probably 30-40% for six months or more. You lose the person clients trust... Marcus potentially builds a competing product using the knowledge he accumulated at your company."

`reasoning_shape`: second_order_thinking

`expected_primary_models`: *Second Order Thinking*

`acceptable_secondary_models`: *Premortem* (the "if Marcus leaves, here's the full failure chain" is failure-mode pre-tracing)

`should_reject_models`: *Theory Of Constraints*

`ambiguous`: no

`gold_ambiguity_note`: Operationalization is high — explicit causal chain "leaves → engineers follow → capacity drops → multiple drops → exit value drops".

### C4 — Tom is the wrong reference class

`source_quotes`:
- Turn 3 ASSISTANT: "You're using Tom as a data point, but it's the wrong comparison. Tom was a senior designer. Marcus is your head of engineering who built your core infrastructure, has six years of institutional knowledge, and would take your two best engineers with him."
- Turn 3 ASSISTANT: "Using Tom's departure to inform the Marcus decision is like saying 'I got a flat tire once so I know what a car accident feels like.'"

`reasoning_shape`: base_rate_statistical / representativeness

`expected_primary_models`: *Representativeness Heuristic*

`acceptable_secondary_models`: *Base Rates* (the user is using N=1 as if it's a base rate; secondary because the move is specifically about reference-class fit, not population statistics)

`should_reject_models`: *Hindsight Bias*, *Anchoring Bias*

`ambiguous`: no

`gold_ambiguity_note`: This is a textbook *Representativeness Heuristic* call-out — using one past case (Tom) as if it's representative of a different category of case (Marcus). The flat-tire/car-accident analogy literally operationalizes the misclassification.

### C5 — Exit math: opportunity cost with explicit numbers and mutual exclusion

`source_quotes`:
- Turn 4 ASSISTANT: "Your agency does $2.2M EBITDA. At 5x, that's an $11M exit... If Marcus leaves: [chain of consequences]. In that scenario, your EBITDA doesn't stay at $2.2M. It might drop to $1.5M or lower while you rebuild. And an agency with visible talent instability and declining capability doesn't get 5x. It gets 3x if you're lucky. So now you're looking at a $4.5-5M exit."
- Turn 4 ASSISTANT: "The difference between an $11M exit and a $5M exit is $6M. You're worried about giving away $1.3-2M to protect $6M of value."
- Turn 4 ASSISTANT: "Even a modest $2M ARR SaaS product could add $16-30M to your company's value at exit. Marcus's 15% of that upside is a bargain compared to him building it without you."

`reasoning_shape`: tradeoff_opportunity_sizing

`expected_primary_models`: *Opportunity Cost*

`acceptable_secondary_models`: *Second Order Thinking* (the cost of not-deciding chains through specific consequences); *Inversion* (testing the inverse exit-value scenario)

`should_reject_models`: *Sunk Cost Fallacy*, *Loss Aversion*

`ambiguous`: no

`gold_ambiguity_note`: Operationalization is the highest in this conversation — explicit dollar math, mutual-exclusion phrasing ("$1.3-2M to protect $6M"), and explicit comparison of paths. Per the case-4 OC update, the mutual-exclusion language alone should operationalize OC sufficiently.

### C6 — Founder's "I built this" emotional bias [GENUINELY AMBIGUOUS PRIMARY]

`source_quotes`:
- Turn 4 USER: "I built it from nothing. I remember when it was just me and a laptop in my apartment pitching clients. Marcus joined when we were already at $2M revenue with 12 people. He didn't build this. He joined something I built."
- Turn 4 USER: "Giving Marcus 15% means giving away $1.3-2M of that. That's real money."
- Turn 4 ASSISTANT: "You're running two calculations simultaneously and they're contradicting each other. Calculation one: Marcus is so important that losing him would cause 'a year of chaos, maybe worse.' Calculation two: Marcus doesn't deserve equity because he 'joined something I built.' Both of these cannot be true at the same time."
- Turn 4 ASSISTANT: "The version of the company that was 'just you' was worth $2M. The $9M in between — that's shared territory, whether or not the cap table reflects it."

`reasoning_shape`: framing_reframing / cognitive_bias_correction

`expected_primary_models`: **`gold_ambiguity_note: multiple defensible primaries`**
- *Sunk Cost Fallacy* — anchoring on past investment (18 months without salary, early risk) as if it controls the current decision. Defensible reading.
- *Endowment Effect* — overvaluing the equity because of ownership. Equally defensible.
- *Inversion* — the assistant's "two calculations contradicting" call-out is an inversion-shaped move (testing whether both beliefs can coexist; they can't).
- *Problem Framing And Reframing* — the "shared territory" / "$9M of growth happened with him as a central figure" reframe.

`acceptable_secondary_models`: any of the above not chosen as primary

`should_reject_models`: *Status Quo Bias*, *Confidence Calibration*

`ambiguous`: **yes**

`gold_ambiguity_note`: **This is the cluster that tests Lane 2 stability under genuine source ambiguity.** The conversation contains real founder-bias reasoning that doesn't map cleanly to a single 222 model. Different runs of Lane 2 may legitimately surface different models here (Sunk Cost Fallacy, Endowment Effect, or others) — none of those would be obviously wrong. **The "right" answer per the audit's discipline is: accept any of these as plausible, flag if Lane 2 forces something not on the list.** The current run's *Sunk Cost Fallacy* anchor falls within the acceptable range; whether it's the *best* read is genuinely contested.

### C7 — Pattern of proposing alternatives that avoid the actual question

`source_quotes`:
- Turn 6 ASSISTANT: "You've now proposed three different alternatives to what Marcus actually asked for: profit-sharing, retention bonus, higher salary. Each time, you're looking for a version of 'yes' that avoids giving him what he's asking for. That pattern suggests the resistance isn't about finding the right structure. It's about the fundamental question of whether you're willing to share ownership of this company with anyone. If the answer to that question is no, no structure will fix this."

`reasoning_shape`: framing_reframing / pattern_recognition

`expected_primary_models`: ambiguous — *Problem Framing And Reframing* OR `no_clean_primary`

`acceptable_secondary_models`: *Inversion* (testing whether the user's stated goal matches their behavior)

`should_reject_models`: *Sunk Cost Fallacy*

`ambiguous`: **yes**

`gold_ambiguity_note`: The cluster is calling out a behavioral pattern (3 alternatives proposed, all avoiding the actual ask) and reframing it as evidence about the user's deeper resistance. Could be PFR if we count the "your behavior reveals what you actually want" as a reframe. Could be `no_clean_primary` if we say this is wisdom about reading behavioral patterns that doesn't map to a 222 model. Marcin's call.

## Cluster summary (pre-attribution)

| Cluster | Primary | Ambiguity | Op level |
|---|---|---|---|
| C1 — Subsidy reframe | *Problem Framing And Reframing* | no | medium |
| C2 — Equity + platform tangled | *PFR* OR *Decomposition* (ambiguous) | yes | medium |
| C3 — Departure as competitive threat | *Second Order Thinking* | no | high |
| C4 — Tom wrong reference class | *Representativeness Heuristic* | no | high |
| C5 — Exit math opportunity cost | *Opportunity Cost* | no | high (numbers + mutual exclusion) |
| C6 — Founder "I built this" bias | **AMBIGUOUS: Sunk Cost / Endowment / Inversion / PFR all defensible** | **yes (gold-level ambiguity)** | medium-high |
| C7 — Three alternatives avoid the question | *PFR* OR `no_clean_primary` (ambiguous) | yes | medium |

### Counts

- 7 clusters
- 4 with non-ambiguous primary
- 3 with `gold_ambiguity_note` flagging genuine source-level underdetermination (C2, C6, C7)
- Distinct expected primary models in non-ambiguous set: *PFR*, *Second Order Thinking*, *Representativeness Heuristic*, *Opportunity Cost*

## Pre-registered F1''' prediction table

Operationalization levels: high / medium / low (per case 4 protocol).

| Cluster | Expected primary | Op level | F1''' prediction | Stability prediction |
|---|---|---|---|---|
| C1 | *Problem Framing And Reframing* | medium | **recall-risk** (PFR pattern N=4) | unstable across runs (PFR-shaped reasoning may surface different models) |
| C2 | *PFR* OR *Decomposition* | medium | **recall-risk for PFR; possibly accept for Decomposition** | unstable (Lane 2 may pick PFR or Decomposition or neither across runs) |
| C3 | *Second Order Thinking* | high | **accept** | stable (high op + named chain) |
| C4 | *Representativeness Heuristic* | high (named bias + analogy operationalization) | **accept** | stable (this is in current anchor set; should recur) |
| C5 | *Opportunity Cost* | high (numbers + mutual exclusion) | **accept** per case-4 update | stable |
| C6 | **AMBIGUOUS** | medium-high | **accept some primary** (Lane 2 will pick *something* — Sunk Cost, Endowment, or related — and may legitimately differ across runs) | **highly unstable** (this cluster is the engine of Marcus's low Accepted-pre stability — different defensible models per run) |
| C7 | *PFR* OR `no_clean_primary` | medium | **recall-risk** (PFR pattern); if `no_clean_primary` is the right read, no anchor surfaces | unstable |

### Pre-registered stability hypothesis

Marcus's low Accepted-pre (0.13 across N=3 runs) is consistent with **C6 being a genuine-ambiguity cluster** where different defensible models surface across runs. If attribution shows Lane 2's Sunk Cost Fallacy (or whatever this run picks) lands cluster-aligned to C6 with one of the defensible primaries, the cross-run instability is likely *honest hypothesis diversity* — different runs picking different valid reads, not the producer chain failing.

If instead Lane 2's anchors land on clusters where C6's "true" primary is actually clean (and Lane 2 just picked a wrong one), then the instability is producer-quality noise.

The case-4 finding on F1''' (operational language → accept) plus the case-3 finding (verifier accepts when source operationalizes) suggest Marcus C6 will produce *legitimate hypothesis diversity* — the source is genuinely contested, so different operational-language readings will pass at different times.

### What this case can decide (per Marcin's pre-registered branches)

**If Marcus shows low noisy-anchor rate, low strictness failure, but low friction yield due to recall/fingerprint churn:**
→ Architecture work points toward source/fingerprint decomposition and better recall substrate, not verifier prompt work.

**If Marcus shows multiple plausible gold clusters, acceptable anchors shifting across equally defensible interpretations:**
→ Lane 2 may need to expose hypothesis diversity, not chase one stable canonical anchor. (This is the case I'm predicting at C6.)

**If Marcus shows clear gold clusters, candidates present, verifier rejecting non-operational but valid mental models:**
→ F1''' survives but tells us the product needs a second path for interpretive models: "hypothesis-grade friction" alongside validated anchors.

Step 2 attribution will determine which of these branches fires.

## What I'm holding for step 2

- 7 clusters, 4 with non-ambiguous primary, 3 with `gold_ambiguity_note`.
- Pre-registered F1''' predictions: 1 accept, 4 recall-risk-or-ambiguous-primary, 2 high-confidence accept (C4 RH, C5 OC).
- Pre-registered stability prediction: C6 ambiguity is the likely engine of cross-run instability.
- After opening Lane 2 artifacts, attribution will compare actual anchors to gold clusters AND assess whether the ambiguity-clusters surface defensible options.
