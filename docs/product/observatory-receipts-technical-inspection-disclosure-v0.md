# Observatory Receipts Technical Inspection Disclosure

Status: implemented UX reduction slice.

Date: 2026-07-07

Decision gate: `ready_for_human_hierarchy_review_after_receipts_reduction`

## Purpose

The latest browser audit showed that Receipts are the right home for custody,
missingness, non-claims, and technical inspection. The remaining risk is that
technical audit links can still look like a normal next product step.

This slice makes Receipts more explicitly custody-first. Technical audit links
remain present, but they now sit behind a closed optional disclosure.

## UX Change

Receipts still starts with:

- trust summary;
- status chips;
- visible non-claims;
- human review entry.

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

The first read of Receipts now emphasizes what exists, what is missing, what is
not claimed, and where to review the product journey. A user can still inspect
technical evidence, but they have to make an explicit choice to open the
optional technical section.

## What It Does Not Solve

This does not remove the technical audit routes. Those routes remain useful for
builders and reviewers.

This also does not prove that a human learner understands the hierarchy. It only
makes the hierarchy easier to evaluate in the next human review.

Remaining risks:

- a user can still enter audit routes directly;
- advanced audit pages are still dense once opened;
- human hierarchy review is still pending.

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

The next human hierarchy review should specifically check whether Receipts now
read as custody and optional inspection rather than a competing product surface.

Recommended next gate:

`ready_for_human_hierarchy_review_after_receipts_reduction`
