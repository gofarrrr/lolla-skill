# PR #5: Extraction Contract — reasoning_passages.move_type + generalize hard-fail

**Branch:** `feat/extraction-contract-phase-5-move-type-hard-fail`
**Roadmap:** `research/extraction-contract-roadmap.md` → PR #5
**Normative spec:** `research/extraction-contract-observations-2026-04-22.md` → `reasoning_passages` section
**Blocked on:** PR #1 merged. Independent of #1b, #2, #3, #4a, #4b — can interleave anywhere.
**Scope:** Two related changes. (1) Add `move_type` enum subfield to each `Passage` in `reasoning_passages`. Reduced from observation-doc's 7 values to **5 values** to minimize close-disambiguation drift. (2) Generalize existing retry-then-drop quote-validation into a reusable helper so future PRs referencing verbatim turn content don't re-implement. **No behavior change** on the quote validation itself — just a refactor for reusability.

## Why this PR exists

`reasoning_passages` has the highest cross-capture text Jaccard of any list field (0.357-0.418 across three measured states). It's already structurally stable because the extractor is forced to emit literal substrings. What's NOT captured: **the type of reasoning move** each passage represents. Lanes 1 and 2 currently re-derive this from prose; adding `move_type` as a structured signal lets them filter passages by type without re-reading.

The observations doc proposed 7 values: `leap`, `dismissal`, `assertion_without_evidence`, `framing_shift`, `closure`, `inversion`, `comparison`. Disambiguation-difficulty analysis (see §"Design decisions" below) suggests reducing to 5: drop `inversion` (too-close to `framing_shift`) and `comparison` (too-close to `leap`). Can be added back in a follow-up PR if a real case surfaces where the 5-value set is insufficient.

The generalized hard-fail helper is pure infrastructure. Today, `_validate_passages` + retry logic in `main()` of `run_extract.py` is embedded in the main flow. PR #5 refactors this into a helper so future PRs adding verbatim-text fields (e.g., any canonical-quote field) can reuse the retry-then-drop pattern without re-implementation. **No behavior change** to quote-validation on this PR.

## Testing approach

Red-green-refactor TDD for:
1. **`move_type` enum validator** (pure function).
2. **`_apply_move_type_validation`** (extends the post-processing pattern; pure function).
3. **Generalized hard-fail helper** (pure function; refactor of existing `_validate_passages` + retry logic).

Not TDD: move_type selection semantics (empirical), enum-stability measurement (design question — see below).

## Design decisions to answer at task start

### 1. Enum values — 5 or 7?

Proposed **5-value set** with clear disambiguation criteria:

| Value | Definition | Distinguishing signal |
|---|---|---|
| `leap` | Jump from observation to recommendation without intermediate reasoning | Verb-noun gap: claim made without causal chain |
| `dismissal` | Acknowledging a risk/concern then minimizing without evidence | Pattern: "while X, Y is unlikely to matter" |
| `assertion_without_evidence` | Precise claim (number, certainty) with no stated basis | Quantified claim + no citation |
| `framing_shift` | Choosing one lens and implicitly excluding others | Phrase pattern: "the real question is…" |
| `closure` | Declaring resolution / moving past something prematurely | Verb pattern: "let's move on," "that's settled" |

Dropped from observation doc's original 7:
- `inversion` — often overlaps with `framing_shift` (both reframe). Merged in.
- `comparison` — often overlaps with `leap` (comparing without establishing relevance). Merged in.

If task-time analysis suggests the 5 are still too blurry, reduce further to 3-4. Document the choice.

### 2. Measurement — how do you measure enum-agreement when passage text itself drifts?

Current cross-capture `reasoning_passages` text Jaccard is 0.357-0.418. Different runs extract DIFFERENT passages. You can't measure "when the same passage is extracted, do runs agree on move_type?" if the passages aren't the same.

Three measurement options:

**Option A — Fuzzy-match passages, then measure enum agreement on matched set.**
- Step 1: For each pair of runs, find passages with ≥ 0.80 fuzzy similarity (use rapidfuzz or difflib).
- Step 2: On the matched pairs, check move_type equality.
- Report: matched-pair count + agreement rate.
- Complexity: medium.

