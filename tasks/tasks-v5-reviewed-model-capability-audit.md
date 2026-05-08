## Relevant Files

- `research/v5-reviewed-model-capability-audit-2026-05-07.md` - Main PR31 capability audit answering what the 65 reviewed records can and cannot tell us.
- `data/compiled/model_affordances/affordances_v5.json` - Reviewed v5 artifact audited for counts, affordances, absence records, treatment requirements, diagnostic questions, and misuse guards.
- `data/knowledge_graph.json` - Runtime graph used to preserve the 222-breadth / 65-depth distinction.
- `research/reasoning-substrate-next-session-handover-2026-05-06.md` - Updated handover with the PR31 posture and next enrichment direction.
- `plans/knowledge-substrate-roadmap-2026-05-04.md` - Updated roadmap so future work follows capability gaps instead of count momentum.
- `plans/knowledge-use-schema-2026-05-04.md` - Updated schema doctrine with PR31 as capability audit, not extraction.
- `research/decision-pressure-product-doctrine-2026-05-06.md` - Updated doctrine with the answer to what the 65 reviewed records can support.

### Notes

- PR31 is docs/research only.
- No extraction, runtime behavior, prompt changes, lane rewrites, model calls, judges, UI, memo, or user-facing surfaces are part of this slice.
- The audit uses structured compiled artifacts and human/reviewer capability grouping. It does not extract new affordances from source files.

## Instructions for Completing Tasks

**IMPORTANT:** As you complete each task, you must check it off in this markdown file by changing `- [ ]` to `- [x]`. This helps track progress and ensures you don't skip any steps.

Example:
- `- [ ] 1.1 Read file` -> `- [x] 1.1 Read file` (after completing)

Update the file after completing each sub-task, not just after completing an entire parent task.

## Tasks

- [x] 0.0 Create feature branch
  - [x] 0.1 Create and checkout `feature/reasoning-substrate-pr31-v5-capability-audit`
- [x] 1.0 Audit the current v5 reviewed corpus shape
  - [x] 1.1 Count reviewed model records, affordances, absence records, source-evidence references, treatment requirements, diagnostic questions, and misuse guards.
  - [x] 1.2 Confirm runtime breadth remains 222 models and graph-only after v5 remains 157 models.
  - [x] 1.3 Confirm PR31 does not change v5 data or runtime artifacts.
- [x] 2.0 Answer what the 65 reviewed records can tell us
  - [x] 2.1 Identify the core thing being tested: handoff depth for the next LLM, not deterministic pressure selection.
  - [x] 2.2 Group reviewed records into reviewer capability families.
  - [x] 2.3 Name what each capability family can help the next LLM check.
  - [x] 2.4 Record what the 65 reviewed records cannot support yet.
- [x] 3.0 Define what future enrichment should check
  - [x] 3.1 Specify activation, evidence-needed, do-not-use, misuse guard, treatment, absence, and packet-burden checks.
  - [x] 3.2 Preserve absence records as knowledge, not leftovers.
  - [x] 3.3 Recommend a next controlled enrichment batch based on capability gaps, not count completion.
- [x] 4.0 Update durable docs
  - [x] 4.1 Add `research/v5-reviewed-model-capability-audit-2026-05-07.md`.
  - [x] 4.2 Update next-session handover with `v5_capability_audit_complete`.
  - [x] 4.3 Update roadmap/schema/doctrine with the PR31 posture.
- [x] 5.0 Verify and prepare handoff
  - [x] 5.1 Run `git diff --check`.
  - [x] 5.2 Run focused existing rails that protect packet/source/trace infrastructure.
  - [x] 5.3 Confirm no extraction, runtime, prompt, lane, model-call, judge, UI, memo, or user-facing files were modified.
