# PR #1: Extraction Contract — live_constraints.canonical_key

**Branch:** `feat/extraction-contract-phase-1-live-constraints`
**Roadmap:** `research/extraction-contract-roadmap.md` → PR #1
**Normative spec:** `research/extraction-contract-observations-2026-04-22.md` → `live_constraints` section
**Scope:** Add `canonical_key` field to each `Constraint`, canonical-phrasing rule on `constraint` text (≤120 chars), Python-side slug validator, and Mode C harness metrics (canonical_key Jaccard with empty-string exclusion + `invalid_key_rate`).

## Testing approach

Red-green-refactor TDD for the two deterministic Python components:

1. **Slug validator** (`run_extract.py`) — pure function, regex-based. Classic TDD fit.
2. **Extended drift metrics** (`stability_check.py`) — empty-string-aware Jaccard, `invalid_key_rate`, cross-capture aggregation. Pure functions, testable with synthetic extraction dicts.

**Not** TDD'd:

- Prompt text changes — validated empirically by the Mode C acceptance gate. Unit-testing prompt text against mocked LLM output would test the mock, not the prompt.
- Schema addition — data structure change; behavior is LLM-side.
- HOW_IT_WORKS.md edit — documentation.

## Relevant Files

- `scripts/run_extract.py` — Modify `EXTRACTION_SYSTEM_PROMPT` (lines 130–213) to add canonical_key rule + ≤120-char constraint rule; add `_validate_canonical_key()` regex-based validator; invoke validator after extraction, drop invalid keys to empty string, append `capture_warning` listing offenders.
- `scripts/stability_check.py` — Extend `compute_extraction_drift()` (lines 389–481) with canonical_key Jaccard (empty-string exclusion) + `invalid_key_rate`; extend `render_drift_markdown()` (lines 484–528) with new rows; add a cross-capture CLI mode that takes pre-extracted JSON paths and reuses `compute_extraction_drift`.
- `tests/test_run_extract.py` — **NEW** — unit tests for `_validate_canonical_key()` and the invalid-key-to-empty-string post-processing.
- `tests/test_stability_check.py` — **NEW** — unit tests for the empty-string-aware Jaccard, `invalid_key_rate` computation, and cross-capture aggregation on synthetic extraction dicts.
- `HOW_IT_WORKS.md` — §Step 2 `live_constraints` row gains a `canonical_key` subfield note.
- `research/extraction-contract-roadmap.md` — PR #1 status: `NOT STARTED` → `IN PROGRESS` (at branch creation) → `SHIPPED (commit: <hash>)` (at merge).
- `research/stability-runs/contract-phase1-pre-ship-2026-04-22/` — pre-ship baseline evidence: Mode C N=5 drift.json + 9-capture cross-capture drift.json + summary markdown.
- `research/stability-runs/contract-phase1-post-ship-2026-04-22/` — post-ship acceptance-gate evidence, same shape as pre-ship.

### Notes

- Test runner: `python3 -m pytest tests/test_<file>.py -v`.
- **Do NOT create the branch until task 0.0 is complete.** The baseline must run against the current extractor on `main`.
- **Acceptance gate is not a formality.** If any axis fails (task 5.3), pause, diagnose, and update the roadmap PR #1 section with the failure. Do NOT silently iterate on the prompt hoping numbers move.
- The 9 Marcus captures for the cross-capture axis are under `/tmp/lolla_2026042[12]T*_conversation.txt`. The synthetic capture (`lolla_synthetic_critical_conversation.txt`) is excluded.
- Newest capture for Mode C N=5: `/tmp/lolla_20260422T155622Z_conversation.txt`.
- Regex choice for canonical_key: `^[a-z][a-z0-9]+(-[a-z0-9]+){1,3}$`. Letter-first requirement is deliberate (common case) — slugs like `401k-vesting-risk` fail this and would need iteration; noted in code comment at the validator.

## Instructions for Completing Tasks

**IMPORTANT:** As you complete each task, you must check it off in this markdown file by changing `- [ ]` to `- [x]`. This helps track progress and ensures you don't skip any steps.

Example:
- `- [ ] 1.1 Read file` → `- [x] 1.1 Read file` (after completing)

Update the file after completing each sub-task, not just after completing an entire parent task.

## Acceptance Gate (from roadmap)

