# PR67 Reversibility Guard Enrichment v29 Report

Status: draft review substrate only.

## Purpose

PR67 continues the slow corpus-quality pass after v28. The scope is a small reversibility and recovery-path slice:

- add one `optionality` absence guard for disjunctive/failsafe pickup;
- fold the `second-order-thinking` recovery-path check into the existing downstream reversal affordance;
- leave `inversion` unchanged after full source review.

This is not runtime pickup work. It does not change `/lolla`, prompts, packet production, renderer behavior, lane adapters, or artifact selection.

## Source Review

Reviewed corpus files:

- `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216/Optionality_rag.md`
- `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216/Second_Order_Thinking_rag.md`
- `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216/Inversion_rag.md`

Reviewed current records:

- `data/model_affordances/pilot/optionality.json`
- `data/model_affordances/pilot/second-order-thinking.json`
- `data/model_affordances/pilot/inversion.json`

## Changes

Added one absence guard to `optionality`:

- `disjunctive-failsafe-as-optionality`

Reason: the source mentions alternative solutions, fail-safes, and disjunctive structures, but that material is not a separate optionality affordance by itself. Runtime-style pickup should require reversible paths, capped downside, learning value, or a commitment boundary before optionality is promoted. Pure component-failure mitigation belongs more naturally to adjacent risk, redundancy, resilience, or margin-of-safety records.

Strengthened `second-order-thinking.downstream-reversal-stress-test` with:

- a new case-evidence item for later dependencies made harder to reverse by acting now;
- a new treatment requirement: `recovery-path-check`;
- a diagnostic question for the first signal that the cheap recovery path has disappeared;
- exact source evidence from `Second_Order_Thinking_rag.md`.

No new `second-order-thinking` affordance was added. This preserves transaction identity: the recovery-path check is a sharper treatment requirement inside the existing downstream reversal affordance, not a separate card.

## No-Change Finding

`inversion` was reviewed and left unchanged.

The current three affordances already cover:

- anti-goal failure mechanism mapping;
- disconfirmation before defense;
- obstacle removal before added force.

The extra source material, including premortem, margin-of-safety, RAF, Vanguard, Patagonia, India, and Atomic Habits examples, illustrates existing inversion mechanisms or relation semantics. It did not justify a new transaction-distinct affordance.

## Compiled Artifact

Compiled:

- `data/compiled/model_affordances/affordances_v29.json`
- `data/compiled/model_affordances/quality_report_v29.md`

v29 metadata:

- contributing records: `222`
- affordances: `268`
- absence records: `469`
- schema validation failures: `0`
- source quote rejections: `0`

Delta from v28:

- model IDs unchanged;
- affordance IDs unchanged;
- absence records increased by `1`;
- second-order treatment detail strengthened without changing affordance count;
- runtime dormancy preserved.

## Quality Rationale

This PR follows the current enrichment rule:

> Add a positive affordance only if it changes downstream use/reject/defer/merge behavior with distinct activation conditions, evidence, treatment, and misuse guards.

The source review did not justify a new positive affordance. It did justify:

- one absence/routing guard for optionality, because fail-safe language can otherwise over-route to optionality;
- one treatment hardening for second-order-thinking, because the recovery-path check changes how the existing affordance should be used;
- no inversion expansion, because the existing record already captures the source's distinct operational moves.

## Runtime Boundary

`affordances_v29` is not imported by live runtime paths.

The following remain out of scope:

- changing `engine/system_b/reasoning_substrate_packet.py`;
- changing packet review rendering;
- changing `/lolla` prompts;
- changing lane-to-nomination adapters;
- selecting v29 automatically;
- using this artifact as retrieval or product context.

## Verification

Focused tests:

```bash
pytest tests/test_pr67_v29_reversibility_guard_enrichment.py tests/test_model_affordance_compiler.py tests/test_pr66_v28_broad_system_guard_enrichment.py tests/test_pr65_v27_decision_method_guard_enrichment.py tests/test_pr64_v26_undercompression_guard_enrichment.py
```

Additional checks:

```bash
rg -n "affordances_v29|model_affordances_v29" engine scripts tests -g '*.py'
git diff --check
```

Expected runtime scan result:

- only PR67 test references v29;
- no `engine/` or `scripts/` live runtime references v29.
