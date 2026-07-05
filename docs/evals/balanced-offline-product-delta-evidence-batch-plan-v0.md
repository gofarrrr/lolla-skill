# Balanced Offline Product Delta Evidence Batch Plan v0

Status: plan / phase gate
Date: 2026-07-04

Review artifact:
`reviews/codex-assisted/balanced-offline-product-delta-evidence-batch-plan-v0/review.json`

Source PRD:
[Product Delta Evaluation Readiness PRD](product-delta-evaluation-readiness-prd-v0.md)

## Purpose

This plan defines the next offline evidence milestone for Product Delta: a
balanced batch that can challenge Lolla rather than only make it look useful.

The principle is:

```text
The goal is not to prove Lolla is better.
The goal is to build an evidence batch where Lolla can be found useful,
partial, no-change, noisy, worse, or inconclusive.
```

This PR is plan-only. It does not implement candidate selection, run Product
Delta review, call providers or models, invoke the Lolla skill, create new
Lolla runs, create a live evaluator, create an LLM-as-judge system, score
answer quality, claim product proof, claim human validation, validate advice
correctness, approve agent use, or change runtime behavior.

## Existing Infrastructure To Reuse

The balanced batch should build on the current lower-claim eval stack.

Protocol and reports:

- [Product Delta Evidence Thesis](product-delta-evidence-thesis-v0.md)
- [Vanilla-vs-Lolla Provisional Review Protocol](vanilla-vs-lolla-provisional-review-protocol-v0.md)
- [Vanilla-vs-Lolla Provisional Review Schema](vanilla-vs-lolla-provisional-review-v0.json)
- [Product Delta Eval Readiness And Provisional Run](product-delta-eval-readiness-and-provisional-run-v0.md)
- [Codex-Assisted Product Delta Batch](codex-assisted-product-delta-batch-v0.md)
- [Product Delta Provisional Report](product-delta-provisional-report-v0.md)
- [Context-Engineered Provisional Review Architecture](context-engineered-provisional-review-architecture-v0.md)
- [Product Delta Specialist Review Contracts](product-delta-specialist-review-contracts-v0.md)
- [Codex-Assisted Specialist Review Batch](codex-assisted-specialist-review-batch-v0.md)
- [Product Delta Fan-In / Disagreement Report](product-delta-fan-in-disagreement-report-v0.md)
- [Product Delta PR71-PR84 Packaging Gate](product-delta-pr71-pr84-packaging-gate-v0.md)

Human review references:

- [Human Review Workflow](human-review-workflow.md)
- [Lolla Failure Taxonomy](lolla-failure-taxonomy.md)
- [Human Review Schema](lolla-human-review-v0.json)
- [Actionable Delta Rubric](actionable-delta-rubric-v0.md)

Implementation references to mention in the next implementation plan, not
modify here:

- [`engine/system_b/product_delta_readiness.py`](../../engine/system_b/product_delta_readiness.py)
- [`scripts/evals/build_product_delta_provisional_review.py`](../../scripts/evals/build_product_delta_provisional_review.py)
- [`engine/system_b/product_delta_boundary_lint.py`](../../engine/system_b/product_delta_boundary_lint.py)
- [`scripts/evals/lint_product_delta_evidence.py`](../../scripts/evals/lint_product_delta_evidence.py)
- [`engine/system_b/product_delta_specialist_packets.py`](../../engine/system_b/product_delta_specialist_packets.py)
- [`scripts/evals/build_product_delta_specialist_packets.py`](../../scripts/evals/build_product_delta_specialist_packets.py)
- [`engine/system_b/human_review.py`](../../engine/system_b/human_review.py)
- [`engine/system_b/review_corpus.py`](../../engine/system_b/review_corpus.py)
- [`scripts/export_review_corpus.py`](../../scripts/export_review_corpus.py)

## Batch Buckets

The balanced batch should deliberately include these buckets. The next PR may
define exact counts, but every bucket should have at least a candidate-search
rule or explicit absence finding.

| Bucket | Why it matters |
|---|---|
| likely material improvement candidates | Checks whether strong candidate wins still survive balanced selection and later decomposition. |
| partial improvement candidates | Tests whether the eval can avoid inflating partial leverage into material improvement. |
| likely no-change cases | Tests whether the eval can avoid flattering the product when the revised answer changes little or nothing. |
| noisy or worse candidates | Tests whether the eval can find harm, added burden, weaker advice, or decision friction that lacks leverage. |
| inconclusive cases | Tests whether the eval can tolerate uncertainty rather than forcing a positive or negative read. |
| lost-user-intent candidates | Tests whether Lolla preserves the user's actual goals, constraints, and intended action shape. |
| friction without leverage cases | Tests whether Lolla added caution, structure, or process without changing a useful decision variable. |
| vanilla already good enough cases | Tests whether Lolla adds unnecessary friction when the original answer already handled the decision adequately. |
| verification, deferral, boundary, or decision-leverage improvement cases | Preserves the positive target: Lolla may improve verification, delay, boundary-setting, or decision leverage without claiming correctness. |
| overcorrection or user-need drift cases | Tests whether Lolla made useful advice too timid, generic, or misaligned with what the user actually needed. |

