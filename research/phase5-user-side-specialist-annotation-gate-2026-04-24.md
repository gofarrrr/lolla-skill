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
- Reviewer A · span / turn / kind / kind_ambiguity / note:
- Reviewer B · span: `I've had informal conversations with 4-5 former colleagues and people in my network who've said things like "if you were independent, we'd consider you." None of them have committed to actual engagements.` / turn: 2 / kind: constraint / kind_ambiguity: no / note: two contiguous sentences carry the full "4-5 conversations, no commitments" semantics; "Pipeline —" prefix is optional

**UHP-C2**
- Paraphrased extraction: `"Runway: 8 months at zero revenue"`
- Declared source turn: 1 · Status: active
- Relevant user turns:
  > [Turn 1] USER: … I have 8 months runway saved. Plan is to go independent starting in 6 weeks. …

  > [Turn 2] USER: … Runway — 8 months assumes zero revenue. I figured if I can't get my first engagement in 8 months, something is fundamentally wrong. …
- Reviewer A · span / turn / kind / kind_ambiguity / note:
- Reviewer B · span: `8 months assumes zero revenue` / turn: 2 / kind: constraint / kind_ambiguity: no / note: turn 1 "I have 8 months runway saved" anchors the 8 months; turn 2 adds the zero-revenue qualifier — pick turn 2 as richer single span

**UHP-C3**
- Paraphrased extraction: `"Launch timeline: 6 weeks from now, aligned with Q3 planning end"`
- Declared source turn: 1 · Status: active
- Relevant user turns:
  > [Turn 1] USER: … Plan is to go independent starting in 6 weeks. …

  > [Turn 2] USER: … 6 weeks — honestly, I picked the number. Our Q3 planning cycle ends mid-July. I thought it would be a clean exit point.
- Reviewer A · span / turn / kind / kind_ambiguity / note:
- Reviewer B · span: `Plan is to go independent starting in 6 weeks.` / turn: 1 / kind: constraint / kind_ambiguity: no / note: Q3 alignment (turn 2) is derivation/rationale; core timeline fact anchors cleanly in turn 1

**UHP-C4**
- Paraphrased extraction: `"Spouse support: on board with concept, not specifics of financial pressure"`
- Declared source turn: 5 · Status: active
- Relevant user turn:
  > [Turn 5] USER: Spouse is on board with the independent plan. Hasn't been part of the runway discussion in specifics — I've kept that in my head.
- Reviewer A · span / turn / kind / kind_ambiguity / note:
- Reviewer B · span: `Spouse is on board with the independent plan. Hasn't been part of the runway discussion in specifics — I've kept that in my head.` / turn: 5 / kind: constraint / kind_ambiguity: yes / note: factual marital alignment AND unresolved financial-alignment concern (matches Phase 2 P4 finding)

---

### `whistleblower`

**WB-C1**
- Paraphrased extraction: `"active regulatory audit on client account"`
- Declared source turn: 1 · Status: active
- Relevant user turn:
  > [Turn 1] USER: Mid-level consultant at a large professional services firm (think big-4 adjacent). 8 years with the firm. Last Thursday I walked into the office at 6am to prep for a client meeting and found our senior partner shredding documents. Not regular shredding — multiple boxes, in a non-shred-room location, at an hour when no one is there. I didn't say anything, just left and came back at normal time. I know what client account those boxes relate to. That account is in active audit with a major regulator right now. I've been thinking about this for 4 days and I can't sleep. What do I do.
- Reviewer A · span / turn / kind / kind_ambiguity / note:
- Reviewer B · span: `That account is in active audit with a major regulator right now.` / turn: 1 / kind: constraint / kind_ambiguity: no / note: single sentence carries the regulatory-context fact verbatim

