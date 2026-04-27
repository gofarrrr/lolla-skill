# Source-first cluster labeling - `year-old-oncologist-accept`

Status: **STEP 1-3 only** (per design memo §6.1-§6.3). Lane 2 outputs (`result.json`, `companion_cheat_sheet`, `revised.txt`) NOT opened for this attribution step.

Case: `year-old-oncologist-accept`
Run timestamp: `20260425T121607Z`
Bucket hypothesis: false-positive risk control (industry job-offer decision where broad career/negotiation models may over-recall)
Source consulted: `conversation.txt` Turn 1-10 ASSISTANT messages only.

## Counter-labeler disclosure

Codex had prior conversational exposure to this case's archived anchor names from the corpus survey, so this is not a perfectly blind human-authored gold set. To reduce that bias, I ran two isolated subagent passes with `fork_context:false`. The subagents received only the pasted assistant turns, did not read files, and were not told the current Lane 2 anchors.

The blind passes converged on the same large reasoning clusters:

- separate the bundled decision into different questions
- test escape-vs-fit
- treat mother-time as finite and non-fungible
- treat the husband's real buy-in as the gating condition
- convert constraints into negotiated terms
- distinguish real duties from veto-level obligations
- preserve exit options under non-compete lock-in
- sequence due diligence before counteroffer/commitment

They disagreed mainly on exact model display names, often proposing plausible but non-substrate labels (`Bottleneck`, `Real Options`, `Critical Path`, `Problem Decomposition`). The reconciliation below maps those concepts to exact curated display names when the fit is clean, or uses `no_clean_primary` when forcing a 222-model label would inflate the gold set.

## Important calibration note

This calibration case should not be preloaded as "Theory Of Constraints and Decomposition are automatically false positives." The source-first reads surfaced narrow conditions where those models can be defensible:

- *Theory Of Constraints* is defensible only for the husband's buy-in as the non-workaround blocking condition. It should not get credit for generic career-decision complexity.
- *Decomposition* is acceptable only as a secondary lens for separating the bundled decision questions. It should not replace *Problem Framing And Reframing* as the primary model.
- *Batna* is acceptable only where the answer is reasoning about fallback/walk-away posture. It should not become a generic negotiation label.
- *Information Asymmetry* is primary only where the answer says decisive information is missing or controlled by another party and must be surfaced before commitment.

That is the anti-overfit move: we preserve flexibility where the source supports it, while making the evidence boundary explicit enough that broad lexical hits can still be rejected.

## Clusters

### C1 - Separate the bundled decision into different questions

`source_quotes`:
- Turn 1 ASSISTANT: "There's a career question (is this the right role for you professionally), a family question (what does 3 days/week away for years look like), and a financial question (what does the money buy and at what cost). These aren't the same question and they don't have the same answer."
- Turn 3 ASSISTANT: "I want to be careful to name it explicitly rather than fold it into a general "consider family" bucket."
- Turn 3 ASSISTANT: "The same logic doesn't apply as cleanly to the fellows or the husband."

`reasoning_shape`: framing_reframing

`expected_primary_models`: *Problem Framing And Reframing*

`acceptable_secondary_models`: *Decomposition* (the answer separates tangled decision dimensions, but the load-bearing move is reframing the decision boundary rather than merely breaking a task into parts)

`should_reject_models`: *Theory Of Constraints* (no single binding constraint is being named yet), *Opportunity Cost* (the tradeoff appears later, not in this framing move)

`ambiguous`: no

`note`: Both blind labelers found this cluster. The exact substrate primary is *Problem Framing And Reframing*, not the nonexistent "Problem Decomposition." *Decomposition* can receive secondary credit only if the evidence quote is this explicit separation of career/family/financial questions.

---

### C2 - Test escape-versus-fit with a counterfactual role

`source_quotes`:
- Turn 2 ASSISTANT: "The "stuck" feeling matters because taking a big role for the wrong reason — escape rather than fit — is how people end up 3 years in wishing they'd stayed."
- Turn 2 ASSISTANT: "The test question is: if Merck offered you a role that was a lateral move content-wise, still the same portfolio work you do now but with a commute, would you take it?"
- Turn 2 ASSISTANT: "If yes, it's genuinely a career-leverage move. If no, some of what's pulling you is the dissatisfaction, not the opportunity."
- Turn 3 ASSISTANT: "The "if it's escape not fit, stay" framing still holds"

`reasoning_shape`: diagnostic_counterfactual

