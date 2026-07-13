# Extraction call custody contract v0

Status: implemented, provider-free verified, and live smoke passed
Date: 2026-07-10

## Purpose

Make every provider-bound extraction terminal reconstructable without asking
deterministic code to interpret conversation meaning. The contract separates
three facts that older artifacts conflated:

1. a provider call was attempted;
2. a corresponding call record was persisted;
3. the returned object became an admissible extraction.

None implies either of the others.

## Constitutional boundary

The LLM still decides whether the conversation is strategic and produces the
semantic fields. Existing required-field and exact-quote validation remains
unchanged. Deterministic code may persist, hash, count, time, and validate
custody; it must not synthesize a missing `decision_situation`, infer a missing
position, or treat an empty object as understanding.

## Runtime contract

`scripts/run_extract.py` writes the existing list-shaped sidecar at
`/tmp/lolla_<run_id>_extraction_calls.json`. The list shape is retained so
`engine/system_b/usage_summary.py` and the pipeline need no migration.

The sidecar is now written atomically immediately after the initial extraction
call returns or raises. If the one allowed quote-repair call runs, the sidecar
is atomically replaced with both records. This happens before any
`not_strategic`, missing-required-field, quote, or success terminal can return.

The extraction artifact also carries `provider_call_custody`:

| field | meaning |
| --- | --- |
| `call_attempted` | the provider boundary was entered |
| `sidecar_persisted` | a complete JSON sidecar replaced the target path |
| `call_record_persisted` | at least one call record exists in that sidecar |
| `recorded_call_count` | exact number of persisted records |
| `admissible_extraction` | semantic validation reached the existing success terminal |
| `terminal_status` | mechanical terminal label, not a quality judgment |
| `usage_evidence_state` | `recorded`, `missing_after_attempt`, or `not_applicable_no_call` |
| `failure_reason` | bounded persistence failure class without provider content |

Unexpected exceptions escaping the OpenAI-compatible boundary now append an
`unexpected_error` record before being re-raised. Raw provider content remains
in the local call sidecar. Review-safe smoke results contain only aggregated
usage and hashes.

## Honest unknowns

The extraction-admission sealer treats an attempted or unobservable call with
no record as unknown usage:

- `provider_call_count: null`;
- token fields: `null`;
- `estimated_total_cost_usd: null`;
- `cost_estimate_state: unknown_missing_call_record`.

It does not convert absent evidence into zero calls or zero cost. A no-call
terminal may report zero only when `call_attempted: false` was explicitly
preserved.

The requested model must exactly match the frozen contract. The served model
may be that exact ID or a provider-reported dated version alias recognized by
the boundary (`served_version_alias`). A materially different served model or
missing attribution still fails admission.

## Time boundary

Smoke contract v1 freezes both:

- `provider_timeout_seconds`, passed to the boundary client; and
- `wall_clock_timeout_seconds`, enforced around the extractor subprocess.

The outer ceiling must exceed the provider timeout and may not exceed 300
seconds. A wall-clock timeout terminates that one subprocess, seals a failed
result with exit code 124 and unknown usage when no record survived, and never
retries the experiment.

Future smoke contracts hash-lock the extractor, audit mode, quote matcher,
boundary provider, capture adequacy, run-state guard, usage aggregator, pricing
table, and smoke runner. Pricing is a transitive admission dependency because
the cost ceiling is a frozen gate, not commentary.

## Evidence and non-claims

Provider-free tests cover success, non-strategic decline, empty/schema-invalid
output, provider exception, quote repair, missing usage, contract timeout
validation, and outer-timeout sealing.

The first contract-v1 live smoke then passed all gates on the heavily reused
six-turn Case 01 fixture: one recorded call, no repair, 6/6 turns, three exact
quotes, complete usage, 2,087 tokens, `$0.001190` estimated cost, and 2.618
seconds wall time. The requested model was exact and the served model was its
accepted dated version alias. No graph, embedding, or downstream call ran.

This repair and smoke do not prove extraction accuracy, graph relevance,
reconsideration value, or receipt usefulness. They do not retroactively pass
the failed Case 12 smoke and do not authorize a paired holdout. Their only
promotion consequence is permission to plan and freeze one untouched Stage A
extraction-plus-pipeline contract.

## Restart point

Read, in order:

1. this contract;
2. `research/extraction-admission-smoke-case01-v1-2026-07-10/review.md`;
3. `research/extraction-call-custody-repair-2026-07-10/cycle-status.json`;
4. `research/extraction-admission-smoke-2026-07-10/review.md`;
5. `docs/evals/reasoning-portfolio-two-stage-holdout-protocol-v0.md`.

The next goal is one untouched Stage A contract. No call may run until that
contract freezes the case, extraction and pipeline dependencies, provider and
model, direct OpenAI-only embedding policy, calls, time, cost, and stop rules.