The prior `accept-operations-role-startup` downgrade is the reference
anti-flattery example: the eval machinery should be able to lower a candidate
read when specialist decomposition exposes lost value, value-overwrite risk,
ambition, or proportionality uncertainty.

## Candidate Source Rules

The next implementation PR should choose candidates from existing safe
artifacts only. Candidate selection may read deterministic metadata and
checked-in safe eval artifacts, such as:

- existing Product Delta readiness outputs;
- prior provisional review reports;
- review-corpus metadata;
- human-review corpus summaries;
- archived-run metadata when kept local and not copied into checked-in batch
  artifacts;
- existing checked-in review JSON and docs that already passed boundary lint.

The selector plan should not choose cases by reading broad raw conversations
into checked-in artifacts. It should prepare a candidate list with source refs,
bucket hypotheses, readiness status, privacy/custody status, and missingness.

The selector must preserve the possibility that a bucket has too few safe
candidates. A missing bucket is a finding, not permission to fill the gap with
invented semantics.

## Privacy And Custody Rules

The batch plan must keep raw/private material local unless a later approved
workflow explicitly creates a checked-in-safe summary.

Do not check in:

- raw conversation text;
- raw memo text;
- raw revised-answer text;
- raw model/provider text;
- provider reasoning details;
- private ledgers;
- control argument values;
- local absolute private paths;
- secrets;
- live eval outputs;
- broad archive exports.

Checked-in artifacts may include:

- case IDs when already used safely in existing eval docs;
- relative source refs;
- readiness statuses;
- bucket hypotheses;
- compact missingness/custody summaries;
- provisional candidate labels already permitted by the Product Delta protocol;
- explicit non-claims;
- review JSON that contains no raw/private/provider content.

## Batch Output Shape For The Next PR

The next PR should plan, then a later PR may implement, a deterministic
candidate selector/readiness builder that emits a checked-in-safe or temp-only
candidate packet with fields like:

- case ID;
- source refs;
- candidate bucket hypotheses;
- review-readiness status;
- privacy/custody status;
- missing required artifacts;
- prior provisional label when already available;
- known uncertainty;
- operator/human follow-up questions;
- non-claims.

The candidate selector must not run Product Delta review, generate new
semantic interpretations, call models, or decide that Lolla improved a case.
It should route candidates into a future review batch.

## Anti-Overclaim Rules

The balanced batch must preserve these rules:

- no product-proof claims;
- no answer-quality scoring;
- no automatic winner labels;
- no approval or certification language;
- no agent-use approval;
- no advice-correctness claim;
- no claim that Lolla reliably improves outputs;
- no conversion of provisional labels into ground truth;
- no statement that absence of noisy/worse examples proves noisy/worse does
  not happen.

No-change, noisy, worse, inconclusive, and lost-intent outcomes are not
embarrassing. They are the reason to run the batch.

## Follow-On PRs

Recommended follow-on sequence:

1. Balanced Batch Candidate Selector / Readiness Builder Plan v0
2. Balanced Batch Candidate Review v0
3. Balanced Batch Provisional Review Run v0
4. Negative / No-Change Case Review v0
5. Specialist Decomposition Expansion Plan v0
6. Fan-In / Disagreement Report Refresh v0
7. Evaluation Evidence Package Gate v0
8. Optional Live Eval Harness Plan v0, plan-only and later

The next PR should be the candidate selector/readiness builder plan. It should
define how to choose candidate cases safely before any new batch is run.

## Non-Goals

This plan does not:

- implement the batch;
- select actual batch cases beyond selection criteria;
- run Product Delta review;
- call provider/model APIs;
- invoke `$lolla` or the Lolla skill;
- create new Lolla runs;
- create an LLM-as-judge system;
- build a live evaluator;
- score answer quality;
- claim product proof;
- claim human validation;
- claim advice correctness;
- approve agent use;
- change runtime behavior;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- touch `scripts/archive_run.py`.

## Decision Gate

Gate options:

- `proceed_to_balanced_batch_candidate_selector_plan`
- `proceed_to_balanced_batch_candidate_readiness_builder`
- `proceed_to_human_review_calibration_plan`
- `repair_balanced_batch_plan_before_continuing`

Selected gate:

```text
proceed_to_balanced_batch_candidate_selector_plan
```

Recommended next PR:

```text
Balanced Batch Candidate Selector / Readiness Builder Plan v0
```

That next PR should remain a planning slice unless it explicitly gates to a
deterministic selector implementation. It should not run a batch, create a live
judge, call models/providers, run Lolla, score answer quality, or claim
product proof.

## Implemented Follow-Up

The follow-up plan now exists as
[Balanced Batch Candidate Selector / Readiness Builder Plan](balanced-batch-candidate-selector-readiness-builder-plan-v0.md).
It defines safe source scopes, allowed selection signals, candidate bucket
hypotheses, readiness criteria, output shape, refusal/defer statuses, and
anti-flattery rules for a future deterministic selector/readiness builder
without implementing the selector, scanning archives broadly, running Product
Delta review, calling models, creating a live judge, scoring answers, or
claiming product proof.