**Option B — Distribution sanity only.**
- Check that across all 9 runs' passages, no single move_type value covers > 60% of all passages.
- Ensures the enum isn't degenerate (LLM just picking one value for everything).
- Simple; weaker signal.

**Option C — Ask the LLM directly in a self-check call.**
- For each pair of passages with high textual similarity, ask an LLM "do these two passages represent the same reasoning move?"
- Too expensive / adds complexity. SKIP.

**Recommendation lean: A+B combined.** A gives the real answer when passages can be matched; B catches the degenerate case. Both cheap.

### 3. Strict enum vs str+validator?

Strict enum via Python enum or TypedDict: type safety, harder to extend.

`str` + validator against known-values list: loose type, extends via one-line constant update.

**Recommendation lean:** `str` + validator. Matches PR #1b's slug pattern. Allows future values without breaking change.

## Relevant Files

- `scripts/run_extract.py` — prompt addition (move_type rule + 5-value list + examples); `_validate_move_type` function; `_apply_move_type_validation` post-processor; **refactor** of `_validate_passages` + retry logic into a reusable `_retry_then_drop(payload_validator, retry_prompt, conversation_text, client)` helper.
- `scripts/stability_check.py` — extend `compute_extraction_drift` to compute move_type metrics (fuzzy-match passages, then enum agreement + distribution sanity).
- `tests/test_run_extract.py` — tests for move_type validator + post-processor + refactored helper.
- `tests/test_stability_check.py` — tests for move_type drift metrics.
- `HOW_IT_WORKS.md` — §Step 2 `reasoning_passages` row: note move_type subfield + enum values.
- `research/extraction-contract-roadmap.md` — PR #5 status transitions.
- `research/stability-runs/contract-phase5-pre-ship-<date>/` + `-post-ship-<date>/`.

### Notes

- The hard-fail refactor MUST preserve behavior. Run existing fabrication tests before/after to confirm zero regression.
- Fuzzy-match passages implementation: use `rapidfuzz.fuzz.ratio(a, b) / 100 >= 0.80` or equivalent. Keep dependency optional — fall back to `difflib.SequenceMatcher` if rapidfuzz unavailable.

## Instructions for Completing Tasks

As each sub-task completes, change `- [ ]` → `- [x]`.

## Acceptance Gate (from roadmap)

| Axis | Target |
|---|---|
| `reasoning_passages.text` Jaccard (regression check — existing metric) | no decrease vs PR #1 baseline (stay ≥ 0.30) |
| `move_type` distribution sanity (no single value > 60%) | pass across all 9 cross-capture runs |
| `move_type` enum agreement on fuzzy-matched passages (if Option A chosen) | ≥ 0.60 |
| `_quote_validation.fabricated` count | 0 |
| Refactor regression: existing retry-then-drop tests all pass | yes |
| Regression on other fields | no decrease > 0.03 |
| Cost per extraction call | ≤ +10% |

## Tasks

- [ ] 0.0 Pre-flight
  - [ ] 0.1 Confirm PR #1 merged.
  - [ ] 0.2 Create branch.
  - [ ] 0.3 Read current `_validate_passages` and retry block in `run_extract.py` (~lines 615-670).

- [ ] 1.0 Design decisions (document before coding)
  - [ ] 1.1 Enum values — confirm 5 vs 7. Default 5.
  - [ ] 1.2 Measurement approach — Option A+B. Confirm or change.
  - [ ] 1.3 Strict enum vs str+validator. Default str+validator.

- [ ] 2.0 Move_type validator (TDD)
  - [ ] 2.1 RED: test `_validate_move_type("leap") is True`.
  - [ ] 2.2 GREEN: add `_validate_move_type(v: str) -> bool` in `run_extract.py`. Constants list of 5 values.
  - [ ] 2.3 RED: tests for invalid (`"unknown"`, `""`, `None`, `"INVERSION"` uppercase).
  - [ ] 2.4 GREEN: verify.
  - [ ] 2.5 RED: test for `_apply_move_type_validation(payload, warnings)` — invalid move_type set to empty, valid preserved, warnings appended.
  - [ ] 2.6 GREEN: add the post-processor (mirrors `_apply_canonical_key_validation` shape).

