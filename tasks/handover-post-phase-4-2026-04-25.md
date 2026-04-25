# Handover — post-Phase-4

**Date:** 2026-04-25
**Audience:** the coder picking up after Phase 4 merged.
**Status of main:** all 383 tests green at commit `0457060` (PR #29 merge).

## Where we are

The conversation-first rearchitecture is largely complete. The `ConversationIR` is provenance-bearing across all four extraction fields, three LLM-backed specialists are wired (live_constraints, dropped_threads, stance), and all four lanes consume the IR via `Lane4Packet` projection.

Remaining work is **cleanup + structural** — no more new features needed for the architecture itself. Three meaningful phases left, plus one optional cleanup.

## What's left

| Phase | What | Risk | Time |
|---|---|---|---|
| **4d** | Remove legacy `_from_context` paths (now redundant since IR-driven path is wired) | Low | ~2h |
| **6** | Remove `CritiqueRequest` shim (the legacy data contract) | Medium-high | ~4-6h |
| **7** | Split `pipeline.py` (2200 lines into cohesive modules) | Medium | ~4-6h |
| **8** | Operational: token/cost tracking + real-conversation corpus | Medium | open-ended |

Suggested order: **4d → 7 → 6 → 8**. 4d is the warmup. 7 (split pipeline) makes 6 easier because the legacy CritiqueRequest path becomes more isolated. 8 is mostly independent.

## How to work safely (the TDD recipe used through Phase 5 and Phase 4)

This pattern caught two real bugs during Phase 4c. Use it for every task.

### For every code change

1. **RED**: write the test first. It must fail before you implement. If it doesn't fail, the test isn't testing what you think.
2. **GREEN**: write the smallest code that makes the test pass.
3. **VERIFY**: `python3 -m pytest tests -q` — full suite must stay at the current green count or higher. If it drops, you broke something. Revert and try again.
4. **REFACTOR** (optional): clean up after the slice is green. If you refactor, run the full suite again.

### For every removal

1. **VERIFY current state**: full suite must be green BEFORE you remove anything.
2. **RED-by-removal**: delete the symbol/file. Run full suite. Failures show what depended on it.
3. **GREEN by migration**: for each failure, either migrate the caller OR re-add the symbol if removal isn't ready yet.
4. **VERIFY**: full suite green again.

### Never do

- **Skip running tests** after a change. Even "obvious" refactors break things.
- **Use --no-verify** on commits. Hooks are there for a reason.
- **Force-push to main.** All work goes through PRs. Branches: `feat/<phase>-<short-description>`.
- **Touch user-owned files**: `research/conversation-first-extraction-evaluation-2026-04-24.md` is theirs; leave alone.
- **Bundle multiple phases in one PR.** One phase per PR makes review tractable.

### What to ask Marcin (PM) about

- If a test fixture needs changing in a way that affects more than one test file → confirm first.
- If you find a bug that's not in scope but is real → flag it; don't silently fix.
- If you find a piece of behavior that seems wrong → confirm before "fixing" it. The Phase 5.5 "kind drift" was an example: documented as a known difference, not a bug.
- If the "obvious right move" requires changing the Phase 1 IR schema (UserIssueEvent, FrameAnchor, StanceEvent, Provenance) → STOP. The IR is the substrate; schema changes need explicit PM approval.

## Per-phase task files

Each phase has its own task file with TDD-sliced tasks. The coder is stateless — each task file is self-contained (you don't need to remember other phases' details).

- **Phase 4d** (cleanup, optional warmup): `tasks/tasks-phase-4d-cleanup-legacy-from-context.md`
- **Phase 6** (legacy CritiqueRequest removal): `tasks/tasks-phase-6-remove-critiquerequest-shim.md`
- **Phase 7** (split pipeline.py): `tasks/tasks-phase-7-split-pipeline.md`
- **Phase 8** (operational corpus + telemetry): `tasks/tasks-phase-8-operational-corpus.md`

## Repo conventions to follow

- Branch name: `feat/<phase>-<short-description>`
- Commit messages: imperative present tense ("add", "remove", "split"); reference phase in subject; explain "why" in body
- PR description: Summary + Test plan + Out-of-scope (use the existing PR template style)
- Co-author trailer: `Co-Authored-By: <model name> <noreply@anthropic.com>`
- For commits via Bash heredoc: see `git log` for examples (recent commits all use this pattern)

## Where the architecture documentation lives

- `HOW_IT_WORKS.md` — high-level architecture summary
- `engine/system_b/ir.py` — IR schema (do NOT change without PM approval)
- `engine/system_b/ir_constructor.py` — how IR is built from ConversationContext
- `engine/system_b/packet_builders/lane4.py` — packet projection for lane consumption
- `research/phase*.md` — historical gates and acceptance memos (read for context, do not modify)

## Final note

The architecture is sound. The remaining phases are cleanup and operational maturity, not new design. Keep the TDD discipline, run the full suite often, and ship one phase at a time. If you finish 4d, 6, 7, 8 — the project is structurally complete.
