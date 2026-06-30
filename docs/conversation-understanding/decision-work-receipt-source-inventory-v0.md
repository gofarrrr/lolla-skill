# Decision Work Receipt Source Inventory v0

Status: PR106 read-only exporter slice
Date: 2026-06-30
Schema: `lolla.decision_work_receipt.v0`

## Purpose

PR106 implements the first Decision Work Receipt exporter.

The slice is intentionally narrow:

> Build a deterministic source/context inventory over a completed Lolla run
> directory, then emit a sparse `lolla.decision_work_receipt.v0` receipt.

It does not try to tell the full work story yet. It records what source
artifacts exist, which are missing, which are redacted/private in checked-in
safe mode, and which later receipt fields still need interpretation.

## Files

- `engine/system_b/decision_work_receipt.py`
- `scripts/evals/build_decision_work_receipt.py`
- `tests/test_decision_work_receipt.py`
- `docs/conversation-understanding/decision-work-receipt-source-inventory-v0.md`

## Usage

```bash
python3 scripts/evals/build_decision_work_receipt.py \
  --run-dir <archive-run-dir> \
  --out /tmp/decision_work_receipt.json \
  --pretty
```

The output path must be outside the run directory.

PR106 implements `checked_in_safe_mode` only. Other modes are rejected with a
sanitized error.

## What It Reads

In checked-in safe mode, the exporter reads safe structured JSON artifacts such
as:

- `evaluation.json`
- `agent_result.json`
- `reasoning_trace.json`
- `extraction_adequacy_report.json`
- `extraction.json`
- `result.json`

It also records selected generated runtime artifacts when present:

- `memo_note.json`
- `gapcheck_lanes.json`
- `run_events.json`
- `control_result.json`
- `graph_survival_report.json`

For raw/private artifacts, the exporter records existence and byte count, but
does not read content:

- `conversation.txt`
- `memo.md`
- `revised.txt`
- `live_transcript.txt`
- `operator.log`
- private ledgers and private tables

## What It Does Not Read

PR106 does not read raw/private text in checked-in safe mode.

It does not read:

- raw conversation text;
- raw memo text;
- raw revised-answer text;
- live transcript text;
- provider text;
- private ledger content;
- private table content;
- local absolute paths.

## Attachment / PDF Constraint

PDFs, uploaded files, and external links are not first-class archived source
objects today.

If PDF text was pasted into the conversation, the current runtime may preserve
that text inside `conversation.txt`, but PR106 does not read raw conversation
content in checked-in safe mode.

If a PDF was only referenced externally and not archived by the runtime, PR106
cannot prove its contents were available or used.

The receipt records this as an attachment-custody limitation rather than
pretending to solve it.

## What The Receipt Contains

PR106 emits a complete but sparse `lolla.decision_work_receipt.v0` object.

Populated:

- `receipt_metadata`
- `source_context_inventory`
- `missingness_and_redaction`
- `human_review`
- `non_claims`
- `boundary`

Explicitly sparse or not measured in PR106:

- `challenge_coverage`
- `decision_trail_summary`
- `product_delta_summary`

The sparse sections are not failures. They mark the boundary between source
custody and later interpretation work.

PR107 now populates the deterministic part of `conversation_process_map` when
safe structured turn or capture metadata is available. See
[Decision Work Receipt Conversation Process Map v0](decision-work-receipt-conversation-process-map-v0.md).

PR108 now populates `challenge_coverage` when safe structured challenge-surface
artifacts are available. See
[Decision Work Receipt Challenge Coverage Map v0](decision-work-receipt-challenge-coverage-map-v0.md).

PR109 now composes the sparse receipt shell and links optional Decision
Trail/Product Delta references when checked-in-safe report artifacts are
present. See
[Decision Work Receipt Exporter v0](decision-work-receipt-exporter-v0.md).

## Boundary

PR106 does not:

- run `$lolla`;
- invoke the Lolla skill;
- call providers or models;
- mutate archives;
- change runtime behavior;
- change prompts;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- parse raw conversation in checked-in safe mode;
- infer PDF or file usage from prose;
- infer conversation process events;
- score answer quality;
- add an LLM judge;
- add automatic labels;
- authorize agent action;
- add graph DB, memory, embeddings, chunking, or GraphRAG.

## Current Meaning

A clean PR106 receipt means:

- the run directory can be inspected read-only;
- the exporter can identify source/context artifacts;
- missing, redacted, private, and malformed source states are explicit;
- attachment/PDF custody gaps are visible;
- later interpretation fields are not guessed.

It does not mean:

- the final answer is good;
- Lolla improved the decision;
- the work process was deep;
- the conversation was fully interpreted;
- an agent may act on the result.

## Follow-Up Slice

The first follow-up slice is now implemented:

```text
PR107 Conversation Process Map Shell v0
```

- [Decision Work Receipt Conversation Process Map v0](decision-work-receipt-conversation-process-map-v0.md)

It adds deterministic process metadata, such as turn count and one-shot versus
multi-turn evidence status where safe structured data allows it. It still
avoids semantic interpretation from prose.

The second follow-up slice is also implemented:

```text
PR108 Challenge Coverage Map v0
```

- [Decision Work Receipt Challenge Coverage Map v0](decision-work-receipt-challenge-coverage-map-v0.md)

It maps which Lolla challenge surfaces and run-health caveats are visible from
structured artifacts. It still does not score lane quality or answer quality.

The third follow-up slice is also implemented:

```text
PR109 Decision Work Receipt Exporter v0
```

- [Decision Work Receipt Exporter v0](decision-work-receipt-exporter-v0.md)

It composes source inventory, process metadata, challenge coverage, optional
Decision Trail references, optional Product Delta references, readiness labels,
missingness, non-claims, and boundary flags into the first sparse work-trail
receipt.
