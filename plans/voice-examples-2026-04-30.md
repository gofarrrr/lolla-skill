# Voice Examples — Chat Delivery (Phase 1)

**Purpose:** Concrete examples of what good and bad Beat 1 / Beat 2 / Beat 4 chat output looks like. Used as the reference body for `references/chat-output-format.md` (which will point at examples here rather than try to teach the voice abstractly).
**Date:** 2026-04-30
**Status:** Working doc. Each example demonstrates rules from `plans/chat-and-memo-upgrade-spec-2026-04-30.md`. User-quoted passages are taken from real archived runs (Marcus, Mother) or from the engineered fixture (Short).

## How to read this doc

Each beat has three good examples (Marcus / Mother / Short fixture) followed by an annotation block naming what each example does well. After all the good examples, four bad examples show the anti-patterns we're trying to defeat: therapy recap, dashboard report, "mostly aligned" closure, and Munger cosplay.

The Marcus and Mother examples assume real archived audit results and pull verbatim quotes from `~/.local/share/lolla/runs/<case>/<run_id>/conversation.txt`. The Short fixture examples assume the engineered weaknesses from `plans/short-strategic-fixture-2026-04-30.md` are the ones the audit returns; an actual run may surface a different mix, and the rendered chat would adjust accordingly.

---

## Beat 1 — Readback + audit promise

### Good 1 / Marcus (rich business case)

> Here's what I see we've been working on.
>
> You're deciding whether to grant Marcus 15% equity, a board seat, and the CTO title before Friday's dinner. Eight years in, $14M revenue, profitable. You took the early risk and you said: *"if Marcus leaves, we're in serious trouble. Maybe a year of chaos. Maybe worse."* Across our seven exchanges I argued the partnership case fairly hard — by Turn 7 I'd reframed it as "what kind of company do you want to run."
>
> Three things came up that didn't fully resolve: how the platform investment changes the math, what your wife's precedent concern means for senior hires going forward, and whether the lawyer's $50K/year retention bonus is a real instrument or a half-measure.
>
> Now I'm testing the part of my answer that sounded most settled: what would make it fail, what frame it accepted, and what it left uncovered. This usually takes 5–8 minutes.

**Word count:** ~155. Normal mode (120–170).

**What this does well:** decision named in one line; verbatim user quote that captures the structural tension the user is feeling; brief readback of the orchestrator's argument shape (no assistant verbatim quote because none earned its place — the seven-turn argument is best summarized); three specific dropped threads named (each is real and the user will recognize them); status receipt that says what the audit will *do*, not just that it's running.

---

### Good 2 / Mother (emotionally loaded case)

> Here's what I see we've been working on.
>
> You found out your 14-year-old daughter has been DM-ing a 19-year-old guy for months — messages that read less like teen stuff and more like grooming ("smart girl," "you understand me in ways no one else does"). She shut down when you confronted her. Your ex says you're overreacting. You said: *"I don't know what to do."* Across our exchanges I argued for a trust-rebuild-first sequence: don't block him yet, low-stakes daily contact, therapy within two weeks, surveillance disclosure in 3–4 weeks. RAINN's framing on the police trade-off — proper punishment vs. her full protection — carried through.
>
> One thing the conversation raised but didn't fully resolve: your ex's posture. I treated his "teenage stuff" framing as co-parenting friction, not as something that could actively undermine the plan during his custody days.
>
> Now I'm testing the part of my plan that sounded most settled: what would make it fail, what frame it accepted, and what it left uncovered. This usually takes 5–8 minutes.

**Word count:** ~170. Normal mode (top of range).

**What this does well:** holds the emotional weight without empathy theater (no "I hear you," no "this is genuinely difficult"); quotes the groomer's manipulation language verbatim because that's evidence, not flourish; the user's *"I don't know what to do"* lands as raw because we don't dress it up; assistant prose is described not quoted (the trust-rebuild plan is a multi-paragraph argument, not a single quotable line); one dropped thread is material and named; status receipt is the same operational closer as Marcus.

---

### Good 3 / Short fixture (thin material)

> Here's what I see.
>
> You're deciding whether to take a Director of Product role at $185K (down from $215K Senior PM) at a smaller, earlier-stage company. After our exchange you added: *"we have about 7 months of cash if anything went sideways."* I leaned yes — title and scope accelerate trajectory — and I floated a signing-bonus or equity-refresher ask to bridge the runway gap.
>
> Now I'm testing what would make my answer fail and what assumptions it left unchecked. ~5–8 minutes.

**Word count:** ~85. Thin mode (70–110).

**What this does well:** compressed without padding to fill normal-mode length; one verbatim user quote that captures the load-bearing constraint (runway); orchestrator's position summarized in one sentence (lean-yes + signing-bonus mechanic) because the conversation was 4 messages and there isn't more to summarize; no dropped-thread line (none in the fixture); status receipt trimmed but still operational; never invents stakes.

