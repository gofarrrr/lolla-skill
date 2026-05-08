# PR87 Meta-Reasoning Absence Hardening v49 Report

Date: 2026-05-08

## Scope

PR87 continues the dormant model-affordance enrichment track. It does not wire
affordances into `/lolla`, prompts, lane adapters, packet rendering, or runtime
pickup.

The audit target was the broad meta-reasoning/context-engineering ring:
chain-of-thought, chain-of-verification, reasoning-mode-router,
meta-cognitive-reflection, latticework of mental models, mental models of
reality, System 1, System 2, cognitive gaps assessment, formal reasoning,
logical fallacies, and dialectical reasoning.

The operating question was not "can these sources say more?" They can. The
stricter question was: would a separate positive affordance change the future
receiver transaction enough to justify another identity, or would it merely
make broad reasoning vocabulary look more authoritative?

## Source-Read Verdict

The ring produced zero positive split candidates and five absence-rail
hardening candidates.

Positive splits:

- None.

Absence rails:

- `latticework-of-mental-models.surface-model-familiarity-as-expertise`
- `mental-models-of-reality.high-level-abstraction-without-mechanism-threshold-or-protocol`
- `system-2.pseudo-deliberation-as-system-2`
- `system-2.depleted-deliberation-window-as-reliable-audit`
- `system-2.over-deliberation-overrides-validated-expert-intuition`

Compression/no-change decisions:

- `chain-of-thought` remains one affordance. The source supports disciplined
  stepwise decomposition, but its key runtime danger is confidence theater.
  That danger is already carried by the existing anti-overclaim shape rather
  than by a separate positive card.
- `chain-of-verification` remains one affordance. Its transaction is already
  the verification pass: check generated claims against explicit evidence,
  expose assumptions, and avoid treating fluent reasoning as proof.
- `reasoning-mode-router` remains one affordance. Splitting by every possible
  mode would create router theater unless future packet stress shows distinct
  use/reject/defer decisions.
- `meta-cognitive-reflection` remains one affordance. It is useful as process
  audit, but the source does not justify extra runtime cards for introspection
  language.
- `latticework-of-mental-models` remains one affordance. The source supports a
  small, pruned model set translated into tests. It does not support surface
  model familiarity as expertise.
- `mental-models-of-reality` remains one affordance. The source supports
  testing maps against predictions, explanations, and actions. It does not
  support elegant abstraction without mechanism, threshold, or protocol.
- `System 1` remains one affordance. Its transaction is recognition of fast,
  fluent pattern generation with explicit boundaries.
- `System 2` remains one affordance. The useful change was guarding three
  false promotions: pseudo-deliberation, depleted deliberation windows, and
  over-deliberation that overrides calibrated expert intuition.
- `cognitive-gaps-assessment`, `formal-reasoning`, `logical-fallacies`, and
  `dialectical-reasoning` remain compressed. Their current cards are already
  transaction-shaped enough for candidate packets.

## What Changed

### Latticework of Mental Models

PR87 added `surface-model-familiarity-as-expertise` as an absence rail. The
source says the latticework is not a substitute for expertise and explicitly
warns against surface-level model familiarity as cargo-cult thinking.

Receiver implication:

- Use the card only when multiple models become concrete tests, comparisons,
  or decision pressures.
- Do not promote model-name familiarity as operational mastery.

### Mental Models of Reality

PR87 added `high-level-abstraction-without-mechanism-threshold-or-protocol` as
an absence rail. The source is strongest when a mental model improves
prediction, explanation, or action guidance; it warns against abstractions that
feel explanatory but do not create operational consequences.

Receiver implication:

- Use the card when a map can be tested against reality.
- Do not promote an elegant abstraction unless it names a mechanism, threshold,
  protocol, measurement, or decision consequence.

### System 2

PR87 added three absence rails:

- `pseudo-deliberation-as-system-2`
- `depleted-deliberation-window-as-reliable-audit`
- `over-deliberation-overrides-validated-expert-intuition`

