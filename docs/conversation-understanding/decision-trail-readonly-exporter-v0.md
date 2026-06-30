# Decision Trail Read-Only Exporter v0

Status: PR87 implementation note
Date: 2026-06-29
Schema: `lolla.decision_trail_report.v0`

## Purpose

PR87 implements a deterministic read-only exporter for the PR86 Decision Trail
report contract.

The exporter produces a sparse but honest `lolla.decision_trail_report.v0`
JSON report from one completed Lolla run directory. It is an offline
reader/reporting tool over existing artifacts. It is not runtime integration
and it does not create new interpretation.

## Files

PR87 adds:

- `engine/system_b/decision_trail_report.py`
- `scripts/evals/build_decision_trail_report.py`
- `tests/test_decision_trail_report.py`
- `docs/conversation-understanding/decision-trail-readonly-exporter-v0.md`

The exporter targets the PR86 schema:

- `docs/conversation-understanding/decision-trail-report-v0.json`

## CLI

Run the exporter against an existing archived run directory and an explicit
output path outside that run directory:

```bash
python3 scripts/evals/build_decision_trail_report.py \
  --run-dir <archive-run-dir> \
  --out /tmp/decision_trail_report.json \
  --pretty
```

PR87 implements `checked_in_safe_mode` only. The CLI accepts `--report-mode`,
but `local_private_mode` and `future_runtime_mode_not_implemented` are rejected
as deferred modes.

The output path is refused if it resolves inside the run directory. The exporter
writes JSON only to the requested path.

## What It Reads

In `checked_in_safe_mode`, the exporter reads structured JSON artifacts only:

- `evaluation.json`
- `agent_result.json`
- `reasoning_trace.json`
- `extraction_adequacy_report.json`
- `extraction.json`
- `result.json`

For each structured artifact, it records status, source status, schema version,
byte count, hash, relative path, activity kind, and whether content was copied
into the report.

## What It Does Not Read

In `checked_in_safe_mode`, the exporter records presence/redaction status for
the following artifacts without reading their content:

- `conversation.txt`
- `memo.md`
- `revised.txt`
- `live_transcript.txt`
- `operator.log`
- private table files
- private ledgers

Existing raw artifacts are reported as
`available_but_redacted_in_safe_mode` or
`available_in_private_artifact_not_exported`, not as missing. Missing artifacts
are separately reported as `unavailable_missing_artifact`.

## Populated Fields

The exporter may populate fields only from safe structured artifacts:

- report metadata from `agent_result.json`, `evaluation.json`,
  `reasoning_trace.json`, or the run directory shape;
- source artifact status and artifact health deterministically;
- custody flags and non-claims deterministically;
- decision question from `extraction.json` or `reasoning_trace.json`;
- conversation-understanding presence/count summary from `extraction.json`;
- constraints from `extraction.json` when `live_constraints` are structured;
- audit pressure summary from `agent_result.json` or `result.json` when a
  compact structured field exists;
- structural delta from `agent_result.json` `changed_advice_summary` and
  `take_backs`;
- unresolved questions from `agent_result.json` `human_questions`;
- future-compatible trace context from `reasoning_trace.json` metadata.

When the exporter copies a structured field, it sets
`exporter_inferred_from_prose: false` and records `source_refs`.

## Not Populated In PR87

The exporter intentionally leaves the following fields empty with explicit
`requires_llm_interpretation` status unless a later safe structured review
artifact supplies them:

- vanilla likely next action;
- revised likely next action;
- option map and option status;
- stakeholders;
- values or priorities;
- assistant influence;
- useful versus noisy friction;
- lost value.

These are messy interpretation fields. Deterministic code must not infer them
from raw conversation, memo, revised-answer, or arbitrary prose fields.

## Missingness And Redaction

PR87 preserves the PR86 distinction between:

- `unavailable_missing_artifact`;
- `unavailable_malformed_artifact`;
- `not_supplied`;
- `requires_llm_interpretation`;
- `available_but_redacted_in_safe_mode`;
- `available_in_private_artifact_not_exported`.

Every semantic section includes `empty_meaning`, `source_status`,
`source_refs`, `owner`, `requires_llm_interpretation`, and
`exporter_inferred_from_prose`.

## Boundary

PR87 does not:

- run `$lolla`;
- invoke the Lolla skill;
- call providers or models;
- mutate archives;
- change runtime behavior;
- change prompts;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- add model calls;
- add a judge;
- add answer-quality scoring;
- add automatic labels;
- add an agent-readiness authorization field;
- add graph DB, memory, embeddings, chunking, or GraphRAG;
- claim product proof;
- treat clean artifacts as proof of good advice.

Custody flags preserve:

- `model_calls: 0`;
- `archive_mutated: false`;
- `runtime_invoked: false`;
- `skill_invoked: false`;
- `human_validated: false`;
- `product_proof: false`;
- `answer_quality_scored: false`;
- `automatic_labels_created: false`;
- `agent_action_authorized: false`.

## Validation

PR87 adds focused tests for:

- schema version stability;
- checked-in-safe structured-artifact reading only;
- raw artifact non-reading;
- output path rejection inside the run directory;
- missing and malformed structured artifact status handling;
- false/zero custody flags;
- no deterministic inference of messy semantic fields;
- redaction/private-availability statuses distinct from missingness;
- semantic-section `empty_meaning`;
- future-compatible trace context with no external dependency;
- CLI write behavior;
- Product Delta boundary lint over generated safe JSON.

Passing tests and lint validate exporter boundary hygiene. They do not prove the
Decision Trail report is useful enough as a product surface.

## Next Step

PR88 is recorded in
[Decision Trail Export Fixture Review v0](decision-trail-export-fixture-review-v0.md).

It found the exporter output useful as a custody and missingness shell, but too
sparse for the full Decision Trail product without later bounded interpretation
or human review. The next recommended slice is PR89: Conversation
Interpretation Gap Decision v0.
