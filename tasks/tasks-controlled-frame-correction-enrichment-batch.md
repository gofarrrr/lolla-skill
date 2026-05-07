# Controlled Frame Correction Enrichment Batch

## Relevant Files

- `research/v10-graph-only-priority-audit-2026-05-07.md` - PR44 audit that selects frame correction / metacognitive blind-spot discipline as the next controlled family.
- `references/model-affordance-extraction.md` - Extraction doctrine and no-completeness-theater contract.
- `data/schemas/model_affordance.schema.json` - Reviewed affordance record schema.
- `data/model_sources/` - Repo-custodied canonical Markdown source files used for PR45 extraction.
- `data/model_affordances/batch_10/` - PR45 reviewed records for frame correction, metacognition, counterfactuals, and evidence-boundary models.
- `data/compiled/model_affordances/affordances_v11.json` - Draft/review-only compiled artifact after PR45.
- `data/compiled/model_affordances/quality_report_v11.md` - Draft/review-only quality report after PR45.
- `tests/test_pr45_batch10_records.py` - PR45 batch scope, schema, source custody, compile, and dormancy tests.
- `research/pr45-controlled-frame-correction-enrichment-report-2026-05-07.md` - PR45 extraction report.
- `research/reasoning-substrate-next-session-handover-2026-05-06.md` - Handover update for PR45.
- `plans/knowledge-substrate-roadmap-2026-05-04.md` - Roadmap update for PR45.
- `plans/knowledge-use-schema-2026-05-04.md` - Schema doctrine update for PR45.
- `research/decision-pressure-product-doctrine-2026-05-06.md` - Product doctrine update for PR45.
- `research/knowledge-matching-current-state-audit-2026-05-06.md` - Current-state posture update after PR45.

## Guardrails

- PR45 is controlled source-backed enrichment, not broad Batch 3b.
- Read full repo-custodied canonical Markdown before extracting.
- Do not mechanically parse headings, bullets, or keywords into fields.
- Extract only source-supported operational depth.
- Preserve absence records as knowledge, not failure.
- Keep `affordances_v11.json` `draft_review_only`.
- Do not promote runtime, prompts, lanes, `/lolla`, Observatory, memo, Step 8, Step 6, Lane 4 runtime, model calls, judges, or user-facing Decision Pressure.
- Do not make Python choose final pressure, wisdom, or reasoning mode.
- Do not turn `reasoning-mode-router` into deterministic routing, a new lane, prompt mechanics, or case-type rules.

## Instructions For Completing Tasks

Change `- [ ]` to `- [x]` as each sub-task is completed.

## Tasks

- [x] 0.0 Branch setup and grounding
  - [x] 0.1 Start from `feature/knowledge-substrate-pr11-gate4-edge-probes` after PR44 merge.
  - [x] 0.2 Create `feature/reasoning-substrate-pr45-controlled-frame-correction-enrichment`.
  - [x] 0.3 Read PR44 audit, extraction contract, prior batch tests, and source metadata.
  - [x] 0.4 Verify the 12 target model IDs exist in the runtime graph and source manifest and are absent from v10.

- [x] 1.0 RED: add PR45 batch tests
  - [x] 1.1 Test that `batch_10` contains exactly the 12 approved model IDs.
  - [x] 1.2 Test each record validates against schema and repo-custodied sources.
  - [x] 1.3 Test every source quote is an exact substring of the repo-custodied source file.
  - [x] 1.4 Test records are compact and preserve absence records.
  - [x] 1.5 Test drift-blocking absences include deterministic routing, infinite deferral, gap theater, theory shopping, and coherence-as-proof.
  - [x] 1.6 Test PR45 target models were graph-only before v11.
  - [x] 1.7 Test compiled v11 includes v10 plus batch 10 and remains `draft_review_only`.
  - [x] 1.8 Test v11 is not imported by live runtime paths.

- [x] 2.0 Read sources and extract records
  - [x] 2.1 Read `cognitive-gaps-assessment`.
  - [x] 2.2 Read `critical-thinking`.
  - [x] 2.3 Read `counterfactual-reasoning`.
  - [x] 2.4 Read `metacognitive-questioning`.
  - [x] 2.5 Read `reasoning-mode-router`.
  - [x] 2.6 Read `reframing-perspective`.
  - [x] 2.7 Read `theory-induced-blindness`.
  - [x] 2.8 Read `einstellung-effect`.
  - [x] 2.9 Read `dialectical-reasoning`.
  - [x] 2.10 Read `bias-blind-spot`.
  - [x] 2.11 Read `false-precision-avoidance`.
  - [x] 2.12 Read `wysiati`.
  - [x] 2.13 Add one reviewed JSON record per target model under `data/model_affordances/batch_10/`.

- [x] 3.0 Compile and report
  - [x] 3.1 Compile `affordances_v11.json` and `quality_report_v11.md`.
  - [x] 3.2 Write `research/pr45-controlled-frame-correction-enrichment-report-2026-05-07.md`.
  - [x] 3.3 Record target list, source files, outcomes, affordance counts, absence counts, and corpus lessons.
  - [x] 3.4 Recommend whether PR46 should compare packets, continue small controlled enrichment, or pause.

- [x] 4.0 Update living docs narrowly
  - [x] 4.1 Update next-session handover.
  - [x] 4.2 Update knowledge-substrate roadmap.
  - [x] 4.3 Update knowledge-use schema.
  - [x] 4.4 Update decision-pressure product doctrine.
  - [x] 4.5 Update current-state audit posture found by drift scan.

- [x] 5.0 Verify and hand off
  - [x] 5.1 Run `PYTHONPATH=. pytest tests/test_pr45_batch10_records.py`.
  - [x] 5.2 Run affordance compiler/schema/batch tests.
  - [x] 5.3 Run packet/render/source-custody/coverage tests.
  - [x] 5.4 Run decision-pressure trace regression tests.
  - [x] 5.5 Run `git diff --check`.
  - [x] 5.6 Run changed-path guardrail checks.
  - [x] 5.7 Open PR and summarize target models, outcomes, counts, tests, and PR46 recommendation.
