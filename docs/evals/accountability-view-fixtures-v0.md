# Accountability View Fixtures v0

Status: PR63 docs/JSON fixture pack
Date: 2026-06-29
Owner: Lolla maintainers

PR63 creates a paraphrase-only fixture pack for the combined accountability
view bundle:

- `audit_decision_record`
- `provenance_map`
- `review_conflict_register`
- `case_graph`

This is docs/JSON only. PR63 does not implement an exporter, run `$lolla`, call
models, inspect raw archives, mutate archives, change prompts, change
`SKILL.md`, change provider-boundary policy, create labels, score advice, add a
graph DB, add memory, or ship runtime artifacts.

## Why This Exists

PR58 through PR62 designed the views separately. A reviewer can understand each
view in isolation, but implementation should wait until we test whether the
views help together.

The PR63 question is:

```text
If a reviewer sees all four accountability views for one case, does the bundle
make the Lolla run easier to inspect without creating false certainty?
```

The answer must come from fixture review before exporter work.

## Fixture Scope

The pack covers three existing reviewed cases from checked-in summaries:

| fixture_id | case_id | source run id | bundle focus |
|---|---|---|---|
| `avf_v0_001_launch_public_enterprise_beta` | `launch-public-enterprise-beta` | `20260627T104146Z_7bfe79` | Same-shape buyer proof before public enterprise beta posture. |
| `avf_v0_002_deploy_assisted_intake_routing` | `deploy-assisted-intake-routing` | `20260627T130339Z_4cd3cb` | Operable controls, escalation ownership, and stop conditions. |
| `avf_v0_003_ceo_remove_founding_cofounder` | `ceo-remove-founding-cofounder` | `20260627T093131Z_59d153` | Authority transfer before bounded transition support. |

Fixture JSON:

- [accountability-view-fixtures-v0.json](accountability-view-fixtures-v0.json)

Inputs:

- [Audit Decision Record v0](../conversation-understanding/audit-decision-record-v0.md)
- [Provenance Map v0](../conversation-understanding/provenance-map-v0.md)
- [Review Conflict Register v0](review-conflict-register-v0.md)
- [Case Graph Export Design v0](../conversation-understanding/case-graph-export-v0.md)
- [Audit Decision Record Fixtures v0](audit-decision-record-fixtures-v0.md)
- [Actionable Delta Rubric v0](actionable-delta-rubric-v0.md)
- [Complex Baseline Human Review v0](complex-baseline-human-review-v0.md)

## How Each View Contributes

Audit decision record:

- answers what decision changed;
- maps the change to PR31 actionable-delta labels;
- keeps unresolved conflicts and questions visible;
- does not decide whether the advice is true, safe, or approved.

Provenance map:

- answers which safe artifact names, activities, and review files support the
  bundle;
- uses placeholder hashes only;
- keeps lineage separate from answer quality.

Review conflict register:

- answers what remains in tension;
- keeps conflicts human-review-owned;
- does not resolve conflicts, score severity, or enforce policy.

Case graph:

- connects the decision, recommendations, deltas, conflicts, artifacts, and
  review records in a compact node/edge view;
- remains a view, not memory, graph DB, GraphRAG, source of truth, or score.

## Fixture Success

A fixture bundle is useful if a reviewer can quickly see:

- the main decision delta;
- which PR31 labels are implicated;
- which artifacts and review summaries support the projection;
- which conflict remains unresolved;
- why clean structure is not the same as good advice.

## False Certainty And Drift

A fixture bundle is drifting if it:

- implies the advice is correct because the bundle is clean;
- treats provenance as answer quality;
- treats the conflict register as conflict resolution;
- treats the case graph as memory or a graph database;
- uses raw transcript, raw memo, raw revised-answer, provider/model, or private
  reasoning text;
- uses local absolute paths or real archive hashes;
- implies an exporter or runtime feature has shipped.

Current anti-drift sentence:

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

PR63 does not add or approve:

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

## PR64 Review Result

Implemented next as:

```text
PR64 Accountability View Fixture Review v0
```

Review artifacts:

- [Accountability View Fixture Review v0](accountability-view-fixture-review-v0.md)
- [review.json](../../reviews/human/accountability-view-fixture-review-v0/review.json)

PR64 reviewed all three bundles and found:

- 3 pass, 0 revise, 0 exclude;
- `audit_decision_record` has high value on all three fixtures and is ready for
  a later exporter-design decision;
- `provenance_map` and `review_conflict_register` are useful but need more
  fixtures before implementation;
- `case_graph` should hold before implementation because its graph-shaped view
  can become decorative structure or memory drift.

The next slice is PR65 Accountability Implementation Decision Gate v0. PR65 must
remain docs-only and must not implement exporters or runtime behavior.
