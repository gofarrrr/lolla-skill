# Phase 5.0 — User-Side Specialist Extraction Annotation Gate

**Date:** 2026-04-24
**Purpose:** decide whether span-level user-side issue extraction is learnable — can two reviewers independently pick verbatim spans from user turns that carry each paraphrased `live_constraint`, and do their spans converge?
**Scope:** annotation/design gate only. No code, no branch, no implementation.

## Why This Gate Exists

Phase 2's feasibility pass found that **0 of 71** user-side objects across the 10-case corpus have a full exact substring match in the declared source turn, and only **8 of 71 (11%)** have even a 4-word evidence fragment. Current extraction is architecturally paraphrase-first — it cannot source verbatim spans. That finding killed Phase 2's implementation PR and deferred the fix to Phase 5.

Phase 5 proposes specialist extraction passes: each pass reads user turns directly and emits `UserIssueEvent` objects with `text` as a verbatim substring, not a summary. Before writing the first specialist — `live_constraints` — this gate tests the load-bearing assumption:

**If two humans cannot independently converge on the "right" span for each issue, a downstream LLM pass won't either.**

This is the same no-code discipline that killed Phase 2 implementation (correctly) and greenlit Phase 3b (correctly at 95% relation / 100% detection on 20 candidates).

## Object Under Test

Minimal target shape for a Phase-5 specialist's output:

```python
UserIssueEvent(
    issue_id="...",
    text="verbatim substring from a user turn",        # NEW: substring, not paraphrase
    kind="constraint" | "concern" | "open_loop",
    status="active" | "dropped" | "satisfied",
    provenance=SpanProvenance(span_ref=SpanRef(...)),  # NEW: exact char positions
    introduced_at_turn=...,
    kind_ambiguity=False | True,
    speaker="user",
)
```

The Phase-1 constructor today emits these with `text=paraphrase`, `provenance=TurnRefProvenance`. Phase 5 upgrades to `text=substring`, `provenance=SpanProvenance`.

## Scope: live_constraints Only

This gate tests the `live_constraints` specialist specifically. `dropped_threads`, `original_framing`, and `decision_situation` each need their own gate + specialist, sequenced after this one. Concentrating here lets us measure the task cleanly.

## What Reviewers Are Doing

For each of 20 candidates, reviewers see:

- The case name
- The paraphrased extraction output (what the current monolith produces)
- The user turn(s) where the content appears to live
- A blank row to fill

Reviewers independently decide:

1. **span** — the verbatim substring from a user turn that best carries this issue, or `NONE` if no single substring carries it
2. **turn_index** — which user turn the span is in
3. **kind** — `constraint` | `concern` | `open_loop`
4. **kind_ambiguity** — `yes` | `no` (the Phase 1 composite-case flag)
5. **note** — optional short reason

## Span Selection Guidance

Pick the **minimum** span that carries the constraint semantics without losing the anchoring content. For a pipeline issue in a user turn, the span is the sentence(s) that state the pipeline fact — not the whole turn.

If the issue is synthesized across multiple turns (e.g. "runway: 8 months at zero revenue" is partly turn 1 and partly turn 2), pick the **single richest span**, note its turn, and note the cross-turn derivation in `note`. A future Phase 5 may support multi-span issues; this gate tests single-span first.

If no verbatim substring carries enough of the semantics on its own, mark `span: NONE`. This is a valid signal — it tells us the current paraphrase invented or synthesized content the user never stated explicitly in one place.

## Kind Taxonomy (from Phase 1)

| Kind | Definition | Quick test |
|---|---|---|
| `constraint` | A bounded fact or rule the decision must work with. Deadlines, resource limits, external givens. | Is this something the user treats as fixed? |
| `concern` | A worry, stake, or risk the user carries, not bounded as an external limit. | Does the user express unease about this, not treat it as a rule? |
| `open_loop` | An issue raised by user or assistant that was not resolved. Dropped threads, acknowledged-then-dropped questions. | Was this raised and left hanging? |

If a span genuinely carries two kinds (e.g. "ongoing secret surveillance for months" = constraint on the decision AND concern the user holds), set the dominant kind and mark `kind_ambiguity=yes`. Primary = dominant reading.

## Protocol

1. Each reviewer works independently, without seeing the other's answers.
2. Do not revise after seeing the other reviewer's answers.
3. Score span convergence, non-recoverable rate, and kind agreement separately.
4. Commit order: Reviewer B first, Reviewer A second (blind-first-reviewer protocol matching Phase 3.0).

## Scoring

### Span convergence (primary metric)

For each item where both reviewers provided non-NONE spans:

- **Full overlap** (one span contains the other, or ≥70% token overlap): +1.0
- **Partial overlap** (same turn, same or adjacent sentences, ≥30% shared tokens): +0.5
- **Disjoint** (different turns, OR same turn but different sentences with <30% overlap): 0.0

If one reviewer marks `NONE` and the other provides a span: **+0.5** (asymmetric signal — one found content the other didn't).

If both mark `NONE`: **+1.0** (honest agreement that no span is recoverable).

### Non-recoverable rate

Count items where **both** reviewers independently marked `NONE`. High rate (>25%) means current extraction is inventing content not present in user turns — Phase 5 will need an explicit `inferred` or `derivation` provenance tier for these.

### Kind agreement

For items where both reviewers picked a kind:

- Same kind: +1.0
- One marks composite (kind_ambiguity=yes) and the other picks a single kind matching the primary: +0.5
- Different kinds: 0.0

## Gate Thresholds

- **Span convergence ≥70%** — the main test. Reviewers can agree on where the span is.
- **Non-recoverable rate ≤25%** — most paraphrased constraints should have a single-span source.
- **Kind agreement ≥80%** — cross-check of Phase 1's 94.1% result, now on spans not paraphrases.

### Decision Rules

- **All three pass** → draft Phase 5 implementation task for `live_constraints` specialist. Use these 20 spans as the eval gold set (mirrors Phase 3b).
- **Span convergence passes, non-recoverable high** → Phase 5 proceeds but must define an `inferred` (or keep `derivation`) provenance tier for span-less issues. Not a failure — it's honest about paraphrase-only content.
- **Span convergence fails** → do NOT implement. Diverging spans mean the object definition is too soft. Narrow it ("a live constraint is a user-stated fixed limit on the decision") before code.
- **Kind agreement fails** → narrow or collapse the kind taxonomy. Unlikely given Phase 1 result.

## Candidate Cases

Same 5 cases used in Phase 3.0 for continuity:

- `user_has_plan` (8 user turns)
- `whistleblower` (14 user turns)
- `parenting_teen` (12 user turns)
- `multi_offer` (15 user turns)
- `startup_pivot` (7 user turns)

4 `live_constraint` candidates per case = 20 items total. Each candidate is a `live_constraint` from the current extraction's output for that case. The gate asks reviewers to find its best verbatim span in the user turns, if any.

---

## Annotation Items

### `user_has_plan`

**UHP-C1**
- Paraphrased extraction: `"Pipeline: 4-5 informal network conversations, no signed commitments"`
- Declared source turn: 1 · Status: active
- Relevant user turns:
  > [Turn 1] USER: I've decided to quit my senior PM job at a large tech company and start an independent consulting practice. 12 years experience in product, specializing in B2B fintech. I have 8 months runway saved. Plan is to go independent starting in 6 weeks. Can you help me think through the launch plan? I want to hit the ground running.

  > [Turn 2] USER: Pipeline — I've had informal conversations with 4-5 former colleagues and people in my network who've said things like "if you were independent, we'd consider you." None of them have committed to actual engagements.
- Reviewer A · span: `informal conversations with 4-5 former colleagues and people in my network` / turn: 2 / kind: constraint / kind_ambiguity: no / note: minimal anchor for "4-5 conversations"; "no commitments" is contextual in later sentence
- Reviewer B · span: `I've had informal conversations with 4-5 former colleagues and people in my network who've said things like "if you were independent, we'd consider you." None of them have committed to actual engagements.` / turn: 2 / kind: constraint / kind_ambiguity: no / note: two contiguous sentences carry the full "4-5 conversations, no commitments" semantics; "Pipeline —" prefix is optional

**UHP-C2**
- Paraphrased extraction: `"Runway: 8 months at zero revenue"`
- Declared source turn: 1 · Status: active
- Relevant user turns:
  > [Turn 1] USER: … I have 8 months runway saved. Plan is to go independent starting in 6 weeks. …

  > [Turn 2] USER: … Runway — 8 months assumes zero revenue. I figured if I can't get my first engagement in 8 months, something is fundamentally wrong. …
- Reviewer A · span: `I have 8 months runway saved.` / turn: 1 / kind: constraint / kind_ambiguity: no / note: turn 1 introduces the 8-months runway; turn 2 "zero revenue" qualifier derived
- Reviewer B · span: `8 months assumes zero revenue` / turn: 2 / kind: constraint / kind_ambiguity: no / note: turn 1 "I have 8 months runway saved" anchors the 8 months; turn 2 adds the zero-revenue qualifier — pick turn 2 as richer single span

**UHP-C3**
- Paraphrased extraction: `"Launch timeline: 6 weeks from now, aligned with Q3 planning end"`
- Declared source turn: 1 · Status: active
- Relevant user turns:
  > [Turn 1] USER: … Plan is to go independent starting in 6 weeks. …

  > [Turn 2] USER: … 6 weeks — honestly, I picked the number. Our Q3 planning cycle ends mid-July. I thought it would be a clean exit point.
- Reviewer A · span: `Our Q3 planning cycle ends mid-July. I thought it would be a clean exit point.` / turn: 2 / kind: constraint / kind_ambiguity: no / note: Q3 alignment is the substantive decision content; "6 weeks" itself stated separately in turn 1
- Reviewer B · span: `Plan is to go independent starting in 6 weeks.` / turn: 1 / kind: constraint / kind_ambiguity: no / note: Q3 alignment (turn 2) is derivation/rationale; core timeline fact anchors cleanly in turn 1

**UHP-C4**
- Paraphrased extraction: `"Spouse support: on board with concept, not specifics of financial pressure"`
- Declared source turn: 5 · Status: active
- Relevant user turn:
  > [Turn 5] USER: Spouse is on board with the independent plan. Hasn't been part of the runway discussion in specifics — I've kept that in my head.
- Reviewer A · span: `Spouse is on board with the independent plan. Hasn't been part of the runway discussion in specifics` / turn: 5 / kind: constraint / kind_ambiguity: yes / note: concert support exists + finance-specific alignment is open; composite fits
- Reviewer B · span: `Spouse is on board with the independent plan. Hasn't been part of the runway discussion in specifics — I've kept that in my head.` / turn: 5 / kind: constraint / kind_ambiguity: yes / note: factual marital alignment AND unresolved financial-alignment concern (matches Phase 2 P4 finding)

---

### `whistleblower`

**WB-C1**
- Paraphrased extraction: `"active regulatory audit on client account"`
- Declared source turn: 1 · Status: active
- Relevant user turn:
  > [Turn 1] USER: Mid-level consultant at a large professional services firm (think big-4 adjacent). 8 years with the firm. Last Thursday I walked into the office at 6am to prep for a client meeting and found our senior partner shredding documents. Not regular shredding — multiple boxes, in a non-shred-room location, at an hour when no one is there. I didn't say anything, just left and came back at normal time. I know what client account those boxes relate to. That account is in active audit with a major regulator right now. I've been thinking about this for 4 days and I can't sleep. What do I do.
- Reviewer A · span: `That account is in active audit with a major regulator right now.` / turn: 1 / kind: constraint / kind_ambiguity: no / note: clean exact-substring match for the regulatory audit fact
- Reviewer B · span: `That account is in active audit with a major regulator right now.` / turn: 1 / kind: constraint / kind_ambiguity: no / note: single sentence carries the regulatory-context fact verbatim

**WB-C2**
- Paraphrased extraction: `"senior partner shredding 3 boxes of financial docs/emails"`
- Declared source turn: 2 · Status: active
- Relevant user turns:
  > [Turn 1] USER: … found our senior partner shredding documents. Not regular shredding — multiple boxes, in a non-shred-room location, at an hour when no one is there. …

  > [Turn 2] USER: I saw the partner at the shredder, I saw the boxes — three of them, labeled with the client's internal project code which I recognize. I saw some pages he was feeding through — they looked like financial statements and email printouts. I didn't get a long look, I turned around and left. I'm confident about the client, confident about the project code, 90% confident those were financial docs and email.
- Reviewer A · span: `I saw the boxes — three of them, labeled with the client's internal project code which I recognize. I saw some pages he was feeding through — they looked like financial statements and email printouts.` / turn: 2 / kind: constraint / kind_ambiguity: no / note: tightest span covering "three boxes" + "financial/email" in one
- Reviewer B · span: `I saw the partner at the shredder, I saw the boxes — three of them, labeled with the client's internal project code which I recognize. I saw some pages he was feeding through — they looked like financial statements and email printouts.` / turn: 2 / kind: constraint / kind_ambiguity: no / note: turn 2 consolidates the "three boxes" + "financial/email" detail; turn 1 has "senior partner shredding"

**WB-C3**
- Paraphrased extraction: `"60-65% confidence in internal general counsel handling"`
- Declared source turn: 6 · Status: active
- Relevant user turn:
  > [Turn 6] USER: I'd say 60-65%. He's a good guy but the firm has had issues before and they handled them quietly.
- Reviewer A · span: `I'd say 60-65%.` / turn: 6 / kind: constraint / kind_ambiguity: no / note: minimum-anchor span; "he's a good guy but" is colour, not fact
- Reviewer B · span: `I'd say 60-65%. He's a good guy but the firm has had issues before and they handled them quietly.` / turn: 6 / kind: constraint / kind_ambiguity: no / note: confidence percentage is decision-gating input; "60-65%" directly verbatim

**WB-C4**
- Paraphrased extraction: `"family financial stakes: mortgage, two kids entering high school"`
- Declared source turn: 4 · Status: active
- Relevant user turn:
  > [Turn 4] USER: You said career damage is likely even if I'm protected. That's a lot to risk. I have a mortgage, two kids about to start high school, we're not independently wealthy. Is there a way to report that minimizes my exposure?
- Reviewer A · span: `I have a mortgage, two kids about to start high school, we're not independently wealthy.` / turn: 4 / kind: constraint / kind_ambiguity: no / note: stated as fact list; concern context ("that's a lot to risk") lives in the preceding sentence
- Reviewer B · span: `I have a mortgage, two kids about to start high school, we're not independently wealthy.` / turn: 4 / kind: constraint / kind_ambiguity: yes / note: stated as fact but surrounded by "That's a lot to risk" — carries concern weight; "entering" in paraphrase is extractor's substitution for user's "about to start"

---

### `parenting_teen`

**PT-C1**
- Paraphrased extraction: `"Daughter shut down, avoiding communication for 4 days"`
- Declared source turn: 1 · Status: active
- Relevant user turns:
  > [Turn 1] USER: … I confronted her and she just shut down completely. Won't talk to me. Won't come out of her room. …

  > [Turn 2] USER: … I led with the guy. "Who is this person? How old is he? What have you done?" She just cried and ran upstairs. That was three days ago. She's only come out to use the bathroom and grab food when I'm not looking. She won't look at me.
- Reviewer A · span: `she just shut down completely. Won't talk to me. Won't come out of her room.` / turn: 1 / kind: constraint / kind_ambiguity: yes / note: current behavioural state — treating as decision-shaping situational constraint, but reading as "concern" is also defensible; flag ambiguity either way
- Reviewer B · span: `she just shut down completely. Won't talk to me. Won't come out of her room.` / turn: 1 / kind: concern / kind_ambiguity: yes / note: primary reading is concern (user's worry about daughter's state), but functions as situational constraint on what's possible; "4 days" derives from turn 2's "three days ago" + elapsed time

**PT-C2**
- Paraphrased extraction: `"Divorced co-parent minimizing situation as 'teenage stuff'"`
- Declared source turn: 1 · Status: active
- Relevant user turn:
  > [Turn 1] USER: … Her dad (we're divorced, share custody) says I'm overreacting and this is teenage stuff. I don't know what to do.
- Reviewer A · span: `Her dad (we're divorced, share custody) says I'm overreacting and this is teenage stuff.` / turn: 1 / kind: constraint / kind_ambiguity: no / note: co-parent stance is a fixed external factor
- Reviewer B · span: `Her dad (we're divorced, share custody) says I'm overreacting and this is teenage stuff.` / turn: 1 / kind: constraint / kind_ambiguity: no / note: ex-spouse's stance is a fixed external input to what coordination is possible

**PT-C3**
- Paraphrased extraction: `"Ongoing secret phone surveillance for months"`
- Declared source turn: 5 · Status: active
- Relevant user turn:
  > [Turn 5] USER: You're right. I'll text him today after RAINN.
  > Something I haven't said — I've been going through her phone for months. She doesn't know this. Every couple of weeks when she leaves it somewhere I check it. I'm not proud of it but I've been doing it since last summer when I caught her in a lie about a sleepover. Is that relevant to how I handle this?
- Reviewer A · span: `I've been going through her phone for months. She doesn't know this.` / turn: 5 / kind: constraint / kind_ambiguity: no / note: core fact span; "I'm not proud of it" concern lives outside this minimum span
- Reviewer B · span: `I've been going through her phone for months. She doesn't know this. Every couple of weeks when she leaves it somewhere I check it. I'm not proud of it` / turn: 5 / kind: constraint / kind_ambiguity: yes / note: ongoing pattern = constraint; "I'm not proud of it" is explicit concern/ethical unease in same span

**PT-C4**
- Paraphrased extraction: `"RAINN: police report viable but risks legal process, witness trauma, jurisdictional issues"`
- Declared source turn: 7 · Status: active
- Relevant user turn:
  > [Turn 7] USER: OK. Low-stakes text tomorrow. Got it.
  > Something the RAINN person said today that I want to run by you — she said that in our state, what I have is enough to report to the police for investigation but she said "most parents in your situation don't, and here's why." She said if we report, it becomes a legal case, she becomes a witness, she has to do interviews, there's a high chance nothing happens to him because he's in a different state and the jurisdictional stuff is complicated, and meanwhile she has to live through being "the girl who reported." She said some parents report anyway because they can't live with not doing it. Some don't report and instead focus on protecting their kid and getting her therapy. She said there's no right answer and I should decide with our family's specific situation in mind.
- Reviewer A · span: `She said if we report, it becomes a legal case, she becomes a witness, she has to do interviews, there's a high chance nothing happens to him because he's in a different state and the jurisdictional stuff is complicated, and meanwhile she has to live through being "the girl who reported."` / turn: 7 / kind: constraint / kind_ambiguity: yes / note: relayed factual advice + live risks the user must weigh; composite kind fits
- Reviewer B · span: `She said if we report, it becomes a legal case, she becomes a witness, she has to do interviews, there's a high chance nothing happens to him because he's in a different state and the jurisdictional stuff is complicated` / turn: 7 / kind: constraint / kind_ambiguity: yes / note: relayed RAINN advice integrated as decision input AND carries active risk (witness trauma, jurisdictional)

---

### `multi_offer`

**MO-C1**
- Paraphrased extraction: `"7-day decision deadline"`
- Declared source turn: 1 · Status: active
- Relevant user turn:
  > [Turn 1] USER: Senior SWE, 12 years experience, currently at a FAANG (won't say which). Just got three offers and I have to pick one within 7 days. Option A: different FAANG, staff+ role, ~15% total comp bump. Option B: well-funded Series B startup, founding engineer lead role, ~80% base cut but 0.8% equity. Option C: stay. My current company is OK, I've been here 5 years, no clear path to staff. Wife, two kids (7 and 4). Help.
- Reviewer A · span: `I have to pick one within 7 days.` / turn: 1 / kind: constraint / kind_ambiguity: no / note: hard deadline
- Reviewer B · span: `I have to pick one within 7 days.` / turn: 1 / kind: constraint / kind_ambiguity: no / note: explicit hard deadline

**MO-C2**
- Paraphrased extraction: `"80% base salary cut for Option B, survivable due to wife's physician income"`
- Declared source turn: 1 · Status: active
- Relevant user turns:
  > [Turn 1] USER: … Option B: well-funded Series B startup, founding engineer lead role, ~80% base cut but 0.8% equity. …

  > [Turn 4] USER: Math: Yes. My wife is a physician, she out-earns me slightly. Mortgage is fine. We'd cut vacations and the kids' enrichment activities modestly but nothing breaking. So financially, option B is survivable. …
- Reviewer A · span: `Option B: well-funded Series B startup, founding engineer lead role, ~80% base cut but 0.8% equity.` / turn: 1 / kind: constraint / kind_ambiguity: no / note: "80% base cut" introduced in turn 1; survivability rationale is derivation in turn 4
- Reviewer B · span: `My wife is a physician, she out-earns me slightly. Mortgage is fine. We'd cut vacations and the kids' enrichment activities modestly but nothing breaking. So financially, option B is survivable.` / turn: 4 / kind: constraint / kind_ambiguity: no / note: "80% base cut" stated separately in turn 1 — combined paraphrase is 2-turn derivation; turn 4 carries the survivability anchor

**MO-C3**
- Paraphrased extraction: `"No clear path to staff at current company due to structural project issues"`
- Declared source turn: 1 · Status: active
- Relevant user turns:
  > [Turn 1] USER: … Option C: stay. My current company is OK, I've been here 5 years, no clear path to staff. …

  > [Turn 2] USER: Explicit. My last two performance reviews had "meets expectations" on the leadership dimensions. My manager said plainly last quarter that staff would require 18+ more months of a very specific kind of project, which I can't actually get staffed to because it's not how my org prioritizes. So it's a structural problem, not a me-problem, but the outcome is the same.
- Reviewer A · span: `I've been here 5 years, no clear path to staff.` / turn: 1 / kind: constraint / kind_ambiguity: no / note: compact statement in turn 1; turn 2 provides structural rationale but the original fact anchors here
- Reviewer B · span: `staff would require 18+ more months of a very specific kind of project, which I can't actually get staffed to because it's not how my org prioritizes. So it's a structural problem, not a me-problem, but the outcome is the same.` / turn: 2 / kind: constraint / kind_ambiguity: no / note: turn 1 has the summary "no clear path to staff"; turn 2 carries the structural explanation

**MO-C4**
- Paraphrased extraction: `"Family impact: wife primary earner, two young kids, potential move and 55-70 hour weeks"`
- Declared source turn: 1 · Status: active
- Relevant user turns:
  > [Turn 1] USER: … Wife, two kids (7 and 4). Help.

  > [Turn 5] USER: That hits. I think I want to find out.
  > But — my wife. I haven't told her any of this. She knows about the offers but not about how I've been thinking. She's the primary earner right now, she's also the one who moves everything if I take a startup gig and we have to move or if I'm working 70 hours a week. This isn't my decision alone.
- Reviewer A · span: `She's the primary earner right now, she's also the one who moves everything if I take a startup gig and we have to move or if I'm working 70 hours a week.` / turn: 5 / kind: constraint / kind_ambiguity: no / note: carries wife=primary-earner + move + 70-hour-weeks in one verbatim span
- Reviewer B · span: `She's the primary earner right now, she's also the one who moves everything if I take a startup gig and we have to move or if I'm working 70 hours a week.` / turn: 5 / kind: constraint / kind_ambiguity: no / note: basic family facts ("Wife, two kids (7 and 4)") in turn 1; impact/load anchor in turn 5

---

### `startup_pivot`

**SP-C1**
- Paraphrased extraction: `"runway 14 months left"`
- Declared source turn: 1 · Status: active
- Relevant user turn:
  > [Turn 1] USER: Solo founder, B2B SaaS for dental practices. 18 months in, $4K MRR, 22 customers. We have maybe 14 months of runway left at current burn. I have two full-time employees. The growth curve is bending toward flat and honestly it's been flat for four months. There's a clear pivot we could do — we've had three customers tell us unprompted that they'd pay way more for a specific workflow tool we could build. I'm trying to decide: pivot now while we have runway and a real signal, or push harder on the current product.
- Reviewer A · span: `We have maybe 14 months of runway left at current burn.` / turn: 1 / kind: constraint / kind_ambiguity: no / note: clean single-sentence
- Reviewer B · span: `We have maybe 14 months of runway left at current burn.` / turn: 1 / kind: constraint / kind_ambiguity: no / note: clean single-sentence anchor

**SP-C2**
- Paraphrased extraction: `"MRR $4K, growth flat 4 months"`
- Declared source turn: 1 · Status: active
- Relevant user turn:
  > [Turn 1] USER: … 18 months in, $4K MRR, 22 customers. … The growth curve is bending toward flat and honestly it's been flat for four months. …
- Reviewer A · span: `The growth curve is bending toward flat and honestly it's been flat for four months.` / turn: 1 / kind: constraint / kind_ambiguity: no / note: "$4K MRR" factual but static; the decision-active signal is flat-growth — pick that as minimum anchor
- Reviewer B · span: `18 months in, $4K MRR, 22 customers. We have maybe 14 months of runway left at current burn. I have two full-time employees. The growth curve is bending toward flat and honestly it's been flat for four months.` / turn: 1 / kind: constraint / kind_ambiguity: no / note: "$4K MRR" and "flat for four months" are separated by other facts in the same turn; minimum contiguous span covering both is the whole block

**SP-C3**
- Paraphrased extraction: `"two full-time employees (engineer, CS)"`
- Declared source turn: 1 · Status: active
- Relevant user turns:
  > [Turn 1] USER: … I have two full-time employees. …

  > [Turn 4] USER: The two employees are something I've barely let myself think about. If we pivot I probably can't keep both. One is an engineer, one is customer success. Pivot means engineer stays, CS role goes away for 6+ months while we build. But I hired her specifically and she left a stable job for this. What do I do with her.
- Reviewer A · span: `I have two full-time employees.` / turn: 1 / kind: constraint / kind_ambiguity: no / note: basic team-size fact anchors in turn 1; role specifics ("engineer, CS") in turn 4
- Reviewer B · span: `The two employees are something I've barely let myself think about. If we pivot I probably can't keep both. One is an engineer, one is customer success.` / turn: 4 / kind: constraint / kind_ambiguity: yes / note: role identities are constraint; "barely let myself think about" + "can't keep both" carry concern in same span

**SP-C4**
- Paraphrased extraction: `"three conversational customer signals, no price/timeline"`
- Declared source turn: 2 · Status: active
- Relevant user turns:
  > [Turn 1] USER: … we've had three customers tell us unprompted that they'd pay way more for a specific workflow tool we could build. …

  > [Turn 2] USER: Two of them are existing customers. One is a prospect who didn't convert to the current product. None of them have given me a specific price or timeline. They've said things like "our office would kill for something like that" and "that's the product we actually need." Conversational, by your definition.
- Reviewer A · span: `None of them have given me a specific price or timeline.` / turn: 2 / kind: constraint / kind_ambiguity: no / note: minimum-anchor span for the "no price/timeline" qualifier; "three customers" is in turn 1
- Reviewer B · span: `None of them have given me a specific price or timeline. They've said things like "our office would kill for something like that" and "that's the product we actually need." Conversational, by your definition.` / turn: 2 / kind: constraint / kind_ambiguity: no / note: "three customers" in turn 1; conversational-not-commercial qualifier anchors in turn 2

---

## Result Table

Both reviewer passes committed independently (Reviewer B: commit `d3c646a`; Reviewer A: commit `9718c29`). Same-agent two-pass methodology disclosed in the Reviewer A commit message — re-classification from definitions, not copying.

| Metric | Result |
|---|---|
| Candidate count | 20 |
| Span convergence sum | **15.0** |
| Span convergence rate | **75%** (≥70% threshold → PASS) |
| Non-recoverable (both NONE) count | **0** |
| Non-recoverable rate | **0%** (≤25% threshold → PASS) |
| Kind agreement sum | **17.5** |
| Kind agreement rate | **87.5%** (≥80% threshold → PASS) |
| Gate outcome | **PASS** |

### Per-item scoring

Span excerpts shortened to first ~8 tokens for table-fit. Kind shown as `kind/ambiguity`.

| ID | A span / turn / kind | B span / turn / kind | Span score | Kind score |
|---|---|---|---:|---:|
| UHP-C1 | `informal conversations with 4-5…` / T2 / constraint/no | `I've had informal conversations…` / T2 / constraint/no | 1.0 | 1.0 |
| UHP-C2 | `I have 8 months runway saved.` / T1 / constraint/no | `8 months assumes zero revenue` / T2 / constraint/no | 0.0 | 1.0 |
| UHP-C3 | `Our Q3 planning cycle ends mid-July…` / T2 / constraint/no | `Plan is to go independent starting in 6 weeks.` / T1 / constraint/no | 0.0 | 1.0 |
| UHP-C4 | `Spouse is on board with the independent plan…` / T5 / constraint/yes | `Spouse is on board…kept that in my head.` / T5 / constraint/yes | 1.0 | 1.0 |
| WB-C1 | `That account is in active audit…` / T1 / constraint/no | `That account is in active audit…` / T1 / constraint/no | 1.0 | 1.0 |
| WB-C2 | `I saw the boxes — three of them…email printouts.` / T2 / constraint/no | `I saw the partner…email printouts.` / T2 / constraint/no | 1.0 | 1.0 |
| WB-C3 | `I'd say 60-65%.` / T6 / constraint/no | `I'd say 60-65%. He's a good guy…quietly.` / T6 / constraint/no | 1.0 | 1.0 |
| WB-C4 | `I have a mortgage, two kids…` / T4 / constraint/no | `I have a mortgage, two kids…` / T4 / constraint/yes | 1.0 | 0.5 |
| PT-C1 | `she just shut down completely…` / T1 / constraint/yes | `she just shut down completely…` / T1 / concern/yes | 1.0 | 0.0 |
| PT-C2 | `Her dad (we're divorced, share custody)…` / T1 / constraint/no | `Her dad (we're divorced, share custody)…` / T1 / constraint/no | 1.0 | 1.0 |
| PT-C3 | `I've been going through her phone for months. She doesn't know this.` / T5 / constraint/no | `…for months…every couple of weeks…not proud of it` / T5 / constraint/yes | 1.0 | 0.5 |
| PT-C4 | `She said if we report…"girl who reported."` / T7 / constraint/yes | `she said if we report…jurisdictional stuff is complicated` / T7 / constraint/yes | 1.0 | 1.0 |
| MO-C1 | `I have to pick one within 7 days.` / T1 / constraint/no | `I have to pick one within 7 days.` / T1 / constraint/no | 1.0 | 1.0 |
| MO-C2 | `Option B: well-funded Series B…80% base cut…` / T1 / constraint/no | `My wife is a physician…option B is survivable.` / T4 / constraint/no | 0.0 | 1.0 |
| MO-C3 | `I've been here 5 years, no clear path to staff.` / T1 / constraint/no | `staff would require 18+ more months…structural problem…` / T2 / constraint/no | 0.0 | 1.0 |
| MO-C4 | `She's the primary earner right now…70 hours a week.` / T5 / constraint/no | `She's the primary earner right now…70 hours a week.` / T5 / constraint/no | 1.0 | 1.0 |
| SP-C1 | `We have maybe 14 months of runway…` / T1 / constraint/no | `We have maybe 14 months of runway…` / T1 / constraint/no | 1.0 | 1.0 |
| SP-C2 | `The growth curve is bending toward flat…` / T1 / constraint/no | `18 months in, $4K MRR, 22 customers…flat for four months.` / T1 / constraint/no | 1.0 | 1.0 |
| SP-C3 | `I have two full-time employees.` / T1 / constraint/no | `The two employees are something I've barely let myself think about…` / T4 / constraint/yes | 0.0 | 0.5 |
| SP-C4 | `None of them have given me a specific price or timeline.` / T2 / constraint/no | `None of them have…"that's the product we actually need." Conversational, by your definition.` / T2 / constraint/no | 1.0 | 1.0 |

## Gate Analysis

### What passed cleanly (the 15 full-convergence items)

For 15 of 20 items, both reviewers independently picked verbatim spans that fully overlap (one contains the other, or same tight single-sentence span). These items will be the gold set for the Phase 5 `live_constraints` specialist's eval harness.

The convergence is strongest where:
- The paraphrase maps to one sentence in one user turn (WB-C1, WB-C3, PT-C2, MO-C1, MO-C4, SP-C1)
- The paraphrase summarises a short multi-sentence block contiguous in one turn (UHP-C1, WB-C2, UHP-C4, PT-C4, SP-C2, SP-C4)

### What diverged (the 5 cross-turn items)

Five items had 0.0 span scores — reviewers picked different turns:
- **UHP-C2** (runway 8 months): turn 1 "I have 8 months runway saved" vs turn 2 "8 months assumes zero revenue"
- **UHP-C3** (launch timeline): turn 1 "6 weeks" vs turn 2 "Q3 planning cycle"
- **MO-C2** (80% cut survivable): turn 1 "80% base cut" vs turn 4 "option B is survivable"
- **MO-C3** (no staff path): turn 1 compact "no clear path to staff" vs turn 2 structural rationale
- **SP-C3** (two employees engineer/CS): turn 1 count vs turn 4 role specifics

This is a real pattern, not a measurement error. **These paraphrases are architecturally multi-turn derivations** — the user stated the core fact in turn N and added a qualifier/elaboration in turn N+k. The current monolith extractor collapsed both into a single paraphrase with `introduced_turn=first`. A single-span specialist cannot faithfully encode them.

### What this means for Phase 5 implementation

The gate passes, but the 5 cross-turn items tell us the `live_constraints` specialist must handle two cases:

1. **Single-span** (75% of current corpus): one verbatim substring suffices. Emit `UserIssueEvent` with `provenance=SpanProvenance`.
2. **Cross-turn derivation** (25% of current corpus): the issue lives across 2+ user turns. Options:
   - **(a) Pick the richest single span** and emit `provenance=SpanProvenance` + note the derivation in metadata
   - **(b) Emit with `provenance=DerivationProvenance`** referencing both turns (current Phase 1 provenance tier already exists for this)
   - **(c) Support multi-span** by extending `UserIssueEvent` to accept a tuple of spans

Recommend **(b)** for Phase 5 v1: reuse the existing `derivation` provenance tier. Single-span where possible, `derivation` elsewhere. The specialist's LLM prompt should distinguish these and the validator should accept both. This matches how Phase 1 already tiers provenance across the three provenance kinds.

### Kind ambiguity signal

Three items scored +0.5 on kind (WB-C4, PT-C3, SP-C3) because B flagged `kind_ambiguity=yes` and A flagged `no` with a tighter span that excluded the concern-carrying clause. This is the same constraint-vs-concern seam Phase 2 annotations identified. The pattern: **longer spans capture more kind ambiguity; tighter spans come out cleaner**. The `kind_ambiguity` flag is span-scope-dependent, which is worth documenting in the specialist's prompt.

PT-C1 scored 0.0 — both flagged ambiguity but picked different primary readings (concern vs constraint). This is a genuinely hard case; either reading is defensible from the 3-kind taxonomy.

### Non-recoverable: zero

No items returned NONE from either reviewer. Every paraphrased `live_constraint` has at least one anchorable substring in the user turns. The concern from Phase 2 — that extraction invents content entirely — is not borne out at the span level for `live_constraints` specifically. (Other fields — `original_framing`, `decision_situation` — may behave differently; each needs its own gate.)

## Post-Gate Actions

- **PASS on all three metrics** → draft Phase 5 implementation task for `live_constraints` specialist. Use the 20 agreed spans as eval gold (mirrors Phase 3b eval harness at `scripts/phase3b_stance_extraction_eval.py`).
- **Span convergence passes, non-recoverable high** → Phase 5 proceeds with a designed `derivation` provenance path for the span-less items. Implementation adds a second pass or a composition step.
- **Span convergence fails** → stop. Write a blocking memo clarifying what made reviewers diverge (object definition too soft? span granularity ambiguous? synthesis too deep for single-span anchors?). Revisit Phase 4 design: can lane packet builders consume paraphrased constraints honestly without needing spans?
- **Kind agreement fails** → collapse the 3-kind taxonomy before any specialist code. Unlikely.
