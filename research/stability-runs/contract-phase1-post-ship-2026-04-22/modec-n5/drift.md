# Extraction drift report — contract-phase1-post-ship

Generated: 2026-04-22T21:01:55Z
Conversation: `/private/tmp/lolla_20260422T155622Z_conversation.txt` (26304 bytes)
Runs: 5
Run IDs: 20260422T210155Zdrift0, 20260422T210209Zdrift1, 20260422T210226Zdrift2, 20260422T210241Zdrift3, 20260422T210258Zdrift4

**Reading the metrics:**
- Free-text fields (`decision_situation`, `original_framing`, `synthesized_position`) — difflib SequenceMatcher ratio (character-level). 1.0 = identical; 0.7+ = very similar; 0.4–0.7 = material drift (paraphrase or reshape); <0.4 = shape-shift.
- List fields (`live_constraints`, `reasoning_passages`, `dropped_threads`) — Jaccard on normalized item text (strip, lowercase).
- `live_constraints_canonical_key` — Jaccard on `canonical_key` slugs with empty-string exclusion: empty/missing keys are filtered from BOTH sets before intersection so two failed extractions do not trivially match. A pair with all-empty keys on both sides is reported as `—` (undefined); the failure rate lives in `invalid_key_rate`.
- `invalid_key_rate` — share of constraints where `canonical_key` is missing or empty (the LLM failed the slug format rule). Per-run + overall. Acceptance gate target: ≤ 10%.
- `fabricated_count_per_run` — passages the extractor marked as not-a-literal-substring. Higher is worse.

## Aggregate drift

| Field | Metric | Mean | Min | Max |
|---|---|---|---|---|
| `decision_situation` | similarity | 0.282 | 0.109 | 0.707 |
| `original_framing` | similarity | 0.181 | 0.025 | 0.424 |
| `synthesized_position` | similarity | 0.233 | 0.129 | 0.511 |
| `live_constraints` | jaccard | 0.330 | 0.000 | 0.667 |
| `reasoning_passages` | jaccard | 0.371 | 0.182 | 0.625 |
| `dropped_threads` | jaccard | 0.100 | 0.000 | 1.000 |
| `live_constraints_canonical_key` | jaccard (empty-excl) | 0.466 | 0.222 | 0.833 |

**`invalid_key_rate` per run:** [0.0, 0.0, 0.0, 0.0, 0.0]
**`invalid_key_rate` overall:** 0.000 (0 invalid of 27 total constraints)
**Fabricated-quote counts per run:** [0, 0, 0, 0, 0]
**Capture health per run:** ['good', 'good', 'good', 'good', 'good']

## Pairwise detail

### `20260422T210155Zdrift0` vs `20260422T210209Zdrift1`
- **decision_situation**: similarity=0.249, lengths 470 ↔ 544
- **original_framing**: similarity=0.211, lengths 300 ↔ 384
- **synthesized_position**: similarity=0.322, lengths 729 ↔ 800
- **live_constraints**: jaccard=0.375, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.182, counts 7 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.833, counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `20260422T210155Zdrift0` vs `20260422T210226Zdrift2`
- **decision_situation**: similarity=0.277, lengths 470 ↔ 439
- **original_framing**: similarity=0.107, lengths 300 ↔ 336
- **synthesized_position**: similarity=0.183, lengths 729 ↔ 649
- **live_constraints**: jaccard=0.250, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.444, counts 7 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.250, counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `20260422T210155Zdrift0` vs `20260422T210241Zdrift3`
- **decision_situation**: similarity=0.298, lengths 470 ↔ 430
- **original_framing**: similarity=0.424, lengths 300 ↔ 394
- **synthesized_position**: similarity=0.511, lengths 729 ↔ 740
- **live_constraints**: jaccard=0.571, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.300, counts 7 ↔ 6
- **dropped_threads**: jaccard=1.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.571, counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `20260422T210155Zdrift0` vs `20260422T210258Zdrift4`
- **decision_situation**: similarity=0.293, lengths 470 ↔ 323
- **original_framing**: similarity=0.125, lengths 300 ↔ 308
- **synthesized_position**: similarity=0.133, lengths 729 ↔ 595
- **live_constraints**: jaccard=0.667, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.556, counts 7 ↔ 7
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.667, counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `20260422T210209Zdrift1` vs `20260422T210226Zdrift2`
- **decision_situation**: similarity=0.244, lengths 544 ↔ 439
- **original_framing**: similarity=0.047, lengths 384 ↔ 336
- **synthesized_position**: similarity=0.167, lengths 800 ↔ 649
- **live_constraints**: jaccard=0.000, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.333, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.222, counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `20260422T210209Zdrift1` vs `20260422T210241Zdrift3`
- **decision_situation**: similarity=0.263, lengths 544 ↔ 430
- **original_framing**: similarity=0.267, lengths 384 ↔ 394
- **synthesized_position**: similarity=0.138, lengths 800 ↔ 740
- **live_constraints**: jaccard=0.200, counts 6 ↔ 6
- **reasoning_passages**: jaccard=0.333, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.500, counts 6 ↔ 6
- **fabricated**: a=0, b=0

### `20260422T210209Zdrift1` vs `20260422T210258Zdrift4`
- **decision_situation**: similarity=0.221, lengths 544 ↔ 323
- **original_framing**: similarity=0.197, lengths 384 ↔ 308
- **synthesized_position**: similarity=0.129, lengths 800 ↔ 595
- **live_constraints**: jaccard=0.375, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.300, counts 6 ↔ 7
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.571, counts 6 ↔ 5
- **fabricated**: a=0, b=0

### `20260422T210226Zdrift2` vs `20260422T210241Zdrift3`
- **decision_situation**: similarity=0.707, lengths 439 ↔ 430
- **original_framing**: similarity=0.258, lengths 336 ↔ 394
- **synthesized_position**: similarity=0.335, lengths 649 ↔ 740
- **live_constraints**: jaccard=0.375, counts 5 ↔ 6
- **reasoning_passages**: jaccard=0.333, counts 6 ↔ 6
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.222, counts 5 ↔ 6
- **fabricated**: a=0, b=0

### `20260422T210226Zdrift2` vs `20260422T210258Zdrift4`
- **decision_situation**: similarity=0.157, lengths 439 ↔ 323
- **original_framing**: similarity=0.025, lengths 336 ↔ 308
- **synthesized_position**: similarity=0.259, lengths 649 ↔ 595
- **live_constraints**: jaccard=0.111, counts 5 ↔ 5
- **reasoning_passages**: jaccard=0.625, counts 6 ↔ 7
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.250, counts 5 ↔ 5
- **fabricated**: a=0, b=0

### `20260422T210241Zdrift3` vs `20260422T210258Zdrift4`
- **decision_situation**: similarity=0.109, lengths 430 ↔ 323
- **original_framing**: similarity=0.148, lengths 394 ↔ 308
- **synthesized_position**: similarity=0.157, lengths 740 ↔ 595
- **live_constraints**: jaccard=0.375, counts 6 ↔ 5
- **reasoning_passages**: jaccard=0.300, counts 6 ↔ 7
- **dropped_threads**: jaccard=0.000, counts 2 ↔ 2
- **live_constraints_canonical_key**: jaccard=0.571, counts 6 ↔ 5
- **fabricated**: a=0, b=0
