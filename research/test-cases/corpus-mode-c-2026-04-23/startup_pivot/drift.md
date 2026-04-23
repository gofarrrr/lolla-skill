# Extraction drift report — corpus-startup_pivot

Generated: 2026-04-23T10:18:03Z
Conversation: `/private/tmp/lolla_case_startup_pivot_conversation.txt` (8363 bytes)
Runs: 3
Run IDs: 20260423T101803Zdrift0, 20260423T101811Zdrift1, 20260423T101818Zdrift2

**Reading the metrics:**
- Free-text fields (`decision_situation`, `original_framing`, `synthesized_position`) — difflib SequenceMatcher ratio (character-level). 1.0 = identical; 0.7+ = very similar; 0.4–0.7 = material drift (paraphrase or reshape); <0.4 = shape-shift.
- List fields (`live_constraints`, `reasoning_passages`, `dropped_threads`) — Jaccard on normalized item text (strip, lowercase).
- `live_constraints_canonical_key` — Jaccard on `canonical_key` slugs with empty-string exclusion: empty/missing keys are filtered from BOTH sets before intersection so two failed extractions do not trivially match. A pair with all-empty keys on both sides is reported as `—` (undefined); the failure rate lives in `invalid_key_rate`.
- `invalid_key_rate` — share of constraints where `canonical_key` is missing or empty (the LLM failed the slug format rule). Per-run + overall. Acceptance gate target: ≤ 10%.
- `fabricated_count_per_run` — passages the extractor marked as not-a-literal-substring. Higher is worse.

## Aggregate drift

| Field | Metric | Mean | Min | Max |
|---|---|---|---|---|
| `decision_situation` | similarity | 0.989 | 0.983 | 1.000 |
| `original_framing` | similarity | 0.563 | 0.474 | 0.688 |
| `synthesized_position` | similarity | 0.318 | 0.198 | 0.452 |
| `live_constraints` | jaccard | 0.370 | 0.222 | 0.667 |
| `reasoning_passages` | jaccard | 0.333 | 0.000 | 1.000 |
| `dropped_threads` | jaccard | 0.333 | 0.000 | 1.000 |
| `live_constraints_canonical_key` | jaccard (empty-excl) | — | — | — |
> `live_constraints_canonical_key` has 3 undefined pair(s) — both runs had no valid canonical_keys. See `invalid_key_rate` below.
| `live_constraints_canonical_key_embedding` | cosine (empty-excl) | — | — | — |

**`invalid_key_rate` per run:** [1.0, 1.0, 1.0]
**`invalid_key_rate` overall:** 1.000 (16 invalid of 16 total constraints)
**Fabricated-quote counts per run:** [0, 6, 6]
**Capture health per run:** ['good', 'good', 'good']

## Pairwise detail

### `20260423T101803Zdrift0` vs `20260423T101811Zdrift1`
- **decision_situation**: similarity=1.000, lengths 147 ↔ 147
- **original_framing**: similarity=0.688, lengths 193 ↔ 147
- **synthesized_position**: similarity=0.198, lengths 421 ↔ 488
- **live_constraints**: jaccard=0.222, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.000, counts 8 ↔ 0
- **dropped_threads**: jaccard=1.000, counts 0 ↔ 0
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=6

### `20260423T101803Zdrift0` vs `20260423T101818Zdrift2`
- **decision_situation**: similarity=0.983, lengths 147 ↔ 146
- **original_framing**: similarity=0.474, lengths 193 ↔ 199
- **synthesized_position**: similarity=0.452, lengths 421 ↔ 509
- **live_constraints**: jaccard=0.222, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.000, counts 8 ↔ 0
- **dropped_threads**: jaccard=0.000, counts 0 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=6

### `20260423T101811Zdrift1` vs `20260423T101818Zdrift2`
- **decision_situation**: similarity=0.983, lengths 147 ↔ 146
- **original_framing**: similarity=0.526, lengths 147 ↔ 199
- **synthesized_position**: similarity=0.305, lengths 488 ↔ 509
- **live_constraints**: jaccard=0.667, counts 5 ↔ 5
- **reasoning_passages**: jaccard=1.000, counts 0 ↔ 0
- **dropped_threads**: jaccard=0.000, counts 0 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=6, b=6
