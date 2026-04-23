# Extraction drift report — contract-phase1b-post-ship

Generated: 2026-04-23T08:52:32Z
Conversation: `/private/tmp/lolla_20260422T155622Z_conversation.txt` (26304 bytes)
Runs: 5
Run IDs: 20260423T085232Zdrift0, 20260423T085244Zdrift1, 20260423T085252Zdrift2, 20260423T085259Zdrift3, 20260423T085311Zdrift4

**Reading the metrics:**
- Free-text fields (`decision_situation`, `original_framing`, `synthesized_position`) — difflib SequenceMatcher ratio (character-level). 1.0 = identical; 0.7+ = very similar; 0.4–0.7 = material drift (paraphrase or reshape); <0.4 = shape-shift.
- List fields (`live_constraints`, `reasoning_passages`, `dropped_threads`) — Jaccard on normalized item text (strip, lowercase).
- `live_constraints_canonical_key` — Jaccard on `canonical_key` slugs with empty-string exclusion: empty/missing keys are filtered from BOTH sets before intersection so two failed extractions do not trivially match. A pair with all-empty keys on both sides is reported as `—` (undefined); the failure rate lives in `invalid_key_rate`.
- `invalid_key_rate` — share of constraints where `canonical_key` is missing or empty (the LLM failed the slug format rule). Per-run + overall. Acceptance gate target: ≤ 10%.
- `fabricated_count_per_run` — passages the extractor marked as not-a-literal-substring. Higher is worse.

## Aggregate drift

| Field | Metric | Mean | Min | Max |
|---|---|---|---|---|
| `decision_situation` | similarity | 0.467 | 0.192 | 0.844 |
| `original_framing` | similarity | 0.166 | 0.080 | 0.393 |
| `synthesized_position` | similarity | 0.451 | 0.189 | 0.758 |
| `live_constraints` | jaccard | 0.042 | 0.000 | 0.111 |
| `reasoning_passages` | jaccard | 0.335 | 0.200 | 0.667 |
| `dropped_threads` | jaccard | 0.033 | 0.000 | 0.333 |
| `live_constraints_canonical_key` | jaccard (empty-excl) | 0.688 | 0.571 | 1.000 |
| `live_constraints_canonical_key_embedding` | cosine (empty-excl) | 0.848 | 0.740 | 1.000 |

**`invalid_key_rate` per run:** [0.0, 0.0, 0.0, 0.0, 0.0]
**`invalid_key_rate` overall:** 0.000 (0 invalid of 26 total constraints)
**Fabricated-quote counts per run:** [0, 0, 0, 0, 0]
**Capture health per run:** ['good', 'good', 'good', 'good', 'good']

## Pairwise detail

### `20260423T085232Zdrift0` vs `20260423T085244Zdrift1`
- **decision_situation**: similarity=0.493, lengths 285 ↔ 490
- **original_framing**: similarity=0.393, lengths 297 ↔ 426
- **synthesized_position**: similarity=0.672, lengths 581 ↔ 683
- **live_constraints**: jaccard=0.111, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.375, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.667, counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `20260423T085232Zdrift0` vs `20260423T085252Zdrift2`
- **decision_situation**: similarity=0.262, lengths 285 ↔ 516
- **original_framing**: similarity=0.199, lengths 297 ↔ 396
- **synthesized_position**: similarity=0.246, lengths 581 ↔ 826
- **live_constraints**: jaccard=0.100, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.222, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.333, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.833, counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `20260423T085232Zdrift0` vs `20260423T085259Zdrift3`
- **decision_situation**: similarity=0.768, lengths 285 ↔ 288
- **original_framing**: similarity=0.209, lengths 297 ↔ 286
- **synthesized_position**: similarity=0.758, lengths 581 ↔ 545
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.300, counts 6 ↔ 7
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.667, counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `20260423T085232Zdrift0` vs `20260423T085311Zdrift4`
- **decision_situation**: similarity=0.799, lengths 285 ↔ 271
- **original_framing**: similarity=0.117, lengths 297 ↔ 299
- **synthesized_position**: similarity=0.589, lengths 581 ↔ 515
- **live_constraints**: jaccard=0.111, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.200, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.667, counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `20260423T085244Zdrift1` vs `20260423T085252Zdrift2`
- **decision_situation**: similarity=0.249, lengths 490 ↔ 516
- **original_framing**: similarity=0.158, lengths 426 ↔ 396
- **synthesized_position**: similarity=0.297, lengths 683 ↔ 826
- **live_constraints**: jaccard=0.100, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.667, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.571, counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `20260423T085244Zdrift1` vs `20260423T085259Zdrift3`
- **decision_situation**: similarity=0.442, lengths 490 ↔ 288
- **original_framing**: similarity=0.110, lengths 426 ↔ 286
- **synthesized_position**: similarity=0.550, lengths 683 ↔ 545
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.333, counts 5 ↔ 7
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.667, counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `20260423T085244Zdrift1` vs `20260423T085311Zdrift4`
- **decision_situation**: similarity=0.397, lengths 490 ↔ 271
- **original_framing**: similarity=0.080, lengths 426 ↔ 299
- **synthesized_position**: similarity=0.457, lengths 683 ↔ 515
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.375, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=1.000, counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `20260423T085252Zdrift2` vs `20260423T085259Zdrift3`
- **decision_situation**: similarity=0.192, lengths 516 ↔ 288
- **original_framing**: similarity=0.141, lengths 396 ↔ 286
- **synthesized_position**: similarity=0.248, lengths 826 ↔ 545
- **live_constraints**: jaccard=0.000, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.200, counts 5 ↔ 7
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.571, counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `20260423T085252Zdrift2` vs `20260423T085311Zdrift4`
- **decision_situation**: similarity=0.219, lengths 516 ↔ 271
- **original_framing**: similarity=0.081, lengths 396 ↔ 299
- **synthesized_position**: similarity=0.189, lengths 826 ↔ 515
- **live_constraints**: jaccard=0.000, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.375, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.571, counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `20260423T085259Zdrift3` vs `20260423T085311Zdrift4`
- **decision_situation**: similarity=0.844, lengths 288 ↔ 271
- **original_framing**: similarity=0.171, lengths 286 ↔ 299
- **synthesized_position**: similarity=0.500, lengths 545 ↔ 515
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.300, counts 7 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.667, counts 5 ↔ 5
- **fabricated**: a=0, b=0
