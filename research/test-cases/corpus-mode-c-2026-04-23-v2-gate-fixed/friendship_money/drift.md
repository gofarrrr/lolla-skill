# Extraction drift report — corpus-v2-friendship_money

Generated: 2026-04-23T10:29:27Z
Conversation: `/private/tmp/lolla_case_friendship_money_conversation.txt` (9306 bytes)
Runs: 3
Run IDs: 20260423T102927Zdrift0, 20260423T102932Zdrift1, 20260423T102937Zdrift2

**Reading the metrics:**
- Free-text fields (`decision_situation`, `original_framing`, `synthesized_position`) — difflib SequenceMatcher ratio (character-level). 1.0 = identical; 0.7+ = very similar; 0.4–0.7 = material drift (paraphrase or reshape); <0.4 = shape-shift.
- List fields (`live_constraints`, `reasoning_passages`, `dropped_threads`) — Jaccard on normalized item text (strip, lowercase).
- `live_constraints_canonical_key` — Jaccard on `canonical_key` slugs with empty-string exclusion: empty/missing keys are filtered from BOTH sets before intersection so two failed extractions do not trivially match. A pair with all-empty keys on both sides is reported as `—` (undefined); the failure rate lives in `invalid_key_rate`.
- `invalid_key_rate` — share of constraints where `canonical_key` is missing or empty (the LLM failed the slug format rule). Per-run + overall. Acceptance gate target: ≤ 10%.
- `fabricated_count_per_run` — passages the extractor marked as not-a-literal-substring. Higher is worse.

## Aggregate drift

| Field | Metric | Mean | Min | Max |
|---|---|---|---|---|
| `decision_situation` | similarity | 1.000 | 1.000 | 1.000 |
| `original_framing` | similarity | 0.866 | 0.791 | 0.990 |
| `synthesized_position` | similarity | 0.496 | 0.439 | 0.596 |
| `live_constraints` | jaccard | 0.733 | 0.600 | 1.000 |
| `reasoning_passages` | jaccard | 0.619 | 0.571 | 0.714 |
| `dropped_threads` | jaccard | 0.000 | 0.000 | 0.000 |
| `live_constraints_canonical_key` | jaccard (empty-excl) | — | — | — |
> `live_constraints_canonical_key` has 3 undefined pair(s) — both runs had no valid canonical_keys. See `invalid_key_rate` below.
| `live_constraints_canonical_key_embedding` | cosine (empty-excl) | — | — | — |

**`invalid_key_rate` per run:** [1.0, 1.0, 1.0]
**`invalid_key_rate` overall:** 1.000 (12 invalid of 12 total constraints)
**Fabricated-quote counts per run:** [0, 0, 0]
**Capture health per run:** ['good', 'good', 'good']

## Pairwise detail

### `20260423T102927Zdrift0` vs `20260423T102932Zdrift1`
- **decision_situation**: similarity=1.000, lengths 132 ↔ 132
- **original_framing**: similarity=0.791, lengths 194 ↔ 193
- **synthesized_position**: similarity=0.596, lengths 322 ↔ 302
- **live_constraints**: jaccard=0.600, counts 4 ↔ 4
- **reasoning_passages**: jaccard=0.571, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 4 ↔ 4
- **fabricated**: a=0, b=0

### `20260423T102927Zdrift0` vs `20260423T102937Zdrift2`
- **decision_situation**: similarity=1.000, lengths 132 ↔ 132
- **original_framing**: similarity=0.990, lengths 194 ↔ 192
- **synthesized_position**: similarity=0.439, lengths 322 ↔ 311
- **live_constraints**: jaccard=1.000, counts 4 ↔ 4
- **reasoning_passages**: jaccard=0.714, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 4 ↔ 4
- **fabricated**: a=0, b=0

### `20260423T102932Zdrift1` vs `20260423T102937Zdrift2`
- **decision_situation**: similarity=1.000, lengths 132 ↔ 132
- **original_framing**: similarity=0.816, lengths 193 ↔ 192
- **synthesized_position**: similarity=0.454, lengths 302 ↔ 311
- **live_constraints**: jaccard=0.600, counts 4 ↔ 4
- **reasoning_passages**: jaccard=0.571, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 4 ↔ 4
- **fabricated**: a=0, b=0