| Axis | Target |
|---|---|
| Mode C N=5, `live_constraints.canonical_key` Jaccard (empty-excl) | ≥ 0.80 |
| Mode C N=5 + cross-capture, `invalid_key_rate` | ≤ 10% |
| Cross-capture (9 captures), `canonical_key` Jaccard (empty-excl) | ≥ 0.70 |
| Qualitative: canonical_keys read as stable identifiers | yes (3 spot-checks) |
| Regression: other fields' similarity/Jaccard | no decrease vs pre-ship baseline |
| Regression: `live_constraints.constraint` exact-text Jaccard | no decrease vs pre-ship baseline (bonus: tightening is allowed) |
| Cost delta per extraction call | ≤ +10% |

## Tasks

- [x] 0.0 Run pre-ship baseline on `main` (current extractor, both metrics)
  - [x] 0.1 Verify you're on `main` with a clean working tree: `git status` shows only the expected untracked research/ files from prior work. Abort if `git branch --show-current` is not `main`.
  - [x] 0.2 Create output directories: `mkdir -p research/stability-runs/contract-phase1-pre-ship-2026-04-22/{modec-n5,cross-capture}`
  - [x] 0.3 Run Mode C N=5 on the newest capture against the current extractor: `python3 scripts/stability_check.py --drift --conversation /tmp/lolla_20260422T155622Z_conversation.txt -n 5 --case-id contract-phase1-pre-ship --output-dir research/stability-runs/contract-phase1-pre-ship-2026-04-22/modec-n5/`. Confirm `drift.json` + `drift.md` + `runs.txt` + `config.json` are written.
  - [x] 0.4 Run the current extractor once per Marcus capture. For each of the 9 captures under `/tmp/lolla_2026042[12]T*_conversation.txt` (exclude the synthetic one): `python3 scripts/run_extract.py --conversation-file <capture> --output-file research/stability-runs/contract-phase1-pre-ship-2026-04-22/cross-capture/extraction_<run_id>.json`. Preserve the run_id in the filename.
  - [x] 0.5 Write a one-off analysis script at `research/stability-runs/contract-phase1-pre-ship-2026-04-22/compute_cross_capture.py` that imports `compute_extraction_drift` and `render_drift_markdown` from `scripts.stability_check`, loads all 9 extraction JSONs from the `cross-capture/` directory, calls `compute_extraction_drift`, and writes `drift.json` + `drift.md` to the cross-capture directory. Run it.
  - [x] 0.6 Verify the pre-ship extraction JSONs do NOT contain `canonical_key` on any constraint (this confirms the baseline reflects pre-ship state). A single `grep -l "canonical_key" research/stability-runs/contract-phase1-pre-ship-2026-04-22/cross-capture/*.json` should return nothing.
  - [x] 0.7 Write `research/stability-runs/contract-phase1-pre-ship-2026-04-22/README.md` summarizing: Mode C N=5 means (per field) + cross-capture means (per field) + baseline capture count per run + note that canonical_key is absent so no canonical_key baseline exists (baseline for canonical_key = undefined, first measurement is post-ship).
  - [x] 0.8 Share the baseline numbers with the user before proceeding. Do NOT start the branch until the user has seen the baseline.

- [x] 1.0 Create feature branch and flip roadmap status to `IN PROGRESS`
  - [x] 1.1 Create and checkout the branch: `git checkout -b feat/extraction-contract-phase-1-live-constraints`
  - [x] 1.2 Stage and commit the pre-ship baseline evidence on the new branch: `git add research/stability-runs/contract-phase1-pre-ship-2026-04-22/` then `git commit -m "baseline: pre-ship Mode C N=5 + 9-capture cross-run"`.
  - [x] 1.3 Edit `research/extraction-contract-roadmap.md` PR #1 section: change status `NOT STARTED` → `IN PROGRESS`.
  - [x] 1.4 Commit roadmap update: `git commit -am "docs: flip PR #1 to IN PROGRESS"`

