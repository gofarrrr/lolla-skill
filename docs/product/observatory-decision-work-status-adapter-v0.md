# Observatory Decision Work Status Adapter v0

Status: implementation slice
Date: 2026-07-06
Decision gate: `proceed_to_observatory_conversation_understanding_receipts_card`

## Purpose

This slice implements the first code step from the Observatory Conversation
Understanding boundary:

```text
/api/case/<id>/decision-work
```

The endpoint reads the selected run and any existing `decision_work/` sidecar
files, then returns a product-safe status payload for Observatory.

It does not run Lolla.
It does not invoke the Lolla skill.
It does not call providers or model APIs.
It does not create interpretation reads.
It does not run the offline operator.
It does not write sidecars.
It does not mutate archives.
It does not change live answer generation or runtime behavior.

## What The Adapter Does

For the selected Observatory case, the adapter reports:

- live extraction availability;
- Decision Work sidecar availability;
- attachment state;
- source artifact refs;
- safe user receipt markdown when present;
- blockers;
- deferred reasons;
- missingness;
- links to `/audit/extraction`;
- explicit non-claims.

The adapter maps runtime sidecar states into Observatory product states:

| Attachment state | Observatory state |
| --- | --- |
| no sidecar files | `decision_work_not_present` |
| `not_requested`, `disabled`, `not_eligible` | `decision_work_not_requested` |
| `deferred` | `decision_work_deferred` |
| `blocked` | `decision_work_blocked` |
| `generated`, `generated_with_caveats`, `generated_agent_only` | `decision_work_available` |
| `failed_closed` | `decision_work_failed_closed` |
| malformed status JSON | `decision_work_malformed` |

## API Shape

The new route is:

```text
/api/case/<id>/decision-work
```

The payload schema is:

```text
lolla.observatory_decision_work_status.v0
```

Important top-level fields:

- `selected_case_id`;
- `selected_run_id`;
- `available`;
- `decision_work_status`;
- `attachment_state`;
- `live_extraction_status`;
- `conversation_understanding`;
- `source_artifacts`;
- `receipt`;
- `blockers`;
- `deferred_reasons`;
- `missingness`;
- `links`;
- `non_claims`;
- `custody_flags`.

## Current-Run Behavior

For a current run served from `/tmp`, Observatory may discover the completed
archive path through `run_events.json`. The adapter uses the same selected-run
sidecar lookup pattern as the existing Observatory sidecar endpoints, so a
current run can still report an archived `decision_work/` sidecar after archive
completion.

## Safety Rules

The status payload must not expose:

- local absolute paths;
- raw conversation text;
- raw private generated reads;
- operator logs;
- provider text;
- Product Delta eval internals as product copy;
- approval, certification, quality-score, proof, or action-authorization
  claims.

If `user_receipt.md` contains a local/private marker, the adapter reports the
receipt as blocked and does not return its Markdown.

## What This Enables

This slice makes the next UI step testable:

```text
Receipts
  -> Conversation Understanding
  -> live extraction available
  -> Decision Work not present/deferred/blocked/available
  -> safe receipt when present
```

## Stop Line

This slice stops before:

- Receipts UI rendering;
- a browser action button;
- post-run opt-in flow design;
- automatic semantic supply;
- offline job runner for arbitrary completed runs;
- Observatory-triggered generation;
- runtime default-on behavior;
- `SKILL.md` changes;
- `scripts/skill/*` changes;
- `scripts/archive_run.py` changes.

Recommended next gate:

```text
proceed_to_observatory_conversation_understanding_receipts_card
```
