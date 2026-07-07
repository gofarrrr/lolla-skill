# Observatory Receipts Technical Inspection Disclosure

Status: implemented UX reduction slice.

Date: 2026-07-07

Decision gate: `proceed_to_observatory_data_exposure_audit`

## Purpose

The latest browser audit showed that Receipts are the right home for custody,
missingness, non-claims, and technical inspection. The remaining risk is that
technical audit links can still look like a normal next product step.

This slice makes Receipts more explicitly custody-first. Technical audit links
remain present, but they now sit behind a closed optional disclosure.

## UX Change

Receipts now starts with:

- trust summary;
- status chips;
- visible non-claims.

The user-facing Receipts surface does not ask the user to review the product
or open a Review Guide. That review process is internal process machinery, not
part of the product journey.

The technical links are now inside:

```text
Technical inspection (optional)
```

The disclosure explains:

```text
This is inspection, not the learning path.
```

The disclosure keeps these links available:

- `Extraction audit`;
- `Usage`;
- `Advanced audit`.

## What This Improves

The first read of Receipts now emphasizes what exists, what is missing, and
what is not claimed. A user can still inspect technical evidence, but they have
to make an explicit choice to open the optional technical section.

## What It Does Not Solve

This does not remove the technical audit routes. Those routes remain useful for
builders and reviewers.

This also does not prove that a human learner understands the hierarchy. It only
keeps Receipts from mixing product trust information with internal review
process.

Remaining risks:

- a user can still enter audit routes directly;
- advanced audit pages are still dense once opened;
- the data exposure audit still needs to decide what gathered data should be
  shown, summarized, expanded, hidden, or kept agent-only.

## Boundary

This slice:

- does not run Lolla;
- does not invoke the Lolla skill;
- does not call providers or model APIs;
- does not create a new run;
- does not generate or attach sidecars;
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
- does not treat relation confidence as certification.

## Validation Target

The next audit should categorize the gathered Observatory and Teacher data by
user value, default visibility, expansion state, and internal-only custody.

Recommended next gate:

`proceed_to_observatory_data_exposure_audit`
