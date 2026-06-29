# Audit Decision Record Export Review Re-Run v0

Status: PR69 docs/review/data slice
Date: 2026-06-29
Owner: Lolla maintainers

PR69 re-runs the PR67 smoke review against the PR68-refined
`lolla.audit_decision_record.v0` output.

The slice asks one narrow product question:

```text
After PR68, can a human reviewer understand what the exported record is saying
and not saying from the record itself?
```

This is not a new implementation slice. PR69 does not change the exporter,
change runtime behavior, add archive integration, add automatic generation,
add batch export, add scoring, add labels, add a judge, or decide
`safe_for_agent_use`.

## Review Method

The review used a two-pass read for each generated record.

Pass 1 was record-only interpretation. The reviewer answered from the exported
JSON alone:

- what an empty PR31 bucket means;
- whether the record claims no conflicts exist;
- whether the exporter inferred PR31 labels from revised-answer prose;
- which fields came from structured sources;
- which fields are not supplied or not measured;
- whether the record says the advice is good;
- whether an agent could treat the record as a quality label.

Pass 2 was docs-assisted interpretation. The reviewer then checked whether the
docs changed the interpretation.

`clear_non_claim` means the reviewer can tell, from the record itself, that an
empty field is not a substantive finding about the audited decision.

## Smoke Strategy

PR69 reviewed seven records:

- the same 4 existing reviewed archive cases used in PR67 where available;
- the same 2 fixture-backed temp-run styles used in PR67;
- 1 optional fixture-backed temp run with safe review-json-supplied PR31
  buckets, to check PR68's `populated_from_review` path without exporter code
  changes.

The existing archive relpaths were selected from checked-in review JSON and
fixture docs, not by reading raw archive transcripts:

- `ceo-remove-founding-cofounder/20260627T093131Z_59d153`
- `launch-public-enterprise-beta/20260627T104146Z_7bfe79`
- `deploy-assisted-intake-routing/20260627T130339Z_4cd3cb`
- `implement-price-increase-three/20260627T083231Z_52724d`

The fixture-backed temp runs used only safe structured JSON, plus raw trap
files that were not read or copied:

- missing-artifacts style case;
- malformed-evaluation style case;
- review-json-supplied PR31 bucket case.

## Export Commands

Existing reviewed archive pattern:

```bash
python3 scripts/build_audit_decision_record.py \
  --run-dir <archive-root>/<archive-relpath> \
  --review-json reviews/human/audit-decision-record-fixture-review-v0/review.json \
  --out /tmp/lolla_audit_decision_record_pr69_<case>.json \
  --pretty

jq . /tmp/lolla_audit_decision_record_pr69_<case>.json
```

Fixture-backed temp run pattern:

```bash
python3 scripts/build_audit_decision_record.py \
  --run-dir <fixture-temp-run-dir> \
  --out /tmp/lolla_audit_decision_record_pr69_<case>.json \
  --pretty

jq . /tmp/lolla_audit_decision_record_pr69_<case>.json
```

Review-json-supplied fixture pattern:

```bash
python3 scripts/build_audit_decision_record.py \
  --run-dir <fixture-temp-run-dir> \
  --review-json <safe-review-json> \
  --out /tmp/lolla_audit_decision_record_pr69_<case>.json \
  --pretty

jq . /tmp/lolla_audit_decision_record_pr69_<case>.json
```

All generated outputs parsed with `jq`.

## Checked-In Artifacts

PR69 checks in:

- [review.json](../../reviews/human/audit-decision-record-export-review-rerun-v0/review.json)
- [exported-records-summary.json](../../reviews/human/audit-decision-record-export-review-rerun-v0/exported-records-summary.json)

PR69 does not check in full exported records. The checked-in summary is a
structural, privacy-safe digest of the generated records: source type,
relative archive identifiers, PR31 bucket-status counts, semantic-field
statuses, artifact-status counts, custody flags, and safety review results.

The summary intentionally omits raw transcript text, raw memo text, raw
revised-answer text, live transcript text, provider/model text, private
reasoning, local absolute archive paths, secrets, and copied archive content.

## Review Results

Reviewed records: 7.

Source type breakdown:

| Source type | Count |
|---|---:|
| `existing_reviewed_archive` | 4 |
| `fixture_backed_temp_run` | 2 |
| `fixture_backed_temp_run_review_json_supplied` | 1 |

Aggregate review read:

| Dimension | Result |
|---|---|
| Export status | 7 pass, 0 revise, 0 fail, 0 exclude |
| Record understandability | 7 clear |
| Empty PR31 bucket clarity | 7 clear non-claim |
| Semantic empty-field clarity | 7 clear non-claim |
| Bucket status usefulness | 7 useful |
| Population policy usefulness | 7 useful |
| Artifact status usefulness | 7 useful |
| Custody clarity | 7 clear |
| Limitation clarity | 7 clear |
| Cognitive load | 6 acceptable, 1 heavy but usable, 0 too heavy |
| False-certainty risk | 2 none, 5 low, 0 medium, 0 high |
| Raw content safety | 7 safe |
| Reviewer use without raw content | 7 yes |
| Reviewer needed docs to avoid misread | 7 no |
| Implementation readiness | 7 ready for integration plan |
| Primary issue | 7 none |

## Comparison To PR67

| Dimension | PR67 | PR69 |
|---|---|---|
| Empty PR31 bucket clarity | 2 `clear_non_claim`, 4 `partly_clear` | 7 `clear_non_claim` |
| Implementation readiness | 2 `ready_for_next_review`, 4 `needs_schema_adjustment` | 7 `ready_for_integration_plan` |
| Primary issue | 4 `empty_fields_confusing`, 2 `none` | 7 `none` |

The PR68 refinement materially improved the original weakness. Empty PR31
buckets now read as `not_supplied` / not inferred, not as "no meaningful
delta." Semantic empty arrays also read as non-claims because they carry
`status`, `items`, `empty_meaning`, `owner`, and
`exporter_inferred_from_prose`.

## Findings

The refined record is readable enough for the next decision gate.

The record itself now makes these distinctions visible without requiring the
reader to open docs first:

- empty bucket means no safe explicit label source supplied unless
  `bucket_status` says otherwise;
- missing artifact is an artifact availability issue;
- malformed artifact is an artifact parse issue;
- empty semantic array is not evidence that no conflicts or unresolved
  questions exist;
- review-supplied buckets can be marked `populated_from_review`;
- the exporter does not infer PR31 labels from prose;
- the record is not answer-quality scoring, recommendation approval, domain
  approval, or `safe_for_agent_use`.

The one load caveat is acceptable: the refined JSON carries more caveat
metadata. One record was marked `heavy_but_usable` because the reader must scan
population policy, bucket statuses, semantic statuses, custody flags, and
limitations together. That is a presentation issue for future human surfaces,
not a schema failure.

## Answers

Are empty PR31 buckets understandable as "not supplied / not inferred"?

Yes. All seven records were reviewed as `clear_non_claim`.

Is there a visible difference between missing artifact, malformed artifact, not
measured, and empty semantic field?

Yes. Source artifact status, semantic-field status, and empty-meaning metadata
now keep those cases separate.

Does the record make it obvious that no answer-quality scoring happened?

Yes. The record's limitations, custody flags, and population policy preserve
that boundary.

Does the record make it obvious that human review still owns improvement
judgment?

Yes. The record remains an accountability shell. It does not decide whether the
recommendation improved.

Does the record help an agent inspect run readiness without overclaiming?

Yes, as an inspectable artifact. It should still pass through a separate
integration decision before any archive generation or runtime use.

## Non-Goals Preserved

PR69 did not:

- change the exporter;
- change production code;
- change runtime behavior;
- add archive integration;
- add automatic generation inside a Lolla run;
- add batch export;
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
- infer PR31 labels from prose;
- add automatic labels;
- add a judge;
- decide `safe_for_agent_use`.

## Decision

Recommended PR70:

```text
PR70 Audit Decision Record Archive Integration Decision Gate v0
```

Reason:

PR69 finds the PR68-refined record readable, raw-content-safe, and clear about
empty-field non-claims. The next step should still be a decision gate, not
archive integration implementation. That gate should decide whether and how
the manual exporter may later become a first-class archive artifact while
preserving read-only/manual boundaries until explicitly approved.
