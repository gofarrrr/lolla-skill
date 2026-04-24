# Phase 0.5 Drill-Back Spike

**Date:** 2026-04-24
**Case:** `user_has_plan`
**Lane:** Lane 3 / Frame Pressure
**Status:** produced for PM review; Phase 1 implementation remains gated.

## Purpose

This spike proves one narrow thing before Phase 1 starts: a Lane 3 output can
walk back to a prototype IR object, then to an exact source span, then to the
original user turn text.

This is a research artifact, not production IR code. It intentionally does not
create `engine/system_b/ir.py`, `ir_builders.py`, or `ir_constructor.py`.
Phase 1 formalizes the shapes shown here.

## Source Artifacts

- Conversation: `research/test-cases/case_user_has_plan_conversation.txt`
- Extraction: `research/test-cases/phase2a-lane3-equivalence-2026-04-23/_scratch/user_has_plan_extraction.json`
- Lane 3 run: `research/test-cases/phase2a-lane3-equivalence-2026-04-23/_scratch/user_has_plan_new_run1.json`

No fresh pipeline run was performed. The spike uses existing local artifacts to
avoid API cost and live-model variability.

## Prototype Provenance Rules

Phase 1 should preserve three provenance tiers instead of pretending every
derived object has exact substring support:

| Tier | Meaning | Required shape |
|---|---|---|
| `span` | exact substring in a single turn | `SpanRef(turn_index, speaker, start_char, end_char)` |
| `turn_ref` | source turn is known, but object text is paraphrased | one or more `(turn_index, speaker)` refs |
| `derivation` | inferred from multiple turns or derived objects | lineage refs to turns and/or IR objects |

`SpanRef` offsets are turn-relative and end-exclusive. The current capture file
uses the same `turn_index` for user and assistant messages in a pair, so this
spike treats `(turn_index, speaker)` as the stable turn reference.

## Prototype IR Subset

### SpanRefs

These exact spans were found in user turns:

| id | source | start | end | text |
|---|---|---:|---:|---|
| `span_frame_pipeline` | Turn 2 / user | 0 | 164 | `Pipeline — I've had informal conversations with 4-5 former colleagues and people in my network who've said things like "if you were independent, we'd consider you."` |
| `span_frame_runway` | Turn 2 / user | 217 | 348 | `Runway — 8 months assumes zero revenue. I figured if I can't get my first engagement in 8 months, something is fundamentally wrong.` |
| `span_frame_timing` | Turn 1 / user | 199 | 245 | `Plan is to go independent starting in 6 weeks.` |
| `span_user_commitment` | Turn 1 / user | 0 | 20 | `I've decided to quit` |

### FrameAnchors

Lane 3 frame elements become `FrameAnchor` objects, not `UserIssueEvent`s.

| id | from Lane 3 | frame_pattern | provenance |
|---|---|---|---|
| `frame_anchor_001` | `frame_elements[0]` | `borrowed_premise` | `span_frame_pipeline` |
| `frame_anchor_002` | `frame_elements[1]` | `temporal_fixation` | `span_frame_runway` |
| `frame_anchor_003` | `frame_elements[2]` | `temporal_fixation` | `span_frame_timing` |

### UserIssueEvents

Current extraction fields are mostly paraphrased summaries, so they should not
masquerade as exact spans. They get `turn_ref` provenance in this spike.

| id | kind | status | text | provenance |
|---|---|---|---|---|
| `issue_001` | `constraint` | `active` | Pipeline: 4-5 informal network conversations, no signed commitments | `turn_ref`: Turn 2 / user |
| `issue_002` | `constraint` | `active` | Runway: 8 months at zero revenue | `turn_ref`: Turn 2 / user |
| `issue_003` | `constraint` | `active` | Launch timeline: 6 weeks from now, aligned with Q3 planning end | `turn_ref`: Turn 1 / user and Turn 2 / user |
| `issue_004` | `constraint` | `active` | Spouse support: on board with concept, not specifics of financial pressure | `turn_ref`: Turn 5 / user |
| `issue_005` | `open_loop` | `acknowledged_then_dropped` | Tactical launch plan details | `turn_ref`: Turn 1 / user and Turn 3 / user |

Kind mapping used here:

