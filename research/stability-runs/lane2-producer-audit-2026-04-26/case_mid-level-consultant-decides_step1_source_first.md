# Source-first cluster labeling — `mid-level-consultant-decides`

Status: **STEP 1–3 only** (per design memo §6.1–§6.3). Lane 2 outputs (`result.json`, `companion_cheat_sheet`, `revised.txt`) NOT opened for this case.

Case: `mid-level-consultant-decides`
Run timestamp: `20260425T110621Z`
Bucket hypothesis: failure-rich (whistleblower / regulatory ethical decision; lowest Step 6 consumption rate at 20% in the existing attribution synthesis)
Source consulted: `conversation.txt` Turn 1–14 ASSISTANT messages only.

## Honesty disclosure (heavy author bias on this case)

Claude has seen this case's anchor set MANY times in this session — it has been the recurring example throughout the Path D wording-contract work, and Claude has read drafted Step 6 outputs for it during the live-validation cycles. The current Lane 2 anchors (5 of them) are deeply familiar.

Mitigation: clusters and primaries below are derived from re-reading `conversation.txt` Turn 1–14 ASSISTANT only. Where my knowledge of the anchor set could shape a label, I've flagged it. The strongest discipline is the family-prediction table at the end (§"Predictions per Marcin's family hypothesis") — those predictions are made *before* opening `result.json` and provide a check on whether attribution conforms to the hypothesis or breaks it.

## Clusters

### C1 — Probabilistic obstruction read (likely-but-not-certain)

`source_quotes`:
- Turn 2 ASSISTANT: "A reasonable person would conclude this is likely obstruction-related conduct. I want to be careful not to conclude it definitively — there's a non-zero chance there's a legitimate explanation (he was destroying duplicates after an official retention decision, he was destroying personal work product, etc). But the timing and location make any benign explanation hard to believe."

`reasoning_shape`: evidence_calibration

`expected_primary_models`: *Probabilistic Thinking*

`acceptable_secondary_models`: *Confidence Calibration* (related but secondary — the move is holding multiple probability-weighted outcomes simultaneously, not pre-committing a confidence threshold)

`should_reject_models`: *Authority Bias* (user is calibrating evidence, not deferring to authority), *Status Quo Bias*

`ambiguous`: no

`bias_flag`: yes — *Probabilistic Thinking* is in this case's anchor set. I'm conscious that my clean-primary call here may be biased toward what I expect Lane 2 to have surfaced.

### C2 — Three-dimensional decomposition of the decision

`source_quotes`:
- Turn 3 ASSISTANT: "The shape of the decision has three major dimensions you need to hold at once. One: legal exposure if you don't report... Two: career consequences... Three: moral and practical consequences of not reporting."

`reasoning_shape`: framing_reframing

`expected_primary_models`: *Problem Framing And Reframing*

`acceptable_secondary_models`: *Decomposition* (the answer literally separates the decision into three dimensions; *Decomposition* receives secondary credit only if the evidence quote IS this explicit three-way decomposition, per the same narrow-boundary rule from C1 of the oncologist case)

`should_reject_models`: *Theory Of Constraints* (no single binding constraint named here), *Opportunity Cost*

`ambiguous`: no

`bias_flag`: no — *Problem Framing And Reframing* is NOT in this case's anchor set. If Lane 2 missed it, that's a real producer leak finding (and same as case 2 C1).

### C3 — External-with-counsel preserves information asymmetry over the partner

`source_quotes`:
- Turn 4 ASSISTANT: "An internal report in a situation like this is likely to tip off the partner you saw, giving him time to construct a cover story."
- Turn 4 ASSISTANT: "your most protected path is probably a whistleblower attorney who files on your behalf with the regulator, anonymously to the firm. This preserves your current job as long as possible and provides the strongest legal shield."
- Turn 8 ASSISTANT: "Do not do any of your own investigation."
- Turn 9 ASSISTANT: "Canceling unusually would be noticeable... investigators will eventually ask what you did between Thursday and the filing; 'attended regular meetings, did my job, told no one' is a clean answer."

`reasoning_shape`: incentives_agency

`expected_primary_models`: *Information Asymmetry*

`acceptable_secondary_models`: *Second Order Thinking* (the "tip off → cover story" chain is downstream-consequence reasoning), *Premortem* (secondary only for the "investigators will eventually ask" forward-tracing)

`should_reject_models`: *Power Dynamics* (this is information topology, not a power game)

`ambiguous`: no

`bias_flag`: yes — *Information Asymmetry* is in this case's anchor set. The cluster is structurally the strongest fit for that model in the entire conversation, but I'm aware I'm pulled toward it by exposure.

### C4 — Principal-Agent Problem on GC (firm incentives override individual integrity)

`source_quotes`:
- Turn 5 ASSISTANT: "Internal is worse when: (a) the conduct involves a senior partner, which means firm leadership has financial and political incentives to minimize..."
- Turn 5 ASSISTANT: "Internal reporting requires you to trust that the general counsel will take action against a senior partner who likely has significant revenue and political weight. That's possible but not the way to bet."
- Turn 6 ASSISTANT: "I'm not saying your GC is corrupt; I'm saying the weight of institutional inertia at firms like yours usually produces 'quiet handling' for senior partners even when GCs mean well."

