# Product Delta Evaluation Readiness PRD v0

Status: PRD / phase gate
Date: 2026-07-04

Review artifact:
`reviews/codex-assisted/product-delta-evaluation-readiness-prd-v0/review.json`

## Purpose

This PRD starts the next evaluation phase after Decision Work Sidecar
Automation Readiness v1. Its job is to define how Lolla should build stronger
offline evidence that the revised answer changes the user-facing decision
surface in useful ways, without turning that evidence into product proof,
answer-quality scoring, live LLM judging, or customer-readiness claims.

The immediate recommendation is conservative:

```text
expand offline Product Delta evidence with a balanced batch
before building any live evaluator
```

This PRD does not implement a live evaluator, call providers or models, invoke
the Lolla skill, create new Lolla runs, change runtime behavior, approve agent
use, or create answer-quality labels.

## Current Eval Lanes

The repo already has three serious but deliberately lower-claim eval lanes.

### 1. Product Delta Evidence Lane

The Product Delta lane is the strongest match for comparing what the user
would likely have received without Lolla against what the revised answer does
after Lolla's audit pressure.

Core doctrine and protocol:

- [Product Delta Evidence Thesis](product-delta-evidence-thesis-v0.md)
- [Vanilla-vs-Lolla Provisional Review Protocol](vanilla-vs-lolla-provisional-review-protocol-v0.md)
- [Vanilla-vs-Lolla Provisional Review Schema](vanilla-vs-lolla-provisional-review-v0.json)

Core deterministic tooling:

- [`engine/system_b/product_delta_readiness.py`](../../engine/system_b/product_delta_readiness.py)
- [`scripts/evals/build_product_delta_provisional_review.py`](../../scripts/evals/build_product_delta_provisional_review.py)
- [`engine/system_b/product_delta_boundary_lint.py`](../../engine/system_b/product_delta_boundary_lint.py)
- [`scripts/evals/lint_product_delta_evidence.py`](../../scripts/evals/lint_product_delta_evidence.py)
- [`engine/system_b/product_delta_specialist_packets.py`](../../engine/system_b/product_delta_specialist_packets.py)
- [`scripts/evals/build_product_delta_specialist_packets.py`](../../scripts/evals/build_product_delta_specialist_packets.py)

This lane asks:

- What did the original strong-model answer likely make the user do next?
- What did the Lolla revised answer make more likely?
- Did the delta change action, threshold, sequence, evidence gate, stop rule,
  written term, scope, or user-answerable question?
- Did Lolla add useful friction, noisy friction, lost value, partial leverage,
  or an inconclusive result?
- Did the review surface preserve uncertainty, missingness, and source-depth
  limits?

It is intentionally not a broad "is Lolla better?" judge. Current labels such
as `material_improvement_candidate`, `partial_improvement_candidate`,
`no_material_change_candidate`, `lolla_added_noise_candidate`,
`lolla_worse_candidate`, and `inconclusive` are provisional review reads, not
ground truth.

Important existing signal:

```text
accept-operations-role-startup
material_improvement_candidate -> partial_improvement_candidate
```

That downgrade after specialist decomposition is a positive Product Delta
signal. It shows the machinery can resist flattering Lolla when the broader
read is underspecified and when lost value, value-overwrite risk, ambition, or
written-gate proportionality needs to remain visible.

### 2. Human Review / Answer-Level Eval Lane

The human-review lane is closer to answer-level judgment, but it is explicitly
human-owned review. It is not an automated judge and not an approval system.

Core artifacts:

- [Human Review Workflow](human-review-workflow.md)
- [Lolla Failure Taxonomy](lolla-failure-taxonomy.md)
- [Human Review Schema](lolla-human-review-v0.json)
- [Actionable Delta Rubric](actionable-delta-rubric-v0.md)
- [`engine/system_b/human_review.py`](../../engine/system_b/human_review.py)

This lane can record human review labels such as:

- `revised_answer_improved`
- useful, noisy, and missing friction
- primary failure mode
- severity
- `safe_for_agent_use`

Those labels remain human-review evidence. They must not be treated as an
automated product-proof layer, a runtime approval system, or a guarantee that
advice was correct.

### 3. Review Corpus / Queue Builder

The review-corpus lane prepares local review queues and blank human-review
templates from archived run metadata.

Core implementation:

- [`engine/system_b/review_corpus.py`](../../engine/system_b/review_corpus.py)
- [`scripts/export_review_corpus.py`](../../scripts/export_review_corpus.py)

This lane intentionally summarizes custody and readiness metadata instead of
copying raw conversation text, memo text, revised-answer text, raw model
messages, provider reasoning details, or private control arguments into broad
corpus artifacts.

It prepares reviewable records. It does not evaluate advice quality by itself.

## Current Evidence Boundary

The existing eval system is useful because it is conservative.

It can currently support claims like:

- Product Delta can prepare lower-claim review packets from existing safe
  artifacts.
- Product Delta can ask what changed, whether the change mattered, and where
  the result is partial, noisy, worse, or inconclusive.
- Boundary lint can catch overclaiming and privacy/custody drift.
- Human review can label answer-level improvement when a human reviewer
  inspects the trace and accepts responsibility for the label.
- Review-corpus tooling can prepare local review queues without broad raw
  content copying.

It cannot currently support claims like:

- Lolla reliably improves outputs.
- Product Delta labels are human validation.
- Codex-assisted provisional reads are ground truth.
- A live judge is calibrated.
- Revised answers are correct.
- Agent use is approved without human review.
- Product value has been proven.

