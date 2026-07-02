# Decision Work Brief Runtime Bundle Resolver Integration v0

Status: PR172 manual bundle resolver integration

Date: 2026-07-02

## Purpose

PR172 teaches the manual post-archive runtime bundle generator to consume the
PR171 safe supply resolver output.

The manual bundle can now take one resolver JSON file and use its feedability
decision to choose whether to:

- copy resolver-approved safe brief, enriched-brief, triage-packet, and
  triage-read refs into the sidecar;
- generate an available receipt;
- generate an agent-inspection-only/caveated receipt;
- defer because no safe semantic inputs exist;
- preserve queued or local-private-required status;
- block when the resolver reports privacy, schema, path, source, or direct
  runtime-interpretation risk.

This is still a manual bundle path. PR172 does not wire the resolver into the
default-off runtime hook and does not create a new interpretation layer.

## CLI

Preferred PR172 shape:

```bash
python3 scripts/evals/build_decision_work_brief_runtime_bundle.py \
  --run-dir <completed-run-dir> \
  --resolver-output /tmp/decision_work_safe_supply_resolver.json \
  --out <safe-output-dir> \
  --pretty
```

The resolver output can be created with:

```bash
python3 scripts/evals/resolve_decision_work_brief_safe_supply.py \
  --run-dir <completed-run-dir> \
  --contract docs/conversation-understanding/decision-work-brief-runtime-safe-supply-resolver-contract-v0.json \
  --brief-markdown docs/conversation-understanding/decision-work-brief-rendered-launch-public-enterprise-beta-v0.md \
  --enriched-brief docs/conversation-understanding/decision-work-brief-builder-enriched-launch-public-enterprise-beta-v0.md \
  --triage-read reviews/codex-assisted/decision-work-automatic-triage-provisional-read-v0/read.json \
  --out /tmp/decision_work_safe_supply_resolver.json \
  --pretty
```

Existing explicit manual-ref flags remain available for operator/debug use:

- `--brief-json`
- `--brief-markdown`
- `--enriched-brief`
- `--triage-packet`
- `--triage-read`

When `--resolver-output` is supplied, the resolver output is treated as the
preferred authority for safe supplied refs. The bundle records the resolver
status and does not invent missing brief meaning.

## Resolver State Handling

The manual bundle now preserves these resolver outcomes:

- `resolved`: copy feedable safe refs and produce an available attachment when
  eligibility also passes.
- `partially_resolved`: copy available safe refs and produce an
  agent-inspection-only/caveated attachment when a safe brief exists but full
  triage inputs are missing.
- `no_safe_inputs`: defer and write a receipt saying the brief is unavailable.
- `queued_for_offline_interpretation`: defer while preserving queue handoff
  status.
- `local_private_operator_required`: defer without exporting private content.
- `blocked_*`: block and preserve the resolver reason.
- `blocked_direct_runtime_interpretation`: block and refuse to interpret.
- unsupported resolver schema or privacy-marker resolver content: fail closed
  into blocked attachment status.

## Attachment Status Additions

`attachment_status.json` now records a `resolver_summary` when resolver output
is supplied. The summary includes:

- resolver output ref;
- resolver mode;
- resolver status;
- whether the resolver says the bundle can be fed;
- resolved input names and safe refs;
- deferred input names;
- blocked input names/reasons;
- unsafe inputs excluded;
- queue handoff status;
- manual operator requirements;
- resolver non-claims.

The sidecar can also include:

- `decision_work/safe_supply_resolver.json`
- `decision_work/automatic_triage_packet.json`

## Receipt Behavior

Receipts remain short:

```text
Decision Work Brief: available

What changed: see the attached brief.

Main caveat: this is an audit summary, not proof that the advice is correct.
```

Deferred resolver states render as:

```text
Decision Work Brief: deferred

Reason: <resolver state and missing-input reasons>.
```

Blocked resolver states render as:

```text
Decision Work Brief: blocked

Reason: <resolver blocker>.
```

The receipt never renders the full brief into chat by default, never scores
advice, and never authorizes action.

## Agent Handoff

The agent handoff packet now carries a compact safe supply resolver summary
from the attachment status:

- resolver output ref;
- resolver status and mode;
- feedability;
- resolved, deferred, and blocked input names;
- unsafe input exclusions;
- queue handoff status;
- explicit no-action-authorization flags.

It still carries refs/status only. It does not copy raw conversation text,
provider text, private ledgers, raw memo text, or local absolute paths.

## What PR172 Does Not Do

PR172 does not:

- run `$lolla`;
- invoke the Lolla skill;
- call provider or model APIs;
- create new Lolla runs;
- mutate historical archives;
- change prompts;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- make the runtime hook default-on;
- wire the resolver into the runtime hook;
- infer messy conversation meaning;
- create a new interpretation read;
- create a new builder output;
- check in raw/private content;
- claim customer readiness;
- claim human validation;
- claim product proof;
- score answer quality;
- approve or certify advice;
- authorize agent or automatic action.

## Strongest Useful Signal

The manual runtime bundle can now consume one deterministic resolver output and
carry safe supply status through attachment status, receipt, and agent handoff.
This makes resolver feedability operational before touching the default-off
post-archive hook.

## Strongest Unresolved Risk

The system is still input-supply-limited for arbitrary live runs. Resolver
output can feed the bundle when safe refs exist, but the runtime hook does not
yet call the resolver, and semantic brief/enrichment/triage inputs still require
safe supplied refs or future offline interpretation.

## Decision Gate

Selected next step:

```text
runtime_hook_resolver_wiring
```

Recommended next PR:

```text
PR173 Runtime Hook Resolver Wiring v0
```

Reason:

The manual bundle now handles resolved, partial, deferred, queued,
local-private-required, blocked, and invalid resolver states while preserving
privacy boundaries and non-claims. The next narrow slice can let the
default-off post-archive hook call the resolver/bundle chain, still behind the
flag and still fail-closed.
