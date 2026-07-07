# Observatory Workspace Human Review Capture Path

Status: implemented offline operator capture path.

Date: 2026-07-07

Decision gate: `ready_to_capture_completed_human_hierarchy_review_intake`

## Purpose

The Observatory workspace now has a focused human hierarchy scorecard. The next
missing link is an operator-safe way to turn a filled JSON review form into a
deterministic intake artifact.

This slice adds that capture path without wiring Observatory runtime and without
claiming that a review has been completed. It only provides the command an
operator can run after a human has filled the review form.

## Command

```bash
python3 scripts/evals/capture_observatory_workspace_human_review.py \
  --review reviews/human/observatory-workspace/review.json \
  --out reviews/human/observatory-workspace/intake.json
```

Optional arguments:

- `--source-ref` records a non-private source reference;
- `--created-at` makes the intake timestamp deterministic for receipts or tests.

If `--source-ref` is omitted, the command records only the review filename, not
the local filesystem path.

## Behavior

The capture path:

- reads one filled Observatory workspace human review JSON form;
- validates it with the existing deterministic intake validator;
- writes one sanitized intake JSON artifact;
- blocks blank, incomplete, unsafe, or boundary-violating forms from downstream
  planning;
- redacts unsafe source refs;
- avoids echoing review prose into the intake output.

The command writes intake results for accepted and blocked forms. A blocked
intake is still useful because it tells the operator what must be repaired before
the review can influence the next product revision gate.

## Gate Behavior

Accepted completed forms may only plan revision work. They do not authorize
expansion, runtime wiring, product proof, answer correctness, advice
correctness, or automatic action.

Possible outputs include:

- `accepted`;
- `blocked_pending_human_review`;
- `blocked_privacy_risk`;
- `rejected_invalid_review_form`;
- `rejected_boundary_claim`.

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

The next real use of this command should be after a human fills the focused
hierarchy scorecard. The output should be reviewed as an intake receipt, not as
a product-readiness claim.

Recommended next gate:

`ready_to_capture_completed_human_hierarchy_review_intake`
