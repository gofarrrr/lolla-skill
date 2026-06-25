# Lolla Agent Result Contract

Status: Implemented
Last updated: 2026-06-25

## Purpose

`agent_result.json` is the first machine-readable handoff for agents that call
Lolla.

It is intentionally compact. It tells a caller whether the archived run is fit
to use automatically, what changed in the advice when the run artifacts make
that visible, what questions still need human judgment, and where to inspect
the full local archive.

It is not a safety guarantee, a policy decision, a sandbox verdict, a proxy
decision, a credential decision, or a generic LLM-judge score.

## Where It Is Written

Each archive pass writes:

- `{archive_root}/{case_id}/{run_id}/agent_result.json`
- `/tmp/lolla_<run_id>_agent_result.json`

The archived `reasoning_trace.json` indexes `agent_result.json` as an
`agent_facing_result` artifact with path, hash, size, and content type.

When an external caller supplies `control_input.json`, the archive also
preserves that file, adds a compact `control_context` summary to
`agent_result.json`, generates an optional `control_result.json` wrapper, and
indexes the control artifacts in `reasoning_trace.json`.

## Risk Mode Metadata

The runtime reads `LOLLA_AUDIT_MODE`, defaults missing or empty values to
`standard`, and accepts only:

- `quick`
- `standard`
- `deep`
- `high_stakes`
- `stability`

The normalized value is persisted as `risk_mode` in `result.json`,
`agent_result.json`, `reasoning_trace.json`, and archive metadata. Invalid
explicit values fail before model calls. Current modes are metadata only: they
do not change prompts, cost, Step 7 behavior, replay/comparison behavior, or
high-stakes domain policy yet.

## Schema

Schema version:

```json
"lolla_agent_result.v1"
```

Core fields:

```json
{
  "schema_version": "lolla_agent_result.v1",
  "run_id": "20260624T120000Z_example",
  "case_id": "founder-pivot",
  "status": "ok",
  "status_reason": "required product artifacts are present",
  "run_health_overall": "healthy",
  "product_output_health": "clean",
  "live_output_health": "not_checked",
  "provider_boundary_health": {
    "schema_version": "lolla.provider_boundary_health.v0.1",
    "status": "clean",
    "reason": "no_provider_boundary_issue",
    "issue_code": "",
    "affected_call_count": 0,
    "affected_models": [],
    "affected_stages": [],
    "reasoning_disabled": null,
    "reasoning_details_returned": false,
    "product_output_health": "clean",
    "product_contamination_detected": false,
    "live_output_health": "not_checked",
    "live_output_contamination_detected": false,
    "archive_custody_contamination_status": "not_applicable",
    "raw_reasoning_details_persisted": false,
    "raw_reasoning_details_persistence_basis": "not_applicable"
  },
  "capture_adequacy": {
    "schema_version": "lolla.capture_adequacy.v0",
    "status": "good",
    "capture_strategy": "full",
    "omitted_turn_count": 0,
    "risk_flags": []
  },
  "risk_mode": "standard",
  "caller_action": "use_revised_answer",
  "control_context": {
    "schema_version": "lolla_control_input.v1",
    "expected_schema_version": "lolla_control_input.v1",
    "status": "valid",
    "control_mode": "pre_action_reasoning_gate",
    "lolla_enforces_actions": false,
    "external_trace_id": "trace_123",
    "external_span_ids": ["span_a", "span_b"],
    "agent_run_id": "agent_run_789",
    "agent_framework": "openai_agents_sdk",
    "proposed_action": {
      "tool_name": "send_email",
      "risk_class": "external_side_effect",
      "has_arguments": true,
      "argument_keys": ["subject", "to"]
    },
    "tool_call_ids": ["tool_call_1"],
    "approval_id": "approval_001",
    "policy_engine": "crabtrap",
    "policy_decision": "needs_review",
    "sandbox_id": "sandbox_abc",
    "credential_scope": "gmail.send"
  },
  "main_counter_pressure": "The answer treated customer interest as evidence before naming a reversal gate.",
  "position_changed": true,
  "changed_advice_summary": [
    "Add a customer evidence gate before pivoting."
  ],
  "take_backs": [
    "Take back the clean recommendation to pivot now."
  ],
  "human_questions": [
    "What evidence would make the pivot unacceptable?"
  ],
  "do_not_act_before": [
    "Run the customer evidence gate before pivoting."
  ],
  "artifact_status": {
    "conversation": "present",
    "extraction": "present",
    "result": "present",
    "revised_answer": "present",
    "memo": "present",
    "reasoning_trace": "present"
  },
  "artifact_paths": {
    "archive": "/Users/example/.local/share/lolla/runs/founder-pivot/20260624T120000Z_example",
    "agent_result": "/Users/example/.local/share/lolla/runs/founder-pivot/20260624T120000Z_example/agent_result.json",
    "memo": "/Users/example/.local/share/lolla/runs/founder-pivot/20260624T120000Z_example/memo.md",
    "reasoning_trace": "/Users/example/.local/share/lolla/runs/founder-pivot/20260624T120000Z_example/reasoning_trace.json"
  },
  "usage": {
    "estimated_total_cost_usd": 0.42,
    "cost_estimate_state": "complete",
    "pricing_table_version": "2026-06-24"
  },
  "notes": [
    "Use the revised answer, memo, and artifact pointers together; this contract is not a safety or fact-checking guarantee."
  ]
}
```

