# Observatory Decision Work Opt-In Flow Design v0

Status: design contract
Date: 2026-07-06
Decision gate: `proceed_to_observatory_offline_process_brief_runner`

## Purpose

This slice defines what the future Observatory action named
`Prepare process brief` should mean.

The answer is intentionally narrow:

```text
Prepare process brief means:
  take a completed run,
  inspect existing Conversation Understanding and Decision Work state,
  run only explicit offline/operator-safe steps when inputs are present,
  preserve blockers and missingness,
  and make the resulting receipt visible in Observatory.
```

It does not mean:

- run `$lolla`;
- invoke the Lolla skill;
- create a new Lolla run;
- revise the answer;
- call providers or models from Observatory;
- generate arbitrary semantic interpretation from a browser click;
- turn Decision Work into Teacher Learn;
- score answer quality;
- validate advice correctness;
- approve, certify, or authorize action;
- make Decision Work default-on runtime behavior.

## Product Problem

The current Observatory can now show whether Conversation Understanding exists,
whether live extraction is available, and whether a richer Decision Work sidecar
is attached.

That is useful, but the user still needs a clear next step:

```text
I see there is no process brief.
Can I ask for one?
What will that do?
What will it cost?
What private material will it touch?
Why is it blocked or deferred?
How do I know it did not mutate the run or make proof claims?
```

The UI must answer those questions before it offers an action.

## Current System Truth

There are three existing layers:

| Layer | Current state | UX consequence |
| --- | --- | --- |
| Live extraction | Already part of normal runs | Show as available or missing, link to `/audit/extraction` |
| Decision Work status adapter | Read-only API at `/api/case/<id>/decision-work` | Use it as the source of truth for the card |
| Offline operator runner | Existing command-only runner requiring explicit generated-read and generated-triage inputs | First action must be CLI-first or state-first, not magic generation |

The runner today can orchestrate deterministic Decision Work steps from
explicit inputs. It can produce a `runner_summary.json`. It does not create
semantic reads, call providers, write sidecars, mutate archives, or approve
resolver refs.

That means the first honest Observatory flow is:

```text
show status
  -> explain what would be needed
  -> provide the exact CLI path when safe inputs exist or are supplied
  -> refresh when a sidecar is later attached
```

The first browser action should not pretend to produce a complete process brief
when the required generated-read or generated-triage input is absent.

## Information Architecture

The process-brief action belongs in the existing Receipts / Conversation
Understanding card, not in Teacher Learn and not in Advanced telemetry.

| Information | UX tier | User-facing treatment |
| --- | --- | --- |
| Conversation captured/extracted | First-class status | Compact status row with extraction audit link |
| Decision Work sidecar status | First-class status | Plain-language state and receipt preview if safe |
| Process brief next step | First-class action/status | Explain whether a brief can be prepared now |
| Runner summary | Second-class receipt detail | Link or collapsible technical summary after run |
| Sidecar JSON files | Second-class technical detail | Status JSON link, not normal copy |
| Raw conversation | Internal/private | Never shown as product copy |
| Raw generated reads | Internal/operator | Mention existence or absence only |
| Provider output | Internal/operator | Never surfaced as product copy |
| Private ledgers / Product Delta internals | Internal-only | Not used as product copy |
| Teacher reasoning move | Separate Learn surface | Linkable, but not part of process brief generation |

## Page Shape

The Receipts card should eventually have four visible blocks.

### 1. Status Strip

Purpose:

```text
Tell the user what exists before asking them to do anything.
```

Example states:

- `Conversation captured and extracted`
- `Decision Work not requested`
- `Decision Work deferred`
- `Decision Work blocked`
- `Process brief attached`

### 2. What This Would Do

When no process brief is attached, the card should say:

```text
Prepare a process brief for this completed run.
It summarizes the decision process and preserves caveats, blockers,
missing inputs, and non-claims. It does not revise the answer or certify it.
```

This text should be visible before an action. The user should not have to infer
meaning from raw sidecar names.

### 3. Action Or Next Step

The action area should have one primary state at a time:

| State | Primary presentation |
| --- | --- |
| Existing sidecar available | `View receipt` |
| Not requested, required inputs absent | `Needs safe inputs` plus exact missing items |
| Generated-read and generated-triage supplied | `Copy offline command` in CLI-first v0 |
| Runner summary exists but no sidecar | `Review runner summary` |
| Write/attach step required | `Explicit attach required` with no automatic write |
| Blocked | Blocker reasons and no primary run action |

The future button label can be `Prepare process brief`, but it should only be
enabled when the action has a real implementation behind it. Until then, the
UI should show a state explanation and command, not a placebo button.

### 4. Receipt And Technical Links

When a safe `user_receipt.md` exists, show it inline as a receipt.