- [x] 2.0 Extend Mode C harness — canonical_key Jaccard (empty-excl) + `invalid_key_rate` + cross-capture aggregation mode (TDD)
  - [x] 2.1 Read `scripts/stability_check.py` — study `compute_extraction_drift()` (lines 389–481) particularly the `live_constraints` block (lines 419–425), the aggregate computation (lines 456–469), and `render_drift_markdown()` (lines 484–528). Also `jaccard()` (lines 162–167) and `_list_jaccard_keyed()` (lines 348–357).
  - [x] 2.2 RED: Write test in `tests/test_stability_check.py` — given two extraction dicts where both have 3 constraints with matching `canonical_key` values (non-empty), `compute_extraction_drift` returns a `live_constraints_canonical_key` Jaccard of 1.0 for that pair.
  - [x] 2.3 GREEN: Extend `compute_extraction_drift()`'s per-pair block to compute `live_constraints_canonical_key` Jaccard. Key: `lambda c: (c.get("canonical_key", "") or "").strip().lower()`. Filter out items where the key is empty BEFORE set construction in a new helper `_list_jaccard_keyed_nonempty(a, b, key)` (or inline the filter). Record per-pair in the `pair` dict.
  - [x] 2.4 RED: Write test — when run A has 3 constraints all with valid non-empty canonical_keys and run B has 3 constraints where 2 have empty canonical_key, the Jaccard considers only the single valid key on both sides. Do NOT match-by-absence: two empty-keyed constraints must NOT count as a trivial match.
  - [x] 2.5 GREEN: Verify the nonempty filter handles this. If the test fails, the filter is set-wrong — fix it so empty-string items are dropped from both sets before intersection.
  - [x] 2.6 RED: Write test — when both runs have ALL canonical_keys empty (full-degenerate case), the per-pair `live_constraints_canonical_key` Jaccard is reported as `None` (undefined), not 1.0. `invalid_key_rate` captures the "why" in this case.
  - [x] 2.7 GREEN: Handle the both-empty case in the keyer — if both filtered sets are empty, return `None` for the canonical_key metric.
  - [x] 2.8 RED: Write test — the aggregate result has a `live_constraints_canonical_key` block with `mean_jaccard` / `min_jaccard` / `max_jaccard`, skipping None pairs from aggregation.
  - [x] 2.9 GREEN: Extend the aggregate computation (near line 463) to include canonical_key Jaccard aggregates, filtering None values before mean/min/max.
  - [x] 2.10 RED: Write test — `compute_extraction_drift` returns `invalid_key_rate_per_run` list: for a run with 5 constraints where 1 has empty canonical_key (after python-side validation), rate = 0.2.
  - [x] 2.11 GREEN: Add `invalid_key_rate_per_run` computation in the aggregate section — iterate each run's `live_constraints`, count constraints with missing or empty-string `canonical_key`, divide by total. Store as a list aligned with run_ids.
  - [x] 2.12 RED: Write test — aggregate result contains `invalid_key_rate_overall` = (sum of invalid keys across all runs) / (sum of total constraints across all runs).
  - [x] 2.13 GREEN: Add the overall aggregate computation.
  - [x] 2.14 RED: Write test — `compute_extraction_drift` works with N ≥ 2 input extractions regardless of whether they came from the same conversation (i.e. it does not assume single-conversation input). [Implicitly covered — all unit tests use synthetic extractions not bound to a single conversation.]
  - [x] 2.15 GREEN: This should already pass — the function operates on a list of tuples and has no conversation-identity coupling. Verify by running the test.
  - [x] 2.16 Add new CLI mode `--from-extractions` to `scripts/stability_check.py`'s argparse. Takes `nargs="*"` space-separated extraction JSON paths. Loads each via `_load_extraction`, pairs each with a run_id via `_run_id_from_extraction_path`, then calls `compute_extraction_drift` and writes `drift.json` + `drift.md` + `runs.txt` + `config.json` to the output directory. Reuses existing functions (no new business logic).
  - [x] 2.17 Extend `render_drift_markdown()` to render the new metrics: add a `canonical_key` row in the aggregate table with jaccard mean/min/max; add an `invalid_key_rate_per_run` line + `invalid_key_rate_overall` line below the table; add per-pair canonical_key Jaccard in the pairwise detail block. Update the "Reading the metrics" section to mention the empty-string exclusion rule.
  - [x] 2.18 REFACTOR: Run `python3 -m pytest tests/test_stability_check.py -v`. Confirm all tests green. Run against the 9 pre-ship extraction JSONs from task 0.5 to spot-check that the new CLI mode produces the same drift.json content as the ad-hoc script did (canonical_key will be None/undefined because no pre-ship extraction had the field, which is the correct answer).
  - [x] 2.19 Commit: `git add scripts/stability_check.py tests/test_stability_check.py && git commit -m "feat(stability): canonical_key Jaccard (empty-excl) + invalid_key_rate + --from-extractions mode"`.

