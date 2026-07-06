# Observatory Conversation Understanding Receipts Card v0

Status: implementation slice
Date: 2026-07-06
Decision gate: `proceed_to_observatory_decision_work_opt_in_flow_design`

## Purpose

This slice adds the first visible Observatory UI for the read-only Decision
Work status adapter:

```text
Run Custody
  -> Conversation Understanding
```

The card lives in the portable selected-run custody panel injected by
`observatory/serve_result.py`. It uses the existing Observatory visual language
and compiled SPA wrapper without editing bundled frontend assets.

## What The Card Shows

For the selected run, the card displays:

- live extraction status;
- Decision Work status;
- plain-language meaning;
- link to `/audit/extraction`;
- link to `/api/case/<id>/decision-work`;
- existing `user_receipt.md` text when the adapter marks it safe and available.

The card consumes:

```text
/api/case/<id>/decision-work
```

It does not create or request a process brief.

## Status Copy

The card maps the read-only API state into compact user-facing labels:

| API state | UI status |
| --- | --- |
| `decision_work_available` | `available` |
| `decision_work_deferred` | `deferred` |
| `decision_work_blocked` | `blocked` |
| `decision_work_failed_closed` | `failed` |
| `decision_work_not_requested` | `not requested` |
| `decision_work_not_present` | `not attached` |
| malformed or unknown state | `inspect` |

The copy stays descriptive. It does not say approval, certification, proof,
quality score, validated, or authorized.

## Why This Shape

The user needs to understand:

```text
The run captured and extracted conversation context.
Richer Decision Work may or may not be attached.
If it is missing, that is a status, not a failure.
If it is present, the receipt is inspectable but not proof.
```

Putting this in the custody panel makes the information findable without
forcing every normal user into raw telemetry.

## Stop Line

This slice stops before:

- a "Prepare process brief" button;
- Observatory-triggered jobs;
- offline semantic generation;
- provider/model calls;
- running Lolla;
- invoking the Lolla skill;
- sidecar writes;
- archive mutation;
- runtime behavior changes;
- `SKILL.md` changes;
- `scripts/skill/*` changes;
- `scripts/archive_run.py` changes.

Recommended next gate:

```text
proceed_to_observatory_decision_work_opt_in_flow_design
```
