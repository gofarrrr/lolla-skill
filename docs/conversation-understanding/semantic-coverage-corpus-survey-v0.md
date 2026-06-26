# Semantic Coverage Corpus Survey v0

PR27 adds a deterministic corpus survey over PR26 semantic coverage reports.

The purpose is to answer whether PR25's semantic-coverage pattern repeats
across archived runs:

- semantic evidence exists, but is often scattered across artifacts;
- live constraints are usually turn-reference grounded rather than
  span-grounded;
- user values or priorities are not first-class in current artifacts;
- assistant stance or recommendation lineage is often artifact-level;
- changed constraints and dropped threads are unevenly represented.

This is evidence gathering before any runtime or IR work.

## What The Exporter Does

The exporter scans an archive root, normally `~/.local/share/lolla/runs`, and
writes:

- JSONL records with schema `lolla.semantic_coverage_corpus_record.v0`;
- an aggregate manifest with schema `lolla.semantic_coverage_corpus_manifest.v0`.

For each archived run, it:

- prefers an existing `semantic_coverage_report.json` if present;
- otherwise builds the PR26 report in memory;
- never writes the report back into the archive;
- emits compact status, grounding, artifact-availability, and review-bucket
  fields.

Example:

```bash
python3 scripts/export_semantic_coverage_corpus.py \
  ~/.local/share/lolla/runs \
  --out /tmp/lolla_semantic_coverage_corpus.jsonl \
  --manifest-out /tmp/lolla_semantic_coverage_corpus_manifest.json
```

## Record Shape

Each record includes:

- `case_id`;
- `run_id`;
- relative `archive_relpath`;
- `valid` and `record_status`;
- whether a semantic coverage report was available or built in memory;
- source scope flags;
- artifact availability summary;
- semantic element statuses;
- semantic element grounding types;
- per-element review-needed flags;
- `needs_review_count`;
- status and grounding count summaries;
- build error categories;
- recommended review bucket.

The recommended review buckets are:

- `modern_semantic_baseline`;
- `semantic_gap_review`;
- `missing_artifacts_review`;
- `legacy_semantic_backfill`;
- `invalid_or_unreadable`.

## Manifest Shape

The manifest includes:

- total, valid, and invalid record counts;
- status counts by semantic element;
- grounding counts by semantic element;
- review-needed counts by semantic element;
- total review-needed count;
- report availability and in-memory build counts;
- missing-artifact counts;
- invalid-JSON artifact counts;
- recommended review bucket counts;
- local-only custody flags.

It does not include the archive root path.

## Privacy And Custody

The corpus export does not copy:

- raw transcript text;
- memo text;
- revised-answer text;
- model messages;
- provider reasoning details;
- failed quote text;
- absolute archive paths;
- control argument values.

The export remains local-only and is marked `shareable_without_review: false`.

## Non-Goals

- no `$lolla` runtime changes;
- no `archive_run.py` integration;
- no normal archive artifact generation yet;
- no prompt changes;
- no model calls;
- no LLM judge;
- no answer-quality score;
- no automatic human-review labels;
- no graph DB;
- no embeddings;
- no chunking;
- no `conversation_understanding_ir.v0`;
- no provider-boundary policy change;
- no `SKILL.md` change.

## Decision Use

PR26 proves the semantic coverage report can describe one run. PR27 asks
whether the pattern repeats across the corpus.

If the corpus shows the same repeated gaps, the next slice can target one
measured missing field or grounding weakness. If the gaps do not repeat, Lolla
should hold and avoid a broad conversation-understanding implementation.
