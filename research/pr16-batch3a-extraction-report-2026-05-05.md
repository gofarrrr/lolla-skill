# PR16 Batch 3a Affordance Extraction Report

**Date:** 2026-05-05
**Status:** Targeted extraction patch. Draft-review-only. Runtime-dormant.

**Branch:** `feature/decision-pressure-pr16-batch3a-affordance-extraction`

**Contract:** `research/affordance-batch3a-extraction-brief-2026-05-05.md`

Doctrine line:

> Surface pulls extraction. Extraction does not push the product.

## Scope

PR16 extracted records for exactly the five PR15 Batch 3a target models:

1. `opportunity-cost`
2. `true-uncertainty-navigation`
3. `falsifiability`
4. `principal-agent-problem`
5. `probabilistic-thinking`

This PR did not run paid model calls, judge calls, or live `/lolla`. It did not
modify runtime behavior, prompts, validators, existing affordance records, or
user-facing surfaces.

## Source Custody

All five canonical source files were made resident under `data/model_sources/`
using the existing packet-assembly source-custody path:

- `Opportunity_Cost_rag.md`
- `True_Uncertainty_Navigation_rag.md`
- `Falsifiability_rag.md`
- `Principal_Agent_Problem_rag.md`
- `Probabilistic_Thinking_rag.md`

`data/model_sources/manifest.json` now records each file with `sha256` and byte
count. The source files match the canonical root declared by the existing
manifest.

## Extraction Outcome

Batch 3a produced `5` records, `5` affordances, and `12` absence records.

The extraction deliberately stayed small: one Decision Pressure-ready affordance
per model, plus absence records where broader material would create coverage
theater, duplicate existing v3 records, or exceed source support.

| Model | Source file | Outcome | Affordances | Absences | High-value fields found | Source quote validation | Decision Pressure relevance | Runtime policy |
| --- | --- | --- | ---: | ---: | --- | --- | --- | --- |
| `opportunity-cost` | `Opportunity_Cost_rag.md` | `strong_affordance_record` | 1 | 2 | next-best alternative, displaced work, stop condition, unrealistic-alternative guard | pass | improves sacrifice, dismissal, and tripwire quality for allocation pressures | dormant |
| `true-uncertainty-navigation` | `True_Uncertainty_Navigation_rag.md` | `strong_affordance_record` | 1 | 2 | robust action, scenario-to-commitment shape, scenario-theater guard, reversible-action trigger | pass | improves uncertainty pressures that need action under ambiguity without false certainty | dormant |
| `falsifiability` | `Falsifiability_rag.md` | `strong_affordance_record` | 1 | 2 | disconfirming evidence, reversal condition, kill criterion, protected-belief guard | pass | directly improves `Dismiss if` and `Tripwire or next action` quality | dormant |
| `principal-agent-problem` | `Principal_Agent_Problem_rag.md` | `thin_narrow_affordance_record` | 1 | 3 | delegated objective gap, hidden behavior, metric-compliance audit, capability/capacity dismissal | pass | supports future incentive-alignment pressure review, especially the PR14 suppressed PhD pressure | dormant |
| `probabilistic-thinking` | `Probabilistic_Thinking_rag.md` | `strong_affordance_record` | 1 | 3 | probability ranges, sensitivity checks, false-precision guard, update rule | pass | improves uncertainty pressure tripwires without making probability language a delay tactic | dormant |

## Per-Model Notes

### `opportunity-cost`

Record: `data/model_affordances/batch_3a/opportunity-cost.json`

Extracted one `displaced-alternative-commitment-gate` affordance. The useful
Decision Pressure move is not "consider alternatives"; it is naming the
specific executable next-best use of the same scarce resource and defining when
the current yes should stop.

Do-not-promote notes:

- Do not promote generic alternative comparison.
- Do not load the comparison with unrealistic alternatives.
- Do not duplicate `trade-offs` or `prioritization` unless the displaced
  next-best use is explicit.

### `true-uncertainty-navigation`

Record: `data/model_affordances/batch_3a/true-uncertainty-navigation.json`

