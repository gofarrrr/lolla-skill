# PR68 Broad Reasoning Guard Enrichment v30 Report

Status: draft review substrate only.

## Purpose

PR68 continues the post-coverage quality pass by hardening broad reasoning cards against "reasoning theater" pickup:

- `chain-of-thought` should not be promoted when an elaborate stepwise chain hides the core variable or suppresses a better nonlinear leap;
- `chain-of-verification` should not be promoted when verification steps merely confirm prior steps without disconfirmation pressure;
- `reasoning-mode-router` should not be promoted when the route is captured by the first frame, favored tool, familiar label, or high-status template.
- `latticework-of-mental-models` should surface pruning pressure, not just model breadth;
- `mental-models-of-reality` should not fire on every actor/prospect/persona inference case;
- `meta-cognitive-reflection` should not be foregrounded when the case lacks cognitive quiet or action budget.

This is not runtime pickup work. It does not change `/lolla`, prompts, packet production, renderer behavior, lane adapters, or artifact selection.

## Source Review

Reviewed corpus files:

- `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216/Chain_Of_Thought_rag.md`
- `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216/Chain_Of_Verification_rag.md`
- `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216/Reasoning_Mode_Router_rag.md`
- `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216/Latticework_Of_Mental_Models_rag.md`
- `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216/Mental_Models_of_Reality_rag.md`
- `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216/Meta_Cognitive_Reflection_rag.md`

Reviewed current records:

- `data/model_affordances/batch_17/chain-of-thought.json`
- `data/model_affordances/batch_4/chain-of-verification.json`
- `data/model_affordances/batch_10/reasoning-mode-router.json`
- `data/model_affordances/batch_17/latticework-of-mental-models.json`
- `data/model_affordances/batch_17/mental-models-of-reality.json`
- `data/model_affordances/batch_17/meta-cognitive-reflection.json`

## Changes

Added one absence guard to `chain-of-thought`:

- `elaborate-stepwise-chain-when-core-variable-or-nonlinear-leap-is-needed`

Reason: the source supports stepwise decomposition when it exposes weak links. It does not support elaborate chain-of-thought when sequential decomposition suppresses a better nonlinear leap, obscures the one or two variables that actually drive the outcome, or increases cognitive load without changing the decision.

Added one absence guard to `chain-of-verification`:

- `confirmation-only-verification-chain`

Reason: the source supports verification only when links are genuinely tested, including disconfirming evidence. It does not support a verification chain whose steps unconsciously confirm the initial hypothesis or protect prior links.

Added one absence guard to `reasoning-mode-router`:

- `anchored-or-template-captured-mode-selection`

Reason: the source requires context-driven mode selection and switching as evidence changes. It does not support routing when the first framing, favored tool, familiar label, or high-status template keeps control despite contradictory evidence.

Also merged that same guard into the first positive treatment path:

- `reasoning-mode-router.context-driven-mode-selection-check`
- `name-stage-and-mode-fit`

Reason: if packet display only surfaces one detail field, the most common routing failure should still be visible in the positive card: the answer must show that the selected mode is not merely the first frame, familiar label, favored tool, or high-status template.

Added one treatment requirement to `latticework-of-mental-models`:

- `cap-and-prune-model-set`

Reason: the source supports testing several model cuts, pruning dead-end analyses, and avoiding cognitive overload. For broad-card pickup, this must be visible as a treatment requirement, not only as an absence warning.

Added one absence guard to `mental-models-of-reality`:

- `actor-mental-model-inference`

Reason: the source contains actor/prospect/persona mental-map material, but that should not make the broad `mental-models-of-reality` card fire on every stakeholder, sales, audience, or counterpart case. Route or merge to narrower empathy, understanding-motivations, mental-simulation, UX, communication, or persuasion records unless a later pass proves a narrow predictive actor-map affordance with explicit boundaries.

Added one absence guard to `meta-cognitive-reflection`:

- `reflection-without-cognitive-quiet-or-action-budget`

Reason: the source says focused reflection requires cognitive quiet and mental effort. This creates a distinct defer condition when stress, heightened emotion, sustained execution, or timely relational response makes introspective monitoring too costly.

No positive affordances were added.

## No-Change Findings

No positive affordance was added for `latticework-of-mental-models`, `mental-models-of-reality`, or `meta-cognitive-reflection`.

Their current positive records remain the right transaction identities:

- latticework remains cross-checking causal layers with multiple models;
- mental models of reality remains comparing frame to territory;
- meta-cognitive reflection remains checking thinking before adding motion.

The extra source material improved treatment and absence surfaces but did not justify new transaction-distinct cards.

## Compiled Artifact

Compiled:

- `data/compiled/model_affordances/affordances_v30.json`
- `data/compiled/model_affordances/quality_report_v30.md`

v30 metadata:

- contributing records: `222`
- affordances: `268`
- absence records: `474`
- schema validation failures: `0`
- source quote rejections: `0`

Delta from v29:

- model IDs unchanged;
- affordance IDs unchanged;
- absence records increased by `5`;
- two positive affordances were treatment-hardened without changing affordance count;
- runtime dormancy preserved.

## Quality Rationale

This PR follows the current enrichment rule:

> Add a positive affordance only if it changes downstream use/reject/defer/merge behavior with distinct activation conditions, evidence, treatment, and misuse guards.

The source review did not justify positive expansion. The value is in preventing high-status reasoning vocabulary from being treated as judgment:

- a chain can look rigorous while hiding the wrong variable;
- verification can look rigorous while only confirming itself;
- mode routing can look sophisticated while anchored by the first frame.
- latticework can look wise while becoming a model pile;
- actor mental-map inference can over-route a narrow stakeholder case into a broad reality-map card;
- reflection can sound responsible while the context cannot pay the cognitive cost.

These are absence records and treatment hardenings because they should block, defer, merge, or prune pickup. They are not new positive reasoning recommendations.

## Runtime Boundary

`affordances_v30` is not imported by live runtime paths.

The following remain out of scope:

- changing `engine/system_b/reasoning_substrate_packet.py`;
- changing packet review rendering;
- changing `/lolla` prompts;
- changing lane-to-nomination adapters;
- selecting v30 automatically;
- using this artifact as retrieval or product context.

## Verification

Focused tests:

```bash
pytest tests/test_pr68_v30_broad_reasoning_guard_enrichment.py tests/test_model_affordance_compiler.py tests/test_pr67_v29_reversibility_guard_enrichment.py tests/test_pr66_v28_broad_system_guard_enrichment.py tests/test_pr65_v27_decision_method_guard_enrichment.py
```

Additional checks:

```bash
rg -n "affordances_v30|model_affordances_v30" engine scripts tests -g '*.py'
git diff --check
```

Expected runtime scan result:

- only PR68 test references v30;
- no `engine/` or `scripts/` live runtime references v30.
