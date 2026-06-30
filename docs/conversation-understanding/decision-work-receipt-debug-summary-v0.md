# Decision Work Receipt Debug Summary v0

Status: internal read-only renderer slice
Date: 2026-06-30

## Purpose

The Decision Work Receipt Debug Summary turns existing Decision Work Receipt and
Decision Trail JSON into a short Markdown packet that maintainers can read
without opening raw JSON.

It answers:

- What case and run is this?
- Was this one prompt or a real conversation?
- Which Lolla challenge surfaces were visible?
- Is a Decision Trail report linked?
- Which fields can be read from structured artifacts?
- Which fields still require LLM or human interpretation?
- What is missing, private, or redacted?
- What must not be claimed?

It does **not** answer whether the final advice was good.

It also does **not** answer the product question a customer or board member
really cares about:

> What did this audit make me see or do differently?

That requires a separate Decision Work Brief layer. This debug summary is the
receipt appendix underneath that future brief, not the brief itself.

## Usage

```bash
python3 scripts/evals/render_decision_work_receipt_debug_summary.py \
  --receipt /tmp/decision_work_receipt.json \
  --decision-trail-report /tmp/decision_trail_report.json \
  --out /tmp/decision-work-receipt-debug-summary.md
```

The Decision Trail report is optional:

```bash
python3 scripts/evals/render_decision_work_receipt_debug_summary.py \
  --receipt /tmp/decision_work_receipt.json \
  --out /tmp/decision-work-receipt-debug-summary.md
```

## Why This Is Internal

The renderer only reads known safe status/count fields from:

- `lolla.decision_work_receipt.v0`
- optionally `lolla.decision_trail_report.v0`

It does not walk arbitrary report prose and does not copy raw/private content.
This is intentional. The summary is a maintainer-facing explanation of custody
and field status, not a new semantic interpretation pass.

That makes it good for checking whether the archive/report package is coherent.
It makes it weak as a user artifact. A user does not mainly care that a
pressure surface existed; the user cares what changed in the decision, what
trade-off became clearer, what risk remains, and what should not be claimed.

## What This Debug Summary Can Say

The Markdown summary can say:

- the conversation looked one-shot or multi-turn from structured metadata;
- challenge surfaces were visible or not visible;
- safe structured sources were read;
- raw/private sources were present but not exported;
- a Decision Trail report was linked or not supplied;
- some Decision Trail fields are populated from structured artifacts;
- deeper fields still require LLM or human interpretation;
- clean artifacts do not prove good advice.

## What It Must Not Say

The Markdown summary must not say:

- the answer was correct;
- Lolla improved the decision;
- the challenge was sufficient;
- a human validated the result;
- an agent may act;
- clean artifacts are proof of good advice.

## Example

See the checked-in internal example:

- [Launch Public Enterprise Beta Decision Work Receipt Debug Summary](decision-work-receipt-debug-summary-launch-public-enterprise-beta-v0.md)

That example was generated from a real completed archive using temporary
Decision Trail and Work Receipt artifacts in `/tmp`. It is safe because it
contains status, count, and source-shape information only, not raw transcript,
memo, revised-answer, provider, or private ledger content.

## Product Follow-Up

The next product layer should be a Decision Work Brief. It should use bounded
LLM or human interpretation to explain:

- the decision being made;
- the likely starting action;
- what Lolla pressed on;
- what changed in the recommendation, threshold, sequence, evidence gate, or
  scope;
- what the decision-maker would do differently now;
- what remains unresolved;
- what the audit must not claim.

See [Decision Work Brief PRD v0](decision-work-brief-prd-v0.md).

## Boundary

This renderer does not:

- run `$lolla`;
- invoke the Lolla skill;
- call providers or models;
- mutate archives;
- change runtime behavior;
- change prompts;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- copy raw/private content;
- infer messy conversation semantics from prose;
- score answer quality;
- add an LLM judge;
- add automatic labels;
- authorize agent action;
- add graph DB, memory, embeddings, chunking, or GraphRAG.