- [x] 3.0 Extend `run_extract.py` — prompt canonical-form rule, schema addition, Python-side slug validator (TDD for validator)
  - [x] 3.1 Read `scripts/run_extract.py` — study `EXTRACTION_SYSTEM_PROMPT` (lines 130–213, particularly the `live_constraints` block at lines 161–171) and the existing post-extraction validation pattern for `reasoning_passages` (lines 546–612) to follow the same shape for canonical_key validation.
  - [x] 3.2 RED: Write test in `tests/test_run_extract.py` — `_validate_canonical_key("marcus-comp-below-market")` returns True.
  - [x] 3.3 GREEN: Add `_validate_canonical_key(key: str) -> bool` at module level in `run_extract.py`. Regex: `^[a-z][a-z0-9]+(-[a-z0-9]+){1,3}$`. Compile once at module level for efficiency. Add a one-line comment at the regex: `# letter-first + lowercase only by design; "401k-vesting-risk" and friends fail and will be iterated on if a real case needs them.`
  - [x] 3.4 RED: Write tests for invalid inputs that should all return False — `"UPPERCASE"`, `"only-one-token"` (0 hyphens), `"a-b-c-d-e-f"` (5 tokens, too many), `""` (empty), `"has_underscore"`, `"has space"`, `"-leading-hyphen"`, `"trailing-hyphen-"`, `"double--hyphen"`, `"a-b"` (first token only 1 char).
  - [x] 3.5 GREEN: Verify the regex rejects all of them. Adjust regex if any slip through.
  - [x] 3.6 RED: Write a test for the 2-token minimum boundary — `"marcus-comp"` (2 tokens, first token ≥2 chars) returns True.
  - [x] 3.7 GREEN: Verify the regex allows this.
  - [x] 3.8 RED: Write a test for the 4-token maximum boundary — `"marcus-comp-below-market"` (4 tokens) returns True; `"marcus-comp-below-market-rate"` (5 tokens) returns False.
  - [x] 3.9 GREEN: Verify.
  - [x] 3.10 RED: Write test for the post-extraction flow — given a mock payload with 3 live_constraints (one with valid canonical_key, one with invalid canonical_key `"BAD-KEY"`, one missing the field entirely), after running the validator pass, the valid one keeps its key, the invalid is set to `""`, and the missing stays missing. Additionally, a `capture_warning` listing the offenders is appended.
  - [x] 3.11 GREEN: In `main()` after the `_quote_validation` block (~line 612), add a validator pass over `payload.get("live_constraints", [])`. For each constraint: if `canonical_key` key is present and `_validate_canonical_key(value)` is False, record the bad value, set to `""`. Append one `capture_warning` summarizing the invalid keys if any were found.
  - [x] 3.12 RED: Write test — if all canonical_keys are valid, no capture_warning is added and all keys are preserved.
  - [x] 3.13 GREEN: Verify the conditional emission.
  - [x] 3.14 REFACTOR: Run `python3 -m pytest tests/test_run_extract.py -v`. Confirm all green. Run the full suite `python3 -m pytest tests/ -v` to confirm no regression.
  - [x] 3.15 Read the current `EXTRACTION_SYSTEM_PROMPT` live_constraints block (lines 161–171) and draft the updated version. Changes: (a) add `canonical_key` as the FIRST subfield with the 2-4 token rule + examples, (b) add the ≤120-char terse noun-phrase-+-state rule on `constraint` text. Keep `introduced_turn`, `status`, `weight` unchanged.
  - [x] 3.16 **Propose the updated prompt text + schema diff to the user for review BEFORE committing.** Do not proceed to 3.17 until the user approves the exact wording. This is a blocking review gate per the user's original flow.
  - [x] 3.17 After approval: apply the prompt edit to `scripts/run_extract.py` and commit: `git add scripts/run_extract.py && git commit -m "feat(extract): add canonical_key + ≤120-char constraint rule to live_constraints"`.

