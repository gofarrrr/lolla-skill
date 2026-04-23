# PR #2: Extraction Contract — dropped_threads.canonical_key + tie-break rule + ≤120-char thread rule

**Branch:** `feat/extraction-contract-phase-2-dropped-threads`
**Roadmap:** `research/extraction-contract-roadmap.md` → PR #2
**Normative spec:** `research/extraction-contract-observations-2026-04-22.md` → `dropped_threads` section
**Blocked on:** PR #1b merged (canonical_key pattern must be proven on live_constraints with embedding cosine before applying to dropped_threads)
**Scope:** Three related changes to `dropped_threads` output. (1) Add `canonical_key` subfield mirroring PR #1b's pattern. (2) Add ≤120-char terse-form rule on `thread` text mirroring PR #1's proven win on `constraint`. (3) Implement tie-break rule in the prompt: a concern raised by a third party briefly addressed by the AI is a `Constraint` with `weight: situational`, NOT a `dropped_thread` — unless the user explicitly abandoned it later.

## Why this PR exists

From the observations doc: `dropped_threads` cross-capture exact-text Jaccard is 0.132 (pre-PR-#1), better than `live_constraints` but still low. Three failure modes:

1. **Phrasing drift on `thread` text** — same class of problem as `constraint` text. PR #1's ≤120-char rule generalizes here.
2. **No canonical_key subfield** — same stable-identifier problem solved in PR #1b for live_constraints. This PR applies that pattern.
3. **Taxonomy ambiguity at edges** — the observations doc §live_constraints identifies a concrete case: a concern raised by the user's wife in Turn 3 that the AI briefly addresses and moves past is *legitimately both* a dropped thread AND a situational constraint. The current prompt has no tie-break rule; runs disagree; `_map_to_critique_request` formats the two fields differently so the output to downstream lanes looks materially different across runs.

The tie-break rule resolves ambiguity (3) by a mechanical test: **if the user returned to the concern, it's live (`live_constraints` with `weight: situational`); if the user never revisited it, it's a `dropped_thread`.** Third-party proxy (wife, lawyer, etc.) treated as user-adjacent for this rule.

## Testing approach

Red-green-refactor TDD for the tie-break violation detector (pure function, deterministic given extraction JSON). Not TDD for prompt text — empirical via acceptance gate.

Reuse PR #1's `_validate_canonical_key` and `_apply_canonical_key_validation` — extend the post-processor to walk dropped_threads as well as live_constraints. TDD the extension.

## Relevant Files

- `scripts/run_extract.py` — prompt additions to dropped_threads block (canonical_key + ≤120-char + tie-break rule); extend `_apply_canonical_key_validation` to walk dropped_threads.
- `scripts/stability_check.py` — extend `compute_extraction_drift` to compute embedding-cosine metric on `dropped_threads.canonical_key` (reuse PR #1b's helper); compute tie-break violation count as a new metric.
- `tests/test_run_extract.py` — extend tests for `_apply_canonical_key_validation` covering dropped_threads path.
- `tests/test_stability_check.py` — new tests for `dropped_threads_canonical_key_embedding` metric + tie-break violation detector.
- `HOW_IT_WORKS.md` — §Step 2 `dropped_threads` row: note the canonical_key, ≤120-char, and tie-break rules.
- `research/extraction-contract-roadmap.md` — PR #2 status transitions.
- `research/stability-runs/contract-phase2-pre-ship-<date>/` and `-post-ship-<date>/`.

### Notes

- Test runner: `python3 -m pytest tests/ -v`.
- Embedding helper `_compute_embedding_cosine` and drift function extensions are inherited from PR #1b. This PR reuses, doesn't rebuild.
- The tie-break rule is the main new risk. Watch the violation-count axis carefully.

## Instructions for Completing Tasks

As each sub-task completes, change `- [ ]` → `- [x]`.

## Acceptance Gate (from roadmap)

| Axis | Target |
|---|---|
| Cross-capture `dropped_threads.canonical_key` embedding cosine mean | ≥ 0.60 |
| Cross-capture `dropped_threads.thread` exact-text Jaccard | ≥ 0.20 (vs pre-ship baseline 0.132) |
| Tie-break violations (items appearing in both `live_constraints` AND `dropped_threads` by canonical_key across any run) | 0 across all 9 runs |
| `invalid_key_rate` overall (dropped_threads) | ≤ 10% |
| Regression on `live_constraints` canonical_key embedding cosine | no decrease vs PR #1b shipped state |
| Regression on other fields | no decrease > 0.03 |
| Fabricated count | 0 |
| Cost per extraction call | ≤ +10% vs PR #1b |

## Tasks

- [ ] 0.0 Pre-flight
  - [ ] 0.1 Confirm PR #1b merged to main.
  - [ ] 0.2 Create branch: `git checkout -b feat/extraction-contract-phase-2-dropped-threads`.
  - [ ] 0.3 Verify `_validate_canonical_key`, `_apply_canonical_key_validation`, `_compute_embedding_cosine`, and `compute_extraction_drift` canonical_key embedding extension exist.

- [ ] 1.0 Extend validator post-processor to dropped_threads (TDD)
  - [ ] 1.1 Read current `_apply_canonical_key_validation` (in `scripts/run_extract.py`). It walks `payload["live_constraints"]`.
  - [ ] 1.2 RED: write test — given a payload with BOTH `live_constraints` and `dropped_threads`, each with valid canonical_keys on some items and invalid on others, the validator blanks invalid keys in BOTH lists and emits capture_warnings listing offenders from both.
  - [ ] 1.3 GREEN: refactor `_apply_canonical_key_validation(payload, capture_warnings, lists=("live_constraints", "dropped_threads"))` — iterate the list names, apply the same validation logic.
  - [ ] 1.4 RED: write test — legacy call shape `_apply_canonical_key_validation(payload, capture_warnings)` still works (walks live_constraints by default for backward compat).
  - [ ] 1.5 GREEN: default the `lists` parameter to both names so the main() call site still works without change.

- [ ] 2.0 Extend drift harness to dropped_threads canonical_key (TDD)
  - [ ] 2.1 RED: write test in `tests/test_stability_check.py` — when both runs have dropped_threads with matching canonical_keys, pair's `dropped_threads_canonical_key_embedding.mean_cosine` is high (near 1.0).
  - [ ] 2.2 GREEN: extend `compute_extraction_drift`'s per-pair block to compute `dropped_threads_canonical_key_embedding` using the same `_compute_embedding_mean_for_lists` helper from PR #1b.
  - [ ] 2.3 RED: aggregate test — `live_constraints_canonical_key_embedding` and `dropped_threads_canonical_key_embedding` both appear in aggregate with mean/min/max.
  - [ ] 2.4 GREEN: extend aggregate block.
  - [ ] 2.5 Extend `render_drift_markdown` to include dropped_threads canonical_key rows.

- [ ] 3.0 Add tie-break violation detector (TDD)
  - [ ] 3.1 RED: test in `tests/test_run_extract.py` — given a payload where one canonical_key appears in BOTH live_constraints and dropped_threads, `_detect_tie_break_violations(payload) -> list[str]` returns that key.
  - [ ] 3.2 GREEN: add `_detect_tie_break_violations(payload)` — collect canonical_keys from live_constraints and dropped_threads; return the intersection.
  - [ ] 3.3 RED: test — when all canonical_keys are distinct, returns empty list.
  - [ ] 3.4 GREEN: verify.
  - [ ] 3.5 RED: test — empty canonical_keys (validated to "") are excluded from the intersection detection.
  - [ ] 3.6 GREEN: add the filter.
  - [ ] 3.7 Wire the detector into `main()` — after `_apply_canonical_key_validation`, call `_detect_tie_break_violations(payload)`. If violations, append a `capture_warning` listing them.
  - [ ] 3.8 Optionally extend the drift harness to count tie-break violations per run in the drift aggregate.

- [ ] 4.0 Draft prompt edits (three changes to dropped_threads block)
  - [ ] 4.1 Read current `6. "dropped_threads"` block in `EXTRACTION_SYSTEM_PROMPT`.
  - [ ] 4.2 Draft: add `canonical_key` (condensed form mirroring PR #1b's condensed block — 2-4 token slug; same-concept-same-key rule).
  - [ ] 4.3 Draft: add ≤120-char rule on `thread` text with a good/bad example pair.
  - [ ] 4.4 Draft: add tie-break rule as a prose paragraph after the subfield list. Example wording:
    ```
    Tie-break with live_constraints: a concern raised by a third party
    (user's wife, lawyer, etc.) that the AI addressed briefly is a
    Constraint with weight: situational, NOT a dropped_thread — unless
    the user explicitly abandoned it in a later turn. Mechanical rule:
    if the user returned to it, it's live; if the user never revisited
    and never resolved, it's a dropped_thread.
    ```
  - [ ] 4.5 Budget check: total added prompt text ≤ 500 chars. Condense if over.
  - [ ] 4.6 Share the full draft with user for review before committing.

- [ ] 5.0 Apply prompt edit + run tests
  - [ ] 5.1 Apply the edit to `scripts/run_extract.py` dropped_threads block.
  - [ ] 5.2 Run full test suite `python3 -m pytest tests/ -v`.

- [ ] 6.0 Update HOW_IT_WORKS.md
  - [ ] 6.1 Update the `dropped_threads` table row: note canonical_key, ≤120-char, and tie-break rule.

- [ ] 7.0 Pre-ship baseline + post-ship acceptance gate
  - [ ] 7.1 Create evidence dirs.
  - [ ] 7.2 Pre-ship baseline: reuse PR #1b shipped-state output (same Marcus captures).
  - [ ] 7.3 Post-ship: run Mode C N=5 + 9-capture cross-run + cross-capture drift.
  - [ ] 7.4 Check all gate axes. Verify tie-break violation count = 0.
  - [ ] 7.5 Qualitative: read 3 extractions. Confirm: (a) dropped_threads have canonical_keys, (b) thread text is terse, (c) third-party concerns are assigned to live_constraints (situational) not dropped_threads.

- [ ] 8.0 Ship or pause
  - [ ] 8.1 If all axes pass: commit evidence, flip roadmap, push, open PR.
  - [ ] 8.2 If tie-break violations > 0: investigate. Likely prompt needs strengthening on the "user returned to it = live" rule.
  - [ ] 8.3 If gate fails otherwise: STOP. Update roadmap. Share findings.

- [ ] 9.0 PR metadata
  - [ ] 9.1 PR title: `feat(extract): dropped_threads canonical_key + terse form + tie-break rule (phase 2)`.
  - [ ] 9.2 PR description: evidence of tie-break zero violations, canonical_key embedding cosine, thread exact-text improvement, regression table on all other fields.
