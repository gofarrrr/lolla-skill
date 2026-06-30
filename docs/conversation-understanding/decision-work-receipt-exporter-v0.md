# Decision Work Receipt Exporter v0

Status: PR109 read-only exporter slice
Date: 2026-06-30
Schema: `lolla.decision_work_receipt.v0`

## Purpose

PR109 composes the first sparse Decision Work Receipt from the pieces built in
PR106 through PR108.

The receipt answers a practical product question:

> What evidence do we have about the work trail behind this AI-assisted output?

It does not answer whether the final answer was correct, whether Lolla improved
the decision, or whether a human or agent should act.

## What It Composes

The exporter now combines:

- source/context inventory from safe structured artifacts;
- raw/private source availability without reading raw/private content;
- deterministic conversation-process metadata such as turn counts and process
  depth;
- challenge-surface coverage and run-health caveats;
- optional Decision Trail report references when a checked-in-safe report JSON
  is present next to the run;
- optional Product Delta review/report references when a checked-in-safe review
  JSON is present next to the run;
- process-evidence readiness;
- missingness, redaction/private availability, human-review state, non-claims,
  and boundary flags.

This makes the receipt a single work-trail shell instead of separate fragments.

## Usage

```bash
python3 scripts/evals/build_decision_work_receipt.py \
  --run-dir <archive-run-dir> \
  --out /tmp/decision_work_receipt.json \
  --pretty
```

The output path must be outside the run directory.

PR109 still implements `checked_in_safe_mode` only. Local-private receipt mode
and future runtime integration remain deferred.

## Optional Report References

PR109 may notice these optional checked-in-safe JSON artifacts if they are
present in the run directory:

- `decision_trail_report.json`
- `decision_trail_report.v0.json`
- `product_delta_review.json`
- `product_delta_report.json`
- `product_delta_provisional_review.json`

These are optional references. If they are absent, the receipt records
`not_supplied` in the linked summary sections rather than treating the run as
broken. This matters because Decision Trail and Product Delta reports are
usually generated outside archive run folders.

When optional references are present, the exporter records their existence and
safe structured metadata. It does not copy full report content, review
conclusions, raw transcript text, raw memo text, revised-answer text, provider
text, private tables, private ledgers, or local absolute paths.

## Process Evidence Readiness

PR109 updates `process_evidence_readiness.label` as an artifact-readiness
classification:

- `insufficient_process_evidence`: no useful structured process metadata was
  available;
- `one_shot_or_thin_process`: available metadata looks like one user prompt and
  one assistant answer;
- `multi_turn_unreviewed_process`: multi-turn evidence exists, but no core
  Lolla challenge surfaces are visible;
- `challenged_and_revised_process`: core Lolla challenge surfaces are visible;
- `decision_trail_review_ready`: a Decision Trail or Product Delta reference is
  present, making the receipt more ready for review.

These labels are deliberately humble. They classify visible work-trail evidence,
not the quality of the advice.

## What Remains Semantic

PR109 still does not interpret messy conversation meaning.

These remain LLM or human interpretation tasks:

- whether new context changed the decision;
- which live options were considered or abandoned;
- whether the assistant pushed back or merely agreed;
- whether the final answer lost useful momentum or user-specific ambition;
- whether challenge surfaces were actually useful;
- whether Lolla improved the decision.

The deterministic exporter keeps those gaps visible. It does not fill them by
guessing from prose.

## Boundary

PR109 does not:

- run `$lolla`;
- invoke the Lolla skill;
- call providers or models;
- mutate archives;
- change runtime behavior;
- change prompts;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- read raw/private content in checked-in safe mode;
- infer messy conversation semantics from prose;
- score answer quality;
- add an LLM judge;
- add automatic labels;
- authorize agent action;
- add graph DB, memory, embeddings, chunking, or GraphRAG.

## Current Meaning

A clean PR109 receipt means:

- the run can be inspected read-only;
- available source/context artifacts are visible;
- one-shot versus multi-turn process metadata is visible when structured
  capture metadata supports it;
- visible Lolla challenge surfaces are mapped;
- optional Decision Trail/Product Delta references can be linked;
- missingness and redaction/private availability are explicit;
- the receipt says what still needs LLM or human interpretation.

It does not mean:

- the answer is correct;
- the work was good;
- Lolla improved the decision;
- the final memo is safe to rely on;
- an agent may act.

## Next Slice

The next planned slice is:

```text
PR110 Decision Work Receipt Fixture Review v0
```

That review should ask whether the PR109 receipt is useful, too thin, too
confusing, or too authoritative-looking before any new interpretation machinery
is added.