- [x] 4.0 Update `HOW_IT_WORKS.md` §Step 2 `live_constraints` description
  - [x] 4.1 Read HOW_IT_WORKS.md lines 380–400 — the Step 2 field table and the paragraph immediately after.
  - [x] 4.2 Edit the `live_constraints` row in the field table to add a note about the new `canonical_key` subfield: its purpose (stable cross-run identity), its format (2–4 token slug), and why it matters (decouples concept from phrasing so drift metrics measure concept stability, not paraphrase). Preserve the existing "killer feature of conversation mode" framing.
  - [x] 4.3 If no further narrative update is needed (the table row change is sufficient), skip. If the immediately surrounding paragraphs reference constraint phrasing in a way that now contradicts the ≤120-char rule, update them to match.
  - [x] 4.4 Commit: `git add HOW_IT_WORKS.md && git commit -m "docs: add canonical_key note to HOW_IT_WORKS live_constraints"`.

- [ ] 5.0 Run post-ship acceptance gate; if all axes pass, open PR and flip roadmap to `SHIPPED`
  - [x] 5.1 Create output directories: `mkdir -p research/stability-runs/contract-phase1-post-ship-2026-04-22/{modec-n5,cross-capture}`
  - [x] 5.2 Run Mode C N=5 on the newest capture against the NEW extractor: `python3 scripts/stability_check.py --drift --conversation /tmp/lolla_20260422T155622Z_conversation.txt -n 5 --case-id contract-phase1-post-ship --output-dir research/stability-runs/contract-phase1-post-ship-2026-04-22/modec-n5/`. Confirm the drift.md shows `canonical_key` Jaccard + `invalid_key_rate_overall`.
  - [x] 5.3 Run the new extractor on each of the 9 Marcus captures: `python3 scripts/run_extract.py --conversation-file <capture> --output-file research/stability-runs/contract-phase1-post-ship-2026-04-22/cross-capture/extraction_<run_id>.json` for each.
  - [x] 5.4 Compute cross-capture drift via the new CLI mode: `python3 scripts/stability_check.py --from-extractions research/stability-runs/contract-phase1-post-ship-2026-04-22/cross-capture/extraction_*.json --case-id contract-phase1-post-ship-cross --output-dir research/stability-runs/contract-phase1-post-ship-2026-04-22/cross-capture-drift/`. Confirm drift.md includes all new metrics.
  - [x] 5.5 Compare each axis against the acceptance gate table at the top of this file: Mode C canonical_key Jaccard ≥ 0.80; Mode C + cross-capture invalid_key_rate ≤ 10%; cross-capture canonical_key Jaccard ≥ 0.70; no regression on the other fields' similarity/Jaccard vs pre-ship; `live_constraints.constraint` exact-text Jaccard not decreased vs pre-ship; cost per extraction call ≤ +10%.
  - [x] 5.6 Qualitative spot-check: open 3 extraction JSONs (from cross-capture/). For each, confirm the canonical_keys read as stable identifiers (same concept → same key across runs). Write findings to `research/stability-runs/contract-phase1-post-ship-2026-04-22/qualitative-spot-check.md`.
  - [x] 5.7 Write `research/stability-runs/contract-phase1-post-ship-2026-04-22/README.md`: acceptance-gate table showing target vs actual for every axis + pre-ship vs post-ship comparison for regression fields. This is what the PR description links to.
  - [x] 5.8 **If ANY axis fails**: STOP. Do not proceed to PR. Update `research/extraction-contract-roadmap.md` PR #1 section with a failure note (which axis, measured value, hypothesis). Share findings with the user. Do NOT silently iterate on the prompt. → GATE HIT — canonical_key Jaccard 0.466 Mode C / 0.332 cross-capture, both below target. Surfaced to user.
  - [x] 5.9 ~~If all axes pass: commit the post-ship evidence~~ → Gate failed; executed diagnostic C-medium path instead: stripped canonical_key prompt rules, re-measured, confirmed context-pollution theory, committed diagnostic evidence.
  - [x] 5.10 ~~Ask the user for approval before pushing~~ → User approved C-medium ship after diagnostic findings.
  - [x] 5.11 Push the branch: `git push -u origin feat/extraction-contract-phase-1-live-constraints`.
  - [x] 5.12 Open PR — https://github.com/gofarrrr/lolla-skill/pull/13. Title: `feat(extract): live_constraints terse canonical form (phase 1)`. C-medium scope.
  - [ ] 5.13 After merge: flip roadmap PR #1 status `IN REVIEW` → `SHIPPED (commit: <merge-hash>)`. Schedule PR #1b for canonical_key field + embedding metric.
