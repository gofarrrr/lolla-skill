# Extraction drift report — contract-phase2-cross

Generated: 2026-04-23T09:16:52Z
Conversation: `cross-capture (no single conversation)` (? bytes)
Runs: 9
Run IDs: extraction_20260421T144534Z, extraction_20260421T162225Z, extraction_20260421T172513Z, extraction_20260422T091837Z, extraction_20260422T100308Z, extraction_20260422T113930Z, extraction_20260422T123205Z, extraction_20260422T130506Z, extraction_20260422T155622Z

**Reading the metrics:**
- Free-text fields (`decision_situation`, `original_framing`, `synthesized_position`) — difflib SequenceMatcher ratio (character-level). 1.0 = identical; 0.7+ = very similar; 0.4–0.7 = material drift (paraphrase or reshape); <0.4 = shape-shift.
- List fields (`live_constraints`, `reasoning_passages`, `dropped_threads`) — Jaccard on normalized item text (strip, lowercase).
- `live_constraints_canonical_key` — Jaccard on `canonical_key` slugs with empty-string exclusion: empty/missing keys are filtered from BOTH sets before intersection so two failed extractions do not trivially match. A pair with all-empty keys on both sides is reported as `—` (undefined); the failure rate lives in `invalid_key_rate`.
- `invalid_key_rate` — share of constraints where `canonical_key` is missing or empty (the LLM failed the slug format rule). Per-run + overall. Acceptance gate target: ≤ 10%.
- `fabricated_count_per_run` — passages the extractor marked as not-a-literal-substring. Higher is worse.

## Aggregate drift

| Field | Metric | Mean | Min | Max |
|---|---|---|---|---|
| `decision_situation` | similarity | 0.833 | 0.623 | 1.000 |
| `original_framing` | similarity | 0.337 | 0.048 | 0.728 |
| `synthesized_position` | similarity | 0.166 | 0.004 | 0.382 |
| `live_constraints` | jaccard | 0.261 | 0.000 | 1.000 |
| `reasoning_passages` | jaccard | 0.401 | 0.091 | 0.714 |
| `dropped_threads` | jaccard | 0.278 | 0.000 | 1.000 |
| `live_constraints_canonical_key` | jaccard (empty-excl) | — | — | — |
> `live_constraints_canonical_key` has 36 undefined pair(s) — both runs had no valid canonical_keys. See `invalid_key_rate` below.
| `live_constraints_canonical_key_embedding` | cosine (empty-excl) | — | — | — |

