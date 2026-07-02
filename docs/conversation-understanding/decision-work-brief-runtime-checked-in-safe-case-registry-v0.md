# Decision Work Brief Runtime Checked-In Safe Case Registry v0

Status: PR175 deterministic safe-ref registry

Date: 2026-07-02

Schema:
`lolla.decision_work_brief_runtime_checked_in_safe_case_registry.v0`

Registry:
[decision-work-brief-runtime-checked-in-safe-case-registry-v0.json](decision-work-brief-runtime-checked-in-safe-case-registry-v0.json)

## Purpose

PR175 adds a deterministic checked-in-safe registry for the runtime-attached
Decision Work Brief path.

The registry maps known case keys to approved checked-in-safe refs:

- rendered brief Markdown;
- builder-enriched brief Markdown;
- interpretation read JSON;
- automatic triage read JSON when available.

This gives demos and regression tests a repeatable safe input source. It avoids
manual env refs for the three known examples while preserving the important
boundary: arbitrary completed runs still do not get semantic interpretation
from deterministic runtime code.

## Included Entries

The registry includes three cases because each has checked-in-safe rendered
brief, builder-enriched brief, interpretation read, and provisional automatic
triage read coverage:

| Case | Decision Family | Registry Status |
|---|---|---|
| `launch-public-enterprise-beta` | go-to-market / enterprise launch timing | Included as the lowest-sensitivity demo candidate. |
| `deploy-assisted-intake-routing` | healthcare operations / deployment controls | Included with domain/compliance sensitivity preserved. |
| `ceo-remove-founding-cofounder` | founder governance / relationship-sensitive authority transition | Included but marked high relationship/governance sensitivity. |

No case-specific automatic triage packet fixture is checked in. The registry
therefore omits `automatic_triage_packet_json_ref` and records that status as
`not_checked_in` instead of inventing one.

## How Registry Mode Works

Registry mode is still resolver-first:

```text
case key
-> checked-in-safe registry
-> safe supply resolver in checked_in_safe_case_registry mode
-> resolver-aware runtime bundle
-> attachment status / receipt / handoff
```

The registry loader validates that refs:

- are relative repo refs;
- exist;
- have the expected suffix;
- parse when JSON;
- use supported schema versions for known JSON inputs;
- contain no private markers;
- carry conservative non-claims.

The resolver then emits normal PR171 output with
`resolver_mode: checked_in_safe_case_registry`. A resolved registry entry can
feed the PR172 bundle and produce a generated sidecar in tests. That does not
mean the runtime hook is default-on or generally product-ready.

## CLI

Inspect one registry entry:

```bash
python3 scripts/evals/resolve_decision_work_brief_safe_case_registry.py \
  --case-key launch-public-enterprise-beta \
  --case-registry docs/conversation-understanding/decision-work-brief-runtime-checked-in-safe-case-registry-v0.json \
  --out /tmp/decision_work_safe_case_registry_entry.json \
  --pretty
```

Feed registry refs through the resolver:

```bash
python3 scripts/evals/resolve_decision_work_brief_safe_supply.py \
  --run-dir <completed-run-dir> \
  --mode checked_in_safe_case_registry \
  --case-registry docs/conversation-understanding/decision-work-brief-runtime-checked-in-safe-case-registry-v0.json \
  --case-key launch-public-enterprise-beta \
  --out /tmp/decision_work_safe_supply_resolver.json \
  --pretty
```

## What This Is Not

The registry is not:

- a general arbitrary-run solution;
- an interpretation queue;
- a direct runtime interpretation path;
- a model-call layer;
- product proof;
- human validation;
- answer-quality scoring;
- approval or certification;
- action authorization.

It is a deterministic safe-ref supply source for known checked-in-safe examples.

## Strongest Useful Signal

The resolver and bundle can now reach generated sidecars for known examples
without manual env refs. That makes runtime attachment demos and regression
tests repeatable while keeping safe refs explicit.

## Strongest Unresolved Risk

The registry covers curated examples only. Real arbitrary runs still normally
defer until a safe offline interpretation queue, local-private operator flow, or
another reviewed supply path creates run-specific brief/enrichment/triage refs.

## Decision Gate

Selected next step:

```text
runtime_hook_registry_fixture_review
```

Recommended next PR:

```text
PR176 Decision Work Brief Runtime Hook Registry Fixture Review v0
```

Reason:

Registry integration works through the resolver and manual bundle path. The
next narrow check should review concrete hook sidecars produced from
registry-supplied safe refs, without making the hook default-on or treating the
registry as arbitrary-run product readiness.

PR176 performs that registry-backed fixture review with temporary sidecars. It
confirms that the launch-beta, deploy-intake, and cofounder registry entries
can drive generated hook sidecars through the resolver-aware bundle seam, while
still recording that arbitrary completed runs need future safe semantic supply.
