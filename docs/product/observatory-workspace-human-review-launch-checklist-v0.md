# Observatory Workspace Human Review Launch Checklist

Status: review launch checklist only; no completed human review.

Date: 2026-07-07

Decision gate: `ready_to_launch_real_human_hierarchy_review`

Review packet:
[Observatory workspace user review packet](observatory-workspace-user-review-packet-v0/index.md)

Awaiting-response gate:
[Observatory workspace human review awaiting response gate](observatory-workspace-human-review-awaiting-response-gate-v0.md)

## Purpose

The Observatory workspace is paused at the human-review gate. The missing step
is not more product surface. The missing step is making it easy for a real
reviewer to launch the local workspace, open the right route, click through the
right surfaces, and then fill the blank form.

This checklist is review enablement only. It does not add a completed review,
does not capture an intake artifact, and does not expand the visible
Observatory UX.

## Inputs

Use an existing completed run result JSON. Do not create a new run for the
review.

Acceptable inputs:

- an archived completed run result, such as
  `~/.local/share/lolla/runs/<run-id>/result.json`;
- an already completed active-run result, such as
  `/tmp/lolla_<run-id>_result.json`.

Do not use this checklist to run Lolla, invoke the Lolla skill, call providers
or models, create sidecars, or write runtime artifacts.

## Launch

Set the result path and a case id for the selected run:

```bash
export LOLLA_OBSERVATORY_REVIEW_RESULT="<existing-result-json>"
export LOLLA_OBSERVATORY_REVIEW_CASE_ID="<case-id>"
```

For the current Teacher/Observatory pilot review, the case id may be:

```text
launch-public-enterprise-beta
```

Then start the portable Observatory server:

```bash
python3 observatory/serve_result.py \
  --result "$LOLLA_OBSERVATORY_REVIEW_RESULT" \
  --port 8080
```

If port `8080` is already in use, the server will try the next ports and print
the chosen local URL.

Optional read-only preflight before launch:

```bash
python3 scripts/evals/preflight_observatory_workspace_human_review.py \
  --result "$LOLLA_OBSERVATORY_REVIEW_RESULT" \
  --case-id "$LOLLA_OBSERVATORY_REVIEW_CASE_ID" \
  --pretty
```

The preflight checks the result JSON and current review/intake artifact state.
It does not launch Observatory or write review answers.

## Start Route

Open the Review Guide first:

```text
http://localhost:8080/review/observatory-workspace?case_id=<case-id>
```

If the server chose another port, replace `8080` with the printed port.

## Clickthrough Order

Use this order for the review:

```text
Review Guide -> Outcome -> Learn -> Models -> model detail -> Relations -> relation detail -> Map -> Receipts
```

Optional inspection routes are allowed only after Receipts:

```text
Extraction audit -> Usage -> Advanced audit
```

The normal product journey being evaluated is still:

```text
Outcome -> Learn -> Models -> Relations -> Map -> Receipts
```

## What To Record While Clicking

The reviewer should record:

- whether the first page explains what Observatory is asking them to do;
- whether Outcome and Learn feel primary;
- whether Models, Relations, and Map feel like support instead of equal tasks;
- whether Receipts and Audit feel like inspection rather than the product;
- the first confusing label, sentence, card, or click target;
- the first place where technical detail appears too early;
- the first place where a graph edge, confidence label, or receipt could be
  misread as proof.

## Fill The Form

After the clickthrough, copy the blank JSON form:

```text
docs/product/observatory-workspace-user-review-packet-v0/human-review-form.json
```

Save the real completed response here:

```text
reviews/human/observatory-workspace/review.json
```

Negative, partial, and `cannot_judge` answers are useful. Do not pre-fill a
positive result.

## Capture The Intake

After the real review response exists, run:

```bash
python3 scripts/evals/capture_observatory_workspace_human_review.py \
  --review reviews/human/observatory-workspace/review.json \
  --out reviews/human/observatory-workspace/intake.json \
  --source-ref reviews/human/observatory-workspace/review.json
```

The captured intake can plan the next product revision slice if accepted. It
does not authorize product expansion, runtime wiring, human-validation claims,
product-proof claims, answer-correctness claims, advice-correctness claims, or
automatic action.

## Boundary

This checklist:

- does not add a completed review or intake artifact;
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

The next gate remains:

```text
awaiting_real_human_hierarchy_review_response
```

This checklist only makes that review easier to launch.
