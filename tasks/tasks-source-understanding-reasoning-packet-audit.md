# Source Understanding And Reasoning Packet Audit

## Relevant Files

- `research/source-understanding-and-reasoning-packet-audit-brief-2026-05-06.md` - Current brief defining the next slice, boundaries, substrate facts, packet strategy, and expansion doctrine.
- `research/source-understanding-and-reasoning-packet-audit-2026-05-06.md` - New audit artifact to create with all-222 runtime graph inventory, v4 coverage, and expansion implications.
- `research/reasoning-substrate-packet-v1-spec-2026-05-06.md` - New dormant packet spec describing the enriched model-card packet shape.
- `research/enriched-mental-model-packet-strategy-2026-05-06.md` - Current architecture simplification note: pull shelves, enrich cards, let the LLM reason.
- `research/knowledge-matching-current-state-audit-2026-05-06.md` - Current audit of runtime graph, v4 affordance substrate, lanes, and deterministic/LLM boundary.
- `research/decision-pressure-product-doctrine-2026-05-06.md` - Product doctrine that must remain consistent with the packet strategy.
- `plans/knowledge-substrate-roadmap-2026-05-04.md` - Living roadmap to update only if the audit/spec changes the next-step posture.
- `plans/knowledge-use-schema-2026-05-04.md` - Living schema doctrine to update only if the audit/spec clarifies the knowledge-use shape.
- `data/knowledge_graph.json` - Runtime graph with 222 model records and broad graph fields.
- `data/compiled/model_affordances/affordances_v4.json` - Dormant v4 reviewed affordance corpus with 55 model records.
- `data/model_sources/manifest.json` - Source custody manifest for the 55 reviewed v4 source files.
- `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216/*.md` - Canonical markdown source files for the full 222-model source corpus.
- `engine/system_b/pipeline.py` - Existing lane orchestration and embedding tendency recall; read only unless a later approved implementation slice changes packet production.
- `engine/system_b/companion_routing.py` - Lane 2 assistant-attribution logic; read only for this audit.
- `engine/system_b/frame_pressure.py` - Lane 3 user-framing logic; read only for this audit.
- `engine/system_b/structural_coverage.py` - Lane 4 structural gap logic; read only for this audit.

### Notes

- This is a docs/research and optional fixture-only slice.
- Do not change runtime behavior.
- Do not change prompts.
- Do not build a Decision Pressure producer.
- Do not expand v4 records in this slice.
- Do not run paid model calls or judges.
- If a helper script is created for deterministic inventory, keep it local to this slice and test only mechanical counts/shape.

## Instructions for Completing Tasks

**IMPORTANT:** As you complete each task, you must check it off in this markdown file by changing `- [ ]` to `- [x]`. This helps track progress and ensures you don't skip any steps.

Example:
- `- [ ] 1.1 Read file` -> `- [x] 1.1 Read file` (after completing)

Update the file after completing each sub-task, not just after completing an entire parent task.

## Tasks

- [x] 0.0 Create feature branch
  - [x] 0.1 Create and checkout a new branch for this slice from the current root base, e.g. `git checkout -b feature/reasoning-substrate-pr24-source-packet-audit`.
  - [x] 0.2 Confirm branch base includes the merged PR13-PR23 stack and the May 6 doctrine docs.
  - [x] 0.3 Confirm the working tree has no tracked changes unrelated to this slice; leave unrelated untracked workspace noise alone.

- [x] 1.0 Re-ground on the current architecture boundary
  - [x] 1.1 Read `research/enriched-mental-model-packet-strategy-2026-05-06.md`.
  - [x] 1.2 Read `research/knowledge-matching-current-state-audit-2026-05-06.md`.
  - [x] 1.3 Read `research/decision-pressure-product-doctrine-2026-05-06.md`.
  - [x] 1.4 Record the doctrine in the audit: broad intake, disciplined output; pull shelves, enrich cards, let the LLM reason; Python guards rails and does not decide wisdom.
  - [x] 1.5 List non-goals explicitly: no runtime, no prompt changes, no lane rewrites, no Decision Pressure producer, no extraction, no user-facing output.

- [x] 2.0 Inventory the all-222 runtime graph
  - [x] 2.1 Parse `data/knowledge_graph.json` and count runtime models, tendencies, and key graph fields.
  - [x] 2.2 Report field coverage across all 222 models: `select_when`, `danger_when`, `failure_modes`, `premortem_questions`, `heuristics`, and `reasoning_types`.
  - [x] 2.3 Report reasoning-type distribution and v4 coverage by reasoning type.
  - [x] 2.4 Identify graph-only models after v4 and list representative high-signal examples.
  - [x] 2.5 Note that graph-only means broad runtime card, not source-reviewed v4 affordance.

