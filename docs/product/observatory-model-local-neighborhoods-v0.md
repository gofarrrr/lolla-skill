# Observatory Model Local Neighborhoods v0

Status: implemented UI slice.

Date: 2026-07-07

Decision gate:
`proceed_to_relation_page_library_fallback_or_graph_neighborhood_refinement`

Related design:
[Observatory Run Inventory Receipt Panel](observatory-run-inventory-receipt-panel-v0.md)

Previous slice:
[Observatory Run Contents Panel](observatory-run-contents-panel-v0.md)

## Purpose

This slice fixes a product mismatch in the model detail experience.

Before this slice, a selected-run model page could make the mental model world
look artificially small. A run might show one selected-run relation, even when
the reviewed library substrate already has several source-backed relations for
the same model.

The new page shape separates three things:

- selected-run lesson context;
- local library neighborhood;
- later graph experience.

The user can now click a mental model and see a clean `Reviewed Neighbors`
section before opening the deeper source and boundary disclosures.

## What Changed

Model detail pages now include a `Reviewed Neighbors` section.

For a model such as `authority-bias`, Observatory shows:

- direct allies from reviewed relation semantics;
- direct antagonists from reviewed relation semantics;
- direct structured tensions from reviewed relation semantics;
- a count of reviewed relation-semantics neighbors shown;
- a count of direct relationship-graph edges accounted for;
- a visible non-claim that this is navigation, not proof.

The section is not shown on the model index cards. The model index stays light:
name, first-read meaning, use cue, mislead cue, and the action to open the
model page.

## Data Sources

The user-facing section uses:

| Source | Product use | What is not exposed |
| --- | --- | --- |
| `data/curation/relation_semantics/<model_id>.json` | Primary source for reviewed neighbor cards, relation type, rationale, confidence, extraction type, and optional source quote. | Raw extraction metadata as a dominant UI, unsupported speculation, internal curation sprawl. |
| `data/relationship_graph.json` | Accounting count and fallback only when relation semantics are absent. | `composition_affinity`, raw ranking, raw affinity rationale as truth. |
| `data/knowledge_graph.json` | Library fallback model pages for neighbor models not present in the selected run. | Full topology as the first user surface. |
| `data/model_sources/*.md` | Source custody for library fallback model pages. | Canonical model Markdown is still source material, not raw UI. |

## Information Flow

The intended progression is:

1. The user starts in the selected-run workspace.
2. The user opens a model from the Models surface or from a relation/map link.
3. The model page starts with the reusable model explanation and run-context cue.
4. The user sees `Reviewed Neighbors` as a local library neighborhood.
5. The user can click a neighbor model page.
6. If that neighbor was not part of the selected run, Observatory renders a
   library fallback model page from the canonical/knowledge graph substrate.
7. Source, status, missingness, and non-claims remain available in disclosures.

This creates an understandable path from a run-specific lesson into the broader
model library without pretending the broader library was selected by the run.

## What We Show

We show:

- the neighbor model display name;
- the relation type label;
- the plain-language rationale;
- confidence as curation status;
- extraction type as source context;
- optional source quote behind a disclosure;
- a link to the neighbor model page;
- source artifact names behind a disclosure;
- non-claims behind a disclosure.

This is first-class product navigation because it helps a user answer:

```text
What other mental models are close to this one, and why?
```

## What We Do Not Show

We do not show:

- raw relationship graph affinity as truth;
- raw relationship graph ranking;
- embedding neighbors;
- the full corpus graph;
- unsupported relation speculation;
- local filesystem paths;
- raw canonical Markdown as the page UI;
- raw JSON blobs;
- technical graph survival or evaluation internals.

Those may remain useful for export, inspection, or later graph work, but they
are not the first-read model detail experience.

## Why This Is Not The Final Graph

This slice is not the visual graph. It is the readable, clickable local
neighborhood that should exist before a graph is useful.

The selected-run map remains a small run-specific map. The new model
neighborhood is broader library navigation. A future graph can use this same
distinction:

- selected-run map: what this run used;
- local library neighborhood: what this model connects to;
- full corpus graph: optional later exploration.

## Boundary

This slice:

- does not run Lolla;
- does not invoke the Lolla skill;
- does not call providers or model APIs;
- does not create a new run;
- does not generate sidecars;
- does not wire skill runtime behavior;
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

## Recommended Next Gate

`proceed_to_relation_page_library_fallback_or_graph_neighborhood_refinement`

Reason: model pages now have a reviewed local neighborhood and clickable
library fallback pages. The next decision is whether relation pages should get a
similar library fallback, or whether to refine the neighborhood into a visual
graph prototype after another user review pass.
