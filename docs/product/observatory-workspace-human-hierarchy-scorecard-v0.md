# Observatory Workspace Human Hierarchy Scorecard

Status: implemented review-packet refinement.

Date: 2026-07-07

Decision gate: `ready_for_human_hierarchy_review_with_focused_scorecard`

## Purpose

The current Observatory workspace now has a clearer product path and lower
detail overload in model pages and Receipts. The remaining risk is not whether
more information exists. The risk is whether a cold human reviewer can tell what
the information is for.

This slice adds a focused hierarchy scorecard to the existing human review
workflow. It does not create a second review system. It sharpens the existing
Review Guide and blank review form around the exact places where the workspace
can collapse back into a pile of artifacts.

## Scorecard Checks

The scorecard asks a reviewer to check six overload-risk moments:

- first screen orientation;
- Learn as a reasoning move, not answer correctness;
- model detail progressive disclosure;
- relation story before taxonomy;
- Map as navigation, not proof;
- Receipts as custody and optional inspection.

These checks are visible on the server-rendered Review Guide and mirrored in the
blank Markdown and JSON human review forms.

## Product Logic

The intended progression remains:

```text
Outcome -> Learn -> Models -> Relations -> Map -> Receipts
```

The intended information ladder remains:

```text
first read -> optional support -> drill-down page -> receipts/audit
```

The scorecard exists because a reviewer can now evaluate each part of that
ladder directly:

- first screen answers what the workspace is asking the user to do;
- Learn answers what reasoning move can be practiced;
- model detail answers what this model means without flooding the first read;
- relation detail answers how two models interact before showing taxonomy;
- Map answers where to navigate next without turning edges into proof;
- Receipts answers what exists, what is missing, and what is not claimed.

## Implementation

Implemented changes:

- Review Guide adds a visible `Focused hierarchy scorecard` card.
- Human review Markdown form adds a `Focused Hierarchy Scorecard` section.
- Human review JSON form adds `focused_hierarchy_checks`.
- Human review intake reports focused-check coverage for completed forms.
- The existing review packet manifest records the two overload-reduction source
  slices that motivated the focused scorecard.

The blank form remains blank. This slice does not fill a human review response.

## Boundary

This slice:

- does not complete human review;
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

The next human review should use this scorecard after one full workspace
clickthrough. A useful result can be positive, negative, partial, or
`cannot judge`. The scorecard is meant to find the next product revision gate,
not to certify the product.

Recommended next gate:

`ready_for_human_hierarchy_review_with_focused_scorecard`
