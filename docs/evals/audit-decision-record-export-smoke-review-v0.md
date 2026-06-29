# Audit Decision Record Export Smoke Review v0

Status: PR67 docs/review/data slice; followed by PR68 refinement
Date: 2026-06-29
Owner: Lolla maintainers

PR67 reviews whether the PR66 read-only audit decision record exporter produces
records that are useful, humble, and raw-content-safe when run against safe
known or fixture-backed Lolla run folders.

This slice does not change the exporter. It does not change runtime behavior,
add archive integration, add automatic generation, add scoring, add labels, add
a judge, or decide `safe_for_agent_use`.

## Question

PR67 asks:

```text
When this exporter is used on safe known or fixture-backed Lolla run folders,
is the exported audit decision record actually useful to a human reviewer, and
are its caveats clear enough?
```

## Smoke Strategy

PR67 generated eight `/tmp` export outputs and reviewed six of them.

Reviewed source mix:

- 4 existing reviewed archives selected from checked-in PR59 fixture relpaths;
- 2 fixture-backed temp runs created from safe structured JSON only.

The existing archive relpaths were selected from:

- [audit-decision-record-fixtures-v0.json](audit-decision-record-fixtures-v0.json)
- [review.json](../../reviews/human/audit-decision-record-fixture-review-v0/review.json)

No examples were discovered by reading raw archive transcripts.

The fixture-backed temp runs exercised caveat paths:

- missing structured artifacts;
- malformed `evaluation.json`;
- raw trap files that must not appear in exported output.

## Export Commands

Existing reviewed archive pattern:

```bash
python3 scripts/build_audit_decision_record.py \
  --run-dir <archive-root>/<archive-relpath> \
  --review-json reviews/human/audit-decision-record-fixture-review-v0/review.json \
  --out /tmp/lolla_audit_decision_record_pr67_<case>.json \
  --pretty

jq . /tmp/lolla_audit_decision_record_pr67_<case>.json
```

Fixture-backed temp run pattern:

```bash
python3 scripts/build_audit_decision_record.py \
  --run-dir <fixture-temp-run-dir> \
  --out /tmp/lolla_audit_decision_record_pr67_<case>.json \
  --pretty

jq . /tmp/lolla_audit_decision_record_pr67_<case>.json
```

All generated outputs parsed with `jq`.

## Checked-In Review

Human/product review:

- [review.json](../../reviews/human/audit-decision-record-export-smoke-review-v0/review.json)

PR67 does not check in generated exported records.

Reason: the existing-archive smoke outputs are privacy-safe enough for local
review, but they include local run artifact metadata, checksums, and structured
run summaries produced from local archives. The durable repo artifact for this
slice is the review, not copied local export payloads.

## Review Results

Reviewed records: 6.

Source type breakdown:

| Source type | Count |
|---|---:|
| `existing_reviewed_archive` | 4 |
| `fixture_backed_temp_run` | 2 |

Aggregate review read:

| Dimension | Result |
|---|---|
| Export status | 6 pass, 0 revise, 0 fail, 0 exclude |
| Record understandability | 5 clear, 1 mostly clear |
| Artifact status usefulness | 6 useful |
| Empty PR31 bucket clarity | 2 clear non-claim, 4 partly clear |
| Custody clarity | 6 clear |
| Limitation clarity | 6 clear |
| Raw content safety | 6 safe |
| False-certainty risk | 2 none, 4 low |
| Reviewer use without raw content | 6 yes |

## Findings

The exporter is useful as a read-only accountability shell.

It makes these facts easy to inspect:

- run identity;
- relative archive reference;
- safe structured artifact presence;
- malformed artifact status;
- missing artifact status;
- `not_measured` semantic fields;
- empty PR31 buckets;
- review-reference metadata;
- raw/private exclusion flags;
- limitations and non-claims.

The strongest positive finding is custody clarity. The record repeatedly says
that it is not answer-quality scoring, not recommendation approval, not domain
approval, and not `safe_for_agent_use`. Custody flags also make excluded raw and
private content visible as excluded.

The main caveat is empty PR31 bucket clarity. Empty arrays are correct because
PR66 does not infer labels from prose. In real archive exports, though, they can
look like "no meaningful delta" unless the reader catches the limitation saying
labels were not inferred. That is a schema/readability issue, not an exporter
bug.

The fixture-backed records were useful because they showed that:

- missing artifacts are visibly `missing`;
- malformed artifacts are visibly `malformed`;
- semantic fields without safe structured sources are `not_measured`;
- raw trap files do not appear in the exported output.

## Answers

Are empty PR31 buckets understandable as "not supplied / not inferred"?

Partly. The limitation text says this, but the buckets themselves do not carry
their own population policy or status. Before deeper integration, that should
be made harder to miss.

Is there a visible difference between missing artifact, malformed artifact, not
measured, and empty semantic field?

Yes. Source artifacts use `missing` and `malformed`; semantic fields use
`not_measured` / `not_included`; PR31 buckets use empty arrays. The distinction
is present, but PR31 empty-array semantics deserve a clearer cue.

Does the record make it obvious that no answer-quality scoring happened?

Yes. Limitations, custody flags, and review refs all preserve this boundary.

Does the record make it obvious that human review still owns improvement
judgment?

Yes. The limitations say human review remains responsible for judging
improvement.

Does the record help an agent inspect run readiness without overclaiming?

Yes, with one caveat. The artifact statuses and custody flags are useful for
inspection. Empty PR31 buckets should be clarified before an agent-facing or
batch-review surface relies on the record.

## Non-Goals Preserved

PR67 did not:

- change the exporter;
- change production code;
- change runtime behavior;
- add archive integration;
- add automatic generation inside a Lolla run;
- add Observatory UI;
- run `$lolla`;
- call models;
- mutate archives;
- change prompts;
- change `SKILL.md`;
- change `caller_action`;
- change provider-boundary policy;
- create high-stakes evidence;
- implement provenance-map, conflict-register, or case-graph exporters;
- add graph DB, embeddings, chunking, memory, GraphRAG, or Semantica-style
  platform work;
- add answer-quality scoring;
- add automatic labels;
- add a judge;
- decide `safe_for_agent_use`.

## Decision

Recommended PR68:

```text
PR68 Audit Decision Record Schema/Exporter Refinement v0
```

Reason:

Before archive integration, batch export, or automatic generation is planned,
the decision record should make empty PR31 buckets and semantic-field
population policy clearer. The likely refinement is small: add or design an
explicit population-policy/status cue so empty arrays cannot be mistaken for a
substantive no-delta judgment.

## PR68 Follow-Up

PR68 has now implemented that narrow refinement:

- [Audit Decision Record Schema / Exporter Refinement v0](audit-decision-record-schema-exporter-refinement-v0.md)

The schema version remains `lolla.audit_decision_record.v0`. Generated records
now include `actionable_deltas.population_policy`,
`actionable_deltas.bucket_status`, and `actionable_deltas.buckets`, with empty
bucket defaults marked `not_supplied`. Semantic arrays now include `status`,
`items`, `empty_meaning`, `owner`, and `exporter_inferred_from_prose`.

Recommended PR69 is a re-run of this smoke/review against the refined output to
verify that empty PR31 bucket clarity improves to `clear_non_claim` before any
archive integration, batch export, automatic generation, scoring, labels,
judges, or runtime behavior is considered.
