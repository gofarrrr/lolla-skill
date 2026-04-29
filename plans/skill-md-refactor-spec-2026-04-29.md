# SKILL.md Progressive-Disclosure Refactor — Spec & Test Contract

**Date:** 2026-04-29
**Branch:** `chore/skill-md-progressive-disclosure`
**Baseline SKILL.md:** commit `62e3eca` (812 lines)
**Status:** local-only; do not push or merge until comparison passes

---

## Why now

SKILL.md grew from operational orchestration into a hybrid carrying (a) orchestration, (b) voice/quality doctrine, (c) chat render spec, (d) field reference duplicating `references/output-field-guide.md`, and (e) ~108 lines of static sub-agent prompt templates. At 812 lines it diverges from the exemplar pattern in best-practices research (`last30days-skill`, `gstack`, Anthropic `skill-creator`): SKILL.md should describe *phases and invariants*; references and scripts carry the rest.

The strategic motivation is **stability before further engine work**. Performance/triggering improvements on the deterministic engine will pressure SKILL.md unless its shape is locked to orchestration only. Doctrine, render rules, and templates that need to evolve as the engine evolves should live in references that load on demand — so engine changes pressure references, not SKILL.md.

---

## Best practices being applied

From the research:

1. **Progressive disclosure** — *"When SKILL.md becomes too long, move specialized or rarely used sections into separate files."* (Anthropic best-practices docs)
2. **Markdown defines behavior; scripts/references implement mechanics** — orchestration in SKILL.md, doctrine and render specs in references.
3. **Single source of truth** — eliminate duplications. If `output-field-guide.md` documents Card fields, SKILL.md does not also document them.
4. **Discoverability via pushy descriptions** — keep the existing trigger-rich frontmatter (already strong).
5. **Stable-API scripts** — keep existing CLI contracts (`run_extract.py`, `run_pipeline.py`, `render_memo.py`, `archive_run.py`) unchanged.

---

## Scope

In scope: SKILL.md, `references/` (new files added; existing files left alone unless de-duplication requires).
Out of scope: `HOW_IT_WORKS.md` (943 lines, user-facing), engine code (`engine/system_b/*`), scripts (`scripts/*`), Observatory.

---

## What stays in SKILL.md

Pure operational orchestration. Each step retains: bash to run, what files to read, what artifacts get produced, branching on result codes. Doctrine and render details are replaced with one-line "load this reference now" triggers.

| Section | Lines (current) | Lines (target) | Change |
|---------|-----------------|----------------|--------|
| Frontmatter | 1–18 | unchanged | Keep |
| Header + 4-lane summary | 20–28 | unchanged | Keep |
| Model Requirements (block 1) + Self-check (block 2) | 32–38, 108–115 | merged → one block (~18 lines) | Collapse |
| Preamble bash | 40–105 | unchanged | Keep |
| Step 1 capture | 123–156 | unchanged | Keep |
| Step 2 extract | 158–174 | unchanged | Keep |
| Step 3 run pipeline | 176–185 | unchanged | Keep |
| Step 4 present results | 187–306 (~120) | ~30 lines | Slim: "load `chat-output-format.md`, present per format" |
| Step 5 placeholder | 308–310 | unchanged | Keep |
| Quality Doctrine inline | 314–325 | **0** | Delete (lives in `anti-bullshit-doctrine.md` + `presentation-voice.md`) |
| Step 6 update position | 326–409 (~84) | ~30 lines | Slim: "load `presentation-voice.md`, `anti-bullshit-doctrine.md`, `anchor-treatment.md`; follow §1/§2/§3; anchor-naming invariant" |
| Step 6b persist | 411–435 | unchanged | Keep bash |
| Step 6c memo | 439–447 | unchanged | Keep |
| Step 7 sub-agents | 449–479 (~31) | ~20 lines | Slim: "spawn N agents; templates in `sub-agent-prompts.md`; skip rules" |
| Step 8 comparison | 481–514 (~34) | ~25 lines | Slim: keep three questions + attribution rule; drop elaborations |
| Step 8b persist | 516–629 | unchanged | Keep all bash + sub-agent merge |
| Step 9 Observatory | 631–643 | unchanged | Keep |
| Step 10 archive | 645–669 | unchanged | Keep |
| Completion | 671–687 | unchanged | Keep |
| References table | 691–704 | expanded with 3 new entries | Update |
| Sub-Agent Prompt Templates | 705–812 | **0** | Move to `references/sub-agent-prompts.md` |

