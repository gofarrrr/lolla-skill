# PR71 Low Absence Guard Enrichment v33 Report

Status: draft review substrate only.

## Purpose

PR71 continues the post-coverage quality pass by reviewing high-confidence records with unusually thin absence coverage:

- `lindy-effect`
- `premortem`
- `sunk-cost-fallacy`
- `inversion`
- `leverage-points`
- `second-order-thinking`

The goal is a minimum overclaim floor. Strong positive cards can still become dangerous if the receiver sees only the useful move and not the conditions where the card should be rejected, narrowed, or merged.

This is not runtime pickup work. It does not change `/lolla`, prompts, packet production, packet rendering, lane adapters, artifact selection, or any product surface.

## Source Review

Reviewed corpus files:

- `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216/Lindy_Effect_rag.md`
- `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216/Premortem_rag.md`
- `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216/Sunk_Cost_Fallacy_rag.md`
- `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216/Inversion_rag.md`
- `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216/Leverage_Points_rag.md`
- `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216/Second_Order_Thinking_rag.md`

Reviewed current records:

- `data/model_affordances/batch_1/lindy-effect.json`
- `data/model_affordances/pilot/premortem.json`
- `data/model_affordances/batch_1/sunk-cost-fallacy.json`
- `data/model_affordances/pilot/inversion.json`
- `data/model_affordances/batch_1/leverage-points.json`
- `data/model_affordances/pilot/second-order-thinking.json`

All six records remain valid high-confidence cards. The issue was not weak positive extraction. The issue was that several strong records had too little first-class absence display.

## Changes

Added two absence guards to `lindy-effect`:

- `age-as-proof-of-superiority`
- `lindy-for-perishable-or-fast-baseline-break-context`

Reason: Lindy is a durability prior for non-perishable entities, not proof that older is better. It should not fire when age means wear, obsolescence, perishability, or when rapid change breaks the old baseline.

Also hardened the existing affordance:

- added durable relationships/partnerships to activation;
- separated enduring principle from legacy implementation;
- added baseline-breaking alternatives and premortem-style failure paths for major durability commitments.

Added two absence guards to `premortem`:

- `after-commitment-criticism-theater`
- `obvious-worry-list-without-owner-or-plan-change`

Reason: premortem is a pre-commitment plan-improvement tool. It should not become after-the-fact criticism theater or an obvious worry list without owners, mitigations, thresholds, or decision changes.

Also hardened the existing treatment with:

- known/unknown risk triage;
- severe tail/base-case pressure;
- controllable next-step filtering.

Added two absence guards to `sunk-cost-fallacy`:

- `reckless-abandonment-as-anti-sunk-cost-discipline`
- `ordinary-option-comparison-without-prior-investment-pressure`

Reason: anti-sunk-cost reasoning should not become automatic quitting, and sunk-cost routing requires irretrievable prior investment pressure or a pre-commitment need to define exit criteria for a high-cost commitment.

Also hardened the existing treatment with:

- pre-commitment stop/change criteria;
- marginal future value and cash-flow discipline for financial cases;
- future harm and opportunity-cost tracing.

Added one absence guard to `inversion`:

- `avoidance-only-inversion-without-forward-action`

Reason: the source says inversion is incomplete when it identifies what to avoid but never commits to a positive next action.

Added one absence guard to `leverage-points`:

- `preferred-initiative-as-leverage-point-without-mechanism`

Reason: a preferred initiative is not a leverage point until the source-backed system mechanism is proved: feedback loop, bottleneck, governing rule, incentive, flow, or constraint.

Added one absence guard to `second-order-thinking`:

- `speculative-consequence-chain-without-mechanism`

Reason: second-order thinking should not become sophisticated storytelling. Consequence chains need real mechanism, actor reaction, constraint, and evidence anchors.

Also hardened the existing treatment with:

- hidden cost evidence: rework, fragility, lock-in, incentive distortion;
- structure-before-chain evidence;
- action threshold / one-day-answer bound;
- human-system data when implementation depends on actor behavior.

No positive affordances were added.

## Deferred Split Candidates

The source audits surfaced plausible future split candidates, but PR71 deliberately does not take them:

- `inversion`: zero-base continuation test;
- `inversion`: survivor-absence signal;
- `leverage-points`: metric-coupled process lever;
- `leverage-points`: value-driver sensitivity tree;
- `second-order-thinking`: machine-level diagnosis before solution;
- `second-order-thinking`: communication second-order effects.

These may be real. They should be evaluated in a dedicated split-candidate audit, not smuggled into a low-absence guard pass.

The current operating rule still holds:

> Add a positive affordance only if it changes downstream use/reject/defer/merge behavior with distinct activation conditions, evidence, treatment, and misuse guards.

PR71 found enough evidence to record candidates, but not enough reason to mix positive expansion into this PR.

## Compiled Artifact

Compiled:

- `data/compiled/model_affordances/affordances_v33.json`
- `data/compiled/model_affordances/quality_report_v33.md`

v33 metadata:

- contributing records: `222`
- affordances: `268`
- absence records: `495`
- schema validation failures: `0`
- source quote rejections: `0`

Delta from v32:

- model IDs unchanged;
- affordance IDs unchanged;
- absence records increased by `9`;
- low-absence target records now each have at least `2` absence records;
- four positive affordances were treatment-hardened without changing affordance count;
- runtime dormancy preserved.

## Quality Rationale

This PR is intentionally not a richness expansion. It protects strong records from overclaiming:

- Lindy should not become old-is-better reasoning.
- Premortem should not become worry theater.
- Sunk-cost fallacy should not become reckless quitting.
- Inversion should not become avoidance-only paralysis.
- Leverage points should not become preferred-initiative labeling.
- Second-order thinking should not become speculative chain theater.

These rails are first-class absence records because they should block, defer, narrow, or require stronger evidence. They are not new positive reasoning recommendations.

## Runtime Boundary

`affordances_v33` is not imported by live runtime paths.

The following remain out of scope:

- changing `engine/system_b/reasoning_substrate_packet.py`;
- changing packet review rendering;
- changing `/lolla` prompts;
- changing lane-to-nomination adapters;
- selecting v33 automatically;
- using this artifact as retrieval or product context.

## Verification

Focused tests:

```bash
pytest tests/test_pr71_v33_low_absence_guard_enrichment.py tests/test_pr70_v32_medium_supported_guard_enrichment.py tests/test_model_affordance_compiler.py tests/test_pr69_v31_weak_support_guard_enrichment.py
```

Additional checks:

```bash
rg -n "affordances_v33|model_affordances_v33" engine scripts tests -g '*.py'
git diff --check
```

Expected runtime scan result:

- only PR71 test references v33;
- no `engine/` or `scripts/` live runtime references v33.
