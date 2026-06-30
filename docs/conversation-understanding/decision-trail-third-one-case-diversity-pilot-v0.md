# Decision Trail Third One-Case Diversity Pilot v0

Status: third one-case local-private specialist-output pilot
Date: 2026-06-30
Slice: PR102 Decision Trail Third One-Case Diversity Pilot v0

## Purpose

PR102 runs the one diversity-targeted pilot allowed by PR101.

The narrow question is:

> Does the patched specialist shape still preserve downgrade pressure on a
> non-cofounder, non-career decision family?

The answer is yes, with a different useful signal. PR102 does not make Lolla
look broadly stronger. It shows a deployment-controls case where the revised
answer is partly useful because it reduces noisy friction and adds an
operational precondition, while the core narrow-launch action was already
present in the vanilla conversation.

## Case Selection

PR102 pre-registered this case before reading local-private packet content:

```text
deploy-assisted-intake-routing/20260627T130339Z_4cd3cb
```

This case is a deployment-controls decision. It contrasts with the earlier
pilots:

- PR97: cofounder authority and operating control;
- PR100: career/family/startup role choice;
- PR102: outpatient-clinic workflow deployment controls.

The goal was not to find a more positive case. The goal was to test the
specialist lane on a different decision family where useful friction and noisy
friction can point in opposite directions.

## Local Packet Handling

PR102 generated local-private packet outputs under local temp paths only:

- metadata-only packet;
- include-text packet.

Both local packet outputs were deleted after review. The checked-in review
records only paraphrase-safe, summary-level specialist reads.

The include-text packet read 16 artifact records:

- 12 records were read as complete text;
- 4 large structured trace artifacts were truncated;
- the main conversation, revised answer, and memo were complete.

Every specialist role had to cite source-scope and truncation impact.

## Main Result

The PR102 net read is:

```text
local_private_specialist_read_partly_useful
```

The revised answer is not credited with inventing the core action. The vanilla
conversation already contained the central leadership recommendation: no broad
deployment, one urgent pilot clinic only, scheduling and billing as the lowest
risk auto-routing scope, higher-risk queues constrained, compliance/audit
language, support coverage, monitoring, and rollback.

The useful delta is narrower:

- the nine-gate leadership answer is compressed into fewer must-pass operating
  gates;
- the revised answer treats admin operating load as part of safety, not just
  rollout execution;
- it adds a backlog-diagnosis precondition before treating AI routing as the
  backlog solution;
- it changes passive monitoring into explicit pause and rollback triggers;
- it narrows the sales meaning of the pilot.

The strongest PR102 signal is therefore not more caution. It is better
friction: reduce process bloat while keeping the real stop conditions.

## What The Specialists Made Easier To See

The patched specialist shape made these points legible:

- material vanilla overlap remains load-bearing;
- useful friction can be the removal of noisy controls, not only the addition
  of gates;
- lost value can point in the opposite direction from PR97 and PR100: a simpler
  revised answer may lose stakeholder-specific checklist detail;
- fan-in should stay partial because the pilot lacks admin, compliance,
  patient, and clinic outcome evidence;
- local-private source access makes the distinction between core action and
  operating-shape delta much clearer than sparse checked-in-safe reports.

## What Remains Missing

PR102 still cannot answer:

- whether the clinic actually had routing uncertainty as the backlog cause;
- whether admins could operate the simplified controls under pressure;
- whether compliance would accept the narrowed release package;
- whether patients, doctors, support, and sales would experience the revised
  plan as clearer or under-specified;
- whether a human reviewer would call the revised answer better, partly better,
  too compressed, or mostly a restatement.

These are messy interpretation and outcome questions. Deterministic code should
not invent them.

## Boundary

PR102 did not:

- run `$lolla`;
- invoke the Lolla skill;
- call provider or model APIs;
- mutate archives;
- change runtime behavior;
- change prompts;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- add a broad judge;
- add answer-quality scoring;
- create automatic labels;
- authorize agent action;
- add graph DB, memory, embeddings, chunking, or GraphRAG;
- check in local-private packet output.

## Next Slice

PR102 should be the last one-case specialist-output pilot in this local-only
phase.

The next conservative slice should be:

```text
PR103 Decision Trail Specialist Pilot Phase Closure Gate v0
```

PR103 should compare PR97, PR100, and PR102 and decide whether to:

- pause until human review capacity returns;
- prepare a human-review intake packet;
- simplify the specialist contracts;
- or define one tiny multi-case review only if the three pilots justify it.

It should not run a fourth one-case pilot by momentum.

## Files

- [`review.json`](../../reviews/codex-assisted/decision-trail-third-one-case-diversity-pilot-v0/review.json)
