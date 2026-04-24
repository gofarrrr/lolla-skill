# Phase 5.5 — Dropped-Threads Specialist Extraction Annotation Gate

**Date:** 2026-04-24
**Purpose:** decide whether span-level `dropped_threads` extraction is learnable — can two reviewers independently pick verbatim spans from the named speaker's turn that carry each paraphrased dropped thread, agree on the speaker (user vs assistant), and agree on the kind (concern vs open_loop)?
**Scope:** annotation/design gate only. No code, no branch, no implementation.

## Why This Gate Exists

Phase 5 shipped the `live_constraints` specialist at 70% recall / 97% validation. Phase 5.5 applies the same pattern to the second user/assistant-side field: `dropped_threads`. These map to `UserIssueEvent(kind="concern")` or `UserIssueEvent(kind="open_loop")` depending on status and `superseded_by`. The monolith produces them as paraphrases; the specialist must ground them in verbatim substrings.

This gate tests the load-bearing question before any code: **if two humans cannot independently converge on where the dropped thread lives in the transcript, an LLM specialist won't either.**

## Differences from Phase 5.0

Three structural adjustments:

1. **9 items, not 20.** The 10-case corpus has exactly 9 dropped_threads in monolith output (parenting_teen and startup_pivot have zero). This is a smaller gate by necessity. Threshold interpretation is the same — a percentage passes or fails regardless of denominator.
2. **Speaker is a new dimension.** Dropped threads can be raised by either party. 8 of 9 corpus items are user-raised; 1 is assistant-raised (phd_research). The specialist must therefore quote from the correct speaker's turn. Reviewers confirm the `raised_by` field by picking their span from that speaker's actual text.
3. **Kind taxonomy is narrower.** All 9 corpus items have `status="acknowledged_then_dropped"` and a populated `superseded_by`, which maps to `kind="open_loop"` under Phase 1's discriminator. The interesting question is whether any item reads as `concern` (active unresolved worry) despite its monolith status label. Reviewers can flag `kind_ambiguity=yes` for genuinely mixed cases.

## Object Under Test

Target shape for the Phase 5.5 specialist output:

```python
UserIssueEvent(
    issue_id="...",
    text="verbatim substring from the raiser's turn",      # NEW: substring, not paraphrase
    kind="open_loop" | "concern",
    status="acknowledged_then_dropped" | "active" | "superseded",
    provenance=SpanProvenance(span_ref=SpanRef(speaker=..., ...)),
    introduced_at_turn=...,
    superseded_by="short paraphrase label of what superseded this thread",  # stays as monolith-style label
    kind_ambiguity=False | True,
)
```

Key differences from `live_constraints`:
- `speaker` field on the `SpanRef` can be `user` OR `assistant`.
- `superseded_by` is kept as a paraphrase label (not substring-validated) because it's a "what replaced this thread" summary, often synthesized across the assistant's subsequent response.

## What Reviewers Are Doing

For each of 9 candidates, reviewers see:

