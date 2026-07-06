# Observatory Offline Process Brief Runner v0

Status: implementation slice
Date: 2026-07-06
Decision gate: `proceed_to_observatory_prepare_process_brief_action`

## Purpose

This slice implements the CLI-first adapter from the opt-in design:

```text
completed run
  -> inspect existing Decision Work sidecar status
  -> explain missing safe inputs
  -> expose a safe offline command
  -> optionally run the existing offline operator runner
  -> write a runner state JSON outside the repo
```

The new adapter is:

- `engine/system_b/observatory_process_brief_runner.py`;
- `scripts/evals/prepare_observatory_process_brief.py`.

It is the bridge between Observatory UX language and the existing Decision Work
offline operator runner.

## What It Does

The adapter accepts:

- `--case-id`;
- `--completed-run-archive-dir`;
- `--safe-output-dir`;
- optional `--generated-read`;
- optional `--generated-triage`;
- optional `--run-offline-operator`;
- optional `--out`.

It returns a product-safe state payload:

```text
lolla.observatory_process_brief_runner.v0
```

Primary states:

- `process_brief_already_attached`;
- `needs_safe_inputs`;
- `offline_command_available`;
- `offline_runner_summary_ready`;
- `blocked_completed_run_unavailable`;
- `runner_failed_closed`.

## Important Behavior

If a Decision Work sidecar is already attached, the adapter stops with:

```text
process_brief_already_attached
```

If generated-read or generated-triage refs are missing, the adapter stops with:

```text
needs_safe_inputs
```

If both refs exist and `--run-offline-operator` is not supplied, the adapter
returns:

```text
offline_command_available
```

If both refs exist and `--run-offline-operator` is supplied, the adapter runs
the existing offline operator runner and writes:

```text
runner_summary.json
observatory_process_brief_runner.json
```

under the explicit safe output directory.

## What It Does Not Do

The adapter does not:

- run `$lolla`;
- invoke the Lolla skill;
- create a new Lolla run;
- create generated interpretation reads;
- call providers or models;
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

The generated interpretation read remains an explicit safe input. When it is
missing, this adapter records missingness instead of inventing one.

## Example

```bash
python3 scripts/evals/prepare_observatory_process_brief.py \
  --case-id launch-public-enterprise-beta \
  --completed-run-archive-dir <completed-run-archive-dir> \
  --generated-read <generated-read-json> \
  --generated-triage <generated-triage-json> \
  --safe-output-dir <safe-output-dir> \
  --run-offline-operator \
  --out <safe-output-dir>/observatory_process_brief_runner.json \
  --pretty
```

The command is still local and explicit. It does not add an Observatory browser
button yet.

## Observatory Meaning

The future Receipts card can use this adapter to decide which user state to
show:

| Adapter state | UI meaning |
| --- | --- |
| `process_brief_already_attached` | Show receipt |
| `needs_safe_inputs` | Show missing generated-read or generated-triage input |
| `offline_command_available` | Show copyable CLI command |
| `offline_runner_summary_ready` | Show runner summary and next review/attach state |
| `blocked_completed_run_unavailable` | Explain that the selected run cannot be prepared |
| `runner_failed_closed` | Show failed-closed state and blockers |

The next Observatory PR may add a browser action that calls this adapter or
shows its command/state. That action still must not create semantic reads,
write sidecars, mutate archives, call providers, or wire runtime.

## Stop Line

This slice stops before:

- an Observatory browser action;
- new Observatory API route;
- generated-read creation;
- provider/model calls;
- sidecar writes;
- archive mutation;
- runtime wiring;
- default-on behavior;
- `SKILL.md` changes;
- `scripts/skill/*` changes;
- `scripts/archive_run.py` changes.

Recommended next gate:

```text
proceed_to_observatory_prepare_process_brief_action
```
