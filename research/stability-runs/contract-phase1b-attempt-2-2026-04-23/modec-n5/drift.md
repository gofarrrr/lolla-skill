# Extraction drift report — contract-phase1b-iter2

Generated: 2026-04-23T08:59:48Z
Conversation: `/private/tmp/lolla_20260422T155622Z_conversation.txt` (26304 bytes)
Runs: 5
Run IDs: 20260423T085948Zdrift0, 20260423T085954Zdrift1, 20260423T090006Zdrift2, 20260423T090020Zdrift3, 20260423T090028Zdrift4

**Reading the metrics:**
- Free-text fields (`decision_situation`, `original_framing`, `synthesized_position`) — difflib SequenceMatcher ratio (character-level). 1.0 = identical; 0.7+ = very similar; 0.4–0.7 = material drift (paraphrase or reshape); <0.4 = shape-shift.
- List fields (`live_constraints`, `reasoning_passages`, `dropped_threads`) — Jaccard on normalized item text (strip, lowercase).
- `live_constraints_canonical_key` — Jaccard on `canonical_key` slugs with empty-string exclusion: empty/missing keys are filtered from BOTH sets before intersection so two failed extractions do not trivially match. A pair with all-empty keys on both sides is reported as `—` (undefined); the failure rate lives in `invalid_key_rate`.
- `invalid_key_rate` — share of constraints where `canonical_key` is missing or empty (the LLM failed the slug format rule). Per-run + overall. Acceptance gate target: ≤ 10%.
- `fabricated_count_per_run` — passages the extractor marked as not-a-literal-substring. Higher is worse.

## Aggregate drift

| Field | Metric | Mean | Min | Max |
|---|---|---|---|---|
| `decision_situation` | similarity | 0.237 | 0.068 | 0.701 |
| `original_framing` | similarity | 0.099 | 0.036 | 0.223 |
| `synthesized_position` | similarity | 0.272 | 0.125 | 0.491 |
| `live_constraints` | jaccard | 0.022 | 0.000 | 0.222 |
| `reasoning_passages` | jaccard | 0.330 | 0.200 | 0.571 |
| `dropped_threads` | jaccard | 0.058 | 0.000 | 0.333 |
| `live_constraints_canonical_key` | jaccard (empty-excl) | 0.292 | 0.100 | 0.571 |
| `live_constraints_canonical_key_embedding` | cosine (empty-excl) | 0.679 | 0.550 | 0.823 |

**`invalid_key_rate` per run:** [0.0, 0.0, 0.0, 0.167, 0.0]
**`invalid_key_rate` overall:** 0.036 (1 invalid of 28 total constraints)
**Fabricated-quote counts per run:** [0, 0, 0, 0, 0]
**Capture health per run:** ['good', 'good', 'good', 'good', 'good']

## Pairwise detail

### `20260423T085948Zdrift0` vs `20260423T085954Zdrift1`
- **decision_situation**: similarity=0.135, lengths 393 ↔ 275
- **original_framing**: similarity=0.073, lengths 397 ↔ 292
- **synthesized_position**: similarity=0.125, lengths 679 ↔ 442
- **live_constraints**: jaccard=0.000, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.222, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.250, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.429, counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `20260423T085948Zdrift0` vs `20260423T090006Zdrift2`
- **decision_situation**: similarity=0.453, lengths 393 ↔ 472
- **original_framing**: similarity=0.063, lengths 397 ↔ 394
- **synthesized_position**: similarity=0.310, lengths 679 ↔ 806
- **live_constraints**: jaccard=0.000, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.222, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.571, counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `20260423T085948Zdrift0` vs `20260423T090020Zdrift3`
- **decision_situation**: similarity=0.272, lengths 393 ↔ 527
- **original_framing**: similarity=0.068, lengths 397 ↔ 394
- **synthesized_position**: similarity=0.292, lengths 679 ↔ 959
- **live_constraints**: jaccard=0.000, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.429, counts 5 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.111, counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `20260423T085948Zdrift0` vs `20260423T090028Zdrift4`
- **decision_situation**: similarity=0.130, lengths 393 ↔ 301
- **original_framing**: similarity=0.083, lengths 397 ↔ 323
- **synthesized_position**: similarity=0.180, lengths 679 ↔ 673
- **live_constraints**: jaccard=0.000, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.222, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 3 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.571, counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `20260423T085954Zdrift1` vs `20260423T090006Zdrift2`
- **decision_situation**: similarity=0.118, lengths 275 ↔ 472
- **original_framing**: similarity=0.087, lengths 292 ↔ 394
- **synthesized_position**: similarity=0.197, lengths 442 ↔ 806
- **live_constraints**: jaccard=0.222, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.500, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.375, counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `20260423T085954Zdrift1` vs `20260423T090020Zdrift3`
- **decision_situation**: similarity=0.097, lengths 275 ↔ 527
- **original_framing**: similarity=0.102, lengths 292 ↔ 394
- **synthesized_position**: similarity=0.187, lengths 442 ↔ 959
- **live_constraints**: jaccard=0.000, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.222, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.111, counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `20260423T085954Zdrift1` vs `20260423T090028Zdrift4`
- **decision_situation**: similarity=0.701, lengths 275 ↔ 301
- **original_framing**: similarity=0.036, lengths 292 ↔ 323
- **synthesized_position**: similarity=0.409, lengths 442 ↔ 673
- **live_constraints**: jaccard=0.000, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.200, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.333, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.222, counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `20260423T090006Zdrift2` vs `20260423T090020Zdrift3`
- **decision_situation**: similarity=0.276, lengths 472 ↔ 527
- **original_framing**: similarity=0.155, lengths 394 ↔ 394
- **synthesized_position**: similarity=0.491, lengths 806 ↔ 959
- **live_constraints**: jaccard=0.000, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.375, counts 6 ↔ 5
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.100, counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `20260423T090006Zdrift2` vs `20260423T090028Zdrift4`
- **decision_situation**: similarity=0.116, lengths 472 ↔ 301
- **original_framing**: similarity=0.098, lengths 394 ↔ 323
- **synthesized_position**: similarity=0.272, lengths 806 ↔ 673
- **live_constraints**: jaccard=0.000, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.333, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.333, counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `20260423T090020Zdrift3` vs `20260423T090028Zdrift4`
- **decision_situation**: similarity=0.068, lengths 527 ↔ 301
- **original_framing**: similarity=0.223, lengths 394 ↔ 323
- **synthesized_position**: similarity=0.261, lengths 959 ↔ 673
- **live_constraints**: jaccard=0.000, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.571, counts 5 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.100, counts 6 ↔ 6
- **fabricated**: a=0, b=0
