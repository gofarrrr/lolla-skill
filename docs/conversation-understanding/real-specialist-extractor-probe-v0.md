# Real Specialist Extractor Probe v0

PR29B ran the existing specialist extractors on the four modern baseline
archives using real approved boundary calls.

This is an offline measurement probe. It does not change `$lolla` runtime
behavior, prompts, archive generation, `SKILL.md`, provider-boundary policy,
semantic coverage archive integration, or `conversation_understanding_ir.v0`.

## Purpose

PR27 showed repeated semantic coverage gaps:

- `live_constraints` were mostly `turn_ref` grounded rather than span-grounded;
- `assistant_stance_or_recommendation_lineage` was always partial and
  artifact-level;
- `dropped_or_under_carried_threads` were uneven;
- `user_values_or_priorities_signal` was not first-class.

PR29A proved the probe harness with fake boundary payloads. PR29B asked the
narrow real question:

> Do existing specialist extractor calls materially improve semantic coverage
> on modern archives?

## Sample

The probe used the four modern current-main baseline archives:

| case | run_id |
|---|---|
| `launch-limited-beta-workflow` | `20260626T125112Z_b861fd` |
| `initiate-pre-sale-coffee` | `20260626T131939Z_368960` |
| `implement-price-increase-three` | `20260626T132915Z_49172d` |
| `five-person-saas-team` | `20260626T133147Z_99712f` |

Outputs were written outside archive folders under `/tmp`. The archive folders
were not mutated.

The PR29B runner is OpenRouter-only for real-boundary cost telemetry. Other
providers are intentionally rejected until a later PR adds provider-specific
usage and cost reporting.

## Aggregate Result

| metric | value |
|---|---:|
| records inspected | 4 |
| model calls | 12 |
| estimated cost USD | 0.008547 |
| cost estimate state | complete |
| boundary status counts | `ok:12` |
| provider-boundary warning count | 12 |
| improved target elements | 12 |

The provider-boundary warning count means the provider returned reasoning
metadata despite disabled reasoning. The probe did not export provider
reasoning details. Treat this as a separate provider-boundary issue, not an
extractor-validation failure.

## Per-Run Coverage Delta

| case | run_id | live constraints | stance lineage | dropped threads | calls | cost |
|---|---|---:|---:|---:|---:|---:|
| `launch-limited-beta-workflow` | `20260626T125112Z_b861fd` | yes | yes | yes | 3 | 0.002618 |
| `initiate-pre-sale-coffee` | `20260626T131939Z_368960` | yes | yes | yes | 3 | 0.002187 |
| `implement-price-increase-three` | `20260626T132915Z_49172d` | yes | yes | yes | 3 | 0.001970 |
| `five-person-saas-team` | `20260626T133147Z_99712f` | yes | yes | yes | 3 | 0.001772 |

## Per-Specialist Validation

| specialist | attempted | raw candidates | validated | improved runs | grounding | failures |
|---|---:|---:|---:|---:|---|---|
| `live_constraints` | 4 | 18 | 18 | 4 | `span:18` | none |
| `stance` | 4 | 21 | 21 | 4 | `span:21` | none |
| `dropped_threads` | 4 | 5 | 5 | 4 | `span:5` | none |

All emitted candidates validated. All validated events were span-grounded. All
three target semantic elements improved on all four sampled runs.

## Decision

Decision: **A. Existing specialists are worth later runtime-design discussion.**

Reason: the existing `live_constraints`, `stance`, and `dropped_threads`
specialists materially improved their target semantic coverage elements on all
four modern archives, with complete cost telemetry and no validation failures.

This is not approval to integrate specialists into runtime. It is approval to
design a later runtime or offline-integration proposal that preserves the same
custody constraints.

## Still Unsolved

Decision: **D. User-values gap remains unsolved by current specialists.**

The current specialist set does not produce first-class user values or stated
priorities. Do not smuggle a user-values extractor into the next runtime design.
Treat it as a separate future design question.

## Privacy And Custody

The probe read raw archive artifacts internally because the validators need
conversation context. The generated reports did not include:

- raw transcript text;
- memo text;
- revised-answer text;
- raw model messages;
- provider reasoning details;
- failed quote text;
- absolute archive paths;
- control argument values.

The privacy scan over the generated Markdown, aggregate JSON, and per-run JSON
had no hits for local home paths, secret markers, raw-message markers,
fabricated-passage markers, provider-reasoning markers, or credential markers.

The archive mutation check confirmed all four sampled archive folders were
unchanged.

## Recommended Next Slice

Recommended next slice:

```text
specialist_runtime_design_without_integration_v0
```

The next step should be a design PR, not immediate runtime integration. It
should specify where specialist calls would run, how cost approval works, how
provider-boundary warnings affect readiness, whether outputs remain offline or
become archived artifacts, and how semantic coverage deltas stay measurable.

Do not start:

- `$lolla` runtime integration;
- prompt redesign;
- `archive_run.py` integration;
- semantic coverage archive integration;
- `conversation_understanding_ir.v0`;
- graph DB, embeddings, or chunking;
- user-values extraction;
- LLM judge or answer-quality scoring;
- provider-boundary policy changes.
