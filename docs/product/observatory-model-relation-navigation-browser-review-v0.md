# Observatory Model Relation Navigation Browser Review v0

Status: implemented browser-review slice.

Date: 2026-07-07

Decision gate: `proceed_to_model_detail_library_navigation_polish`

Previous slice:
[Observatory Relation Page Library Fallback](observatory-relation-page-library-fallback-v0.md)

Related context:
[Observatory Data Exposure Audit](observatory-data-exposure-audit-v0.md)

## Purpose

This slice browser-reviewed the model-to-relation path after the relation-page
library fallback landed.

The question was:

```text
Can a user move from the selected run to a mental model, then from that model
to a broader reviewed relation, without confusing that relation for selected-run
evidence or graph proof?
```

This review does not add graph UI. It records what the browser now shows and
which product rule should govern the next UI slice.

## What Was Clicked

The browser review opened and checked:

- `/workspace?case_id=lolla-audit#models`;
- `/models/authority-bias?case_id=lolla-audit`;
- `/relations/authority-bias__wysiati__ally?case_id=lolla-audit`;
- `/relations/authority-bias__critical-thinking__antagonist?case_id=lolla-audit`;
- `/relations/analogies-and-metaphors__representativeness-heuristic__antagonist?case_id=lolla-audit`;
- `/relations/authority-bias__first-principles-thinking__antagonist?case_id=lolla-audit`;
- `/workspace?case_id=lolla-audit#map`.

The review also checked the Map search/filter empty state.

## Browser Findings

| Surface | What the browser showed | Product judgment |
| --- | --- | --- |
| Workspace Models | Three selected-run model cards with `Open model page`. | Correct. The first read should stay selected-run and not turn into the full library. |
| Model detail | `Authority Bias` first read, run role, and a `Library neighborhood` with reviewed neighbors. | Useful. This is the right bridge from selected-run learning into the broader model library. |
| Model detail neighbors | Neighbor cards include `Open model page` and `Open relation page`. | Correct path. The user can now ask what a connection means, not only jump to another model. |
| Library relation from relation semantics | Relation page opens with `Library Relation Context`, plain-language story, misread risk, practice prompt, source quote, and non-claims. | Good. It is clear that this is reviewed library knowledge, not selected-run evidence. |
| Library relation from relationship graph fallback | Relationship-graph relation page renders without affinity or ranking internals. | Acceptable fallback. It should remain secondary to relation semantics. |
| Selected-run relation | `Authority Bias and First Principles Thinking` opens without `Library Relation Context` and keeps the Teacher relation story. | Correct. Selected-run relation pages still win. |
| Map | Small selected-run graph with search, relation filter, reset, and `edges are navigation, not proof`. | Correct boundary. This is not the full mental-model graph. |

## What We Are Showing Now

The current product hierarchy is:

1. Workspace Models shows selected-run models only.
2. Model detail shows the reusable model page and its local reviewed library
   neighborhood.
3. Library relation pages explain broader reviewed model pairs.
4. Selected-run relation pages remain the lesson-specific relation story.
5. Map remains the selected-run wayfinding graph.

This matters because the user can now read:

```text
This run used Authority Bias.
Authority Bias has a broader reviewed local neighborhood.
One neighbor is WYSIATI.
The Authority Bias/WYSIATI relation has a story, risk, prompt, and source.
That does not prove the current run used that relation.
```

## What We Are Not Showing By Default

The browser review confirmed that the first path does not default to:

- all 222 canonical mental models;
- the full corpus graph;
- raw canonical Markdown;
- raw JSON;
- relationship-graph affinity or ranking;
- embedding similarity;
- graph survival or eval internals;
- Product Delta internals;
- relation confidence as proof.

Those can support product-safe pages, but they should not become the default
first read.

## Product Rule

Keep three relation scopes distinct:

| Scope | User meaning | Where it belongs |
| --- | --- | --- |
| selected-run relation | The relation used by this lesson. | Relations tab, selected-run relation page, selected-run Map. |
| local library relation | A reviewed relation connected to a model page. | Model detail neighborhood and library fallback relation pages. |
| global graph relation | Full corpus navigation or search. | Future library graph, not current Map. |

The next UI work should improve the local library relation path before adding a
global graph.

## UX Risk

The path works, but discoverability still depends on opening a model detail
page. The workspace Models tab does not yet hint that a model page contains a
local library neighborhood.

The model page also exposes a lot of neighbor cards once the user reaches the
library section. The next slice should make that section easier to scan before
adding more graph surface.

## Recommended Next UI Slice

`proceed_to_model_detail_library_navigation_polish`

Recommended work:

- keep Workspace Models selected-run simple;
- add a clearer model-detail summary of available library neighbors;
- make relation-type switching or scanning easier inside the model detail page;
- keep `Open relation page` available for each reviewed neighbor;
- do not move the full corpus graph into the selected-run Map;
- do not expose raw affinity, embeddings, or graph proof language.

## Boundary

This review:

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

The browser now supports a coherent product path from selected-run model to
reviewed library relation while keeping selected-run relation pages distinct.

## Strongest Unresolved Risk

Users may still expect the Map to contain all known model relations. The UI
needs clearer separation between the selected-run Map and model-detail library
neighborhoods before a full graph is added.
