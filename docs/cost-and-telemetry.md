# Cost & Telemetry — How Lolla Measures What a Run Costs

This is the single canonical reference for "what API calls did this run make and what did they cost." If anything in the codebase contradicts this doc, fix the code, not the doc.

## TL;DR

Every Lolla run produces a `usage_summary` block in the result JSON at `/tmp/lolla_<run_id>_result.json`. It looks like:

```json
{
  "usage_summary": {
    "run_id": "20260428T064421Z",
    "pricing_table_version": "2026-05-25",
    "estimated_total_cost_usd": 2.4234,
    "cost_estimate_state": "complete",
    "cost_estimate_coverage": {
      "calls_with_known_price": 42,
      "calls_with_unknown_price": 0,
      "unknown_price_models": []
    },
    "vendors": {
      "openrouter":         { ... },
      "openai_embeddings":  { ... },
      "anthropic_subagents": { ... }
    },
    "notes": [...]
  }
}
```

Three places to read it:

| Place | URL / path |
|---|---|
| Visual page | `http://localhost:8080/usage` (after launching the Observatory) |
| API | `GET http://localhost:8080/api/case/<case_id>/usage` |
| Raw | `cat /tmp/lolla_<run_id>_result.json \| jq .usage_summary` |

The live receipt prints a one-line cost estimate. If `cost_estimate_state` is not `complete`, treat the amount as a lower bound and inspect `usage_summary.cost_estimate_coverage`.

The `/usage` page surfaces the following blocks (server-side rendered, no SPA rebuild required):

- **By vendor** — OpenRouter / OpenAI / Anthropic totals, calls, tokens, cache-hit rate, cost.
- **OpenRouter — by stage** — per-stage call count, prompt / cached / completion tokens, and **cache-hit % per stage**. This per-stage cache rate is the highest-value diagnostic on the page: stages with identical system prompts across calls (for example, `bullshit_index`) can reuse more prefix material; stages with per-call-varying system prompts (most pipeline lanes) are the candidates for the prompt-restructure follow-up.
- **OpenAI — by model** — embedding model vs. expansion model split.
- **Anthropic Step-7 sub-agents — by lane, optional only** — which Step-7 lane (1 = Delta, 2 = Companion, 3 = Frame, 4 = Coverage) was spawned when deeper-review mode was explicitly enabled, its model, status, total tokens, duration, and estimated cost. Default-off runs show no Anthropic sub-agent calls. Lanes that were `skipped_empty` or `skipped_error` do not appear because they were never spawned (per the SKILL Step 8b filter — see `merge_subagent_calls` and the input-record validation).
- **Prompt versions** — 12-char hash of the system prompt used at each pipeline stage. Useful for reproducibility ("which prompt revision produced this finding?") and for diffing two runs of the same case.
- **V60 private enrichment** — selected chunks, skipped candidates, not-presented model IDs, embedding mode, and Step-6 consideration-ledger uptake live under `/audit/v60`. This is reasoning-transport telemetry, not a separate vendor-cost block.

## What gets measured

Lolla can record calls to three vendor groups. Each active group is recorded into `usage_summary.vendors.<vendor>`; default runs usually have OpenRouter calls, optional OpenAI embedding calls, and no Anthropic sub-agent calls.

### OpenRouter (chat completions)

Every OpenRouter chat call from anywhere in the pipeline. Recorded automatically by `OpenAICompatibleBoundaryClient` — every `run_json` / `run_json_with_metadata` call appends to `client.call_log` with the `stage=` label the caller passed in.

Stages currently recorded:

| Stage | Where it fires | Calls per run (typical) |
|---|---|---|
| `extraction` | `scripts/run_extract.py` | 1 |
| `extraction_retry` | retry path on quote-fabrication | 0–1 |
| `pass1_cluster_<cluster_id>` | `engine/system_b/pass1_runner.py` | 6 (one per family cluster: authority, closure, incentive, availability, self_regard, residual) |
| `pass2` | `engine/system_b/pass2_runner.py`, one per triggered tendency | 0–8 |
| `frame_extraction` | frame pressure lane, element detection | 1 |
| `frame_reframing` | frame pressure lane, alternative-question generation | 1 |
| `companion_fingerprint` | companion lane, model activation detection | 1 |
| `companion_verification` | companion lane, evidence validation | 0–1 |
| `structural_coverage_classification` | coverage lane, problem typing | 1 |
| `structural_coverage_detection` | coverage lane, dimension scan | 1 |
| `bullshit_index` | `engine/system_b/bullshit_index.py`, one per evaluation passage of the audited answer | 0–12; adjacent source passages are merged when the uncapped split exceeds 12 |
| `revision` | optional post-pipeline revision (skipped under `--skip-revision`) | 0–1 |

The Bullshit Index used to grow one call per split passage and could exceed 30
or 50 calls on a long multi-turn answer. It now has a hard 12-call ceiling.
When the uncapped split is larger, adjacent passages are merged
deterministically. No passage is selected away, but localization becomes
coarser. Its payload reports `source_passage_count`,
`evaluation_passage_count`, `max_evaluation_passages`, and
`passage_compaction_applied` so the trade-off is visible.

Per-call records carry: `stage`, `tendency_id`, `provider_name`,
`served_provider_name`, `model`, `status`, `finish_reason`,
`raw_message_content`, `temperature`, `prompt_tokens`, `completion_tokens`,
`total_tokens`, `cached_tokens`, `cache_write_tokens`, and
`reasoning_tokens`. Safe failure diagnostics additionally preserve
`provider_error_source`, `provider_error_type`, `provider_error_code`,
`provider_error_provider_code`, `provider_error_message_sha256`, and
`retry_after_seconds`. The raw provider error message is not duplicated into
those diagnostic fields. Status is `ok` for successful calls, an HTTP error
code, `timeout`, `missing_api_key`, `response_json_error`, or
`provider_finish_error` for failures. `raw_message_content` is the full model
message content per call—persisted so any LLM decision is investigable from
`result.json` alone without re-running the pipeline. Adds roughly 10–50 KB to a
typical `result.json`, scaling with call count and per-call output size.

Extraction call custody is transactional. `run_extract.py` atomically writes
the run-scoped extraction sidecar immediately after the initial provider call,
before strategic/schema validation can return, and replaces it with both
records if the one quote-repair call runs. The extraction artifact separately
records `provider_call_custody`: call attempted, sidecar persisted, call record
persisted, recorded count, terminal status, and admissible extraction. An
unexpected boundary exception is recorded as `unexpected_error` before it is
re-raised.

If a call was attempted but no record survived, usage is unknown—not zero. The
admission sealer emits null calls/tokens/cost and
`cost_estimate_state: unknown_missing_call_record`. Numeric zero is valid only
when a no-call terminal was explicitly recorded. See
`docs/evals/extraction-call-custody-contract-v0.md`.

### OpenAI (embeddings + query expansion)

Every embedding or chat call inside `engine/system_b/embedding_retriever.py`. Recorded via a `ContextVar`-scoped capture (`capture_usage()` opened at the top of the pipeline run, closed before `usage_summary` is built). Per-run isolation is structural — calls outside the scope are silently ignored, not leaked into another run's totals.

These requests use the direct OpenAI endpoints and `OPENAI_API_KEY`; the
OpenRouter key is not a fallback credential for embeddings or expansion. In
automatic mode, an empty OpenAI key disables this layer and the run degrades to
the non-embedding retrieval path.

Three call types:

| Endpoint | Model | Use |
|---|---|---|
| `embeddings` | `text-embedding-3-large` | Query embedding for model retrieval |
| `embeddings` | `text-embedding-3-large` | Batch embedding of expanded query variants |
| `chat` | `gpt-4o-mini` | Query expansion (2 alternative phrasings per query) |

