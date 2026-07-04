# Decision Work Sidecar Internal v1 Current State

Status: PR223 current-state narrative
Date: 2026-07-04

Review artifact:
[Decision Work Sidecar Internal v1 current-state review](../../reviews/codex-assisted/decision-work-sidecar-internal-v1-current-state-v0/review.json)

## Short Version

Decision Work Sidecar Internal v1 is functional as a command-only, explicit-operator, no-overwrite sidecar pipeline for validated Decision Work artifacts, ending in a `decision_work/` sidecar on a completed-run archive, with receipts and non-claims preserved.

It can write an auditable Decision Work sidecar into a completed-run archive through an explicit operator command. It preserves caveats and blocked-state outcomes. It does not prove the advice was correct. It does not make Lolla automatically better. It is not default-on runtime behavior. It is not customer-ready automation.

## What It Does

Decision Work Sidecar Internal v1 gives an operator a bounded path from safe
Decision Work artifacts to an inspectable archive sidecar.

The operator can:

- start from an already completed run;
- validate a generated interpretation read;
- build brief supply;
- render a generated-read brief;
- build triage supply;
- use a generated triage read;
- build resolver-supply candidate state;
- build a sidecar update packet;
- run a dry-run sidecar preview;
- explicitly write a `decision_work/` sidecar into a completed-run archive;
- inspect the resulting receipt and sidecar files.

The written sidecar contains the expected file set:

- `attachment_status.json`;
- `user_receipt.md`;
- `agent_handoff_packet.json`;
- `safe_supply_summary.json`;
- `sidecar_update_packet.json`;
- `sidecar_write_receipt.json`.

This is useful because it turns a fragile chain of generated-read artifacts
into a durable archive-adjacent record with clear custody, status, blockers,
and non-claims.

## Why It Matters

Before this path, Decision Work could prepare and preview sidecar-shaped
outputs, but the system did not have a packaged, command-only way to complete
the internal archive sidecar loop.

Internal v1 closes that loop. It does not make the product automatic. It makes
the operator workflow inspectable:

- what was validated;
- what was copied;
- what was blocked or deferred;
- what was written;
- what was not claimed.

That matters because the dangerous failure mode is not merely a missing file.
It is a fluent sidecar or brief being mistaken for proof, approval, or runtime
readiness. Internal v1 makes the receipts and caveats travel with the sidecar.

## Launch-Like Case

For a launch-like case, the path can reach:

```text
real_archive_sidecar_write_completed
```

That means the explicit operator command wrote the allowed sidecar file set
into the chosen completed-run archive directory. It does not mean the advice
was correct, that a resolver approved refs, that a human validated the
decision, that the answer was scored, or that an agent may act.

## Deploy Or High-Risk Case

For a deploy/high-risk case, the path can preserve:

```text
real_archive_sidecar_write_completed_blocked_state
```

That is intentionally different. The sidecar can record that the generated-read
path is blocked for runtime or user-surface use. It can preserve domain,
compliance, private-context, and overtrust caveats without converting them
into availability.

This is the point: blocked-state sidecars are not failures when the risk calls
for blocking. They are evidence that the system did not smooth a high-risk case
into a product-ready surface.

## What It Is Not

Decision Work Sidecar Internal v1 is not:

- customer readiness;
- default-on runtime behavior;
- automatic arbitrary-run semantic interpretation;
- direct runtime interpretation;
- runtime model or provider calls;
- queue worker behavior;
- resolver approval;
- resolver refs marked usable;
- product proof;
- human validation;
- answer-quality scoring;
- advice correctness;
- approval or certification;
- action authorization.

It also does not prove that Lolla improved the decision. The sidecar is an
auditable internal record, not a truth certificate.

## What Remains Manual

The operator still has to:

- obtain or prepare the generated interpretation read;
- choose the completed-run archive target;
- inspect intake and supply statuses;
- inspect the dry-run preview;
- supply explicit write confirmation;
- inspect `attachment_status.json`, `user_receipt.md`, and
  `sidecar_write_receipt.json`;
- stop on blocked, deferred, privacy-risk, mismatch, or missing-marker states.

No background worker performs this flow. No runtime hook triggers it
automatically.

## What Remains Blocked

The current system still blocks or defers:

- missing source refs;
- missing uncertainty;
- privacy or provider-text markers;
- local path leaks;
- resolver approval claims;
- product-proof claims;
- human-validation claims;
- answer-quality scoring claims;
- advice-correctness claims;
- agent or automatic action authorization;
- mismatched sidecar update packet and dry-run result;
- existing `decision_work/` sidecars in no-overwrite v1;
- target paths that fail archive marker or path-safety checks.

## What Should Come Next

The next phase should pause and review before automation.

Future work can consider:

- automatic semantic generation for arbitrary runs;
- queue worker or operator runner;
- resolver approval policy;
- runtime hook integration;
- default-off runtime attachment to real generated artifacts;
- broader case and eval coverage;
- user-facing UI or receipt;
- human/product calibration later.

Those are separate phases. They should not be smuggled into the Internal v1
closeout.

The follow-on phase anchor is
[Decision Work Sidecar Automation Readiness PRD](../conversation-understanding/decision-work-sidecar-automation-readiness-prd-v0.md).
It keeps the next step offline and operator-directed, defines sidecar-ready,
blocked, deferred, and rejected states for newly completed runs, and recommends
an offline operator runner plan before any queue worker, runtime hook,
resolver approval, or default-on behavior.

## Decision Gate

Selected gate:

```text
decision_work_sidecar_internal_v1_complete
```

Recommended next phase:

```text
Decision Work Sidecar Internal v1 pause / review before automation phase
```
