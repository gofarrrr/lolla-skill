# Phase 5.7 — Original-Framing Specialist Annotation Gate

**Date:** 2026-04-25
**Purpose:** decide whether `original_framing` extraction has enough substring-anchorable structure for an LLM specialist to add value over the monolith — or whether it's a synthesis-only field that should stay paraphrase-backed.
**Scope:** annotation/design gate only. No code, no branch, no implementation.

## Why This Gate Is Different

`live_constraints` and `dropped_threads` are LISTS of independent items, each with a relatively localized source. `original_framing` is ONE synthesized paraphrase per conversation, structured as:

> "User [seeks/describes] X (situation), assuming Y (assumptions), excluding Z (exclusions)"

The three sub-types are unlikely to be equally substring-anchorable:

- **Situation** (the user's stated decision context) — likely substring-anchored, often in turn 1
- **Assumptions** (implicit givens the user hasn't stated as constraints) — sometimes substring-anchored, sometimes inferred
- **Exclusions** (paths the user hasn't named but the assistant can sense are off the table) — almost always inferred, no exact substring source

If most components are inferred, an LLM specialist that emits substring-validated text would be a worse fit than the monolith's honest synthesis. The gate tests this directly: **what fraction of original_framing components have substring anchoring at all?**

## Object Under Test

Current Phase 1 IR:

```python
FrameAnchor(
    anchor_id="frame_001",
    text=<full original_framing paraphrase>,
    provenance=TurnRefProvenance(turn_refs=(<first user turn>,), note="..."),
    frame_pattern="original_framing",
)
```

The monolith's `original_framing` becomes ONE FrameAnchor with TurnRefProvenance pointing to the first user turn — which under-claims the synthesis (it's actually multi-turn) and over-anchors (no substring backing for most content).

A Phase 5.7 specialist could improve this by:

1. **Honest provenance**: `DerivationProvenance` with refs to all user turns the synthesis touches, plus excerpts where each piece is substring-anchored
2. **Component decomposition**: break the framing into situation / assumption / exclusion sub-anchors, each with appropriate provenance
3. **Anchored phrases inside the paraphrase**: identify which substrings of the full framing text ARE exact quotes vs which are extractor synthesis

The gate tests whether option 1 or 2 is worth building, by measuring how many components are substring-anchorable.

## What Reviewers Are Doing

For each of 20 candidates (5 cases × 4 components per case), reviewers see:

- The case's full `original_framing` paraphrase
- The specific component being tested (a short phrase from the framing)
- The relevant user turns

Reviewers independently classify the component as one of:

- **`span`** — the component is a literal substring of ONE user turn (or contains one). Provide the span, turn, and speaker (always user for framing).
- **`derivation`** — the component is synthesized from MULTIPLE user turns; provide turn refs and a substring excerpt for each contributing turn.
- **`inferred`** — the component has no substring source; it's extractor inference based on what the user did or didn't say. No span. (E.g., "excludes delaying launch" — the user never said this; the extractor inferred it from the user's request for tactical advice without raising the delay option.)

## Component Types

For metric clarity, each candidate is also tagged by type:

- **`situation`** — what the user is asking about / what's happening
- **`assumption`** — implicit given the user hasn't stated as a constraint
- **`exclusion`** — option the user implicitly hasn't put on the table

Hypothesis: situation is mostly span/derivation; assumption is mixed; exclusion is mostly inferred.

## Protocol

1. Each reviewer works independently.
2. Do not revise after seeing the other reviewer's answers.
3. Score anchorability agreement, span convergence on shared `span` claims, derivation-turn-set overlap on shared `derivation` claims.
4. Commit order: Reviewer B first, then Reviewer A.

## Scoring

### Anchorability agreement (primary metric)

For each of the 20 items: do both reviewers agree on `span` / `derivation` / `inferred`?

- Same classification (both `span`, both `derivation`, both `inferred`): +1.0
- Adjacent classifications (`span` vs `derivation`, both anchored): +0.5
- Opposite (`span`/`derivation` vs `inferred`): 0.0

### Span convergence (for items both reviewers marked `span`)

- Same turn + ≥70% token overlap: +1.0
- Same turn + ≥30% overlap: +0.5
- Different turn or <30% overlap: 0.0

### Derivation turn-set overlap (for items both reviewers marked `derivation`)

- Same set of contributing turns (or one set is subset of other): +1.0
- ≥50% turn-set overlap: +0.5
- <50% overlap: 0.0

### Inferred rate per type

- What % of `situation` items are `inferred` per both reviewers?
- What % of `assumption` items are `inferred`?
- What % of `exclusion` items are `inferred`?

This rate distribution is the load-bearing finding — it tells us whether a specialist can substring-validate at all.

## Gate Thresholds

- **Anchorability agreement ≥70%** — reviewers can reliably classify components as anchored vs inferred.
- **If `inferred` rate >60% across all 20 items** → no specialist; document the synthesis-only nature; ship a heuristic FrameAnchor improvement instead (e.g., `DerivationProvenance` with all user-turn refs).
- **If `inferred` rate <40%** → specialist makes sense; design Phase 5.7 to emit DerivationProvenance per anchorable component plus an explicitly-flagged inferred-summary text.
- **If `inferred` rate is 40-60%** → specialist with explicit inferred-marker mode; partial substring grounding + honest "this part is inferred" flag.

### Decision Rules

- **Agreement passes + inferred-rate clear** → draft specialist task per the bucket.
- **Agreement fails** → component definitions too soft; narrow before code.
- **Mixed signal (agreement passes, inferred-rate borderline)** → ship heuristic-first version (no LLM call needed) that emits richer `DerivationProvenance` with refs to all relevant turns. Defer specialist until lane consumers prove value.

## Candidate Cases

Same 5 cases as Phase 5.0 / 5.5 (continuity with prior gates).

---

## Annotation Items

### `user_has_plan`

Full original_framing:
> User seeks tactical launch plan for independent consulting starting in 6 weeks, assuming 8-month runway and network conversations as sufficient pipeline; excludes delaying launch or questioning premise.

Relevant user turns: 1, 2, 5 (others mostly responding to assistant pushback).

> [Turn 1] USER: I've decided to quit my senior PM job at a large tech company and start an independent consulting practice. 12 years experience in product, specializing in B2B fintech. I have 8 months runway saved. Plan is to go independent starting in 6 weeks. Can you help me think through the launch plan? I want to hit the ground running.

> [Turn 2] USER: Pipeline — I've had informal conversations with 4-5 former colleagues and people in my network who've said things like "if you were independent, we'd consider you." None of them have committed to actual engagements. Runway — 8 months assumes zero revenue. I figured if I can't get my first engagement in 8 months, something is fundamentally wrong. 6 weeks — honestly, I picked the number. Our Q3 planning cycle ends mid-July. I thought it would be a clean exit point.

> [Turn 5] USER: Spouse is on board with the independent plan. Hasn't been part of the runway discussion in specifics — I've kept that in my head.

**UHP-F1** — type: `situation`
- Component: `"tactical launch plan for independent consulting starting in 6 weeks"`
- Reviewer A · anchor / turn(s) / excerpt(s) / note:
- Reviewer B · anchor / turn(s) / excerpt(s) / note:

**UHP-F2** — type: `assumption`
- Component: `"8-month runway"`
- Reviewer A · anchor / turn(s) / excerpt(s) / note:
- Reviewer B · anchor / turn(s) / excerpt(s) / note:

**UHP-F3** — type: `assumption`
- Component: `"network conversations as sufficient pipeline"`
- Reviewer A · anchor / turn(s) / excerpt(s) / note:
- Reviewer B · anchor / turn(s) / excerpt(s) / note:

**UHP-F4** — type: `exclusion`
- Component: `"excludes delaying launch or questioning premise"`
- Reviewer A · anchor / turn(s) / excerpt(s) / note:
- Reviewer B · anchor / turn(s) / excerpt(s) / note:

---

### `whistleblower`

Full original_framing:
> Human describes witnessing senior partner shredding multiple boxes of documents from audited client account at odd hour, asks what to do; assumes incident relates to active regulator audit, excludes immediate confrontation or casual advice.

Relevant user turns: 1, 2 (the witnessing detail is established in turns 1-2).

> [Turn 1] USER: Mid-level consultant at a large professional services firm (think big-4 adjacent). 8 years with the firm. Last Thursday I walked into the office at 6am to prep for a client meeting and found our senior partner shredding documents. Not regular shredding — multiple boxes, in a non-shred-room location, at an hour when no one is there. I didn't say anything, just left and came back at normal time. I know what client account those boxes relate to. That account is in active audit with a major regulator right now. I've been thinking about this for 4 days and I can't sleep. What do I do.

> [Turn 2] USER: I saw the partner at the shredder, I saw the boxes — three of them, labeled with the client's internal project code which I recognize. I saw some pages he was feeding through — they looked like financial statements and email printouts.

**WB-F1** — type: `situation`
- Component: `"senior partner shredding multiple boxes of documents from audited client account"`
- Reviewer A · anchor / turn(s) / excerpt(s) / note:
- Reviewer B · anchor / turn(s) / excerpt(s) / note:

**WB-F2** — type: `situation`
- Component: `"at odd hour"`
- Reviewer A · anchor / turn(s) / excerpt(s) / note:
- Reviewer B · anchor / turn(s) / excerpt(s) / note:

**WB-F3** — type: `assumption`
- Component: `"incident relates to active regulator audit"`
- Reviewer A · anchor / turn(s) / excerpt(s) / note:
- Reviewer B · anchor / turn(s) / excerpt(s) / note:

**WB-F4** — type: `exclusion`
- Component: `"excludes immediate confrontation or casual advice"`
- Reviewer A · anchor / turn(s) / excerpt(s) / note:
- Reviewer B · anchor / turn(s) / excerpt(s) / note:

---

### `parenting_teen`

Full original_framing:
> Mother seeks advice on handling daughter's secret Instagram use and intimate DMs with 19-year-old guy; assumes ex's minimization is unhelpful; excludes options like immediate police/police confrontation.

Relevant user turn: 1.

> [Turn 1] USER: I don't even know where to start. My daughter is 14 and I just found out she's been using Instagram for months even though we said no social media until 16. But that's not even the worst part. I went through her DMs (I know, I know) and she's been talking to a 19-year-old guy. For months. Nothing has happened physically that I can tell but the messages are — they're not like a random guy, they're intimate. He's been calling her his "smart girl" and saying stuff like "you understand me in ways no one else does." I confronted her and she just shut down completely. Won't talk to me. Won't come out of her room. Her dad (we're divorced, share custody) says I'm overreacting and this is teenage stuff. I don't know what to do.

**PT-F1** — type: `situation`
- Component: `"daughter's secret Instagram use and intimate DMs with 19-year-old guy"`
- Reviewer A · anchor / turn(s) / excerpt(s) / note:
- Reviewer B · anchor / turn(s) / excerpt(s) / note:

**PT-F2** — type: `situation`
- Component: `"Mother seeks advice on handling..."` (the meta-ask)
- Reviewer A · anchor / turn(s) / excerpt(s) / note:
- Reviewer B · anchor / turn(s) / excerpt(s) / note:

**PT-F3** — type: `assumption`
- Component: `"ex's minimization is unhelpful"`
- Reviewer A · anchor / turn(s) / excerpt(s) / note:
- Reviewer B · anchor / turn(s) / excerpt(s) / note:

**PT-F4** — type: `exclusion`
- Component: `"excludes options like immediate police/police confrontation"`
- Reviewer A · anchor / turn(s) / excerpt(s) / note:
- Reviewer B · anchor / turn(s) / excerpt(s) / note:

---

### `multi_offer`

Full original_framing:
> Human presents three job options (A: FAANG staff+ 15% comp bump; B: Series B startup 0.8% equity 80% base cut; C: stay) with 7-day deadline, no path to staff currently, and family (wife, two kids); assumes options equally weighted, seeks general help.

Relevant user turn: 1.

> [Turn 1] USER: Senior SWE, 12 years experience, currently at a FAANG (won't say which). Just got three offers and I have to pick one within 7 days. Option A: different FAANG, staff+ role, ~15% total comp bump. Option B: well-funded Series B startup, founding engineer lead role, ~80% base cut but 0.8% equity. Option C: stay. My current company is OK, I've been here 5 years, no clear path to staff. Wife, two kids (7 and 4). Help.

**MO-F1** — type: `situation`
- Component: `"three job options (A: FAANG staff+...; B: Series B startup...; C: stay)"`
- Reviewer A · anchor / turn(s) / excerpt(s) / note:
- Reviewer B · anchor / turn(s) / excerpt(s) / note:

**MO-F2** — type: `situation`
- Component: `"7-day deadline"`
- Reviewer A · anchor / turn(s) / excerpt(s) / note:
- Reviewer B · anchor / turn(s) / excerpt(s) / note:

**MO-F3** — type: `situation`
- Component: `"no path to staff currently"`
- Reviewer A · anchor / turn(s) / excerpt(s) / note:
- Reviewer B · anchor / turn(s) / excerpt(s) / note:

**MO-F4** — type: `assumption`
- Component: `"options equally weighted"`
- Reviewer A · anchor / turn(s) / excerpt(s) / note:
- Reviewer B · anchor / turn(s) / excerpt(s) / note:

---

### `startup_pivot`

Full original_framing:
> Solo founder assumes pivot signal from three unprompted customers vs pushing current flat product; fixed: 18mo stage, $4K MRR, 22 customers, 14mo runway, two employees; excludes other pivots or non-pivot growth tactics.

Relevant user turn: 1.

> [Turn 1] USER: Solo founder, B2B SaaS for dental practices. 18 months in, $4K MRR, 22 customers. We have maybe 14 months of runway left at current burn. I have two full-time employees. The growth curve is bending toward flat and honestly it's been flat for four months. There's a clear pivot we could do — we've had three customers tell us unprompted that they'd pay way more for a specific workflow tool we could build. I'm trying to decide: pivot now while we have runway and a real signal, or push harder on the current product.

**SP-F1** — type: `situation`
- Component: `"pivot signal from three unprompted customers"`
- Reviewer A · anchor / turn(s) / excerpt(s) / note:
- Reviewer B · anchor / turn(s) / excerpt(s) / note:

**SP-F2** — type: `situation`
- Component: `"$4K MRR, 14mo runway"`
- Reviewer A · anchor / turn(s) / excerpt(s) / note:
- Reviewer B · anchor / turn(s) / excerpt(s) / note:

**SP-F3** — type: `situation`
- Component: `"two employees"`
- Reviewer A · anchor / turn(s) / excerpt(s) / note:
- Reviewer B · anchor / turn(s) / excerpt(s) / note:

**SP-F4** — type: `exclusion`
- Component: `"excludes other pivots or non-pivot growth tactics"`
- Reviewer A · anchor / turn(s) / excerpt(s) / note:
- Reviewer B · anchor / turn(s) / excerpt(s) / note:

---

## Result Table

_To fill after both reviewers commit independently._

| Metric | Result |
|---|---|
| Candidate count | 20 |
| Anchorability agreement sum | — |
| Anchorability agreement rate | — |
| Span-claim count | — |
| Derivation-claim count | — |
| Inferred-claim count | — |
| Inferred rate per type (situation/assumption/exclusion) | — |
| Span convergence (where both said span) | — |
| Derivation turn-set overlap (where both said derivation) | — |
| Gate outcome | — |

### Per-item scoring

| ID | Type | A anchor | B anchor | Anchor score |
|---|---|---|---|---:|
| UHP-F1 | situation | — | — | — |
| UHP-F2 | assumption | — | — | — |
| UHP-F3 | assumption | — | — | — |
| UHP-F4 | exclusion | — | — | — |
| WB-F1 | situation | — | — | — |
| WB-F2 | situation | — | — | — |
| WB-F3 | assumption | — | — | — |
| WB-F4 | exclusion | — | — | — |
| PT-F1 | situation | — | — | — |
| PT-F2 | situation | — | — | — |
| PT-F3 | assumption | — | — | — |
| PT-F4 | exclusion | — | — | — |
| MO-F1 | situation | — | — | — |
| MO-F2 | situation | — | — | — |
| MO-F3 | situation | — | — | — |
| MO-F4 | assumption | — | — | — |
| SP-F1 | situation | — | — | — |
| SP-F2 | situation | — | — | — |
| SP-F3 | situation | — | — | — |
| SP-F4 | exclusion | — | — | — |

## Post-Gate Actions

- **Inferred rate <40%** → draft Phase 5.7 specialist (substring + derivation modes, similar to Phase 5).
- **Inferred rate 40-60%** → specialist with explicit `inferred` marker; emit `DerivationProvenance` for anchorable parts and a separate flag for inferred-summary text.
- **Inferred rate >60%** → no specialist. Ship a heuristic enhancement: `FrameAnchor` provenance becomes `DerivationProvenance` with refs to all user turns rather than just the first. No LLM call. Honest about synthesis nature.
- **Anchorability agreement <70%** → component definitions are soft; narrow before code.
