# Observatory Library Graph Scope And Coverage Decision v0

Status: decision and coverage slice.

Date: 2026-07-08

Decision gate: `proceed_to_observatory_model_detail_visual_neighborhood_v0`

Machine-readable decision:
[Observatory library graph scope decision JSON](observatory-library-graph-scope-decision-v0.json)

## Purpose

This slice stops new UI work long enough to reconcile what Observatory already
shows, what it accounts for, what stays hidden or exported, and which graph
surface should come next.

The correction is explicit:

```text
Observatory is the portable presentation surface after a selected run.
Teacher is not a separate main product path right now.
Teacher lives inside Observatory as Learn, Models, Relations, Map, and Receipts.
```

That means the next product decision is not "build a full graph." It is:

```text
Which graph mode is this surface allowed to show, at what depth, and with what
non-claim?
```

## Current Product Thesis

The current product thesis is:

```text
selected run is the anchor
outcome is the first read
Teacher is the practice layer
models are reusable concepts
relations are model-pair lessons
map is navigation
receipts are accountability
Download MD is private agent memory
Advanced Audit is technical inspection
```

This decision keeps that thesis and prevents the graph/library work from
turning Observatory back into an all-data dashboard.

## What Is Already Done

The original Mental Model Teacher product-surface package is reviewable through
PR-P11.

| Slice | State | Product meaning |
| --- | --- | --- |
| PR-P1 through PR-P10 | published | PRD, substrate inventory, contracts, pilot builders, renderers, lesson graph, static graph prototype, three-case pilot, and UX review packet exist. |
| PR-P11 | package gate exists | The package is staged for review with explicit non-claims and no runtime authorization. |
| PR-P12 | deferred | Full-corpus graph planning is not the next default surface. |
| PR-P13 | deferred | Full-corpus graph pilot is not authorized by the package gate. |

The PR-P11 package gate remains important because it says the package is
reviewable, not product-proof, human-validated, answer-correct, or
advice-correct.

Related package sources:

- [Mental Model Teacher Product Surface and Visual Library PRD](mental-model-teacher-product-surface-and-visual-library-prd-v0.md)
- [Mental Model Teacher Product Surface Package Gate](mental-model-teacher-product-surface-package-gate-v0.md)
- [Mental Model Teacher Product Surface Package Manifest](mental-model-teacher-product-surface-package-manifest-v0.json)

## Count Reconciliation

The 48, 36, and 29 counts are different accounting levels, not contradictory
answers.

| Count | Source | Meaning | Product use |
| --- | --- | --- | --- |
| 48 broad visibility-matrix families | [Observatory Run Data Visibility Matrix](observatory-run-data-visibility-matrix-v0.md) | The broad universe of run, archive, substrate, telemetry, export, operator, and future-design families that must be accounted for. | Source-of-truth accountability universe. Do not show all 48 as product UI. |
| 36 data-exposure audit items | [Observatory Data Exposure Audit JSON](observatory-data-exposure-audit-v0.json) | A machine-readable rollup used by the data-exposure audit to assign desired layers. | Planning bridge between broad substrate and product layers. |
| 29 current run-inventory UI families | [Observatory Run Inventory Receipt Panel](observatory-run-inventory-receipt-panel-v0.md) | The grouped Receipts inventory currently implemented in Observatory. | Current user-accountable receipt surface. |
| 8 first-read product-path families | [Observatory Content Progression PRD](observatory-content-progression-prd-v0.md) | The subset allowed to compete for normal product attention: selected run context, Outcome, strongest pressure, Teacher lesson, practice rep, model pages, relation pages, and selected-run map. | First-read product path. |

The rule is:

```text
48 is the accountability universe.
36 is the prior exposure-audit rollup.
29 is the current Receipts/UI inventory.
8 is the first-read product path.
```

The product should account for gathered data, but it should not flatten all
counts into one screen.

## Graph Modes

Observatory now needs five graph modes with separate jobs.

| Mode | Status | User question | Surface | Product rule |
| --- | --- | --- | --- | --- |
| Selected-run learning map | present | What did this run use, and where can I navigate inside this lesson? | Map | Small selected-run neighborhood only. Graph edges are navigation, not proof. |
| Model-detail reviewed local neighborhood | present as cards, not visual graph | I clicked one model. What reviewed neighbors are directly connected to it, and why? | Model detail | Show reviewed relation cards and relation links. Do not imply these were selected by the run. |
| Model-detail visual neighborhood | recommended next UI build | Can I see this one model's direct reviewed neighborhood as a small map? | Model detail | Visualize the already-reviewed local neighborhood only. Do not build the full corpus graph. |
| Filtered library graph | future | Can I browse reviewed library relations by search, family, model, or relation type? | Future library surface inside Observatory | Needs separate filtering, density, and missingness design before implementation. |
| Full corpus graph | future, not first surface | Can I inspect the entire topology? | Future advanced/library exploration | Not the first user surface and not proof of relation truth. |

