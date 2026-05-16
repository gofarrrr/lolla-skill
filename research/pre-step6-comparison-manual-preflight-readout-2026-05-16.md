# Pre-Step-6 Manual Preflight Readout

Date: 2026-05-16

Status: research preflight only. This does not change runtime behavior,
`SKILL.md`, `HOW_IT_WORKS.md`, default `/lolla`, product docs, Lane 1, V60, the
canonical knowledge base, or public output.

Template:

```text
research/pre-step6-comparison-readout-template-2026-05-16.md
```

Fixtures checked:

```text
research/pre-step6-comparison-fixtures/third-year-phd-student-20260430T140800Z.md
research/pre-step6-comparison-fixtures/founder-grant-marcus-equity-20260428T064421Z.md
research/pre-step6-comparison-fixtures/mid-level-consultant-report-2-20260429T144611Z.md
```

## Scope

This is not the real comparison. It does not generate final-answer variants.

This preflight asks whether the three fixtures are good enough to run through the
actual comparison template and what each fixture is likely to test.

## Summary Verdict

```text
preflight only - run answer variants next
```

The fixtures are useful enough to run. They cover the three first-pass shapes we
wanted:

- conflict and fallback viability;
- duplicate demotion;
- hard-boundary preservation with discard handling.

They do not prove that `reasoning_bundle.v1` beats raw artifacts. The next step
must generate or collect actual Step-6-style answer variants for:

```text
current control
raw artifacts
indexed bundle
```

## Case 1: Third-Year PhD Student

```text
case_id: third-year-phd-student
source_run_id: third-year-phd-student__20260430T140800Z
fixture_path: research/pre-step6-comparison-fixtures/third-year-phd-student-20260430T140800Z.md
readout_type: preflight
```

Case shape:

```text
primary reasoning shape: conflict / constraint / fallback viability
secondary reasoning shapes: pseudo-quantitative base-rate pressure, quiet option expansion
what makes this case high-clutter: option 3 can be attractive while the fallback may decay and the Silva/data constraint may remain unresolved
what would make this case a bad test: if final-answer variants simply repeat the current control without integrating fallback executability
```

Arm expectations:

```text
Arm A expected risk: preserves a good current answer but may leave the 18-month fallback too abstract.
Arm B expected risk: raw artifacts may surface all issues but over-caveat the answer.
Arm C expected risk: bundle may help preserve tension, but could over-privilege primary labels.
```

Preflight assessment:

- fixture caps are respected;
- the artifacts are distinct enough to test bundle indexing;
- the bundle has a real job: preserve unresolved tension instead of choosing a
  clean answer too early;
- the likely bundle lift, if any, would come from `conflicts_or_tensions`,
  `hard_boundaries`, and `rethinking_questions`.

Decision:

```text
run_answer_variants
```

## Case 2: Founder Grant Marcus Equity

```text
case_id: founder-grant-marcus-equity
source_run_id: founder-grant-marcus-equity__20260428T064421Z
fixture_path: research/pre-step6-comparison-fixtures/founder-grant-marcus-equity-20260428T064421Z.md
readout_type: preflight
```

Case shape:

```text
primary reasoning shape: duplicate / low marginal value / systems pressure
secondary reasoning shapes: discard guard against unsupported architecture diagnosis
what makes this case high-clutter: several valid cautions are already covered, while one systems-pressure family may add value
what would make this case a bad test: if raw artifacts and bundle both merely restate valuation and instrument caveats
```

Arm expectations:

```text
Arm A expected risk: may miss the systems-pressure family.
Arm B expected risk: may amplify duplicate valuation and option-expansion cautions.
Arm C expected risk: should demote duplicates, but may turn systems language generic.
```

Preflight assessment:

- this is the cleanest duplicate-demotion test;
- the bundle has a concrete job: carry systems pressure while keeping repeated
  valuation/instrument cautions quiet;
- the likely bundle lift, if any, would come from `duplicate_or_lower_priority`,
  `quiet_or_discard_candidates`, and `final_reasoner_instruction`;
- this case is a good early kill test because raw artifacts may already be
  enough for a careful final reasoner.

Decision:

```text
run_answer_variants
```

## Case 3: Mid-Level Consultant Report

```text
case_id: mid-level-consultant-report-2
source_run_id: mid-level-consultant-report-2__20260429T144611Z
fixture_path: research/pre-step6-comparison-fixtures/mid-level-consultant-report-2-20260429T144611Z.md
readout_type: preflight
```

Case shape:

```text
primary reasoning shape: hard boundary / option expansion / misfit discard
secondary reasoning shapes: counsel-incentive testing, Wednesday protocol, internal-channel distinction
what makes this case high-clutter: useful option expansion can accidentally weaken the safety sequence
what would make this case a bad test: if variants become legal-channel advice instead of counsel-gated decision support
```

Arm expectations:

```text
Arm A expected risk: keeps safety sequence but may miss counsel-incentive and channel distinctions.
Arm B expected risk: may add too many useful cautions and bury the first actions.
Arm C expected risk: should protect hard boundaries, but could make the answer over-structured.
```

Preflight assessment:

- this is the strongest hard-boundary test;
- the bundle has a concrete job: add nuance only inside the safety sequence;
- the likely bundle lift, if any, would come from `hard_boundaries`,
  `conflicts_or_tensions`, and `quiet_or_discard_candidates`;
- this case must be scored harshly: if the bundle makes the answer longer,
  more legalistic, or less direct, it loses even if private traceability improves.

Decision:

```text
run_answer_variants
```

## Aggregate Preflight

| Case | Fixture Quality | Main Test | Preflight Decision |
| --- | --- | --- | --- |
| Third-year PhD student | usable | conflict preservation | run answer variants |
| Founder grant Marcus equity | usable | duplicate demotion | run answer variants |
| Mid-level consultant report | usable | hard-boundary preservation | run answer variants |

## What Would Count As Real Evidence Next

The next readout must include actual final-answer variants or equivalent
Step-6-style outputs for all three arms.

First answer-variant readout:

```text
research/pre-step6-comparison-readouts/founder-grant-marcus-equity-answer-variant-readout-2026-05-16.md
```

Minimum next outputs:

```text
case_id
Arm A final-answer variant
Arm B final-answer variant
Arm C final-answer variant
criterion scores
win/tie/loss
kill/proceed decision
```

Do not proceed to implementation from this preflight alone.

## Current Decision

```text
run_answer_variants
```

The comparison bench is ready enough to test. The bundle path is not yet
validated.
