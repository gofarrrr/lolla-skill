# SK3 Explicit-Schema Repair — Three-Case Result

Date: 2026-07-10  
Cases: 02, 08, and 11  
Repeats: three per case  
Decision: **retain as the offline experimental base; proceed to bounded SK4;
do not run the full corpus or graph yet**

## Why these cases

Cases 02, 08, and 11 were selected before the repair because the frozen SK3
reader showed different diagnostic failures across them:

- multi-option question and stance instability;
- career/family current-question instability;
- a precommitted user plan with unusually high prior repeatability but low
  gold recall.

Sources, gold observations, compact artifacts, scoring, model, temperature,
and three-repeat contract remained frozen.

## Aggregate result

| Measure | Frozen SK3 | Explicit-schema repair | Change |
| --- | ---: | ---: | ---: |
| Weighted exact-span recall | 0.413 | 0.547 | +0.134 |
| Macro exact-span recall | 0.417 | 0.546 | +0.129 |
| Stable observations | 8 / 25 | 13 / 25 | +5 |
| Never recovered | 11 / 25 | 10 / 25 | -1 |
| Macro span repeatability | 0.450 | 0.628 | +0.178 |
| Macro labeled repeatability | 0.410 | 0.577 | +0.167 |
| Lowest case recall | 0.333 | 0.500 | +0.167 |

The authoritative subset artifacts are:

- `three-case-comparison.json` and `three-case-comparison.md`;
- `three-case-frozen-sk3-comparison.json` and
  `three-case-frozen-sk3-comparison.md`.

## Per-case result

| Case | Frozen recall | Repair recall | Frozen span J | Repair span J |
| --- | ---: | ---: | ---: | ---: |
| 02 — multi-offer career | 0.375 | 0.583 | 0.335 | 0.453 |
| 08 — oncologist career/family | 0.542 | 0.500 | 0.460 | 0.693 |
| 11 — consulting launch plan | 0.333 | 0.556 | 0.554 | 0.738 |

Case 08 lost a small amount of strict recall while becoming much more
repeatable. Cases 02 and 11 improved materially on both usefulness signals.
The repair is not uniformly better on every measure or case.

## Semantic-dimension result

| Dimension | Frozen recall | Repair recall | Stable frozen | Stable repair |
| --- | ---: | ---: | ---: | ---: |
| Assistant positions and revisions | 0.667 | 0.600 | 3 | 3 |
| Constraints and options | 0.667 | 0.800 | 3 | 4 |
| Dropped or under-carried threads | 0.000 | 0.000 | 0 | 0 |
| Operative questions | 0.500 | 0.889 | 2 | 5 |
| Uncertainty and evidence boundaries | 0.111 | 0.333 | 0 | 1 |
| User corrections and pressure | 0.111 | 0.111 | 0 | 0 |

The question repair clearly generalizes. User pressure and dropped-thread
treatment do not improve enough to justify a full-corpus promotion.

## Repeatability by event family

Macro repeatability across the three cases improved in every family:

| Family | Frozen span J | Repair span J | Frozen label J | Repair label J |
| --- | ---: | ---: | ---: | ---: |
| Assistant stances | 0.481 | 0.496 | 0.408 | 0.436 |
| Questions | 0.704 | 0.736 | 0.704 | 0.723 |
| Live constraints | 0.499 | 0.720 | 0.393 | 0.606 |
| User pressure | 0.220 | 0.403 | 0.220 | 0.367 |
| Options | 0.531 | 0.770 | 0.531 | 0.770 |
| Evidence boundaries | 0.268 | 0.493 | 0.244 | 0.357 |
| Dropped threads | 0.444 | 0.778 | 0.370 | 0.778 |

Repeatable dropped-thread output with zero gold recovery is particularly
important: stability is not correctness, and the standalone dropped-thread
classifier is still selecting the wrong semantic object.

## Source-first interpretation

### Questions

The focused question reader recovered 0.889 of required question spans and
made five of six stable. Cases 08 and 11 selected the same current question in
all repeats. Case 02 remained genuinely difficult: one run treated the latest
seven-day-feasibility question as current, while two retained the earlier
due-diligence question. Both are real user questions.

This does not justify a deterministic latest-question rule or an immediate
sixth selection call. The three-case result shows that the existing focused
reader generalizes overall; Case 02's current-stage disagreement should remain
visible as uncertainty.

### Stances

Stance repeatability improved slightly in aggregate, while strict gold recall
fell from 0.667 to 0.600. Source-first review explains part of the mismatch:

- the reader often selected a shorter commitment such as `Take the role.`
  rather than the gold's longer recommendation bundle;
- in Case 11 it repeatedly selected the later operational four-week delay
  condition rather than the earlier gold sentence saying a six-week launch was
  viable;
- Case 02 still missed the final conditional choice while preserving the
  financial reframe and several surrounding conditions.

These are not all equivalent semantic readings, but the strict decline cannot
be read as simple quality loss. Gold completeness and exact-span granularity
remain evaluation limitations.

Across 58 validated stance events, 8 prior-candidate links resolved and 50
were explicitly null. The contract is now observable; it has not demonstrated
rich stance-link coverage.

### Pressure, evidence, and dropped threads

User-pressure gold recovery remains 0.111 with no stable observation. Evidence
boundaries improve but remain weak at 0.333. These are the correct targets for
SK4.

Dropped-thread recovery remains zero. More prompt rules should not be added to
the binary classifier. SK5's planned topic-and-treatment representation remains
the appropriate repair.

## Custody and operational result

- Successful final artifacts: 9.
- Successful calls inside final artifacts: 45.
- Final-artifact token proxy: 218,992.
- Preserved failed attempts: 1.
- Calls including the preserved Case 02 attempt: 49.
- Tokens including that attempt: 235,736.
- Candidate disposition explicitly declared: 0 of 277 proposals; this is now
  recorded as unobserved rather than treated as a complete hypothesis search.
- Candidate custody: complete in all final artifacts.
- Credential, provider-message, and prompt-text leakage: none observed.

Across all exploratory Case 02 repair rounds plus the final Cases 08 and 11,
83 calls and 416,360 recorded tokens were used. Historical failed preflights
remain archived and are excluded from the comparison.

## Decision

The five-reader, explicit-schema shadow path becomes the offline experimental
base for the next semantic-kernel work. This is a research promotion, not a
live-path, graph, or quality-proof promotion.

Do not spend on the remaining nine corpus cases yet. The three-case result is
already sufficient to show that the known SK4 and SK5 families would block the
v0.1 promotion thresholds.

Next:

1. SK4 should give user pressure one focused semantic job rather than adding
   deterministic gates or more instructions to the three-array
   decision-context prompt.
2. Keep options and evidence together for the first bounded ablation; split
   them only if evidence remains weak while option quality holds.
3. Test the SK4 change on the same diagnostic subset before any full corpus
   rerun.
4. Then implement SK5 topic-and-treatment semantics for dropped threads.
5. Run the full locked corpus only after the SK4 and SK5 readers are frozen.

Graph integration, live routing, parallel execution, and Step 6 changes remain
out of scope.

## SK4 local implementation update

The first next step above is now implemented locally. User pressure has a
focused one-array reader; options and evidence remain in a narrowed two-array
reader. Exact duplicate events are preserved in the candidate ledger with a
structural duplicate state, while one selected identity enters the current
view. Same-span/different-role pressure interpretations remain distinct.

The six-reader implementation passes 3,864 non-network tests with one
pre-existing skip. It has not made a paid call. The proposed diagnostic rerun
is 54 successful calls across the same three cases, plus bounded retries.
