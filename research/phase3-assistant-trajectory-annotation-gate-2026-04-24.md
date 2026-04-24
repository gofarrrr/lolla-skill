# Phase 3.0 - Assistant Trajectory Annotation Gate

**Date:** 2026-04-24
**Purpose:** decide whether minimal assistant-side `StanceEvent` population is learnable and span-backed enough to implement Phase 3.
**Scope:** annotation/design gate only. No code, no branch, no implementation.

## Why This Gate Exists

Phase 1 created `StanceEvent` but correctly emitted zero events from the current
constructor. Current extraction's `synthesized_position` is a paraphrased final
summary, not an assistant trajectory. Phase 3 should populate `StanceEvent` only
if reviewers can reliably identify exact assistant spans and agree on the
minimal relation taxonomy.

This gate tests that before implementation.

## Object Under Test

Minimal candidate shape:

```python
StanceEvent(
    stance_id="...",
    speaker="assistant",
    stance="...",
    text="exact assistant span",
    provenance=SpanProvenance(span_ref=SpanRef(...)),
    turn_index=...
)
```

`speaker` is included explicitly even though this gate only annotates assistant
turns. The IR primitive supports both user and assistant stances; Phase 3 simply
tests whether assistant-side trajectory is ready to populate.

## What Counts As A StanceEvent

A candidate span should be marked `include=yes` only if it records a meaningful
position in the assistant's reasoning trajectory, not just ordinary explanation.

Include:

- a concrete recommendation or commitment
- a material qualification or boundary on earlier advice
- an if/then decision criterion
- a deferral, parking, or "not now" instruction
- a revision in how the assistant frames the user's decision

Exclude:

- generic empathy or reassurance
- background explanation with no position change
- examples that merely illustrate an already-recorded stance
- operational details that do not change the stance trajectory

## Relation Taxonomy

Reviewers classify included candidates with one relation. If genuinely
ambiguous, use two relations separated by `/`, for example
`commitment/condition`.

| Relation | Definition | Quick test |
|---|---|---|
| `initial` | First substantive stance on a decision axis. | Does this establish a position before later changes refine it? |
| `revision` | Material shift from an earlier stance or from the user's framing. | Does this change what the conversation is really deciding? |
| `qualification` | Caveat, boundary, or limiting condition on an existing stance. | Does it narrow or soften another stance? |
| `commitment` | Direct recommendation, directive, or firm conclusion. | Could the user act on this as advice? |
| `condition` | If/then gate, test, or criterion for deciding. | Does it define what evidence should trigger an action? |
| `deferral` | Explicitly parks an action, topic, or decision for later. | Does it say "not now" or "later under conditions"? |

If relation-level agreement is poor, narrow the taxonomy before any Phase 3
implementation. Do not argue a fine-grained taxonomy into existence.

## Protocol

1. Each reviewer works independently.
2. For every candidate, fill:
   - `include`: `yes`, `no`, or `unsure`
   - `relation`: one relation, or two separated by `/` if ambiguous
   - `note`: optional short reason
3. Do not revise after seeing the other reviewer's answers.
4. Score detection agreement and relation agreement separately.

## Scoring

Detection score:

- Full agreement (`yes/yes`, `no/no`, `unsure/unsure`): +1.0
- Partial agreement where one reviewer uses `unsure` and the other uses
  `yes` or `no`: +0.5
- Direct disagreement (`yes/no`): 0.0

Relation score:

- Score only candidates where both reviewers mark `include=yes` or where one
  marks `yes` and the other marks `unsure`.
- Same single relation: +1.0
- Ambiguous relation overlaps with the other reviewer, e.g.
  `commitment/condition` vs `condition`: +0.5
- No overlap: 0.0

Gate:

- Detection agreement >=80%.
- Relation agreement >=80%.
- At least 12 of 20 candidates should survive as `include=yes` or
  `include=unsure`; otherwise the candidate pool is too noisy.
- Every included event must be exact-span-backed in an assistant turn.

If detection passes but relation fails, Phase 3 may still proceed with a
narrower relation taxonomy. If exact spans are not stable, stop.

## Candidate Cases

Five cases are used because the 3-case Phase 2 feasibility pass proved too thin:

- `user_has_plan`
- `whistleblower`
- `parenting_teen`
- `multi_offer`
- `startup_pivot`

The candidate spans below are deliberately exact assistant text. They are not an
answer key; reviewers decide independently whether each span should become a
`StanceEvent` and which relation it has.

