# Decision Work Brief Runtime Safe Supply Resolver v0

Status: PR171 deterministic resolver implementation

Date: 2026-07-02

Contract:
[runtime safe supply resolver contract](decision-work-brief-runtime-safe-supply-resolver-contract-v0.md)

## Purpose

PR171 implements the deterministic safe supply resolver defined by PR170.

The resolver answers:

```text
Do safe Decision Work Brief inputs exist for this completed run, and can those
refs feed the PR162 runtime bundle?
```

It does not answer what the conversation meant. It does not create a Decision
Work Brief, produce an interpretation read, create a triage read, call a model,
score advice, approve output, or authorize action.

## What The Resolver Does

The resolver reads:

- a completed run directory ref;
- the PR170 resolver contract;
- optional operator-supplied safe refs for brief, enriched brief,
  interpretation, triage, eligibility, or attachment-status artifacts;
- optional checked-in-safe case registry and case key;
- a resolver mode.

It emits a JSON object with:

- `schema_version: lolla.decision_work_brief_runtime_safe_supply_resolver.v0`;
- source run ref;
- resolver mode and resolver status;
- input classification for each PR170 input type;
- resolved, deferred, blocked, and excluded inputs;
- queue handoff status;
- manual operator requirements;
- privacy policy;
- conservative custody flags;
- non-claims;
- whether the result can feed the runtime bundle.

The output carries refs and status only. It does not copy raw/private content
into the resolver result.

## CLI

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

Optional inputs:

- `--case-registry`
- `--case-key`
- `--brief-json`
- `--brief-markdown`
- `--enriched-brief`
- `--interpretation-read`
- `--triage-packet`
- `--triage-read`
- `--eligibility-result`
- `--attachment-status`
- `--mode`

The CLI writes resolver output only. It does not write a sidecar, mutate the
run archive, or call the runtime hook.

PR175 adds registry mode:

```bash
python3 scripts/evals/resolve_decision_work_brief_safe_supply.py \
  --run-dir <completed-run-dir> \
  --mode checked_in_safe_case_registry \
  --case-registry docs/conversation-understanding/decision-work-brief-runtime-checked-in-safe-case-registry-v0.json \
  --case-key launch-public-enterprise-beta \
  --out /tmp/decision_work_safe_supply_resolver.json \
  --pretty
```

In this mode, the resolver validates the checked-in-safe registry entry first
and then emits the same resolver output shape used by the manual bundle. The
registry supplies refs only. It does not create interpretation or make the
runtime hook default-on.

## Modes Implemented

PR171 supports the PR170 modes:

- `disabled`
- `manual_ref_supply_only`
- `checked_in_safe_case_registry`
- `archive_local_safe_resolver`
- `offline_interpretation_queue`
- `local_private_operator_mode`
- `future_direct_runtime_interpretation_not_allowed`

`future_direct_runtime_interpretation_not_allowed` always returns
`blocked_direct_runtime_interpretation`.

`offline_interpretation_queue` records queue handoff status and does not feed
the bundle.

`local_private_operator_mode` records that an operator is required and does
not feed the default runtime bundle.

## Status Logic

The resolver emits:

- `not_requested` when disabled;
- `blocked_direct_runtime_interpretation` for the rejected runtime model-call
  mode;
- `queued_for_offline_interpretation` for offline queue mode;
- `local_private_operator_required` for local-private operator mode;
- `blocked_privacy_risk` when supplied refs contain private markers;
- `blocked_unsafe_path` when a checked-in-safe registry ref is not repo
  relative;
- `blocked_untrusted_source` for missing or unsupported supplied refs;
- `blocked_schema_invalid` for malformed or unsupported JSON refs;
- `no_safe_inputs` when no safe semantic brief/triage refs are supplied;
- `partially_resolved` when a safe brief ref exists but full triage/enrichment
  inputs are missing;
- `resolved` when safe brief and triage-read refs are supplied.

`partially_resolved` can still feed the PR162 bundle because the bundle can
produce an agent-inspection-only or caveated attachment from a safe brief ref.

## Safety Checks

The resolver:

- rejects missing supplied refs;
- rejects unsupported file suffixes;
- rejects malformed JSON refs;
- rejects unsupported JSON schema versions for known JSON inputs;
- rejects privacy-marker content;
- redacts local absolute paths in output by carrying only file names for
  operator-supplied local refs;
- requires repo-relative refs for checked-in-safe registry mode;
- validates checked-in-safe registry refs before using them;
- preserves conservative custody flags;
- excludes raw/private and authority-bearing inputs.

## What It Refuses To Do

The resolver does not:

- run `$lolla`;
- invoke the Lolla skill;
- call provider or model APIs;
- create new Lolla runs;
- mutate historical archives;
- change prompts;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- make the runtime hook default-on;
- broaden runtime hook behavior;
- add direct runtime interpretation;
- infer messy conversation meaning;
- check in raw/private content;
- claim customer readiness;
- claim human validation;
- claim product proof;
- score answer quality;
- approve or certify advice;
- authorize agent or automatic action;
- prove that Lolla improved decisions.

## What Remains Missing

The resolver makes safe input supply real. PR172 wires resolver output into the
manual runtime bundle path, so resolver-approved refs can now feed attachment
status, receipt, and agent handoff. PR173 wires that resolver-aware bundle into
the default-off hook. PR175 adds a checked-in-safe registry for known examples
so demos and regression tests no longer depend only on manual env refs.

It can identify feedable manual or registry refs, reject unsafe refs, and
return clear deferred or blocked states. It still does not solve the hardest
product question: how arbitrary completed runs get safe run-specific brief,
interpretation, enrichment, and triage artifacts without copying private
content or moving semantic interpretation into deterministic runtime code.

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

The resolver can now emit deterministic feedability output from explicit safe
refs, and PR172 shows the manual PR162 bundle can consume that output across
resolved, partial, deferred, queued, local-private-required, blocked, and
invalid states. The next smallest useful slice is to let the default-off
post-archive hook call the resolver/bundle chain without changing the flag
default, adding interpretation, or adding model calls.

PR173 should not make runtime attachment default-on. It should not add model
calls or interpretation. It should only connect resolver-approved refs to the
already default-off hook path and preserve blocked/deferred output.
