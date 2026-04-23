# Kickoff prompt for next session

Drop the text below into a fresh Claude Code session (on the `lolla-skill` repo). It orients the session, points to the handover, and makes the first action clear.

---

## PROMPT TO PASTE

You're picking up the `lolla-skill` conversation-first rearchitecture work. Prior session ended 2026-04-23 with a full audit, 10-case test corpus, and strategic plan written down.

**Before doing anything, read these four documents in order:**

1. `research/conversation-first-rearchitecture-handover.md` — the full handover, including strategic context, plan phases, constraints, and measurement approach.
2. `research/full-system-audit-2026-04-23.md` — architectural audit of the whole system. Pay special attention to §2 (9-step pipeline), §3 (the 4 lanes), §7 (design decisions), §10 (recent changes in PR #13), and §12 (open strategic questions).
3. `research/pipeline-py-structural-map.md` — navigation guide for the 2200-line `engine/system_b/pipeline.py`. Identifies load-bearing vs extractable code, the shim injection points, and the `run()` method's state machine. Read this before touching pipeline.py.
4. `tasks/tasks-conversation-first-phase-1-contract.md` — the executable Phase 1 plan with sub-tasks.

**Then check the current state of the world:**
- `git status` — current branch
- `gh pr list` — is PR #13 still open or has it merged?
- `ls research/test-cases/` — the 10-case corpus should be present
- `git log --oneline -20` — last commits

**Preflight rules (non-negotiable):**
- If PR #13 is open: DO NOT start Phase 1 yet. Recommend merging PR #13 first. The handover explains why.
- If PR #13 is merged and you're on main: proceed to Phase 1 task 0.0.
- If you're on another branch: determine what's going on before acting.

**Absolute don't-list** (read full handover for rationale):
- Don't stack on PR #13 — merge first, then start Phase 1 from fresh main
- Don't do Track A (specialist extraction calls) preemptively — only if a specific lane reveals need
- Don't break the current `/lolla` skill during migration — shim preserves old path
- Don't rewrite `pipeline.py` (2200 lines) first — that's Phase 4, after lane migrations
- Don't ship without outcome measurement comparing old-path vs new-path

**What the user wants at the end:**
A conversation-first system that (a) doesn't collapse rich extraction into `query + vanilla_answer`, (b) is measurable via the 10-case corpus, (c) still runs as the `/lolla` skill, (d) has a cleaner codebase than the current 2200-line monolith.

**First concrete action after reading the three docs:**
Either (a) recommend merging PR #13 and stop, or (b) if PR #13 is merged, start the preflight sub-tasks in the Phase 1 task file.

Prior session handed you comprehensive documentation on purpose. Read it. Don't rediscover context that's already been written down.

---

## Length + shape rationale

Short intentionally. Gets the session oriented in a minute, then points to the handover for depth. Don't expand this unless the handover meaningfully changes.
