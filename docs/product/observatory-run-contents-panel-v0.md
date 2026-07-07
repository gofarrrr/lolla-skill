# Observatory Run Contents Panel v0

Status: implemented UI slice.

Date: 2026-07-07

Decision gate: `proceed_to_observatory_run_inventory_receipt_panel`

Related design:
[Observatory Run Data Visibility Matrix](observatory-run-data-visibility-matrix-v0.md)

## Purpose

This slice turns the visibility-matrix idea into a calm first-read product
surface. The user should not see a giant table of artifacts. The user should
see one plain-language card:

```text
What This Run Contains
```

The card explains that the selected run contains enough material to:

- explain the result;
- teach the reasoning move;
- show the mental models and relations;
- preserve the run for later agent review.

This is not a table and not a technical inventory dump. It is a first-read card
with short status chips and a `View details` disclosure.

## What Changed

The root Observatory workspace now shows a visible run-contents card in the
main start area, before the Outcome section.

The card includes:

- a short explanation of what the run contains;
- compact status chips for Conversation, Interpretation, Outcome, Models,
  Relations, Practice, Receipts, and MD export;
- a plain-language MD export row that points users to the persistent workspace
  header action or to Receipts;
- expandable grouped detail sections.

The detail sections are grouped by user job:

Follow-up browser review removed the duplicate `Download MD` button from this
card. The private Markdown memory file remains available from the visible
workspace header, with hover/help text, and from Receipts where custody and
export context are explained. Run Contents names the export but does not make
the user choose the same action twice in the Outcome flow.

| Group | User-facing purpose |
| --- | --- |
| Understanding | Conversation, interpretation, and Outcome. |
| Teaching and navigation | Mental models, relations, practice, and Map. |
| Memory, receipts, and inspection | Receipts, full transcript export, agent memory Markdown, process brief status, and Advanced Audit. |

## What It Does Not Do

This slice does not expose raw JSON or raw telemetry as first-read product UI.
It does not add a full inventory receipt yet. It does not inspect every archive
file on disk. It summarizes from the existing product workspace payload.

The next slice should build the deeper inventory receipt panel that accounts
for each gathered artifact family with statuses such as:

- available;
- missing;
- not requested;
- private/export only;
- advanced inspection;
- future design.

## Why This Shape

The visibility matrix is the backstage product map. The user-facing UI needs a
different shape:

```text
Here is what this run contains.
Here is why each part matters.
Here is where to go next.
Here is what is private, missing, or inspection-only.
```

That is why the implemented surface uses a card plus disclosure instead of
rendering the matrix.

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

`proceed_to_observatory_run_inventory_receipt_panel`

Reason: the main page now introduces run contents without overwhelming the
user. The next product step is to implement the deeper expandable inventory
receipt behind Receipts/details so the user can account for every gathered
artifact family without seeing a giant table.
