# Source-first cluster labeling — `third-year-phd-student`

Status: **STEP 1–3 only** (per design memo §6.1–§6.3). Lane 2 outputs (`result.json`, `companion_cheat_sheet`, `revised.txt`) NOT opened for this case.

Case: `third-year-phd-student`
Run timestamp: `20260425T122400Z`
Bucket hypothesis: mixed-positive (Step 6 consumption 80%, Lane 2 stability 0.39 — best of the failure-named four). Tests F2 across academic/cognitive content.
Source consulted: `conversation.txt` Turn 1–22 ASSISTANT messages only.

## Honesty disclosure

Claude has seen this case's anchor set during the corpus survey (Optionality, Premortem, Status Quo Bias, Base Rates, Problem Framing And Reframing). Medium bias. Five clusters below have an expected primary that's in the current anchor set.

## Current prediction frame after Marcus (F2)

F1''' was partially falsified by Marcus C5 OC (explicit dollar math + mutual-exclusion phrasing, still rejected). Re-anchored hypothesis per Marcin's case-5 verdict:

> **F2: verifier acceptance depends on local, literal, model-specific mechanism evidence. Operational language helps, but only when it makes the model's mechanism explicit in the verifier's terms. Numbers, chains, or tradeoff math are not enough by themselves.**

The shift from F1''' to F2:
- F1''': "operationalized mechanism language predicts acceptance"
- F2: "the verifier accepts when the quote makes the specific model mechanism easy to recognize, preferably locally and literally"

What F2 absorbs that F1''' didn't:
- *Representativeness Heuristic* passes (Marcus C4) because the quote made the "wrong comparison class" mechanism locally obvious.
- *Opportunity Cost* failed (Marcus C5) despite dollar math because the quote showed valuation tradeoff, but apparently did not spell the OC mechanism in the verifier's terms.
- *Second Order Thinking* failed as "too generic" (Marcus C3, case 3) because a long causal chain is not enough; the verifier may want a compact "downstream consequence of this choice" mechanism.
- *Feedback Loops*, *Information Asymmetry*, *Theory Of Constraints*, *Confidence Calibration*, *Probabilistic Thinking* passed when the quote contained local recognizable mechanism markers.
- *PFR*, *Optionality*, *Premortem*, *Opportunity Cost* remain fragile because they require interpretive translation unless the source is unusually explicit.

Per Marcin's pre-registered F2 predictions for case 6:

- **Base Rates**: likely accept if explicit frequency/base-rate comparison; otherwise reject-risk
- **Status Quo Bias**: likely accept if quote names default/staying-put inertia locally; reject-risk if it is just "you are hesitating"
- **Optionality**: recall/verifier risk unless source explicitly names preserving multiple paths or option value
- **Premortem**: verifier risk even if in candidates, unless quote literally has failure pre-registration or "imagine this failed because X"
- **Problem Framing And Reframing**: chronic recall/verifier risk; likely absent or rejected unless language explicitly says the question/frame is wrong
- **Opportunity Cost**: predict accept only if quote locally contrasts "choosing A means giving up B" in unmistakable opportunity-cost terms

## Clusters

### C1 — "Everyone does it" is not differentiating (Status Quo Bias)

`source_quotes`:
- Turn 5 ASSISTANT: "'It's common in my department' is also a status-quo signal — if everyone is doing it, it's by definition not differentiating."
- Turn 5 ASSISTANT: "If you're OK with the postdoc-broadening path, option 1 is fine. But you should be honest with yourself: that's a 7-10 year horizon to a permanent job, with declining odds each year. It's not 'the safe path'; it's the path with lower short-term risk and high long-term uncertainty."

`reasoning_shape`: framing_reframing / evidence_calibration

`expected_primary_models`: *Status Quo Bias*

`acceptable_secondary_models`: *Confidence Calibration* (recalibrating "safe" against actual long-term odds)

`should_reject_models`: *Sunk Cost Fallacy*

`ambiguous`: no

`bias_flag`: yes — *Status Quo Bias* is in this case's anchor set.

### C2 — Base rate on novel combinations: 20-30%, not 50%

`source_quotes`:
- Turn 6 ASSISTANT: "The base rate of success on genuinely novel combinations in a PhD timeline is probably 20-30%, not 50%."
- Turn 6 ASSISTANT: "There's also a selection bias in how this conversation goes. Weird combinations that work become famous. Weird combinations that don't work become dropped theses that nobody remembers. You only hear about the winners; the losers are silent."

`reasoning_shape`: base_rate_statistical

`expected_primary_models`: *Base Rates*

