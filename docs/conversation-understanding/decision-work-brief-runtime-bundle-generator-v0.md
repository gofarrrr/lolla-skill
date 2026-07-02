# Decision Work Brief Runtime Bundle Generator v0

Status: PR162 manual post-archive bundle generator

Date: 2026-07-02

## Purpose

PR162 adds a deterministic manual CLI for producing a Decision Work Brief
runtime-attachment bundle from a completed run directory and optional existing
safe brief artifacts.

The generator is deliberately conservative. It can package existing safe
brief/triage artifacts into the PR161 sidecar shape, but it does not infer a
new Decision Work Brief from raw run content. If no safe rendered brief is
supplied, it writes a `deferred` attachment status and a short receipt saying
the brief is unavailable.

PR172 adds a preferred resolver-aware input path. The generator can now consume
one PR171 safe supply resolver output JSON and use its feedability decision to
copy only resolver-approved safe refs, defer missing inputs, or block unsafe
states. This still does not wire the resolver into the runtime hook.

## CLI

```bash
python3 scripts/evals/build_decision_work_brief_runtime_bundle.py \
  --run-dir <completed-run-dir> \
  --resolver-output /tmp/decision_work_safe_supply_resolver.json \
  --out <safe-output-dir> \
  --pretty
```

Legacy/manual operator refs remain available:

```bash
python3 scripts/evals/build_decision_work_brief_runtime_bundle.py \
  --run-dir <completed-run-dir> \
  --out <safe-output-dir> \
  --brief-markdown docs/conversation-understanding/decision-work-brief-rendered-launch-public-enterprise-beta-v0.md \
  --enriched-brief docs/conversation-understanding/decision-work-brief-builder-enriched-launch-public-enterprise-beta-v0.md \
  --triage-packet /tmp/decision_work_automatic_triage_packet.json \
  --triage-read reviews/codex-assisted/decision-work-automatic-triage-provisional-read-v0/read.json \
  --pretty
```

`--resolver-output` is the preferred PR172 input when a resolver result exists.
`--brief-markdown`, `--enriched-brief`, `--triage-packet`, and `--triage-read`
are optional manual refs. They must point at existing safe artifacts. Without
safe brief refs, the CLI still produces an attachment status and user receipt,
but the state is `deferred` rather than `generated`.

## Outputs

The CLI writes a `decision_work/` bundle under the selected output directory:

- `attachment_status.json`
- optional `safe_supply_resolver.json`
- `user_receipt.md`
- optional `decision_work_brief.md`
- optional `decision_work_brief_enriched.md`
- optional `automatic_triage_packet.json`
- optional `automatic_triage_read.json`

PR163-PR166 add formal eligibility logic, receipt rendering, agent handoff, and
the default-off runtime hook. PR172 keeps the resolver integration on the
manual bundle path only.

## Safety Rules

The manual generator:

- refuses output inside the input run directory by default;
- reads structured runtime artifacts only for presence and parseability;
- does not copy raw conversation, revised answer, memo text, provider text, or
  private ledgers;
- copies only explicitly provided safe artifacts;
- copies only resolver-approved refs when `--resolver-output` is supplied;
- records blocked/deferred/failure reasons;
- records resolver mode, resolver status, feedability, deferred inputs, blocked
  inputs, and unsafe excluded inputs;
- uses relative bundle refs;
- preserves conservative custody flags;
- does not score advice;
- does not authorize agent or automatic action.

## Decision Gate

Decision gate:

```text
runtime_hook_resolver_wiring
```

Reason:

The manual generator can now create a safe attachment bundle from
resolver-approved source artifacts, can produce agent-only/caveated output for
partial supply, can defer for no-safe-inputs, queue, or local-private-required
states, and can block resolver-reported unsafe states. The next slice may wire
the resolver/bundle chain into the default-off post-archive hook, still behind
the flag and still fail-closed.

## Explicit Non-Claims

PR162 does not:

- run `$lolla`;
- invoke the Lolla skill;
- call provider or model APIs from repo code;
- mutate input archives;
- change runtime behavior;
- change prompts;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- create new Lolla runs;
- create new interpretation reads;
- create new semantic brief content;
- check in raw/private content;
- claim human validation;
- claim product proof;
- score answer quality;
- approve or certify advice;
- authorize agent or automatic action;
- implement runtime attachment.