- [x] 3.0 Audit canonical markdown source shape
  - [x] 3.1 Enumerate canonical markdown files under `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216/`.
  - [x] 3.2 Report file count, approximate word count, median/mean file size, and common section presence.
  - [x] 3.3 Confirm whether the files consistently contain source material suitable for operational extraction: strengths, weaknesses, anti-patterns, risks, mitigations, tensions, and premortem questions.
  - [x] 3.4 Identify whether the canonical files likely support broad expansion beyond 55 without requiring blind extraction.

- [x] 4.0 Compare v4 depth against runtime graph breadth
  - [x] 4.1 Parse `data/compiled/model_affordances/affordances_v4.json`.
  - [x] 4.2 Confirm v4 remains `draft_review_only`.
  - [x] 4.3 Count v4 model records, affordances, absence records, and source files.
  - [x] 4.4 Compare the 55 v4 model IDs against the 222 runtime model IDs and confirm there are no v4 IDs outside the graph.
  - [x] 4.5 For a small representative sample, compare runtime fields against v4 fields:
    - `select_when` vs `activation_shape.use_when`
    - `danger_when` vs `do_not_use_when` / `misuse_guards`
    - `premortem_questions` vs `diagnostic_questions`
    - `heuristics` vs `treatment_requirements`
  - [x] 4.6 Record what v4 adds that the runtime graph does not: source evidence, absence records, evidence requirements, do-not-use conditions, misuse guards, and treatment requirements.

- [x] 5.0 Define `reasoning_substrate_packet.v1`
  - [x] 5.1 Create `research/reasoning-substrate-packet-v1-spec-2026-05-06.md`.
  - [x] 5.2 Define top-level packet fields: version, runtime policy, transaction context, candidate cards, suppressed candidates, coverage summary, packet policy, blocked surfaces.
  - [x] 5.3 Define candidate-card fields: model identity, pulled_by, why_pulled, evidence source type, coverage status, graph fields, v4 fields, absence records, do_not_overclaim, and LLM instruction.
  - [x] 5.4 Define coverage statuses:
    - `v4_reviewed_affordance_available`
    - `graph_only_runtime_card`
    - `absence_only`
    - `missing_reviewed_record`
    - `source_too_thin`
    - `conflicting_or_weak_support`
  - [x] 5.5 Define caps: target 5-12 candidate cards and 1-3 high-value snippets per card.
  - [x] 5.6 Explicitly forbid final pressure selection, user-facing prose, semantic ranking by Python, and case-type templates.

- [x] 6.0 Produce the source-understanding and packet audit artifact
  - [x] 6.1 Create `research/source-understanding-and-reasoning-packet-audit-2026-05-06.md`.
  - [x] 6.2 Summarize the current state: 222 breadth, 55 v4 depth, 167 graph-only models, and why both matter.
  - [x] 6.3 Explain how the packet fits the existing lane system without disturbing it.
  - [x] 6.4 Explain how v4 should be additive to lane-selected candidates.
  - [x] 6.5 Define expansion beyond 55 as pressure-family and packet-usefulness driven, not count-driven.
  - [x] 6.6 Include risks and falsifiers: packet bloat, v4 swallowing breadth, graph-only pretending to be reviewed, deterministic pressure selection, and blind extraction.

- [x] 7.0 Optional sample packet sketch
  - [x] 7.1 Decide whether a tiny static sample packet is useful in this slice.
  - [x] 7.2 No separate sample fixture created; the spec includes non-normative card fragments instead.
  - [x] 7.3 Confirm the illustrative fragments contain no final pressure selection and no user-facing prose.
  - [x] 7.4 Ensure graph-only and v4-reviewed illustrative fragments are visibly different.
  - [x] 7.5 If no sample is created, document why the spec/audit is sufficient for this slice.

- [x] 8.0 Update living docs narrowly
  - [x] 8.1 Update `plans/knowledge-substrate-roadmap-2026-05-04.md` only if the audit/spec changes the next-step posture.
  - [x] 8.2 Update `plans/knowledge-use-schema-2026-05-04.md` only if the packet spec clarifies the knowledge-use schema.
  - [x] 8.3 Preserve the post-PR23 boundary: no runtime, no prompt changes, no lane rewrites, no user-facing promotion.

- [x] 9.0 Verify and hand off
  - [x] 9.1 Run `git diff --check`.
  - [x] 9.2 No helper script or fixture validator was added, so focused code tests were not needed.
  - [x] 9.3 Docs-only slice; no tests were needed.
  - [x] 9.4 Summarize findings, files changed, and remaining decisions.
  - [x] 9.5 Confirm no paid model calls, judge calls, runtime changes, prompt changes, extraction, Batch 3b, or user-facing output were done.
  - [x] 9.6 Add `research/reasoning-substrate-next-session-handover-2026-05-06.md` so a fresh session starts from the current architecture and reviews PR24 before selecting any next slice.
  - [x] 9.7 Fold PR24 review memo drift fixes into the docs and record `stop_and_consolidate_after_pr24_review` as the active posture.