## Annotation Items

### `user_has_plan`

**UHP-S1**
- Speaker: `assistant`
- Source: turn 2
- Candidate span: `"if you were independent, we'd consider you" is almost exactly zero in actual conversion terms. It means they like you and they're being polite. The number of those conversations that convert to signed engagements in the first 3 months is typically less than 1 in 5, and often zero. You don't have a pipeline; you have a network that might become a pipeline.`
- Reviewer A include / relation / note: yes / revision / reframes pipeline claim vs. polite interest; not mere explanation
- Reviewer B include / relation / note: yes / revision / reframes user's "4-5 conversations = pipeline" premise

**UHP-S2**
- Speaker: `assistant`
- Source: turn 3
- Candidate span: `the tactical advice — pricing, positioning, website, legal structure — only matters if the fundamentals are solid.`
- Reviewer A include / relation / note: yes / qualification / when tactical advice is relevant
- Reviewer B include / relation / note: yes / qualification / boundary on when tactical advice applies

**UHP-S3**
- Speaker: `assistant`
- Source: turn 7
- Candidate span: `Launching in 6 weeks is viable if you do three things in those 6 weeks: (1) have the full runway conversation with your spouse, (2) go back to your network with the specific fractional ask and see if 1-2 convert, (3) prepare for months 1-3 as business development, not delivery.`
- Reviewer A include / relation / note: yes / condition / viability gated on three explicit prerequisites
- Reviewer B include / relation / note: yes / condition / "viable if X" — explicit if/then

**UHP-S4**
- Speaker: `assistant`
- Source: turn 7
- Candidate span: `If after 4 weeks you have zero fractional commitments and your spouse is not aligned on the 5-months-of-revenue-pressure reality, push back by 2-3 months.`
- Reviewer A include / relation / note: yes / condition / trigger conditions for schedule pushback
- Reviewer B include / relation / note: yes / condition / if/then gate for deferral trigger

### `whistleblower`

**WB-S1**
- Speaker: `assistant`
- Source: turn 1
- Candidate span: `I cannot give you legal advice, and this is a situation where you need a lawyer within days, not weeks. The first concrete action I'd recommend is retaining a whistleblower attorney — typically free consultations, often working on contingency — before you do anything else.`
- Reviewer A include / relation / note: yes / commitment / concrete retain-attorney directive; legal caveat secondary
- Reviewer B include / relation / note: yes / commitment / "first concrete action I'd recommend is retaining..." — directive; qualification embedded ("I cannot give legal advice") but dominant move is commitment

**WB-S2**
- Speaker: `assistant`
- Source: turn 4
- Candidate span: `My honest read: your most protected path is probably a whistleblower attorney who files on your behalf with the regulator, anonymously to the firm.`
- Reviewer A include / relation / note: yes / commitment / names preferred path
- Reviewer B include / relation / note: yes / commitment / "your most protected path is..." — direct recommendation

**WB-S3**
- Speaker: `assistant`
- Source: turn 6
- Candidate span: `At 60-65% confidence in internal handling, with a senior partner involved, external-with-counsel is the defensible path.`
- Reviewer A include / relation / note: yes / commitment / defensible path conclusion at stated confidence
- Reviewer B include / relation / note: yes / commitment / firm conclusion on path despite conditional framing

**WB-S4**
- Speaker: `assistant`
- Source: turn 8
- Candidate span: `Within 7-14 days: with attorney, make the filing. Between now and then, say nothing to colleagues. Behave normally. Do not do any of your own investigation. Do not access files, systems, or communications related to the client beyond what you'd normally do for your work.`
- Reviewer A include / relation / note: yes / commitment / time-bounded do/don't instructions
- Reviewer B include / relation / note: yes / commitment / imperative directive list

### `parenting_teen`

**PT-S1**
- Speaker: `assistant`
- Source: turn 2
- Candidate span: `The first move here isn't to push on the 19-year-old. It's to create a way for her to re-enter the relationship without losing all face.`
- Reviewer A include / relation / note: yes / revision / reframes first move (trust re-entry vs. pressuring teen)
- Reviewer B include / relation / note: yes / revision / redirects user's framing from "the guy" to trust repair

**PT-S2**
- Speaker: `assistant`
- Source: turn 3
- Candidate span: `The guy: you don't call the police today. You call the National Sexual Assault Hotline (RAINN — 800.656.HOPE) this afternoon and describe what you saw.`
- Reviewer A include / relation / note: yes / commitment/deferral / defer police now + immediate hotline directive; two stance moves
- Reviewer B include / relation / note: yes / commitment / concrete action directive (deferral component on "not today" but commitment dominant)