`reasoning_shape`: incentives_agency

`expected_primary_models`: *Principal Agent Problem*

`acceptable_secondary_models`: *Authority Bias* (the user's instinct to trust the GC because GC = authority is a related lens; the assistant's pushback uses PAP to reframe authority deference as institutional-incentive-misalignment), *Information Asymmetry* (the user has info GC doesn't, but PAP is the load-bearing read), *Power Dynamics* (firm leadership has political weight; secondary only)

`should_reject_models`: *Theory Of Constraints* (no single bottleneck being named)

`ambiguous`: no

`bias_flag`: yes — *Principal Agent Problem* and *Authority Bias* are both in this case's anchor set. The PAP fit is strong from source; the AB fit is acceptable_secondary at most.

### C5 — Pre-registered confidence threshold for internal vs external

`source_quotes`:
- Turn 5 ASSISTANT: "Test it this way: if the general counsel got a report about a senior partner, how confident are you that action would actually follow? If you're 90%+ confident, internal first is reasonable. If you're 70% or below, external-with-counsel is safer."
- Turn 6 ASSISTANT: "At 60-65% confidence in internal handling, with a senior partner involved, external-with-counsel is the defensible path."

`reasoning_shape`: evidence_calibration

`expected_primary_models`: *Confidence Calibration*

`acceptable_secondary_models`: *Probabilistic Thinking* (related; the threshold IS a probability rule, but the move is pre-commitment of an action rule, which is calibration-flavored)

`should_reject_models`: *Status Quo Bias* (the user is not anchored on the status quo here)

`ambiguous`: no — *Probabilistic Thinking* and *Confidence Calibration* are different moves on different clusters (C1 = probabilistic reading of evidence; C5 = pre-committed confidence threshold). Marcin's "one primary per reasoning move" rule supports treating them separately.

`bias_flag`: yes — *Confidence Calibration* is in this case's anchor set.

### C6 — "Career" reframe: the specific version vs the underlying career

`source_quotes`:
- Turn 12 ASSISTANT: "Whether it 'costs' you the career depends on what you think your career is. If the career is 'senior consultant at a large firm in this specific vertical,' yes, likely. If the career is 'professional who helps organizations do things right,' that career opens up in different places — regulatory work, internal audit at a client company, compliance roles, even teaching or writing."
- Turn 12 ASSISTANT: "I just want to distinguish 'career ended' from 'this specific version of the career ended.' The second is true; the first usually isn't."

`reasoning_shape`: framing_reframing

`expected_primary_models`: *Problem Framing And Reframing*

`acceptable_secondary_models`: *Optionality* (alternative paths exist outside the current vertical; secondary only)

`should_reject_models`: *Status Quo Bias*, *Sunk Cost Fallacy* (tempting but the move is reframing, not loss-aversion correction)

`ambiguous`: no

`bias_flag`: no — *Problem Framing And Reframing* is NOT in this case's anchor set. Same producer-leak hypothesis as C2.

### C7 — Premortem on future self-doubt + clarity-write-down baseline

`source_quotes`:
- Turn 14 ASSISTANT: "in the months ahead, you're going to second-guess this decision repeatedly. You'll wonder if you imagined what you saw, if there was a benign explanation, if you're destroying your career for nothing. That's normal."
- Turn 14 ASSISTANT: "Write down tonight exactly what you saw — clear, specific, first-person — and read it when you're doubting yourself. Your future self will need your present self's clarity more than you realize."

`reasoning_shape`: commitment_reversibility (pre-registering a clarity baseline before doubt sets in)

`expected_primary_models`: *Premortem*

`acceptable_secondary_models`: *Confidence Calibration* (separating future emotional doubt from present-state evidence)

`should_reject_models`: *Status Quo Bias*, *Hindsight Bias*

`ambiguous`: no

`bias_flag`: no — *Premortem* is NOT in this case's anchor set. Same as case 1 C7.

### C8 — Refuse responsibility for someone else's prior non-decision (`no_clean_primary`)

`source_quotes`:
- Turn 7 ASSISTANT: "If she saw something and didn't report, that's her decision and her consequence. Your obligation is based on what you saw, not on protecting her from what she may have seen."
- Turn 7 ASSISTANT: "If you don't report because you're worried about implicating her, you've let someone else's non-reporting control your own. That's a hard standard to hold over time."

`reasoning_shape`: incentives_agency / other

`expected_primary_models`: **`no_clean_primary`**

`acceptable_secondary_models`: *Boundaries* (stretches; the cluster is about responsibility-scoping, not interpersonal limits)

`should_reject_models`: *Principal Agent Problem* (the senior manager is not an agent of the user)

`ambiguous`: no — primary is deliberately `no_clean_primary`. This is real reasoning, but forcing a 222 model would inflate the gold set. Same discipline as oncologist C6 (duties vs vetoes triage).

## Cluster summary (pre-attribution)

| Cluster | Primary | Secondary | Key boundary |
|---|---|---|---|
| C1 — Probabilistic obstruction read | *Probabilistic Thinking* | *Confidence Calibration* | Holding multiple outcomes, not pre-committing a threshold |
| C2 — Three-dimensional decomposition | *Problem Framing And Reframing* | *Decomposition* | *Decomposition* secondary only if quote IS the explicit three-way separation |
| C3 — External preserves information asymmetry | *Information Asymmetry* | *Second Order Thinking*, *Premortem* | Information topology, not power |
| C4 — Principal-Agent on GC | *Principal Agent Problem* | *Authority Bias*, *Information Asymmetry*, *Power Dynamics* | Institutional-incentive misalignment, not authority deference |
| C5 — 90/70 pre-registered threshold | *Confidence Calibration* | *Probabilistic Thinking* | Pre-committed action rule, not just probabilistic reading |
| C6 — Career reframe | *Problem Framing And Reframing* | *Optionality* | Reframing what "career" means, not optionality-on-paths |
| C7 — Premortem on future self-doubt | *Premortem* | *Confidence Calibration* | Pre-registering clarity baseline against future doubt |
| C8 — Other-person responsibility refusal | `no_clean_primary` | — | Anchor-worthiness rule applied: real reasoning, no clean 222 fit |

### Counts

- 8 clusters
- 7 with non-ambiguous expected primary
- 1 (`C8`) with non-ambiguous `no_clean_primary`
- Distinct expected_primary_models: 6 (*Probabilistic Thinking*, *Problem Framing And Reframing* ×2, *Information Asymmetry*, *Principal Agent Problem*, *Confidence Calibration*, *Premortem*)

## Predictions per Marcin's family hypothesis

This table is recorded **before opening Lane 2 outputs** as a pre-registered diagnostic check on the family hypothesis from cross-case discussion (case 1 + case 2). The hypothesis: externally legible dependency / diligence / buffer models pass the verifier; interpretive / counterfactual / option / comparative-value models miss.

| Cluster | Expected primary | Predicted family | Predicted verifier behavior |
|---|---|---|---|
| C1 | *Probabilistic Thinking* | calibration / abstract-cognitive (new family — adjacent to interpretive but distinct) | **REJECTED predicted** (the move is "hold multiple probability-weighted outcomes simultaneously" — a cognitive operation, not a concrete external mechanism) |
| C2 | *Problem Framing And Reframing* | interpretive / reframing | **REJECTED predicted** (PFR rejected on cases 1 and 2) |
| C3 | *Information Asymmetry* | external-information / diligence | **ACCEPTED predicted** (IA accepted cleanly on case 2 C8) |
| C4 | *Principal Agent Problem* | agency / incentive-structure | **STRESS TEST** — agency models are not yet established. Could pass if verifier reads PAP as concrete incentive-misalignment mechanism ("firm rewards X, GC reports to firm"); could miss if verifier reads it as interpretive social-structure reasoning. **Hold the prediction explicitly open.** |
| C5 | *Confidence Calibration* | calibration / abstract-cognitive | **REJECTED predicted** (same family as C1) |
| C6 | *Problem Framing And Reframing* | interpretive / reframing | **REJECTED predicted** (same family as C2) |
| C7 | *Premortem* | counterfactual / failure-planning | **REJECTED predicted** (Premortem rejected on case 1 C7) |
| C8 | n/a | n/a | n/a |

### Pre-registered hypothesis-test interpretation

Marcin's stop conditions for rethinking the family hypothesis:

> *"if consultant shows Information Asymmetry rejected despite a clean missing-info quote, or if Confidence Calibration / Probabilistic Thinking pass cleanly with aligned quotes. Either would weaken the 'external-legible vs interpretive-operation' split."*

So the calibration/abstract-cognitive sub-question matters. If C1 (Probabilistic Thinking) and C5 (Confidence Calibration) BOTH pass cleanly with cluster-aligned quotes, the family hypothesis weakens — abstract cognitive operations would be passing too, which contradicts "interpretive misses."

If they BOTH fail (or pass with quote drift), the family hypothesis strengthens.

If they SPLIT (one passes, one fails), the categorical framing needs refinement — possibly a sub-distinction between "calibration as evidence-reading" vs "calibration as pre-committed action rule."

C4 (Principal Agent Problem) is the second stress test. Agency/incentive-structure models haven't been seen on prior cases. If PAP passes cleanly, that family joins the "passes" list. If it misses, the "passes" list narrows further.

## What I'm holding for step 2

- 8 clusters, 6 distinct primaries, 1 `no_clean_primary`.
- Predictions for 7 anchor-worthy clusters: 5 expected REJECTED, 1 expected ACCEPTED, 1 STRESS-TEST OPEN.
- Heavy author bias acknowledged on C1, C3, C4, C5 (where the expected primary is in the case's anchor set).
- After opening Lane 2 artifacts, I'll attribute against this gold table, compute strict/broad friction-yield and strictness-failure metrics, and report verifier acceptance rate **by family** to test whether the cross-case hypothesis holds.
