# Source-first span labeling — `user-launch-independent-fintech`

Status: **STEP 1–3 only** (per design memo §6.1–§6.3). Lane 2 outputs (`result.json`, `companion_cheat_sheet`) NOT opened yet. `revised.txt` is Step 6 output and is also being held until Step 4.

Case: `user-launch-independent-fintech`
Run timestamp: `20260424T123050Z`
Bucket hypothesis: cleaner positive control (low anchor count, concrete runway/launch-plan logic)
Source consulted: `conversation.txt` Turn 1–8 ASSISTANT messages only.

## Honesty disclosure (author bias)

I (Claude) already saw this case's anchor set during the corpus-survey scan that produced the design memo's §4 table. I know `user-launch-independent-fintech` surfaced 2 anchors: *Margin Of Safety* and *Optimism Bias And Planning Fallacy*. I also briefly read `revised.txt` while sizing the case. That makes my source-first pass on this case impure.

Mitigation:
- For span labeling below, I worked off the original Turn 1–8 ASSISTANT text only.
- I will flag any span where my expected-model label might have been influenced by prior exposure to the anchor set.
- This is the second-cleanest run we have on protocol purity. The cleanest would have been a case I had not surveyed. Going forward, for cases I have not yet exposed myself to (the 3 false-positive risk + positive control cases that are not in our hot path), the source-first protocol can be honored fully if Marcin labels first.

## Spans

For brevity, `assistant_quote` excerpts the load-bearing portion; full quote is the assistant turn at the listed location.

### Span S1 — Turn 1 ASSISTANT: refusing to take the request at face value

`assistant_quote`: "Before diving into tactics, can I ask a few things to make sure we're solving the right problem... what's your current pipeline... the 8 months runway — does that assume zero revenue, or is there an assumed ramp... the 6-week transition — why 6 weeks specifically?"

`reasoning_shape`: framing_reframing

`expected_primary_models`: *Problem Framing And Reframing*

`acceptable_secondary_models`: *First Principles Thinking* (probing the underlying assumptions before accepting the surface request)

`should_reject_models`: none obvious

`ambiguous`: no

`bias_flag`: no — Problem Framing And Reframing is not in the surfaced anchor set, so this label was not biased toward what Lane 2 picked.

### Span S2 — Turn 2 ASSISTANT: base-rate on network conversions

`assistant_quote`: "the number of those conversations that convert to signed engagements in the first 3 months is typically less than 1 in 5, and often zero. You don't have a pipeline; you have a network that might become a pipeline."

`reasoning_shape`: base_rate_statistical

`expected_primary_models`: *Base Rates*

`acceptable_secondary_models`: *Optimism Bias And Planning Fallacy* (the user was treating informal interest as pipeline — that's optimism bias on conversion); *Confidence Calibration* (correcting the user's overconfidence in their pipeline)

`should_reject_models`: none obvious

`ambiguous`: no

`bias_flag`: *Optimism Bias And Planning Fallacy* is in the anchor set. I might be over-eager to surface it as secondary here. Marcin: please confirm whether Base Rates is the load-bearing read or whether Optimism Bias is.

### Span S3 — Turn 2 ASSISTANT: runway as safety buffer

`assistant_quote`: "8 months at zero revenue is tight for a first-time independent consultant. Industry experience suggests the first paid engagement often takes 3-5 months from launch... If you don't have an engagement by month 5, your remaining 3 months of runway pressure-cooks you into taking whatever comes along, which is usually badly-fit work."

`reasoning_shape`: commitment_reversibility (margin of safety in financial commitment)

`expected_primary_models`: *Margin Of Safety*

`acceptable_secondary_models`: *Second Order Thinking* (downstream consequence: pressure-cook → bad-fit work — the harm is two steps from the runway gap, not one)

`should_reject_models`: *Loss Aversion* (would be a tempting but wrong fit — this is about runway dynamics, not loss-framed psychology)

`ambiguous`: no

`bias_flag`: *Margin Of Safety* is in the anchor set. The assistant's word "tight" + the explicit math about 5+3 months supports Margin Of Safety as primary independently of what Lane 2 picked.

### Span S4 — Turn 2 ASSISTANT: trigger-condition timing

`assistant_quote`: "A better exit timing would be when you have at least one signed LOI or verbal commitment for an engagement that starts within 30-60 days of your last day. Launching without that is possible but harder than launching with it."

`reasoning_shape`: commitment_reversibility

