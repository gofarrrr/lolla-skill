# PR #3: Extraction Contract — synthesized_position as Position object

**Branch:** `feat/extraction-contract-phase-3-synthesized-position`
**Roadmap:** `research/extraction-contract-roadmap.md` → PR #3
**Normative spec:** `research/extraction-contract-observations-2026-04-22.md` → `synthesized_position` section
**Blocked on:** PR #1 merged to main. Independent of PR #1b, #2, #4a, #4b, #5 — can ship in parallel.
**Scope:** Biggest structural change in the roadmap. Replace `synthesized_position: str` with structured `Position` object containing `stance` enum, `latest_stance_text`, `superseded_stances` list, and `is_ambiguous` flag. Mechanically anchor `latest_stance_text` to the FINAL assistant turn. Update `_map_to_critique_request` to absorb the shape change so downstream lanes don't see it.

## Why this PR exists

From the observations doc: synthesized_position has the LOWEST baseline stability of any field (cross-capture similarity 0.169). The loudest observed failure: **shape drift**. Same Marcus conversation, three runs:
- Run 1: extracted as "user's A/B choice"
- Run 2: extracted as "advisor's prescription"
- Run 3: extracted as "third-person tradeoff summary"

Free-text synthesis resolves the "what IS the stance" ambiguity three different ways, driving character-level similarity to near-zero. No prompt refinement on a free-text field can fix an underspecified contract.