- `live_constraints` -> `kind="constraint"`
- `dropped_threads` with `status="acknowledged_then_dropped"` or
  `superseded_by` set -> `kind="open_loop"`
- frame elements remain `FrameAnchor`

### StanceEvents

`StanceEvent` carries `speaker` in the prototype. Phase 3 can deepen the
assistant-side trajectory later; Phase 1 only needs the primitive.

| id | speaker | stance | provenance |
|---|---|---|---|
| `stance_001` | `user` | `commitment` | `span_user_commitment` |

## Drill-Back Demonstration

### Chain 1: Lane 3 Reframing 0

**Lane 3 output:**

```text
reframings[0].reframed_question =
"What evidence from my 4-5 informal network conversations points to a realistic 20%+ conversion rate to signed B2B fintech engagements??"
```

**Existing anchor:**

```text
reframings[0].source_element_index = 0
```

**Walk:**

1. `reframings[0].source_element_index = 0`
2. `frame_elements[0]`
3. prototype IR object: `frame_anchor_001`
4. `frame_anchor_001.source_span = span_frame_pipeline`
5. `span_frame_pipeline = SpanRef(turn_index=2, speaker="user", start_char=0, end_char=164)`
6. source substring:

```text
Pipeline — I've had informal conversations with 4-5 former colleagues and people in my network who've said things like "if you were independent, we'd consider you."
```

**Result:** Lane 3 finding -> IR object -> source span -> raw turn text works
in six explicit steps today. Phase 1 can reduce the public API walk to three
logical hops by formalizing `source_ref`.

### Chain 2: Lane 3 Reframing 1

**Lane 3 output:**

```text
reframings[1].reframed_question =
"If my first paid engagement takes 3-5 months as typical for first-time independents, how does my 8-month runway change the risk profile??"
```

**Existing anchor:**

```text
reframings[1].source_element_index = 1
```

**Walk:**

1. `reframings[1].source_element_index = 1`
2. `frame_elements[1]`
3. prototype IR object: `frame_anchor_002`
4. `frame_anchor_002.source_span = span_frame_runway`
5. `span_frame_runway = SpanRef(turn_index=2, speaker="user", start_char=217, end_char=348)`
6. source substring:

```text
Runway — 8 months assumes zero revenue. I figured if I can't get my first engagement in 8 months, something is fundamentally wrong.
```

### Chain 3: Unused Frame Element

Lane 3 produced three frame elements but only two reframings because the card
budget is two. The third frame element still drills back cleanly:

1. `frame_elements[2]`
2. prototype IR object: `frame_anchor_003`
3. `frame_anchor_003.source_span = span_frame_timing`
4. `span_frame_timing = SpanRef(turn_index=1, speaker="user", start_char=199, end_char=245)`
5. source substring:

```text
Plan is to go independent starting in 6 weeks.
```

## Acceptance Check

| Requirement | Result |
|---|---|
| Uses one existing corpus case | PASS: `user_has_plan` |
| Uses one lane | PASS: Lane 3 / Frame Pressure |
| Uses existing artifacts, no fresh API run | PASS |
| Demonstrates at least one finding -> IR object -> SpanRef -> raw turn chain | PASS: Chain 1 |
| Demonstrates exact turn-relative character offsets | PASS |
| Marks paraphrased extraction fields as non-span provenance | PASS |
| Avoids production IR implementation | PASS |

## Phase 1 Implications

Phase 1 tasking should formalize:

- `SpanRef(turn_index, speaker, start_char, end_char)` with turn-relative,
  end-exclusive offsets.
- A provenance union with at least `span`, `turn_ref`, and `derivation`.
- `FrameAnchor` as the IR home for Lane 3 frame elements.
- `UserIssueEvent.kind` mapping from extraction fields, with
  `dropped_threads.status` determining `concern` vs `open_loop`.
- `StanceEvent.speaker`, so user commitments and assistant trajectory events
  share one primitive without conflating speaker roles.
- A drill-back resolver that can walk from a packet-local source reference to
  the source turn text.

## Non-Goals Confirmed

- No production builder was created.
- No lane behavior changed.
- No API call was made.
- No raw-file offsets were used.
- No paraphrased extraction summary was promoted to an exact span.

Phase 0.5 can close after PM review of this artifact and the Phase 1 task file.
