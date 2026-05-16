# Pre-Step-6 Raw Vs Control Rubric Comparison Readout

Date: 2026-05-16

Status: research-only readout. This does not change runtime behavior,
`SKILL.md`, `HOW_IT_WORKS.md`, default `/lolla`, product docs, Lane 1, V60, the
canonical knowledge base, or public output.

Related:

```text
research/pre-step6-raw-artifact-answer-consumption-readout-2026-05-16.md
research/pre-step6-raw-artifact-four-fixture-render-readout-2026-05-16.md
research/pre-step6-raw-artifact-render-validation-slice-2026-05-16.md
research/pre-step6-next-slice-decision-note-2026-05-16.md
research/pre-step6-cognitive-worker-system-plan-2026-05-16.md
```

## Question

Do raw-handoff answer cores beat current-control answer cores under a strict
local rubric before any indexed bundle challenger or worker orchestration is
authorized?

## What Compared

Each fixture compares two answer cores for the same case:

```text
control_answer_core
raw_answer_core_ref
```

`control_answer_core` is a compact current-control answer core without the new
raw handoff. `raw_answer_core_ref` points to the authored Step-6-style answer
core that consumed the raw `reasoning_artifact.v1` handoff.

The indexed bundle challenger was not run. The gate for that challenger was:

```text
run only if raw visibly loses against current control
```

Raw did not visibly lose in any case, so the bundle challenger stayed closed.

## How The Comparison Worked

This slice adds the dormant fixture type:

```text
pre_step6_answer_comparison.v1
```

Each comparison fixture:

- embeds one current-control answer core;
- references one raw-handoff answer-core fixture;
- validates that the referenced raw answer core exists and matches the case;
- validates public-answer hygiene for both answer cores;
- scores 1-8 case-specific criteria as `control`, `raw`, or `tie`;
- computes the aggregate decision from criterion winners.

The tie rule is conservative:

```text
tie_break_rule: raw_tie_with_control_stops
```

That means raw does not win by merely existing. If raw and control have equal
criterion wins, the decision is `tie_stop`, not promotion.

## Criteria

The criteria were local to each case rather than generic preference questions.
They tested whether the final answer preserved or improved the decision-relevant
pressure without leaking private machinery.

Common criterion families:

- preserve the current-control strength before rewarding raw;
- keep source-grounded force;
- reduce unsupported precision;
- preserve hard boundaries unless relaxation facts are present;
- make conflicts or constraints more operational;
- demote duplicates and quiet artifacts instead of amplifying them;
- avoid tempting but unsupported lenses;
- stay compact and usable;
- avoid public machinery terms.

## Fixture Files

```text
research/pre-step6-raw-artifact-comparisons/third-year-phd-student.raw-vs-control-comparison.v1.json
research/pre-step6-raw-artifact-comparisons/founder-grant-marcus-equity.raw-vs-control-comparison.v1.json
research/pre-step6-raw-artifact-comparisons/mid-level-consultant-report-2.raw-vs-control-comparison.v1.json
research/pre-step6-raw-artifact-comparisons/mother-address-year.raw-vs-control-comparison.v1.json
```

## Result

| Case | Raw Wins | Control Wins | Ties | Decision | Main Raw Lift |
| --- | ---: | ---: | ---: | --- | --- |
| Third-year PhD student | 3 | 0 | 2 | `raw_wins` | Fallback executability, Silva/data constraint, base-rate humility |
| Founder grant Marcus equity | 2 | 0 | 3 | `raw_wins` | Dependency-system framing and 90-day measurement chain |
| Mid-level consultant report | 3 | 0 | 2 | `raw_wins` | Counsel-incentive gate, Wednesday protocol, channel distinction |
| Mother deciding address year | 3 | 0 | 2 | `raw_wins` | Instrument-trust warning, tripwire sizing, explicit leverage decline |

Aggregate:

```text
all four comparison fixtures validate: yes
raw beats control in all four strict local comparisons: yes
control beats raw on any criterion: no
bundle challenger triggered: no
worker orchestration authorized: no
```

## What This Supports

This supports the simpler raw path as the current research winner:

```text
raw reasoning_artifact.v1 handoff
  -> Step-6-style answer core
  -> strict local comparison against current control
```

It does not support:

```text
reasoning_bundle.v1 runtime machinery
reasoning_workpack.v1 builder
worker prompt builders
subagent orchestration
OpenRouter synthesis
product docs
default /lolla behavior
```

## Caveat

This is stricter and more useful than a loose preference read, but it is still
local research evidence.

It is not:

```text
a blind model judgment
production evidence
a live /lolla run
proof that subagents can produce the artifacts reliably
proof that raw artifacts beat every future bundle challenger
```

The fixtures are authored. The value of this result is that it blocks premature
bundle and worker work. It does not authorize promotion.

## Verification

Focused test command:

```text
python3 -m pytest tests/test_pre_step6_raw_artifacts.py -q
```

Observed result:

```text
14 passed
```

## Decision

```text
continue_raw_path
freeze_raw_path_as_current_research_winner
do_not_build_bundle
do_not_build_workers
do_not_promote_product_behavior
```

Next acceptable work:

```text
stop research here and keep the clean decision record
or run a genuinely blind evaluator only if more evidence is needed
or build a minimal research-only raw-render interface if implementation resumes
```

The bundle path returns only if a future high-clutter case shows raw losing in
final public-answer quality, not merely in private operator neatness.