The source treats System 2 as expensive audit infrastructure, not as a magic
label for correct reasoning. A review memo, rubric, or meeting is not reliable
deliberation if the conclusion was already formed by System 1. Deliberation is
also capacity-limited and can degrade under fatigue, time pressure, or excessive
override of stable expert intuition.

Receiver implication:

- Use the card when novelty, asymmetry, calibration, or logical validity makes
  deliberate audit worth its cost.
- Do not promote formal process as proof of genuine deliberation.
- Do not promote depleted late-stage deliberation as reliable audit.
- Do not force deliberative override where calibrated expert intuition is the
  better tool.

## v49 Compile Result

Artifact: `model_affordances_v49`

- Status: `draft_review_only`
- Records: `222`
- Affordances: `293`
- Absence records: `567`
- Schema-validation failures: `0`
- Source-quote rejections: `0`
- Source-hash failures: `0`

Delta from v48:

- Affordances: `+0`
- Absence records: `+5`
- Runtime references: none

## Quality Interpretation

PR87 is intentionally anti-bloat. The most important result is that rich
meta-reasoning sources were not converted into extra positive cards merely
because they contain many useful ideas. Broad cards are especially likely to
become reasoning theater, so the right move was to strengthen their negative
boundaries where the source explicitly supports that boundary.

This ring supports the larger substrate plan in three ways:

- It preserves the principle that affordance splits require downstream
  transaction identity, not source richness alone.
- It strengthens absence records as first-class anti-overclaim material.
- It keeps broad meta-cards from presenting model vocabulary, abstraction, or
  formal deliberation as judgment.

## Critic Verdict

Verdict: PASS as dormant reviewed substrate; REVISE before runtime pickup.

Contradicting evidence first:

- Broad reasoning cards still carry packet-risk even when their records are
  clean. A future renderer could hide the decisive absence rail while showing
  the positive card.
- The current dormant packet shape is still too lossy for affordance-level
  transaction ledgers. PR87 does not solve that packaging problem.
- A one-affordance broad card can still crowd out narrower cards under caps if
  packet policy later treats broad cards as intrinsically more strategic.

What would falsify this PR87 decision:

- Static packet stress shows that `latticework-of-mental-models`,
  `mental-models-of-reality`, or `system-2` need multiple separate
  use/reject/defer decisions that cannot be represented by the current card plus
  absence rails.
- Future archived-case review shows that the added absence rails do not change
  receiver behavior.
- Broad meta-cards keep winning packet space without case-specific evidence
  despite these absence rails.

Minimum changes before runtime pickup remain outside PR87:

- Explicit artifact selection with no latest-file magic.
- Confidence visibility in the receiver handoff.
- Weak-support warning visibility.
- Absence visibility strong enough to block overclaiming.
- Grouped affordance identity if the future receiver needs per-affordance
  use/reject/defer ledgers.
- Lane provenance mapping that does not flatten user, assistant, and structural
  evidence into one generic reason.

## Validation

Focused validation should cover:

- edited records validate against schema and exact source quotes;
- v49 preserves all 222 model IDs from v48;
- v49 adds no positive affordance IDs;
- v49 adds only the five expected absence fields;
- audited broad reasoning records remain compressed;
- v49 is not referenced by live runtime paths.

Focused command:

```bash
PYTHONPATH=. pytest tests/test_pr87_v49_meta_reasoning_absence_hardening.py tests/test_pr86_v48_reasoning_debiasing_enrichment.py tests/test_model_affordance_compiler.py
```

## Runtime Boundary

This PR remains dormant substrate work. It does not:

- change packet producer defaults;
- add a lane-to-nomination adapter;
- import v49 from engine or scripts;
- change prompts or receiver rubrics;
- alter `/lolla` behavior.

Future packet-stress work should continue to ask whether grouped affordance
identity, confidence visibility, weak-support warnings, broad-card cap behavior,
and absence display are strong enough before any live pickup experiment.