Total OpenAI cost per run is typically well under $0.01.

V60 enrichment can reuse the same `embedding_retriever.rank_models_expanded(...)` path for low-trust model recall when embeddings are enabled. Those OpenAI calls are captured by the same `capture_usage()` scope and therefore appear in `usage_summary.vendors.openai_embeddings`; V60 itself does not introduce a new vendor or manual cost hook.

### Anthropic (optional Step 7 sub-agents)

The 4 pressure-check sub-agents are rested by default. If the user/operator explicitly enables deeper-review mode, they fire from inside the SKILL orchestration via Claude Code's Agent tool, NOT through `OpenAICompatibleBoundaryClient`. Their cost can be the largest single line item on optional runs because they use whatever Claude model the orchestrator runs on (typically Opus).

**Resolution gap:** Claude Code's task notification surfaces only `total_tokens`, not a prompt/completion split. The cost estimator treats the entire total as input tokens at the model's input price — a conservative over-estimate. The real cost is somewhere lower, depending on how much was completion vs. prompt. The result JSON marks this with `vendors.anthropic_subagents.estimation_method = "conservative_input_only_no_split_available"`.

Default-off runs do not write sub-agent usage records. Optional Step 8b (`SKILL.md`) records the sub-agent records into the `usage_summary` after both Step 6 and Step 7 are complete.

## Where the numbers come from (data flow)

```
┌────────────────┐     stage="extraction"          ┌────────────────────────────┐
│ run_extract.py │────────────────────────────────▶│ /tmp/lolla_<run_id>_       │
│                │   atomically merges call_log    │   extraction_calls.json    │
└────────────────┘   after each provider boundary  └────────────────────────────┘
                                                                │
                                                                ▼
┌─────────────────────┐                              load_extraction_sidecar()
│  pipeline lanes      │ stage="pass1_cluster_*"           │
│  (pass1, pass2,      │ stage="pass2"               ┌─────▼──────────────┐
│   frame, coverage,   │ stage="frame_*"             │ build_usage_       │
│   companion)         │ stage="companion_*"         │ summary()          │
└─────────────────────┘─▶ result.audit.boundary_calls─▶ engine/system_b/  │
                                                     │ usage_summary.py    │
┌─────────────────────┐ stage="bullshit_index"       │                     │
│ bullshit_index.py   │─────────────────────────────▶│                     │
│ (separate client)   │ → bi_call_log                │                     │
└─────────────────────┘                              │                     │
                                                     │                     │
┌─────────────────────┐ stage="revision"             │                     │
│ revision (separate  │─────────────────────────────▶│                     │
│ client)             │ → revision_call_log          │                     │
└─────────────────────┘                              │                     │
                                                     │                     │
┌─────────────────────┐ ContextVar scope             │                     │
│ embedding_retriever │─────────────────────────────▶│                     │
│ (capture_usage)     │ → embedding_usage_records    │                     │
└─────────────────────┘                              └────┬────────────────┘
                                                          │
                                                          ▼
                                                 usage_summary block in
                                                 /tmp/lolla_<run_id>_result.json

[ optional only, after Step 7 sub-agents complete, SKILL Step 8b: ]

┌─────────────────────┐                           ┌─────────────────────────┐
│ task notifications  │ total_tokens per agent    │ merge_subagent_calls()  │
│ from Agent tool     │──────────────────────────▶│ → updates the           │
│ (Claude Code)       │                           │   anthropic_subagents   │
└─────────────────────┘                           │   block + grand total   │
                                                   └─────────────────────────┘
```

Five input streams → one canonical `usage_summary` block. Per-run isolation is enforced by:

1. Each script invocation is its own Python process — boundary clients are instantiated fresh.
2. The embedding `capture_usage()` context manager uses `ContextVar`, not module globals.
3. The extraction sidecar path is namespaced by `$LOLLA_RUN_ID`; each process
   append-preserves earlier records instead of replacing them.
