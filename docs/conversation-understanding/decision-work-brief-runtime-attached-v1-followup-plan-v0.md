# Decision Work Brief Runtime-Attached Internal v1 Follow-up Plan v0

Status: PR168 follow-up choice gate

Date: 2026-07-02

Review JSON:
[PR168 review](../../reviews/codex-assisted/decision-work-brief-runtime-attached-v1-followup-plan-v0/review.json)

## Purpose

PR168 reviews the PR160-PR167 runtime-attached internal v1 sequence after the
first default-off hook exists. It asks whether the system is only mechanically
attached, whether it is product-useful yet, and what the next safest PR should
be.

This is a planning gate. It does not add runtime behavior, does not make the
hook default-on, does not run Lolla, does not call provider or model APIs, and
does not claim customer readiness, human validation, product proof,
answer-quality scoring, advice correctness, or action authorization.

## What PR160-PR167 Made Functional

The current worktree shows a coherent runtime-attached internal v1 package:

- PR160 defines a default-off, post-archive runtime attachment contract.
- PR161 defines the `decision_work/` sidecar layout and path-safety policy.
- PR162 adds a manual post-archive bundle generator for completed runs and
  explicitly supplied safe brief artifacts.
- PR163 adds a deterministic eligibility and blocker gate.
- PR164 adds a short user receipt renderer for available, caveated,
  agent-only, blocked, deferred, failed-closed, and disabled states.
- PR165 adds a checked-in-safe agent handoff packet.
- PR166 wires a default-off post-archive hook in `scripts/archive_run.py`
  behind `LOLLA_DECISION_WORK_BRIEF_AFTER_ARCHIVE`.
- PR167 reviews and packages the internal v1 runtime-attached slice.

The useful runtime hinge is real: archive completion can optionally write a
post-archive sidecar without touching live answer generation, prompts,
`SKILL.md`, or `scripts/skill/*`.

## What Is Still Not Truly Functional

The hook is mechanically attached, but not yet product-useful on its own.

The manual bundle generator can produce an available attachment only when safe
brief, enriched brief, and triage artifacts are explicitly supplied. The
runtime hook currently calls that path without run-specific safe brief inputs,
so a clean completed run normally records `deferred` with reasons such as
`safe_rendered_brief_not_supplied` and
`runtime_specific_triage_read_not_supplied`.

That is the right fail-closed behavior, but it means runtime-attached internal
v1 has not yet solved safe brief supply. It records status, receipt, handoff,
and blockers; it does not automatically create a semantically rich
run-specific brief.

The short receipt is intentionally conservative, but available receipts can
still be generic when no action-consequence line is supplied. The agent handoff
preserves refs, missingness, route outputs, and non-claims, but its usefulness
depends on whether the bundle contains a real brief and triage read rather than
only a deferred status.

## Options Considered

### A. Product Surface Simplification

This would patch receipt wording so available, blocked, deferred, caveated,
and agent-only states are clearer.

Use it when the main weakness is that users cannot understand the receipt
state. It would not solve safe run-specific brief supply.

### B. Safe Brief Supply Planning

This would plan how the runtime hook should obtain safe run-specific rendered
briefs, enriched briefs, and triage inputs without relying on manually passed
fixture paths and without exposing raw/private content.

Use it when the hook can attach sidecars but cannot yet supply useful
run-specific brief material. That is the current state.

### C. Small Internal Demo Walkthrough

This would show the flagged hook, sidecar, receipt, and handoff on a safe
fixture or temp run artifact set.

Use it after the supply path is clear enough that the demo would show product
behavior rather than mostly deferred plumbing.

### D. Runtime Fixture Expansion

This would add more fixture states for available, blocked, deferred,
caveated, and agent-inspection-only runtime attachments.

Use it when the mechanics are under-tested. The current tests already cover
the core states well enough to avoid making fixture expansion the immediate
next slice.

### E. Package And Pause

This would stop with PR160-PR167 as enough for maintainer review.

Use it if the next move needs product or maintainer input more than a
technical plan. The current evidence points to one concrete planning gap
instead.

## Decision Gate

Selected next step:

```text
safe_brief_supply_planning
```

Recommended next PR:

```text
PR169 Decision Work Brief Runtime Safe Brief Supply Plan v0
```

Reason:

The default-off runtime hook is coherent and safe, but the most important
unresolved gap is not receipt polish or more fixture breadth. It is how a
runtime-attached path should acquire safe run-specific Decision Work Brief,
enriched brief, and triage inputs without copying raw/private content, calling
models from the runtime, or pretending deterministic code can interpret messy
conversation meaning.

## PR169 Follow-up

PR169 implements that planning slice:

[runtime safe brief supply plan](decision-work-brief-runtime-safe-brief-supply-plan-v0.md)

It selects `build_safe_brief_supply_resolver_contract` and recommends
`PR170 Decision Work Brief Runtime Safe Supply Resolver Contract v0`.

## Explicit Non-Claims

PR168 does not:

- run `$lolla`;
- invoke the Lolla skill;
- call provider or model APIs;
- mutate historical archives;
- change runtime behavior;
- change prompts;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- create new Lolla runs;
- create new interpretation reads;
- create new builder outputs;
- check in raw/private content;
- claim customer readiness;
- claim human validation;
- claim product proof;
- score answer quality;
- approve or certify advice;
- authorize agent or automatic action;
- make runtime attachment default-on.
