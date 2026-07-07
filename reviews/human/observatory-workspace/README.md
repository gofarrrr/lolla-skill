# Observatory Workspace Human Review Instructions

Status: instructions only; no completed human review is included here.

## Purpose

Use this folder only when a real human reviewer has completed the Observatory
workspace hierarchy review.

The current review packet asks the reviewer to judge whether Observatory reads
as one product journey:

```text
Outcome -> Learn -> Models -> Relations -> Map -> Receipts
```

It also asks the reviewer to complete the focused hierarchy scorecard for:

- first screen orientation;
- Learn as a reasoning move, not answer correctness;
- model detail progressive disclosure;
- relation story before taxonomy;
- Map as navigation, not proof;
- Receipts as custody and optional inspection.

## Source Form

Start from the blank JSON form:

```text
docs/product/observatory-workspace-user-review-packet-v0/human-review-form.json
```

The Markdown companion is:

```text
docs/product/observatory-workspace-user-review-packet-v0/human-review-form.md
```

Do not pre-fill a positive result. Negative, partial, and `cannot_judge` reviews
are useful.

## Expected Local Files

When a human reviewer actually completes the review, place the completed JSON
form at:

```text
reviews/human/observatory-workspace/review.json
```

Then run:

```bash
python3 scripts/evals/capture_observatory_workspace_human_review.py \
  --review reviews/human/observatory-workspace/review.json \
  --out reviews/human/observatory-workspace/intake.json \
  --source-ref reviews/human/observatory-workspace/review.json
```

The command writes:

```text
reviews/human/observatory-workspace/intake.json
```

Do not create `review.json` or `intake.json` until a real completed review
exists.

## Intake Status Meaning

- `accepted`: the review form is complete enough to plan the next product
  revision gate.
- `blocked_pending_human_review`: the form is still blank or not marked
  completed.
- `blocked_privacy_risk`: the form contains private markers or local absolute
  paths that must be repaired.
- `rejected_invalid_review_form`: the form is malformed or missing required
  review fields.
- `rejected_boundary_claim`: the form tries to claim proof, correctness,
  validation, runtime integration, or action authorization.

Accepted intake still does not authorize expansion, runtime wiring, product
proof, answer correctness, advice correctness, or automatic action.

## Boundary

These instructions:

- do not complete human review;
- do not run Lolla;
- do not invoke the Lolla skill;
- do not call providers or model APIs;
- do not create a new run;
- do not generate or attach sidecars;
- do not wire skill runtime behavior;
- do not mutate archives;
- do not edit `observatory/build`;
- do not touch `SKILL.md`;
- do not touch `scripts/skill/*`;
- do not touch `scripts/archive_run.py`;
- do not claim product proof;
- do not claim human validation;
- do not claim answer correctness;
- do not claim advice correctness;
- do not authorize automatic action;
- do not treat graph edges as proof;
- do not treat relation confidence as certification.
