# Decision Work Brief Flagged Post-Archive Runtime Hook v0

Status: PR166 default-off runtime attachment hook, updated by PR173 resolver wiring

Date: 2026-07-02

Flag: `LOLLA_DECISION_WORK_BRIEF_AFTER_ARCHIVE`

## Purpose

PR166 adds the first runtime-attached behavior for Decision Work Briefs. PR173
wires that hook to the safe supply resolver and resolver-aware runtime bundle
chain. The hook runs from the Python archive writer after a run archive has
been created and its deterministic archive artifacts have been written.

The hook is default off. When the flag is not enabled, archive behavior remains
unchanged and no `decision_work/` sidecar is created.

## Runtime Shape

When explicitly enabled, the hook:

- runs only after archive completion;
- writes a `decision_work/` sidecar under the newly completed run directory;
- calls the PR171 safe supply resolver;
- passes resolver output to the PR172 resolver-aware bundle path in
  archive-sidecar mode;
- calls the PR163 eligibility gate;
- renders the PR164 short receipt;
- writes the PR165 agent handoff packet;
- records blocked, deferred, generated, agent-only, or failed-closed status;
- never blocks archive completion or the revised answer;
- fails closed if any attachment step raises.

## Flag Behavior

The flag is off unless set to one of:

- `1`
- `true`
- `on`
- `yes`

Any other value is treated as off.

## Default Output

For a clean completed archive without safe prebuilt Decision Work Brief
artifacts supplied, the hook records `deferred` with resolver status
`no_safe_inputs`. That is intentional: runtime attachment is wired, but
deterministic code does not invent a brief from raw conversation material.

Explicit operator-supplied safe refs may be passed by env and are validated by
the resolver before the bundle can consume them:

- `LOLLA_DECISION_WORK_BRIEF_JSON_REF`
- `LOLLA_DECISION_WORK_BRIEF_REF`
- `LOLLA_DECISION_WORK_BRIEF_ENRICHED_REF`
- `LOLLA_DECISION_WORK_BRIEF_INTERPRETATION_READ_REF`
- `LOLLA_DECISION_WORK_BRIEF_TRIAGE_PACKET_REF`
- `LOLLA_DECISION_WORK_BRIEF_TRIAGE_READ_REF`

`LOLLA_DECISION_WORK_BRIEF_RESOLVER_MODE` can override resolver mode for
operator debugging and tests. The direct runtime interpretation mode remains
blocked.

## Decision Gate

Decision gate:

```text
runtime_hook_resolver_fixture_review
```

Reason:

The default-off hook is post-archive, non-blocking, fail-closed, sidecar-only,
and now uses the resolver-aware bundle, eligibility, receipt, and handoff path.
The next useful slice should review concrete flag-off, deferred, available,
agent-only, blocked, and failed-closed sidecars before adding more machinery.
It does not touch `SKILL.md` or `scripts/skill/*`.

PR174 performs that review over temporary fixture sidecars and selects a
checked-in-safe case registry as the next supply step. The hook behavior itself
does not change in PR174.

PR175 adds that checked-in-safe registry, and PR176 reviews registry-backed
temporary hook sidecars for the three known examples. The hook remains
default-off and still does not interpret arbitrary completed runs.

## Explicit Non-Claims

PR166 does not:

- run `$lolla`;
- invoke the Lolla skill;
- call provider or model APIs from repo code;
- mutate historical archives;
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
- make runtime attachment default-on;
- render the full brief into chat by default.