- [ ] 3.0 Generalize retry-then-drop helper (TDD, pure refactor — no behavior change)
  - [ ] 3.1 RED: test — given the current inputs that reproduce today's `_validate_passages` + retry behavior, the generalized helper returns the same (verified, fabricated, retry_attempted, retry_succeeded) tuple.
  - [ ] 3.2 GREEN: extract `_retry_then_drop(item_validator, retry_prompt_template, conversation_text, client, initial_payload)` as a pure helper. Returns payload + metadata.
  - [ ] 3.3 RED: test that existing quote-fabrication tests still pass with refactor.
  - [ ] 3.4 GREEN: replace the inline retry block in `main()` with a call to the helper.
  - [ ] 3.5 REFACTOR: run full test suite to confirm zero regression.

- [ ] 4.0 Draft move_type prompt addition
  - [ ] 4.1 Read current `4. "reasoning_passages"` prompt block.
  - [ ] 4.2 Draft addition — ≤400 chars. Example:
    ```
    Each passage object adds a "move_type" field — one of:
      * "leap" — jump from observation to recommendation
      * "dismissal" — acknowledge a risk then minimize without evidence
      * "assertion_without_evidence" — precise claim (number, certainty)
        with no stated basis
      * "framing_shift" — choose one lens, implicitly exclude others
      * "closure" — declare resolution / move past prematurely
    ```
  - [ ] 4.3 Share with user for review.
  - [ ] 4.4 Apply the edit.

- [ ] 5.0 Extend drift harness for move_type (TDD, Option A+B)
  - [ ] 5.1 RED: test — `_fuzzy_match_passages(listA, listB, threshold=0.80)` returns pairs of similar passages.
  - [ ] 5.2 GREEN: add helper using `difflib.SequenceMatcher` (no external dep) or `rapidfuzz`.
  - [ ] 5.3 RED: test — for matched passage pairs, compute `move_type` agreement rate.
  - [ ] 5.4 GREEN: extend `compute_extraction_drift` per-pair block with `reasoning_passages_move_type_agreement`.
  - [ ] 5.5 RED: test — aggregate computes move_type distribution across all runs; flag if any value > 60%.
  - [ ] 5.6 GREEN: add aggregate block.
  - [ ] 5.7 Update `render_drift_markdown` to show move_type distribution table + matched-pair agreement rate.

- [ ] 6.0 Update HOW_IT_WORKS.md
  - [ ] 6.1 Update `reasoning_passages` row to note move_type subfield + the 5-value list.

- [ ] 7.0 Pre-ship baseline + post-ship acceptance gate
  - [ ] 7.1 Evidence dirs.
  - [ ] 7.2 Pre-ship: reuse whatever is the most recent shipped-state cross-capture output.
  - [ ] 7.3 Post-ship: Mode C + cross-capture.
  - [ ] 7.4 Check gate axes. Investigate if fuzzy-match finds very few pairs (means passages drift so much even fuzzy matching fails; consider relaxing threshold).
  - [ ] 7.5 Qualitative: read 3 extractions. Confirm move_type values make sense for the passage content.

- [ ] 8.0 Ship or pause
  - [ ] 8.1 If all axes pass: commit, push, open PR.
  - [ ] 8.2 If refactor regressed quote-validation: revert refactor; ship move_type only.
  - [ ] 8.3 If distribution sanity fails (some value > 60%): the enum is too coarse or LLM is defaulting. Investigate.

- [ ] 9.0 PR metadata
  - [ ] 9.1 PR title: `feat(extract): reasoning_passages.move_type enum + generalize retry-then-drop helper (phase 5)`.
  - [ ] 9.2 PR description: acceptance table, enum-value choice rationale (why 5 vs 7), refactor-preservation evidence.
