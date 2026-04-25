# Phase 8 — Operational maturity: token/cost tracking + real-conversation corpus

**Future branch:** `feat/phase-8-token-cost-tracking` (cost first, corpus second)
**Risk:** Medium — touches every LLM boundary call.
**Estimated time:** open-ended; sized as two sub-projects.
**Prerequisite:** Phase 4d minimum. Phase 6 + 7 ideally done first because telemetry surfaces are cleaner after splits.

## Why this phase

Two distinct things, both flagged by the PM as production-sizing prerequisites:

1. **Token + cost tracking per call and per pipeline run.** Today, `BoundaryCallTrace` records wall-time only. Production sizing requires knowing how many tokens each call costs, which model was used, and aggregate cost per pipeline run.

2. **Real-conversation corpus.** The 10-case synthetic corpus has been the regression surface for all lane migrations. Real production conversations would surface edge cases the synthetic corpus doesn't.

These can ship independently. **Telemetry first** (higher leverage; production-blocker per PM memory).

---

## Sub-phase 8a: Cost computation (token tracking ALREADY EXISTS)

### Critical correction from initial draft

**Token tracking is already implemented.** Initial handover assumed it wasn't — that's wrong. Audit before this phase confirmed:

- `engine/system_b/boundary_provider.py:16-28` defines `BoundaryCallMetadata` with: `provider_name`, `model`, `status`, `prompt_tokens`, `completion_tokens`, `total_tokens`, `cached_tokens`, `cache_write_tokens`, `reasoning_tokens`, `reasoning_disabled`, `reasoning_details_present`.
- `engine/system_b/boundary_provider.py:366-399` (`_build_call_metadata`) extracts these from OpenRouter's `usage` block.
- `engine/system_b/pipeline.py:250-264` (`BoundaryCallTrace`) carries the same fields end-to-end.
- `engine/system_b/testing_harness.py:143-152` (`summarize_boundary_calls`) already aggregates `prompt_tokens_total`, `completion_tokens_total`, `total_tokens_total`, `cached_tokens_total`, `cache_write_tokens_total`, `reasoning_tokens_total` per pipeline run.

So Phase 8a is much smaller than originally drafted: **it's just adding cost (USD) computation on top of the existing token data, plus deciding where the per-run cost aggregate lives.**

### Approved decisions

- **Preserve existing field names.** `prompt_tokens` / `completion_tokens` / `total_tokens` / `model` are already consumed by `summarize_boundary_calls` and any external tooling. Do NOT rename to `input_tokens` / `output_tokens` / `model_id`.
- **Add cost fields only.** New: `cost_usd: float | None = None` on `BoundaryCallTrace` (and `BoundaryCallMetadata` if useful). Existing fields stay.
- **Price table is config-driven.** Load from `engine/system_b/model_pricing.yaml` (or similar).
- **Aggregate cost lives next to existing token aggregates** in `summarize_boundary_calls` — add `cost_usd_total` to its output dict. Don't introduce a separate aggregator unless there's a reason.
- **Backward compatible**: missing prices (model not in price table) record `cost_usd=None` and log a warning. Don't fail the pipeline run.

### Out of scope (8a)

- **Adding new token fields.** They already exist; do not touch.
- Real-time alerting on cost overruns. Just measurement for now.
- Per-user / per-tenant aggregation. The pipeline doesn't have tenant context.
- Historical cost analysis tooling. Just the data; analysis is downstream.

### Files involved

- `engine/system_b/pipeline.py` (or wherever `BoundaryCallTrace` lives after Phase 7.1) — add `cost_usd` field
- `engine/system_b/boundary_provider.py` — possibly add `cost_usd` to `BoundaryCallMetadata`; or compute cost in pipeline.py at trace-construction time (likely cleaner)
- `engine/system_b/model_pricing.yaml` — NEW. Price table.
- `engine/system_b/testing_harness.py` — extend `summarize_boundary_calls` with `cost_usd_total`
- Tests: new `tests/test_boundary_cost_computation.py`

### Tasks (TDD)

#### 0.0 Branch + baseline

- [ ] 0.1 `git switch -c feat/phase-8a-cost-computation`
- [ ] 0.2 `pytest tests -q`. Record baseline.
- [ ] 0.3 Read `engine/system_b/boundary_provider.py:16-28` and `pipeline.py:250-264` to confirm the existing field names. Match them exactly.

#### 1.0 Add cost field on BoundaryCallTrace