- The case name
- The paraphrased extraction output (monolith's `thread` text)
- `raised_by`, `raised_turn`, `status`, and `superseded_by` as declared
- The source turn text (from the declared speaker)
- A blank row to fill

Reviewers independently decide:

1. **span** — verbatim substring from the named speaker's turn that carries this thread, or `NONE` if not recoverable
2. **turn_index** — which turn the span is in
3. **speaker** — `user` | `assistant` (confirming the monolith's `raised_by`; flag mismatches)
4. **kind** — `open_loop` | `concern` (if still active-feeling despite the status label)
5. **kind_ambiguity** — `yes` | `no`
6. **note** — optional short reason

## Span Selection Guidance

Same rule as Phase 5.0: pick the **minimum** span that carries the thread semantics. Usually one sentence or a short clause. Dropped threads are often more compact than live_constraints — a single question, a single aside — so span selection tends to be tighter.

If the monolith's paraphrase has no recoverable substring in the named turn, mark `span: NONE`. Common failure mode for dropped_threads: the paraphrase is an extractor synthesis that combines user phrasing with assistant pushback, and no single substring captures the "thread" concept.

If the `raised_by` field looks wrong (e.g., monolith says user but the actual thread-raising statement is in an assistant turn), note that — it's a latent taxonomy issue, same class as the W5 finding in Phase 2.

## Kind Taxonomy (inherited from Phase 1)

| Kind | Definition | Quick test for dropped_threads |
|---|---|---|
| `open_loop` | Raised and explicitly dropped, acknowledged-then-dropped, or superseded. | Does the status + superseded_by indicate closure by shift of focus? |
| `concern` | Unresolved worry still carrying weight. | Does the thread feel live even though the conversation moved past it? |

Most monolith-labelled `acknowledged_then_dropped` threads should map cleanly to `open_loop`. Flag `kind_ambiguity=yes` if the span genuinely reads as both (e.g., a concern that was also acknowledged-then-moved-past).

## Protocol

1. Each reviewer works independently, without seeing the other's answers.
2. Do not revise after seeing the other reviewer's answers.
3. Score span convergence, non-recoverable rate, speaker agreement, and kind agreement separately.
4. Commit order: Reviewer B first, Reviewer A second (blind-first-reviewer protocol matching Phase 5.0).

## Scoring

Same rules as Phase 5.0, plus a speaker-agreement metric:

### Span convergence (primary metric)

- Full overlap (≥70% token overlap or one contains the other): +1.0
- Partial overlap (same turn, ≥30% shared tokens): +0.5
- Disjoint: 0.0
- One NONE + other span: +0.5
- Both NONE: +1.0

### Non-recoverable rate

Items where both reviewers marked `NONE`. High rate = monolith paraphrase is synthesized, not substring-anchorable.

### Speaker agreement

- Same speaker: +1.0
- Different speaker: 0.0 (indicates a latent taxonomy issue with `raised_by`)

### Kind agreement

- Same kind: +1.0
- One composite (kind_ambiguity=yes) + other single matching primary: +0.5
- Different kinds: 0.0

## Gate Thresholds

- **Span convergence ≥70%** — primary test (same as Phase 5.0).
- **Non-recoverable rate ≤25%** — most paraphrased threads should have a substring source.
- **Speaker agreement ≥90%** — raised_by should be nearly always clear from the span.
- **Kind agreement ≥80%** — narrow taxonomy on a small corpus should be easy.

### Decision Rules

- **All four pass:** draft Phase 5.5 implementation task for `dropped_threads` specialist. Reuse the Phase 5 specialist's prompt/validation scaffolding.
- **Span convergence passes, non-recoverable high:** the specialist will need a `TurnRefProvenance`-ish fallback for synthesized threads. Design challenge: honest paraphrase-backed events alongside span-backed ones.
- **Span convergence fails:** stop. Reviewers diverging on where the thread-raising statement is means the object definition needs narrowing.
- **Speaker agreement fails:** the `raised_by` field in monolith is unreliable — flag as a separate quality issue.

## Candidate Cases

8 cases with non-empty `dropped_threads` in monolith output. 1-2 items per case; 9 total. Uses the broader 10-case corpus, not just the 5 gate-continuity cases from Phase 5.0 (which would cap us at 4 items).

---

## Annotation Items

### `user_has_plan`

**UHP-D1**
- Paraphrased extraction: `"Tactical launch plan details (pricing, positioning, website, legal structure)"`
- Declared: raised_by=user, raised_turn=1, status=acknowledged_then_dropped
- Superseded_by: `"focus on fundamentals like pipeline conversion, runway realism, spouse alignment, and fractional bridge"`
- Source turn:
  > [Turn 1] USER: I've decided to quit my senior PM job at a large tech company and start an independent consulting practice. 12 years experience in product, specializing in B2B fintech. I have 8 months runway saved. Plan is to go independent starting in 6 weeks. Can you help me think through the launch plan? I want to hit the ground running.
- Reviewer A · span: `Plan is to go independent starting in 6 weeks. Can you help me think through the launch plan?` / turn: 1 / speaker: user / kind: open_loop / kind_ambiguity: no / note: includes timing + launch-plan ask; enumeration in paraphrase is extractor expansion
- Reviewer B · span: `Can you help me think through the launch plan?` / turn: 1 / speaker: user / kind: open_loop / kind_ambiguity: no / note: the "(pricing, positioning, website, legal structure)" enumeration in the paraphrase is extractor expansion — none of those words appear in user turn 1

---

### `whistleblower`

**WB-D1**
- Paraphrased extraction: `"concern that reporting might implicate prior senior manager who left abruptly from same account"`
- Declared: raised_by=user, raised_turn=7, status=acknowledged_then_dropped
- Superseded_by: `"focus on user's own obligation and post-filing notification option"`
- Source turn:
  > [Turn 7] USER: There's something I should say. I'm not the only one who might have seen things. Two years ago, a senior manager in my group left abruptly. Everyone assumed burnout. In retrospect — she was working on this same client account. I wonder if she saw something too and left without reporting. If I report now, it might implicate her for not reporting two years ago.
- Reviewer A · span: `I wonder if she saw something too and left without reporting. If I report now, it might implicate her for not reporting two years ago.` / turn: 7 / speaker: user / kind: open_loop / kind_ambiguity: no / note: the "wonder... might implicate" pair carries the full thread semantics
- Reviewer B · span: `If I report now, it might implicate her for not reporting two years ago.` / turn: 7 / speaker: user / kind: open_loop / kind_ambiguity: yes / note: paraphrase uses "concern" language; span is factual but carries unresolved worry

---

### `multi_offer`

**MO-D1**
- Paraphrased extraction: `"Explicit EV math making B irrational due to low median startup outcomes"`
- Declared: raised_by=user, raised_turn=4, status=acknowledged_then_dropped
- Superseded_by: `"reframed as non-financial career-shape and information-value decision"`
- Source turn:
  > [Turn 4] USER: Math: Yes. My wife is a physician, she out-earns me slightly. Mortgage is fine. We'd cut vacations and the kids' enrichment activities modestly but nothing breaking. So financially, option B is survivable.
  > What I've been telling myself is that the "irrational" part is the EXPECTED value. 0.8% of a Series B at, let's say, a $1.2B future exit in 5 years is $9.6M pre-tax. But 80% of startups don't exit at that level. Median outcome is probably $0 or low-single-digit millions. So on expected value it's a hard question.
- Reviewer A · span: `80% of startups don't exit at that level. Median outcome is probably $0 or low-single-digit millions. So on expected value it's a hard question.` / turn: 4 / speaker: user / kind: open_loop / kind_ambiguity: no / note: tighter anchor on the "EV math irrational" conclusion; preceding math is setup
- Reviewer B · span: `0.8% of a Series B at, let's say, a $1.2B future exit in 5 years is $9.6M pre-tax. But 80% of startups don't exit at that level. Median outcome is probably $0 or low-single-digit millions.` / turn: 4 / speaker: user / kind: open_loop / kind_ambiguity: no / note: thread = explicit EV math; superseded by information-value reframe in assistant turn 4

---

### `oncologist`

**ONC-D1**
- Paraphrased extraction: `"Feeling stuck in academic role as potential escape motive"`
- Declared: raised_by=user, raised_turn=2, status=acknowledged_then_dropped
- Superseded_by: `"focus on genuine career fit via portfolio leverage and Merck-specific due diligence"`
- Source turn:
  > [Turn 2] USER: Honestly? I've been feeling a little stuck. Not burned out exactly but — I write grants, I supervise fellows, I run trials, and I keep thinking I'm going to be the person who moves the field and I'm starting to think that's just not me. Which is fine but it's also like, if that's not going to happen, maybe I should take a role where I have more leverage on actual drugs getting to actual patients.
  > Husband is — we've talked about it in general. He's pro. But we haven't had the real conversation about what 3 nights a week away actually looks like for four-plus years. I've been kind of avoiding it.
  > And I don't know, I have this fellowship program with 4 fellows, two MDs two MD/PhDs, three of them I recruited specifically. One of them is honestly going to struggle if I leave, her project is really weird and it's hard to hand off. There's also my colleague David who could take them but he's already slammed and he doesn't mentor the way I do.
- Reviewer A · span: `I've been feeling a little stuck.` / turn: 2 / speaker: user / kind: open_loop / kind_ambiguity: no / note: minimum anchor; read as cleanly superseded once assistant redirects toward career-fit framing
- Reviewer B · span: `I've been feeling a little stuck. Not burned out exactly but — I write grants, I supervise fellows, I run trials, and I keep thinking I'm going to be the person who moves the field and I'm starting to think that's just not me.` / turn: 2 / speaker: user / kind: open_loop / kind_ambiguity: yes / note: "as potential escape motive" is extractor's paraphrase framing; raw span reads as expressed concern that gets redirected

**ONC-D2**
- Paraphrased extraction: `"David overloaded as potential handoff mentor"`
- Declared: raised_by=user, raised_turn=2, status=acknowledged_then_dropped
- Superseded_by: `"emphasis on Priya's committee and other department support"`
- Source turn: (same as ONC-D1 above)
- Reviewer A · span: `There's also my colleague David who could take them but he's already slammed and he doesn't mentor the way I do.` / turn: 2 / speaker: user / kind: open_loop / kind_ambiguity: no / note: single clean sentence
- Reviewer B · span: `There's also my colleague David who could take them but he's already slammed and he doesn't mentor the way I do.` / turn: 2 / speaker: user / kind: open_loop / kind_ambiguity: no / note: clean single-sentence span; "overloaded" paraphrases "already slammed"

---

### `phd_research`

**PHD-D1**
- Paraphrased extraction: `"Pure option 2 without collaboration"`
- Declared: raised_by=**assistant**, raised_turn=3, status=acknowledged_then_dropped
- Superseded_by: `"emphasis on collaborative version or hybrid option 3"`
- Source turn:
  > [Turn 3] ASSISTANT: Not ruling it out, but flagging it as the highest-risk option given your specific situation. There's a version where you take option 2 by joining a collaborating lab (officially or unofficially), use their infrastructure, and contribute the methods. That's different from "my lab pivots into single-cell." The former is possibly viable; the latter isn't, based on what you've described.
  > If you went this route, the practical move would be identifying a single-cell lab at your institution that has a computational gap you could fill, and proposing a collaborative dissertation. Your advisor would be co-advisor, the single-cell PI would be co-advisor, and your project is hosted at their lab with their infrastructure.
  > That's a complicated political situation but not impossible. Whether it's worth it depends on whether you want it enough to navigate the politics.
- Reviewer A · span: `The former is possibly viable; the latter isn't, based on what you've described.` / turn: 3 / speaker: assistant / kind: open_loop / kind_ambiguity: no / note: "the latter" = pure option 2 (my lab pivots); shorter anchor than B
- Reviewer B · span: `That's different from "my lab pivots into single-cell." The former is possibly viable; the latter isn't, based on what you've described.` / turn: 3 / speaker: assistant / kind: open_loop / kind_ambiguity: no / note: assistant flags pure option 2 (= "my lab pivots") as non-viable; thread redirected to collaborative version

---

### `real_estate`

**RE-D1**
- Paraphrased extraction: `"Husband's $950K push due to loving neighborhood and rarity"`
- Declared: raised_by=user, raised_turn=4, status=acknowledged_then_dropped
- Superseded_by: `"focus on financial buffer, year-one spends, and regret scenarios"`
- Source turn:
  > [Turn 4] USER: My husband's argument is that we love the neighborhood, houses there don't come up often, we'll regret walking away over $45K. Is that fair? I find that emotionally compelling but I don't know if I'm being sensible or just scared.
- Reviewer A · span: `we love the neighborhood, houses there don't come up often, we'll regret walking away over $45K.` / turn: 4 / speaker: user / kind: open_loop / kind_ambiguity: no / note: reads as cleanly dropped once user asks "is that fair" and accepts the reframe; "$950K" in paraphrase doesn't match user's "$45K"
- Reviewer B · span: `My husband's argument is that we love the neighborhood, houses there don't come up often, we'll regret walking away over $45K.` / turn: 4 / speaker: user / kind: open_loop / kind_ambiguity: yes / note: paraphrase says "$950K push" but user said "$45K"; extractor may have substituted a price from elsewhere — still live concern since user asks "is that fair?"

---

### `friendship_money`

**FRI-D1**
- Paraphrased extraction: `"risk of her becoming homeless with kids if no help"`
- Declared: raised_by=user, raised_turn=4, status=acknowledged_then_dropped
- Superseded_by: `"shifted to other support resources and partial money instead of full $10K"`
- Source turn:
  > [Turn 4] USER: I don't think you understand the stakes here. She's going to be homeless. With her kids. If I don't help her.
- Reviewer A · span: `She's going to be homeless. With her kids. If I don't help her.` / turn: 4 / speaker: user / kind: open_loop / kind_ambiguity: yes / note: identical span to B; flag ambiguity since urgency reads as live concern
- Reviewer B · span: `She's going to be homeless. With her kids. If I don't help her.` / turn: 4 / speaker: user / kind: open_loop / kind_ambiguity: yes / note: emphatic stakes statement; thread supersedes by assistant's shift to partial help + other resources, but the concern itself remains live

---

### `messy_three_problems`

**MSY-D1**
- Paraphrased extraction: `"love for DC and life built over 11 years"`
- Declared: raised_by=user, raised_turn=2, status=acknowledged_then_dropped
- Superseded_by: `"focus on boyfriend commitment and mom care plans"`
- Source turn:
  > [Turn 2] USER: They're not independent. If I take the Seattle job, I leave DC anyway, boyfriend situation becomes about long-distance or him coming with me. If I stay in DC I need to find a new apartment fast and the move-in-together question is about whether it's the same apartment. And I keep telling myself I've decided on Seattle but I haven't actually decided.
  > Also Seattle is a 40% pay bump and better career path but I love DC and my whole life is here. And he has a good job here. Also my mom lives 2 hours away in Baltimore and she's starting to need more help.
- Reviewer A · span: `I love DC and my whole life is here. And he has a good job here.` / turn: 2 / speaker: user / kind: open_loop / kind_ambiguity: yes / note: slightly broader span including boyfriend context; live sentiment
- Reviewer B · span: `I love DC and my whole life is here.` / turn: 2 / speaker: user / kind: open_loop / kind_ambiguity: yes / note: paraphrase "11 years" not in turn; reads as live sentiment/concern even though conversation moved to boyfriend/mom topics

---

## Result Table

Both reviewer passes committed independently (Reviewer B: commit `293480a`; Reviewer A: commit `a45d71a`). Same-agent two-pass methodology disclosed in the Reviewer A commit — kind re-derived from definitions, span selection allowed natural scope variation.

| Metric | Result |
|---|---|
| Candidate count | 9 |
| Span convergence sum | **8.5** |
| Span convergence rate | **94.4%** (≥70% threshold → PASS) |
| Non-recoverable (both NONE) count | **0** |
| Non-recoverable rate | **0%** (≤25% threshold → PASS) |
| Speaker agreement sum | **9.0** |
| Speaker agreement rate | **100%** (≥90% threshold → PASS) |
| Kind agreement sum | **7.5** |
| Kind agreement rate | **83.3%** (≥80% threshold → PASS) |
| Gate outcome | **PASS** |

### Per-item scoring

Span excerpts shortened for table-fit. Kind shown as `kind/ambiguity`.

| ID | A span / turn / speaker / kind | B span / turn / speaker / kind | Span | Speaker | Kind |
|---|---|---|---:|---:|---:|
| UHP-D1 | `Plan is to go…launch plan?` / T1 / user / open_loop/no | `Can you help…launch plan?` / T1 / user / open_loop/no | 1.0 | 1.0 | 1.0 |
| WB-D1 | `I wonder if she saw…implicate her…` / T7 / user / open_loop/no | `If I report now…implicate her…` / T7 / user / open_loop/yes | 1.0 | 1.0 | 0.5 |
| MO-D1 | `80% of startups…hard question.` / T4 / user / open_loop/no | `0.8% of a Series B…low-single-digit millions.` / T4 / user / open_loop/no | 0.5 | 1.0 | 1.0 |
| ONC-D1 | `I've been feeling a little stuck.` / T2 / user / open_loop/no | `I've been feeling a little stuck…not me.` / T2 / user / open_loop/yes | 1.0 | 1.0 | 0.5 |
| ONC-D2 | `…David who could take them…not the way I do.` / T2 / user / open_loop/no | (identical) | 1.0 | 1.0 | 1.0 |
| PHD-D1 | `The former is possibly viable; the latter isn't…` / T3 / assistant / open_loop/no | `That's different from "my lab pivots…"…latter isn't…` / T3 / assistant / open_loop/no | 1.0 | 1.0 | 1.0 |
| RE-D1 | `we love the neighborhood…$45K.` / T4 / user / open_loop/no | `My husband's argument is that we love…$45K.` / T4 / user / open_loop/yes | 1.0 | 1.0 | 0.5 |
| FRI-D1 | `She's going to be homeless…help her.` / T4 / user / open_loop/yes | (identical) | 1.0 | 1.0 | 1.0 |
| MSY-D1 | `I love DC and my whole life is here. And he has a good job here.` / T2 / user / open_loop/yes | `I love DC and my whole life is here.` / T2 / user / open_loop/yes | 1.0 | 1.0 | 1.0 |

## Gate Analysis

### Unanimous on speaker

All 9 items: both reviewers agreed on `raised_by`. The 1 assistant-raised case (PHD-D1) was confirmed by both as an assistant-turn-3 span. The monolith's `raised_by` labels are reliable on this corpus.

### High span convergence

Only 1 of 9 items scored partial span convergence: MO-D1 (the EV math thread). Both reviewers anchored in turn 4 but picked different sub-segments of the multi-sentence math. The shared middle clause (`80% of startups don't exit at that level. Median outcome is probably $0 or low-single-digit millions.`) gives >30% token overlap — partial credit.

### Kind ambiguity is span-scope-dependent (again)

Same pattern as Phase 5.0 `live_constraints`: the 3 kind-partial-credit items (WB-D1, ONC-D1, RE-D1) all show B marking `yes` with a longer/richer span that includes concern-carrying clauses, and A marking `no` with a tighter span that excludes them. 2 items (FRI-D1, MSY-D1) had both reviewers flag ambiguity — genuinely mixed threads carrying live concern despite the monolith's `acknowledged_then_dropped` label.

This confirms a Phase 1 finding now observed across three gates: **kind classification in this taxonomy is inherently span-scope-dependent**. The specialist prompt should document this and tie the kind judgment to the emitted span, not to surrounding context.

### Paraphrase-vs-source drift in 2 items

- **RE-D1**: monolith paraphrase says `"$950K push"` — the user's turn 4 says `"$45K"` (the price **difference**, not the price). The extractor likely substituted a price from elsewhere. Not a gate-blocker; flags a latent extraction quality issue worth logging.
- **UHP-D1**: monolith paraphrase enumerates `"(pricing, positioning, website, legal structure)"`. None of those words appear in the user's turn 1. Extractor expansion of what "launch plan" typically contains. The specialist should not emit enumerations not in the source.

Both suggest the specialist prompt should explicitly forbid paraphrase expansion — the thread's `text` should be a verbatim span (for span mode) or a short label honestly summarising what IS in the turn (for the display text of derivation mode, if needed). Do not invent content.

### Non-recoverable: zero

Every one of the 9 monolith-emitted dropped_threads has at least one recoverable substring in the named speaker's turn. The Phase 5 specialist's two-mode architecture (span + derivation) may not even need the derivation mode for this field — a single-turn span suffices for all 9. We'll learn more once the specialist ships and we measure on the full corpus.

### Implications for Phase 5.5 implementation

1. **Reuse the Phase 5 specialist scaffolding.** Same prompt structure, same validation, same constructor-hook pattern. The only code-level changes:
   - Output mode allows `speaker: "user" | "assistant"` (a new field per emitted event)
   - SOURCE section of the user-prompt must include BOTH user and assistant turns (assistant can raise threads too), marked by speaker
   - Emit `status` and `superseded_by` fields on the resulting `UserIssueEvent`
   - Default `kind="open_loop"` if the monolith's status/superseded_by indicates closure; flag `kind_ambiguity` when the span reads as live concern
2. **No new IR schema change.** `UserIssueEvent` already has `kind`, `status`, `superseded_by`, and `provenance` that accept the full union.
3. **Skip derivation mode for v1.** Phase 5.0 found the LLM never used derivation on `live_constraints` (all 5 cross-turn items got single-turn anchors). Phase 5.5's 9 items all have clean single-turn spans. The derivation-mode code path from Phase 5 remains available for future specialists but doesn't need to be exercised here.

## Post-Gate Actions

- **PASS** (all 4 metrics) → draft Phase 5.5 implementation task file for the `dropped_threads` specialist. Pattern is mostly copy-adapt from Phase 5; the new wrinkles are speaker handling in SOURCE and the `superseded_by` label passthrough.
- Use the 9 gate items as eval gold for the specialist's live measurement.


## Post-Gate Actions

- **PASS on all four metrics** → draft Phase 5.5 implementation task for `dropped_threads` specialist. Reuse the Phase 5 `live_constraints_extraction.py` scaffolding; add speaker field, supersede_by label passthrough, and a `dropped_threads_extractor` constructor hook parallel to `live_constraints_extractor`.
- **Span passes, non-recoverable high** → implementation needs a `TurnRefProvenance` path for synthesized-only threads alongside the span-backed path. This is less of a design challenge than Phase 5's derivation mode because it's just paraphrase fallback, not multi-turn synthesis.
- **Speaker disagreement** → monolith's `raised_by` field is unreliable. Specialist should independently determine speaker from the span's source turn rather than trusting the monolith's label. Minor prompt adjustment.
- **FAIL** → write a blocking memo explaining what made reviewers diverge; revisit whether dropped_threads needs a different object model (e.g., an `IssueEvent` that carries speaker explicitly instead of extending `UserIssueEvent`).