**PT-S3**
- Speaker: `assistant`
- Source: turn 7
- Candidate span: `My honest read: if your goal is protecting her, not reporting and getting her to a specialized therapist is probably the better path given your co-parenting situation.`
- Reviewer A include / relation / note: yes / commitment / ranked path given stated goal; goal clause is framing not full condition taxonomy
- Reviewer B include / relation / note: yes / commitment / recommendation conditional on user's goal (assumed shared)

**PT-S4**
- Speaker: `assistant`
- Source: turn 11
- Candidate span: `This week: DON'T report to police (decision made, stop re-litigating it); DON'T call Mia's mom; DON'T block the 19-year-old yet; DON'T take the phone away.`
- Reviewer A include / relation / note: yes / commitment / this-week prohibitions; closes debate
- Reviewer B include / relation / note: yes / commitment / firm directive list consolidating prior decisions ("decision made")

### `multi_offer`

**MO-S1**
- Speaker: `assistant`
- Source: turn 4
- Candidate span: `It's not actually a financial decision, or not primarily. The reason B keeps pulling you is that it solves a career-shape problem that A doesn't.`
- Reviewer A include / relation / note: yes / revision / reframes as career-shape vs. finance
- Reviewer B include / relation / note: yes / revision / reframes decision type (financial → career-shape)

**MO-S2**
- Speaker: `assistant`
- Source: turn 6
- Candidate span: `So it's not really "B is risky for the marriage so stay at C." It's more like: the distraction is going to be there regardless`
- Reviewer A include / relation / note: yes / revision / corrects "B risky for marriage → stay at C" framing
- Reviewer B include / relation / note: yes / revision / "not really X, it's more like Y" — reframe of user's mental model

**MO-S3**
- Speaker: `assistant`
- Source: turn 9
- Candidate span: `So A answers a question you probably already know the answer to. B answers one you genuinely don't know. From an information-value standpoint, B is the more interesting move.`
- Reviewer A include / relation / note: yes / revision / information-value lens; reframes how to rank A vs. B
- Reviewer B include / relation / note: yes / revision / information-value lens shift; borderline commitment but dominant move is reframe

**MO-S4**
- Speaker: `assistant`
- Source: turn 15
- Candidate span: `If the wife conversation goes well, take B. If it doesn't, take A but with clear eyes about what it is. Don't stay.`
- Reviewer A include / relation / note: yes / condition / wife-outcome if/then plus embedded exit directive
- Reviewer B include / relation / note: yes / condition / dual if/then gate; "don't stay" is embedded commitment

### `startup_pivot`

**SP-S1**
- Speaker: `assistant`
- Source: turn 2
- Candidate span: `If two of three say yes, you have enough signal to pivot. If all three pass when money is actually involved, you have a feature idea, not a product.`
- Reviewer A include / relation / note: yes / condition / threshold tests for pivot vs. feature-idea
- Reviewer B include / relation / note: yes / condition / decision criteria for pivot/no-pivot

**SP-S2**
- Speaker: `assistant`
- Source: turn 4
- Candidate span: `My honest read: option three, then option one if the pivot confirms. She deserves to hear this before you've made the decision, not after.`
- Reviewer A include / relation / note: yes / commitment / recommended sequence; pivot conditional branches option one
- Reviewer B include / relation / note: yes / commitment / primary recommendation with nested condition

**SP-S3**
- Speaker: `assistant`
- Source: turn 6
- Candidate span: `Give yourself 14 days. After the pre-buy test and the three conversations, you make the call.`
- Reviewer A include / relation / note: yes / deferral/condition / 14-day pause; call after pre-buy + convos
- Reviewer B include / relation / note: yes / deferral / time-bound parking of decision; condition component embedded

**SP-S4**
- Speaker: `assistant`
- Source: turn 7
- Candidate span: `Those conversations are the bottleneck, not the strategic question.`
- Reviewer A include / relation / note: yes / revision / reframes bottleneck to conversations; still a stance on priority
- Reviewer B include / relation / note: yes / revision / frame-shift on where effort should go; borderline brief

## Result Table

Both reviewers annotated independently; Reviewer B was committed first (commit `006e58f`) before Reviewer A (commit `b703a12`), preserving blind-first-reviewer protocol.

