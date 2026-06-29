# Audit Decision Record Schema / Exporter Refinement v0

Status: PR68 code/tests/docs slice
Date: 2026-06-29
Owner: Lolla maintainers

PR68 refines the PR66 read-only audit decision record exporter after the PR67
smoke review found one narrow readability issue: empty PR31 buckets were safe
but only partly clear as "not supplied / not inferred" non-claims.

This slice keeps the schema version:

```text
lolla.audit_decision_record.v0
```

It does not make the exporter smarter. It makes absence more legible.

## What Changed

The exporter now emits explicit population metadata for PR31 actionable deltas:

- `actionable_deltas.population_policy`
- `actionable_deltas.bucket_status`
- `actionable_deltas.buckets`

The `buckets` object still carries the stable PR31 label keys. The new
`bucket_status` object tells readers why a bucket is empty or populated.

Default minimal exports use:

```json
{
  "bucket_status": {
    "action_changed": "not_supplied"
  },
  "buckets": {
    "action_changed": []
  }
}
```

That means the exporter did not receive a safe structured label source. It does
not mean the audited answer had no meaningful action change.

The population policy now states that:

- human review owns PR31 label population;
- the exporter does not infer PR31 labels from prose;
- a label source is required before buckets are populated;
- empty arrays are non-claims unless a bucket is explicitly marked
  `measured_empty`.

## Bucket Status Vocabulary

PR68 defines these bucket status values:

- `not_supplied`
- `not_measured`
- `measured_empty`
- `populated_from_review`
- `populated_from_structured_artifact`
- `unavailable_missing_artifact`
- `unavailable_malformed_artifact`

The default is `not_supplied`. If an optional review JSON supplies explicit
safe `actionable_deltas` data, the affected bucket can be marked
`populated_from_review`. The exporter still does not create labels or infer
them from revised-answer prose.

## Semantic Field Statuses

PR68 also removes bare ambiguous semantic arrays from generated output.

Generated records now give these fields explicit population metadata:

- `decision_question`
- `original_recommendation_summary`
- `revised_recommendation_summary`
- `conflicts_or_unresolved_tensions`
- `unresolved_questions`

For scalar fields, generated records include status, source refs when
available, and `exporter_inferred_from_prose: false`.

For semantic arrays, generated records now use an object with:

- `status`
- `items`
- `empty_meaning`
- `owner`
- `exporter_inferred_from_prose`

For example:

```json
{
  "status": "not_supplied",
  "items": [],
  "empty_meaning": "not supplied to exporter; not evidence that no conflicts or unresolved tensions exist",
  "owner": "human_review",
  "exporter_inferred_from_prose": false
}
```

This preserves the PR67 review finding: absence should be visible as absence,
not mistaken for a negative semantic finding.

## Review JSON Behavior

The optional `--review-json` reference still records safe review metadata:

- relative file name;
- schema version;
- review row count when available;
- no labels created by the exporter;
- no answer-quality scoring;
- no raw content copied.

PR68 adds one narrow explicit-source path: if the review JSON contains a safe
structured `actionable_deltas.buckets` object with PR31 labels and item
summaries, those items can populate matching buckets as
`populated_from_review`.

The exporter does not copy review notes, does not create labels, and does not
infer labels from prose.

## Non-Goals Preserved

PR68 does not:

- run `$lolla`;
- call models;
- mutate archives;
- change prompts;
- change `SKILL.md`;
- change runtime pipeline behavior;
- change `caller_action`;
- change provider-boundary policy;
- add archive integration;
- add automatic generation inside a Lolla run;
- add Observatory UI;
- infer PR31 labels from prose;
- add automatic labels;
- add answer-quality scoring;
- add a judge;
- decide `safe_for_agent_use`;
- create high-stakes evidence;
- implement provenance-map, conflict-register, or case-graph exporters;
- add graph DB, embeddings, chunking, memory, GraphRAG, or Semantica-style
  platform work.

## Validation

PR68 validation:

```bash
python3 -m py_compile \
  engine/system_b/audit_decision_record.py \
  scripts/build_audit_decision_record.py \
  tests/test_audit_decision_record.py

PYTHONPATH=. pytest -q tests/test_audit_decision_record.py
```

The tests cover stable schema version, PR31 bucket status defaults, population
policy, semantic-field non-claim metadata, explicit review-supplied labels
without prose inference, malformed and missing artifacts, raw file non-reading,
custody flags, local-path exclusion, CLI behavior, and output-path guards.

## Next Gate

Recommended PR69:

```text
PR69 Audit Decision Record Export Review Re-Run v0
```

PR69 should re-run the PR67 smoke/review against the refined output and verify
that empty PR31 bucket clarity improves from `partly_clear` to
`clear_non_claim` before any archive integration, batch export, or automatic
generation is planned.
