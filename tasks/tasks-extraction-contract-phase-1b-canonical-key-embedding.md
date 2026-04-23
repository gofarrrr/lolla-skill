# PR #1b: Extraction Contract — canonical_key field + embedding-cosine metric

**Branch:** `feat/extraction-contract-phase-1b-canonical-key-embedding`
**Roadmap:** `research/extraction-contract-roadmap.md` → PR #1b
**Normative spec:** `research/extraction-contract-observations-2026-04-22.md` → `live_constraints` section
**Blocks:** PR #2 (needs canonical_key pattern proven with an honest metric before applying to dropped_threads)
**Blocked on:** PR #1 merged to main
**Scope:** Reintroduce `canonical_key` field in extraction output (condensed prompt addition) + add embedding-cosine metric to the stability harness + update acceptance-gate to cite the embedding metric as canonical_key primary axis. Preserve the PR #1 ≤120-char rule untouched. PR #1 already shipped the validator + field-level infrastructure.

## Why this PR exists (context for cold-start sessions)

PR #1 originally bundled ≤120-char rule + canonical_key into one ship. The canonical_key half failed its acceptance gate:
- Format rule was fine (0% invalid slugs), but LLM oscillated between semantically-equivalent valid slugs (`marcus-comp` vs `marcus-comp-below-market` vs `marcus-comp-undermarket`).
- Prompt text caused context pollution (fabricated quotes 0→3, `original_framing` similarity regression).
- Measurement metric (exact-text Jaccard) was wrong for semantically-equivalent slugs.

PR #1 was re-scoped to C-medium (stripped canonical_key prompt rules; kept validator + harness infrastructure pre-wired). PR #1b picks up the canonical_key ambition with two fixes:
1. **Condensed prompt addition** to avoid re-triggering pollution. Target budget: ~40% of the original canonical_key prompt block's character count.
2. **Embedding-cosine metric** (industry pattern: EDC, Zep, Kamradt). Semantic agreement measurement that sees `marcus-comp` and `marcus-comp-below-market` as highly similar, unlike exact-text Jaccard.

## Testing approach

Red-green-refactor TDD for the pure-function components:

1. **Embedding-cosine helper** (`scripts/stability_check.py`) — pure function given model pinned. Test with synthetic slug pairs for known behavior.
2. **Canonical_key embedding Jaccard / mean-cosine** — drift-metric extension.
3. **Condensed prompt text** — NOT TDD (validated empirically by acceptance gate).

## Design decisions to answer at task start

These are non-obvious and require a short conversation with the user (or a documented self-decision if autonomous):

1. **Local sentence-transformer vs remote embedding API?**
   - Local: `sentence-transformers/all-MiniLM-L6-v2` (~90MB model). Free, fast, no network. Adds dependency.
   - Remote: OpenAI `text-embedding-3-small` ($0.00002/1K tokens; ~$0.0001 per slug). No local deps; minor API cost.
   - Recommendation lean: **local** — avoids adding API dependency to the harness; acceptance gate is on-demand and CI-friendly.

2. **Embedding-cluster-then-Jaccard vs pairwise mean cosine?**
   - Cluster-then-Jaccard: run clustering (e.g., threshold 0.85 cosine), treat each cluster as an "item," compute Jaccard on clustered sets. More Jaccard-like; more threshold tuning.
   - Pairwise mean cosine: for each pair of slugs across runs, compute cosine; report mean/min/max. Simpler; no threshold.
   - Recommendation lean: **pairwise mean cosine primary + clustered-Jaccard as secondary diagnostic.** Pairwise is the simpler cleaner number for a gate; clustered helps interpretability.

3. **Condensed prompt text — what to strip from the PR #1 original?**
   - Original canonical_key block was ~600 chars including examples. Target condensed: ≤250 chars.
   - Keep: the naming-the-subject rule, one worked example, the 2-4 token format.
   - Strip: the multi-bullet "rules" list, the "how would I index this?" prose.
   - Example condensed (proposed; to be reviewed at task start):
     ```
     - "canonical_key": 2-4 token slug (lowercase, hyphens, letters+digits)
       naming THE THING this constraint is about, independent of phrasing.
       Example: "marcus-comp-below-market". Same concept across runs must
       produce the same key.
     ```
     That's ~280 chars. Tighter pass should get under 250.

## Relevant Files

