# Observatory Workspace Map Interaction Slice v0

Status: portable selected-run Map interaction
Date: 2026-07-06
Decision gate: `proceed_to_observatory_workspace_product_flow_review`

## Purpose

This slice turns the workspace Map from a static summary into an interactive selected-run Map.

The prior workspace already had durable model and relation pages. The remaining
UX problem was that the Map still behaved like a list of links rather than a
place to inspect the relationship neighborhood. Users could move through the
page, but they could not search, filter, select, and understand the graph as a
small learning surface.

This slice adds an Observatory-native graph workbench to the portable Python
renderer.

## What Changed

The workspace Map now renders:

- node search;
- relation-type filters;
- selected node or edge panel;
- SVG node and edge targets;
- visible result counts;
- durable model and relation page links;
- graph scope and layout chips;
- source custody;
- missingness;
- explicit graph non-claims.

The Map is still selected-run scoped. It is not a full corpus graph and it is
not a proof surface.

## User Flow

The intended flow is:

```text
Open selected run -> scan Outcome/Learn -> inspect Models/Relations -> use Map to explore the neighborhood -> open model/relation page from the selection panel
```

Inside the Map:

1. The user searches by model name, model id, or role.
2. The user filters by relation type.
3. The user selects a node or edge.
4. The side panel explains what is selected.
5. The side panel links to the durable model or relation page.

This keeps graph exploration from becoming accidental navigation while still
making model and relation pages one click away.

## Product Interpretation

The Map answers:

```text
What model neighborhood is relevant to this selected run?
```

It does not answer:

```text
Which relation is objectively true?
Which answer is correct?
Which advice should be approved?
Which action should be authorized?
```

Graph edges are navigation and teaching context, not proof.

## Route And Rendering Boundary

The Map lives inside:

```text
/workspace?case_id=<selected-case-id>#map
```

Model and relation detail pages remain:

```text
/models/<id>?case_id=<selected-case-id>
/relations/<id>?case_id=<selected-case-id>
```

The renderer stays in:

```text
observatory/serve_result.py
```

No compiled SPA source is required.

## Boundary Confirmation

This slice:

- does not run Lolla;
- does not invoke the Lolla skill;
- does not call providers or model APIs;
- does not create new Lolla runs;
- does not wire runtime behavior;
- does not mutate archives;
- does not write sidecars;
- does not edit `observatory/build`;
- does not edit observatory/build;
- does not touch `SKILL.md`;
- does not touch `scripts/skill/*`;
- does not touch `scripts/archive_run.py`;
- does not claim product proof;
- does not claim human validation;
- does not claim answer correctness;
- does not claim advice correctness;
- does not authorize action;
- does not treat graph edges as proof;
- does not treat embedding similarity as validated relation semantics.

## Stop Line

This PR stops before:

- full corpus graph;
- full corpus mental model library;
- runtime integration;
- default-on Conversation Understanding generation;
- product readiness claims;
- human validation claims;
- answer/advice correctness claims;
- action authorization.

Recommended next gate:
`proceed_to_observatory_workspace_product_flow_review`
