# Observatory Prepare Process Brief Action v0

Status: implementation slice
Date: 2026-07-06
Decision gate: `observatory_process_brief_opt_in_path_reviewable`

## Purpose

This slice adds the first Observatory action for the process-brief flow:

```text
Receipts / Conversation Understanding
  -> Prepare process brief
  -> GET /api/case/<id>/decision-work/prepare
  -> show attached / needs inputs / blocked / command-ready state
```

The action is intentionally a state check. It does not create semantic reads,
call providers, run the offline operator, attach sidecars, mutate archives, or
change runtime behavior.

## What Changed

`observatory/serve_result.py` now exposes:

```text
/api/case/<id>/decision-work/prepare
```

The endpoint calls the offline process-brief adapter in state-check mode:

```text
run_offline_operator=False
```

The selected-run custody card now includes:

- a `Prepare process brief` button;
- a compact status pill;
- a short explanation of the next safe step;
- a `Prepare JSON` link for technical inspection;
- a command disclosure if a command is available later.

## Current User Experience

For most runs without explicit generated-read and generated-triage refs, the
button returns:

```text
needs_safe_inputs
```

The user sees that a process brief cannot be prepared from the browser click
alone. This is the intended behavior. It avoids implying that Observatory can
magically create a richer Decision Work brief from absent semantic inputs.

If a Decision Work sidecar is already attached, the endpoint returns:

```text
process_brief_already_attached
```

The card then points the user back to the receipt.

If the selected run is not a completed archive run yet, the endpoint can return:

```text
blocked_completed_run_unavailable
```

That keeps the completed-run boundary visible.

## Boundary

This action does not:

- run `$lolla`;
- invoke the Lolla skill;
- create a new Lolla run;
- create generated interpretation reads;
- call providers or models;
- run the offline operator from the browser;
- write `decision_work/`;
- mutate archives;
- change runtime behavior;
- make Decision Work default-on;
- approve resolver refs;
- score answer quality;
- claim product proof;
- claim human validation;
- validate advice correctness;
- authorize agent or automatic action.

It also does not touch:

- `SKILL.md`;
- `scripts/skill/*`;
- `scripts/archive_run.py`.

## Why This Is Useful

The user now has a visible thing to click, but the click teaches the correct
system state:

```text
Conversation Understanding exists.
Decision Work may be attached, absent, blocked, or deferred.
A process brief needs explicit safe inputs.
The browser does not silently generate or attach it.
```

This makes the path testable without crossing into provider calls, runtime
wiring, or archive mutation.

## Next Gate

Recommended gate:

```text
observatory_process_brief_opt_in_path_reviewable
```

The next review should decide whether the button copy is understandable enough
for the user, and whether a later version should accept explicit generated-read
and generated-triage refs from an operator panel.