Extracted one `scenario-bound-robust-action` affordance. The useful Decision
Pressure move is converting genuine ambiguity into commitment shape: no-regrets
move, reversible probe, staged commitment, delayed commitment, or big bet.

Do-not-promote notes:

- Do not promote generic unknown-unknowns inventories.
- Do not turn scenario work into narrative theater.
- Do not use uncertainty language to postpone action after robust action is
  available.

### `falsifiability`

Record: `data/model_affordances/batch_3a/falsifiability.json`

Extracted one `disconfirming-reversal-gate` affordance. The useful Decision
Pressure move is user-verifiable dismissal: a fact, threshold, or observation
that would stop, reverse, or revise the recommendation.

Do-not-promote notes:

- Do not promote generic skepticism.
- Do not invent tidy kill criteria beyond the source.
- Do not use falsifiability rhetoric when politics, ego, or mandate status
  means reversal would not be accepted.

### `principal-agent-problem`

Record: `data/model_affordances/batch_3a/principal-agent-problem.json`

Extracted one `delegated-alignment-drift-audit` affordance with `medium`
confidence. The named model itself is marked in the source as synthesized from
available materials, so the honest outcome is `thin_narrow_affordance_record`,
not a rich record.

Do-not-promote notes:

- Do not turn delegated alignment into bad-faith suspicion.
- Do not promote micromanagement as the control mechanism.
- Do not extract standalone AI-agent orchestration from this PR; that would
  widen Batch 3a beyond the Decision Pressure patch.

### `probabilistic-thinking`

Record: `data/model_affordances/batch_3a/probabilistic-thinking.json`

Extracted one `range-and-sensitivity-decision-gate` affordance. The useful
Decision Pressure move is honest probability range plus update rule, not exact
percentages.

Do-not-promote notes:

- Do not promote exact point estimates.
- Do not let probability language delay a needed commitment.
- Do not duplicate `confidence-calibration` unless the record adds range,
  sensitivity, tail, or update-rule discipline.

## Compiled Artifact

PR16 compiles the existing pilot, Batch 1, Batch 2, and Batch 3a records into:

- `data/compiled/model_affordances/affordances_v4.json`
- `data/compiled/model_affordances/quality_report_v4.md`
- `data/compiled/model_affordances/quality_report_v4_extra.md`

Compiled v4 shape:

- contributing records: `55`
- affordances: `91`
- absence records: `95`
- schema validation failures: `0`
- source quote rejections: `0`

The v4 artifact is still `draft_review_only`. It is not wired into runtime.

## Validation

Focused validation:

- `PYTHONPATH=. pytest tests/test_pr16_batch3a_records.py tests/test_model_affordance_compiler.py`

The PR16 tests check:

- only the five approved Batch 3a model records exist in `batch_3a`;
- records validate against schema and exact source quotes;
- records match `data/model_sources/manifest.json`;
- Batch 3a stays targeted at one affordance per model;
- the principal-agent record preserves its medium-confidence honesty signal;
- the compiler can produce deterministic v4 output from pilot + Batch 1 +
  Batch 2 + Batch 3a.

## Product Judgment

Batch 3a is a good extraction result because it improves future compact
Decision Pressure selection, dismissal, and tripwire quality without forcing
all five models into rich records.

The most important honesty signal is `principal-agent-problem`: the source is
operationally useful but not as strong as the other four. It should remain a
thin, medium-confidence record until a later dry review shows that it improves
the suppressed PhD incentive-alignment pressure without creating suspicion or
micromanagement theater.

## Next Checkpoint

Do not promote these records into `/lolla`, Observatory, memo, Step 8, Step 6,
or a new lane.

The next useful PR is a post-Batch-3a Decision Pressure dry surface review. It
should re-run the compact pressure selection against the same packet and gates
with v4 available, then ask:

- Did any selected pressure become sharper?
- Did any suppressed pressure become worth selecting?
- Did zero-output decisions change?
- Did `Dismiss if` quality improve?
- Did `Tripwire or next action` quality improve?
- Did coverage honesty improve without adding bloat?
- Would two reviewers apply the new records similarly?

Only after that dry review should the project decide whether a receiving
surface deserves runtime or user-facing work.
