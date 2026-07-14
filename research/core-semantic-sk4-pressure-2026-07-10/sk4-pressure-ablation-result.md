# SK4 Focused User-Pressure Ablation Result

Date: 2026-07-10  
Cases: 02, 08, and 11  
Repeats: three per case  
Model: `google/gemini-3.1-flash-lite` through OpenRouter  
Decision: **fail the SK4 promotion gate; retain the five-reader SK3 repair as the offline base**

## What changed

The ablation added one focused probabilistic reader for user pressure and left
options plus evidence boundaries in a narrowed companion reader. Constraint,
stance, dropped-thread, and question readers were unchanged. Deterministic
code continued to validate schema, allowed kinds, source turns, exact quotes,
caps, and event identity; it did not assign semantic roles.

The comparison reused the nine existing compact artifacts. It created nine new
shadow artifacts, with six successful calls per artifact. No graph, lane,
Step 6, receipt, archive, or live runtime behavior changed.

## Locked gate result

| gate | SK3 base | SK4 ablation | result |
| --- | ---: | ---: | --- |
| user corrections and pressure weighted recall | 0.111 | 0.111 | fail: no improvement |
| stable gold pressure observations | 0 / 3 | 0 / 3 | fail |
| accepted pressure candidates with exact-source validation | n/a | 61 / 61 | pass |
| constraints and options weighted recall | 0.800 | 0.733 | regression |
| uncertainty and evidence-boundary weighted recall | 0.333 | 0.000 | material regression |
| option span repeatability | 0.770 | 0.624 | regression |
| evidence-boundary span repeatability | 0.493 | 0.370 | regression |

The ablation therefore fails three parts of the four-part promotion gate. The
six-reader topology is not promoted.

## Broader comparison

| measure | SK3 base | SK4 ablation |
| --- | ---: | ---: |
| weighted exact-span recall | 0.547 | 0.493 |
| macro exact-span recall | 0.546 | 0.491 |
| stable observations | 13 / 25 | 11 / 25 |
| never recovered | 10 / 25 | 10 / 25 |
| lowest case recall | 0.500 | 0.375 |
| macro span repeatability | 0.628 | 0.628 |
| macro labeled repeatability | 0.577 | 0.575 |

Pressure-family repeatability itself improved: mean span Jaccard rose from
0.403 to 0.578 and labeled Jaccard from 0.367 to 0.558. That improvement did
not recover more of the pressure evidence required by the locked gold set.
This is a repeatable-reading improvement, not a semantic-coverage improvement.

The reader's 61 accepted events comprised 39 concerns, 13 corrections, six
evidence requests, and three timing-pressure events. Concerns therefore used
64% of the selection capacity. No event was labeled as a value.

## What the source shows

### Case 02 — multi-offer career

The required correction was `This isn't my decision alone.` The focused reader
recovered it in only one repeat, as part of a much larger compound span about
the user's wife, income, relocation, working hours, and joint decision. The
other repeats selected nearby spouse and marriage concerns but not the required
correction. This remained one recovery in three rather than becoming stable.

### Case 08 — oncologist career and family

The required qualification was `we haven't had the real conversation about
what 3 nights a week away actually looks like for four-plus years`. The reader
returned the same eight exact, plausible concerns in all three repeats, but
never selected this qualification. The eight-item cap was fully occupied by
other concerns. This is the clearest sign that the current target is too broad:
the reader can be perfectly repeatable while consistently prioritizing the
wrong material.

### Case 11 — consulting launch plan

The required qualification was `None of them have committed to actual
engagements.` The reader never selected it. It instead selected later
corrections, concerns, and evidence requests. The missed statement can
reasonably look like an evidence boundary as well as counter-pressure. The
current prompt tells the pressure reader not to extract evidence boundaries,
while the gold contract expects this statement in the pressure dimension.
That semantic boundary is not yet clean enough.

## Interpretation

The experiment does not show that a focused reader is useless. It shows that
the phrase `user pressure` currently combines too many different jobs:
corrections, qualifications, concerns, evidence requests, timing pressure, and
values. On a rich conversation, generic concerns consume the selection budget
before the narrower reasoning corrections and qualifications that the product
cares about.

It also shows that splitting work can stabilize the model without making the
output more useful. Deterministic validation correctly guaranteed exact source
custody, but it could not and should not decide which valid concern mattered.
That semantic prioritization remains probabilistic work and needs a clearer
product definition.

The option/evidence regression is a second reason not to promote. The first
SK4 ablation changed both the pressure reader and the option/evidence prompt.
The result cannot isolate whether those regressions came from prompt wording,
the changed job allocation, or normal model variance. A future pressure test
should keep the SK3 decision-context call byte-for-byte unchanged and ignore
its pressure output for comparison, so the only semantic variable is the new
focused pressure reader.

## Operational custody

- Successful shadow artifacts: 9.
- Successful calls represented in those artifacts: 54.
- One bounded retry occurred after the assistant-stance call omitted its
  required top-level key.
- Calls recorded across the successful run and preserved failed attempt: 56.
- Tokens recorded for successful artifacts: 253,157.
- Additional tokens recorded in the failed attempt: 5,349; the invalid-output
  response reported zero usage, so its token use is not known from the receipt.
- All 54 calls in successful artifacts report status `ok`.
- Served model version: `google/gemini-3.1-flash-lite-20260507`.
- Provider billing amounts are not persisted, so token totals remain the cost
  proxy.

## Unknowns and limits

- Three gold pressure observations are enough to reject this ablation, but not
  enough to define the complete pressure taxonomy.
- Exact-span recall tests recovery of locked source evidence; it does not prove
  total semantic correctness or usefulness.
- The eight-item cap exposed prioritization pressure, but this test does not
  show whether a higher cap would improve useful coverage or merely add noise.
- Some product-important statements genuinely cross pressure, constraint, and
  evidence-boundary roles. The representation needs an explicit rule for
  preserving such overlap without deterministic semantic guessing.
- This result concerns offline conversation understanding only. It makes no
  claim about mental-model graph selection or final reconsideration quality.

## Next bounded step

Do not run the remaining corpus and do not add another reader. First perform a
source-first target review:

1. Define the product-relevant target as user statements that materially
   correct, qualify, challenge, or impose a decision-relevant condition on the
   reasoning—not every concern or value in the conversation.
2. Review the three locked gold observations and the 61 accepted pressure
   candidates against that definition. Preserve cross-family roles when the
   probabilistic reader explicitly assigns them; do not infer them in Python.
3. Decide whether `concern` and `value` belong in this focused reader or in the
   broader audit trail only.
4. For the next test, restore the SK3 decision-context prompt unchanged for
   option/evidence output so that pressure is the only experimental variable.
5. Run a one-case prompt preflight before another three-case paid ablation.

This review should refine the meaning of the semantic job, not add gates,
agents, graph rules, or architecture.