| Metric | Result |
|---|---|
| Candidate count | 20 |
| Detection agreement sum | 20.0 |
| Detection agreement rate | **100%** |
| Relation-scored candidate count | 20 (both reviewers included all 20) |
| Relation agreement sum | 19.0 |
| Relation agreement rate | **95.0%** |
| Included or unsure candidates | 20 of 20 |
| Gate outcome | **PASS** |

### Per-item relation scoring

| ID | Reviewer A | Reviewer B | Score |
|---|---|---|---:|
| UHP-S1 | revision | revision | 1.0 |
| UHP-S2 | qualification | qualification | 1.0 |
| UHP-S3 | condition | condition | 1.0 |
| UHP-S4 | condition | condition | 1.0 |
| WB-S1 | commitment | commitment | 1.0 |
| WB-S2 | commitment | commitment | 1.0 |
| WB-S3 | commitment | commitment | 1.0 |
| WB-S4 | commitment | commitment | 1.0 |
| PT-S1 | revision | revision | 1.0 |
| PT-S2 | commitment/deferral | commitment | 0.5 |
| PT-S3 | commitment | commitment | 1.0 |
| PT-S4 | commitment | commitment | 1.0 |
| MO-S1 | revision | revision | 1.0 |
| MO-S2 | revision | revision | 1.0 |
| MO-S3 | revision | revision | 1.0 |
| MO-S4 | condition | condition | 1.0 |
| SP-S1 | condition | condition | 1.0 |
| SP-S2 | commitment | commitment | 1.0 |
| SP-S3 | deferral/condition | deferral | 0.5 |
| SP-S4 | revision | revision | 1.0 |

### Observed ontology seam — composite stance moves

The two partial-disagreement items (PT-S2, SP-S3) share a structural pattern: **a stance span carries two of the six relations simultaneously**. One reviewer marked both; the other picked the dominant one.

- **PT-S2** (`"you don't call the police today. You call RAINN this afternoon"`): commitment (call RAINN) + deferral (not police today).
- **SP-S3** (`"Give yourself 14 days. After the pre-buy test and the three conversations, you make the call"`): deferral (14-day park) + condition (after specific tests).

This is the same class of finding as the `constraint/concern` seam in the Phase 1 annotation exercise — real ambiguity where an object carries two legitimate labels.

**Phase 3 implementation should mirror the Phase 1 `kind_ambiguity` pattern:** add `relation_ambiguity: bool = False` to `StanceEvent`. The primary `relation` field stays single (dominant reading); the flag is informational. The constructor sets it when a span carries two of the six relations.

### Observed distribution (Reviewer A ∪ Reviewer B)

- `commitment`: 7-8 (dominant for directive spans)
- `revision`: 6 (reframing moves)
- `condition`: 5-6 (if/then gates)
- `qualification`: 1 (boundary on earlier advice)
- `deferral`: 1-2 (explicit parking)
- `initial`: 0 (not observed in candidate pool)

Three observations:

1. **`initial` is unpopulated** across both reviewers. On reflection, candidates were selected to be stance-meaningful, and the first stance on a decision axis is often already a revision-from-user-framing, so `initial` as-defined is thin. Phase 3 implementation can either drop `initial` from the v1 taxonomy or keep it for future population (e.g., by lane-2/lane-3 packet builders that track first-stance-per-axis). **Leaning: keep `initial` reserved in the taxonomy but document it as expected-rare for the current candidate shape.**
2. **`commitment` is dominant.** Most assistant stance moves are firm recommendations. This confirms Phase 3's claim that assistant turns are span-friendly — the explicit "I recommend X" / "take Y" / "don't do Z" patterns produce clean verbatim anchors.
3. **`qualification` is rare** (1 of 20). Might merit re-examination — is "UHP-S2 (tactical advice only matters if fundamentals solid)" the only qualification, or should some items labeled `condition` instead be `qualification`? The definitional boundary between the two may need sharpening during implementation.

## Decision Rules

- If both detection and relation agreement pass: draft Phase 3 implementation
  task file for minimal `StanceEvent` population.
- If detection passes but relation agreement fails: collapse or rename relation
  taxonomy, then rerun the relation pass before implementation.
- If detection fails: do not implement Phase 3; write a blocking note and
  revisit whether assistant trajectory needs specialist extraction or a smaller
  object definition.
- If included spans are not exact substrings of assistant turns: stop. Phase 3
  must be exact-span-backed, not paraphrase-backed.
