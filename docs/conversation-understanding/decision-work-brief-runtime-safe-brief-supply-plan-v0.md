# Decision Work Brief Runtime Safe Brief Supply Plan v0

Status: PR169 safe supply planning gate

Date: 2026-07-02

Review JSON:
[PR169 review](../../reviews/codex-assisted/decision-work-brief-runtime-safe-brief-supply-plan-v0/review.json)

## Purpose

PR169 decides how the runtime-attached Decision Work Brief path should safely
obtain run-specific brief, enriched brief, and triage inputs.

The current runtime hook is deliberately cautious. It can run after archive
completion behind `LOLLA_DECISION_WORK_BRIEF_AFTER_ARCHIVE`, write a
`decision_work/` sidecar, render a short receipt, and create an agent handoff
packet. But when no safe run-specific brief or triage artifacts are supplied,
it correctly records `deferred`.

PR169 does not implement a resolver. It defines the next safe contract slice.
It does not run Lolla, invoke the skill, call provider or model APIs, change
prompts, change runtime behavior, make the hook default-on, create new runs,
claim customer readiness, claim human validation, claim product proof, score
answer quality, or authorize action.

## Current Supply Shape

The PR162 manual bundle generator accepts:

- a completed run directory;
- optional Decision Work Brief JSON;
- optional rendered brief Markdown;
- optional enriched brief Markdown;
- optional automatic triage read JSON;
- runtime attachment and sidecar contracts.

The PR166 runtime hook currently supplies only the completed run directory and
the default contracts. That means it can create status, receipt, blocker state,
and handoff output, but it cannot create a useful run-specific brief by itself.

Offline builders already exist, but each has a different boundary:

- the Decision Work Brief packet builder can create a metadata-only source
  packet from a completed run;
- the brief renderer can render an existing populated brief JSON;
- the enrichment builder can enrich an existing rendered brief only when an
  existing interpretation read is supplied;
- the automatic triage packet builder can prepare metadata packets for the
  current checked-in-safe examples, but it does not produce a semantic triage
  read;
- provisional triage reads remain Codex-assisted/offline and are not runtime
  products.

So the missing piece is not another runtime hook. It is a safe supply contract
that tells the hook what it may use, what it must reject, and what deferred
state to record when semantic inputs do not exist.

## Required Inputs And Current Classification

| Input | Current status | Safe default |
|---|---|---|
| Completed run directory | `available_from_completed_run_artifacts` | Use for structured artifact presence, parseability, refs, and blocker state only. |
| Attachment and sidecar contracts | `available_from_manual_operator_ref` | Use repo contract defaults; reject unsupported schemas. |
| Decision Work Brief JSON | `not_available_yet` for arbitrary runtime runs | Do not synthesize from raw conversation; defer until a bounded interpreter or safe resolver supplies it. |
| Rendered brief Markdown | `available_from_existing_checked_in_safe_example_only` | Copy only an explicit safe ref or future resolver-approved run-specific ref. |
| Enriched brief Markdown | `available_from_existing_checked_in_safe_example_only` | Copy only when both rendered brief and interpretation read are resolver-approved. |
| Interpretation read JSON | `requires_future_llm_interpretation` | Keep out of runtime generation for now; route to future offline or calibrated interpretation. |
| Automatic triage packet JSON | `available_from_existing_offline_builder` only for the current fixed examples | Allow metadata-only packet generation later, but do not treat it as a triage read. |
| Automatic triage read JSON | `requires_future_triage_read` | Defer unless a safe provisional or calibrated read already exists. |
| Attachment status | `available_from_completed_run_artifacts` | Generate deterministically from run status, supplied refs, blockers, and deferred reasons. |
| Eligibility and blocker state | `available_from_completed_run_artifacts` | Generate deterministically from artifact status, custody flags, path safety, and explicit triage routes. |
| User receipt | `available_from_existing_offline_builder` | Render from attachment status; stay short and caveated. |
| Agent handoff packet | `available_from_existing_offline_builder` | Generate from status, refs, missingness, and route outputs; never authorize action. |
| Source refs | `available_from_completed_run_artifacts` | Preserve refs and source status, not raw/private contents. |

## Unsafe To Auto-Supply

The resolver must not auto-supply or export:

- raw conversation text;
- raw revised answer text;
- raw memo text;
- provider text;
- private ledgers;
- local absolute paths;
- local-private packet contents;
- outputs that require a new provider/model call inside runtime;
- provisional interpretation presented as proof;
- any artifact that creates scoring, approval, certification, or action
  authority.

These sources may be recorded as available, missing, withheld, or requiring a
future offline process. They must not become default agent handoff or user
receipt content.

## Options Considered

### A. Manual Ref Supply Only

Operators supply safe brief, enriched brief, and triage refs to the manual
bundle generator.

This is safest and already close to PR162, but it is too manual and not
product-useful for normal runtime attachment.

### B. Checked-In-Safe Case Registry

A registry maps known safe case/run ids to approved checked-in-safe brief,
enriched brief, and triage artifacts.

This is useful for demos and regression tests. It is not enough for arbitrary
live runs and can look more product-complete than it is.

### C. Archive Local Safe Resolver

After archive completion, a resolver reads only safe structured artifacts and
generates metadata/status artifacts. If no interpreted brief exists, it records
`deferred_missing_interpretation`.

This is honest and run-specific. It should be part of the next contract, but
by itself it still does not solve semantic interpretation.

### D. Offline Interpretation Queue

Runtime writes an attachment-needed packet. A separate offline, LLM-assisted,
Codex-assisted, or human-calibrated process later fills the interpreted brief
and triage read.

This matches the system doctrine, but it needs a queue/status contract before
implementation.

### E. Local Private Operator Mode

A local operator can generate richer brief inputs from private artifacts in a
non-checked-in mode.

This is valuable for internal validation, but unsafe as the default runtime or
agent handoff path.

### F. Direct Runtime Interpretation

The runtime calls a model/provider after archive to interpret the conversation
and produce the brief.

Reject for now. It would move semantic interpretation into runtime, add
provider/model calls, increase privacy and overtrust risk, and undermine the
current default-off conservative boundary.

## Decision Gate

Selected next step:

```text
build_safe_brief_supply_resolver_contract
```

Recommended next PR:

```text
PR170 Decision Work Brief Runtime Safe Supply Resolver Contract v0
```

The next PR should define the resolver contract, not the runtime behavior. It
should specify:

- allowed supply modes: explicit operator refs, checked-in-safe registry,
  archive-local metadata resolver, attachment-needed queue, and local-private
  operator mode;
- required statuses such as `supplied`, `missing`, `deferred_missing_brief`,
  `deferred_missing_interpretation`, `deferred_missing_triage_read`, `blocked`,
  and `unsafe_to_export`;
- how resolver output feeds the existing PR162 bundle path;
- how the runtime hook remains default-off and fail-closed;
- how no raw/private content, provider text, local absolute path, score,
  product-proof claim, human-validation claim, or action authorization enters
  the sidecar.

## PR170 Follow-up

PR170 implements that contract slice:

[runtime safe supply resolver contract](decision-work-brief-runtime-safe-supply-resolver-contract-v0.md)

It defines resolver modes, statuses, input types, unsafe exclusions, output
shape, custody flags, and non-claims. It recommends:

```text
PR171 Decision Work Brief Runtime Safe Supply Resolver v0
```

PR171 should implement deterministic resolver code without adding direct
runtime interpretation, provider/model calls, archive mutation, default-on
behavior, or runtime hook changes.

## PR171 Follow-up

PR171 implements the deterministic resolver and CLI:

[runtime safe supply resolver](decision-work-brief-runtime-safe-supply-resolver-v0.md)

It validates explicit safe refs, classifies resolved/deferred/blocked inputs,
redacts local paths in output, excludes unsafe inputs, and emits
`feeds_runtime_bundle` status. It recommends:

```text
PR172 Wire Safe Supply Resolver Into Runtime Bundle v0
```

The next slice should let the manual bundle consume resolver output. It should
not change the default-off runtime hook yet.

## Explicit Non-Claims

PR169 does not:

- run `$lolla`;
- invoke the Lolla skill;
- call provider or model APIs;
- create new Lolla runs;
- mutate historical archives;
- change prompts;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- make the runtime hook default-on;
- broaden runtime behavior;
- create a supply resolver implementation;
- create new interpretation reads;
- create new builder outputs;
- check in raw/private content;
- claim customer readiness;
- claim human validation;
- claim product proof;
- score answer quality;
- approve or certify advice;
- authorize agent or automatic action.