**`invalid_key_rate` per run:** [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
**`invalid_key_rate` overall:** 1.000 (50 invalid of 50 total constraints)
**Fabricated-quote counts per run:** [0, 0, 0, 0, 0, 0, 0, 0, 0]
**Capture health per run:** ['good', 'good', 'good', 'good', 'good', 'good', 'good', 'good', 'good']

## Pairwise detail

### `extraction_20260421T144534Z` vs `extraction_20260421T162225Z`
- **decision_situation**: similarity=0.805, lengths 138 ↔ 180
- **original_framing**: similarity=0.244, lengths 198 ↔ 237
- **synthesized_position**: similarity=0.006, lengths 799 ↔ 561
- **live_constraints**: jaccard=0.375, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.091, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260421T172513Z`
- **decision_situation**: similarity=0.688, lengths 138 ↔ 144
- **original_framing**: similarity=0.367, lengths 198 ↔ 145
- **synthesized_position**: similarity=0.011, lengths 799 ↔ 461
- **live_constraints**: jaccard=0.222, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.222, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T091837Z`
- **decision_situation**: similarity=1.000, lengths 138 ↔ 138
- **original_framing**: similarity=0.278, lengths 198 ↔ 226
- **synthesized_position**: similarity=0.004, lengths 799 ↔ 625
- **live_constraints**: jaccard=0.100, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.333, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T100308Z`
- **decision_situation**: similarity=1.000, lengths 138 ↔ 138
- **original_framing**: similarity=0.566, lengths 198 ↔ 180
- **synthesized_position**: similarity=0.037, lengths 799 ↔ 555
- **live_constraints**: jaccard=0.222, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.100, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T113930Z`
- **decision_situation**: similarity=1.000, lengths 138 ↔ 138
- **original_framing**: similarity=0.305, lengths 198 ↔ 222
- **synthesized_position**: similarity=0.018, lengths 799 ↔ 436
- **live_constraints**: jaccard=0.667, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.100, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.500, counts 1 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.891, lengths 138 ↔ 138
- **original_framing**: similarity=0.386, lengths 198 ↔ 237
- **synthesized_position**: similarity=0.013, lengths 799 ↔ 427
- **live_constraints**: jaccard=0.667, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.091, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.859, lengths 138 ↔ 160
- **original_framing**: similarity=0.255, lengths 198 ↔ 226
- **synthesized_position**: similarity=0.007, lengths 799 ↔ 720
- **live_constraints**: jaccard=0.000, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.100, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T144534Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.823, lengths 138 ↔ 122
- **original_framing**: similarity=0.213, lengths 198 ↔ 225
- **synthesized_position**: similarity=0.009, lengths 799 ↔ 476
- **live_constraints**: jaccard=0.429, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.091, counts 6 ↔ 6
- **dropped_threads**: jaccard=1.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260421T172513Z`
- **decision_situation**: similarity=0.722, lengths 180 ↔ 144
- **original_framing**: similarity=0.225, lengths 237 ↔ 145
- **synthesized_position**: similarity=0.149, lengths 561 ↔ 461
- **live_constraints**: jaccard=0.000, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.375, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.500, counts 2 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T091837Z`
- **decision_situation**: similarity=0.786, lengths 180 ↔ 138
- **original_framing**: similarity=0.501, lengths 237 ↔ 226
- **synthesized_position**: similarity=0.157, lengths 561 ↔ 625
- **live_constraints**: jaccard=0.200, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.333, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T100308Z`
- **decision_situation**: similarity=0.786, lengths 180 ↔ 138
- **original_framing**: similarity=0.724, lengths 237 ↔ 180
- **synthesized_position**: similarity=0.278, lengths 561 ↔ 555
- **live_constraints**: jaccard=0.000, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.571, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.500, counts 2 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T113930Z`
- **decision_situation**: similarity=0.786, lengths 180 ↔ 138
- **original_framing**: similarity=0.675, lengths 237 ↔ 222
- **synthesized_position**: similarity=0.279, lengths 561 ↔ 436
- **live_constraints**: jaccard=0.571, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.571, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.692, lengths 180 ↔ 138
- **original_framing**: similarity=0.321, lengths 237 ↔ 237
- **synthesized_position**: similarity=0.300, lengths 561 ↔ 427
- **live_constraints**: jaccard=0.375, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.714, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.500, counts 2 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.912, lengths 180 ↔ 160
- **original_framing**: similarity=0.518, lengths 237 ↔ 226
- **synthesized_position**: similarity=0.354, lengths 561 ↔ 720
- **live_constraints**: jaccard=0.000, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.375, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.500, counts 2 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T162225Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.623, lengths 180 ↔ 122
- **original_framing**: similarity=0.048, lengths 237 ↔ 225
- **synthesized_position**: similarity=0.260, lengths 561 ↔ 476
- **live_constraints**: jaccard=0.375, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.714, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T091837Z`
- **decision_situation**: similarity=0.688, lengths 144 ↔ 138
- **original_framing**: similarity=0.199, lengths 145 ↔ 226
- **synthesized_position**: similarity=0.122, lengths 461 ↔ 625
- **live_constraints**: jaccard=0.200, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.571, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T100308Z`
- **decision_situation**: similarity=0.688, lengths 144 ↔ 138
- **original_framing**: similarity=0.271, lengths 145 ↔ 180
- **synthesized_position**: similarity=0.382, lengths 461 ↔ 555
- **live_constraints**: jaccard=1.000, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.429, counts 5 ↔ 5
- **dropped_threads**: jaccard=1.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T113930Z`
- **decision_situation**: similarity=0.688, lengths 144 ↔ 138
- **original_framing**: similarity=0.196, lengths 145 ↔ 222
- **synthesized_position**: similarity=0.082, lengths 461 ↔ 436
- **live_constraints**: jaccard=0.100, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.429, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.794, lengths 144 ↔ 138
- **original_framing**: similarity=0.115, lengths 145 ↔ 237
- **synthesized_position**: similarity=0.164, lengths 461 ↔ 427
- **live_constraints**: jaccard=0.100, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.375, counts 5 ↔ 6
- **dropped_threads**: jaccard=1.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.803, lengths 144 ↔ 160
- **original_framing**: similarity=0.183, lengths 145 ↔ 226
- **synthesized_position**: similarity=0.141, lengths 461 ↔ 720
- **live_constraints**: jaccard=0.500, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.429, counts 5 ↔ 5
- **dropped_threads**: jaccard=1.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260421T172513Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.842, lengths 144 ↔ 122
- **original_framing**: similarity=0.162, lengths 145 ↔ 225
- **synthesized_position**: similarity=0.158, lengths 461 ↔ 476
- **live_constraints**: jaccard=0.100, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.375, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T091837Z` vs `extraction_20260422T100308Z`
- **decision_situation**: similarity=1.000, lengths 138 ↔ 138
- **original_framing**: similarity=0.685, lengths 226 ↔ 180
- **synthesized_position**: similarity=0.198, lengths 625 ↔ 555
- **live_constraints**: jaccard=0.200, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.375, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260422T091837Z` vs `extraction_20260422T113930Z`
- **decision_situation**: similarity=1.000, lengths 138 ↔ 138
- **original_framing**: similarity=0.728, lengths 226 ↔ 222
- **synthesized_position**: similarity=0.111, lengths 625 ↔ 436
- **live_constraints**: jaccard=0.222, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.375, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T091837Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.891, lengths 138 ↔ 138
- **original_framing**: similarity=0.320, lengths 226 ↔ 237
- **synthesized_position**: similarity=0.226, lengths 625 ↔ 427
- **live_constraints**: jaccard=0.100, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.333, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T091837Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.859, lengths 138 ↔ 160
- **original_framing**: similarity=0.527, lengths 226 ↔ 226
- **synthesized_position**: similarity=0.125, lengths 625 ↔ 720
- **live_constraints**: jaccard=0.333, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.375, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260422T091837Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.823, lengths 138 ↔ 122
- **original_framing**: similarity=0.182, lengths 226 ↔ 225
- **synthesized_position**: similarity=0.042, lengths 625 ↔ 476
- **live_constraints**: jaccard=0.000, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.333, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T100308Z` vs `extraction_20260422T113930Z`
- **decision_situation**: similarity=1.000, lengths 138 ↔ 138
- **original_framing**: similarity=0.373, lengths 180 ↔ 222
- **synthesized_position**: similarity=0.242, lengths 555 ↔ 436
- **live_constraints**: jaccard=0.100, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.667, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 2
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T100308Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.891, lengths 138 ↔ 138
- **original_framing**: similarity=0.293, lengths 180 ↔ 237
- **synthesized_position**: similarity=0.246, lengths 555 ↔ 427
- **live_constraints**: jaccard=0.100, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.571, counts 5 ↔ 6
- **dropped_threads**: jaccard=1.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T100308Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.859, lengths 138 ↔ 160
- **original_framing**: similarity=0.488, lengths 180 ↔ 226
- **synthesized_position**: similarity=0.249, lengths 555 ↔ 720
- **live_constraints**: jaccard=0.500, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.429, counts 5 ↔ 5
- **dropped_threads**: jaccard=1.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260422T100308Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.823, lengths 138 ↔ 122
- **original_framing**: similarity=0.198, lengths 180 ↔ 225
- **synthesized_position**: similarity=0.221, lengths 555 ↔ 476
- **live_constraints**: jaccard=0.100, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.571, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T113930Z` vs `extraction_20260422T123205Z`
- **decision_situation**: similarity=0.891, lengths 138 ↔ 138
- **original_framing**: similarity=0.266, lengths 222 ↔ 237
- **synthesized_position**: similarity=0.239, lengths 436 ↔ 427
- **live_constraints**: jaccard=0.667, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.571, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T113930Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.859, lengths 138 ↔ 160
- **original_framing**: similarity=0.451, lengths 222 ↔ 226
- **synthesized_position**: similarity=0.268, lengths 436 ↔ 720
- **live_constraints**: jaccard=0.000, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.429, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260422T113930Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.823, lengths 138 ↔ 122
- **original_framing**: similarity=0.152, lengths 222 ↔ 225
- **synthesized_position**: similarity=0.138, lengths 436 ↔ 476
- **live_constraints**: jaccard=0.429, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.571, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.500, counts 2 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T123205Z` vs `extraction_20260422T130506Z`
- **decision_situation**: similarity=0.758, lengths 138 ↔ 160
- **original_framing**: similarity=0.294, lengths 237 ↔ 226
- **synthesized_position**: similarity=0.316, lengths 427 ↔ 720
- **live_constraints**: jaccard=0.000, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.375, counts 6 ↔ 5
- **dropped_threads**: jaccard=1.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `extraction_20260422T123205Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.938, lengths 138 ↔ 122
- **original_framing**: similarity=0.173, lengths 237 ↔ 225
- **synthesized_position**: similarity=0.275, lengths 427 ↔ 476
- **live_constraints**: jaccard=0.429, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.714, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `extraction_20260422T130506Z` vs `extraction_20260422T155622Z`
- **decision_situation**: similarity=0.688, lengths 160 ↔ 122
- **original_framing**: similarity=0.239, lengths 226 ↔ 225
- **synthesized_position**: similarity=0.132, lengths 720 ↔ 476
- **live_constraints**: jaccard=0.000, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.375, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 1 ↔ 1
- **live_constraints_canonical_key**: jaccard=undefined (both-empty), counts 6 ↔ 5
- **fabricated**: a=0, b=0