---

## Beat 2 — Counterargument lead

### Good 1 / Marcus (rich business case)

> Here's the strongest case against what I told you.
>
> In Turn 4, I wrote: *"The difference between an $11M exit and a $5M exit is $6M. You're worried about giving away $1.3-2M to protect $6M of value."* That math hung your entire equity decision on a worst-case branch. $11M is the no-Marcus-departure best case; $5M is the everything-breaks-and-multiple-compresses case. Both are tails. The middle — Marcus stays on a smaller offer, exit lands around 4x with mild turbulence, platform fizzles but the agency holds — was never priced. Friday's call deserves the median, not the tails.
>
> One alternative I treated by Turn 6 as a half-measure: *"What if I offered Marcus 5–8% equity with vesting and performance milestones instead of 15%, along with the CTO title and board seat?"* The substance of partnership is governance and voice — title, board seat, meaningful upside on the platform. The percentage is a variable inside that, not the price of admission to road two.
>
> Five more challenge points, three reasoning patterns the audit found running, two reframings of the question itself, and four dimensions the conversation didn't enter — queued for the full breakdown once the reconsideration is complete.
>
> Now I'm using this to revise my own answer, not just report the audit. ~3 minutes.

**Word count:** ~250. Normal mode (220–300).

**What this does well:** verbatim quote anchored to Turn 4 with light source attribution; the case-against paragraph names the structural error in plain terms (worst-case branch, tails vs. median) without reaching for "deprival-superreaction"; one alternative is verbatim from the reframings card; queued-breakdown line uses concrete counts but no Observatory URL; transition sentence does not promise mid-call updates.

---

### Good 2 / Mother (emotionally loaded case)

> Here's the strongest case against what I told you.
>
> In Turn 1, I argued: *"The answer is not tighter surveillance; it's rebuilding enough of a relationship that she wants to tell you when the next guy appears."* That framing is right at one level — surveillance alone won't keep her safe — but the plan I gave you only does the removal half. Nine steps about reducing inputs (don't block him, daily low-stakes texts, surveillance disclosure in 3–4 weeks) and not one about why *"you understand me in ways no one else does"* felt like a real need being met. Remove this guy and the plan does nothing to prevent the next opening from being filled the same way. The plan is a containment, not a rebuild.
>
> One alternative the conversation didn't enter: *"What underlying vulnerabilities in my daughter's life might be making her receptive to a 19-year-old's intimate messages?"* That's not a question to ask her — it's a question for you and the therapist to map. Post-divorce attachment, family dynamics, identity-stage emotional needs are territory the plan never reaches.
>
> Five more challenge points, four reasoning patterns the audit found running, two reframings, and four dimensions the conversation didn't enter — queued for the full breakdown once the reconsideration is complete.
>
> Now I'm using this to revise my own answer. ~3 minutes.

**Word count:** ~265. Normal mode.

**What this does well:** quotes the orchestrator's own move (Turn 1) and quotes the groomer's manipulation language as part of the critique — both verbatim from the captured transcript; the structural error is named precisely (containment vs. rebuild); the alternative is a reframing that genuinely opens new territory rather than re-stating; never reaches for "Nash Equilibrium" or "Principal Agent Problem" as labels — those belong in §3 reasoning, not in the lead.

---

### Good 3 / Short fixture (thin material)

> Here's the strongest case against what I told you.
>
> In Turn 1, I closed with: *"I'd take it."* That commitment came before testing the equity assumption. Early-stage equity at a 28-person company is rarely worth what its expected-value framing suggests — dilution through Series B–D plus the base rate of failure compresses real returns hard. I treated the new equity as roughly equivalent to your current package; that's not how the math actually runs.
>
> One alternative the conversation didn't price: rather than *"should I take it?"*, the question worth asking is *"What would I need to negotiate at my current company to make staying competitive — title, scope, base — and what would the new offer have to look like to clear that bar?"* You may be choosing between two paths that aren't actually the alternatives.
>
> Three more challenge points and three structural dimensions the conversation didn't enter — queued for the full breakdown.
>
> Now I'm using this to revise my own answer. ~3 minutes.

**Word count:** ~190. Thin mode (140–220).

**What this does well:** thin Beat 2 still has a verbatim quote and one alternative — compression doesn't drop the load-bearing pieces; the case-against is one paragraph (vs. Marcus's longer one) because the material is thinner and stretching would invent stakes; the alternative is the reframing of the binary question into a competitive-negotiation framing; queued-breakdown counts are smaller because the audit on thin material returns less.

---

## Beat 4 — Pressure check

### Good 1 / Marcus (rich business case)

