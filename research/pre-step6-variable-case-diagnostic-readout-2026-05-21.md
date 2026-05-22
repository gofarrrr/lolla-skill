# Pre-Step 6 Variable-Case Diagnostic Readout

Date: 2026-05-21

Slice: `pre_step6_variable_case_diagnostic_v0`

Runtime policy: `runtime_dormant`

Promotion effect: `none_research_only`

## Question

The repaired Kimi calibration left four cases variable after same-prompt repeat
sampling:

```text
founder-grant-marcus-equity.high-clutter.v60-on
mid-level-consultant-report-2
third-year-phd-student.v2.v60-off
third-year-phd-student.v2.v60-on
```

The diagnostic asked:

```text
Is this only Step 6 ledger-label variance, or does the visible answer itself
also vary?
```

Then it ran a small alternative-model probe to see whether the variance is
Kimi-specific or case-shape-specific.

## Kimi Diagnostic

Artifacts:

- `research/pre-step6-variable-case-diagnostic/variable-case-diagnostic-contract.v1.json`
- `research/pre-step6-variable-case-diagnostic/variable-case-diagnostic-result.v1.json`

Aggregate:

```text
variable_case_count = 4
total_sample_count = 24
balanced_or_near_balanced_case_count = 3
strong_positive_tilt_case_count = 1
ledger_label_variance_dominant_count = 0
answer_and_ledger_variance_count = 4
diagnostic_read = variable_cases_include_answer_level_variance
```

Case read:

| Case | Unlock Ratio | V60 Mode | Min Token Jaccard | Read |
| --- | ---: | --- | ---: | --- |
| `founder-grant-marcus-equity.high-clutter.v60-on` | 4/6 | on | 0.549 | answer and ledger variance |
| `mid-level-consultant-report-2` | 3/6 | not_applicable | 0.504 | answer and ledger variance |
| `third-year-phd-student.v2.v60-off` | 3/6 | off | 0.596 | answer and ledger variance |
| `third-year-phd-student.v2.v60-on` | 5/6 | on | 0.409 | answer and ledger variance |

Interpretation:

The variable cases are not merely stable answers with unstable self-labels. The
answer content itself varies substantially across samples. This makes the
variance a real cognition-stability problem rather than a simple ledger
formatting problem.

## Alternative-Model Probe

Artifacts:

- `research/pre-step6-variable-case-alt-model-gpt51/step6-samples/*.json`
- `research/pre-step6-variable-case-alt-model-gpt51/calibration-step6-result.v1.json`
- `research/pre-step6-variable-case-alt-model-gpt51/variable-case-diagnostic-result.v1.json`

Step 6 model:

```text
openai/gpt-5.1-chat
```

Result:

| Case | GPT Ledger Read | GPT Visibility Read |
| --- | --- | --- |
| `founder-grant-marcus-equity.high-clutter.v60-on` | 2 additive / 1 private | still variable |
| `mid-level-consultant-report-2` | 3 private / 0 additive | stable stand-down |
| `third-year-phd-student.v2.v60-off` | 3 additive / 0 private | visibility-stable positive |
| `third-year-phd-student.v2.v60-on` | 3 additive / 0 private | visibility-stable positive |

Important nuance:

The calibration stability classifier still marks the GPT PhD cases as
`unstable` because the specificity bucket varies between
`concrete_delta_present` and `structural_delta_present`. But both buckets
unlock under the answer-delta policy. So for visibility behavior, those cases
are stable positive under GPT.

## Structural Delta Update

The prior Kimi corpus had:

```text
structural_delta_sample_count = 0
```

The GPT variable-case probe produced:

```text
structural_delta_sample_count = 5
structural_delta_field_sample_count = 9
```

This means the pure `structural_delta_present` path is no longer merely
theoretical. It did not fire under Kimi calibration, but it did fire under the
alternative Step 6 model. Do not collapse the answer-delta vocabulary back to
four fields yet.

## Interpretation

The variable-case problem is partly model-dependent:

- consultant is variable under Kimi but stable stand-down under GPT;
- PhD off/on are variable under Kimi but visibility-stable positive under GPT;
- founder V60-on remains variable under both model families.

So the variable cases are not one single failure mode.

The evidence points to two live questions:

1. Does Step 6 need model routing or model selection for ledger stability?
2. Is founder V60-on a genuinely borderline case shape that needs a special
   research answer before runtime?

Neither question should be answered by a deterministic wisdom gate.

## Decision

Do not promote globally.

Do not add another deterministic selector.

Do not update `SKILL.md`.

Do not discard `structural_delta`; the alternative model exercised it.

Next research move:

```text
inspect variable answer cores and compare model-family behavior before
architecture decision
```

The strongest near-term architectural hypothesis is not "add a gate." It is:

```text
Step 6 ledger stability may be model-family-sensitive.
```

That hypothesis should be tested and designed around before any global shadow
implementation.
