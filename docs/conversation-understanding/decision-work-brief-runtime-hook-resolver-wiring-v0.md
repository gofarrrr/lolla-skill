# Decision Work Brief Runtime Hook Resolver Wiring v0

Status: PR173 default-off hook resolver wiring

Date: 2026-07-02

## Purpose

PR173 wires the existing default-off post-archive runtime hook to the PR171 safe
supply resolver and the PR172 resolver-aware runtime bundle.

The hook now has a real deterministic chain when explicitly enabled:

```text
completed archive
-> safe supply resolver
-> resolver-aware runtime bundle
-> eligibility gate
-> short receipt
-> agent handoff packet
```

The hook still runs only after archive completion, still uses
`LOLLA_DECISION_WORK_BRIEF_AFTER_ARCHIVE`, and still remains off by default.

## Flag Behavior

The hook is enabled only when:

```text
LOLLA_DECISION_WORK_BRIEF_AFTER_ARCHIVE=1
LOLLA_DECISION_WORK_BRIEF_AFTER_ARCHIVE=true
LOLLA_DECISION_WORK_BRIEF_AFTER_ARCHIVE=on
LOLLA_DECISION_WORK_BRIEF_AFTER_ARCHIVE=yes
```

When the flag is off:

- no resolver runs;
- no bundle runs;
- no `decision_work/` sidecar is written;
- archive behavior remains unchanged.

## Resolver Mode

The hook chooses the safest resolver mode available from local inputs:

- `archive_local_safe_resolver` when no explicit safe refs are supplied;
- `manual_ref_supply_only` when explicit safe refs are supplied by env;
- an explicit `LOLLA_DECISION_WORK_BRIEF_RESOLVER_MODE` override for tests and
  operator debugging.

`future_direct_runtime_interpretation_not_allowed` remains a supported blocked
mode. It records `blocked_direct_runtime_interpretation` and never calls a
model.

## Optional Safe Ref Env Vars

The hook can pass explicit operator-supplied refs into the resolver:

- `LOLLA_DECISION_WORK_BRIEF_JSON_REF`
- `LOLLA_DECISION_WORK_BRIEF_REF`
- `LOLLA_DECISION_WORK_BRIEF_ENRICHED_REF`
- `LOLLA_DECISION_WORK_BRIEF_INTERPRETATION_READ_REF`
- `LOLLA_DECISION_WORK_BRIEF_TRIAGE_PACKET_REF`
- `LOLLA_DECISION_WORK_BRIEF_TRIAGE_READ_REF`

These refs do not bypass the resolver. The hook copies supplied refs into a
temporary local resolver workspace, asks the resolver to validate them, and then
passes only resolver output to the runtime bundle. The sidecar records refs and
status, not local absolute paths.

## Runtime Outcomes

The enabled hook now handles:

- no safe refs: `deferred` with resolver status `no_safe_inputs`;
- safe brief plus triage refs: `generated` with available receipt;
- safe brief without triage read: `generated_agent_only` with caveated/agent
  inspection receipt;
- offline queue mode: `deferred` with queue handoff status;
- local-private operator mode: `deferred` without exporting private content;
- blocked resolver status: `blocked`;
- direct runtime interpretation mode: `blocked`;
- resolver or bundle exception: `failed_closed`.

Archive completion remains non-blocking in all cases.

## Sidecar Outputs

When enabled, the hook can write:

- `decision_work/attachment_status.json`
- `decision_work/safe_supply_resolver.json`
- `decision_work/user_receipt.md`
- optional safe copied brief/enriched/triage refs
- `decision_work/agent_handoff_packet.json`

When no safe semantic refs exist, the hook still writes status and receipt, but
does not invent a brief.

## What PR173 Does Not Do

PR173 does not:

- run `$lolla`;
- invoke the Lolla skill;
- call provider or model APIs;
- create new Lolla runs;
- mutate historical archives;
- change prompts;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- make runtime attachment default-on;
- add direct runtime interpretation;
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

The default-off runtime hook is no longer merely mechanical. When enabled, it
can call the resolver-aware bundle chain and produce a concrete sidecar state:
available, agent-only/caveated, deferred, blocked, or failed closed.

## Strongest Unresolved Risk

The hook is still not product-complete for arbitrary live runs. Without safe
operator-supplied or future resolver-discovered semantic refs, the normal state
is still deferred/no-safe-inputs. The system needs sidecar output review before
more machinery is added.

## Decision Gate

Selected next step:

```text
runtime_hook_resolver_fixture_review
```

Recommended next PR:

```text
PR174 Runtime Hook Resolver Fixture Review v0
```

Reason:

The hook now calls the resolver/bundle chain safely behind the existing flag.
The next useful step is to review actual sidecar outputs for flag-off,
deferred/no-safe-inputs, safe-ref available, agent-only, blocked, and
failed-closed states before adding a registry, queue, or broader runtime
behavior.

## PR174 Follow-Up

PR174 performs that review without changing runtime behavior. The fixture pass
finds the sidecar states coherent and selects:

```text
checked_in_safe_case_registry
```

Recommended next PR:

```text
PR175 Decision Work Brief Runtime Checked-In Safe Case Registry v0
```

Reason:

The hook can produce coherent available, agent-only, deferred, blocked, and
failed-closed states, but useful generated states still depend on explicit safe
refs. A checked-in-safe registry is the smallest next supply layer for stable
demos and tests without adding runtime interpretation.