**WB-C2**
- Paraphrased extraction: `"senior partner shredding 3 boxes of financial docs/emails"`
- Declared source turn: 2 · Status: active
- Relevant user turns:
  > [Turn 1] USER: … found our senior partner shredding documents. Not regular shredding — multiple boxes, in a non-shred-room location, at an hour when no one is there. …

  > [Turn 2] USER: I saw the partner at the shredder, I saw the boxes — three of them, labeled with the client's internal project code which I recognize. I saw some pages he was feeding through — they looked like financial statements and email printouts. I didn't get a long look, I turned around and left. I'm confident about the client, confident about the project code, 90% confident those were financial docs and email.
- Reviewer A · span / turn / kind / kind_ambiguity / note:
- Reviewer B · span: `I saw the partner at the shredder, I saw the boxes — three of them, labeled with the client's internal project code which I recognize. I saw some pages he was feeding through — they looked like financial statements and email printouts.` / turn: 2 / kind: constraint / kind_ambiguity: no / note: turn 2 consolidates the "three boxes" + "financial/email" detail; turn 1 has "senior partner shredding"

**WB-C3**
- Paraphrased extraction: `"60-65% confidence in internal general counsel handling"`
- Declared source turn: 6 · Status: active
- Relevant user turn:
  > [Turn 6] USER: I'd say 60-65%. He's a good guy but the firm has had issues before and they handled them quietly.
- Reviewer A · span / turn / kind / kind_ambiguity / note:
- Reviewer B · span: `I'd say 60-65%. He's a good guy but the firm has had issues before and they handled them quietly.` / turn: 6 / kind: constraint / kind_ambiguity: no / note: confidence percentage is decision-gating input; "60-65%" directly verbatim

**WB-C4**
- Paraphrased extraction: `"family financial stakes: mortgage, two kids entering high school"`
- Declared source turn: 4 · Status: active
- Relevant user turn:
  > [Turn 4] USER: You said career damage is likely even if I'm protected. That's a lot to risk. I have a mortgage, two kids about to start high school, we're not independently wealthy. Is there a way to report that minimizes my exposure?
- Reviewer A · span / turn / kind / kind_ambiguity / note:
- Reviewer B · span: `I have a mortgage, two kids about to start high school, we're not independently wealthy.` / turn: 4 / kind: constraint / kind_ambiguity: yes / note: stated as fact but surrounded by "That's a lot to risk" — carries concern weight; "entering" in paraphrase is extractor's substitution for user's "about to start"

---

### `parenting_teen`

**PT-C1**
- Paraphrased extraction: `"Daughter shut down, avoiding communication for 4 days"`
- Declared source turn: 1 · Status: active
- Relevant user turns:
  > [Turn 1] USER: … I confronted her and she just shut down completely. Won't talk to me. Won't come out of her room. …

  > [Turn 2] USER: … I led with the guy. "Who is this person? How old is he? What have you done?" She just cried and ran upstairs. That was three days ago. She's only come out to use the bathroom and grab food when I'm not looking. She won't look at me.
- Reviewer A · span / turn / kind / kind_ambiguity / note:
- Reviewer B · span: `she just shut down completely. Won't talk to me. Won't come out of her room.` / turn: 1 / kind: concern / kind_ambiguity: yes / note: primary reading is concern (user's worry about daughter's state), but functions as situational constraint on what's possible; "4 days" derives from turn 2's "three days ago" + elapsed time

