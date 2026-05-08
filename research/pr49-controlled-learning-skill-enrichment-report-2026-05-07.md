# PR49 Controlled Learning And Skill Enrichment Report

**Date:** 2026-05-07
**PR slice:** PR49 - controlled learning / skill-acquisition enrichment
**Status:** controlled reviewed extraction; no runtime, prompt, lane, model-call,
judge, UI, memo, `/lolla`, Batch 3b, deterministic mastery classification, or
user-facing surface
**Decision label:** `controlled_learning_skill_enrichment_ready`

## Purpose

After PR48, the reviewed corpus covered 146 of the 222 runtime models and 76
runtime models remained graph-only. The user explicitly approved continuing
controlled extraction toward the full 222-model set, while keeping the quality
standard source-backed and nuance-driven.

PR49 executes the next bounded family:

> learning, pedagogy, and skill-acquisition discipline.

The goal is not to fill fields mechanically. The goal is to read 12
source-custodied files, extract one compact operational affordance where the
source supports it, and record absences where tempting learning vocabulary
would overclaim.

## Source And Artifact Scope

Inputs:

- `data/knowledge_graph.json`
- `data/model_sources/manifest.json`
- `data/model_sources/`
- `data/compiled/model_affordances/affordances_v12.json`
- `references/model-affordance-extraction.md`
- `data/schemas/model_affordance.schema.json`

Outputs:

- `data/model_affordances/batch_12/`
- `data/compiled/model_affordances/affordances_v13.json`
- `data/compiled/model_affordances/quality_report_v13.md`
- `tests/test_pr49_batch12_records.py`

Compiled v13 shape:

| Measure | Count / state |
| --- | ---: |
| Reviewed records | 158 |
| Reviewed affordances | 194 |
| Absence records | 301 |
| Schema validation failures | 0 |
| Source quote rejections | 0 |
| Runtime graph models still graph-only after v13 | 64 |
| Status | `draft_review_only` |

v13 is not runtime-promoted.

## Target Models

PR49 extracted exactly 12 learning / skill-acquisition models:

| Model ID | Source file | Outcome | Affordances | Absences | Why selected |
| --- | --- | --- | ---: | ---: | --- |
| `blooms-taxonomy` | `Blooms_Taxonomy_rag.md` | `strong_affordance_record` | 1 | 2 | Diagnoses current mastery layer before asking for higher-order work. |
| `cognitive-load-theory` | `Cognitive_Load_Theory_rag.md` | `strong_affordance_record` | 1 | 2 | Reduces avoidable load while preserving decision-critical cues. |
| `deliberate-practice` | `Deliberate_Practice_rag.md` | `strong_affordance_record` | 1 | 2 | Turns vague improvement into specific reps, feedback, and transfer checks. |
| `desirable-difficulties` | `Desirable_Difficulties_rag.md` | `strong_affordance_record` | 1 | 2 | Separates productive struggle from needless friction or overload. |
| `expertise-reversal-effect` | `Expertise_Reversal_Effect_rag.md` | `strong_affordance_record` | 1 | 2 | Matches support level to novice/expert state without status shortcuts. |
| `feynman-technique` | `Feynman_Technique_rag.md` | `strong_affordance_record` | 1 | 2 | Uses plain-language explanation to expose and repair gaps. |
| `generation-effect` | `Generation_Effect_rag.md` | `strong_affordance_record` | 1 | 2 | Requires active articulation plus calibration, not passive agreement. |
| `learning-curve` | `Learning_Curve_rag.md` | `strong_affordance_record` | 1 | 2 | Measures capability compounding without treating progress as automatic. |
| `scaffolding` | `Scaffolding_rag.md` | `strong_affordance_record` | 1 | 2 | Provides temporary support with an explicit fade plan. |
| `schema-acquisition` | `Schema_Acquisition_rag.md` | `strong_affordance_record` | 1 | 2 | Builds usable patterns while checking against the real case. |
| `varied-practice-interleaving` | `Varied_Practice_Interleaving_rag.md` | `strong_affordance_record` | 1 | 2 | Tests contrasting frames before commitment, then prunes. |
| `zone-of-development` | `Zone_Of_Development_rag.md` | `strong_affordance_record` | 1 | 2 | Calibrates the next reachable stretch with support and feedback. |

## Extraction Read

The sources were strong enough for one compact affordance per model. The common
depth pattern is:

- diagnose current capability instead of prescribing generic learning;
- match challenge, support, and cognitive load to the actual learner state;
- require retrieval, feedback, measurement, or transfer evidence;
- prevent smooth explanations, familiar schemas, or early progress from
  masquerading as mastery;
- include explicit fade, calibration, or pruning conditions so learning
  methods do not become ritual.

This is useful depth because future packets often need to decide whether advice
is teachable, learnable, transferable, or executable by the actual person or
team. These cards make that reasoning more concrete without asking Python to
choose the final answer.

## Absence Records

The 24 absence records block tempting overclaims such as:

- taxonomy labels as learning;
- simplification that erases causal distinctions;
- repetition without feedback;
- difficulty as virtue;
- status-labeled expertise;
- smooth explanation as mastery;
- generation without calibration;
- progress without measurement;
- permanent scaffolding;
- schema labels replacing reality;
- interleaving as random variety;
- unsupported challenge as growth.

Absence is useful here. It prevents learning models from turning into
encouraging but weak advice.

## Quality Notes

What felt strong:

- The sources consistently contain activation conditions and misuse guards.
- Learning models produce especially clear "do not overclaim" boundaries.
- Exact source custody was sufficient for every reviewed quote.
- The family adds operational depth around capability, support, transfer, and
  feedback rather than motivational language.

What stayed narrow:

- PR49 does not decide whether a user should learn, teach, delegate, hire, or
  stop.
- PR49 does not create deterministic mastery classification.
- PR49 does not convert learning theory into prompt mechanics.
- PR49 does not test a packet. It continues extraction under explicit user
  approval to move toward full coverage.

## Guardrails Preserved

PR49 adds no:

- live `/lolla`;
- prompt changes;
- lane rewrites;
- live lane adapter;
- runtime packet production;
- v13 runtime promotion;
- model calls;
- judges;
- Batch 3b;
- Observatory, memo, Step 8, Step 6, or Lane 4 runtime wiring;
- user-facing Decision Pressure;
- deterministic final pressure selection;
- deterministic mastery classification.

Python validated quote custody, schema shape, counts, compilation, and dormant
runtime boundaries. It did not decide wisdom.

## Recommendation For PR50

Continue controlled extraction toward the full 222-model set, but keep the
batch discipline:

- 8-12 models per family;
- direct source reading;
- one strong affordance preferred over many weak ones;
- absence records welcomed;
- compile only as `draft_review_only`;
- periodic packet usefulness review after several extraction families or when a
  family is likely to affect handoff shape.

The next remaining family should be selected from the 64 graph-only models
after v13, not by broad completion pressure alone.
