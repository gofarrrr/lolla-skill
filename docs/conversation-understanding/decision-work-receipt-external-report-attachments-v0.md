# Decision Work Receipt External Report Attachments v0

Status: PR112 read-only bridge slice
Date: 2026-06-30

## Purpose

PR112 adds a narrow bridge between the sparse Decision Work Receipt and the
offline Decision Trail/Product Delta artifacts that are normally generated
outside archive run folders.

The trigger was the real-run smoke after PR111:

- completed Lolla archives had good process and challenge evidence;
- the Work Receipt could identify them as challenged-and-revised processes;
- optional Decision Trail and Product Delta summaries stayed `not_supplied`
  because those artifacts are offline outputs, not archive sidecars.

That is a concrete reopen condition from
[Decision Work Receipt Decision Gate v0](decision-work-receipt-decision-gate-v0.md):
downstream Decision Trail/Product Delta artifacts can become hard to locate
without a receipt wrapper.

PR112 does **not** add a new interpretation system. It lets an operator pass
already-generated checked-in-safe report JSON files into the receipt CLI, so
the receipt can link those reports by safe structured metadata.

## Usage

```bash
python3 scripts/evals/build_decision_work_receipt.py \
  --run-dir <archive-run-dir> \
  --decision-trail-report /tmp/decision_trail_report.json \
  --product-delta-report /tmp/product_delta_report.json \
  --out /tmp/decision_work_receipt.json \
  --pretty
```

Both report flags may be repeated.

The output path must still be outside the run directory.

## What Gets Included

The receipt records:

- a sanitized external report artifact name;
- source kind: `decision_trail_report` or `product_delta_artifact`;
- status such as `available_from_structured_artifact`,
  `unavailable_missing_artifact`, or `unavailable_malformed_artifact`;
- read status;
- hash and byte count for readable structured JSON;
- source refs for the linked summary.

The receipt does **not** include:

- the local absolute report path;
- raw transcript text;
- raw memo text;
- revised-answer text;
- provider text;
- private ledgers;
- full Decision Trail report content;
- full Product Delta review content;
- semantic conclusions copied from the reports.

The linked summaries remain references, not verdicts.

## Readiness Meaning

If a Decision Trail or Product Delta report reference is available, the receipt
may classify the process as:

```text
decision_trail_review_ready
```

That means:

> The work trail has a linked review/custody artifact that can help a reviewer
> inspect the process.

It does **not** mean:

- the answer is correct;
- Lolla improved the decision;
- the linked report is human validated;
- the linked report is product proof;
- an agent may act.

## Why This Is Not A Parallel System

PR112 keeps the Work Receipt role narrow:

- Work Receipt: wraps source inventory, process shape, challenge coverage,
  linked report availability, missingness, and non-claims.
- Decision Trail: owns bounded conversation/process interpretation when such
  interpretation exists.
- Product Delta: owns provisional comparison of vanilla versus Lolla output.

The Work Receipt now knows how to point at those artifacts. It does not replace
them and does not interpret their messy fields.

## Boundary

PR112 does not:

- run `$lolla`;
- invoke the Lolla skill;
- call providers or models;
- mutate archives;
- change runtime behavior;
- change prompts;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- read raw/private run content in checked-in safe mode;
- copy report conclusions into the receipt;
- infer messy conversation semantics from prose;
- score answer quality;
- add an LLM judge;
- add automatic labels;
- authorize agent action;
- add graph DB, memory, embeddings, chunking, or GraphRAG.

## Validation Focus

PR112 tests should prove:

- external Decision Trail and Product Delta paths can be supplied to the
  builder and CLI;
- external report local paths are not copied into the receipt;
- report content is not copied into the receipt;
- linked summaries become available from structured artifacts;
- missing external paths become explicit artifact status, not crashes;
- readiness may rise to `decision_trail_review_ready` without human validation
  or answer-quality scoring;
- generated receipts continue to pass boundary lint.
