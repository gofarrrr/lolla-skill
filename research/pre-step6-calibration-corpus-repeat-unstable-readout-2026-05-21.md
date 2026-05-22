# Pre-Step 6 Calibration Repeat-Unstable Readout

Date: 2026-05-21

Slice: `calibration_corpus_unstable_repeat_v0`

Runtime policy: `runtime_dormant`

Promotion effect: `none_calibration_only`

## Question

The first calibration corpus run met the corpus floor but not the Step 6
stability floor:

```text
17 cases
51 Step 6 samples
10 stable cases
7 unstable cases
```

Before running reviewer adjudication, the responsible next move was to repeat
only the unstable cases with the same prompt, same model, and no redesign.

The question:

Were the seven unstable cases one-pass noise, or do they remain unstable under
same-prompt repeat sampling?

## Method

Repeated cases:

- `bridge-high-clutter-sensitive-overlay`
- `founder-grant-marcus-equity.high-clutter.v60-off`
- `founder-grant-marcus-equity.high-clutter.v60-on`
- `marker-entity-attempt-1-resource-generalization`
- `startup-pivot-new-run2`
- `third-year-phd-student.v2.v60-off`
- `third-year-phd-student.v2.v60-on`

Artifacts:

- `research/pre-step6-calibration-corpus-repeat-unstable/step6-samples/*.json`
- `research/pre-step6-calibration-corpus-repeat-unstable/calibration-step6-result.v1.json`
- `research/pre-step6-calibration-corpus-repeat-unstable/calibration-stability-review.v1.json`

The repeat pass ran 21 additional live Step 6 samples with
`openai/gpt-5.1-chat`.

No reviewer calls were run.

No prompt redesign was introduced.

No runtime behavior changed.

`SKILL.md` remained untouched.

## Repeat Result

```text
case_count = 7
stable_positive_count = 1
stable_standdown_count = 1
borderline_unlock_count = 2
abstract_additive_only_count = 0
unstable_mixed_count = 3
reviewer_phase_decision = blocked_for_full_calibration_repeat_or_partition_first
```

## Original vs Repeat

| Case | Original Classification | Repeat Classification | Interpretation |
| --- | --- | --- | --- |
| `bridge-high-clutter-sensitive-overlay` | `borderline_unlock` | `borderline_unlock` | Persistent 2/3 unlock. The case keeps showing real value, but not stable enough for clean reviewer calibration. |
| `founder-grant-marcus-equity.high-clutter.v60-off` | `abstract_additive_only` | `unstable_mixed` | Step 6 now always saw additive pressure, but mostly as reframe-only rather than concrete payload. |
| `founder-grant-marcus-equity.high-clutter.v60-on` | `unstable_mixed` | `unstable_mixed` | Same pattern: additive pressure appears, but concrete answer-delta specificity is unstable. |
| `marker-entity-attempt-1-resource-generalization` | `abstract_additive_only` | `stable_standdown` | Resolved safely. Step 6 kept generic marker/entity pressure private/confirming 3/3. |
| `startup-pivot-new-run2` | `abstract_additive_only` | `unstable_mixed` | Step 6 always saw additive pressure, but mostly as reframe-only. |
| `third-year-phd-student.v2.v60-off` | `unstable_mixed` | `borderline_unlock` | Improved toward concrete value, but still not clean: 2 concrete unlocks and 1 reframe-only sample. |
| `third-year-phd-student.v2.v60-on` | `borderline_unlock` | `stable_positive` | Resolved positively. V60-on PhD produced concrete additive pressure 3/3. |

## What We Learned

The repeat pass did not justify moving to full reviewer calibration.

It also did not falsify the architecture.

It clarified the bottleneck:

```text
The unstable zone is not generic overpromotion.
The unstable zone is high-clutter / V60-adjacent / reframe-vs-concrete custody.
```

The marker/entity-loss risk got safer, not worse:

- `marker-entity-attempt-1-resource-generalization` resolved to stable
  stand-down.
- The prior stable marker/entity cases stayed outside the repeat set because
  they had already stood down cleanly.

The PhD V60-on case got stronger:

- repeat pass produced `stable_positive`;
- this supports the idea that V60 can help Step 6 name concrete sequence
  deltas when the problem is naturally sequencing-shaped.

The founder/startup/high-clutter family is still the live issue:

- Step 6 often marks deck pressure as additive;
- but it often populates `reframed_emphasis` rather than `added_entities`,
  `removed_entities`, or `reordered_sequences`;
- the current answer-delta guardrail therefore suppresses those outputs.

That may be correct. Abstract reframing is not enough for public visibility.

But it may also be too strict for high-clutter cases, where the useful change
may be structural framing, sharper decision boundaries, or stress-reducing
order rather than a newly named entity.

This is the exact issue the calibration plan told us to watch:

```text
If Step 6 routinely lands in reframed_emphasis only on cases where reviewers
prefer deck-visible, the vocabulary is constraining honest expression.
```

We now have enough frequency to treat this as a live calibration question, but
not enough reviewer evidence to redesign the vocabulary.

## Decision

Do not run full reviewer calibration yet.

Do not keep blindly repeating the same unstable cases.

Do not add a new deterministic gate.

Do not loosen the answer-delta guardrail merely because high-clutter cases are
noisy.

The right next move is a narrow diagnostic reviewer phase over saved samples,
not a runtime or prompt redesign:

1. Review stable positives and stable stand-downs as sanity anchors.
2. Review selected persistent high-clutter/reframe-only samples to answer one
   question:

```text
Are reframe-only Step 6 outputs ever genuinely better/non-inferior to the
anchor, or are they correctly suppressed by the answer-delta guardrail?
```

This keeps cognition where it belongs. Reviewers judge usefulness. Code only
keeps custody of what kind of claim Step 6 made.

## Recommendation

Run `calibration_reframe_diagnostic_review_v0` next.

Scope:

- no runtime effect;
- no `SKILL.md` edit;
- no new Step 6 calls;
- reviewer calls only against saved Step 6 samples;
- include stable anchors plus the persistent high-clutter/reframe-only cases;
- require reviewer label/winner-arm consistency, as in the previous probe
  contract.

Expected decision after that review:

- If reviewers do not prefer reframe-only samples, keep the answer-delta
  guardrail and treat those cases as correctly suppressed.
- If reviewers do prefer reframe-only samples, do not remove the guardrail.
  Instead, design-review the answer-delta vocabulary so Step 6 can express
  concrete structural changes without pretending they are added entities.

Runtime promotion remains blocked.