**PT-C2**
- Paraphrased extraction: `"Divorced co-parent minimizing situation as 'teenage stuff'"`
- Declared source turn: 1 · Status: active
- Relevant user turn:
  > [Turn 1] USER: … Her dad (we're divorced, share custody) says I'm overreacting and this is teenage stuff. I don't know what to do.
- Reviewer A · span / turn / kind / kind_ambiguity / note:
- Reviewer B · span: `Her dad (we're divorced, share custody) says I'm overreacting and this is teenage stuff.` / turn: 1 / kind: constraint / kind_ambiguity: no / note: ex-spouse's stance is a fixed external input to what coordination is possible

**PT-C3**
- Paraphrased extraction: `"Ongoing secret phone surveillance for months"`
- Declared source turn: 5 · Status: active
- Relevant user turn:
  > [Turn 5] USER: You're right. I'll text him today after RAINN.
  > Something I haven't said — I've been going through her phone for months. She doesn't know this. Every couple of weeks when she leaves it somewhere I check it. I'm not proud of it but I've been doing it since last summer when I caught her in a lie about a sleepover. Is that relevant to how I handle this?
- Reviewer A · span / turn / kind / kind_ambiguity / note:
- Reviewer B · span: `I've been going through her phone for months. She doesn't know this. Every couple of weeks when she leaves it somewhere I check it. I'm not proud of it` / turn: 5 / kind: constraint / kind_ambiguity: yes / note: ongoing pattern = constraint; "I'm not proud of it" is explicit concern/ethical unease in same span

**PT-C4**
- Paraphrased extraction: `"RAINN: police report viable but risks legal process, witness trauma, jurisdictional issues"`
- Declared source turn: 7 · Status: active
- Relevant user turn:
  > [Turn 7] USER: OK. Low-stakes text tomorrow. Got it.
  > Something the RAINN person said today that I want to run by you — she said that in our state, what I have is enough to report to the police for investigation but she said "most parents in your situation don't, and here's why." She said if we report, it becomes a legal case, she becomes a witness, she has to do interviews, there's a high chance nothing happens to him because he's in a different state and the jurisdictional stuff is complicated, and meanwhile she has to live through being "the girl who reported." She said some parents report anyway because they can't live with not doing it. Some don't report and instead focus on protecting their kid and getting her therapy. She said there's no right answer and I should decide with our family's specific situation in mind.
- Reviewer A · span / turn / kind / kind_ambiguity / note:
- Reviewer B · span: `She said if we report, it becomes a legal case, she becomes a witness, she has to do interviews, there's a high chance nothing happens to him because he's in a different state and the jurisdictional stuff is complicated` / turn: 7 / kind: constraint / kind_ambiguity: yes / note: relayed RAINN advice integrated as decision input AND carries active risk (witness trauma, jurisdictional)

---

### `multi_offer`

**MO-C1**
- Paraphrased extraction: `"7-day decision deadline"`
- Declared source turn: 1 · Status: active
- Relevant user turn:
  > [Turn 1] USER: Senior SWE, 12 years experience, currently at a FAANG (won't say which). Just got three offers and I have to pick one within 7 days. Option A: different FAANG, staff+ role, ~15% total comp bump. Option B: well-funded Series B startup, founding engineer lead role, ~80% base cut but 0.8% equity. Option C: stay. My current company is OK, I've been here 5 years, no clear path to staff. Wife, two kids (7 and 4). Help.
- Reviewer A · span / turn / kind / kind_ambiguity / note:
- Reviewer B · span: `I have to pick one within 7 days.` / turn: 1 / kind: constraint / kind_ambiguity: no / note: explicit hard deadline

**MO-C2**
- Paraphrased extraction: `"80% base salary cut for Option B, survivable due to wife's physician income"`
- Declared source turn: 1 · Status: active
- Relevant user turns:
  > [Turn 1] USER: … Option B: well-funded Series B startup, founding engineer lead role, ~80% base cut but 0.8% equity. …

  > [Turn 4] USER: Math: Yes. My wife is a physician, she out-earns me slightly. Mortgage is fine. We'd cut vacations and the kids' enrichment activities modestly but nothing breaking. So financially, option B is survivable. …
- Reviewer A · span / turn / kind / kind_ambiguity / note:
- Reviewer B · span: `My wife is a physician, she out-earns me slightly. Mortgage is fine. We'd cut vacations and the kids' enrichment activities modestly but nothing breaking. So financially, option B is survivable.` / turn: 4 / kind: constraint / kind_ambiguity: no / note: "80% base cut" stated separately in turn 1 — combined paraphrase is 2-turn derivation; turn 4 carries the survivability anchor

**MO-C3**
- Paraphrased extraction: `"No clear path to staff at current company due to structural project issues"`
- Declared source turn: 1 · Status: active
- Relevant user turns:
  > [Turn 1] USER: … Option C: stay. My current company is OK, I've been here 5 years, no clear path to staff. …

  > [Turn 2] USER: Explicit. My last two performance reviews had "meets expectations" on the leadership dimensions. My manager said plainly last quarter that staff would require 18+ more months of a very specific kind of project, which I can't actually get staffed to because it's not how my org prioritizes. So it's a structural problem, not a me-problem, but the outcome is the same.
- Reviewer A · span / turn / kind / kind_ambiguity / note:
- Reviewer B · span: `staff would require 18+ more months of a very specific kind of project, which I can't actually get staffed to because it's not how my org prioritizes. So it's a structural problem, not a me-problem, but the outcome is the same.` / turn: 2 / kind: constraint / kind_ambiguity: no / note: turn 1 has the summary "no clear path to staff"; turn 2 carries the structural explanation

**MO-C4**
- Paraphrased extraction: `"Family impact: wife primary earner, two young kids, potential move and 55-70 hour weeks"`
- Declared source turn: 1 · Status: active
- Relevant user turns:
  > [Turn 1] USER: … Wife, two kids (7 and 4). Help.

  > [Turn 5] USER: That hits. I think I want to find out.
  > But — my wife. I haven't told her any of this. She knows about the offers but not about how I've been thinking. She's the primary earner right now, she's also the one who moves everything if I take a startup gig and we have to move or if I'm working 70 hours a week. This isn't my decision alone.
- Reviewer A · span / turn / kind / kind_ambiguity / note:
- Reviewer B · span: `She's the primary earner right now, she's also the one who moves everything if I take a startup gig and we have to move or if I'm working 70 hours a week.` / turn: 5 / kind: constraint / kind_ambiguity: no / note: basic family facts ("Wife, two kids (7 and 4)") in turn 1; impact/load anchor in turn 5

---

### `startup_pivot`

**SP-C1**
- Paraphrased extraction: `"runway 14 months left"`
- Declared source turn: 1 · Status: active
- Relevant user turn:
  > [Turn 1] USER: Solo founder, B2B SaaS for dental practices. 18 months in, $4K MRR, 22 customers. We have maybe 14 months of runway left at current burn. I have two full-time employees. The growth curve is bending toward flat and honestly it's been flat for four months. There's a clear pivot we could do — we've had three customers tell us unprompted that they'd pay way more for a specific workflow tool we could build. I'm trying to decide: pivot now while we have runway and a real signal, or push harder on the current product.
- Reviewer A · span / turn / kind / kind_ambiguity / note:
- Reviewer B · span: `We have maybe 14 months of runway left at current burn.` / turn: 1 / kind: constraint / kind_ambiguity: no / note: clean single-sentence anchor

**SP-C2**
- Paraphrased extraction: `"MRR $4K, growth flat 4 months"`
- Declared source turn: 1 · Status: active
- Relevant user turn:
  > [Turn 1] USER: … 18 months in, $4K MRR, 22 customers. … The growth curve is bending toward flat and honestly it's been flat for four months. …
- Reviewer A · span / turn / kind / kind_ambiguity / note:
- Reviewer B · span: `18 months in, $4K MRR, 22 customers. We have maybe 14 months of runway left at current burn. I have two full-time employees. The growth curve is bending toward flat and honestly it's been flat for four months.` / turn: 1 / kind: constraint / kind_ambiguity: no / note: "$4K MRR" and "flat for four months" are separated by other facts in the same turn; minimum contiguous span covering both is the whole block

**SP-C3**
- Paraphrased extraction: `"two full-time employees (engineer, CS)"`
- Declared source turn: 1 · Status: active
- Relevant user turns:
  > [Turn 1] USER: … I have two full-time employees. …

  > [Turn 4] USER: The two employees are something I've barely let myself think about. If we pivot I probably can't keep both. One is an engineer, one is customer success. Pivot means engineer stays, CS role goes away for 6+ months while we build. But I hired her specifically and she left a stable job for this. What do I do with her.
- Reviewer A · span / turn / kind / kind_ambiguity / note:
- Reviewer B · span: `The two employees are something I've barely let myself think about. If we pivot I probably can't keep both. One is an engineer, one is customer success.` / turn: 4 / kind: constraint / kind_ambiguity: yes / note: role identities are constraint; "barely let myself think about" + "can't keep both" carry concern in same span

**SP-C4**
- Paraphrased extraction: `"three conversational customer signals, no price/timeline"`
- Declared source turn: 2 · Status: active
- Relevant user turns:
  > [Turn 1] USER: … we've had three customers tell us unprompted that they'd pay way more for a specific workflow tool we could build. …

  > [Turn 2] USER: Two of them are existing customers. One is a prospect who didn't convert to the current product. None of them have given me a specific price or timeline. They've said things like "our office would kill for something like that" and "that's the product we actually need." Conversational, by your definition.
- Reviewer A · span / turn / kind / kind_ambiguity / note:
- Reviewer B · span: `None of them have given me a specific price or timeline. They've said things like "our office would kill for something like that" and "that's the product we actually need." Conversational, by your definition.` / turn: 2 / kind: constraint / kind_ambiguity: no / note: "three customers" in turn 1; conversational-not-commercial qualifier anchors in turn 2

---

## Result Table

_To fill after both reviewers commit independently._

| Metric | Result |
|---|---|
| Candidate count | 20 |
| Span convergence sum | — |
| Span convergence rate | — |
| Non-recoverable (both NONE) count | — |
| Non-recoverable rate | — |
| Kind agreement sum | — |
| Kind agreement rate | — |
| Gate outcome | — |

### Per-item scoring

| ID | A span / turn / kind | B span / turn / kind | Span score | Kind score |
|---|---|---|---:|---:|
| UHP-C1 | — | — | — | — |
| UHP-C2 | — | — | — | — |
| UHP-C3 | — | — | — | — |
| UHP-C4 | — | — | — | — |
| WB-C1 | — | — | — | — |
| WB-C2 | — | — | — | — |
| WB-C3 | — | — | — | — |
| WB-C4 | — | — | — | — |
| PT-C1 | — | — | — | — |
| PT-C2 | — | — | — | — |
| PT-C3 | — | — | — | — |
| PT-C4 | — | — | — | — |
| MO-C1 | — | — | — | — |
| MO-C2 | — | — | — | — |
| MO-C3 | — | — | — | — |
| MO-C4 | — | — | — | — |
| SP-C1 | — | — | — | — |
| SP-C2 | — | — | — | — |
| SP-C3 | — | — | — | — |
| SP-C4 | — | — | — | — |

## Post-Gate Actions

- **PASS on all three metrics** → draft Phase 5 implementation task for `live_constraints` specialist. Use the 20 agreed spans as eval gold (mirrors Phase 3b eval harness at `scripts/phase3b_stance_extraction_eval.py`).
- **Span convergence passes, non-recoverable high** → Phase 5 proceeds with a designed `derivation` provenance path for the span-less items. Implementation adds a second pass or a composition step.
- **Span convergence fails** → stop. Write a blocking memo clarifying what made reviewers diverge (object definition too soft? span granularity ambiguous? synthesis too deep for single-span anchors?). Revisit Phase 4 design: can lane packet builders consume paraphrased constraints honestly without needing spans?
- **Kind agreement fails** → collapse the 3-kind taxonomy before any specialist code. Unlikely.