- `scripts/run_extract.py` — reintroduce condensed canonical_key block in `EXTRACTION_SYSTEM_PROMPT`. `_validate_canonical_key` + `_apply_canonical_key_validation` already exist from PR #1.
- `scripts/stability_check.py` — add embedding-cosine helper (`_compute_embedding_cosine`), extend `compute_extraction_drift` with `live_constraints_canonical_key_embedding` metrics, extend `render_drift_markdown` to include embedding rows.
- `tests/test_stability_check.py` — NEW tests for embedding helper + drift metric extension.
- `tests/test_run_extract.py` — unchanged (validator + post-processing already tested in PR #1).
- `HOW_IT_WORKS.md` — §Step 2 `live_constraints` row: note `canonical_key` is now emitted and measured via embedding cosine.
- `research/extraction-contract-roadmap.md` — PR #1b status `NOT STARTED` → `IN PROGRESS` → `SHIPPED`.
- `research/stability-runs/contract-phase1b-pre-ship-<date>/` — baseline with PR #1 shipped state (current main after PR #13 merges). Canonical_key metric undefined here (no field).
- `research/stability-runs/contract-phase1b-post-ship-<date>/` — post-ship evidence.

### Notes

- Test runner: `python3 -m pytest tests/test_<file>.py -v`.
- Embedding model choice: **pin the version** in code. Cosine scores drift slightly across model updates.
- Cost: if remote embedding API is chosen, each full cross-capture run embeds ~50 slugs total × $0.00002 = negligible (< $0.01 per gate run).
- This PR uses the PR #1 diagnostic extraction JSONs as its pre-ship baseline's comparison point on non-canonical-key fields (i.e., same 9 Marcus captures; canonical_key column was N/A in those).

## Instructions for Completing Tasks

As each sub-task completes, change `- [ ]` → `- [x]` in this file. Update the file after each sub-task, not in batches.

## Acceptance Gate (from roadmap)

| Axis | Target |
|---|---|
| Cross-capture `canonical_key` embedding cosine mean | ≥ 0.70 |
| Cross-capture `canonical_key` embedding cosine min | ≥ 0.50 |
| `invalid_key_rate` overall | ≤ 10% |
| Regression on `original_framing` similarity (sentinel for pollution) | no decrease vs PR #1 baseline (0.218 cross-capture) |
| Regression on fabricated count | always 0 across 9 runs |
| Regression on other fields | no decrease > 0.03 |
| Cost per extraction call | ≤ +10% vs PR #1 shipped state |
| Qualitative: canonical_keys read as stable identifiers | yes (3 spot-checks) |

## Tasks

- [ ] 0.0 Pre-flight — confirm PR #1 merged; branch from fresh main
  - [ ] 0.1 Confirm PR #13 merged: `git checkout main && git pull && git log --oneline -5` shows the PR #1 merge commit.
  - [ ] 0.2 Create branch: `git checkout -b feat/extraction-contract-phase-1b-canonical-key-embedding`.
  - [ ] 0.3 Verify `_validate_canonical_key` and `_apply_canonical_key_validation` exist in `scripts/run_extract.py` (carried from PR #1).
  - [ ] 0.4 Verify harness `--from-extractions` mode + canonical_key Jaccard + `invalid_key_rate` exist in `scripts/stability_check.py`.

- [x] 1.0 Design decisions — DOCUMENTED
  - [x] 1.1 Embedding source: **OpenAI `text-embedding-3-small` via existing `openai` Python client.** Rationale: `sentence-transformers` not installed; installing adds ~500MB; `openai` v2.29.0 already present; `OPENAI_API_KEY` already in `.env`; existing `boundary_provider.py` has OpenAI class method; cost is negligible (~$0.00005 per slug).
  - [x] 1.2 Metric form: **pairwise mean cosine primary.** Clustered Jaccard deferred (simpler primary number is better for a gate).
  - [x] 1.3 Condensed canonical_key prompt text: draft below, ~240 chars. Applied in task 4.3.

- [ ] 2.0 Add embedding-cosine infrastructure (TDD)
  - [ ] 2.1 Install dependency if needed: `pip install sentence-transformers` (or document OpenAI SDK path).
  - [ ] 2.2 RED: write test in `tests/test_stability_check.py` — `_compute_embedding_cosine("marcus-comp", "marcus-comp")` returns 1.0 (self-similarity sanity).
  - [ ] 2.3 GREEN: add `_compute_embedding_cosine(a: str, b: str, model=<pinned>) -> float` to `scripts/stability_check.py`. Lazy-load the model on first call (cache at module level). Use numpy for cosine or sentence-transformers' built-in.
  - [ ] 2.4 RED: write test — `_compute_embedding_cosine("marcus-comp", "marcus-comp-below-market")` returns a value > 0.75 (semantically close).
  - [ ] 2.5 GREEN: verify (should pass by model behavior; no code change needed).
  - [ ] 2.6 RED: write test — `_compute_embedding_cosine("marcus-comp", "platform-prototype")` returns a value < 0.75 (different concepts).
  - [ ] 2.7 GREEN: verify.
  - [ ] 2.8 RED: write test — `_compute_embedding_mean_for_lists(["marcus-comp", "marcus-equity"], ["marcus-comp", "marcus-equity"]) == 1.0` (identical lists produce full match).
  - [ ] 2.9 GREEN: add `_compute_embedding_mean_for_lists(a, b)` helper. For each pair (one from a, one from b), compute cosine. Return mean of best-match cosines (greedy matching — each item from a matched to its highest-cosine partner in b).
  - [ ] 2.10 RED: write test for lists of different lengths — short list is matched greedily; longer list's unmatched items penalize by counting as 0 against the longer-list size.
  - [ ] 2.11 GREEN: refine the function per the test.

- [ ] 3.0 Extend compute_extraction_drift with canonical_key embedding metric (TDD)
  - [ ] 3.1 RED: write test — when two extraction dicts have live_constraints with overlapping canonical_keys (semantically equivalent but exactly matching), the pair's `live_constraints_canonical_key_embedding` mean_cosine ≥ 0.99.
  - [ ] 3.2 GREEN: extend `compute_extraction_drift`'s per-pair block to compute `live_constraints_canonical_key_embedding` via `_compute_embedding_mean_for_lists` on the canonical_key lists (filter empties before comparison).
  - [ ] 3.3 RED: write test — when lists contain semantically-equivalent-but-surface-different slugs (`marcus-comp` vs `marcus-comp-below-market`), the mean cosine is ≥ 0.75.
  - [ ] 3.4 GREEN: verify (should pass by model behavior).
  - [ ] 3.5 RED: write test — aggregate result contains `live_constraints_canonical_key_embedding` block with mean/min/max across all pairs.
  - [ ] 3.6 GREEN: extend the aggregate computation block.
  - [ ] 3.7 Extend `render_drift_markdown` to render the new embedding metric in the aggregate table + per-pair block.

- [ ] 4.0 Reintroduce canonical_key prompt text — condensed (manual; empirical via gate)
  - [ ] 4.1 Read PR #1's original canonical_key block from git history (diff of commit `3340a24`).
  - [ ] 4.2 Draft condensed version (~250 chars). Share with user for approval before committing if interactive.
  - [ ] 4.3 Apply the edit to `scripts/run_extract.py` EXTRACTION_SYSTEM_PROMPT. Keep it directly above the `constraint` subfield so the validator flow is natural.
  - [ ] 4.4 Run `python3 -m pytest tests/ -v` — full suite green.

- [ ] 5.0 Update HOW_IT_WORKS.md §Step 2 live_constraints row
  - [ ] 5.1 Update the row to note canonical_key is emitted and measured via embedding cosine (PR #1 row had noted the field shape is prepared; this PR ships the field itself).

- [ ] 6.0 Pre-ship baseline + post-ship acceptance gate
  - [ ] 6.1 Create directories: `mkdir -p research/stability-runs/contract-phase1b-pre-ship-<date>/{modec-n5,cross-capture,cross-capture-drift}` and same for `-post-ship-`.
  - [ ] 6.2 Pre-ship baseline: run extractor on 9 Marcus captures with the current branch state MINUS the canonical_key prompt addition (so it's == PR #1 shipped state). **Shortcut**: if PR #1 diagnostic files are still in `research/stability-runs/contract-phase1-diagnostic-2026-04-23/cross-capture/`, reuse them. Otherwise re-run.
  - [ ] 6.3 Post-ship: apply the canonical_key prompt addition (task 4.3 result). Run Mode C N=5 on newest capture + extract on 9 Marcus captures + cross-capture drift via `--from-extractions`.
  - [ ] 6.4 Compare all fields against pre-ship. Check every acceptance-gate axis.
  - [ ] 6.5 If ANY axis fails (especially original_framing sentinel): STOP. Update the roadmap PR #1b section with failure note. Share findings with user. Do NOT silently iterate.
  - [ ] 6.6 Qualitative spot-check: read 3 extractions, confirm canonical_keys read as stable identifiers in context.

- [ ] 7.0 Commit + PR
  - [ ] 7.1 Flip roadmap status to `IN REVIEW`.
  - [ ] 7.2 Commit evidence + roadmap update.
  - [ ] 7.3 Push + open PR with title `feat(extract): canonical_key field + embedding-cosine metric (phase 1b)`.
  - [ ] 7.4 PR description links to pre-ship and post-ship evidence directories; states gate results explicitly; applies the honesty clause.
  - [ ] 7.5 On merge: flip roadmap to `SHIPPED (commit: <merge-hash>)`.