**Net target: SKILL.md from 812 → ~460 lines (43% reduction).**

---

## New reference files

### `references/chat-output-format.md` (~80 lines moved)

Step 4 render spec, verbatim from current SKILL.md lines 209–283 with light tightening:
- Run-health surface (material issue → user-visible line mapping)
- BLUF rules (Sinatra Test, one sentence, structural weakness)
- Finding block format (name + bridge + concrete detail; no severity labels)
- Anchor-naming line ("Mental models active: …" with verbatim `display_name`s)
- Alternative-question line
- Structural-gaps line
- Delivery-check line
- Run-cost line
- Closing line
- Zero-detection fallback
- "What NOT to put in chat" (process artifacts, machinery language)

Loaded: at start of Step 4 (alongside existing `output-field-guide.md`).

### `references/anchor-treatment.md` (~70 lines moved)

Step 6 anchor doctrine, verbatim from current SKILL.md lines 357–408 with light tightening:
- Anchor-naming invariant
- Three-treatment vocabulary (primary pressure / secondary lens / set aside)
- "One primary-pressure anchor per reasoning move" rule
- When to use stronger / softer / set-aside framing (criteria lists)
- Critical: do NOT enumerate mechanically (the integration test)
- "Test: anchor-parade shape" warning
- Forbidden patterns
- "What good looks like" examples

Loaded: at start of Step 6 (alongside existing `presentation-voice.md` and `anti-bullshit-doctrine.md`).

### `references/sub-agent-prompts.md` (~108 lines moved)

Step 7 prompt templates, verbatim from current SKILL.md lines 705–812:
- Shared preamble template (with `{DECISION_SITUATION}`, `{LIVE_CONSTRAINTS}`, `{SYNTHESIZED_POSITION}`, `{REASONING_PASSAGES}`, `{ORIGINAL_FRAMING}`, `{DROPPED_THREADS}` placeholders)
- Lane 1 suffix (DeltaCard)
- Lane 2 suffix (CompanionCheatSheet)
- Lane 3 suffix (FramePressureCard)
- Lane 4 suffix (StructuralCoverageCard, gaps-only filtered)

Loaded: at Step 7, just before spawning sub-agents.

---

## Eliminated (duplicates collapsed)

1. **Card Reference subsection** (current lines 287–306) — fields documented in `references/output-field-guide.md`. SKILL.md keeps the existing pointer to that reference.
2. **Quality Doctrine section** (current lines 314–325) — same principles in `references/anti-bullshit-doctrine.md` and `references/presentation-voice.md`.
3. **Second Model Requirements block** (current lines 108–115) — collapsed with the first block at lines 32–38 into one block stating tier + operational refusal rule + self-check guidance.

---

## Test corpus

Three archived runs from `~/.local/share/lolla/runs/` selected for diversity along independent axes:

| Case | Run ID | Why |
|------|--------|-----|
| `founder-grant-marcus-equity` | `20260428T064421Z` | Full load: 5 anchors, 2 reframings, 8 dimensions. Stresses anchor-naming invariant + Step 7 4-way parallel spawn |
| `mid-level-consultant-report-1` | `20260428T110004Z` | `run_health.overall = degraded` (quote_fabrication=1) + 25 BI clear detections. Stresses run-health line + delivery-check rendering |
| `mother-deciding-protect-year` | `20260428T093545Z` | Personal-domain (non-business) case. Sanity check on voice/doctrine generality |

The archived `result.json` from each run is treated as the **baseline** for comparison against a fresh `/lolla` run on the refactored branch.

Note: founder-marcus baseline was archived ~3 hours before SKILL.md commit `62e3eca` (12-line Step 8b sub-agent filter fix). The other two baselines are post-`62e3eca`. The fix is preserved verbatim in this refactor; the comparison is unaffected.

---

## Test execution

Each case runs through this sequence:

