# Case Graph Export Design v0

Status: PR62 docs/JSON design
Date: 2026-06-29
Owner: Lolla maintainers

PR62 designs `lolla.case_graph.v0` as a future run-local case graph
export/view shape over existing Lolla review artifacts.

This is a design artifact only. PR62 does not implement an exporter, add code,
read archives, run `$lolla`, call models, mutate archives, add graph storage,
or add runtime integration.

## Problem

PR58, PR60, and PR61 each make one accountability surface clearer:

- `lolla.audit_decision_record.v0` summarizes what changed in the audited
  decision;
- `lolla.provenance_map.v0` summarizes local artifact lineage;
- `lolla.review_conflict_register.v0` preserves unresolved tensions for human
  review.

Those surfaces are useful separately, but reviewers still need a compact way to
see how a decision, action delta, evidence gate, unresolved conflict, source
artifact, and human review relate to each other. A case graph view can provide
that review map without becoming the source of truth.

The design goal is:

```text
Show how this run's review-safe artifacts relate.
Do not claim the graph knows whether the advice is good.
```

## Inspiration

Semantica-style accountability treats decision records, provenance, conflicts,
and exports as first-class review surfaces. Lolla borrows that discipline only
as a local, deterministic, review-owned view.

Lolla is not borrowing Semantica's broader platform scope. PR62 does not approve
a graph DB, RDF/PROV-O compliance, embeddings, GraphRAG, memory, policy engine,
or general context platform.

## Schema

Schema version:

```text
lolla.case_graph.v0
```

Design example:

- [case-graph-export-v0.json](case-graph-export-v0.json)

High-level fields:

| Field | Meaning |
|---|---|
| `schema_version` | Fixed string: `lolla.case_graph.v0`. |
| `case_id` | Compact reviewed case identifier. |
| `run_id` | Compact run identifier already safe for review surfaces. |
| `archive_relpath` | Relative archive reference only. |
| `status` | Design/example status, not a runtime health result. |
| `scope` | Flags proving this is a run-local design view, not a platform. |
| `source_refs` | Relative docs or artifact names used by the example. |
| `vocabulary` | Allowed node and edge types for v0. |
| `nodes` | Review-safe nodes. |
| `edges` | Review-safe relationships between nodes. |
| `custody_flags` | Whole-export raw/private content exclusions. |
| `limitations` | Non-claims and caveats. |

## Scope Flags

The v0 shape must make these boundaries machine-readable:

- `future_export_shape_only: true`
- `exporter_implemented: false`
- `graph_database_required: false`
- `global_memory: false`
- `runtime_integration: false`
- `archive_reads_in_design: false`
- `model_calls: 0`
- `archives_mutated: false`

These flags prevent a design example from being mistaken for a shipped feature.

## Node Types

The v0 vocabulary may include:

- `decision`
- `original_recommendation`
- `revised_recommendation`
- `actionable_delta`
- `evidence_gate`
- `threshold`
- `sequence`
- `stop_rule`
- `written_term`
- `user_question`
- `value_or_priority`
- `stakeholder`
- `unresolved_conflict`
- `artifact`
- `provenance_activity`
- `review_record`
- `doctor_check`
- `limitation`

Nodes are review projections. They do not replace source artifacts, human
review rows, decision records, provenance maps, or conflict registers.

## Edge Types

The v0 vocabulary may include:

- `summarizes`
- `changed_by`
- `adds_gate`
- `adds_threshold`
- `changes_sequence`
- `adds_stop_rule`
- `adds_written_term`
- `raises_question`
- `has_conflict`
- `preserves_conflict`
- `supported_by_artifact`
- `reviewed_by`
- `derived_from`
- `used_by`
- `generated_by`
- `has_limitation`
- `not_applicable`

Edges are review-safe relationships, not causal proofs. An edge can say that a
review surface links two ideas; it cannot prove that the underlying advice is
true, safe, approved, or optimal.

## Relationship To Existing Accountability Artifacts

Audit decision record:

- can contribute decision, original recommendation, revised recommendation, and
  actionable-delta nodes;
- remains the source for decision-delta summaries;
- must not be replaced by the graph.

Provenance map:

- can contribute artifact, activity, agent, and lineage relationships;
- remains the source for artifact-lineage custody;
- must not become a graph DB requirement.

Review conflict register:

- can contribute unresolved-conflict nodes and conflict-preservation edges;
- remains human-review-owned;
- must not become conflict resolution, severity automation, or policy
  enforcement.

Values/priorities worksheet:

- can contribute value, priority, stakeholder, and unresolved-question nodes
  when a human-filled worksheet exists;
- does not become memory, extraction, or automatic user profiling.

Human review:

- can contribute review-record nodes and reviewer-read edges;
- remains the owner of answer-level judgment, labels, and future calibration
  decisions.

Doctor/preflight:

- can contribute doctor-check nodes only when a safe doctor report already
  exists;
- does not run doctor, approve the environment, or mutate archives.

## Example Read

The PR62 JSON example uses the already documented
`deploy-assisted-intake-routing` case. It paraphrases checked-in review
summaries and design artifacts. It uses relative artifact names and placeholder
checksum values only.

The example shows:

- a decision node for a bounded assisted-routing pilot;
- original and revised recommendation nodes;
- evidence-gate, stop-rule, and user-question nodes;
- an unresolved conflict node from the PR61 register design;
- review, artifact, provenance, and limitation nodes;
- edges that make the review path easier to inspect.

The example does not include raw transcript, raw memo, raw revised-answer text,
provider/model text, private reasoning, local absolute paths, real archive
hashes, or answer-quality scoring.

## Non-Goals

PR62 does not add or approve:

- an exporter implementation;
- tests;
- schemas under `engine/`;
- CLI support;
- archive reading behavior;
- runtime integration;
- `$lolla` runs;
- model calls;
- archive mutation;
- prompt changes;
- `SKILL.md` changes;
- provider-boundary policy changes;
- `caller_action` changes;
- high-stakes runs;
- high-stakes archive evidence;
- answer-quality scoring;
- LLM judges;
- automatic human-review labels;
- automatic `safe_for_agent_use`;
- conflict resolution;
- severity automation;
- policy enforcement;
- domain approval;
- graph DB;
- RDF or PROV-O compliance claims;
- OWL, SHACL, or W3C-grade provenance claims;
- embeddings;
- chunking;
- memory;
- entity resolution;
- GraphRAG;
- source quote dumps;
- Semantica-style platform work.

Extra stop rule:

If a future PR62 continuation feels tempted to add code, tests, exporters,
schemas under `engine/`, CLI support, runtime integration, or archive-reading
behavior, stop and report. PR62 is only a design artifact and safe example
JSON.

## PR63 Gate

PR63 has now created the broader accountability-view fixture pack. It uses the
case graph as one view beside audit decision record, provenance map, and review
conflict register views. It remains paraphrase-only docs/JSON and does not
implement an exporter.

## PR63 Accountability View Fixtures

PR63 now tests the case graph view inside combined accountability-view bundles:

- [Accountability View Fixtures v0](../evals/accountability-view-fixtures-v0.md)
- [accountability-view-fixtures-v0.json](../evals/accountability-view-fixtures-v0.json)

Those fixtures use the graph only as a compact relationship view over
review-safe summaries. They do not implement a graph exporter, graph DB,
GraphRAG, memory, entity resolution, runtime integration, score, label, or
judge.