The fix is **structural, not linguistic**: replace free text with a typed object whose shape the LLM must fill in. The stance becomes an enum (3 values). The "latest" stance is mechanically the FINAL assistant turn — no more interpretation. Superseded stances (AI's earlier positions the conversation abandoned) get their own field. `is_ambiguous` flags the edge case where the final turn presents tradeoffs without a recommendation.

## Testing approach

Red-green-refactor TDD for:
1. **Stance enum validator** (pure function).
2. **`_map_to_critique_request` with new Position input** (pure function; produces the same `query` + `vanilla_answer` shape as today to avoid downstream changes).
3. **Migration helper** (pure function; if we version the schema, v1 → v2 conversion for archived JSONs).

Not TDD: prompt text, LLM `is_ambiguous` judgment, stance-selection semantics.

## Design decisions to answer at task start

1. **Schema versioning vs immediate breaking change?**
   - Version: add `"extraction_version": 2` to output. Old consumers can check and adapt. Complicates `_map_to_critique_request`. Benefit: archived JSONs keep parsing.
   - Immediate: replace the shape; bump an implicit version through code. Simpler. Archive JSONs need migration or are treated as legacy.
   - Recommendation lean: **immediate breaking change** — `_map_to_critique_request` already will be updated in this PR, so there's no in-place backward compat cost at the consumer layer. Archived JSONs become "old version, no re-parse needed" since the archive is for inspection not for re-running.

2. **What if the final assistant turn is a clarifying question, not a stance?**
   - Option A: `stance: "declines_to_recommend"` + `latest_stance_text = the clarifying question text` + `is_ambiguous: true`.
   - Option B: Fall back to the most-recent turn that WAS a stance.
   - Recommendation lean: **Option A** — mechanical rule stays clean; `is_ambiguous` absorbs.

3. **Downstream consumers: any code outside `_map_to_critique_request` that reads `synthesized_position`?**
   - Must grep before writing: `grep -r "synthesized_position" engine/ scripts/`.
   - If any consumer reads it as a string, update inline OR route through `_map_to_critique_request`'s new shape-absorb logic.

## Relevant Files

- `scripts/run_extract.py` — schema (implicit via prompt), prompt rewrite for `synthesized_position`, `_map_to_critique_request` updates. ~30% of the file's effective prompt size is touched by this PR.
- `scripts/stability_check.py` — extend `compute_extraction_drift` to handle the new Position shape: stance-enum Jaccard (same pattern as canonical_key Jaccard), latest_stance_text similarity.
- `engine/system_b/` — grep for `synthesized_position` consumers (likely zero beyond `_map_to_critique_request`, but verify).
- `tests/test_run_extract.py` — tests for stance validator, Position post-processing, `_map_to_critique_request` with new input.
- `tests/test_stability_check.py` — tests for stance Jaccard + latest_stance_text similarity.
- `HOW_IT_WORKS.md` — §Step 2 `synthesized_position` row: major update.
- `research/extraction-contract-roadmap.md` — PR #3 status transitions.
- `research/stability-runs/contract-phase3-pre-ship-<date>/` + `-post-ship-<date>/`.

### Notes

- **This is the biggest PR in the remaining roadmap.** Budget extra time for the `_map_to_critique_request` consumer check and the downstream-lane verification.
- Prompt addition risk: biggest of any remaining PR (~800 chars new content). Aggressive condensation required. Pre/post-measure pollution budget carefully.
- The PR does NOT change lane behavior. `_map_to_critique_request` must produce functionally equivalent `query` and `vanilla_answer` strings after this change.

## Instructions for Completing Tasks

As each sub-task completes, change `- [ ]` → `- [x]`.

## Acceptance Gate (from roadmap)

| Axis | Target |
|---|---|
| Cross-capture `stance` enum Jaccard (empty-excl) | ≥ 0.90 (1.0 is a WARNING per harness doctrine) |
| Cross-capture `latest_stance_text` similarity mean | ≥ 0.35 (vs pre-ship `synthesized_position` similarity 0.169) |
| Qualitative: `is_ambiguous` correctly flags tradeoff-presentation cases | yes (3 spot-checks; at least one Marcus capture should flag false, one should flag true if ambiguity exists) |
| Downstream `_map_to_critique_request` output functionally equivalent to today (string similarity ≥ 0.95 pre-vs-post on same extraction input, with only the synthesized_position shape varying) | yes (diff-test via archived JSONs) |
| Regression on other fields | no decrease > 0.03 |
| Fabricated count | 0 |
| Cost per extraction call | ≤ +10% |

## Tasks

- [ ] 0.0 Pre-flight
  - [ ] 0.1 Confirm PR #1 merged. (#1b, #4a, #4b not required for this PR.)
  - [ ] 0.2 Create branch.
  - [ ] 0.3 Grep for consumers: `grep -rn "synthesized_position" engine/ scripts/` — document every hit.
  - [ ] 0.4 For each hit outside `_map_to_critique_request`, note how it uses the field (as string? as dict?). List in task file below.

- [ ] 1.0 Design decisions (document here before writing code)
  - [ ] 1.1 Schema versioning choice (version vs immediate). Default: immediate. Document rationale if different.
  - [ ] 1.2 Final-turn-is-clarifying-question fallback. Default: Option A (declines_to_recommend + is_ambiguous true).
  - [ ] 1.3 Consumer inventory complete (from 0.3 + 0.4).

- [ ] 2.0 Stance enum validator (TDD)
  - [ ] 2.1 RED: test — `_validate_stance("recommends_action") is True`.
  - [ ] 2.2 GREEN: add `_validate_stance(value: str) -> bool` in `run_extract.py`. Constants list: `recommends_action`, `presents_tradeoffs`, `declines_to_recommend`.
  - [ ] 2.3 RED: tests for invalid values (`"yes"`, `""`, `None`, other).
  - [ ] 2.4 GREEN: verify.
  - [ ] 2.5 RED: tests for post-processing — given a payload with a Position object where stance is invalid, the validator sets stance to `"declines_to_recommend"` (safe fallback) and emits a capture_warning.
  - [ ] 2.6 GREEN: add `_apply_position_validation(payload, capture_warnings)` — validates stance, coerces invalid to fallback.

- [ ] 3.0 `_map_to_critique_request` updates (TDD)
  - [ ] 3.1 RED: test — given an old-shape payload (synthesized_position as string), `_map_to_critique_request(payload)` still produces a valid query+vanilla_answer (backward compat for transition).
    - Decision: if we go "immediate breaking change," skip this test; the PR assumes all inputs are new-shape.
  - [ ] 3.2 RED: test — given a new-shape payload (Position object), `_map_to_critique_request(payload)` produces `vanilla_answer` containing `latest_stance_text` + superseded_stances summary + full assistant text. Format should match what today's string-form produces character-for-character on equivalent input.
  - [ ] 3.3 GREEN: update `_map_to_critique_request` to read the Position object. Build `vanilla_answer` with: `"SYNTHESIZED POSITION:\n" + position.latest_stance_text + "\n\nSUPERSEDED STANCES:\n" + <formatted superseded list> + "\n\nFULL ASSISTANT REASONING:\n" + assistant_text`.
  - [ ] 3.4 RED: diff-test — run the new `_map_to_critique_request` on a hand-built Position object derived from a PR #1b archive JSON. Compare to the string produced by today's path on the equivalent string-form input. Similarity should be ≥ 0.95 on the synthesized_position preamble section.
  - [ ] 3.5 GREEN: refine string formatting until the diff-test passes.

- [ ] 4.0 Draft the Position prompt block (condensed, budget-balanced)
  - [ ] 4.1 Current `3. "synthesized_position"` block is ~250 chars. Target new version: ≤ 600 chars (it's structurally bigger so this is a real increase — mitigation is that most of those chars are unavoidable: object shape + 3 subfields + 2 rules).
  - [ ] 4.2 Draft example:
    ```
    3. "synthesized_position": object with four fields:
       - "stance": exactly one of "recommends_action" | "presents_tradeoffs" | "declines_to_recommend"
       - "latest_stance_text": the stance expressed in the FINAL assistant
         turn (mechanical rule — NOT "most developed"). ≤300 chars.
       - "superseded_stances": array of {turn: int, stance_text: str,
         superseded_reason: str} objects for AI positions abandoned
         earlier in the conversation. Empty array if none.
       - "is_ambiguous": true if the final turn presents tradeoffs
         without a recommendation; false otherwise.
    ```
  - [ ] 4.3 Share with user for review before committing.
  - [ ] 4.4 Apply the edit.

- [ ] 5.0 Update downstream consumers
  - [ ] 5.1 Apply updates to any consumers identified in 0.3/0.4. Most should already be absorbed by `_map_to_critique_request` changes. Confirm by running any downstream tests.

- [ ] 6.0 Extend drift harness for Position shape (TDD)
  - [ ] 6.1 RED: test — when two extractions have matching `stance` values, the pair's `synthesized_position_stance.jaccard == 1.0`.
  - [ ] 6.2 GREEN: extend `compute_extraction_drift` to compute stance Jaccard (reuse `_list_jaccard_keyed_nonempty` with key = `lambda x: x.get("stance", "")`). Handle shape-check (if synthesized_position is a string, mark as `{"stance": None}` for backward compat or skip).
  - [ ] 6.3 RED: test — `latest_stance_text` similarity appears in pair + aggregate.
  - [ ] 6.4 GREEN: extend similarity computation for the new subfield.
  - [ ] 6.5 Update `render_drift_markdown` to render the new Position metrics.

- [ ] 7.0 Update HOW_IT_WORKS.md
  - [ ] 7.1 Major rewrite of the `synthesized_position` table row — new field shape, mechanical-rule anchor, 4 subfields.

- [ ] 8.0 Pre-ship baseline + post-ship acceptance gate
  - [ ] 8.1 Create evidence dirs.
  - [ ] 8.2 Pre-ship baseline: reuse PR #1b / #2 / #4a / #4b shipped-state cross-capture output (whichever is most recent).
  - [ ] 8.3 Post-ship: Mode C N=5 + 9-capture cross-run + cross-capture drift via `--from-extractions`.
  - [ ] 8.4 Diff-test `_map_to_critique_request`: hand-pick 3 archived JSONs; run through new + old mapper; compare output similarity (≥ 0.95 expected).
  - [ ] 8.5 Check every gate axis. If stance Jaccard = 1.0, investigate — may indicate mechanical rule is too simple and collapsing variance trivially.
  - [ ] 8.6 Qualitative: read 3 post-ship extractions. Confirm Position object shape, mechanical rule holding, is_ambiguous assigned correctly.

- [ ] 9.0 Ship or pause
  - [ ] 9.1 If all axes pass: commit, push, open PR.
  - [ ] 9.2 If consumers broke: revert the Position shape, ship in smaller pieces.
  - [ ] 9.3 If pollution budget failed: STOP. Condense the prompt further.

- [ ] 10.0 PR metadata
  - [ ] 10.1 PR title: `feat(extract): synthesized_position as Position object with mechanical stance anchor (phase 3)`.
  - [ ] 10.2 PR description: includes the `_map_to_critique_request` diff-test results prominently (reviewers will worry about downstream impact).
