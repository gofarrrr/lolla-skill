# PR66 Broad/System Guard Enrichment v28 Report

Status: draft review substrate only.

## Purpose

PR66 continues the post-coverage enrichment audit after v27. The scope is intentionally narrow:

- protect `incentives` from being promoted by emotional-copy or desire-language alone;
- protect `systems-thinking` from generic complexity, latticework, or environment-change language that lacks system behavior evidence;
- keep `leverage-points` unchanged after source review because its current record already carries proof-of-mechanism, bounded-analysis, and execution-hardening guards.

This is not runtime pickup work. It does not change `/lolla`, packet production, renderer behavior, prompts, lane adapters, or artifact selection.

## Source Review

Reviewed corpus files:

- `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216/Incentives_rag.md`
- `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216/Systems_Thinking_rag.md`
- `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216/Leverage_Points_rag.md`

Reviewed current records:

- `data/model_affordances/batch_1/incentives.json`
- `data/model_affordances/pilot/systems-thinking.json`
- `data/model_affordances/batch_1/leverage-points.json`

## Changes

Added one absence guard to `incentives`:

- `emotional-desire-communication-as-standalone-incentives-affordance`

Reason: the source contains customer desire, fear, self-serving motivation, and hot-cognition marketing examples. Those are useful as evidence inside incentive diagnosis, but they should not become a standalone incentives affordance unless the case is actually redesigning a reward, penalty, status, feedback, or motivation structure.

Added two absence guards to `systems-thinking`:

- `generic-complexity-or-latticework-without-system-behavior`
- `environment-reshaping-decision-without-loop-evidence`

Reason: the source supports systems thinking when interrelationships, feedback loops, delayed effects, distributed actors, recurring symptoms, or a variable-to-move can be shown. It does not support promoting generic big-picture language as systems thinking. The environment-reshaping material is real, but it is already carried by structure-over-events, feedback-loop mapping, and metric/leverage design unless a case supplies traceable system-change evidence.

No positive affordances were added.

## No-Change Finding

`leverage-points` was reviewed and left unchanged.

The current three affordances already cover:

- proving a structural point before action;
- bounding analysis to leverage-testing facts;
- hardening leverage choices against resistance, bias, and execution failure.

The tempting extra material, especially communication-core and startup-pitching examples, is already guarded by the existing absence record:

- `standalone-communication-core-affordance`

Adding another positive affordance here would increase surface area without changing downstream use/reject/defer behavior.

## Compiled Artifact

Compiled:

- `data/compiled/model_affordances/affordances_v28.json`
- `data/compiled/model_affordances/quality_report_v28.md`

v28 metadata:

- contributing records: `222`
- affordances: `268`
- absence records: `468`
- schema validation failures: `0`
- source quote rejections: `0`

Delta from v27:

- model IDs unchanged;
- affordance IDs unchanged;
- absence records increased by `3`;
- runtime dormancy preserved.

## Quality Rationale

This PR follows the current enrichment rule:

> Add a positive affordance only if it changes downstream use/reject/defer/merge behavior with distinct activation conditions, evidence, treatment, and misuse guards.

The source review did not justify a positive split. The more valuable move is ownership protection:

- emotion/desire evidence should not route a case into `incentives` unless reward or motivation structure is actually at stake;
- systems language should not route a case into `systems-thinking` unless system behavior, loops, delays, recurring patterns, or environment-change effects are visible;
- leverage-point language should remain tied to proof of mechanism, not strategic-sounding priority labels.

## Runtime Boundary

`affordances_v28` is not imported by live runtime paths.

The following remain out of scope:

- changing `engine/system_b/reasoning_substrate_packet.py`;
- changing packet review rendering;
- changing `/lolla` prompts;
- changing lane-to-nomination adapters;
- selecting v28 automatically;
- using this artifact as retrieval or product context.

## Verification

Focused tests:

```bash
pytest tests/test_pr66_v28_broad_system_guard_enrichment.py tests/test_model_affordance_compiler.py tests/test_pr65_v27_decision_method_guard_enrichment.py tests/test_pr64_v26_undercompression_guard_enrichment.py tests/test_pr63_v25_zero_absence_audit.py tests/test_pr62_v24_guard_enrichment.py
```

Additional checks:

```bash
rg -n "affordances_v28|model_affordances_v28" engine scripts tests -g '*.py'
git diff --check
```

Expected runtime scan result:

- only PR66 test references v28;
- no `engine/` or `scripts/` live runtime references v28.