- [ ] 1.1 RED: in `tests/test_boundary_cost_computation.py`, write a test that constructs a `BoundaryCallTrace` with `cost_usd=0.0123` and asserts the field is preserved through serialization. Should fail (field doesn't exist).
- [ ] 1.2 GREEN: add `cost_usd: float | None = None` to `BoundaryCallTrace`. Do NOT change existing fields.
- [ ] 1.3 Verify full suite — backward-compat preserved (existing traces with no `cost_usd` still work).

#### 2.0 Add price table + cost computation

- [ ] 2.1 Create `engine/system_b/model_pricing.yaml`. Confirm the values with PM before committing — don't make up prices.
  ```yaml
  # Prices in USD per 1M tokens. Confirm with PM before merge.
  prices:
    "x-ai/grok-4-fast":
      input: 0.20
      output: 0.50
    # ... other models actually used
  ```
- [ ] 2.2 RED: write a test that given a known `model` and token counts, returns the correct cost in USD. Should fail (no compute function exists yet).
- [ ] 2.3 GREEN: implement `_compute_cost_usd(model: str, prompt_tokens: int, completion_tokens: int) -> float | None` that loads the YAML and computes. If `model` isn't in the table, log a warning and return `None`.

#### 3.0 Wire cost into the trace

- [ ] 3.1 RED: write a test that runs a mocked boundary call and asserts the resulting `BoundaryCallTrace` has `cost_usd` populated. Should fail (the wiring isn't there).
- [ ] 3.2 GREEN: at the point where `BoundaryCallTrace` is constructed from `BoundaryCallMetadata` (search for `_metadata_to_boundary_call_trace` or equivalent), call `_compute_cost_usd` and pass the result.

#### 4.0 Extend the existing aggregator

- [ ] 4.1 RED: write a test that `summarize_boundary_calls(traces_with_costs)` returns a `cost_usd_total` field equal to the sum of per-trace `cost_usd` (None values treated as 0).
- [ ] 4.2 GREEN: extend `engine/system_b/testing_harness.py:143-152` to add `cost_usd_total: sum(call.cost_usd or 0 for call in calls)`.

#### 5.0 Verify + PR

- [ ] Full suite green at baseline pass count or higher.
- [ ] PR title: `feat: Phase 8a — per-call and per-run cost (USD) computation`.

### What to ask Marcin (PM) before doing this

- **Price table values.** Don't make these up. PM should confirm input/output rates per model actually in use.
- **Model name format.** Verify whether `model` records the OpenRouter slug (e.g. `x-ai/grok-4-fast`), the bare name, or both. The price table's keys must match.
- **Whether `cost_usd_total` belongs in `summarize_boundary_calls`'s output** or somewhere else (e.g. a new `cost_summary` field on `AuditTrace`). Default to `summarize_boundary_calls`.

---

## Sub-phase 8b: Real-conversation corpus

### Approved decisions

- **Real conversations come from production runs.** Capture mechanism: extend `/lolla run` archival (already shipped per PM memory) to optionally save raw transcripts plus extraction outputs.
- **Anonymization**: any PII (names, locations, specific dollar amounts in personal contexts) gets redacted before the corpus is committed. PII detection is heuristic; PM-reviews the corpus before it ships.
- **Corpus location**: `research/test-cases-real/` parallel to the existing `research/test-cases/`. Same shape (case_X_conversation.txt + case_X_extraction.json).

### Out of scope (8b)

- Automated PII redaction beyond simple regex. PM-review is the gate.
- Replacing the synthetic corpus. Both stay; synthetic for fast regression, real for edge-case discovery.

### Tasks

#### 0.0 Pick real conversations

- [ ] Run the pipeline a few times in production-like settings. The archive (`/lolla run` artifacts) captures the inputs.
- [ ] PM picks 5-10 to anonymize. Variety: short / long, single-issue / multi-issue, technical / personal-stakes.

#### 1.0 Anonymize

- [ ] Per case: replace names, specific dates, dollar amounts (where they're personal, not market data).
- [ ] PM reviews each anonymized case before commit.

#### 2.0 Add to corpus

- [ ] Create `research/test-cases-real/` directory.
- [ ] Add anonymized cases.
- [ ] Document in `research/test-cases-real/README.md` what was anonymized and how.

#### 3.0 Use the corpus

- [ ] Extend the eval scripts (e.g. `scripts/phase5_live_constraints_eval.py`) to optionally run against the real corpus too.
- [ ] PM reviews diffs in metrics: are real conversations harder than synthetic?

#### 4.0 PR

- [ ] PR title: `feat: Phase 8b — real-conversation corpus (anonymized)`.

### Risks and mitigations (8b)

| Risk | Mitigation |
|---|---|
| PII slips through anonymization | PM review is mandatory before commit; multiple passes over each case |
| Real corpus reveals broken extraction | Document; flag to PM; do NOT silently update specialists to handle the new patterns — that's a separate phase |
| Real corpus changes regression baseline | Keep synthetic as primary regression; real is supplementary |

---

## Combined: how to know Phase 8 is done

**8a:**
- Every `BoundaryCallTrace` has `input_tokens`, `output_tokens`, `cost_usd`, `model_id` (None where unknown is OK).
- `AuditTrace` (or equivalent) has aggregate `total_*` fields.
- Tests pass with mocked usage data.

**8b:**
- `research/test-cases-real/` has at least 3 anonymized cases.
- Eval scripts can run against either corpus.
- PM has signed off on anonymization.

## What to ask Marcin (PM) about

- **Before 8a step 3.0**: confirm the price table values. Don't make these up.
- **Before 8b**: which production runs to pull from. Don't pick at random.
- **Anonymization standard**: PM dictates "what counts as PII". Don't decide unilaterally.
- **If any test in the existing corpus would benefit from the new telemetry data**: ask before adding new test fixtures.
