# Decision Work Brief Runtime Sidecar v0

Status: PR161 runtime sidecar contract

Date: 2026-07-02

Schema: `lolla.decision_work_brief_runtime_sidecar.v0`

## Purpose

PR161 defines where Decision Work Brief runtime-attachment artifacts should
live relative to a completed Lolla archive. It does not implement generation,
runtime hooks, archive writing, model calls, scoring, product proof, human
validation, or agent action authorization.

The sidecar is designed for the PR160 contract:

- default off;
- post-archive only;
- fail closed;
- source refs by default;
- no raw/private export by default;
- blocked/deferred states as first-class outcomes.

## Recommended Sidecar Layout

Future runtime-attached artifacts should live under:

```text
decision_work/
  attachment_status.json
  decision_work_brief.json
  decision_work_brief.md
  decision_work_brief_enriched.md
  automatic_triage_packet.json
  automatic_triage_read.json
  agent_handoff_packet.json
  user_receipt.md
```

The files are optional except `attachment_status.json`. Missing artifacts must
be recorded explicitly as missing, deferred, blocked, or failed closed.

## Manual Output Mode

Before a runtime hook exists, PR162 should write the same bundle shape to an
operator-selected output directory outside the input run archive. That lets the
bundle be tested without mutating completed archives.

## Runtime Sidecar Mode

A future PR166 hook may write the sidecar into `decision_work/` only after the
archive is complete and only behind an explicit local flag. That write is a
post-archive sidecar append, not a mutation of historical source artifacts.

If the run is incomplete, source refs do not resolve, hygiene is unsafe, or
privacy export would be unsafe, the sidecar state must be `blocked` or
`failed_closed`.

## Path Safety

The sidecar contract requires:

- manual outputs outside the input run directory unless explicitly testing a
  post-archive sidecar path;
- relative artifact refs in checked-in or agent-facing output;
- no local absolute paths in generated JSON or Markdown;
- no raw/private content;
- no provider text;
- no private ledgers;
- no secrets;
- no broad archive rewriting.

## Decision Gate

Decision gate:

```text
proceed_to_manual_runtime_bundle_generator
```

Reason:

The sidecar plan is coherent enough to build a manual post-archive generator.
The manual generator should produce the same artifact shape outside the input
archive first, then a later flagged hook can write it beside completed archive
artifacts.

## Explicit Non-Claims

PR161 does not:

- run `$lolla`;
- invoke the Lolla skill;
- call provider or model APIs from repo code;
- mutate archives;
- change runtime behavior;
- change prompts;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- create new Lolla runs;
- create new interpretation reads;
- create new builder outputs;
- check in raw/private content;
- claim human validation;
- claim product proof;
- score answer quality;
- approve or certify advice;
- authorize agent or automatic action;
- implement runtime attachment.
