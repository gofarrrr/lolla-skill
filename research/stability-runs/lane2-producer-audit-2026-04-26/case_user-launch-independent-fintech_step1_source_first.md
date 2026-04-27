# Source-first cluster labeling — `user-launch-independent-fintech`

Status: **STEP 1–3 only** (per design memo §6.1–§6.3). Lane 2 outputs (`result.json`, `companion_cheat_sheet`, `revised.txt`) NOT opened yet.

Case: `user-launch-independent-fintech`
Run timestamp: `20260424T123050Z`
Bucket hypothesis: cleaner positive control (low anchor count, concrete runway/launch-plan logic)
Source consulted: `conversation.txt` Turn 1–8 ASSISTANT messages only.

## Revision note

This is a v2 rewrite of the source-first pass. The v1 draft over-split the assistant's reasoning into 10 spans, which biased the audit toward "Lane 2 has terrible recall." The v2 clustering uses ~7 anchor-worthy reasoning clusters per Marcin's verdict, on the rule:

> The audit unit is a load-bearing reasoning cluster that deserves a mental-model anchor, not every reasoning sentence. A good answer can contain 10 reasoning moves; Lane 2 is not supposed to surface 10 anchors.

Cluster IDs C1–C7 are durable. The underlying source quotes from v1 (S1–S10) are preserved inside the clusters that absorb them, so the original granular labeling is recoverable if needed for debugging.

## Honesty disclosure (author bias)

Claude already saw this case's anchor set during the corpus-survey scan that produced the design memo's §4 table. I worked off the original Turn 1–8 ASSISTANT text only for cluster labeling, but my prior exposure to the anchor set means this case is not a clean source-first run. The proposed mitigation (now in design memo §12.4) is that Marcin do the source-first cluster pass on at least one false-positive risk control case (`year-old-oncologist-accept`) before Claude attribution, as a cross-labeler calibration check.

## Clusters

### C1 — Refuse tactics-first framing

`source_quotes` (from S1, S5):
- Turn 1 ASSISTANT: "Before diving into tactics, can I ask a few things to make sure we're solving the right problem... what's your current pipeline... the 8 months runway — does that assume zero revenue, or is there an assumed ramp... the 6-week transition — why 6 weeks specifically?"
- Turn 3 ASSISTANT: "the tactical advice — pricing, positioning, website, legal structure — only matters if the fundamentals are solid. Right now the fundamentals are shaky in a specific way that a lot of first-time independents don't see until they're 4 months in and burning through savings."

`reasoning_shape`: framing_reframing

`expected_primary_models`: *Problem Framing And Reframing*

