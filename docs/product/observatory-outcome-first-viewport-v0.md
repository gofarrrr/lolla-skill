# Observatory Outcome First Viewport v0

Status: implemented server-rendered UX slice.

Date: 2026-07-07

Decision gate: `proceed_to_outcome_browser_review`

Depends on:
[Observatory Outcome Object Contract](observatory-outcome-object-contract-v0.md)

## Purpose

This slice fixes the immediate Outcome page mismatch found in browser review.

Before this slice, the center of the workspace started with a navigation
starter, a run-contents card, repeated action links, status chips, and only then
the run outcome. That made the page feel like product ceremony instead of a
result.

After this slice, the center of the default workspace starts with:

1. compact run context;
2. visible `Download MD`;
3. the actual Outcome section;
4. the full `outcome_value` headline and answer;
5. why the answer changed;
6. main reasons;
7. confidence boundary;
8. next useful moves;
9. expandable outcome details and run contents.

Browser review then found a second failure mode: when a selected run has a
normal result artifact but no matching Teacher learning packet, the root page
showed only a missing product-workspace message. That hid the outcome even
though the run result was available. This slice now renders a run-only fallback
for that case: Outcome and Receipts stay visible, while Learn, Models,
Relations, and Map are explicit missing source-artifact sections.

## What Changed

The server-rendered workspace now passes both objects into Outcome:

```text
outcome_summary
outcome_value
```

`outcome_summary` stays as support detail. `outcome_value` owns the first read.

The hero no longer renders the center six-step start panel. The sidebar still offers the reading path, but the center of the page does not repeat it.

The run contents card is now below the Outcome first read, inside the Outcome
surface. It remains available, but it no longer preempts the result.

The product adapter also exposes a run-only preview object for the portable
server. It is not a full product workspace contract and does not fake Teacher
data. It exists so a selected run can still show its outcome, receipts, agent
memory export, and missingness when the Teacher packet is absent.

## First-Read Shape

Outcome now shows:

- `outcome_value.stance` as the kicker;
- `outcome_value.outcome_headline` as the main result;
- `outcome_value.plain_language_answer` without clipping;
- `outcome_value.what_changed`;
- `outcome_value.primary_reasons`;
- `outcome_value.confidence_boundary`;
- up to three `outcome_value.recommended_next_moves`.

The `Download MD` action remains visible in the hero and in run contents. The
button keeps hover/focus help explaining that the export is a private Markdown
memory for a future agent.

When Teacher packet surfaces are missing, the page shows:

- the same Outcome first read;
- `Unavailable Teaching Surfaces`;
- one explicit missing section each for Learn, Models, Relations, and Map;
- Receipts and run inventory showing which families are available, private
  export, inspection-only, or missing.

## What Did Not Change

This slice does not change runtime behavior.

It also:

- does not invoke Lolla;
- does not call providers or model APIs;
- does not create a new run;
- does not mutate archives;
- does not edit `SKILL.md`;
- does not edit `scripts/skill/*`;
- does not edit `scripts/archive_run.py`;
- does not edit `observatory/build/*`;
- does not claim product proof;
- does not claim human validation;
- does not claim answer correctness;
- does not claim advice correctness;
- does not authorize any action.

## Remaining UX Risk

This fixes the first-read order, but it is still a server-rendered iteration.
The next check should be browser review of:

- whether the first viewport now makes sense without explanation;
- whether the Outcome reason groups are too dense;
- whether `Download MD` is visible enough without competing with the answer;
- whether run contents should remain inside Outcome or move fully into
  Receipts later.
- whether run-only fallback copy is sufficiently helpful for cases without
  Teacher packets.

Recommended next gate:
`proceed_to_outcome_browser_review`
