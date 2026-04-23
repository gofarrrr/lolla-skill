# Phase 2c — Lane 1 (Structural Pressure) migration to ConversationContext

You are a fresh Claude Code session starting the biggest lane migration of Phase 2. Phase 1, 2a, and 2b have all shipped to main. This kickoff is your complete brief.

---

## What you are NOT doing tonight

You are NOT executing the migration. You are planning it. PM (Marcin) reviews the plan in the morning before execution begins. A flawed plan on the biggest-and-most-coupled lane costs far more to fix mid-execution than mid-planning. **STOP after you've produced the plan doc + task file + summary report.**

---

## Preflight (mandatory, no shortcuts)

Read in this order, in full:

1. `research/conversation-first-rearchitecture-handover.md` — strategic context, constraints, measurement protocol
2. `research/phase2-lane-migration-plan.md` — quality protocol for all lane migrations
3. `gh pr view 15` — Phase 2a (Lane 3) PR description, the template
4. `gh pr view 16` — Phase 2b (Lane 4) PR description, includes the iteration-as-durable-lesson callout
5. `research/test-cases/phase2a-marcus-controlled-comparison-2026-04-23/README.md` — CONTEXT/SOURCE pattern
6. `tasks/tasks-conversation-first-phase-2b-lane4-structural-coverage.md` — task-file structure template
7. `research/test-cases/phase2b-lane4-equivalence-2026-04-23/` — what "success at the measurement layer" looks like post-iteration
8. `engine/system_b/structural_pressure.py` (or whatever Lane 1 module is called — could be multiple files; start with `engine/system_b/` directory listing)

Then check state:

```
git status                               # should be clean
git log --oneline main -5                # confirm 2a (#15) and 2b (#16) merges present
git checkout main && git pull
git checkout -b feat/conversation-first-phase-2c-lane1-structural-pressure
```

---

## Durable lessons from 2a and 2b to carry into 2c

1. **CONTEXT/SOURCE split with RIGHT/WRONG examples.** CONTEXT = extractor summaries (NOT citable as evidence). SOURCE = raw turns verbatim. For Lane 1, read the module carefully to decide which turns belong in SOURCE — user turns, assistant turns, or both. The choice depends on what Lane 1 audits.

2. **Dimension/enum-checklist reminder (2b iteration lesson).** Initial new-path prompts under-flag abstract structural concepts because LLMs bias toward what surfaces verbatim in user turns. If Lane 1 has any enumerated concept space (tendency types, pressure types, 222 models, etc.), the system prompt MUST explicitly remind the LLM to check ALL of them, including ones that are abstract/implicit rather than surfacing in literal text. Bake this into the first draft of the prompt — do not wait for measurement to force the iteration.

3. **Three-angle evidence structure (required):**
   - Controlled Marcus A/B — same conversation, same fresh extraction, only input shape differs — PRIMARY evidence
   - 10-case aggregate, N=3 per path per case — CORPUS evidence
   - Ablation on one case (SOURCE vs CONTEXT-trimmed) — ARCHITECTURAL ISOLATION

4. **Full re-measurement after any prompt iteration.** Do not ship on 2-case verification of an iteration. Full 10-case re-measurement confirms the fix holds corpus-wide.

5. **Qualitative human read (Task 7.0) is mandatory, not `[~]`.** 2b marked this partial; don't repeat that. Render a side-by-side diff markdown file for ≥3 cases, surface to PM.

6. **Write honestly; lead with cleanest evidence.** Usually the Marcus A/B is cleanest (isolated variable). Aggregate is supporting. Document any iteration cycle as a durable lesson for Phase 2d.

---

## Your deliverables tonight

### 1. `research/phase2c-lane1-migration-plan.md`

Adapt from `research/phase2-lane-migration-plan.md`. Phase 2c specifics:

- What Lane 1 does (Structural Pressure — read structural_pressure.py to characterize)
- What it currently consumes (the CritiqueRequest shape it reads from)
- What input shape it needs post-migration (user turns? assistant turns? both? extraction fields still?)
- Any couplings to other lanes (Lane 1 is reportedly the most coupled — document what exactly)
- Measurement plan (same three-angle structure as 2a/2b)
- Risks specific to Lane 1 (flag anything you discover that makes 2c harder than 2b)

### 2. `tasks/tasks-conversation-first-phase-2c-lane1-structural-pressure.md`

Adapt from `tasks/tasks-conversation-first-phase-2b-lane4-structural-coverage.md`. Required task blocks:

- 0.0 Preflight
- 1.0 Conversation-aware entry points (TDD)
- 2.0 Prompts with CONTEXT/SOURCE + RIGHT/WRONG + enum-checklist reminder (durable lesson from 2b — in the FIRST DRAFT, not an iteration)
- 3.0 `pipeline.py` dispatch wiring
- 4.0 Anti-echo preservation (if Lane 1 uses anti-echo)
- 5.0 Quality-metrics script (`scripts/phase2c_lane1_quality_check.py`)
- 6.0 Full N=3 × 10-case measurement + Controlled Marcus A/B + Ablation
- 7.0 Qualitative human read (proper markdown diff, not `[~]`)
- 8.0 Negative-check gate
- 9.0 Documentation (`HOW_IT_WORKS.md` §Step 3 Lane 1)
- 10.0 Ship decision + post-merge handover update

### 3. Summary report for PM review

Write this as the last thing before you stop. Include:

- One-paragraph characterization of Lane 1 based on your reading
- Input shape decision (what goes in SOURCE, what goes in CONTEXT) with rationale
- Anything surprising you found in structural_pressure.py
- Whether the 2b template transfers cleanly or needs structural changes
- Risks you'd want PM to weigh before approving execution

---

## Stop condition

When the plan doc + task file are committed to the branch and you have written the summary report, STOP. Do not proceed to execution. PM reviews in the morning.

If mid-planning you discover that Lane 1 has fundamentally different architectural characteristics than 2a/2b (e.g., multiple modules, cross-lane dependencies that break the migration pattern), STOP EARLIER and flag it in the summary. Don't force a plan that doesn't fit.

---

## Constraints

- Synthetic test data only (same 10-case corpus as 2a/2b).
- No API keys in any committed file.
- No code tonight. Plan + task file only.
- Commit the plan doc + task file + any planning-only changes to the branch; don't push yet.
- Do not skip preflight reading.

---

## When PM wakes up

PM reads your summary → reviews plan doc + task file → either approves execution or asks for revisions. Your next session continues from there.
