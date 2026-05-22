# Pre-Step 6 Reframe Diagnostic Review Readout

Date: 2026-05-21

Slice: `calibration_reframe_diagnostic_review_v0`

Runtime policy: `runtime_dormant`

Promotion effect: `none_research_only`

## Question

The repeat-unstable calibration pass showed a persistent pattern:

Step 6 often sees additive value in high-clutter or V60-adjacent cases, but it
sometimes records that value only as `reframed_emphasis`, not as
`added_entities`, `removed_entities`, or `reordered_sequences`.

The narrow diagnostic question was:

```text
Are reframe-only Step 6 outputs genuinely useful enough to challenge the
answer-delta vocabulary, or are they correctly suppressed?
```

This diagnostic used saved Step 6 samples only.

No new Step 6 calls were made.

No runtime behavior changed.

`SKILL.md` remained untouched.

## Method

Artifacts:

- `research/pre-step6-reframe-diagnostic-review/reframe-diagnostic-contract.v1.json`
- `research/pre-step6-reframe-diagnostic-review/judgments/*.json`
- `research/pre-step6-reframe-diagnostic-review/reframe-diagnostic-result.v1.json`

The diagnostic selected 10 saved samples:

- 3 stable controls;
- 7 reframe-only diagnostics from the same-prompt repeat pass.

Each sample was reviewed by two model families:

- `openai/gpt-5.1-chat`
- `google/gemini-3.1-flash-lite`

Reviewers compared the saved Step 6 visible answer against the anchor answer
under blind shuffle. The reviewer task was not "is this prompt contract valid?"
It was only:

```text
Is the saved Step 6 answer better, non-inferior, worse, ambiguous, or
not-observed for the user's actual decision?
```

The deterministic layer only preserved custody:

- blind map;
- reviewer labels;
- winner arms;
- label/winner-arm consistency;
- confirmed label.

## Aggregate Result

```text
case_count = 10
control_case_count = 3
reframe_case_count = 7
confirmed_reframe_useful_count = 2
confirmed_reframe_correctly_suppressed_count = 0
ambiguous_count = 6
tension_count = 5
diagnostic_read = answer_delta_vocabulary_design_review_required
recommended_next_action = review_answer_delta_vocabulary_for_structural_framing_delta
```

## Case Results

| Case | Role | Confirmed Label | Consistency | Reviewer Labels | Winner Arms |
| --- | --- | --- | --- | --- | --- |
| `bridge-sensitive-anchor-misses-tripwire.sample-0` | control positive | `control_step6_supported` | aligned | step6_better, step6_better | step6, step6 |
| `mother-address-year.sample-0` | control stand-down | `control_step6_supported` | aligned | step6_non_inferior, step6_non_inferior | tie, tie |
| `multi-offer-new-run2.sample-0` | control positive | `ambiguous` | tension | step6_non_inferior, anchor_better | tie, step6 |
| `founder...v60-off.sample-0` | reframe-only | `ambiguous` | aligned | ambiguous, step6_non_inferior | step6, step6 |
| `founder...v60-off.sample-1` | reframe-only | `ambiguous` | tension | anchor_better, step6_non_inferior | step6, anchor |
| `founder...v60-on.sample-0` | reframe-only | `reframe_useful` | aligned | step6_non_inferior, step6_non_inferior | step6, anchor |
| `founder...v60-on.sample-2` | reframe-only | `ambiguous` | tension | anchor_better, step6_non_inferior | step6, step6 |
| `startup-pivot.sample-1` | reframe-only | `ambiguous` | tension | anchor_better, anchor_better | step6, step6 |
| `startup-pivot.sample-2` | reframe-only | `ambiguous` | tension | step6_non_inferior, anchor_better | anchor, step6 |
| `phd.v60-off.sample-2` | reframe-only | `reframe_useful` | aligned | step6_non_inferior, step6_non_inferior | tie, anchor |

## What Held

The controls were useful.

The clear positive bridge control was confirmed: both reviewers preferred the
saved Step 6 answer because it preserved concrete tripwires.

The mother stand-down control was also fine: both reviewers saw the Step 6
answer as non-inferior/tied, which is consistent with the earlier finding that
this case should not force visible deck expansion.

The diagnostic did not show generic overpromotion. Reframe-only did not become
a license to show everything.

## What Broke Or Got Sharper

The current answer-delta vocabulary is too narrow for at least some cases.

Two reframe-only samples were confirmed `reframe_useful`:

- `founder-grant-marcus-equity.high-clutter.v60-on.sample-0`
- `third-year-phd-student.v2.v60-off.sample-2`

In both, reviewers did not say the Step 6 answer was necessarily the clear
winner. They said it was non-inferior. That matters because the runtime
visibility question is not "does the deck always beat the anchor?" It is:

```text
Would suppressing this Step 6 output solely because its delta is reframe-only
hide a useful/non-inferior answer?
```

For at least two samples, yes.

The strongest signal is not "show reframe-only outputs." That would be too
loose.

The stronger signal is:

```text
Some structural improvements are real, but our answer_delta vocabulary has no
place to record them except reframed_emphasis.
```

Examples reviewers treated as useful:

- shifting a founder equity decision away from instrument-catalog thinking and
  toward explicit unlock conditions;
- treating a PhD decision as a short verification process with stop-date logic.

Those are not merely "tone" changes. They are structural reasoning changes.
But they are also not simple entity additions.

## Reviewer Tension

Five records had label/winner-arm tension.

That means this diagnostic is not a runtime promotion signal.

The tension itself is useful. It shows reviewers find high-clutter strategic
framing hard to classify with the current label set. That should make us more
careful, not more eager.

The deterministic layer did the right thing: it did not smooth over those
records. It kept them visible as ambiguous/tension.

## Decision

Do not loosen the answer-delta guardrail in runtime.

Do not add a new deterministic selector.

Do not run full reviewer calibration yet.

Do run an answer-delta vocabulary design review.

The design review should add a way for Step 6 to record concrete structural
reasoning changes without pretending they are added entities. A candidate field
is:

```json
"structural_delta": [
  "Decision boundary, test design, stop condition, sequencing frame, or 
   commitment-shape change that affects the visible answer."
]
```

This would keep the principle intact:

- Step 6 remains the cognitive actor.
- Code does not decide whether a structural delta is wise.
- Code only checks whether Step 6 recorded a specific kind of visible-answer
  change.
- Broad private context remains available.
- Public visibility remains accountable.

## Recommendation

Run `answer_delta_structural_delta_design_v0` next.

Scope:

- research-only;
- no runtime promotion;
- no `SKILL.md` edit;
- update the Step 6 answer-delta vocabulary in research prompts only;
- add tests proving generic `reframed_emphasis` still does not unlock;
- add tests proving a non-empty `structural_delta` can be recorded separately
  from entities and sequences;
- rerun only the persistent reframe-only samples before any broader
  calibration phase.

This is a vocabulary repair, not a gate expansion.

Runtime promotion remains blocked.
