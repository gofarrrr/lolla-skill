# Observatory Relation Page Library Fallback v0

Status: implemented UI slice.

Date: 2026-07-07

Decision gate: `proceed_to_model_relation_navigation_browser_review`

Previous slice:
[Observatory Outcome Browser Review](observatory-outcome-browser-review-v0.md)

Related context:
[Observatory Model Local Neighborhoods](observatory-model-local-neighborhoods-v0.md)

## Purpose

This slice finishes the clickable path that the model-neighborhood work opened.

Before this slice, a model page could show `Reviewed Neighbors`, but each
neighbor card only linked to the other model. That helped the user see that the
library was richer than one selected-run edge, but it did not let the user open
the relation itself.

Now the user can click:

```text
Mental model -> Reviewed Neighbors -> Open relation page
```

The relation-page library fallback lets Observatory explain reviewed model
pairs even when that pair was not attached to the selected-run Teacher packet.

## Product Rule

The rule is:

- selected-run relation pages still win;
- relation semantics first;
- relationship graph fallback;
- graph edges are navigation, not proof;
- no embeddings as validated relation semantics;
- no raw JSON or affinity scoring in product UI.

This keeps the run-specific teaching path honest while still making the broader
reviewed mental-model library reachable.

## What Changed

Model `Reviewed Neighbors` cards now include two actions:

- `Open model page`;
- `Open relation page`.

The relation route can now render a library relation page from relation IDs in
this shape:

```text
<source-model-id>__<target-model-id>__<relation-type>
```

For example:

```text
/relations/authority-bias__critical-thinking__antagonist?case_id=lolla-audit
```

If the selected run already has that relation page, Observatory uses the
selected-run relation page. If not, it tries reviewed relation semantics. If no
relation-semantics item exists, it tries a curated relationship-graph fallback.

## User-Facing Page Shape

Library fallback relation pages show:

- model pair title;
- `Library Relation Context`;
- plain-language story;
- why the relation matters;
- misread risk;
- practice prompt;
- links to both model pages;
- optional source quote/reference;
- taxonomy, confidence, custody, missingness, and non-claims behind disclosure.

The page explicitly says that a library relation is not selected-run proof.

## Data Sources

| Source | Product use | What is not exposed |
| --- | --- | --- |
| `data/curation/relation_semantics/<model_id>.json` | Primary source for reviewed library relation pages. | Unsupported speculation, raw extraction clutter as the first read. |
| `data/relationship_graph.json` | Fallback only when relation semantics are absent. | `composition_affinity`, raw ranking, raw affinity rationale as truth. |
| `data/knowledge_graph.json` | Display names and model-page links. | Full topology as the first user surface. |

## What We Show

We show:

- the source and target model names;
- relation type;
- plain-language rationale or graph description;
- confidence as curation status;
- extraction type as source context;
- source artifacts;
- non-claims.

This is useful because the user can now ask:

```text
I see that these models are connected. What is the lesson in that connection?
```

## What We Do Not Show

We do not show:

- raw relationship graph affinity;
- raw graph ranking;
- embedding neighbors;
- the full corpus graph;
- raw JSON blobs;
- local filesystem paths;
- graph survival or evaluation internals;
- relation confidence as proof;
- relation pages as answer/advice correctness.

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

## Strongest Useful Signal

A user can now move from a mental model to the broader reviewed relation
library without leaving Observatory or seeing raw substrate files.

## Strongest Unresolved Risk

The page is still a readable relation fallback, not the final graph experience.
The next check should use a browser to confirm whether the path from Models to
Reviewed Neighbors to relation pages feels obvious enough before expanding the
graph surface.

## Recommended Next Gate

`proceed_to_model_relation_navigation_browser_review`

Reason: the core clickable model-to-relation fallback now exists. The next step
should be a browser pass over the actual navigation path before adding more
graph or library UI.
