# Phase 2: Lane-by-lane migration plan

**Authored:** 2026-04-24
**Status:** plan for review; execution not started
**Prior phase:** Phase 1 (PR #14) merged 2026-04-24 — `ConversationContext` + loader + shim in `SystemBPipeline.run()` landed on main.
**Prerequisite reading:** `research/conversation-first-rearchitecture-handover.md` §"The plan" and §"Legacy to remove"; `research/full-system-audit-2026-04-23.md` §3 (lanes).

## Purpose

Phase 1 introduced `ConversationContext` alongside `CritiqueRequest`. Lanes still consume the legacy shape via the shim. Phase 2 migrates each of the four lanes one at a time to consume `ConversationContext` directly, eliminating information loss at the lane boundary.

After Phase 2 completes, Phase 3 removes `CritiqueRequest` + `_context_to_critique` entirely.

## Four PRs at a glance

| PR | Lane | Why this order | Estimated size |
|---|---|---|---|
| **2a** | Lane 3 — Frame Pressure | Smallest, most self-contained. Has the clearest current defect (noisy `original_framing` when first user turn is a context-dump). Lowest-blast-radius first migration — proves the pattern. | S |
| 2b | Lane 4 — Structural Coverage | Also self-contained, informative-only (doesn't feed other lanes). Safe second step. | M |
| 2c | Lane 1 — Structural Pressure | Biggest. Pass 1 (6 clusters) + Pass 2 (per-tendency) both need rewiring. Highest complexity; migrate after two smaller lanes have de-risked the pattern. | L |
| 2d | Lane 2 — Companion | Last. Currently does its own fingerprint extraction from `vanilla_answer`; may need least change or a ground-up rewrite. Sequencing last because the anti-echo interaction with already-migrated lanes is cleanest to reason about once 1/3/4 are settled. | M-L |

**Dependencies between PRs:** none hard. Each lane is independently migratable because `pipeline.py::run()` calls each lane method as a separate step; as long as the `ConversationContext` is threaded into the specific method being migrated, the other lanes keep working via the shim. Recommended order is about risk + learning, not technical necessity.

## What each migration changes (scope template)

Every Phase 2 PR has the same shape:

1. **Additive in the lane module.** Add new conversation-aware entry points (e.g. `run_frame_extraction_from_context`) alongside the existing `run_frame_extraction(query, vanilla_answer)`. Don't delete the legacy function — it still serves the shim path until Phase 3.
2. **Prompt rewrite** to consume the richer context. Turn-by-turn conversation, typed extraction fields (constraints with turn metadata, dropped threads, etc.) instead of the collapsed query.
3. **Small pipeline.py change**: thread the optional `ConversationContext` from `SystemBPipeline.run()` into the lane method; the lane method dispatches between legacy and new paths based on whether a context is available.
4. **Measurement**: run the quality-comparison protocol (below) on the 10-case corpus. Gate the ship decision on the result.
5. **Docs**: update `HOW_IT_WORKS.md §Step 3` to note the lane is now conversation-first; update the handover's "What's shipped" on merge.

## Quality-comparison protocol — new design work

Phase 1's "bit-identical" gate doesn't apply to Phase 2 — by design, lane output changes because the point of migration is better output. The pipeline also uses `temperature=0.2`, so same-path runs aren't bit-identical either. We need a different gate.

### Four signals

Each Phase 2 PR runs all four on the 10-case corpus before shipping.

**Signal 1 — Structural metrics.** Counts and distributions that don't depend on exact text. Lane-specific; example for Lane 3:

- `frame_elements_count`: 0-5 integer
- `frame_elements_type_distribution`: count by `element_type`
- `dropped_frame_elements_count`: count of LLM outputs that failed validation (**lower is better** — indicates the LLM had more stable evidence to ground against)
- `reframings_count`: 0-2
- `reframings_move_type_distribution`: count by `reframe_move_type`

Per-path mean + std-dev across 3 runs. Report per-case + aggregate.

**Signal 2 — Multi-sample runs (N=3).** Per case, run each path 3 times. Gives us a variance estimate per path so we know whether a difference between old-path and new-path is larger than same-path noise.

Cost: 10 cases × 2 paths × 3 runs × ~$0.05-0.15/run ≈ **$3-9 per Phase 2 PR**. Expensive but finite.

**Signal 3 — Qualitative human read.** For 3 cases chosen to stress variance, a human (Marcin) reads both old-path and new-path outputs side-by-side and calls whether new-path is ≥ old-path quality. Proposed 3 cases:

- **Messy:** `messy_three_problems` (11 turns, topic-jumping, multi-domain) — tests whether the new path's access to the actual first user turn cleans up noisy framing.
- **Clean:** `startup_pivot` (7 turns, clean business decision) — tests that the new path doesn't over-produce on already-clean framings.
- **Edge-case:** `phd_research` (22 turns, longest) — tests handling of long conversations.

**Signal 4 — Negative check.** A hard blocker that trips on obviously-worse output. Operational definition:

- Non-empty lane card on old path → empty lane card on new path, OR
- Hallucinated evidence (evidence_quote fails `literal substring` check on any user turn), OR
- `dropped_frame_elements_rate` > 50% on any case when old-path drop rate was < 20% on the same case.

Any of these on any case = **STOP, diagnose, do not ship**.

### Thresholds for PR 2a (Lane 3) — approved policy

| Axis | Target | Rationale |
|---|---|---|
| Aggregate `dropped_frame_elements_rate` | new-path ≤ old-path **within 5% tolerance band** | Drop rate is a guard against catastrophic failure, not an improvement target. The migration's real wins show up in qualitative read + `frame_elements_count` stability; drop rate just can't collapse. |
| `frame_elements_count` per case | within ±2 of old-path median across 3 samples | Stability check — we don't want the new path to suddenly produce many more or fewer elements |
| Qualitative human read | ≥ 2 of 3 cases rated "new ≥ old" | Majority bar on human judgment |
| Negative check | zero trips on any case | Hard blocker |

**Partial-regression policy (net-positive with mandatory diagnosis):**

If any case regresses on any metric, the PR description MUST name a specific hypothesis for why that case regressed. No "within noise" hand-waving — each regression gets a named tradeoff. Two or more undiagnosed regressions = block. Diagnosed regressions with a stated tradeoff = ship. Reasoning: Lane 3 migration will expose something real about how the lane reacts to richer inputs; regressions are information, not just failure. Ship with honesty, not stasis.

**Operational protocol (approved):**
- Sample size **N=3** per path per case (cost ~$3-9 per PR is noise-level; weaker statistics aren't worth cutting).
- Qualitative cases: `messy_three_problems` (multi-thread frame drift), `startup_pivot` (clean baseline), `phd_research` (long-evolved framing).
- Negative-check criteria: (a) non-empty card on old → empty card on new; (b) hallucinated evidence (fails literal-substring check against user turns); (c) `dropped_frame_elements_rate` > 50% on any case where old was < 20%.

## Rollback posture

Every Phase 2 PR is independently revertible because:

- Lane modules keep the legacy functions alongside the new ones.
- `pipeline.py::run()` dispatches between paths based on whether it has a `ConversationContext` — without the context, everything goes through the shim → legacy path, unchanged.
- Each PR merges as its own commit-range; reverting reverts the one lane.

If a deployed Phase 2 PR shows a problem in production, the revert path is:

```
git revert <merge-commit-of-PR-2x>
```

Pipeline falls back to Phase 1 state. All existing lanes keep working.

## Out of scope for Phase 2

- **Not** removing `CritiqueRequest`, `_context_to_critique`, or the shim — those go in Phase 3.
- **Not** restructuring `pipeline.py` (the 2200-line monolith) — Phase 4.
- **Not** changing extraction (`scripts/run_extract.py`) — Phase 2 migrations use existing extraction output, just pass it to lanes in the richer shape.
- **Not** Track A (specialist extraction calls). If a lane migration discovers it needs a field current extraction doesn't emit, we flag it and decide per-field; preemptive Track A stays frozen.
- **Not** changing `SKILL.md` — Claude's orchestration is unaffected.

## After all 4 PRs ship

- Phase 3: remove `CritiqueRequest` + `_context_to_critique` + shim dispatch. Small PR.
- Phase 4: split `pipeline.py` into orchestration + per-lane modules. By then the lane migrations will have shown which parts of the 2200-line file are essential vs vestigial.
- Handover doc gets its final "What's shipped" update declaring the rearchitecture complete.