`control_context` is omitted for ordinary `$lolla` runs. When present, it is a
compact summary only: proposed-action argument values remain in the archived
`control_input.json` artifact and are not copied into `agent_result.json`.

## Status Values

`status` is the compact contract state:

- `ok`: required product artifacts are present and run health is usable.
- `partial`: runtime health is partial; the caller should not treat the run as
  automatic approval.
- `degraded`: runtime health or product/live output health indicates a material
  problem.
- `incomplete`: required artifacts such as `result.json`, `revised.txt`, or
  `memo.md` are missing, or capture was critical.

`run_health_overall` preserves the runtime value from `result.json`, usually
`healthy`, `partial`, `degraded`, or `critical`.

`provider_boundary_health` is a compact structured summary of provider-boundary
issues. Today it distinguishes a vendor returning reasoning details despite
disabled reasoning from product/live-output contamination. It intentionally
records presence/count metadata, model/stage labels, and contamination status;
it does not expose raw provider reasoning details.

`capture_adequacy` is a compact structured summary of the capture shape. It
records whether capture was full, warning-level, or critical, including omitted
turn counts and risk flags. It does not include raw transcript text and does
not semantically reconstruct omitted turns.

## Caller Action

`caller_action` is a closed enum:

- `use_revised_answer`
- `ask_user_first`
- `rerun_deeper`
- `do_not_use_run_degraded`
- `unsupported_high_stakes_domain`

The first implementation is conservative:

- Clean completed standard runs can return `use_revised_answer`.
- Partial, degraded, incomplete, or product/live-output-unsafe runs return
  `do_not_use_run_degraded`.
- A contained provider-boundary warning (`provider_boundary_health.status:
  "warning_contained"`) is still conservative in this contract. It receives a
  more specific `status_reason` and note, but it does not become automatic
  approval.
- If `risk_mode` is `high_stakes` on an otherwise clean run, the first contract
  returns `ask_user_first`. This is a conservative caller hint, not a claim
  that high-stakes domain policy is implemented.

The caller remains responsible for enforcement. A policy engine, approval
system, sandbox, proxy, identity broker, or human reviewer can consume this
field, but Lolla does not replace those systems.

## What The Contract Does Not Include

The contract deliberately avoids ordinary exposure of:

- private chunk IDs,
- V60 internals,
- lane labels,
- hidden ledger details,
- model-call raw content,
- full conversation text.

Those details remain inspectable in local artifacts where appropriate. The
agent result is a handoff, not the full instrument panel.

## Control-Plane Wrapper

`lolla_control_input.v1` and `lolla_control_result.v1` are now additive archive
contracts.

To supply external metadata, write `/tmp/lolla_<run_id>_control_input.json`
before archive. The archive copies it to `control_input.json`, summarizes it in
`agent_result.json`, and writes `control_result.json` plus
`/tmp/lolla_<run_id>_control_result.json`.

`control_result.json` wraps the existing agent result. It maps `caller_action`
to approval-system language, carries `do_not_act_before`, includes human
approval context, and points back to artifacts. It does not approve actions,
replace policy engines, replace sandboxes, replace identity scopes, or make
network/tool decisions.

Current caller-action mappings:

| `caller_action` | Control-plane outcome |
|---|---|
| `use_revised_answer` | `proceed_with_external_policy` |
| `ask_user_first` | `require_human_approval` |
| `rerun_deeper` | `rerun_deeper` |
| `do_not_use_run_degraded` | `block_reasoning_incomplete` |
| `unsupported_high_stakes_domain` | `block_unsupported_stakes` |

## Current Limitations

Risk mode is currently metadata only and defaults to `standard` unless a future
runtime path writes a mode field into `result.json`.

The control-plane wrapper preserves metadata and maps Lolla's result for other
systems. It does not auto-trigger Lolla, enforce approvals, call tools, replay
external traces, or turn Lolla into a proxy/firewall/sandbox/identity broker.

`evaluation.json` now exists as a deterministic run-readiness receipt for
archived runs. It checks artifact presence, schemas, custody links, hygiene
states, and caller-policy consistency. It does not claim that the revised
answer passed a subjective quality, helpfulness, or correctness judge.
