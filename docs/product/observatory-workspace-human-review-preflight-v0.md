# Observatory Workspace Human Review Preflight

Status: read-only preflight for launching a real human hierarchy review.

Date: 2026-07-07

Decision gate: `ready_to_preflight_real_human_hierarchy_review_launch`

Launch checklist:
[Observatory workspace human review launch checklist](observatory-workspace-human-review-launch-checklist-v0.md)

Awaiting-response gate:
[Observatory workspace human review awaiting response gate](observatory-workspace-human-review-awaiting-response-gate-v0.md)

## Purpose

The human-review gate is still waiting for a real response. This slice adds a
small operator preflight so a reviewer can check whether the selected local
result path, case id, review artifact state, and capture next step are coherent
before opening Observatory.

The preflight is review enablement only. It does not launch Observatory, add a
new product surface, collect review answers, capture an intake, or expand UX.

## Command

```bash
python3 scripts/evals/preflight_observatory_workspace_human_review.py \
  --result "$LOLLA_OBSERVATORY_REVIEW_RESULT" \
  --case-id "$LOLLA_OBSERVATORY_REVIEW_CASE_ID" \
  --pretty
```

Optional arguments:

- `--port` changes the printed local URL port;
- `--review` points to a non-default review response path;
- `--intake` points to a non-default intake path;
- `--out` writes a safe JSON report instead of printing it.

The command records the result filename as a safe ref and does not write the
absolute result path into the report.

The preflight does not write the absolute result path into the report.

## Statuses

The preflight can return:

- `ready_to_launch_review`: result JSON exists, parses as an object, and no
  review/intake artifact is present yet;
- `review_ready_to_capture`: a review response exists and should be captured;
- `intake_ready_to_inspect`: review and intake artifacts both exist;
- `blocked_missing_result`: the result path is absent;
- `blocked_invalid_json`: the result path is not valid JSON;
- `blocked_invalid_root`: the result JSON root is not an object;
- `blocked_unreadable`: the result file could not be read;
- `blocked_intake_without_review`: an intake exists without its source review.

Only `ready_to_launch_review` returns exit code `0`. The other statuses return
exit code `2` because the reviewer should act on the next step before starting
or continuing the review.

## Output

The preflight report includes:

- safe result status;
- review and intake artifact status;
- the local Review Guide URL;
- the normal product journey;
- the review clickthrough order;
- the blank form path;
- the completed review path;
- the capture command;
- explicit non-claims.

The preflight does not decide whether the Observatory workspace is good. It only
checks whether the operator can begin or continue the review workflow.

## Boundary

This preflight:

- does not add a completed review or intake artifact;
- does not launch Observatory;
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

The preflight only reduces launch friction for that review.
