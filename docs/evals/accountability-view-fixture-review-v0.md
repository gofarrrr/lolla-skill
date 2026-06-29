# Accountability View Fixture Review v0

Status: PR64 docs/eval-only fixture review
Date: 2026-06-29
Owner: Lolla maintainers

PR64 reviews the PR63 accountability-view fixture bundles before any exporter
or runtime work exists. The review asks whether four views together help a
human/product reviewer inspect a Lolla run without turning clean structure into
false certainty.

Inputs:

- [Accountability View Fixtures v0](accountability-view-fixtures-v0.md)
- [accountability-view-fixtures-v0.json](accountability-view-fixtures-v0.json)
- [Audit Decision Record v0](../conversation-understanding/audit-decision-record-v0.md)
- [Provenance Map v0](../conversation-understanding/provenance-map-v0.md)
- [Review Conflict Register v0](review-conflict-register-v0.md)
- [Case Graph Export Design v0](../conversation-understanding/case-graph-export-v0.md)
- [Actionable Delta Rubric v0](actionable-delta-rubric-v0.md)

Review JSON:

- [review.json](../../reviews/human/accountability-view-fixture-review-v0/review.json)

This slice is docs/eval-only. It does not implement an exporter, add tests,
change runtime behavior, run `$lolla`, call models, inspect raw archives, mutate
archives, change prompts, change `SKILL.md`, create labels, score advice,
approve high-stakes use, add graph DB, add memory, or ship Semantica-style
platform work.

## Review Scope

The review covers all three PR63 fixture bundles:

| fixture_id | case_id | review read |
|---|---|---|
| `avf_v0_001_launch_public_enterprise_beta` | `launch-public-enterprise-beta` | Same-shape buyer proof before public enterprise beta posture. |
| `avf_v0_002_deploy_assisted_intake_routing` | `deploy-assisted-intake-routing` | Operable controls, escalation ownership, and stop conditions. |
| `avf_v0_003_ceo_remove_founding_cofounder` | `ceo-remove-founding-cofounder` | Authority transfer before bounded transition support. |

Every row is paraphrase-only and uses checked-in PR63 fixture content. The
review does not inspect raw archive transcripts, raw memos, raw revised answers,
provider/model text, or private reasoning.

## Aggregate Result

The review rows exactly match the three PR63 fixture IDs.

| Field | Result |
|---|---|
| fixture count reviewed | 3 |
| review_status | 3 pass, 0 revise, 0 exclude |
| bundle_inspection_value | 2 high, 1 medium, 0 low, 0 none |
| decision_record_value | 3 high, 0 medium, 0 low, 0 none |
| provenance_map_value | 0 high, 3 medium, 0 low, 0 none |
| conflict_register_value | 3 high, 0 medium, 0 low, 0 none |
| case_graph_value | 0 high, 2 medium, 1 low, 0 none |
| false_certainty_risk | 0 none, 3 low, 0 medium, 0 high |
| raw_content_safety | 3 safe, 0 needs_revision, 0 unsafe |
| recommended_next | 3 implement_one_exporter, 0 more_fixtures, 0 revise_shapes, 0 stop_lane |

## Per-View Read

Audit decision record:

- highest implementation readiness across the bundle;
- directly answers what changed in the recommendation;
- maps cleanly to PR31 actionable-delta labels;
- has the lowest graph/memory drift risk;
- should be the default candidate for a later read-only exporter design gate.

Provenance map:

- useful as artifact-lineage context;
- should remain design-only until exporter custody details are narrower;
- must stay lineage-only and never imply answer quality.

Review conflict register:

- useful for preserving unresolved tensions that compact decision records can
  flatten;
- should remain human-review-owned and needs more fixture work before helper or
  exporter design;
- must not become conflict resolution, severity automation, policy enforcement,
  or a labeler.

Case graph:

- sometimes helps show relationships among decision, delta, conflict, and
  artifact nodes;
- carries the highest risk of decorative structure, memory vibes, graph DB
  drift, and false source-of-truth posture;
- should hold before implementation.

## Implementation-Readiness Summary

| View | Review outcome |
|---|---|
| `audit_decision_record` | `ready_for_exporter_design` on all 3 fixtures |
| `provenance_map` | `needs_more_fixtures` on all 3 fixtures |
| `review_conflict_register` | `needs_more_fixtures` on all 3 fixtures |
| `case_graph` | `hold` on all 3 fixtures |

The safe implementation signal is narrow:

```text
Implement at most one read-only exporter next, and make it the audit decision
record exporter if PR65 approves implementation at all.
```

## PR65 Decision Result

PR65 has now landed as an implementation decision gate, not implementation:

- [Accountability Implementation Decision Gate v0](accountability-implementation-decision-gate-v0.md)

The review supported outcome A from the PR65 option set:

```text
A. Implement audit_decision_record exporter next.
```

PR65 chose outcome A and recommends future PR66 Audit Decision Record Read-Only
Exporter v0. It still rejects or defers graph DB, memory, case graph exporter
work, provenance exporter work, conflict-register helper/exporter work,
answer-quality scoring, automatic labels, judges, high-stakes evidence creation,
runtime integration, and Semantica-style platform work.

PR65 names the next implementation slice only as a future PR:

```text
PR66 Audit Decision Record Read-Only Exporter v0
```

PR64 did not start PR65 implementation, and PR65 does not start PR66.

## Anti-Drift Sentence

```text
doctor != runtime approval
decision record != truth
provenance map != advice quality
conflict register != conflict resolution
case graph != memory
fixtures != real runtime feature
design JSON != shipped artifact
```

## Non-Goals

PR64 does not add or approve:

- an exporter;
- tests;
- schemas under `engine/`;
- CLI support;
- runtime integration;
- archive reading behavior;
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
- graph DB;
- embeddings;
- chunking;
- memory;
- GraphRAG;
- entity resolution;
- policy enforcement;
- Semantica-style platform work.

## Stop Point

PR64 moved only to the docs-only decision gate:

```text
PR65 Accountability Implementation Decision Gate v0
```

PR65 now recommends a future PR66, but it does not implement it.
