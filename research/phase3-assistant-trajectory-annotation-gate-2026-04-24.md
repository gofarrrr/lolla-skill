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
- Reviewer A include / relation / note:
- Reviewer B include / relation / note:

**UHP-S2**
- Speaker: `assistant`
- Source: turn 3
- Candidate span: `the tactical advice — pricing, positioning, website, legal structure — only matters if the fundamentals are solid.`
- Reviewer A include / relation / note:
- Reviewer B include / relation / note:

**UHP-S3**
- Speaker: `assistant`
- Source: turn 7
- Candidate span: `Launching in 6 weeks is viable if you do three things in those 6 weeks: (1) have the full runway conversation with your spouse, (2) go back to your network with the specific fractional ask and see if 1-2 convert, (3) prepare for months 1-3 as business development, not delivery.`
- Reviewer A include / relation / note:
- Reviewer B include / relation / note:

**UHP-S4**
- Speaker: `assistant`
- Source: turn 7
- Candidate span: `If after 4 weeks you have zero fractional commitments and your spouse is not aligned on the 5-months-of-revenue-pressure reality, push back by 2-3 months.`
- Reviewer A include / relation / note:
- Reviewer B include / relation / note:

### `whistleblower`

**WB-S1**
- Speaker: `assistant`
- Source: turn 1
- Candidate span: `I cannot give you legal advice, and this is a situation where you need a lawyer within days, not weeks. The first concrete action I'd recommend is retaining a whistleblower attorney — typically free consultations, often working on contingency — before you do anything else.`
- Reviewer A include / relation / note:
- Reviewer B include / relation / note:

**WB-S2**
- Speaker: `assistant`
- Source: turn 4
- Candidate span: `My honest read: your most protected path is probably a whistleblower attorney who files on your behalf with the regulator, anonymously to the firm.`
- Reviewer A include / relation / note:
- Reviewer B include / relation / note:

**WB-S3**
- Speaker: `assistant`
- Source: turn 6
- Candidate span: `At 60-65% confidence in internal handling, with a senior partner involved, external-with-counsel is the defensible path.`
- Reviewer A include / relation / note:
- Reviewer B include / relation / note:

**WB-S4**
- Speaker: `assistant`
- Source: turn 8
- Candidate span: `Within 7-14 days: with attorney, make the filing. Between now and then, say nothing to colleagues. Behave normally. Do not do any of your own investigation. Do not access files, systems, or communications related to the client beyond what you'd normally do for your work.`
- Reviewer A include / relation / note:
- Reviewer B include / relation / note:

### `parenting_teen`

**PT-S1**
- Speaker: `assistant`
- Source: turn 2
- Candidate span: `The first move here isn't to push on the 19-year-old. It's to create a way for her to re-enter the relationship without losing all face.`
- Reviewer A include / relation / note:
- Reviewer B include / relation / note:

**PT-S2**
- Speaker: `assistant`
- Source: turn 3
- Candidate span: `The guy: you don't call the police today. You call the National Sexual Assault Hotline (RAINN — 800.656.HOPE) this afternoon and describe what you saw.`
- Reviewer A include / relation / note:
- Reviewer B include / relation / note:

**PT-S3**
- Speaker: `assistant`
- Source: turn 7
- Candidate span: `My honest read: if your goal is protecting her, not reporting and getting her to a specialized therapist is probably the better path given your co-parenting situation.`
- Reviewer A include / relation / note:
- Reviewer B include / relation / note:

**PT-S4**
- Speaker: `assistant`
- Source: turn 11
- Candidate span: `This week: DON'T report to police (decision made, stop re-litigating it); DON'T call Mia's mom; DON'T block the 19-year-old yet; DON'T take the phone away.`
- Reviewer A include / relation / note:
- Reviewer B include / relation / note:

### `multi_offer`

**MO-S1**
- Speaker: `assistant`
- Source: turn 4
- Candidate span: `It's not actually a financial decision, or not primarily. The reason B keeps pulling you is that it solves a career-shape problem that A doesn't.`
- Reviewer A include / relation / note:
- Reviewer B include / relation / note:

**MO-S2**
- Speaker: `assistant`
- Source: turn 6
- Candidate span: `So it's not really "B is risky for the marriage so stay at C." It's more like: the distraction is going to be there regardless`
- Reviewer A include / relation / note:
- Reviewer B include / relation / note:

**MO-S3**
- Speaker: `assistant`
- Source: turn 9
- Candidate span: `So A answers a question you probably already know the answer to. B answers one you genuinely don't know. From an information-value standpoint, B is the more interesting move.`
- Reviewer A include / relation / note:
- Reviewer B include / relation / note:

**MO-S4**
- Speaker: `assistant`
- Source: turn 15
- Candidate span: `If the wife conversation goes well, take B. If it doesn't, take A but with clear eyes about what it is. Don't stay.`
- Reviewer A include / relation / note:
- Reviewer B include / relation / note:

### `startup_pivot`

**SP-S1**
- Speaker: `assistant`
- Source: turn 2
- Candidate span: `If two of three say yes, you have enough signal to pivot. If all three pass when money is actually involved, you have a feature idea, not a product.`
- Reviewer A include / relation / note:
- Reviewer B include / relation / note:

**SP-S2**
- Speaker: `assistant`
- Source: turn 4
- Candidate span: `My honest read: option three, then option one if the pivot confirms. She deserves to hear this before you've made the decision, not after.`
- Reviewer A include / relation / note:
- Reviewer B include / relation / note:

**SP-S3**
- Speaker: `assistant`
- Source: turn 6
- Candidate span: `Give yourself 14 days. After the pre-buy test and the three conversations, you make the call.`
- Reviewer A include / relation / note:
- Reviewer B include / relation / note:

**SP-S4**
- Speaker: `assistant`
- Source: turn 7
- Candidate span: `Those conversations are the bottleneck, not the strategic question.`
- Reviewer A include / relation / note:
- Reviewer B include / relation / note:

## Result Table

Fill after both reviewers annotate independently.

| Metric | Result |
|---|---|
| Candidate count | 20 |
| Detection agreement sum |  |
| Detection agreement rate |  |
| Relation-scored candidate count |  |
| Relation agreement sum |  |
| Relation agreement rate |  |
| Included or unsure candidates |  |
| Gate outcome |  |

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