`acceptable_secondary_models`: *Survivorship Bias* (the explicit selection-bias call-out about visible winners), *Optimism Bias And Planning Fallacy* (the user's intuition was 50%, base rate corrects it down)

`should_reject_models`: *Hindsight Bias*

`ambiguous`: no

`bias_flag`: yes — *Base Rates* is in this case's anchor set. The quote has explicit frequency comparison ("20-30%, not 50%"), exactly the F2 condition for likely accept.

### C3 — Career-optionality argument: option 3 preserves multiple paths

`source_quotes`:
- Turn 7 ASSISTANT: "There's also the career-optionality argument. A novel combination that's 60% worked gives you: multiple paper possibilities, a methods contribution, industry interest if it has practical applications, and a unique pitch for both postdoc and direct-to-industry paths. Option 1 gives you one of those things (papers); option 3 potentially gives you all."

`reasoning_shape`: option_design

`expected_primary_models`: *Optionality*

`acceptable_secondary_models`: *Second Order Thinking* (downstream consequence of preserved paths)

`should_reject_models`: *Theory Of Constraints*

`ambiguous`: no

`bias_flag`: yes — *Optionality* is in this case's anchor set. The quote literally names "career-optionality argument" and lists preserved paths — this is exactly the F2 condition Marcin specified for Optionality acceptance.

### C4 — Multi-instance reframing (smart vs ambitious; option 3 specificity)

`source_quotes`:
- Turn 8 ASSISTANT: "When you describe it that way, it's much more specific and much less wild. 'Apply existing tumor evolution methods to existing single-cell datasets to extract something the single-cell field currently can't see' is a defined project, not a blue-sky combination. That's a different risk profile."
- Turn 8 ASSISTANT: "What changed when you said it out loud was that the combination is actually methodologically conservative — you'd be doing evolutionary modeling, your known competency, but on novel data. The novelty is in the application, not in the methods development."
- Turn 16 ASSISTANT: "I'd push back gently on the framing. You're treating 'smart' and 'ambitious' as different. In this case they're not... It's not a choice between smart and ambitious; it's between ambitious-and-smart (option 3) versus defensible-but-narrower (option 1)."

`reasoning_shape`: framing_reframing

`expected_primary_models`: *Problem Framing And Reframing*

`acceptable_secondary_models`: none clean

`should_reject_models`: *Status Quo Bias*

`ambiguous`: no

`bias_flag`: yes — *PFR* is in this case's anchor set. The quote contains explicit framing language ("I'd push back gently on the framing") + the "described it differently" reframe. Per F2, PFR has chronic recall/verifier risk; this is a test of whether explicit "framing" language saves PFR.

### C5 — Retiring advisor as institutional dependency risk

`source_quotes`:
- Turn 12 ASSISTANT: "A retiring advisor in the last 2-3 years before retirement tends to: be less invested in long-term lab planning, less politically active on your behalf for funding or positions, and less available for letter-writing/networking that peaks in the postdoc transition years. Some retire earlier than planned once they've publicly committed to it, which can orphan students mid-PhD."

`reasoning_shape`: incentives_agency / systems_feedback

`expected_primary_models`: ambiguous — *Theory Of Constraints* (advisor as binding constraint on certain career resources) OR *Power Dynamics* (institutional power that shrinks with retirement) OR `no_clean_primary`

`acceptable_secondary_models`: *Information Asymmetry* (advisor's real timeline is uncertain)

`should_reject_models`: *Principal Agent Problem*

`ambiguous`: yes

`bias_flag`: no — none of the candidates are in this case's anchor set.

### C6 — Co-advisor as risk mitigation

`source_quotes`:
- Turn 12 ASSISTANT: "Risk mitigation here: establish a second faculty relationship during your PhD, not just after. A co-advisor arrangement, a thesis committee member who takes an active mentoring role, or a collaborator (like the single-cell PI) who becomes invested in your progress. You want someone besides your advisor who knows your work and would advocate for you."
- Turn 12 ASSISTANT: "Option 3 with a single-cell collaboration naturally sets up a co-advisor dynamic. That's another point in its favor — it solves the retirement-risk problem as a byproduct."

`reasoning_shape`: option_design / commitment_reversibility

`expected_primary_models`: ambiguous — *Margin Of Safety* (buffer against retirement risk) OR *Optionality* (preserving alternative supporters) OR *Theory Of Constraints* (decoupling from binding constraint)

`acceptable_secondary_models`: any of the above not chosen

`should_reject_models`: *Principal Agent Problem*

`ambiguous`: yes

`bias_flag`: no — none of the candidates are in this case's anchor set.

### C7 — Premortem with explicit go/no-go pre-registration

`source_quotes`:
- Turn 17 ASSISTANT: "The failure mode to avoid is spending 2.5 years on option 3 hoping it'll come together, and finding yourself in year 6 with nothing to salvage. Set a go/no-go checkpoint at 18 months — do you have at least one publishable result on the pipeline — and commit to pivoting if the answer is no."
- Turn 22 ASSISTANT: "write down your current thinking tonight while it's fresh — specifically, the reasons option 3 feels right, the conditions under which it could work, the fallback plan if it doesn't. Future-you, six months from now when you're stuck on a technical problem and doubting your choice, will need present-you's clarity about why you chose this."

`reasoning_shape`: counterfactual / failure-planning

`expected_primary_models`: *Premortem*

`acceptable_secondary_models`: *Confidence Calibration* (separating future doubt from present-state evidence)

`should_reject_models`: *Hindsight Bias*

`ambiguous`: no

`bias_flag`: yes — *Premortem* is in this case's anchor set.

`note`: **This is the F2 test cluster Marcin flagged.** Source has literal failure-pre-registration language: "Set a go/no-go checkpoint at 18 months — do you have at least one publishable result on the pipeline — and commit to pivoting if the answer is no." That's exactly the "imagine this failed because X" pattern F2 says should save Premortem. If Premortem still rejects here, the model-specific verifier blind-spot hypothesis is supported.

## Cluster summary (pre-attribution)

| Cluster | Primary | Op level (per F2) | F2 prediction |
|---|---|---|---|
| C1 — Status Quo Bias call-out | *Status Quo Bias* | medium-high (names "status-quo signal" + "everyone is doing it" inertia) | **accept** |
| C2 — Base rate 20-30% | *Base Rates* | **high** (explicit frequency comparison) | **accept** |
| C3 — Career-optionality argument | *Optionality* | medium-high (literally names "career-optionality" + lists preserved paths) | **lean accept** with hedge (Optionality has chronic recall/verifier failure across cases 1-2-3; explicit naming may not save it) |
| C4 — Multi-instance reframing | *Problem Framing And Reframing* | medium (explicit "I'd push back on the framing" + multi-instance) | **recall/verifier risk** (PFR pattern N=5; even explicit "framing" language hasn't saved it) |
| C5 — Retiring advisor risk | ambiguous (TOC/PD/no_clean_primary) | n/a | n/a — no anchor expected unless surprise |
| C6 — Co-advisor protection | ambiguous (MoS/Optionality/TOC) | n/a | n/a — no anchor expected unless surprise |
| C7 — Premortem with go/no-go | *Premortem* | **high** (literal "go/no-go checkpoint... if no, pivot" + write-it-down baseline) | **F2 KEY TEST** — predicts accept; if rejects, model-specific blind-spot hypothesis supported |

### Counts

- 7 clusters
- 5 with non-ambiguous expected primary
- 2 with ambiguous primary (C5, C6) where the gold ambiguity-discipline applies — no canonical 222 fits cleanly
- Distinct expected_primary_models in non-ambiguous set: *Status Quo Bias*, *Base Rates*, *Optionality*, *Problem Framing And Reframing*, *Premortem*

### Pre-registered prediction summary

**3 high-confidence accepts:** C1 (Status Quo Bias), C2 (Base Rates explicit frequency), C7 (Premortem literal pre-registration — KEY F2 TEST)

**1 lean-accept-with-hedge:** C3 (Optionality with explicit naming, but model has chronic-fail pattern)

**1 recall/verifier-risk:** C4 (PFR — chronic-fail pattern N=5)

**2 ambiguous, no anchor expected:** C5, C6 (gold-ambiguity primaries; not in anchor set)

### What case 6 can decide

The PhD case has 5 of 7 clusters with expected primaries in the current anchor set (C1, C2, C3, C4, C7). If F2 predicts correctly:
- C1, C2, C7 should all be cluster-aligned primary hits (high friction yield)
- C3 Optionality is the test of whether "explicit naming" saves the chronic-fail model
- C4 PFR is the test of whether "explicit framing language" saves PFR

If C7 Premortem **passes** with the literal pre-registration language: F2 explains Premortem; the audit's path-of-least-resistance fix for Premortem is "make the source quote contain literal pre-registration language" via verifier prompt.

If C7 Premortem **rejects** despite the literal language: model-specific blind-spot hypothesis is supported; Premortem rejection isn't fully explained by F2 — need refinement (possibly a model-specific quirk in the verifier rubric).

Step 2 attribution will resolve these.

## What I'm holding for step 2

- 7 clusters, 5 non-ambiguous primaries, 2 with gold ambiguity.
- 5 expected primaries in current anchor set; if F2 holds, this case should yield ~4-5/7 friction (highest in audit).
- KEY F2 test: C7 Premortem with literal pre-registration language.
- Secondary tests: C3 Optionality + C4 PFR with explicit-language saving them or not.
- After opening Lane 2 artifacts, attribution will compare actuals to F2 predictions and update the hypothesis accordingly.