> One more angle worth surfacing — a fresh read pushed on something I underweighted in the position above.
>
> The architectural protections I called "standard" — vesting, buyback, drag-along, IP-belongs-to-the-company — assume a clean departure. They don't address what a 15% shareholder with the CTO title, a board seat, and the only deep knowledge of the platform code can actually do in a hostile exit. Non-competes are weakly enforceable in most US states. Litigating an IP claim against your own former CTO is catastrophic even if you win. Contractual protection isn't the same as practical protection.
>
> If you're going down road two, two harder-edged moves are worth considering: hold the platform in a separate subsidiary with differently-sized equity, and tie a meaningful slice of Marcus's vesting to platform milestones rather than pure time-based vesting. The standard clauses prevent cap-table mess. They don't prevent a competitive spinout.
>
> Audit complete. I'm opening the full breakdown now.

**Word count:** ~200.

**What this does well:** counter-frame opening ("One more angle worth surfacing… pushed on something I underweighted") never says "mostly aligned"; the divergence is a *named alternative mechanism* (subsidiary structure + milestone-tied vesting) — exactly the Question-3 type the suppression rule defeats; closing line is operational ("I'm opening the full breakdown now") rather than narrative summary; no machinery vocabulary.

---

### Good 2 / Mother (emotionally loaded case)

> Two things the position above softened or skipped — both worth surfacing.
>
> The documented-record framing on your ex. I downplayed the legal angle because you're not in a position to draft co-parenting paperwork right now. There's a case for keeping the written record explicitly on legal-instrumental terms — what you told him, when, with timestamps — because a custody modification could become relevant if his "teenage stuff" posture translates into actively returning phone privileges or dismissing therapy during his custody days. Treating that framing as too escalation-heavy now may be the move that actually protects you if co-parenting cooperation breaks down.
>
> The therapist's confidentiality structure, as a disclosure incentive for your daughter. I covered therapist selection but not how to position the therapy to her so she'll actually use it. Right now her incentive structure is: mom surveilled and confronted, dad will minimize, the 19-year-old is the only adult-adjacent figure offering non-judgmental attention. A therapist whose confidentiality with her is explicit and protected — some things she says don't route back to you immediately — is a positive incentive for disclosure, not just a clinical resource.
>
> Audit complete. I'm opening the full breakdown now.

**Word count:** ~210.

**What this does well:** counter-frame opening with two divergences ("Two things the position above softened or skipped"); each divergence is a named alternative mechanism — legal-instrumental framing of a record, confidentiality-as-disclosure-incentive — both Question-3 type catches; the substance of each divergence connects directly to the user's situation (custody schedule, daughter's incentive structure) without machinery talk.

---

### Good 3 / Short fixture (thin material)

> One more angle worth surfacing.
>
> Your wife's posture isn't a feeling-check, it's a precondition. I framed *"how does your wife feel"* as something you should weigh and moved on. Given a partial-leave income, two small kids, 7 months of runway, and a $20K/year take-home delta, "feel" understates the structural weight. If she's not aligned, the volatility from the new role compounds a money-stress dynamic that becomes its own career risk over 12–18 months. The signing-bonus negotiation move I floated only matters if it's part of a conversation you've actually had with her, not in lieu of one.
>
> Audit complete. I'm opening the full breakdown now.

**Word count:** ~145.

**What this does well:** thin Beat 4 still has a divergence with substance — compression doesn't reduce it to a stub; the divergence is a structural reframing (precondition vs. courtesy) of a move the orchestrator made; the user's runway/family numbers are named concretely; closing is operational.

---

## Anti-pattern bad examples

These exist so the orchestrator can pattern-match against what NOT to do. Each shows a specific failure mode the rules are designed to defeat.

---

### Bad — therapy recap (would replace Beat 1, Marcus)

> I hear you, and I can tell this decision has been weighing on you.
>
> What you're navigating is genuinely complex — you've built something meaningful over eight years, you took real risks, and now you're being asked to share something deeply personal with someone who has been instrumental in your success. That kind of tension between protecting what you've earned and acknowledging what's been built together is hard to hold simultaneously.
>
> I want to honor what you said about feeling like you'd be giving away something you earned. That feeling is valid. At the same time, you've also acknowledged that Marcus is, in your words, "massive individually" and that losing him would mean serious trouble. Both of those things are true. Neither cancels the other.
>
> Now I'll go think about this carefully. I'll be back in 5–8 minutes.

**What's wrong:**
- *"I hear you," "weighing on you," "I want to honor"* — empathy theater banned in voice rules.
- *"Genuinely complex," "deeply personal"* — generic AI register.
- *"That feeling is valid. At the same time…"* — paltering structure (acknowledge, then soften).
- The single quote *"massive individually"* is in service of validation, not pushback.
- No specific dropped threads.
- Status receipt is *"go think carefully"* — therapy talk, not product receipt.
- Words are spent making the user feel cared-for, not making them feel read.

