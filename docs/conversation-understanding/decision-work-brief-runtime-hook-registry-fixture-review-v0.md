# Decision Work Brief Runtime Hook Registry Fixture Review v0

Status: PR176 review-only fixture gate

Date: 2026-07-02

## Purpose

PR176 reviews whether the runtime-attached Decision Work Brief hook can produce
coherent sidecar outputs when its safe semantic inputs come from the
checked-in-safe case registry added in PR175.

This is a review and test slice only. It does not add runtime behavior, change
the hook flag, add an interpretation queue, call models, create interpretation,
score answer quality, approve advice, or authorize action.

The review asks a narrow question:

> When registry-approved refs are supplied to the existing hook and
> resolver-aware bundle seam in temporary fixtures, do the sidecar outputs stay
> coherent for the three known examples?

## Registry Scope

PR176 uses the checked-in-safe registry:

`decision-work-brief-runtime-checked-in-safe-case-registry-v0.json`

The registry entries reviewed are:

| Case | Decision Family | Review Read |
|---|---|---|
| `launch-public-enterprise-beta` | Go-to-market / enterprise launch timing | Generated sidecar and available receipt. |
| `deploy-assisted-intake-routing` | Healthcare operations / deployment controls | Generated sidecar and available receipt; compliance caveats remain in the copied brief. |
| `ceo-remove-founding-cofounder` | Founder governance / relationship-sensitive authority transition | Generated sidecar and available receipt; relationship, governance, legal, equity, and board caveats remain in the copied brief. |

PR176 does not check in runtime sidecar fixtures. The tests build temporary
archive-like directories, feed registry-mode resolver output into the existing
hook/bundle path, inspect the resulting sidecars, and discard them.

## Fixture Scope

PR176 reviews eight fixture states.

| Fixture | Expected Result | Review Finding |
|---|---|---|
| `flag_off_registry_present` | no resolver lookup, bundle call, receipt, or sidecar | Coherent default-off behavior even when registry exists. |
| `registry_hit_launch_beta` | resolver status `resolved`, attachment state `generated` | Launch registry refs generate a coherent sidecar. |
| `registry_hit_deploy_intake` | resolver status `resolved`, attachment state `generated` | Deploy-intake registry refs generate a coherent sidecar. |
| `registry_hit_cofounder_high_risk` | resolver status `resolved`, attachment state `generated` | Cofounder registry refs generate a coherent sidecar, but the receipt is still generic. |
| `registry_miss_unknown_case` | registry lookup rejected before sidecar generation | No fake brief is supplied. |
| `registry_entry_missing_ref` | registry validation rejected before sidecar generation | Missing checked-in-safe refs do not partially succeed. |
| `registry_entry_privacy_marker` | registry validation rejected before sidecar generation | Unsafe content is blocked before it can feed a sidecar. |
| `registry_direct_runtime_interpretation_forbidden` | resolver status `blocked_direct_runtime_interpretation`, attachment state `blocked` | Direct runtime interpretation remains refused. |

Three fixture states are intentionally marked not directly runnable as hook
sidecars in PR176: unknown registry case, missing registry ref, and registry
privacy-marker input. They are rejected by the registry/resolver layer before a
sidecar exists. Exercising them as hook sidecars would require adding a
first-class registry case-key input to the hook, which PR176 does not do.

## Aggregate Read

The registry-backed fixture pass is coherent. The three registry entries can
feed resolver-approved refs into the existing hook and resolver-aware runtime
bundle seam. The hook then writes generated attachment status, short receipt,
safe supply resolver output, copied safe brief artifacts, and agent handoff
packets in temporary sidecars.

The strongest useful signal is repeatability. PR174 showed useful sidecar
states using manually supplied safe refs. PR175 added a deterministic registry.
PR176 shows those registry refs can drive the same generated hook sidecars in
tests without checking in path-sensitive sidecar outputs.

The strongest unresolved risk is still supply. The production hook has not been
changed to look up registry cases by itself, and arbitrary completed runs still
normally defer because safe run-specific brief, enrichment, and triage inputs
are not automatically available.

The highest overtrust risk is the cofounder case. The copied brief carries
relationship, governance, legal, equity, and board caveats, but the short
receipt still says the Decision Work Brief is available. That is acceptable for
an internal fixture gate only if the package refresh keeps the limitation
visible.

## Fixture Policy

PR176 checks in only the review conclusions:

- no checked-in runtime sidecar fixtures;
- no raw/private conversation text;
- no raw revised-answer text;
- no raw memo text;
- no provider text;
- no private ledgers;
- no local absolute paths;
- no secrets;
- no human-review answers.

## Decision Gate

Selected next step:

```text
runtime_attached_v1_package_refresh
```

Recommended next PR:

```text
PR177 Decision Work Brief Runtime-Attached Internal v1 Package Refresh v0
```

Reason:

The registry-backed fixture pass is coherent enough to package the
runtime-attached internal v1 tranche with limitations. The package refresh
should not claim arbitrary-run semantic supply, product readiness, human
validation, product proof, answer-quality scoring, advice correctness, or
action authorization. It should explicitly disclose that the checked-in
registry is a curated demo/test supply source, not a general live-run solution.

PR177 performs that package refresh:

[runtime-attached internal v1 package refresh](decision-work-brief-runtime-attached-internal-v1-package-refresh-v0.md)

The refresh keeps the package internal, default-off, and source-limited, and
recommends a narrow manifest-derived audit/stage/commit step.

## Explicit Non-Claims

PR176 does not claim:

- customer readiness;
- default-on runtime behavior;
- human validation;
- product proof;
- advice correctness;
- proof that Lolla improved decisions;
- answer-quality scoring;
- approval or certification;
- agent or automatic action authorization;
- a general arbitrary-run solution;
- runtime interpretation;
- safe operation from checked-in-safe fixtures alone.
