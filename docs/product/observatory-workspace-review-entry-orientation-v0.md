# Observatory Workspace Review Entry Orientation

Status: implemented as a narrow Observatory presentation slice.

Date: 2026-07-07

Decision gate: `ready_for_human_review_with_visible_review_guide`

## Purpose

The workspace now has a review packet and a blank human review form, but the live
Observatory page still needed to answer a simpler first question: what am I
supposed to evaluate?

This slice adds a visible review entry point from the workspace itself. It is not
a new product surface, a new run, or a new evaluation system. It is a bridge from
the selected-run Observatory workspace to the already-created human review task.

## Browser finding

The browser review found that the first screen now has a clearer Reading Path,
and Receipts shows trust, non-claims, and technical inspection links. The missing
piece was a plain-language bridge from the live page to the reviewer task.

Without that bridge, a user could see Outcome, Learn, Models, Relations, Map,
Receipts, audits, and packet files, but still not know whether they were judging:

- the answer;
- the lesson;
- the mental model pages;
- the graph;
- the technical receipts;
- or the whole Observatory journey.

## Change

The portable Observatory server now exposes:

- a sidebar `Review Guide` panel next to the `Reading Path`;
- a `Human review` subsection in Receipts, before technical inspection links;
- a server-rendered `/review/observatory-workspace` page.

The review guide tells the reviewer to move through:

Outcome -> Learn -> Models -> Relations -> Map -> Receipts

It asks the reviewer to judge whether those six surfaces feel like one
Observatory product surface or several artifacts placed together.

## What The Guide Answers

The guide is intentionally small. It answers:

- what am I supposed to evaluate;
- what order should I click through;
- what should I write down;
- which blank form receives the human review;
- what claims this review is not allowed to make.

It keeps technical inspection as a later drill-down. The first reviewer task is
not to inspect JSON. The first reviewer task is to notice whether the product
story is understandable.

## Human Review Output

The linked review task remains the blank form in:

`docs/product/observatory-workspace-user-review-packet-v0/human-review-form.md`

The form is still not completed. A negative, confused, or partial review is a
valid review outcome. This slice only makes the task visible from Observatory.

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

## Next Gate

Recommended next gate:

`ready_for_human_review_with_visible_review_guide`

The next useful step is a real human review using the visible guide and blank
review form. Synthetic or Codex-assisted review remains diagnostic only.
