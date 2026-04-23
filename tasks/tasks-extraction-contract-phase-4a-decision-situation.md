# PR #4a: Extraction Contract — decision_situation terse canonical form

**Branch:** `feat/extraction-contract-phase-4a-decision-situation`
**Roadmap:** `research/extraction-contract-roadmap.md` → PR #4a
**Normative spec:** `research/extraction-contract-observations-2026-04-22.md` → `decision_situation` section
**Blocks:** PR #4b (same file; ship sequentially to avoid concurrent prompt edits on one block)
**Blocked on:** PR #1 merged to main
**Scope:** Prompt-only change. Add ≤200-char rule + "single sentence, neutral third-person, declarative" rule to `decision_situation` extraction instructions. No schema change. Apply PR #1's proven terse-rule discipline rather than the observation-doc's fill-in template.

## Why this PR exists

Mode C drift on `decision_situation` was 0.256 in the observations doc N=3; cross-capture 0.367 on 36 pairs. Higher than some other fields but still well below target. Pre-ship diagnosis: the prompt says "State it as a neutral problem statement, not as the AI framed it. Include the domain, key stakeholders, and what is at stake. Be specific" — no length ceiling, no single-sentence rule. LLM samples produce prose of varying length (60-300+ chars), opening with varying structural forms ("A founder-CEO of…", "Whether Marcus should…", "The decision is…"), driving character-level similarity down.

PR #1 proved that a **terse-form length rule** on the `constraint` field tightened exact-text Jaccard 10× without semantic loss. PR #4a applies the same mechanism to `decision_situation`: one sentence, ≤200 chars, declarative third-person. The observation doc's fill-in template (`"[Whether|How|When] [action] [subject]..."`) is explicitly NOT adopted — rigid templates break on edge cases (compound decisions, multi-part framing). The terse-rule preserves the LLM's flexibility within a length budget.

## Testing approach

No TDD. This PR is prompt-only.

Minimal Python-side addition: optional length assertion (if ≤200 chars is enforced programmatically via a `capture_warning` rather than just prompt-level instruction). Decide at task start.

The PR succeeds by measurement (cross-capture similarity), not by unit test.

## Relevant Files

- `scripts/run_extract.py` — edit `EXTRACTION_SYSTEM_PROMPT` field `1. "decision_situation"` paragraph only. Lines ~215-218 in current file.
- `HOW_IT_WORKS.md` — §Step 2 `decision_situation` row: note the terse-form rule.
- `research/extraction-contract-roadmap.md` — PR #4a status transitions.
- `research/stability-runs/contract-phase4a-pre-ship-<date>/` — baseline (can reuse PR #1's post-ship cross-capture for non-canonical-key fields; `decision_situation` post-PR-#1 cross-capture was 0.335).
- `research/stability-runs/contract-phase4a-post-ship-<date>/` — post-ship evidence.

### Notes

- Test runner: `python3 -m pytest tests/ -v` (regression check only — no new tests expected).
- Keep the prompt addition small — context pollution is the known risk even for small additions. Aim for ~200 chars of added prompt text maximum.
- Do NOT add a template or fill-in form. Terse-rule discipline only.

## Instructions for Completing Tasks

As each sub-task completes, change `- [ ]` → `- [x]` in this file.

## Acceptance Gate (from roadmap)

| Axis | Target |
|---|---|
| Cross-capture `decision_situation` similarity mean | ≥ 0.55 (vs PR #1 post-ship baseline 0.335; vs pre-PR-#1 baseline 0.367) |
| `decision_situation` length ≤ 200 chars | 9/9 runs |
| Qualitative: neutral third-person, single sentence | yes (3 spot-checks) |
| Regression on all other fields | no decrease > 0.03 vs PR #1b shipped state |
| Regression on fabricated count | 0 |
| Cost per extraction call | ≤ +5% |

## Tasks

- [ ] 0.0 Pre-flight
  - [ ] 0.1 Confirm PR #1 and PR #1b merged to main (if PR #1b is merged; if not, PR #4a can still ship independently — it doesn't depend on canonical_key).
  - [ ] 0.2 Create branch: `git checkout -b feat/extraction-contract-phase-4a-decision-situation`.
  - [ ] 0.3 Read current `decision_situation` prompt section in `scripts/run_extract.py` (~lines 215-218).

- [ ] 1.0 Draft the prompt edit
  - [ ] 1.1 Propose new text (example to adjust):
    ```
    1. "decision_situation": the core decision as a single declarative
       sentence, ≤200 characters, neutral third-person. State the subject,
       the action being decided, and the material context. Avoid prose,
       emotive language, and speculative outcomes. Example: "Whether
       Marcus should receive 15% equity given retention risk and
       $9-13M exit valuation."
    ```
  - [ ] 1.2 Share with user for review before committing if in interactive mode.
  - [ ] 1.3 Apply the edit to `scripts/run_extract.py`.
  - [ ] 1.4 Run `python3 -m pytest tests/ -v` — full suite green.

- [ ] 2.0 (Optional) Add length-assertion `capture_warning`
  - [ ] 2.1 Decide at task start: enforce ≤200 chars programmatically or rely on prompt? Default: prompt-only; add the assertion only if post-ship evidence shows the LLM regularly exceeds 200.

- [ ] 3.0 Update HOW_IT_WORKS.md
  - [ ] 3.1 Update the `decision_situation` table row to note the terse-form rule.

- [ ] 4.0 Post-ship acceptance gate
  - [ ] 4.1 Create directory: `mkdir -p research/stability-runs/contract-phase4a-post-ship-<date>/{modec-n5,cross-capture,cross-capture-drift}`.
  - [ ] 4.2 Run Mode C N=5 on newest capture.
  - [ ] 4.3 Run extractor on all 9 Marcus captures.
  - [ ] 4.4 Run cross-capture drift via `--from-extractions`.
  - [ ] 4.5 Compare against baseline (PR #1's post-ship cross-capture for non-canonical-key fields).
  - [ ] 4.6 Check every gate axis. Record length distribution across 9+5=14 `decision_situation` strings.
  - [ ] 4.7 Qualitative: read 3 extractions, confirm single-sentence + neutral + declarative.

- [ ] 5.0 Ship or pause
  - [ ] 5.1 If all axes pass: commit evidence, flip roadmap to IN REVIEW, push, open PR.
  - [ ] 5.2 If any axis fails: STOP. Update roadmap PR #4a section. Share findings.
  - [ ] 5.3 On merge: flip roadmap to SHIPPED.

- [ ] 6.0 PR metadata
  - [ ] 6.1 PR title: `feat(extract): decision_situation terse canonical form (phase 4a)`.
  - [ ] 6.2 PR description: before/after cross-capture similarity, length distribution, 3 qualitative samples. Links to evidence dir. Honesty clause.
