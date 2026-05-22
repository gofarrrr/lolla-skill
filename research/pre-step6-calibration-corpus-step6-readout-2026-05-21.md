# Pre-Step 6 Calibration Corpus Step 6 Readout

Date: 2026-05-21

Slice: `calibration_corpus_step6_stability_v0`

Runtime policy: `runtime_dormant`

Promotion effect: `none_calibration_only`

## Question

The answer-delta guardrail survived both directed probes:

- it suppressed abstract additive claims in the false-positive direction;
- it preserved the original bridge wins in the false-standdown direction.

The next question was broader:

Can a pre-registered 12-20 case calibration corpus produce stable Step 6
private-ledger signals before reviewer adjudication?

This is a Step 6 stability phase only. It does not judge final answer quality.
It asks whether the cognitive actor is producing a stable enough private record
for reviewer calibration to be meaningful.

## Method

Artifact:

`research/pre-step6-calibration-corpus/calibration-corpus.v1.json`

The corpus contains 17 pre-registered cases:

- 5 high-clutter cases;
- 6 sequencing/problem-shape cases;
- 7 sensitive/safety/legal cases;
- 7 negative-control cases;
- 2 same-case V60 on/off pairs.

Each case was sampled 3 times with `openai/gpt-5.1-chat`, producing 51 live
Step 6 samples:

`research/pre-step6-calibration-corpus/step6-samples/*.json`

The prompt supplied broad private material:

- anchor visible candidate;
- deck pressure candidate;
- V60 private context where applicable;
- structured private visibility ledger;
- structured `answer_delta` fields.

The deterministic layer only derived:

- `ledger_signal`;
- `answer_delta_specificity`;
- whether a sample would be eligible for the answer-delta guarded policy.

No reviewer phase was run. No runtime behavior changed. `SKILL.md` was not
edited.

## Aggregate Result

Artifact:

`research/pre-step6-calibration-corpus/calibration-step6-result.v1.json`

```text
case_count = 17
sample_count = 51
stable_case_count = 10
unstable_case_count = 7
additive_samples = 21
private_or_confirming_samples = 30
concrete_delta_samples = 15
reframe_only_samples = 6
unlock_sample_count = 15
calibration_read = stability_review_required_before_reviewer_phase
```

The corpus floor is met. The stability floor is not.

## Case Results

| Case | Stability | Ledger Signal Counts | Answer-Delta Counts | Unlocks |
| --- | --- | --- | --- | --- |
| `bridge-high-clutter-sensitive-overlay` | unstable | additive 2, private/confirming 1 | concrete 2, n/a 1 | 2/3 |
| `bridge-sensitive-anchor-misses-tripwire` | stable | additive 3 | concrete 3 | 3/3 |
| `bridge-sequencing-sensitive-boundary` | stable | additive 3 | concrete 3 | 3/3 |
| `founder-grant-marcus-equity.high-clutter.v60-off` | unstable | additive 1, private/confirming 2 | reframe 1, n/a 2 | 0/3 |
| `founder-grant-marcus-equity.high-clutter.v60-on` | unstable | additive 2, private/confirming 1 | concrete 1, reframe 1, n/a 1 | 1/3 |
| `fp-bevelin-irrelevant-incentives` | stable | private/confirming 3 | n/a 3 | 0/3 |
| `fp-marker-preserved-entity-lost` | stable | private/confirming 3 | n/a 3 | 0/3 |
| `fp-polya-true-but-useless` | stable | private/confirming 3 | n/a 3 | 0/3 |
| `marker-entity-attempt-1-resource-generalization` | unstable | additive 1, private/confirming 2 | reframe 1, n/a 2 | 0/3 |
| `marker-entity-attempt-2-tripwire-compression` | stable | private/confirming 3 | n/a 3 | 0/3 |
| `marker-entity-attempt-3-actor-sequence-blur` | stable | private/confirming 3 | n/a 3 | 0/3 |
| `mid-level-consultant-report-2` | stable | private/confirming 3 | n/a 3 | 0/3 |
| `mother-address-year` | stable | private/confirming 3 | n/a 3 | 0/3 |
| `multi-offer-new-run2` | stable | additive 3 | concrete 3 | 3/3 |
| `startup-pivot-new-run2` | unstable | additive 2, private/confirming 1 | reframe 2, n/a 1 | 0/3 |
| `third-year-phd-student.v2.v60-off` | unstable | additive 2, private/confirming 1 | concrete 1, reframe 1, n/a 1 | 1/3 |
| `third-year-phd-student.v2.v60-on` | unstable | additive 2, private/confirming 1 | concrete 2, n/a 1 | 2/3 |

