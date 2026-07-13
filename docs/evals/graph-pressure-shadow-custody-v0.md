# Graph pressure shadow custody v0

Status: provider-free eval contract; no runtime integration  
Date: 2026-07-10

## Problem

The current companion path can put deterministic relationship-graph chunks
inside a directly detected model's cheat-sheet anchor. Step 6 sees the chunk,
but the private-table receipt dispositions the parent anchor rather than each
relationship chunk.

That creates an attribution gap:

```text
anchor marked used
  does not prove
each embedded graph relationship was used, rejected, deferred, or guarded
```

It also prevents a fair graph-disabled comparison because the experiment cannot
name exactly which graph contribution is present or absent.

## Narrow repair

`scripts/evals/build_graph_pressure_shadow_custody.py` reads a frozen pipeline
artifact after the run and creates metadata-only identities for graph-derived
companion chunks. It does not call a provider, rerun graph traversal, alter
selection, change Step 6 context, or modify runtime artifacts.

Each identity has this form:

```text
graph::<source-anchor>::<relation-type>::<target-model>::<text-sha-prefix>
```

The full text hash, source JSON pointer, raw-expansion JSON pointer, source and
target model IDs, relation type, and substrate activation metadata remain
available for exact replay and review. Checked-in shadow custody omits raw chunk
text.

## Empty ledger fields

The exporter creates empty fields for later source-first review:

- `disposition`;
- `strongest_plausible_application`;
- `condition_that_passed_or_failed`;
- `why`;
- `visible_effect`;
- `private_guardrail`;
- `risk_if_forced`;
- `risk_if_ignored`;
- `technical_blocker`;
- `source_review_status`.

Deterministic code creates identity and validates hashes. It must not fill the
semantic disposition. A later LLM/human reviewer may use, reject, defer, or keep
the pressure private, but must preserve the exact `graph_pressure_id`.

## Relationship to existing ledgers

This is a research-side supplement, not a replacement for:

- the pre-Step-6 private-table ledger;
- the V60 chunk ledger;
- the public revised answer;
- the final reasoning receipt.

The supplement exists because graph relationship chunks currently inherit
parent-anchor custody. Runtime integration is deferred until a graph-specific
experiment demonstrates value and the smallest useful receipt surface is clear.

## Future ablation contract

The first fair graph-specific downstream experiment should use one new holdout
and freeze all three arms before generation:

1. **strong transcript control** — complete conversation and neutral fresh
   reconsideration;
2. **non-graph portfolio** — the same control plus direct-label, frame-route,
   and embedding material under the frozen cap;
3. **graph-added portfolio** — identical to arm 2 plus one exact,
   source-reviewed `graph_pressure_id`.

This three-arm shape isolates both questions:

- Does any portfolio pressure add value beyond a strong reread?
- Does the exact graph relationship add value beyond the non-graph portfolio?

One call per arm, no retry, and no evaluator call is the initial ceiling. A
shuffled-edge arm is considered only after a clean graph-added signal; it is not
free evidence and may create unsafe noise.

Public revision and private receipt must follow
`public-revision-private-receipt-boundary-v0.md`. Public answer length, private
receipt volume, and whole-run cost are measured separately.

## Promotion requirements

Before any paid call, the exact graph chunk must be:

- source-supported;
- absent or materially incomplete in the strong control;
- absent from direct labels, frame routes, and the capped embedding packet;
- capable of a bounded action, evidence, confidence, frame, or private
  guardrail consequence;
- safe against forcing and lost value;
- individually dispositionable by exact ID.

If no chunk satisfies all conditions, Gate 6 stays blocked. The system should
not manufacture a candidate just to exercise the graph.

## Non-claims

Shadow identity is not relevance, usefulness, reasoning depth, a quality score,
graph promotion, or autonomous-action authority.
