# Controlled Capability-Gap Enrichment Batch

## Relevant Files

- `research/v5-reviewed-model-capability-audit-2026-05-07.md` - PR31 audit naming the capability gaps that justify this controlled enrichment batch.
- `references/model-affordance-extraction.md` - Extraction doctrine and no-completeness-theater contract.
- `data/schemas/model_affordance.schema.json` - Reviewed affordance record schema.
- `data/model_sources/` - Repo-custodied canonical Markdown source files used for PR32 extraction.
- `data/model_affordances/batch_5/` - PR32 reviewed records for the 16 approved capability-gap models.
- `data/compiled/model_affordances/affordances_v6.json` - Draft/review-only compiled artifact after PR32.
- `data/compiled/model_affordances/quality_report_v6.md` - Draft/review-only quality report after PR32.
- `tests/test_pr32_batch5_records.py` - PR32 batch scope, schema, source custody, compile, and dormancy tests.
- `research/pr32-controlled-capability-gap-enrichment-report-2026-05-07.md` - PR32 extraction report.
- `research/reasoning-substrate-next-session-handover-2026-05-06.md` - Handover update for PR32.
- `plans/knowledge-substrate-roadmap-2026-05-04.md` - Roadmap update for PR32.
- `plans/knowledge-use-schema-2026-05-04.md` - Schema doctrine update for PR32.
- `research/decision-pressure-product-doctrine-2026-05-06.md` - Product doctrine update for PR32.

## Guardrails

- PR32 is controlled source-backed enrichment, not broad Batch 3b.
- Read full repo-custodied canonical Markdown before extracting.
- Do not mechanically parse headings, bullets, or keywords into fields.
- Extract only source-supported operational depth.
- Preserve absence records as knowledge, not failure.
- Keep `affordances_v6.json` `draft_review_only`.
- Do not promote runtime, prompts, lanes, `/lolla`, Observatory, memo, Step 8, Step 6, Lane 4 runtime, model calls, judges, or user-facing Decision Pressure.
- Do not make Python choose final pressure or wisdom.

## Instructions For Completing Tasks

Change `- [ ]` to `- [x]` as each sub-task is completed.

## Tasks

- [x] 0.0 Branch setup and grounding
  - [x] 0.1 Start from `feature/knowledge-substrate-pr11-gate4-edge-probes`.
  - [x] 0.2 Create `feature/reasoning-substrate-pr32-controlled-capability-gap-enrichment`.
  - [x] 0.3 Read PR31 audit, handover, extraction contract, schema, PR28 batch test, and existing batch examples.
  - [x] 0.4 Verify the 16 target model IDs exist in the runtime graph and source manifest and are absent from v5.

- [x] 1.0 RED: add PR32 batch tests
  - [x] 1.1 Test that `batch_5` contains exactly the 16 approved model IDs.
  - [x] 1.2 Test each record validates against schema and repo-custodied sources.
  - [x] 1.3 Test every source quote is an exact substring of the repo-custodied source file.
  - [x] 1.4 Test absence records are first-class and counted.
  - [x] 1.5 Test PR32 target models were graph-only before v6.
  - [x] 1.6 Test compiled v6 includes v5 plus batch 5 and remains `draft_review_only`.
  - [x] 1.7 Test v6 is not imported by live runtime paths.

- [x] 2.0 Read sources and extract records
  - [x] 2.1 Read `delays`.
  - [x] 2.2 Read `obligations-controls-mapping`.
  - [x] 2.3 Read `peer-review-your-perspectives`.
  - [x] 2.4 Read `formal-reasoning`.
  - [x] 2.5 Read `checklists`.
  - [x] 2.6 Read `status-quo-bias`.
  - [x] 2.7 Read `commitment-bias`.
  - [x] 2.8 Read `optimism-bias-and-planning-fallacy`.
  - [x] 2.9 Read `batna`.
  - [x] 2.10 Read `game-theory-payoffs`.
  - [x] 2.11 Read `red-queen-effect`.
  - [x] 2.12 Read `jobs-to-be-done`.
  - [x] 2.13 Read `user-centered-design`.
  - [x] 2.14 Read `lock-in`.
  - [x] 2.15 Read `path-dependence`.
  - [x] 2.16 Read `cross-cultural-communication-frameworks`.
  - [x] 2.17 Add one reviewed JSON record per target model under `data/model_affordances/batch_5/`.

- [x] 3.0 Compile and report
  - [x] 3.1 Compile `affordances_v6.json` and `quality_report_v6.md`.
  - [x] 3.2 Write `research/pr32-controlled-capability-gap-enrichment-report-2026-05-07.md`.
  - [x] 3.3 Record target list, source files, outcomes, affordance counts, absence counts, and corpus lessons.
  - [x] 3.4 Recommend whether PR33 should compare packets, review receiver usefulness, or pause.

- [x] 4.0 Update living docs narrowly
  - [x] 4.1 Update next-session handover.
  - [x] 4.2 Update knowledge-substrate roadmap.
  - [x] 4.3 Update knowledge-use schema.
  - [x] 4.4 Update decision-pressure product doctrine.

- [x] 5.0 Verify and hand off
  - [x] 5.1 Run `PYTHONPATH=. pytest tests/test_pr32_batch5_records.py`.
  - [x] 5.2 Run affordance compiler/schema/batch tests.
  - [x] 5.3 Run packet/render/source-custody/coverage tests.
  - [x] 5.4 Run decision-pressure trace regression tests.
  - [x] 5.5 Run `git diff --check`.
  - [x] 5.6 Run changed-path guardrail checks.
  - [x] 5.7 Open PR and summarize target models, outcomes, counts, tests, and PR33 recommendation.
