# Audit Decision Record Read-Only Exporter v0

Status: PR66 code/tests/docs slice
Date: 2026-06-29
Owner: Lolla maintainers

PR66 implements the narrow read-only exporter selected by the PR65
implementation decision gate.

The exporter builds a conservative `lolla.audit_decision_record.v0` JSON
artifact from an existing Lolla run archive directory. It is meant to give
humans and future agents a compact accountability shell: what run this appears
to be about, which safe structured artifacts exist, what structured fields are
available, what was not measured, and which raw/private content stayed out.

It does not claim the advice is good, safe, correct, domain-approved, or ready
for autonomous use.

## Command Shape

Required run directory and external output:

```bash
python3 scripts/build_audit_decision_record.py \
  --run-dir <run-dir> \
  --out /tmp/lolla_audit_decision_record.json
```

Optional review reference and pretty output:

```bash
python3 scripts/build_audit_decision_record.py \
  --run-dir <run-dir> \
  --review-json <review-json> \
  --out /tmp/lolla_audit_decision_record.json \
  --pretty
```

`--out` is required. The CLI refuses output paths that resolve to the run
directory or inside it, so the exporter does not write into archives.

## Output Contract

Schema version:

```text
lolla.audit_decision_record.v0
```

High-level output fields:

- `schema_version`
- `case_id`
- `run_id`
- `archive_relpath`
- `decision_question`
- `original_recommendation_summary`
- `revised_recommendation_summary`
- `actionable_deltas`
- `conflicts_or_unresolved_tensions`
- `unresolved_questions`
- `source_artifacts`
- `review_refs`
- `custody_flags`
- `limitations`

Semantic fields use conservative states such as `not_measured`, `not_included`,
`artifact_present_only`, `unknown`, or empty arrays when no safe structured
source exists. Empty fields are intentional non-claims, not missing code paths.

## Input Artifacts

The exporter reads only structured/custody-safe JSON surfaces:

- `evaluation.json`
- `agent_result.json`
- `reasoning_trace.json`
- `extraction_adequacy_report.json`
- optional `--review-json`

It may stat but does not semantically read these broader pipeline artifacts:

- `extraction.json`
- `result.json`

For every known source artifact, the output records compact safe metadata:

- artifact name;
- role;
- status: `present`, `missing`, `malformed`, `not_applicable`, or `unknown`;
- relative path only;
- schema version when safely known;
- byte count when safe;
- checksum for structured JSON that was read;
- `raw_content_read: false`.

Malformed optional JSON is reported as `malformed` with a deterministic error
code instead of crashing or guessing.

## Raw Content Exclusion

The exporter does not read or copy raw/private content from:

- `conversation.txt`
- `memo.md`
- `revised.txt`
- `live_transcript.txt`
- provider/model text
- private reasoning artifacts
- private ledger artifacts

If a field cannot be populated without reading excluded content, the exporter
marks that field as `not_measured`, `not_included`, or empty.

## Actionable Deltas

The exporter emits every PR31 actionable-delta bucket as a stable key:

- `action_changed`
- `threshold_changed`
- `sequence_changed`
- `evidence_gate_added`
- `stop_rule_added`
- `written_term_added`
- `user_question_added`
- `scope_narrowed`
- `overclaim_retracted`
- `no_op_prose_change`

PR66 does not infer PR31 labels from prose. Buckets remain empty unless a later
approved safe structured source explicitly supplies them.

## Review References

When `--review-json` is supplied, the exporter records only safe reference
metadata:

- relative file name;
- schema version when present;
- review row count when shaped as a `reviews` array;
- `labels_created: false`;
- `answer_quality_scored: false`;
- `raw_content_included: false`.

It does not copy review notes, create labels, decide `safe_for_agent_use`, or
score answer quality.

## Custody Flags

Generated records keep these flags explicit:

```json
{
  "raw_transcript_included": false,
  "raw_memo_included": false,
  "raw_revised_answer_included": false,
  "provider_text_included": false,
  "private_reasoning_included": false,
  "local_absolute_paths_included": false,
  "secrets_included": false,
  "model_calls": 0,
  "archive_mutated": false
}
```

## Output Path Guard

Blocking output-path failures:

- `--out` equals the run directory;
- `--out` resolves inside the run directory;
- `--out` points to an existing directory.

The CLI writes only the requested external output file. Tests verify that the
archive directory contents are unchanged after a successful CLI run.

## Limitations

Every generated record states that:

- the record is an accountability artifact, not answer-quality scoring;
- it does not approve the recommendation;
- it does not decide `safe_for_agent_use`;
- it does not provide domain approval;
- it may contain empty semantic fields when no safe structured source exists;
- human review remains responsible for judging improvement;
- the exporter does not infer PR31 actionable-delta labels from prose;
- raw transcript, memo, revised answer, provider text, and private reasoning
  artifacts were intentionally not read.

## What PR66 Does Not Do

PR66 does not:

- run `$lolla`;
- call models;
- mutate archives;
- change prompts;
- change `SKILL.md`;
- change runtime pipeline behavior;
- change `caller_action`;
- change provider-boundary policy;
- create high-stakes evidence;
- implement provenance-map, conflict-register, or case-graph exporters;
- add graph DB, embeddings, chunking, memory, GraphRAG, or Semantica-style
  platform work;
- add an LLM judge;
- add answer-quality scoring;
- add automatic PR31 labels;
- add automatic human-review labels;
- decide domain approval;
- decide `safe_for_agent_use`.

## Validation

PR66 validation:

```bash
python3 -m py_compile \
  engine/system_b/audit_decision_record.py \
  scripts/build_audit_decision_record.py \
  tests/test_audit_decision_record.py

PYTHONPATH=. pytest -q tests/test_audit_decision_record.py
```

The tests cover stable schema shape, output-path refusal inside/equal to the
run directory, PR31 bucket stability, raw file non-reading, malformed optional
JSON, missing optional artifacts, custody flags, absence of local absolute
archive paths, safe review references, and external-only CLI writes.

## Next Gate

Stop after PR66.

A possible PR67 should happen only after maintainer review of the PR66 exporter
output and should not be treated as automatic generation, runtime integration,
label population, answer scoring, or archive mutation.