4. Optional sub-agent records are passed in by the SKILL after Step 7, not pulled from any shared state. Default-off runs pass no sub-agent records.

V60 and the pre-Step-6 private table add non-cost telemetry streams inside the same `result.json`:

| Block | Written by | What it answers |
|---|---|---|
| `pre_step6_private_table` | `scripts/run_pipeline.py` | Which compact private table was placed in front of Step 6, whether cached portfolio cards were appended, which sidecars were written, and the zero-call/no-live-generation envelope |
| `pre_step6_private_table_ledger` | `SKILL.md` Step 6b | Which private-table sections or cached cards Step 6 used, rejected, deferred, kept private as guardrails, or treated as confirming support |
| `v60_enrichment` | `scripts/run_pipeline.py` | Which lane/embedding candidates were considered, which V60 cards/chunks were selected, local chunk selection score/reason/effect type, record-order fallback counts, which candidates were skipped, which model IDs were left outside the hot context, and whether the explicit `affordances_v60.json` artifact loaded cleanly |
| `v60_consideration_ledger` | `SKILL.md` Step 6b | For every selected V60 chunk shell from the deterministic skeleton: did Claude/Codex use it, reject it, defer it, or not consider it; through what route; and what visible/private effect, blocker, or guardrail it had |
| `v60_consideration_validation` | `engine/system_b/v60_enrichment.py` | Whether the ledger accounts for every selected chunk exactly once, preserves card/model/chunk identity, respects route/disposition compatibility, and fills required visible/private/absence-blocker fields |
| `run_health.v60_*` | `scripts/run_pipeline.py` + `SKILL.md` Step 6b | Runtime status/counts before Step 6, then ledger status, transaction count, disposition counts, used chunk count, and presented-but-not-used count after Step 6b |
| `product_output_hygiene` + `run_health.product_output_*` | `scripts/archive_run.py` + `engine/system_b/output_hygiene.py` | Archive-time scan of revised text, memo markdown, and memo-note fields for internal machinery leaks; unsafe product output degrades the run |
| `live_output_hygiene` + `run_health.live_output_*` | `scripts/finalize_live_output_hygiene.py` + `scripts/archive_run.py` + `engine/system_b/output_hygiene.py` | Scan of `/tmp/lolla_<run_id>_live_transcript.txt`, the agent prose/status transcript artifact; unsafe live output degrades the run, missing capture is recorded as `missing`, and a clean manual artifact is `not_checked` until a complete trusted transcript is finalized with `--trusted-transcript` |
| `run_health.provider_call_*` + `provider_call_terminal_loss` | `scripts/run_pipeline.py` | Attempted provider-backed calls with a non-`ok` terminal status. Failed-call count, stage, tendency ID, status, safe provider/model identity, and safe error type/code make semantic missingness partial even when other lanes complete. This is separate from provider-boundary privacy health. |

The operational kill switch is `LOLLA_V60_ENRICHMENT=off` or `--v60-enrichment off`. Disabled runs still write a small `v60_enrichment.status = "disabled"` block so the absence is intentional and observable.

The pre-Step-6 private table adds no OpenRouter or Anthropic calls. `--pre-step6-portfolio step6_private` renders from already-built lane/V60 payloads and only reads cached card decks when present. A cache miss does not generate cards.

The `/audit/v60` Observatory panel is the process-comparison surface: it renders the candidate pool, lane source counts, embedding hits as retrieval/rank signals, selected cards/chunks, local relevance/fallback methods, skipped or not-presented candidates, effect-type labels, and the Step-6 consideration ledger. Use it to compare how the system reasoned, not only whether the final answer changed. For archived run-to-run comparison, use `scripts/compare_archived_runs.py`; it reports trace/product eligibility before answer and memo diffs.

## Pricing

