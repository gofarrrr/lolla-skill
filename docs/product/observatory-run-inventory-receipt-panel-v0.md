# Observatory Run Inventory Receipt Panel v0

Status: implemented UI slice.

Date: 2026-07-07

Decision gate: `proceed_to_model_detail_local_neighborhoods_or_inventory_refinement`

Related design:
[Observatory Run Data Visibility Matrix](observatory-run-data-visibility-matrix-v0.md)

Previous slice:
[Observatory Run Contents Panel](observatory-run-contents-panel-v0.md)

## Purpose

This slice turns the visibility matrix into an expandable receipt inside the
Observatory Receipts surface.

The user problem was:

```text
We gather a lot of data, but the user cannot tell what exists, what is being
shown, what is only in export or inspection, and what is absent or future.
```

The receipt answers that without throwing a table at the user. It starts with
four counts:

- Accounted for;
- Product path;
- Export or inspection;
- Missing or future.

Then it exposes grouped cards for the deeper read.

## What Changed

The Receipts surface now includes a `Run inventory receipt` block.

It accounts for run data families in these groups:

| Group | Examples |
| --- | --- |
| First-read product path | selected run context, Outcome, strongest pressure, Teacher lesson, practice, model pages, relation pages, selected-run map. |
| Conversation and interpretation | Conversation transcript, Conversation Understanding, reasoning trace, suppressed or unadjudicated signals. |
| Memory, receipts, and sidecars | Agent memory Markdown, memo artifact, Process brief sidecar, source custody and non-claims. |
| Technical and operator inspection | result object, agent result object, evaluation artifact, run events, usage telemetry, graph survival, private tables, operator log. |
| Library substrate accounted for | canonical model Markdown, activation/intervention curation, relation semantics, relationship graph substrate, knowledge graph and embeddings. |

Each card says:

- what the item is;
- how it comes into the system;
- what it helps the user or operator understand;
- what action the user should take;
- which disclosure layer it belongs to.

This is not a table and not a raw telemetry dump. It is an expandable receipt.

## Compact Pressure Fallback

The selected archived launch run exposed a product bug: older `delta_card`
payloads can store the top pressure as `challenge_statement` rather than
`description`, `summary`, `finding`, or `title`.

The product adapter now treats `challenge_statement` as a valid compact
pressure source. That means the Outcome surface can show the actual pressure
when the archive has it instead of saying no compact pressure summary is
available.

## Why This Shape

The user should not start with the archive, the graph, a technical audit, or a
giant matrix. The first screen should still say what the run contains and where
to go next.

The inventory receipt belongs under Receipts because it answers:

```text
What exists here?
What is visible as product?
What is private export?
What is technical inspection?
What was not requested?
What is only future design?
```

This keeps the product path readable while preserving accountability for the
data we gather.

## Important Interpretation

If `Conversation transcript` is available, the run has the source conversation
or captured turns. The transcript remains a private/export layer, not first-read
UI.

If `Conversation Understanding` is available, the extraction/interpretation
layer exists.

If `Process brief sidecar` is `not_requested`, that means the richer Decision
Work/process brief sidecar was not generated for the run. It is not the same as
missing conversation.

If `Knowledge graph and embeddings` is `future_design`, that means the
substrate exists or may exist, but it is not yet a reviewed product navigation
surface. Embedding similarity is not validated relation semantics.

## What This Still Does Not Solve

This slice does not build the missing richer graph experience. It only accounts
for the graph and library substrate.

The model pages still need a local-neighborhood design so a model can show more
than the one selected-run relation when reviewed substrate supports it.

The receipt does not render raw canonical Markdown. Model pages should continue
to translate canonical source into clean user-facing sections.

The receipt does not create or request Decision Work. It only shows whether a
process brief sidecar is available, absent, or not requested.

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

`proceed_to_model_detail_local_neighborhoods_or_inventory_refinement`

Reason: Observatory now has a visible first-read contents card and a deeper
Receipts inventory. The next product question is whether to improve model detail
pages with reviewed local neighborhoods from the relationship graph, or to
refine the receipt after user review of the current grouped inventory.
