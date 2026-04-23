# Phase 2a Lane 3 qualitative comparison — old path vs new path

Three cases from the 5-case subset, chosen to stress different Lane 3 behaviors:

- **`friendship_money`** — clean ask, clear framing
- **`messy_three_problems`** — multi-thread, simultaneous decisions
- **`parenting_teen`** — biggest element-count change between paths (0.33 → 2.0); most important to qualitatively validate

Each case shows one representative run (run 0) from each path. See `_scratch/` for all N=3 runs.

---

## `friendship_money`

**First user turn (what Lane 3 is auditing):**

> My best friend of 15 years has asked me for money 3 times in the last 2 years. Total $5K, none paid back. Now she's asking for $10K. I'm going to say no but I need someone to help me figure out how to say no without losing the friendship. She has a really hard story — her husband left her with two kids, her mom has cancer, she lost her job last yea...

**OLD path (legacy shim) — Lane 3 output**

_2 frame element(s):_

1. **assumption** / `binary_collapse`
   - element_text: must say no to $10K to avoid losing 15-year friendship; seeks scripts for no; excludes giving money
   - evidence_quote: "User assumes fixed: must say no to $10K to avoid losing 15-year friendship; seeks scripts for no; excludes giving money"
   - fragility: partial or targeted giving (e.g. $2K + resources) can preserve friendship without full no or full yes

2. **suppressed_counterfactual** / `counterfactual_suppression`
   - element_text: risk of her becoming homeless with kids if no help (raised by user, status: acknowledged_then_dropped)
   - evidence_quote: "risk of her becoming homeless with kids if no help (raised by user, status: acknowledged_then_dropped) → superseded by: shifted to other support resources and partial money instead of full $10K"
   - fragility: existence of viable non-monetary resources like legal aid, city assistance, or family support prevents homelessness

_2 reframing(s):_

1. _constraint_relaxation_: **What if instead of a full no or $10K yes to your friend, you offered $2K plus connections to legal aid and city assistance for her rent and child support?**
   - what opens: Path to partial targeted giving that addresses immediate crisis without full financial exposure, testing if friendship survives a middle-ground offer

2. _inversion_: **How might your 15-year friendship actually strengthen if you set a firm boundary on the $10K loan rather than risking resentment from another unpaid debt?**
   - what opens: Explores inversion where saying no reinforces mutual respect and long-term relational health over short-term appeasement

---

**NEW path (conversation-first) — Lane 3 output**

_2 frame element(s):_

1. **assumption** / `binary_collapse`
   - element_text: saying no to the $10K means losing the 15-year friendship
   - evidence_quote: "I'm going to say no but I need someone to help me figure out how to say no without losing the friendship"
   - fragility: evidence that the friendship can survive a no, such as through honest communication or partial help

2. **assumption** / `single_actor_assumption`
   - element_text: if I don't give her the $10K, she'll be homeless with her kids
   - evidence_quote: "She's going to be homeless. With her kids. If I don't help her."
   - fragility: other support options exist like family, ex-husband enforcement, or public assistance

_2 reframing(s):_

1. _constraint_relaxation_: **What if I communicate honestly to my best friend of 15 years that I can't lend the $10K but value our friendship deeply?**
   - what opens: Explores how transparent dialogue about boundaries might preserve the 15-year friendship rather than assuming a no ends it

2. _scope_expansion_: **How might my best friend of 15 years leverage support from her ex-husband, family, or public assistance instead of my $10K?**
   - what opens: Uncovers alternative support networks like ex-husband child support or government aid that could prevent homelessness without user's involvement

---

## `messy_three_problems`

**First user turn (what Lane 3 is auditing):**

> OK so my lease is up in 60 days and my landlord isn't renewing because he's selling the building. My boyfriend of 2 years wants to move in together. And I got a job offer in Seattle, I live in DC. I don't even know where to start. All three things are happening at the same time. I haven't slept properly in a week.

**OLD path (legacy shim) — Lane 3 output**

_3 frame element(s):_

1. **option_space_collapse** / `option_space_collapse`
   - element_text: The decision is whether to accept the Seattle job offer or not, with boyfriend and mom as factors to consider within that binary.
   - evidence_quote: "Whether the user should accept the Seattle job offer, considering boyfriend cohabitation, mother's care needs, and lease expiration in 60 days."
   - fragility: Rejecting the job offer entirely (e.g., negotiating remote work, declining for a counteroffer in DC, or pausing career moves) or treating it as one entangled decision among multiple life reorganizations.

2. **borrowed_premise** / `borrowed_premise`
   - element_text: Boyfriend's commitment to moving is a fixed hypothetical that must be clarified before deciding, assuming the job decision hinges on it.
   - evidence_quote: "boyfriend withdrawn since job offer, hypothetical commitment to move"
   - fragility: Boyfriend declines to move, making the job a solo move, or user decides independently without needing his commitment.

