# Cost & Telemetry — How Lolla Measures What a Run Costs

This is the single canonical reference for "what API calls did this run make and what did they cost." If anything in the codebase contradicts this doc, fix the code, not the doc.

## TL;DR

Every Lolla run produces a `usage_summary` block in the result JSON at `/tmp/lolla_<run_id>_result.json`. It looks like:

```json
{
  "usage_summary": {
    "run_id": "20260428T064421Z",
    "pricing_table_version": "2026-04-28",
    "estimated_total_cost_usd": 2.4234,
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

The chat summary at end of Step 4 prints a one-line version (`Run cost so far: $X.XX • Y OpenRouter calls • Z.Z% cache hit`).

## What gets measured

Lolla makes calls to three vendors. Each is recorded into `usage_summary.vendors.<vendor>`.

### OpenRouter (chat completions)

Every Grok / OpenRouter call from anywhere in the pipeline. Recorded automatically by `OpenAICompatibleBoundaryClient` — every `run_json` / `run_json_with_metadata` call appends to `client.call_log` with the `stage=` label the caller passed in.

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
| `bullshit_index` | `engine/system_b/bullshit_index.py`, one per passage of the audited answer | 1 per ~1500 chars (~30–60 typical) |
| `revision` | optional post-pipeline revision (skipped under `--skip-revision`) | 0–1 |

Most expensive lane: **bullshit_index** (1 call per passage, in parallel — easily 50+ calls on a long answer).

Per-call records carry: `prompt_tokens`, `completion_tokens`, `cached_tokens`, `total_tokens`, `status`. Status is `ok` for successful calls, an HTTP error code, `timeout`, `missing_api_key`, or `response_json_error` for failures.

### OpenAI (embeddings + query expansion)

Every embedding or chat call inside `engine/system_b/embedding_retriever.py`. Recorded via a `ContextVar`-scoped capture (`capture_usage()` opened at the top of the pipeline run, closed before `usage_summary` is built). Per-run isolation is structural — calls outside the scope are silently ignored, not leaked into another run's totals.

Three call types:

| Endpoint | Model | Use |
|---|---|---|
| `embeddings` | `text-embedding-3-large` | Query embedding for model retrieval |
| `embeddings` | `text-embedding-3-large` | Batch embedding of expanded query variants |
| `chat` | `gpt-4o-mini` | Query expansion (2 alternative phrasings per query) |

Total OpenAI cost per run is typically well under $0.01.

### Anthropic (Step 7 sub-agents)

The 4 pressure-check sub-agents fire from inside the SKILL orchestration via Claude Code's Agent tool, NOT through `OpenAICompatibleBoundaryClient`. Their cost is the largest single line item on most runs because they use whatever Claude model the orchestrator runs on (typically Opus).

**Resolution gap:** Claude Code's task notification surfaces only `total_tokens`, not a prompt/completion split. The cost estimator treats the entire total as input tokens at the model's input price — a conservative over-estimate. The real cost is somewhere lower, depending on how much was completion vs. prompt. The result JSON marks this with `vendors.anthropic_subagents.estimation_method = "conservative_input_only_no_split_available"`.

Step 8b (`SKILL.md`) records the sub-agent records into the `usage_summary` after both Step 6 and Step 7 are complete.

## Where the numbers come from (data flow)

```
┌────────────────┐     stage="extraction"          ┌────────────────────────────┐
│ run_extract.py │────────────────────────────────▶│ /tmp/lolla_<run_id>_       │
│                │   writes client.call_log to     │   extraction_calls.json    │
└────────────────┘   sidecar at end                └────────────────────────────┘
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

[ later, after Step 7 sub-agents complete, SKILL Step 8b: ]

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
3. The extraction sidecar path is namespaced by `$LOLLA_RUN_ID`.
4. Sub-agent records are passed in by the SKILL after Step 7, not pulled from any shared state.

## Pricing

Hardcoded in `engine/system_b/pricing.py`. The constant `PRICES_LAST_VERIFIED` is surfaced into every `usage_summary` so consumers can tell whether the estimate is fresh.

To bump prices:

1. Edit `engine/system_b/pricing.py`.
2. Update `PRICES_LAST_VERIFIED` to today's date.
3. Cross-check against the provider's pricing page. Specifically:
   - OpenRouter: `https://openrouter.ai/docs#models` (per-model rates)
   - OpenAI: `https://openai.com/api/pricing/`
   - Anthropic: `https://www.anthropic.com/pricing#anthropic-api`

If the model used on a run isn't in the price table, the call counts and tokens still record but `estimated_cost_usd` for that vendor stays at zero and `cost_estimate_coverage.calls_with_unknown_price` is non-zero. Watch this field — a drift to non-zero means a new model showed up that hasn't been priced yet.

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

## Caching — why the hit rate is low and what to do about it

Current cache hit rate on most runs: ~2-5%. Achievable: ~60-75%.

**Why it's low:** xAI Grok via OpenRouter caches the longest matching prompt prefix from position zero (system message first, then user message). Lolla currently puts the **per-stage instructions** in the system message and the **conversation transcript + extraction context** (the big stable block — same across ~16 pipeline calls) in the user message. Since the system message diverges first, the cache prefix breaks before reaching the conversation. Only the small shared preamble at the top of system prompts caches (~160 tokens/call).

**The fix:** swap message slots. Put the stable conversation+extraction in the system message; put per-stage instructions in the user message. Estimated impact: cache hit rate to ~70%, total run cost down ~40% (cached input is ~25% of fresh input on Grok). 

**Why it isn't done yet:** reordering prompt slots is content-equivalent on paper but can shift model behavior in practice. Some models weight system vs. user content differently. This change requires running the existing test cases (in `tests/`) before/after to confirm audit findings don't drift. Telemetry first, optimization second.

The cache hit rate is surfaced as `vendors.openrouter.cache_hit_rate` in `usage_summary` and on the Observatory `/usage` page, so the savings (or lack thereof) from any future prompt restructuring will be visible directly.

## Verifying the telemetry is honest

Two checks:

1. **Call count sanity check.** After a run, compare:
   - `usage_summary.vendors.openrouter.calls`
   - against `len(audit_summary.boundary_calls) + len(bullshit_profile.passages) + (1 or 2 — extraction, plus retry on quote-fabrication ~14% of runs) + (0 or 1 — revision, only when not skipped)`
   These should match. If they don't, a call site is missing a `stage=` label or a code path is bypassing the boundary client. Read `usage_summary.vendors.openrouter.stages.extraction.calls` and `.extraction_retry.calls` to see which extraction path the run actually took.

2. **Coverage check.** Look at `cost_estimate_coverage.calls_with_unknown_price` for each vendor. If any are non-zero, a model is being used that isn't in the price table — add it to `pricing.py`.

The CI script at `scripts/inspect_run.py` (or the planned `scripts/audit_telemetry.py`, if added) should fail loudly if either check fails. The point is: numbers shown to the user must come from real telemetry, not estimates dressed up as measurements.

## Cross-references

- Boundary client: `engine/system_b/boundary_provider.py`
- Embedding capture: `engine/system_b/embedding_retriever.py` (`capture_usage()`)
- Aggregator: `engine/system_b/usage_summary.py`
- Pricing table: `engine/system_b/pricing.py`
- Observatory route: `observatory/serve_result.py` (`/usage` and `/api/case/<id>/usage`)
- SKILL chat surface: `SKILL.md` Step 4 (cost line) and Step 8b (sub-agent merge)
