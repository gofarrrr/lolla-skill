# Observatory Teacher Route Consolidation v0

## Purpose

This slice removes the visible duplicate Teacher UX path from the portable
Observatory.

The prior state had two user-facing ways to read the same learning material:

- `/workspace?case_id=<id>#learn` as the selected-run Observatory product flow;
- `/teacher-learning` as an older all-in-one Teacher Learn page.

That made it too easy for the product to feel like two applications stitched
together. The route family now treats the selected-run workspace as the single
visible product path.

## Decision

`/teacher-learning` is now a compatibility entry point. It redirects to:

```text
/workspace?case_id=<selected-case-id>#learn
```

The selected-run workspace remains the canonical visible Observatory product
flow:

```text
Outcome -> Learn -> Models -> Relations -> Map -> Receipts
```

This is now the single visible product path for Teacher learning inside
Observatory.

The legacy Teacher Learn renderer remains in code only as a historical fixture
while older tests and docs are migrated. It is no longer the HTTP product route.

## What Changed

- Audit navigation now links `Learn` to `/workspace#learn`.
- The injected fallback `LEARN` button now links to `/workspace#learn`.
- The injected case-surface toolbar now links to:
  - `/workspace#learn`;
  - `/workspace#models`;
  - `/workspace#relations`;
  - `/workspace#map`;
  - `/workspace#receipts`.
- `/teacher-learning` responds with a redirect to the selected-run workspace
  Learn surface.
- `/api/case/<id>/teacher-learning` remains unchanged as the read-only packet
  adapter route.

## User Flow

The user now has one visible path:

1. Open Observatory.
2. Read Outcome first.
3. Switch to Learn for the reasoning move.
4. Open Models for canonical mental model pages.
5. Open Relations for model-pair lessons.
6. Use Map as wayfinding.
7. Use Receipts and Advanced Audit only for inspection.

This keeps Teacher inside Observatory without maintaining two different page
hierarchies.

## Compatibility Notes

Existing bookmarks to `/teacher-learning` still land in Observatory. Because URL
fragments such as `#models` are not sent to the server, legacy fragment-specific
bookmarks are redirected to the Learn surface. New links emitted by Observatory
use workspace anchors directly.

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

## Remaining Risk

The old `_render_teacher_learning_html` function still exists as a direct
renderer for historical coverage. The HTTP route no longer exposes it as the
product page. A later cleanup can either delete it or convert its tests to
workspace-surface assertions once the old docs are fully retired.

The next product risk is not route duplication; it is information hierarchy
inside the remaining workspace surfaces, especially Receipts expansion and Map
filter empty states.

## Decision Gate

Recommended gate:

`proceed_to_observatory_workspace_information_hierarchy_review`
