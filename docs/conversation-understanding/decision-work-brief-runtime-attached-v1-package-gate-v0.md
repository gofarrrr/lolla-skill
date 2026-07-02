# Decision Work Brief Runtime-Attached Internal v1 Package Gate v0

Status: PR167 package gate

Date: 2026-07-02

Manifest:
[runtime-attached internal v1 package manifest](decision-work-brief-runtime-attached-v1-package-manifest-v0.json)

Review:
[runtime attachment review](decision-work-brief-runtime-attachment-review-v0.md)

## Package Scope

This package covers PR160-PR167:

- runtime attachment contract;
- sidecar/artifact location contract;
- manual post-archive bundle generator;
- eligibility and blocker gate;
- short receipt renderer;
- agent handoff packet;
- default-off post-archive archive-run hook;
- runtime attachment review and package manifest.

## Narrow v1 Claim

Decision Work Brief Runtime-Attached Internal v1 is functional behind a flag for
completed clean runs, with explicit blocked/deferred states, short user
receipts, evidence links, and agent handoff packets.

The flag is:

```text
LOLLA_DECISION_WORK_BRIEF_AFTER_ARCHIVE
```

Default behavior is off. When off, no Decision Work Brief sidecar is written.

## What This Does Not Claim

This package does not claim:

- customer readiness;
- default-on runtime behavior;
- human validation;
- product proof;
- answer-quality scoring;
- advice correctness;
- proof that Lolla improved the decision;
- agent or automatic action authorization;
- safe operation from checked-in-safe artifacts alone.

## Strongest Useful Signal

The system now has a safe runtime hinge: archive completion can optionally
write a post-archive `decision_work/` sidecar without touching the live answer
generation path or the skill shell.

## Strongest Unresolved Risk

Runtime-attached internal v1 can defer safely, but it does not yet solve safe
runtime supply of semantically rich briefs or calibrated user-facing product
design.

## Decision Gate

Decision gate:

```text
runtime_attached_internal_v1_packaged
```

Recommended next PR:

```text
PR168 Decision Work Brief Runtime-Attached Internal v1 Follow-up Planning v0
```

The next slice should choose between product-surface simplification, safe brief
supply planning, runtime fixture expansion, or internal demo walkthroughs. It
should not make the feature default-on.

## PR168 Follow-up

PR168 makes that choice:

[runtime-attached internal v1 follow-up plan](decision-work-brief-runtime-attached-v1-followup-plan-v0.md)

It selects `safe_brief_supply_planning` because PR160-PR167 produced coherent
runtime plumbing, but the hook still defers when run-specific safe brief,
enriched brief, and triage inputs are not supplied.