Always keep links available for technical inspection:

- `/audit/extraction`;
- `/api/case/<id>/decision-work`;
- future runner summary JSON when present.

## State Machine

The opt-in flow should use operational states, not product-readiness labels.

```text
decision_work_not_present
  -> process_brief_not_requested
  -> needs_safe_inputs
  -> offline_command_available
  -> offline_runner_ready_for_review
  -> explicit_attach_required
  -> decision_work_available
```

Blocked and deferred states can appear at multiple points:

```text
needs_safe_inputs
  -> deferred_missing_semantic_read
  -> deferred_missing_triage

offline_runner_ready_for_review
  -> sidecar_ready_for_explicit_write
  -> sidecar_ready_blocked_state
  -> blocked_privacy_risk
  -> blocked_source_depth_insufficient
  -> blocked_schema_or_custody_failure
  -> blocked_runtime_or_user_surface_risk
```

The UI should preserve blocked states as meaningful outcomes. A blocked
high-risk case is not a failed product; it is the system refusing to smooth
over risk.

## Exact Meaning Of Prepare Process Brief

The future action should perform these checks in order:

1. Resolve the selected completed run.
2. Read `/api/case/<id>/decision-work`.
3. If `decision_work_available`, show the receipt and stop.
4. If no sidecar exists, inspect whether explicit generated-read and
   generated-triage inputs are available or supplied.
5. If semantic inputs are missing, stop with `needs_safe_inputs`.
6. If safe inputs exist, build a deterministic offline runner packet.
7. Run the existing offline operator chain up to `runner_summary.json`.
8. Show `sidecar_ready_for_explicit_write`, `sidecar_ready_blocked_state`, or
   the first blocker/deferred state.
9. Do not write `decision_work/` in the first Observatory action.
10. Refresh status after an explicit attach step creates a sidecar.

This keeps three things separate:

- status display;
- offline runner preparation;
- archive sidecar attachment.

## CLI-First Decision

The next implementation should be CLI-first:

```bash
python3 scripts/evals/run_decision_work_offline_operator.py \
  --completed-run-archive-dir <completed-run-archive-dir> \
  --generated-read <generated-read-json> \
  --generated-triage <generated-triage-json> \
  --case-id <case-id> \
  --safe-output-dir <safe-output-dir> \
  --out <safe-output-dir>/runner_summary.json \
  --pretty
```

Observatory should first display this command or its required missing inputs.
That gives the user something testable without adding a background worker or
browser-triggered archive mutation.

## Later Observatory Action

A later browser action can be considered after the CLI-first runner is proven
usable from arbitrary completed runs.

Suggested future route:

```text
POST /api/case/<id>/decision-work/prepare
```

Suggested behavior:

- accept explicit safe refs only;
- return `needs_safe_inputs` when refs are absent;
- run the offline runner only when all inputs are present;
- write runner output under an explicit safe output directory;
- never call providers or models;
- never create generated reads from the browser;
- never write `decision_work/` in the first action version;
- return a job/status object that the card can refresh.

If a later phase allows sidecar attachment, it should require a separate
explicit attach gate, no-overwrite checks, and visible confirmation copy.

## Privacy Copy

The card should use plain copy like this:

```text
This uses artifacts from this completed run on this machine. It may inspect
conversation-derived material and Decision Work inputs. It does not upload raw
conversation text from this button, and this action does not call a model.
```

If a future phase adds semantic-read generation, the copy must change before
that phase ships:

```text
This step will send a bounded interpretation packet to a model provider.
It may take longer and may incur provider cost. Continue only if you want that.
```

That future copy is not active in v0.

## Cost Copy

For the CLI-first and Observatory-offline runner path:

```text
No model/provider call is made by this preparation step.
```

If generated-read creation is missing, the UI should say:

```text
A generated interpretation read is required before this runner can prepare a
brief. This screen will not create it automatically.
```

## Latency Copy

For deterministic runner preparation:

```text
This usually takes seconds and writes a local runner summary.
```

For future model-backed interpretation:

```text
The interpretation-read step may take longer because it is a separate explicit
generation step.
```

## Copy Rules

Allowed words:

- `available`;
- `attached`;
- `not requested`;
- `needs safe inputs`;
- `deferred`;
- `blocked`;
- `failed closed`;
- `ready for explicit review`;
- `ready for explicit attach`.

Forbidden product meanings:

- approval;
- certification;
- proof;
- quality score;
- validated answer;
- correct advice;
- authorized action;
- automatic action.

## Stop Line

This design stops before:

- implementing a browser button;
- implementing a new server route;
- running the offline operator from Observatory;
- creating interpretation reads;
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
proceed_to_observatory_offline_process_brief_runner
```
