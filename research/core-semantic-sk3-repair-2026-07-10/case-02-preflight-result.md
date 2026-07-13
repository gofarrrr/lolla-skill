# SK3 Repair — Case 02 Preflight Result

Date: 2026-07-10  
Case: `case-02-multi-offer-career`  
Decision: **repair v1 failed; explicit-schema v2 is partial; Cases 08 and 11
not run**

## Why the experiment stopped

The bounded repair required stance stability to improve without losing
operative-question coverage before continuing beyond Case 02. That gate did
not pass.

The dedicated question reader produced a strong local signal: question span
and label repeatability rose from 0.444 to 1.000, and the later due-diligence
question became stable across all three repeats.

The stance reader moved in the opposite direction. Stance span repeatability
fell from 0.458 to 0.222 and labeled repeatability fell from 0.348 to 0.143.
One repeat assigned all six stance quotes to incorrect source turns, so exact
validation correctly excluded all six. None of the ten validated stance events
declared the new prior-event index.

Continuing to Cases 08 and 11 would therefore have spent more money without
satisfying the experiment's first promotion condition.

## Comparison with the frozen SK3 Case 02 result

| Measure | Frozen SK3 | Repair preflight | Change |
| --- | ---: | ---: | ---: |
| Exact-span recall | 0.375 | 0.208 | -0.167 |
| Mean span repeatability | 0.335 | 0.464 | +0.129 |
| Mean labeled repeatability | 0.320 | 0.444 | +0.125 |
| Question span repeatability | 0.444 | 1.000 | +0.556 |
| Question label repeatability | 0.444 | 1.000 | +0.556 |
| Stance span repeatability | 0.458 | 0.222 | -0.236 |
| Stance label repeatability | 0.348 | 0.143 | -0.205 |

The higher overall repeatability should not be mistaken for a pass. It was
concentrated in questions and constraints, while gold recall and the targeted
stance family worsened.

## Two deterministic defects exposed

The first paid preflight produced all five transport-success calls per repeat,
but one stance response omitted `stance_events` and one decision-context
response omitted all three required arrays. The parser returned empty objects,
which the initial harness accepted as semantically empty responses. Those
artifacts are preserved under
`case-02-multi-offer-career/preflight-invalid-output-contract/` and excluded
from this result.

The harness was then repaired to require every reader's top-level keys. On the
valid rerun it caught and preserved one further missing-key question response,
then retried only that shadow artifact. The resulting error receipt is
`shadow-02-attempt-01.error.json`.

This is an important distinction:

- an existing required array that is empty may be a semantic result;
- a missing required array is a mechanical output-contract failure.

The second defect was prompt-schema incompleteness. In two valid
decision-context responses, option and evidence objects contained their
quotes and turns but omitted `speaker`, causing every item in those families
to fail deterministic source validation. The prompt described the field in
prose but did not show the complete item schema. The stance-link field was
similarly absent.

## Local repair after stopping paid calls

No further paid call was made. The local prompts now include:

- complete object-shape illustrations for every focused reader;
- explicit required `speaker` keys for option and evidence events;
- an explicit nullable `related_stance_event_index` on every stance object;
- a rule forbidding `...` or other shortening inside exact evidence quotes;
- structural observability that distinguishes an explicit null stance link
  from a missing stance-link field.

These are general contract improvements. No Case 02 phrase, label, or gold
annotation was added to a runtime prompt.

## Cost and custody

- Paid calls submitted and recorded: 34.
- Recorded token proxy: 180,624.
- Invalid first preflight: 15 calls / 82,603 tokens.
- Valid rerun plus one preserved failed attempt: 19 calls / 98,021 tokens.
- Cases 08 and 11: no new calls.
- Provider-message text, prompt text, and credentials were not persisted.

## Decision

The focused-question decomposition is promising enough to preserve as an
experimental branch. The combined repair is not promoted. Before any further
paid run, the founder should explicitly approve one more Case 02-only test of
the now-complete object schemas. Cases 08 and 11 remain downstream of that
gate.

## Explicit-schema v2 result

The founder approved the final Case 02-only test. The repair-v1 artifacts and
their failure receipt were moved to
`case-02-multi-offer-career/preflight-v1-incomplete-item-schema/`, and three
fresh five-reader repeats were run with the explicit object schemas.

The schema change materially improved the result:

| Measure | Frozen SK3 | Repair v1 | Explicit-schema v2 |
| --- | ---: | ---: | ---: |
| Exact-span recall | 0.375 | 0.208 | 0.583 |
| Mean span repeatability | 0.335 | 0.464 | 0.453 |
| Mean labeled repeatability | 0.320 | 0.444 | 0.411 |
| Question span repeatability | 0.444 | 1.000 | 0.208 |
| Stance span repeatability | 0.458 | 0.222 | 0.602 |
| Stance label repeatability | 0.348 | 0.143 | 0.496 |
| Option span repeatability | 0.733 | 0.333 | 1.000 |

Mechanical adherence improved decisively:

- all 23 validated stance events used exact quotes and correct turns;
- all option and evidence candidates included `speaker`;
- all stance candidates included the new link field;
- 22 stance links were explicitly null and 1 revision link resolved to an
  earlier stance candidate;
- no stance, option, or evidence candidate was rejected for source or shape;
- one missing-key question response was preserved and automatically retried;
- candidate custody remained complete.

Gold recovery also broadened. Four of eight observations became stable:

- spouse-as-primary-earner constraint;
- uncertainty about whether the spouse's yes is genuine;
- current due-diligence question span;
- financial-decision reframe stance.

Only the expected-value dropped thread and final conditional-choice stance
were never recovered. The initial three-offer question became variable rather
than never recovered.

## Why v2 is still partial

Question-family repeatability fell because the focused reader returned
different sets of real intermediate user questions: 8, 5, and 4 validated
events. This was not fabrication. Source-first review found legitimate stages
such as renegotiation, re-examining Option A, spouse conversation scripting,
due diligence, and whether the work fits inside the deadline.

The semantic designation of the current question remained unstable:

- one repeat selected `Realistic — all of this in 7 days?`;
- two selected the earlier due-diligence question;
- the due-diligence span itself was recovered in every repeat, sometimes as an
  intermediate question rather than current.

The comparator gives recall credit for the span regardless of its current
stage, so stable gold recovery does not prove stable operative-question
assignment. The explicit schema solved evidence and field adherence; it did
not solve the remaining semantic selection problem.

Question references also remained weak: only 3 of 17 resolved, while 11
pointed to source questions that were not emitted as candidates in the same
run. This is the same candidate/link mismatch previously observed for stances.

## Updated cost

The explicit-schema v2 run used 19 recorded calls and 100,970 tokens: 15 calls
in the three successful artifacts plus four completed calls in one preserved
missing-key attempt.

Across all Case 02 repair rounds:

- calls: 53;
- recorded token proxy: 281,594;
- Cases 08 and 11: no new calls.

## Updated decision

Explicit item schemas are retained. They improved exact evidence adherence,
stance stability, option stability, and gold recall without adding
deterministic semantic rules.

Cases 08 and 11 remain paused because the predeclared no-cross-family-
regression condition is not cleanly satisfied: operative-question spans were
not lost, but question-family and current-stage stability worsened.

The next design question is whether to separate question candidate extraction
from question-trajectory interpretation. That would follow the focused-context
principle but add a sixth, serial semantic call. It should be discussed as a
cost/complexity trade-off before implementation or further paid evaluation.