`expected_primary_models`: *Inversion*

`acceptable_secondary_models`: *Problem Framing And Reframing* (the test reframes the decision motive), *Confidence Calibration* (secondary only if the surfaced pressure is about recalibrating confidence in the attraction to the role)

`should_reject_models`: *Status Quo Bias* (the answer is not saying she is irrationally attached to staying), *Sunk Cost Fallacy*, *Opportunity Cost*

`ambiguous`: no

`note`: One blind labeler proposed "Revealed Preference," which is not a curated display name. The closest clean substrate model is *Inversion*: remove the prestige/upside and test whether the role still attracts.

---

### C3 - Treat mother-time as finite and non-fungible

`source_quotes`:
- Turn 3 ASSISTANT: "Your mother's window is finite and not recoverable."
- Turn 3 ASSISTANT: "3-5 good years where visits mean something is a specific quantity of time, and any plan that makes monthly visits impossible is trading that specific quantity for money."
- Turn 3 ASSISTANT: "The money is large but not singular — other high-compensation roles exist at other points in your career. The mother-time doesn't."
- Turn 3 ASSISTANT: "Your mother is not negotiable in the same way."
- Turn 9 ASSISTANT: "add a timeline item specifically for your mother — before you say yes to Merck, know what the next 90 days of Chicago trips looks like under the flexible-day model."

`reasoning_shape`: tradeoff_opportunity_sizing

`expected_primary_models`: *Opportunity Cost*

`acceptable_secondary_models`: *Inversion* (secondary only if the answer frames the decision from the lost mother-time side), *Second Order Thinking* (secondary only for downstream schedule consequences)

`should_reject_models`: *Margin Of Safety*, *Power Dynamics*, *Theory Of Constraints*, *Decomposition*

`ambiguous`: no

`note`: This is the cleanest source-first primary. The answer explicitly prices a scarce, unrecoverable time window against money and career opportunity.

---

### C4 - Husband buy-in is the non-workaround constraint

`source_quotes`:
- Turn 2 ASSISTANT: "if the husband conversation hasn't happened, that's the thing that makes everything else speculative. Nothing downstream matters if that answer isn't clear."
- Turn 4 ASSISTANT: ""I will not stop you" is not the same answer as "yes.""
- Turn 4 ASSISTANT: "Having the real version of this conversation is load-bearing, and it matters that you do it before responding to Merck, not after."
- Turn 6 ASSISTANT: "If his real answer to that is yes, take the role. If his answer is "I'll try," that's a different conversation and possibly a different answer."
- Turn 6 ASSISTANT: "The thing that blocks yes is if the husband's answer is hedged. Everything else has a work-around. His buy-in doesn't."
- Turn 10 ASSISTANT: "The husband conversation is genuinely first. If his answer is hedged, you're not negotiating with Merck this week — you're back in conversation with him, and the rest of the list waits."

`reasoning_shape`: constraint_bottleneck

`expected_primary_models`: *Theory Of Constraints*

`acceptable_secondary_models`: *Information Asymmetry* (the real preference is not yet explicit), *Premortem* (secondary only for the later family check-in / failure-condition setup), *Power Dynamics* (secondary only if the household-load asymmetry is explicitly discussed)

`should_reject_models`: *Principal Agent Problem*, *Opportunity Cost*, *Status Quo Bias*

`ambiguous`: yes - accepted as primary only under a narrow evidence boundary.

`note`: This is the main countermeasure against overfitting. Before reading current Lane 2 artifacts, the blind labelers independently described this as a bottleneck/gating-constraint cluster. Because the substrate has no "Bottleneck" display name and *Theory Of Constraints* selects for a blocking dependency that caps the plan, *Theory Of Constraints* is defensible here. It should not receive credit anywhere else unless the evidence quote is this explicit husband-buy-in constraint.

---

### C5 - Convert constraints into negotiated terms

`source_quotes`:
- Turn 3 ASSISTANT: "is there a version of this Merck role that doesn't preclude Chicago trips? Two days a week in NJ instead of three? Remote-first with quarterly on-site?"
- Turn 4 ASSISTANT: "The answer here is to negotiate the start date. You don't start at Merck in 6 weeks, you start in 90 days."
- Turn 4 ASSISTANT: "A 3-day/week role that flexes to 2-days-on-Chicago-weeks is a different role from 3-days-in-NJ-nonnegotiable. I'd want that in writing from the hiring manager, not verbal."
- Turn 5 ASSISTANT: "Asking for 90 days, asking for a defined schedule with Chicago flexibility, asking for adjunct status at BAMC so your grants can transfer — all of these are normal. Merck expects it."
- Turn 6 ASSISTANT: "Negotiate the 90-day start date, the flexible-day schedule with Chicago weeks explicitly protected, and adjunct status at BAMC so your NIH grants transfer rather than closing."

