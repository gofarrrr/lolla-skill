# Controlled Quantitative Inference Enrichment Batch

## Relevant Files

- `data/model_affordances/batch_13/` - PR50 reviewed records for quantitative inference / distributional reasoning.
- `data/compiled/model_affordances/affordances_v14.json` - Draft/review-only compiled artifact after PR50.
- `data/compiled/model_affordances/quality_report_v14.md` - v14 quality report.
- `tests/test_pr50_batch13_records.py` - PR50 validation tests.
- `research/pr50-controlled-quantitative-inference-enrichment-report-2026-05-07.md` - PR50 extraction report.
- `research/reasoning-substrate-next-session-handover-2026-05-06.md` - Handover update for PR50.
- `plans/knowledge-substrate-roadmap-2026-05-04.md` - Roadmap update for PR50.
- `plans/knowledge-use-schema-2026-05-04.md` - Schema doctrine update for PR50.
- `research/decision-pressure-product-doctrine-2026-05-06.md` - Product doctrine update for PR50.
- `research/knowledge-matching-current-state-audit-2026-05-06.md` - Current-state posture update after PR50.

## Guardrails

- PR50 is controlled source-backed enrichment, not broad Batch 3b.
- Keep `affordances_v14.json` `draft_review_only`.
- Do not promote v14 into runtime.
- Do not change prompts, lanes, `/lolla`, Observatory, memo, Step 8, Step 6, Lane 4 runtime, or user-facing output.
- Do not run model calls or judges.
- Do not make Python choose a final pressure, final option, final reasoning mode, or final statistical route.
- Treat absence records as first-class source understanding.

## Instructions For Completing Tasks

Change `- [ ]` to `- [x]` as each sub-task is completed.

## Tasks

- [x] 1.0 Branch setup and grounding
  - [x] 1.1 Merge PR49 into `feature/knowledge-substrate-pr11-gate4-edge-probes`.
  - [x] 1.2 Create `feature/reasoning-substrate-pr50-controlled-quantitative-inference-enrichment`.
  - [x] 1.3 Select a bounded quantitative inference / distributional reasoning family from the remaining graph-only set.
  - [x] 1.4 Add failing PR50 tests before adding Batch 13 records.

- [x] 2.0 Extract Batch 13 records
  - [x] 2.1 Read each target source from `data/model_sources/`.
  - [x] 2.2 Add exactly 12 records under `data/model_affordances/batch_13/`.
  - [x] 2.3 Add one compact reviewed affordance per target model.
  - [x] 2.4 Add two absence records per target model.
  - [x] 2.5 Verify each quote is an exact repo-custodied substring.
  - [x] 2.6 Confirm no target model was already reviewed in v13.

- [x] 3.0 Compile v14
  - [x] 3.1 Compile `affordances_v14.json` and `quality_report_v14.md`.
  - [x] 3.2 Confirm v14 remains `draft_review_only`.
  - [x] 3.3 Confirm v14 has 170 reviewed records, 206 affordances, and 325 absence records.
  - [x] 3.4 Confirm zero schema failures and zero source-quote rejections.

- [x] 4.0 Write reports and update living docs
  - [x] 4.1 Add PR50 extraction report.
  - [x] 4.2 Update next-session handover current posture and PR50 references.
  - [x] 4.3 Update roadmap current posture and PR50 references.
  - [x] 4.4 Update schema doctrine current posture and PR50 references.
  - [x] 4.5 Update product doctrine current posture and PR50 references.
  - [x] 4.6 Update knowledge-matching current-state posture.

- [x] 5.0 Verify and hand off
  - [x] 5.1 Run focused PR50 tests.
  - [x] 5.2 Run affordance/schema compiler regression tests.
  - [x] 5.3 Run packet fixture/render regressions.
  - [x] 5.4 Run source custody / coverage tests.
  - [x] 5.5 Run Decision Pressure trace schema / adapter regressions.
  - [x] 5.6 Run `git diff --check` and cached whitespace checks before commit.
  - [x] 5.7 Run changed-path guardrail checks.
  - [x] 5.8 Open PR and summarize target models, outcomes, counts, tests, and PR51 recommendation.