## What Held

The broad-private design still looks right.

Step 6 was not forced into deck use. Across 51 samples, it kept the deck private
or confirming in 30 samples and marked additive pressure in 21. Of those 21
additive samples, only 15 had concrete deltas strong enough to unlock the
answer-delta guarded policy.

The negative-control side is encouraging:

- `fp-bevelin-irrelevant-incentives` stood down 3/3;
- `fp-polya-true-but-useless` stood down 3/3;
- `fp-marker-preserved-entity-lost` stood down 3/3;
- `mother-address-year` stood down 3/3;
- `mid-level-consultant-report-2` stood down 3/3 under this prompt;
- two of three marker/entity construction attempts stood down 3/3.

The answer-delta guardrail also did useful mechanical work. Six samples had
`reframe_only` specificity. None became unlocks. Code did not decide whether
the reframing was wise; it only refused to treat abstract reframing as concrete
public payload.

Two original bridge wins remained fully stable:

- `bridge-sensitive-anchor-misses-tripwire` unlocked 3/3;
- `bridge-sequencing-sensitive-boundary` unlocked 3/3.

The new `multi-offer-new-run2` case also unlocked 3/3, which suggests the deck
can add stable concrete value outside the original bridge trio.

## What Did Not Hold

Seven cases were unstable across three samples.

The unstable set is not random. It clusters around high-clutter and borderline
V60/deck cases:

- high-clutter: 4 unstable cases out of 5;
- sequencing/problem-shape: 2 unstable cases out of 6;
- sensitive/safety/legal: 1 unstable case out of 7;
- negative controls: 1 unstable case out of 7.

The V60 on/off pairs are also unstable:

- founder V60 off: 0 unlocks, but 1 abstract additive claim;
- founder V60 on: 1 unlock, 1 abstract additive claim, 1 stand-down;
- PhD V60 off: 1 unlock, 1 abstract additive claim, 1 stand-down;
- PhD V60 on: 2 unlocks, 1 stand-down.

These V60 pairs are useful but still synthetic harness evidence, not production
V60 selected-item evidence.

The strongest interpretation is not "the gate failed." It is:

Step 6 can discriminate, but the current single-sample ledger signal is not yet
stable enough on borderline high-clutter/V60 cases to support reviewer-phase
calibration as if every case had one fixed truth.

## Interpretation

This result respects the original goal.

We did not narrow Step 6 too early. Step 6 received broad private material and
was allowed to use, combine, reject, or keep pressure private.

We also did not let deterministic code become the brain. Code did not decide
which answer was wiser. It only checked whether Step 6's private ledger had
enough concrete custody to justify a visibility upgrade.

What we learned is sharper:

- The system is not blindly over-promoting deck pressure.
- The answer-delta guardrail blocks abstract additive claims.
- Some positive cases produce stable concrete value.
- Some negative cases produce stable stand-down.
- Borderline high-clutter and V60 cases are noisy enough that a single Step 6
  ledger sample should not be treated as calibrated evidence yet.

That is real progress. The calibration run made the invisible uncertainty
visible.

## Recommendation

Do not run the reviewer phase yet.

Reviewer adjudication now would mix two questions that should stay separate:

1. Did Step 6 produce a stable visibility ledger?
2. Given a stable candidate, did reviewers agree that the deck-aware answer is
   better or non-inferior?

The first question is not resolved for 7 of 17 cases.

Next move:

Run a no-redesign stability review over the existing 51 samples. Classify cases
as:

- `stable_positive`: 3/3 unlock or 3/3 concrete additive;
- `stable_standdown`: 3/3 private/confirming;
- `borderline_unlock`: 2/3 unlock;
- `abstract_additive_only`: additive appears but never with concrete deltas;
- `unstable_mixed`: signal and specificity both vary.

Then decide, before any new model calls, whether the reviewer phase should run
only on stable cases while unstable cases remain calibration blockers, or
whether the seven unstable cases need a pre-registered repeat-sampling pass
under the same prompt.

Do not change `SKILL.md`.

Do not promote runtime visibility.

Do not add a new gate because of this result. The issue surfaced here is
calibration stability, not a missing deterministic cognition layer.
