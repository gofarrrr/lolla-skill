# Case 08 Paid Counter-Pressure Preflight Result

Date: 2026-07-10  
Case: `case-08-oncologist-career-family`  
Contract: three repeats, one focused reader call per repeat  
Decision: **fail the locked one-case gate; do not run the three-case v2 ablation**

## Formal gate result

| gate | result |
| --- | --- |
| locked pressure-span recall | fail: 0 / 3 repeats |
| stable locked pressure observation | fail: 0 / 1 |
| exact-source validity | pass: 11 / 11 candidates |
| one semantic reader call per artifact | pass: 3 / 3 artifacts |
| no old catch-all kinds returned | pass |

The required quote was:

> `we haven't had the real conversation about what 3 nights a week away actually looks like for four-plus years`

The v2 reader did not return that turn-2 span in any repeat. Under the frozen
contract, the preflight therefore fails regardless of the other improvements.

## What the reader returned

The three runs selected four, three, and four events. All 11 events were
source-valid and all were labeled `material_qualification`.

Three themes were recovered in all three runs, with some exact-span variation:

- Chicago travel becomes difficult under the three-night schedule;
- the specific patient handoff changes the departure constraint;
- the non-compete invalidates the proposed industry bridge.

Two runs also recovered the later husband-alignment qualification:

> `But he said it in the way that means "I will not stop you from taking it." Which is different from "yes this is a good idea for us."`

That later statement expresses a closely related and arguably stronger form of
the locked observation, but it was not declared as gold evidence before the
run. It receives no recall credit and must not be added retroactively to make
the experiment pass.

## What changed relative to the failed SK4 reader

The first SK4 reader filled all eight slots with concerns in every Case 08
repeat: 24 selections in total. The v2 reader returned 11 narrower
qualifications in total and did not use the cap. This means the original
generic-concern crowding problem was materially reduced.

The remaining failure is different. The v2 reader favored later statements
that visibly changed developed reasoning and under-carried the earlier point
where the husband-alignment issue first entered the conversation. The issue is
now temporal coverage and evaluation representation, not broad catch-all
selection or exact-source custody.

## Interpretation

The result supports four bounded conclusions:

1. The narrower semantic target reduced noise.
2. Deterministic source and schema custody worked exactly as intended.
3. The reader still does not preserve the first introduction of an important
   counter-pressure thread reliably.
4. The locked exact-span gold set is too narrow to distinguish total conceptual
   omission from recovery through a later, stronger source span.

Conclusion 4 does not invalidate the formal failure. It identifies a second
measurement that should be designed prospectively: predeclared alternative
source spans for the same observation, kept separate from strict first-
introduction recall.

## Operational custody

- Successful paid calls: 3.
- Retry calls: 0.
- Successful artifacts: 3.
- Prompt tokens: 13,300.
- Completion tokens: 806.
- Total recorded tokens: 14,106.
- Provider statuses: 3 `ok`.
- Served model: `google/gemini-3.1-flash-lite-20260507`.
- Temperature: 0.2.
- Graph, lane, Step 6, receipt, archive, and live runtime changes: none.

## Next bounded step

Do not run Cases 02 and 11 yet. Perform a no-cost source-first review with two
separate targets:

1. **First-introduction coverage:** did the reader preserve where a material
   counter-pressure thread first entered the conversation?
2. **Concept coverage:** did it preserve the same material issue through any
   source-valid span predeclared before the next run?

Do not use an LLM judge, embeddings, or post-run semantic matching in the
scorer. If alternative spans are accepted, they must be researcher-reviewed,
stored in the gold fixture before another call, and scored deterministically.

If first-introduction coverage remains a product requirement, the next prompt
revision should explicitly ask the LLM to preserve both the first introduction
of a counter-pressure thread and a later strengthening only when the later
statement materially changes it. That remains an LLM semantic job; Python
should validate the declared source relationships without deciding the thread.

The approved no-cost follow-up is complete. Its diagnostic rescore is in
`temporal-concept-review-result.md`. V2 recovered the concept through the later
husband-alignment span in 2/3 runs but recovered the first introduction in 0/3.
This confirms partial reasoning-substrate improvement without audit-trail or
stability readiness. The original failed decision is unchanged.