This resolves the "only one relation" concern without overbuilding. The
selected-run Map can remain small because the model-detail page already shows a
broader reviewed local neighborhood. The next build should make that local
neighborhood visual, not global.

## Data Exposure Decision

Every gathered family gets a layer. The layer decides how the user encounters
it.

| Layer | What goes there | Current decision |
| --- | --- | --- |
| Default first read | Selected run context, Outcome, strongest pressure or compact challenge, availability status, visible `Download MD` action. | Keep concise and readable. Do not add graph substrate or transcript bodies here. |
| Primary product surfaces | Learn, Models, Relations, Map, Receipts. | Keep each surface focused on one job. |
| Expandable product detail | Model detail pages, relation detail pages, source/custody disclosure, reviewed model-neighborhood cards. | This is where durable library knowledge belongs after a click. |
| Explicit export | Conversation memory Markdown through `Download MD`. | This is the current agent-memory path. |
| Optional technical inspection | Advanced Audit, extraction detail, usage, run events, graph survival, evaluation artifacts. | Reach from Receipts or Advanced Audit, not the learning path. |
| Operator-only inspection | Private ledgers, operator logs, provider-private bodies, raw rankings, raw vectors, local paths. | Account for existence safely; do not render bodies in product UI. |
| Future design | Filtered library graph, full corpus graph, semantic-neighbor browsing, V60 affordance pages. | Requires later gates. |
| Private hidden | Raw 1:1 transcript and private/operator bodies. | Raw transcript belongs only in explicit private Markdown export or explicit inspection, not normal first-read UI. |

## Specific Decisions

1. Observatory remains the portable product surface for the selected run.
2. Teacher remains the practice layer inside Observatory, not a separate main UI
   path for this phase.
3. Outcome remains the first read.
4. Learn owns the case-anchored practice rep.
5. Models own reusable model explanations and local reviewed neighborhoods.
6. Relations own model-pair lessons.
7. Map owns the selected-run learning neighborhood only.
8. Receipts own accountability, missingness, inventory, and non-claims.
9. Download MD is the current private agent-memory export path.
10. The raw 1:1 transcript stays out of normal UI and appears only through an
    explicit private Markdown export or explicit inspection.
11. Model-detail visual neighborhoods should come before any filtered or full
    corpus graph.
12. Graph edges are navigation context, not proof.
13. Embedding similarity is not validated relation semantics.

## Recommended Next PR

Recommended next PR:

```text
Observatory Model Detail Visual Neighborhood v0
```

That PR should answer:

```text
I clicked Authority Bias. What else is directly connected to it, and why?
```

It should:

- use the already-existing reviewed model-detail neighborhood data;
- render a small local visual neighborhood on model detail pages;
- keep the readable neighbor cards and relation-page links;
- distinguish selected-run relations from local library relations;
- avoid a full-corpus graph and do not build the full corpus graph;
- avoid raw affinity, raw rankings, embeddings, and graph-proof language;
- preserve missingness and non-claims.

It should not change runtime behavior, default skill behavior, archives, provider
calls, or compiled Observatory build output.

## Boundary

This decision:

- does not run Lolla;
- does not invoke the Lolla skill;
- does not call providers or model APIs;
- does not create a new run;
- does not generate sidecars;
- does not wire runtime or default skill behavior;
- does not mutate archives;
- does not edit `observatory/build`;
- does not touch `SKILL.md`;
- does not touch `scripts/skill/*`;
- does not touch `scripts/archive_run.py`;
- does not claim product proof;
- does not claim human validation;
- does not claim answer correctness;
- does not claim advice correctness;
- does not authorize automatic action;
- does not treat graph edges as proof;
- does not treat embedding similarity as validated relation semantics.

## Strongest Useful Signal

The product can now explain why the selected-run Map is intentionally small
while still giving users a path from one model to the broader reviewed relation
library.

## Strongest Unresolved Risk

If the next UI slice skips directly to a filtered or full-corpus graph, the
product will blur selected-run evidence, reviewed library navigation, and future
exploration into one surface. The safer next build is the model-detail visual
neighborhood.