`expected_primary_models`: *Margin Of Safety* (the signed LOI is the safety condition before the irreversible commitment)

`acceptable_secondary_models`: *Optionality* (waiting for the LOI preserves optionality on launch timing)

`should_reject_models`: none obvious

`ambiguous`: yes — could be argued as primarily *Optionality*. The reasoning is "don't pull the irreversible trigger until X condition is met," which is both Margin-of-Safety and Optionality flavored. Marcin's call.

`bias_flag`: yes. Margin Of Safety is in the anchor set; I'm conscious of that. Optionality is NOT in this case's anchor set but IS in `third-year-phd-student`'s. Either way, my label is influenced by knowing both.

### Span S5 — Turn 3 ASSISTANT: fundamentals before tactics

`assistant_quote`: "the tactical advice — pricing, positioning, website, legal structure — only matters if the fundamentals are solid. Right now the fundamentals are shaky in a specific way that a lot of first-time independents don't see until they're 4 months in and burning through savings."

`reasoning_shape`: framing_reframing OR constraint_bottleneck

`expected_primary_models`: *Problem Framing And Reframing* (refusing to optimize the wrong layer)

`acceptable_secondary_models`: *Theory Of Constraints* (the bottleneck is the foundation, not the surface tactics — fixing surface won't help)

`should_reject_models`: none obvious

`ambiguous`: yes — Problem Framing vs Theory Of Constraints is a real call. Both fit. Marcin's call.

`bias_flag`: no — neither is in this case's anchor set, so my label is not pulled toward Lane 2.

### Span S6 — Turn 4 ASSISTANT: three options with tradeoffs

`assistant_quote`: "Option 1: Delay launch by 2-3 months... Option 2: Launch on your current timeline but accept that months 1-3 are business development, not delivery... Option 3: Launch on current timeline but with a specific safety net — a part-time arrangement..."

`reasoning_shape`: option_design

`expected_primary_models`: *Optionality* (generating multiple paths with explicit tradeoffs)

`acceptable_secondary_models`: *Second Order Thinking* (each option's downstream consequence chain is explicitly named)

`should_reject_models`: *Decomposition* (would be a tempting but wrong fit — this is option-generation, not problem-decomposition)

`ambiguous`: no

`bias_flag`: no — Optionality is NOT in this case's anchor set. If the audit shows Optionality is missing here, that is a real producer leak finding, not a labeling artifact.

### Span S7 — Turn 5 ASSISTANT: concept-level vs specific-level alignment

`assistant_quote`: "If your spouse hasn't seen the specific math, their on-board-ness is for a concept, not for the reality... Supportive-in-concept but not-aligned-on-specifics is exactly how couples end up fighting about money six months into a new business."

`reasoning_shape`: incentives_agency OR systems_feedback (the misalignment compounds over time)

`expected_primary_models`: ambiguous — possibly *Information Asymmetry* (one party has the math, the other doesn't), possibly *Second Order Thinking* (the downstream-conflict prediction)

`acceptable_secondary_models`: *Principal Agent Problem* (stretches: spouse as principal whose information set differs)

`should_reject_models`: none obvious

`ambiguous`: yes — multiple plausible primaries, none clean. Marcin's call.

`bias_flag`: no — neither candidate is in this case's anchor set.

### Span S8 — Turn 6 ASSISTANT: fractional tradeoff

`assistant_quote`: "The tradeoff: fractional work locks you into a company's cadence, makes it harder to take on larger client engagements, and tends to pay less per hour than project work. But it's the de-risking move for month 1 if you don't have signed project engagements."

`reasoning_shape`: tradeoff_opportunity_sizing

`expected_primary_models`: *Opportunity Cost* (fractional vs project work, explicitly framed as tradeoff)

`acceptable_secondary_models`: *Margin Of Safety* (de-risking framing)

`should_reject_models`: none obvious

`ambiguous`: no

`bias_flag`: no — Opportunity Cost is NOT in this case's anchor set. If Opportunity Cost is missing in Lane 2 output, that's a finding worth attributing.

### Span S9 — Turn 7 ASSISTANT: pre-registered checkpoint with conditions

`assistant_quote`: "If after 4 weeks you have zero fractional commitments and your spouse is not aligned on the 5-months-of-revenue-pressure reality, push back by 2-3 months. That's not failure; that's responding to signal."

`reasoning_shape`: commitment_reversibility OR option_design

`expected_primary_models`: *Premortem* (decide now what would make you reverse — that's pre-registered failure conditions)

`acceptable_secondary_models`: *Optionality* (preserves the option to delay)

`should_reject_models`: none obvious

`ambiguous`: yes — Premortem vs Optionality is a real call.

`bias_flag`: no — neither is in this case's anchor set.

### Span S10 — Turn 7 ASSISTANT: filter nervousness from signal

`assistant_quote`: "Don't push back just because you're nervous. Push back only if the fundamentals haven't come together. The nervousness is always there; it's not good information by itself."

`reasoning_shape`: evidence_calibration

`expected_primary_models`: ambiguous — possibly *Confidence Calibration* (separating gut-feel from evidence-based confidence), possibly nothing in the 222 corpus that fits cleanly

`acceptable_secondary_models`: none clean

`should_reject_models`: none obvious

`ambiguous`: yes — may be a span where the right answer is "no clean primary model."

`bias_flag`: no — Confidence Calibration is NOT in this case's anchor set.

## Initial summary (pre-attribution)

10 spans identified across Turn 1–8 ASSISTANT.

### Expected primary models surfaced from the source pass

| Model (display_name) | Spans | In current Lane 2 anchor set? |
|---|---|---|
| Problem Framing And Reframing | S1, S5 | no |
| Base Rates | S2 | no |
| Margin Of Safety | S3, S4 | **yes** |
| Optionality | S6 | no |
| Premortem | S9 | no |
| Information Asymmetry / Second Order Thinking | S7 (ambiguous) | no |
| Opportunity Cost | S8 | no |
| Confidence Calibration | S10 (ambiguous) | no |
| Theory Of Constraints | S5 (acceptable_secondary) | no |

### Anchor I expected from corpus survey but didn't independently land

*Optimism Bias And Planning Fallacy* — I noted it as `acceptable_secondary` on S2 (base-rate span) with a bias flag. I did NOT independently land on it as a primary on any span from the source-first pass. That is a finding worth holding for step 4 attribution: did Lane 2 surface it because of a span I missed, or because the keyword recall hit a generic "optimism / planning" pattern in the conversation?

### Counts

- 10 spans
- 7 spans with non-ambiguous primary
- 3 spans flagged ambiguous
- Distinct expected_primary_models: 8

## What this means before opening Lane 2 outputs

Pre-attribution, the source-first pass suggests this case is reasoning-rich (10 spans, 8 distinct primary models) but Lane 2 only surfaced 2 anchors. **If those 2 anchors map to spans that have my labels of *Margin Of Safety* (S3, S4) and *Optimism Bias And Planning Fallacy* (S2 acceptable_secondary), then Lane 2 is correctly hitting the most defensible ones — but is missing 6 other primary-eligible spans entirely.**

That is the hypothesis to test in step 4: is Lane 2 a high-precision low-recall picker on this case, or is it picking the right 2 *because* the conversation only had ~2 strong moves and I am over-counting spans?

This is exactly the kind of question the audit is designed to answer. I am stopping here per protocol §6.4 — Marcin reviews this draft, especially the ambiguous spans (S4, S5, S7, S9, S10) and the bias flags on S2 and S4. After Marcin's review and any corrections to the gold set, I open `result.json`, `companion_cheat_sheet`, and `revised.txt`, attribute hits/misses/false positives, and produce the audit table for this case.

## Open questions for Marcin

1. **Is 10 spans too granular?** I split fairly aggressively. If you'd prefer ~5-7 spans per case (one per turn-level reasoning move), say so and I'll re-cluster.
2. **Span S7 (spouse alignment)** — is there a 222 model that fits cleanly here, or is this a case of "no clean primary"? *Information Asymmetry* and *Second Order Thinking* both stretch.
3. **Span S5 (fundamentals before tactics)** — your call: *Problem Framing And Reframing* (refusing to optimize the wrong layer) vs *Theory Of Constraints* (the bottleneck is the foundation).
4. **Span S10 (filter nervousness)** — is *Confidence Calibration* the right read, or is this a span where "no clean primary" is the honest label?
5. **Bias flag on S2** — was I right that *Base Rates* is primary and *Optimism Bias* is secondary, or should they swap?
6. **Author-bias mitigation going forward.** For the cases I have not yet seen the anchor set on (`year-old-oncologist-accept`, `mid-level-consultant-report`), should you label spans first and have me attribute against your gold set? That would close the source-first hole.
