# Extraction drift report — contract-phase4b-post-ship

Generated: 2026-04-23T09:10:54Z
Conversation: `/private/tmp/lolla_20260422T155622Z_conversation.txt` (26304 bytes)
Runs: 5
Run IDs: 20260423T091054Zdrift0, 20260423T091104Zdrift1, 20260423T091116Zdrift2, 20260423T091128Zdrift3, 20260423T091134Zdrift4

**Reading the metrics:**
- Free-text fields (`decision_situation`, `original_framing`, `synthesized_position`) — difflib SequenceMatcher ratio (character-level). 1.0 = identical; 0.7+ = very similar; 0.4–0.7 = material drift (paraphrase or reshape); <0.4 = shape-shift.
- List fields (`live_constraints`, `reasoning_passages`, `dropped_threads`) — Jaccard on normalized item text (strip, lowercase).
- `live_constraints_canonical_key` — Jaccard on `canonical_key` slugs with empty-string exclusion: empty/missing keys are filtered from BOTH sets before intersection so two failed extractions do not trivially match. A pair with all-empty keys on both sides is reported as `—` (undefined); the failure rate lives in `invalid_key_rate`.
- `invalid_key_rate` — share of constraints where `canonical_key` is missing or empty (the LLM failed the slug format rule). Per-run + overall. Acceptance gate target: ≤ 10%.
- `fabricated_count_per_run` — passages the extractor marked as not-a-literal-substring. Higher is worse.

## Aggregate drift

| Field | Metric | Mean | Min | Max |
|---|---|---|---|---|
| `decision_situation` | similarity | 0.827 | 0.688 | 1.000 |
| `original_framing` | similarity | 0.551 | 0.265 | 0.921 |
| `synthesized_position` | similarity | 0.362 | 0.156 | 0.693 |
| `live_constraints` | jaccard | 0.359 | 0.100 | 0.833 |
| `reasoning_passages` | jaccard | 0.294 | 0.200 | 0.500 |
| `dropped_threads` | jaccard | 0.070 | 0.000 | 0.250 |
| `live_constraints_canonical_key` | jaccard (empty-excl) | — | — | — |
> `live_constraints_canonical_key` has 10 undefined pair(s) — both runs had no valid canonical_keys. See `invalid_key_rate` below.
| `live_constraints_canonical_key_embedding` | cosine (empty-excl) | — | — | — |

**`invalid_key_rate` per run:** [1.0, 1.0, 1.0, 1.0, 1.0]
**`invalid_key_rate` overall:** 1.000 (27 invalid of 27 total constraints)
**Fabricated-quote counts per run:** [0, 0, 0, 0, 0]
**Capture health per run:** ['good', 'good', 'good', 'good', 'good']

## Pairwise detail

### `20260423T091054Zdrift0` vs `20260423T091104Zdrift1`
- **decision_situation**: similarity=0.794, lengths 144 ↔ 138
- **original_framing**: similarity=0.617, lengths 210 ↔ 176
- **synthesized_position**: similarity=0.693, lengths 530 ↔ 547
- **live_constraints**: jaccard=0.100, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.333, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.250, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `20260423T091054Zdrift0` vs `20260423T091116Zdrift2`
- **decision_situation**: similarity=0.896, lengths 144 ↔ 144
- **original_framing**: similarity=0.790, lengths 210 ↔ 205
- **synthesized_position**: similarity=0.369, lengths 530 ↔ 474
- **live_constraints**: jaccard=0.250, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.333, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.200, counts 3 ↔ 3
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `20260423T091054Zdrift0` vs `20260423T091128Zdrift3`
- **decision_situation**: similarity=0.932, lengths 144 ↔ 165
- **original_framing**: similarity=0.848, lengths 210 ↔ 186
- **synthesized_position**: similarity=0.156, lengths 530 ↔ 691
- **live_constraints**: jaccard=0.375, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.222, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `20260423T091054Zdrift0` vs `20260423T091134Zdrift4`
- **decision_situation**: similarity=0.794, lengths 144 ↔ 138
- **original_framing**: similarity=0.272, lengths 210 ↔ 239
- **synthesized_position**: similarity=0.392, lengths 530 ↔ 546
- **live_constraints**: jaccard=0.429, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.333, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `20260423T091104Zdrift1` vs `20260423T091116Zdrift2`
- **decision_situation**: similarity=0.688, lengths 138 ↔ 144
- **original_framing**: similarity=0.541, lengths 176 ↔ 205
- **synthesized_position**: similarity=0.204, lengths 547 ↔ 474
- **live_constraints**: jaccard=0.375, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.500, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 3
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `20260423T091104Zdrift1` vs `20260423T091128Zdrift3`
- **decision_situation**: similarity=0.825, lengths 138 ↔ 165
- **original_framing**: similarity=0.691, lengths 176 ↔ 186
- **synthesized_position**: similarity=0.205, lengths 547 ↔ 691
- **live_constraints**: jaccard=0.200, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.222, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `20260423T091104Zdrift1` vs `20260423T091134Zdrift4`
- **decision_situation**: similarity=1.000, lengths 138 ↔ 138
- **original_framing**: similarity=0.265, lengths 176 ↔ 239
- **synthesized_position**: similarity=0.434, lengths 547 ↔ 546
- **live_constraints**: jaccard=0.222, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.200, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `20260423T091116Zdrift2` vs `20260423T091128Zdrift3`
- **decision_situation**: similarity=0.835, lengths 144 ↔ 165
- **original_framing**: similarity=0.921, lengths 205 ↔ 186
- **synthesized_position**: similarity=0.182, lengths 474 ↔ 691
- **live_constraints**: jaccard=0.375, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.222, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.250, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `20260423T091116Zdrift2` vs `20260423T091134Zdrift4`
- **decision_situation**: similarity=0.688, lengths 144 ↔ 138
- **original_framing**: similarity=0.284, lengths 205 ↔ 239
- **synthesized_position**: similarity=0.457, lengths 474 ↔ 546
- **live_constraints**: jaccard=0.429, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.200, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `20260423T091128Zdrift3` vs `20260423T091134Zdrift4`
- **decision_situation**: similarity=0.818, lengths 165 ↔ 138
- **original_framing**: similarity=0.278, lengths 186 ↔ 239
- **synthesized_position**: similarity=0.525, lengths 691 ↔ 546
- **live_constraints**: jaccard=0.833, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.375, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0
