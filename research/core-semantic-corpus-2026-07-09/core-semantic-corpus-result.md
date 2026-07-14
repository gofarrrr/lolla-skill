# Core Semantic Corpus — Result and Development Decision

Date: 2026-07-09  
Corpus: `core-semantic-corpus-v0`  
Cases: 12  
Repeats: three compact and three shadow runs per case  
Graph runtime changed: no

## Decision

The shared source-grounded semantic-kernel direction is confirmed as the
correct development path. It is **not ready for graph integration**.

The rich shadow path recovered more gold observations than the compact path in
all 12 cases and was more repeatable in 11 of 12. This generalizes the Case 01
finding beyond one business example. However, only 49 of 102 gold observations
were recovered in every shadow repeat, 41 were never recovered, and the lowest
case recall was 0.208. Feeding this representation into the graph now would
make graph behavior depend on incomplete and unstable semantic selection.

The immediate next development slice is semantic-kernel v0.1, followed by an
unchanged rerun of this fixed corpus. Graph ablations remain downstream.

## What this experiment gives us

It answers five questions that Case 01 could not answer alone.

1. **The architecture generalizes.** The richer path wins exact-span recall on
   every domain: business, career, family, ethics, money, research, and a short
   governance exchange.
2. **Compact extraction is not a process representation.** It achieved 0.065
   weighted exact-span recall and stably recovered only 6 of 102 observations.
   Its useful paraphrases do not preserve question changes, user pressure,
   options, uncertainty, or dropped threads as inspectable source events.
3. **The shadow design is materially useful but incomplete.** It achieved
   0.542 weighted recall and 49 stable observations. It is a credible research
   prototype, not a production semantic contract.
4. **The failure modes are now localized.** Questions and constraints are the
   strongest families. Dropped-thread status, evidence boundaries, user
   pressure, option/threshold completeness, and stance trajectories are the
   main blockers.
5. **We now have a reusable test asset.** The fixed source hashes, gold spans,
   repeated outputs, failure artifact, usage metadata, and deterministic
   aggregation let future changes be compared without changing the target.

## Corpus result

The authoritative deterministic comparison is in `corpus-comparison.json` and
`corpus-comparison.md`.

| Measure | Compact | Shadow |
| --- | ---: | ---: |
| Macro exact-span recall | 0.076 | 0.528 |
| Weighted exact-span recall | 0.065 | 0.542 |
| Stable observations | 6 / 102 | 49 / 102 |
| Never recovered | 94 / 102 | 41 / 102 |
| Macro span repeatability | 0.376 | 0.642 |
| Macro labeled repeatability | 0.376 | 0.628 |
| Lowest case recall | 0.000 | 0.208 |

Shadow recall ranged from 0.208 on the multi-offer career case to 0.778 on
Case 01. One strong case therefore overstated general readiness.

## Recovery by semantic job

| Semantic dimension | Shadow weighted recall | Stable / gold | Interpretation |
| --- | ---: | ---: | --- |
| Operative questions | 0.697 | 13 / 22 | Strongest family, but “latest operative” selection is still inconsistent. |
| Constraints and options | 0.614 | 11 / 19 | Promising; exact provenance for derivations is incomplete. |
| Assistant positions and revisions | 0.545 | 12 / 22 | Spans recur more reliably than relation labels or full trajectory coverage. |
| User corrections and pressure | 0.479 | 7 / 16 | Later counter-pressure is frequently missed or assigned only as a constraint. |
| Uncertainty and evidence boundaries | 0.472 | 4 / 12 | Low repeatability and high invalid-source rejection. |
| Dropped or under-carried threads | 0.273 | 2 / 11 | The current standalone dropped-thread classifier is not dependable. |

Question events had the best mean family span repeatability (0.824). Evidence
boundaries had the worst (0.384). Dropped-thread outputs were often internally
repeatable while recovering the wrong thread relative to gold; repeatability
therefore cannot substitute for coverage.

## Important measurement correction

The corpus audit exposed a comparator defect: derivation-mode constraints were
being represented by their synthesized label when no single source span
existed. The comparator now gives exact-span credit only to literal spans.
Turn-only derivation references remain visible as provenance but do not receive
span-grounding credit.

This also identifies a product defect: validated derivation excerpts are not
currently serialized into the final event; only their turn references survive.
Semantic-kernel v0.1 must preserve every exact component excerpt or offsets.

## Operational cost and reliability

The compact path used 261,801 recorded tokens across 33 usage-tracked runs;
the three older Case 01 compact runs did not retain usage metadata. The shadow
path used 631,439 tokens across all 36 runs and made 144 successful calls.

On tracked runs, the shadow path averaged about 17,540 tokens versus 7,933 for
compact, or 2.21 times as many. This is acceptable for the present research
phase but creates a clear consolidation target.

One compact provider response returned an empty extraction object on the
friendship-money case. The failed artifact is preserved and the bounded retry
succeeded. All 144 shadow calls completed with provider status `ok`. Provider
billing amounts are not persisted, so token use is a cost proxy rather than a
dollar claim.

## Field-contract reassessment

All 46 Case 01 field decisions were reconsidered. None is reversed:

- 17 keep;
- 17 merge;
- 10 defer;
- 2 remove.

The corpus supports the structure—especially two projections, typed events,
source refs, and separation of pre-audit semantics from post-audit review—but
does not promote every field to implementation-ready status. The detailed
reassessment is in `field-decisions-corpus-reassessment.json`.

The main strengthening is that `source_refs` must contain exact component
evidence for derivations. Post-audit accountability, privacy, review, and
release fields were not tested by this pre-audit corpus; their decisions remain
policy/timing boundaries rather than empirical quality findings.

## Semantic-kernel v0.1 development slice

The governing architecture is now explicit in
`docs/conversation-understanding/hybrid-reasoning-boundary-v0.md`, and the full
implementation sequence is in
`plans/lolla-semantic-kernel-v0.1-plan-2026-07-10.md`.

The corrected plan does not use deterministic rules to choose the current
question, assign stance relations, or decide whether a topic was under-carried.
Those are LLM/human semantic judgments. Deterministic code will preserve and
validate evidence, retain competing interpretations, check structural
consistency, and make disagreement measurable.

The work sequence is:

1. repair exact multi-turn derivation provenance;
2. add an append-oriented semantic candidate ledger with explicit rejection
   and ambiguity states;
3. improve LLM question and stance trajectory reading;
4. improve LLM pressure, option/condition, and evidence-boundary reading;
5. replace binary dropped-thread output with LLM-interpreted topic treatment;
6. rerun the unchanged corpus and decide whether pattern experiments are
   authorized.

No case-specific prompt patches or deterministic semantic approximations may
be added. The same reader must improve the fixed corpus as a whole.

## Gate before graph work

The following gate is locked before the v0.1 rerun:

- weighted exact-span recall at least 0.75;
- every semantic dimension at least 0.60;
- every case at least 0.60;
- macro span and labeled repeatability at least 0.75;
- every derivation preserves exact component provenance;
- no unvalidated source span can enter the routing projection;
- fact-leak lint and same-reasoning/different-facts invariance checks pass.

The current reader fails this gate. Therefore the reasoning-pattern packet
remains a design artifact, and no graph input, graph edge, routing rule, or
live runtime behavior is changed in this phase.
