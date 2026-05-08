# Controlled Graph-Only Extraction Batch

## Relevant Files

- `data/model_sources/` - Repo-custodied canonical markdown sources for all 222 runtime models.
- `data/model_affordances/batch_4/` - PR28 controlled reviewed extraction records for ten graph-only models.
- `data/compiled/model_affordances/affordances_v5.json` - Draft/review-only compiled artifact including v4 plus PR28 records if compilation remains safe.
- `data/compiled/model_affordances/quality_report_v5.md` - Draft/review-only compiler quality report for v5 if compilation remains safe.
- `tests/test_pr28_batch4_records.py` - Focused PR28 tests for target IDs, schema validation, source custody, exact quotes, absence records, and dormant compiled output.
- `research/pr28-controlled-graph-only-extraction-report-2026-05-06.md` - PR28 extraction quality report and PR29 recommendation.
- `research/reasoning-substrate-next-session-handover-2026-05-06.md` - Next-session handover update for PR28.
- `plans/knowledge-substrate-roadmap-2026-05-04.md` - Living roadmap update for PR28 posture.
- `plans/knowledge-use-schema-2026-05-04.md` - Living schema doctrine update for PR28 posture.
- `research/decision-pressure-product-doctrine-2026-05-06.md` - Product doctrine update for controlled extraction.

## Guardrails

- PR28 is a controlled extraction quality loop, not broad Batch 3b.
- Do not broaden beyond the ten approved target models.
- Do not treat source custody as reviewed affordance depth.
- Do not fill schema fields for completeness.
- Do not invent unsupported do-not-use conditions, misuse guards, or treatment requirements.
- Do not modify prompts, lanes, runtime packet production, live `/lolla`, Observatory, memo, Step 8, Step 6, or Lane 4 runtime.
- Do not promote v5 into runtime.
- Do not run paid model calls or judges.
- Keep absence records first-class.

## Instructions For Completing Tasks

Change `- [ ]` to `- [x]` as each sub-task is completed.

## Tasks

- [x] 0.0 Branch setup and grounding
  - [x] 0.1 Start from `feature/knowledge-substrate-pr11-gate4-edge-probes`.
  - [x] 0.2 Create `feature/reasoning-substrate-pr28-controlled-graph-only-extraction`.
  - [x] 0.3 Read PR27 packet review, fixture, coverage audit, source-custody report, handover, extraction reference, schema, and prior batch examples.
  - [x] 0.4 Verify the ten target models are runtime graph models, source-custodied, and absent from v4.

- [x] 1.0 RED: add focused PR28 tests
  - [x] 1.1 Test that `batch_4` contains exactly the ten approved model IDs.
  - [x] 1.2 Test that each record validates against schema and repo-custodied sources.
  - [x] 1.3 Test source manifest matching and exact quote custody.
  - [x] 1.4 Test that absence records are accepted and counted.
  - [x] 1.5 Test that compiled v5 includes v4 plus PR28 records and remains draft/review-only.
  - [x] 1.6 Test that no live runtime path imports v5.

- [x] 2.0 GREEN: create reviewed batch records
  - [x] 2.1 Read all ten repo-custodied source files as source material.
  - [x] 2.2 Extract only source-supported operational affordances.
  - [x] 2.3 Add absence records where the source is thin, generic, duplicate, or unsupported.
  - [x] 2.4 Keep exactly one JSON record per target model under `batch_4`.

- [x] 3.0 Compile dormant v5 artifact
  - [x] 3.1 Compile pilot, batch_1, batch_2, batch_3a, and batch_4 into `affordances_v5.json`.
  - [x] 3.2 Generate `quality_report_v5.md`.
  - [x] 3.3 Confirm v5 status remains draft/review-only and is not imported by live runtime paths.

- [x] 4.0 Write extraction report
  - [x] 4.1 Document target model list, selection reasons, source files, and source custody notes.
  - [x] 4.2 Document extraction outcome, affordance count, and absence count per model.
  - [x] 4.3 Document strong, weak, missing, and too-thin fields.
  - [x] 4.4 Recommend PR29 packet regeneration and comparison.
  - [x] 4.5 Choose the PR28 decision label.

- [x] 5.0 Update living docs narrowly
  - [x] 5.1 Update next-session handover.
  - [x] 5.2 Update knowledge-substrate roadmap.
  - [x] 5.3 Update knowledge-use schema.
  - [x] 5.4 Update decision-pressure product doctrine.

- [x] 6.0 Verify and hand off
  - [x] 6.1 Run PR28 focused tests.
  - [x] 6.2 Run affordance schema/compiler/batch tests.
  - [x] 6.3 Run packet, fixture, source-custody, and coverage tests.
  - [x] 6.4 Run decision-pressure trace regression tests.
  - [x] 6.5 Run `git diff --check`.
  - [x] 6.6 Run changed-path guardrail check.
  - [x] 6.7 Open PR and summarize outcomes, tests, thin sources, and PR29 recommendation.