The strongest current eval posture is:

```text
serious offline evidence scaffolding exists;
the evidence is not yet broad, balanced, human-calibrated, or product-proof.
```

## Recommended Evidence Milestone

The next milestone should be:

```text
Balanced Offline Product Delta Evidence Batch v0
```

The batch should deliberately include positive, partial, weak, negative, and
ambiguous cases. The goal is not to collect nicer stories about Lolla. The
goal is to learn whether the evaluation path can find its weak spots while
preserving enough structure for later human review.

The batch should include:

- likely no-change cases;
- noisy or worse candidates;
- inconclusive cases;
- lost-user-intent cases;
- cases where Lolla added friction without leverage;
- cases where the vanilla answer was already good enough;
- cases where Lolla improved verification, deferral, or boundaries;
- cases where improvement is partial or ambiguous.

The batch should use existing safe artifacts and local-only review surfaces.
It should not run the live skill, call model/provider APIs, create a live LLM
judge, score answer quality, or claim product proof.

## Why Not A Live Evaluator Next

The next immediate move should not be:

```text
a live evaluator that reads the current conversation and judges the Lolla answer
```

That move combines too many dangerous boundaries at once:

- raw/private text handling;
- provider/model calls;
- answer-quality scoring pressure;
- live judge calibration risk;
- product-proof creep;
- possible action-approval confusion;
- a temptation to convert provisional review language into automated labels.

A live harness may become useful later as a plan-only surface, but only after
offline evidence is broader, includes negative and no-change examples, and has
clearer human-review calibration requirements.

## Roadmap

Recommended follow-on sequence:

| PR | Slice | Purpose |
|---|---|---|
| PR235 | Product Delta Evaluation Readiness PRD v0 | Define this evidence phase and reject a live judge as the immediate move. |
| PR236 | Balanced Offline Evidence Batch Plan v0 | Define the balanced batch shape, candidate classes, refusal rules, and validation. |
| PR237 | Balanced Batch Candidate Selector / Readiness Builder v0 | Build deterministic selection/readiness support for the balanced batch from existing safe artifacts. |
| PR238 | Balanced Batch Provisional Review Run v0 | Run the lower-claim provisional Product Delta pass over the balanced candidate set. |
| PR239 | Negative / No-Change Case Review v0 | Inspect no-change, noisy, worse, lost-intent, and inconclusive candidates specifically. |
| PR240 | Specialist Decomposition Expansion v0 | Expand specialist packets beyond the two-case PR83 slice. |
| PR241 | Fan-In / Disagreement Report Refresh v0 | Refresh disagreement reporting over the broader and more balanced evidence. |
| PR242 | Human Review Calibration Plan v0 | Plan how human review should calibrate, correct, or reject provisional reads. |
| PR243 | Evaluation Evidence Package Gate v0 | Package the offline eval evidence state and non-claims. |
| Optional PR244 | Live Eval Harness Plan v0 | Plan-only live harness discussion after offline evidence is broader. |

The numbers are illustrative for the phase. The required next PR is the
balanced offline batch plan.

## Non-Goals

This phase must not:

- implement a live evaluator;
- call provider/model APIs;
- invoke `$lolla` or the Lolla skill;
- create new Lolla runs;
- create an LLM-as-judge system;
- score answer quality;
- claim product proof;
- claim human validation;
- claim advice correctness;
- approve agent use without human review;
- alter runtime behavior;
- change prompts;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- touch `scripts/archive_run.py`.

## Acceptance Criteria

This PRD is acceptable when it:

- names the existing Product Delta, Human Review, and Review Corpus lanes;
- records the current evidence boundary without overstating it;
- preserves the specialist-review downgrade as a useful anti-flattery signal;
- selects balanced offline evidence before live eval;
- lists positive, partial, no-change, noisy, worse, lost-intent, and
  inconclusive batch targets;
- rejects immediate live conversation judging;
- keeps product proof, answer scoring, human-validation claims, advice
  correctness claims, and agent approval out of scope;
- selects the balanced offline batch plan as the next PR.

## Decision Gate

Gate options:

- `proceed_to_balanced_offline_product_delta_batch_plan`
- `proceed_to_human_review_calibration_plan`
- `proceed_to_live_eval_harness_plan_only`
- `repair_eval_readiness_prd_before_continuing`

Selected gate:

```text
proceed_to_balanced_offline_product_delta_batch_plan
```

Recommended next PR:

```text
Balanced Offline Product Delta Evidence Batch Plan v0
```

That next PR should plan the balanced offline batch only. It should not
implement live judging, model/provider calls, answer-quality scoring, runtime
changes, new Lolla runs, or product-proof claims.

## Implemented Follow-Up

The follow-up plan now exists as
[Balanced Offline Product Delta Evidence Batch Plan](balanced-offline-product-delta-evidence-batch-plan-v0.md).
It defines the balanced batch buckets, source rules, privacy/custody rules,
check-in policy, anti-overclaim rules, and the next candidate-selector plan
gate without selecting actual cases or running Product Delta review.

The next plan-only follow-up now exists as
[Balanced Batch Candidate Selector / Readiness Builder Plan](balanced-batch-candidate-selector-readiness-builder-plan-v0.md).
It defines safe source scopes, allowed selection signals, bucket hypotheses,
readiness criteria, output shape, refusal/defer statuses, and anti-flattery
rules for a future deterministic builder without implementing that builder,
scanning archives broadly, running Product Delta review, calling models,
scoring answers, or claiming product proof.
