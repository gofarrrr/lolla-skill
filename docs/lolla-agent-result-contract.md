# Lolla Agent Result Contract

Status: Implemented
Last updated: 2026-06-24

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
  "risk_mode": "standard",
  "caller_action": "use_revised_answer",
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

## Current Limitations

Risk mode is currently metadata only and defaults to `standard` unless a future
runtime path writes a mode field into `result.json`.

Control-plane wrappers such as `lolla_control_input.v1` and
`lolla_control_result.v1` are still proposed roadmap items.

`evaluation.json` is not implemented yet. The agent result does not claim that
the revised answer passed a deterministic or calibrated subjective eval. It
only summarizes existing run health, product artifacts, and safe-to-consume
status.