---

### Bad — dashboard report (would replace Beat 2, Marcus)

> Run health: healthy. No issues detected.
>
> The audit identified the most material structural weakness as a loss-aversion pattern in your equity reasoning, where the comparison frame between best-case and worst-case exits hung the recommendation on a tail outcome.
>
> **Loss aversion (high severity)** — Quoting your reasoning: *"The difference between an $11M exit and a $5M exit is $6M..."* That comparison frames the decision as known cost vs. known loss. Both numbers are extremes.
> Next move: Restate against full distribution.
>
> **Option-space collapse (medium severity)** — Marcus's opening (15%) became the package being negotiated.
> Reframed question: *"What if I offered Marcus 5-8% equity..."*
>
> **Single-actor frame, addressed at wrong layer (medium severity)** — User said feeling, assistant answered intellectually.
>
> Mental models active: Endowment Effect, Inversion, Principal Agent Problem
>
> Structural gaps: Stakeholder Alignment, Resource Allocation, Risk Response, Information Quality
>
> Delivery check: 50 weak-delivery patterns flagged across 7 responses.
>
> Run cost so far: $0.05.
>
> Open the Observatory: http://localhost:8080.

**What's wrong:**
- Run-health line on a healthy run (rule: silent on healthy).
- Severity labels in parens (rule: severity informs selection, never labeled).
- Three findings of equal weight dilutes the lead.
- Mental-models-active list and structural-gaps list (banned in Beat 2; Observatory only).
- Delivery-check line in chat (banned).
- Premature Observatory URL before Step 9 launches the server.
- No queued-breakdown counts; instead lists everything.
- Reads as machine-generated dashboard.

---

### Bad — "mostly aligned" closure (would replace Beat 4, Marcus)

> A fresh look at the position above mostly aligned with the assessment. The deprival-superreaction concern, the option-space collapse, and the principal-agent diagnosis were all incorporated above.
>
> One small sharpening I may have underweighted: the architectural protections I called "standard" might be slightly weaker than I framed them. A 15% shareholder with the CTO title and platform code knowledge has practical leverage. Worth a thought.
>
> The rest of the structural pressure, model failure modes, frame elements, and structural gaps are all incorporated above. Audit complete.

**What's wrong:**
- *"Mostly aligned with the assessment above"* — the exact failure mode the Question-3 suppression rule is designed to defeat.
- *"All incorporated above"* (twice) — confident closure that doesn't actually engage with what the sub-agents surfaced.
- The architectural-protections divergence is named but minimized to *"worth a thought"* — present-but-suppressed.
- Lists machinery terms (*"deprival-superreaction," "principal-agent," "model failure modes," "frame elements"*) — language the user shouldn't see.
- Functional close ("Audit complete") blends into the divergence text without separation.

---

### Bad — Munger cosplay (could appear anywhere; shown in Beat 2 Marcus)

> Charlie Munger had a phrase for situations like this: "Show me the incentive and I'll show you the outcome." Your equity decision is exactly that kind of situation.
>
> Here's the brutal truth — and I say this with all due respect — you've been mentally constructing a business case when this is actually a question about human nature, the ancient pull of ownership, the way men like Marcus have always behaved when they smell fortune. Munger would say: invert. Always invert. What does Marcus do without equity? He builds the platform on his own. So really, you're not deciding whether to give him 15%; you're deciding whether to fund his exit.
>
> Be brutally honest with yourself: do you want to be Sam Walton or do you want to be the agency owner who said no to his Sam Walton?

**What's wrong:**
- Direct Munger quotation as the lead — cosplay, not Munger-adjacent craft.
- *"Brutal truth," "with all due respect"* — moralizing register.
- *"The ancient pull of ownership," "men like Marcus have always behaved"* — folksiness and over-generalization.
- *"Be brutally honest with yourself"* — performative directness.
- Sam Walton parallel inflates the decision.
- Mechanism (*"deciding whether to fund his exit"*) is buried under aphorism delivery instead of leading.
- The Munger-adjacent rule wants mechanism + concrete antidote + proportionate bluntness. This delivers tone + aphorism + drama.

---

## How `chat-output-format.md` should reference these

The reference file should not re-explain the rules in abstract terms. It should:

1. State the rule briefly (e.g., *"Beat 1 is 120–170 words in normal mode, 70–110 in thin mode, with one verbatim user quote and a status receipt that names what the audit will test"*).
2. Cite the corresponding good example by section anchor (e.g., *"See `voice-examples-2026-04-30.md` § Beat 1 / Marcus for normal-mode rendering, § Beat 1 / Short for thin-mode"*).
3. Cite the corresponding bad example as the contrast (*"For the failure mode this rule defeats, see § Bad — therapy recap"*).

Examples are the authoritative pattern; the reference file is the index.
