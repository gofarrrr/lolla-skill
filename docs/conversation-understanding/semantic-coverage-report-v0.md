# Semantic Coverage Report v0

This note describes the PR26 semantic coverage report.

PR25 found that modern runs preserve quote/capture/turn-reference mechanics,
but important semantic hinges are scattered across `extraction.json`,
`result.json`, `revised.txt`, `memo.md`, `agent_result.json`,
`evaluation.json`, and custody artifacts. PR26 does not make extraction smarter.
It adds an offline report that makes the current artifact coverage visible.

## What It Measures

The report reads one archived run directory and emits JSON with schema:

`lolla.semantic_coverage_report.v0`

It records:

- `run_id`, `case_id`, and relative `archive_relpath`;
- source artifact availability, byte counts, and SHA-256 hashes;
- local-only scope flags;
- deterministic signal counts from existing artifacts;
- coverage for ten semantic elements;
- overall status, grounding, and review-needed counts.

The semantic elements are:

- decision;
- live constraints;
- user values or priorities signal;
- changed constraints or later pushback;
- dropped or under-carried threads;
- assistant stance or recommendation lineage;
- counter-pressure;
- revised-answer change reason;
- unanswered dimensions;
- actionability boundaries.

For each element the report returns:

- `status`: `present`, `partial`, `missing`, or `not_measured`;
- `artifact_owners`: which existing artifacts carry the signal;
- `grounding`: `span`, `turn_ref`, `derivation`, `artifact_present_only`, or
  `none`;
- `evidence_counts`: deterministic counts only;
- `needs_review`: whether human review is still needed;
- `notes`: short custody-safe interpretation.

## What It Does Not Measure

The report does not decide whether the conversation was understood correctly.
It does not score answer quality, agent readiness, or semantic truth.

It also does not copy:

- raw transcript text;
- memo text;
- revised-answer text;
- raw model messages;
- provider reasoning details;
- failed quote text;
- absolute local archive paths.

Hashes, byte counts, artifact names, statuses, grounding types, and counts are
safe enough for local custody review, but the report remains marked
`shareable_without_review: false`.

## Why This Exists After PR25

PR20-PR24 tested the mechanical extraction layer. The modern baseline showed
that quote validation, capture adequacy, and turn references were clean in the
current sample. PR25 then shifted the question:

> Do the artifacts preserve the important reasoning work of the conversation?

The answer was: partly, but not in one compact place. Some evidence lives in
extraction, some in audit cards, some in the revised answer, some in the memo,
and some in agent/evaluation artifacts.

The semantic coverage report is the narrow next step. It does not create a new
semantic representation. It exposes what the current representation already
preserves, weakens, or misses.

## Why This Comes Before `conversation_understanding_ir.v0`

A durable conversation-understanding IR should be justified by repeated,
specific missing fields. PR26 is designed to collect that evidence without
adding runtime cost or changing production behavior.

If the report shows that existing artifacts already preserve enough semantic
evidence, then a new IR may be unnecessary. If it repeatedly shows weak
grounding or missing elements, later work can name the exact fields needed
instead of building a broad memory system by instinct.

## Offline And Local First

The CLI is read-only:

```bash
python3 scripts/build_semantic_coverage_report.py \
  /path/to/archive/run \
  --out /tmp/lolla_semantic_coverage_report.json
```

It reads only existing artifacts and does not mutate the archive. Missing
optional artifacts degrade element statuses instead of crashing. Invalid input
or output paths return a deterministic nonzero error.

PR26 intentionally does not add `semantic_coverage_report.json` to normal
`$lolla` archives yet. Integration should wait until the offline report proves
useful on real archives.

## Non-Goals

- no `$lolla` runtime changes;
- no `archive_run.py` integration;
- no reasoning-trace or evaluation integration yet;
- no prompt changes;
- no model calls;
- no LLM judge;
- no answer-quality scoring;
- no automatic human-review labels;
- no graph DB;
- no embeddings;
- no chunking;
- no `conversation_understanding_ir.v0`;
- no provider-boundary policy change;
- no `SKILL.md` change.
