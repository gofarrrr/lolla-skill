# Decision Work Brief Runtime Safe Supply Resolver Contract v0

Status: PR170 resolver contract only

Date: 2026-07-02

Contract JSON:
[runtime safe supply resolver contract](decision-work-brief-runtime-safe-supply-resolver-contract-v0.json)

Source plan:
[runtime safe brief supply plan](decision-work-brief-runtime-safe-brief-supply-plan-v0.md)

## Purpose

PR170 defines the contract for a future safe supply resolver in the
runtime-attached Decision Work Brief path.

The resolver should answer a narrow question:

```text
Do we have safe run-specific Decision Work Brief inputs, where are they,
can they feed the runtime bundle, or should this attachment defer, block,
or queue for offline interpretation?
```

It must not answer whether the advice was good, whether Lolla improved the
decision, what the conversation really meant, or whether an agent may act.

This PR does not implement the resolver. It does not change the runtime hook,
make the hook default-on, run Lolla, call provider or model APIs, create new
runs, mutate archives, change prompts, or touch `SKILL.md` or
`scripts/skill/*`.

## What The Resolver Receives

The future resolver receives only refs, status, contracts, and explicit
operator or registry inputs:

- completed run directory ref;
- runtime attachment contract ref;
- sidecar contract ref;
- optional eligibility/blocker result ref;
- optional manual operator refs;
- optional checked-in-safe case-registry refs;
- optional offline interpretation queue refs;
- optional local-private availability metadata;
- target resolver mode.

Local-private availability can be recorded as status, but private contents
must not be exported by default.

## Resolver Modes

The contract defines these modes:

- `disabled`
- `manual_ref_supply_only`
- `checked_in_safe_case_registry`
- `archive_local_safe_resolver`
- `offline_interpretation_queue`
- `local_private_operator_mode`
- `future_direct_runtime_interpretation_not_allowed`

The final mode is deliberately named as a blocker. Runtime-side provider/model
interpretation is not allowed by this contract.

## Resolver Statuses

The contract defines statuses that downstream bundle code can preserve without
pretending missing interpretation is a product result:

- `not_requested`
- `no_safe_inputs`
- `resolved`
- `partially_resolved`
- `deferred_missing_brief`
- `deferred_missing_enriched_brief`
- `deferred_missing_interpretation_read`
- `deferred_missing_triage_read`
- `blocked_privacy_risk`
- `blocked_unsafe_path`
- `blocked_untrusted_source`
- `blocked_schema_invalid`
- `blocked_direct_runtime_interpretation`
- `queued_for_offline_interpretation`
- `local_private_operator_required`

These statuses are routing and custody facts. They are not quality labels.

## Inputs That Can Feed The Runtime Bundle

The resolver contract covers the sidecar inputs that the current PR162 bundle
shape can use:

- `completed_run_dir_ref`
- `decision_work_brief_json_ref`
- `rendered_brief_markdown_ref`
- `enriched_brief_markdown_ref`
- `interpretation_read_json_ref`
- `automatic_triage_packet_json_ref`
- `automatic_triage_read_json_ref`
- `source_refs`
- `eligibility_result_ref`
- `attachment_status_ref`
- `user_receipt_ref`
- `agent_handoff_ref`

Each input declares whether it is required for the user receipt, full brief,
agent handoff, or triage; which resolver modes may supply it; how absence
should be recorded; and whether it depends on LLM interpretation or local
private context.

The key boundary remains:

- the resolver may preserve refs, status, missingness, path safety, custody
  flags, and non-claims;
- the resolver must not create new semantic interpretation from messy
  conversation content.

## Inputs That Must Never Be Auto-Supplied

The resolver must exclude:

- raw conversation text;
- raw revised answer text;
- raw memo text;
- provider text;
- private ledgers;
- local absolute paths;
- secrets;
- hidden chain-of-thought style material;
- runtime model-generated interpretation;
- action authorization;
- score or approval labels.

Those materials may be described as unavailable, withheld, blocked, or needing
offline/local-private handling. They must not be copied into user receipts,
agent handoff packets, or default sidecars.

## How This Feeds The Existing Runtime Path

PR162 can already package explicit safe refs into a `decision_work/` sidecar.
PR166 can already call that path after archive completion when
`LOLLA_DECISION_WORK_BRIEF_AFTER_ARCHIVE` is enabled. Without safe supplied
inputs, it correctly records a deferred state.

PR170 defines the contract that a future resolver must satisfy before it can
feed PR162:

- no privacy/path/schema blocker;
- all unsafe inputs excluded;
- source refs relative or redacted;
- conservative custody flags;
- no runtime model-generated interpretation;
- explicit `reason_if_not_feedable` when the resolver cannot safely feed the
  bundle.

## Decision Gate

Recommended next PR:

```text
PR171 Decision Work Brief Runtime Safe Supply Resolver v0
```

PR171 should implement deterministic resolver code that reads safe refs and
status, accepts manual refs or a checked-in-safe registry, emits resolver
output, and does not call models, interpret messy content, mutate archives, or
change the runtime hook behavior.

## PR171 Follow-up

PR171 implements the resolver described here:

[runtime safe supply resolver](decision-work-brief-runtime-safe-supply-resolver-v0.md)

It emits `lolla.decision_work_brief_runtime_safe_supply_resolver.v0` output
with input classification, resolved/deferred/blocked inputs, unsafe exclusions,
queue handoff status, manual operator requirements, custody flags, non-claims,
and bundle feedability. It recommends:

```text
PR172 Wire Safe Supply Resolver Into Runtime Bundle v0
```

PR172 should connect resolver-approved refs to the manual bundle path without
changing the default-off runtime hook.

## Explicit Non-Claims

PR170 does not:

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
- implement a supply resolver;
- add direct runtime interpretation;
- check in raw/private content;
- claim customer readiness;
- claim human validation;
- claim product proof;
- score answer quality;
- approve or certify advice;
- authorize agent or automatic action;
- prove that Lolla improved decisions.