Rates are looked up in `engine/system_b/pricing.py`. That file is also covered
by historical evaluation hashes, so current maintenance must not casually
rewrite it. The frozen provider-boundary contract retains its 2026-07-13
active-route freshness date. New `usage_summary` receipts qualify it with
`pricing_verification_scope = active_openrouter_route_only` and separately
report `pricing_table_wide_last_verified = 2026-05-25`. A narrow check of one
active route is no longer presented as verification of every vendor and model.

Known current limitation: the optional Step 7 Anthropic entries are historical
calibration rates, not a current model-selection or budgeting contract. The
Opus 4.7 row was found stale against official Anthropic pricing on 2026-07-22.
Step 7 is default-off; do not budget from that row. Before any future optional
run, verify the exact reported model and current rate in
[Anthropic's official pricing documentation](https://platform.claude.com/docs/en/about-claude/pricing).
Correcting the table requires a prospective version plus receipt migration and
tests, not an edit that rewrites frozen evidence.

For a prospective price-table revision:

1. freeze the current table and the receipts that depend on it;
2. add a new versioned table and update the live lookup prospectively;
3. verify every retained row against the provider's official price source;
4. record per-vendor/per-model verification scope and date;
5. test unknown-model and partial-estimate behavior before switching receipts.

If the model used on a run is not in the price table, the call counts and tokens still record but `estimated_cost_usd` for that vendor only includes the priced calls. `cost_estimate_state` becomes `partial` or `unknown`, and `cost_estimate_coverage.calls_with_unknown_price` is non-zero. Treat `estimated_total_cost_usd` as a lower bound. A known but stale row is also unsuitable for budgeting even though the current schema cannot yet distinguish it from a current row.

OpenRouter call telemetry records both `requested_model` and `served_model` when the provider returns a model ID. The compatibility `model` field is the served/billing model when available. Provider version aliases such as `deepseek/deepseek-v4-flash` being served as `deepseek/deepseek-v4-flash-20260423` are recorded as `served_version_alias`. If OpenRouter routes a request to a materially different model, `vendors.openrouter.model_attribution.mismatch_count` becomes non-zero and the mismatch is listed in `vendors.openrouter.model_attribution.mismatches`.

Mismatch detection is **record-and-continue**, not record-and-halt. The run continues, costs are estimated against the served/billing model, and operators review `usage_summary` to decide whether model-specific evidence from that run is attribution-uncertain. A future strict mode may promote mismatches to a hard stop for calibration or regulated environments.

## Adding a new vendor or stage

**New stage on an existing vendor (e.g., adding a new pipeline lane):**

1. Pass `stage="my_new_stage"` to `client.run_json(...)` or `client.run_json_with_metadata(...)`.
2. That's it. The auto-recording inside the boundary client appends to `client.call_log` with the new stage label, and `usage_summary` picks it up automatically. The Observatory's `/usage` page shows it under the OpenRouter "by stage" table.

**New vendor (e.g., a different LLM provider):**

1. Add a price entry in `pricing.py`.
2. Either: (a) implement a new boundary client class that mirrors `OpenAICompatibleBoundaryClient`'s `call_log` / `run_json_with_metadata(..., stage=...)` shape; OR (b) wrap the calls in a ContextVar capture similar to `embedding_retriever.capture_usage()`.
3. In `usage_summary.py`, add a `_build_<vendor>_block` and wire it into `build_usage_summary`.
4. In `observatory/serve_result.py`, add a row in `_render_usage_html`.

The structural rule: **every API call is recorded by default**. If you add a new call site that needs a manual recording hook, you've taken a step backward from the design — refactor so recording happens automatically.

## Caching — how it works on Grok via OpenRouter

xAI Grok caches automatically — no `cache_control` configuration needed. The cache works **from the start of the messages array**: when a request arrives, xAI checks how many messages at the beginning match a previous request *exactly*, and the matching portion becomes the cached prefix. Both system and user messages participate in prefix matching.

Two server-side caveats from the xAI docs ([How Prompt Caching Works](https://docs.x.ai/developers/advanced-api-usage/prompt-caching/how-it-works)):

- Cache entries can be evicted under memory pressure — there is no published TTL
- Requests may be routed to different backend servers, and each server has its own cache

To minimize the routing problem, xAI provides the `x-grok-conv-id` header — a constant uuid that pins requests to the same backend.

### What Lolla does about it

**(implemented)** The boundary client sets `x-grok-conv-id` on every Grok request, derived deterministically from `$LOLLA_RUN_ID` via `uuid5`. This means every BoundaryClient instance spawned during the same run (pipeline + BI + revision + extraction) emits the same conv_id and lands on the same xAI backend, maximizing cross-call cache reuse within a run. Different runs get different conv_ids (per-run isolation).

If `$LOLLA_RUN_ID` is unset (e.g., ad-hoc scripts or tests), the client falls back to a fresh `uuid4` per process. The header is only added for `x-ai/grok*` models.

**(not implemented — future work)** Lolla currently puts the **per-stage instructions** in the system message and the **conversation transcript + extraction context** (the big stable block — same across ~16 pipeline calls) in the user message. Since the system message diverges first, the prefix breaks before reaching the conversation, and only the small shared preamble at the top of the system prompts caches.

The fix is to swap message slots — put the stable conversation+extraction in the system message and the per-stage instructions in the user message. Estimated impact: cache hit rate from ~20% (current, with conv_id stickiness) to ~60-75%, total run cost down ~30-40%.

Why it isn't done yet: reordering prompt slots is content-equivalent on paper but can shift model behavior in practice. Some models weight system vs. user content differently. This change requires running the existing test cases (in `tests/`) before/after to confirm audit findings don't drift. Telemetry first, optimization second.

The cache hit rate is surfaced as `vendors.openrouter.cache_hit_rate` in `usage_summary` and on the Observatory `/usage` page, so the savings (or lack thereof) from any change to the prompt structure will be visible directly.

## Verifying the telemetry is honest

Two checks:

1. **Call count sanity check.** After a run, compare:
   - `usage_summary.vendors.openrouter.calls`
   - against `len(audit_summary.boundary_calls) + len(bullshit_profile.passages) + (1 or 2 — extraction, plus retry on quote-fabrication ~14% of runs) + (0 or 1 — revision, only when not skipped)`
   These should match. If they don't, a call site is missing a `stage=` label or a code path is bypassing the boundary client. Read `usage_summary.vendors.openrouter.stages.extraction.calls` and `.extraction_retry.calls` to see which extraction path the run actually took.

2. **Coverage check.** Look at top-level `cost_estimate_state` and `cost_estimate_coverage.calls_with_unknown_price`. If any are non-zero, a model is being used that isn't in the price table — add it to `pricing.py`.
3. **Model attribution check.** Look at `usage_summary.vendors.openrouter.model_attribution.mismatch_count`. If it is non-zero, the served model differed from the requested model. Treat model-specific evidence from that run as attribution-uncertain until reviewed.

The CI script at `scripts/inspect_run.py` (or the planned `scripts/audit_telemetry.py`, if added) should fail loudly if either check fails. The point is: numbers shown to the user must come from real telemetry, not estimates dressed up as measurements.

## Cross-references

- Boundary client: `engine/system_b/boundary_provider.py`
- Embedding capture: `engine/system_b/embedding_retriever.py` (`capture_usage()`)
- Aggregator: `engine/system_b/usage_summary.py`
- Pricing table: `engine/system_b/pricing.py`
- Observatory route: `observatory/serve_result.py` (`/usage` and `/api/case/<id>/usage`)
- V60 enrichment and ledger validation: `engine/system_b/v60_enrichment.py`
- V60 Observatory route: `observatory/serve_result.py` (`/audit/v60`)
- SKILL chat surface: `SKILL.md` Step 4 (cost line), Step 8b default-off state, and optional Step 8b sub-agent merge
