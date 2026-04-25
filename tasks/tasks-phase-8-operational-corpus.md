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

## Sub-phase 8a: Token + cost tracking

### Approved decisions

- **Capture at the boundary call level.** Every `boundary.run_json` / `run_json_with_metadata` call records: model id, input tokens, output tokens, cost (computed from a model-id-keyed price table).
- **Aggregate at the pipeline run level.** `AuditTrace` (or a new field) carries total tokens + total cost for the run.
- **Price table is config-driven.** Don't hardcode prices in code; load from `engine/system_b/model_pricing.yaml` (or similar).
- **Backward compatible**: missing token counts (e.g. mocked boundaries in tests) record `None` and don't fail.

### Out of scope (8a)

- Real-time alerting on cost overruns. Just measurement for now.
- Per-user / per-tenant aggregation. The pipeline doesn't have tenant context.
- Historical cost analysis tooling. Just the data; analysis is downstream.

### Files involved

- `engine/system_b/boundary_provider.py` — wrap the boundary client to extract usage metadata
- `engine/system_b/pipeline.py` (or new `engine/system_b/boundary_tracing.py` if Phase 7.1 happened) — `BoundaryCallTrace` dataclass extension
- `engine/system_b/audit_trace.py` (if exists, else in `pipeline.py`) — `AuditTrace` aggregate
- `engine/system_b/model_pricing.yaml` — NEW. Price table.
- Tests: new `tests/test_boundary_token_tracking.py` + extensions to existing pipeline tests

### Tasks (TDD)

#### 0.0 Branch + baseline

- [ ] `git switch -c feat/phase-8a-token-tracking`
- [ ] `pytest tests -q`. Record baseline.

#### 1.0 Extend BoundaryCallTrace shape

- [ ] 1.1 RED: in `tests/test_boundary_token_tracking.py`, write a test that constructs a `BoundaryCallTrace` with `input_tokens=100, output_tokens=200, cost_usd=0.005` and serializes it to dict. Should fail (fields don't exist).
- [ ] 1.2 GREEN: add fields to `BoundaryCallTrace`: `input_tokens: int | None = None`, `output_tokens: int | None = None`, `cost_usd: float | None = None`, `model_id: str | None = None`.
- [ ] 1.3 RED: existing tests that round-trip `BoundaryCallTrace` should still pass. If any break, the new fields aren't backward-compatible.
- [ ] 1.4 Verify with full suite.

#### 2.0 Capture usage from OpenRouter response

- [ ] 2.1 Read OpenRouter docs / inspect actual response shape: usage info comes back in the response payload (typically `usage.prompt_tokens` + `usage.completion_tokens`).
- [ ] 2.2 RED: write a test that mocks an OpenRouter response with usage block. The boundary client (or its trace metadata) should expose those numbers.
- [ ] 2.3 GREEN: in `boundary_provider.py`, modify `run_json_with_metadata` to extract usage and pass through to caller via `metadata`.
- [ ] 2.4 In `_metadata_to_boundary_call_trace` (pipeline.py or boundary_tracing.py), populate the new fields.

#### 3.0 Cost computation from price table

- [ ] 3.1 Create `engine/system_b/model_pricing.yaml`:
  ```yaml
  prices:
    grok-4.1-fast:
      input_per_1m: 0.20
      output_per_1m: 0.50
    # ... other models
  ```
- [ ] 3.2 RED: test that for a known model_id and token counts, cost is computed correctly. Should fail (no cost computation yet).
- [ ] 3.3 GREEN: load the YAML, compute cost in `_metadata_to_boundary_call_trace`. If model_id not in table, log a warning and leave cost=None.

#### 4.0 Aggregate at pipeline-run level

- [ ] 4.1 RED: test that after pipeline.run() completes, the returned audit/trace has `total_input_tokens`, `total_output_tokens`, `total_cost_usd` matching the sum of boundary call traces.
- [ ] 4.2 GREEN: in pipeline.py (after all lanes run, before returning), compute the aggregates from `boundary_calls` and attach to AuditTrace.

#### 5.0 Verify + PR

- [ ] Full suite green.
- [ ] PR title: `feat: Phase 8a — per-call and per-run token + cost tracking`.

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
