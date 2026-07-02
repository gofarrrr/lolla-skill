# Decision Work Brief Runtime Hook Resolver Fixture Review v0

Status: PR174 review-only fixture gate

Date: 2026-07-02

## Purpose

PR174 reviews the actual sidecar states produced by the PR173 default-off
post-archive Decision Work Brief hook.

This is a review and test slice only. It does not add runtime behavior, change
the hook flag, add a registry, add a queue, call models, create interpretation,
score answer quality, approve advice, or authorize action.

The review asks a narrow question:

> When the hook is exercised against safe temporary fixtures, do the sidecar
> outputs stay coherent across flag-off, deferred, available, agent-only,
> blocked, privacy-blocked, and failed-closed states?

## Fixture Scope

PR174 reviews seven local fixture states. The tests create temporary completed
archive-like directories and safe temporary brief refs, then invoke only the
local hook and bundle code paths. No checked-in sidecar fixture is created,
because runtime sidecars are path-sensitive and would add noise without adding
more evidence.

| Fixture | Expected Hook Result | Review Finding |
|---|---|---|
| `flag_off` | no resolver call, no bundle call, no `decision_work/` sidecar | Coherent default-off behavior. |
| `flag_on_no_safe_refs` | resolver status `no_safe_inputs`, attachment state `deferred` | Coherent deferred state with no fake brief. |
| `flag_on_safe_refs_available` | resolver status `resolved`, attachment state `generated` | Coherent available state when explicit safe refs exist. |
| `flag_on_safe_brief_only_agent_or_caveated` | resolver status `partially_resolved`, attachment state `generated_agent_only` | Coherent agent-inspection path with missing triage/enrichment visible. |
| `direct_runtime_interpretation_blocked` | resolver status `blocked_direct_runtime_interpretation`, attachment state `blocked` | Coherent hard block with no interpretation attempt. |
| `unsafe_private_marker_blocked` | resolver status `blocked_privacy_risk`, attachment state `blocked` | Coherent privacy block with no unsafe marker copied into sidecar output. |
| `bundle_exception_failed_closed` | attachment state `failed_closed` | Coherent fail-closed state; archive caller remains non-blocked. |

## Aggregate Read

The hook output is coherent for the fixture states PR173 claims to support.
When the flag is off, it does nothing. When enabled without safe semantic refs,
it defers rather than inventing a brief. When explicit safe refs are supplied,
it can produce an available or agent-inspection-only sidecar. When direct
runtime interpretation or unsafe content appears, it blocks. When the bundle
raises, it writes a failed-closed status if possible and returns a non-blocking
result.

The strongest useful signal is that the hook is no longer just plumbing. It can
carry resolver status through attachment status, receipt, and agent handoff
without making runtime attachment default-on or adding model calls.

The strongest unresolved risk is supply. The useful available and agent-only
states still require explicit safe refs. Arbitrary completed runs normally
defer because no safe run-specific brief, enrichment, and triage read are
available yet.

## Fixture Policy

PR174 checks in only the review conclusions:

- no checked-in runtime sidecar fixtures;
- no raw/private conversation text;
- no raw revised-answer text;
- no raw memo text;
- no provider text;
- no private ledgers;
- no local absolute paths;
- no secrets;
- no human-review answers.

The tests use temporary directories to verify the hook sidecar shape and then
discard those outputs.

## Decision Gate

Selected next step:

```text
checked_in_safe_case_registry
```

Recommended next PR:

```text
PR175 Decision Work Brief Runtime Checked-In Safe Case Registry v0
```

Reason:

The hook sidecar states are coherent enough to review, but useful available and
caveated states still depend on manual safe refs. A deterministic
checked-in-safe registry would give demos and regression tests stable approved
refs without pretending arbitrary live runs can be interpreted automatically.
An offline interpretation queue remains important later for arbitrary runs, but
the next smallest useful slice is stable safe-ref supply for known examples.

PR175 implements that registry and connects it to the safe supply resolver. The
hook behavior itself remains unchanged.

PR176 then reviews registry-backed hook fixtures. It shows that the three
registry entries can generate temporary hook sidecars through the existing
resolver-aware bundle seam, while keeping the registry curated-example-only.

## Explicit Non-Claims

PR174 does not claim:

- customer readiness;
- default-on runtime behavior;
- human validation;
- product proof;
- advice correctness;
- proof that Lolla improved decisions;
- answer-quality scoring;
- approval or certification;
- agent or automatic action authorization;
- safe operation from checked-in-safe fixtures alone.