1. **Switch to refactored branch** (`git checkout chore/skill-md-progressive-disclosure`). Symlink `~/.claude/skills/lolla` → working tree means `/lolla` will load the refactored SKILL.md automatically.
2. **Open fresh Claude Code session** with no prior context.
3. **Paste the conversation** from `~/.local/share/lolla/runs/<case>/<baseline_run_id>/conversation.txt` into the session as the user input.
4. **Invoke `/lolla`**. Run end-to-end through Steps 1–10.
5. **Locate the new run's archive** (Step 10 fingerprint-matches into the same case folder as the baseline; new `<run_id>` subfolder).
6. **Apply the invariant checklist** below to compare baseline vs. new artifacts.

Pipeline temperature is 0.2; finding *content* will shift between runs but *shape* and *presence* should not. The checklist tolerates content shift and tests structural invariants only.

---

## Invariant checklist (per case)

### Step 4 chat output (visual inspection from session transcript)

- [ ] Run-health line present iff baseline had a material issue
  - founder-marcus: should NOT show one (`overall: healthy` likely)
  - consultant-report: SHOULD show `quote_fabrication` line
  - mother-deciding: TBD — depends on baseline `run_health`
- [ ] BLUF: one sentence, names a structural weakness
- [ ] 2–4 finding blocks, each with bridge sentence + concrete detail (not field names, no severity labels in parens)
- [ ] "Mental models active:" line iff `companion_cheat_sheet.anchors` non-empty, with verbatim `display_name`s
- [ ] "Alternative question:" line iff `frame_pressure_card.reframings` non-empty
- [ ] "Structural gaps:" line iff Lane 4 has uncovered dimensions
- [ ] "Delivery check:" line iff `bullshit_profile.summary.total_clear > 0`
- [ ] "Run cost so far:" line present
- [ ] Closing line points to Observatory + `/usage`

### Step 6 revised_answer (read `revised.txt`)

- [ ] Three-part structure (§1 What survived / §2 What set aside / §3 What shifted) present and labeled
- [ ] **Anchor-naming invariant**: every anchor in `companion_cheat_sheet.anchors[].display_name` appears verbatim in `revised.txt` — verifiable by literal grep per anchor
- [ ] No machinery leaks: `grep -iE "sub-agent|the audit|the pipeline|delta card|companion cheat|gap check|pressure check.*sub"` returns zero hits in `revised.txt`
- [ ] Anchor treatment vocabulary present: at least one of *"primary pressure" / "secondary lens" / "set aside" / "appears to rely on" / "a related lens" / "a possible second read"* per anchor

### Persistence (read new run's `result.json`)

- [ ] `revised_answer_present: true`, `revised_answer_source: "claude_step6"`
- [ ] `gap_check.lanes` has 4 entries with valid `status` (`completed` / `skipped_empty` / `skipped_error`) and `divergences[]` arrays
- [ ] `usage_summary.vendors.anthropic_subagents.calls` ≤ 4 and matches the count of non-empty lanes (no phantom zero-token records)
- [ ] `gap_check_summary` is non-empty text

### Step 9/10

- [ ] Observatory launched (port 8080) — confirm by browsing
- [ ] Archive folder created at `~/.local/share/lolla/runs/<case>/<new_run_id>/` with all 7 expected artifacts

---

## Decision criteria

- **3/3 cases pass all invariants** → ship. Squash-merge to main.
- **2/3 pass** → diagnose the failing case. Failure tells us *which* moved doctrine wasn't being followed:
  1. **Strengthen the inline trigger** in SKILL.md (expand the "load this reference" line to name the key rules to check). Re-test that case only.
  2. **Pull the doctrine back inline** for the specific rule that broke. Re-test.
- **0–1 pass** → refactor abandoned. Revert branch, re-think structure.

Per `feedback_lane_calibration_avoid_overfitting`: do not extend the corpus to chase per-case wins. 3 cases is the budget.

---

## Reversibility

- All changes on `chore/skill-md-progressive-disclosure` only.
- No `git push` until decision criteria pass.
- If abandoned: `git checkout main && git branch -D chore/skill-md-progressive-disclosure`.
- Stashed spike WIP (`stash@{0}`) restored via `git stash pop` after returning to spike branch.

---

## Out of scope (intentional)

- HOW_IT_WORKS.md cleanup (user-facing doc, separate effort)
- Persistence-bash → script migration (Option C — deferred; new code surface)
- Phase verb cosmetic pass (out of scope per agreement)
- Engine, scripts, Observatory changes
- New 4th test case for short-conversation Lane 3 stress (deferred)