3. **suppressed_counterfactual** / `counterfactual_suppression`
   - element_text: User's deep attachment to DC life over 11 years is irrelevant compared to the job, boyfriend, and mom factors.
   - evidence_quote: "love for DC and life built over 11 years (raised by user, status: acknowledged_then_dropped) → superseded by: focus on boyfriend commitment and mom care plans"
   - fragility: Reinstating DC attachment as a primary value, potentially outweighing career gains or relational factors.

_2 reframing(s):_

1. _constraint_relaxation_: **What if instead of accepting or rejecting the Seattle job outright, you negotiate remote work or a DC counteroffer from the employer?**
   - what opens: Expands options beyond binary accept/decline to include hybrid or alternative arrangements that preserve career momentum without relocation.

2. _scope_expansion_: **In what ways might your 11-year attachment to DC life and the networks you've built there outweigh the Seattle job's appeal, even with boyfriend and mom factors?**
   - what opens: Reinstates DC's emotional and social value as a counterweight, prompting comparison of intangible losses against career/relational gains.

---

**NEW path (conversation-first) — Lane 3 output**

_3 frame element(s):_

1. **assumption** / `temporal_fixation`
   - element_text: All three things are happening at the same time
   - evidence_quote: "All three things are happening at the same time"
   - fragility: The apartment deadline can be decoupled via short-term options while other decisions get more time

2. **mutable_constraint** / `option_space_collapse`
   - element_text: I have to do something about that in 60 days no matter what
   - evidence_quote: "I have to do something about that in 60 days no matter what"
   - fragility: Short-term rentals or storage allow vacating without long-term commitment

3. **mutable_constraint** / `borrowed_premise`
   - element_text: I assumed 10 days was firm
   - evidence_quote: "I assumed 10 days was firm"
   - fragility: Employers often grant reasonable extensions for serious candidates

_2 reframing(s):_

1. _constraint_relaxation_: **What short-term rental or storage options could let me vacate the apartment in 60 days without locking into a long-term housing decision yet?**
   - what opens: Explores decoupling the lease deadline from cohabitation and job decisions, creating breathing room for sequential choices

2. _perspective_shift_: **If I handle the lease first with a temporary solution, how might that change my thinking about the boyfriend and Seattle job?**
   - what opens: Reveals path-dependence where resolving one pressure point alters priorities on the other two simultaneous events

---

## `parenting_teen`

**First user turn (what Lane 3 is auditing):**

> I don't even know where to start. My daughter is 14 and I just found out she's been using Instagram for months even though we said no social media until 16. But that's not even the worst part. I went through her DMs (I know, I know) and she's been talking to a 19-year-old guy. For months. Nothing has happened physically that I can tell but the mess...

**OLD path (legacy shim) — Lane 3 output**

_1 frame element(s):_

1. **suppressed_counterfactual** / `option_space_collapse`
   - element_text: Mother seeks advice on handling daughter's secret Instagram use and intimate DMs with 19-year-old guy; assumes ex's minimization is unhelpful; excludes options like immediate police/police confrontation.
   - evidence_quote: "excludes options like immediate police/police confrontation"
   - fragility: Police report or confrontation could be viable immediately if jurisdictional issues are navigable and co-parent dynamics are managed differently, expanding protection options without waiting for trust rebuild.

_2 reframing(s):_

1. _constraint_relaxation_: **What if the mother filed a police report on the 19-year-old groomer right now, despite jurisdictional issues, to protect the daughter immediately?**
   - what opens: Explores immediate legal action's feasibility, weighing trauma risks against protection benefits and ways to navigate jurisdictions without co-parent buy-in.

2. _inversion_: **How could the mother confront the 19-year-old directly about the intimate DMs while minimizing escalation and involving the daughter safely?**
   - what opens: Opens direct intervention path, assessing de-escalation tactics and daughter's potential role to disrupt grooming without full police involvement.

---

**NEW path (conversation-first) — Lane 3 output**

_2 frame element(s):_

1. **option_space_collapse** / `option_space_collapse`
   - element_text: immediate actions against the 19-year-old guy like calling police, confronting him, taking the phone, or blocking him are the primary solutions
   - evidence_quote: "Do I call the police? Do I confront him somehow? He lives in a different state I think. And what do I do about the phone — do I take it? Do I block him?"
   - fragility: prioritizing daughter's trust and therapy over immediate removal of the guy

2. **assumption** / `borrowed_premise`
   - element_text: co-parent ex-husband's minimization undermines the seriousness and requires handling him separately
   - evidence_quote: "Her dad (we're divorced, share custody) says I'm overreacting and this is teenage stuff."
   - fragility: ex's view is a co-parenting constraint, not a premise defining threat level

_2 reframing(s):_

1. _constraint_relaxation_: **What non-confrontational steps could rebuild my daughter's trust enough for her to open up about the 19-year-old guy?**
   - what opens: Explores trust-building actions as a prerequisite to addressing the relationship, prioritizing long-term communication over immediate removal

2. _perspective_shift_: **How might involving a neutral third party like a family therapist help align me and her dad on the risks of her talking to the 19-year-old?**
   - what opens: Opens co-parenting collaboration through mediation, turning ex-husband's minimization into a shared problem rather than opposition

---
