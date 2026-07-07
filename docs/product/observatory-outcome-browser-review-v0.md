# Observatory Outcome Browser Review v0

Status: implemented browser-review slice.

Date: 2026-07-07

Decision gate: `proceed_to_relation_page_library_fallback`

Previous slice:
[Observatory Outcome Progressive Disclosure](observatory-outcome-progressive-disclosure-v0.md)

Related context:
[Observatory Run Contents Panel](observatory-run-contents-panel-v0.md)

## Purpose

This slice browser-reviewed the current Outcome flow against two practical
states:

- a Teacher-backed run, where Learn, Models, Relations, Map, and Receipts can
  all render;
- a run-only fallback, where the run result exists but no Teacher learning
  packet is attached.

The question was not whether Observatory has enough information somewhere in
the code. The question was what the page actually shows when opened and clicked
like a user.

## What Was Checked

The browser review checked:

- the root workspace;
- Outcome first-read order;
- the recommended continuation from Outcome;
- Teacher-backed continuation into Learn;
- run-only continuation into Receipts;
- unavailable Teacher surfaces;
- the private Markdown export route;
- repeated `Download MD` affordances.

The Teacher-backed run showed the answer first, then one recommended
continuation into Learn. It also kept the learning surfaces available:
model pages, relation pages, the selected-run map, and Receipts.

The run-only fallback showed the answer first and then sent the user to
Receipts with a missingness explanation. It did not fake a lesson, model page,
relation page, or graph when the Teacher packet was absent.

## Product Fix

Browser review found one avoidable source of confusion: the main page repeated
`Download MD` too often.

The chosen rule is:

- keep header `Download MD` visible as the always-available private export;
- keep Receipts `Download MD` because Receipts explains custody, missingness,
  and non-claims;
- Run Contents no longer owns a duplicate `Download MD` button.

Run Contents still names the agent-memory Markdown export as part of what the
run contains, but it points users to the header action or Receipts instead of
making the same action compete with Outcome.

## Current User Flow

For a Teacher-backed run:

```text
Outcome -> Practice the reasoning move -> Learn -> Relations / Map / Receipts
```

For a run-only fallback:

```text
Outcome -> Check what is available -> Receipts
```

That split matters. The page should not claim a Teacher product surface exists
when the source artifact is missing.

## What This Does Not Solve

This slice does not solve the broader model-library problem. Some relation
pages are still only run-specific and can feel thin when compared with the
canonical mental-model substrate. The next useful product slice should make
relation/model fallback behavior explicit: when run-specific relation data is
small, Observatory should be able to point to reviewed library-level model and
relation material without treating graph edges or embeddings as proof.

This slice also does not implement a global mental-model graph. That remains a
later product surface after the information hierarchy is stable.

## Boundary

This slice:

- does not run Lolla;
- does not invoke the Lolla skill;
- does not call providers or model APIs;
- does not create a new run;
- does not generate sidecars;
- does not wire skill runtime behavior;
- does not mutate archives;
- does not edit `observatory/build/*`;
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

The Outcome flow now has a browser-checked split between “Teacher surfaces are
available” and “only the run result is available.” That lets the UI stay honest
without going blank.

## Strongest Unresolved Risk

The relation/model learning surfaces can still feel too narrow when the
selected run exposes only a tiny local neighborhood. The next slice should
define how Observatory borrows from reviewed library-level mental model and
relation material without duplicating product surfaces or overclaiming
relation truth.

## Recommended Next Gate

`proceed_to_relation_page_library_fallback`

Reason: the main Outcome path is now browser-checked and the duplicate export
button has been simplified. The next product gap is not another export button;
it is making sparse run-specific model/relation surfaces feel connected to the
broader reviewed mental-model library.
