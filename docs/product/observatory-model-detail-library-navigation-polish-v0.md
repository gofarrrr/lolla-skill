# Observatory Model Detail Library Navigation Polish v0

Status: implemented UI slice.

Date: 2026-07-07

Decision gate: `proceed_to_library_graph_scope_decision`

Previous slice:
[Observatory Model Relation Navigation Browser Review](observatory-model-relation-navigation-browser-review-v0.md)

Related context:
[Observatory Model Local Neighborhoods](observatory-model-local-neighborhoods-v0.md)

## Purpose

The previous browser review confirmed that the model-to-relation path works,
but the local library neighborhood could still feel abrupt: after the first
read, the user immediately landed in a list of many relation cards.

This slice keeps the same data and adds a scan layer before the cards.

## Product Rule

Model detail pages are the bridge from the selected run to the reviewed mental
model library.

That bridge should explain:

- what the local neighborhood is;
- how to scan it;
- how to trust it;
- which relation types are available;
- why it is separate from the selected-run Map.

The selected-run Map remains small wayfinding for the current lesson. It is not
the full graph.

## What Changed

The model detail `Library neighborhood` now starts with a compact guide:

- `What this is`: local reviewed neighborhood, not the selected-run Map and not
  the full corpus graph.
- `How to scan`: pick a relation type, then open the relation page for the
  lesson in the connection.
- `How to trust it`: relation edges and confidence are navigation context, not
  proof or an official quality label.

It also adds relation-type jump chips, for example:

```text
Jump to: Ally 3 | Antagonist 3 | Structured tension 3
```

The existing neighbor cards remain available with:

- relation story;
- confidence and extraction context;
- optional source quote;
- `Open model page`;
- `Open relation page`.

## What Did Not Change

This slice does not:

- add a global graph;
- put all canonical models into the workspace first read;
- move library neighbors into the Workspace Models tab;
- expose raw affinity, ranking, embeddings, or JSON;
- treat graph edges as proof;
- claim product proof or human validation.

## Why This Matters

The page now answers the user question before the cards:

```text
Am I looking at this run, this model's local library neighborhood, or the full graph?
```

The answer is:

```text
This is the model's local reviewed library neighborhood.
Use it to navigate relations.
Use the selected-run Map for the current lesson.
Do not treat either as proof.
```

## Browser Expectation

On `/models/authority-bias?case_id=lolla-audit`, the user should see:

- the model first read;
- `Library neighborhood`;
- the three-card guide;
- relation-type jump chips;
- grouped relation cards;
- relation page links.

The Workspace Models tab should remain lighter and should not show the full
neighborhood list.

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

The model detail page now has a clear scan layer between the model first read
and the broader library relation cards.

## Strongest Unresolved Risk

The product still needs a decision on whether the next graph work should be a
filtered local-library graph, a full corpus graph plan, or another selected-run
Map refinement.

## Recommended Next Gate

`proceed_to_library_graph_scope_decision`

Reason: model-detail library navigation is now understandable enough to support
a deliberate graph scope decision instead of collapsing the selected-run Map and
the broader library graph into one surface.
