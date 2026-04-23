# PR #4b: Extraction Contract — original_framing first-turn anchor + terse form

**Branch:** `feat/extraction-contract-phase-4b-original-framing`
**Roadmap:** `research/extraction-contract-roadmap.md` → PR #4b
**Normative spec:** `research/extraction-contract-observations-2026-04-22.md` → `original_framing` section
**Blocked on:** PR #4a merged (same file; avoid concurrent prompt edits)
**Scope:** Prompt-only change. Anchor `original_framing` mechanically to the FIRST user turn, add ≤200-char rule. Forbid conversation-evolved framing (that belongs in `synthesized_position.superseded_stances` per PR #3).

## Why this PR exists

Cross-capture `original_framing` similarity is **0.209** pre-ship — the lowest baseline of any free-text field. Two failure modes from the observations doc:

1. **Phrasing drift** — each run produces a different paraphrase of the same underlying framing. The ≤200-char rule compresses surface variance (same mechanism as PR #1 and PR #4a).
2. **Ontology drift** — some runs describe first-turn framing; others describe the AI's evolved framing (which belongs in `synthesized_position.superseded_stances`). Mechanically anchoring to the FIRST user turn eliminates this ambiguity.

PR #4b combines both fixes. Lower realistic target than other fields because the baseline is genuinely low and the field is inherently judgment-heavy.

## Testing approach

No TDD. Prompt-only change, empirical via acceptance gate.

## Relevant Files

- `scripts/run_extract.py` — edit `EXTRACTION_SYSTEM_PROMPT` field `5. "original_framing"` (line ~196 in current file).
- `HOW_IT_WORKS.md` — §Step 2 `original_framing` row: note the first-turn anchor + terse-form rule.
- `research/extraction-contract-roadmap.md` — PR #4b status transitions.
- `research/stability-runs/contract-phase4b-pre-ship-<date>/` — baseline (reuse PR #4a post-ship for non-target fields; original_framing post-PR-#4a baseline TBD).
- `research/stability-runs/contract-phase4b-post-ship-<date>/` — post-ship evidence.

### Notes

- This PR is the second "terse canonical form" PR. Mirror PR #4a's structure exactly.
- original_framing is the hardest-to-move free-text field in the roadmap. The 0.35 target IS a stretch; if qualitative criteria pass but the metric stays flat at pre-ship levels, SHIP. The anchor-to-first-turn rule produces structurally correct output even when character-level similarity is low.

## Instructions for Completing Tasks

As each sub-task completes, change `- [ ]` → `- [x]` in this file.

## Acceptance Gate (from roadmap)

| Axis | Target |
|---|---|
| Cross-capture `original_framing` similarity mean | ≥ 0.35 (vs pre-ship baseline 0.209 — stretch) |
| `original_framing` length ≤ 200 chars | 9/9 runs |
| Qualitative: anchored to first user turn, no conversation-evolved framing | yes (3 spot-checks) |
| Regression on all other fields | no decrease > 0.03 |
| Regression on fabricated count | 0 |

**Acceptable alternative outcome:** if quantitative similarity stays flat (~0.20) but all 9 runs clearly anchor to the first user turn with no conversation-evolved framing leakage → SHIP. Structural correctness matters more than the character-level score on this field.

## Tasks

- [ ] 0.0 Pre-flight
  - [ ] 0.1 Confirm PR #4a merged to main.
  - [ ] 0.2 Create branch: `git checkout -b feat/extraction-contract-phase-4b-original-framing`.
  - [ ] 0.3 Read current `original_framing` prompt section in `scripts/run_extract.py` (line ~196-198).

- [ ] 1.0 Draft the prompt edit
  - [ ] 1.1 Propose new text (example to adjust):
    ```
    5. "original_framing": how the HUMAN posed the question IN THE FIRST
       TURN. ≤200 chars, neutral third-person. Describe: what was assumed
       fixed, what alternatives were excluded, what lens the human brought.
       MUST NOT describe: framing shifts later in the conversation (those
       belong in synthesized_position.superseded_stances).
    ```
  - [ ] 1.2 Share with user for review.
  - [ ] 1.3 Apply the edit.
  - [ ] 1.4 Run full test suite.

- [ ] 2.0 Update HOW_IT_WORKS.md
  - [ ] 2.1 Note the first-turn anchor + ≤200-char rule in the `original_framing` row.

- [ ] 3.0 Post-ship acceptance gate (mirror PR #4a structure)
  - [ ] 3.1 Create evidence directories.
  - [ ] 3.2 Run Mode C N=5.
  - [ ] 3.3 Extract on 9 captures.
  - [ ] 3.4 Cross-capture drift.
  - [ ] 3.5 Check gate axes. Note the "acceptable alternative outcome" above — a flat-quantitative, strong-qualitative result ships.

- [ ] 4.0 Ship or pause
  - [ ] 4.1 If gate passes (strict OR alternative): commit evidence, open PR.
  - [ ] 4.2 If gate fails: STOP. Update roadmap.

- [ ] 5.0 PR metadata
  - [ ] 5.1 PR title: `feat(extract): original_framing first-turn anchor + terse form (phase 4b)`.
