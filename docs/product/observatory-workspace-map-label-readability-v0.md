# Observatory Workspace Map Label Readability v0

Status: implemented small map-label readability cleanup
Date: 2026-07-06
Decision gate: `ready_for_human_review_with_cleaner_map_labels`

## Purpose

This slice follows the visible Observatory UX audit. The browser check showed
that the main workspace flow is now much clearer, but the Map still leaked raw
contract tokens into the learner-facing reading path.

The problem was small but important:

```text
MENTAL_MODEL
LESSON_NEIGHBORHOOD
SMALL_NEIGHBORHOOD
PARTIAL
```

The specific raw tokens were `MENTAL_MODEL`, `LESSON_NEIGHBORHOOD`,
`SMALL_NEIGHBORHOOD`, and `PARTIAL`.

Those terms are useful to contracts and automation. They are not useful as the
first text a learner sees while trying to understand the map.

## Browser finding

The browser pass opened the portable server-rendered Observatory with an
existing Teacher packet case and checked:

- Models;
- standalone model page;
- Learn;
- Relations;
- Map;
- Receipts.

Models, Learn, Relations, and Receipts were already closer to the desired
progressive flow than the earlier audit. The Map remained the clearest visible
label mismatch: it mixed product navigation with raw object-type, scope, layout,
and source-status terms.

## Change

Visible map labels now translate current contract tokens into product-facing
labels:

| Raw contract token | Visible label |
| --- | --- |
| `mental_model` | Model |
| `lesson_neighborhood` | Lesson map |
| `selected_run_learning_neighborhood` | Selected-run map |
| `small_neighborhood` | Small map |
| `partial` | Partial source coverage |
| `structured_tension` | Structured tension |

Raw contract tokens stay in data attributes for filtering, selection state,
tests, and custody:

```text
raw contract tokens stay in data attributes
visible labels explain the map to the user
```

The selection panel also uses display labels, so clicking a node or edge does
not reintroduce raw terms into the metadata line.

## Why This Matters

The Map is supposed to answer:

```text
what small neighborhood helps me navigate this lesson?
```

It should not ask the user to decode schema vocabulary before they know why the
graph exists. The graph can still preserve machine-readable state underneath,
but the visible layer should speak in product language.

## Boundary

This slice:

- does not run Lolla;
- does not invoke the Lolla skill;
- does not call providers or model APIs;
- does not create new Lolla runs;
- does not mutate archives;
- does not write sidecars;
- does not wire runtime behavior;
- does not edit `observatory/build`;
- does not touch `SKILL.md`;
- does not touch `scripts/skill/*`;
- does not touch `scripts/archive_run.py`;
- does not claim product proof;
- does not claim human validation;
- does not claim answer correctness;
- does not claim advice correctness;
- does not authorize action;
- does not treat graph edges as proof;
- does not treat relation confidence as certification.

## Next

This does not replace the human review packet. It makes the current workspace
cleaner before the review by removing avoidable schema noise from the Map.

Recommended next gate:

```text
ready_for_human_review_with_cleaner_map_labels
```
