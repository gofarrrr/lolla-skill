# V10 Graph-Only Priority Audit

## Relevant Files

- `research/reasoning-substrate-v10-packet-usefulness-review-2026-05-07.md` - PR43 proof that v10 risk/reversibility cards improved one stable-nomination packet.
- `research/pr42-controlled-risk-reversibility-enrichment-report-2026-05-07.md` - PR42 extraction report and v10 corpus shape.
- `research/v10-graph-only-priority-audit-2026-05-07.md` - PR44 graph-only priority audit.
- `data/knowledge_graph.json` - 222-model runtime graph used for breadth and graph-only gap counts.
- `data/compiled/model_affordances/affordances_v10.json` - Draft/review-only reviewed corpus after PR42.
- `data/model_sources/manifest.json` - Repo-local source custody manifest.
- `data/curated/compiled_chunks.json` - Static Lane 1 chunk signal source.
- `research/reasoning-substrate-next-session-handover-2026-05-06.md` - Handover update for PR44.
- `plans/knowledge-substrate-roadmap-2026-05-04.md` - Roadmap update for PR44.
- `plans/knowledge-use-schema-2026-05-04.md` - Schema doctrine update for PR44.
- `research/decision-pressure-product-doctrine-2026-05-06.md` - Product doctrine update for PR44.
- `research/knowledge-matching-current-state-audit-2026-05-06.md` - Current-state posture update after PR44.

## Guardrails

- PR44 is a docs/research priority audit, not extraction.
- Do not edit affordance records.
- Do not compile v11.
- Do not parse source files into records.
- Do not run model calls or judges.
- Do not change prompts, lanes, `/lolla`, Observatory, memo, Step 8, Step 6, Lane 4 runtime, or user-facing output.
- Do not make Python choose final pressure or final reasoning mode.
- Family labels in the audit are reviewer planning groups, not runtime classes.

## Instructions For Completing Tasks

Change `- [ ]` to `- [x]` as each sub-task is completed.

## Tasks

- [x] 1.0 Branch setup and grounding
  - [x] 1.1 Start from `feature/knowledge-substrate-pr11-gate4-edge-probes` after PR43 merge.
  - [x] 1.2 Create `feature/reasoning-substrate-pr44-v10-graph-only-priority-audit`.
  - [x] 1.3 Read PR38/PR41 priority audit patterns and PR43 handoff.

- [x] 2.0 Audit remaining graph-only substrate
  - [x] 2.1 Confirm runtime graph count is 222.
  - [x] 2.2 Confirm v10 reviewed record count is 122.
  - [x] 2.3 Confirm graph-only runtime model count after v10 is 100.
  - [x] 2.4 Compute reasoning-type gaps after v10.
  - [x] 2.5 Compute static lane-signal priorities after v10.
  - [x] 2.6 Compare candidate families against packet-usefulness criteria.

- [x] 3.0 Write PR44 audit
  - [x] 3.1 Add `research/v10-graph-only-priority-audit-2026-05-07.md`.
  - [x] 3.2 Record corpus state, reasoning-type gaps, and static lane-signal read.
  - [x] 3.3 Name candidate families and reasons to defer.
  - [x] 3.4 Recommend one capped next family and target set.
  - [x] 3.5 Record extraction standards, failure modes, and required PR46 usefulness proof.

- [x] 4.0 Update living docs narrowly
  - [x] 4.1 Update the roadmap current posture and PR44 references.
  - [x] 4.2 Update the schema doctrine current posture and PR44 references.
  - [x] 4.3 Update the product doctrine current posture and PR44 references.
  - [x] 4.4 Update the knowledge-matching current-state audit posture.
  - [x] 4.5 Update the next-session handover current posture, read list, and kickoff prompt.

- [x] 5.0 Verify and hand off
  - [x] 5.1 Run focused coverage/packet tests.
  - [x] 5.2 Run `git diff --check`.
  - [x] 5.3 Run changed-path guardrail checks.
  - [x] 5.4 Run drift scan over PR44/PR45/PR46/posture language.
  - [x] 5.5 Open PR and summarize audit result, recommended PR45 family, guardrails, and tests.
