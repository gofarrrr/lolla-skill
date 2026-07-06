# Observatory Workspace First-Read Progression v0

Status: implemented small first-read progression cleanup
Date: 2026-07-06
Decision gate: `ready_for_human_review_with_clearer_first_read_path`

## Purpose

This slice follows the visible Observatory UX audit. The workspace had become
much clearer page by page, but the first-read journey still asked the user to
infer too much from tab names.

The user should not have to guess whether this is:

- a run result page;
- a Teacher lesson page;
- a mental model library;
- a relation browser;
- a graph;
- an audit surface.

The first screen now presents these as one reading path:

```text
Outcome -> Learn -> Models -> Relations -> Map -> Receipts
```

## Browser finding

The browser pass opened the portable server-rendered Observatory and checked
Outcome, Learn, Models, Relations, Map, and Receipts.

The strongest remaining mismatch was not a broken page. It was progression:

- the sidebar said `Surface Homes`, which named tabs but did not explain what
  each surface was for;
- the start card mentioned Outcome, Learn, Models, and Receipts but skipped
  Relation and Map as explicit steps;
- the user could click the top navigation, but the page did not clearly narrate
  why those surfaces exist or in what order to read them.

## Change

The sidebar now has a `Reading Path` panel. It is clickable and explanatory:

| Step | Surface | User question |
| --- | --- | --- |
| 1 | Outcome | What changed in the run? |
| 2 | Learn | What reasoning move can I practice? |
| 3 | Models | Which tools explain the move? |
| 4 | Relations | How do the models interact? |
| 5 | Map | Where can I jump next? |
| 6 | Receipts | What is present or not claimed? |

The Start Here panel now shows the same six-step progression with links.
Relation and Map are no longer skipped in the first-read path.
Its visible frame starts with the same instruction as the page: Start from the selected run,
then move through the learning and inspection layers.

The active surface script also updates Reading Path and Start Here active
states, so the current surface stays visible after the user clicks through.

## Product Rule

This keeps the top-level view general:

```text
what happened -> what can I learn -> what models matter -> how they relate
-> where can I navigate -> what can I trust or inspect
```

Detailed source, missingness, and audit material remains behind Receipts and
disclosures. The path introduces what each information layer is for before
asking the user to open the layer.

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

Recommended next gate:

```text
ready_for_human_review_with_clearer_first_read_path
```

The remaining review question is whether a real user understands the workspace
journey without verbal explanation from us.
