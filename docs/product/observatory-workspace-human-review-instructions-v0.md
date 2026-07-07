# Observatory Workspace Human Review Instructions

Status: implemented reviewer/operator instruction slice.

Date: 2026-07-07

Decision gate: `ready_for_real_human_hierarchy_review_response`

## Purpose

The Observatory workspace now has:

- a visible Review Guide;
- a focused hierarchy scorecard;
- a blank human review form;
- a deterministic intake validator;
- an offline capture command.

The missing piece was a concrete handoff location and operator instruction set.
This slice adds that without inventing a completed review.

## Reviewer Location

Instructions now live at:

```text
reviews/human/observatory-workspace/README.md
```

That folder is the future home for:

```text
reviews/human/observatory-workspace/review.json
reviews/human/observatory-workspace/intake.json
```

Those files are not created in this slice. They should appear only after a real
human reviewer completes the scorecard and an operator captures the intake.

## Manual Workflow

1. Open the Observatory workspace and Review Guide.
2. Click through:

```text
Outcome -> Learn -> Models -> Relations -> Map -> Receipts
```

3. Fill the blank JSON review form:

```text
docs/product/observatory-workspace-user-review-packet-v0/human-review-form.json
```

4. Save the completed review as:

```text
reviews/human/observatory-workspace/review.json
```

5. Capture the intake:

```bash
python3 scripts/evals/capture_observatory_workspace_human_review.py \
  --review reviews/human/observatory-workspace/review.json \
  --out reviews/human/observatory-workspace/intake.json \
  --source-ref reviews/human/observatory-workspace/review.json
```

## What To Evaluate

The reviewer should evaluate whether the workspace reads as one product journey,
not a pile of artifacts.

The focused hierarchy scorecard asks whether:

- the first screen explains what Observatory is asking the user to do;
- Learn teaches a reasoning move rather than answer correctness;
- model pages keep source-derived detail behind progressive disclosure;
- relation pages put the plain-language story before taxonomy;
- Map stays navigational rather than evidentiary;
- Receipts lead with custody and non-claims while keeping technical inspection
  optional.

## Gate Meaning

An accepted intake can plan the next product revision gate. It cannot claim
product proof, human validation, answer correctness, advice correctness, runtime
integration, or action authorization.

Blocked or rejected intake is also useful. It tells us the review response needs
repair before it can drive product planning.

## Boundary

This slice:

- does not complete human review;
- does not add `reviews/human/observatory-workspace/review.json`;
- does not add `reviews/human/observatory-workspace/intake.json`;
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

## Recommended Next Gate

`ready_for_real_human_hierarchy_review_response`
