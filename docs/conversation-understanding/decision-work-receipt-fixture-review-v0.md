# Decision Work Receipt Fixture Review v0

Status: PR110 fixture review
Date: 2026-06-30
Review fixture:
[Decision Work Receipt fixture review JSON](../../reviews/codex-assisted/decision-work-receipt-fixture-review-v0/review.json)

## Purpose

PR110 reviews the PR109 Decision Work Receipt exporter before adding any new
conversation-interpretation machinery.

The question is not whether Lolla improved a decision. The question is whether
the sparse `lolla.decision_work_receipt.v0` receipt is understandable enough to
show the work trail behind an AI-assisted output without creating false
confidence.

PR110 asks:

- Can a reader tell what inputs and artifacts existed?
- Can a reader distinguish missing from redacted/private from malformed?
- Can a reader tell whether the work was one-shot, multi-turn, challenged, or
  review-ready?
- Can a reader see what still requires LLM or human interpretation?
- Does the receipt make the work more inspectable or merely more impressive?

## Evidence Mode

PR110 uses `checked_in_safe_fixture_review`.

No local-private shadow review was run. PR111 must treat this evidence as
safe-fixture-only. That matters because checked-in safe mode does not read raw
conversation text, raw memo text, raw revised-answer text, provider text,
private ledgers, or local private archive content.

The review can inspect receipt shape, missingness behavior, redaction/private
status, optional reference handling, and overtrust risk. It cannot decide
whether the receipt accurately explains a real messy conversation.

## Inputs

PR110 reviews PR109 exporter behavior using four safe fixture shapes:

- sparse multi-turn fixture;
- challenged fixture with Lolla challenge surfaces;
- review-ready fixture with optional Decision Trail and Product Delta
  references;
- malformed optional-reference fixture.

The generated receipt outputs are not checked in. The exporter tests pin the
generated shape, and PR110 checks in the durable review findings.

Source implementation:

- [Decision Work Receipt PRD](decision-work-receipt-prd-v0.md)
- [Decision Work Receipt Schema](decision-work-receipt-v0.json)
- [Decision Work Receipt Source Inventory](decision-work-receipt-source-inventory-v0.md)
- [Decision Work Receipt Conversation Process Map](decision-work-receipt-conversation-process-map-v0.md)
- [Decision Work Receipt Challenge Coverage Map](decision-work-receipt-challenge-coverage-map-v0.md)
- [Decision Work Receipt Exporter](decision-work-receipt-exporter-v0.md)
- [Decision Work Receipt exporter tests](../../tests/test_decision_work_receipt.py)

## What The Receipt Makes Easier To See

The receipt is useful as a work-trail state shell.

It can show:

- which structured artifacts existed;
- which raw/private artifacts were not read in checked-in safe mode;
- whether the process shape looks one-shot or multi-turn from structured
  metadata;
- whether visible Lolla challenge surfaces exist;
- whether run-health caveats weaken the process evidence;
- whether optional Decision Trail or Product Delta references are present;
- whether optional downstream references are malformed;
- what remains missing or interpretation-needed.

That is the main product win so far. The receipt turns hidden process state into
explicit status.

## What The Receipt Still Fails To Preserve

The receipt still does not explain the messy semantic story users ultimately
care about.

It does not tell us:

- what new context mattered;
- which options were explored or abandoned;
- whether the assistant pushed back or merely agreed;
- whether the challenge changed a real action, threshold, or evidence gate;
- whether useful friction or noisy friction was added;
- what value was lost from the original answer;
- whether Lolla improved the final decision.

Those are LLM or human interpretation questions. Deterministic receipt code
should not guess them from prose.

## Readiness Labels

PR110 finds the readiness labels useful if they remain framed as artifact-state
labels:

- `multi_turn_unreviewed_process`: multi-turn shape is visible, but no challenge
  surfaces or downstream review refs are supplied;
- `challenged_and_revised_process`: challenge surfaces exist, but challenge
  quality is not assessed;
- `decision_trail_review_ready`: Decision Trail or Product Delta references
  exist, but the work is not human reviewed.

The labels become risky if a future UI or agent reads them as approval,
correctness, or quality.

## Overtrust Risk

The strongest overtrust risk is that the receipt can look governed even when the
underlying reasoning is weak.

Three fields need especially careful wording:

- `challenged_and_revised_process`;
- `decision_trail_review_ready`;
- optional Product Delta references.

All three can make a reader feel the work is safer than the evidence supports.
They must stay next to visible non-claims:

- not human validated;
- not product proof;
- not answer-quality scoring;
- not agent authorization;
- clean receipt does not imply good advice.

## PR111 Implication

PR110 pushed PR111 toward a decision gate, not another automatic build step.

PR111 now selects:

> Keep the sparse receipt as useful internal evidence. Do not add a separate
> Work Receipt interpretation system yet.

The fixture review does not justify runtime integration, a broad
conversation-understanding IR, judges, scores, approval labels, or agent action
authorization.

See [Decision Work Receipt Decision Gate v0](decision-work-receipt-decision-gate-v0.md).

## Non-Claims

PR110 does not claim:

- human validation;
- product proof;
- answer-quality scoring;
- Lolla improvement;
- judge calibration;
- automatic labels;
- agent action authorization;
- runtime integration.

Clean fixture review means the receipt shape is coherent enough to inspect. It
does not mean the underlying advice is good.
