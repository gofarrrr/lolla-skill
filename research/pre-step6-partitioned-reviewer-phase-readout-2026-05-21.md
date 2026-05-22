# Pre-Step 6 Partitioned Reviewer Phase Readout

Date: 2026-05-21

Slice: `pre_step6_partitioned_reviewer_phase_v0`

Runtime policy: `runtime_dormant`

Promotion effect: `none_research_only`

## Question

The repaired Kimi calibration produced a stable partition:

```text
6 stable-positive candidates
7 stable-standdown candidates
4 variable cases quarantined
```

This reviewer phase asked a narrow question:

```text
On the 13 stable cases only, do two blinded reviewer families agree with the
Step 6 visibility read?
```

This phase explicitly did not review the four variable cases. It cannot unlock
shadow implementation by itself.

## Method

Artifacts:

- `research/pre-step6-partitioned-reviewer-phase/partitioned-reviewer-contract.v1.json`
- `research/pre-step6-partitioned-reviewer-phase/judgments/*.json`
- `research/pre-step6-partitioned-reviewer-phase/partitioned-reviewer-result.v1.json`

Reviewer families:

```text
openai/gpt-5.1-chat
google/gemini-3.1-flash-lite
```

The packets were blind A/B comparisons. The reviewer saw the case brief,
ledger signal, answer-delta summary, and two candidate answers, but not which
candidate was anchor or Step 6.

## Result

Aggregate:

```text
case_count = 13
stable_positive_case_count = 6
stable_standdown_case_count = 7
stable_positive_supported_count = 6
stable_positive_rejected_count = 0
stable_standdown_supported_count = 6
stable_standdown_rejected_count = 0
ambiguous_count = 1
tension_count = 0
reviewer_read = stable_partition_partial_or_ambiguous
```

Stable-positive cases:

```text
bridge-high-clutter-sensitive-overlay       supported
bridge-sensitive-anchor-misses-tripwire     supported
bridge-sequencing-sensitive-boundary        supported
founder-grant-marcus-equity.v60-off         supported
multi-offer-new-run2                        supported
startup-pivot-new-run2                      supported
```

Stable-standdown cases:

```text
fp-bevelin-irrelevant-incentives            supported
fp-marker-preserved-entity-lost             supported
fp-polya-true-but-useless                   supported
marker-entity-attempt-1-resource-generalization supported
marker-entity-attempt-2-tripwire-compression ambiguous
marker-entity-attempt-3-actor-sequence-blur supported
mother-address-year                         supported
```

## Ambiguous Case

The one ambiguous case was benign but correctly left ambiguous:

```text
marker-entity-attempt-2-tripwire-compression
```

The anchor answer and Step 6 answer differed by one word:

```text
anchor: name the tripwires
step6: name the specific tripwires
```

OpenAI reviewer:

```text
tie
```

Gemini reviewer:

```text
step6_non_inferior
```

Both reviewers said there was no meaningful payload loss or bloat. The strict
contract keeps this as `ambiguous` rather than silently promoting it to
support. That is the right custody posture.

## Interpretation

The stable-positive partition is strongly supported: all six cases were
preferred by both reviewer families.

The stable-standdown partition is mostly supported and has no rejection. The
single ambiguous case is a near-identical answer pair, not evidence that the
stand-down policy is unsafe.

This is good evidence for the stable partition.

It is not global promotion evidence.

The four variable cases still need their own answer before runtime or shadow
implementation can move forward.

## Decision

Do not promote globally.

Do not update `SKILL.md`.

Do not treat the stable partition reviewer pass as permission to ignore the
variable cases.

Use this result as:

```text
stable_partition_supported_with_one_benign_ambiguity
```

Continue the variable-case diagnostic track before any shadow implementation.
