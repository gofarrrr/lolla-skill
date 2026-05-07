# Controlled Trust And Negotiation Enrichment Batch

## Relevant Files

- `research/reasoning-substrate-v7-packet-usefulness-review-2026-05-07.md` - PR35 packet usefulness review that justifies another controlled, gap-driven enrichment slice.
- `references/model-affordance-extraction.md` - Extraction doctrine and no-completeness-theater contract.
- `data/schemas/model_affordance.schema.json` - Reviewed affordance record schema.
- `data/model_sources/` - Repo-custodied canonical Markdown source files used for PR36 extraction.
- `data/model_affordances/batch_7/` - PR36 reviewed records for trust, relationship repair, negotiation, persuasion, and signaling models.
- `data/compiled/model_affordances/affordances_v8.json` - Draft/review-only compiled artifact after PR36.
- `data/compiled/model_affordances/quality_report_v8.md` - Draft/review-only quality report after PR36.
- `tests/test_pr36_batch7_records.py` - PR36 batch scope, schema, source custody, compile, and dormancy tests.
- `research/pr36-controlled-trust-negotiation-enrichment-report-2026-05-07.md` - PR36 extraction report.
- `research/reasoning-substrate-next-session-handover-2026-05-06.md` - Handover update for PR36.
- `plans/knowledge-substrate-roadmap-2026-05-04.md` - Roadmap update for PR36.
- `plans/knowledge-use-schema-2026-05-04.md` - Schema doctrine update for PR36.
- `research/decision-pressure-product-doctrine-2026-05-06.md` - Product doctrine update for PR36.

## Guardrails

- PR36 is controlled source-backed enrichment, not broad Batch 3b.
- Read full repo-custodied canonical Markdown before extracting.
- Do not mechanically parse headings, bullets, or keywords into fields.
- Extract only source-supported operational depth.
- Preserve absence records as knowledge, not failure.
- Keep `affordances_v8.json` `draft_review_only`.
- Do not promote runtime, prompts, lanes, `/lolla`, Observatory, memo, Step 8, Step 6, Lane 4 runtime, model calls, judges, or user-facing Decision Pressure.
- Do not make Python choose final pressure or wisdom.

## Instructions For Completing Tasks

Change `- [ ]` to `- [x]` as each sub-task is completed.

## Tasks

- [x] 0.0 Branch setup and grounding
  - [x] 0.1 Start from `feature/knowledge-substrate-pr11-gate4-edge-probes`.
  - [x] 0.2 Create `feature/reasoning-substrate-pr36-controlled-trust-negotiation-enrichment`.
  - [x] 0.3 Read PR35 packet review, handover, extraction contract, schema, prior batch tests, and source files.
  - [x] 0.4 Verify the 10 target model IDs exist in the runtime graph and source manifest and are absent from v7.

- [x] 1.0 RED: add PR36 batch tests
  - [x] 1.1 Test that `batch_7` contains exactly the 10 approved model IDs.
  - [x] 1.2 Test each record validates against schema and repo-custodied sources.
  - [x] 1.3 Test every source quote is an exact substring of the repo-custodied source file.
  - [x] 1.4 Test absence records are first-class and counted.
  - [x] 1.5 Test PR36 target models were graph-only before v8.
  - [x] 1.6 Test compiled v8 includes v7 plus batch 7 and remains `draft_review_only`.
  - [x] 1.7 Test v8 is not imported by live runtime paths.

- [x] 2.0 Read sources and extract records
  - [x] 2.1 Read `non-violent-communication`.
  - [x] 2.2 Read `emotional-intelligence`.
  - [x] 2.3 Read `understanding-motivations`.
  - [x] 2.4 Read `boundaries`.
  - [x] 2.5 Read `authenticity`.
  - [x] 2.6 Read `hanlons-razor`.
  - [x] 2.7 Read `reciprocity-principle`.
  - [x] 2.8 Read `persuasion-principles`.
  - [x] 2.9 Read `international-negotiation-and-diplomacy-models`.
  - [x] 2.10 Read `signaling`.
  - [x] 2.11 Add one reviewed JSON record per target model under `data/model_affordances/batch_7/`.

- [x] 3.0 Compile and report
  - [x] 3.1 Compile `affordances_v8.json` and `quality_report_v8.md`.
  - [x] 3.2 Write `research/pr36-controlled-trust-negotiation-enrichment-report-2026-05-07.md`.
  - [x] 3.3 Record target list, source files, outcomes, affordance counts, absence counts, and corpus lessons.
  - [x] 3.4 Recommend whether PR37 should compare packets, continue small controlled enrichment, or pause.

- [x] 4.0 Update living docs narrowly
  - [x] 4.1 Update next-session handover.
  - [x] 4.2 Update knowledge-substrate roadmap.
  - [x] 4.3 Update knowledge-use schema.
  - [x] 4.4 Update decision-pressure product doctrine.

- [x] 5.0 Verify and hand off
  - [x] 5.1 Run `PYTHONPATH=. pytest tests/test_pr36_batch7_records.py`.
  - [x] 5.2 Run affordance compiler/schema/batch tests.
  - [x] 5.3 Run packet/render/source-custody/coverage tests.
  - [x] 5.4 Run decision-pressure trace regression tests.
  - [x] 5.5 Run `git diff --check`.
  - [x] 5.6 Run changed-path guardrail checks.
  - [x] 5.7 Open PR and summarize target models, outcomes, counts, tests, and PR37 recommendation.
