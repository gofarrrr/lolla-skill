# Pre-Step 6 Kimi Structural-Delta Calibration Readout

Date: 2026-05-21

Slice: `calibration_corpus_kimi_structural_delta_v0`

Runtime policy: `runtime_dormant`

Promotion effect: `none_calibration_only`

## Question

After the `structural_delta` vocabulary repair and targeted rerun, the next
gate was the full calibration corpus under one pinned Step 6 model:

```text
moonshotai/kimi-k2.6
```

The calibration question was:

```text
Does the repaired Step 6 prompt produce stable enough private-ledger signals to
justify reviewer adjudication, without reintroducing reframe-only unlocks or
false-positive pressure?
```

This readout measures the production-condition bundle:

```text
Kimi + repaired prompt + five-field answer_delta vocabulary
```

It does not isolate the vocabulary repair from model-family effects.

## Method

Artifacts:

- `research/pre-step6-calibration-corpus-kimi-structural-delta/calibration-corpus.v1.json`
- `research/pre-step6-calibration-corpus-kimi-structural-delta/step6-samples/*.json`
- `research/pre-step6-calibration-corpus-kimi-structural-delta/calibration-step6-result.v1.json`
- `research/pre-step6-calibration-corpus-kimi-structural-delta/calibration-stability-review.v1.json`

The corpus contains 17 pre-registered cases and meets the required floor:

```text
high_clutter: 5 observed / 3 required
sequencing_or_problem_shape: 6 observed / 3 required
sensitive_safety_legal: 7 observed / 3 required
negative_control: 7 observed / 3 required
v60_on_off_pairs: 2 observed / 2 required
floor_status = corpus_floor_met
```

The run produced:

```text
51 planned Step 6 samples
12 same-prompt repeat samples on variable cases
63 total saved samples
0 incomplete samples remaining
```

No reviewer calls were run in this slice.

No runtime behavior changed.

`SKILL.md` remained untouched.

## Runner Hardening

The live calibration run exposed two research-runner issues and both were fixed
in the research tooling:

- resumable `--skip-existing` sampling, so a malformed or timed-out response
  does not force the whole corpus to restart;
- an outer per-sample timeout plus exception normalization, so `urllib`
  `IncompleteRead` failures become calibration errors handled by the retry path.

The runner also now clears stale `calibration-live-errors.txt` files after a
later resume succeeds.

This is tooling hygiene only. It does not affect runtime.

## Aggregate Result

Final aggregate after repeat sampling:

```text
case_count = 17
sample_count = 63
stable_case_count = 13
unstable_case_count = 4
incomplete_case_count = 0
unlock_sample_count = 33
reframe_only_sample_count = 0
structural_delta_sample_count = 0
structural_delta_field_sample_count = 38
calibration_read = stability_review_required_before_reviewer_phase
```

Stability review:

```text
stable_positive_count = 6
stable_standdown_count = 7
borderline_unlock_count = 1
unstable_mixed_count = 3
abstract_additive_only_count = 0
incomplete_sampling_count = 0
reviewer_phase_decision = blocked_for_full_calibration_repeat_or_partition_first
```

## Stable Positive Cases

These cases produced additive pressure with concrete answer deltas in every
sample:

```text
bridge-high-clutter-sensitive-overlay        3/3 unlock
bridge-sensitive-anchor-misses-tripwire      3/3 unlock
bridge-sequencing-sensitive-boundary         3/3 unlock
founder-grant-marcus-equity.v60-off          3/3 unlock
multi-offer-new-run2                         3/3 unlock
startup-pivot-new-run2                       3/3 unlock
```

Interpretation:

The original bridge wins survived the repaired prompt. The answer-delta
specificity gate did not over-suppress the cases that originally motivated the
visibility redesign.

## Stable Stand-Down Cases

These cases kept deck pressure private or confirming in every sample:

```text
fp-bevelin-irrelevant-incentives             3/3 stand-down
fp-marker-preserved-entity-lost              3/3 stand-down
fp-polya-true-but-useless                    3/3 stand-down
marker-entity-attempt-1-resource-generalization 3/3 stand-down
marker-entity-attempt-2-tripwire-compression 3/3 stand-down
marker-entity-attempt-3-actor-sequence-blur  3/3 stand-down
mother-address-year                          3/3 stand-down
```

Interpretation:

The repaired vocabulary did not turn generic Bevelin/Polya pressure into
visible output. This is important: broader Step 6 reporting language did not
automatically make the system more permissive.

## Variable Cases

Four cases remained variable after same-prompt repeat sampling:

| Case | Samples | Unlock Read | Interpretation |
| --- | ---: | --- | --- |
| `founder-grant-marcus-equity.high-clutter.v60-on` | 6 | 4/6 unlock | V60-on founder remains real but unstable. |
| `mid-level-consultant-report-2` | 6 | 3/6 unlock | Consultant remains a case-type ambiguity; Step 6 flips between visible deck value and private confirmation. |
| `third-year-phd-student.v2.v60-off` | 6 | 3/6 unlock | Without V60, PhD sequencing pressure is unstable. |
| `third-year-phd-student.v2.v60-on` | 6 | 5/6 unlock | V60-on PhD is strongly positive but still not perfectly stable. |

Interpretation:

The remaining problem is not `reframed_emphasis` leakage. It is Step 6's own
private-ledger variance: in the same case shape, same prompt, same model, Step
6 sometimes records concrete additive pressure and sometimes records the deck
as private/confirming.

That is a cognition-stability issue, not a deterministic-gate issue.

## Answer-Delta Read

The repaired prompt eliminated the earlier reframe-only trap in this corpus:

```text
reframe_only_sample_count = 0
```

Step 6 used `structural_delta` frequently:

```text
structural_delta_field_sample_count = 38 / 63
```

But no live sample required pure structural-only unlock:

```text
structural_delta_sample_count = 0
```

Interpretation:

The `structural_delta` field is useful as custody evidence, but the live Kimi
samples that unlocked still named concrete payload. The pure
`structural_delta_present` path remains implemented and tested, but
`not_observed` in live calibration.

## Decision

Do not move to shadow implementation yet.

Do not change `SKILL.md`.

Do not add another answer-delta vocabulary field.

Do not add a deterministic selector to force these four variable cases into a
single visible policy.

The stable partition is real and should be preserved:

```text
13 / 17 cases stable
6 stable-positive candidates
7 stable-standdown candidates
```

The global policy is not yet stable enough for promotion because:

```text
4 / 17 cases remain variable
```

## Recommendation

Use a partitioned reviewer phase next:

1. Run reviewer adjudication only on the 13 stable cases.
2. Keep the four variable cases quarantined from promotion.
3. Treat reviewer results as evidence for the stable partition, not for global
   runtime promotion.
4. For the four variable cases, open design review on Step 6 ledger stability:
   reduce sampling variance, improve Step 6 ledger self-reporting, or require a
   narrower dormant pilot that defaults variable cases to deck-private.

This preserves the core philosophy:

```text
broad private context
Step 6 cognition
deterministic custody
no early castration
no public bloat without accountable evidence
```

The system got smarter here. It learned that the repaired vocabulary solves the
reframe-only problem, while exposing a more precise next bottleneck: stable
case partitioning versus variable Step 6 ledger behavior.
