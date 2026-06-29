# Provenance Map v0

Status: PR60 docs/JSON design
Date: 2026-06-29
Owner: Lolla maintainers

PR60 designs `lolla.provenance_map.v0` as a local artifact-lineage map for a
single Lolla run or review surface.

The provenance map answers a narrow custody question:

```text
How did this run's artifacts come into existence, and how do they depend on
each other?
```

It does not decide whether the advice was good, whether the audited decision was
correct, whether an action is approved, or whether the map is regulator-grade
provenance.

## Why This Matters

Lolla already has many artifacts that help humans review a run:

- `conversation.txt`
- `extraction.json`
- `result.json`
- `revised.txt`
- `memo.md`
- `agent_result.json`
- `evaluation.json`
- `reasoning_trace.json`
- review files
- doctor reports, where relevant
- audit decision records, where relevant

Those artifacts are useful because deterministic custody keeps semantic
judgment inspectable. But a reviewer still needs to know how the artifacts
relate. A clean `evaluation.json` is not the same as good advice. A missing
`memo.md` is different from a malformed review file. A future audit decision
record depends on source artifacts and review summaries; it should not appear
from nowhere.

`lolla.provenance_map.v0` makes that lineage explicit.

## Inspiration

Semantica's provenance module uses W3C PROV-O-style ideas such as entities,
activities, agents, usage, generation, and derivation. Lolla borrows that
vocabulary lightly.

Lolla does not borrow the compliance stack. PR60 does not require RDF, OWL,
SHACL, W3C compliance, graph databases, embeddings, chunking, memory, hosted
services, or platform work.

## Schema

Schema version:

```text
lolla.provenance_map.v0
```

Design example:

- [provenance-map-v0.json](provenance-map-v0.json)

High-level fields:

| Field | Meaning |
|---|---|
| `schema_version` | Fixed string: `lolla.provenance_map.v0`. |
| `case_id` | Compact case identifier already safe for review surfaces. |
| `run_id` | Compact run identifier already safe for review surfaces. |
| `archive_relpath` | Relative archive reference only. |
| `scope` | Declares map type, generator class, and raw-content exclusion. |
| `entities` | Artifact-like things whose existence, schema, hash, and custody can be inspected. |
| `activities` | Local actions that used entities and generated entities. |
| `agents` | Local scripts, model/provider roles, humans, or external control layers involved in custody. |
| `relationships` | Safe-to-print links such as `used`, `generated`, `derived_from`, `validated_by`, `reviewed_by`, and `summarized_by`. |
| `custody_flags` | Whole-map privacy and custody exclusions. |
| `limitations` | Non-claims and missing/degraded lineage caveats. |

## Vocabulary

PR60 uses these terms in a Lolla-shaped way:

- `entity`: an artifact or review object, such as `conversation.txt`,
  `evaluation.json`, a doctor report, or an audit decision record.
- `activity`: a local process that uses or generates entities, such as capture,
  extraction, pipeline execution, memo rendering, evaluation, archive, doctor
  preflight, human review, or future decision-record projection.
- `agent`: the producer, reviewer, validator, or preflight checker associated
  with an activity.
- `used`: an activity consumed or inspected an entity.
- `generated`: an activity produced an entity.
- `derived_from`: an entity is a review-safe projection or summary of another
  entity.
- `validated_by`: an entity was checked by another entity or activity.
- `reviewed_by`: an entity or decision surface was reviewed by a human-owned
  review file.
- `summarized_by`: an entity's review-safe meaning was summarized by another
  entity.

This vocabulary is descriptive. It is not a claim that the JSON is PROV-O,
RDF, W3C compliant, regulator-grade, or complete.

## Entity Fields

Each entity should be safe to print:

- `entity_id`: stable local identifier inside the map.
- `artifact`: relative artifact name or safe review-file path.
- `artifact_role`: Lolla-specific role such as `captured_conversation`,
  `audit_pipeline_result`, `run_readiness_receipt`, or `human_review_file`.
- `status`: `present`, `missing`, `not_applicable`, or `unknown`.
- `schema_version`: known schema string, `null`, or a safe placeholder.
- `hash`: algorithm and value. Design fixtures should not include real archive
  hashes unless those hashes are already checked-in and safe to repeat.
- `byte_count`: number if known and safe, otherwise `null`.
- `custody_flags`: per-entity raw-content and local-path exclusions.

## Activities And Agents

Activities should preserve the distinction between artifact existence and
semantic quality. For example:

- `activity.evaluate` may generate `evaluation.json`;
- `evaluation.json` may validate that required artifacts exist;
- that does not mean the revised advice is correct.

Agents are local custody participants, not autonomous authorities. A model
provider may be listed as an agent type when it generated audit pressure, but
the provenance map still must not include provider text or private reasoning.

## Relationship To Other Artifacts

Doctor/preflight:

- `lolla.doctor_report.v0` checks local readiness before a run.
- `lolla.provenance_map.v0` maps lineage after, around, or beside a run.
- Doctor can be an optional entity when a report exists, but PR60 does not
  change doctor behavior.

Reasoning trace:

- `reasoning_trace.json` already indexes local artifacts by path/hash and
  custody metadata.
- The provenance map is a review-safe lineage projection over those artifacts,
  not a replacement for the trace.

Evaluation:

- `evaluation.json` is a deterministic run-readiness receipt.
- The provenance map can show that `evaluation.json` validated or referenced
  artifacts, but it does not turn run readiness into advice quality.

Audit decision record:

- `lolla.audit_decision_record.v0` summarizes what decision changed.
- The provenance map shows which artifacts and review files support that
  projection.

Human review:

- Human review files remain the source of answer-level review labels.
- The provenance map may point to them, but it does not create or copy labels.

## Non-Goals

PR60 does not add or approve:

- an exporter;
- runtime integration;
- `$lolla` runs;
- model calls;
- archive mutation;
- archive reading behavior;
- prompt changes;
- `SKILL.md` changes;
- provider-boundary policy changes;
- `caller_action` changes;
- high-stakes runs;
- answer-quality scoring;
- LLM judges;
- automatic human-review labels;
- automatic `safe_for_agent_use`;
- source quote dumps;
- raw transcript inclusion;
- raw memo inclusion;
- raw revised-answer inclusion;
- provider/model text inclusion;
- private reasoning inclusion;
- local absolute paths in checked-in examples;
- RDF requirement;
- W3C compliance claim;
- PROV-O compliance claim;
- OWL or SHACL;
- graph DB;
- embeddings;
- chunking;
- memory;
- policy engine;
- Semantica-style platform work.

Extra stop rule:

If a future PR60 continuation feels tempted to add code, tests, exporters,
schemas under `engine/`, CLI support, runtime integration, or archive-reading
behavior, stop and report. PR60 is only a design artifact and safe example
JSON.

## Example Read

The PR60 JSON example uses the already documented
`ceo-remove-founding-cofounder` case. It lists safe artifact names and placeholder
hash states only. It does not inspect raw archives, copy raw content, or repeat
real archive hashes.

## PR61 Gate

The next possible slice is:

```text
PR61 Review Conflict Register Design v0
```

PR61 should remain docs/JSON design only. It should design a human-review-owned
conflict register without resolving conflicts, scoring severity into actions,
adding policy enforcement, implementing an exporter, reading archives, changing
runtime behavior, or beginning Semantica-style platform work.
