# Extraction drift report — corpus-multi_offer

Generated: 2026-04-23T10:18:50Z
Conversation: `/private/tmp/lolla_case_multi_offer_conversation.txt` (15787 bytes)
Runs: 3
Run IDs: 20260423T101850Zdrift0, 20260423T101856Zdrift1, 20260423T101901Zdrift2

**Reading the metrics:**
- Free-text fields (`decision_situation`, `original_framing`, `synthesized_position`) — difflib SequenceMatcher ratio (character-level). 1.0 = identical; 0.7+ = very similar; 0.4–0.7 = material drift (paraphrase or reshape); <0.4 = shape-shift.
- List fields (`live_constraints`, `reasoning_passages`, `dropped_threads`) — Jaccard on normalized item text (strip, lowercase).
- `live_constraints_canonical_key` — Jaccard on `canonical_key` slugs with empty-string exclusion: empty/missing keys are filtered from BOTH sets before intersection so two failed extractions do not trivially match. A pair with all-empty keys on both sides is reported as `—` (undefined); the failure rate lives in `invalid_key_rate`.
- `invalid_key_rate` — share of constraints where `canonical_key` is missing or empty (the LLM failed the slug format rule). Per-run + overall. Acceptance gate target: ≤ 10%.
- `fabricated_count_per_run` — passages the extractor marked as not-a-literal-substring. Higher is worse.

## Aggregate drift

| Field | Metric | Mean | Min | Max |
|---|---|---|---|---|
| `decision_situation` | similarity | 0.942 | 0.913 | 1.000 |
| `original_framing` | similarity | 0.948 | 0.922 | 0.977 |
| `synthesized_position` | similarity | 0.124 | 0.077 | 0.193 |
| `live_constraints` | jaccard | 0.667 | 0.500 | 1.000 |
| `reasoning_passages` | jaccard | 0.524 | 0.286 | 1.000 |
| `dropped_threads` | jaccard | 0.333 | 0.000 | 1.000 |
| `live_constraints_canonical_key` | jaccard (empty-excl) | — | — | — |
> `live_constraints_canonical_key` has 3 undefined pair(s) — both runs had no valid canonical_keys. See `invalid_key_rate` below.
| `live_constraints_canonical_key_embedding` | cosine (empty-excl) | — | — | — |

**`invalid_key_rate` per run:** [1.0, 1.0, 1.0]
**`invalid_key_rate` overall:** 1.000 (18 invalid of 18 total constraints)
**Fabricated-quote counts per run:** [0, 0, 0]
**Capture health per run:** ['good', 'good', 'good']

## Pairwise detail

### `20260423T101850Zdrift0` vs `20260423T101856Zdrift1`
- **decision_situation**: similarity=1.000, lengths 187 ↔ 187
- **original_framing**: similarity=0.946, lengths 267 ↔ 270
- **synthesized_position**: similarity=0.102, lengths 592 ↔ 521
- **live_constraints**: jaccard=1.000, counts 6 ↔ 6
- **reasoning_passages**: jaccard=1.000, counts 4 ↔ 4
- **dropped_threads**: jaccard=1.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `20260423T101850Zdrift0` vs `20260423T101901Zdrift2`
- **decision_situation**: similarity=0.913, lengths 187 ↔ 205
- **original_framing**: similarity=0.922, lengths 267 ↔ 258
- **synthesized_position**: similarity=0.077, lengths 592 ↔ 714
- **live_constraints**: jaccard=0.500, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.286, counts 4 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `20260423T101856Zdrift1` vs `20260423T101901Zdrift2`
- **decision_situation**: similarity=0.913, lengths 187 ↔ 205
- **original_framing**: similarity=0.977, lengths 270 ↔ 258
- **synthesized_position**: similarity=0.193, lengths 521 ↔ 714
- **live_constraints**: jaccard=0.500, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.286, counts 4 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 6
- **fabricated**: a=0, b=0
