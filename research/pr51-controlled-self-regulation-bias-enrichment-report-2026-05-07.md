# PR51 Controlled Self-Regulation Bias Enrichment Report

**Status:** controlled source-backed extraction; no runtime, prompt, lane,
judge, UI, memo, `/lolla`, Batch 3b, deterministic pressure selection,
deterministic psychological diagnosis, or user-facing output.

**PR slice:** PR51 - controlled self-regulation / bias-calibration enrichment

**Decision label:** `controlled_self_regulation_bias_enrichment_ready`

## Why This Batch

After PR50, the reviewed corpus covered 170 of the 222 runtime models and 52
runtime models remained source-custodied graph-only.

The next useful gap was self-regulation and bias calibration. Future packets
will often need to help a later LLM reason about confidence, defensiveness,
post-hoc stories, audience understanding, hindsight, agency, follow-through,
motivation, persistence, mindset, and regret without turning psychology labels
into accusations or deterministic diagnosis.

PR51 executes a bounded 12-model batch. It does not try to finish the remaining
52 in one broad pass.

## Target Models

| Model | Source file | Selection reason | Outcome |
| --- | --- | --- | --- |
| `cognitive-biases` | `Cognitive_Biases_rag.md` | General debiasing process when no narrower reviewed card is clearly dominant. | `strong_affordance_record` |
| `cognitive-dissonance` | `Cognitive_Dissonance_rag.md` | Commitment, identity threat, and belief-revision pressure. | `strong_affordance_record` |
| `rationalization` | `Rationalization_rag.md` | Stated rationale versus actual driver and falsification discipline. | `strong_affordance_record` |
| `dunning-kruger-effect` | `Dunning_Kruger_Effect_rag.md` | Confidence/fluency versus objective competence calibration. | `strong_affordance_record` |
| `curse-of-knowledge` | `Curse_of_Knowledge_rag.md` | Expert-to-audience scaffolding and teach-back checks. | `strong_affordance_record` |
| `hindsight-bias` | `Hindsight_Bias_rag.md` | Post-outcome review discipline and process/outcome separation. | `strong_affordance_record` |
| `internal-locus-of-control` | `Internal_Locus_Of_Control_rag.md` | Controllable-lever ownership without denying constraints. | `strong_affordance_record` |
| `self-control` | `Self_Control_rag.md` | Follow-through system design instead of willpower moralizing. | `strong_affordance_record` |
| `self-determination-theory` | `Self_Determination_Theory_rag.md` | Motivation architecture across autonomy, competence, and relatedness. | `strong_affordance_record` |
| `growth-mindset` | `Growth_Mindset_rag.md` | Feedback-driven capability growth with constraint honesty. | `strong_affordance_record` |
| `persistence-grit` | `Persistence_Grit_rag.md` | Sustained effort paired with progress evidence and stop rules. | `strong_affordance_record` |
| `regret-theory` | `Regret_Theory_rag.md` | Long-run values regret with probability and reversibility checks. | `strong_affordance_record` |

## Extraction Result

PR51 adds exactly:

- 12 reviewed Batch 14 records;
- 12 compact reviewed affordances;
- 24 absence records;
- 0 runtime references;
- 0 prompt, lane, live adapter, packet, memo, UI, or `/lolla` changes.

v15 compiled artifact:

- path: `data/compiled/model_affordances/affordances_v15.json`;
- status: `draft_review_only`;
- artifact id: `model_affordances_v15`;
- reviewed model records: 182;
- reviewed affordances: 218;
- absence records: 349;
- remaining graph-only runtime models: 40;
- schema validation failures: 0;
- source quote rejections: 0.

## What Got Stronger

PR51 gives future reasoning packets better handoff material for:

- symmetric debiasing checks instead of bias-label theater;
- commitment and identity-pressure review before escalation;
- rationale-versus-driver testing when arguments are cleaner than evidence;
- objective calibration before trusting confidence or fluency;
- audience-starting-state reconstruction and teach-back verification;
- predecision records before postmortem lessons;
- controllable-lever mapping without self-blame or constraint denial;
- follow-through design around triggers, habits, rest, and environment;
- motivation architecture across autonomy, competence, relatedness, and standards;
- feedback-loop design for genuinely expandable capability;
- persistence with progress metrics, stop rules, and pivot criteria;
- regret as a long-run values signal only when paired with risk work.

## Absences Matter

The absence records intentionally block tempting but unsupported uses:

- bias lists as diagnosis;
- bias labels as proof;
- discomfort as proof of error;
- attitude-change claims without commitment evidence;
- confidence as competence;
- Dunning-Kruger as dismissal;
- expert clarity as audience clarity;
- audience confusion as inattention;
- known outcomes as foreseeable;
- postmortems without prior-state documentation;
- control as total responsibility;
- agency without constraint mapping;
- willpower as a moral trait;
- restraint without environment design;
- motivation as reward size;
- autonomy without competence and relatedness;
- effort as guarantee;
- mindset as substitute for feedback;
- persistence as unconditional virtue;
- grit without stop condition;
- regret as universal decision rule;
- anticipated regret without probability.

These absences are not failures. They keep future packets from overclaiming
psychological certainty.

## Quality Notes

- The batch keeps psychological models as source-backed reasoning material, not
  deterministic diagnosis of a person or team.
- `cognitive-biases` is intentionally broad; it should support general
  debiasing process only when a narrower reviewed bias card is not the better
  shelf.
- `regret-theory` is bounded to high-stakes, values-loaded, hard-to-revisit
  decisions and explicitly blocked from routine operational choices.
- No record uses regex or heading parsing as semantic extraction. The fields are
  reviewer-normalized from source reading and exact source quotes.

## Guardrails Preserved

PR51 adds no:

- live `/lolla`;
- prompt changes;
- lane rewrites;
- live lane adapter;
- runtime packet production;
- v15 runtime promotion;
- model calls;
- judges;
- Batch 3b;
- Observatory, memo, Step 8, Step 6, or Lane 4 runtime wiring;
- user-facing Decision Pressure;
- deterministic final pressure selection;
- deterministic psychological diagnosis.

## Verification

Passed:

```bash
PYTHONPATH=. pytest tests/test_pr51_batch14_records.py
```

Result: 9 passed.

v15 shape:

```text
model_affordances_v15 draft_review_only 182 40
218 349 0 0
```

## Recommendation For PR52

Continue toward full 222 coverage with another capped, source-backed family
from the remaining 40 graph-only models. Keep the current operating rule:

> direct source reading, one compact operational affordance where supported,
> absence records where the source does not support tempting claims, draft-only
> compilation, and no runtime or prompt promotion.

Likely next families should be selected from the remaining graph-only set.
Candidate directions include:

- economic / market-structure reasoning;
- cultural and organizational interpretation;
- meta-model hygiene and System 1/System 2 cleanup;
- product, UX, and narrative communication support.

PR52 should pick one coherent family, cap it, extract only source-supported
depth, and keep the same no-runtime boundary.
