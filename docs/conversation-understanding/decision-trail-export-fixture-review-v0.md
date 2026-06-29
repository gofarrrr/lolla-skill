# Decision Trail Export Fixture Review v0

Status: PR88 fixture review
Date: 2026-06-29
Review fixture:
[Decision Trail fixture review JSON](../../reviews/codex-assisted/decision-trail-fixture-review-v0/review.json)

## Purpose

PR88 reviews the PR87 Decision Trail exporter surface before any new
conversation-interpretation machinery is added.

The question is not whether Lolla improved a decision. The question is whether
the sparse `lolla.decision_trail_report.v0` report is understandable enough to
serve as an answer-plus-process receipt without creating false confidence.

PR88 asks:

- Which fields populate from current structured artifacts?
- Which fields stay missing or require later LLM interpretation?
- Are redacted/private-available sources clearly different from missing ones?
- Can a reviewer see what changed, what supports it, what is missing, and what
  must not be claimed?
- Does the report make the reader more careful, or merely more impressed?

## Evidence Mode

PR88 uses `checked_in_safe_fixture_review`.

No local-private shadow review was run. PR89 must treat this evidence as
safe-fixture-only. That matters because checked-in safe mode does not read raw
conversation text, raw memo text, raw revised-answer text, provider text,
private ledgers, or local private archive content. The review can inspect the
report shape and missingness behavior, but it cannot decide semantic adequacy
for a real messy conversation.

## Inputs

PR88 reviews the PR87 exporter behavior using safe fixture-style reports:

- a structured fixture report with readable structured artifacts;
- a sparse fixture report with missing structured artifacts.

The fixture review records findings in JSON rather than checking in bulky
generated report output. The PR87 exporter tests continue to pin the report
shape directly.

Source implementation:

- [Decision Trail Report PRD](decision-trail-report-prd-v0.md)
- [Decision Trail Report Schema](decision-trail-report-v0.json)
- [Decision Trail Read-Only Exporter](decision-trail-readonly-exporter-v0.md)
- [Decision Trail exporter tests](../../tests/test_decision_trail_report.py)

## What The Reports Make Easier To See

The structured fixture makes artifact custody legible. A reviewer can see that
the report was built from structured JSON artifacts, that raw/private artifacts
were not read, and that the exporter records explicit custody flags rather than
quietly implying runtime activity.

The structured fixture also makes the first useful Decision Trail spine visible:

- decision question;
- conversation-understanding presence counts;
- live constraints when supplied structurally;
- audit pressure summary;
- structural delta;
- unresolved human questions;
- trace/custody compatibility.

This is useful, with a caveat: it is process visibility, not human validation
and not product proof.

## What The Reports Fail To Preserve

The sparse areas are the load-bearing product areas:

- vanilla likely next action;
- revised likely next action;
- live options and option status;
- stakeholders;
- values or priorities;
- assistant influence;
- useful versus noisy friction;
- lost value.

PR87 correctly marks these as requiring interpretation rather than filling them
deterministically. PR88 therefore finds the exporter boundary healthy, but the
report incomplete for the full customer-facing Decision Trail vision.

## Overtrust Risk

The main overtrust risk is the `structural_delta` section. When it is populated
from `agent_result.json`, it can make the report feel like it explains what
Lolla improved. It does not. It only records structured change material that an
existing artifact supplied.

The report is safest when the reader treats populated fields as custody/source
evidence and treats missing interpretive fields as first-class gaps.

## Redaction Versus Missingness

PR88 finds the distinction useful:

- missing structured artifacts are represented as missing or malformed;
- raw/private artifacts that exist in checked-in safe mode are represented as
  redacted or private-available;
- empty semantic fields include empty meanings.

That distinction prevents a reviewer from reading an empty field as a negative
semantic finding.

## Behavioral Read

For the structured fixture:

- what changed is partly answerable from `structural_delta`;
- what supports the change is answerable at the source-ref level;
- what is missing is clear;
- what must not be claimed is clear if the non-claims are read;
- the report makes the reviewer more careful rather than merely impressed.

For the sparse fixture:

- what changed is not answerable;
- artifact missingness is easy to see;
- the report is useful mainly as a diagnostic shell;
- no product or semantic read should be made from it.

## PR89 Implication

PR88 should push PR89 toward this decision:

> The PR87 exporter is useful as a custody and missingness shell, but the full
> Decision Trail product needs bounded LLM-backed interpretation for the messy
> fields before it can explain the decision process users care about.

That does not mean build a giant conversation-understanding platform. It means
PR89 should decide whether the next move is narrow offline specialist
enrichment, local-private review, simplification, or a pause.

## Non-Claims

PR88 does not claim:

- human validation;
- product proof;
- answer-quality scoring;
- Lolla improvement;
- judge calibration;
- automatic labels;
- agent action authorization;
- runtime integration.

Clean fixture review means the report shape is coherent enough to inspect. It
does not mean the underlying advice is good.
