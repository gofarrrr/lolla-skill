# Controlled Communication And Competition Enrichment Batch

## Relevant Files

- `research/reasoning-substrate-v6-packet-usefulness-review-2026-05-07.md` - PR33 packet usefulness review that justifies another controlled, gap-driven enrichment slice.
- `references/model-affordance-extraction.md` - Extraction doctrine and no-completeness-theater contract.
- `data/schemas/model_affordance.schema.json` - Reviewed affordance record schema.
- `data/model_sources/` - Repo-custodied canonical Markdown source files used for PR34 extraction.
- `data/model_affordances/batch_6/` - PR34 reviewed records for the approved communication, feedback, competitive, and analogical models.
- `data/compiled/model_affordances/affordances_v7.json` - Draft/review-only compiled artifact after PR34.
- `data/compiled/model_affordances/quality_report_v7.md` - Draft/review-only quality report after PR34.
- `tests/test_pr34_batch6_records.py` - PR34 batch scope, schema, source custody, compile, and dormancy tests.
- `research/pr34-controlled-communication-competition-enrichment-report-2026-05-07.md` - PR34 extraction report.
- `research/reasoning-substrate-next-session-handover-2026-05-06.md` - Handover update for PR34.
- `plans/knowledge-substrate-roadmap-2026-05-04.md` - Roadmap update for PR34.
- `plans/knowledge-use-schema-2026-05-04.md` - Schema doctrine update for PR34.
- `research/decision-pressure-product-doctrine-2026-05-06.md` - Product doctrine update for PR34.

## Guardrails

- PR34 is controlled source-backed enrichment, not broad Batch 3b.
- Read full repo-custodied canonical Markdown before extracting.
- Do not mechanically parse headings, bullets, or keywords into fields.
- Extract only source-supported operational depth.
- Preserve absence records as knowledge, not failure.
- Keep `affordances_v7.json` `draft_review_only`.
- Do not promote runtime, prompts, lanes, `/lolla`, Observatory, memo, Step 8, Step 6, Lane 4 runtime, model calls, judges, or user-facing Decision Pressure.
- Do not make Python choose final pressure or wisdom.

## Instructions For Completing Tasks

Change `- [ ]` to `- [x]` as each sub-task is completed.

## Tasks

- [ ] 0.0 Branch setup and grounding
  - [x] 0.1 Start from `feature/knowledge-substrate-pr11-gate4-edge-probes`.
  - [x] 0.2 Create `feature/reasoning-substrate-pr34-controlled-communication-competition-enrichment`.
  - [x] 0.3 Read PR33 packet review, handover, extraction contract, schema, PR32 batch test, and source files.
  - [x] 0.4 Verify the 7 target model IDs exist in the runtime graph and source manifest and are absent from v6.

- [x] 1.0 RED: add PR34 batch tests
  - [x] 1.1 Test that `batch_6` contains exactly the 7 approved model IDs.
  - [x] 1.2 Test each record validates against schema and repo-custodied sources.
  - [x] 1.3 Test every source quote is an exact substring of the repo-custodied source file.
  - [x] 1.4 Test absence records are first-class and counted.
  - [x] 1.5 Test PR34 target models were graph-only before v7.
  - [x] 1.6 Test compiled v7 includes v6 plus batch 6 and remains `draft_review_only`.
  - [x] 1.7 Test v7 is not imported by live runtime paths.

- [x] 2.0 Read sources and extract records
  - [x] 2.1 Read `nash-equilibrium`.
  - [x] 2.2 Read `prisoners-dilemma`.
  - [x] 2.3 Read `active-listening`.
  - [x] 2.4 Read `constructive-feedback-models`.
  - [x] 2.5 Read `feedback-models-sbi`.
  - [x] 2.6 Read `analogies-and-metaphors`.
  - [x] 2.7 Read `natural-selection-analogy`.
  - [x] 2.8 Add one reviewed JSON record per target model under `data/model_affordances/batch_6/`.

- [x] 3.0 Compile and report
  - [x] 3.1 Compile `affordances_v7.json` and `quality_report_v7.md`.
  - [x] 3.2 Write `research/pr34-controlled-communication-competition-enrichment-report-2026-05-07.md`.
  - [x] 3.3 Record target list, source files, outcomes, affordance counts, absence counts, and corpus lessons.
  - [x] 3.4 Recommend whether PR35 should compare packets, continue small controlled enrichment, or pause.

- [x] 4.0 Update living docs narrowly
  - [x] 4.1 Update next-session handover.
  - [x] 4.2 Update knowledge-substrate roadmap.
  - [x] 4.3 Update knowledge-use schema.
  - [x] 4.4 Update decision-pressure product doctrine.

- [x] 5.0 Verify and hand off
  - [x] 5.1 Run `PYTHONPATH=. pytest tests/test_pr34_batch6_records.py`.
  - [x] 5.2 Run affordance compiler/schema/batch tests.
  - [x] 5.3 Run packet/render/source-custody/coverage tests.
  - [x] 5.4 Run decision-pressure trace regression tests.
  - [x] 5.5 Run `git diff --check`.
  - [x] 5.6 Run changed-path guardrail checks.
  - [x] 5.7 Open PR and summarize target models, outcomes, counts, tests, and PR35 recommendation.