`acceptable_secondary_models`: *Theory Of Constraints* (the foundation is the binding constraint; surface tactics can't fix it)

`should_reject_models`: none

`ambiguous`: no

`bias_flag`: no — neither model is in this case's anchor set.

`note`: Turn 1's pipeline/runway/timing questions and Turn 3's "fundamentals before tactics" pushback are the same structural move (refusing to accept the launch-plan request at face value). Treating them as one cluster is right; they were S1+S5 in v1.

---

### C2 — Network interest is not pipeline (base-rate correction)

`source_quotes` (from S2):
- Turn 2 ASSISTANT: "the number of those conversations that convert to signed engagements in the first 3 months is typically less than 1 in 5, and often zero. You don't have a pipeline; you have a network that might become a pipeline."

`reasoning_shape`: base_rate_statistical

`expected_primary_models`: *Base Rates*

`acceptable_secondary_models`: *Optimism Bias And Planning Fallacy* (the user was treating informal interest as pipeline — that's optimism bias, but the assistant's *move* is base-rate correction)

`should_reject_models`: none

`ambiguous`: no

`bias_flag`: yes — *Optimism Bias And Planning Fallacy* is in this case's anchor set; I noted this in v1. Marcin's call confirmed: *Base Rates* primary, *Optimism Bias And Planning Fallacy* secondary.

---

### C3 — Runway as safety buffer + signed-LOI as exit trigger

`source_quotes` (from S3, S4):
- Turn 2 ASSISTANT: "8 months at zero revenue is tight for a first-time independent consultant... If you don't have an engagement by month 5, your remaining 3 months of runway pressure-cooks you into taking whatever comes along, which is usually badly-fit work."
- Turn 2 ASSISTANT: "A better exit timing would be when you have at least one signed LOI or verbal commitment for an engagement that starts within 30-60 days of your last day. Launching without that is possible but harder than launching with it."

`reasoning_shape`: commitment_reversibility

`expected_primary_models`: *Margin Of Safety*

`acceptable_secondary_models`: *Optionality* (waiting for the LOI preserves optionality, but the load-bearing function is safety threshold)

`should_reject_models`: *Loss Aversion* (tempting wrong fit — this is runway dynamics, not loss-framed psychology)

`ambiguous`: no

`bias_flag`: yes — *Margin Of Safety* is in this case's anchor set. The "tight" + explicit 5+3-months math supports it independently of Lane 2.

`note`: v1 split the runway claim (S3) and the LOI exit-trigger (S4) into separate spans. They're the same structural move: "preserve a buffer before the irreversible commitment." One cluster.

---

### C4 — Three launch paths with explicit tradeoffs

`source_quotes` (from S6):
- Turn 4 ASSISTANT: "Option 1: Delay launch by 2-3 months... Option 2: Launch on your current timeline but accept that months 1-3 are business development, not delivery... Option 3: Launch on current timeline but with a specific safety net — a part-time arrangement..."

`reasoning_shape`: option_design

`expected_primary_models`: *Optionality*

`acceptable_secondary_models`: *Second Order Thinking* (each option's downstream consequence chain is explicitly named)

`should_reject_models`: *Decomposition* (tempting wrong fit — this is option-generation, not problem-decomposition)

`ambiguous`: no

`bias_flag`: no — *Optionality* is NOT in this case's anchor set. If C4 expects Optionality and Lane 2 missed it, that is a real producer-leak finding.

---

### C5 — Spouse alignment on specifics, not concept

`source_quotes` (from S7):
- Turn 5 ASSISTANT: "If your spouse hasn't seen the specific math, their on-board-ness is for a concept, not for the reality... Supportive-in-concept but not-aligned-on-specifics is exactly how couples end up fighting about money six months into a new business."

`reasoning_shape`: incentives_agency / systems_feedback (misalignment compounds over time)

`expected_primary_models`: **`no_clean_primary`** — this is real and important advice but no 222 model fits cleanly as primary. *Information Asymmetry* and *Second Order Thinking* both stretch; *Principal Agent Problem* is forced.

`acceptable_secondary_models`: *Information Asymmetry* (one party has the math, one doesn't)

`should_reject_models`: *Principal Agent Problem* (would be a stretch — spouse is not an agent in the principal-agent sense)

`ambiguous`: no (the cluster is non-ambiguous — its primary is `no_clean_primary`)

`bias_flag`: no — none of the candidates are in this case's anchor set.

`note`: This cluster tests the §6.3 rule that `no_clean_primary` is a valid label. If we forced *Information Asymmetry* in here, the audit would later show "Lane 2 missed Information Asymmetry on this case" — but that would be a labeling artifact, not a real leak. The cluster doesn't deserve an anchor.

---

### C6 — Fractional work tradeoff

`source_quotes` (from S8):
- Turn 6 ASSISTANT: "The tradeoff: fractional work locks you into a company's cadence, makes it harder to take on larger client engagements, and tends to pay less per hour than project work. But it's the de-risking move for month 1 if you don't have signed project engagements."

`reasoning_shape`: tradeoff_opportunity_sizing

`expected_primary_models`: *Opportunity Cost*

`acceptable_secondary_models`: *Margin Of Safety* (de-risking framing)

`should_reject_models`: none

`ambiguous`: no

`bias_flag`: no — *Opportunity Cost* is NOT in this case's anchor set. If Lane 2 missed it on C6, that is a real producer-leak finding.

---

### C7 — Pre-registered checkpoint and signal discipline

`source_quotes` (from S9, S10):
- Turn 7 ASSISTANT: "If after 4 weeks you have zero fractional commitments and your spouse is not aligned on the 5-months-of-revenue-pressure reality, push back by 2-3 months. That's not failure; that's responding to signal."
- Turn 7 ASSISTANT: "Don't push back just because you're nervous. Push back only if the fundamentals haven't come together. The nervousness is always there; it's not good information by itself."

`reasoning_shape`: commitment_reversibility (pre-registered conditions for reversal)

`expected_primary_models`: *Premortem*

`acceptable_secondary_models`: *Confidence Calibration* (separating gut-feel from evidence-based confidence — supports the primary but is too thin alone)

`should_reject_models`: none

`ambiguous`: no

`bias_flag`: no — neither candidate is in this case's anchor set.

`note`: v1 split S9 (decision rule with conditions) and S10 (filter nervousness from signal) into separate spans. They're the same structural move: pre-register what would change your mind, then filter noise from signal against that pre-registration. *Confidence Calibration* alone (S10 in v1) is too thin to count as primary; folded as secondary supporting the *Premortem* primary.

---

## Cluster summary (pre-attribution)

| Cluster | Primary | Secondary | In current Lane 2 anchor set? |
|---|---|---|---|
| C1 — Refuse tactics-first | *Problem Framing And Reframing* | *Theory Of Constraints* | no |
| C2 — Base-rate correction | *Base Rates* | *Optimism Bias And Planning Fallacy* | secondary in set |
| C3 — Runway + LOI safety | *Margin Of Safety* | *Optionality* | **primary in set** |
| C4 — Three launch paths | *Optionality* | *Second Order Thinking* | no |
| C5 — Spouse alignment | `no_clean_primary` | *Information Asymmetry* | no |
| C6 — Fractional tradeoff | *Opportunity Cost* | *Margin Of Safety* | no |
| C7 — Pre-registered checkpoint | *Premortem* | *Confidence Calibration* | no |

### Counts (v2)

- 7 clusters
- 6 with non-ambiguous primary, 1 (`C5`) with non-ambiguous `no_clean_primary`
- 0 ambiguous clusters (down from 5 in v1)
- Distinct expected_primary_models: 6 (Problem Framing And Reframing, Base Rates, Margin Of Safety, Optionality, Opportunity Cost, Premortem)

### Pre-attribution hypothesis

The v2 clustering surfaces **6 anchor-worthy primary models**. Lane 2's current output has **2 anchors** (*Margin Of Safety* and *Optimism Bias And Planning Fallacy*).

If the attribution step (§6.4) confirms that:
- Lane 2 correctly hits C3 (*Margin Of Safety* primary) — high precision on the strongest cluster
- Lane 2 surfaces *Optimism Bias And Planning Fallacy* on C2 (where it's secondary, with *Base Rates* primary) — partial credit; primary missed, secondary lens hit
- Lane 2 misses C1, C4, C6, C7 entirely

…then this case shows Lane 2 as **medium-precision low-recall** — correctly hitting the most defensible cluster but missing 4 anchor-worthy reasoning structures. That's a recall finding worth attributing to fingerprint vs recall vs verifier.

If instead Lane 2's *Optimism Bias And Planning Fallacy* is firing on a span outside C2 (a false-positive lexical hit on the conversation's general "optimism / planning" texture), the attribution should record that observed-anchor row as `noisy_adjacent` or `false_positive`.

This is exactly the kind of question the audit is designed to answer. Stopping here per protocol §6.4 — Marcin reviews the cluster table, primaries, and `no_clean_primary` call on C5 before Claude opens `result.json`, `companion_cheat_sheet`, and `revised.txt`.

## Open questions for Marcin (v2)

1. **C5 (`no_clean_primary`).** Is this the right call, or do you want *Information Asymmetry* promoted to primary? My v2 reading is that no clean primary is correct; the rule's existence is what protects against label inflation.
2. **C7 (Premortem).** Premortem is a defensible read but the cluster is also doing some "tripwire / stop-loss" work that doesn't have a clean 222 corresponding model. If Premortem feels stretched, `no_clean_primary` is also defensible. Your call.
3. **PR cadence confirmed.** Per your verdict: hold the branch, one PR when all 7 cases are labeled and the leak map exists. I will not open a draft PR.
4. **Calibration case.** Confirming you'll do the source-first cluster pass on `year-old-oncologist-accept` before I attribute it. Easiest workflow: you drop a `case_year-old-oncologist-accept_step1_source_first.md` in the same directory, I work from your gold set.
