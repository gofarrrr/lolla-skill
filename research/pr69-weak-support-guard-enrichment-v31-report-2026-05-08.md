# PR69 Weak Support Guard Enrichment v31 Report

Status: draft review substrate only.

## Purpose

PR69 continues the post-coverage quality pass by hardening the two remaining `weak_support` records before any future packet pickup:

- `devops-and-continuous-integration`
- `price-discrimination`

The goal is not to make weak records look stronger. The goal is the opposite: preserve the value of their narrow source-backed cards while making overpromotion harder.

This is not runtime pickup work. It does not change `/lolla`, prompts, packet production, packet rendering, lane adapters, artifact selection, or any product surface.

## Source Review

Reviewed corpus files:

- `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216/Devops_and_Continuous_Integration_rag.md`
- `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216/Price_Discrimination_rag.md`

Reviewed current records:

- `data/model_affordances/batch_8/devops-and-continuous-integration.json`
- `data/model_affordances/batch_16/price-discrimination.json`

Both sources explain why the current records are weak support:

- `Devops_and_Continuous_Integration_rag.md` says DevOps and Continuous Integration is not explicitly defined in the provided source material. The useful material is adjacent systems, iteration, disciplined problem solving, and continuous learning.
- `Price_Discrimination_rag.md` says the term Price Discrimination is not found in the sources. The useful material is adjacent differentiated-offer, buyer-understanding, persuasion, segmentation, and trust-risk material.

That means neither source justifies a full positive doctrine expansion.

## Changes

Added one absence guard to `devops-and-continuous-integration`:

- `abstract-continuous-improvement-as-devops-ci`

Reason: the source supports adjacent operating-loop material, but also says good problem solving cannot be done in the abstract and requires field knowledge. This weak-support card should not be promoted when a case merely contains generic systems thinking, iteration, or continuous improvement language without a concrete delivery system or integration loop.

Also added one treatment requirement to the existing affordance:

- `verify-concrete-delivery-system-before-use`

Reason: if a future packet displays only one or two details, the card itself should still tell the receiver that the support is adjacent and must stay at operating-loop level unless stronger DevOps/CI evidence is available.

Added two absence guards to `price-discrimination`:

- `persona-or-archetype-as-willingness-to-pay-proof`
- `formal-economics-or-legal-price-discrimination-doctrine`

Reason: the source uses persona, archetype, and buyer-psychology material as guides, but the pricing card requires willingness-to-pay, urgency, risk, or use-case evidence. It also does not provide formal economics, legal, regulatory, or market-power doctrine. Those uses require a stronger source.

Also added one treatment requirement to the existing affordance:

- `anchor-offer-differences-against-comparison-and-limits`

Reason: the source asks "Compared to what?" and recommends transparent treatment of lower-tier limits and risks. That belongs inside the existing segmented-offer affordance as a treatment hardening, not as a new positive card.

No positive affordances were added.

## No-Change Findings

No second positive affordance was added for either record.

For `devops-and-continuous-integration`, the source contains many adjacent mental-model and problem-solving ideas, but they do not become transaction-distinct DevOps/CI affordances. The current positive card remains the right narrow identity: build, observe, diagnose, adjust, and protect reliability.

For `price-discrimination`, the source contains differentiated persuasion, feature-to-benefit conversion, comparison framing, archetype language, and risk transparency. Those details improve the treatment of the current segmented-offer affordance, but they do not justify a separate formal price-discrimination doctrine or manipulative buyer-psychology card.

## Compiled Artifact

Compiled:

- `data/compiled/model_affordances/affordances_v31.json`
- `data/compiled/model_affordances/quality_report_v31.md`

v31 metadata:

- contributing records: `222`
- affordances: `268`
- absence records: `477`
- schema validation failures: `0`
- source quote rejections: `0`

Delta from v30:

- model IDs unchanged;
- affordance IDs unchanged;
- absence records increased by `3`;
- two weak-support positive affordances were treatment-hardened without changing affordance count;
- runtime dormancy preserved.

## Quality Rationale

This PR follows the current enrichment rule:

> Add a positive affordance only if it changes downstream use/reject/defer/merge behavior with distinct activation conditions, evidence, treatment, and misuse guards.

The source review did not justify positive expansion. The value is in making weak-support cards harder to misuse after future nomination:

- DevOps/CI should not become generic continuous-improvement advice.
- Price discrimination should not become persona-based pricing guesswork.
- Price discrimination should not become formal economics, legal, or market-power doctrine.

These are absence records and treatment hardenings because they should block, defer, narrow, or require stronger evidence. They are not new positive reasoning recommendations.

## Runtime Boundary

`affordances_v31` is not imported by live runtime paths.

The following remain out of scope:

- changing `engine/system_b/reasoning_substrate_packet.py`;
- changing packet review rendering;
- changing `/lolla` prompts;
- changing lane-to-nomination adapters;
- selecting v31 automatically;
- using this artifact as retrieval or product context.

## Verification

Focused tests:

```bash
pytest tests/test_pr69_v31_weak_support_guard_enrichment.py tests/test_model_affordance_compiler.py tests/test_pr68_v30_broad_reasoning_guard_enrichment.py tests/test_pr67_v29_reversibility_guard_enrichment.py
```

Additional checks:

```bash
rg -n "affordances_v31|model_affordances_v31" engine scripts tests -g '*.py'
git diff --check
```

Expected runtime scan result:

- only PR69 test references v31;
- no `engine/` or `scripts/` live runtime references v31.