`reasoning_shape`: option_design

`expected_primary_models`: *Optionality*

`acceptable_secondary_models`: *Batna* (secondary if the answer uses Merck's seriousness / walk-away posture), *Information Asymmetry* (secondary if the emphasis is getting schedule flexibility in writing), *Margin Of Safety* (secondary only for protective buffers around mother/patient/grants)

`should_reject_models`: *Theory Of Constraints* (not the primary here; the move is designing options, not naming one bottleneck), *Decomposition*, *Principal Agent Problem*

`ambiguous`: no

`note`: The repeated source move is not "negotiate hard" in the abstract. It is redesigning the offer so the threatened values remain possible: Chicago trips, Robert transition, grant continuity, and academic exit.

---

### C6 - Separate real duties from veto-level obligations

`source_quotes`:
- Turn 4 ASSISTANT: "On Robert: that's a specific duty to a specific person, not a general duty-of-care abstraction."
- Turn 4 ASSISTANT: "That covers Robert's protocol initiation and lets you transition him to someone clinically appropriate rather than mid-treatment."
- Turn 5 ASSISTANT: "there's a version of this where you're treating "mentor continuity" as a hard constraint and a version where you're treating it as a real cost worth naming but not a veto."
- Turn 5 ASSISTANT: "Priya has a committee. She has other people in the department. She will not fail because you leave."
- Turn 5 ASSISTANT: "She will have a harder second half of her fellowship, which is a real cost, but it's not the same as her career ending."
- Turn 5 ASSISTANT: "The "the other fellows will see it" thing is a status concern about how you leave, not a concern about whether you leave. Those are two different problems."

`reasoning_shape`: responsibility_triage

`expected_primary_models`: **`no_clean_primary`**

`acceptable_secondary_models`: *Problem Framing And Reframing* (the answer separates patient duty, fellow cost, and status concern), *Opportunity Cost* (secondary only if the lost mentorship capacity is explicitly priced)

`should_reject_models`: *Principal Agent Problem*, *Power Dynamics*, *Theory Of Constraints*, *Decomposition*

`ambiguous`: no - the primary is deliberately `no_clean_primary`.

`note`: This is important reasoning, but forcing a curated model would create a fake producer leak. The answer is doing moral-load triage: Robert is a specific duty with a transition solution; Priya is a real cost but not a veto; fellow perception is status/how-to-leave, not whether-to-leave.

---

### C7 - Non-compete changes the exit option set

`source_quotes`:
- Turn 7 ASSISTANT: "Adjunct status at BAMC keeps the door open — you can return to a senior academic role at 48 without starting from zero, especially if your NIH grants have transferred and you've stayed published."
- Turn 8 ASSISTANT: "That changes the framing of Merck-as-bridge. It's not a bridge to a better industry role; it's a 2-year lock-in to the specific company."
- Turn 8 ASSISTANT: "Your options on exit are: stay at Merck, return to academia, or leave the field (which isn't really an option). That narrows the back-up plan meaningfully."
- Turn 8 ASSISTANT: "the adjunct status at BAMC becomes more important, not less — it's your only clean exit if Merck goes sideways."
- Turn 8 ASSISTANT: "Because if you don't love the Merck role specifically, you're locked into it or you're going back to academia. There's no "try industry, pick a better version" route for 2 years."

`reasoning_shape`: commitment_reversibility

`expected_primary_models`: *Switching Costs*

`acceptable_secondary_models`: *Optionality* (adjunct status preserves one exit route), *Batna* (fallback comparison to academia), *Inversion* (secondary if the evidence is about testing the role under the lock-in downside)

`should_reject_models`: *Theory Of Constraints*, *Decomposition*, *Margin Of Safety*

`ambiguous`: no

`note`: One blind labeler proposed "Real Options," which is not a curated display name. The best exact substrate primary is *Switching Costs*: the non-compete makes the move less reversible and raises the cost of choosing wrong.

---

### C8 - Resolve missing deal facts before setting the counteroffer

`source_quotes`:
- Turn 8 ASSISTANT: "Have you spent time with the specific portfolio you'd be overseeing? Not the glossy overview but the actual compounds, the pipeline priorities, the people you'd be working with."
- Turn 8 ASSISTANT: "If you haven't, that's the piece of due diligence I'd front-load before signing."
- Turn 9 ASSISTANT: "get the non-compete reviewed by a lawyer you trust, not a Merck-provided one."
- Turn 9 ASSISTANT: "the 2-year window may be narrower or broader than the face language suggests depending on how "development" is defined."
- Turn 10 ASSISTANT: "the second Merck conversation (portfolio + team) should happen before you draft the counter-offer, not in parallel."
- Turn 10 ASSISTANT: "What you learn about the actual compounds and the people might change what you're asking for — a role you're lukewarm on warrants harder terms or a pass; a role you're excited about warrants asking for less and moving faster."
- Turn 10 ASSISTANT: "Don't anchor your counter before you know what you're countering for."

`reasoning_shape`: information_due_diligence

`expected_primary_models`: *Information Asymmetry*

`acceptable_secondary_models`: *Batna* (the counteroffer/walk-away posture depends on what diligence reveals), *Confidence Calibration* (secondary if the answer is about adjusting confidence in the role after better evidence), *Premortem* (secondary only if the evidence is about pressure-testing the flexible-day model before commitment)

`should_reject_models`: *Decomposition*, *Theory Of Constraints*, *Power Dynamics*

`ambiguous`: no

`note`: This cluster is about missing or other-party-controlled information: actual portfolio/team quality, non-compete scope, schedule promise, and how those facts change the counteroffer. *Information Asymmetry* should not get credit for generic uncertainty; it gets credit if the evidence quote points to concrete missing information that must be surfaced before commitment.

---

## Cluster summary (pre-attribution)

| Cluster | Primary | Secondary | False-positive boundary |
|---|---|---|---|
| C1 - Separate bundled decision | *Problem Framing And Reframing* | *Decomposition* | *Decomposition* secondary only; not primary |
| C2 - Escape-vs-fit test | *Inversion* | *Problem Framing And Reframing*, *Confidence Calibration* | Reject status-quo / sunk-cost readings |
| C3 - Mother-time tradeoff | *Opportunity Cost* | *Inversion*, *Second Order Thinking* | Reject generic risk/safety labels |
| C4 - Husband buy-in gate | *Theory Of Constraints* | *Information Asymmetry*, *Premortem*, *Power Dynamics* | *Theory Of Constraints* credit only for husband-as-blocking-condition evidence |
| C5 - Negotiated terms preserve values | *Optionality* | *Batna*, *Information Asymmetry*, *Margin Of Safety* | Reject generic negotiation/process labels |
| C6 - Duties vs vetoes | `no_clean_primary` | *Problem Framing And Reframing*, *Opportunity Cost* | Reject forced agency/power/constraint labels |
| C7 - Non-compete lock-in | *Switching Costs* | *Optionality*, *Batna*, *Inversion* | Reject generic decomposition/constraint labels |
| C8 - Missing deal facts before counteroffer | *Information Asymmetry* | *Batna*, *Confidence Calibration*, *Premortem* | Credit only for concrete missing-information/diligence evidence |

### Counts

- 8 clusters
- 7 with clean expected primary models
- 1 with non-ambiguous `no_clean_primary`
- Distinct expected_primary_models: 7 (*Problem Framing And Reframing*, *Inversion*, *Opportunity Cost*, *Theory Of Constraints*, *Optionality*, *Switching Costs*, *Information Asymmetry*)

### Pre-attribution hypothesis

This source-first pass is more generous to the current-looking broad models than the initial suspicion expected, but with narrow evidence boundaries.

If attribution shows that surfaced anchors use quotes aligned to C4/C8/C1/C7, then this case may be a trust positive control rather than a false-positive control: Lane 2 found broad models, but some broad models were genuinely active.

If attribution shows those same models attached to generic job-offer language, paraphrased quotes, or the wrong cluster, then the observed-anchor rows should classify them as `acceptable_*_with_quote_drift`, `noisy_adjacent`, or `false_positive` according to §7.2. The gold labels above should not let a broad anchor pass just because the display name appears somewhere in the file.

The key recurrence question remains: does this case repeat case 1's low-friction-yield pattern, or does it show that the system can surface defensible friction when the source contains strong gating/diligence/lock-in reasoning?
