# PR70 Medium Supported Guard Enrichment v32 Report

Status: draft review substrate only.

## Purpose

PR70 continues the post-coverage quality pass by reviewing the five remaining medium-confidence records whose top-level status is `supported`:

- `adverse-selection`
- `batna`
- `markov-chains`
- `principal-agent-problem`
- `six-thinking-hats`

The purpose is not to expand them into broader doctrine. The purpose is to preserve their useful narrow cards while making their limits visible before any future packet pickup.

This is not runtime pickup work. It does not change `/lolla`, prompts, packet production, packet rendering, lane adapters, artifact selection, or any product surface.

## Source Review

Reviewed corpus files:

- `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216/Adverse Selection_rag.md`
- `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216/BATNA_rag.md`
- `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216/Markov_Chains_rag.md`
- `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216/Principal_Agent_Problem_rag.md`
- `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216/Six_Thinking_Hats_rag.md`

Reviewed current records:

- `data/model_affordances/batch_2/adverse-selection.json`
- `data/model_affordances/batch_5/batna.json`
- `data/model_affordances/batch_13/markov-chains.json`
- `data/model_affordances/batch_3a/principal-agent-problem.json`
- `data/model_affordances/batch_2/six-thinking-hats.json`

All five records remain appropriate as one-affordance medium-confidence cards. The source review found additional runtime-useful boundaries, but not transaction-distinct positive affordances.

## Changes

Added two absence guards to `adverse-selection`:

- `post-commitment-incentive-drift-as-adverse-selection`
- `naive-rule-screening-as-adverse-selection-fix`

Reason: adverse selection is source-backed as pre-commitment hidden-type sorting. It should not absorb post-commitment incentive drift, and a screening/filtering recommendation must check whether the screen itself can amplify hidden-information asymmetry, shift risk elsewhere, or confirm prior beliefs.

Also hardened the existing treatment:

- `adverse-selection.verify-hidden-type-selection`
- `specify-filter-before-commitment`

Added two absence guards to `batna`:

- `base-case-fallback-as-batna`
- `reciprocal-competitive-choice-modeling-as-batna`

Reason: BATNA should compare a proposed agreement to an executable fallback under downside and timing pressure, not just the fallback's base case. Reciprocal competitor-move modeling belongs to game theory, not this narrow BATNA card.

Also added two treatment requirements to the existing affordance:

- `stress-test-fallback-downside-before-leverage`
- `separate-fallback-set-before-naming-best-alternative`

Added two absence guards to `markov-chains`:

- `formal-markov-math-or-transition-matrix-affordance`
- `branching-novelty-as-markov-state-path`

Reason: the source supports bounded state-transition simplification, not formal Markov-chain mathematics. It also warns against using the card when branching, novelty, creativity, or optionality exceed transition evidence quality.

Also added one treatment requirement to the existing affordance:

- `stress-transition-chain-against-conjunctive-and-tail-risk`

Added one absence guard to `principal-agent-problem`:

- `single-principal-agent-frame-for-wicked-multi-owner-conflict`

Reason: the source says principal-agent framing fails when there is no clear owner or when multiple owners have conflicting, irreconcilable objectives. A future receiver should route those cases to broader governance, stakeholder, or systems reasoning rather than forcing a clean principal-agent frame.

Also added one treatment requirement to the existing affordance:

- `verify-owner-success-criteria-and-delegation-structure`

Added two absence guards to `six-thinking-hats`:

- `hat-rotation-before-problem-definition`
- `formal-six-hats-taxonomy-or-color-sequence`

Reason: the source supports analogous mode separation, not formal named-method doctrine, color taxonomy, or de Bono-specific sequence. It also warns that ideating while defining problems can anchor later thinking.

Also added one treatment requirement to the existing affordance:

- `define-shared-output-before-mode-rotation`

No positive affordances were added.

## No-Change Findings

No record was split.

For `adverse-selection`, screening, signaling, filtering, pricing, access, and policy all remain one mechanism: pre-commitment hidden-type sorting.

For `batna`, the extra source material improves the fallback test but does not justify turning BATNA into general negotiation strategy, game theory, or decision analysis.

For `markov-chains`, the source supports state-transition reasoning with caveats. It does not support formal stochastic-process depth.

For `principal-agent-problem`, AI agents, conductor/orchestra, consulting, internal cognition, dashboards, incentives, and role clarity are all parts of the same delegated-alignment audit, not separate positive cards.

For `six-thinking-hats`, role prompts, AI advisory boards, dialectic, divergent/convergent sequencing, and perspective rotation all compress into one transaction: mode-separated deliberation before synthesis.

## Compiled Artifact

Compiled:

- `data/compiled/model_affordances/affordances_v32.json`
- `data/compiled/model_affordances/quality_report_v32.md`

v32 metadata:

- contributing records: `222`
- affordances: `268`
- absence records: `486`
- schema validation failures: `0`
- source quote rejections: `0`

Delta from v31:

- model IDs unchanged;
- affordance IDs unchanged;
- absence records increased by `9`;
- five medium-confidence affordances were treatment-hardened without changing affordance count;
- runtime dormancy preserved.

## Quality Rationale

This PR follows the current enrichment rule:

> Add a positive affordance only if it changes downstream use/reject/defer/merge behavior with distinct activation conditions, evidence, treatment, and misuse guards.

The source review did not justify positive expansion. The useful enrichment is negative and procedural:

- block wrong routing;
- make medium-confidence support visibly bounded;
- fold source-backed checks into existing treatments;
- keep future receiver packets from promoting analogous material into full doctrine.

These are absence records and treatment hardenings because they should block, defer, narrow, or require stronger evidence. They are not new positive reasoning recommendations.

## Runtime Boundary

`affordances_v32` is not imported by live runtime paths.

The following remain out of scope:

- changing `engine/system_b/reasoning_substrate_packet.py`;
- changing packet review rendering;
- changing `/lolla` prompts;
- changing lane-to-nomination adapters;
- selecting v32 automatically;
- using this artifact as retrieval or product context.

## Verification

Focused tests:

```bash
pytest tests/test_pr70_v32_medium_supported_guard_enrichment.py tests/test_pr69_v31_weak_support_guard_enrichment.py tests/test_model_affordance_compiler.py tests/test_pr68_v30_broad_reasoning_guard_enrichment.py
```

Additional checks:

```bash
rg -n "affordances_v32|model_affordances_v32" engine scripts tests -g '*.py'
git diff --check
```

Expected runtime scan result:

- only PR70 test references v32;
- no `engine/` or `scripts/` live runtime references v32.
